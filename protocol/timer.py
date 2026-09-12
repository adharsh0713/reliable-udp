import time


class Timer:
    def __init__(self, timeout):
        self.timeout = timeout
        self.start_time = None

    def start(self):
        self.start_time = time.monotonic()

    def expired(self):
        if self.start_time is None:
            return False

        return (
            time.monotonic() - self.start_time >= self.timeout
        )

    def stop(self):
        self.start_time = None


class TimerManager:

    def __init__(self, timeout):
        self.timeout = timeout
        self.timers = {}


    def start(self, seq):
        timer = Timer(self.timeout)
        timer.start()
        self.timers[seq] = timer


    def stop(self, seq):
        if seq in self.timers:
            del self.timers[seq]


    def expired(self, seq):
        if seq not in self.timers:
            return False

        return self.timers[seq].expired()