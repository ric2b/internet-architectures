import threading
import time


class TimedEvent:
    def __init__(self, timeout=5, user_handler=None, loop=False):  # timeout in seconds
        self.timeout = timeout
        self.user_handler = user_handler
        self.loop = loop
        self.timer = threading.Timer(self.timeout, self.default_handler)

    def start(self):
        self.timer.start()

    def reset(self):
        self.timer.cancel()
        self.timer = threading.Timer(self.timeout, self.default_handler)
        self.timer.start()

    def stop(self):
        self.timer.cancel()
        self.timer = threading.Timer(self.timeout, self.default_handler)

    def default_handler(self):
        if self.loop:
            self.reset()
        if self.user_handler is None:
            print('TimedEvent expired. No user handler defined')
        else:
            self.user_handler()


if __name__ == '__main__':

    def wait_for_output(t):
        time.sleep(t)
        print('done!')

    def print_a():
        print('a')

    watchdog = TimedEvent(3, user_handler=print_a, loop=True)
    watchdog.start()

    wait_for_output(5)
    wait_for_output(1)
    wait_for_output(3)
    wait_for_output(2)
    watchdog.reset()
    wait_for_output(2)
    watchdog.stop()
    watchdog.stop()
