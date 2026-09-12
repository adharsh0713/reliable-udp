import socket

from network.fault_injector import FaultInjector
from protocol.packet import Packet, DATA, ACK, END

SHUTDOWN_AFTER_TRANSFER = True

PROXY_IP = "0.0.0.0"
PROXY_PORT = 5001

RECEIVER_ADDRESS = (
    "127.0.0.1",
    5000
)

BUFFER_SIZE = 1024


data_injector = FaultInjector(
    loss_rate=0.0,
    corruption_rate=0.0,
    delay=0.0,
    duplicate_rate=0.5
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


while True:

    data, sender_address = sock.recvfrom(
        BUFFER_SIZE
    )

    packet = Packet.decode(data)

    print(
        f"Proxy received type={packet.packet_type}, seq={packet.sequence}"
    )

    if packet.packet_type == DATA:

        modified = data_injector.process_packet_with_duplicate(data)

    else:

        modified = data_injector.process_packet(data)


    if modified is None:
        print("Packet dropped")
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


    if packet.packet_type == DATA or packet.packet_type == END:

        ack, _ = sock.recvfrom(
            BUFFER_SIZE
        )

        print("ACK received from receiver")


        modified_ack = ack_injector.process_packet(ack)


        if modified_ack is None:
            print("ACK dropped")
            continue


        sock.sendto(
            modified_ack,
            sender_address
        )


    if packet.packet_type == END:

        print("END forwarded")

        if SHUTDOWN_AFTER_TRANSFER:
            print("Test transfer complete. Proxy shutting down.")
            break