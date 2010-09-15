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
		self.range = 32678.0
		self.xoff = 40
		self.y = i * gheight + hgheight
		self.buffer = []
		font = pygame.font.Font(None, 24)
		self.text = font.render(self.name, 1, (255, 0, 0))
		self.textpos = self.text.get_rect()
		self.textpos.centery = self.y
	
	def update(self, packet):
		if len(self.buffer) == 800 - self.xoff:
			self.buffer = self.buffer[1:]
		self.buffer.append(getattr(packet, self.name))
	
	def calcY(self, val):
		return int(val / self.range * gheight * 0.5)
	
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
	if debug == False:
		graphers.append(Grapher(screen, 'L1', len(graphers)))
		graphers.append(Grapher(screen, 'L2', len(graphers)))
		graphers.append(Grapher(screen, 'L3', len(graphers)))
		graphers.append(Grapher(screen, 'L4', len(graphers)))
		graphers.append(Grapher(screen, 'L5', len(graphers)))
		graphers.append(Grapher(screen, 'L6', len(graphers)))
		graphers.append(Grapher(screen, 'L7', len(graphers)))
		graphers.append(Grapher(screen, 'R1', len(graphers)))
		graphers.append(Grapher(screen, 'R2', len(graphers)))
		graphers.append(Grapher(screen, 'R3', len(graphers)))
		graphers.append(Grapher(screen, 'R4', len(graphers)))
		graphers.append(Grapher(screen, 'R5', len(graphers)))
		graphers.append(Grapher(screen, 'R6', len(graphers)))
		graphers.append(Grapher(screen, 'R7', len(graphers)))
	else:
		gheight = 600 / 28
		for x in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 31]:
			graphers.append(Grapher(screen, str(x), len(graphers)))
	
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
