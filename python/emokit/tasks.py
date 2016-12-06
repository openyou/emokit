# -*- coding: utf-8 -*-


class EmotivOutputTask(object):
    def __init__(self, received=False, decrypted=False, data=None):
        self.packet_received = received
        self.packet_decrypted = decrypted
        self.packet_data = data


class EmotivReaderTask(object):
    def __init__(self, data, timestamp):
        self.data = data
        self.timestamp = timestamp


class EmotivWriterTask(object):
    def __init__(self, data=None, encrypted=False, values=True, timestamp=None):
        self.is_encrypted = encrypted
        self.is_values = values
        self.data = data
        self.timestamp = timestamp
