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

def test_regexReplace():
	assert regexReplace('abca', 'a', 'b') == 'bbcb'
	assert regexReplace('abc123a', r'\d', '5') == 'abc555a'

def test_regexMatch():
	assert regexMatch('ab 12 def 123', r'.*\d{2}')
	assert not regexMatch('ab 1 def 1m2', r'.*\d{2}.*')

def test_regex_lines():
	# regexReplaceLines
	assert regexReplaceLines(['a', 'b', '25', 'c'], r'\d+', '7') == ['a', 'b', '7', 'c']
	assert regexReplaceLines(['a1', '2b', '3', ''], r'\d', '7') == ['a7', '7b', '7', '']
	assert regexReplaceLines(['a1', '2b', '3', ''], r'.*\d.*', '7') == ['7', '7', '7', '']
	# regexFilterLines
	assert regexFilterLines(['a1', '2b', '3', ''], r'.*\d.*') == ['a1', '2b', '3']
	assert regexFilterLines(['a1', '2b', '3', ''], r'dupa') == []
	# regexSearchFile
	assert regexSearchFile('test/res/findme', r'\t*<author>(\w*)</author>', 1) == 'Anonim'
	assert regexSearchFile('test/res/findme', r'\t*<name>(\w*)</name><sur>(\w*)</sur>', 2) == 'Sur'

def test_input23():
	sys.stdin = open('test/res/inputs')
	assert input23() == 'in1'
	assert input23('prompt') == 'in2'