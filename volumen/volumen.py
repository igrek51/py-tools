#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os
import sys
import time
import argparse
import subprocess
import re

# Console text formatting characters
class Colouring:
    C_RESET = '\033[0m'
    C_BOLD = '\033[1m'
    C_DIM = '\033[2m'
    C_ITALIC = '\033[3m'
    C_UNDERLINE = '\033[4m'

    C_BLACK = 0
    C_RED = 1
    C_GREEN = 2
    C_YELLOW = 3
    C_BLUE = 4
    C_MAGENTA = 5
    C_CYAN = 6
    C_WHITE = 7

    def textColor(colorNumber):
        return '\033[%dm' % (30 + colorNumber)

    def backgroundColor(colorNumber):
        return '\033[%dm' % (40 + colorNumber)

    C_INFO = textColor(C_BLUE) + C_BOLD
    C_WARN = textColor(C_YELLOW) + C_BOLD
    C_ERROR = textColor(C_RED) + C_BOLD

T_INFO = Colouring.C_INFO + '[info]' + Colouring.C_RESET
T_WARN = Colouring.C_WARN + '[warn]' + Colouring.C_RESET
T_ERROR = Colouring.C_ERROR + '[ERROR]' + Colouring.C_RESET

def info(message):
    print(T_INFO + " " + message)

def warn(message):
    print(T_WARN + " " + message)

def error(message):
    print(T_ERROR + " " + message)

def fatal(message):
    error(message)
    sys.exit()



def shellExec(cmd):
    errCode = subprocess.call(cmd, shell=True)
    if errCode != 0:
        fatal('failed executing: %s' % cmd)

def shellExecErrorCode(cmd):
    return subprocess.call(cmd, shell=True)

def shellGetOutput(cmd):
    return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)


def start():
    args = parseArguments()
    masterVolume = readMasterVolume()
    iconName = getNotificationIcon(masterVolume)
    summary = 'Volume'
    body = '%d%%' % masterVolume
    replaceNotification(iconName, summary, body)

def readMasterVolume():
    masterVolumeRegex = r'^(.*)Front (Right|Left): Playback (\d*) \[(\d+)%\] \[on\]$'
    for line in shellGetOutput('amixer get Master').split('\n'):
        match = re.match(masterVolumeRegex, line)
        if match:
            return int(match.group(4))
    warn('Master volume could not have been read')
    return None

def getNotificationIcon(volume):
    if volume is None:
        return 'audio-card'
    if volume == 0:
        return "notification-audio-volume-off"
    elif volume < 30:
        return "notification-audio-volume-low"
    elif volume < 60:
        return "notification-audio-volume-medium"
    else:
        return "notification-audio-volume-high"

def replaceNotification(iconName, summary, body):
    lastNotificationId = readLastNotificationId()
    if lastNotificationId is None:
        lastNotificationId = 0
    showNotification(lastNotificationId, iconName, summary, body)

def readLastNotificationId():
    lastNIdRegex = r'^\(uint32 (\d+),\)$'
    filepath = 'lastNotification'
    with open(filepath) as f:
        for line in f:
            match = re.match(lastNIdRegex, line)
            if match:
                return match.group(1)
    warn('last notification id could not have been read')
    return None

def showNotification(oldNotificationId, iconName, summary, body):
    shellExec('gdbus call --session --dest org.freedesktop.Notifications --object-path /org/freedesktop/Notifications --method org.freedesktop.Notifications.Notify my_app_name %s %s "%s" "%s" [] {} 10 > lastNotification' % (oldNotificationId, iconName, summary, body))

def parseArguments():
    parser = argparse.ArgumentParser(description='Volume notifier')
    return parser.parse_args()


start()
