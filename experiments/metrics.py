import time


class Metrics:
    def __init__(self, protocol):
        self.protocol = protocol

        self.start_time = None
        self.end_time = None

        self.packets_sent = 0
        self.packets_received = 0

        self.acks_sent = 0
        self.acks_received = 0

        self.retransmissions = 0

        self.data_packets_sent = 0
        self.control_packets_sent = 0


    def start_timer(self):
        self.start_time = time.time()


    def stop_timer(self):
        self.end_time = time.time()


    def packet_sent(self):
        self.packets_sent += 1


    def packet_received(self):
        self.packets_received += 1


    def ack_sent(self):
        self.acks_sent += 1


    def ack_received(self):
        self.acks_received += 1


    def retransmission(self):
        self.retransmissions += 1

    def data_packet_sent(self):
        self.data_packets_sent += 1


    def control_packet_sent(self):
        self.control_packets_sent += 1


    def completion_time(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time

        return 0


    def throughput(self, file_size):
        duration = self.completion_time()

        if duration == 0:
            return 0

        return file_size / duration


    def report(self, file_size):
        return {
            "protocol": self.protocol,

            "file_size": file_size,

            "packets_sent": self.packets_sent,
            "packets_received": self.packets_received,

            "acks_sent": self.acks_sent,
            "acks_received": self.acks_received,

            "retransmissions": self.retransmissions,

            "completion_time": round(
                self.completion_time(),
                4
            ),

            "throughput": round(
                self.throughput(file_size),
                4
            )
        }