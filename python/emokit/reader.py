# -*- coding: utf-8 -*-
from __future__ import absolute_import, division

import csv
import os
import platform
import sys
import time
from threading import Thread

from queue import Queue

from .util import validate_data, device_is_emotiv, hid_enumerate, print_hid_enumerate

system_platform = platform.system()
if system_platform == "Windows":
    import pywinusb.hid as hid
else:
    import hidapi

    hidapi.hid_init()


class EmotivReader(object):
    """
    Read data from file or hid. Only CSV for now.
    """

    def __init__(self, file_name=None, mode="hid", hid=None, file=None, **kwargs):
        self.mode = mode
        self.file = file
        self.hid = hid
        self.platform = system_platform
        self.serial_number = None
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
            self.file = open(file_name, 'rb')
            self.reader = csv.reader(self.file, quoting=csv.QUOTE_ALL)
            self.platform = "Reader"
        elif self.mode == 'hid':
            self.reader = None
        else:
            self.reader = None
        self.data = Queue()
        self.setup_platform[self.platform]()
        self.running = True
        if self.reader is not None:
            self.thread = Thread(target=self.run, kwargs={'source': self.reader})
        else:
            self.thread = Thread(target=self.run, kwargs={'source': self.hid})
        self.thread.start()

    def run(self, source=None):
        """Do not call explicitly, called upon initialization of class"""
        if self.platform == 'Windows':
            source.set_raw_data_handler(self.data_handler)
        while self.running:
            if not self.platform == 'Windows':
                try:
                    self.data.put_nowait(read_platform[self.platform](source))
                except StopIteration:
                    self.running = False
            else:
                time.sleep(0.0005)
        if self.file is not None:
            self.file.close()
        else:
            source.close()

    def data_handler(self, data):
        """
        Receives packets from headset for Windows. Sends them to a Queue to be processed
        by the crypto thread.
        """
        data = validate_data(data)
        if data is not None:
            self.data.put_nowait(data)
            return True

    def __exit__(self, exc_type, exc_value, traceback):
        if self.reader:
            self.reader.close()
        self.file.close()
        if 'eeg_raw' in self.platform and self.hid is not None:
            self.hid.close()
        elif 'Windows' not in self.platform and self.hid is not None:
            hidapi.hid_close(self.hid)

    def setup_reader(self):
        print(self.reader)
        first_row = self.reader.next()
        first_row = ''.join(first_row).split(', ')
        print(first_row)
        if first_row[0] != 'serial_number' and first_row[0] != 'decrypted_data':
            raise ValueError('File is not formatted correctly. Expected serial_number or decrypted data as '
                             'first value. Reading by values not supported, yet.')
        if first_row[0] == 'serial_number':
            self.serial_number = first_row[1]
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
    return source.next()


def read_reader_encrypted(source):
    """
    Read from EmotivReader only. Return data for decryption.
    """
    data = validate_data(read_csv(source))
    if data is not None:
        data = [int(item) for item in data]
        data = ''.join(map(chr, data[1:]))
        return data


def read_reader_decrypted(source):
    """
    Read from EmotivReader only.
    :return:
    """
    data = read_csv(source)
    if len(data):
        pos = 0
        for char in data:
            if char == '':
                data[pos] = ' '
            pos += 1
        data = ''.join(data)
        return data


def read_non_windows(source):
    # Doesn't seem to matter how big we make the buffer 32 returned every time, 33 for other platforms
    data = validate_data(hidapi.hid_read(source, 34))
    if data is not None:
        return ''.join(map(chr, data[1:]))


def read_os_decrypted_non_windows(source):
    data = source.read(32)
    if data != "":
        return data


read_platform = {
    'Darwin': read_non_windows,
    'Linux': read_non_windows,
    'Darwin raw_eeg': read_os_decrypted_non_windows,
    'Linux raw_eeg': read_os_decrypted_non_windows,
    'Reader': read_reader_decrypted,
    'Reader encrypted': read_reader_encrypted
}
