import gevent
try:
  import pywinusb.hid as hid
  windows = True
except:
  windows = False

import sys, os
import logging
from gevent.queue import Queue
from gevent import Greenlet

#Do we really need this logger? Seems like a waste. Too much data to log anyhow.
logger = logging.getLogger("emotiv")

from subprocess import check_output
from Crypto.Cipher import AES
from Crypto import Random

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
tasks = Queue()

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
      #TODO: Fix this.
      strength = 4#(ord(data[j]) >> 3) & 1
      setattr(self, name, (level, strength))

  def __repr__(self):
    return 'EmotivPacket(counter=%i, battery=%i, gyroX=%i, gyroY=%i, F3=%i)' % (
      self.counter,
      self.battery,
      self.gyroX,
      self.gyroY,
      self.F3[0],
    )

class Emotiv(object):
  def __init__(self,displayOutput=True, headsetId=0, research_headset = True):
    self._goOn = True
    self.packets = []
    self.packetsRecieved = 0
    self.packetsProcessed = 0
    if windows:
      self.setupWin(headsetId) 
    else:
      self.setupPosix()

  def updateStdout(self):
    while self._goOn:
      if windows:
        os.system('cls')
      else:
        os.system('clear')
      #TODO: Make this more elegant?
      print "Total Packets: %i Packets Processed: %i" % (self.packetsRecieved, self.packetsProcessed)
      print "Current Sensor States"
      print "F3 Reading:  %i Strength: %i" % (self.lastPacket.F3[0], self.lastPacket.F3[1]) 
      print "FC6 Reading:  %i Strength: %i" % (self.lastPacket.FC6[0], self.lastPacket.FC6[1])
      print "P7 Reading:  %i Strength: %i" % (self.lastPacket.P7[0], self.lastPacket.P7[1])
      print "T8 Reading:  %i Strength: %i" % (self.lastPacket.T8[0], self.lastPacket.T8[1])
      print "F7 Reading:  %i Strength: %i" % (self.lastPacket.F7[0], self.lastPacket.F7[1])
      print "F8 Reading:  %i Strength: %i" % (self.lastPacket.F8[0], self.lastPacket.F8[1])
      print "T7 Reading:  %i Strength: %i" % (self.lastPacket.T7[0], self.lastPacket.T7[1])
      print "P8 Reading:  %i Strength: %i" % (self.lastPacket.P8[0], self.lastPacket.P8[1])
      print "AF4 Reading:  %i Strength: %i" % (self.lastPacket.AF4[0], self.lastPacket.AF4[1])
      print "F4 Reading:  %i Strength: %i" % (self.lastPacket.F4[0], self.lastPacket.F4[1])
      print "AF3 Reading:  %i Strength: %i" % (self.lastPacket.AF3[0], self.lastPacket.AF3[1])
      print "O2 Reading:  %i Strength: %i" % (self.lastPacket.O2[0], self.lastPacket.O2[1])
      print "O1 Reading:  %i Strength: %i" % (self.lastPacket.O1[0], self.lastPacket.O1[1])
      print "FC5 Reading:  %i Strength: %i" % (self.lastPacket.FC5[0], self.lastPacket.FC5[1])
      print "Gyro X: %i, Gyro Y: %i Battery: %i" % (self.lastPacket.gyroX, self.lastPacket.gyroY, self.lastPacket.battery)
      gevent.sleep(1)

  def getLinuxSetup(self):
      rawinputs = []
      for filename in os.listdir("/sys/class/hidraw"):
          realInputPath = check_output(["realpath", "/sys/class/hidraw/" + filename])
          sPaths = realInputPath.split('/')
          s = len(sPaths)
          s = s - 4
          i = 0
          path = ""
          while s > i:
              path = path + sPaths[i] + "/"
              i += 1
          rawinputs.append([path, filename])
      hiddevices = []
      #TODO: Add support for multiple USB sticks? make a bit more elegant
      for input in rawinputs:
        #print input[0] + " Device: " + input[1]
        try:
          with open(input[0] + "/manufacturer", 'r') as f:
            manufacturer = f.readline()
            f.close()
          if "Emotiv Systems Inc." in manufacturer:
            with open (input[0] + "/serial", 'r') as f:
              serial = f.readline().strip()
              f.close()
            print "Serial: " + serial + " Device: " + input[1]
            #Great we found it. But we need to use the second one...
            hidraw = input[1]
            id_hidraw = int(hidraw[-1])
            #The dev headset might use the first device, or maybe if more than one are connected they might. 
            id_hidraw += 1
            hidraw = "hidraw" + id_hidraw.__str__()
            print "Serial: " + serial + " Device: " + hidraw + " (Active)"
            return [serial, hidraw,]
        except IOError as e:
          print "Couldn't open file: %s" % e
  
  def setupWin(self, headsetId):
    filter = hid.HidDeviceFilter(vendor_id=0x21A1, product_name='Brain Waves')#This doesn't seem right... I'm not using windows though so w/e
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
  
  def setupPosix(self):
    _os_decryption = False
    if os.path.exists('/dev/eeg/raw'):
      #The decrpytion is handled by the Linux epoc daemon. We don't need to handle it there.
      _os_decryption = True
      self.hidraw = open("/dev/eeg/raw")
    else:
      setup = self.getLinuxSetup()
      self.serialNum = setup[0]
      #self.hidraw = open("/dev/hidraw4")
      if os.path.exists("/dev/" + setup[1]):
        self.hidraw = open("/dev/" + setup[1])
      else:
        self.hidraw = open("/dev/hidraw4")
      gevent.spawn(self.setupCrypto, self.serialNum)
      gevent.spawn(self.updateStdout)
    while self._goOn:
      try: 
        data = self.hidraw.read(32)
        if data != "":
          if _os_decryption:
            self.packets.append(EmotivPacket(data))
          else:
            #Queue it!
            self.packetsRecieved += 1
            tasks.put_nowait(data)
            gevent.sleep(0)
      except KeyboardInterrupt:
        self._goOn = False          
    return True
  
  def setupCrypto(self, sn):
    type = 0 #feature[5] 
    type &= 0xF
    type = 0
    #I believe type == True is for the Dev headset, I'm not using that. That's the point of this library in the first place I thought. 
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
    #The rijndael was slowing us down... Even using PyCrypto the old code was sloooow. Crypto needs to be handled in a seperate thread/microthread/greenlet.
    #Normal threads might have worked well(haven't tested), but I like gevent.
    #It also doesn't make sense to have more than one greenlet handling this as data needs to be in order anyhow. I guess you could assign an ID or something
    #to each packet but that seems like a waste also or is it? The ID might be useful if your using multiple headsets or usb sticks.
    #It should be noted that I am basing all this off of the performance of the Raspberry Pi. Other platforms might have run just fine.
    key = ''.join(k)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_ECB, iv)
    for i in k: print "0x%.02x " % (ord(i))
    while self._goOn:
      while not tasks.empty():
        task = tasks.get()
        data = cipher.decrypt(task[:16]) + cipher.decrypt(task[16:])
        self.lastPacket = EmotivPacket(data)
        self.packets.append(self.lastPacket)
        self.packetsProcessed += 1
        gevent.sleep(0)
      gevent.sleep(0)
  
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

if __name__ == "__main__":
  try:
    a = Emotiv()
  except KeyboardInterrupt:
    a.close()
    gevent.shutdown()
