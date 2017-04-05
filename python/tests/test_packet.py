# -*- encoding: utf-8 -*-

from emokit.emotiv import EmotivPacket
from emokit.sensors import sensor_bits


def get_test_data():
    '''
    test_package.data
    
    | Sensor |   Value  | Quality  | Quality L1 | Quality L2 |
    +--------+----------+----------+------------+------------+
    |   F3   |    2     |    0     |  Nothing   |  Nothing   |
    |   FC5  |    81    |    0     |  Nothing   |  Nothing   |
    |   AF3  |   -100   |    0     |  Nothing   |  Nothing   |
    |   F7   |    75    |    0     |  Nothing   |  Nothing   |
    |   T7   |    68    |    0     |  Nothing   |  Nothing   |
    |   P7   |    84    |    0     |  Nothing   |  Nothing   |
    |   O1   |    80    |    0     |  Nothing   |  Nothing   |
    |   O2   |    54    |    0     |  Nothing   |  Nothing   |
    |   P8   |    55    |    0     |  Nothing   |  Nothing   |
    |   T8   |    55    |    0     |  Nothing   |  Nothing   |
    |   F8   |    16    |    0     |  Nothing   |  Nothing   |
    |   AF4  |    43    |    0     |  Nothing   |  Nothing   |
    |   FC6  |   128    |    0     |  Nothing   |  Nothing   |
    |   F4   |   1504   |    0     |  Nothing   |  Nothing   |
    |   X    |    21    |   N/A    |    N/A     |    N/A     |
    |   Y    |    22    |   N/A    |    N/A     |    N/A     |
    |   Z    |    ?     |   N/A    |    N/A     |    N/A     |
    |  Batt  |   None   |   N/A    |    N/A     |    N/A     |
    '''
    with open("test_package.data", "rb") as bin_data:
        data = bin_data.read()
        return data


def test_init():
    data = get_test_data()
    packet = EmotivPacket(data)
    for sensor in sensor_bits.keys():
        assert sensor in packet.sensors.keys()


def test_repr():
    data = get_test_data()
    packet = EmotivPacket(data)

    # tests #214
    assert packet.battery == None
    print(packet)