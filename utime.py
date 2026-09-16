# utime.py
import time as _time

sleep = _time.sleep

def sleep_ms(ms):
    _time.sleep(ms / 1000.0)

def sleep_us(us):
    _time.sleep(us / 1_000_000.0)

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

def localtime(secs=None):
    if secs is None:
        return _time.localtime()
    return _time.localtime(secs)

def mktime(t):
    return _time.mktime(t)

def monotonic():
    return _time.monotonic()
