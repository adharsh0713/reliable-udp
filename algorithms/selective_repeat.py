import socket

from protocol.timer import Timer
from protocol.packet import Packet, ACK
from config import TIMEOUT, WINDOW_SIZE, MAX_RETRIES


def send_file(sock, address, packets, metrics):
    base = 0
    next_seq = 0
    total = len(packets)

    timers = {}
    retries = {}
    acked = {}

    try:
        while base < total:
            # Send new packets that fit inside the current window.
            while (
                next_seq < total
                and next_seq < base + WINDOW_SIZE
            ):
                packet = packets[next_seq]
                seq = packet.sequence

                sock.sendto(packet.encode(), address)
                metrics.data_packet_sent()

                print(f"Sending packet {seq}")

                timers[seq] = Timer(TIMEOUT)
                timers[seq].start()

                retries[seq] = 0
                acked[seq] = False

                next_seq += 1

            # Wait briefly for ACKs, then check each outstanding timer.
            sock.settimeout(0.1)

            try:
                data, source = sock.recvfrom(65535)

                if source != address:
                    continue

                try:
                    ack_packet = Packet.decode(data)
                except ValueError:
                    print("Invalid ACK packet discarded")
                    continue

                if ack_packet.packet_type != ACK:
                    continue

                ack_no = ack_packet.sequence

                # Accept ACKs only for packets sent and not already
                # acknowledged.
                if ack_no not in acked:
                    continue

                if acked[ack_no]:
                    continue

                metrics.ack_received()
                print(f"ACK received {ack_no}")

                acked[ack_no] = True
                timers[ack_no].stop()

                # Advance the window only over consecutively ACKed packets.
                while base < total and acked.get(
                    packets[base].sequence,
                    False,
                ):
                    base += 1

            except socket.timeout:
                pass

            # Retransmit only individual packets whose timers expired.
            for seq in list(timers):
                if acked[seq] or not timers[seq].expired():
                    continue

                if retries[seq] >= MAX_RETRIES:
                    raise TimeoutError(
                        f"Selective Repeat failed for packet {seq} "
                        f"after {MAX_RETRIES} retransmissions"
                    )

                sock.sendto(packets[seq].encode(), address)

                metrics.data_packet_sent()
                metrics.retransmission()

                retries[seq] += 1
                timers[seq].start()

                print(
                    f"Retransmitting packet {seq} "
                    f"(retry {retries[seq]}/{MAX_RETRIES})"
                )

    finally:
        sock.settimeout(None)