# -*- coding: utf-8 -*-
from __future__ import absolute_import, division

import os
import sys
import time
from threading import Thread, Lock

from Crypto.Cipher import AES

from .python_queue import Queue
from .util import crypto_key, new_crypto_key, epoc_plus_crypto_key


class EmotivCrypto:
    def __init__(self, serial_number=None, is_research=False, verbose=False, force_epoc_mode=False,
                 force_old_crypto=False):
        """
        Performs decryption of packets received. Stores decrypted packets in a Queue for use.

        :param serial_number - The serial number to use for AES key generation.
        :param is_research - Is this a research edition headset? Also, EPOC+ uses this now.
        """
        # Where the encrypted data is Queued.
        self._encrypted_queue = Queue()
        # Where the decrypted data is Queued.
        self._decrypted_queue = Queue()
        self.force_epoc_mode = force_epoc_mode
        self.force_old_crypto = force_old_crypto
        # Running state.
        self.running = False
        self.verbose = verbose
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
        cipher = self.new_cipher(self.verbose)
        self.lock.acquire()
        while self.running:
            self.lock.release()
            # While the encrypted queue is not empty.
            while not self._encrypted_queue.empty():
                # Get some encrypted data off of the encrypted Queue.
                encrypted_task = self._encrypted_queue.get()
                # Make sure the encrypted data is not None.
                if encrypted_task is not None:
                    # Make sure the encrypted data is not empty.
                    if encrypted_task.data is not None:
                        if len(encrypted_task.data):
                            try:
                                # Python 3 compatibility
                                if sys.version_info >= (3, 0):
                                    # Convert to byte array or bytes like object.
                                    encrypted_data = bytes(encrypted_task.data, encoding='latin-1')
                                else:
                                    encrypted_data = encrypted_task.data
                                # Decrypt the encrypted data.
                                decrypted_data = decrypt_data(cipher, encrypted_data)
                                # Put the decrypted data onto the decrypted Queue.
                                encrypted_task.data = decrypted_data
                                self._decrypted_queue.put_nowait(encrypted_task)
                            except Exception as ex:
                                # Catch everything, and print exception.
                                # TODO: Make this more specific perhaps?
                                print(
                                    "Emotiv CryptoError ", sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2],
                                    " : ",
                                    ex)
            # If stop signal is received and all the pending data in the encrypted Queue is processed, stop running.
            self.lock.acquire()
            if self._stop_signal and self._encrypted_queue.empty():
                print("Crypto thread stopping.")
                self.running = False
            time.sleep(0.00001)
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

    def new_cipher(self, verbose=False):
        """
        Generates a new AES cipher from the serial number and headset version.
        :return: New AES cipher
        """
        if verbose:
            print("EmotivCrypto: Generating new AES cipher.")
        # Create initialization vector.
        iv = os.urandom(AES.block_size)
        # Make sure the serial number was set.
        if self.serial_number is None:
            raise ValueError("Serial number must not be None.")
        if verbose:
            print("EmotivCrypto: Serial Number - {serial_number}".format(serial_number=self.serial_number))
        # Create and return new AES class, using the serial number and headset version.
        if self.serial_number.startswith('UD2016') and not self.force_old_crypto:
            if self.force_epoc_mode:
                return AES.new(epoc_plus_crypto_key(self.serial_number), AES.MODE_ECB, iv)
            else:
                return AES.new(new_crypto_key(self.serial_number, self.verbose))
        else:
            return AES.new(crypto_key(self.serial_number, self.is_research, verbose), AES.MODE_ECB, iv)

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
