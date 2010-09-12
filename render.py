import emotiv, pygame, time

emotiv = emotiv.Emotiv()

gheight = 600 / 14
hgheight = gheight >> 1

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
		if len(self.buffer) == 1024 - self.xoff:
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

def main():
	pygame.init()
	screen = pygame.display.set_mode((1024, 600))
	
	curX, curY = 512, 300
	
	graphers = []
	graphers.append(Grapher(screen, 'AF3', len(graphers)))
	graphers.append(Grapher(screen, 'AF4', len(graphers)))
	graphers.append(Grapher(screen, 'F3', len(graphers)))
	graphers.append(Grapher(screen, 'F4', len(graphers)))
	graphers.append(Grapher(screen, 'F7', len(graphers)))
	graphers.append(Grapher(screen, 'F8', len(graphers)))
	graphers.append(Grapher(screen, 'FC5', len(graphers)))
	graphers.append(Grapher(screen, 'FC6', len(graphers)))
	graphers.append(Grapher(screen, 'T7', len(graphers)))
	graphers.append(Grapher(screen, 'T8', len(graphers)))
	graphers.append(Grapher(screen, 'P7', len(graphers)))
	graphers.append(Grapher(screen, 'P8', len(graphers)))
	graphers.append(Grapher(screen, 'O1', len(graphers)))
	graphers.append(Grapher(screen, 'O2', len(graphers)))
	#for x in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 31]:
	#	graphers.append(Grapher(screen, str(x), len(graphers)))
	
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
			map(lambda x: x.update(packet), graphers)
		
		if updated:
			screen.fill((75, 75, 75))
			map(lambda x: x.draw(), graphers)
			pygame.draw.rect(screen, (255, 255, 255), (curX-5, curY-5, 10, 10), 0)
			pygame.display.flip()
		time.sleep(1.0/60)

try:
	main()
finally:
	emotiv.close()
