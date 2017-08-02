#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
import re
import subprocess
import threading
import string
import readline # interactive input
import argparse
import os
import signal


# CONFIGURATION
LOG_FILE = '/var/log/sodir/so/output.log' # log file path
LINES_END = '--lines=200' # number of lines from the end of file

# Console text formatting characters
class Colouring:
	C_RESET = '\033[0m'
	C_BOLD = '\033[1m'
	C_DIM = '\033[2m'
	C_ITALIC = '\033[3m'
	C_UNDERLINE = '\033[4m'

	C_BLACK = 0
	C_RED = 1
	C_GREEN = 2
	C_YELLOW = 3
	C_BLUE = 4
	C_MAGENTA = 5
	C_CYAN = 6
	C_WHITE = 7

	def textColor(colorNumber):
		return '\033[%dm' % (30 + colorNumber)

	def backgroundColor(colorNumber):
		return '\033[%dm' % (40 + colorNumber)

	C_DEBUG = textColor(C_GREEN) + C_BOLD
	C_INFO = textColor(C_BLUE) + C_BOLD
	C_WARN = textColor(C_YELLOW) + C_BOLD
	C_ERROR = textColor(C_RED) + C_BOLD
	C_EXCEPTION = textColor(C_RED)
	C_GREP = textColor(C_CYAN) + C_BOLD
	C_HIGHLIGHT = backgroundColor(C_CYAN) + C_BOLD
	C_HIGHLIGHT2 = backgroundColor(C_GREEN) + C_BOLD
	C_TRACE = C_DIM
	C_DATE = C_DIM
	C_XML_ELEMENT = textColor(C_RED)
	C_XML_ATTR_NAME = textColor(C_GREEN)
	C_XML_ATTR_VALUE = textColor(C_YELLOW)


# RegEx
def sedRegexReplace(findPattern, replacePattern):
	return " -e \"s/%s/%s/g\"" % (findPattern, replacePattern)

def sedRegexReplaceCaseI(findPattern, replacePattern):
	return " -e \"s/%s/%s/Ig\"" % (findPattern, replacePattern)

def highlightLogLevelRegex(logLevelName, colorChar):
	return sedRegexReplace(logLevelName, colorChar + logLevelName + Colouring.C_RESET)

HIDE_LINES_REGEX = ""
SHORT_TRACE_REGEX = sedRegexReplace(" \\[(\\w+)\\] ", " " + Colouring.C_TRACE + "\\1" + Colouring.C_RESET + " ")
NO_TRACE_REGEX = sedRegexReplace(" \\[\\w+\\] ", " ")
SHORT_DATE_REGEX = sedRegexReplace("^([0-9]+:[0-9]+:[0-9]+),([0-9]+) ", Colouring.C_DATE + "\\1,\\2" + Colouring.C_RESET + " ")
NO_DATE_REGEX = sedRegexReplace("^[0-9]+:[0-9]+:[0-9]+,[0-9]+ ", "")
CLEAR_DEBUG = sedRegexReplace("^(.*)DEBUG(.*)$", "")
CLEAR_INFO = sedRegexReplace("^(.*)INFO(.*)$", "")
CLEAR_WARN = sedRegexReplace("^(.*)WARN(.*)$", "")
REMOVE_EMPTY_LINES = " -e \"/^\\s*$/d\""
EXCEPTION_REGEX = sedRegexReplace("^\tat (.*)\\((.*)\\)$", "\\t" + Colouring.C_EXCEPTION + "at \\1" + Colouring.C_BOLD + "\\(\\2\\)" + Colouring.C_RESET)
STARTUP_HIGHLIGHT_REGEX = sedRegexReplaceCaseI("^(O D P O W I E D Z)$", Colouring.C_RESET + Colouring.C_HIGHLIGHT2 + "\\1" + Colouring.C_RESET)
STARTUP_HIGHLIGHT_REGEX += sedRegexReplaceCaseI("^(P Y T A N I E)$", Colouring.C_RESET + Colouring.C_HIGHLIGHT2 + "\\1" + Colouring.C_RESET)

XML_SYNTAX_REGEX = sedRegexReplace(r"<(\w+)", Colouring.C_RESET + "<" + Colouring.C_XML_ELEMENT + "\\1" + Colouring.C_RESET)
XML_SYNTAX_REGEX += sedRegexReplace(r"<\/(\w+)", Colouring.C_RESET + "<\/" + Colouring.C_XML_ELEMENT + "\\1" + Colouring.C_RESET)
XML_SYNTAX_REGEX += sedRegexReplace(r"((\w|\:)+)=\"([^\"]*?)\"", Colouring.C_RESET + Colouring.C_XML_ATTR_NAME + r"\1=" + Colouring.C_XML_ATTR_VALUE + r"\"\3\"" + Colouring.C_RESET)

LINES_ALL = '-n +0'
LINES_NONE = '--lines=0'


class BackgroundExecuteThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True
		self.__cmd = None
		self.__cmd2 = None
		self.__proc = None
		self.__proc2 = None

	def execute(self, cmd1, cmd2):
		"""executes one command or two commands linked by pipeline"""
		self.__cmd = cmd1
		self.__cmd2 = cmd2
		self.start()

	def run(self):
		if self.__cmd2 is None:
			# 1 command - output to console
			self.__proc = subprocess.Popen(self.__cmd, stdout=None, shell=True, preexec_fn=os.setsid)
		else:
			# 2 commands - streams redirection between processes
			self.__proc = subprocess.Popen(self.__cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
			self.__proc2 = subprocess.Popen(self.__cmd2, stdin=self.__proc.stdout, stdout=None, shell=True, preexec_fn=os.setsid)
		if self.__proc is not None:
			self.__proc.wait()
			self.__proc = None
		if self.__proc2 is not None:
			self.__proc2.wait()
			self.__proc2 = None

	def stop(self):
		self.__proc2 = self.__killProcess(self.__proc2)
		self.__proc = self.__killProcess(self.__proc)

	def __killProcess(self, proc):
		if proc is not None:
			if proc.poll() is None:
				os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
				proc.terminate()
		return None


class Main:
	def __init__(self):
		self.tailThread = None
		self.args = self.parseArguments()
		self.setDefaultSettings()

	def parseArguments(self):
		parser = argparse.ArgumentParser(description='Interactive log follower with syntax highlighting and formatting')
		return parser.parse_args()

	def start(self):
		try:
			self.checkLogFile()
			# run log tail with default settings
			self.restartLogTail()
			# wait for typed commands
			self.handleCommands()
		except KeyboardInterrupt: # Ctrl + C handling without printing stack trace
			print
			pass
		except: # closing threads before exit caused by critical error
			self.cleanUp()
			raise
		
		self.cleanUp()

	def checkLogFile(self):
		self.logFile = self.buildLogFilename()
		if not os.path.isfile(self.logFile):
			self.fatalError('log file does not exist: %s' % self.logFile)

	def buildLogFilename(self):
		self.logFile = LOG_FILE
		return self.logFile

	def shellExec(self, cmd):
		errCode = subprocess.call(cmd, shell=True)
		if errCode != 0:
			self.fatalError('failed executing: %s' % cmd)

	def shellOutput(self, cmd):
		process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
		output, err = process.communicate()
		return output

	def fatalError(self, message):
		print('[ERROR] %s' % message)
		self.cleanUp()
		sys.exit()

	def cleanUp(self):
		if self.tailThread is not None:
			self.tailThread.stop()


	def executeInBackground(self, backgroundThread, cmd1, cmd2=None):
		if backgroundThread is not None:
			backgroundThread.stop()
			del backgroundThread
		backgroundThread = BackgroundExecuteThread()
		backgroundThread.execute(cmd1, cmd2)
		return backgroundThread

	def restartLogTail(self, clear=True):
		if clear == True:
			self.consoleReset()
		(cmdTail, cmdSed) = self.buildCmds()
		self.tailThread = self.executeInBackground(self.tailThread, cmdTail, cmdSed)
	

	def consoleReset(self):
		"""clears screen"""
		self.shellExec('tput reset')

	def clearLog(self):
		fileSize = self.getFileSizeH(self.logFile)
		self.shellExec('echo "" > %s' % self.logFile)
		print(Colouring.C_DIM + self.logFile + ' (' + fileSize + ') cleared.' + Colouring.C_RESET)

	def getFileSizeBytes(self, filename):
		sizeOutput = self.shellOutput('stat --format=%%s %s' % self.logFile)
		sizeParts = re.split(r'[\t\n]+', sizeOutput)
		if len(sizeParts) > 0:
			return sizeParts[0]
		return None

	def getFileSizeH(self, filename):
		"""returns file size in human readable format"""
		bytesStr = self.getFileSizeBytes(filename)
		if bytesStr == None:
			return None
		Bs = int(bytesStr)
		if Bs < 1024:
			return "%d B" % Bs
		kBs = Bs / 1024.0
		if kBs < 1024:
			return "%.1f kB" % kBs
		MBs = kBs / 1024.0
		return "%.1f MB" % MBs

	def showLogStats(self):
		fileSize = self.getFileSizeH(self.logFile)
		print("File size: %s" % fileSize)
		linesCountOutput = self.shellOutput("wc -l %s" % self.logFile)
		linesParts = re.split(r'[\t ]+', linesCountOutput)
		if len(linesParts) > 0:
			print("Lines count: %s" % linesParts[0])

	def showSettings(self):
		print("LINES = " + self.LINES)
		print("LOG_LEVEL = " + self.LOG_LEVEL)
		print("DATE_FILTER = " + self.DATE_FILTER)
		print("TRACE_FILTER = " + self.TRACE_FILTER)
		print("SEARCH_FILTER = " + self.SEARCH_FILTER)
		print("FOLLOW_LOG = " + self.FOLLOW_LOG)
		print("HIDE_LINES = " + self.HIDE_LINES)
		print("cmd = %s | %s" % self.buildCmds())

	def buildCmds(self):
		cmdTail = "tail" + self.FOLLOW_LOG + " " + self.LINES + " " + self.logFile
		cmdSed = "sed -E"
		# colouring log levels
		cmdSed += highlightLogLevelRegex('INFO', Colouring.C_INFO)
		cmdSed += highlightLogLevelRegex('DEBUG', Colouring.C_DEBUG)
		cmdSed += highlightLogLevelRegex('WARN', Colouring.C_WARN)
		cmdSed += highlightLogLevelRegex('ERROR', Colouring.C_ERROR)
		# colouring exceptions
		cmdSed += EXCEPTION_REGEX
		# hiding lines containing specific text
		cmdSed += self.HIDE_LINES
		# filtering log levels
		cmdSed += self.LOG_LEVEL
		# filtering rubbish
		cmdSed += self.DATE_FILTER + self.TRACE_FILTER
		# text searching
		cmdSed += self.SEARCH_FILTER
		cmdSed += XML_SYNTAX_REGEX
		cmdSed += REMOVE_EMPTY_LINES
		return (cmdTail, cmdSed)

	# DEFAULT SETTINGS
	def setDefaultSettings(self):
		self.LINES = LINES_ALL
		self.DATE_FILTER = SHORT_DATE_REGEX
		self.TRACE_FILTER = SHORT_TRACE_REGEX
		self.HIDE_LINES = ""
		self.LOG_LEVEL = ""
		self.SEARCH_FILTER = STARTUP_HIGHLIGHT_REGEX
		self.FOLLOW_LOG = " -f"

	def printHelp(self):
		print('commands:')
		print('\t' + 'exit');
		print('\t' + 'clear - clear log file')
		print('\t' + 'stat - show log file statistics')
		print('\t' + 'new - new session (without clearing log)')
		print('\t' + 'all - display whole file')
		print('\t' + 'end - display only the last lines of file')
		print('\t' + 'debug, info, warn, error - set log level filter')
		print('\t' + 'nodate, shortdate, fulldate - format date')
		print('\t' + 'notrace, shorttrace, fulltrace - format trace')
		print('\t' + 'grep <text> / grepi <text> - show lines containing text (case sensitive / case insensitive)')
		print('\t' + 'highlight <text> - highlight text occurences')
		print('\t' + 'nofilter - turn off search filter')
		print('\t' + 'stop - stop following log file')
		print('\t' + 'reset - reset settings to default')
		print('\t' + 'settings - show current settings')

	def handleCommands(self):
		"""executing commands typed at runtime"""
		while True:
			inputCmd = raw_input()
			if self.executeCommand(inputCmd):
				break

	def executeCommand(self, inputCmd):
		"""executes command and returns true if exits"""
		# quit
		if inputCmd == "exit":
			return True
		# clear log
		elif inputCmd == "clear":
			self.consoleReset()
			self.clearLog()
			self.restartLogTail(clear=False)
			return False
		# log file statistics
		elif inputCmd == "stat":
			self.showLogStats()
			return False
		# new sessions without clearing log
		elif inputCmd == "new":
			self.LINES = LINES_NONE
		# showing whole file
		elif inputCmd == "all":
			self.LINES = LINES_ALL
		# showing few last lines
		elif inputCmd == "end":
			self.LINES = LINES_END
		# log level
		elif inputCmd == "debug":
			self.LOG_LEVEL = ""
		elif inputCmd == "info":
			self.LOG_LEVEL = CLEAR_DEBUG
		elif inputCmd == "warn":
			self.LOG_LEVEL = CLEAR_DEBUG + CLEAR_INFO
		elif inputCmd == "error":
			self.LOG_LEVEL = CLEAR_DEBUG + CLEAR_INFO + CLEAR_WARN
		# date filter
		elif inputCmd == "nodate": # without date and hour
			self.DATE_FILTER = NO_DATE_REGEX
		elif inputCmd == "shortdate": # short hour only
			self.DATE_FILTER = SHORT_DATE_REGEX
		elif inputCmd == "fulldate":
			self.DATE_FILTER = ""
		# trace filter
		elif inputCmd == "notrace": # without full name and source
			self.TRACE_FILTER = NO_TRACE_REGEX
		elif inputCmd == "shorttrace": # method name, short class name, row number
			self.TRACE_FILTER = SHORT_TRACE_REGEX
		elif inputCmd == "fulltrace":
			self.TRACE_FILTER = ""
		# case sensitive grep
		elif inputCmd.startswith("grep "):
			searchText = inputCmd[5:]
			self.SEARCH_FILTER = sedRegexReplace("(" + searchText + ")", Colouring.C_RESET + Colouring.C_GREP + "\\1" + Colouring.C_RESET)
			self.SEARCH_FILTER += " -n -e \"/" + searchText + "/p\""
		# case insensitive grep
		elif inputCmd.startswith("grepi "):
			searchText = inputCmd[6:]
			self.SEARCH_FILTER = sedRegexReplaceCaseI("(" + searchText + ")", Colouring.C_RESET + Colouring.C_GREP + "\\1" + Colouring.C_RESET)
			self.SEARCH_FILTER += " -n -e \"/" + searchText + "/Ip\""
		# highlighting found text
		elif inputCmd.startswith("highlight "):
			searchText = inputCmd[10:]
			self.SEARCH_FILTER = sedRegexReplaceCaseI("(" + searchText + ")", Colouring.C_RESET + Colouring.C_HIGHLIGHT + "\\1" + Colouring.C_RESET)
		# no filter
		elif inputCmd == "nofilter":
			self.SEARCH_FILTER=""
		# reset to default settings
		elif inputCmd == "reset":
			self.setDefaultSettings()
		# show current settings
		elif inputCmd == "settings":
			self.showSettings()
			return False
		# stops following log file
		elif inputCmd == "stop":
			if self.tailThread is not None:
				self.tailThread.stop()
			return False
		# prints available commands with description
		elif inputCmd == "help":
			self.printHelp()
			return False
		elif inputCmd and inputCmd.encode('base64') == "ZHVwYQ==\n":
			secret = "Q29uZ3JhdHVsYXRpb25zISBZb3UgZGlzY292ZXJlZCBFYXN0ZXIgRWdnIDop"
			print(secret.decode('base64'))
			return False
		else:
			if len(inputCmd) > 0:
				print('unknown command: %s (type "help")' % inputCmd)
			return False

		self.restartLogTail()
		return False


Main().start()
