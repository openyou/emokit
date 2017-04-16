import struct

values = "153 16 6 126 203 125 175 125 210 128 196 125 176 125 198 125 29 0 149 115 206 125 247 125 216 125 230 133 126 127 8 149"
values = values.split()
print(values)
values = [int(value) for value in values]
print(values)
sensors_16_bits = {
    'counter': [0, 1, 2, 3, 4, 5, 6, 7],
    'type': [8, 9, 10, 11, 12, 13, 14, 15],

    'F3': [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
    'FC5': [32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47],
    'AF3': [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63],
    'F7': [64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79],
    'T7': [80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95],
    'P7': [96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
    'O1': [112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127],
    'QUALITY': [128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143],
    'O2': [144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159],
    'P8': [160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175],
    'T8': [176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191],
    'F8': [192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207],
    'AF4': [208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223],
    'FC6': [224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239],
    'F4': [240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255]
    # 'F3':      [24,   25,  26,  27,  28,  29,  30,  31,  16,  17,  18,  19,  20,  21,  22,  23],
    # 'FC5':     [40,   41,  42,  43,  44,  45,  46,  47,  32,  33,  34,  35,  36,  37,  38,  39],
    # 'AF3':     [56,   57,  58,  59,  60,  61,  62,  63,  48,  49,  50,  51,  52,  53,  54,  55],
    # 'F7':      [72,   73,  74,  75,  76,  77,  78,  79,  64,  65,  66,  67,  68,  69,  70,  71],
    # 'T7':      [88,   89,  90,  91,  92,  93,  94,  95,  80,  81,  82,  83,  84,  85,  86,  87],
    # 'P7':      [104, 105, 106, 107, 108, 109, 110, 111,  96,  97,  98,  99, 100, 101, 102, 103],
    # 'O1':      [120, 121, 122, 123, 124, 125, 126, 127, 112, 113, 114, 115, 116, 117, 118, 119],
    # 'QUALITY': [136, 137, 138, 139, 140, 141, 142, 143, 128, 129, 130, 131, 132, 133, 134, 135],
    # 'O2':      [152, 153, 154, 155, 156, 157, 158, 159, 144, 145, 146, 147, 148, 149, 150, 151],
    # 'P8':      [168, 169, 170, 171, 172, 173, 174, 175, 160, 161, 162, 163, 164, 165, 166, 167],
    # 'T8':      [184, 185, 186, 187, 188, 189, 190, 191, 176, 177, 178, 179, 180, 181, 182, 183],
    # 'F8':      [200, 201, 202, 203, 204, 205, 206, 207, 192, 193, 194, 195, 196, 197, 198, 199],
    # 'AF4':     [216, 217, 218, 219, 220, 221, 222, 223, 208, 209, 210, 211, 212, 213, 214, 215],
    # 'FC6':     [232, 233, 234, 235, 236, 237, 238, 239, 224, 225, 226, 227, 228, 229, 230, 231],
    # 'F4':      [248, 249, 250, 251, 252, 253, 254, 255, 240, 241, 242, 243, 244, 245, 246, 247]
}
pos = 0
print(pos)
max_values = len(values) * 8
print(max_values)
this_value = struct.unpack('h', ''.join([chr(values[2]), chr(values[3])]))
print(this_value[0] / 8)
print(this_value[0] / 8 + abs(this_value[0]) * 0.0013131313)
this_value = struct.unpack('h', ''.join([chr(values[3]), chr(values[2])]))
print(this_value[0] / 8)
print(this_value[0] / 8 + abs(this_value[0]) * 0.0013131313)
this_value = struct.unpack('h', ''.join([chr(values[4]), chr(values[5])]))
print(this_value[0] / 8)
print(this_value[0] / 8 + abs(this_value[0]) * 0.0013131313)
this_value = struct.unpack('h', ''.join([chr(values[6]), chr(values[7])]))
print(this_value[0] / 8)
print(this_value[0] / 8 + abs(this_value[0]) * 0.0013131313)
this_value = struct.unpack('h', ''.join([chr(values[8]), chr(values[9])]))
print(this_value[0] / 8)
print(this_value[0] / 8 + abs(this_value[0]) * 0.0013131313)
this_value = struct.unpack('h', ''.join([chr(values[10]), chr(values[11])]))
print(this_value[0] / 8)
print(this_value[0] / 8 + abs(this_value[0]) * 0.0013131313)
this_value = struct.unpack('h', ''.join([chr(values[12]), chr(values[13])]))
print(this_value[0] / 8)
print(this_value[0] / 8 + abs(this_value[0]) * 0.0013131313)
this_value = struct.unpack('h', ''.join([chr(values[14]), chr(values[15])]))
print(this_value[0] / 8)
print(this_value[0] / 8 + abs(this_value[0]) * 0.0013131313)
this_value = struct.unpack('h', ''.join([chr(values[16]), chr(values[17])]))
print(this_value[0] / 8)
print(this_value[0] / 8 + abs(this_value[0]) * 0.0013131313)
this_value = struct.unpack('h', ''.join([chr(values[18]), chr(values[19])]))
print(this_value[0] / 8)
print(this_value[0] / 8 + abs(this_value[0]) * 0.0013131313)
this_value = struct.unpack('h', ''.join([chr(values[20]), chr(values[21])]))
print(this_value[0] / 8)
print(this_value[0] / 8 + abs(this_value[0]) * 0.0013131313)
this_value = struct.unpack('h', ''.join([chr(values[22]), chr(values[23])]))
print(this_value[0] / 8)
print(abs(this_value[0]) / 8 + abs(this_value[0]) * 0.0013131313)
this_value = struct.unpack('h', ''.join([chr(values[24]), chr(values[25])]))
print(this_value[0] / 8)
print(abs(this_value[0]) / 8 + abs(this_value[0]) * 0.0013131313)
this_value = struct.unpack('h', ''.join([chr(values[26]), chr(values[27])]))
print(this_value[0] / 8)
print(abs(this_value[0]) / 8 + abs(this_value[0]) * 0.0013131313)
this_value = struct.unpack('h', ''.join([chr(values[28]), chr(values[29])]))
print(this_value[0] / 8)
print(abs(this_value[0]) / 8 + abs(this_value[0]) * 0.0013131313)
this_value = struct.unpack('h', ''.join([chr(values[30]), chr(values[31])]))
print(this_value[0] / 8)
print(abs(this_value[0]) / 8 + abs(this_value[0]) * 0.0013131313)
bits = []

level = 0
all_list = []
bit_list = []
print(bit_list)
for byte in values:
    level = 0
    bit_list = []
    for i in range(7, -1, -1):
        level <<= 1
        bit_list.append(byte >> i & 1)
        level |= byte >> i & 1
    print(level)
    print(bit_list)
    all_list.append(bit_list)

print()
print("Sensor values")
for sensor, bits in sensors_16_bits.items():
    if len(bits) == 16:
        level = 0
        bit_list = []
        value = 0
        for i in range(16):
            # print(i)
            level <<= 1
            b = (bits[i] // 8)
            o = bits[i] % 8
            # print("B: {}, O: {}".format(b, o))
            # print("Level before shift: {}".format(level))
            level <<= 1

            # print("Level after shift: {}".format(level))
            bit_list.append(values[b] >> o & 1)
            if i == 6:
                value = abs(level - 4096) * 0.13
                # level = level - 4096

            level |= values[b] >> o & 1
            # print("Level after add: {}".format(level))
        # print(len(bit_list))
        value += 4096
        value = str(value) + str(abs(level))
        # print(value)
        # print(struct.unpack('>d', ''.join(chr(char) for char in bit_list[:8])))
        # print(level)
        print(bit_list)
        # print(struct.unpack('>l', ''.join(chr(char) for char in bit_list[-8:])))
