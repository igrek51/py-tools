#!/usr/bin/env python
# -*- coding: utf-8 -*-
from glue import *
from random import randint

WARCRAFT_DIR = '/home/thrall/games/warcraft-3-pl/'
AOE2_DIR = '/home/thrall/games/aoe2/'
HOMM3_DIR = '/mnt/games/games/heroes3-hota/'
VOICES_DIR = './voices/'
VERSION = '1.18.3'


def play_wav(path):
    shell('aplay %s' % path)


def play_mp3(path):
    shell('mplayer "%s" 1>/dev/null' % path)


def play_mp3_infinitely(path):
    try:
        shell('mpg123 --loop -1 --no-control -q "%s"' % path)
    except KeyboardInterrupt:
        shell('pkill mpg123')


def play_voice(voice_name):
    if not voice_name.endswith('.wav'):
        voice_name = voice_name + '.wav'
    if not os.path.isfile(VOICES_DIR + voice_name):
        error('no voice file named %s' % voice_name)
    else:
        play_wav(VOICES_DIR + voice_name)


def list_voices(subdir=''):
    voices_dir = VOICES_DIR + subdir
    voices = list_dir(voices_dir)
    voices = filter(lambda file: os.path.isfile(voices_dir + file), voices)
    voices = filter(lambda file: file.endswith('.wav'), voices)
    return list(map(lambda file: subdir + file[:-4], voices))


def random_item(a_list):
    return a_list[randint(0, len(a_list) - 1)]


def play_random_voice(subdir=''):
    if subdir and not subdir.endswith('/'):
        subdir += '/'
    # populate voices list
    voices = list_voices(subdir)
    # draw random voice
    if not voices:
        fatal('no voice available')
    random_voice = random_item(voices)
    info('Playing voice %s...' % random_voice)
    play_voice(random_voice)


def test_sound():
    info('testing audio...')
    try:
        while True:
            play_random_voice()
    except KeyboardInterrupt:
        pass


def test_network():
    info('Useful Linux commands: ifconfig, ping, nmap, ip')
    info('available network interfaces (up):')
    ifconfig = shell_output('sudo ifconfig')
    lines = nonempty_lines(ifconfig)
    lines = regex_filter_list(lines, r'^([a-z0-9]+).*')
    lines = regex_replace_list(lines, r'^([a-z0-9]+).*', '\\1')
    if not lines:
        fatal('no available network interfaces')
    for interface in lines:
        print(interface)
    info('testing IPv4 global DNS connectivity...')
    shell('ping 8.8.8.8 -c 4')
    info('testing global IP connectivity...')
    shell('ping google.pl -c 4')


def test_graphics():
    info('testing GLX (OpenGL for X Window System)...')
    error_code = shell_error_code('glxgears')
    debug('glxgears error code: %d' % error_code)


def test_wine():
    info('testing wine...')
    shell('wine --version')
    debug('launching notepad...')
    error_code = shell_error_code('wine notepad')
    debug('error code: %d' % error_code)


def network_disable_ipv6():
    debug('sudo sysctl -p')
    shell('sudo sysctl -p')
    info('IPv6 has been disabled')


def list_screens():
    # list outputs
    xrandr = shell_output('xrandr 2>/dev/null')
    lines = nonempty_lines(xrandr)
    lines = regex_filter_list(lines, r'^([a-zA-Z0-9\-]+) connected')
    lines = regex_replace_list(lines, r'^([a-zA-Z0-9\-]+) connected[a-z ]*([0-9]+)x([0-9]+).*', '\\1\t\\2\t\\3')
    if not lines:
        fatal('no xrandr outputs - something\'s fucked up')
    return split_to_tuples(lines, attrs_count=3, splitter='\t')


def set_screen_primary(screen_name):
    shell('xrandr --output %s --primary' % screen_name)
    info('%s set as primary' % screen_name)


def set_largest_screen_primary():
    largest_screen = None
    largest_size = 0
    for screen_name2, w, h in list_screens():
        size = int(w) * int(h)
        if size >= largest_size:  # when equal - the last one
            largest_size = size
            largest_screen = screen_name2
    if not largest_screen:
        fatal('largest screen not found')
    info('setting largest screen "%s" as primary...' % largest_screen)
    set_screen_primary(largest_screen)


def select_audio_output_device():
    info('select proper output device by disabling profiles in "Configuration" tab')
    shell('pavucontrol &')
    debug('playing test audio indefinitely...')
    play_mp3_infinitely('./data/illidan-jestem-slepy-a-nie-gluchy.mp3')


# ----- Actions -----
def action_run_war3():
    set_workdir(WARCRAFT_DIR)
    # taunt on startup
    play_random_voice()
    # RUN WINE
    shell('export LANG=pl_PL.UTF-8')  # LANG settings
    # 32 bit wine
    shell('export WINEARCH=win32')
    # shell('export WINEPREFIX=/home/thrall/.wine32')
    # 64 bit wine
    # shell('export WINEARCH=win64')
    # shell('unset WINEPREFIX')
    error_code = shell_error_code('wine "Warcraft III.exe" -opengl')
    debug('wine error code: %d' % error_code)
    # taunt on shutdown
    play_random_voice('war-close')


def action_play_voice(ap):
    voice_name = ap.poll_next()
    if voice_name:
        play_voice(voice_name)
    else:
        # list available voices - default
        action_list_voices(ap)


def completer_voices_list():
    return list_voices()


def action_play_voices_group(ap):
    group = ap.poll_next('group')
    play_random_voice(group)


def action_play_random_voice(ap):
    play_random_voice()


def action_list_voices(ap):
    info('Available voices:')
    for voice_name in list_voices():
        print(voice_name)


def action_tips_dota(ap):
    shell('sublime %swar-info/dota-info.md' % WARCRAFT_DIR)


def action_tips_age(ap):
    shell('sublime %sTaunt/cheatsheet.md' % get_aoe2_dir())


def action_set_screen_primary(ap):
    screen_name = ap.poll_next()
    if screen_name:
        info('setting screen "%s" as primary...' % screen_name)
        set_screen_primary(screen_name)
    else:
        action_list_screen(ap)


def action_list_screen(ap):
    info('Available screens:')
    for screenName2, w, h in list_screens():
        print(screenName2)


def completer_screen_list():
    return list(map(lambda s: s[0], list_screens()))


def action_vsync_set(ap):
    state = ap.poll_next('state')
    if state == 'on':
        shell('export vblank_mode=3')
        os.environ['vblank_mode'] = '3'
        info('please execute in parent shell process: export vblank_mode=3')
    elif state == 'off':
        os.environ['vblank_mode'] = '0'
        shell('export vblank_mode=0')
        info('please execute in parent shell process: export vblank_mode=0')
    else:
        raise CliSyntaxError('unknown state: %s' % state)


def action_memory_clear(ap):
    info('syncing...')
    shell('sync')
    info('memory (before):')
    shell('free -h')
    info('clearing PageCache, dentries and inodes (3)...')
    shell('sync; echo 3 | sudo tee /proc/sys/vm/drop_caches')
    info('cache / buffer memory dropped (after):')
    shell('free -h')


def action_memory_watch(ap):
    shell('watch -n 1 cat /proc/meminfo')


# Age
def get_aoe2_dir():
	if os.path.isdir(AOE2_DIR):
		return AOE2_DIR
	else:
		return './'

def action_run_aoe2():
    set_workdir(get_aoe2_dir() + 'age2_x1/')
    aoe_stachu_version = read_file(get_aoe2_dir() + 'stachu-version.txt')
    info('Running Age of Empires 2 - StachuJones-%s...' % aoe_stachu_version)
    play_wav('./data/stachu-2.wav')
    # run wine
    shell('export LANG=pl_PL.UTF-8')  # LANG settings
    shell('export WINEARCH=win32')  # 32 bit wine
    error_code = shell_error_code('wine age2_x2.exe -opengl')
    debug('wine error code: %d' % error_code)
    play_wav('./data/stachu-8.wav')


def action_aoe_taunt_list(ap):
    info('Available taunts:')
    taunt_list_file = get_aoe2_dir() + 'Taunt/cheatsheet.md'
    taunts_cheatsheet = read_file(taunt_list_file)
    print(taunts_cheatsheet)


def completer_taunts_list():
    return list(map(lambda num: str(num), range(1, 43)))


def action_aoe_taunt(ap):
    taunt_number = ap.poll_next()
    if taunt_number:
        # play selected taunt
        # preceding zero
        if len(taunt_number) == 1:
            taunt_number = '0' + taunt_number
        # find taunt by number
        taunts_dir = get_aoe2_dir() + 'Taunt/'
        taunts = list_dir(taunts_dir)
        taunts = filter_list(lambda file: os.path.isfile(taunts_dir + file), taunts)
        taunts = filter_list(lambda file: file.startswith(taunt_number), taunts)
        taunts = filter_list(lambda file: file.endswith('.mp3'), taunts)
        if not taunts:
            fatal('Taunt with number %s was not found' % taunt_number)
        if len(taunts) > 1:
            warn('too many taunts found')
        play_mp3(taunts_dir + taunts[0])
    else:  # list available taunts - default
        action_aoe_taunt_list(ap)


# HOMM3
def get_homm3_dir():
    if os.path.isdir(HOMM3_DIR):
        return HOMM3_DIR
    else:
        return './'


def action_run_homm3():
    set_workdir(get_homm3_dir())
    info('Running Heroes of Might & Magic 3...')
    error_code = shell_error_code('LANG=pl_PL.UTF-8 wine HD_Launcher.exe')
    debug('wine error code: %d' % error_code)


# ----- Args definitions -----
def main():
    set_workdir(script_real_dir())

    ap = ArgsProcessor(app_name='LichKing tool', version=VERSION)
    ap.add_subcommand(['war', 'go'], action=action_run_war3, help='run Warcraft3 using wine')
    ap.add_subcommand(['age', 'aoe'], action=action_run_aoe2, help='run AOE2 using wine')
    ap.add_subcommand(['heroes', 'homm3'], action=action_run_homm3, help='run HOMM3 using wine')

    ap_test = ap.add_subcommand('test')
    ap_test.add_subcommand('audio', action=test_sound, help='perform continuous audio test')
    ap_test.add_subcommand('graphics', action=test_graphics, help='perform graphics tests')
    ap_test.add_subcommand('network', action=test_network, help='perform network tests')
    ap_test.add_subcommand('wine', action=test_wine, help='perform wine tests')

    ap_screen = ap.add_subcommand('screen', action=action_set_screen_primary, syntax='[<screenName>]',
                                  help='set screen as primary', choices=completer_screen_list)
    ap_screen.add_subcommand('list', action=action_list_screen, help='list available screens')
    ap_screen.add_subcommand('largest', action=set_largest_screen_primary,
                             help='automatically set largest screen as primary')

    ap.add_subcommand('network').add_subcommand('noipv6', action=network_disable_ipv6, help='disable IPv6 (IPv4 only)')

    ap.add_subcommand('audio').add_subcommand('select-output', action=select_audio_output_device,
                                              help='select audio output device')

    ap.add_subcommand('vsync', action=action_vsync_set, syntax='<on|off>', choices=['on', 'off'],
                      help='enable / disable VSync')

    ap_voice = ap.add_subcommand('voice', action=action_play_voice, syntax='[<voiceName>]',
                                 help='play selected voice sound', choices=completer_voices_list)
    ap_voice.add_subcommand('list', action=action_list_voices, help='list available voices')
    ap_voice.add_subcommand('random', action=action_play_random_voice, help='play random voice sound')
    ap_voice.add_subcommand('group', action=action_play_voices_group, syntax='<group>',
                            help='play random voice from a group', choices=['startup', 'war-close', 'war-launch'])

    ap_info = ap.add_subcommand('info')
    ap_info.add_subcommand('dota', action=action_tips_dota, help='open Dota cheatsheet')
    ap_info.add_subcommand('age', action=action_tips_age, help='open AOE2 Taunts cheatsheet')

    ap_taunt = ap.add_subcommand('taunt', action=action_aoe_taunt, syntax='[<tauntNumber>]', help='play AOE2 Taunt',
                                 choices=completer_taunts_list)
    ap_taunt.add_subcommand('list', action=action_aoe_taunt_list, help='list available AOE2 Taunts')

    ap_memory = ap.add_subcommand('memory')
    ap_memory.add_subcommand('clear', action=action_memory_clear, help='clear cache / buffer RAM memory')
    ap_memory.add_subcommand('watch', action=action_memory_watch, help='watch memory cache / buffers / sections size')

    ap.add_subcommand('help', action=print_help, help='display this help and exit')

    ap.process()  # do the magic


if __name__ == '__main__':
    main()
