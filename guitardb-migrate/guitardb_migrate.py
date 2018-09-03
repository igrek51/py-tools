#!/usr/bin/env python
# -*- coding: utf-8 -*-
from glue import *

# ----- Actions
def actionMigrate(ap):
	inputDir = ap.getParam('input')
	if not inputDir:
		fatal('no input parameter')
	outputDb = ap.getParam('output')
	if not outputDb:
		fatal('no output parameter')


# ----- Main
def main():
	ap = ArgsProcessor('GuitarDb migrate', '1.0.1')
	ap.bindDefaultAction(actionMigrate, help='migrate from guitarDb CRD files to SQLite database')
	ap.bindParam('input', help='guitarDb CRD main directory')
	ap.bindParam('output', help='SQLite database output file')
	# do the magic
	ap.processAll()

if __name__ == '__main__':
	main() # testing purposes
