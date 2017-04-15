import struct

value = struct.unpack('>i', ''.join([chr(148), chr(125), chr(127), chr(125)][2::-2]))
print([value, ])
value = struct.pack('l', value[0])
print(value)
value = struct.unpack('d', value)
print(value)
"""
   F3   |   8514   |   1024   |    Okay    |    None    |
|   FC5  |   1298   |   1024   |    Okay    |    None    |
|   AF3  |  15618   |   1024   |    Okay    |    None    |
|   F7   |  24834   |   2048   |    None    |    None    |
|   T7   |  14658   |   3072   |    None    |    None    |
|   P7   |   3714   |   2048   |    None    |    None    |
|   O1   |  24060   |    0     |  Nothing   |  Nothing   |
|   O2   |  18818   |   1024   |    Okay    |  Nothing   |
|   P8   |  21244   |   2048   |    None    |    None    |
|   T8   |  31522   |   1024   |    Okay    |    None    |
|   F8   |  28690   |   3072   |    None    |    None    |
|   AF4  |  14786   |   1024   |    Okay    |    None    |
|   FC6  |   2274   |    0     |  Nothing   |  Nothing   |
|   F4   |  24674   |   1024   |    Okay    |    None    |
"""
