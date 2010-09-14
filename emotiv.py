try:
	import pywinusb.hid as hid
	windows = True
except:
	windows = False

import sys
import logging
logger = logging.getLogger("emotiv")

from aes import rijndael
import struct

from threading import Thread

consumer_key = '\x31\x00\x35\x54\x38\x10\x37\x42\x31\x00\x35\x48\x38\x00\x37\x50'
research_key = '\x31\x00\x39\x54\x38\x10\x37\x42\x31\x00\x39\x48\x38\x00\x37\x50'

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
	def __init__(self, headsetId=0, research_headset = False):
		
		if research_headset:
			self.rijn = rijndael(research_key, 16)
		else:
			self.rijn = rijndael(consumer_key, 16)
		
		self._goOn = True
		
		if self.setupWin(headsetId) if windows else self.setupPosix(headsetId):
			logger.info("Fine, connected to the Emotiv receiver")
		else:
			logger.error("Unable to connect to the Emotiv receiver :-(")
			sys.exit(1)
			
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
		def reader():
			self.hidraw = open("/dev/hidraw1")
			while self._goOn:
				#ret, data = hid.hid_interrupt_read(interface, 0x81, 0x20, 0)
				data = self.hidraw.read(32)
				if data != "":
					self.gotData(data)
		self._dataReader = Thread(target=reader)
		self._dataReader.start()
		return True
	
	def gotData(self, data):
		assert len(data) == 32
		data = self.rijn.decrypt(data[:16]) + self.rijn.decrypt(data[16:])
		self.packets.append(EmotivPacket(data))
	
	def dequeue(self):
		while len(self.packets):
			yield self.packets.pop(0)
	
	def close(self):
		if windows:
			self.device.close()
		else:
			self._goOn = False
			self._dataReader.join()
			
			self.hidraw.close()
