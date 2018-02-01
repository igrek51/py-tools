#!/usr/bin/python
from glue import *

DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'
DATETIME_FORMAT = TIME_FORMAT + ', ' + DATE_FORMAT
now = time.localtime()
DB_FILE_PATH = 'hours'

class WorktimeRecord:
    def __init__(self, startTime, endTime):
        self.startTime = startTime
        self.endTime = endTime

    @staticmethod
    def parse(dateStr, startTimeStr, endTimeStr):
        date = str2time(dateStr, DATE_FORMAT)
        startTime = parseDatetime(startTimeStr, date)
        endTime = parseDatetime(endTimeStr, date)
        return WorktimeRecord(startTime, endTime)

    def __str__(self):
        date = time2str(self.startTime, DATE_FORMAT)
        startTime = time2str(self.startTime, TIME_FORMAT)
        endTime = time2str(self.endTime, TIME_FORMAT)
        return '%s\t%s\t%s' % (date, startTime, endTime)

def loadHoursDB(path):
    if not fileExists(path):
        warn('not existing db file: %s' % path)
        return []
    db = []
    linesRaw = readFile(path)
    for date, startTime, endTime in splitToTuples(linesRaw, 3, splitter='\t'):
        db.append(WorktimeRecord.parse(date, startTime, endTime))
    return db

def lastWorktime(db):
    if db:
        return db[-1]

def saveHoursDB(path, db):
    output = ''
    for record in db:
        output += str(record) + '\n'
    saveFile(path, output)

def parseDatetime(timeRaw, now):
    t = str2time(timeRaw, DATETIME_FORMAT)
    if not t:
        # HH:MM:SS - append today date
        timeRaw2 = timeRaw + ', ' + time2str(now, DATE_FORMAT)
        t = str2time(timeRaw2, DATETIME_FORMAT)
    if not t:
        # HH:MM - append today date and seconds
        timeRaw2 = timeRaw + ':00, ' + time2str(now, DATE_FORMAT)
        t = str2time(timeRaw2, DATETIME_FORMAT)
    if not t:
        # HH - append today date , minutes, seconds
        timeRaw2 = timeRaw + ':00:00, ' + time2str(now, DATE_FORMAT)
        t = str2time(timeRaw2, DATETIME_FORMAT)
    return t

def sameDay(time1, time2):
    if time1 is None or time2 is None:
        return False
    dayFormat = '%d.%m.%Y'
    return time2str(time1, dayFormat) == time2str(time2, dayFormat)

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


def updateTime(db):
    lastWork = lastWorktime(db)
    if not lastWork or not sameDay(lastWork.startTime, now): # no previous entry or from previous day
        info('Creating new worktime entry')
        lastWork = WorktimeRecord(now, now)
        db.append(lastWork)
    else:
        # update endTime
        lastWork.endTime = now
    return lastWork

def showUptime(lastWork):
    info('Start time: %s' % time2str(lastWork.startTime, DATETIME_FORMAT))
    info('Now:        %s' % time2str(now, DATETIME_FORMAT))
    info('Uptime:     %s' % uptime(lastWork.startTime, now))

# ----- Actions
def actionShowUptime(argsProcessor):
    dbPath = os.path.join(getScriptRealDir(), DB_FILE_PATH)
    db = loadHoursDB(dbPath)
    lastWork = updateTime(db)

    showUptime(lastWork)
    saveHoursDB(dbPath, db)

def actionSetStartTime(argsProcessor):
    dbPath = os.path.join(getScriptRealDir(), DB_FILE_PATH)
    db = loadHoursDB(dbPath)
    lastWork = updateTime(db)

    customTimeStr = argsProcessor.pollNextRequired('customTime')
    customTime = parseDatetime(customTimeStr, now)
    if not customTime:
        fatal('invalid date format: %s' % customTimeStr)
    lastWork.startTime = customTime

    showUptime(lastWork)
    saveHoursDB(dbPath, db)

def actionMonthReport(argsProcessor):
    pass


# ----- Main
def main():
    argsProcessor = ArgsProcessor('Worktime registering and reporting tool', '1.0.1')

    argsProcessor.bindCommand(actionShowUptime, 'uptime', description='show today uptime')
    argsProcessor.bindCommand(actionSetStartTime, 'start', description='save custom start time ("HH:MM:SS, YYYY-mm-dd", "HH:MM:SS" or "HH:MM")', syntaxSuffix='<customTime>')
    argsProcessor.bindCommand(actionMonthReport, 'month', description='show monthly report, month formats: YYYY-mm or mm', syntaxSuffix='[<month>]')
    argsProcessor.bindDefaultAction(actionShowUptime)

    argsProcessor.processAll()

if __name__ == '__main__': # for testing purposes
    main() # will not be invoked when importing this file