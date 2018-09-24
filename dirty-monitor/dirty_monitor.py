#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
from glue import *
import time
import threading


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
        return '%.1f MB' % mbs
    gbs = mbs / 1024.0
    return '%.1f GB' % gbs

def kb_to_human_just(kbs):
    return kb_to_human(kbs).rjust(9)

def calc_speed(mem_sizes_buffer):
    if len(mem_sizes_buffer) < 2:
        return 0

    diff = mem_sizes_buffer[-1][2] - mem_sizes_buffer[0][2]
    return diff / (len(mem_sizes_buffer) - 1)

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

# ----- Actions -----
def action_monitor_meminfo(ap):

    background_thread = None
    if ap.is_flag_set('sync'):
        background_thread = run_sync_background()

    mem_sizes_buffer = []

    try:
        while True:
            # rerun sync
            if ap.is_flag_set('sync') and not background_thread.is_alive():
                info('running sync in background...')
                background_thread.stop()
                background_thread = run_sync_background()

            dirty_kb, writeback_kb = get_mem_dirty_writeback()
            remaining_kb = dirty_kb + writeback_kb
            
            mem_sizes_buffer.append((dirty_kb, writeback_kb, remaining_kb))
            # max buffer size
            if len(mem_sizes_buffer) > 10:
                mem_sizes_buffer.pop(0)

            speed = calc_speed(mem_sizes_buffer)
            speed_human = kb_to_human_just(speed)
            eta_s = calc_eta(remaining_kb, speed)
            eta_human = seconds_to_human(eta_s).rjust(12)

            print('Dirty: %s, Writeback: %s, Remaining: %s, Speed: %s / s, ETA: %s' % (kb_to_human_just(dirty_kb), kb_to_human_just(writeback_kb), kb_to_human_just(remaining_kb), speed_human, eta_human))

            # delay before next loop
            time.sleep(1)
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
