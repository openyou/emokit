# -*- coding: utf-8 -*-
import struct
import sys
from datetime import datetime

from .battery import battery_values
from .sensors import sensor_bits, quality_bits, sensor_quality_bit, sensors_mapping
from .util import get_level, get_quality_scale

output_format = "Position {} - Char: {} SChar: {} UChar: {} Bool: {} Short: {} UShort: {} Int: {} UInt: {}\n" \
                "             Long: {} ULong: {} 64Long: {} U64Long: {} Float: {}\n" \
                "             Double: {} String: {} PString: {} Pointer: {}"


def try_unpack(byte_buffer, byte_format):
    return struct.unpack(byte_format, byte_buffer)


def values_at_position(byte_buffer, position=None, bits=None):
    position_values = []
    for b_format, length, value_type in formats:
        try:
            if bits is not None:
                unpacked = try_unpack(bits, b_format)
            else:
                if position is not None:
                    unpacked = try_unpack(byte_buffer[position:position + length], b_format)
        except:
            unpacked = "Error"
        print('Unpacked {}: {}'.format(value_type, unpacked))
        position_values.append(unpacked)
    print(output_format.format(position, *position_values))


#                                     C Type             | Python Type | Size  #
formats = [  # -------------------+-------------+------ #
    # ('x', 0),                       # Padding            | no value    | Null  #
    ('c', 1, "Character"),  # Char               | string      | 1     #
    ('b', 1, "Signed Char"),  # Signed Char        | integer     | 1     #
    ('B', 1, "Unsigned Char"),  # Unsigned Char      | integer     | 1     #
    ('?', 1, "Boolean"),  # Boolean            | boolean     | 1     #
    ('h', 2, "Short"),  # Short              | integer     | 2     #
    ('H', 2, "Unsigned Short"),  # Unsigned Short     | integer     | 2     #
    ('i', 4, "Int"),  # int                | integer     | 4     #
    ('I', 4, "UInt"),  # unsigned int       | integer     | 4     #
    ('l', 8, "Long"),  # long               | integer     | 8     #
    ('L', 8, "ULong"),  # unsigned long      | integer     | 8     #
    ('q', 8, "LongLong"),  # long long          | integer     | 8     #
    ('Q', 8, "ULongLong"),  # unsigned long long | integer     | 8     #
    ('f', 4, "Float"),  # float              | float       | 4     #
    ('d', 8, "Double"),  # double             | float       | 8     #
    ('s', 1, "String"),  # char[]             | string      | ?     #
    ('p', 1, "Pascal String"),  # char[]  (Pascal)   | string      | ?     #
    ('P', 1, "Pointer")  # void *             | integer     | ?     #
]


class EmotivExtraPacket(object):
    """
    Basic semantics for input bytes for ExtraPackets.
    """

    def __init__(self, data, timestamp=None, verbose=False):
        self.data = data
        if timestamp is None:
            self.timestamp = datetime.now()
        else:
            self.timestamp = timestamp
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


class EmotivNewPacket(object):
    """
    Basic semantics for input bytes for New Format packets.
    """

    def __init__(self, data, timestamp=None, verbose=False):
        """
        Initializes packet data. Sets the global battery value.
        Updates each sensor with current sensor value from the packet data.

        :param data - Values decrypted to be processed
        :param verbose - Flag for outputting debug values.
        """
        if timestamp is None:
            self.timestamp = datetime.now()
        else:
            self.timestamp = timestamp
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
        # if self.counter > 127:
        #     self.battery = battery_values[str(self.counter)]
        #     self.counter = 128
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
            value = get_level(self.raw_data, bits, verbose) - 8192
            setattr(self, name, (value,))
            self.sensors[name]['value'] = value
        self.quality_bit, self.quality_value = self.handle_quality(self.sensors, verbose)

    def handle_quality(self, sensors, verbose=False):
        """
        Sets the quality value for the sensor from the quality bits in the packet data.
        Optionally will return the value.

        :param sensors - reference to sensors dict in Emotiv class.
        :param verbose - Flag for outputting debug values.

        """
        current_contact_quality = get_level(self.raw_data, quality_bits, verbose)

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
        return 'EmotivPacket(counter={}, battery={}, gyro_x={}, gyro_y={}, gyro_z={})'.format(
            self.counter,
            self.battery,
            self.sensors['X']['value'],
            self.sensors['Y']['value'],
            self.sensors['Z']['value'])

    def get_quality_scale(self, old_model=False):
        return get_quality_scale(self.quality_value, old_model)


class EmotivOldPacket(object):
    """
    Basic semantics for input bytes for Old Format packets.
    """

    def __init__(self, data, timestamp=None, verbose=False):
        """
        Initializes packet data. Sets the global battery value.
        Updates each sensor with current sensor value from the packet data.

        :param data - Values decrypted to be processed
        :param verbose - Flag for outputting debug values.
        """
        if timestamp is None:
            self.timestamp = datetime.now()
        else:
            self.timestamp = timestamp
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
        print([ord(c) for c in data])
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
            value = get_level(self.raw_data, bits, verbose) - 8192
            setattr(self, name, (value,))
            self.sensors[name]['value'] = value
        self.quality_bit, self.quality_value = self.handle_quality(self.sensors, verbose)

    def handle_quality(self, sensors, verbose=False):
        """
        Sets the quality value for the sensor from the quality bits in the packet data.
        Optionally will return the value.

        :param sensors - reference to sensors dict in Emotiv class.
        :param verbose - Flag for outputting debug values.

        """
        current_contact_quality = get_level(self.raw_data, quality_bits, verbose)

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
        return 'EmotivPacket(counter={}, battery={}, gyro_x={}, gyro_y={}, gyro_z={})'.format(
            self.counter,
            self.battery,
            self.sensors['X']['value'],
            self.sensors['Y']['value'],
            self.sensors['Z']['value'])

    def get_quality_scale(self, old_model=False):
        return get_quality_scale(self.quality_value, old_model)
