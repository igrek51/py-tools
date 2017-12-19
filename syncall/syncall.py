#!/usr/bin/python2
# -*- coding: utf-8 -*-

from glue import *

def start():
	for d in listDir('.'):
		if os.path.isdir(d):
			setWorkdir(d)
			info('Repository: %s...' % d)
			shellExec('git pull')
			statusOutput = shellOutput('git status')
			if not ('Your branch is up-to-date' in statusOutput and 'nothing to commit, working tree clean' in statusOutput):
				debug('git status - %s:' % d)
				print(statusOutput)
				if 'Your branch is ahead' in statusOutput:
					debug('pushing - %s...' % d)
					shellExec('git push')
			setWorkdir('..')

start()
