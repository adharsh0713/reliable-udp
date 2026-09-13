import os


PROTOCOL = os.getenv(
    "PROTOCOL",
    "selective_repeat"
)

WINDOW_SIZE = int(
    os.getenv(
        "WINDOW_SIZE",
        "4"
    )
)

CHUNK_SIZE = int(
    os.getenv(
        "CHUNK_SIZE",
        "4096"
    )
)

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5001

TIMEOUT = 1
MAX_RETRIES = 15


# Receiver output file
OUTPUT_FILE = os.getenv(
    "OUTPUT_FILE",
    f"data/results/{PROTOCOL}_received.txt"
)


# DATA direction
DATA_LOSS_RATE = float(
    os.getenv("DATA_LOSS_RATE", "0.10")
)

DATA_CORRUPTION_RATE = float(
    os.getenv("DATA_CORRUPTION_RATE", "0.05")
)

DATA_DELAY = float(
    os.getenv("DATA_DELAY", "0.2")
)

DATA_DUPLICATE_RATE = float(
    os.getenv("DATA_DUPLICATE_RATE", "0.05")
)


# ACK direction
ACK_LOSS_RATE = float(
    os.getenv("ACK_LOSS_RATE", "0.02")
)

ACK_CORRUPTION_RATE = float(
    os.getenv("ACK_CORRUPTION_RATE", "0.01")
)

ACK_DELAY = float(
    os.getenv("ACK_DELAY", "0.05")
)

ACK_DUPLICATE_RATE = float(
    os.getenv("ACK_DUPLICATE_RATE", "0.01")
)