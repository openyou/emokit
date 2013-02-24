#!/usr/bin/python
import ctypes
from ctypes import cdll

import sys
import platform
import gevent

from emokit.emotiv import Emotiv

class Xlib:
    def __init__(self):
        self.xlib = cdll.LoadLibrary('libX11.so')

        display = self.xlib.XOpenDisplay(None)
        dflt_screen_num = self.xlib.XDefaultScreen(display)
        default_screen = self.xlib.XScreenOfDisplay(display, dflt_screen_num)

        self.width = self.xlib.XWidthOfScreen(default_screen)
        self.height = self.xlib.XHeightOfScreen(default_screen)
        self.xlib.XCloseDisplay(display)

    def move_mouse(self, x, y):
        display = self.xlib.XOpenDisplay(None)
        root = self.xlib.XDefaultRootWindow(display)
        self.xlib.XWarpPointer(display, None, root, 0, 0, 0, 0, x, y)
        self.xlib.XCloseDisplay(display)


class WinMouse:
    def __init__(self):
        user32 = ctypes.windll.user32
        self.width = user32.GetSystemMetrics(0)
        self.height = user32.GetSystemMetrics(1)

    def click(self, x, y):
        ctypes.windll.user32.SetCursorPos(x, y)
        ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0) # left down
        ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0) # left up

    def move_mouse(self, x, y):
        ctypes.windll.user32.SetCursorPos(x, y)


def main(debug=False):
    if not platform.system() == 'Windows':
        screen = Xlib()
        width = screen.width
        height = screen.height
    else:
        screen = WinMouse()
        width = screen.width
        height = screen.height

        curX, curY = width / 2, height / 2
        while True:
            updated = False
            packet = emotiv.dequeue()
            if abs(packet.gyroX) > 1:
                curX -= packet.gyroX
                updated = True
            if abs(packet.gyroY) > 1:
                curY += packet.gyroY
                updated = True
            curX = max(0, min(curX, width))
            curY = max(0, min(curY, height))
            if updated:
                screen.move_mouse(curX, curY)
            gevent.sleep(0)


emotiv = None
if __name__ == "__main__":
    try:
        emotiv = Emotiv()
        gevent.spawn(emotiv.setup)
        gevent.sleep(1)
        main(*sys.argv[1:])

    finally:
        if emotiv:
            emotiv.close()


