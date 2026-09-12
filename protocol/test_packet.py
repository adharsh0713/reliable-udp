from protocol.packet import Packet, DATA


packet = Packet(
    1,
    DATA,
    b"hello"
)

encoded = packet.encode()

print("Original:")
print(Packet.decode(encoded))


print("\nCorruption test:")

corrupted = bytearray(encoded)

# Flip one bit in payload
corrupted[-1] ^= 1

try:
    Packet.decode(bytes(corrupted))
    print("ERROR: corruption was not detected")

except ValueError as e:
    print(e)