import socket

from protocol.packet import Packet, ACK
from config import MAX_RETRIES, TIMEOUT


def send_control_packet(sock, address, packet, metrics):
    try:
        for attempt in range(MAX_RETRIES):
            sock.sendto(packet.encode(), address)
            metrics.control_packet_sent()

            print(
                f"Sending control packet {packet.sequence} "
                f"(attempt {attempt + 1}/{MAX_RETRIES})"
            )

            sock.settimeout(TIMEOUT)

            while True:
                try:
                    data, source = sock.recvfrom(65535)
                except socket.timeout:
                    break
                except ConnectionResetError:
                    break

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
                print(f"ACK received {ack.sequence}")
                return

        raise TimeoutError(
            f"Control packet {packet.sequence} failed "
            f"after {MAX_RETRIES} attempts"
        )

    finally:
        sock.settimeout(None)