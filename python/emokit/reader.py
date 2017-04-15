# -*- coding: utf-8 -*-
from __future__ import absolute_import, division

import os
import sys
import time
from datetime import datetime
from threading import Thread, Lock

from .python_queue import Queue
from .tasks import EmotivReaderTask
from .util import validate_data, device_is_emotiv, hid_enumerate, print_hid_enumerate, system_platform

if system_platform == "Windows":
    import pywinusb.hid as hid
else:
    import hidapi


class EmotivReader(object):
    """
    Read data from file or hid. Only CSV for now.
    """

    def __init__(self, file_name=None, mode="hid", hid=None, file=None, new_format=False, **kwargs):
        self.mode = mode
        self.file = file
        self.file_name = file_name
        self.hid = hid
        self.new_format = new_format
        self.platform = system_platform
        self.serial_number = None
        self.lock = Lock()
        if self.platform != "Windows":
            hidapi.hid_init()
        self.setup_platform = {
            'Windows': self.setup_windows,
            'Darwin': self.setup_not_windows,
            'Linux': self.setup_not_windows,
            'Reader': self.setup_reader,
        }
        if self.mode == "csv":
            if file_name is None:
                raise ValueError("CSV file name must be specified when initializing an EmotivReader class using mode "
                                 "'csv'.")

            if sys.version_info >= (3, 0):
                self.file = open(file_name, 'r')
            else:
                self.file = open(file_name, 'rb')
            contents = self.file.read().split('\n')
            self.reader = read_csv(contents)
            self.platform = "Reader"
        elif self.mode == 'hid':
            self.reader = None
        else:
            self.reader = None
        self.data = Queue()
        self.setup_platform[self.platform]()
        self.running = False
        self.stopped = True
        if self.reader is not None:
            self.thread = Thread(target=self.run, kwargs={'source': self.reader})
        else:
            self.thread = Thread(target=self.run, kwargs={'source': self.hid})
        self.thread.setDaemon(True)
        self._stop_signal = False

    def start(self):
        """
        Starts the reader thread.
        """
        self.running = True
        self.stopped = False
        self.thread.start()

    def stop(self):
        """
        Stops the reader thread.
        """
        self.lock.acquire()
        self._stop_signal = True
        self.lock.release()

    def run(self, source=None):
        """Do not call explicitly, called upon initialization of class"""
        if self.platform == 'Windows':
            source.set_raw_data_handler(self.data_handler)
            source.open()
        self.lock.acquire()
        while self.running:
            self.lock.release()
            if not self.platform == 'Windows':
                try:
                    if not self._stop_signal:
                        data = read_platform[self.platform](source, new_format=self.new_format)
                        self.data.put_nowait(EmotivReaderTask(data=data, timestamp=datetime.now()))
                except Exception as ex:

                    print("Reader Error: {}".format(ex.message))
                    # Catching StopIteration for some reason stops at the second record,
                    #  even though there are more results.
            else:
                time.sleep(0.00001)
            self.lock.acquire()
            if self._stop_signal:
                print("Reader stopping...")
                self.running = False
        if self.file is not None:
            self.file.close()
        if type(source) != int and type(source) != list:
            source.close()
        if self.hid is not None:
            if type(self.hid) != int:
                self.hid.close()
        if system_platform != "Windows":
            try:
                hidapi.hid_close(source)
            except Exception:
                pass
            try:
                hidapi.hid_exit()
            except Exception:
                pass
        print("Reader stopped...")
        self.stopped = True
        return

    def data_handler(self, data):
        """
        Receives packets from headset for Windows. Sends them to a Queue to be processed
        by the crypto thread.
        """
        self.lock.acquire()
        if not self._stop_signal:
            self.lock.release()
            data = validate_data(data, new_format=self.new_format)
            if data is not None:
                self.data.put_nowait(EmotivReaderTask(data=''.join(map(chr, data[1:])), timestamp=datetime.now()))
        else:
            self.lock.release()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        if self.reader:
            self.reader.close()
        self.file.close()
        if 'eeg_raw' in self.platform and self.hid is not None:
            self.hid.close()
        elif 'Windows' not in self.platform and self.hid is not None:
            hidapi.hid_close(self.hid)

    def setup_reader(self):
        """
        Setup reader stuff, not much to do here right now.
        """
        if 'encrypted' in self.file_name:
            self.platform += ' encrypted'

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
                print_hid_enumerate(system_platform, hid)
                sys.exit()
            device = devices[1]
            device.open()
            self.hid = device
            self.serial_number = device.serial_number
            print("Reader detected serial number: {serial_number}".format(serial_number=self.serial_number))
            device.set_raw_data_handler(self.data_handler)
        except Exception as ex:
            print("Emotiv WindowsSetupError ", sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2], " : ", ex)
        finally:
            if self.hid is not None:
                self.hid.close()

    def setup_not_windows(self):
        """
        Setup for headset on a non-windows platform.
        Receives packets from headset and sends them to a Queue to be processed
        by the crypto thread.
        """
        if os.path.exists('/dev/eeg/raw'):
            self.hid = open("/dev/eeg/raw")
        if self.hid is not None:
            # The decryption is handled by the Linux epoc daemon. We don't need to handle it.
            self.platform += " raw_eeg"
        else:
            path, serial_number = hid_enumerate(hidapi, self.platform)
            if len(path) == 0:
                print_hid_enumerate(system_platform, hidapi)
                raise Exception("Device not found")
            self.serial_number = serial_number
            self.hid = hidapi.hid_open_path(path)


def read_csv(source):
    """
    Iterate over data from CSV file.
    :param source: CSV reader
    :return: Next row in CSV file.
    """
    while True:
        for line in source:
            yield line


def read_reader(source, new_format=False):
    """
    Read from EmotivReader only. Return data for decryption.
    :param source: Emotiv data reader
    :return: Next row in Emotiv data file.
    """
    value = next(source)
    value = value.split(',')
    return value


def read_non_windows(source, new_format=False):
    """
    Read from Emotiv hid device.
    :param source: Emotiv hid device
    :param new_format: Read more data?
    :return: Next encrypted packet from Emotiv device.
    """
    # Doesn't seem to matter how big we make the buffer 32 returned every time, 33 for other platforms
    # Set timeout for 1 second, to help with thread shutdown.
    if new_format:
        data = validate_data(hidapi.hid_read_timeout(source, 64, 1000), new_format)
    else:
        data = validate_data(hidapi.hid_read_timeout(source, 34, 1000), new_format)
    if data is not None:
        return ''.join(map(chr, data[1:]))


def read_os_decrypted_non_windows(source):
    """
    Read from Emotiv hid device.
    :param source: Emotiv hid device
    :return: Next packet from Emotiv device.
    """
    data = source.read(32)
    if data != "":
        return data


read_platform = {
    'Darwin': read_non_windows,
    'Linux': read_non_windows,
    'Darwin raw_eeg': read_os_decrypted_non_windows,
    'Linux raw_eeg': read_os_decrypted_non_windows,
    'Reader': read_reader,
    'Reader encrypted': read_reader
}
