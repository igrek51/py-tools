#!/usr/bin/python
from glue import *

LAST_TIME_FILENAME_DEFAULT = 'start'
LAST_DATETIME_FORMAT = '%H:%M:%S, %d.%m.%Y'
DATE_SUFFIX_FORMAT = ', %d.%m.%Y'
lastTime = None
now = time.localtime()

def readLastTime(filename):
	if not os.path.isfile(filename):
		warn('not existing file: %s' % filename)
		return None
	content = readFile(filename).strip()
	try:
		return time.strptime(content, LAST_DATETIME_FORMAT)
	except ValueError as e:
		warn(str(e))
		return None

def saveNewTime(datetime, filename):
	saveFile(filename, formatTime(datetime))

def sameDay(time1, time2):
	if time1 is None or time2 is None:
		return False
	dayFormat = '%d.%m.%Y'
	return time2str(time1, dayFormat) == time2str(time2, dayFormat)

def formatTime(datetime):
	return time2str(datetime, LAST_DATETIME_FORMAT)

def uptime(lastTime, now):
	elapsedS = int(time.mktime(now) - time.mktime(lastTime))
	if elapsedS < 0:
		warn('Elapsed time is less than 0')
		return '- ' + uptime(now, lastTime)
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

def parseDatetimeOrTime(timeRaw, now):
	t = str2time(timeRaw, LAST_DATETIME_FORMAT)
	if not t:
		# only time check - append today date
		timeRaw2 = timeRaw + time2str(now, DATE_SUFFIX_FORMAT)
		t = str2time(timeRaw2, LAST_DATETIME_FORMAT)
	if not t:
		# only time check - append today date and seconds
		timeRaw2 = timeRaw + ':00' + time2str(now, DATE_SUFFIX_FORMAT)
		t = str2time(timeRaw2, LAST_DATETIME_FORMAT)
	return t

# ----- Commands and options
def optionSetCustomTime(argsProcessor):
	# setting custom time
	customtimeRaw = argsProcessor.pollNextRequired('customtime')
	# try to get datetime or time only with today date
	customTime = parseDatetimeOrTime(customtimeRaw, now)
	if not customTime:
		fatal('Invalid time format: %s' % customtimeRaw)
	argsProcessor.setParam('customtime', customTime)

def actionSaveTime(argsProcessor):
	filename = LAST_TIME_FILENAME_DEFAULT
	if argsProcessor.getParam('io-file'):
		filename = argsProcessor.getParam('io-file')

	lastTime = readLastTime(filename)
	customtime = argsProcessor.getParam('customtime')

	if customtime: # custom time set
		# try to get datetime or time only with today date
		saveNewTime(customtime, filename)
		info('Previous start time: %s' % formatTime(lastTime))
		info('Custom time saved:   %s' % formatTime(customtime))
		info('Now:                 %s' % formatTime(now))
		info('Uptime:              %s' % uptime(customtime, now))

	elif sameDay(lastTime, now):
		# show start datetime
		info('Start time: %s' % formatTime(lastTime))
		info('Now:        %s' % formatTime(now))
		info('Uptime:     %s' % uptime(lastTime, now))
		
	else:
		# save new day
		saveNewTime(now, filename)
		info('Previous start time:  %s' % formatTime(lastTime))
		info('New start time (now): %s' % formatTime(now))

# ----- Main
def start():
	argsProcessor = ArgumentsProcessor('Daily uptime registering tool', '1.0.1')

	argsProcessor.bindParam('io-file', ['-f', '--file'], description='last time datafile ("%s" by default)' % LAST_TIME_FILENAME_DEFAULT)
	argsProcessor.bindOption(optionSetCustomTime, ['-s', '--set'], description='save custom time ("HH:MM:SS, dd.mm.YYYY" or "HH:MM:SS" or "HH:MM")', syntaxSuffix='<customtime>')
	argsProcessor.bindDefaultAction(actionSaveTime)
	argsProcessor.bindDefaults()

	argsProcessor.processAll()

if __name__ == '__main__': # for debugging by importing module
	start()
