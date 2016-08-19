import sys

from emokit.battery import battery_values
from emokit.sensors import sensor_bits, quality_bits, sensor_quality_bit
from emokit.util import get_level


class EmotivPacket(object):
    """
    Basic semantics for input bytes.
    """

    def __init__(self, data, sensors, model):
        """
        Initializes packet data. Sets the global battery value.
        Updates each sensor with current sensor value from the packet data.

        :param data - Values decrypted to be processed
        :param sensors - Reference to sensors dict in Emotiv class.
        :param model - Is headset old model? Old is relative now I guess.
        """
        self.raw_data = data
        if sys.version_info >= (3, 0):
            self.counter = data[0]
        else:
            self.counter = ord(data[0])
        self.battery = None
        if self.counter > 127:
            self.battery = battery_values[str(self.counter)]
            self.counter = 128
        self.sync = self.counter == 0xe9
        if sys.version_info >= (3, 0):
            self.gyro_x = data[29] - 106
            self.gyro_y = data[30] - 105
            self.gyro_z = '?'
        else:
            self.gyro_x = ord(data[29]) - 106
            self.gyro_y = ord(data[30]) - 105
            self.gyro_z = '?'
        sensors['X']['value'] = self.gyro_x
        sensors['Y']['value'] = self.gyro_y
        sensors['Z']['value'] = self.gyro_z
        for name, bits in sensor_bits.items():
            # Get Level for sensors subtract 8192 to get signed value
            value = get_level(self.raw_data, bits) - 8192
            setattr(self, name, (value,))
            sensors[name]['value'] = value
        self.old_model = model
        self.handle_quality(sensors)
        self.sensors = sensors

    def handle_quality(self, sensors):
        """
        Sets the quality value for the sensor from the quality bits in the packet data.
        Optionally will return the value.

        :param sensors - reference to sensors dict in Emotiv class.

        """
        if self.old_model:
            current_contact_quality = get_level(self.raw_data, quality_bits) // 540
        else:
            current_contact_quality = get_level(self.raw_data, quality_bits) // 1024

        if sys.version_info >= (3, 0):
            sensor_bit = self.raw_data[0]
        else:
            sensor_bit = ord(self.raw_data[0])
        if sensor_quality_bit.get(sensor_bit, False):
            sensors[sensor_quality_bit[sensor_bit]]['quality'] = current_contact_quality
        else:
            sensors['Unknown']['quality'] = current_contact_quality
            sensors['Unknown']['value'] = sensor_bit
        return current_contact_quality

    def __repr__(self):
        """
        Returns custom string representation of the Emotiv Packet.
        """
        return 'EmotivPacket(counter=%i, battery=%i, gyro_x=%i, gyro_y=%i, gyro_z=%s)' % (
            self.counter,
            self.battery,
            self.gyro_x,
            self.gyro_y,
            self.gyro_z)
