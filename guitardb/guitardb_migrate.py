#!/usr/bin/env python
# -*- coding: utf-8 -*-
from glue import *
import sqlite3
import datetime
import time

NOW = datetime.datetime.now()
DB_VERSION_NUMBER = 2

categoriesIdDict = {}

lockedDict = {
	'Z jajem': 'zjajem',
	'BFF': 'bff',
	'Inżynier': 'engineer',
	'Religijne': 'religijne'
}

# ----- Actions
def actionMigrate(ap):
	inputDir = ap.getParam('input')
	if not inputDir:
		fatal('no input parameter')
	outputDb = ap.getParam('output')
	if not outputDb:
		fatal('no output parameter')
	# clear file before
	if os.path.exists(outputDb):
  		os.remove(outputDb)
	# sql connection
	conn = sqlite3.connect(outputDb)
	c = conn.cursor()
	createSchema(c)
	addDbInfo(c)
	addCategories(c, inputDir)
	addSongs(c, inputDir)
	# Save (commit) the changes
	conn.commit()
	conn.close()

def createSchema(c):
	# Create tables
	c.execute('''CREATE TABLE songs (
		id integer PRIMARY KEY,
		title text NOT NULL,
		categoryId integer NOT NULL,
		fileContent text,
		versionNumber integer NOT NULL,
		updateTime integer,
		custom integer NOT NULL,
		filename text,
		comment text,
		preferredKey text,
		locked integer NOT NULL,
		lockPassword text,
		author text
		);''')
	c.execute('''CREATE TABLE categories (
		id integer PRIMARY KEY,
		typeId integer NOT NULL,
		name text
		);''')
	c.execute('''CREATE TABLE info (
		name text,
		value text
		);''')

def addDbInfo(c):
	c.execute('''INSERT INTO info (name, value)
		VALUES ('versionDate', ?);''',
		(time2str(NOW, '%Y-%m-%d'),))
	c.execute('''INSERT INTO info (name, value)
		VALUES ('versionTimestamp', ?);''',
		(int(time.mktime(NOW.timetuple())),))
	c.execute('''INSERT INTO info (name, value)
		VALUES ('versionNumber', ?);''',
		(DB_VERSION_NUMBER,))

def listCategories(inputDir):
	return filter(lambda d: os.path.isdir(os.path.join(inputDir, d)) and not d.startswith('.'), listDir(inputDir))

def addCategories(c, inputDir):
	for category in listCategories(inputDir):
		addCategory(c, inputDir, category)

def addCategory(c, inputDir, categoryName0):
	typeId = 1
	categoryName = categoryName0
	if categoryName == '0thers':
		typeId = 3
		categoryName = None
	# inserting record
	c.execute('SELECT MAX(id) AS id FROM categories')
	identifier = c.fetchone()[0]
	identifier = 1 if not identifier else identifier + 1
	c.execute('''INSERT INTO categories
		(id, typeId, name)
		VALUES (?, ?, ?);
		''', (identifier, typeId, None if not categoryName else categoryName.decode('utf-8')))
	categoriesIdDict[categoryName0] = identifier
	info('category saved: %d - %s' % (identifier, categoryName))

def addSongs(c, inputDir):
	for category in listCategories(inputDir):
		subdirPath = os.path.join(inputDir, category)
		categoryId = categoriesIdDict[category]
		names = listDir(subdirPath)
		for filename in names:
			addSong(c, inputDir, category, categoryId, filename)

def addSong(c, inputDir, category, categoryId, filename):
	songname = filename.capitalize()
	if songname.endswith('.crd'):
		songname = songname[:-4]
	fullPath = os.path.join(inputDir, category, filename)
	fileContent = readFile(fullPath).encode('utf-8')
	versionNumber = 1
	updateTime = time.mktime(NOW.timetuple())
	custom = 0
	# lock
	locked = 0
	lockPassword = None
	if category in lockedDict:
		locked = 1
		lockPassword = lockedDict[category].decode('utf-8')
	# content trim, comments read
	lines = fileContent.splitlines()
	firstLine = lines[0]
	comment = None
	preferredKey = None
	if regexMatch(firstLine, r'^{(.*)}$'):
		debug('retrieving comment: ' + firstLine)
		comment = regexReplace(firstLine, r'^{(.*)}$', '\\1')
		preferredKey = comment
		comment = None
		fileContent = '\n'.join(lines[1:])
	fileContent = fileContent.strip()
	author = 'igrek'
	# inserting record
	c.execute('SELECT MAX(id) AS id FROM songs')
	identifier = c.fetchone()[0]
	identifier = 1 if not identifier else identifier + 1
	c.execute('''INSERT INTO songs
		(id,
		fileContent, title, categoryId,
		versionNumber, updateTime,custom,filename,
		comment,preferredKey,locked,lockPassword, author)
		VALUES (?, ?, ?, ?,
		?, ?, ?, ?,
		?, ?, ?, ?, ?);
		''', (identifier, fileContent.decode('utf-8'), songname.decode('utf-8'),
			categoryId,
			versionNumber, updateTime, custom, filename.decode('utf-8'),
			comment, preferredKey, locked, lockPassword, author))
	info('song saved: %d - %s - %s' % (identifier, category, songname))

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
