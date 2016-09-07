# This is an example of popping a packet from the Emotiv class's packet queue
# and printing the gyro x and y values to the console. 
# Additionally, exports the data to a CSV file.


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
