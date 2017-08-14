#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os
import sys
import time
import argparse

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



def start():
    args = parseArguments()




def parseArguments():
    parser = argparse.ArgumentParser(description='Volume notifier')
    return parser.parse_args()


start()
