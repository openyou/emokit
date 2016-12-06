#!/usr/bin/python
# Example of using the gyro values to control mouse movement.
# May or may not work?
import ctypes
import platform
import time
from ctypes import cdll

if platform.system() == "Windows":
    pass

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


def main():
    if not platform.system() == 'Windows':
        screen = Xlib()
    else:
        screen = WinMouse()
    width = screen.width
    height = screen.height

    cursor_x, cursor_y = width // 2, height // 2
    while True:
        updated = False
        packet = headset.dequeue()
        if abs(packet.sensors['X']['value']) > 1:
            cursor_x -= packet.sensors['X']['value']
            updated = True
        if abs(packet.sensors['Y']['value']) > 1:
            cursor_y += packet.sensors['Y']['value']
            updated = True
        cursor_x = max(0, min(cursor_x, width))
        cursor_y = max(0, min(cursor_y, height))
        if updated:
            screen.move_mouse(cursor_x, cursor_y)
        time.sleep(0.001)

if __name__ == "__main__":
    with Emotiv() as headset:
        main()
