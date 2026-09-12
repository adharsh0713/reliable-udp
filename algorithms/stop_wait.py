from protocol.packet import Packet, ACK
from protocol.timer import Timer
import socket

TIMEOUT = 1
MAX_TRIES = 5

def send_file(sock, address, packets):
    for packet in packets:
        send_packet(sock, address, packet)

def send_packet(sock, address, packet):

    timer = Timer(TIMEOUT)
    tries = 0

    while tries < MAX_TRIES:

        tries += 1

        print(
            f"Sending packet {packet.sequence} "
            f"(attempt {tries}/{MAX_TRIES})"
        )

        sock.sendto(
            packet.encode(),
            address
        )

        timer.start()

        sock.settimeout(TIMEOUT)

        try:
            data, _ = sock.recvfrom(1024)

            try:
                ack = Packet.decode(data)

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
            print(
                f"Timeout: packet {packet.sequence}"
            )

        except ConnectionResetError:
            print("Receiver unavailable")

    sock.settimeout(None)

    raise TimeoutError(
        f"Packet {packet.sequence} failed after {MAX_TRIES} attempts"
    )