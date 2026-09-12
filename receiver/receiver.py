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
    while True:
        data, address = sock.recvfrom(BUFFER_SIZE)

        packet = Packet.decode(data)

        if packet.packet_type == END:
            break

        if packet.packet_type == DATA:
            ack = Packet(
                packet.sequence,
                ACK,
                b""
            )

            sock.sendto(
                ack.encode(),
                address
            )

sock.close()

print(f"File received: {OUTPUT_FILE}")