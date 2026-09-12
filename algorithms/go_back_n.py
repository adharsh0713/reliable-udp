import socket

from protocol.packet import Packet, ACK


WINDOW_SIZE = 4
TIMEOUT = 2


class GoBackN:

    def __init__(self, sock, receiver_addr):
        self.sock = sock
        self.receiver_addr = receiver_addr

        self.base = 0
        self.next_seq = 0
        self.window_size = WINDOW_SIZE


    def send_file(self, packets):

        while self.base < len(packets):

            self.send_window(packets)

            self.wait_for_ack()


    def send_window(self, packets):

        while (
            self.next_seq < self.base + self.window_size
            and self.next_seq < len(packets)
        ):

            packet = packets[self.next_seq]

            self.sock.sendto(
                packet.encode(),
                self.receiver_addr
            )

            print(
                f"Sending packet {self.next_seq}"
            )

            self.next_seq += 1


    def wait_for_ack(self):

        self.sock.settimeout(TIMEOUT)

        while self.base < self.next_seq:

            try:
                data, _ = self.sock.recvfrom(1024)

                ack_packet = Packet.decode(data)

                if ack_packet.packet_type == ACK:

                    ack_num = ack_packet.sequence

                    print(
                        f"ACK received {ack_num}"
                    )

                    if ack_num >= self.base:
                        self.base = ack_num + 1


            except socket.timeout:

                print(
                    "Timeout. Resending window"
                )

                self.next_seq = self.base
                return

def send_file(sock, address, packets):

    gbn = GoBackN(sock, address)

    gbn.send_file(packets)