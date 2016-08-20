# -*- coding: utf-8 -*-
from __future__ import absolute_import, division

import os
import platform
import sys
from datetime import datetime
from threading import Thread

from emokit.decrypter import EmotivCrypto
from emokit.reader import EmotivReader
from queue import Queue

from .packet import EmotivPacket
from .sensors import sensors_mapping
from .util import EmotivWriter

system_platform = platform.system()


class Emotiv(object):
    """
    Receives, decrypts and stores packets received from Emotiv Headsets and other sources.
    """

    def __init__(self, display_output=True, serial_number=None, is_research=False, write=True, io_type="csv",
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
        self.packets = Queue()
        self.battery = 0
        self.display_output = display_output
        self.verbose = verbose
        self.is_research = is_research
        self.sensors = sensors_mapping
        self.serial_number = serial_number  # You will need to set this manually for OS X.
        self.old_model = False
        self.write = write
        self.read_raw = False
        self.write_raw = False
        self.platform = sys_platform
        self.other_input_source = None
        self.packets_received = 0
        self.packets_processed = 0
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
        self.crypto = None
        self.reader = EmotivReader()
        if self.serial_number is None:
            self.serial_number = self.reader.serial_number
        self.crypto = EmotivCrypto(self.serial_number, self.is_research)
        self.thread = Thread(target=self.run, kwargs={'reader': self.reader, 'crypto': self.crypto})
        self.thread.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if traceback:
            self.log(traceback)

    def log(self, message):
        if self.display_output and self.verbose:
            print("%s" % message)

    def run(self, reader=None, crypto=None):
        """Do not call explicitly, called upon initialization of class"""
        while self.running:
            if not reader.data.empty():
                raw_data = reader.data.get()
                if self.write and self.write_raw:
                    self.writer.write(raw_data)
                self.packets_received += 1
                crypto.encrypted_queue.put_nowait(raw_data)
            if not crypto.decrypted_queue.empty():
                decrypted_packet_data = crypto.decrypted_queue.get()
                if self.write and not self.write_raw:
                    self.writer.write(decrypted_packet_data)
                self.packets_processed += 1
                self.packets.put_nowait(EmotivPacket(decrypted_packet_data))
            if self.display_output:
                if system_platform == "Windows":
                    os.system('cls')
                else:
                    os.system('clear')
                print("Packets Received: %s Packets Processed: %s" % (self.packets_received, self.packets_processed))
                print('\n'.join("%s Reading: %s Quality: %s" %
                                (k[1], self.sensors[k[1]]['value'],
                                 self.sensors[k[1]]['quality']) for k in enumerate(self.sensors)))
                print("Battery: %i" % self.battery)
                # print("Packets: %s Reader: %s Encrypted: %s Decrypted: %s" % (str(self.packets.qsize()),
                #                                                               str(self.reader.data.qsize()),
                #                                                               str(self.crypto.encrypted_queue.qsize()),
                #                                                               str(self.crypto.decrypted_queue.qsize())))

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

if __name__ == "__main__":
    a = Emotiv()
    try:
        a.setup()
    except KeyboardInterrupt:
        a.close()
