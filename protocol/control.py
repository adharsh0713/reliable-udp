import socket

from protocol.packet import Packet, ACK
from config import MAX_RETRIES, TIMEOUT


def send_control_packet(sock, address, packet, metrics):

    for attempt in range(MAX_RETRIES):

        sock.sendto(
            packet.encode(),
            address
        )

        metrics.control_packet_sent()

        print(
            f"Sending control packet {packet.sequence}"
        )

        sock.settimeout(TIMEOUT)

        try:
            data, _ = sock.recvfrom(65535)

            ack = Packet.decode(data)

            if (
                ack.packet_type == ACK
                and ack.sequence == packet.sequence
            ):
                print(
                    f"ACK received {ack.sequence}"
                )
                return

        except socket.timeout:
            pass

        except ValueError:
            print("Invalid ACK packet")

        except Exception:
            pass


    raise TimeoutError(
        f"Control packet {packet.sequence} failed"
    )