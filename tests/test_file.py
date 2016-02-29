#! /usr/bin/python3

import os
import tempfile
import servercheck
import itertools
import stat
import random

from nose.tools import *
from testfixtures import LogCapture


class TestFile:

    def __init__(self):
        self.tmpdir = tempfile.mkdtemp()
        self.file_that_exists = tempfile.mkstemp(dir=self.tmpdir)[1]
        self.file_that_does_not_exist = os.path.join(self.tmpdir,
                                                     'does_not_exist')
        os.chmod(self.file_that_exists, 0o644)
        self.link = os.path.join(self.tmpdir, 'symlink')

        os.symlink(self.file_that_exists, self.link)

        self.test_string = 'Hello, looking for me?'
        self.missing_string = 'HAHA you will never catch me!!'

        self.pass_str = '\033[1;32mPASS: File {} {}\033[0m'
        self.fail_str = '\033[1;31mFAIL: File {} {}\033[0m'

        self.log_name = 'servercheck.FileTester.{}'

        with open(self.file_that_exists, 'w') as fd:
            fd.writelines([self.test_string])

    def setup(self):
        self.file_exists = servercheck.FileTester(self.file_that_exists,
                                                  verbose=True)
        self.file_does_not_exist = servercheck.FileTester(self.file_that_does_not_exist,  # nopep8
                                                          verbose=True)
        self.dir = servercheck.FileTester(self.tmpdir,
                                          verbose=True)
        self.symlink = servercheck.FileTester(self.link,
                                              verbose=True)

        self.log_capture = LogCapture()

    def teardown(self):
        self.log_capture.uninstall()

    def test_file_path_attribute(self):
        assert_equal(self.file_exists._file_path, self.file_that_exists)

    def test_true_file_exists(self):
        self.file_exists.exists()

        self.log_capture.check(
            (self.log_name.format(self.file_that_exists),
             'INFO',
             self.pass_str.format(self.file_that_exists,
                                  'exists.'),
             ),
        )

    def test_false_file_exists(self):
        self.file_does_not_exist.exists()

        self.log_capture.check(
            (self.log_name.format(self.file_that_does_not_exist),
             'WARNING',
             self.fail_str.format(self.file_that_does_not_exist,
                                  'does not exist.'),
             ),
        )

    def generate_file_perms(self, num):

        def tup2str(t):
            return ''.join(map(str, t))

        rwx_perms = set(map(lambda x: x[0] | x[1] | x[2] | x[3],
                            itertools.combinations_with_replacement([4, 2, 1, 0],  # nopep8
                                                                    4)))
        perms = [tup2str(x)
                 for x in itertools.permutations(rwx_perms, 4)]

        random.shuffle(perms)

        return perms[1:num]

    def check_incorrect_file_mode(self, file_mode, test_mode):
        m = stat.S_IMODE(int(str(file_mode), 8))
        os.chmod(self.file_that_exists, m)
        ft = servercheck.FileTester(self.file_that_exists,
                                    verbose=True)
        ft.mode(test_mode)

        self.log_capture.check(
            (self.log_name.format(self.file_that_exists),
             'WARNING',
             self.fail_str.format(self.file_that_exists,
                                  'does not have expected permissions.')
             ),
        )

    def check_correct_file_mode(self, mode):
        m = stat.S_IMODE(int(str(mode), 8))
        os.chmod(self.file_that_exists, m)
        ft = servercheck.FileTester(self.file_that_exists,
                                    verbose=True)
        ft.mode(mode)

        self.log_capture.check(
            (self.log_name.format(self.file_that_exists),
             'INFO',
             self.pass_str.format(self.file_that_exists,
                                  'has correct perms.')
             ),
        )

    def test_correct_file_perms(self):
        for p in self.generate_file_perms(50):
            yield self.check_correct_file_mode, p

    def test_incorrect_file_perms(self):
        for x, y in zip(self.generate_file_perms(50),
                        self.generate_file_perms(50)):
            yield self.check_incorrect_file_mode, x, y

    def test_true_file_is_file(self):
        self.file_exists.is_file()

        self.log_capture.check(
            (self.log_name.format(self.file_that_exists),
             'INFO',
             self.pass_str.format(self.file_that_exists,
                                  'is a regular file.')
             ),
        )

    def test_false_symlink_is_file(self):
        self.symlink.is_file()

        self.log_capture.check(
            (self.log_name.format(self.link),
             'WARNING',
             self.fail_str.format(self.link,
                                  'is not a regular file. {} is a symlink.'.format(self.link))  # nopep8
             ),
        )

    def test_false_file_is_file(self):
        self.dir.is_file()

        self.log_capture.check(
            (self.log_name.format(self.tmpdir),
             'WARNING',
             self.fail_str.format(self.tmpdir,
                                  'is not a regular file. {} is a directory.'.format(self.tmpdir))  # nopep8
             ),
        )

    def test_true_file_is_dir(self):
        self.dir.is_dir()

        self.log_capture.check(
            (self.log_name.format(self.tmpdir),
             'INFO',
             self.pass_str.format(self.tmpdir,
                                  'is a directory.')
             ),
        )

    def test_false_symlink_is_dir(self):
        self.symlink.is_dir()

        self.log_capture.check(
            (self.log_name.format(self.link),
             'WARNING',
             self.fail_str.format(self.link,
                                  'is not a directory. {} is a symlink.'.format(self.link))  # nopep8
             ),
        )

    def test_false_file_is_dir(self):
        self.file_exists.is_dir()

        self.log_capture.check(
            (self.log_name.format(self.file_that_exists),
             'WARNING',
             self.fail_str.format(self.file_that_exists,
                                  'is not a directory. {} is a regular file.'.format(self.file_that_exists))  # nopep8
             ),
        )

    def test_false_file_is_not_a_symlink(self):
        self.file_exists.is_symlinked_to(self.file_that_exists)

        self.log_capture.check(
            (self.log_name.format(self.file_that_exists),
             'WARNING',
             self.fail_str.format(self.file_that_exists,
                                  'is not a symlink.')
             ),
        )

    def test_true_file_is_symlinked_to(self):
        self.symlink.is_symlinked_to(self.file_that_exists)

        self.log_capture.check(
            (self.log_name.format(self.link),
             'INFO',
             self.pass_str.format(self.link,
                                  'is symlinked to {}.'.format(self.file_that_exists))  # nopep8
             ),
        )

    def test_false_file_is_symlinked_to(self):
        self.symlink.is_symlinked_to(self.file_that_does_not_exist)  # nopep8

        self.log_capture.check(
            (self.log_name.format(self.link),
             'WARNING',
             self.fail_str.format(self.link,
                                  'is not symlinked to {}.'.format(self.file_that_does_not_exist))  # nopep8
             ),
        )

    def test_true_file_has_string(self):
        self.file_exists.has_string(self.test_string)

        self.log_capture.check(
            (self.log_name.format(self.file_that_exists),
             'INFO',
             self.pass_str.format(self.file_that_exists,
                                  'contains the string: "{}".'.format(self.test_string))  # nopep8
             ),
        )

    def test_false_file_has_string(self):
        self.file_exists.has_string(self.missing_string)

        self.log_capture.check(
            (self.log_name.format(self.file_that_exists),
             'WARNING',
             self.fail_str.format(self.file_that_exists,
                                  'does not contain the string: "{}".'.format(self.missing_string))  # nopep8
             ),
        )

    def check_excecute_perms(self, p, u):
        os.chmod(self.file_that_exists, int(str(p), 8))

        ft = servercheck.FileTester(self.file_that_exists,
                                    verbose=True)
        ft.is_executable_by(u)

        if u == 'user':
            mask = stat.S_IXUSR
        elif u == 'group':
            mask = stat.S_IXGRP
        elif u == 'other':
            mask = stat.S_IXOTH

        if int(str(p), 8) & mask:
            lvl = 'INFO'
            msg = self.pass_str.format(self.file_that_exists,
                                       'is executable by {}.'.format(u))
        else:
            lvl = 'WARNING'
            msg = self.fail_str.format(self.file_that_exists,
                                       'is not executable by {}.'.format(u))

        self.log_capture.check(
            (self.log_name.format(self.file_that_exists),
             lvl,
             msg
             )
        )

    def test_executable_generator(self):
        for i in ['user', 'group', 'other']:
            for p in self.generate_file_perms(20):
                yield self.check_excecute_perms, p, i
