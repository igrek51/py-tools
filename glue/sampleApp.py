#!/usr/bin/python
from glue import *

# ----- Commands
def commandSample(argsProcessor):
	print(argsProcessor.pollNextRequired('param'))

# ----- Main
def start():
	argsProcessor = ArgumentsProcessor('SampleApp', '1.0.1')

	argsProcessor.bindCommand(commandSample, 'sample', description='description', syntaxSuffix='<param>')

	argsProcessor.bindOption(printHelp, ['-h', '--help'], description='display this help and exit')
	argsProcessor.bindOption(printVersion, ['-v', '--version'], description='print version and exit')

	argsProcessor.processAll()

if __name__ == '__main__': # for debugging by importing module
	start()
