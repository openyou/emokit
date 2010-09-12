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
	
	def draw(self):
		if len(self.buffer) == 0:
			return
		pos = self.xoff, int(self.buffer[0] / self.range * gheight * 0.5) + self.y
		for i, x in enumerate(self.buffer):
			y = int(x / self.range * gheight * 0.5) + self.y
			pygame.draw.line(self.screen, (255, 255, 255), pos, (self.xoff + i, y))
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
	
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return
		
		updated = False
		for packet in emotiv.dequeue():
			updated = True
			if abs(packet.gyroX) > 1:
				curX -= packet.gyroX
			if abs(packet.gyroY) > 1:
				curY += packet.gyroY
			map(lambda x: x.update(packet), graphers)
		
		if updated:
			screen.fill((0, 0, 0))
			map(lambda x: x.draw(), graphers)
			pygame.draw.rect(screen, (255, 255, 255), (curX-5, curY-5, 10, 10), 0)
			pygame.display.flip()
		time.sleep(1.0/60)

try:
	main()
finally:
	emotiv.close()
