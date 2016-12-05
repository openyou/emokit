# -*- coding: utf-8 -*-
import csv
import sys
from threading import Thread, Lock

from .python_queue import Queue


class EmotivWriter(object):
    """
    Write data from headset to output. CSV file for now.
    """

    def __init__(self, file_name, mode="csv", header_row=None, **kwargs):
        self.mode = mode
        self.lock = Lock()
        self.data = Queue()
        self.file_name = file_name
        self.header_row = header_row
        self.running = True
        self.stopped = False
        self.thread = Thread(target=self.run)
        self.thread.setDaemon(True)
        self._stop_signal = False
        self._stop_notified = False

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

        if sys.version_info >= (3, 0):
            file = open(self.file_name, 'w', newline='')
        else:
            file = open(self.file_name, 'wb')
        if self.mode == "csv":
            writer = csv.writer(file, quoting=csv.QUOTE_ALL)
            if self.header_row is not None:
                if sys.version_info >= (3, 0):
                    if type(self.header_row) == str:
                        data = bytes(self.header_row, encoding='latin-1')
                        writer.writerow(data)
                    else:
                        writer.writerow(self.header_row)
                else:
                    if type(self.header_row) == str:
                        data = [ord(char) for char in self.header_row]
                        writer.writerow(data)
                    else:
                        writer.writerow(self.header_row)

        else:
            writer = None
        self.lock.acquire()
        while self.running:
            self.lock.release()
            try:
                if not self.data.empty():
                    next_task = self.data.get_nowait()
                    if next_task.is_values:
                        data_to_write = [next_task.timestamp,
                                         next_task.data['F3']['value'], next_task.data['F3']['quality'],
                                         next_task.data['FC5']['value'], next_task.data['FC5']['quality'],
                                         next_task.data['F7']['value'], next_task.data['F7']['quality'],
                                         next_task.data['T7']['value'], next_task.data['T7']['quality'],
                                         next_task.data['P7']['value'], next_task.data['P7']['quality'],
                                         next_task.data['O1']['value'], next_task.data['O1']['quality'],
                                         next_task.data['O2']['value'], next_task.data['O2']['quality'],
                                         next_task.data['P8']['value'], next_task.data['P8']['quality'],
                                         next_task.data['T8']['value'], next_task.data['T8']['quality'],
                                         next_task.data['F8']['value'], next_task.data['F8']['quality'],
                                         next_task.data['AF4']['value'], next_task.data['AF4']['quality'],
                                         next_task.data['FC6']['value'], next_task.data['FC6']['quality'],
                                         next_task.data['F4']['value'], next_task.data['F4']['quality'],
                                         next_task.data['X']['value'], next_task.data['Y']['value'],
                                         next_task.data['Z']['value'],
                                         ]
                    else:
                        if next_task.is_encrypted:
                            if sys.version_info >= (3, 0):
                                data = map(bin, bytearray(next_task.data, encoding='latin-1'))
                            else:
                                data = map(bin, bytearray(next_task.data))
                        else:
                            data = next_task.data
                        if sys.version_info >= (3, 0):
                            if type(data) == str:
                                data = bytes(data, encoding='latin-1')
                        else:
                            if type(data) == str:
                                data = [ord(char) for char in data]
                        data_to_write = [next_task.timestamp, data]
                    writer.writerow(data_to_write)
            except Exception as ex:
                print(ex.message)
            self.lock.acquire()
            if self._stop_signal:
                if self.data.empty():
                    print("Writer thread stopping...")
                    self.running = False
                if not self._stop_notified:
                    print("Stop request received, Writer will empty queue before exiting.")
                    self._stop_notified = True

        if file is not None:
            file.close()
        print("Writer stopped...")
        self.stopped = True
        return
