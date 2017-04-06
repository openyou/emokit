import itertools
import os
import random
import sys
from datetime import datetime, timedelta

from Crypto.Cipher import AES

filename = 'emotiv_encrypted_data_UD20160103001874_2017-04-05.17-21-32.384061.txt'
# filename = 'emotiv_encrypted_data_UD20160103001874_2017-04-05.17-42-23.292665.txt'
serial_number = 'UD20160103001874'
iv = os.urandom(AES.block_size)

# Probably need to expand this and probably use a serial brute force like approach, but meh
# Lets just see if it works.
charset = [char for char in serial_number[-4:]]
charset.extend(['\x00', '\x10', 'H', 'T', 'B', 'P'])
possible_combinations = len(charset) * 16 * 16


# Credit http://stackoverflow.com/questions/11747254/python-brute-force-algorithm
def next_value():
    return (''.join(candidate)
            for candidate in itertools.chain.from_iterable(itertools.product(charset, repeat=i)
                                                           for i in range(16, 16 + 1)))


def random_key(serial_number):
    keyset = [serial_number[-5], serial_number[-4], serial_number[-3], serial_number[-2], serial_number[-1]]
    # Probably need to expand this and probably use a serial brute force like approach, but meh
    # Lets just see if it works.
    emotiv_key_possiblities = ['\0', 'H', 'T', '\x10', 'B', 'P']
    keyset.extend(emotiv_key_possiblities)
    k = [random.choice(keyset) for value in range(0, 16)]
    return AES.new(''.join(k), AES.MODE_ECB, iv), k


def next_key(charset, previous_key):
    k = [random.choice(charset) for value in range(0, 16)]

    return AES.new(''.join(k), AES.MODE_ECB, iv), k


def original_key(serial_number, is_research):
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
    return AES.new(''.join(k), AES.MODE_ECB, iv), k


def counter_check(file_data, cipher, swap_data=False):
    counter_misses = 0
    counter_checks = 0
    last_counter = 0
    for line in file_data:
        data = line.split(',')[1:]

        data = [int(value, 2) for value in data]
        data = ''.join(map(chr, data))
        if not swap_data:
            decrypted = cipher.decrypt(data[:16]) + cipher.decrypt(data[16:])
        else:
            decrypted = cipher.decrypt(data[16:]) + cipher.decrypt(data[:16])
        counter = ord(decrypted[0])
        if counter != last_counter + 1:
            counter_misses += 1
        if counter_misses > 4 and counter_checks > 5:
            return False
        if counter_checks > 5 and counter_misses < 4:
            return True
        counter_checks += 1
        last_counter = counter


def unencrypted_counter_check(file_data, swap_data=False):
    counter_misses = 0
    counter_checks = 0
    last_counter = 0
    for line in file_data:
        data = line.split(',')[1:]
        data = [int(value, 2) for value in data]
        data = ''.join(map(chr, data))
        if not swap_data:
            decrypted = data[:16] + data[16:]
        else:
            decrypted = data[16:] + data[:16]
        counter = ord(decrypted[0])
        if counter != last_counter + 1:
            counter_misses += 1
        if counter_misses > 4 and counter_checks > 5:
            return False
        if counter_checks > 5 and counter_misses < 4:
            return True
        counter_checks += 1
        last_counter = counter


with open('{}'.format(filename), 'r') as encrypted_data:
    file_data = encrypted_data.readlines()
    found_looping = False
    i = 0
    # key = [charset[0], ] * 15
    # key.append('P')
    then = datetime.now()
    last_i = 1
    for key in next_value():
        cipher = AES.new(''.join(key), AES.MODE_ECB, iv)
        if counter_check(file_data, cipher):
            print("Correct Key Found! {}".format(key))
            sys.exit()
        i += 1
        now = datetime.now()
        if now - then > timedelta(minutes=1):
            print("{} out of {} combinations tried,  {} tries/minute, last key {}".format(i, possible_combinations,
                                                                                          i - last_i / 60, key))
            last_i = i
            i = 0
            then = now
    i = 0
    while not found_looping and i < 10000000:
        cipher, key = random_key(serial_number)
        if counter_check(file_data, cipher):
            print("Correct Key Found! {}".format(key))
            sys.exit()
        i += 1
    i = 0
    while not found_looping and i < 10000000:
        cipher, key = random_key(serial_number)
        if counter_check(file_data, cipher, True):
            print("Correct Key Found! Swap the data! {}".format(key))
            sys.exit()
        i += 1
    i = 0
    while not found_looping and i < 10000000:
        cipher, key = random_key(serial_number)
        if counter_check(file_data, cipher, True):
            print("Correct Key Found! Swap the data! {}".format(key))
            sys.exit()
        i += 1
    i = 0
    while not found_looping and i < 13:
        if unencrypted_counter_check(file_data, False):
            print("Not encrypted!")
            sys.exit()
        i += 1
    i = 0
    while not found_looping and i < 13:
        if unencrypted_counter_check(file_data, True):
            print("Not Encrypted! Swap the data!")
            sys.exit()
        i += 1
    print("Your script is terrible, try again...")
