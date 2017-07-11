#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os
import re
import getpass
import readline # interactive input
import argparse

# CONFIGURATION
DEFAULT_WORKSPACE_DIR = '/home/' + getpass.getuser() + '/workspace/solarstore/'
BASE_FILE_MASK = r'(.*)\.properties$'
TRANSLATED_FILE_MASK = r'(.*)_(\w{2})\.properties$'


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

def listSrcDirs(workspaceDir):
	srcDirs = []
	# for all projects
	for path in os.listdir(workspaceDir):
		absPath = os.path.join(workspaceDir, path)
		if os.path.isdir(absPath):
			# scan dir inside
			for name in os.listdir(absPath):
				# search for src dir
				if name == 'src':
					srcPath = os.path.join(absPath, name)
					if os.path.isdir(srcPath):
						srcDirs.append(srcPath)
	return srcDirs

def findAllLanguages(workspaceDir):
	langs = set()
	for srcPath in listSrcDirs(workspaceDir):
		# scan src dir
		for subdir, dirs, files in os.walk(srcPath):
			for file in files:
				match = re.match(TRANSLATED_FILE_MASK, file)
				if match:
					lang = match.group(2)
					langs.add(lang)
	return langs

def scanAll(workspaceDir, langs, args):
	for srcPath in listSrcDirs(workspaceDir):
		scanSrcDir(workspaceDir, srcPath, langs, args)

def scanSrcDir(workspaceDir, srcPath, langs, args):
	for subdir, dirs, files in os.walk(srcPath):
		for file in files:
			if re.match(BASE_FILE_MASK, file) and not re.match(TRANSLATED_FILE_MASK, file):
				checkFile(workspaceDir, subdir, file, langs, args)

def checkFile(workspaceDir, subdir, propertiesFile, langs, args):
	propertiesPath = os.path.join(subdir, propertiesFile)
	relPropertiesPath = os.path.relpath(propertiesPath, workspaceDir)

	properties = readProperties(propertiesPath)

	for lang in langs:
		checkLangFile(workspaceDir, subdir, propertiesPath, properties, lang, args)

def checkLangFile(workspaceDir, subdir, propertiesPath, properties, lang, args):
	translatedPath = translatedPropertiesFilename(propertiesPath, lang)
	relTranslatedPath = os.path.relpath(translatedPath, workspaceDir)
		
	# check if language file exists
	if not os.path.isfile(translatedPath):
		printMissing('!!!!! Missing translations properties file', lang, relTranslatedPath)
		return

	translatedProperties = readProperties(translatedPath)

	for key in properties:
		
		value = properties[key]

		# check if all keys exist in translated properties
		if not translatedProperties.has_key(key):
			if len(value) > 0:
				printMissing('!!!!! No translation for a key: %s' % key, lang, relTranslatedPath)
			continue

		translatedValue = translatedProperties[key]

		# empty translated value
		if len(value) > 0 and len(translatedValue) == 0:
			printMissing(' !!!  Empty translation for a key: %s' % key, lang, relTranslatedPath)
			continue

		# same translated value
		if len(value) > 0 and translatedValue == value:
			printMissing(' !!!  Translated value is equal to base value: %s = %s' % (key, value), lang, relTranslatedPath)
			continue
		
	for key in translatedProperties:
		# check for reduntant keys in translated properties
		if not properties.has_key(key):
			translatedValue = translatedProperties[key]
			printMissing('  !   Redundant translation for not existing base value: %s = %s' % (key, translatedValue), lang, relTranslatedPath)
			if args.repair:
				fixRedundantTranslation(key, translatedValue, lang, relTranslatedPath, translatedPath)
			continue

def printMissing(message, lang, relTranslatedPath):
	print('[%s] %s\t--- file: %s' % (lang, message, relTranslatedPath))
	global errorsCount
	errorsCount += 1

def readProperties(path):
	properties = {}
	with open(path) as f:
		for line in f:
			if (not line.startswith('#')) and ('=' in line or ':' in line):
				splitted = re.split(r'=|:', line)
				name = splitted[0]
				value = ':'.join(splitted[1:])
				properties[name.strip()] = value.strip()
	return properties

def translatedPropertiesFilename(baseFileName, lang):
	match = re.match(BASE_FILE_MASK, baseFileName)
	if match:
		return match.group(1) + '_' + lang + '.properties'
	return None

def fixRedundantTranslation(key, translatedValue, lang, relTranslatedPath, translatedPath):
	f = open(translatedPath, "r")
	lines = f.readlines()
	f.close()
	# rewrite file without redundant key
	f = open(translatedPath, "w")
	deletions = 0
	for line in lines:
		if line.startswith(key+' =') or line.startswith(key+'=') or line.startswith(key+' :') or line.startswith(key+':'):
			deletions += 1
		else:
			f.write(line)
	f.close()
	
	if deletions == 0:
		raise Exception('no line has been removed when fixing reduntant translation %s = %s, file: %s' % (key, translatedValue, relTranslatedPath))
	if deletions > 1:
		raise Exception('more than 1 (%s) line have been removed when fixing reduntant translation %s = %s, file: %s' % (deletions, key, translatedValue, relTranslatedPath))
	printMissing('----- Redundant translation has been removed: %s = %s' % (key, translatedValue), lang, relTranslatedPath)

def parseArguments():
	parser = argparse.ArgumentParser(description='Scan for missing or broken properties translations')
	parser.add_argument('--repair', action='store_true', help='fix if possible')
	return parser.parse_args()


args = parseArguments()
workspaceDir = inputDirectory('Workspace dir', DEFAULT_WORKSPACE_DIR)

langs = findAllLanguages(workspaceDir)
print("Languages: " + ', '.join(langs))

errorsCount = 0
scanAll(workspaceDir, langs, args)
print('Errors: %s' % errorsCount)
