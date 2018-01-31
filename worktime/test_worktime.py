from worktime import *
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


def test_WorktimeRecord():
    worktime = WorktimeRecord.parse('2018-01-03', '9:21:42', '17:21:42')
    assert time2str(worktime.startTime, '%H:%M:%S, %Y-%m-%d') == '09:21:42, 2018-01-03'
    assert time2str(worktime.endTime, '%H:%M:%S, %Y-%m-%d') == '17:21:42, 2018-01-03'

def test_saveHoursDB():
    db = []
    db += [WorktimeRecord.parse('2018-01-03', '9:21:42', '17:21:42')]
    db += [WorktimeRecord.parse('2018-01-04', '9:21:42', '17:21:42')]
    db += [WorktimeRecord.parse('2018-01-05', '10:21:42', '17:21:42')]
    saveHoursDB('test/save-db', db)
    assert readFile('test/save-db') == u'2018-01-03\t09:21:42\t17:21:42\n2018-01-04\t10:21:42\t17:21:42\n2018-01-05\t09:21:42\t17:21:42\n'
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
    assert uptime(t1, t2) == '06 h 11 min 01 s'
    assert uptime(t2, t1) == '- 06 h 11 min 01 s'

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

def test_actionSetStartTime():
    global DB_FILE_PATH
    global now
    DB_FILE_PATH = 'test/hours-test'
    now = str2time('15:31:06, 1951-03-21', '%H:%M:%S, %Y-%m-%d')
    saveFile('test/hours-test', [])
    assert readFile(DB_FILE_PATH) == ''
    with mockArgs(['start', '9:07']), mockOutput() as out:
        main()
        assert readFile(DB_FILE_PATH) == '1951-03-21\t9:07:00\t15:31:06'

def test_actionSetStartTime_invalid():
    global DB_FILE_PATH
    global now
    DB_FILE_PATH = 'test/hours-test'
    now = str2time('15:31:06, 1951-03-21', '%H:%M:%S, %Y-%m-%d')
    saveFile('test/hours-test', [])
    assert readFile(DB_FILE_PATH) == ''
    with mockArgs(['start', 'dupa']), mockOutput() as out:
        assertError(lambda: main())

