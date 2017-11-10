#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os
import subprocess
import time

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

# ----- Main
def start():
	# start jack daemon
	print('starting jack daemon...')
	CMD_START_JACKD = 'jackd -dalsa -dhw:MID,0 -r44100 -p1024 -n2'
	shellExec('gnome-terminal -- sh -c \'%s\'' % CMD_START_JACKD)
	time.sleep(1)

	# songs list
	print('starting sublime...')
	shellExec('sublime -n /mnt/data/Igrek/linux/guitaramp/guitar-amp.md')

	# rakarrack
	print('starting rakarrack...')
	shellExec('rakarrack')

start()
