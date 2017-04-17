#!/usr/bin/python
# Renders a window with graph values for each sensor and a box for gyro values.
try:
    import psyco
    psyco.full()
except ImportError:
    print('No psyco. Expect poor performance. Not really...')
import platform
import sys
import time

import pygame
from pygame import FULLSCREEN

from emokit.emotiv import Emotiv
from emokit.packet import EmotivExtraPacket
from emokit.util import get_quality_scale_level_color

if platform.system() == "Windows":
    pass


class Grapher(object):
    """
    Worker that draws a line for the sensor value.
    """

    def __init__(self, screen, name, i, old_model=False):
        """
        Initializes graph worker
        """
        self.screen = screen
        self.name = name
        self.range = float(1 << 13)
        self.x_offset = 40
        self.y = i * gheight
        self.buffer = []
        font = pygame.font.Font(None, 24)
        self.text = font.render(self.name, 1, (255, 0, 0))
        self.text_pos = self.text.get_rect()
        self.text_pos.centery = self.y + gheight
        self.first_packet = True
        self.y_offset = 0
        self.old_model = old_model

    def update(self, packet):
        """
        Appends value and quality values to drawing buffer.
        """
        if len(self.buffer) == 800 - self.x_offset:
            self.buffer = self.buffer[1:]
        self.buffer.append([packet.sensors[self.name]['value'], packet.sensors[self.name]['quality']])

    def calc_y(self, val):
        """
        Calculates line height from value.
        """
        return val - self.y_offset + gheight

    def draw(self):
        """
        Draws a line from values stored in buffer.
        """
        if len(self.buffer) == 0:
            return

        if self.first_packet:
            self.y_offset = self.buffer[0][0]
            # print(self.y_offset)
            self.first_packet = False
        pos = self.x_offset, self.calc_y(self.buffer[0][0]) + self.y
        for i, (value, quality) in enumerate(self.buffer):
            y = self.calc_y(value) + self.y
            color = get_quality_scale_level_color(quality, self.old_model)
            pygame.draw.line(self.screen, color, pos, (self.x_offset + i, y))
            pos = (self.x_offset + i, y)
        self.screen.blit(self.text, self.text_pos)


def main():
    """
    Creates pygame window and graph drawing workers for each sensor.
    """
    global gheight
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    graphers = []
    recordings = []
    recording = False
    record_packets = []
    updated = False
    cursor_x, cursor_y = 400, 300
    fullscreen = False
    with Emotiv(display_output=False) as emotiv:
        for name in 'AF3 F7 F3 FC5 T7 P7 O1 O2 P8 T8 FC6 F4 F8 AF4'.split(' '):
            graphers.append(Grapher(screen, name, len(graphers), emotiv.old_model))
        while emotiv.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    emotiv.close()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        emotiv.close()
                        return
                    elif event.key == pygame.K_f:
                        if fullscreen:
                            screen = pygame.display.set_mode((800, 600))
                            fullscreen = False
                        else:
                            screen = pygame.display.set_mode((800, 600), FULLSCREEN, 16)
                            fullscreen = True
                    elif event.key == pygame.K_r:
                        if not recording:
                            record_packets = []
                            recording = True
                        else:
                            recording = False
                            recordings.append(list(record_packets))
                            record_packets = None
            packets_in_queue = 0
            try:
                while packets_in_queue < 8:
                    packet = emotiv.dequeue()

                    if packet is not None:
                        if type(packet) != EmotivExtraPacket:
                            if abs(packet.sensors['X']['value']) > 1:
                                cursor_x = max(0, min(cursor_x, 800))
                                cursor_x -= packet.sensors['X']['value']
                            if abs(packet.sensors['Y']['value']) > 1:
                                cursor_y += packet.sensors['Y']['value']
                                cursor_y = max(0, min(cursor_y, 600))
                            map(lambda x: x.update(packet), graphers)
                            if recording:
                                record_packets.append(packet)
                            updated = True
                            packets_in_queue += 1
                    time.sleep(0.001)
            except Exception as ex:
                print("EmotivRender DequeuePlotError ", sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2],
                      " : ", ex)

            if updated:
                screen.fill((75, 75, 75))
                map(lambda x: x.draw(), graphers)
                pygame.draw.rect(screen, (255, 255, 255), (cursor_x - 5, cursor_y - 5, 10, 10), 0)
                pygame.display.flip()
                updated = False


if __name__ == "__main__":
    try:
        gheight = 580 // 14
        main()
    except Exception as ex:
        print("EmotivRender ", sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2], " : ", ex)
