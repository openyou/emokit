# This is an example of popping a packet from the Emotiv class's packet queue
# and printing the gyro x and y values to the console. 

from emokit.emotiv import Emotiv
import gevent

if __name__ == "__main__":
    headset = Emotiv()
    gevent.spawn(headset.setup)
    gevent.sleep(0)
    try:
        while True:
            packet = headset.dequeue()
            print packet.gyro_x, packet.gyro_y
            gevent.sleep(0)
    except KeyboardInterrupt:
        headset.close()
    finally:
        headset.close()
