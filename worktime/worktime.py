#!/usr/bin/python
from glue import *

DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'
MONTH_FORMAT = '%Y-%m'
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
    return db[-1] if db else None

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

def parseMonth(monthRaw, now):
    t = str2time(monthRaw, MONTH_FORMAT)
    if not t:
        # %mm or %m
        monthRaw2 = time2str(now, '%Y') + '-' + monthRaw
        t = str2time(monthRaw2, MONTH_FORMAT)
    return t

def parseDay(dayRaw, now):
    t = str2time(dayRaw, DATE_FORMAT) # YYYY-mm-dd
    if not t: # mm-dd
        dayRaw2 = time2str(now, '%Y') + '-' + dayRaw
        t = str2time(dayRaw2, DATE_FORMAT)
    if not t: # dd
        dayRaw2 = time2str(now, '%Y-%m') + '-' + dayRaw
        t = str2time(dayRaw2, DATE_FORMAT)
    return t

def sameDay(time1, time2):
    if time1 is None or time2 is None:
        return False
    dayFormat = '%Y-%m-%d'
    return time2str(time1, dayFormat) == time2str(time2, dayFormat)

def isBefore(before, after):
    return int(time.mktime(after) - time.mktime(before)) > 0

def elapsedSeconds(timeFrom, timeTo):
    return int(time.mktime(timeTo) - time.mktime(timeFrom))

def formatDuration(elapsedS):
    if elapsedS < 0:
        return '-' + formatDuration(-elapsedS)
    seconds = elapsedS % 60
    minutes = (elapsedS // 60) % 60
    hours = (elapsedS // 60 // 60)
    return '%d:%02d:%02d' % (hours, minutes, seconds)

def uptime(startTime, now):
    elapsedS = elapsedSeconds(startTime, now)
    if elapsedS < 0:
        warn('Elapsed time is less than 0')
    return formatDuration(elapsedS)


def updateTime(db):
    lastWork = lastWorktime(db)
    if not lastWork or not sameDay(lastWork.startTime, now): # no previous entry or from previous day
        info('Creating new worktime entry')
        lastWork = WorktimeRecord(now, now)
        db.append(lastWork)
    else:
        # update endTime
        if isBefore(lastWork.endTime, now):
            lastWork.endTime = now
    return lastWork

def showUptime(lastWork):
    info('Start time: %s' % time2str(lastWork.startTime, DATETIME_FORMAT))
    if now != lastWork.endTime:
        info('End time:   %s' % time2str(lastWork.endTime, DATETIME_FORMAT))
    info('Now:        %s' % time2str(now, DATETIME_FORMAT))
    elapsedS = elapsedSeconds(lastWork.startTime, lastWork.endTime)
    info('Uptime:     %s' % uptime(lastWork.startTime, lastWork.endTime))
    info('8h diff:    %s' % formatDuration(elapsedS - 8 * 3600))

def isDatetimeInRange(datetime, fromTime, toTime):
    if fromTime and toTime:
        return (not isBefore(datetime, fromTime)) and (not isBefore(toTime, datetime))
    elif fromTime:
        return not isBefore(datetime, fromTime)
    elif toTime:
        return not isBefore(toTime, datetime)
    else:
        return True

def endOfDay(datetime):
    endDayStr = time2str(datetime, DATE_FORMAT) + ', 23:59:59'
    return str2time(endDayStr, DATE_FORMAT + ', %H:%M:%S')

def setStartTimeDecorator(argsProcessor, lastWork):
    customTimeStr = argsProcessor.pollNextRequired('customStartTime')
    customTime = parseDatetime(customTimeStr, now)
    if not customTime:
        fatal('invalid date format: %s' % customTimeStr)
    lastWork.startTime = customTime

def setEndTimeDecorator(argsProcessor, lastWork):
    customTimeStr = argsProcessor.pollNextRequired('customEndTime')
    customTime = parseDatetime(customTimeStr, now)
    if not customTime:
        fatal('invalid date format: %s' % customTimeStr)
    lastWork.endTime = customTime

def getReportDateRange(argsProcessor):
    fromDateStr = argsProcessor.getParam('fromDate')
    fromDate = parseDay(fromDateStr, now) if fromDateStr else None
    toDateStr = argsProcessor.getParam('toDate')
    toDate = parseDay(toDateStr, now) if toDateStr else None
    return (fromDate, toDate)

def showReport(works):
    elapsedSum = 0
    for work in works:
        date = time2str(work.startTime, DATE_FORMAT)
        startTime = time2str(work.startTime, TIME_FORMAT)
        endTime = time2str(work.endTime, TIME_FORMAT)
        up = uptime(work.startTime, work.endTime)
        elapsedSum += elapsedSeconds(work.startTime, work.endTime)
        print('%s: %s - %s, uptime: %s' % (date, startTime, endTime, up))
    # summary
    recordsCount = len(works)
    info('Days: %d' % recordsCount)
    if recordsCount > 0:
        info('Sum: %s' % formatDuration(elapsedSum))
        info('Avg: %s' % formatDuration(elapsedSum // recordsCount))
        info('avg8h diff: %s' % formatDuration(elapsedSum - recordsCount * 8 * 3600))

def daysRangeWorksFilter(db, argsProcessor):
    fromDate, toDate = getReportDateRange(argsProcessor)
    # complete missing date ranges
    if toDate:
        toDate = endOfDay(toDate)
    fromDateStr = time2str(fromDate, DATE_FORMAT) if fromDate else None
    toDateStr = time2str(toDate, DATE_FORMAT) if toDate else None
    info('Report for date range: %s - %s' % (fromDateStr, toDateStr))
    return list(filter(lambda w: isDatetimeInRange(w.startTime, fromDate, toDate), db))

def monthWorksFilter(db, argsProcessor):
    if argsProcessor.hasNext():
        reportMonthTime = parseMonth(argsProcessor.pollNext(), now)
        reportMonth = time2str(reportMonthTime, MONTH_FORMAT)
    else:
        reportMonth = time2str(now, MONTH_FORMAT)
    info('Monthly report for: %s' % reportMonth)
    return list(filter(lambda w: time2str(w.startTime, MONTH_FORMAT) == reportMonth, db))

def allWorksFilter(db, argsProcessor):
    info('All records report:')
    return db

def reportDays(argsProcessor, worksFilter):
    dbPath = os.path.join(getScriptRealDir(), DB_FILE_PATH)
    db = loadHoursDB(dbPath)
    if argsProcessor.isFlag('update'):
        updateTime(db)
        saveHoursDB(dbPath, db)

    works = worksFilter(db, argsProcessor)

    showReport(works)

# ----- Actions
def actionShowUptime(argsProcessor, decorator=None):
    dbPath = os.path.join(getScriptRealDir(), DB_FILE_PATH)
    db = loadHoursDB(dbPath)
    lastWork = updateTime(db)

    if decorator:
        decorator(argsProcessor, lastWork)

    showUptime(lastWork)
    saveHoursDB(dbPath, db)

def actionSetStartTime(argsProcessor):
    actionShowUptime(argsProcessor, setStartTimeDecorator)

def actionSetEndTime(argsProcessor):
    actionShowUptime(argsProcessor, setEndTimeDecorator)

def actionReport(argsProcessor):
    (fromDate, toDate) = getReportDateRange(argsProcessor)
    if fromDate or toDate:
        reportDays(argsProcessor, daysRangeWorksFilter)
    elif argsProcessor.hasNext():
        reportType = argsProcessor.pollNext()
        if reportType == 'month':
            reportDays(argsProcessor, monthWorksFilter)
        elif reportType == 'all':
            reportDays(argsProcessor, allWorksFilter)
        else:
            fatal('unknown report type: %s' % reportType)
    else:
        reportDays(argsProcessor, monthWorksFilter)

def actionEdit(argsProcessor):
    editor = argsProcessor.pollRemainingJoined(' ')
    if not editor:
        fatal('no editor given')
    # open in external editor
    dbPath = os.path.join(getScriptRealDir(), DB_FILE_PATH)
    shellExec(editor + ' ' + dbPath)

# ----- Main
def main():
    ap = ArgsProcessor('Worktime registering and reporting tool', '1.1.0')

    ap.bindDefaultAction(actionShowUptime)
    ap.bindCommand(actionShowUptime, 'uptime', description='show today uptime')
    ap.bindCommand(actionSetStartTime, 'start', description='save custom start time ("HH:MM:SS", "HH:MM" or "HH")', syntaxSuffix='<customStartTime>')
    ap.bindCommand(actionSetEndTime, 'end', description='save custom end time ("HH:MM:SS", "HH:MM" or "HH")', syntaxSuffix='<customEndTime>')
    ap.bindCommand(actionReport, ['report', 'r'], description='show current month report')
    ap.bindCommand(actionReport, 'report', description='show monthly report, month formats: YYYY-mm or mm', syntaxSuffix='month [<month>]')
    ap.bindCommand(actionReport, 'report', description='show all records report', syntaxSuffix='all')
    ap.bindCommand(actionEdit, 'edit', syntaxSuffix='<editor>', description='open db in external editor')
    ap.bindFlag('update', syntax=['-u', '--update'], description='update last end time')
    ap.bindParam('fromDate', syntax='--from', description='set report starting date ("YYYY-mm-dd", "mm-dd" or "dd")')
    ap.bindParam('toDate', syntax='--to', description='set report ending date ("YYYY-mm-dd", "mm-dd" or "dd")')

    ap.processAll()

if __name__ == '__main__': # for testing purposes
    main() # will not be invoked when importing this file