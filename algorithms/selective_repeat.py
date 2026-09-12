from protocol.timer import Timer
from protocol.packet import Packet, ACK
import socket


WINDOW_SIZE = 4
TIMEOUT = 2
MAX_RETRIES = 5


def send_file(sock, address, packets):

    base = 0
    next_seq = 0

    total = len(packets)

    timers = {}
    retries = {}
    acked = {}

    while base < total:

        # Send packets inside window
        while (
            next_seq < total and
            next_seq < base + WINDOW_SIZE
        ):

            packet = packets[next_seq]

            sock.sendto(
                packet.encode(),
                address
            )

            print(
                f"Sending packet {next_seq}"
            )

            timers[next_seq] = Timer(TIMEOUT)
            timers[next_seq].start()

            retries[next_seq] = 0
            acked[next_seq] = False

            next_seq += 1


        sock.settimeout(0.1)

        try:
            data, _ = sock.recvfrom(1024)

            ack_packet = Packet.decode(data)

            ack_no = ack_packet.sequence

            if ack_no in acked:

                print(
                    f"ACK received {ack_no}"
                )

                acked[ack_no] = True

                timers[ack_no].stop()


                # Slide window
                while (
                    base < total and
                    acked.get(base, False)
                ):
                    base += 1


        except socket.timeout:
            pass


        # Check individual timers
        for seq in list(timers):

            if (
                not acked[seq]
                and timers[seq].expired()
            ):

                if retries[seq] >= MAX_RETRIES:
                    raise Exception(
                        f"Packet {seq} failed"
                    )


                print(
                    f"Timeout packet {seq}"
                )


                sock.sendto(
                    packets[seq].encode(),
                    address
                )

                print(
                    f"Resending packet {seq}"
                )


                retries[seq] += 1

                timers[seq].start()