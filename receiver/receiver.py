import socket
import os

from protocol.packet import Packet, DATA, ACK, END
from experiments.metrics import Metrics


PROTOCOL = os.getenv(
    "PROTOCOL",
    "stop_wait"
)

WINDOW_SIZE = int(
    os.getenv(
        "WINDOW_SIZE",
        "4"
    )
)

OUTPUT_FILE = os.getenv(
    "OUTPUT_FILE",
    f"data/results/{PROTOCOL}_received.txt"
)


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

            if not receive_buffer:

                send_ack(
                    packet.sequence,
                    address
                )

                print(
                    f"Sent ACK {packet.sequence}"
                )

                file.flush()

                metrics.save_json(
                    "data/results/receiver_metrics.json",
                    os.path.getsize(OUTPUT_FILE)
                )

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