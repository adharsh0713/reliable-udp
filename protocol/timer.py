import time

class Timer:
    def __init__(self, timeout):
        self.timeout = timeout
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def expired(self):
        if self.start_time is None:
            return False

        return (
            time.time() - self.start_time
            >= self.timeout
        )

    def stop(self):
        self.start_time = None