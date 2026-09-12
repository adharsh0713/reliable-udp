from algorithms.stop_wait import send_file as stop_wait
from algorithms.go_back_n import send_file as go_back_n
from algorithms.selective_repeat import send_file as selective_repeat


PROTOCOLS = {
    "stop_wait": stop_wait,
    "go_back_n": go_back_n,
    "selective_repeat": selective_repeat,
}


def get_protocol(name):
    return PROTOCOLS[name]