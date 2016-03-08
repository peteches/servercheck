#! /usr/bin/python

import argparse

from servercheck import FileTester

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
