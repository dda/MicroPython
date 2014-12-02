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
    capacity=chipType
    address=addr
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

def test1():
  eep=SingleEEPROM(t24C512)
  print("Scanning...")
  print(i2c.scan())
  for i in range(0, 16):
    a=eep.writeEEPROM(i, i)
    print("Writing",i,"to",i)
  for i in range(0, 16):
    a=eep.readEEPROM(i)
    print(i,"=",a)
