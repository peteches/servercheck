'''Servercheck module for various file related checks.
'''

import os
import stat


class File(object):
    """Docstring for File. """

    def __init__(self, file_path):
        """TODO: to be defined1.

        :file_path: TODO

        """
        self._file_path = file_path

        if self.exists():
            self._stat = os.stat(self._file_path)

    def exists(self):
        try:
            return os.path.exists(self._file_path)
        except:
            return False

    def is_file(self):
        return os.path.isfile(self._file_path)

    def is_dir(self):
        return os.path.isdir(self._file_path)

    def mode(self, mode):
        file_perm = stat.S_IMODE(self._stat.st_mode)
        test_perm = stat.S_IMODE(int(str(mode), 8))

        return file_perm == test_perm

    def is_symlinked_to(self, dst):
        if os.path.islink(self._file_path):
            real_path = os.path.realpath(self._file_path)
            test_path = os.path.realpath(dst)

            return real_path == test_path

    def has_string(self, string):
        if string in open(self._file_path, 'r').read():
            return True
        else:
            return False
