# -*- coding: utf-8 -*-
from __future__ import absolute_import, division

import os
import sys
from threading import Thread, Lock

from Crypto.Cipher import AES
from emokit.util import crypto_key
from queue import Queue


class EmotivCrypto:
    def __init__(self, serial_number=None, is_research=False):
        """
        Performs decryption of packets received. Stores decrypted packets in a Queue for use.

        :param serial_number - The serial number to use for AES key generation.
        :param is_research - Is this a research edition headset? Also, EPOC+ uses this now.
        """
        # Where the encrypted data is Queued.
        self._encrypted_queue = Queue()
        # Where the decrypted data is Queued.
        self._decrypted_queue = Queue()
        # Running state.
        self.running = False
        # Stop signal tells the loop to stop after processing remaining tasks.
        self._stop_signal = False
        # The emotiv serial number.
        self.serial_number = serial_number
        # EPOC+ and research edition may need to have this set to True
        # TODO: Add functions that check variance in data received. If extreme toggle is_research and check again.
        #  If extreme again raise exception and shutdown emokit.
        self.is_research = is_research
        self.lock = Lock()
        self.thread = Thread(target=self.run)
        self.thread.setDaemon(True)

    def run(self):
        """
        The crypto loop. Decrypts data in encrypted Queue and puts it onto the decrypted Queue.

        Do not call explicitly, use .start() instead.
        """
        # Initialize AES
        cipher = self.new_cipher()
        self.lock.acquire()
        while self.running:
            self.lock.release()
            # While the encrypted queue is not empty.
            while not self._encrypted_queue.empty():
                # Get some encrypted data off of the encrypted Queue.
                encrypted_data = self._encrypted_queue.get()
                # Make sure the encrypted data is not None.
                if encrypted_data is not None:
                    # Make sure the encrypted data is not empty.
                    if len(encrypted_data):
                        try:
                            # Python 3 compatibility
                            if sys.version_info >= (3, 0):
                                # Convert to byte array or bytes like object.
                                encrypted_data = bytes(encrypted_data, encoding='latin-1')
                            # Decrypt the encrypted data.
                            decrypted_data = decrypt_data(cipher, encrypted_data)
                            # Put the decrypted data onto the decrypted Queue.
                            self._decrypted_queue.put_nowait(decrypted_data)
                        except Exception as ex:
                            # Catch everything, and print exception.
                            # TODO: Make this more specific perhaps?
                            print("Emotiv CryptoError ", sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2], " : ",
                                  ex)
            # If stop signal is received and all the pending data in the encrypted Queue is processed, stop running.
            self.lock.acquire()
            if self._stop_signal and self._encrypted_queue.empty():
                print("Crypto stopping.")
                self.running = False
        self.lock.release()

    def start(self):
        """
        Starts the crypto thread.
        """
        self.running = True
        self.thread.start()

    def stop(self):
        """
        Stops the crypto thread.
        """
        self.lock.acquire()
        self._stop_signal = True
        self.lock.release()
        self.thread.join(60)

    def new_cipher(self):
        """
        Generates a new AES cipher from the serial number and headset version.
        :return: New AES cipher
        """
        # Create initialization vector.
        iv = os.urandom(AES.block_size)
        # Make sure the serial number was set.
        if self.serial_number is None:
            raise ValueError("Serial number must not be None.")
        # Create and return new AES class, using the serial number and headset version.
        return AES.new(crypto_key(self.serial_number, self.is_research), AES.MODE_ECB, iv)

    def add_task(self, data):
        """
        Gives the crypto thread some encrypted data to decrypt, unless the crypto class' _stop_signal is True.
        :param data: Encrypted Data
        """
        # If the stop signal has not been set yet.
        if not self._stop_signal:
            # Add encrypted data to the encrypted Queue.
            self._encrypted_queue.put_nowait(data)

    def get_data(self):
        """
        Gives decrypted data from the crypto thread, if the queue isn't empty.
        :return: Decrypted data or None
        """
        # If the decrypted queue is not empty, get data from the Queue and return it.
        if not self._decrypted_queue.empty():
            return self._decrypted_queue.get_nowait()
        # Otherwise, return None.
        return None

    def data_ready(self):
        """
        :return: If queue is not empty, return True
        """
        if not self._decrypted_queue.empty():
            return True
        return False

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
            Do cleanup stuff.
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self.stop()


def decrypt_data(cipher, data):
    """
    Returns decrypted data.
    :param cipher: AES cipher
    :param data: Encrypted Data
    :return: Decrypted Data
    """
    return cipher.decrypt(data[:16]) + cipher.decrypt(data[16:])
