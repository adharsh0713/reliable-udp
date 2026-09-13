from experiments.metrics import Metrics
import time


metrics = Metrics("go_back_n")


metrics.start_timer()


metrics.packet_sent()
metrics.packet_sent()

metrics.packet_received()

metrics.retransmission()


time.sleep(1)


metrics.stop_timer()


result = metrics.report(1000)


print(result)