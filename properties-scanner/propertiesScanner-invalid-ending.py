#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os
import re
import getpass
import readline # interactive input
import argparse

# CONFIGURATION
DEFAULT_WORKSPACE_DIR = '/home/' + getpass.getuser() + '/workspace/solarstore/'
SEARCH_FILE_MASK = r'(.*)\.properties$'


def inputDirectory(directoryName, defaultDirectory):
	while True:
		directory = raw_input(directoryName + ' (default: ' + defaultDirectory + '): ')
		if not directory:
			directory = defaultDirectory
			print '(default ' + directoryName + ' set: ' + directory + ')'
		if not directory.endswith("/"):
			directory += "/"
		if not os.path.isdir(directory):
			print('ERROR: directory does not exist: ' + directory)
			continue
		print
		return directory

def scanAll(workspaceDir, args):
	for path in os.listdir(workspaceDir):
		absPath = os.path.join(workspaceDir, path)
		if os.path.isdir(absPath):
			scanDir(workspaceDir, absPath, args)

def scanDir(workspaceDir, path, args):
	for name in os.listdir(path):
		if name == 'src':
			srcPath = os.path.join(path, name)
			if os.path.isdir(srcPath):
				scanSrcDir(workspaceDir, srcPath, args)

def scanSrcDir(workspaceDir, srcPath, args):
	pattern = re.compile(SEARCH_FILE_MASK)
	for subdir, dirs, files in os.walk(srcPath):
		for file in files:
			if pattern.match(file):
				checkFile(workspaceDir, subdir, file, args)

def checkFile(workspaceDir, subdir, propertiesFile, args):
	propertiesPath = os.path.join(subdir, propertiesFile)
	relPropertiesPath = os.path.relpath(propertiesPath, workspaceDir)

	properties = readProperties(propertiesPath)
	# check all properties entries
	for key in properties:
		value = properties[key]
		if value.endswith('\\'):
			print('value %s = %s ends with \\: %s' % (key, value, relPropertiesPath))

def readProperties(path):
	properties = {}
	with open(path) as f:
		for line in f:
			if (not line.startswith('#')) and '=' in line:
				name, value = line.split('=', 1)
				properties[name.strip()] = value.strip()
	return properties

def parseArguments():
	parser = argparse.ArgumentParser(description='Scan for missing properties')
	parser.add_argument('--create', action='store_true', help='create missing properties')
	return parser.parse_args()

args = parseArguments()
workspaceDir = inputDirectory('Workspace dir', DEFAULT_WORKSPACE_DIR)
scanAll(workspaceDir, args)
