from network.fault_injector import FaultInjector


injector = FaultInjector(
    loss_rate=0.2
)

total_packets = 1000
dropped = 0


for _ in range(total_packets):

    if injector.should_drop():
        dropped += 1


print(f"Total packets: {total_packets}")
print(f"Dropped packets: {dropped}")

loss_percentage = (dropped / total_packets) * 100

print(f"Loss rate: {loss_percentage:.2f}%")