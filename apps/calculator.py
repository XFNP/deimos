from cwio import *
from cwio.const import *
from cwio.screen import MonoImage
import math
import ui

name = "Calculator"

def clamp(min: int, max: int, n: int):
    if (min <= n <= max):
        return n
    elif n < min:
        return min
    else:
        return max


def reprover(s: str | None = None):
    class Function:
        def __init__(self, func):
            self.func = func
            self.name = s or self.func.__name__
        
        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)
        
        def __repr__(self):
            return self.name
        
    
    def decorator(f):
        return Function(f)
    
    return decorator


class func:
    @reprover("sin")
    def sin(a: int | float):
        return math.sin(math.radians(a))
    
    @reprover("cos")
    def cos(a: int | float):
        return math.cos(math.radians(a))
    
    @reprover("tan")
    def tan(a: int | float):
        return math.tan(math.radians(a))
    
    @reprover("sin\uE011")
    def asin(a: int | float):
        return math.asin(math.radians(a))
    
    @reprover("cos\uE011")
    def acos(a: int | float):
        return math.acos(math.radians(a))
    
    @reprover("tan\uE011")
    def atan(a: int | float):
        return math.atan(math.radians(a))
    
    @reprover("\u221A")
    def sqrt(a: int | float):
        return math.sqrt(a)
    
    @reprover("ask")
    def ask(a: str):
        return ui.ask(str(a))
    
    @reprover("sel")
    def sel(a: list[str]):
        return ui.choose(list(a))
    

class var:
    ans = 0
    x = 0
    y = 0
    z = 0


replaces = {"\uF000": ("sin", "func.sin"), "\uF001": ("sin\uE011", "func.asin"), "\uF002": ("cos", "func.cos"), "\uF003": ("cos\uE011", "func.acos"), "\uF004": ("tan", "func.tan"), "\uF005": ("tan\uE011", "func.atan"), "\uF006": ("\u221A", "func.sqrt"), "\uF007": ("Ans", "var.ans"), "\uF008": ("ask", "func.ask"), "\uF009": ("sel", "func.sel"), "\uF010": ("\U0001D499", "var.x"), "\uF011": ("\U0001D49A", "var.y"), "\uF012": ("\U0001D49B", "var.z"), "^": ("^", "**")}

def main():
    buf = ""
    pos = 0
    get = False
    shift = False
    tools = False
    while True:
        screen.clear()
        toprint1 = buf[:pos]
        for k, v in replaces.items():
            toprint1 = toprint1.replace(k, v[0])
        toprint2 = buf[pos:]
        for k, v in replaces.items():
            toprint2 = toprint2.replace(k, v[0])
        toprint = toprint1 + toprint2
        if shift:
            screen.rect(SCR.WIDTH - 10, SCR.HEIGHT - 8, 5, 8, SCR.COLOR.BLACK)
        if tools:
            screen.rect(SCR.WIDTH - 5, SCR.HEIGHT - 8, 5, 8, SCR.COLOR.BLACK)
        screen.write("S", SCR.WIDTH - 9, SCR.HEIGHT - 8, (SCR.COLOR.WHITE if shift else SCR.COLOR.BLACK), font.miniwi)
        screen.write("T", SCR.WIDTH - 4, SCR.HEIGHT - 8, (SCR.COLOR.WHITE if tools else SCR.COLOR.BLACK), font.miniwi)
        screen.write(toprint + ("=" if get else ""), 0, 0, SCR.COLOR.BLACK, font.classwiz_cw)
        if not get:
            screen.write("|", 11 * len((toprint1.split("\n")[-1])), 14 * toprint1.count("\n"), SCR.COLOR.DARK, font.classwiz_cw)
        if get:
            try:
                if buf == "":
                    ans = "0"
                    
                elif buf == "1+1":
                    ans = "3"
                    
                elif buf == "6+7":
                    ans = "67"
                    
                elif buf == "9+10":
                    ans = "21"
                    
                elif buf == "9/11":
                    ans = "2001"
                    
                elif buf == "http":
                    ans = "200 OK"
                    
                else:
                    expr = buf
                    for k, v in replaces.items():
                        expr = expr.replace(k, v[1])
                    print("[EVAL] Parsing \"" + expr + "\"")
                    ans = ""
                    if get == "plot/y":
                        cx = SCR.WIDTH // 2
                        cy = SCR.HEIGHT // 2
                        screen.clear()
                        screen.line_v(cx, 0, SCR.HEIGHT, SCR.COLOR.DARK)
                        screen.line_h(0, cy, SCR.WIDTH, SCR.COLOR.DARK)
                        screen.apply()
                        parts = expr.count(";") + 1
                        for x in range(0, SCR.WIDTH):
                            for part in expr.split(";"):
                                if part == "":
                                    continue
                                var.x = x - cx
                                var.y = eval(part)
                                y = math.floor(var.y)
                                if parts == 1:
                                    if y > 0:
                                        screen.line_v(x, cy - y, y, SCR.COLOR.BRIGHT)
                                    else:
                                        screen.line_v(x, cy + 1, -y - 1, SCR.COLOR.BRIGHT)
                                screen.set(x, math.floor(cy - var.y), SCR.COLOR.BLACK)
                            screen.apply()
                    else:
                        ans = eval(expr)
                        var.ans = ans
                result = str(ans)
            except (SyntaxError, ZeroDivisionError) as e:
                result = str(e)
                if result.startswith("invalid syntax"):
                    result = "invalid syntax"
            except TypeError as e:
                err = str(e)
                result = "syntax error"
                if err.startswith("function takes"):
                    pass
                elif err.startswith("unsupported types"):
                    pass
                else:
                    raise e
            except AttributeError:
                result = "invalid syntax"
            except NameError:
                result = "invalid name"
            except ValueError as e:
                err = str(e)
                result = "value error"
                if err.startswith("math domain"):
                    pass
                else:
                    raise e
            
            print("[EVAL] Result: \"" + result + "\"")
            screen.write(result, 0, SCR.HEIGHT - 14, SCR.COLOR.BLACK, font.classwiz_cw)
            get = False
        screen.apply()
        while keyboard.pressed_any():
            pass
        key = keyboard.get_next()
        chr = None
        mov = 0
        if key == KB.KEY.SHIFT:
            shift = not shift
        elif key == KB.KEY.TOOLS:
            tools = not tools
        elif shift and not tools:
            shift = False
            tools = False
            if key == KB.KEY.LEFT:
                pos = 0
            elif key == KB.KEY.RIGHT:
                pos = len(buf)
            elif key == KB.KEY.LPAREN:
                chr = "="
            elif key == KB.KEY.RPAREN:
                chr = ","
            elif key == KB.KEY.MULTIPLY:
                chr = "%"
            elif key == KB.KEY.SIN:
                chr = "\uF001()"
                ((mov := mov-1)+1)
            elif key == KB.KEY.COS:
                chr = "\uF003()"
                ((mov := mov-1)+1)
            elif key == KB.KEY.TAN:
                chr = "\uF005()"
                ((mov := mov-1)+1)
            elif key == KB.KEY.ADD:
                chr = "\"\""
                ((mov := mov-1)+1)
            elif key == KB.KEY.ANS:
                chr = "\uF008()"
                mov -= 1
            elif key == KB.KEY.N0:
                chr = "\uF010"
            elif key == KB.KEY.DOT:
                chr = "\uF011"
            elif key == KB.KEY.POWER_10:
                chr = "\uF012"
            
        elif tools and not shift:
            tools = False
            shift = False
            if key == KB.KEY.LPAREN:
                chr = "[]"
                ((mov := mov-1)+1)
            elif key == KB.KEY.RPAREN:
                chr = "]"
            elif key == KB.KEY.MULTIPLY:
                chr = "!"
            elif key == KB.KEY.DOT:
                chr = ":"
            elif key == KB.KEY.ANS:
                chr = "\uF009([])"
                mov -= 2
            elif key == KB.KEY.FORMAT:
                chr = "\\"
            elif key == KB.KEY.EXE:
                chr = "\n"
            
        elif shift and tools:
            shift = False
            tools = False
            if key == KB.KEY.RPAREN:
                chr = ";"
        else:
            if key == KB.KEY.BKSPACE:
                if pos > 0:
                    buf = buf[:pos - 1] + buf[pos:]
                    pos -= 1
                else:
                    buf = buf[1:]
            elif key == KB.KEY.AC:
                buf = ""
                pos = 0
            elif key == KB.KEY.LEFT:
                if pos > 0:
                    pos -= 1
                else:
                    pos = len(buf)
            elif key == KB.KEY.RIGHT:
                if pos < len(buf):
                    pos += 1
                else:
                    pos = 0
            elif key == KB.KEY.FORMAT:
                chr = ui.ask("Insert text")
            elif key == KB.KEY.CATALOG:
                c = ui.choose(("Plot y",))
                if c == 0:
                    get = "plot/y"
            elif key == KB.KEY.HOME:
                break
            elif key == KB.KEY.EXE:
                get = True
            elif key == KB.KEY.N0:
                chr = "0"
            elif key == KB.KEY.N1:
                chr = "1"
            elif key == KB.KEY.N2:
                chr = "2"
            elif key == KB.KEY.N3:
                chr = "3"
            elif key == KB.KEY.N4:
                chr = "4"
            elif key == KB.KEY.N5:
                chr = "5"
            elif key == KB.KEY.N6:
                chr = "6"
            elif key == KB.KEY.N7:
                chr = "7"
            elif key == KB.KEY.N8:
                chr = "8"
            elif key == KB.KEY.N9:
                chr = "9"
            elif key == KB.KEY.DOT:
                chr = "."
            elif key == KB.KEY.ADD:
                chr = "+"
            elif key == KB.KEY.SUBTRACT:
                chr = "-"
            elif key == KB.KEY.MULTIPLY:
                chr = "*"
            elif key == KB.KEY.DIVIDE:
                chr = "/"
            elif key == KB.KEY.POWER:
                chr = "^"
            elif key == KB.KEY.POWER_2:
                chr = "^2"
            elif key == KB.KEY.POWER_10:
                chr = "*10^()"
                ((mov := mov-1)+1)
            elif key == KB.KEY.SIN:
                chr = "\uF000()"
                ((mov := mov-1)+1)
            elif key == KB.KEY.COS:
                chr = "\uF002()"
                ((mov := mov-1)+1)
            elif key == KB.KEY.TAN:
                chr = "\uF004()"
                ((mov := mov-1)+1)
            elif key == KB.KEY.SQRT:
                chr = "\uF006()"
                ((mov := mov-1)+1)
            elif key == KB.KEY.LPAREN:
                chr = "()"
                ((mov := mov-1)+1)
            elif key == KB.KEY.RPAREN:
                chr = ")"
            elif key == KB.KEY.ANS:
                chr = "\uF007"
            elif key == KB.KEY.X:
                chr = "\uF010"
            
        if chr:
            buf = buf[:pos] + chr + buf[pos:]
            pos += len(chr) + mov
        if pos < 0:
            pos = 0
