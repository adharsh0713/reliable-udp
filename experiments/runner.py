import hashlib
import os
import subprocess
import sys
import time

from experiments.launcher import (
    start_receiver,
    start_proxy,
    merge_metrics,
)
from experiments.results import save_result

TEST_FILES = [
    "small.txt",
    "medium.txt",
    "large.txt",
    "image.jpg",
]
TEST_DIR = "data/test_files"
RESULT_DIR = "data/results"
RECEIVED_DIR = os.path.join(RESULT_DIR, "received")

RUNS = 3
WINDOW_VALUES = [1, 4, 16]
PROTOCOLS = [
    "stop_wait",
    "go_back_n",
    "selective_repeat",
]
LOSS_VALUES = [0.0, 0.1, 0.2]

SENDER_METRICS = os.path.join(RESULT_DIR, "sender_metrics.json")
RECEIVER_METRICS = os.path.join(RESULT_DIR, "receiver_metrics.json")

def sha256_file(path):
    digest = hashlib.sha256()

    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)

    return digest.hexdigest()


def stop_process(process):
    if process is None:
        return

    if process.poll() is None:
        process.terminate()

    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def run_experiment(protocol, filename, loss, window, run):
    file_path = os.path.join(TEST_DIR, filename)

    if not os.path.isfile(file_path):
        raise FileNotFoundError(
            f"Test file does not exist: {file_path}"
        )

    output_file = os.path.join(
        RECEIVED_DIR,
        f"{protocol}_{os.path.splitext(filename)[0]}"
        f"_window{window}_loss{loss}_run{run}"
        f"{os.path.splitext(filename)[1]}",
    )

    os.makedirs(RECEIVED_DIR, exist_ok=True)
    os.makedirs(RESULT_DIR, exist_ok=True)

    # Prevent previous metrics from being mistaken for this run.
    for path in (SENDER_METRICS, RECEIVER_METRICS):
        if os.path.exists(path):
            os.remove(path)

    env = os.environ.copy()
    env.update({
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
        "ACK_DUPLICATE_RATE": "0",
    })

    receiver = None
    proxy = None

    try:
        print(
            f"\nProtocol={protocol}, file={filename}, "
            f"window={window}, loss={loss}, run={run}"
        )

        receiver = start_receiver(env)
        time.sleep(1)

        if receiver.poll() is not None:
            raise RuntimeError(
                "Receiver exited during startup."
            )

        proxy = start_proxy(env)
        time.sleep(1)

        if proxy.poll() is not None:
            raise RuntimeError(
                "Proxy exited during startup."
            )

        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "sender.sender",
                file_path,
            ],
            env=env,
            check=False,
        )

        if completed.returncode != 0:
            raise RuntimeError(
                f"Sender exited with code {completed.returncode}"
            )

        if not os.path.isfile(output_file):
            raise RuntimeError(
                "Receiver output file was not created."
            )

        source_hash = sha256_file(file_path)
        received_hash = sha256_file(output_file)

        if source_hash != received_hash:
            raise RuntimeError(
                "SHA-256 mismatch: received file differs from source."
            )

        if not os.path.isfile(SENDER_METRICS):
            raise RuntimeError("Sender metrics were not created.")

        if not os.path.isfile(RECEIVER_METRICS):
            raise RuntimeError("Receiver metrics were not created.")

        result = merge_metrics()

        result.update({
            "file_name": filename,
            "file_size": os.path.getsize(file_path),
            "window": window,
            "run": run,
            "data_loss": loss,

            "data_delay": 0,
            "data_corruption": 0,
            "data_duplicate": 0,

            "ack_loss": 0,
            "ack_delay": 0,
            "ack_corruption": 0,
            "ack_duplicate": 0,

            "hash_verified": True,
        })

        print("Transfer and SHA-256 verification passed.")
        print(result)

        save_result(result)
        return result

    finally:
        stop_process(proxy)
        stop_process(receiver)


def main():
    failures = []

    for protocol in PROTOCOLS:
        windows = [1] if protocol == "stop_wait" else WINDOW_VALUES

        for filename in TEST_FILES:
            for loss in LOSS_VALUES:
                for window in windows:
                    for run in range(1, RUNS + 1):
                        try:
                            run_experiment(
                                protocol,
                                filename,
                                loss,
                                window,
                                run,
                            )
                        except Exception as error:
                            failure = {
                                "protocol": protocol,
                                "file_name": filename,
                                "data_loss": loss,
                                "window": window,
                                "run": run,
                                "error": str(error),
                            }
                            failures.append(failure)
                            print(f"EXPERIMENT FAILED: {failure}")

    print("\n========== EXPERIMENT SUMMARY ==========")
    print(f"Failures: {len(failures)}")

    for failure in failures:
        print(failure)

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()