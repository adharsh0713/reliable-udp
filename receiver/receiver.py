import socket
import os
import time

from protocol.packet import Packet, DATA, ACK, END
from experiments.metrics import Metrics
import config

PROTOCOL = config.PROTOCOL
WINDOW_SIZE = config.WINDOW_SIZE
OUTPUT_FILE = config.OUTPUT_FILE
END_ACK_WAIT = 3.0

metrics = Metrics(PROTOCOL)


SUPPORTED = [
    "stop_wait",
    "go_back_n",
    "selective_repeat"
]


HOST = "0.0.0.0"
PORT = 5000
BUFFER_SIZE = 65535


sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

sock.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

sock.bind(
    (HOST, PORT)
)


receive_buffer = {}
expected_sequence = 0


print(
    f"Listening on UDP port {PORT}..."
)

print(
    f"Protocol: {PROTOCOL}"
)

print(
    f"Window: {WINDOW_SIZE}"
)

print(
    f"Output: {OUTPUT_FILE}"
)


def send_ack(sequence, address):

    ack = Packet(
        sequence,
        ACK,
        b""
    )

    sock.sendto(
        ack.encode(),
        address
    )

    metrics.ack_sent()


os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)


with open(
    OUTPUT_FILE,
    "wb"
) as file:

    while True:

        data, address = sock.recvfrom(
            BUFFER_SIZE
        )

        try:

            packet = Packet.decode(data)

        except ValueError:

            print(
                "Corrupted packet discarded (CRC mismatch)"
            )

            continue


        if packet.packet_type == DATA:

            metrics.packet_received()


        if packet.packet_type == END:
            transfer_complete = (
                packet.sequence == expected_sequence
                and not receive_buffer
            )

            if not transfer_complete:
                print(
                    f"Premature END rejected: received sequence "
                    f"{packet.sequence}, expected {expected_sequence}"
                )
                continue

            send_ack(packet.sequence, address)
            print(f"Sent END ACK {packet.sequence}")

            file.flush()

            metrics.save_json(
                "data/results/receiver_metrics.json",
                os.path.getsize(OUTPUT_FILE)
            )

            deadline = time.monotonic() + END_ACK_WAIT

            while time.monotonic() < deadline:
                sock.settimeout(
                    max(0.01, deadline - time.monotonic())
                )

                try:
                    retry_data, retry_address = sock.recvfrom(BUFFER_SIZE)
                except socket.timeout:
                    break

                try:
                    retry_packet = Packet.decode(retry_data)
                except ValueError:
                    continue

                if (
                    retry_packet.packet_type == END
                    and retry_packet.sequence == expected_sequence
                ):
                    send_ack(
                        retry_packet.sequence,
                        retry_address
                    )
                    print(
                        f"Re-acknowledged END {retry_packet.sequence}"
                    )

            sock.settimeout(None)
            break

        if packet.packet_type != DATA:
            continue


        seq = packet.sequence


        if PROTOCOL not in SUPPORTED:

            raise ValueError(
                f"Unsupported protocol: {PROTOCOL}"
            )


        # ----------------------------
        # Selective Repeat receiver
        # ----------------------------

        if PROTOCOL == "selective_repeat":

            if (
                expected_sequence <= seq <
                expected_sequence + WINDOW_SIZE
            ):

                if seq not in receive_buffer:

                    receive_buffer[seq] = packet.payload

                    print(
                        f"Buffered packet {seq}"
                    )

                else:

                    print(
                        f"Duplicate packet {seq}"
                    )


                send_ack(
                    seq,
                    address
                )


                while expected_sequence in receive_buffer:

                    payload = receive_buffer.pop(
                        expected_sequence
                    )

                    file.write(
                        payload
                    )

                    print(
                        f"Wrote packet {expected_sequence}"
                    )

                    expected_sequence += 1


            else:

                send_ack(
                    seq,
                    address
                )


        # ----------------------------
        # Go-Back-N receiver
        # ----------------------------

        elif PROTOCOL == "go_back_n":

            if seq == expected_sequence:

                file.write(
                    packet.payload
                )

                print(
                    f"Wrote packet {seq}"
                )

                send_ack(
                    seq,
                    address
                )

                expected_sequence += 1

            else:

                if expected_sequence > 0:

                    print(
                        f"Out of order packet {seq}, "
                        f"expected {expected_sequence}"
                    )

                    send_ack(
                        expected_sequence - 1,
                        address
                    )


        # ----------------------------
        # Stop-and-Wait receiver
        # ----------------------------

        elif PROTOCOL == "stop_wait":

            if seq == expected_sequence:

                file.write(
                    packet.payload
                )

                print(
                    f"Wrote packet {seq}"
                )

                send_ack(
                    seq,
                    address
                )

                expected_sequence += 1

            else:

                send_ack(
                    seq,
                    address
                )


sock.close()


print(
    f"File received: {OUTPUT_FILE}"
)