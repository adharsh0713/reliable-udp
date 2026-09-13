import os
import time
import config

from experiments.launcher import (
    start_receiver,
    start_proxy,
    merge_metrics
)

from sender.sender import send_file
from experiments.results import save_result


TEST_FILES = [
    "small.txt",
    "medium.txt",
    # "large.txt",
    # "image.jpg"
]


TEST_DIR = "data/test_files"

RUNS = 3


WINDOW_VALUES = [
    1,
    4,
    # 8,
    16
]


PROTOCOLS = [
    "stop_wait",
    "go_back_n",
    "selective_repeat"
]


LOSS_VALUES = [
    0.0,
    # 0.1,
    0.2
]


def run_experiment(protocol, filename, loss, window, run):

    print(
        "\n===================="
    )

    print(
        f"Protocol: {protocol}"
    )

    print(
        f"Window: {window}"
    )

    print(
        f"Loss: {loss}"
    )

    print(
        f"Run: {run}"
    )


    config.PROTOCOL = protocol
    config.DATA_LOSS_RATE = loss
    config.WINDOW_SIZE = window


    env = os.environ.copy()

    output_file = os.path.join(
        "data",
        "results",
        "received",
        f"{protocol}_{filename}_window{window}_run{run}"
    )


    os.makedirs(
        "data/results/received",
        exist_ok=True
    )


    env.update(
        {
            "PROTOCOL": protocol,

            "WINDOW_SIZE": str(window),

            "OUTPUT_FILE": output_file,

            "DATA_LOSS_RATE": str(loss),

            "DATA_CORRUPTION_RATE": "0",
            "DATA_DELAY": "0",
            "DATA_DUPLICATE_RATE": "0",

            "ACK_LOSS_RATE": "0",
            "ACK_CORRUPTION_RATE": "0",
            "ACK_DELAY": "0",
            "ACK_DUPLICATE_RATE": "0"
        }
    )


    try:

        file_path = os.path.join(
            TEST_DIR,
            filename
        )


        send_file(
            file_path
        )


        result = merge_metrics()


        result.update(
            {
                "file_name": filename,

                "file_size": os.path.getsize(
                    file_path
                ),

                "window": window,

                "run": run,

                "data_loss": loss,

                "data_delay": 0,
                "data_corruption": 0,
                "data_duplicate": 0,

                "ack_loss": 0,
                "ack_delay": 0,
                "ack_corruption": 0,
                "ack_duplicate": 0
            }
        )


        print(result)


        save_result(
            result
        )


    except Exception as e:

        print(
            "Experiment failed:",
            e
        )



def run_protocol(protocol):

    if protocol == "stop_wait":
        windows = [1]
    else:
        windows = WINDOW_VALUES


    for filename in TEST_FILES:

        for loss in LOSS_VALUES:

            for window in windows:

                for run in range(1, RUNS + 1):

                    env = os.environ.copy()

                    env.update(
                        {
                            "PROTOCOL": protocol,
                            "WINDOW_SIZE": str(window),
                            "DATA_LOSS_RATE": str(loss)
                        }
                    )


                    receiver = start_receiver(env)

                    time.sleep(1)

                    proxy = start_proxy(env)

                    time.sleep(1)


                    try:

                        run_experiment(
                            protocol,
                            filename,
                            loss,
                            window,
                            run
                        )


                    finally:

                        receiver.terminate()
                        proxy.terminate()

                        receiver.wait()
                        proxy.wait()

                        time.sleep(1)

def main():

    for protocol in PROTOCOLS:

        run_protocol(
            protocol
        )



if __name__ == "__main__":

    main()