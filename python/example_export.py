# This is an example of popping a packet from the Emotiv class's packet queue
# and printing the gyro x and y values to the console. 
# Additionally, exports the data to a CSV file.


import platform

from emokit.emotiv import Emotiv

if platform.system() == "Windows":
    pass
import gevent

if __name__ == "__main__":
    headset = Emotiv(write=True, write_raw=True)
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
