import picoease as raw
from compat import sleep_ms

read = raw.read
def write(addr, data):
    print(f"CALC WRITE: addr=0x{addr:04X}, data=0x{data:02X}")
    raw.write(addr, data)
init = raw.init

er0 = 0

def halt():
    global er0
    global pc
    print("halt")
    raw.pwrite(13, 8)
    er0 = raw.pread(4)


def resume():
    print("resume")
    print(er0)
    raw.run(0 | ((er0 >> 8) & 255), 256 | (er0 & 255))
    raw.pwrite(13, 0)
    raw.run(65167, 65039)


def connect():
    raw.connect()
    halt()
