# -*- coding: utf-8 -*-
import os
import time
from threading import Thread, Lock

from packet import EmotivExtraPacket
from .python_queue import Queue
from .sensors import sensors_mapping
from .util import get_quality_scale_level, system_platform


class EmotivOutput(object):
    """
        Write output to console.
    """

    def __init__(self, serial_number="", old_model=False, verbose=False):
        self.tasks = Queue()
        self.running = True
        self.stopped = False
        self.packets_received = 0
        # The number of times data was decrypted or made into EmotivPackets.
        self.packets_processed = 0
        self._stop_signal = False
        self.serial_number = serial_number
        self.old_model = old_model
        self.lock = Lock()
        self.verbose = verbose
        self.thread = Thread(target=self.run, kwargs={'verbose': self.verbose})
        self.thread.setDaemon(True)

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

    def run(self, source=None, verbose=False):
        """Do not call explicitly, called upon initialization of class"""
        # self.lock.acquire()
        dirty = False
        tick_time = time.time()
        last_packets_received = 0
        last_packets_decrypted = 0
        packets_received_since_last_update = 0
        packets_processed_since_last_update = 0
        battery = 0
        last_sensors = sensors_mapping.copy()
        self.lock.acquire()
        while self.running:
            self.lock.release()
            while not self.tasks.empty():
                next_task = self.tasks.get_nowait()

                if next_task.packet_received:
                    self.packets_received += 1

                if next_task.packet_decrypted:
                    self.packets_processed += 1
                    if type(next_task.packet_data) != EmotivExtraPacket:
                        if next_task.packet_data.battery is not None:
                            battery = next_task.packet_data.battery
                        last_sensors = next_task.packet_data.sensors
                        # print(type(next_task.packet_data))
                if time.time() - tick_time > 1:
                    tick_time = time.time()
                    packets_received_since_last_update = self.packets_received - last_packets_received
                    packets_processed_since_last_update = self.packets_processed - last_packets_decrypted
                    last_packets_decrypted = self.packets_processed
                    last_packets_received = self.packets_received
                    dirty = True
                if dirty or verbose:
                    if not verbose:
                        if system_platform == "Windows":
                            os.system('cls')
                        else:
                            os.system('clear')
                    if battery is None:
                        # TODO: Figure out why battery is None, probably just because the counter
                        #  hasn't rolled to the battery counter yet. except for new devices apparently.
                        battery = 0
                    print(output_template.format(
                        serial_number=self.serial_number,
                        f3_value=last_sensors['F3']['value'],
                        fc5_value=last_sensors['FC5']['value'],
                        af3_value=last_sensors['AF3']['value'],
                        f7_value=last_sensors['F7']['value'],
                        t7_value=last_sensors['T7']['value'],
                        p7_value=last_sensors['P7']['value'],
                        o1_value=last_sensors['O1']['value'],
                        o2_value=last_sensors['O2']['value'],
                        p8_value=last_sensors['P8']['value'],
                        t8_value=last_sensors['T8']['value'],
                        f8_value=last_sensors['F8']['value'],
                        af4_value=last_sensors['AF4']['value'],
                        fc6_value=last_sensors['FC6']['value'],
                        f4_value=last_sensors['F4']['value'],
                        f3_quality=last_sensors['F3']['quality'],
                        fc5_quality=last_sensors['FC5']['quality'],
                        af3_quality=last_sensors['AF3']['quality'],
                        f7_quality=last_sensors['F7']['quality'],
                        t7_quality=last_sensors['T7']['quality'],
                        p7_quality=last_sensors['P7']['quality'],
                        o1_quality=last_sensors['O1']['quality'],
                        o2_quality=last_sensors['O2']['quality'],
                        p8_quality=last_sensors['P8']['quality'],
                        t8_quality=last_sensors['T8']['quality'],
                        f8_quality=last_sensors['F8']['quality'],
                        af4_quality=last_sensors['AF4']['quality'],
                        fc6_quality=last_sensors['FC6']['quality'],
                        f4_quality=last_sensors['F4']['quality'],
                        f3_quality_old=get_quality_scale_level(last_sensors['F3']['quality'], True),
                        fc5_quality_old=get_quality_scale_level(last_sensors['FC5']['quality'], True),
                        af3_quality_old=get_quality_scale_level(last_sensors['AF3']['quality'], True),
                        f7_quality_old=get_quality_scale_level(last_sensors['F7']['quality'], True),
                        t7_quality_old=get_quality_scale_level(last_sensors['T7']['quality'], True),
                        p7_quality_old=get_quality_scale_level(last_sensors['P7']['quality'], True),
                        o1_quality_old=get_quality_scale_level(last_sensors['O1']['quality'], True),
                        o2_quality_old=get_quality_scale_level(last_sensors['O2']['quality'], True),
                        p8_quality_old=get_quality_scale_level(last_sensors['P8']['quality'], True),
                        t8_quality_old=get_quality_scale_level(last_sensors['T8']['quality'], True),
                        f8_quality_old=get_quality_scale_level(last_sensors['F8']['quality'], True),
                        af4_quality_old=get_quality_scale_level(last_sensors['AF4']['quality'], True),
                        fc6_quality_old=get_quality_scale_level(last_sensors['FC6']['quality'], True),
                        f4_quality_old=get_quality_scale_level(last_sensors['F4']['quality'], True),
                        f3_quality_new=get_quality_scale_level(last_sensors['F3']['quality'], False),
                        fc5_quality_new=get_quality_scale_level(last_sensors['FC5']['quality'], False),
                        af3_quality_new=get_quality_scale_level(last_sensors['AF3']['quality'], False),
                        f7_quality_new=get_quality_scale_level(last_sensors['F7']['quality'], False),
                        t7_quality_new=get_quality_scale_level(last_sensors['T7']['quality'], False),
                        p7_quality_new=get_quality_scale_level(last_sensors['P7']['quality'], False),
                        o1_quality_new=get_quality_scale_level(last_sensors['O1']['quality'], False),
                        o2_quality_new=get_quality_scale_level(last_sensors['O2']['quality'], False),
                        p8_quality_new=get_quality_scale_level(last_sensors['P8']['quality'], False),
                        t8_quality_new=get_quality_scale_level(last_sensors['T8']['quality'], False),
                        f8_quality_new=get_quality_scale_level(last_sensors['F8']['quality'], False),
                        af4_quality_new=get_quality_scale_level(last_sensors['AF4']['quality'], False),
                        fc6_quality_new=get_quality_scale_level(last_sensors['FC6']['quality'], False),
                        f4_quality_new=get_quality_scale_level(last_sensors['F4']['quality'], False),
                        x=str(last_sensors['X']['value']),
                        y=str(last_sensors['Y']['value']),
                        z=str(last_sensors['Z']['value']),
                        battery=battery,
                        sample_rate=str(packets_received_since_last_update),
                        crypto_rate=str(packets_processed_since_last_update),
                        received=str(self.packets_received),
                        processed=str(self.packets_processed),
                        old_model=self.old_model
                    ))
                    dirty = False
            self.lock.acquire()
            if self._stop_signal:
                print("Output thread stopping.")
                self.running = False
            time.sleep(0.11)
        self.lock.release()


output_template = """
Emokit - v0.0.8 SN: {serial_number}  Old Model: {old_model}
+========================================================+
| Sensor |   Value  | Quality  | Quality L1 | Quality L2 |
+--------+----------+----------+------------+------------+
|   F3   | {f3_value:^8.10f} | {f3_quality:^8} |  {f3_quality_old:^8}  |  {f3_quality_new:^8}  |
|   FC5  | {fc5_value:^8.10f} | {fc5_quality:^8} |  {fc5_quality_old:^8}  |  {fc5_quality_new:^8}  |
|   AF3  | {af3_value:^8.10f} | {af3_quality:^8} |  {af3_quality_old:^8}  |  {af3_quality_new:^8}  |
|   F7   | {f7_value:^8.10f} | {f7_quality:^8} |  {f7_quality_old:^8}  |  {f7_quality_new:^8}  |
|   T7   | {t7_value:^8.10f} | {t7_quality:^8} |  {t7_quality_old:^8}  |  {t7_quality_new:^8}  |
|   P7   | {p7_value:^8.10f} | {p7_quality:^8} |  {p7_quality_old:^8}  |  {p7_quality_new:^8}  |
|   O1   | {o1_value:^8.10f} | {o1_quality:^8} |  {o1_quality_old:^8}  |  {o1_quality_new:^8}  |
|   O2   | {o2_value:^8.10f} | {o2_quality:^8} |  {o2_quality_old:^8}  |  {o1_quality_new:^8}  |
|   P8   | {p8_value:^8.10f} | {p8_quality:^8} |  {p8_quality_old:^8}  |  {p8_quality_new:^8}  |
|   T8   | {t8_value:^8.10f} | {t8_quality:^8} |  {t8_quality_old:^8}  |  {t8_quality_new:^8}  |
|   F8   | {f8_value:^8.10f} | {f8_quality:^8} |  {f8_quality_old:^8}  |  {f8_quality_new:^8}  |
|   AF4  | {af4_value:^8.10f} | {af4_quality:^8} |  {af4_quality_old:^8}  |  {af4_quality_new:^8}  |
|   FC6  | {fc6_value:^8.10f} | {fc6_quality:^8} |  {fc6_quality_old:^8}  |  {fc6_quality_new:^8}  |
|   F4   | {f4_value:^8.10f} | {f4_quality:^8} |  {f4_quality_old:^8}  |  {f4_quality_new:^8}  |
|   X    | {x:^8} |   N/A    |    N/A     |    N/A     |
|   Y    | {y:^8} |   N/A    |    N/A     |    N/A     |
|   Z    | {z:^8} |   N/A    |    N/A     |    N/A     |
|  Batt  | {battery:^8} |   N/A    |    N/A     |    N/A     |
+--------+----------+----------+------------+------------+
|Packets Received: {received:^7}  |  Packets Processed: {processed:^7}|
|   Sampling Rate: {sample_rate:^7}  |        Crypto Rate: {crypto_rate:^7}|
+========================================================+
"""
