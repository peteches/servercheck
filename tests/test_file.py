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

    def setup(self):
        with open(self.file_that_exists, 'w') as fd:
            fd.writelines([self.test_string])

        self.f = servercheck.File(self.file_that_exists)
        self.no_f = servercheck.File(self.file_that_does_not_exist)

        self.d = servercheck.File(self.tmpdir)

        self.s = servercheck.File(self.link)

    def test_true_file_exists(self):
        assert_true(self.f.exists(), 'File exists')

    def test_false_file_exists(self):
        assert_false(self.no_f.exists(), 'File Missing')

    def test_true_file_mode(self):
        assert_true(self.f.mode(644))

    def test_false_file_mode(self):
        assert_false(self.f.mode(775))

    def test_true_file_is_file(self):
        assert_true(self.f.is_file())

    def test_false_file_is_file(self):
        assert_false(self.d.is_file())

    def test_true_file_is_dir(self):
        assert_true(self.d.is_dir())

    def test_false_file_is_dir(self):
        assert_false(self.f.is_dir())

    def test_true_file_is_symlinked_to(self):
        assert_true(self.s.is_symlinked_to(self.file_that_exists))

    def test_false_file_is_symlinked_to(self):
        assert_false(self.s.is_symlinked_to(self.file_that_does_not_exist))

    def test_true_file_has_string(self):
        assert_true(self.f.has_string(self.test_string))

    def test_false_file_has_string(self):
        assert_false(self.f.has_string(self.missing_string))
