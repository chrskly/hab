
# Barometer

import smbus
import time

class barometer:

  def _write(self, data):
    for c in range(50):
      try:
        self.bus.write_byte(self.address, data)
      except Exception, e:
        continue
      return

  def _read(self, command, data):
    for c in range(50):
      try:
        value = self.bus.read_i2c_block_data(self.address, command, data)
      except Exception, e:
        continue
      return value

  def __init__(self):
    # we use rPi i2c bus 1
    self.bus = smbus.SMBus(1)
    # This is the adderess on the i2c box
    self.address = 0x77

    self._reset()
    self._calibrate()


  def _reset(self):
    #self.bus.write_byte(self.address, 0x1E)
    self._write(0x1E)
    time.sleep(0.5)

  def _calibrate(self):
    # Read pressure sensitivity
    #data = self.bus.read_i2c_block_data(self.address, 0xA2, 2)
    data = self._read(0xA2, 2)
    self.C1 = data[0] * 256 + data[1]
    # Read pressure offset
    #data = self.bus.read_i2c_block_data(self.address, 0xA4, 2)
    data = self._read(0xA4, 2)
    self.C2 = data[0] * 256 + data[1]
    # Read temperature coefficient of pressure sensitivity
    #data = self.bus.read_i2c_block_data(0x77, 0xA6, 2)
    data = self._read(0xA6, 2)
    self.C3 = data[0] * 256 + data[1]
    # Read temperature coefficient of pressure offset
    #data = self.bus.read_i2c_block_data(0x77, 0xA8, 2)
    data = self._read(0xA8, 2)
    self.C4 = data[0] * 256 + data[1]
    # Read reference temperature
    #data = self.bus.read_i2c_block_data(0x77, 0xAA, 2)
    data = self._read(0xAA, 2)
    self.C5 = data[0] * 256 + data[1]
    # Read temperature coefficient of the temperature
    #data = self.bus.read_i2c_block_data(0x77, 0xAC, 2)
    data = self._read(0xAC, 2)
    self.C6 = data[0] * 256 + data[1]

    # MS5611_01BXXX address, 0x77(118)
    #		0x40(64)	Pressure conversion(OSR = 256) command
    #self.bus.write_byte(0x77, 0x40)
    #time.sleep(0.5)

  def read_temperature_and_pressure(self):
    # Read digital pressure value
    # Read data back from 0x00(0), 3 bytes
    # D1 MSB2, D1 MSB1, D1 LSB
    value = self._read(0x00, 3)
    D1 = value[0] * 65536 + value[1] * 256 + value[2]

    # MS5611_01BXXX address, 0x77(118)
    #		0x50(64)	Temperature conversion(OSR = 256) command
    #self.bus.write_byte(0x77, 0x50)
    self._write(0x50)

    time.sleep(0.5)

    # Read digital temperature value
    # Read data back from 0x00(0), 3 bytes
    # D2 MSB2, D2 MSB1, D2 LSB
    #value = self.bus.read_i2c_block_data(0x77, 0x00, 3)
    value = self._read(0x00, 3)
    D2 = value[0] * 65536 + value[1] * 256 + value[2]

    dT = D2 - self.C5 * 256
    TEMP = 2000 + dT * self.C6 / 8388608
    OFF = self.C2 * 65536 + (self.C4 * dT) / 128
    SENS = self.C1 * 32768 + (self.C3 * dT ) / 256
    T2 = 0
    OFF2 = 0
    SENS2 = 0

    if TEMP >= 2000 :
        T2 = 0
        OFF2 = 0
        SENS2 = 0
    elif TEMP < 2000 :
        T2 = (dT * dT) / 2147483648
        OFF2 = 5 * ((TEMP - 2000) * (TEMP - 2000)) / 2
        SENS2 = 5 * ((TEMP - 2000) * (TEMP - 2000)) / 4
        if TEMP < -1500 :
            OFF2 = OFF2 + 7 * ((TEMP + 1500) * (TEMP + 1500))
            SENS2 = SENS2 + 11 * ((TEMP + 1500) * (TEMP + 1500)) / 2

    TEMP = TEMP - T2
    OFF = OFF - OFF2
    SENS = SENS - SENS2
    pressure = ((((D1 * SENS) / 2097152) - OFF) / 32768.0) / 100.0
    cTemp = TEMP / 100.0
    #fTemp = cTemp * 1.8 + 32
    print "pressure : %.4f mbar, temperature : %.4f C" % (pressure, cTemp)
    return (pressure, cTemp)



