#!/usr/bin/env python
# -*- coding: utf-8 -*-
from glue import *
from random import randint

WARCRAFT_DIR = '/home/thrall/games/warcraft-3-pl/'
AOE2_DIR = '/home/thrall/games/aoe2/'
LICHKING_HOME = '/home/thrall/lichking/'
OS_VERSION = '/home/thrall/.osversion'
VERSION = '1.17.8'

def playWav(path):
    shellExec('aplay %s' % path)

def playMp3(path):
    shellExec('mplayer "%s" 1>/dev/null' % path)

def playMp3Infinitely(path):
    try:
        shellExec('mpg123 --loop -1 --no-control -q "%s"' % path)
    except KeyboardInterrupt:
        shellExec('pkill mpg123')

def playVoice(voiceName):
    voicesDir = getVoicesDir()
    if not voiceName.endswith('.wav'):
        voiceName = voiceName + '.wav'
    if not os.path.isfile(voicesDir + voiceName):
        error('no voice file named %s' % voiceName)
    else:
        playWav(voicesDir + voiceName)

def listVoices(subdir=''):
    voicesDir = getVoicesDir() + subdir
    voices = listDir(voicesDir)
    voices = filter(lambda file: os.path.isfile(voicesDir + file), voices)
    voices = filter(lambda file: file.endswith('.wav'), voices)
    return list(map(lambda file: subdir + file[:-4], voices))

def randomItem(aList):
    return aList[randint(0, len(aList)-1)]

def playRandomVoice(subdir=''):
    if subdir and not subdir.endswith('/'):
        subdir += '/'
    # populate voices list
    voices = listVoices(subdir)
    # draw random voice
    if not voices:
        fatal('no voice available')
    randomVoice = randomItem(voices)
    info('Playing voice %s...' % randomVoice)
    playVoice(randomVoice)

def validateHomeDir():
    global LICHKING_HOME
    if not os.path.isdir(LICHKING_HOME) and LICHKING_HOME:
        LICHKING_HOME = getScriptRealDir()
        if not LICHKING_HOME.endswith('/'):
            LICHKING_HOME += '/'
        warn('lichking home set to: %s' % LICHKING_HOME)

def getVoicesDir():
    return LICHKING_HOME + 'voices/'

def testSound():
    info('testing audio...')
    while(True):
        playRandomVoice()

def testNetwork():
    info('Useful Linux commands: ifconfig, ping, nmap, ip')
    info('available network interfaces (up):')
    ifconfig = shellOutput('sudo ifconfig')
    lines = splitLines(ifconfig)
    lines = regexFilterList(lines, r'^([a-z0-9]+).*')
    lines = regexReplaceList(lines, r'^([a-z0-9]+).*', '\\1')
    if not lines:
        fatal('no available network interfaces')
    for interface in lines:
        print(interface)
    info('testing IPv4 global DNS connectivity...')
    shellExec('ping 8.8.8.8 -c 4')
    info('testing global IP connectivity...')
    shellExec('ping google.pl -c 4')

def testGraphics():
    info('testing GLX (OpenGL for X Window System)...')
    errorCode = shellExecErrorCode('glxgears')
    debug('glxgears error code: %d' % errorCode)

def testWine():
    info('testing wine...')
    shellExec('wine --version')
    debug('launching notepad...')
    errorCode = shellExecErrorCode('wine notepad')
    debug('error code: %d' % errorCode)

def showWarcraftosInfo():
    info('Welcome to the WarcraftOS v%s created by Igrek' % readFile(OS_VERSION).strip())
    info('thrall user has no password.')
    info('root user password is: war')
    info('When launching WC3 game, you have custom keys shortcuts (QWER) already enabled.')

def disableIPv6():
    debug('sudo sysctl -p')
    shellExec('sudo sysctl -p')
    info('IPv6 has been disabled')

def listScreens():
    # list outputs
    xrandr = shellOutput('xrandr 2>/dev/null')
    lines = splitLines(xrandr)
    lines = regexFilterList(lines, r'^([a-zA-Z0-9\-]+) connected')
    lines = regexReplaceList(lines, r'^([a-zA-Z0-9\-]+) connected[a-z ]*([0-9]+)x([0-9]+).*', '\\1\t\\2\t\\3')
    if not lines:
        fatal('no xrandr outputs - something\'s fucked up')
    return splitToTuples(lines, attrsCount=3, splitter='\t')

def setScreenPrimary(screenName):
    shellExec('xrandr --output %s --primary' % screenName)
    info('%s set as primary' % screenName)

def setLargestScreenPrimary():
    largestScreen = None
    largestSize = 0
    for screenName2, w, h in listScreens():
        size = int(w) * int(h)
        if size >= largestSize: # when equal - the last one
            largestSize = size
            largestScreen = screenName2
    if not largestScreen:
        fatal('largest screen not found')
    info('setting largest screen "%s" as primary...' % largestScreen)
    setScreenPrimary(largestScreen)

def selectAudioOutputDevice():
    info('select proper output device by disabling profiles in "Configuration" tab')
    shellExec('pavucontrol &')
    debug('playing test audio indefinitely...')
    playMp3Infinitely(LICHKING_HOME + 'data/illidan-jestem-slepy-a-nie-gluchy.mp3')

# ----- Actions
def actionRunWar3():
    setWorkdir(WARCRAFT_DIR)
    # taunt on startup
    playRandomVoice()
    # RUN WINE
    shellExec('LANG=pl_PL.UTF-8') # LANG settings
    # 32 bit wine
    shellExec('export WINEARCH=win32')
    #shellExec('export WINEPREFIX=/home/thrall/.wine32')
    # 64 bit wine
    #shellExec('export WINEARCH=win64')
    #shellExec('unset WINEPREFIX')
    errorCode = shellExecErrorCode('wine "Warcraft III.exe" -opengl')
    debug('wine error code: %d' % errorCode)
    # taunt on shutdown
    playRandomVoice('war-close')

def actionPlayVoice(ap):
    voiceName = ap.pollNext()
    if not voiceName or voiceName == 'list': # list available voices - default
        info('Available voices:')
        for voiceName in listVoices():
            print(voiceName)
    elif voiceName == 'random': # play random voice
        playRandomVoice()
    else: # play selected voice
        playVoice(voiceName)

def actionPlayVoices(ap):
    group = ap.pollNext('group')
    playRandomVoice(group)

def actionTips(ap):
    tipsName = ap.pollNext()
    if not tipsName or tipsName == 'warcraftos': # default
        showWarcraftosInfo()
    elif tipsName == 'dota':
        shellExec('sublime %swar-info/dota-info.md' % WARCRAFT_DIR)
    elif tipsName == 'age':
        shellExec('sublime %sTaunt/cheatsheet.md' % AOE2_DIR)
    else:
        fatal('unknown tipsName: %s' % tipsName)

def actionTest(ap):
    testName = ap.pollNext('testName')
    if testName == 'audio':
        testSound()
    elif testName == 'graphics':
        testGraphics()
    elif testName == 'network':
        testNetwork()
    elif testName == 'wine':
        testWine()
    else:
        fatal('unknown testName: %s' % testName)

def actionConfigNetwork(ap):
    comamndName = ap.pollNext('comamndName')
    if comamndName == 'noipv6':
        disableIPv6()
    else:
        fatal('unknown comamndName: %s' % comamndName)

def actionConfigAudio(ap):
    comamndName = ap.pollNext('comamndName')
    if comamndName == 'select-output':
        selectAudioOutputDevice()
    else:
        fatal('unknown comamndName: %s' % comamndName)

def actionScreen(ap):
    screenName = ap.pollNext()
    if not screenName or screenName == 'list':
        info('Available screens:')
        for screenName2, w, h in listScreens():
            print(screenName2)
    elif screenName == 'largest': # auto select largest screen
        setLargestScreenPrimary()
    else: # set output primary
        info('setting screen "%s" as primary...' % screenName)
        setScreenPrimary(screenName)

def actionVsyncSet(ap):
    state = ap.pollNext('state')
    if state == 'on':
        shellExec('export vblank_mode=3')
        os.environ['vblank_mode'] = '3'
        info('please execute in parent shell process: export vblank_mode=3')
    elif state == 'off':
        os.environ['vblank_mode'] = '0'
        shellExec('export vblank_mode=0')
        info('please execute in parent shell process: export vblank_mode=0')
    else:
        fatal('unknown state: %s' % state)

# Age
def actionRunAOE2():
    setWorkdir(AOE2_DIR + 'age2_x1/')
    aoeStachuVersion = readFile(AOE2_DIR + 'stachu-version.txt')
    info('Running Age of Empires 2 - StachuJones-%s...' % aoeStachuVersion)
    playWav(LICHKING_HOME + 'data/stachu-2.wav')
    # run wine
    shellExec('LANG=pl_PL.UTF-8') # LANG settings
    shellExec('export WINEARCH=win32') # 32 bit wine
    errorCode = shellExecErrorCode('wine age2_x2.exe -opengl')
    debug('wine error code: %d' % errorCode)
    playWav(LICHKING_HOME + 'data/stachu-8.wav')

def actionAOETaunt(ap):
    tauntNumber = ap.pollNext()
    if not tauntNumber or tauntNumber == 'list': # list available taunts - default
        info('Available taunts:')
        tauntsCheatsheet = readFile(AOE2_DIR + 'Taunt/cheatsheet.md')
        print(tauntsCheatsheet)
    else: # play selected taunt
        # preceding zero
        if len(tauntNumber) == 1:
            tauntNumber = '0' + tauntNumber
        # find taunt by number
        tauntsDir = AOE2_DIR + 'Taunt/'
        taunts = listDir(tauntsDir)
        taunts = filter(lambda file: os.path.isfile(tauntsDir + file), taunts)
        taunts = filter(lambda file: file.startswith(tauntNumber), taunts)
        taunts = filter(lambda file: file.endswith('.mp3'), taunts)
        if not taunts:
            fatal('Taunt with number %s was not found' % tauntNumber)
        if len(taunts) > 1:
            warn('too many taunts found')
        playMp3(tauntsDir + taunts[0])

# ----- Main
def main():
    validateHomeDir()
    ap = ArgsProcessor('LichKing - WarcraftOS tool', VERSION)
    ap.bindCommand(actionRunWar3, ['war', 'go'], help='run Warcraft3 using wine')
    ap.bindCommand(actionRunAOE2, ['age', 'aoe'], help='run AOE2 using wine')
    ap.bindCommand(actionTest, 'test', suffix='audio', help='perform continuous audio test')
    ap.bindCommand(actionTest, 'test', suffix='graphics', help='perform graphics tests')
    ap.bindCommand(actionTest, 'test', suffix='network', help='perform network tests')
    ap.bindCommand(actionTest, 'test', suffix='wine', help='perform wine tests')
    ap.bindCommand(actionScreen, 'screen', suffix='[list]', help='list available screens')
    ap.bindCommand(actionScreen, 'screen', suffix='<screenName>', help='set screen as primary')
    ap.bindCommand(actionScreen, 'screen', suffix='largest', help='automatically set largest screen as primary')
    ap.bindCommand(actionConfigNetwork, 'network', suffix='noipv6', help='disable IPv6 (IPv4 only)')
    ap.bindCommand(actionConfigAudio, 'audio', suffix='select-output', help='select audio output device')
    ap.bindCommand(actionVsyncSet, 'vsync', suffix='<on|off>', help='enable / disable VSync')
    ap.bindCommand(actionPlayVoice, 'voice', suffix='[list]', help='list available voices')
    ap.bindCommand(actionPlayVoice, 'voice', suffix='<voiceName>', help='play selected voice sound')
    ap.bindCommand(actionPlayVoice, 'voice', suffix='random', help='play random voice sound')
    ap.bindCommand(actionPlayVoices, 'voices', suffix='<group>', help='play random voice from a group')
    ap.bindCommand(actionTips, 'info', suffix='[warcraftos]', help='show WarcraftOS info')
    ap.bindCommand(actionTips, 'info', suffix='dota', help='open Dota cheatsheet')
    ap.bindCommand(actionTips, 'info', suffix='age', help='open AOE2 Taunts cheatsheet')
    ap.bindCommand(actionAOETaunt, 'taunt', suffix='[list]', help='list available AOE2 Taunts')
    ap.bindCommand(actionAOETaunt, 'taunt', suffix='<tauntNumber>', help='play AOE2 Taunt')
    ap.bindCommand(printHelp, 'help', help='display this help and exit')
    ap.processAll() # do the magic

if __name__ == '__main__': # for testing purposes
    main() # will not be invoked when importing this file
