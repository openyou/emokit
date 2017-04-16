import struct

# print(struct.unpack('>i', ''.join([chr(242), chr(108)])))

bit_list = []

level = 0
(chr(108), 29)
for char, byte in [(chr(108), 29), (chr(253), 28)]:
    level = 0
    print(byte)
    bit_list = []
    for i in range(232, 240, 1):
        print(i)
        level <<= 1
        print(level)
        o = i % 8
        bit_list.append(chr(ord(char) >> o & 1))
        level += ord(char) >> o & 1
    print(bit_list)
    print(level)
    print(struct.unpack('>ii', ''.join(bit_list)))
    print(struct.unpack('>ff', ''.join(bit_list)))
    print(struct.unpack('hhhh', ''.join(bit_list)))
    print(struct.unpack('d', ''.join(bit_list)))
    print(struct.unpack('l', ''.join(bit_list)))
    bit_list = []
    level = 0

    for i in range(239, 231, -1):
        print(i)
        level <<= 1
        print(level)
        o = i % 8
        bit_list.append(chr(ord(char) >> o & 1))
        level += ord(char) >> o & 1
    print(bit_list)
    print(level)
    print(struct.unpack('ii', ''.join(bit_list)))
    print(struct.unpack('ff', ''.join(bit_list)))
    print(struct.unpack('hhhh', ''.join(bit_list)))
    print(struct.unpack('d', ''.join(bit_list)))
    print(struct.unpack('l', ''.join(bit_list)))
    bit_list = []
    for i in range(224, 232, 1):
        print(i)
        level <<= 1
        print(level)
        o = i % 8
        bit_list.append(chr(ord(char) >> o & 1))
        level += ord(char) >> o & 1
    print(bit_list)
    print(level)
    print(struct.unpack('ii', ''.join(bit_list)))
    print(struct.unpack('ff', ''.join(bit_list)))
    print(struct.unpack('hhhh', ''.join(bit_list)))
    print(struct.unpack('d', ''.join(bit_list)))
    print(struct.unpack('l', ''.join(bit_list)))
    level = 0

    bit_list = []
    for i in range(231, 223, -1):
        print(i)
        level <<= 1
        print(level)
        o = i % 8
        bit_list.append(chr(ord(char) >> o & 1))
        level += ord(char) >> o & 1
    print(bit_list)
    print(level)
    print(struct.unpack('ii', ''.join(bit_list)))
    print(struct.unpack('ff', ''.join(bit_list)))
    print(struct.unpack('hhhh', ''.join(bit_list)))
    print(struct.unpack('d', ''.join(bit_list)))
    print(struct.unpack('l', ''.join(bit_list)))
"""
    print(struct.unpack('ii', ''.join(bit_list)))

    print(struct.unpack('>ii', ''.join(bit_list)))

    print(struct.unpack('hhhh', ''.join(bit_list)))

    print(struct.unpack('>hhhh', ''.join(bit_list)))

    print(struct.unpack('ff', ''.join(bit_list)))

    print(struct.unpack('>ff', ''.join(bit_list)))

    print(struct.unpack('d', ''.join(bit_list)))

    print(struct.unpack('>d', ''.join(bit_list)))
    bit_list = []
    for i in range(8):
        level <<= 1
        print(level)
        bit_list.append(chr(ord(byte) >> i & 1))
        print(bit_list)
        if sys.version_info >= (3, 0):
            level |= (byte >> i * 8) & 1
        else:
            level |= (ord(chr(105)) >> i) & 1

    print(struct.unpack('ii', ''.join(bit_list)))

    values = struct.unpack('>ii', ''.join(bit_list))
    value_1 = struct.pack('<i', values[0])
    value_2 = struct.pack('<i', values[1])
    print(value_1)
    print('------------')
    print(struct.unpack('ff', value_1 + value_2))
    print(struct.unpack('hhhh', ''.join(bit_list)))

    print(struct.unpack('>hhhh', ''.join(bit_list)))

    print(struct.unpack('ff', ''.join(bit_list)))

    print(struct.unpack('>ff', ''.join(bit_list)))

    print(struct.unpack('d', ''.join(bit_list)))

    print(struct.unpack('>d', ''.join(bit_list)))

print(256 * 0.51)

value = struct.pack('>f', 2048.00)
print(struct.unpack('>hh', value))
print(struct.unpack('>l', value))
value_2 = struct.unpack('hh', value)
value_3 = struct.pack('i', value_2)
print(value_3)
"""
