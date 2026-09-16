import time

def sleep_ms(ms):
    time.sleep(ms)

def sleep_us(us):
    time.sleep(us / 1_000_000.0)

def ticks_ms():
    return time.monotonic_ns() // 1_000_000

def ticks_us():
    return time.monotonic_ns() // 1_000

def ticks_cpu():
    return time.monotonic_ns()

def ticks_diff(a, b):
    return a - b
