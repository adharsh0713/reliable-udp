import pytest

from protocol.packet import Packet, DATA, ACK, END


@pytest.mark.parametrize(
    "packet_type,payload",
    [
        (DATA, b"Hello, world!"),
        (ACK, b""),
        (END, b""),
        (DATA, bytes(range(256))),
    ],
)
def test_packet_encode_decode_round_trip(packet_type, payload):
    original = Packet(
        sequence=7,
        packet_type=packet_type,
        payload=payload,
    )

    decoded = Packet.decode(original.encode())

    assert decoded.sequence == original.sequence
    assert decoded.packet_type == original.packet_type
    assert decoded.payload == original.payload


def test_decode_rejects_packet_smaller_than_header():
    with pytest.raises(ValueError, match="Packet too small"):
        Packet.decode(b"\x00")


def test_decode_rejects_incomplete_payload():
    packet = Packet(
        sequence=1,
        packet_type=DATA,
        payload=b"hello",
    ).encode()

    with pytest.raises(ValueError, match="Incomplete packet"):
        Packet.decode(packet[:-1])


def test_decode_rejects_trailing_bytes():
    packet = Packet(
        sequence=1,
        packet_type=DATA,
        payload=b"hello",
    ).encode()

    with pytest.raises(ValueError, match="Unexpected trailing bytes"):
        Packet.decode(packet + b"\x00")


def test_decode_rejects_corrupted_payload():
    packet = bytearray(
        Packet(
            sequence=1,
            packet_type=DATA,
            payload=b"hello",
        ).encode()
    )

    packet[-1] ^= 0x01

    with pytest.raises(ValueError, match="CRC mismatch"):
        Packet.decode(bytes(packet))


def test_decode_rejects_invalid_packet_type():
    packet = bytearray(
        Packet(
            sequence=1,
            packet_type=DATA,
            payload=b"hello",
        ).encode()
    )

    # Header format is !IBHI: packet type is byte index 4.
    packet[4] = 99

    with pytest.raises(ValueError, match="Invalid packet type"):
        Packet.decode(bytes(packet))