#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glue

WARCRAFT_DIR = '/home/thrall/games/warcraft-3-pl/'
AOE2_DIR = '/home/thrall/games/aoe2/'
LICHKING_HOME = '/home/thrall/lichking/'
OS_VERSION = '/home/thrall/.osversion'
VERSION = '1.17.5'

autocompletes = []
parts = None
prefix = None
last = None

def defineAutocompletes(requiredPrefix, requiredLevel, possibleCmds):
    global autocompletes
    if prefix.startswith(requiredPrefix) and len(parts) == requiredLevel:
        filtered = list(filter(lambda c: c.startswith(last), possibleCmds))
        autocompletes.extend(filtered)

def actionAutocomplete(ap):
    global autocompletes
    global parts
    global prefix
    global last
    autocompletes = []
    compLine = ap.getParam('autocomplete')
    if compLine.startswith('"') and compLine.endswith('"'):
        compLine = compLine[1:-1]
    parts = compLine.split(' ')
    prefix = ' '.join(parts[1:])
    last = parts[-1]
    # first command help
    if len(parts) == 2:
        cmds = ['war', 'go', 'age', 'aoe', 'test', 'screen', 'network', 'audio', 'vsync', 'voice', 'voices', 'info', 'taunt', 'help']
        filtered = list(filter(lambda c: c.startswith(last), cmds))
        autocompletes.extend(filtered)
    else:
        # subcommands
        defineAutocompletes('test ', 3, ['audio', 'graphics', 'network', 'wine'])
        defineAutocompletes('screen ', 3, ['list', 'largest']) # TODO screen names
        defineAutocompletes('network ', 3, ['noipv6'])
        defineAutocompletes('audio ', 3, ['select-output'])
        defineAutocompletes('vsync ', 3, ['on', 'off'])
        defineAutocompletes('voice ', 3, ['list', 'random']) # TODO voice names
        defineAutocompletes('voices ', 3, []) # TODO voices group names
        defineAutocompletes('info ', 3, ['warcraftos', 'dota', 'age'])
        defineAutocompletes('taunt ', 3, ['list']) # TODO taunt numbers
    print('\n'.join(autocompletes))

# ----- Main
def main():
    ap = glue.ArgsProcessor('LichKing autocomplete', VERSION).clear()
    ap.bindDefaultAction(actionAutocomplete)
    ap.bindParam('autocomplete')
    ap.processAll() # do the magic

if __name__ == '__main__': # for testing purposes
    main() # will not be invoked when importing this file
