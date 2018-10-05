#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
from glue import *
import time
import threading
import select


def get_mem_dirty_writeback():
    meminfo = nonempty_lines(shell_output('cat /proc/meminfo'))
    dirty = regex_filter_list(meminfo, r'Dirty: +([0-9]+) kB')
    dirty = regex_replace_list(dirty, r'Dirty: +([0-9]+) kB', '\\1')
    writeback = regex_filter_list(meminfo, r'Writeback: +([0-9]+) kB')
    writeback = regex_replace_list(writeback, r'Writeback: +([0-9]+) kB', '\\1')
    return (int(dirty[0]), int(writeback[0]))

def run_sync_background():
    background_thread = BackgroundExecuteThread('sync')
    background_thread.start()
    return background_thread

class BackgroundExecuteThread(threading.Thread):
    def __init__(self, cmd):
        threading.Thread.__init__(self)
        self.daemon = True
        self.__cmd = cmd
        self.__proc = None

    def run(self):
        # output to console
        self.__proc = subprocess.Popen(self.__cmd, stdout=None, shell=True, preexec_fn=os.setsid)
        if self.__proc is not None:
            self.__proc.wait()
            self.__proc = None

    def stop(self):
        self.__proc = self.__killProcess(self.__proc)

    def __killProcess(self, proc):
        if proc is not None:
            if proc.poll() is None:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                proc.terminate()

def kb_to_human(kbs):
    if kbs < 0:
        return '-' + kb_to_human(-kbs)
    if kbs < 1024:
        return '%d kB' % kbs
    mbs = kbs / 1024.0
    if mbs < 1024:
        return '%.2f MB' % mbs
    gbs = mbs / 1024.0
    return '%.2f GB' % gbs

def kb_to_human_just(kbs):
    return kb_to_human(kbs).rjust(10)

def kb_to_speed_human_just(kbs):
    kb_human = kb_to_human(kbs) + '/s'
    if kbs > 0:
        kb_human = '+' + kb_human
    return kb_human.rjust(10)

def calc_avg_speed(mem_sizes_buffer):
    if len(mem_sizes_buffer) < 2:
        return 0
    diff = mem_sizes_buffer[-1][2] - mem_sizes_buffer[0][2]
    return diff / (len(mem_sizes_buffer) - 1)

def calc_temporary_speed(mem_sizes_buffer):
    if len(mem_sizes_buffer) < 2:
        return 0
    return mem_sizes_buffer[-1][2] - mem_sizes_buffer[-2][2]

def calc_eta(remaining_kb, speed):
    if speed >= 0:
        return None
    return remaining_kb / -speed

def seconds_to_human(seconds):
    if not seconds:
        return 'Infinity'
    strout = '%d s' % (int(seconds) % 60)
    minutes = int(seconds) // 60
    if minutes > 0:
        strout = '%d min %s' % (minutes, strout)
    return strout

def current_time():
    now = datetime.datetime.now()
    return time2str(now, '%H:%M:%S')

CHAR_BOLD = '\033[1m'
CHAR_RESET = '\033[0m'
CHAR_GREEN = '\033[32m'
CHAR_BLUE = '\033[34m'
CHAR_YELLOW = '\033[33m'
CHAR_RED = '\033[31m'

def input_or_timeout(timeout):
    i, o, e = select.select( [sys.stdin], [], [], timeout)
    if (i):
        return sys.stdin.readline().strip()
    else:
        return None

# ----- Actions -----
def action_monitor_meminfo(ap):

    background_thread = None
    if ap.is_flag_set('sync'):
        background_thread = run_sync_background()

    mem_sizes_buffer = []

    try:
        while True:
            # rerun sync
            if ap.is_flag_set('sync') and background_thread and not background_thread.is_alive():
                info('running sync in background...')
                background_thread.stop()
                background_thread = run_sync_background()

            dirty_kb, writeback_kb = get_mem_dirty_writeback()
            remaining_kb = dirty_kb + writeback_kb
            
            mem_sizes_buffer.append((dirty_kb, writeback_kb, remaining_kb))
            # max buffer size
            if len(mem_sizes_buffer) > 10:
                mem_sizes_buffer.pop(0)

            speed_temp = calc_temporary_speed(mem_sizes_buffer)
            speed_avg = calc_avg_speed(mem_sizes_buffer)
            eta_s = calc_eta(remaining_kb, speed_avg)

            # output values
            print_timestamp = CHAR_BOLD + current_time() + CHAR_RESET
            print_remaining = CHAR_BOLD + kb_to_human_just(remaining_kb) + CHAR_RESET
            print_temporary_speed = CHAR_BOLD + kb_to_speed_human_just(speed_temp) + CHAR_RESET
            print_avg_speed = CHAR_BOLD + kb_to_speed_human_just(speed_avg) + CHAR_RESET
            print_eta = CHAR_BOLD + seconds_to_human(eta_s).rjust(12) + CHAR_RESET

            # output formatting
            if remaining_kb < 100:
                print_remaining = CHAR_GREEN + print_remaining

            if speed_temp > 0:
                print_temporary_speed = CHAR_RED + print_temporary_speed
            elif speed_temp == 0:
                print_temporary_speed = CHAR_YELLOW + print_temporary_speed
            else:
                print_temporary_speed = CHAR_GREEN + print_temporary_speed

            if speed_avg > 0:
                print_avg_speed = CHAR_RED + print_avg_speed
            elif speed_avg == 0:
                print_avg_speed = CHAR_YELLOW + print_avg_speed
            else:
                print_avg_speed = CHAR_GREEN + print_avg_speed

            if not eta_s:
                print_eta = CHAR_YELLOW + print_eta
            elif eta_s < 60:
                print_eta = CHAR_GREEN + print_eta

            print('[%s] Remaining: %s, Speed: %s, AVG speed: %s, ETA: %s' % (print_timestamp, print_remaining, print_temporary_speed, print_avg_speed, print_eta))

            # delay before next loop
            inp = input_or_timeout(1)
            # sync command
            if inp == 's':
                if not background_thread or not background_thread.is_alive():
                    info('running sync in background...')
                    background_thread = run_sync_background()

            #time.sleep(1)
    except KeyboardInterrupt:
        # Ctrl + C handling without printing stack trace
        print  # new line
    except:
        # closing threads before exit caused by critical error
        raise
    finally:
        # cleanup_thread
        if background_thread is not None:
            background_thread.stop()


# ----- CLI definitions -----
def main():
    ap = ArgsProcessor(app_name='Dirty-Writeback memory stream monitor', version='1.0.1', default_action=action_monitor_meminfo)
    ap.add_flag('sync', help='run sync continuously')
    ap.process()


if __name__ == '__main__':
    main()
