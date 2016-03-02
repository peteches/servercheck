'''Servercheck module for various file related checks.
'''

import os
import stat

from servercheck.base import BaseTester


class FileTester(BaseTester):
    """File test object that provides several methods for
    testing the properties of the given file.
    """

    def __init__(self, file_path, **kwargs):
        """File test object that provides several methods
        for testing the properties of a file

        :param str file_path: path to file ( Does **NOT** need to exist )

        :return: `servercheck.File` object

        """
        self._file_path = file_path
        super().__init__(item=file_path, **kwargs)

        try:
            self._stat = os.lstat(self._file_path)
        except FileNotFoundError:
            self._stat = None

    def passed(self, msg):
        super().passed('File {} {}'.format(self._file_path,
                                           msg))

    def failed(self, msg):
        super().failed('File {} {}'.format(self._file_path,
                                           msg))
    def exists(self):
        """Test if file exists

        """
        if self._stat:
            self.passed('exists.')
        else:
            self.failed('does not exist.')

    def is_symlink(self):

        if not self._stat:
            self.failed('does not exist.')
            return

        if stat.S_ISLNK(self._stat.st_mode):
            self.passed('is a symlink.')
        else:
            self.failed('is not a symlink.')

    def is_file(self):
        """Tests if file is a regular file


        """
        if not self._stat:
            self.failed('does not exist.')
            return

        if os.path.isfile(self._file_path) \
                and not os.path.islink(self._file_path):
            self.passed('is a regular file.')
        else:
            msg = 'is not a regular file.'

            self.failed(msg)

    def is_dir(self):
        """Tests if file is a directory.


        """
        if not self._stat:
            self.failed('does not exist.')
            return

        if os.path.isdir(self._file_path) \
                and not os.path.islink(self._file_path):
            self.passed('is a directory.')
        else:
            msg = 'is not a directory. {} '.format(self._file_path)

            if os.path.islink(self._file_path):
                msg += 'is a symlink.'
            elif os.path.isfile(self._file_path):
                msg += 'is a regular file.'

            self.failed(msg)

    def mode(self, mode):
        """Tests if file permissions match mode.

        :param int mode: File perms


        """
        file_perm = stat.S_IMODE(self._stat.st_mode)
        test_perm = stat.S_IMODE(int(str(mode), 8))

        if file_perm == test_perm:
            self.passed('has correct perms.')
        else:
            self.failed('does not have expected permissions.')

    def is_symlinked_to(self, dst):
        """Tests if file is a symlink pointing to dst.


        """
        if os.path.islink(self._file_path):
            real_path = os.path.realpath(self._file_path)
            test_path = os.path.realpath(dst)

            if real_path == test_path:
                self.passed('is symlinked to {}.'.format(dst))
            else:
                self.failed('is not symlinked to {}.'.format(dst))

        else:
            self.failed('is not a symlink.')

    def contains_string(self, string):
        """Tests if file has a line containing string.


        """
        if string in open(self._file_path, 'r').read():
            self.passed('contains the string: "{}".'.format(string))
        else:
            self.failed('does not contain the string: "{}".'.format(string))

    def is_executable_by(self, x):
        file_perm = stat.S_IMODE(self._stat.st_mode)

        if x == 'user':
            mask = stat.S_IXUSR
        elif x == 'group':
            mask = stat.S_IXGRP
        elif x == 'other':
            mask = stat.S_IXOTH

        if file_perm & mask:
            self.passed('is executable by {}.'.format(x))
        else:
            self.failed('is not executable by {}.'.format(x))
