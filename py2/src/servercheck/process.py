import psutil

from servercheck.base import BaseTester


class ProcessTester(BaseTester):

    def __init__(self, pname, **kwargs):

        self.pname = pname
        super(ProcessTester, self).__init__(item=pname, **kwargs)

        self.processes = []

        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict()
            except psutil.NoSuchProcess:
                pass

            if self.pname in [pinfo['name'],
                              pinfo['exe']]:
                self.processes.append(pinfo)

    def passed(self, msg):
        super(ProcessTester, self).passed('Process "{}" {}'.format(self.pname,
                                                msg))

    def failed(self, msg):
        super(ProcessTester, self).failed('Process "{}" {}'.format(self.pname,
                                                msg))

    def is_running(self):
        if self.processes:
            self.passed('is running.')
        else:
            self.failed('is not running.')

    def is_running_as(self, user):
        users = set([x['username'] for x in self.processes
                     if x['username'] == user])

        if len(users) == 0:
            self.failed('is not running as {}.'.format(user))
        elif len(users) == 1:
            self.passed('is running as {}.'.format(user))

        else:

            self.failed('Some process run as {}.'.format(user))
