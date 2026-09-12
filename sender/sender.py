import socket
import sys

from protocol.packet import Packet, DATA, END
# from algorithms.stop_wait import send_file
from algorithms.stop_wait import send_packet
# from algorithms.go_back_n import send_file
from algorithms.selective_repeat import send_file

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5001
BUFFER_SIZE = 1024
CHUNK_SIZE = 20

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

if len(sys.argv) != 2:
    print("Usage: python sender/sender.py <file>")
    sys.exit(1)

filename = sys.argv[1]

packets = []

sequence = 0

with open(filename, "rb") as file:

    while True:

        data = file.read(CHUNK_SIZE)

        if not data:
            break

        packets.append(
            Packet(
                sequence,
                DATA,
                data
            )
        )

        sequence += 1


send_file(
    sock,
    (SERVER_IP, SERVER_PORT),
    packets
)

end_packet = Packet(
    sequence,
    END,
    b""
)

send_packet(
    sock,
    (SERVER_IP, SERVER_PORT),
    end_packet
)

sock.close()

print("File sent")