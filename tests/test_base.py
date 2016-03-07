#! /usr/bin/python3

import io
import logging

from testfixtures import LogCapture
from servercheck.base import BaseTester


class TestBase(object):

    """Tests Servercheck base class"""

    def __init__(self):
        """TODO: to be defined1. """
        self.logger = logging.getLogger('TestBase')

        self.passing_msg = 'Test has Passed'
        self.failing_msg = 'Test has Failed'

        self.report_logname = 'servercheck'

    def setup(self):
        self.log_capture = LogCapture()
        self.verbose_tester = BaseTester(verbose=True,
                                         item='verbose_test')

        self.default_tester = BaseTester(item='default_test')

        self.verbose_logname = '{}.{}.verbose_test'.format('servercheck',
                                                           self.verbose_tester.__class__.__name__)  # nopep8
        self.default_logname = '{}.{}.default_test'.format('servercheck',
                                                        self.default_tester.__class__.__name__)  # nopep8

    def teardown(self):
        self.log_capture.uninstall_all()

    def test_verbose_output_from_passing_test(self):
        self.verbose_tester.passed(self.passing_msg)

        self.log_capture.check(
            (self.verbose_logname,
             'INFO',
             '\033[1;32mPASS: {}\033[0m'.format(self.passing_msg)
             )
        )

    def test_default_output_from_passing_test(self):
        self.default_tester.passed(self.passing_msg)

        self.log_capture.check()

    def test_verbose_output_from_failing_test(self):
        self.verbose_tester.failed(self.failing_msg)

        self.log_capture.check(
            (self.verbose_logname,
             'WARNING',
             '\033[1;31mFAIL: {}\033[0m'.format(self.failing_msg)
             )
        )

    def test_default_output_from_failing_test(self):
        self.default_tester.failed(self.failing_msg)

        self.log_capture.check(
            (self.default_logname,
             'WARNING',
             '\033[1;31mFAIL: {}\033[0m'.format(self.failing_msg)
             )
        )

    def test_report_with_no_failing_tests(self):
        self.default_tester.passed(self.passing_msg)

        self.default_tester.report()

        self.log_capture.check(
            (self.report_logname,
             'INFO',
             '----- Report: -----\n\n'
             '\033[1;32mAll tests passed, YAY!\033[0m\n\n'
             '-------------------',
             )
        )

    def test_report_with_one_failing_test(self):
        self.default_tester.failed(self.failing_msg)

        self.default_tester.report()

        self.log_capture.check(
            (self.default_logname,
             'WARNING',
             '\033[1;31mFAIL: {}\033[0m'.format(self.failing_msg)
             ),
            (self.report_logname,
             'WARNING',
             '----- Report: -----\n\n'
             '\033[1;31mFAIL: {}\033[0m\n\n'
             '-------------------'.format(self.failing_msg),
             ),
        )

    def test_report_with_multiple_failing_tests(self):
        self.default_tester.failed(self.failing_msg)
        self.default_tester.failed(self.failing_msg)

        self.default_tester.report()

        self.log_capture.check(
            (self.default_logname,
             'WARNING',
             '\033[1;31mFAIL: {}\033[0m'.format(self.failing_msg)
             ),
            (self.default_logname,
             'WARNING',
             '\033[1;31mFAIL: {}\033[0m'.format(self.failing_msg)
             ),
            (self.report_logname,
             'WARNING',
             '----- Report: -----\n\n'
             '\033[1;31mFAIL: {}\033[0m\n'
             '\033[1;31mFAIL: {}\033[0m\n\n'
             '-------------------'.format(self.failing_msg,
                                          self.failing_msg)
             )
        )
