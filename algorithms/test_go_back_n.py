import socket

import pytest

from algorithms.go_back_n import GoBackN
from experiments.metrics import Metrics
from protocol.packet import Packet, DATA, ACK


class FakeSocket:
    def __init__(self, responses=None):
        self.responses = list(responses or [])
        self.sent = []
        self.timeout = None

    def sendto(self, data, address):
        self.sent.append((data, address))

    def recvfrom(self, buffer_size):
        if not self.responses:
            raise socket.timeout()

        response = self.responses.pop(0)

        if isinstance(response, Exception):
            raise response

        return response

    def settimeout(self, timeout):
        self.timeout = timeout


def make_ack(sequence, address=("127.0.0.1", 5001)):
    return Packet(sequence, ACK, b"").encode(), address


def make_packets(count):
    return [
        Packet(sequence, DATA, f"packet-{sequence}".encode())
        for sequence in range(count)
    ]


def test_gbn_accepts_cumulative_ack_and_advances_base():
    address = ("127.0.0.1", 5001)
    sock = FakeSocket([
        make_ack(1, address),
        make_ack(2, address),
    ])
    metrics = Metrics("go_back_n")
    gbn = GoBackN(sock, address, metrics)

    packets = make_packets(3)
    gbn.send_window(packets)
    gbn.wait_for_ack(packets)

    assert gbn.base == 3
    assert gbn.next_seq == 3
    assert metrics.acks_received == 2


def test_gbn_ignores_ack_from_unexpected_address():
    address = ("127.0.0.1", 5001)
    wrong_address = ("127.0.0.1", 9999)

    sock = FakeSocket([
        make_ack(0, wrong_address),
        make_ack(0, address),
    ])
    metrics = Metrics("go_back_n")
    gbn = GoBackN(sock, address, metrics)

    packets = make_packets(1)
    gbn.send_window(packets)
    gbn.wait_for_ack(packets)

    assert gbn.base == 1
    assert metrics.acks_received == 1


def test_gbn_rejects_non_ack_packet():
    address = ("127.0.0.1", 5001)
    non_ack = Packet(0, DATA, b"not an ACK").encode()

    sock = FakeSocket([
        (non_ack, address),
        make_ack(0, address),
    ])
    metrics = Metrics("go_back_n")
    gbn = GoBackN(sock, address, metrics)

    packets = make_packets(1)
    gbn.send_window(packets)
    gbn.wait_for_ack(packets)

    assert gbn.base == 1
    assert metrics.acks_received == 1


def test_gbn_rejects_ack_beyond_sent_range():
    address = ("127.0.0.1", 5001)
    sock = FakeSocket([
        make_ack(5, address),
        make_ack(0, address),
    ])
    metrics = Metrics("go_back_n")
    gbn = GoBackN(sock, address, metrics)

    packets = make_packets(1)
    gbn.send_window(packets)
    gbn.wait_for_ack(packets)

    assert gbn.base == 1
    assert metrics.acks_received == 1


def test_gbn_stops_after_retry_limit(monkeypatch):
    address = ("127.0.0.1", 5001)
    sock = FakeSocket()
    metrics = Metrics("go_back_n")
    gbn = GoBackN(sock, address, metrics)

    packets = make_packets(1)

    monkeypatch.setattr(
        "algorithms.go_back_n.MAX_RETRIES",
        2,
    )

    # Simulate the real send/wait cycle. Each timeout resets
    # next_seq to base, so the next iteration must resend.
    gbn.send_window(packets)
    gbn.wait_for_ack(packets)

    gbn.send_window(packets)
    gbn.wait_for_ack(packets)

    gbn.send_window(packets)

    with pytest.raises(TimeoutError, match="no cumulative ACK progress"):
        gbn.wait_for_ack(packets)

    assert gbn.timeout_retries == 2

def test_selective_repeat_retransmits_expired_packet(monkeypatch):
    from algorithms import selective_repeat

    address = ("127.0.0.1", 5001)
    sock = FakeSocket([
        socket.timeout(),
        make_ack(0, address),
    ])
    metrics = Metrics("selective_repeat")

    monkeypatch.setattr(selective_repeat, "WINDOW_SIZE", 1)
    monkeypatch.setattr(selective_repeat, "TIMEOUT", 1.0)

    # Make the packet timer expire deterministically after the
    # simulated timeout instead of depending on wall-clock timing.
    monkeypatch.setattr(
        selective_repeat.Timer,
        "expired",
        lambda self: True,
    )

    selective_repeat.send_file(
        sock,
        address,
        make_packets(1),
        metrics,
    )

    assert metrics.data_packets_sent == 2
    assert metrics.retransmissions == 1
    assert metrics.acks_received == 1
    address = ("127.0.0.1", 5001)
    sock = FakeSocket([
        socket.timeout(),
        make_ack(1, address),
    ])
    metrics = Metrics("go_back_n")
    gbn = GoBackN(sock, address, metrics)

    packets = make_packets(2)

    gbn.send_window(packets)
    gbn.wait_for_ack(packets)

    assert gbn.base == 0
    assert gbn.next_seq == 0

    gbn.send_window(packets)
    gbn.wait_for_ack(packets)

    assert gbn.base == 2
    assert metrics.data_packets_sent == 4
    assert metrics.retransmissions == 2