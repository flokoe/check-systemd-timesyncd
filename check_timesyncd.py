#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A simple script that checks status of systemd-timesyncd service.
License: MIT
"""

from argparse import ArgumentParser
import sys, subprocess, re

__author__  = 'Florian Köhler'
__version__ = '0.2.0'
__license__ = 'MIT'

def to_dict(list):
    res = []

    for item in list:
        if '=' in item:
            res.append(map(str.strip, item.split('=', 1)))

    return dict(res)

def get_version():
    return int(subprocess.check_output(['systemctl', '--version'], universal_newlines=True).split("\n")[0].split(" ")[1])

def parse_legacy_systemd_output():
    output = subprocess.check_output(['timedatectl', 'status'], universal_newlines=True).split("\n")
    res = {}

    res['Timezone'] = output[3].split(':')[1].strip(' ').split(' ')[0]
    res['NTPSynchronized'] = output[4].split(':')[1].strip(' ')
    res['NTP'] = output[5].split(':')[1].strip(' ')

    return res

def main(args):
    state = 3
    state_msg = 'UNKNOWN - There is something wrong'
    timedatectl_dict = None

    systemd_version = get_version()

    if systemd_version >= 239:
        timedatectl_dict = to_dict(subprocess.check_output(['timedatectl', 'show'], universal_newlines=True).split("\n"))
        # timedatectl_ntp_msg = to_dict(re.sub('[{ }]', '', subprocess.check_output(['timedatectl', 'show-timesync', '-p', 'NTPMessage', '--value'], text=True)).split(','))
    else:
        timedatectl_dict = parse_legacy_systemd_output()

    if args.timezone and timedatectl_dict['Timezone'] != args.timezone:
        state = 2
        state_msg = f"CRITICAL - Timezone is '{timedatectl_dict['Timezone']}', but should be '{args.timezone}'"
    elif timedatectl_dict['NTP'] == 'yes' and timedatectl_dict['NTPSynchronized'] == 'yes':
        state = 0
        state_msg = 'OK - systemd-timesyncd is running fine'
    else:
        state = 2
        state_msg = 'CRITICAL - systemd-timesyncd not in sync or not enabled'

    print(state_msg)
    sys.exit(state)

def parse_cli():
    parser = ArgumentParser(description='A simple script that checks status of systemd-timesyncd service.')

    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("-t", "--timezone", help="Your timezone in form of 'Region/City'. E.g. 'Europe/Berlin'")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_cli()
    main(args)
