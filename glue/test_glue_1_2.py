from glue_1_2 import *
from mock import patch

def test_output():
    debug('debug')
    info('info')
    warn('warn')
    error('error')

def test_fatal():
    try:
        fatal('fatality')
        assert False
    except Exception:
        assert True

def test_shellExec():
    shellExec('echo test')
    try:
        shellExec('dupafatality')
        assert False
    except Exception:
        assert True
    assert shellExecErrorCode('echo test') == 0
    assert shellOutput('echo test') == 'test\n'

def test_splitLines():
    assert splitLines('a\nb\nc') == ['a', 'b', 'c']
    assert splitLines('\na\n\n') == ['a']
    assert splitLines('\n\n\n') == []
    assert splitLines('') == []
    assert splitLines('a\n\n\r\nb') == ['a', 'b']

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

def test_inputRequired():
    sys.stdin = open('test/res/inputRequired')
    assert inputRequired('required: ') == 'valid'

def test_readFile():
    assert readFile('test/res/readme') == 'Readme\n123'

def test_saveFile():
    saveFile('test/res/saveme', 'dupa\n123')
    assert readFile('test/res/saveme') == 'dupa\n123'
    saveFile('test/res/saveme', '')
    assert readFile('test/res/saveme') == ''

def test_listDir():
    assert listDir('test/res/listme') == ['afile', 'dir', 'zlast', 'zlastdir']

def test_workdir():
    setWorkdir('/')
    assert getWorkdir() == '/'
    setWorkdir('/home/')
    assert getWorkdir() == '/home'

def test_filterList():
    assert filterList(lambda e: len(e) <= 3, ['a', '123', '12345']) == ['a', '123']

# CommandArgRule
def test_CommandArgRule():
    assert CommandArgRule(True, None, 'name', 'description', 'syntaxSuffix').displayNames() == 'name'
    assert CommandArgRule(True, None, ['name1', 'name2'], 'description', 'syntaxSuffix').displayNames() == 'name1, name2'
    assert CommandArgRule(True, None, ['name1', 'name2'], 'description', None).displaySyntax() == 'name1, name2'
    assert CommandArgRule(True, None, ['name1', 'name2'], 'description', '<suffix>').displaySyntax() == 'name1, name2 <suffix>'
    assert CommandArgRule(True, None, ['name1', 'name2'], 'description', ' <suffix>').displaySyntax() == 'name1, name2 <suffix>'
    assert CommandArgRule(True, None, ['name'], 'description', None).displayHelp(5) == 'name  - description'
    assert CommandArgRule(True, None, ['name'], 'description', None).displayHelp(3) == 'name - description'
    assert CommandArgRule(True, None, ['name'], 'description', '<suffix>').displayHelp(3) == 'name <suffix> - description'
    assert CommandArgRule(True, None, ['name'], 'description', '<s>').displayHelp(10) == 'name <s>   - description'

# ArgumentsProcessor
def mockArgs(argsList):
    if not argsList:
        argsList = []
    return patch.object(sys, 'argv', ['glue'] + argsList)

def command1():
    print(None)

def command2(argsProcessor):
    print('dupa')

def test_ArgumentsProcessor():
    # basic execution with no args
    with mockArgs(None):
        try:
            argsProcessor = ArgumentsProcessor('appName', '1.0.1')
            argsProcessor.processAll()
            assert False
        except SystemExit:
            # prints help and exit
            assert True

    with mockArgs(None):
        try:
            argsProcessor = ArgumentsProcessor('appName', '1.0.1')
            argsProcessor.bindCommand(command1, 'command1', description='description1')
            argsProcessor.bindCommand(command2, ['command2', 'command22'], description='description2', syntaxSuffix='<param>')
            argsProcessor.bindOption(printHelp, ['-h', '--help'], description='display this help and exit')
            argsProcessor.bindOption(printVersion, ['-v', '--version'], description='print version and exit')
            argsProcessor.processAll()
            assert False
        except SystemExit:
            # prints help and exit
            assert True
    

