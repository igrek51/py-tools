#!/usr/bin/python2
# -*- coding: utf-8 -*-

from random import randint
from utilframe import *


GAME_DIR = '/home/thrall/games/warcraft-3-pl/'
LICHKING_HOME = '/home/thrall/lichking/'
VERSION = '1.8.10'

def listVoices():
	voicesDir = getVoicesDir()
	voices = []
	for file in os.listdir(voicesDir):
		if os.path.isfile(voicesDir + file):
			if file.endswith('.wav'):
				voices.append(file[:-4])
	return sorted(voices)

def playVoice(voiceName):
	voicesDir = getVoicesDir()
	if not voiceName.endswith('.wav'):
		voiceName = voiceName + '.wav'
	if not os.path.isfile(voicesDir + voiceName):
		error('no voice file named %s' % voiceName)
	else:
		shellExec('aplay %s' % (voicesDir + voiceName))

def playRandomVoice():
	# populate voices list
	voices = listVoices()
	# draw random voice
	if not voices:
		fatal('no voice available')
	randomVoice = voices[randint(0, len(voices)-1)]
	playVoice(randomVoice)

def validateHomeDir():
	global LICHKING_HOME
	if not os.path.isdir(LICHKING_HOME) and LICHKING_HOME:
		warn('lichking home not found: %s' % LICHKING_HOME)
		LICHKING_HOME = ''

def getVoicesDir():
	validateHomeDir()
	return LICHKING_HOME + 'voices/'

def testSound():
	info('testing audio...')
	playRandomVoice()

def testNetwork():
	info('Useful Linux commands (for your own purposes): ifconfig, ping, nmap, ip')
	info('available network interfaces (up):')
	ifconfig = shellOutput('sudo ifconfig')
	lines = splitLines(ifconfig)
	lines = regexFilterLines(lines, r'^([a-z0-9]+).*')
	lines = regexReplaceLines(lines, r'^([a-z0-9]+).*', '\\1')
	if not lines:
		fatal('no available network interfaces')
	for interface in lines:
		print(interface)
	info('testing IPv4 global DNS connectivity...')
	shellExec('ping 8.8.8.8 -c 4')
	info('testing global IP connectivity...')
	shellExec('ping google.pl -c 4')

def testGraphics():
	info('testing GLX (OpenGL for X Window System)...')
	errorCode = shellExecErrorCode('glxgears')
	debug('glxgears error code: %d' % errorCode)

def showWarcraftosInfo():
	info('WarcraftOS v%s' % VERSION)
	info('thrall user password: war')
	info('root user password: war')
	info('When launching the game, you have custom keys shortcuts (QWER) already enabled.')

# ----- Commands
def commandRunGame():
	# set workdir
	os.chdir(GAME_DIR)
	info('"Łowy rozpoczęte."')
	playVoice('rexxar-lowy-rozpoczete')
	# RUN WINE
	# LANG settings
	shellExec('LANG=pl_PL.UTF-8')
	# 32 bit wine
	shellExec('export WINEARCH=win32')
	#shellExec('export WINEPREFIX=/home/thrall/.wine32')
	# 64 bit wine
	#shellExec('export WINEARCH=win64')
	#shellExec('unset WINEPREFIX')
	errorCode = shellExecErrorCode('wine "Frozen Throne.exe" -opengl')
	debug('wine error code: %d' % errorCode)
	info('"Jeszcze jedną kolejkę?"')

def commandPlayVoice(argsProcessor):
	# list available voices
	if not argsProcessor.hasNextArgument():
		info('Available voices:')
		for voiceName in listVoices():
			print(voiceName)
	else:
		voiceName = argsProcessor.popArgument()
		if voiceName == 'random': # play random voice
			playRandomVoice()
		else: # play selected voice
			playVoice(voiceName)

def commandOpenTips(argsProcessor):
	tipsName = argsProcessor.popRequiredParam('tipsName')
	if tipsName == 'dota':
		os.chdir(GAME_DIR)
		shellExec('sublime dota-info.md')
	elif tipsName == 'warcraftos':
		showWarcraftosInfo()
	else:
		fatal('unknown tipsName: %s' % tipsName)

def commandTest(argsProcessor):
	testName = argsProcessor.popRequiredParam('testName')
	if testName == 'audio':
		testSound()
	elif testName == 'network':
		testNetwork()
	elif testName == 'graphics':
		testGraphics()
	else:
		fatal('unknown testName: %s' % testName)

def commandScreen(argsProcessor):
	if not argsProcessor.hasNextArgument():
		# list outputs
		xrandr = shellOutput('xrandr 2>/dev/null | grep " connected"')
		lines = splitLines(xrandr)
		lines = regexReplaceLines(lines, r'^([a-zA-Z0-9\-]+).*', '\\1')
		if not lines:
			fatal('no xrandr outputs - something\'s fucked up')
		info('Available screens:')
		for screenName in lines:
			print(screenName)
	else: # set output primary
		screenName = argsProcessor.popArgument()
		info('setting screen %s as primary...' % screenName)
		shellExec('xrandr --output %s --primary' % screenName)
		info('done')

# ----- Main
def start():
	argsProcessor = ArgumentsProcessor('LichKing - WarcraftOS tool', VERSION)
	argsProcessor.bindCommand(commandRunGame, ['war', 'go'], description='run the game using wine')
	argsProcessor.bindCommand(commandTest, 'test', description='perform audio test', syntaxSuffix='audio')
	argsProcessor.bindCommand(commandTest, 'test', description='perform graphics tests', syntaxSuffix='graphics')
	argsProcessor.bindCommand(commandTest, 'test', description='perform network tests', syntaxSuffix='network')
	argsProcessor.bindCommand(commandScreen, 'screen', description='list available screens')
	argsProcessor.bindCommand(commandScreen, 'screen', description='set screen as primary', syntaxSuffix='[screenName]')
	argsProcessor.bindCommand(commandPlayVoice, 'voice', description='list available voices')
	argsProcessor.bindCommand(commandPlayVoice, 'voice', description='play selected voice sound', syntaxSuffix='[voiceName]')
	argsProcessor.bindCommand(commandPlayVoice, 'voice', description='play random voice sound', syntaxSuffix='random')
	argsProcessor.bindCommand(commandOpenTips, 'info', description='show warcraftos tips', syntaxSuffix='warcraftos')
	argsProcessor.bindCommand(commandOpenTips, 'info', description='open Dota tips', syntaxSuffix='dota')
	argsProcessor.bindOption(printHelp, ['-h', '--help', 'help'], description='display this help and exit')
	argsProcessor.bindOption(printVersion, ['-v', '--version'], description='print version number and exit')

	argsProcessor.processAll()

start()
