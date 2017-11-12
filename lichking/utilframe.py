#!/usr/bin/python2
# -*- coding: utf-8 -*-

# UTILITY FRAMEWORK
import os
import sys
import re
import subprocess
import glob
import inspect

# ----- Output
def debug(message):
	print('\033[32m\033[1m[debug]\033[0m ' + message)

def info(message):
	print('\033[34m\033[1m[info]\033[0m ' + message)

def warn(message):
	print('\033[33m\033[1m[warn]\033[0m ' + message)

def error(message):
	print('\033[31m\033[1m[ERROR]\033[0m ' + message)

def fatal(message):
	error(message)
	raise Exception('Fatal error: %s' % message)

# ----- Shell
def shellExec(cmd):
	errCode = subprocess.call(cmd, shell=True)
	if errCode != 0:
		fatal('failed executing: %s' % cmd)

def shellExecErrorCode(cmd):
	return subprocess.call(cmd, shell=True)

def shellOutput(cmd):
	process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	output, err = process.communicate()
	return output

# ----- String operations
def splitLines(inputString):
	allLines = inputString.splitlines()
	return filter(lambda l: len(l) > 0, allLines) # filter nonempty

def regexReplace(inputString, regexMatch, regexReplace):
	regexMatcher = re.compile(regexMatch)
	return regexMatcher.sub(regexReplace, inputString)

def regexMatch(inputString, regexMatch):
	regexMatcher = re.compile(regexMatch)
	return regexMatcher.match(inputString)

def regexReplaceLines(lines, regexMatch, regexReplace):
	regexMatcher = re.compile(regexMatch)
	filtered = []
	for line in lines:
		line = regexMatcher.sub(regexReplace, line)
		filtered.append(line)
	return filtered

def regexFilterLines(lines, regexMatch):
	regexMatcher = re.compile(regexMatch)
	filtered = []
	for line in lines:
		if regexMatcher.match(line):
			filtered.append(line)
	return filtered

def regexSearch(filePath, regexMatch, groupNumber):
	regexMatcher = re.compile(regexMatch)
	with open(filePath) as f:
		for line in f:
			match = regexMatcher.match(line)
			if match:
				return match.group(groupNumber)

# ----- CLI arguments
class CommandArgRule:
	def __init__(self, isOption, action, name, description, syntaxSuffix):
		self.isOption = isOption
		self.action = action
		# store names list
		self.names = name if isinstance(name, list) else [name]
		self.description = description
		self.syntaxSuffix = syntaxSuffix

	def displayNames(self):
		return ', '.join(self.names)

	def displaySyntax(self):
		syntax = self.displayNames()
		if self.syntaxSuffix:
			syntax += self.syntaxSuffix if self.syntaxSuffix[0] == ' ' else ' ' + self.syntaxSuffix
		return syntax

	def displayHelp(self, syntaxPadding):
		dispHelp = self.displaySyntax()
		if self.description:
			dispHelp = dispHelp.ljust(syntaxPadding) + ' - ' + self.description
		return dispHelp

class ArgumentsProcessor:
	def __init__(self, appName):
		self._appName = appName
		self.registeredRules = []

	def bindOption(self, action, name, description=None, syntaxSuffix=None):
		self.registeredRules.append(CommandArgRule(True, action, name, description, syntaxSuffix))

	def bindCommand(self, action, name, description=None, syntaxSuffix=None):
		self.registeredRules.append(CommandArgRule(False, action, name, description, syntaxSuffix))

	def popArgument(self):
		if not self.argsQue:
			return None
		nextArg = self.argsQue[0]
		self.argsQue = self.argsQue[1:]
		return nextArg

	def nextArgument(self):
		return None if not self.argsQue else self.argsQue[0]

	def hasNextArgument(self):
		return len(self.argsQue) > 0

	def popRequiredParam(self, paramName):
		param = self.popArgument()
		if not param:
			fatal('no %s parameter given' % paramName)
		return param

	def processAll(self):
		self.argsQue = sys.argv[1:]  # CLI arguments list
		# empty arguments list - print help
		if not self.argsQue:
			self.printHelp()
		while self.argsQue:
			self._processArgument(self.popArgument())

	def _findCommandArgRule(self, arg):
		for rule in self.registeredRules:
			if arg in rule.names:
				return rule

	def _processArgument(self, arg):
		# TODO first process all options, then left commands
		rule = self._findCommandArgRule(arg)
		if rule:
			(args, _, _, _) = inspect.getargspec(rule.action)
			if len(args) == 0:
				rule.action()
			else:
				rule.action(self)
		else:
			fatal('unknown argument: %s' % arg)

	def _registeredOptionsCount(self):
		return sum(1 for rule in self.registeredRules if rule.isOption)

	def _registeredCommandsCount(self):
		return sum(1 for rule in self.registeredRules if not rule.isOption)

	def _calcMinSyntaxPadding(self):
		minSyntaxPadding = 0
		for rule in self.registeredRules:
			syntax = rule.displaySyntax()
			if len(syntax) > minSyntaxPadding: # min padding = max from len(syntax)
				minSyntaxPadding = len(syntax)
		return minSyntaxPadding

	def printHelp(self):
		# autocomplete help
		print('%s\n' % self._appName)
		print('Usage:')
		usageSyntax = sys.argv[0]
		if self._registeredOptionsCount() > 0:
			usageSyntax += ' [options]'
		if self._registeredCommandsCount() > 0:
			usageSyntax += ' <command>'
		print('  %s' % usageSyntax)
		syntaxPadding = self._calcMinSyntaxPadding()
		if self._registeredCommandsCount() > 0:
			print('\nCommands:')
			for rule in self.registeredRules:
				if not rule.isOption:
					print('  %s' % rule.displayHelp(syntaxPadding))
		if self._registeredOptionsCount() > 0:
			print('\nOptions:')
			for rule in self.registeredRules:
				if rule.isOption:
					print('  %s' % rule.displayHelp(syntaxPadding))
		sys.exit()

def printHelp(argsProcessor):
	# workaround for invoking help by function reference
	argsProcessor.printHelp()
