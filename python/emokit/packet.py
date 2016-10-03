# -*- coding: utf-8 -*-
import sys

from emokit.battery import battery_values
from emokit.sensors import sensor_bits, quality_bits, sensor_quality_bit, sensors_mapping
from emokit.util import get_level


class EmotivPacket(object):
    """
    Basic semantics for input bytes.
    """

    def __init__(self, data):
        """
        Initializes packet data. Sets the global battery value.
        Updates each sensor with current sensor value from the packet data.

        :param data - Values decrypted to be processed
        """
        if sys.version_info >= (3, 0):
            self.raw_data = [int(bit) for bit in data]
            data = self.raw_data
            self.counter = data[0]
        else:
            if type(data[0]) == str and len(data[0]) > 1:
                self.raw_data = [chr(int(bit)) for bit in data]
                data = self.raw_data
            else:
                self.raw_data = data
            self.counter = ord(data[0])
        self.battery = None
        if self.counter > 127:
            self.battery = battery_values[str(self.counter)]
            self.counter = 128
        self.sync = self.counter == 0xe9
        self.sensors = sensors_mapping.copy()
        if sys.version_info >= (3, 0):
            self.sensors['X']['value'] = data[29] - 106
            self.sensors['Y']['value'] = data[30] - 105
            self.sensors['Z']['value'] = '?'
        else:
            self.sensors['X']['value'] = ord(data[29]) - 106
            self.sensors['Y']['value'] = ord(data[30]) - 105
            self.sensors['Z']['value'] = '?'

        for name, bits in sensor_bits.items():
            # Get Level for sensors subtract 8192 to get signed value
            value = get_level(self.raw_data, bits) - 8192
            setattr(self, name, (value,))
            self.sensors[name]['value'] = value
        self.quality_bit, self.quality_value = self.handle_quality(self.sensors)

    def handle_quality(self, sensors):
        """
        Sets the quality value for the sensor from the quality bits in the packet data.
        Optionally will return the value.

        :param sensors - reference to sensors dict in Emotiv class.

        """
        current_contact_quality = get_level(self.raw_data, quality_bits)

        if sys.version_info >= (3, 0):
            sensor_bit = self.raw_data[0]
        else:
            sensor_bit = ord(self.raw_data[0])
        if sensor_quality_bit.get(sensor_bit, False):
            sensors[sensor_quality_bit[sensor_bit]]['quality'] = current_contact_quality
        else:
            sensors['Unknown']['quality'] = current_contact_quality
            sensors['Unknown']['value'] = sensor_bit
        return sensor_bit, current_contact_quality

    def __repr__(self):
        """
        Returns custom string representation of the Emotiv Packet.
        """
        return 'EmotivPacket(counter=%i, battery=%i, gyro_x=%i, gyro_y=%i, gyro_z=%s)' % (
            self.counter,
            self.battery,
            self.sensors['X']['value'],
            self.sensors['Y']['value'],
            self.sensors['Z']['value'])

    def get_quality_scale(self, old_model=False):
        if old_model:
            return self.quality_value // 540
        else:
            return self.quality_value // 1024
