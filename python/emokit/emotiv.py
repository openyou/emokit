# -*- coding: utf-8 -*-
from __future__ import absolute_import, division

import os
import sys
from datetime import datetime
from threading import Thread, Lock
from time import time

from .decrypter import EmotivCrypto
from .output import EmotivOutput
from .packet import EmotivNewPacket, EmotivOldPacket, EmotivExtraPacket
from .python_queue import Queue
from .reader import EmotivReader
from .sensors import sensors_mapping
from .tasks import EmotivOutputTask, EmotivWriterTask
from .util import path_checker, system_platform, values_header, is_extra_data
from .writer import EmotivWriter


class Emotiv(object):
    """
    Receives, decrypts and stores packets received from Emotiv Headsets and other sources.
    """

    # TODO: Add a calibration mechanism, get a "noise average" per sensor or even a "noise pattern" to filter
    #       sensor values when processing packets received. Ideally this would be done not on someone's head.
    # TODO: Add filters for facial expressions, muscle contractions.
    def __init__(self, display_output=False, serial_number=None, is_research=False, write=False,
                 write_encrypted=False, write_decrypted=False, write_values=True, input_source="emotiv",
                 sys_platform=system_platform, verbose=False, output_path=None, chunk_writes=True, chunk_size=32,
                 force_epoc_mode=False, force_old_crypto=False):
        """
        Sets up initial values.

        :param display_output - Should non-error output be displayed to console?
        :param serial_number - Specify serial_number, needed to decrypt packets for raw data reader and special cases.
        :param is_research - Is EPOC headset research edition? Doesn't seem to work even if it is.
        :param write - Write data to csv.
        :param write_encrypted - Write encrypted data, may impact read performance.
        :param write_values - Write decrypted sensor data, True overwrites exporting data from dongle pre-processing.
        :param input_source - Source to read from, emotiv or a file name
                   (must be a csv, exported from emokit or following our format)
        :param sys_platform - Operating system, to avoid global statement
        :param verbose - Detailed logging.
        :param output_path - The path to output data files to.
        :param chunk_writes - Write a chunk of data instead of a single line.
        :param chunk_size - The number of packets to buffer before writing.

        Expect performance to suffer when writing data to a csv, maybe.

        """
        print("Initializing Emokit...")
        self.new_format = False
        self.running = False
        self.chunk_writes = chunk_writes
        self.chunk_size = chunk_size
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
        self.write_encrypted = write_encrypted
        # Write the data received after decrypting it.
        self.write_decrypted = write_decrypted
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
        self.output_path = output_path
        self.force_epoc_mode = force_epoc_mode
        self.force_old_crypto = force_old_crypto
        self.crypto = None
        # Setup the crypto thread, if we are reading from an encrypted data source.

        # Setup emokit loop thread. This thread coordinates the work done from the reader to be decrypted and queued
        # into EmotivPackets.
        self.output = None
        self.thread = Thread(target=self.run)
        self._stop_signal = False
        self.thread.setDaemon(True)
        self.start()

    def initialize_output(self):
        print("Initializing Output Thread...")
        if self.display_output:
            self.output = EmotivOutput(serial_number=self.serial_number, old_model=self.old_model, verbose=self.verbose)

    def initialize_reader(self):
        print("Initializing Reader Thread...")
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
            self.reader = EmotivReader(file_name=self.input_source, mode="csv", new_format=self.new_format)
            # Make sure the reader still has the serial number set, since we won't be obtaining it from the headset.
            self.reader.serial_number = self.serial_number
        else:
            # Initialize an EmotivReader with default values, it will try to locate a headset.
            self.reader = EmotivReader()
            if self.reader.serial_number is not None:
                # If EmotivReader found a serial number automatically, change local serial number to the reader serial.
                self.serial_number = self.reader.serial_number

    def initialize_writer(self):
        print("Initializing Writer Thread(s)...")
        if self.write:
            if self.write_encrypted:
                # Only write encrypted if we are reading encrypted.
                if self.read_encrypted:
                    output_path = "emotiv_encrypted_data_%s_%s.csv" % \
                                  (self.reader.serial_number, str(datetime.now()).replace(':', '-'))
                    if self.output_path is not None:
                        if type(self.output_path) == str:
                            output_path = path_checker(self.output_path, output_path)
                    self.encrypted_writer = EmotivWriter(output_path, mode="csv", chunk_writes=self.chunk_writes,
                                                         chunk_size=self.chunk_size)
                    self.encrypted_writer.start()

            # Setup decrypted data writer.
            if self.write_decrypted:
                # If we are reading values we do not have the decrypted data,
                # rather than reconstructing it do not write it.
                if not self.read_values:
                    output_path = 'emotiv_data_%s.csv' % str(datetime.now()).replace(':', '-')
                    if self.output_path is not None:
                        if type(self.output_path) == str:
                            output_path = path_checker(self.output_path, output_path)
                    self.decrypted_writer = EmotivWriter(output_path, mode="csv", chunk_writes=self.chunk_writes,
                                                         chunk_size=self.chunk_size)
                    self.decrypted_writer.start()

            # Setup sensor value writer.
            if self.write_values:
                output_path = 'emotiv_values_%s.csv' % str(datetime.now()).replace(':', '-')
                if self.output_path is not None:
                    if type(self.output_path) == str:
                        output_path = path_checker(self.output_path, output_path)
                self.value_writer = EmotivWriter(output_path, mode="csv", chunk_writes=self.chunk_writes,
                                                 chunk_size=self.chunk_size)
                # Make the first row in the file the header with the sensor name
                self.value_writer.header_row = values_header
                self.value_writer.start()

    def initialize_crypto(self):
        print("Initializing Crypto Thread...")
        if self.read_encrypted:
            self.crypto = EmotivCrypto(self.serial_number, self.is_research, verbose=self.verbose,
                                       force_epoc_mode=self.force_epoc_mode, force_old_crypto=self.force_old_crypto)

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
        if self.reader is not None:
            self.reader.stop()
        if self.crypto is not None:
            self.crypto.stop()
        if self.decrypted_writer is not None:
            self.decrypted_writer.stop()
        if self.encrypted_writer is not None:
            self.encrypted_writer.stop()
        if self.value_writer is not None:
            self.value_writer.stop()
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
            print("Log: %s" % message)

    def run(self):
        """ Do not call explicitly, called upon initialization of class or self.start()
            The main emokit loop.
        :param reader: EmotivReader class
        :param crypto: EmotivCrypto class
        """
        self.initialize_reader()
        if self.serial_number.startswith("UD2016") and not self.force_epoc_mode:
            self.new_format = True
        self.initialize_writer()
        self.initialize_crypto()
        self.initialize_output()
        if self.output is not None:
            self.output.start()
        self.reader.start()
        if self.crypto is not None:
            self.crypto.start()
        last_packets_received = 0
        tick_time = time()
        stale_rx = 0
        restarting_reader = False
        self.lock.acquire()
        while self.running:
            self.lock.release()
            if not self.reader.data.empty():
                try:
                    reader_task = self.reader.data.get()
                except KeyboardInterrupt:
                    self.quit()
                if self.write and self.write_encrypted and self.input_source == 'emotiv':
                    # Due to some encoding problem to save encrypted data we must first convert it to binary.
                    self.encrypted_writer.data. \
                        put_nowait(EmotivWriterTask(data=reader_task.data, encrypted=True, values=False))

                self.packets_received += 1
                if not self.read_encrypted:
                    if not self.read_values:
                        extra_data = False
                        if self.new_format:
                            extra_data = is_extra_data(reader_task.data)
                            if extra_data:
                                new_packet = EmotivExtraPacket(reader_task.data, verbose=self.verbose)
                            else:
                                new_packet = EmotivNewPacket(reader_task.data, verbose=self.verbose)
                        else:
                            new_packet = EmotivOldPacket(reader_task.data, verbose=self.verbose)
                        if new_packet.battery is not None:
                            self.battery = new_packet.battery
                        self.packets.put_nowait(new_packet)
                        self.packets_processed += 1
                        if self.display_output:
                            if self.new_format:
                                if extra_data:
                                    self.output.tasks.put_nowait(EmotivOutputTask(received=True,
                                                                                  decrypted=True,
                                                                                  data=EmotivExtraPacket(raw_data)))
                                else:
                                    self.output.tasks.put_nowait(EmotivOutputTask(received=True,
                                                                                  decrypted=True,
                                                                                  data=EmotivNewPacket(raw_data)))
                            else:
                                self.output.tasks.put_nowait(EmotivOutputTask(received=True,
                                                                              decrypted=True,
                                                                              data=EmotivOldPacket(raw_data)))
                    else:
                        # TODO: Implement read from values.
                        pass
                else:
                    if self.input_source != 'emotiv' and self.read_encrypted:
                        if len(reader_task.data) == 33:
                            reader_task.data = reader_task.data[1:]
                        if len(reader_task.data) != 32:
                            print("Reader task: {}".format(len(reader_task.data)))
                            self.reader.stop()
                            self.crypto.stop()
                            self.running = False
                            raise ValueError("Reached end of data or corrupted data.")
                        # Decode binary data stored in file.
                        if sys.version_info >= (3, 0):
                            raw_data = [int(bytes(item, encoding='latin-1').decode(), 2) for item in reader_task.data]
                        else:
                            raw_data = [int(item, 2) for item in reader_task.data]

                        raw_data = ''.join(map(chr, raw_data[:]))
                        reader_task.data = raw_data

                    if self.display_output:
                        self.output.tasks.put_nowait(EmotivOutputTask(received=True))
                    self.crypto.add_task(reader_task)
            if self.crypto is not None:
                if self.crypto.data_ready():
                    decrypted_task = self.crypto.get_data()
                    if self.write:
                        if self.write_decrypted:
                            if self.decrypted_writer is not None:
                                self.decrypted_writer.data. \
                                    put_nowait(EmotivWriterTask(decrypted_task.data, values=False,
                                                                timestamp=decrypted_task.timestamp))
                    self.packets_processed += 1
                    extra_data = False
                    if self.new_format:
                        extra_data = is_extra_data(decrypted_task.data)
                        if extra_data:
                            new_packet = EmotivExtraPacket(decrypted_task.data, timestamp=decrypted_task.timestamp)
                        else:
                            if self.force_epoc_mode:
                                new_packet = EmotivOldPacket(decrypted_task.data, timestamp=decrypted_task.timestamp)
                            else:
                                new_packet = EmotivNewPacket(decrypted_task.data, timestamp=decrypted_task.timestamp)
                    else:
                        new_packet = EmotivOldPacket(decrypted_task.data, timestamp=decrypted_task.timestamp)
                    # print(new_packet.counter)
                    # data = []
                    # for c in new_packet.raw_data:
                    #    if c > 0:
                    #        data.append(ord(c))
                    # print(data)

                    # values = [new_packet.sensors[name]['value'] for name in
                    #          'AF3 F7 F3 FC5 T7 P7 O1 O2 P8 T8 FC6 F4 F8 AF4'.split(' ')]
                    # cy = struct.pack('>' + str(len(values)) + 'h', *values)
                    # print(cy)

                    if self.display_output:
                        if self.new_format:
                            if extra_data:
                                self.output.tasks.put_nowait(EmotivOutputTask(decrypted=True,
                                                                              data=EmotivExtraPacket(
                                                                                  decrypted_task.data)))

                            else:
                                self.output.tasks.put_nowait(EmotivOutputTask(decrypted=True,
                                                                              data=EmotivNewPacket(
                                                                                  decrypted_task.data)))
                        else:
                            self.output.tasks.put_nowait(EmotivOutputTask(decrypted=True,
                                                                          data=EmotivOldPacket(decrypted_task.data)))
                    if type(new_packet) == EmotivOldPacket:
                        if new_packet.battery is not None:
                            self.battery = new_packet.battery
                    self.packets.put_nowait(new_packet)
                    if self.write:
                        if self.write_values:
                            if self.value_writer is not None:
                                if not extra_data:
                                    self.value_writer.data.put_nowait(
                                        EmotivWriterTask(
                                            data=new_packet.sensors.copy(),
                                            timestamp=decrypted_task.timestamp
                                        )
                                    )
            tick_diff = time() - tick_time
            if tick_diff >= 1:
                tick_time = time()
                packets_received_since_last_update = self.packets_received - last_packets_received
                if packets_received_since_last_update == 1 or packets_received_since_last_update == 0:
                    stale_rx += 1
                last_packets_received = self.packets_received
                if restarting_reader and self.reader.stopped:
                    print("Restarting Reader")
                    stale_rx = 0
                    self.initialize_reader()
                    self.reader.start()
                    restarting_reader = False
                    print("Reader Thread Restarted")

                if stale_rx > 5 and not restarting_reader:
                    self.reader.stop()
                    restarting_reader = True

            self.lock.acquire()
            if self._stop_signal:
                should_stop = True
                if self.reader.running:
                    should_stop = False
                if self.crypto is not None:
                    if self.crypto.running and self.crypto.data_ready():
                        should_stop = False
                if self.decrypted_writer is not None:
                    if self.decrypted_writer.running:
                        should_stop = False
                if self.encrypted_writer is not None:
                    if self.encrypted_writer.running:
                        should_stop = False
                if self.value_writer is not None:
                    if self.value_writer.running:
                        should_stop = False
                if self.output is not None:
                    if self.output.running:
                        should_stop = False
                if should_stop:
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
