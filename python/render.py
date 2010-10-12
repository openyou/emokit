#!/usr/bin/python

try:
	import psyco
	psyco.full()
except:
	print 'No psyco.  Expect poor performance.'

import pygame, sys, time, logging
from emotiv import Emotiv

class Grapher(object):
	def __init__(self, screen, name, i):
		self.screen = screen
		self.name = name
		self.range = float(1 << 13)
		self.xoff = 40
		self.y = i * gheight
		self.buffer = []
		font = pygame.font.Font(None, 24)
		self.text = font.render(self.name, 1, (255, 0, 0))
		self.textpos = self.text.get_rect()
		self.textpos.centery = self.y + hgheight
	
	def update(self, packet):
		if len(self.buffer) == 800 - self.xoff:
			self.buffer = self.buffer[1:]
		self.buffer.append(getattr(packet, self.name))
	
	def calcY(self, val):
		return int(val / self.range * gheight)
	
	def draw(self):
		if len(self.buffer) == 0:
			return
		pos = self.xoff, self.calcY(self.buffer[0][0]) + self.y
		for i, (x, strength) in enumerate(self.buffer):
			y = self.calcY(x) + self.y
			if strength == 0:
				color = (0, 0, 0)
			elif strength == 1:
				color = (255, 0, 0)
			elif strength == 2:
				color = (255, 165, 0)
			elif strength == 3:
				color = (255, 255, 0)
			elif strength == 4:
				color = (0, 255, 0)
			else:
				color = (255, 255, 255)
			pygame.draw.line(self.screen, color, pos, (self.xoff + i, y))
			pos = (self.xoff+i, y)
		self.screen.blit(self.text, self.textpos)

def main(debug=False):
	global gheight
	
	pygame.init()
	screen = pygame.display.set_mode((800, 600))
	
	curX, curY = 400, 300
	
	graphers = []
	for name in 'AF3 F7 F3 FC5 T7 P7 O1 O2 P8 T8 FC6 F4 F8 AF4'.split(' '):
		graphers.append(Grapher(screen, name, len(graphers)))
	
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return
		
		updated = False
		for packet in emotiv.dequeue():
			updated = True
			if abs(packet.gyroX) > 1:
				curX -= packet.gyroX - 1
			if abs(packet.gyroY) > 1:
				curY += packet.gyroY
			curX = max(0, min(curX, 800))
			curY = max(0, min(curY, 600))
			map(lambda x: x.update(packet), graphers)
		
		if updated:
			screen.fill((75, 75, 75))
			map(lambda x: x.draw(), graphers)
			pygame.draw.rect(screen, (255, 255, 255), (curX-5, curY-5, 10, 10), 0)
			pygame.display.flip()
		time.sleep(1.0/60)


emotiv = None

try:
	logger = logging.getLogger('emotiv')
	logger.setLevel(logging.INFO)
	log_handler = logging.StreamHandler()
	logger.addHandler(log_handler)

	emotiv = Emotiv()

	gheight = 600 / 14
	hgheight = gheight >> 1
	
	main(*sys.argv[1:])

finally:
	if emotiv:
		emotiv.close()
