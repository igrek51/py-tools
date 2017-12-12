#!/usr/bin/python2
# -*- coding: utf-8 -*-

from utilframe import *

def start():
	for d in listDir('.'):
		if os.path.isdir(d):
			os.chdir(d)
			info('Repository: %s' % d)
			debug('pulling %s...' % d)
			shellExec('git pull')
			debug('git status - %s...' % d)
			shellExec('git status')
			os.chdir('..')

start()
