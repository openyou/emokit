import itertools
import multiprocessing
import os
import random
import sys
import time
from datetime import datetime, timedelta

from Crypto.Cipher import AES

filename = 'emotiv_encrypted_data_UD20160103001874_2017-04-05.17-21-32.384061.csv'
# filename = 'emotiv_encrypted_data_UD20160103001874_2017-04-05.17-42-23.292665.csv'
# filename = 'emotiv_encrypted_data_SN201211150798GM_2017-04-05 17-51-45.771149.csv'
serial_number = 'SN201211150798GM'
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


# Make new crypto function match found key.
# ['1', '0', '\x00', '\x00', 'H', '0', '8', '\x10', 'T', '0', '0', '\x10', '7', 'T', '8', '1']
['B', '1', 'H', 'T', '1', 'P', '\x00', '4', '8', 'B', 'P', '7', 'T', '7', '1', 'P']


def test_key():
    return AES.new(''.join(['4', '\x00', '7', '\x15', '8', '\x00', '1', '\x0C', '8', '\x00', '7', 'D', '4', '\x00',
                            '7', 'X']),
                   AES.MODE_ECB, iv)


def new_crypto_key(serial_number, verbose=False):
    k = ['\0'] * 16
    'UD20160103001874'
    ['4', '7', '7', '8', '8', '8', '7', '1', '4', '1', '7', '7', '1', '1', '7', '4']
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
    return k


def reversed_original_key(serial_number, is_research):
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
    k.reverse()
    return AES.new(''.join(k), AES.MODE_ECB, iv), k


data_ouput = "{0:^4} {1:^4} {2:^4} {3:^4} {4:^4} {5:^4} {6:^4} {7:^4} {8:^4} {9:^4} {10:^4} {11:^4} {12:^4} {13:^4} " \
             "{14:^4} {15:^4} {16:^4} {17:^4} {18:^4} {19:^4} {20:^4} {21:^4} {22:^4} {23:^4} {24:^4} {25:^4} {26:^4} " \
             "{27:^4} {28:^4} {29:^4} {30:^4} {31:^4}"

def counter_check(file_data, cipher, swap_data=False):
    counter_misses = 0
    counter_checks = 0
    last_counter = 0
    lines = 258
    i = 0
    for line in file_data:
        i += 1
        if i > lines:
            continue
        data = line.split(',')[1:]
        data = [int(value, 2) for value in data]
        data = ''.join(map(chr, data))
        if not swap_data:
            decrypted = cipher.decrypt(data[:16]) + cipher.decrypt(data[16:])
        else:
            decrypted = cipher.decrypt(data[16:]) + cipher.decrypt(data[:16])
        counter = ord(decrypted[0])
        # (counter)
        strings_of_data = [ord(char) for char in decrypted]
        print(len(strings_of_data))
        print(data_ouput.format(*strings_of_data))
        # Uncomment this
        # print(counter)
        # if counter <= 127:
        #    if counter != last_counter + 1:
        #        counter_misses += 1
        # elif not (counter == 0 and last_counter > 127):
        #    counter_misses += 1
        # if counter_misses > 2 and counter_checks > 16:
        #    return False
        # if counter_checks > 16 and counter_misses < 2:
        #    return True
        counter_checks += 1
        last_counter = counter


def unencrypted_counter_check(file_data, swap_data=True):
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
    # Uncomment this after updating new_crypto_key to verify.
    # while not found_looping and i < 10000000:
    #    cipher = test_key()
    #    if counter_check(file_data, cipher, False):
    #        print("Verified!")
    #        sys.exit()
    #    i += 1
    # i = 0


def check_key(next_check):
    new_cipher = AES.new(''.join(next_check), AES.MODE_ECB, iv)
    if counter_check(file_data, new_cipher):
        print("Correct Key Found! {}".format(next_check))
    sys.exit()


pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
['4', '\x00', '7', 'H', '4', '\x00', '7', 'T', '8', '\x00', '1', 'B', '8', '\x00', '1', 'P']
key = ['4', '7', '7', '8', '8', '8', '7', '1', '4', '1', '7', '7', '1', '1', '7', '4']
# key = original_key(serial_number, False)
check_key(key)
print("?")
i = 0
last_i = 1
then = datetime.now()
for key in next_value():
    pool.apply_async(check_key, args=(key,))
    i += 1

    now = datetime.now()
    if now - then > timedelta(minutes=1):
        print("{} keys per second, last key {}".format(i - last_i / 60, key))
        last_i = i
        then = now
    time.sleep(0.00001)

i += 1
if False:
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
    print("Dumb luck didn't work, starting brute force.")

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

