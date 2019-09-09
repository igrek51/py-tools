#!/usr/bin/python
import time
import difflib
import subprocess
import sys
from colorama import Fore, Back, Style, init

init()


def shell_error_code(cmd):
    return subprocess.call(cmd, shell=True)


def shell(cmd):
    err_code = shell_error_code(cmd)
    if err_code != 0:
        fatal('failed executing: %s' % cmd)


def shell_output(cmd, as_bytes=False):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    output, err = process.communicate()
    if as_bytes:
        return output
    else:
        return output.decode('utf-8')


def color_diff(diff):
    for line in diff:
        if line.startswith('+'):
            yield Fore.GREEN + line + Fore.RESET
        elif line.startswith('-'):
            yield Fore.RED + line + Fore.RESET
        elif line.startswith('^'):
            yield Fore.BLUE + line + Fore.RESET
        else:
            yield line


cmd = ' '.join(sys.argv[1:])
output_0 = shell_output(cmd)

while(True):
	shell('tput reset')

	output_now = shell_output(cmd)

	diff = difflib.ndiff(output_0.splitlines(1), output_now.splitlines(1))
	diff = [d for d in diff if d[0] != ' ']
	diff = color_diff(diff)
	print(''.join(diff))

	time.sleep(1)