# This modue simulates executeCommandLine with a timeout. It will return a tuple (stdoutdata, stdouterr).
import subprocess, threading

class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.data = None

    def run(self, timeout):
        def target():
            self.process = subprocess.Popen(self.cmd,stdout=subprocess.PIPE)
            self.data = self.process.communicate()

        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()
        return self.data
