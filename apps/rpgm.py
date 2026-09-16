from cwio import *
from cwio.const import *
from cwio.screen import MonoImage
import ui

lib = True
name = "RPGMaker engine"

class Tile:
    def __init__(self, data: MonoImage):
        self.data = data
        
    


class Tilemap:
    def __init__(self, w: int, h: int, data: list[list[Tile]]):
        self.w = w
        self.h = h
        self.data = data
        
    


class Character:
    def __init__(self, up: MonoImage, down: MonoImage, left: MonoImage, right: MonoImage):
        self.up = up
        self.down = down
        self.left = left
        self.right = right
        
    


class Sprite:
    def __init__(self, x: int, y: int, dir: int, chr: Character):
        self.x = x
        self.y = y
        self.dir = dir
        self.chr = chr
        
    


class Level:
    def __init__(self, w: int, h: int, tm: Tilemap):
        self.w = w
        self.h = h
        self.tm = tm
        
    


class Game:
    def __init__(self, lvs: list[Level]):
        self.lvs = lvs
        
    
