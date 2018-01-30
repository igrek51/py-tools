#!/usr/bin/python
from glue import *

DATETIME_FORMAT = '%H:%M:%S, %d.%m.%Y'
now = time.localtime()

def loadHoursDB(path):
	pass

def saveHoursDB(path):
	saveFile(filename, formatTime(datetime))
	pass

def _readStartTime(filename):
	if not fileExists(filename):
		warn('not existing file: %s' % filename)
		return None
	content = readFile(filename).strip()
	try:
		return time.strptime(content, DATETIME_FORMAT)
	except ValueError as e:
		warn(str(e))
		return None

def sameDay(time1, time2):
	if time1 is None or time2 is None:
		return False
	dayFormat = '%d.%m.%Y'
	return time2str(time1, dayFormat) == time2str(time2, dayFormat)

def formatTime(datetime):
	return time2str(datetime, DATETIME_FORMAT)

def uptime(startTime, now):
	elapsedS = int(time.mktime(now) - time.mktime(startTime))
	if elapsedS < 0:
		warn('Elapsed time is less than 0')
		return '- ' + uptime(now, startTime)
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
	t = str2time(timeRaw, DATETIME_FORMAT)
	dateSuffixFormat = ', %d.%m.%Y'
	if not t:
		# only time check - append today date
		timeRaw2 = timeRaw + time2str(now, dateSuffixFormat)
		t = str2time(timeRaw2, DATETIME_FORMAT)
	if not t:
		# only time check - append today date and seconds
		timeRaw2 = timeRaw + ':00' + time2str(now, dateSuffixFormat)
		t = str2time(timeRaw2, DATETIME_FORMAT)
	return t

def updateTime():
	pass

def showUptime():
	pass

# ----- Actions
def actionShowUptime(argsProcessor):
	filename = os.path.join(getScriptRealDir(), 'hours')

	startTime = None
	customtime = None

	if customtime: # custom time set
		# try to get datetime or time only with today date
		saveNewTime(customtime, filename)
		info('Previous start time: %s' % formatTime(startTime))
		info('Custom time saved:   %s' % formatTime(customtime))
		info('Now:                 %s' % formatTime(now))
		info('Uptime:              %s' % uptime(customtime, now))
	elif sameDay(startTime, now):
		# show start datetime
		info('Start time: %s' % formatTime(startTime))
		info('Now:        %s' % formatTime(now))
		info('Uptime:     %s' % uptime(startTime, now))
	else:
		# save new day
		# saveNewTime(now, filename)
		info('Previous start time:  %s' % formatTime(startTime))
		info('New start time (now): %s' % formatTime(now))

def actionSetStartTime(argsProcessor):
	customtime = argsProcessor.getParam('customTime')
	pass

def actionMonthReport(argsProcessor):
	pass


# ----- Main
def main():
	argsProcessor = ArgsProcessor('Worktime registering and reporting tool', '1.0.1')

	argsProcessor.bindCommand(actionSetStartTime, 'start', description='save custom start time ("HH:MM:SS, dd.mm.YYYY", "HH:MM:SS" or "HH:MM")', syntaxSuffix='[<customTime>]')
	argsProcessor.bindCommand(actionMonthReport, 'month', description='show monthly report, month formats: RRRR-MM or MM', syntaxSuffix='[<month>]')
	argsProcessor.bindDefaultAction(actionShowUptime)

	argsProcessor.processAll()

if __name__ == '__main__': # for testing purposes
	main() # will not be invoked when importing this file