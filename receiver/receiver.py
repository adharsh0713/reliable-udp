import socket
from protocol.packet import Packet, DATA, ACK, END

HOST = "0.0.0.0"
PORT = 5000
BUFFER_SIZE = 1024
OUTPUT_FILE = "data/results/received.txt"
WINDOW_SIZE = 4

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

sock.bind((HOST, PORT))

receive_buffer = {}

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

            seq = packet.sequence


            # Packet inside receiver window
            if (
                expected_sequence  <= seq < expected_sequence  + WINDOW_SIZE
            ):

                # Store only first copy
                if seq not in receive_buffer:

                    receive_buffer[seq] = packet.payload

                    print(
                        f"Buffered packet {seq}"
                    )

                else:
                    print(
                        f"Duplicate packet {seq}"
                    )


                # Send ACK for this packet
                ack = Packet(
                    seq,
                    ACK,
                    b""
                )

                sock.sendto(
                    ack.encode(),
                    address
                )


                # Deliver consecutive packets
                while expected_sequence  in receive_buffer:

                    data = receive_buffer.pop(
                        expected_sequence 
                    )

                    file.write(data)

                    print(
                        f"Wrote packet {expected_sequence}"
                    )

                    expected_sequence += 1


            else:

                # Old packet, resend ACK
                ack = Packet(
                    seq,
                    ACK,
                    b""
                )

                sock.sendto(
                    ack.encode(),
                    address
                )

sock.close()

print(f"File received: {OUTPUT_FILE}")