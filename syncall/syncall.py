#!/usr/bin/python2
# -*- coding: utf-8 -*-

from utilframe import *

def listDirs():
	dirs = []
	for f in os.listdir('.'):
		if os.path.isdir(f):
			dirs.append(f)
	return sorted(dirs)

# ----- Main
def start():
	dirs = listDirs()
	for d in dirs:
		os.chdir(d)
		info('Repository: %s' % d)
		debug('pulling...')
		shellExec('git pull')
		debug('git status:')
		shellExec('git status')
		os.chdir('..')

start()
