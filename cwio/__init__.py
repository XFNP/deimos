from . import calc
from . import const
from . import screen
from . import keyboard
from compat import sleep_ms

def init():
    calc.init()
    calc.connect()
    calc.connect()
    calc.connect()
