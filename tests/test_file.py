#! /usr/bin/python3

import os
import tempfile
import servercheck

from nose.tools import *


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

        with open(self.file_that_exists, 'w') as fd:
            fd.writelines([self.test_string])

    def setup(self):
        self.file_exists = servercheck.File(self.file_that_exists)
        self.file_does_not_exist = servercheck.File(self.file_that_does_not_exist)  # nopep8

        self.dir = servercheck.File(self.tmpdir)

        self.symlink = servercheck.File(self.link)

    def test_true_file_exists(self):
        assert_true(self.file_exists.exists(), 'File exists')

    def test_false_file_exists(self):
        assert_false(self.file_does_not_exist.exists(), 'File Missing')

    def test_true_file_mode(self):
        assert_true(self.file_exists.mode(644))

    def test_false_file_mode(self):
        assert_false(self.file_exists.mode(775))

    def test_true_file_is_file(self):
        assert_true(self.file_exists.is_file())

    def test_false_file_is_file(self):
        assert_false(self.dir.is_file())

    def test_true_file_is_dir(self):
        assert_true(self.dir.is_dir())

    def test_false_file_is_dir(self):
        assert_false(self.file_exists.is_dir())

    def test_true_file_is_symlinked_to(self):
        assert_true(self.symlink.is_symlinked_to(self.file_that_exists))

    def test_false_file_is_symlinked_to(self):
        assert_false(self.symlink.is_symlinked_to(self.file_that_does_not_exist))  # nopep8

    def test_true_file_has_string(self):
        assert_true(self.file_exists.has_string(self.test_string))

    def test_false_file_has_string(self):
        assert_false(self.file_exists.has_string(self.missing_string))
