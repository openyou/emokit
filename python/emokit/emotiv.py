# -*- coding: utf-8 -*-
import os
import platform
import sys
from datetime import datetime

import gevent
from Crypto import Random
from Crypto.Cipher import AES
from gevent.queue import Queue

from .packet import EmotivPacket
from .sensors import sensors_mapping
from .util import EmotivReader, EmotivWriter, hid_enumerate, is_old_model, print_hid_enumerate, \
    device_is_emotiv, crypto_key, validate_data

system_platform = platform.system()
if system_platform == "Windows":
    import pywinusb.hid as hid
else:
    import hidapi
    hidapi.hid_init()



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


class Emotiv(object):
    """
    Receives, decrypts and stores packets received from Emotiv Headsets and other sources.
    """

    def __init__(self, display_output=True, serial_number=None, is_research=False, write=False, io_type="csv",
                 write_raw=True, read_raw=False, other_input_source=None, sys_platform=system_platform,
                 verbose=True):
        """
        Sets up initial values.

        :param display_output - Should non-error output be displayed to console?
        :param serial_number - Specify serial_number, needed to decrypt packets for raw data reader and special cases.
        :param is_research - Is EPOC headset research edition? Doesn't seem to work even if it is.
        :param write - Write data to io_type.
        :param io_type - Type of source/destination for EmotivReader/Writer
        :param write_raw - Write unencrypted data
        :param read_raw - Read unencrypted data (requires serial_number)
        :param other_input_source - Source to read from, should be filename or other source (not implemented)
        :param sys_platform - Operating system, to avoid global statement

        Obviously, the read_raw needs to match the write_raw value used to capture the data.
        Expect performance to suffer when writing data to a csv.
        """
        self.running = True
        self.crypto_tasks = Queue()
        self.packets = Queue()
        self.packets_received = 0
        self.packets_processed = 0
        self.battery = 0
        self.display_output = display_output
        self.verbose = verbose
        self.is_research = is_research
        self.platform = sys_platform
        self.sensors = sensors_mapping
        self.serial_number = serial_number  # You will need to set this manually for OS X.
        self.old_model = False
        self.write = write
        self.read_raw = False
        self.write_raw = False
        # Start with a pool, maybe later assign different processes to additional headsets or something.
        if self.write and other_input_source is None:
            if io_type == "csv":
                self.writer = EmotivWriter('emotiv_dump_%s.csv' % str(datetime.now()), mode=io_type)
            else:
                self.writer = None
                self.write = False
            self.write_raw = write_raw
        else:
            self.write = False
        self.other_input_source = other_input_source
        if other_input_source and self.serial_number:
            self.read_raw = read_raw
            if self.serial_number == "" and self.read_raw:
                raise ValueError("You must specify a serial number when not reading directly from the headset using"
                                 " raw data!")

            self.reader = EmotivReader(other_input_source, mode=io_type)
        self.run_platform = {
            'Windows': self.run_windows,
            'Darwin': self.run_non_windows,
            'Linux': self.run_non_windows,
            'Darwin raw_eeg': self.run_os_decrypted_non_windows,
            'Linux raw_eeg': self.run_os_decrypted_non_windows,
            'Reader': self.run_reader_decrypted,
            'Reader encrypted': self.run_reader_encrypted
        }
        self.setup_platform = {
            'Windows': self.setup_windows,
            'Darwin': self.setup_not_windows,
            'Linux': self.setup_not_windows,
            'Reader': self.setup_reader
        }
        self.crypto = None
        self.console_updater = None
        self.hid = None
        self.setup()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if traceback:
            self.log(traceback)
        self.on_exit()

    def handler(self, data):
        """
        Receives packets from headset for Windows. Sends them to a Queue to be processed
        by the crypto greenlet.
        """
        data = validate_data(data)
        if data is not None:
            if self.write and self.write_raw:
                self.write_data(data)
            self.crypto_tasks.put_nowait(''.join(map(chr, data[1:])))
            self.packets_received += 1
            return True

    def log(self, message):
        if self.display_output and self.verbose:
            print("%s" % message)

    def on_exit(self, hid=None):
        if self.crypto is not None:
            gevent.kill(self.crypto, KeyboardInterrupt)
        if self.console_updater is not None:
            gevent.kill(self.console_updater, KeyboardInterrupt)
        if 'eeg_raw' in self.platform and hid is not None:
            hid.close()
        elif 'Windows' not in self.platform and hid is not None:
            hidapi.hid_close(hid)

    def run(self):
        if 'raw_eeg' not in self.platform:
            self.crypto = gevent.spawn(self.setup_crypto)
        self.console_updater = gevent.spawn(self.update_console)
        gevent.sleep(DEVICE_POLL_INTERVAL)
        while self.running:
            try:
                self.run_platform[self.platform]()
            except KeyboardInterrupt:
                self.running = False
            except Exception as ex:
                print("Emotiv RunError ", sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2], " : ", ex)
                self.running = False
            gevent.sleep(DEVICE_POLL_INTERVAL)
        self.on_exit(self.hid)

    # We don't need to do anything because of the handler events.
    def run_windows(self):
        pass

    def run_os_decrypted_non_windows(self):
        data = self.hid.read(32)
        if data != "":
            # Write to file if configured.
            if self.write and self.write_raw:
                self.write_data(data)
            # Queue it!
            self.packets_received += 1
            self.packets.put_nowait(EmotivPacket(data, self.sensors, self.old_model))
            self.packets_processed += 1

    def run_non_windows(self):
        # Doesn't seem to matter how big we make the buffer 32 returned every time, 33 for other platforms
        data = validate_data(hidapi.hid_read(self.hid, 34))
        if data is not None:
            # Write to file if configured.
            if self.write and self.write_raw:
                self.write_data(data)
            # Queue it!
            self.crypto_tasks.put_nowait(''.join(map(chr, data[1:])))
            self.packets_received += 1

    def run_reader_decrypted(self):
        """
        Read from EmotivReader only.
        :return:
        """
        data = self.reader.read()
        if len(data):
            self.log(data)
            pos = 0
            for char in data:
                if char == '':
                    data[pos] = ' '
                pos += 1
            data = ''.join(data)
            self.packets.put_nowait(EmotivPacket(data, self.sensors, self.old_model))
            self.packets_processed += 1

    def run_reader_encrypted(self):
        """
        Read from EmotivReader only. Queue data for decryption.
        """
        data = validate_data(self.reader.read())
        if data is not None:
            data = [int(item) for item in data]
            data = ''.join(map(chr, data[1:]))
            try:
                self.crypto_tasks.put_nowait(data)
                self.packets.put_nowait(EmotivPacket(data, self.sensors, self.old_model))
                self.packets_processed += 1
            except Exception as ex:
                print("Emotiv ReadError ", sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2], " : ", ex)
                # Discards packets not divisible by 16 and == 32 with the extra 0,
                # maybe they are for something though? #TODO: Look into this.

    def setup(self):
        """
        Runs setup function depending on platform.
        """
        self.log("%s detected." % self.platform)
        if self.other_input_source is not None:
            self.platform = "Reader"
        self.setup_platform[self.platform]()

    def setup_reader(self):
        if self.read_raw:
            self.platform = 'Reader encrypted'

    def setup_windows(self):
        """
        Setup for headset on the Windows platform.
        """
        devices = []
        try:
            for device in hid.find_all_hid_devices():
                if device_is_emotiv(device, self.platform):
                    devices.append(device)
            if len(devices) == 0:
                print_hid_enumerate[system_platform](hid)
                sys.exit()
            device = devices[1]
            device.open()
            self.hid = device
            self.serial_number = device.serial_number
            device.set_raw_data_handler(self.handler)
            self.run()
        except Exception as ex:
            print("Emotiv WindowsSetupError ", sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2], " : ", ex)
        finally:
            if self.hid is not None:
                self.hid.close()

    def setup_not_windows(self):
        """
        Setup for headset on a non-windows platform.
        Receives packets from headset and sends them to a Queue to be processed
        by the crypto greenlet.
        """
        if os.path.exists('/dev/eeg/raw'):
            self.hid = open("/dev/eeg/raw")
        if self.hid is not None:
            # The decryption is handled by the Linux epoc daemon. We don't need to handle it.
            self.platform += " raw_eeg"
            self.run()
        else:
            path, serial_number = hid_enumerate(hidapi, self.platform)
            if len(path) == 0:
                print_hid_enumerate[system_platform](hidapi)
                raise Exception("Device not found")
            self.serial_number = serial_number
            self.hid = hidapi.hid_open_path(path)
            self.run()

    def setup_crypto(self):
        """
        Performs decryption of packets received. Stores decrypted packets in a Queue for use.
        """
        if is_old_model(self.serial_number):
            self.old_model = True
        if self.display_output:
            print(self.old_model)

        iv = Random.new().read(AES.block_size)
        cipher = AES.new(crypto_key(self.serial_number, self.is_research), AES.MODE_ECB, iv)
        while self.running:
            while not self.crypto_tasks.empty():
                task = self.crypto_tasks.get()
                if len(task):
                    try:
                        if sys.version_info >= (3, 0):
                            task = bytes(task, encoding='latin-1')
                        data = cipher.decrypt(task[:16]) + cipher.decrypt(task[16:])
                        if self.write:
                            if not self.write_raw:
                                self.write_data(data)
                        decrypted_packet = EmotivPacket(data, self.sensors, self.old_model)
                        if decrypted_packet.battery is not None:
                            self.battery = decrypted_packet.battery
                        self.packets.put_nowait(decrypted_packet)
                        self.packets_processed += 1
                    except Exception as ex:
                        print("Emotiv CryptoError ", sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2], " : ",
                              ex)
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
        except Exception as ex:
            print("Emotiv DequeueError ", sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2], " : ", ex)

    def close(self):
        """
        Shuts down the running greenlets.
        """
        self.running = False
        self.on_exit()

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
                print("Packets Received: %s Packets Processed: %s" % (self.packets_received, self.packets_processed))
                print('\n'.join("%s Reading: %s Quality: %s" %
                                (k[1], self.sensors[k[1]]['value'],
                                 self.sensors[k[1]]['quality']) for k in enumerate(self.sensors)))
                print("Battery: %i" % self.battery)
                gevent.sleep(DEVICE_POLL_INTERVAL)

    def write_data(self, data):
        if self.writer:
            self.writer.write(data)

if __name__ == "__main__":
    a = Emotiv()
    try:
        a.setup()
    except KeyboardInterrupt:
        a.close()
