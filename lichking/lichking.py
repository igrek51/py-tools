#!/usr/bin/python2
# -*- coding: utf-8 -*-

from random import randint
from utilframe import *


GAME_DIR = '/home/thrall/games/warcraft-3-pl/'
LICHKING_HOME = '/home/thrall/lichking/'
VERSION = 'v1.0.6'

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
	debug('Error code: %d' % errorCode)
	info('"Jeszcze jedną kolejkę?"')
	playVoice('pandarenbrewmaster-jeszcze-jedna-kolejke')

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
	else:
		fatal('unknown tipsName: %s' % tipsName)

# ----- Main
def start():
	argsProcessor = ArgumentsProcessor('LichKing - WarcraftOS tool %s' % VERSION)
	argsProcessor.bindCommand(commandRunGame, ['war', 'go'], description='run the game using wine')
	argsProcessor.bindCommand(commandPlayVoice, 'voice', description='list available voices')
	argsProcessor.bindCommand(commandPlayVoice, 'voice', description='play selected voice sound', syntaxSuffix='[voiceName]')
	argsProcessor.bindCommand(commandPlayVoice, 'voice', description='play random voice sound', syntaxSuffix='random')
	argsProcessor.bindCommand(commandOpenTips, 'tips', description='open Dota tips', syntaxSuffix='dota')
	argsProcessor.bindOption(printHelp, ['-h', '--help', 'help'], description='display this help and exit')

	argsProcessor.processAll()

start()
