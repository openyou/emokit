# -*- coding: utf-8 -*-
import sys
import time
from threading import Thread, Lock

from .python_queue import Queue


class EmotivWriter(object):
    """
    Write data from headset to output. CSV file for now.
    """

    def __init__(self, file_name, mode="csv", header_row=None, chunk_writes=True, chunk_size=16, **kwargs):
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
                if sys.version_info >= (3, 0):
                    if type(self.header_row) == str:
                        data = bytes(self.header_row, encoding='latin-1')
                        output_file.write(data + '\n')
                    else:
                        output_file.write(','.join(self.header_row) + '\n')
                else:
                    if type(self.header_row) == str:
                        data = [ord(char) for char in self.header_row]
                        output_file.write(data + '\n')
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
                        data_to_write = "{timestamp},{f3_value},{f3_quality},{fc5_value},{fc5_quality},{f7_value}," \
                                        "{f7_quality},{t7_value},{t7_quality},{p7_value},{p7_quality},{o1_value}," \
                                        "{o1_quality},{o2_value},{o2_quality},{p8_value},{p8_quality},{t8_value}," \
                                        "{t8_quality},{f8_value},{f8_quality},{af4_value},{af4_quality},{fc6_value}," \
                                        "{fc6_quality},{f4_value},{f4_quality},{x_value},{y_value},{z_value}\n".format(
                            timestamp=str(next_task.timestamp),
                            f3_value=next_task.data['F3']['value'],
                            f3_quality=next_task.data['F3']['quality'],
                            fc5_value=next_task.data['FC5']['value'],
                            fc5_quality=next_task.data['FC5']['quality'],
                            f7_value=next_task.data['F7']['value'],
                            f7_quality=next_task.data['F7']['quality'],
                            t7_value=next_task.data['T7']['value'],
                            t7_quality=next_task.data['T7']['quality'],
                            p7_value=next_task.data['P7']['value'],
                            p7_quality=next_task.data['P7']['quality'],
                            o1_value=next_task.data['O1']['value'],
                            o1_quality=next_task.data['O1']['quality'],
                            o2_value=next_task.data['O2']['value'],
                            o2_quality=next_task.data['O2']['quality'],
                            p8_value=next_task.data['P8']['value'],
                            p8_quality=next_task.data['P8']['quality'],
                            t8_value=next_task.data['T8']['value'],
                            t8_quality=next_task.data['T8']['quality'],
                            f8_value=next_task.data['F8']['value'],
                            f8_quality=next_task.data['F8']['quality'],
                            af4_value=next_task.data['AF4']['value'],
                            af4_quality=next_task.data['AF4']['quality'],
                            fc6_value=next_task.data['FC6']['value'],
                            fc6_quality=next_task.data['FC6']['quality'],
                            f4_value=next_task.data['F4']['value'],
                            f4_quality=next_task.data['F4']['quality'],
                            x_value=next_task.data['X']['value'],
                            y_value=next_task.data['Y']['value'],
                            z_value=next_task.data['Z']['value']
                        )
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
                        data_to_write = [str(next_task.timestamp), data]
                    if data_buffer is not None:
                        data_buffer.append(data_to_write)
                        if len(data_buffer) >= data_buffer_size - 1:
                            output_file.writelines(data_buffer)
                            data_buffer = []
                    else:
                        output_file.write(data_to_write)

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
                time.sleep(0.00001)
        if output_file is not None:
            output_file.close()
        print("Writer stopped...")
        self.stopped = True
        return
