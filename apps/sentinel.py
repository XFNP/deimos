from cwio import *
from cwio.const import *
import ui

lib = True
name = "Sentinel"
requires = ["cwii"]

class ADDR:
    MODE = 37281
    SUBMODE = 37282
    HISTORY = 37880


def get_mode() -> tuple[int, int]:
    return (calc.read(ADDR.MODE), calc.read(ADDR.SUBMODE))


def set_mode(mode: int | None, submode: int | None) -> None:
    if mode != None:
        calc.write(ADDR.MODE, mode)
    if submode != None:
        calc.write(ADDR.SUBMODE, submode)


def get_history() -> bytes:
    history = bytearray()
    for i in range(0, 400, 1):
        history.append(calc.read(ADDR.HISTORY + i))
    return bytes(history)


def set_history(history: bytes) -> bool:
    if len(history) != 400:
        return False
    for i in range(0, 400, 1):
        calc.write(ADDR.HISTORY + i, history[i])
    return True


def main():
    while True:
        c = ui.choose(["Set mode byte", "Set submode byte", "Inject history", "Resume"])
        if c == 0:
            v = (str(hex(get_mode()[0])))[2:].upper()
            v = eval(ui.ask("New value:", "0x" + ("0" * (2 - len(v))) + v))
            if isinstance(v, int):
                set_mode(v, None)
        elif c == 1:
            v = (str(hex(get_mode()[1])))[2:].upper()
            v = eval(ui.ask("New value:", "0x" + ("0" * (2 - len(v))) + v))
            if isinstance(v, int):
                set_mode(None, v)
        elif c == 2:
            file = ui.choose_file()
            if file != -1:
                with open(file, "rb") as f:
                    data = f.read()
                    if not set_history(data):
                        ui.notify("Malformed file", "The file you chose is not a valid history dump.\nHistory dumps are generally 400B bin files.")
                
        elif c == 3:
            calc.resume()
            print("resumed")
            raise SyntaxError
        elif c == -1:
            break
        
