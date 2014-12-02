import pyb
import time
from pyb import I2C

t24C512= 512 * 1024 / 8 #512 Kbits
t24C256= 256 * 1024 / 8 #256 Kbits
t24C128= 128 * 1024 / 8 #128 Kbits
t24C64= 64 * 1024 / 8 #64 Kbits

i2c = I2C(1, I2C.MASTER)
i2c.init(I2C.MASTER, baudrate=200000)

class SingleEEPROM():
  capacity=0
  address=0x50
  def __init__(self, chipType=t24C512, addr=0x50):
    self.capacity=int(chipType)
    self.address=int(addr)
  def writeEEPROM(self, eeaddress, value):
    data = bytearray(3)
    data[0]=eeaddress >> 8 #MSB
    data[1]=eeaddress & 0xFF #LSB
    data[2]=value
    i2c.send(data, addr=self.address)
    time.sleep(.05)
  def readEEPROM(self, eeaddress):
    data = bytearray(2)
    data[0]=eeaddress >> 8 #MSB
    data[1]=eeaddress & 0xFF #LSB
    i2c.send(data, addr=self.address)
    value=i2c.recv(1, self.address)
    return value[0]
  def selfTest(self):
    i=0
    while i<self.capacity:
      save=self.readEEPROM(i)
      out=pyb.rng() & 0xFF
      self.writeEEPROM(i, out)
      check=self.readEEPROM(i)
      if out==check:
        print(("00000000"+hex(i)[2:])[-8:],"passed")
      else:
        print(("00000000"+hex(i)[2:])[-8:],"failed")
        break
      i+=1024
    print("Capacity:",i,"vs",self.capacity,"declared.")

def test1():
  eep=SingleEEPROM(t24C512)
  print("Scanning...")
  scan=i2c.scan()
  if(scan==[]):
    print("Uh oh, Houston, we have a problem... No I2C device on the bus..."
    return
  eep.selfTest()
  for i in range(0, 16):
    a=eep.writeEEPROM(i, i)
    print("Writing",i,"to",i)
  for i in range(0, 16):
    a=eep.readEEPROM(i)
    print(i,"=",a)
