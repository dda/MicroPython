import pyb
import time
from pyb import I2C

LCD_ADDRESS = (0x7c>>1)
RGB_ADDRESS = (0xc4>>1)
# color define
WHITE = 0
RED = 1
GREEN = 2
BLUE = 3
REG_RED = 0x04
 # pwm2
REG_GREEN = 0x03
 # pwm1
REG_BLUE = 0x02
 # pwm0
REG_MODE1 = 0x00
REG_MODE2 = 0x01
REG_OUTPUT = 0x08
# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80
# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00
# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00
# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00
# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

i2c = I2C(1, I2C.MASTER)
i2c.init(I2C.MASTER, baudrate=400000)

class Grove_RGB_LCD():
  displayfunction=0
  displaycontrol=0
  displaymode=0
  initialized=0
  numlines=0
  currline=0
  color_define = [
    [255, 255, 255],
    [255, 0, 0],
    [0, 255, 0],
    [0, 0, 255]
  ]
  def i2c_send_byte(self, dta):
    data = bytearray(1)
    data[0]=dta
    i2c.send(data, addr=LCD_ADDRESS)
  def i2c_send_bytes(self, data):
    i2c.send(data, addr=LCD_ADDRESS)
  def __init__(self, cols, lines, dotsize=0):
    if (lines > 1):
      self.displayfunction = (self.displayfunction | LCD_2LINE)
    self.numlines = lines
    self.currline = 0
    # for some 1 line displays you can select a 10 pixel high font
    if ((dotsize != 0) & (lines == 1)):
      self.displayfunction = (self.displayfunction | LCD_5x10DOTS)
    time.sleep(.05)
    # Send function set command sequence
    self.command(LCD_FUNCTIONSET | self.displayfunction)
    time.sleep(0.0045)
    # wait more than 4.1ms
    # second try
    self.command(LCD_FUNCTIONSET | self.displayfunction)
    time.sleep(0.00150)
    # third go
    self.command(LCD_FUNCTIONSET | self.displayfunction)
    # finally, set # lines, font size, etc.
    self.command(LCD_FUNCTIONSET | self.displayfunction)
    # turn the display on with no cursor + blinking default
    self.displaycontrol = (LCD_DISPLAYON + LCD_CURSORON + LCD_BLINKON)
    self.display()
    # clear it off
    self.clear()
    # Initialize to default text direction (for romance languages)
    self.displaymode = (LCD_ENTRYLEFT + LCD_ENTRYSHIFTDECREMENT)
    # set the entry mode
    self.command(LCD_ENTRYMODESET + self.displaymode)
    # backlight init
    self.setReg(0, 0)
    self.setReg(1, 0)
    self.setReg(0x08, 0xAA)
    # all led control by pwm
    self.setColorWhite()
    ###### high level commands, for the user! #####
  def clear(self):
    self.command(LCD_CLEARDISPLAY)
    # clear display, set cursor position to zero
    time.sleep(0.002)
    # this command takes a long time!
  def home(self):
    self.command(LCD_RETURNHOME)
    # set cursor position to zero
    time.sleep(0.002)
    # this command takes a long time!
  def setCursor(self, col, row):
    if (row == 0):
      col = (col + 0x80)
    else:
      col = (col + 0xc0)
    dta = bytearray(2)
    dta[0]=0x80
    dta[1]=col
    self.i2c_send_bytes(dta)
  # Turn the display on/off (quickly)
  def noDisplay(self):
    self.displaycontrol = (self.displaycontrol & ~LCD_DISPLAYON)
    self.command(LCD_DISPLAYCONTROL + self.displaycontrol)
  def display(self):
    self.displaycontrol = (self.displaycontrol | LCD_DISPLAYON)
    self.command(LCD_DISPLAYCONTROL + self.displaycontrol)
  # Turns the underline cursor on/off
  def noCursor(self):
    self.displaycontrol = (self.displaycontrol & ~LCD_CURSORON)
    self.command(LCD_DISPLAYCONTROL + self.displaycontrol)
  def cursor(self):
    self.displaycontrol = (self.displaycontrol | LCD_CURSORON)
    self.command(LCD_DISPLAYCONTROL + self.displaycontrol)
  # Turn on and off the blinking cursor
  def noBlink(self):
    self.displaycontrol = (self.displaycontrol & ~LCD_BLINKON)
    self.command(LCD_DISPLAYCONTROL + self.displaycontrol)
  def blink(self):
    self.displaycontrol = (self.displaycontrol | LCD_BLINKON)
    self.command(LCD_DISPLAYCONTROL + self.displaycontrol)
  # These commands scroll the display without changing the RAM
  def scrollDisplayLeft(self):
    self.command(LCD_CURSORSHIFT | LCD_displayMOVE | LCD_MOVELEFT)
  def scrollDisplayRight(self):
    self.command(LCD_CURSORSHIFT | LCD_displayMOVE | LCD_MOVERIGHT)
  # This is for text that flows Left to Right
  def leftToRight(self):
    self.displaymode = (self.displaymode | LCD_ENTRYLEFT)
    self.command(LCD_ENTRYMODESET + self.displaymode)
  # This is for text that flows Right to Left
  def rightToLeft(self):
    self.displaymode = (self.displaymode & ~LCD_ENTRYLEFT)
    self.command(LCD_ENTRYMODESET + self.displaymode)
  # This will 'right justify' text from the cursor
  def autoscroll(self):
    self.displaymode = (self.displaymode | LCD_ENTRYSHIFTINCREMENT)
    self.command(LCD_ENTRYMODESET + self.displaymode)
  # This will 'left justify' text from the cursor
  def noAutoscroll(self):
    self.displaymode = (self.displaymode | ~LCD_ENTRYSHIFTINCREMENT)
    self.command(LCD_ENTRYMODESET | self.displaymode)
  # Allows us to fill the first 8 CGRAM locations
  # with custom characters
  def createChar(self, location, charmap):
    location &=0x7
    # we only have 8 locations 0-7
    self.command(LCD_SETCGRAMADDR + (location << 3))
    dta = bytearray(9)
    dta[0] = 0x40
    for i in range(0, 8):
      dta[i+1] = charmap[i]
    self.i2c_send_bytes(dta)
  ###### mid level commands, for sending data/cmds ######
  # send command
  def command(self, value):
    dta = bytearray(2)
    dta[0]=0x80
    dta[1]=value
    self.i2c_send_bytes(dta)
  # send data
  def write(self, value):
    dta = bytearray(2)
    dta[0]=0x40
    dta[1]=value
    self.i2c_send_bytes(dta)
    return 1
  # assume sucess
  def print(self, st):
    for i in st:
      self.write(ord(i))
  def setReg(self, addr, dta):
    data = bytearray(2)
    data[0]=addr
    data[1]=dta
    i2c.send(data, addr=RGB_ADDRESS)
  def setRGB(self, r, g, b):
    self.setReg(REG_RED, r)
    self.setReg(REG_GREEN, g)
    self.setReg(REG_BLUE, b)
  def setColor(self, color):
    if(color > 3):
      return
    self.setRGB(color_define[color][0], color_define[color][1], color_define[color][2])
  def setColorWhite(self):
    self.setRGB(255, 255, 255)
  def setColorAll(self):
    self.setRGB(0, 0, 0)
  def setPWM(self, color, pwm):
    self.setReg(color, pwm)

lcd=Grove_RGB_LCD(16, 2, 0)
lcd.home()
# Print a message to the LCD.
lcd.print("Hello world!")
heart = bytearray(0)
heart.append(0b01010)
heart.append(0b01110)
heart.append(0b11111)
heart.append(0b11111)
heart.append(0b01110)
heart.append(0b00100)
heart.append(0b00100)
heart.append(0b00000)
# create a new character
lcd.createChar(0, heart)
lcd.setCursor(1, 1)
lcd.write(0)
# createChar() doesn't seem to work for me
