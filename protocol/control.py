import socket

from protocol.packet import Packet, ACK

MAX_TRIES = 5
TIMEOUT = 2


def send_control_packet(sock, address, packet):

    for attempt in range(MAX_TRIES):

        sock.sendto(
            packet.encode(),
            address
        )

        print(
            f"Sending control packet {packet.sequence}"
        )

        sock.settimeout(TIMEOUT)

        try:
            data, _ = sock.recvfrom(1024)

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