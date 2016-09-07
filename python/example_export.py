# This is an example of popping a packet from the Emotiv class's packet queue
# Additionally, exports the data to a CSV file.
# You don't actually need to dequeue packets, although after some time allocation lag may occur if you don't.


import platform

from emokit.emotiv import Emotiv

if platform.system() == "Windows":
    pass


if __name__ == "__main__":
    with Emotiv(display_output=True, verbose=True, write=True) as headset:
        print("Serial Number: %s" % headset.serial_number)
        print("Exporting data... press control+c to stop.")
        while True:
            packet = headset.dequeue()
