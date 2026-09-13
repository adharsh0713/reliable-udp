from protocol.packet import Packet, ACK
from protocol.timer import Timer
import socket

from config import (
    TIMEOUT,
    MAX_RETRIES
)

def send_file(sock, address, packets, metrics):
    for packet in packets:
        send_packet(sock, address, packet, metrics)

def send_packet(sock, address, packet, metrics):

    timer = Timer(TIMEOUT)
    tries = 0

    while tries < MAX_RETRIES:

        tries += 1

        print(
            f"Sending packet {packet.sequence} "
            f"(attempt {tries}/{MAX_RETRIES})"
        )

        sock.sendto(
            packet.encode(),
            address
        )

        metrics.data_packet_sent()

        timer.start()

        sock.settimeout(TIMEOUT)

        try:
            data, _ = sock.recvfrom(1024)

            try:
                ack = Packet.decode(data)
                metrics.ack_received()

            except ValueError:
                print("Corrupted ACK discarded")
                continue

            if (
                ack.packet_type == ACK
                and ack.sequence == packet.sequence
            ):
                print(f"ACK received: {ack.sequence}")
                timer.stop()
                sock.settimeout(None)
                return True

        except socket.timeout:
            metrics.retransmission()
            print(
                f"Timeout: packet {packet.sequence}"
            )

        except ConnectionResetError:
            print("Receiver unavailable")

    sock.settimeout(None)

    raise TimeoutError(
        f"Packet {packet.sequence} failed after {MAX_RETRIES} attempts"
    )