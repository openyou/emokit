# -*- coding: utf-8 -*-
import platform
import struct
import sys

system_platform = platform.system()

if sys.version_info >= (3, 0):  # pragma: no cover
    unicode = str


def is_extra_data(data):
    if ord(data[1]) == 32:
        return True
    return False


def bits(bytes):
    """
    Helper function to get a tuple of the bits in a byte.
    :param byte: The byte from which to get the bits.
    :return: Tuple of bits in the byte param.
    """
    value = 0
    bits_list = []
    for byte in bytes:
        # print(byte)
        bit_list = []
        for i in range(8, -1, -1):
            binary = ''.join(bit_list)
        bits_list.append(int(binary, 2))
    # print()
    bit_list = []
    # print(''.join(map(chr, bin(bits_list[0] & bits_list[1]), 2)))
    for i in range(8, -1, -1):
        bit_list.append(str((ord(bin(bits_list[0] & bits_list[1])) >> i) & 1))
    return value


def get_level(data, bits, verbose=False):
    """
    Returns sensor level value from data using sensor bit mask in micro volts (uV).
    """
    # if verbose:
    #    return detailed_get_level(data, bits)
    level = 0
    bit_list = []
    for i in range(13, -1, -1):
        level <<= 1
        b = (bits[i] // 8) + 1
        o = bits[i] % 8
        bit_list.append(str(ord(data[b]) >> o & 1))
        if sys.version_info >= (3, 0):
            level |= (data[b] >> o) & 1
        else:
            level |= (ord(data[b]) >> o) & 1
            # print(level)
    # print(bit_list)
    # whole_bits = list(reversed(bit_list[0:7]))
    # whole_bits.append('0')
    # whole = int(''.join(whole_bits), 2)
    # print(whole)
    # print(whole / 0.051)
    # precision_bits = bit_list[7:14]
    # precision_bits.append('0')
    # precision_bits.append('0')
    # print(int(''.join(precision_bits), 2))
    # precision = int(''.join(precision_bits), 2)
    # print(precision / 0.51)
    # level = whole / 0.051
    # level += precision / 0.51
    # level = level * 2
    # print((level) * 0.5151515151)
    return level * 0.5151515151


def get_gyro(data, bits, verbose=False):
    """
    Returns sensor level value from data using sensor bit mask in micro volts (uV).
    """

    # if verbose:
    #    return detailed_get_level(data, bits)
    level = 42
    return level


def get_level_16(data, bits, verbose=False):
    """
    Returns sensor level value from data using sensor bit mask in micro volts (uV).
    """
    if verbose:
        return detailed_get_level(data, bits)
    level = 0
    for i in range(15, -1, -1):
        level <<= 1
        b = (bits[i] // 8) + 1
        o = bits[i] % 8
        if sys.version_info >= (3, 0):
            level |= (data[b] >> o) & 1
        else:
            level |= (ord(data[b]) >> o) & 1
    return level


def detailed_get_level(data, bits):
    """
    Returns sensor level value from data using sensor bit mask in micro volts (uV), with detailed logging.
    """
    level = 0
    print("Begin Sensor Level Calculation")
    print("Data: {}".format(data))
    print("Bits: {}".format(bits))
    for i in range(13, -1, -1):
        print("Iteration: {}".format(i))
        print("Level: {}".format(level))
        level <<= 1
        print("Shift left level by one by: {}".format(level))
        bit_at_index = bits[i]
        print("Bit Index: {}".format(bit_at_index))
        b = (bit_at_index // 8) + 1
        print("Floored(ABS or Integer) Quotient of bit and 8 plus one: {}".format(b))
        o = bit_at_index % 8
        print("Remainder of bit and 8: {}".format(o))
        if sys.version_info >= (3, 0):
            data_at_bit_index_divided_by_8_plus_one = data[b]
            print("Data at bit index divided by 8, plus one: {}".format(data_at_bit_index_divided_by_8_plus_one))
            data_shifted_right_by_remainder = data_at_bit_index_divided_by_8_plus_one >> o
            print("Data shifted right by remainder: {}".format(data_shifted_right_by_remainder))
            bitwise_of_data_shifted_right_and_one = data_shifted_right_by_remainder & 1
            print("Bitwise of data shifted right and one: {}".format(bitwise_of_data_shifted_right_and_one))
            level |= bitwise_of_data_shifted_right_and_one
            print("New level value with bitwise value added to level: {}".format(level))
        else:
            data_at_bit_index_divided_by_8_plus_one = ord(data[b])
            print("Data at bit index divided by 8, plus one: {}".format(data_at_bit_index_divided_by_8_plus_one))
            data_shifted_right_by_remainder = data_at_bit_index_divided_by_8_plus_one >> o
            print("Data shifted right by remainder: {}".format(data_shifted_right_by_remainder))
            bitwise_of_data_shifted_right_and_one = data_shifted_right_by_remainder & 1
            print("Bitwise of data shifted right and one: {}".format(bitwise_of_data_shifted_right_and_one))
            level |= bitwise_of_data_shifted_right_and_one
            print("New level value with bitwise value added to level: {}".format(level))
    print("Sensor level: {}".format(level))
    return level


def get_quality_scale(quality_value, old_model=False):
    if old_model:
        return quality_value // 540
    else:
        return quality_value // 1024


def get_quality_scale_level(quality_value, old_model=False):
    if old_model:
        return get_quality_level(quality_value // 540, old_model)
    else:
        return get_quality_level(quality_value // 1024, False)


def get_quality_level(quality_scale, old_model=False):
    if old_model:
        if quality_scale == 0:
            return "Nothing"
        if quality_scale == 1:
            return "Okay"
        if quality_scale == 2:
            return "Good"
        if 3 == quality_scale == 4:
            return "Excellent"
    else:
        if quality_scale == 0:
            return "Nothing"
        if 1 == quality_scale == 2:
            return "Okay"
        if 3 == quality_scale == 4:
            return "Good"
        if quality_scale > 4:
            return "Excellent"


def get_quality_scale_level_color(quality_value, old_model=False):
    if old_model:
        quality_value = quality_value // 520
    else:
        quality_value = quality_value // 1024
    return get_quality_color(quality_value, old_model)


old_color_scale = {
    0: (0, 0, 0),
    1: (255, 0, 0),
    2: (255, 255, 0),
    3: (0, 255, 0),
    4: (0, 255, 0)
}

new_color_scale = {
    0: (0, 0, 0),
    1: (255, 0, 0),
    2: (255, 0, 0),
    3: (255, 255, 0),
    4: (255, 255, 0)
}


def get_quality_color(quality_scale, old_model=False):
    if old_model:
        color = old_color_scale.get(quality_scale)
    else:
        color = new_color_scale.get(quality_scale, (0, 255, 0))
    return color


def is_old_model(serial_number):
    if "GM" in serial_number[-2:]:
        return False
    return True


def hid_enumerate(hidapi, platform):
    """
    Loops over all devices in the hidapi and attempts to locate the emotiv headset.

    Since hidapi ultimately uses the path there is no reason to get the vendor id or product id.

    Although, they may be useful in locating the device.

    :returns
        path - the path to the device
        serial_number - the serial number of the device
    """
    path = ""
    serial_number = ""
    devices = get_hid_devices[platform](hidapi)
    emotiv_devices = []
    for device in devices:
        if device_is_emotiv(device, platform):
            serial_number = device.serial_number
            path = device.path
            emotiv_devices.append(device)
    if platform != "Windows":
        return path, serial_number
    else:
        return emotiv_devices


def print_hid_device_info_win(device):
    print(unicode(device.vendor_name))
    print(unicode(device.product_name))


def print_hid_device_info_nix(device):
    print(unicode(device.manufacturer_string))
    print(unicode(device.product_string))
    print(device.path)


def print_hid_device_info_all(device):
    print(device.vendor_id)
    print(device.product_id)
    print(device.serial_number)
    print("-------------------------")


def hid_enumerate_nix(hidapi):
    return hidapi.hid_enumerate()


def hid_enumerate_win(hidapi):
    return hidapi.find_all_hid_devices()


def print_hid_enumerate(platform, hidapi):
    """
    Loops over all devices in the hidapi and attempts prints information.

    This is a fall back method that give the user information to give the developers when opening an issue.
    """
    devices = get_hid_devices[platform](hidapi)
    print("-------------------------")
    for device in devices:
        print_device_info[platform](device)
        print_hid_device_info_all(device)
    print("Please include this information if you open a new issue.")


get_hid_devices = {
    'Darwin': hid_enumerate_nix,
    'Linux': hid_enumerate_nix,
    'Windows': hid_enumerate_win
}

print_device_info = {
    'Darwin': print_hid_device_info_nix,
    'Linux': print_hid_device_info_nix,
    'Windows': print_hid_device_info_win
}


def new_crypto_key(serial_number, verbose=False):
    k = ['\0'] * 16
    k[0] = serial_number[-1]
    k[1] = serial_number[-2]
    k[2] = serial_number[-2]
    k[3] = serial_number[-3]
    k[4] = serial_number[-3]
    k[5] = serial_number[-3]
    k[6] = serial_number[-2]
    k[7] = serial_number[-4]
    k[8] = serial_number[-1]
    k[9] = serial_number[-4]
    k[10] = serial_number[-2]
    k[11] = serial_number[-2]
    k[12] = serial_number[-4]
    k[13] = serial_number[-4]
    k[14] = serial_number[-2]
    k[15] = serial_number[-1]
    if verbose:
        print("EmotivCrypto: Generated Crypto Key from Serial Number...\n"
              "   Serial Number - {serial_number} \n"
              "   AES KEY - {aes_key}".format(serial_number=serial_number, aes_key=k))

    return ''.join(k)


def epoc_plus_crypto_key(serial_number, verbose=False):
    k = ['\0'] * 16
    k[0] = serial_number[-1]
    k[1] = '\x00'
    k[2] = serial_number[-2]
    k[3] = '\x15'
    k[4] = serial_number[-3]
    k[5] = '\x00'
    k[6] = serial_number[-4]
    k[7] = '\x0C'
    k[8] = serial_number[-3]
    k[9] = '\x00'
    k[10] = serial_number[-2]
    k[11] = 'D'
    k[12] = serial_number[-1]
    k[13] = '\x00'
    k[14] = serial_number[-2]
    k[15] = 'X'
    if verbose:
        print("EmotivCrypto: Generated Crypto Key from Serial Number...\n"
              "   Serial Number - {serial_number} \n"
              "   AES KEY - {aes_key}".format(serial_number=serial_number, aes_key=k))

    return ''.join(k)


def crypto_key(serial_number, is_research=False, verbose=False):
    k = ['\0'] * 16
    k[0] = serial_number[-1]
    k[1] = '\0'
    k[2] = serial_number[-2]
    if is_research:
        k[3] = 'H'
        k[4] = serial_number[-1]
        k[5] = '\0'
        k[6] = serial_number[-2]
        k[7] = 'T'
        k[8] = serial_number[-3]
        k[9] = '\x10'
        k[10] = serial_number[-4]
        k[11] = 'B'
    else:
        k[3] = 'T'
        k[4] = serial_number[-3]
        k[5] = '\x10'
        k[6] = serial_number[-4]
        k[7] = 'B'
        k[8] = serial_number[-1]
        k[9] = '\0'
        k[10] = serial_number[-2]
        k[11] = 'H'
    k[12] = serial_number[-3]
    k[13] = '\0'
    k[14] = serial_number[-4]
    k[15] = 'P'
    if verbose:
        print("EmotivCrypto: Generated Crypto Key from Serial Number...\n"
              "   Serial Number - {serial_number} | is research - {is_research} \n"
              "   AES KEY - {aes_key}".format(serial_number=serial_number, is_research=is_research,
                                              aes_key=k))

    return ''.join(k)


def device_is_emotiv(device, platform):
    is_emotiv = False

    try:
        if platform != 'Windows':
            product_name = unicode(device.product_string)
            vendor_name = unicode(device.manufacturer_string)
        else:
            product_name = unicode(device.product_name)
            vendor_name = unicode(device.vendor_name)
        if u"emotiv" in vendor_name.lower():
            is_emotiv = True
        if u"emotiv" in product_name.lower():
            is_emotiv = True
        if u"epoc" in product_name.lower():
            is_emotiv = True
        if u"brain waves" in product_name.lower():
            is_emotiv = True
        if product_name == u'00000000000':
            is_emotiv = True
        if u"eeg signals" in product_name.lower():
            is_emotiv = True
    except Exception as ex:
        print("Emotiv IsEmotivError ", sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2], " : ", ex)
    return is_emotiv


def validate_data(data, new_format=False):
    if new_format:
        if len(data) == 64:
            data.insert(0, 0)
        if len(data) != 65:
            return None
    else:
        if len(data) == 32:
            data.insert(0, 0)
        if len(data) != 33:
            return None
    return data


def path_checker(user_output_path, emotiv_filename):
    has_slash = False
    if user_output_path[-1:] == '/' or user_output_path[-1:] == '\\':
        has_slash = True
    if has_slash:
        output_path = "{user_specified_output_path}{emotiv_filename}". \
            format(user_specified_output_path=user_output_path, emotiv_filename=emotiv_filename)
    else:
        if system_platform == "Windows":
            output_path = "{user_specified_output_path}\\{emotiv_filename}". \
                format(user_specified_output_path=user_output_path, emotiv_filename=emotiv_filename)
        else:
            output_path = "{user_specified_output_path}/{emotiv_filename}". \
                format(user_specified_output_path=user_output_path, emotiv_filename=emotiv_filename)
    return output_path


values_header = "Timestamp,F3 Value,F3 Quality,FC5 Value,FC5 Quality,F7 Value,F7 Quality,T7 Value,T7 Quality,P7 Value," \
                "P7 Quality,O1 Value,O1 Quality,O2 Value,O2 Quality,P8 Value,P8 Quality,T8 Value,T8 Quality,F8 Value,F8 Quality," \
                "AF4 Value,AF4 Quality,FC6 Value,FC6 Quality,F4 Value,F4 Quality,AF3 Value,AF3 Quality,X Value,Y Value,Z Value\n"


def bits_to_float(b):
    print('bits to float')
    print('b: {}'.format(b))
    print('bj: {}'.format("".join(b)))
    b = "".join(b)
    print('a: {}'.format(b))
    # s = struct.pack('L', b)
    # print("s: {}".format(s))
    return struct.unpack('>d', b)[0]


def writer_task_to_line(next_task):
    return "{timestamp},{f3_value},{f3_quality},{fc5_value},{fc5_quality},{f7_value}," \
           "{f7_quality},{t7_value},{t7_quality},{p7_value},{p7_quality},{o1_value}," \
           "{o1_quality},{o2_value},{o2_quality},{p8_value},{p8_quality},{t8_value}," \
           "{t8_quality},{f8_value},{f8_quality},{af4_value},{af4_quality},{fc6_value}," \
           "{fc6_quality},{f4_value},{f4_quality},{af3_value},{af3_quality},{x_value}," \
           "{y_value},{z_value}\n".format(
        timestamp=str(next_task.timestamp),
        f3_value=next_task.data['F3']['value'], f3_quality=next_task.data['F3']['quality'],
        fc5_value=next_task.data['FC5']['value'], fc5_quality=next_task.data['FC5']['quality'],
        f7_value=next_task.data['F7']['value'], f7_quality=next_task.data['F7']['quality'],
        t7_value=next_task.data['T7']['value'], t7_quality=next_task.data['T7']['quality'],
        p7_value=next_task.data['P7']['value'], p7_quality=next_task.data['P7']['quality'],
        o1_value=next_task.data['O1']['value'], o1_quality=next_task.data['O1']['quality'],
        o2_value=next_task.data['O2']['value'], o2_quality=next_task.data['O2']['quality'],
        p8_value=next_task.data['P8']['value'], p8_quality=next_task.data['P8']['quality'],
        t8_value=next_task.data['T8']['value'], t8_quality=next_task.data['T8']['quality'],
        f8_value=next_task.data['F8']['value'], f8_quality=next_task.data['F8']['quality'],
        af4_value=next_task.data['AF4']['value'], af4_quality=next_task.data['AF4']['quality'],
        fc6_value=next_task.data['FC6']['value'], fc6_quality=next_task.data['FC6']['quality'],
        f4_value=next_task.data['F4']['value'], f4_quality=next_task.data['F4']['quality'],
        af3_value=next_task.data['AF3']['value'], af3_quality=next_task.data['AF3']['quality'],
        x_value=next_task.data['X']['value'], y_value=next_task.data['Y']['value'],
        z_value=next_task.data['Z']['value'])