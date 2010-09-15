try:
	import pywinusb.hid as hid
	windows = True
except:
	import hid
	windows = False
from aes import rijndael
import struct

key = '\x31\x00\x35\x54\x38\x10\x37\x42\x31\x00\x35\x48\x38\x00\x37\x50'
devKey = '\x31\x00\x35\x48\x31\x00\x35\x54\x38\x10\x37\x42\x38\x00\x37\x50'
rijn = rijndael(key, 16)

channels = dict(
	L1=(9, 20), 
	L2=(5, 18), 
	L3=(31, 7), 
	L4=(2, -1), 
	L5=(2, -1), 
	L6=(28, -1), 
	L7=(23, -1), 
	
	R1=(0, -1), 
	R2=(0, -1), 
	R3=(0, -1), 
	R4=(28, -1), 
	R5=(17, -1), 
	R6=(0, -1), 
	R7=(0, -1), 
)

valid = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 31]
channels.update(dict((str(i), (i, -1)) for i in valid))

class EmotivPacket(object):
	def __init__(self, data):
		self.counter = ord(data[0])
		self.sync = self.counter == 0xe9
		self.gyroX = ord(data[29]) - 102
		self.gyroY = ord(data[30]) - 104
		#assert ord(data[15]) == 0
		
		for name, (i, j) in channels.items():
			if j != -1:
				iv, jv = data[i], data[j]
			else:
				iv, jv = data[i], '\0'
			level = struct.unpack('>h', iv + jv)[0]
			#level = struct.unpack('b', data[j])[0]
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
		if windows:
			self.setupWin(headsetId)
		else:
			self.setupPosix(headsetId)
		self.packets = []
	
	def setupWin(self, headsetId):
		filter = hid.HidDeviceFilter(vendor_id=0x21A1, product_name='Brain Waves')
		devices = filter.get_devices()
		assert len(devices) > headsetId
		self.device = devices[headsetId]
		self.device.open()
		def handle(data):
			assert data[0] == 0
			self.gotData(''.join(map(chr, data[1:])))
		self.device.set_raw_data_handler(handle)
	
	def setupPosix(self, headsetId):
		hid.hid_set_debug(HID_DEBUG_ALL)
		hid.hid_init()
		matcher = hid.HIDInterfaceMatcher()
		matcher.vendor_id  = 0x21a1
		matcher.product_id = 0x0001
		self.interface = interface = hid.hid_new_HIDInterface()
		if hid.hid_force_open(interface, 0, matcher, 1000) != HID_RET_SUCCESS:
			self.interface = interface = hid.hid_new_HIDInterface()
			if hid.hid_force_open(interface, 1, matcher, 1000) != HID_RET_SUCCESS:
				return False
		def reader():
			while True:
				ret, data = hid.hid_interrupt_read(interface, 0x81, 0x20, 0)
				if ret == 0:
					self.gotData(data)
		thread.start_new_thread(reader, ())
	
	def gotData(self, data):
		assert len(data) == 32
		data = rijn.decrypt(data[:16]) + rijn.decrypt(data[16:])
		self.packets.append(EmotivPacket(data))
	
	def dequeue(self):
		while len(self.packets):
			yield self.packets.pop(0)
	
	def close(self):
		if windows:
			self.device.close()
		else:
			hid.hid_close(self.interface)
