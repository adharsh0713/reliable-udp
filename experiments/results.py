import csv
import os

RESULT_FILE = "data/results/experiment_results.csv"


FIELDS = [
    "protocol",
    "file_name",
    "run",
    "file_size",

    "window",

    "data_packets_sent",
    "control_packets_sent",

    "packets_received",

    "acks_sent",
    "acks_received",

    "data_loss",
    "data_delay",
    "data_corruption",
    "data_duplicate",

    "ack_loss",
    "ack_delay",
    "ack_corruption",
    "ack_duplicate",

    "completion_time",
    "throughput",
    "retransmissions"
]


def save_result(result):

    os.makedirs(
        "data/results",
        exist_ok=True
    )

    file_exists = os.path.exists(
        RESULT_FILE
    )

    with open(
        RESULT_FILE,
        "a",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(result)