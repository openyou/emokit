try:
  import pywinusb.hid as hid
  windows = True
except:
  windows = False

import sys, os
import logging
logger = logging.getLogger("emotiv")

from aes import rijndael
import struct

from threading import Thread

sensorBits = {
  'F3': [10, 11, 12, 13, 14, 15, 0, 1, 2, 3, 4, 5, 6, 7], 
  'FC6': [214, 215, 200, 201, 202, 203, 204, 205, 206, 207, 192, 193, 194, 195], 
  'P7': [84, 85, 86, 87, 72, 73, 74, 75, 76, 77, 78, 79, 64, 65], 
  'T8': [160, 161, 162, 163, 164, 165, 166, 167, 152, 153, 154, 155, 156, 157], 
  'F7': [48, 49, 50, 51, 52, 53, 54, 55, 40, 41, 42, 43, 44, 45], 
  'F8': [178, 179, 180, 181, 182, 183, 168, 169, 170, 171, 172, 173, 174, 175], 
  'T7': [66, 67, 68, 69, 70, 71, 56, 57, 58, 59, 60, 61, 62, 63], 
  'P8': [158, 159, 144, 145, 146, 147, 148, 149, 150, 151, 136, 137, 138, 139], 
  'AF4': [196, 197, 198, 199, 184, 185, 186, 187, 188, 189, 190, 191, 176, 177], 
  'F4': [216, 217, 218, 219, 220, 221, 222, 223, 208, 209, 210, 211, 212, 213], 
  'AF3': [46, 47, 32, 33, 34, 35, 36, 37, 38, 39, 24, 25, 26, 27], 
  'O2': [140, 141, 142, 143, 128, 129, 130, 131, 132, 133, 134, 135, 120, 121], 
  'O1': [102, 103, 88, 89, 90, 91, 92, 93, 94, 95, 80, 81, 82, 83], 
  'FC5': [28, 29, 30, 31, 16, 17, 18, 19, 20, 21, 22, 23, 8, 9]
}

g_battery = 0

class EmotivPacket(object):
  def __init__(self, data):
    global g_battery
    self.counter = ord(data[0])
    self.battery = g_battery
    if(self.counter > 127):
      self.battery = self.counter
      g_battery = self.battery
      self.counter = 128
    self.sync = self.counter == 0xe9
    self.gyroX = ord(data[29]) - 102
    self.gyroY = ord(data[30]) - 104
    #assert ord(data[15]) == 0
    
    for name, bits in sensorBits.items():
      level = 0
      for i in range(13, -1, -1):
        level <<= 1
        b, o = (bits[i] / 8) + 1, bits[i] % 8
        level |= (ord(data[b]) >> o) & 1
      strength = 4#(ord(data[j]) >> 3) & 1
      setattr(self, name, (level, strength))
  
  def __repr__(self):
    return 'EmotivPacket(counter=%i, battery=%i, gyroX=%i, gyroY=%i, F3=%i)' % (
      self.counter,
      self.battery,
      self.gyroX,
      self.gyroY,
      self.F3[0]
      )

class Emotiv(object):
  def __init__(self, headsetId=0, research_headset = True):
    
    self._goOn = True
    self.packets = []
    
    if self.setupWin(headsetId) if windows else self.setupPosix(headsetId):
      logger.info("Fine, connected to the Emotiv EPOC receiver")
    else:
      logger.error("Unable to connect to the Emotiv EPOC receiver :-(")
      sys.exit(1)
  
  def setupWin(self, headsetId):
    filter = hid.HidDeviceFilter(vendor_id=0x21A1, product_name='Brain Waves')
    devices = filter.get_devices()
    assert len(devices) > headsetId
    self.device = devices[headsetId]
    self.device.open()
    feature = self.device.find_feature_reports()[0]
    self.setupCrypto(self.device.serial_number, feature.get())

    def handle(data):
      assert data[0] == 0
      self.gotData(''.join(map(chr, data[1:])))
    self.device.set_raw_data_handler(handle)
    return True
  
  def setupPosix(self, headsetId):
    _os_decryption = False
    if os.path.exists('/dev/eeg/raw'):
      #The decrpytion is handled by the Linux epoc daemon. We don't need to handle it there.
      _os_decryption = True
      self.hidraw = open("/dev/eeg/raw")
    else:
      if os.path.exists("/dev/hidraw5"):
        self.hidraw = open("/dev/hidraw5")
      else:
        self.hidraw = open("/dev/hidraw5")
        
    while self._goOn:
      try: 
        data = self.hidraw.read(32)
        if data != "":
          if _os_decryption:
            self.packets.append(EmotivPacket(data))
          else:
            #Decrypt it!
            self.gotData(data)
      except KeyboardInterrupt:
        self._goOn = False          
    return True
  
  def setupCrypto(self, sn, feature):
    type = 0 #feature[5]
    type &= 0xF
    type = type == 0

    k = ['\0'] * 16
    k[0] = sn[-1]
    k[1] = '\0'
    k[2] = sn[-2]
    if type:
      k[3] = 'H'
      k[4] = sn[-1]
      k[5] = '\0'
      k[6] = sn[-2]
      k[7] = 'T'
      k[8] = sn[-3]
      k[9] = '\x10'
      k[10] = sn[-4]
      k[11] = 'B'
    else:
      k[3] = 'T'
      k[4] = sn[-3]
      k[5] = '\x10'
      k[6] = sn[-4]
      k[7] = 'B'
      k[8] = sn[-1]
      k[9] = '\0'
      k[10] = sn[-2]
      k[11] = 'H'
    
    k[12] = sn[-3]
    k[13] = '\0'
    k[14] = sn[-4]
    k[15] = 'P'
    self.rijn = rijndael(''.join(k), 16)
    for i in k: print "0x%.02x " % (ord(i))


  def gotData(self, data):
    assert len(data) == 32
    data = self.rijn.decrypt(data[:16]) + self.rijn.decrypt(data[16:])
    print EmotivPacket(data)
    
  
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


def main():
  try:
    e = Emotiv()
  except KeyboardInterrupt:
    e.close()
  return 0

if __name__ == "__main__":
  sys.exit(main())