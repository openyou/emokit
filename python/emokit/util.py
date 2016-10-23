# -*- coding: utf-8 -*-
import csv
import sys

if sys.version_info >= (3, 0):  # pragma: no cover
    unicode = str


def get_level(data, bits):
    """
    Returns sensor level value from data using sensor bit mask in micro volts (uV).
    """
    level = 0
    for i in range(13, -1, -1):
        level <<= 1
        b = (bits[i] // 8) + 1
        o = bits[i] % 8
        if sys.version_info >= (3, 0):
            level |= (data[b] >> o) & 1
        else:
            level |= (ord(data[b]) >> o) & 1
    return level


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


def crypto_key(serial_number, is_research=False):
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


def validate_data(data):
    if len(data) == 32:
        data.insert(0, 0)
    if len(data) != 33:
        return None
    return data


class EmotivWriter(object):
    """
    Write data from headset to output. CSV file for now.
    """

    def __init__(self, file_name, mode="csv", **kwargs):
        self.mode = mode
        if sys.version_info >= (3, 0):
            self.file = open(file_name, 'w', newline='')
        else:
            self.file = open(file_name, 'wb')
        if self.mode == "csv":
            self.writer = csv.writer(self.file, quoting=csv.QUOTE_ALL)
        else:
            self.writer = None

    def write_csv(self, data):
        if sys.version_info >= (3, 0):
            if type(data) == str:
                data = bytes(data, encoding='latin-1')
        else:
            if type(data) == str:
                data = [ord(char) for char in data]
        self.writer.writerow(data)

    def write(self, data):
        if self.mode == "csv":
            self.write_csv(data)

    def __exit__(self, exc_type, exc_value, traceback):
        if self.writer:
            self.writer.close()
        self.file.close()
