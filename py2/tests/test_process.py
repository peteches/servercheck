import psutil
import logging
import subprocess as sp
import servercheck
import pwd
import itertools
import random
import os

from nose.tools import *
from testfixtures import LogCapture


class TestProcessTester(servercheck.ProcessTester):

    __test__ = False

    def __init__(self, *args, **kwargs):
        super(TestProcessTester, self).__init__(verbose=True,
                                                *args,
                                                **kwargs)


class TestProcess:

    def __init__(self, **kwargs):
        self.log_name = 'servercheck.TestProcessTester.{}'

        self.pass_str = '\033[1;32mPASS: Process "{}" {}\033[0m'
        self.fail_str = '\033[1;31mFAIL: Process "{}" {}\033[0m'

        self.processes = [
            ['sleep', '200'],
            ['yes', 'TESTING'],
        ]

        self.fake_processes = [
            'NotAProcess',
            'ThinksItMayBeAProcess',
            'InNoWayIsThisAProcess',
        ]

    def setup(self):

        self.log_capture = LogCapture()

        self.running_procs = []

        with open('/dev/null', 'w') as DEVNULL:
            for p in self.processes:
                self.running_procs.append(sp.Popen(p,
                                                   stderr=DEVNULL,
                                                   stdout=DEVNULL))

    def teardown(self):
        self.log_capture.uninstall()

        for p in self.running_procs:
            p.kill()

    def check_pname_set_correctly(self, pname):

        pt = TestProcessTester(pname)

        assert_equal(pname, pt.pname)

    def test_pname_set_correctly(self):
        for p in [x[0] for x in self.processes]:
            yield self.check_pname_set_correctly, p

        for p in self.fake_processes:
            yield self.check_pname_set_correctly, p

    def check_process_is_running(self, pname):
        pt = TestProcessTester(pname)

        pt.is_running()

        if pname in [x[0] for x in self.processes]:
            lvl = 'INFO'
            msg = self.pass_str.format(pname,
                                       'is running.')
        else:
            lvl = 'WARNING'
            msg = self.fail_str.format(pname,
                                       'is not running.')

        self.log_capture.check(
            (
                self.log_name.format(pname),
                lvl,
                msg,
            ),
        )

    def test_process_running(self):
        for p in [x[0] for x in self.processes]:
            yield self.check_process_is_running, p

        for p in self.fake_processes:
            yield self.check_process_is_running, p

    def check_running_as(self, pname, test_user, exp_user):

        pt = TestProcessTester(pname)

        if test_user == exp_user:
            lvl = 'INFO'
            msg = self.pass_str.format(pname,
                                       'is running as {}.'.format(test_user))
        else:
            lvl = 'WARNING'
            msg = self.fail_str.format(pname,
                                       'is not running as {}.'.format(test_user))  # nopep8

        pt.is_running_as(test_user)

        self.log_capture.check(
            (
                self.log_name.format(pname),
                lvl,
                msg,
            ),
        )

    def test_running_as(self):
        current_user = pwd.getpwuid(os.getuid()).pw_name
        for p in [x[0] for x in self.processes]:
            for u in ['root', current_user]:
                yield self.check_running_as, p, u, current_user
        rp = sp.Popen(['ps', '-U', 'root', '-o', 'comm'], stderr=sp.PIPE,
                      stdout=sp.PIPE).stdout.read()
        root_procs = random.sample([x for x in str(rp).split('\\n')
                                    if not x.count('/') and not x.count('[') and  not x.count('CMD')],
                                   2)
        for p in root_procs:
            for u in ['root', current_user]:
                yield self.check_running_as, p, u, 'root'
