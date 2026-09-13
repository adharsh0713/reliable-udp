import subprocess
import time
import json

from sender.sender import send_file
from experiments.results import save_result

def start_receiver(env):

    return subprocess.Popen(
        [
            "python",
            "-m",
            "receiver.receiver"
        ],
        env=env
    )


def start_proxy(env):

    return subprocess.Popen(
        [
            "python",
            "-m",
            "network.proxy"
        ],
        env=env
    )


def start_sender(filename):

    return subprocess.run(
        [
            "python",
            "-m",
            "sender.sender",
            filename
        ]
    )


def run_experiment(filename):

    receiver = start_receiver()

    time.sleep(1)

    proxy = start_proxy()

    time.sleep(1)

    try:

        result = send_file(
            filename
        )

        print(result)

        final_result = merge_metrics()

        print(final_result)

        save_result(
            final_result
        )

    finally:

        receiver.terminate()
        proxy.terminate()

def merge_metrics():

    with open(
        "data/results/sender_metrics.json"
    ) as file:
        sender = json.load(file)


    with open(
        "data/results/receiver_metrics.json"
    ) as file:
        receiver = json.load(file)


    result = sender.copy()


    result.update(
        {
            "packets_received":
                receiver["packets_received"],

            "acks_sent":
                receiver["acks_sent"]
        }
    )

    return result


if __name__ == "__main__":

    run_experiment(
        "data/test_files/sample.txt"
    )