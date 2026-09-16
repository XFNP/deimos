from cwio import *
from cwio.const import *

name = "Geometry Dash"

class Level:
    def __init__(self, h: int, data: bytes):
        self.h = h
        self.data = data
        
    


def play_level(l: Level):
    px, py = 0
    for x in range(0, len(l.data) // l.h, 1):
        col = l.data[x * l.h:(x + 1) * l.h]
        print(col)


levels = {"Stereo Madness": None}

def main():
    pass
