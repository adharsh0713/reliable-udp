import random
import time


class FaultInjector:

    def __init__(
        self,
        loss_rate=0.0,
        corruption_rate=0.0,
        delay=0.0,
        duplicate_rate=0.0
    ):
        self.loss_rate = loss_rate
        self.corruption_rate = corruption_rate
        self.delay = delay
        self.duplicate_rate = duplicate_rate


    def should_drop(self):
        return random.random() < self.loss_rate


    def should_corrupt(self):
        return random.random() < self.corruption_rate


    def should_duplicate(self):
        return random.random() < self.duplicate_rate


    def apply_delay(self):
        if self.delay > 0:
            time.sleep(self.delay)


    def corrupt_data(self, data):
        """
        Flip one random bit in packet bytes.
        """
        if not data:
            return data

        corrupted = bytearray(data)

        index = random.randint(
            0,
            len(corrupted) - 1
        )

        bit = 1 << random.randint(0, 7)

        corrupted[index] ^= bit

        return bytes(corrupted)