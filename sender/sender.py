import socket
import os
import config
import sys

from protocol.packet import Packet, DATA, END
from protocol.control import send_control_packet
from algorithms.selector import get_protocol
from experiments.metrics import Metrics


def send_file(filename):

    send_protocol = get_protocol(config.PROTOCOL)

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    file_size = os.path.getsize(filename)

    packets = []

    sequence = 0

    with open(filename, "rb") as file:

        while True:

            data = file.read(config.CHUNK_SIZE)

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


    metrics = Metrics(config.PROTOCOL)

    metrics.start_timer()


    send_protocol(
        sock,
        (config.SERVER_IP, config.SERVER_PORT),
        packets,
        metrics
    )


    end_packet = Packet(
        sequence,
        END,
        b""
    )


    send_control_packet(
        sock,
        (config.SERVER_IP, config.SERVER_PORT),
        end_packet,
        metrics
    )


    metrics.stop_timer()


    metrics.save_json(
        "data/results/sender_metrics.json",
        file_size
    )

    sock.close()
    return metrics.report(file_size)



if __name__ == "__main__":

    if len(sys.argv) != 2:
        print(
            "Usage: python -m sender.sender <file>"
        )
        exit(1)


    result = send_file(
        sys.argv[1]
    )


    print(result)

    print("File sent")