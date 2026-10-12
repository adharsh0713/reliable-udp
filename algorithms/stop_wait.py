import socket

from protocol.packet import Packet, ACK
from protocol.timer import Timer
from config import TIMEOUT, MAX_RETRIES


def send_file(sock, address, packets, metrics):
    for packet in packets:
        send_packet(sock, address, packet, metrics)


def send_packet(sock, address, packet, metrics):
    timer = Timer(TIMEOUT)
    retries = 0
    transmitted_before = False

    try:
        while True:
            print(
                f"Sending packet {packet.sequence} "
                f"(attempt {retries + 1}/{MAX_RETRIES})"
            )

            sock.sendto(packet.encode(), address)
            metrics.data_packet_sent()

            if transmitted_before:
                metrics.retransmission()

            transmitted_before = True

            timer.start()
            sock.settimeout(TIMEOUT)

            while True:
                try:
                    data, source = sock.recvfrom(65535)

                except socket.timeout:
                    timer.stop()

                    if retries >= MAX_RETRIES - 1:
                        raise TimeoutError(
                            f"Packet {packet.sequence} failed "
                            f"after {MAX_RETRIES} attempts"
                        )

                    retries += 1
                    print(f"Timeout: packet {packet.sequence}")
                    break

                except ConnectionResetError:
                    # Treat a connection reset as a failed attempt.
                    timer.stop()

                    if retries >= MAX_RETRIES - 1:
                        raise TimeoutError(
                            f"Packet {packet.sequence} failed "
                            f"after {MAX_RETRIES} attempts"
                        )

                    retries += 1
                    print("Receiver unavailable")
                    break

                # Ignore datagrams from unexpected sources.
                if source != address:
                    continue

                try:
                    ack = Packet.decode(data)
                except ValueError:
                    print("Invalid ACK packet discarded")
                    continue

                if ack.packet_type != ACK:
                    continue

                if ack.sequence != packet.sequence:
                    continue

                metrics.ack_received()
                print(f"ACK received: {ack.sequence}")

                timer.stop()
                return True

    finally:
        timer.stop()
        sock.settimeout(None)