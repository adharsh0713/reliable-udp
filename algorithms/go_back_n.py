import socket

from protocol.packet import Packet, ACK
from config import TIMEOUT, MAX_RETRIES, WINDOW_SIZE


class GoBackN:
    def __init__(self, sock, receiver_addr, metrics):
        self.sock = sock
        self.receiver_addr = receiver_addr
        self.metrics = metrics

        self.base = 0
        self.next_seq = 0
        self.window_size = WINDOW_SIZE

        # Track whether each packet has been transmitted before.
        self.sent_sequences = set()

        # Count consecutive timeout retries without cumulative ACK progress.
        self.timeout_retries = 0

    def send_file(self, packets):
        while self.base < len(packets):
            self.send_window(packets)
            self.wait_for_ack(packets)

        self.sock.settimeout(None)

    def send_window(self, packets):
        while (
            self.next_seq < self.base + self.window_size
            and self.next_seq < len(packets)
        ):
            packet = packets[self.next_seq]
            sequence = packet.sequence

            self.sock.sendto(
                packet.encode(),
                self.receiver_addr,
            )

            self.metrics.data_packet_sent()

            if sequence in self.sent_sequences:
                self.metrics.retransmission()
                print(f"Retransmitting packet {sequence}")
            else:
                self.sent_sequences.add(sequence)
                print(f"Sending packet {sequence}")

            self.next_seq += 1

    def wait_for_ack(self, packets):
        self.sock.settimeout(TIMEOUT)

        while self.base < self.next_seq:
            try:
                data, address = self.sock.recvfrom(65535)

                # Ignore datagrams from unexpected sources.
                if address != self.receiver_addr:
                    continue

                try:
                    ack_packet = Packet.decode(data)
                except ValueError:
                    print("Invalid ACK packet discarded")
                    continue

                if ack_packet.packet_type != ACK:
                    continue

                ack_num = ack_packet.sequence

                # GBN ACKs identify the last in-order packet received.
                # Reject ACKs outside the range of sent packets.
                if not (self.base <= ack_num < self.next_seq):
                    continue

                self.metrics.ack_received()
                print(f"ACK received {ack_num}")

                previous_base = self.base
                self.base = ack_num + 1

                if self.base > previous_base:
                    self.timeout_retries = 0

            except socket.timeout:
                if self.timeout_retries >= MAX_RETRIES:
                    raise TimeoutError(
                        f"Go-Back-N failed: no cumulative ACK progress "
                        f"after {MAX_RETRIES} timeout retries "
                        f"at base sequence {self.base}"
                    )

                self.timeout_retries += 1

                print(
                    f"Timeout retry {self.timeout_retries}/{MAX_RETRIES}; "
                    f"resending from packet {self.base}"
                )

                # Reset next_seq so the next send_window retransmits
                # all outstanding packets, as required by Go-Back-N.
                self.next_seq = self.base
                return


def send_file(sock, address, packets, metrics):
    gbn = GoBackN(sock, address, metrics)
    gbn.send_file(packets)