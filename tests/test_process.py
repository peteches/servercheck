import psutil
import logging
import subprocess as sp
import servercheck

from nose.tools import *
from testfixtures import LogCapture


class TestProcessTester(servercheck.ProcessTester):

    __test__ = False

    def __init__(self, *args, **kwargs):
        super().__init__(verbose=True,
                         *args,
                         **kwargs)


class TestProcess:

    def __init__(self, **kwargs):
        self.log_name = 'servercheck.TestProcessTester.{}'

        self.pass_str = '\033[1;32mPASS: Process "{}" {}\033[0m'
        self.fail_str = '\033[1;31mFAIL: Process "{}" {}\033[0m'

    def setup(self):

        self.log_capture = LogCapture()

        self.processes = [
            sp.Popen(['sleep', '200']),
        ]

    def teardown(self):
        self.log_capture.uninstall()

        for p in self.processes:
            p.kill()

    def test_pname_set_correctly(self):

        pname = self.processes[0].args[0]
        pt = TestProcessTester(pname)

        assert_true(pname, pt.pname)

    def test_process_is_running(self):
        pname = self.processes[0].args[0]
        pt = TestProcessTester(pname)

        pt.is_running()

        self.log_capture.check(
            (
                self.log_name.format(pname),
                'INFO',
                self.pass_str.format(pname,
                                     'is running.'),
            ),
        )

    def test_process_is_not_running(self):

        pname = 'missing-process'
        pt = TestProcessTester(pname)

        pt.is_running()

        self.log_capture.check(
            (
                self.log_name.format(pname),
                'WARNING',
                self.fail_str.format(pname,
                                     'is not running.'),
            ),
        )
