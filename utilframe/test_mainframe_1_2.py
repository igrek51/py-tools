from mainframe_1_2 import *

def test_output():
	debug('debug')
	info('info')
	warn('warn')
	error('error')

def test_shellExec():
	shellExec('echo test')
	assert shellExecErrorCode('echo test') == 0
	assert shellOutput('echo test') == 'test\n'

def test_splitLines():
	assert list(splitLines('a\nb\nc')) == ['a', 'b', 'c']
	assert list(splitLines('\na\n\n')) == ['a']
	assert list(splitLines('\n\n\n')) == []
	assert list(splitLines('')) == []
	assert list(splitLines('a\n\n\r\nb')) == ['a', 'b']

def test_split():
	assert split('a b c', ' ') == ['a', 'b', 'c']
	assert split('abc', ' ') == ['abc']
