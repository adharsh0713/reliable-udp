from network.fault_injector import FaultInjector


injector = FaultInjector(
    loss_rate=0.0,
    corruption_rate=0.5
)


packet = b"hello"


for i in range(10):

    result = injector.process_packet(packet)

    if result is None:
        print("Dropped")

    elif result != packet:
        print("Corrupted")

    else:
        print("Delivered")