import logging
import time

from daemon import runner


class TestDaemon():

    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/home/jacob/projects/terMail/daemon.log'
        self.stderr_path = '/home/jacob/projects/terMail/daemon.log'
        self.pidfile_path = '/run/terMail.pid'
        self.pidfile_timeout = 5

    def run(self):
        while True:
            logger.error("Test Daemon")
            time.sleep(10)


app = TestDaemon()
logger = logging.getLogger("DaemonLog")
logger.setLevel(logging.INFO)
handler = logging.FileHandler('/home/jacob/projects/terMail/daemon.log')
logger.addHandler(handler)

daemon_runner = runner.DaemonRunner(app)
daemon_runner.daemon_context.files_preserve = [handler.stream]
daemon_runner.do_action()
