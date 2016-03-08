#! /usr/bin/python3

import argparse
import os

from servercheck import FileTester, ProcessTester

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='store_true')

opts = parser.parse_args()

host_file = FileTester('/etc/hosts',
                       verbose=opts.verbose)

host_file.is_file()
host_file.mode(644)

vhost = FileTester('/etc/httpd/conf.d/vhost.conf',
                   verbose=opts.verbose)

vhost.is_file()
vhost.mode('644')
vhost.contains_string('ServerName: example.com')

home = FileTester(os.path.expanduser('~'),
                  verbose=opts.verbose)

home.is_dir()
home.owner_is(os.getuid())
home.group_is(os.getgid())
home.mode('644')


tmux = ProcessTester('tmux',
                     verbose=opts.verbose)

tmux.is_running()
tmux.is_running_as('peteches')
