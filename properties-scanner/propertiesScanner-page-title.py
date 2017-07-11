#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os
import re
import getpass
import readline # interactive input
import argparse

# CONFIGURATION
DEFAULT_WORKSPACE_DIR = '/home/' + getpass.getuser() + '/workspace/solarstore/'
SEARCH_FILE_MASK = r'(.*)Page\.java$'
PROPERTY_NAME = 'title'
DEFAULT_PROPERTY_VALUE = 'Raport sprzeda\u017cy'.lower()


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

def checkFile(workspaceDir, subdir, srcFile, args):
	propertiesFile = getPropertiesFilename(srcFile)
	propertiesPath = os.path.join(subdir, propertiesFile)
	relPropertiesPath = os.path.relpath(propertiesPath, workspaceDir)

	# skip abstract classes
	if isClassAbstract(subdir, srcFile):
		return

	# check missing properties file
	if not os.path.isfile(propertiesPath):
		print('Missing properties file: %s' % relPropertiesPath)
		if args.repair:
			createMissingProperties(propertiesPath, relPropertiesPath)
		return

	properties = readProperties(propertiesPath)
	# check missing property in file
	if not properties.has_key(PROPERTY_NAME):
		print('Missing %s property: %s' % (PROPERTY_NAME, relPropertiesPath))
		if args.repair:
			addMissingProperties(propertiesPath, relPropertiesPath)
		return

	title = properties[PROPERTY_NAME]
	# check non empty property value
	if len(title) == 0:
		print('Empty %s property value: %s' % (PROPERTY_NAME, relPropertiesPath))
		return

	# check default property value
	if title.lower() == DEFAULT_PROPERTY_VALUE:
		print('[warn] Default property %s = %s in file: %s' % (PROPERTY_NAME, title, relPropertiesPath))
		return

def getPropertiesFilename(file):
	return re.sub(r'\.java$', r'.properties', file)

def readProperties(path):
	properties = {}
	with open(path) as f:
		for line in f:
			if (not line.startswith('#')) and '=' in line:
				name, value = line.split('=', 1)
				properties[name.strip()] = value.strip()
	return properties

def isClassAbstract(subdir, srcFile):
	filePath = os.path.join(subdir, srcFile)
	with open(filePath) as f:
		for line in f:
			if line.startswith('public abstract class'):
				return True
			if line.startswith('public class'):
				return False
	return False

def createMissingProperties(propertiesPath, relPropertiesPath):
	print("+++++ Creating missing properties file: %s" % relPropertiesPath)
	with open(propertiesPath, 'w+') as f:
		f.write(PROPERTY_NAME)
		f.write(' = ')

def addMissingProperties(propertiesPath, relPropertiesPath):
	print("+++++ Adding missing property: %s" % relPropertiesPath)
	with open(propertiesPath, 'r+') as f:
		content = f.read()
		f.seek(0, 0)
		f.write(PROPERTY_NAME + ' = \n' + content)

def parseArguments():
	parser = argparse.ArgumentParser(description='Scan for missing properties')
	parser.add_argument('--repair', action='store_true', help='create missing properties')
	return parser.parse_args()

args = parseArguments()
workspaceDir = inputDirectory('Workspace dir', DEFAULT_WORKSPACE_DIR)
scanAll(workspaceDir, args)
