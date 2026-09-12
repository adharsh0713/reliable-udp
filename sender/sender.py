import socket
import sys

from protocol.packet import Packet, DATA, END
from protocol.control import send_control_packet
from algorithms.selector import get_protocol
from config import (
    PROTOCOL,
    CHUNK_SIZE,
    SERVER_IP,
    SERVER_PORT
)

send_file = get_protocol(PROTOCOL)

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
        # Split file into fixed-size payload chunks
        # Each chunk becomes an independent protocol packet
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

send_control_packet(
    sock,
    (SERVER_IP, SERVER_PORT),
    end_packet
)

sock.close()

print("File sent")