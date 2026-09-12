import socket
import sys

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000
BUFFER_SIZE = 1024

if len(sys.argv) != 2:
    print("Usage: python sender/sender.py <file>")
    sys.exit(1)

filename = sys.argv[1]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

with open(filename, "rb") as file:
    while True:
        data = file.read(BUFFER_SIZE)

        if not data:
            break

        sock.sendto(data, (SERVER_IP, SERVER_PORT))

sock.sendto(b"EOF", (SERVER_IP, SERVER_PORT))

sock.close()

print("File sent")