#!/usr/bin/python

try:
    import psyco

    psyco.full()
except:
    print 'No psyco.  Expect poor performance. Not really...'

import pygame
from pygame import FULLSCREEN
import gevent
import sys, logging
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
        self.textpos.centery = self.y + gheight

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
        strength = 3
        for i, (x) in enumerate(self.buffer):
            y = self.calcY(x[0]) + self.y
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
            pos = (self.xoff + i, y)
        self.screen.blit(self.text, self.textpos)




def main(debug=False):
    global gheight
    pygame.init()
    screen = pygame.display.set_mode((1600, 900))
    graphers = []
    updated = False
    curX, curY = 400, 300

    for name in 'AF3 F7 F3 FC5 T7 P7 O1 O2 P8 T8 FC6 F4 F8 AF4'.split(' '):
        graphers.append(Grapher(screen, name, len(graphers)))
    fullscreen = False
    emotiv = Emotiv(displayOutput=False)
    gevent.spawn(emotiv.setup)
    gevent.sleep(1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                emotiv.close()
                return
            elif event.type == pygame.K_f:
                if fullscreen:
                    screen = pygame.display.set_mode((1600, 900))
                    fullscreen = False
                else:
                    screen = pygame.display.set_mode((1600,900), FULLSCREEN, 16)
                    fullscreen = True




        packetsInQueue = 0
        try:
            while packetsInQueue < 8:
                packet = emotiv.dequeue()
                if abs(packet.gyroX) > 1:
                    curX = max(0, min(curX, 1600))
                    curX -= packet.gyroX
                if abs(packet.gyroY) > 1:
                    curY += packet.gyroY
                    curY = max(0, min(curY, 900))
                map(lambda x: x.update(packet), graphers)
                updated = True
                packetsInQueue += 1
        except Exception, e:
            print e

        if updated:
            screen.fill((75, 75, 75))
            map(lambda x: x.draw(), graphers)
            pygame.draw.rect(screen, (255, 255, 255), (curX - 5, curY - 5, 10, 10), 0)
            pygame.display.flip()
            updated = False
        gevent.sleep(0)

try:
    logger = logging.getLogger('emotiv')
    logger.setLevel(logging.INFO)
    log_handler = logging.StreamHandler()
    logger.addHandler(log_handler)
    gheight = 600 / 14
    hgheight = gheight >> 1
    main(*sys.argv[1:])

except Exception, e:
    print e

