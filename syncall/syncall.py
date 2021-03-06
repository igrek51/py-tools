#!/usr/bin/python2
from glue import *

def main():
	for d in listDir('.'):
		if os.path.isdir(d):
			wd = getWorkdir()
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
			setWorkdir(wd)

if __name__ == '__main__': # for testing purposes
	main() # this will not be invoked when importing this file
