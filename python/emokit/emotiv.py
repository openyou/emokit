# -*- coding: utf-8 -*-
from __future__ import absolute_import, division

import os
import platform
import sys
from datetime import datetime
from threading import Thread, Lock

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

    # TODO: Add a calibration mechanism, get a "noise average" per sensor or even a "noise pattern" to filter
    #       sensor values when processing packets received. Ideally this would be done not on someone's head.
    # TODO: Add filters for facial expressions, muscle contractions.
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

        Expect performance to suffer when writing data to a csv.

        """
        self.running = False
        # Queue with EmotivPackets that have been received.
        self.packets = Queue()
        # Battery percent, as int.
        self.battery = 0
        # Display sensor values in console.
        self.display_output = display_output
        # Print details of operation in console, exceptions, etc.
        self.verbose = verbose
        # Should be True for research edition EPOCs and newer EPOC+s, apparently.
        self.is_research = is_research
        self.sensors = sensors_mapping
        # The EPOCs serial number.
        self.serial_number = serial_number
        # Only really applies to quality value calculation, probably needs some updating.
        self.old_model = False
        # Write data to disk.
        self.write = write
        # Assume we are going to read encrypted data from the headset.
        self.read_encrypted = True
        # Not used at the moment.
        self.read_values = False
        # Write the data received as is.
        self.write_encrypted = False
        # Write the data received after decrypting it.
        self.write_decrypted = False
        # Write values and quality values of each sensor.
        self.write_values = write_values
        # The current platform.
        self.platform = sys_platform
        # The number of times data was received.
        self.packets_received = 0
        # The number of times data was decrypted or made into EmotivPackets.
        self.packets_processed = 0
        # The source of the emotiv data.
        self.input_source = input_source
        # If the input source is not an emotiv headset, it is a file.
        self.reader = None
        self.lock = Lock()
        # Setup output writers, multiple types can be output now at once.
        self.encrypted_writer = None
        self.decrypted_writer = None
        self.value_writer = None

        self.crypto = None
        # Setup the crypto thread, if we are reading from an encrypted data source.

        # Setup emokit loop thread. This thread coordinates the work done from the reader to be decrypted and queued
        # into EmotivPackets.
        self.thread = Thread(target=self.run)
        self._stop_signal = False
        self.thread.setDaemon(True)
        self.start()

    def initialize_reader(self):
        if self.input_source != "emotiv":
            # If the name of the input source starts with emotiv_encrypted, get the serial number.
            if self.input_source.startswith('emotiv_encrypted'):
                # Split the name of the input by _'s and retrieve the serial number, typically located after
                # emotiv_encrypted_data_ so index 3.
                self.serial_number = self.input_source.split('_')[3]
            else:
                # Otherwise, check if it is values only and set read_encrypted to False.
                self.read_encrypted = False
                if self.input_source.startswith('emotiv_values'):
                    self.read_values = True
            self.reader = EmotivReader(file_name=self.input_source, mode="csv")
            # Make sure the reader still has the serial number set, since we won't be obtaining it from the headset.
            self.reader.serial_number = self.serial_number
        else:
            # Initialize an EmotivReader with default values, it will try to locate a headset.
            self.reader = EmotivReader()
            if self.reader.serial_number is not None:
                # If EmotivReader found a serial number automatically, change local serial number to the reader serial.
                self.serial_number = self.reader.serial_number

    def initialize_writer(self):
        if self.write_encrypted:
            # Only write encrypted if we are reading encrypted.
            if self.read_encrypted:
                self.encrypted_writer = EmotivWriter('emotiv_encrypted_data_%s_%s.csv' % (
                    self.reader.serial_number, str(datetime.now()).replace(':', '-')), mode="csv")

        # Setup decrypted data writer.
        if self.write_decrypted:
            # If we are reading values we do not have the decrypted data, rather than reconstructing it do not write it.
            if not self.read_values:
                self.decrypted_writer = EmotivWriter('emotiv_data_%s.csv' % str(datetime.now()).replace(':', '-'),
                                                     mode="csv")
        # Setup sensor value writer.
        if self.write_values:
            self.value_writer = EmotivWriter('emotiv_values_%s.csv' % str(datetime.now()).replace(':', '-'),
                                             mode="csv")
            # Make the first row in the file the header with the sensor name
            header_row = []
            for key in self.sensors.keys():
                header_row.append(key + " Value")
                header_row.append(key + " Quality")
            self.value_writer.write(header_row)

    def initialize_crypto(self):
        if self.read_encrypted:
            self.crypto = EmotivCrypto(self.serial_number, self.is_research)

    def start(self):
        """
        Starts emotiv, called upon initialization.
        """
        self.running = True
        self.thread.start()

    def stop(self):
        """
        Stops emotiv
        :return:
        """
        self.reader.stop()
        if self.crypto is not None:
            self.crypto.stop()
        self._stop_signal = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if traceback:
            self.log(traceback)
        self.stop()

    def log(self, message):
        """
        Logging function, only prints if verbose is True.
        :param message: Message to log/print
        """
        if self.display_output and self.verbose:
            print("%s" % message)

    def run(self):
        """ Do not call explicitly, called upon initialization of class or self.start()
            The main emokit loop.
        :param reader: EmotivReader class
        :param crypto: EmotivCrypto class
        """
        self.initialize_reader()
        self.initialize_writer()
        self.initialize_crypto()
        self.reader.start()
        if self.crypto is not None:
            self.crypto.start()
        dirty = True
        last_packets_received = 0
        last_packets_decrypted = 0
        tick_time = datetime.now()
        packets_received_since_last_update = 0
        packets_processed_since_last_update = 0
        stale_rx = 0
        restarting_reader = False
        self.lock.acquire()
        while self.running:
            self.lock.release()
            if not self.reader.data.empty():
                try:
                    raw_data = self.reader.data.get()
                except KeyboardInterrupt:
                    self.quit()
                if self.write and self.write_encrypted and self.input_source == 'emotiv':
                    # Due to some encoding problem to save encrypted data we must first convert it to binary.
                    if sys.version_info >= (3, 0):
                        self.encrypted_writer.write(map(bin, bytearray(raw_data, encoding='latin-1')))
                    else:
                        self.encrypted_writer.write(map(bin, bytearray(raw_data)))
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
                            self.reader.lock.acquire()
                            self.reader.running = False
                            self.reader.lock.release()
                            self.crypto.stop()
                            self.running = False
                            raise ValueError("Reached end of data or corrupted data.")
                        # Decode binary data stored in file.

                        if sys.version_info >= (3, 0):
                            raw_data = [int(bytes(item, encoding='latin-1').decode(), 2) for item in raw_data]
                        else:
                            raw_data = [int(item.decode(), 2) for item in raw_data]
                        raw_data = ''.join(map(chr, raw_data[:]))
                    self.crypto.add_task(raw_data)
            if self.crypto is not None:
                if self.crypto.data_ready():
                    decrypted_packet_data = self.crypto.get_data()
                    if self.write_decrypted:
                        if self.decrypted_writer is not None:
                            self.decrypted_writer.write(decrypted_packet_data)
                    self.packets_processed += 1
                    new_packet = EmotivPacket(decrypted_packet_data)
                    if new_packet.battery is not None:
                        self.battery = new_packet.battery
                    self.packets.put_nowait(new_packet)
                    if self.write_values:
                        data_to_write = []
                        for key in self.sensors.keys():
                            data_to_write.extend([new_packet.sensors[key]['value'], new_packet.sensors[key]['quality']])
                        if self.value_writer is not None:
                            self.value_writer.write(data_to_write)
                    dirty = True
            if self._stop_signal:
                self.reader.lock.acquire()
                if not self.reader.running and not restarting_reader:
                    if self.crypto is not None:
                        self.crypto.lock.acquire()
                        if not self.crypto.running and not self.crypto.data_ready():
                            self.running = False
                        self.crypto.lock.release()
                    else:
                        self.running = False
                self.reader.lock.release()

            if tick_time.second != datetime.now().second:
                packets_received_since_last_update = self.packets_received - last_packets_received
                if packets_received_since_last_update == 1 or packets_received_since_last_update == 0:
                    stale_rx += 1
                packets_processed_since_last_update = self.packets_processed - last_packets_decrypted
                last_packets_decrypted = self.packets_processed
                last_packets_received = self.packets_received
                tick_time = datetime.now()
                dirty = True
                self.reader.lock.acquire()
                if restarting_reader and self.reader.stopped:
                    self.reader.lock.release()
                    print("Restarting reader")
                    stale_rx = 0
                    self.initialize_reader()
                    self.reader.start()
                    restarting_reader = False
                    print("End restarting")
                else:
                    self.reader.lock.release()

                if stale_rx > 5 and not restarting_reader:
                    self.reader.stop()
                    restarting_reader = True

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
                    print("Sample Rate Rx: {0} Crypto: {1}".format(
                        packets_received_since_last_update,
                        packets_processed_since_last_update)
                    )
                    dirty = False
            self.lock.acquire()
        self.lock.release()

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

    def clear_queue(self):
        self.packets = Queue()

    def quit(self):
        """
        A little more forceful stop.
        """
        self.stop()
        os._exit(1)

    def force_quit(self):
        """
        Kill emokit. Might leave files and other objects open or locked.
        """
        os._exit(1)


if __name__ == "__main__":
    a = Emotiv()
