#!/usr/bin/python

import sys, time, logging
from ctypes import cdll

from emotiv import Emotiv

class Xlib:
    def __init__(self):
        self.xlib = cdll.LoadLibrary('libX11.so')
        
        display = self.xlib.XOpenDisplay(None)
        dflt_screen_num = self.xlib.XDefaultScreen(display)
        default_screen = self.xlib.XScreenOfDisplay(display, dflt_screen_num)
        
        self.width = self.xlib.XWidthOfScreen(default_screen)
        self.height = self.xlib.XHeightOfScreen(default_screen)
        logger.info("Default screen: %d x %d" % (self.width, self.height))
        self.xlib.XCloseDisplay(display)
        
    def move_mouse(self, x,y):
        display = self.xlib.XOpenDisplay(None)
        root = self.xlib.XDefaultRootWindow(display)
        self.xlib.XWarpPointer(display,None,root,0,0,0,0,x,y)
        self.xlib.XCloseDisplay(display)

def main(debug=False):

	screen = Xlib()
	
	width = screen.width
	height = screen.height
	
	curX, curY = width/2, height/2
	while True:
		updated = False
		for packet in emotiv.dequeue():
			updated = True
			if abs(packet.gyroX) > 1:
				curX -= packet.gyroX - 1
			if abs(packet.gyroY) > 1:
				curY += packet.gyroY
			curX = max(0, min(curX, width))
			curY = max(0, min(curY, height))

		if updated:
			screen.move_mouse(curX, curY)
		time.sleep(1.0/60)


emotiv = None

try:
	logger = logging.getLogger('emotiv')
	logger.setLevel(logging.INFO)
	log_handler = logging.StreamHandler()
	logger.addHandler(log_handler)

	emotiv = Emotiv()

	
	main(*sys.argv[1:])

finally:
	if emotiv:
		emotiv.close()

