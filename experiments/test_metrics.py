import time

from experiments.metrics import Metrics


def test_metrics_counts_packets_and_retransmissions():
    metrics = Metrics("go_back_n")

    metrics.data_packet_sent()
    metrics.data_packet_sent()
    metrics.control_packet_sent()
    metrics.packet_received()
    metrics.ack_sent()
    metrics.ack_received()
    metrics.retransmission()

    report = metrics.report(file_size=1000)

    assert report["protocol"] == "go_back_n"
    assert report["file_size"] == 1000
    assert report["data_packets_sent"] == 2
    assert report["control_packets_sent"] == 1
    assert report["packets_received"] == 1
    assert report["acks_sent"] == 1
    assert report["acks_received"] == 1
    assert report["retransmissions"] == 1


def test_metrics_completion_time_and_throughput():
    metrics = Metrics("go_back_n")

    metrics.start_timer()
    time.sleep(0.05)
    metrics.stop_timer()

    duration = metrics.completion_time()
    throughput = metrics.throughput(1000)

    assert duration >= 0.05
    assert throughput > 0


def test_metrics_without_timer_returns_zero():
    metrics = Metrics("go_back_n")

    assert metrics.completion_time() == 0
    assert metrics.throughput(1000) == 0