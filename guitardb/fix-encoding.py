#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os
import codecs

class Main(object):

	def __init__(self):
		self.rootdir = '.'
		self.convertFiles = []
		self.encodings = ['utf-8', 'windows-1250']

	def start(self):
		self._findFiles()
		self._convertFiles()

	def _findFiles(self):
		for subdir, dirs, files in os.walk(self.rootdir):
			for file in files:
				filePath = os.path.join(subdir, file)
				if self._isValid(filePath):
					self.convertFiles.append(filePath)

	def _isValid(self, filePath):
		# skip .git folder
		if os.path.split(filePath)[0].startswith('./.'):
			return False

		ext = os.path.splitext(filePath)[-1]
		if len(ext) > 0:
			return ext == '.crd'
		return False

	def _convertFiles(self):
		for filePath in self.convertFiles:
			self._convertFile(filePath)

	def _convertFile(self, filePath):
		# read content
		file = open(filePath, 'r')
		content = file.read()
		file.close()

		# decode and get encoding
		(decoded, encoding) = self._decode(content)

		# skip utf8 files
		if encoding == 'utf-8':
			return
		print("%s - %s" % (filePath, encoding))
		# print(decoded.encode('utf-8'))

		# save to file with UTF8 encoding
		file = codecs.open(filePath, "w", "utf-8")
		file.write(decoded)
		file.close()

	def _decode(self, str):
		for enc in self.encodings:
			try:
				str = str.decode(enc)
				return (str, enc)
			except Exception as e:
				pass
		return (str, None)

Main().start()