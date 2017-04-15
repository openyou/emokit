import struct

value = struct.pack('>hh', 125, 148)
print([value, ])
print([struct.unpack('f', value)])


def bits(bytes):
    print("+++++++++++++++++++")
    """
    Helper function to get a tuple of the bits in a byte.
    :param byte: The byte from which to get the bits.
    :return: Tuple of bits in the byte param.
    """
    value = 0
    bits_list = []
    packed = []
    for byte in bytes:
        level = 0
        print(byte)
        bit_list = []
        for i in range(8):
            level <<= 1
            bit_list.append(byte >> i & 1)
            level |= byte >> i & 1
            print(level)
        print(bit_list)
        value += level
        print(value)
    packed.append(struct.unpack('f', struct.pack('>l', value)))

    print(packed)
    print("math")
    # print(packed[0][0] + packed[1][0])
    # print(packed[0][1] / packed[0][0] * 16)
    # print(packed[0][0] * packed[0][1] * packed[1][0] * packed[1][1] * 16)
    # print(packed[0] / packed[1])
    # print((packed[0] / packed[1]) / 128)
    # print((packed[0] / packed[1]) / 256)
    # print(packed[0] * packed[1])
    # print("flopped")
    # print(packed[1] + packed[0])
    # print((packed[1] + packed[0]) / 128)
    # print(packed[1] / packed[0])
    # print((packed[1] / packed[0]) / 128)
    # print((packed[1] / packed[0]) / 256)
    # print(packed[1] * packed[0])
    # print("mangled")
    # mange = packed[1] + packed[0]

    # added_mod = struct.pack('l', mange)
    # print([added_mod, ])
    # print(struct.unpack('d', added_mod))

    print("------------------")
    return value


b = bits([227, 125, ])
b = bits([6, 126, ])
print(b)
'4080.00389105'
'4080.99610901'
'4335.0000152'
'4335.003891'
'4335.99609375'


def bits_to_float(b):
    print('bits to float')
    print('b: {}'.format(b))
    print('bj: {}'.format("".join(b)))
    b = "".join(b)
    print('a: {}'.format(b))
    # s = struct.pack('L', b)
    # print("s: {}".format(s))
    return struct.unpack('>d', b)[0]
