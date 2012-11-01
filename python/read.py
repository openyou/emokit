import time
import pywinusb.hid as hid

from aes import rijndael

key = '\x31\x00\x35\x54\x38\x10\x37\x42\x31\x00\x35\x48\x38\x00\x37\x50'
rijn = rijndael(key, 16)

iv = [0]*16
def decrypt(data):
	global iv
	dec = list(map(ord, rijn.decrypt(data[:16])))
	dec2 = list(map(ord, rijn.decrypt(data[16:])))
	data = list(map(ord, data))
	#dec2 = [data[i] ^ dec2[i] for i in range(16)]
	#dec = (dec[i] ^ iv[i] for i in range(16))
	#iv = map(ord, data[16:])
	return ''.join(map(chr, dec + dec2))

count = 0
last = 0
def sample_handler(data):
	global count, last
	assert data[0] == 0
	data = ''.join(map(chr, data[1:]))
	data = decrypt(data)
	#print ' '.join('%02x' % ord(c) for c in data)
	counter = ord(data[0])
	if last == 0x7F:
		print '%02x' % counter
		last = None
	else:
		last = counter
	count += 1

def bci_handler(data):
	print '!!!', `data`

def main(fn=None):
	if fn == None:
		devices = []
		try:
			for device in hid.find_all_hid_devices():
				if device.vendor_id != 0x21A1:
					continue
				if device.product_name == 'Brain Waves':
					devices.append(device)
					device.open()
					device.set_raw_data_handler(sample_handler)
				elif device.product_name == 'EPOC BCI':
					devices.append(device)
					device.open()
					device.set_raw_data_handler(bci_handler)
			while True:#device.is_plugged() and count < 1000:
				time.sleep(0.1)
		finally:
			for device in devices:
				device.close()
	else:
		for line in file(fn, 'r').readlines():
			data = [0] + [int(x, 16) for x in line.strip().split(' ')]
			sample_handler(data)

if __name__=='__main__':
	import sys
	main(*sys.argv[1:])
