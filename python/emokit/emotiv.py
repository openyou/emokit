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
                 write_encrypted=False, write_values=True, input_source="emotiv",
                 sys_platform=system_platform, verbose=False):
        """
        Sets up initial values.

        :param display_output - Should non-error output be displayed to console?
        :param serial_number - Specify serial_number, needed to decrypt packets for raw data reader and special cases.
        :param is_research - Is EPOC headset research edition? Doesn't seem to work even if it is.
        :param write - Write data to csv.
        :param write_encrypted - Write encrypted data
        :param write_values - Write decrypted sensor data, True overwrites exporting data from dongle pre-processing.
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
        self.read_values = False
        self.write_encrypted = False
        self.write_values = write_values
        self.platform = sys_platform
        self.packets_received = 0
        self.packets_processed = 0
        self.input_source = input_source
        if self.input_source != "emotiv":
            if self.input_source.startswith('emotiv_encrypted'):
                self.serial_number = self.input_source.split('_')[3]
            else:
                self.read_encrypted = False
                if self.input_source.startswith('emotiv_values'):
                    self.read_values = True
            self.reader = EmotivReader(file_name=self.input_source, mode="csv")
            self.reader.serial_number = self.serial_number
        else:
            self.reader = EmotivReader()
            if self.reader.serial_number is not None:
                self.serial_number = self.reader.serial_number
            if self.write:
                if not self.write_values:
                    self.write_encrypted = write_encrypted
                    if self.write_encrypted:
                        self.writer = EmotivWriter('emotiv_encrypted_data_%s_%s.csv' % (self.reader.serial_number,
                                                                                        str(datetime.now())),
                                                   mode="csv")
                    else:
                        self.writer = EmotivWriter('emotiv_data_%s.csv' % str(datetime.now()), mode="csv")
            else:
                self.writer = None

        if self.write and self.write_values:
            self.writer = EmotivWriter('emotiv_values_%s.csv' % str(datetime.now()), mode="csv")
            self.write_encrypted = False
            header_row = []
            for key in self.sensors.keys():
                header_row.append(key + " Value")
                header_row.append(key + " Quality")
            self.writer.write(header_row)
        self.crypto = None
        if self.read_encrypted:
            self.crypto = EmotivCrypto(self.serial_number, self.is_research)
        self.thread = Thread(target=self.run, kwargs={'reader': self.reader, 'crypto': self.crypto,
                                                      'running': self.running})
        self.thread.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if traceback:
            self.log(traceback)
        self.quit()

    def log(self, message):
        if self.display_output and self.verbose:
            print("%s" % message)

    def run(self, reader=None, crypto=None, running=False):
        """Do not call explicitly, called upon initialization of class"""
        dirty = True
        while running:
            if not reader.data.empty():
                try:
                    raw_data = reader.data.get()
                except KeyboardInterrupt:
                    self.quit()
                if self.write and self.write_encrypted and self.input_source == 'emotiv':
                    # Due to some encoding problem to save encrypted data we must first convert it to binary.

                    if sys.version_info >= (3, 0):
                        self.writer.write(map(bin, bytearray(raw_data, encoding='latin-1')))
                    else:
                        self.writer.write(map(bin, bytearray(raw_data)))
                self.packets_received += 1
                if not self.read_encrypted:
                    if not self.read_values:
                        new_packet = EmotivPacket(raw_data)
                        if new_packet.battery is not None:
                            self.battery = new_packet.battery
                        self.packets.put_nowait(new_packet)
                        dirty = True
                        self.packets_processed += 1
                    else:
                        # TODO: Implement read from values.
                        pass
                else:
                    if self.input_source != 'emotiv' and self.read_encrypted:
                        if len(raw_data) != 32:
                            self.reader.running = False
                            self.crypto.running = False
                            self.running = False
                            raise ValueError("Reached end of data or corrupted data.")
                        # Decode binary data stored in file.

                        if sys.version_info >= (3, 0):
                            raw_data = [int(bytes(item, encoding='latin-1').decode(), 2) for item in raw_data]
                        else:
                            raw_data = [int(item.decode(), 2) for item in raw_data]
                        raw_data = ''.join(map(chr, raw_data[:]))
                    crypto.encrypted_queue.put_nowait(raw_data)
            if self.crypto is not None:
                if not crypto.decrypted_queue.empty():
                    decrypted_packet_data = crypto.decrypted_queue.get()
                    if self.write and not self.write_encrypted and not self.write_values and self.input_source == 'emotiv':
                        self.writer.write(decrypted_packet_data)
                    self.packets_processed += 1
                    new_packet = EmotivPacket(decrypted_packet_data)
                    if new_packet.battery is not None:
                        self.battery = new_packet.battery
                    self.packets.put_nowait(new_packet)
                    if self.write and self.write_values:
                        data_to_write = []
                        for key in self.sensors.keys():
                            data_to_write.extend([new_packet.sensors[key]['value'], new_packet.sensors[key]['quality']])
                        self.writer.write(data_to_write)
                    dirty = True
            if self.display_output:
                if dirty:
                    if system_platform == "Windows":
                        os.system('cls')
                    else:
                        os.system('clear')
                    print("Packets Received: %s Packets Processed: %s" % (self.packets_received,
                                                                          self.packets_processed))
                    print('\n'.join("%s Reading: %s Quality: %s" %
                                    (k[1], self.sensors[k[1]]['value'],
                                     self.sensors[k[1]]['quality']) for k in enumerate(self.sensors)))
                    print("Battery: %i" % self.battery)
                    dirty = False
            if not self.reader.running:
                if self.crypto is not None:
                    self.crypto.running = False
                self.running = False

    def dequeue(self):
        """
        Returns an EmotivPacket popped off the Queue.
        """
        try:
            if not self.packets.empty():
                return self.packets.get()
        except KeyboardInterrupt:
            self.quit()
        return None

    def quit(self):
        if self.reader is not None:
            self.reader.running = False
        if self.crypto is not None:
            self.crypto.running = False
        self.running = False
        os._exit(1)


if __name__ == "__main__":
    a = Emotiv()
