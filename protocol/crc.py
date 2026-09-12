import zlib


def calculate_crc(data: bytes) -> int:
    return zlib.crc32(data)


def verify_crc(data: bytes, checksum: int) -> bool:
    return calculate_crc(data) == checksum