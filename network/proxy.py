import socket

from network.fault_injector import FaultInjector
from protocol.packet import Packet, DATA, ACK, END


PROXY_IP = "0.0.0.0"
PROXY_PORT = 5001

RECEIVER_ADDRESS = (
    "127.0.0.1",
    5000
)

BUFFER_SIZE = 1024


data_injector = FaultInjector(
    loss_rate=0.2,
    corruption_rate=0.5,
    delay=0.1,
    duplicate_rate=0.0
)


ack_injector = FaultInjector(
    loss_rate=0.0,
    corruption_rate=0.0,
    delay=0.0,
    duplicate_rate=0.0
)


sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

sock.bind(
    (PROXY_IP, PROXY_PORT)
)


print("Proxy listening on port 5001")


sender_address = None


while True:

    try:
        data, address = sock.recvfrom(
            BUFFER_SIZE
        )

    except ConnectionResetError:
        print("Connection reset. Waiting for next packet...")
        continue

    try:
        packet = Packet.decode(data)

    except ValueError:
        print("Proxy discarded corrupted packet")
        continue


    print(
        f"Proxy received type={packet.packet_type}, seq={packet.sequence}"
    )


    # Sender -> Receiver direction
    if packet.packet_type in (DATA, END):

        sender_address = address

        modified = data_injector.process_packet_with_duplicate(
            data
        )


        if modified is None:
            print("DATA packet dropped")
            continue


        if isinstance(modified, tuple):

            print("Sending duplicate packet")

            sock.sendto(
                modified[0],
                RECEIVER_ADDRESS
            )

            sock.sendto(
                modified[1],
                RECEIVER_ADDRESS
            )

        else:

            sock.sendto(
                modified,
                RECEIVER_ADDRESS
            )


    # Receiver -> Sender direction
    elif packet.packet_type == ACK:

        if sender_address is None:
            continue


        modified = ack_injector.process_packet(
            data
        )


        if modified is None:
            print("ACK dropped")
            continue


        sock.sendto(
            modified,
            sender_address
        )