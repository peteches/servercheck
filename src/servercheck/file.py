'''Servercheck module for various file related checks.
'''

import os
import stat


class File(object):
    """File test object that provides several methods for
    testing the properties of the given file.
    """

    def __init__(self, file_path):
        """File test object that provides several methods
        for testing the properties of a file

        :param str file_path: path to file ( Does **NOT** need to exist )

        :return: `servercheck.File` object

        """
        self._file_path = file_path

        if self.exists():
            self._stat = os.stat(self._file_path)

    def exists(self):
        """Test if file exists

        >>> f = File('/etc/hosts')
        >>> f.exists()
        True
        >>>

        """
        try:
            return os.path.exists(self._file_path)
        except:
            return False

    def is_file(self):
        """Tests if file is a regular file

        >>> f = File('/etc/hosts')
        >>> f.is_file()
        True
        >>>

        """
        return os.path.isfile(self._file_path)

    def is_dir(self):
        """Tests if file is a directory.

        >>> f = File('/tmp')
        >>> f.is_dir()
        True
        >>>

        """
        return os.path.isdir(self._file_path)

    def mode(self, mode):
        """Tests if file permissions match mode.

        :param int mode: File perms in octal

        >>> f = File('/etc')
        >>> f.mode(755)
        True
        >>>

        """
        file_perm = stat.S_IMODE(self._stat.st_mode)
        test_perm = stat.S_IMODE(int(str(mode), 8))

        return file_perm == test_perm

    def is_symlinked_to(self, dst):
        """Tests if file is a symlink pointing to dst.

        >>> f = File('/bin')
        >>> f.is_symlinked_to('/usr/bin')
        True
        >>>

        """
        if os.path.islink(self._file_path):
            real_path = os.path.realpath(self._file_path)
            test_path = os.path.realpath(dst)

            return real_path == test_path

    def has_string(self, string):
        """Tests if file has a line containing string.

        >>> f = File('/etc/resolv.conf')
        >>> f.has_string('nameserver')
        True
        >>>

        """
        if string in open(self._file_path, 'r').read():
            return True
        else:
            return False
