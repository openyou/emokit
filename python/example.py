# -*- coding: utf-8 -*-
# This is an example of popping a packet from the Emotiv class's packet queue
# and printing the gyro x and y values to the console. 


import time

from emokit.emotiv import Emotiv

if __name__ == "__main__":
    with Emotiv(display_output=True, verbose=True) as headset:
        while True:
            packet = headset.dequeue()
            if packet is not None:
                # print("Gyro - X:{x_position} Y:{y_position}".format(x_position=packet.sensors['X']['value'],
                #                                                    y_position=packet.sensors['Y']['value']))
                pass
            time.sleep(0.001)
