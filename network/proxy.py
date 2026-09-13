import socket
import os

from network.fault_injector import FaultInjector
from protocol.packet import Packet, DATA, ACK, END

DATA_LOSS_RATE = float(
    os.getenv(
        "DATA_LOSS_RATE",
        0
    )
)

DATA_CORRUPTION_RATE = float(
    os.getenv(
        "DATA_CORRUPTION_RATE",
        0
    )
)

DATA_DELAY = float(
    os.getenv(
        "DATA_DELAY",
        0
    )
)

DATA_DUPLICATE_RATE = float(
    os.getenv(
        "DATA_DUPLICATE_RATE",
        0
    )
)


ACK_LOSS_RATE = float(
    os.getenv(
        "ACK_LOSS_RATE",
        0
    )
)

ACK_CORRUPTION_RATE = float(
    os.getenv(
        "ACK_CORRUPTION_RATE",
        0
    )
)

ACK_DELAY = float(
    os.getenv(
        "ACK_DELAY",
        0
    )
)

ACK_DUPLICATE_RATE = float(
    os.getenv(
        "ACK_DUPLICATE_RATE",
        0
    )
)

PROXY_IP = "0.0.0.0"
PROXY_PORT = 5001

RECEIVER_ADDRESS = (
    "127.0.0.1",
    5000
)

BUFFER_SIZE = 65535


data_injector = FaultInjector(
    loss_rate=DATA_LOSS_RATE,
    corruption_rate=DATA_CORRUPTION_RATE,
    delay=DATA_DELAY,
    duplicate_rate=DATA_DUPLICATE_RATE
)


ack_injector = FaultInjector(
    loss_rate=ACK_LOSS_RATE,
    corruption_rate=ACK_CORRUPTION_RATE,
    delay=ACK_DELAY,
    duplicate_rate=ACK_DUPLICATE_RATE
)


sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

sock.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

sock.bind(
    (PROXY_IP, PROXY_PORT)
)


print("Proxy listening on port 5001")


sender_address = None


try:

    while True:

        try:
            data, address = sock.recvfrom(
                BUFFER_SIZE
            )

        except ConnectionResetError:
            print(
                "Connection reset. Waiting for next packet..."
            )
            continue


        try:
            packet = Packet.decode(data)

        except ValueError:

            print(
                "Proxy received corrupted packet"
            )

            continue


        print(
            f"Proxy received type={packet.packet_type}, seq={packet.sequence}"
        )


        # Sender -> Receiver
        if packet.packet_type in (DATA, END):

            sender_address = address


            modified = data_injector.process_packet_with_duplicate(
                data
            )


            if modified is None:

                print(
                    "DATA packet dropped"
                )

                continue


            if isinstance(modified, tuple):

                print(
                    "Sending duplicate packet"
                )

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


        # Receiver -> Sender
        elif packet.packet_type == ACK:


            if sender_address is None:
                continue


            modified = ack_injector.process_packet(
                data
            )


            if modified is None:

                print(
                    "ACK dropped"
                )

                continue


            sock.sendto(
                modified,
                sender_address
            )


except KeyboardInterrupt:

    print(
        "Proxy shutting down"
    )


finally:

    sock.close()