from worktime import *
import worktime # for overwriting global variables
from mock import patch
# import StringIO (Python 2 and 3 compatible)
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

def assertError(action, expectedError=None):
    try:
        action()
        assert False
    except RuntimeError as e:
        if expectedError:
            assert str(e) == expectedError

def assertSystemExit(action):
    try:
        action()
        assert False
    except SystemExit as e:
        # exit with error code 0
        assert str(e) == '0'

def mockArgs(argsList):
    if not argsList:
        argsList = []
    return patch.object(sys, 'argv', ['glue'] + argsList)

def mockOutput():
    return patch('sys.stdout', new=StringIO())

def recode(string):
    return string.encode().decode() # wtf - encoding special chars


def test_WorktimeRecord():
    work = WorktimeRecord.parse('2018-01-03', '9:21:42', '17:21:42')
    assert time2str(work.startTime, '%H:%M:%S, %Y-%m-%d') == '09:21:42, 2018-01-03'
    assert time2str(work.endTime, '%H:%M:%S, %Y-%m-%d') == '17:21:42, 2018-01-03'

def test_saveHoursDB():
    db = []
    db += [WorktimeRecord.parse('2018-01-03', '9:21:42', '17:21:42')]
    db += [WorktimeRecord.parse('2018-01-04', '10:21:42', '17:21:42')]
    db += [WorktimeRecord.parse('2018-01-05', '9:21:42', '17:21:42')]
    saveHoursDB('test/save-db', db)
    expected = '2018-01-03\t09:21:42\t17:21:42\n2018-01-04\t10:21:42\t17:21:42\n2018-01-05\t09:21:42\t17:21:42\n'
    assert readFile('test/save-db') == expected
    db = []
    saveHoursDB('test/save-db', db)
    assert readFile('test/save-db') == ''

def test_sameDay():
    t1 = str2time('12:20:05, 21.03.1951', '%H:%M:%S, %d.%m.%Y')
    t2 = str2time('12:20:05, 22.03.1951', '%H:%M:%S, %d.%m.%Y')
    t3 = str2time('16:18:55, 21.03.1951', '%H:%M:%S, %d.%m.%Y')
    assert sameDay(t1, t3)
    assert sameDay(t3, t1)
    assert not sameDay(t1, t2)
    assert not sameDay(t2, t3)
    assert not sameDay(None, t1)
    assert not sameDay(t1, None)
    assert not sameDay(None, None)

def test_uptime():
    t1 = str2time('9:20:05, 21.03.1951', '%H:%M:%S, %d.%m.%Y')
    t2 = str2time('15:31:06, 21.03.1951', '%H:%M:%S, %d.%m.%Y')
    assert uptime(t1, t2) == '6:11:01'
    assert uptime(t2, t1) == '-6:11:01'

def test_parseDatetime():
    PATTERN = '%H:%M:%S, %Y-%m-%d'
    now = str2time('15:31:06, 1951-03-21', PATTERN)
    t = parseDatetime('12:01:05, 1985-02-01', now)
    assert time2str(t, PATTERN) == '12:01:05, 1985-02-01'
    t = parseDatetime('12:01:05', now)
    assert time2str(t, PATTERN) == '12:01:05, 1951-03-21'
    t = parseDatetime('12:07', now)
    assert time2str(t, PATTERN) == '12:07:00, 1951-03-21'
    t = parseDatetime('9:07', now)
    assert time2str(t, PATTERN) == '09:07:00, 1951-03-21'
    t = parseDatetime('9', now)
    assert time2str(t, PATTERN) == '09:00:00, 1951-03-21'

def test_actionShowUptime():
    worktime.DB_FILE_PATH = 'test/hours-test'
    worktime.now = str2time('15:31:06, 1951-03-21', '%H:%M:%S, %Y-%m-%d')
    # new record
    dbTxt = recode('1951-03-21\t09:01:00\t14:02:03\n')
    saveFile(worktime.DB_FILE_PATH, dbTxt)
    with mockArgs([]), mockOutput() as out:
        assert worktime.DB_FILE_PATH == 'test/hours-test'
        assert readFile(worktime.DB_FILE_PATH) == dbTxt
        worktime.main()
        assert readFile(worktime.DB_FILE_PATH) == recode('1951-03-21\t09:01:00\t15:31:06\n')
    # new file
    shellExec('rm %s' % worktime.DB_FILE_PATH)
    with mockArgs([]), mockOutput() as out:
        worktime.main()
        assert readFile(worktime.DB_FILE_PATH) == recode('1951-03-21\t15:31:06\t15:31:06\n')
    # next day
    saveFile(worktime.DB_FILE_PATH, '1951-03-19\t11:01:00\t14:02:03\n')
    with mockArgs([]), mockOutput() as out:
        worktime.main()
        assert readFile(worktime.DB_FILE_PATH) == recode('1951-03-19\t11:01:00\t14:02:03\n1951-03-21\t15:31:06\t15:31:06\n')
    # update end time
    worktime.now = str2time('16:33:08, 1951-03-21', '%H:%M:%S, %Y-%m-%d')
    saveFile(worktime.DB_FILE_PATH, '1951-03-21\t11:01:00\t14:02:03\n')
    with mockArgs([]), mockOutput() as out:
        worktime.main()
        assert readFile(worktime.DB_FILE_PATH) == recode('1951-03-21\t11:01:00\t16:33:08\n')
        assert 'Start time: 11:01:00, 1951-03-21' in out.getvalue()
        assert 'Now:        16:33:08, 1951-03-21' in out.getvalue()
        assert 'Uptime:     5:32:08' in out.getvalue()

def test_actionSetStartTime():
    worktime.DB_FILE_PATH = 'test/hours-test'
    worktime.now = str2time('15:31:06, 1951-03-21', '%H:%M:%S, %Y-%m-%d')
    saveFile(worktime.DB_FILE_PATH, '1951-03-21\t09:01:00\t14:02:03\n')
    with mockArgs(['start', '10:01']), mockOutput() as out:
        worktime.main()
        assert readFile(worktime.DB_FILE_PATH) == recode('1951-03-21\t10:01:00\t15:31:06\n')
        assert 'Uptime:     5:30:06' in out.getvalue()
    saveFile(worktime.DB_FILE_PATH, '1951-03-21\t09:01:00\t14:02:03\n')
    with mockArgs(['start', 'dupa']), mockOutput() as out:
        assertError(lambda: worktime.main())

def test_parseMonth():
    PATTERN = '%Y-%m'
    now = str2time('1951-07', PATTERN)
    assert time2str(parseMonth('2017-06', now), PATTERN) == '2017-06'
    assert time2str(parseMonth('06', now), PATTERN) == '1951-06'
    assert time2str(parseMonth('6', now), PATTERN) == '1951-06'

def test_actionMonthReport():
    worktime.DB_FILE_PATH = 'test/hours-test'
    worktime.now = str2time('15:31:06, 1951-03-21', '%H:%M:%S, %Y-%m-%d')
    dbTxt = '1951-03-21\t09:01:00\t15:02:00\n1951-03-22\t09:01:00\t17:02:00\n1951-04-21\t09:01:00\t14:02:03\n'
    saveFile(worktime.DB_FILE_PATH, dbTxt)
    with mockArgs(['month']), mockOutput() as out:
        worktime.main()
        assert 'Monthly report for: 1951-03' in out.getvalue()
        assert 'Days: 2' in out.getvalue()
        assert 'Sum: 14:02:00' in out.getvalue()
        assert 'Avg: 7:01:00' in out.getvalue()
        assert 'avg8h diff: -1:58:00' in out.getvalue()
    # custom month
    with mockArgs(['month', '03']), mockOutput() as out:
        worktime.main()
        assert 'Monthly report for: 1951-03' in out.getvalue()


