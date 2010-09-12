import pywinusb.hid as hid
from aes import rijndael
import struct

key = '\x31\x00\x35\x54\x38\x10\x37\x42\x31\x00\x35\x48\x38\x00\x37\x50'
rijn = rijndael(key, 16)

channels = dict(
	F3=(1, 2), 
	AF3=(5, 6), # Right high byte
	F4=(28, 31), # Right high byte
	F7=(3, 4), # Right high byte
	FC5=(8, 7), 
	T7=(10, 9), 
	P7=(14, 13), 
	P8=(16, 17), # Right high byte
	O1=(12, 11), # Right high byte
	O2=(21, 20), 
	T8=(19, 18), 
	FC6=(22, 23), 
	AF4=(24, 25),  # Right high byte (?)
	F8=(26, 27), 
)

class EmotivPacket(object):
	def __init__(self, data):
		self.counter = ord(data[0])
		self.sync = self.counter == 0xe9
		self.gyroX = ord(data[29]) - 100
		self.gyroY = ord(data[30]) - 104
		#assert ord(data[15]) == 0
		
		for name, (i, j) in channels.items():
			level = struct.unpack('>h', data[i]+data[j])[0]
			strength = 4#(ord(data[j]) >> 3) & 1
			setattr(self, name, (level, strength))
	
	def __repr__(self):
		return 'EmotivPacket(counter=%i, gyroX=%i, gyroY=%i)' % (
				self.counter, 
				self.gyroX, 
				self.gyroY, 
			)

class Emotiv(object):
	def __init__(self, headsetId=0):
		filter = hid.HidDeviceFilter(vendor_id=0x21A1, product_name='Brain Waves')
		devices = filter.get_devices()
		assert len(devices) > headsetId
		self.device = devices[headsetId]
		self.device.open()
		self.device.set_raw_data_handler(self.gotData)
		self.packets = []
	
	def gotData(self, data):
		assert data[0] == 0 and len(data) == 33
		data = ''.join(map(chr, data[1:]))
		data = rijn.decrypt(data[:16]) + rijn.decrypt(data[16:])
		self.packets.append(EmotivPacket(data))
	
	def dequeue(self):
		while len(self.packets):
			yield self.packets.pop(0)
	
	def close(self):
		self.device.close()
