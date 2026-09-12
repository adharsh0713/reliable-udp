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


    def process_packet_with_duplicate(self, data):
        """
        Returns:
        None -> dropped
        bytes -> normal packet
        tuple -> duplicate packet
        """

        if self.should_drop():
            print("FAULT: packet dropped")
            return None

        self.apply_delay()

        if self.should_corrupt():
            print("FAULT: packet corrupted")
            data = self.corrupt_data(data)

        if self.should_duplicate():
            print("FAULT: packet duplicated")
            return data, data

        return data

    def apply_delay(self):
        if self.delay > 0:
            print(f"FAULT: delaying packet by {self.delay}s")
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

    def process_packet(self, data):
        """
        Returns:
        None -> packet dropped
        bytes -> packet forwarded
        """

        if self.should_drop():
            print("FAULT: packet dropped")
            return None

        self.apply_delay()

        if self.should_corrupt():
            print("FAULT: packet corrupted")
            data = self.corrupt_data(data)

        return data