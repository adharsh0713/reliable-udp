import struct
from protocol.crc import calculate_crc, verify_crc

DATA = 0
END = 1


class Packet:

    HEADER_FORMAT = "!IBHI"
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(
        self,
        sequence,
        packet_type,
        payload,
        crc=0
    ):
        self.sequence = sequence
        self.packet_type = packet_type
        self.payload = payload
        self.crc = crc


    def encode(self):
        data = self.payload

        header_without_crc = struct.pack(
            "!IBH",
            self.sequence,
            self.packet_type,
            len(data)
        )

        checksum = calculate_crc(
            header_without_crc + data
        )

        header = struct.pack(
            "!IBHI",
            self.sequence,
            self.packet_type,
            len(data),
            checksum
        )

        return header + data


    @staticmethod
    def decode(data):
        sequence, packet_type, length, checksum = struct.unpack(
            "!IBHI",
            data[:11]
        )

        payload = data[11:11+length]

        verify_data = struct.pack(
            "!IBH",
            sequence,
            packet_type,
            length
        ) + payload

        if not verify_crc(
            verify_data,
            checksum
        ):
            raise ValueError("CRC mismatch")

        return Packet(
            sequence,
            packet_type,
            payload,
            checksum
        )

    def __repr__(self):
        return (
            f"Packet(sequence={self.sequence}, "
            f"type={self.packet_type}, "
            f"payload={self.payload})"
        )