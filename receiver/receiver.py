import socket
from protocol.packet import Packet, DATA, ACK, END

HOST = "0.0.0.0"
PORT = 5000
BUFFER_SIZE = 1024
OUTPUT_FILE = "data/results/received.txt"


sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

sock.bind((HOST, PORT))

print(f"Listening on UDP port {PORT}...")


with open(OUTPUT_FILE, "wb") as file:
    expected_sequence = 0

    while True:

        data, address = sock.recvfrom(BUFFER_SIZE)

        try:
            packet = Packet.decode(data)

        except ValueError:
            print("Corrupted packet discarded  (CRC mismatch)")
            continue

        if packet.packet_type == END:
            ack = Packet(
                packet.sequence,
                ACK,
                b""
            )

            sock.sendto(
                ack.encode(),
                address
            )

            print(
                f"Sent ACK {packet.sequence}"
            )

            break


        if packet.packet_type == DATA:

            print(
                f"Received DATA {packet.sequence}, "
                f"{len(packet.payload)} bytes"
            )

            if packet.sequence == expected_sequence:

                file.write(packet.payload)

                expected_sequence += 1

                ack_number = packet.sequence

            else:
                print(
                    f"Out of order/duplicate packet {packet.sequence}, ignoring data"
                )

                ack_number = max(0, expected_sequence - 1)


            ack = Packet(
                ack_number,
                ACK,
                b""
            )

            sock.sendto(
                ack.encode(),
                address
            )


sock.close()

print(f"File received: {OUTPUT_FILE}")