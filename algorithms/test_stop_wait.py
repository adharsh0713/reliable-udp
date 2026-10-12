import socket

import pytest

from algorithms import stop_wait
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


def make_data(sequence=0):
    return Packet(sequence, DATA, b"test-payload")


def test_stop_wait_accepts_matching_ack(monkeypatch):
    address = ("127.0.0.1", 5001)
    sock = FakeSocket([make_ack(0, address)])
    metrics = Metrics("stop_wait")

    monkeypatch.setattr(stop_wait, "TIMEOUT", 0.1)

    result = stop_wait.send_packet(
        sock,
        address,
        make_data(0),
        metrics,
    )

    assert result is True
    assert metrics.data_packets_sent == 1
    assert metrics.acks_received == 1


def test_stop_wait_ignores_ack_from_wrong_address(monkeypatch):
    address = ("127.0.0.1", 5001)
    wrong_address = ("127.0.0.1", 9999)

    sock = FakeSocket([
        make_ack(0, wrong_address),
        make_ack(0, address),
    ])
    metrics = Metrics("stop_wait")

    monkeypatch.setattr(stop_wait, "TIMEOUT", 0.1)

    result = stop_wait.send_packet(
        sock,
        address,
        make_data(0),
        metrics,
    )

    assert result is True
    assert metrics.acks_received == 1
    assert metrics.data_packets_sent == 1
    assert len(sock.responses) == 0

def test_stop_wait_stops_after_retry_limit(monkeypatch):
    address = ("127.0.0.1", 5001)
    sock = FakeSocket()
    metrics = Metrics("stop_wait")

    monkeypatch.setattr(stop_wait, "MAX_RETRIES", 2)
    monkeypatch.setattr(stop_wait, "TIMEOUT", 0.1)

    with pytest.raises(TimeoutError):
        stop_wait.send_packet(
            sock,
            address,
            make_data(0),
            metrics,
        )

    assert metrics.data_packets_sent == 2
    assert sock.timeout is None