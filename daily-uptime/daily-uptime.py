#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os
import time

# Console text formatting characters
class Colouring:
	C_RESET = '\033[0m'
	C_BOLD = '\033[1m'
	C_DIM = '\033[2m'
	C_ITALIC = '\033[3m'
	C_UNDERLINE = '\033[4m'

	C_BLACK = 0
	C_RED = 1
	C_GREEN = 2
	C_YELLOW = 3
	C_BLUE = 4
	C_MAGENTA = 5
	C_CYAN = 6
	C_WHITE = 7

	def textColor(colorNumber):
		return '\033[%dm' % (30 + colorNumber)

	def backgroundColor(colorNumber):
		return '\033[%dm' % (40 + colorNumber)

	C_INFO = textColor(C_BLUE) + C_BOLD
	C_WARN = textColor(C_YELLOW) + C_BOLD
	C_ERROR = textColor(C_RED) + C_BOLD

T_INFO = Colouring.C_INFO + '[info]' + Colouring.C_RESET
T_WARN = Colouring.C_WARN + '[warn]' + Colouring.C_RESET
T_ERROR = Colouring.C_ERROR + '[ERROR]' + Colouring.C_RESET

def info(message):
	print(T_INFO + " " + message)

def warn(message):
	print(T_WARN + " " + message)

def error(message):
	print(T_ERROR + " " + message)

	
LAST_TIME_FILENAME = 'start'
LAST_TIME_FORMAT = '%H:%M:%S, %d.%m.%Y'
lastTime = None

def start():
	lastTime = readLastTime()
	now = time.localtime()

	if sameDay(lastTime, now):
		# show start datetime
		info('Start time: %s' % time2str(lastTime))
		info('Now:        %s' % time2str(now))
		# show uptime
		info('Uptime:     %s' % uptime(lastTime, now))
		
	else:
		# save new day
		saveNewTime(now)
		info('Previous start time:  %s' % time2str(lastTime))
		info('New start time (now): %s' % time2str(now))


def readLastTime():
	if not os.path.isfile(LAST_TIME_FILENAME):
		warn('not existing file: %s' % LAST_TIME_FILENAME)
		return None
	with open(LAST_TIME_FILENAME) as file:
		content = file.read().strip()
		try:
			datetime = time.strptime(content, LAST_TIME_FORMAT)
			return datetime
		except ValueError as e:
			warn(str(e))
			return None

def saveNewTime(datetime):
	with open(LAST_TIME_FILENAME, 'w') as file:
		file.write(time2str(datetime))

def sameDay(time1, time2):
	if time1 is None or time2 is None:
		return False
	dayFormat = '%d.%m.%Y'
	return time.strftime(dayFormat, time1) == time.strftime(dayFormat, time2)

def time2str(datetime):
	if not datetime:
		return None
	return time.strftime(LAST_TIME_FORMAT, datetime)

def uptime(lastTime, now):
	elapsedS = int(time.mktime(now) - time.mktime(lastTime))
	seconds = elapsedS % 60
	minutes = (elapsedS // 60) % 60
	hours = (elapsedS // 60 // 60)
	# build elapsed time string
	elapsed = ''
	if hours > 0:
		elapsed += '%02d h ' % hours
	if minutes > 0 or hours > 0:
		elapsed += '%02d min ' % minutes
	elapsed += '%02d s' % seconds
	return elapsed

start()
