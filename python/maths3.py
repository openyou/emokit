import struct
import sys

for byte in chr(105):
    level = 0
    print(byte)
    bit_list = []
    for i in range(8):
        level <<= 1
        print(level)
        bit_list.append(chr(ord(byte) >> i & 1))
        print(bit_list)

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
