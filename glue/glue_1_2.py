#!/usr/bin/python
"""
glue v1.2.3
Common Utilities Toolkit compatible with Python 2.7 and 3

Author: igrek51
License: Beerware
"""
import os
import sys
import re
import subprocess
import glob
import inspect
from builtins import bytes

# ----- Output
def debug(message):
    print('\033[32m\033[1m[debug]\033[0m ' + message)

def info(message):
    print('\033[34m\033[1m[ info]\033[0m ' + message)

def warn(message):
    print('\033[33m\033[1m[ warn]\033[0m ' + message)

def error(message):
    print('\033[31m\033[1m[ERROR]\033[0m ' + message)

def fatal(message):
    error(message)
    raise Exception('Fatal error: %s' % message)

# ----- Shell
def shellExec(cmd):
    errCode = subprocess.call(cmd, shell=True)
    if errCode != 0:
        fatal('failed executing: %s' % cmd)

def shellExecErrorCode(cmd):
    return subprocess.call(cmd, shell=True)

def shellOutput(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    output, err = process.communicate()
    return output.decode('utf-8')

# ----- String operations
def splitLines(inputString):
    allLines = inputString.splitlines()
    return list(filter(lambda l: len(l) > 0, allLines)) # filter nonempty

def split(inputString, delimiter):
    return inputString.split(delimiter)

def regexReplace(inputString, regexMatch, regexReplace):
    regexMatcher = re.compile(regexMatch)
    return regexMatcher.sub(regexReplace, inputString)

def regexMatch(inputString, regexMatch):
    regexMatcher = re.compile(regexMatch)
    return bool(regexMatcher.match(inputString))

def regexReplaceLines(lines, regexMatch, regexReplace):
    regexMatcher = re.compile(regexMatch)
    filtered = []
    for line in lines:
        line = regexMatcher.sub(regexReplace, line)
        filtered.append(line)
    return filtered

def regexFilterLines(lines, regexMatch):
    regexMatcher = re.compile(regexMatch)
    filtered = []
    for line in lines:
        if regexMatcher.match(line):
            filtered.append(line)
    return filtered

def regexSearchFile(filePath, regexMatch, groupNumber):
    regexMatcher = re.compile(regexMatch)
    with open(filePath) as f:
        for line in f:
            match = regexMatcher.match(line)
            if match:
                return match.group(groupNumber)

def input23(prompt=None):
    """raw input compatible with python 2 and 3"""
    try:
       return raw_input(prompt) # python2
    except NameError:
       pass
    return input(prompt) # python3

def inputRequired(prompt):
    while True:
        inputted = input23(prompt)
        if not inputted:
            continue
        print
        return inputted

# ----- File operations
def readFile(filePath):
    with open(filePath, 'rb') as f:
        return f.read().decode('utf-8')

def saveFile(filePath, content):
    f = open(filePath, 'wb')
    f.write(bytes(content, 'utf-8'))
    f.close()

def listDir(path):
    return sorted(os.listdir(path))

def setWorkdir(workdir):
    os.chdir(workdir)

def getWorkdir():
    return os.getcwd()

# ----- Collections helpers
def filterList(condition, lst):
    # condition example: lambda l: len(l) > 0
    return list(filter(condition, lst))

# ----- CLI arguments
class CommandArgRule:
    def __init__(self, isOption, action, name, description, syntaxSuffix):
        self.isOption = isOption
        self.action = action
        # store names list
        self.names = name if isinstance(name, list) else [name]
        self.description = description
        self.syntaxSuffix = syntaxSuffix

    def displayNames(self):
        return ', '.join(self.names)

    def displaySyntax(self):
        syntax = self.displayNames()
        if self.syntaxSuffix:
            syntax += self.syntaxSuffix if self.syntaxSuffix[0] == ' ' else ' ' + self.syntaxSuffix
        return syntax

    def displayHelp(self, syntaxPadding):
        dispHelp = self.displaySyntax()
        if self.description:
            dispHelp = dispHelp.ljust(syntaxPadding) + ' - ' + self.description
        return dispHelp

class ArgumentsProcessor:
    def __init__(self, appName, version):
        self._appName = appName
        self._version = version
        self._argRules = []
        self._argsQue = sys.argv[1:] # CLI arguments list
        self._argsOffset = 0

    def bindOption(self, action, name, description=None, syntaxSuffix=None):
        self._argRules.append(CommandArgRule(True, action, name, description, syntaxSuffix))

    def bindCommand(self, action, name, description=None, syntaxSuffix=None):
        self._argRules.append(CommandArgRule(False, action, name, description, syntaxSuffix))

    # Getting args
    def pollNext(self):
        if not self.hasNext():
            return None
        nextArg = self._argsQue[self._argsOffset]
        del self._argsQue[self._argsOffset]
        return nextArg

    def peekNext(self):
        if not self.hasNext():
            return None
        return self._argsQue[self._argsOffset]

    def hasNext(self):
        if not self._argsQue:
            return False
        return len(self._argsQue) > self._argsOffset

    def pollNextRequired(self, paramName):
        param = self.pollNext()
        if not param:
            fatal('no %s parameter given' % paramName)
        return param

    def pollRemaining(self, joiner=' '):
        beginning = self._argsQue[:self._argsOffset]
        ending = self._argsQue[self._argsOffset:]
        remainingArgs = joiner.join(ending)
        self._argsQue = beginning
        return remainingArgs

    # Processing args
    def processAll(self):
        # empty arguments list - print help
        if not self._argsQue:
            self.printHelp()
        # first process all options
        self.processOptions()
        # then process the rest of commands
        self._argsOffset = 0
        while self.hasNext():
            self._processArgument(self.pollNext())

    def processOptions(self):
        self._argsOffset = 0
        while self.hasNext():
            nextArg = self.peekNext()
            if self._isArgOption(nextArg):
                self._processArgument(self.pollNext())
            else:
                self._argsOffset += 1

    def _isArgOption(self, arg):
        rule = self._findCommandArgRule(arg)
        if rule:
            return rule.isOption()
        return False

    def _processArgument(self, arg):
        rule = self._findCommandArgRule(arg)
        if rule:
            # execute action(self) or action()
            (args, _, _, _) = inspect.getargspec(rule.action)
            if args:
                rule.action(self)
            else:
                rule.action()
        else:
            fatal('unknown argument: %s' % arg)

    def _findCommandArgRule(self, arg):
        for rule in self._argRules:
            if arg in rule.names:
                return rule

    # autogenerating help output
    def _optionRulesCount(self):
        return sum(1 for rule in self._argRules if rule.isOption)

    def _commandRulesCount(self):
        return sum(1 for rule in self._argRules if not rule.isOption)

    def _calcMinSyntaxPadding(self):
        minSyntaxPadding = 0
        for rule in self._argRules:
            syntax = rule.displaySyntax()
            if len(syntax) > minSyntaxPadding: # min padding = max from len(syntax)
                minSyntaxPadding = len(syntax)
        return minSyntaxPadding

    def printHelp(self):
        # autogenerate help
        self.printVersion()
        print('\nUsage:')
        usageSyntax = sys.argv[0]
        if self._optionRulesCount() > 0:
            usageSyntax += ' [options]'
        if self._commandRulesCount() > 0:
            usageSyntax += ' <command>'
        print('  %s' % usageSyntax)
        syntaxPadding = self._calcMinSyntaxPadding()
        if self._commandRulesCount() > 0:
            print('\nCommands:')
            for rule in self._argRules:
                if not rule.isOption:
                    print('  %s' % rule.displayHelp(syntaxPadding))
        if self._optionRulesCount() > 0:
            print('\nOptions:')
            for rule in self._argRules:
                if rule.isOption:
                    print('  %s' % rule.displayHelp(syntaxPadding))
        sys.exit()

    def printVersion(self):
        print('%s v%s' % (self._appName, self._version))

# workaround for invoking help by function reference
def printHelp(argsProcessor):
    argsProcessor.printHelp()

def printVersion(argsProcessor):
    argsProcessor.printVersion()
