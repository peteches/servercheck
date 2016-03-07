import psutil

from servercheck.base import BaseTester


class ProcessTester(BaseTester):

    def __init__(self, pname, **kwargs):

        self.pname = pname
        super().__init__(item=pname, **kwargs)

        self.processes = [x for x in psutil.process_iter()
                          if x.name() == self.pname]

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

