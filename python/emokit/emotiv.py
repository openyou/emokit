import os
import sys
import platform
system_platform = platform.system()
if system_platform == "Windows":
    import socket  # Needed to prevent gevent crashing on Windows. (surfly / gevent issue #459)
    import pywinusb.hid as hid
if system_platform == "Darwin" or system_platform == "Linux":
    import hidapi
    hidapi.hid_init()

import gevent
from Crypto.Cipher import AES
from Crypto import Random
from gevent.queue import Queue
from subprocess import check_output

# How long to gevent-sleep if there is no data on the EEG.
# To be precise, this is not the frequency to poll on the input device
# (which happens with a blocking read), but how often the gevent thread
# polls the real threading queue that reads the data in a separate thread
# to not block gevent with the file read().
# This is the main latency control.
# Setting it to 1ms takes about 10% CPU on a Core i5 mobile.
# You can set this lower to reduce idle CPU usage; it has no effect
# as long as data is being read from the queue, so it is rather a
# "resume" delay.
DEVICE_POLL_INTERVAL = 0.001  # in seconds

sensor_bits = {
    'F3': [10, 11, 12, 13, 14, 15, 0, 1, 2, 3, 4, 5, 6, 7],
    'FC5': [28, 29, 30, 31, 16, 17, 18, 19, 20, 21, 22, 23, 8, 9],
    'AF3': [46, 47, 32, 33, 34, 35, 36, 37, 38, 39, 24, 25, 26, 27],
    'F7': [48, 49, 50, 51, 52, 53, 54, 55, 40, 41, 42, 43, 44, 45],
    'T7': [66, 67, 68, 69, 70, 71, 56, 57, 58, 59, 60, 61, 62, 63],
    'P7': [84, 85, 86, 87, 72, 73, 74, 75, 76, 77, 78, 79, 64, 65],
    'O1': [102, 103, 88, 89, 90, 91, 92, 93, 94, 95, 80, 81, 82, 83],
    'O2': [140, 141, 142, 143, 128, 129, 130, 131, 132, 133, 134, 135, 120, 121],
    'P8': [158, 159, 144, 145, 146, 147, 148, 149, 150, 151, 136, 137, 138, 139],
    'T8': [160, 161, 162, 163, 164, 165, 166, 167, 152, 153, 154, 155, 156, 157],
    'F8': [178, 179, 180, 181, 182, 183, 168, 169, 170, 171, 172, 173, 174, 175],
    'AF4': [196, 197, 198, 199, 184, 185, 186, 187, 188, 189, 190, 191, 176, 177],
    'FC6': [214, 215, 200, 201, 202, 203, 204, 205, 206, 207, 192, 193, 194, 195],
    'F4': [216, 217, 218, 219, 220, 221, 222, 223, 208, 209, 210, 211, 212, 213]
}
quality_bits = [99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112]

# this is useful for further reverse engineering for EmotivPacket
byte_names = {
    "saltie-sdk": [  # also clamshell-v1.3-sydney
        "INTERPOLATED",
        "COUNTER",
        "BATTERY",
        "FC6",
        "F8",
        "T8",
        "PO4",
        "F4",
        "AF4",
        "FP2",
        "OZ",
        "P8",
        "FP1",
        "AF3",
        "F3",
        "P7",
        "T7",
        "F7",
        "FC5",
        "GYRO_X",
        "GYRO_Y",
        "RESERVED",
        "ETE1",
        "ETE2",
        "ETE3",
    ],
    "clamshell-v1.3-san-francisco": [  # amadi ?
        "INTERPOLATED",
        "COUNTER",
        "BATTERY",
        "F8",
        "UNUSED",
        "AF4",
        "T8",
        "UNUSED",
        "T7",
        "F7",
        "F3",
        "F4",
        "P8",
        "PO4",
        "FC6",
        "P7",
        "AF3",
        "FC5",
        "OZ",
        "GYRO_X",
        "GYRO_Y",
        "RESERVED",
        "ETE1",
        "ETE2",
        "ETE3",
    ],
    "clamshell-v1.5": [
        "INTERPOLATED",
        "COUNTER",
        "BATTERY",
        "F3",
        "FC5",
        "AF3",
        "F7",
        "T7",
        "P7",
        "O1",
        "SQ_WAVE",
        "UNUSED",
        "O2",
        "P8",
        "T8",
        "F8",
        "AF4",
        "FC6",
        "F4",
        "GYRO_X",
        "GYRO_Y",
        "RESERVED",
        "ETE1",
        "ETE2",
        "ETE3",
    ],
    "clamshell-v3.0": [
        "INTERPOLATED",
        "COUNTER",
        "BATTERY",
        "F3",
        "FC5",
        "AF3",
        "F7",
        "T7",
        "P7",
        "O1",
        "SQ_WAVE",
        "UNUSED",
        "O2",
        "P8",
        "T8",
        "F8",
        "AF4",
        "FC6",
        "F4",
        "GYRO_X",
        "GYRO_Y",
        "RESERVED",
        "ETE1",
        "ETE2",
        "ETE3",
    ],
}

battery_values = {
    "255": 100,
    "254": 100,
    "253": 100,
    "252": 100,
    "251": 100,
    "250": 100,
    "249": 100,
    "248": 100,
    "247": 99,
    "246": 97,
    "245": 93,
    "244": 89,
    "243": 85,
    "242": 82,
    "241": 77,
    "240": 72,
    "239": 66,
    "238": 62,
    "237": 55,
    "236": 46,
    "235": 32,
    "234": 20,
    "233": 12,
    "232": 6,
    "231": 4,
    "230": 3,
    "229": 2,
    "228": 2,
    "227": 2,
    "226": 1,
    "225": 0,
    "224": 0,
}

g_battery = 0
tasks = Queue()


def get_level(data, bits):
    """
    Returns sensor level value from data using sensor bit mask in micro volts (uV).
    """
    level = 0
    for i in range(13, -1, -1):
        level <<= 1
        b, o = (bits[i] / 8) + 1, bits[i] % 8
        level |= (ord(data[b]) >> o) & 1
    return level


def is_old_model(serial_number):
        if "GM" in serial_number[-2:]:
                return False
        return True


class EmotivPacket(object):
    """
    Basic semantics for input bytes.
    """

    def __init__(self, data, sensors, model):
        """
        Initializes packet data. Sets the global battery value.
        Updates each sensor with current sensor value from the packet data.
        """
        global g_battery
        self.raw_data = data
        self.counter = ord(data[0])
        self.battery = g_battery
        if self.counter > 127:
            self.battery = self.counter
            g_battery = battery_values[str(self.battery)]
            self.counter = 128
        self.sync = self.counter == 0xe9
        self.gyro_x = ord(data[29]) - 106
        self.gyro_y = ord(data[30]) - 105
        sensors['X']['value'] = self.gyro_x
        sensors['Y']['value'] = self.gyro_y
        for name, bits in sensor_bits.items():
            #Get Level for sensors subtract 8192 to get signed value
            value = get_level(self.raw_data, bits) - 8192
            setattr(self, name, (value,))
            sensors[name]['value'] = value
        self.old_model = model
        self.handle_quality(sensors)
        self.sensors = sensors

    def handle_quality(self, sensors):
        """
        Sets the quality value for the sensor from the quality bits in the packet data.
        Optionally will return the value.
        """
        if self.old_model:
            current_contact_quality = get_level(self.raw_data, quality_bits) / 540
        else:
            current_contact_quality = get_level(self.raw_data, quality_bits) / 1024
        sensor = ord(self.raw_data[0])
        if sensor == 0 or sensor == 64:
            sensors['F3']['quality'] = current_contact_quality
        elif sensor == 1 or sensor == 65:
            sensors['FC5']['quality'] = current_contact_quality
        elif sensor == 2 or sensor == 66:
            sensors['AF3']['quality'] = current_contact_quality
        elif sensor == 3 or sensor == 67:
            sensors['F7']['quality'] = current_contact_quality
        elif sensor == 4 or sensor == 68:
            sensors['T7']['quality'] = current_contact_quality
        elif sensor == 5 or sensor == 69:
            sensors['P7']['quality'] = current_contact_quality
        elif sensor == 6 or sensor == 70:
            sensors['O1']['quality'] = current_contact_quality
        elif sensor == 7 or sensor == 71:
            sensors['O2']['quality'] = current_contact_quality
        elif sensor == 8 or sensor == 72:
            sensors['P8']['quality'] = current_contact_quality
        elif sensor == 9 or sensor == 73:
            sensors['T8']['quality'] = current_contact_quality
        elif sensor == 10 or sensor == 74:
            sensors['F8']['quality'] = current_contact_quality
        elif sensor == 11 or sensor == 75:
            sensors['AF4']['quality'] = current_contact_quality
        elif sensor == 12 or sensor == 76 or sensor == 80:
            sensors['FC6']['quality'] = current_contact_quality
        elif sensor == 13 or sensor == 77:
            sensors['F4']['quality'] = current_contact_quality
        elif sensor == 14 or sensor == 78:
            sensors['F8']['quality'] = current_contact_quality
        elif sensor == 15 or sensor == 79:
            sensors['AF4']['quality'] = current_contact_quality
        else:
            sensors['Unknown']['quality'] = current_contact_quality
            sensors['Unknown']['value'] = sensor
        return current_contact_quality

    def __repr__(self):
        """
        Returns custom string representation of the Emotiv Packet.
        """
        return 'EmotivPacket(counter=%i, battery=%i, gyro_x=%i, gyro_y=%i)' % (
            self.counter,
            self.battery,
            self.gyro_x,
            self.gyro_y)


class Emotiv(object):
    """
    Receives, decrypts and stores packets received from Emotiv Headsets.
    """
    def __init__(self, display_output=True, serial_number="", is_research=False):
        """
        Sets up initial values.
        """
        self.running = True
        self.packets = Queue()
        self.packets_received = 0
        self.packets_processed = 0
        self.battery = 0
        self.display_output = display_output
        self.is_research = is_research
        self.sensors = {
            'F3': {'value': 0, 'quality': 0},
            'FC6': {'value': 0, 'quality': 0},
            'P7': {'value': 0, 'quality': 0},
            'T8': {'value': 0, 'quality': 0},
            'F7': {'value': 0, 'quality': 0},
            'F8': {'value': 0, 'quality': 0},
            'T7': {'value': 0, 'quality': 0},
            'P8': {'value': 0, 'quality': 0},
            'AF4': {'value': 0, 'quality': 0},
            'F4': {'value': 0, 'quality': 0},
            'AF3': {'value': 0, 'quality': 0},
            'O2': {'value': 0, 'quality': 0},
            'O1': {'value': 0, 'quality': 0},
            'FC5': {'value': 0, 'quality': 0},
            'X': {'value': 0, 'quality': 0},
            'Y': {'value': 0, 'quality': 0},
            'Unknown': {'value': 0, 'quality': 0}
        }
        self.serial_number = serial_number  # You will need to set this manually for OS X.
        self.old_model = False

    def setup(self):
        """
        Runs setup function depending on platform.
        """
        print system_platform + " detected."
        if system_platform == "Windows":
            self.setup_windows()
        elif system_platform == "Darwin" or system_platform == "Linux":
            self.setup_darwin()

    def setup_windows(self):
        """
        Setup for headset on the Windows platform. 
        """
        devices = []
        try:
            for device in hid.find_all_hid_devices():
                if device.vendor_id != 0x21A1 and device.vendor_id != 0xED02:
                    continue
                if device.product_name == 'Brain Waves':
                    devices.append(device)
                    device.open()
                    self.serial_number = device.serial_number
                    device.set_raw_data_handler(self.handler)
                elif device.product_name == 'EPOC BCI':
                    devices.append(device)
                    device.open()
                    self.serial_number = device.serial_number
                    device.set_raw_data_handler(self.handler)
                elif device.product_name == '00000000000':
                    devices.append(device)
                    device.open()
                    self.serial_number = device.serial_number
                    device.set_raw_data_handler(self.handler)
                elif device.product_name == 'Emotiv RAW DATA':
                    devices.append(device)
                    device.open()
                    self.serial_number = device.serial_number
                    device.set_raw_data_handler(self.handler)
            crypto = gevent.spawn(self.setup_crypto, self.serial_number)
            console_updater = gevent.spawn(self.update_console)
            while self.running:
                try:
                    gevent.sleep(0)
                except KeyboardInterrupt:
                    self.running = False
        finally:
            for device in devices:
                device.close()
            gevent.kill(crypto, KeyboardInterrupt)
            gevent.kill(console_updater, KeyboardInterrupt)

    def handler(self, data):
        """
        Receives packets from headset for Windows. Sends them to a Queue to be processed
        by the crypto greenlet.
        """
        assert data[0] == 0
        tasks.put_nowait(''.join(map(chr, data[1:])))
        self.packets_received += 1
        return True

    def setup_posix(self):
        """
        Setup for headset on the Linux platform.
        Receives packets from headset and sends them to a Queue to be processed
        by the crypto greenlet.

	TODO: 
		Move functionality to setup_darwin
		Rename setup_darwin to something more suitable.
		
        """
        _os_decryption = False
        if os.path.exists('/dev/eeg/raw'):
            # The decryption is handled by the Linux epoc daemon. We don't need to handle it.
            _os_decryption = True
            hidraw = open("/dev/eeg/raw")
        while self.running:
            try:
                data = hidraw.read(32)
                if data != "":
                    if _os_decryption:
                        self.packets.put_nowait(EmotivPacket(data))
                    gevent.sleep(0)
                else:
                    # No new data from the device; yield
                    # We cannot sleep(0) here because that would go 100% CPU if both queues are empty
                    gevent.sleep(DEVICE_POLL_INTERVAL)
            except KeyboardInterrupt:
                self.running = False
        hidraw.close()
        if not _os_decryption:
            gevent.kill(crypto, KeyboardInterrupt)
        gevent.kill(console_updater, KeyboardInterrupt)

    def setup_darwin(self):
        """
        Setup for headset on the OS X platform.
        Receives packets from headset and sends them to a Queue to be processed
        by the crypto greenlet.
        """
        _os_decryption = False
        path, serial_number = self.hid_enumerate()
        if len(path) == 0:
            print "Could not find device."
            self.print_hid_enumerate()
        self.serial_number = serial_number
        device = hidapi.hid_open_path(path)
        crypto = gevent.spawn(self.setup_crypto, self.serial_number)
        gevent.sleep(DEVICE_POLL_INTERVAL)
        console_updater = gevent.spawn(self.update_console)
        while self.running:
            try:
                # Doesn't seem to matter how big we make the buffer 32 returned every time, 33 for other platforms
                data = hidapi.hid_read(device, 34)
                if len(data) == 32:
                    # Most of the time the 0 is truncated? That's ok we'll add it...
                    data.insert(0, 0)
                if data != "":
                    if _os_decryption:
                        self.packets.put_nowait(EmotivPacket(data))
                    else:
                        # Queue it!
                        tasks.put_nowait(''.join(map(chr, data[1:])))
                        self.packets_received += 1
                    gevent.sleep(DEVICE_POLL_INTERVAL)
                else:
                    # No new data from the device; yield
                    # We cannot sleep(0) here because that would go 100% CPU if both queues are empty.
                    gevent.sleep(DEVICE_POLL_INTERVAL)
            except KeyboardInterrupt:
                self.running = False
            except Exception, ex:
                print "Setup (line=478): " + ex.message
                self.running = False
            gevent.sleep(DEVICE_POLL_INTERVAL)
        hidapi.hid_close(device)
        gevent.kill(crypto, KeyboardInterrupt)
        gevent.kill(console_updater, KeyboardInterrupt)

    def hid_enumerate(self):
        """
        Loops over all devices in the hidapi and attempts to locate the emotiv headset.

        Since hidapi ultimately uses the path there is no reason to get the vendor id or product id.

        Although, they may be useful in locating the device.

        :returns
            path - the path to the device
            serial_number - the serial number of the device
        """
        path = ""
        serial_number = ""
        is_emotiv = False
        devices = hidapi.hid_enumerate()
        for device in devices:
            try:
                if "Emotiv" in device.manufacturer_string:
                    is_emotiv = True
                if "Emotiv" in device.product_string:
                    is_emotiv = True
                if "EPOC" in device.product_string:
                    is_emotiv = True
                if "Brain Waves" in device.product_string:
                    is_emotiv = True
                if is_emotiv:
                    serial_number = device.serial_number
                    path = device.path
                    is_emotiv = False
            except:
                pass
        return path, serial_number

    def print_hid_enumerate(self):
        """
        Loops over all devices in the hidapi and attempts prints information.

        This is a fall back method that give the user information to give the developers when opening an issue.
        """
        devices = hidapi.hid_enumerate()
        print "-------------------------"
        for device in devices:
            print device.manufacturer_string
            print device.product_string
            print device.path
            print device.vendor_id
            print device.product_id
            print device.serial_number
            print "-------------------------"
        print "Please include this information if you open a new issue."
        sys.exit()

    def setup_crypto(self, sn):
        """
        Performs decryption of packets received. Stores decrypted packets in a Queue for use.
        """
        if is_old_model(sn):
            self.old_model = True
        print self.old_model
        k = ['\0'] * 16
        k[0] = sn[-1]
        k[1] = '\0'
        k[2] = sn[-2]
        if self.is_research:
            k[3] = 'H'
            k[4] = sn[-1]
            k[5] = '\0'
            k[6] = sn[-2]
            k[7] = 'T'
            k[8] = sn[-3]
            k[9] = '\x10'
            k[10] = sn[-4]
            k[11] = 'B'
        else:
            k[3] = 'T'
            k[4] = sn[-3]
            k[5] = '\x10'
            k[6] = sn[-4]
            k[7] = 'B'
            k[8] = sn[-1]
            k[9] = '\0'
            k[10] = sn[-2]
            k[11] = 'H'
        k[12] = sn[-3]
        k[13] = '\0'
        k[14] = sn[-4]
        k[15] = 'P'
        key = ''.join(k)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_ECB, iv)
        for i in k:
            print "0x%.02x " % (ord(i))
        while self.running:
            while not tasks.empty():
                task = tasks.get()
                if len(task):
                    try:
                        data = cipher.decrypt(task[:16]) + cipher.decrypt(task[16:])
                        self.packets.put_nowait(EmotivPacket(data, self.sensors, self.old_model))
                        self.packets_processed += 1
                    except Exception, ex:
                        print "Crypto (line=587): " + ex.message
                gevent.sleep(DEVICE_POLL_INTERVAL)
            gevent.sleep(DEVICE_POLL_INTERVAL)

    def dequeue(self):
        """
        Returns an EmotivPacket popped off the Queue.
        """
        try:
            if not self.packets.empty():
                return self.packets.get()
            return None
        except Exception, e:
            print "Dequeue (line=650): " + e.message

    def close(self):
        """
        Shuts down the running greenlets.
        """
        self.running = False

    def update_console(self):
        """
        Greenlet that outputs sensor, gyro and battery values once per second to the console.
        """
        if self.display_output:
            while self.running:
                if system_platform == "Windows":
                    os.system('cls')
                else:
                    os.system('clear')
                print "Packets Received: %s Packets Processed: %s" % (self.packets_received, self.packets_processed)
                print('\n'.join("%s Reading: %s Quality: %s" %
                                (k[1], self.sensors[k[1]]['value'],
                                 self.sensors[k[1]]['quality']) for k in enumerate(self.sensors)))
                print "Battery: %i" % g_battery
                gevent.sleep(DEVICE_POLL_INTERVAL)

if __name__ == "__main__":
    a = Emotiv()
    try:
        a.setup()
    except KeyboardInterrupt:
        a.close()
