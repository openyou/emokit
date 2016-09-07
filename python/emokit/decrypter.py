# -*- coding: utf-8 -*-
from __future__ import absolute_import, division

import sys
from threading import Thread

from Crypto import Random
from Crypto.Cipher import AES
from emokit.util import crypto_key
from queue import Queue


class EmotivCrypto:
    def __init__(self, serial_number=None, is_research=False):
        self.encrypted_queue = Queue()
        self.decrypted_queue = Queue()
        self.running = True
        self.crypto_thread = Thread(target=self.do_crypto,
                                    kwargs={'serial_number': serial_number,
                                            'is_research': is_research},
                                    )
        self.crypto_thread.start()

    def do_crypto(self, serial_number, is_research):
        """
        Performs decryption of packets received. Stores decrypted packets in a Queue for use.
        """

        iv = Random.new().read(AES.block_size)
        if serial_number is None:
            raise ValueError("Serial number must not be None.")
        cipher = AES.new(crypto_key(serial_number, is_research), AES.MODE_ECB, iv)
        while self.running:
            while not self.encrypted_queue.empty():
                task = self.encrypted_queue.get()
                if len(task):
                    try:
                        if sys.version_info >= (3, 0):
                            task = bytes(task, encoding='latin-1')
                        data = cipher.decrypt(task[:16]) + cipher.decrypt(task[16:])
                        self.decrypted_queue.put_nowait(data)
                    except Exception as ex:
                        print("Emotiv CryptoError ", sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2], " : ",
                              ex)
