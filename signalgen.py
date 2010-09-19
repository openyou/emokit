import sys

total = 0
counter = 0
def emit(lines):
	global counter
	global total
	total += 1
	print '%02X' % counter, 
	counter += 1
	if counter == 0x128:
		counter = 0xF5
	elif counter == 0xF6:
		counter = 0
	print ' '.join('%02X' % c for c in lines)

#for i in range(10):
#	emit([0xFF] * 31)
#	emit([0] * 31)
#
#for i in range(31):
#	for j in range(5):
#		emit([0] * i + [0xFF] + [0] * (30 - i))
#		emit([0] * 31)
#	for o in range(8):
#		emit([0] * i + [1 << o] + [0] * (30 - i))

for i in range(578):
	if i % 200 > 100:
		emit([0x80] + [0] * 30)
	else:
		emit([0] * 31)

print >>sys.stderr, total, 'samples ==', total / 128.0, 'seconds'
