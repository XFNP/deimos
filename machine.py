# machine.py
import os
import subprocess
import time

class Pin:
    IN = 0
    OUT = 1

    PULL_UP = 2
    PULL_DOWN = 3
    PULL_HOLD = 4

    LOW = 0
    HIGH = 1

    def __init__(self, pin, mode=None, pull=None, value=None):
        self.id = pin
        self.mode = mode
        self.pull = pull
        self._value = 0 if value is None else int(value)

    def value(self, value=None):
        if value is None:
            return self._value

        self._value = 1 if value else 0

    def on(self):
        self._value = 1

    def off(self):
        self._value = 0


def reset():
    # Linux equivalent of a hard MicroPython reset.
    os.execv(
        os.sys.executable,
        [os.sys.executable] + os.sys.argv
    )


def soft_reset():
    reset()


def deepsleep(ms=None):
    if ms is None:
        while True:
            time.sleep(3600)

    time.sleep(ms / 1000.0)


def freq():
    # RP2040/MicroPython compatibility.
    return 150000000


def unique_id():
    try:
        with open("/proc/cpuinfo", "rb") as f:
            data = f.read()

        import hashlib
        return hashlib.sha256(data).digest()[:8]
    except Exception:
        return b"\x00" * 8
