from dailyuptime import *
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

def test_readLastTime():
    assert readLastTime('test/res/notexisting') is None
    assert readLastTime('test/res/empty') is None
    assert readLastTime('test/res/sample') is not None

def test_saveNewTime():
    sample = readLastTime('test/res/sample')
    saveNewTime(sample, 'test/res/copy')
    copy = readLastTime('test/res/copy')
    assert sample == copy

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

def test_parseDatetimeOrTime():
    PATTERN = '%H:%M:%S, %d.%m.%Y'
    now = str2time('15:31:06, 21.03.1951', PATTERN)
    t = parseDatetimeOrTime('12:01:05, 01.02.1985', now)
    assert time2str(t, PATTERN) == '12:01:05, 01.02.1985'
    t = parseDatetimeOrTime('12:01:05', now)
    assert time2str(t, PATTERN) == '12:01:05, 21.03.1951'
    t = parseDatetimeOrTime('12:07', now)
    assert time2str(t, PATTERN) == '12:07:00, 21.03.1951'
    t = parseDatetimeOrTime('9:07', now)
    assert time2str(t, PATTERN) == '09:07:00, 21.03.1951'

def test_createStart():
    setWorkdir('test/res/')
    if fileExists('start'):
        shellExec('rm start')
    with mockArgs(None), mockOutput() as out:
        start()
        assert readLastTime('start') is not None
        assert 'not existing file: start' in out.getvalue()
    setWorkdir('../..')

def test_setIOFile():
    setWorkdir('test/res/')
    if fileExists('iofile'):
        shellExec('rm iofile')
    with mockArgs(['--file', 'iofile']), mockOutput() as out:
        start()
        assert readLastTime('iofile') is not None
        assert 'not existing file: iofile' in out.getvalue()
        shellExec('rm iofile')
    setWorkdir('../..')
    with mockArgs(['--file', 'test/res/iofile']), mockOutput() as out:
        start()
        assert readLastTime('test/res/iofile') is not None
        assert 'not existing file: test/res/iofile' in out.getvalue()

def test_setCustomDate():
    with mockArgs(['--file', 'test/res/custom', '--set', '9:07']), mockOutput() as out:
        start()
        assert time2str(readLastTime('test/res/custom'), '%H:%M') == '09:07'

def test_setCustomDate_invalid():
    with mockArgs(['--file', 'test/res/custom', '--set', 'dupa']), mockOutput() as out:
        assertError(lambda: start())



