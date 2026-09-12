import random
import time


class FaultInjector:

    def __init__(
        self,
        loss_rate=0.0,
        corruption_rate=0.0,
        delay=0.0,
        duplicate_rate=0.0,
        seed=None
    ):

        self.validate_rate(loss_rate)
        self.validate_rate(corruption_rate)
        self.validate_rate(duplicate_rate)

        self.loss_rate = loss_rate
        self.corruption_rate = corruption_rate
        self.delay = delay
        self.duplicate_rate = duplicate_rate

        if seed is not None:
            random.seed(seed)


    def validate_rate(self, rate):

        if not 0 <= rate <= 1:
            raise ValueError(
                "Fault rates must be between 0 and 1"
            )


    def should_drop(self):

        return random.random() < self.loss_rate


    def should_corrupt(self):

        return random.random() < self.corruption_rate


    def should_duplicate(self):

        return random.random() < self.duplicate_rate


    def apply_delay(self):

        if self.delay > 0:

            print(
                f"FAULT: delaying packet by {self.delay}s"
            )

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

        bit = 1 << random.randint(
            0,
            7
        )

        corrupted[index] ^= bit

        return bytes(corrupted)


    def process_packet(
        self,
        data,
        allow_duplicate=False
    ):
        """
        Returns:

        None:
            packet dropped

        bytes:
            normal packet

        tuple(bytes, bytes):
            duplicated packet
        """

        if self.should_drop():

            print(
                "FAULT: packet dropped"
            )

            return None


        self.apply_delay()


        if self.should_corrupt():

            print(
                "FAULT: packet corrupted"
            )

            data = self.corrupt_data(data)


        if (
            allow_duplicate
            and self.should_duplicate()
        ):

            print(
                "FAULT: packet duplicated"
            )

            return data, data


        return data


    def process_packet_with_duplicate(self, data):

        return self.process_packet(
            data,
            allow_duplicate=True
        )


    def should_reorder(self):
        """
        Placeholder for future reordering fault.
        """

        return False