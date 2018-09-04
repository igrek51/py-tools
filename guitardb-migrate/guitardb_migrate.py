#!/usr/bin/env python
# -*- coding: utf-8 -*-
from glue import *
import sqlite3
import datetime
import time

NOW = datetime.datetime.now()

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
	
	conn = sqlite3.connect(outputDb)
	c = conn.cursor()

	createSchema(c)
	insertDbInfo(c)
	addSongs(c, inputDir)
	# Save (commit) the changes
	conn.commit()
	# Just be sure any changes have been committed or they will be lost.
	conn.close()

def createSchema(c):
	# Create tables
	c.execute('''CREATE TABLE songs (
		id integer PRIMARY KEY,
		fileContent text NOT NULL,
		title text NOT NULL,
		categoryName text,
		versionNumber integer NOT NULL,
		updateTime integer,
		custom integer NOT NULL,
		filename text,
		comment text,
		preferredKey text,
		locked integer NOT NULL,
		lockPassword text
		);''')
	c.execute('''CREATE TABLE info (
		name text,
		value text
		);''')

def insertDbInfo(c):
	c.execute('''INSERT INTO info (name, value)
		VALUES ('versionDate', ?);''',
		(time2str(NOW, '%Y-%m-%d'),))

def addSongs(c, inputDir):
	categories = filter(lambda d: os.path.isdir(os.path.join(inputDir, d)) and not d.startswith('.'), listDir(inputDir))
	for category in categories:
		subdirPath = os.path.join(inputDir, category)
		names = listDir(subdirPath)
		for filename in names:
			addSong(c, inputDir, category, filename)

def addSong(c, inputDir, category, filename):
	songname = filename.capitalize()
	if songname.endswith('.crd'):
		songname = songname[:-4]
	fullPath = os.path.join(inputDir, category, filename)
	fileContent = readFile(fullPath).encode('utf-8')
	categoryName = None if category == '0thers' else category.decode('utf-8')
	versionNumber = 1
	updateTime = time.mktime(NOW.timetuple())
	custom = 0
	# lock
	locked = 0
	lockPassword = None
	if category in ['Z jajem', 'BFF', 'Inżynier', 'Religijne']:
		locked = 1
		lockPassword = category.decode('utf-8')
	# content trim, comments read
	lines = splitLines(fileContent)
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
	# inserting record
	c.execute('SELECT MAX(id) AS id FROM songs')
	identifier = c.fetchone()[0]
	identifier = 1 if not identifier else identifier + 1
	c.execute('''INSERT INTO songs
		(id,
		fileContent, title, categoryName,
		versionNumber, updateTime,custom,filename,
		comment,preferredKey,locked,lockPassword)
		VALUES (?, ?, ?, ?,
		?, ?, ?, ?,
		?, ?, ?, ?);
		''', (identifier, fileContent.decode('utf-8'), songname.decode('utf-8'),
			categoryName,
			versionNumber, updateTime, custom, filename.decode('utf-8'),
			comment, preferredKey, locked, lockPassword))

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
