from network.fault_injector import FaultInjector

injector = FaultInjector(
    loss_rate=0.2
)

# for i in range(10):
#     if injector.should_drop():
#         print("Packet dropped")

#     else:
#         print("Packet delivered")

data = b"hello"

corrupted = injector.corrupt_data(data)

print(data)
print(corrupted)