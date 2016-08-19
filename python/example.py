# This is an example of popping a packet from the Emotiv class's packet queue
# and printing the gyro x and y values to the console. 

import platform

from emokit.emotiv import Emotiv

if platform.system() == "Windows":
    pass
import gevent

if __name__ == "__main__":
    with Emotiv(display_output=True, verbose=True) as headset:
        gevent.spawn(headset.setup)
        gevent.sleep(0.0001)
        while True:
            packet = headset.dequeue()
            print("%s %s" % (packet.gyro_x, packet.gyro_y))
            gevent.sleep(0.0001)
