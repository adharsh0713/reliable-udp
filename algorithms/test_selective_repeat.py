import socket
import pytest

from experiments.metrics import Metrics
from protocol.packet import Packet, DATA, ACK


def make_ack(sequence, address=("127.0.0.1", 5001)):
    return Packet(sequence, ACK, b"").encode(), address


def make_packets(count):
    return [
        Packet(sequence, DATA, f"packet-{sequence}".encode())
        for sequence in range(count)
    ]


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


def test_selective_repeat_ignores_non_ack_packets(monkeypatch):
    from algorithms import selective_repeat

    address = ("127.0.0.1", 5001)
    sock = FakeSocket([
        (
            Packet(0, DATA, b"not an ACK").encode(),
            address,
        ),
        make_ack(0, address),
    ])
    metrics = Metrics("selective_repeat")

    monkeypatch.setattr(selective_repeat, "WINDOW_SIZE", 1)

    selective_repeat.send_file(
        sock,
        address,
        make_packets(1),
        metrics,
    )

    # The DATA packet must not be counted as an ACK.
    assert metrics.acks_received == 1
    assert metrics.data_packets_sent == 1


def test_selective_repeat_ignores_ack_from_wrong_address(monkeypatch):
    from algorithms import selective_repeat

    address = ("127.0.0.1", 5001)
    wrong_address = ("127.0.0.1", 9999)

    sock = FakeSocket([
        make_ack(0, wrong_address),
        make_ack(0, address),
    ])
    metrics = Metrics("selective_repeat")

    monkeypatch.setattr(selective_repeat, "WINDOW_SIZE", 1)

    selective_repeat.send_file(
        sock,
        address,
        make_packets(1),
        metrics,
    )

    # Only the valid ACK from the expected address should count.
    assert metrics.acks_received == 1
    assert metrics.data_packets_sent == 1


def test_selective_repeat_does_not_count_unrelated_ack(monkeypatch):
    from algorithms import selective_repeat

    address = ("127.0.0.1", 5001)
    sock = FakeSocket([
        make_ack(99, address),
        make_ack(0, address),
    ])
    metrics = Metrics("selective_repeat")

    monkeypatch.setattr(selective_repeat, "WINDOW_SIZE", 1)

    selective_repeat.send_file(
        sock,
        address,
        make_packets(1),
        metrics,
    )

    assert metrics.acks_received == 1
    assert metrics.data_packets_sent == 1
    from algorithms import selective_repeat

    address = ("127.0.0.1", 5001)
    wrong_address = ("127.0.0.1", 9999)

    sock = FakeSocket([
        make_ack(0, wrong_address),
        make_ack(0, address),
    ])
    metrics = Metrics("selective_repeat")

    monkeypatch.setattr(selective_repeat, "WINDOW_SIZE", 1)

    selective_repeat.send_file(
        sock,
        address,
        make_packets(1),
        metrics,
    )

    assert metrics.acks_received == 1
    assert metrics.data_packets_sent == 1

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

def test_selective_repeat_stops_after_retry_limit(monkeypatch):
    from algorithms import selective_repeat

    address = ("127.0.0.1", 5001)
    sock = FakeSocket()
    metrics = Metrics("selective_repeat")

    monkeypatch.setattr(selective_repeat, "WINDOW_SIZE", 1)
    monkeypatch.setattr(selective_repeat, "TIMEOUT", 0.001)
    monkeypatch.setattr(selective_repeat, "MAX_RETRIES", 2)

    with pytest.raises(TimeoutError, match="after 2 retransmissions"):
        selective_repeat.send_file(
            sock,
            address,
            make_packets(1),
            metrics,
        )

    assert metrics.retransmissions == 2
    assert metrics.data_packets_sent == 3