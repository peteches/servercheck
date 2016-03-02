#! /usr/bin/python3

import os
import tempfile
import servercheck
import itertools
import stat
import random
import string

from nose.tools import *
from testfixtures import LogCapture


class TestFileTester(servercheck.FileTester):

    __test__ = False

    def __init__(self, fp, **kwargs):
        super().__init__(fp,
                         verbose=True,
                         **kwargs)


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

        self.log_name = 'servercheck.TestFileTester.{}'

        with open(self.file_that_exists, 'w') as fd:
            fd.writelines([self.test_string])

        self._file_types = ['reg',
                            'dir',
                            'symlink',
                            'broken_symlink',
                            'missing',
                            ]

        self._file_type = {
            'reg': 'regular file',
            'dir': 'directory',
            'symlink': 'symlink',
            'broken_symlink': 'symlink',
        }

    def setup(self):
        self.log_capture = LogCapture()

    def teardown(self):
        self.log_capture.uninstall()

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

    def create_file(self, ft='reg', mode=644, content=None):
        if ft == 'reg':
            path = tempfile.mkstemp(dir=self.tmpdir)[1]
        elif ft == 'dir':
            path = tempfile.mkdtemp(dir=self.tmpdir)
        elif ft == 'symlink':
            link_dst = tempfile.mkstemp(dir=self.tmpdir)[1]
            path = tempfile.mktemp(dir=self.tmpdir)
            os.symlink(link_dst, path)
        elif ft == 'broken_symlink':
            link_dst = tempfile.mkstemp(dir=self.tmpdir)[1]
            path = tempfile.mktemp(dir=self.tmpdir)
            os.symlink(link_dst, path)
            os.remove(link_dst)
        elif ft == 'missing':
            path = tempfile.mktemp()

        if ft in ['reg', 'symlink'] \
                and content:
            with open(path, 'w') as fd:
                fd.write(content)

        if ft not in ['missing', 'broken_symlink']:
            os.chmod(path,
                     int(str(mode), 8))

        return path

    def check_file_path_attribute(self, ft):
        p = self.create_file(ft)
        filetester = TestFileTester(p)
        assert_equal(filetester._file_path, p)

    def test_file_path_attributes(self):
        for i in self._file_types:
            yield self.check_file_path_attribute, i

    def check_exists(self, file_type):
        p = self.create_file(ft=file_type)
        filetester = TestFileTester(p)

        filetester.exists()

        if file_type == 'missing':
            lvl = 'WARNING'
            msg = self.fail_str.format(p, 'does not exist.')
        else:
            lvl = 'INFO'
            msg = self.pass_str.format(p, 'exists.')

        self.log_capture.check(
            (
                self.log_name.format(p),
                lvl,
                msg,
            ),
        )

    def test_exists_checks(self):
        for file_type in self._file_types:
            yield self.check_exists, file_type

    def check_is_file(self, file_type):
        p = self.create_file(ft=file_type)
        filetester = TestFileTester(p)
        if file_type == 'reg':
            lvl = 'INFO'
            msg = self.pass_str.format(p, 'is a regular file.')
        elif file_type == 'missing':
            lvl = 'WARNING'
            msg = self.fail_str.format(p, 'does not exist.')
        else:
            lvl = 'WARNING'
            msg = self.fail_str.format(p, 'is not a regular file.')

        filetester.is_file()

        self.log_capture.check(
            (
                self.log_name.format(p),
                lvl,
                msg,
            ),
        )

    def test_is_file_checks(self):
        for file_type in self._file_types:
            yield self.check_is_file, file_type

    def check_file_is_dir(self, file_type):
        p = self.create_file(ft=file_type)

        filetester = TestFileTester(p)

        if file_type == 'dir':
            lvl = 'INFO'
            msg = self.pass_str.format(p,
                                       'is a {}.'.format(self._file_type[file_type]))  # nopep8
        elif file_type == 'missing':
            lvl = 'WARNING'
            msg = self.fail_str.format(p, 'does not exist.')
        else:
            lvl = 'WARNING'
            msg = self.fail_str.format(p, 'is not a directory.'
                                       ' {} is a {}.'.format(p,
                                                            self._file_type[file_type]))  # nopep8

        filetester.is_dir()

        self.log_capture.check(
            (self.log_name.format(p),
             lvl,
             msg,
             ),
        )

    def test_is_dir_checks(self):
        for ft in self._file_types:
            yield self.check_file_is_dir, ft

    def check_is_symlink(self, file_type):
        p = self.create_file(ft=file_type)

        filetester = TestFileTester(p)

        if file_type in ['symlink', 'broken_symlink']:
            lvl = 'INFO'
            msg = self.pass_str.format(p, 'is a symlink.')
        elif file_type == 'missing':
            lvl = 'WARNING'
            msg = self.fail_str.format(p, 'does not exist.')
        else:
            lvl = 'WARNING'
            msg = self.fail_str.format(p, 'is not a symlink.')

        filetester.is_symlink()

        self.log_capture.check(
            (
                self.log_name.format(p),
                lvl,
                msg,
            ),
        )

    def test_is_symlink_checks(self):
        for ft in self._file_types:
            yield self.check_is_symlink, ft

    def check_true_is_symlinked_to(self, file_type):
        src = self.create_file(file_type)
        dst = tempfile.mktemp()
        os.symlink(src, dst)

        filetester = TestFileTester(dst)

        filetester.is_symlinked_to(src)

        self.log_capture.check(
            (
                self.log_name.format(dst),
                'INFO',
                self.pass_str.format(dst,
                                     'is symlinked to {}.'.format(src))
            ),
        )

    def test_is_symlinked_to(self):
        for ft in [x for x in self._file_types
                   if x != 'missing']:
            yield self.check_true_is_symlinked_to, ft

    def check_incorrect_file_mode(self, ft, file_mode, test_mode):
        p = self.create_file(ft, mode=file_mode)
        filetester = TestFileTester(p)

        filetester.mode(test_mode)

        if ft == 'missing':
            msg = 'does not exist.'
        else:
            msg = 'does not have expected permissions.'

        self.log_capture.check(
            (self.log_name.format(p),
             'WARNING',
             self.fail_str.format(p, msg)
             ),
        )

    def test_incorrect_file_perms(self):
        for t in self._file_types:
            for x, y in zip(self.generate_file_perms(50),
                            self.generate_file_perms(50)):
                yield self.check_incorrect_file_mode, t, x, y

    def check_correct_file_mode(self, mode):
        m = stat.S_IMODE(int(str(mode), 8))
        os.chmod(self.file_that_exists, m)
        ft = TestFileTester(self.file_that_exists)
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

    def check_excecute_perms(self, p, u):
        os.chmod(self.file_that_exists, int(str(p), 8))

        ft = TestFileTester(self.file_that_exists)
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

    def test_file_has_string(self):
        rand_string = ''.join(random.sample(string.ascii_letters, 20))
        p = self.create_file('reg', content=rand_string)

        filetester = TestFileTester(p)

        filetester.contains_string(rand_string)

        self.log_capture.check(
            (
                self.log_name.format(p),
                'INFO',
                self.pass_str.format(p, 'contains the string: "{}".'.format(rand_string))  # nopep8
            )
        )

    def test_false_file_has_string(self):
        string_in_file = ''.join(random.sample(string.ascii_letters, 20))
        string_to_search_for = ''.join(random.sample(string.ascii_letters, 25))
        p = self.create_file('reg', content=string_in_file)

        filetester = TestFileTester(p)

        filetester.contains_string(string_to_search_for)

        self.log_capture.check(
            (
                self.log_name.format(p),
                'WARNING',
                self.fail_str.format(p, 'does not contain the string: "{}".'.format(string_to_search_for))  # nopep8
            )
        )
