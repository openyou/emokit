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

    def __init__(self, display_output=False, serial_number=None, is_research=False, write=False,
                 write_encrypted=False, write_values=False, read_encrypted=False, input_source="emotiv",
                 sys_platform=system_platform, verbose=False):
        """
        Sets up initial values.

        :param display_output - Should non-error output be displayed to console?
        :param serial_number - Specify serial_number, needed to decrypt packets for raw data reader and special cases.
        :param is_research - Is EPOC headset research edition? Doesn't seem to work even if it is.
        :param write - Write data to csv.
        :param write_encrypted - Write encrypted data
        :param write_values - Write decrypted sensor data, True overwrites exporting data from dongle pre-processing.
        :param read_encrypted - Read encrypted data (requires serial_number)
        :param input_source - Source to read from, emotiv or a file name
                   (must be a csv, exported from emokit or following our format)
        :param sys_platform - Operating system, to avoid global statement

        Obviously, the read_encrypted needs to match the write_encrypted value used to capture the data.
        Expect performance to suffer when writing data to a csv.
        """
        self.running = True
        self.packets = Queue()
        self.battery = 0
        self.display_output = display_output
        self.verbose = verbose
        self.is_research = is_research
        self.sensors = sensors_mapping
        self.serial_number = serial_number
        self.old_model = False
        self.write = write
        self.read_encrypted = True
        self.write_encrypted = False
        self.write_values = write_values
        self.platform = sys_platform
        self.packets_received = 0
        self.packets_processed = 0
        self.input_source = input_source
        if self.write and self.input_source == "emotiv":
            self.writer = EmotivWriter('emotiv_dump_%s.csv' % str(datetime.now()), mode="csv")
            if self.write_values:
                if self.writer is None:
                    RuntimeError("EmotivWriter is None, should be set?")
                self.write_encrypted = False
                header_row = []
                for key in self.sensors.keys():
                    header_row.append(key + " Value")
                    header_row.append(key + " Quality")
                self.writer.write(header_row)
            else:
                self.write_encrypted = write_encrypted
        else:
            self.writer = None
            self.write = False

        if self.input_source != "emotiv":
            self.read_encrypted = read_encrypted
            self.reader = EmotivReader(self.input_source, mode="csv")
            first_row = self.reader.read()
            if first_row[0] != 'serial_number' and first_row[0] != 'decrypted_data':
                raise ValueError('File is not formatted correctly. Expected serial_number or decrypted data as '
                                 'first value. Reading by values not supported, yet.')
            if first_row[0] == 'serial_number':
                self.reader.serial_number = first_row[1]
                self.read_encrypted = True
            elif self.serial_number is None and self.read_encrypted:
                if first_row[1] != "decrypted_data":
                    raise ValueError("The first row does not contain the serial number and you didn't provide it, "
                                     "are you sure it's raw encrypted data?")
                else:
                    self.read_encrypted = False
        else:
            self.reader = EmotivReader()

        self.crypto = None
        if self.serial_number is None:
            self.serial_number = self.reader.serial_number
        if self.write and self.write_encrypted:
            self.writer.write(['serial_number', self.serial_number])
        elif self.write and not self.write_encrypted and not self.write_values:
            self.writer.write(['decrypted_data'])
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
        dirty = True
        while self.running:
            if not reader.data.empty():
                raw_data = reader.data.get()
                if self.write and self.write_encrypted and not self.input_source == 'file':
                    self.writer.write(raw_data)
                self.packets_received += 1
                if not self.read_encrypted and self.input_source == 'file':
                    new_packet = EmotivPacket(raw_data)
                    self.packets.put_nowait(new_packet)
                    dirty = True
                    self.packets_processed += 1
                else:
                    crypto.encrypted_queue.put_nowait(raw_data)
            if not crypto.decrypted_queue.empty():
                decrypted_packet_data = crypto.decrypted_queue.get()
                if self.write and not self.write_encrypted and not self.write_values:
                    self.writer.write(decrypted_packet_data)
                self.packets_processed += 1
                new_packet = EmotivPacket(decrypted_packet_data)
                self.packets.put_nowait(new_packet)
                if self.write and self.write_values:
                    data_to_write = []
                    for key in self.sensors.keys():
                        data_to_write.extend([new_packet.sensors[key]['value'], new_packet.sensors[key]['quality']])
                    self.writer.write(data_to_write)
                dirty = True
            if self.display_output:
                if system_platform == "Windows":
                    os.system('cls')
                else:
                    os.system('clear')
                if dirty:
                    print(
                    "Packets Received: %s Packets Processed: %s" % (self.packets_received, self.packets_processed))
                    print('\n'.join("%s Reading: %s Quality: %s" %
                                    (k[1], self.sensors[k[1]]['value'],
                                     self.sensors[k[1]]['quality']) for k in enumerate(self.sensors)))
                    print("Battery: %i" % self.battery)
                    dirty = False
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
                yield self.packets.get()
        except Exception as ex:
            print("Emotiv DequeueError ", sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2], " : ", ex)
        yield None

if __name__ == "__main__":
    a = Emotiv()
    try:
        a.setup()
    except KeyboardInterrupt:
        a.close()
