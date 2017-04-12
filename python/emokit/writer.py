# -*- coding: utf-8 -*-
import sys
import time
from threading import Thread, Lock

from .python_queue import Queue
from .util import writer_task_to_line


class EmotivWriter(object):
    """
    Write data from headset to output. CSV file for now.
    """

    def __init__(self, file_name, mode="csv", header_row=None, chunk_writes=True, chunk_size=32, verbose=False,
                 **kwargs):
        self.mode = mode
        self.lock = Lock()
        self.data = Queue()
        self.file_name = file_name
        self.header_row = header_row
        self.running = True
        self.stopped = False
        self.chunk_writes = chunk_writes
        self.chunk_size = chunk_size
        self.thread = Thread(target=self.run)
        self.thread.setDaemon(True)
        self._stop_signal = False
        self._stop_notified = False
        self.verbose = verbose

    def start(self):
        """
        Starts the writer thread.
        """
        self.running = True
        self.stopped = False
        self.thread.start()

    def stop(self):
        """
        Stops the writer thread.
        """
        self.lock.acquire()
        self._stop_signal = True
        self.lock.release()

    def run(self, source=None):
        """Do not call explicitly, called upon initialization of class"""
        if self.mode == "csv":
            if sys.version_info >= (3, 0):
                output_file = open(self.file_name, 'w', newline='')
            else:
                output_file = open(self.file_name, 'wb')
            if self.header_row is not None:
                if type(self.header_row) == str:
                    output_file.write(self.header_row)
                else:
                    output_file.write(','.join(self.header_row) + '\n')

        else:
            output_file = None

        data_buffer = None
        data_buffer_size = 1
        if self.chunk_writes:
            data_buffer = []
            data_buffer_size = self.chunk_size

        self.lock.acquire()
        while self.running:
            self.lock.release()
            try:
                if not self.data.empty():
                    next_task = self.data.get_nowait()
                    if next_task.is_values:
                        data_to_write = writer_task_to_line(next_task)
                    else:
                        if next_task.is_encrypted:
                            if sys.version_info >= (3, 0):
                                data = map(bin, bytearray(next_task.data, encoding='latin-1'))
                            else:
                                data = map(bin, bytearray(next_task.data))
                        else:
                            data = next_task.data
                        if sys.version_info >= (3, 0):
                            # Values are int
                            data = ','.join([str(value) for value in data])
                        else:
                            if type(data) == str:
                                data = ','.join([str(ord(char)) for char in data])
                            else:
                                # Writing encrypted.
                                data = ','.join([char for char in data])
                        data_to_write = ','.join([str(next_task.timestamp), data])
                        data_to_write += '\n'
                    if data_buffer is not None:
                        data_buffer.append(data_to_write)
                        if len(data_buffer) >= data_buffer_size - 1:
                            output_file.writelines(data_buffer)
                            data_buffer = []
                    else:
                        output_file.write(data_to_write)

            except Exception as ex:
                if self.verbose:
                    print("Error: {}".format(ex.message))
            self.lock.acquire()
            if self._stop_signal:
                print("Writer thread stopping...")
                self.running = False
                if not self._stop_notified:
                    print("Stop request received, Writer will empty queue before exiting.")
                    self._stop_notified = True
                time.sleep(0.00001)
        self.lock.release()
        if output_file is not None:
            if data_buffer is not None:
                if len(data_buffer):
                    output_file.writelines(data_buffer)
            if not self.data.empty():
                while not self.data.empty():
                    packet = self.data.get_nowait()
                    if packet is not None:
                        output_file.write(writer_task_to_line(packet))
            output_file.close()
        print("Writer stopped...")
        self.stopped = True
        return
