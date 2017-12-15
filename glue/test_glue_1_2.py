from glue_1_2 import *
from mock import patch
# import StringIO (Python 2 and 3 compatible)
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

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

def mockOutput():
    return patch('sys.stdout', new=StringIO())

def command1():
    print(None)

def command2(argsProcessor):
    param = argsProcessor.pollNextRequired('param')
    print(param)
    return param

def command3(argsProcessor):
    param = argsProcessor.peekNext()
    if not param:
        assert not argsProcessor.hasNext()
    param2 = argsProcessor.pollNext()
    assert param == param2
    print(param)

def command4Remaining(argsProcessor):
    print(argsProcessor.pollRemaining())

def command5Poll(argsProcessor):
    while(argsProcessor.hasNext()):
        print(argsProcessor.pollNext())

def sampleProcessor1():
    argsProcessor = ArgumentsProcessor('appName', '1.0.1')
    argsProcessor.bindCommand(command1, 'command1', description='description1')
    argsProcessor.bindCommand(command2, ['command2', 'command22'], description='description2', syntaxSuffix='<param>')
    argsProcessor.bindCommand(command3, ['command3', 'command33'], description='description2', syntaxSuffix='<param>')
    argsProcessor.bindCommand(command4Remaining, 'remain', description='description4', syntaxSuffix='<param>')
    argsProcessor.bindCommand(command5Poll, 'poll', description='description5')
    argsProcessor.bindOption(printHelp, ['-h', '--help'], description='display this help and exit')
    argsProcessor.bindOption(printVersion, ['-v', '--version'], description='print version and exit')
    argsProcessor.bindOption(command4Remaining, '--remain', description='join strings')
    return argsProcessor

def test_ArgumentsProcessor_noArg():
    # basic execution with no args
    with mockArgs(None):
        try:
            argsProcessor = ArgumentsProcessor('appName', '1.0.1')
            argsProcessor.processAll()
            assert False
        except SystemExit as e:
            # prints help and exit
            assert str(e) == '0'

def test_ArgumentsProcessor_bindingsSetup():
    # test bindings
    with mockArgs(None):
        try:
            sampleProcessor1().processAll()
            assert False
        except SystemExit as e:
            # prints help and exit
            assert str(e) == '0'

def test_ArgumentsProcessor_optionsFirst():
    # test processing options first
    with mockArgs(['-h', 'dupa']):
        try:
            sampleProcessor1().processAll()
            assert False
        except SystemExit as e:
            # prints help and exit
            assert str(e) == '0'

def test_ArgumentsProcessor_noNextArg():
    # test lack of next argument
    with mockArgs(['command2']):
        try:
            sampleProcessor1().processAll()
            assert False
        except RuntimeError as e:
            # prints help and exit
            assert str(e) == 'Fatal error: no param parameter given'
    with mockArgs(['command33']):
        with mockOutput() as fakeOutput:
            sampleProcessor1().processAll()
            assert fakeOutput.getvalue() == 'None\n'

def test_ArgumentsProcessor_givenParam():
    # test given param
    with mockArgs(['command3', 'dupa']):
        with mockOutput() as fakeOutput:
            sampleProcessor1().processAll()
            assert fakeOutput.getvalue() == 'dupa\n'
    with mockArgs(['command2', 'dupa']):
        with mockOutput() as fakeOutput:
            sampleProcessor1().processAll()
            assert fakeOutput.getvalue() == 'dupa\n'

def test_ArgumentsProcessor_binding():
    # test binding with no argProcessor
    with mockArgs(['command1']):
        with mockOutput() as fakeOutput:
            sampleProcessor1().processAll()
            assert fakeOutput.getvalue() == 'None\n'

def test_ArgumentsProcessor_pollRemaining():
    # test pollRemaining():
    with mockArgs(['remain']):
        with mockOutput() as fakeOutput:
            sampleProcessor1().processAll()
            assert fakeOutput.getvalue() == '\n'
    with mockArgs(['remain', '1']):
        with mockOutput() as fakeOutput:
            sampleProcessor1().processAll()
            assert fakeOutput.getvalue() == '1\n'
    with mockArgs(['remain', '1', 'abc', 'd']):
        with mockOutput() as fakeOutput:
            sampleProcessor1().processAll()
            assert fakeOutput.getvalue() == '1 abc d\n'

def test_ArgumentsProcessor_optionsPrecedence():
    # test options precedence
    with mockArgs(['-v', 'command1']):
        with mockOutput() as fakeOutput:
            sampleProcessor1().processAll()
            assert fakeOutput.getvalue() == 'appName v1.0.1\nNone\n'
    with mockArgs(['--remain', '1', 'abc']):
        with mockOutput() as fakeOutput:
            sampleProcessor1().processAll()
            assert fakeOutput.getvalue() == '1 abc\n'
    with mockArgs(['remain', 'jasna', 'dupa', '--remain', '1', 'abc']):
        with mockOutput() as fakeOutput:
            sampleProcessor1().processAll()
            assert fakeOutput.getvalue() == '1 abc\njasna dupa\n'
    with mockArgs(['remain', 'jasna', 'dupa', '--remain', '1', 'abc']):
        with mockOutput() as fakeOutput:
            sampleProcessor1().processOptions()
            assert fakeOutput.getvalue() == '1 abc\n'

def test_ArgumentsProcessor_poll():
    # test polling
    with mockArgs(['poll', '123', '456', '789']):
        with mockOutput() as fakeOutput:
            sampleProcessor1().processAll()
            assert fakeOutput.getvalue() == '123\n456\n789\n'

def test_ArgumentsProcessor_removingArgs():
    # test removing parameters
    with mockArgs(['remain', 'jasna', 'dupa', '--remain', '1', 'abc']):
        with mockOutput() as fakeOutput:
            argsProcessor = sampleProcessor1()
            argsProcessor.processOptions()
            argsProcessor.processOptions()
            argsProcessor.processOptions()
            assert fakeOutput.getvalue() == '1 abc\n'
    with mockArgs(['remain', 'jasna', 'dupa', '--remain', '1', 'abc']):
        with mockOutput() as fakeOutput:
            argsProcessor = sampleProcessor1()
            argsProcessor.processOptions()
            argsProcessor.processAll()
            assert fakeOutput.getvalue() == '1 abc\njasna dupa\n'

def test_ArgumentsProcessor_unknownArg():
    # test unknown argument
    with mockArgs(['dupa']):
        try:
            sampleProcessor1().processAll()
            assert False
        except RuntimeError as e:
            # prints help and exit
            assert str(e) == 'Fatal error: unknown argument: dupa'
