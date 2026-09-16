import time as _time

sleep = _time.sleep

def sleep_ms(ms):
    _time.sleep(ms / 1000)

def sleep_us(us):
    _time.sleep(us / 1000000.0)

def ticks_ms():
    return _time.monotonic_ns() // 1_000_000

def ticks_us():
    return _time.monotonic_ns() // 1_000

def ticks_cpu():
    return _time.monotonic_ns()

def ticks_diff(a, b):
    return a - b

def ticks_add(a, delta):
    return a + delta

def time():
    return _time.time()

def monotonic():
    return _time.monotonic()
