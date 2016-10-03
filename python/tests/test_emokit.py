# -*- encoding: utf-8 -*-

from emokit.emotiv import Emotiv


def test_emotiv_no_headset():
    try:
        emo_test = Emotiv()
    except Exception as ex:
        assert (ex.message == "Device not found")


def test_import_hidapi():
    hidapi_found = False
    try:
        import hidapi
        hidapi_found = True
    except Exception as ex:
        pass
    try:
        import pywinusb.hid
        hidapi_found = True
    except Exception as ex:
        pass
    assert hidapi_found
