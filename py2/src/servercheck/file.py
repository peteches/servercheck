'''Servercheck module for various file related checks.
'''

import os
import stat
import grp
import pwd

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
        super(FileTester, self).__init__(item=file_path, **kwargs)

        self._stat = None

        self._ftypes = {
            'BLK': 'block device',
            'CHR': 'character device',
            'DIR': 'directory',
            'REG': 'regular file',
            'FIFO': 'fifo',
            'LNK': 'symlink',
            'SOCK': 'socket',
            'PORT': 'event port',
        }

        try:
            self._stat = os.stat(self._file_path)
        except OSError:
            try:
                os.lstat(self._file_path)
            except OSError:
                self.failed('does not exist.')
            else:
                self.failed('is a broken symlink.')

    def passed(self, msg):
        super(FileTester, self).passed('File {} {}'.format(self._file_path,
                                       msg))

    def failed(self, msg):
        super(FileTester, self).failed('File {} {}'.format(self._file_path,
                                       msg))

    @property
    def _type(self):
        if not self._stat:
            try:
                os.lstat(self._file_path)
            except OSError:
                return 'missing'
            else:
                return 'broken symlink'
        elif os.path.islink(self._file_path):
            return self._ftypes['LNK']
        else:
            for t in self._ftypes.keys():
                if getattr(stat, 'S_IS{}'.format(t))(self._stat.st_mode):
                    return self._ftypes[t]
                    break

    def exists(self):
        """Test if file exists

        """
        if self._type not in ['missing', 'broken symlink']:
            self.passed('exists.')

    def is_symlink(self):

        if self._type == self._ftypes['LNK']:
            self.passed('is a symlink.')
        elif self._type in ['missing', 'broken symlink']:
            return
        else:
            self.failed('is not a symlink.')

    def is_file(self):
        """Tests if file is a regular file


        """
        if self._type == self._ftypes['REG']:
            self.passed('is a regular file.')
        elif self._type in ['missing', 'broken symlink']:
            return
        else:
            msg = 'is not a regular file.'

            self.failed(msg)

    def is_dir(self):
        """Tests if file is a directory.


        """

        if self._type == self._ftypes['DIR']:
            self.passed('is a directory.')
        elif self._type in ['missing', 'broken symlink']:
            return
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
        if self._type in ['missing', 'broken symlink']:
            return

        file_perm = stat.S_IMODE(self._stat.st_mode)

        test_perm = stat.S_IMODE(int(str(mode), 8))

        if file_perm == test_perm:
            self.passed('has correct perms.')
        else:
            self.failed('does not have expected permissions.')

    def is_symlinked_to(self, dst):
        """Tests if file is a symlink pointing to dst.


        """
        if self._type in ['missing', 'broken symlink']:
            return

        if self._type == self._ftypes['LNK']:
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
        if self._type in ['missing', 'broken symlink']:
            return

        if string in open(self._file_path, 'r').read():
            self.passed('contains the string: "{}".'.format(string))
        else:
            self.failed('does not contain the string: "{}".'.format(string))

    def is_executable_by(self, x):
        if self._type in ['missing', 'broken symlink']:
            return

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

    def owner_is(self, u):
        pwstruct = None
        try:
            pwstruct = pwd.getpwuid(u)
        except TypeError:
            try:
                pwstruct = pwd.getpwnam(u)
            except KeyError:
                self.failed('no such user {}.'.format(u))
                return
            except TypeError:
                super().failed('Expected user described as int (uid) or str (user name).')
                return
        except KeyError:
            self.failed('no such uid {}.'.format(u))
            return

        if pwstruct.pw_uid == self._stat.st_uid:
            self.passed('is owned by {}.'.format(u))
        else:
            self.failed('is not owned by {}.'.format(u))

    def group_is(self, g):
        grstruct = None
        try:
            grstruct = grp.getgrgid(g)
        except ValueError:
            try:
                grstruct = grp.getgrnam(g)
            except KeyError:
                self.failed('no such group {}.'.format(g))
                return
            except TypeError:
                super().failed('Expected group described as int (gid) or str (group name).')
                return
        except KeyError:
            self.failed('no such gid {}.'.format(g))
            return

        if grstruct.gr_gid == self._stat.st_gid:
            self.passed('is group owned by {}.'.format(g))
        else:
            self.failed('is not group owned by {}.'.format(g))
