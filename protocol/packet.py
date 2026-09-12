import struct


DATA = 0
END = 1


class Packet:

    HEADER_FORMAT = "!IBH"
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(self, sequence, packet_type, payload=b""):
        self.sequence = sequence
        self.packet_type = packet_type
        self.payload = payload


    def encode(self):

        header = struct.pack(
            self.HEADER_FORMAT,
            self.sequence,
            self.packet_type,
            len(self.payload)
        )

        return header + self.payload


    @classmethod
    def decode(cls, raw):

        sequence, packet_type, length = struct.unpack(
            cls.HEADER_FORMAT,
            raw[:cls.HEADER_SIZE]
        )

        payload = raw[
            cls.HEADER_SIZE:
            cls.HEADER_SIZE + length
        ]

        return cls(
            sequence,
            packet_type,
            payload
        )