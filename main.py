from cwio import *
from cwio.const import *
from cwio.font import Font
import compat
import machine
from machine import Pin
import sys
import os
import power
import ui
from ui import choose
import res
import wifi
from wifi import wlan
import update
import garbage
import loader
from loader import apps



print("MAIN: start")

print("MAIN: init()")
init()
print("MAIN: init() done")

print("MAIN: screen.on()")
screen.on()
print("MAIN: screen.on() done")

print("MAIN: screen.init()")
screen.init()
print("MAIN: screen.init() done")

print("MAIN: keyboard.init()")
keyboard.init()
print("MAIN: keyboard.init() done")

print("MAIN: creating Screen")
scr = ui.Screen()
print("MAIN: Screen created")

print("MAIN: creating title")
title = ui.Label(
    0,
    0,
    "Welcome to Deimos",
    SCR.COLOR.BLACK,
    font.classwiz_cw
)
print("MAIN: title created")

print("MAIN: adding title")
scr + title
print("MAIN: title added")

print("MAIN: creating description")
desc = ui.Label(
    0,
    20,
    "Press HOME for a list of apps.\n\n"
    "Go to https://github.com/mgismissing/deimos for\n"
    "more info about this project.",
    SCR.COLOR.BLACK,
    font.miniwi
)
print("MAIN: description created")

print("MAIN: adding description")
scr + desc
print("MAIN: description added")

print("MAIN: entering loop")

applist = []
for app in apps:
    module = app[1]
    applist.append(("[LIB] " if hasattr(module, "lib") else "") + module.name)

def protected_run(func):
    try:
        return func()
    except loader.Error:
        pass
    except Exception as e:
        ui.notify("Python error", (type(e).__name__) + ":\n" + (str(e)), res.ui.error, wait = False)
        raise e
    


def run_app(app):
    def run():
        loader.run(app)
    
    protected_run(run)



while True:
    print("LOOP START")

    print("CLEAR")
    screen.clear()

    print("RENDER")
    scr.render()

    print("APPLY")
    screen.apply()

    print("AFTER APPLY")

    key = keyboard.get_next()
    key = keyboard.get_next()
    if key == KB.KEY.SETTINGS:
        c = choose(["Updates", "WiFi", "Power", "Debug"])
        if c == 0:
            if wifi.support:
                c = choose(("From OFW repo", "From custom repo"))
                if c >= 0:
                    if wifi.choose_connect():
                        if c == 0:
                            ui.notify("Updating", "OS will restart automatically after the update.", res.ui.info, wait = False)
                            garbage.collect()
                            if protected_run(update.download):
                                print("[FWUP] Rebooting device")
                                machine.reset()
                            else:
                                ui.notify("Update error", "Something went wrong while downloading the\nupdate.", res.ui.error)
                        elif c == 1:
                            repo = ui.ask("GitHub repo to fetch from:", update.OFW.REPO)
                            if repo.count("/") == 1:
                                ui.notify("Updating", "OS will restart automatically after the update.", res.ui.info, wait = False)
                                
                                garbage.collect()
                                # lambda macro
                                if protected_run((lambda: update.download(repo))):
                                    print("[FWUP] Rebooting device")
                                    machine.reset()
                                else:
                                    ui.notify("Update error", "Something went wrong while downloading the\nupdate. Are you sure the repository you\nspecified exists?", res.ui.error)
                            else:
                                ui.notify("Invalid repo", "https://github.com/" + repo + "\nis not a valid GitHub repo.", res.ui.error)
                        
                    else:
                        ui.notify("No connection", "A stable Internet connection is required to\nperform updates.", res.ui.error)
            else:
                ui.notify("No WiFi support", "WiFi support is required to perform updates.", res.ui.error)
        elif c == 1:
            if wifi.support:
                wifi.choose_connect()
            else:
                ui.notify("No WiFi support", "WiFi support is required to connect to a\nnetwork.", res.ui.error)
        elif c == 2:
            c = choose(["Deep sleep", "Soft reset", "Hard reset"])
            if c == 0:
                power.deepsleep()
            elif c == 1:
                machine.soft_reset()
            elif c == 2:
                machine.reset()
            
        elif c == 3:
            ui.notify("Debug mode", "Control has been redirected to USB", res.ui.info, wait = False)
            raise DebugInterrupt("Returning to REPL")
        
    elif key == KB.KEY.HOME:
        c = choose(applist)
        if c >= 0:
            run_app(apps[c][0])
    elif key == KB.KEY.AC:
        power.deepsleep()
        
