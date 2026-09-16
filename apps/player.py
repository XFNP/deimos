from cwio import *
from cwio.const import *
from cwio.screen import MonoImage
import ui
import os
import time

name = "Video Player"

CHUNK_SIZE = (192 // 8) * 63

def main():
    raw = ui.choose_file()
    with open(raw, "rb") as f:
        while True:
            old = time.ticks_ms()
            screen.clear()
            chunk = f.read(CHUNK_SIZE)
            if not (chunk and len(chunk) >= CHUNK_SIZE):
                break
            screen.image(MonoImage(192, 63, chunk), 0, 0, SCR.COLOR.BLACK)
            screen.apply()
            wait = 500 + time.ticks_diff(old, time.ticks_ms())
            if wait > 0:
                time.sleep_ms(wait)
    
    keyboard.wait()
