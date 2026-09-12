import struct

from protocol.crc import calculate_crc, verify_crc


DATA = 0
ACK = 1
END = 2

VALID_TYPES = {
    DATA,
    ACK,
    END
}


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

        # Stored checksum from received packet
        # Encoding recalculates CRC
        self.crc = crc


    def encode(self):

        header_without_crc = struct.pack(
            "!IBH",
            self.sequence,
            self.packet_type,
            len(self.payload)
        )

        checksum = calculate_crc(
            header_without_crc + self.payload
        )

        header = struct.pack(
            self.HEADER_FORMAT,
            self.sequence,
            self.packet_type,
            len(self.payload),
            checksum
        )

        return header + self.payload


    @staticmethod
    def decode(data):

        if len(data) < Packet.HEADER_SIZE:
            raise ValueError("Packet too small")


        sequence, packet_type, length, checksum = struct.unpack(
            Packet.HEADER_FORMAT,
            data[:Packet.HEADER_SIZE]
        )


        if packet_type not in VALID_TYPES:
            raise ValueError("Invalid packet type")


        if len(data) < Packet.HEADER_SIZE + length:
            raise ValueError("Incomplete packet")


        payload = data[
            Packet.HEADER_SIZE:
            Packet.HEADER_SIZE + length
        ]


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