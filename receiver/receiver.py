import socket

from protocol.packet import Packet, DATA, ACK, END
from config import PROTOCOL, WINDOW_SIZE
from experiments.metrics import Metrics

metrics = Metrics(PROTOCOL)

SUPPORTED = [
    "stop_wait",
    "go_back_n",
    "selective_repeat"
]

HOST = "0.0.0.0"
PORT = 5000
BUFFER_SIZE = 1024
OUTPUT_FILE = f"data/results/{PROTOCOL}_received.txt"

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

sock.bind((HOST, PORT))


# Used by Selective Repeat to store out-of-order packets
receive_buffer = {}

expected_sequence = 0


print(f"Listening on UDP port {PORT}...")
print(f"Protocol: {PROTOCOL}")


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


with open(OUTPUT_FILE, "wb") as file:

    while True:

        data, address = sock.recvfrom(BUFFER_SIZE)

        try:
            packet = Packet.decode(data)

        except ValueError:
            print("Corrupted packet discarded (CRC mismatch)")
            continue


        if packet.packet_type == END:

            # Do not close before buffered SR packets are written
            if not receive_buffer:

                send_ack(
                    packet.sequence,
                    address
                )

                print(
                    f"Sent ACK {packet.sequence}"
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


                # Individual ACK
                send_ack(
                    seq,
                    address
                )


                # Deliver packets in order
                while expected_sequence in receive_buffer:

                    payload = receive_buffer.pop(
                        expected_sequence
                    )

                    file.write(payload)

                    print(
                        f"Wrote packet {expected_sequence}"
                    )

                    expected_sequence += 1


            else:

                # Old packet, resend ACK
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

                # Reject future packets
                # Send ACK for last correctly received packet
                if expected_sequence > 0:
                    print(
                        f"Out of order packet {seq}, expected {expected_sequence}"
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

                metrics.packet_received()

                expected_sequence += 1

            else:

                # Duplicate packet after timeout
                send_ack(
                    seq,
                    address
                )


sock.close()

print(
    f"File received: {OUTPUT_FILE}"
)