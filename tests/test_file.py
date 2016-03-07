#! /usr/bin/python3

import os
import tempfile
import servercheck
import itertools
import stat
import random
import string
import pwd

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
                            'broken symlink',
                            'missing',
                            ]

        self._file_type = {
            'reg': 'regular file',
            'dir': 'directory',
            'symlink': 'symlink',
            'broken symlink': 'symlink',
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
        elif ft == 'broken symlink':
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

        if ft not in ['missing', 'broken symlink']:
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
        elif file_type == 'broken symlink':
            lvl = 'WARNING'
            msg = self.fail_str.format(p, 'is a broken symlink.')
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
        elif file_type == 'broken symlink':
            lvl = 'WARNING'
            msg = self.fail_str.format(p, 'is a broken symlink.')
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
        elif file_type == 'broken symlink':
            lvl = 'WARNING'
            msg = self.fail_str.format(p, 'is a broken symlink.')
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

        if file_type == 'symlink':
            lvl = 'INFO'
            msg = self.pass_str.format(p, 'is a symlink.')
        elif file_type == 'missing':
            lvl = 'WARNING'
            msg = self.fail_str.format(p, 'does not exist.')
        elif file_type == 'broken symlink':
            lvl = 'WARNING'
            msg = self.fail_str.format(p, 'is a broken symlink.')
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
                   if x not in ['broken symlink',
                                'missing']]:
            yield self.check_true_is_symlinked_to, ft

    def check_file_mode(self, ft, file_mode, test_mode):
        p = self.create_file(ft, mode=file_mode)
        filetester = TestFileTester(p)

        filetester.mode(test_mode)

        if ft == 'missing':
            lvl = 'WARNING'
            msg = self.fail_str.format(p, 'does not exist.')
        elif ft == 'broken symlink':
            lvl = 'WARNING'
            msg = self.fail_str.format(p, 'is a broken symlink.')
        elif file_mode != test_mode:
            lvl = 'WARNING'
            msg = self.fail_str.format(p,
                                       'does not have expected permissions.')
        elif file_mode == test_mode:
            lvl = 'INFO'
            msg = self.pass_str.format(p, 'has correct perms.')

        self.log_capture.check(
            (self.log_name.format(p),
             lvl,
             msg,
             ),
        )

    def test_file_perms(self):
        for t in self._file_types:
            for x, y in zip(self.generate_file_perms(50),
                            self.generate_file_perms(50)):
                yield self.check_file_mode, t, x, y

            for p in self.generate_file_perms(50):
                yield self.check_file_mode, t, p, p

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

    def check_owner_is(self, path, user, expected_result):
        filetester = TestFileTester(path)

        filetester.owner_is(user)

        if expected_result:
            lvl = 'INFO'
            msg = self.pass_str.format(path, 'is owned by {}.'.format(user))
        else:
            lvl = 'WARNING'
            msg = self.fail_str.format(path,
                                       'is not owned by {}.'.format(user))

        self.log_capture.check(
            (
                self.log_name.format(path),
                lvl,
                msg,
            ),
        )

    def check_owner_is_args(self, user):
        fail_str = '\033[1;31mFAIL: {}\033[0m'

        p = self.create_file()
        filetester = TestFileTester(p)

        try:
            if user.isdigit():
                user = int(user)
                msg = self.fail_str.format(p, 'no such uid {}.'.format(user))
            else:
                msg = self.fail_str.format(p, 'no such user {}.'.format(user))
        except AttributeError:
            msg = fail_str.format('Expected user described as int (uid) or str (user name).')  # nopep8

        filetester.owner_is(user)

        self.log_capture.check(
            (
                self.log_name.format(p),
                'WARNING',
                msg,
            ),
        )

    def test_file_ownership(self):

        users = [
            pwd.getpwuid(os.getuid()),
            pwd.getpwnam('root'),
        ]

        for f in [x.pw_dir for x in users]:
            fuid = os.stat(f).st_uid
            for u in [y.pw_uid for y in users]:
                if fuid == u:
                    b = True
                else:
                    b = False
                yield self.check_owner_is, f, u, b

            for u in [y.pw_name for y in users]:
                if fuid == pwd.getpwnam(u).pw_uid:
                    b = True
                else:
                    b = False
                yield self.check_owner_is, f, u, b

        users = ['fdls', 'lpok']
        uids = ['7876', '9098', '8876']

        for u in users + uids:
            yield self.check_owner_is_args, u
