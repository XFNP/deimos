from cwio import *
from cwio.const import *
import wifi
from wifi import wlan
if wifi.support:
    import requests as rq

name = "HTTP Server"
requires = ["wifi"]

def main():
    pass
