import platform
import sys

if sys.version_info >= (3, 0):  # pragma: no cover
    unicode = str

system_platform = platform.system()
if system_platform == "Windows":
    import pywinusb.hid as hidapi
else:
    import hidapi

    hidapi.hid_init()


def hid_enumerate_nix():
    return hidapi.hid_enumerate()


def hid_enumerate_win():
    return hidapi.find_all_hid_devices()


def print_hid_enumerate(platform):
    """
    Loops over all devices in the hidapi and attempts prints information.

    This is a fall back method that gives the user information to give the developers when opening an issue.
    """
    devices = get_hid_devices[platform]()
    for device in devices:
        print("-------------------------")
        for key, value in device.__dict__.items():
            print("%s, %s" % (key, unicode(value)))
            # if not sys.version_info >= (3, 0):
            #    if type(value) == unicode or type(value) == str:
            #        print("%s, %s" % (key, value.encode(locale.getpreferredencoding())))
            #    else:
            #        print("%s, %s" % (key, str(value)))
            # else:
            #    if type(value) == unicode:
            #        print("%s, %s" % (key, value.encode(locale.getpreferredencoding())))
            #    else:
            #        print("%s, %s" % (key, unicode(value)))
    print("************************************************************")
    print("! Please include this information if you open a new issue. !")
    print("************************************************************")


get_hid_devices = {
    'Darwin': hid_enumerate_nix,
    'Linux': hid_enumerate_nix,
    'Windows': hid_enumerate_win
}

print(sys.version_info)
print(system_platform)

print_hid_enumerate(system_platform)
