import psutil

from servercheck.base import BaseTester


class ProcessTester(BaseTester):

    def __init__(self, pname, **kwargs):

        self.pname = pname
        super().__init__(item=pname, **kwargs)

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
        super().passed('Process "{}" {}'.format(self.pname,
                                                msg))

    def failed(self, msg):
        super().failed('Process "{}" {}'.format(self.pname,
                                                msg))

    def is_running(self):
        if self.processes:
            self.passed('is running.')
        else:
            self.failed('is not running.')
