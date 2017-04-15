# -*- coding: utf-8 -*-
# This is an example of popping a packet from the Emotiv class's packet queue


import time

from emokit.emotiv import Emotiv

if __name__ == "__main__":
    with Emotiv(display_output=True, verbose=False,
                input_source="emotiv_encrypted_data_UD20160103001874_2017-04-05.17-21-32.384061.csv") as headset:
        while True:
            packet = headset.dequeue()
            if packet is not None:
                pass
            time.sleep(0.001)
