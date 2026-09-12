import socket

HOST = "0.0.0.0"
PORT = 5000
BUFFER_SIZE = 1024
OUTPUT_FILE = "received.txt"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

print(f"Listening on UDP port {PORT}...")

with open(OUTPUT_FILE, "wb") as file:
    while True:
        data, address = sock.recvfrom(BUFFER_SIZE)

        if data == b"EOF":
            break

        file.write(data)

sock.close()

print(f"File received: {OUTPUT_FILE}")