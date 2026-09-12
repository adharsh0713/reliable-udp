import socket
import sys

from protocol.packet import Packet, DATA, END

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000
BUFFER_SIZE = 1024

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

if len(sys.argv) != 2:
    print("Usage: python sender/sender.py <file>")
    sys.exit(1)

filename = sys.argv[1]

sequence = 0

with open(filename, "rb") as file:

    while True:

        data = file.read(BUFFER_SIZE)

        if not data:
            break

        packet = Packet(
            sequence=sequence,
            packet_type=DATA,
            payload=data
        )

        sock.sendto(
            packet.encode(),
            (SERVER_IP, SERVER_PORT)
        )

        sequence += 1

end_packet = Packet(
    sequence,
    END,
    b""
)

sock.sendto(
    end_packet.encode(),
    (SERVER_IP, SERVER_PORT)
)

sock.close()

print("File sent")