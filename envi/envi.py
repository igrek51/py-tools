#!/usr/bin/env python

import argparse
import os
import sys
import subprocess
import time
from glue import *

def detach_to_background():
    pid = os.fork()
    if pid == 0:  # Child
        os.setsid()  # creates a new session
        print('pid in background:', os.getpid())
    else:  # Parent
        print('pid in foreground:', os.getpid())
        exit()

def key_type(text):
    text = text.replace('"', '\\"')
    shell('xdotool key type "{}"'.format(text))

def key_enter():
    shell('xdotool key Return')

def terminal_title(title):
    key_type('. /usr/bin/title {}'.format(title))
    key_enter()

def type_file(source_file):
    with open(source_file) as f:
        lines = f.readlines()
        for line in lines:
            line_break = line.endswith('\n')
            line = line.strip()
            if line:
                key_type(line)
                if line_break:
                    key_enter()

def type_env(env_name):
    filename = 'env-{}.sh'.format(env_name)
    type_file(os.path.join(script_real_dir(), filename))

def setup_env(env_name):
    detach_to_background()
    time.sleep(0.1)
    type_env(env_name)

def action_setup_env(ap):
    env_name = ap.poll_next()
    if env_name:
        setup_env(env_name)
    else:
        action_print_env_names()

def action_ignite_env():
    info('launching terminal...')
    shell('gnome-terminal --tab &')

    info('launching google chrome...')
    shell('google-chrome-stable \
      "https://mail.google.com/mail/u/0/#inbox" \
      &')

    info('launching sublime...')
    shell('subl &')

def env_names():
    files = list_dir(script_real_dir())
    pattern = r'env-(.+)\.sh'
    files = filter(lambda f: regex_match(f, pattern), files)
    files = map(lambda f: regex_replace(f, pattern, r'\1'), files)
    return files

def action_print_env_names():
    print(env_names())

def add_aliases(ap):
    for env_name in env_names():
        def action_run_alias(name):
            def action():
                setup_env(name)
            return action
        ap.add_subcommand(env_name, action_run_alias(env_name), help='run env {}'.format(env_name))

def main():
    ap = ArgsProcessor(app_name='envi - environment starter', version='1.0.1')
    ap.add_subcommand('run', action_setup_env, help='setup environment', choices=env_names)
    ap.add_subcommand('ignite', action_ignite_env, help='setup start environment')
    ap.add_subcommand('list', action_print_env_names, help='print available env names')
    add_aliases(ap)
    ap.process()


if __name__ == '__main__':
    main()
