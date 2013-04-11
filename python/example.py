from emokit import emotiv
import gevent

if __name__ == "__main__":
    headset = emotiv.Emotiv()
    gevent.spawn(headset.setup)
    gevent.sleep(1)
    try:
        while True:
            packet = headset.dequeue()
            print packet.gyroX, packet.gyroY
            gevent.sleep(0)
    except KeyboardInterrupt:
        headset.close()
    finally:
        headset.close()
