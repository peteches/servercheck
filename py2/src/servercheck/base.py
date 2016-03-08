#! /usr/bin/python3

import logging
import sys

from io import StringIO


class PassFilter(logging.Filter):

    def filter(self, record):

        if record.levelname == 'INFO':
            return 1
        return 0


class FailFilter(logging.Filter):

    def filter(self, record):

        if record.levelname == 'WARNING':
            return 1
        return 0


class BaseReporter(object):

    """Reporter Object to collate the failed tests"""

    def __init__(self):

        self.report_logger = logging.getLogger('servercheck')

        self.failed_tests = StringIO()

        report_handler = logging.StreamHandler(self.failed_tests)
        report_handler.addFilter(FailFilter())
        report_handler.setLevel(logging.WARNING)

        self.report_logger.addHandler(report_handler)

    def report(self):
        failed_tests = self.failed_tests.getvalue()

        msg = '----- Report: -----\n\n'
        if failed_tests:
            msg += self.failed_tests.getvalue()
            log_level = 'warn'
        else:
            msg += '\033[1;32mAll tests passed, YAY!\033[0m\n'
            log_level = 'info'

        msg += '\n-------------------'

        getattr(self.report_logger, log_level)(msg)


class BaseTester(BaseReporter):

    """Docstring for BaseTester. """

    def __init__(self, verbose=False, item=None):
        """Base Class for all testing classes

        Sets up common functionality and handles shipping logs.

        :verbose: `Bool` if true show passing messages too.
        :item: Name of what is being tested, eg file path, process name etc.

        """

        super(BaseTester, self).__init__()

        if item is None:
            import string as s
            import random as r
            item = ''.join([r.choice(s.ascii_letters + s.digits)
                            for n in range(10)])

        self.log_id = 'servercheck.{}.{}'.format(self.__class__.__name__,
                                                 item)
        self._logger = logging.getLogger(self.log_id)

        if verbose:
            self._logger.setLevel(logging.INFO)
        else:
            self._logger.setLevel(logging.WARNING)

        pass_handler = logging.StreamHandler(sys.stdout)
        fail_handler = logging.StreamHandler(sys.stdout)

        pass_handler.addFilter(PassFilter())
        fail_handler.addFilter(FailFilter())

        self._logger.addHandler(pass_handler)
        self._logger.addHandler(fail_handler)

    def passed(self, msg):
        self._logger.info(u'\033[1;32mPASS: {}\033[0m'.format(msg))

    def failed(self, msg):
        self._logger.warn(u'\033[1;31mFAIL: {}\033[0m'.format(msg))
