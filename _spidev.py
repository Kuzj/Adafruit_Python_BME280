import logging
import spidev

logging.basicConfig()

WRITE = 0x7F

class Device(object):
    def __init__(self, bus, dev):
        self._dev = spidev.SpiDev()
        self._dev.open(bus,dev)
        self._logger = logging.getLogger('Spi.Device.Bus.{0}.Dev.{1}'.format(bus, dev))
        #self._logger.setLevel(logging.DEBUG)

    def write8(self, register, value):
        """Write an 8-bit value to the specified register."""
        value = value & 0xFF
        #self._bus.write_byte_data(self._dev, register, value)
        to_send = []
        to_send.append(register&WRITE)
        to_send.append(value)
        self._dev.xfer2(to_send)
        self._logger.debug("Wrote 0x%02X to register 0x%02X",
                     value, register)

    def write16(self, register, value):
        """Write a 16-bit value to the specified register."""
        value = value & 0xFFFF
        #self._bus.write_word_data(self._dev, register, value)
        to_send = []
        to_send.append(register&WRITE)
        to_send.append(value >> 8)
        to_send.append(value&0xff)
        self._logger.debug("Wrote 0x%04X to register pair 0x%02X, 0x%02X",
                     value, register, register+1)

    def writeList(self, register, data):
        """Write bytes to the specified register."""
        #self._bus.write_i2c_block_data(self._dev, register, data)
        to_send = []
        to_send.append(register&WRITE)
        to_send.extend(data)
        self._logger.debug("Wrote to register 0x%02X: %s",
                     register, data)

    def readList(self, register, length):
        """Read a length number of bytes from the specified register.  Results
        will be returned as a bytearray."""
        #results = self._bus.read_i2c_block_data(self._dev, register, length)
        to_send = []
        to_send.append(register)
        to_send.extend([0]*length)
        results = self._dev.xfer2(to_send)[1:]
        self._logger.debug("Read the following from register 0x%02X: %s",
                     register, results)
        return results

    def readU8(self, register):
        """Read an unsigned byte from the specified register."""
        #result = self._bus.read_byte_data(self._dev, register) & 0xFF
        to_send = []
        to_send.append(register)
        to_send.append(0)
        result = self._dev.xfer2(to_send)[1]
        self._logger.debug("Read 0x%02X from register 0x%02X",
                     result, register)
        return result

    def readS8(self, register):
        """Read a signed byte from the specified register."""
        result = self.readU8(register)
        if result > 127:
            result -= 256
        return result

    def readU16(self, register, little_endian=True):
        """Read an unsigned 16-bit value from the specified register, with the
        specified endianness (default little endian, or least significant byte
        first)."""
        #result = self._bus.read_word_data(self._dev,register) & 0xFFFF
        to_send = []
        to_send.append(register)
        to_send.extend([0,0])
        reg,d1,d2 = self._dev.xfer2(to_send)
        result = ((d1<<8)+d2)
        self._logger.debug("Read 0x%04X from register pair 0x%02X, 0x%02X",
                           result, register, register+1)
        # Swap bytes if using big endian because read_word_data assumes little
        # endian on ARM (little endian) systems.
        if not little_endian:
            result = ((result << 8) & 0xFF00) + (result >> 8)
        return result

    def readS16(self, register, little_endian=True):
        """Read a signed 16-bit value from the specified register, with the
        specified endianness (default little endian, or least significant byte
        first)."""
        result = self.readU16(register, little_endian)
        if result > 32767:
            result -= 65536
        return result

    def readU16LE(self, register):
        """Read an unsigned 16-bit value from the specified register, in little
        endian byte order."""
        return self.readU16(register, little_endian=True)

    def readU16BE(self, register):
        """Read an unsigned 16-bit value from the specified register, in big
        endian byte order."""
        return self.readU16(register, little_endian=False)

    def readS16LE(self, register):
        """Read a signed 16-bit value from the specified register, in little
        endian byte order."""
        return self.readS16(register, little_endian=True)

    def readS16BE(self, register):
        """Read a signed 16-bit value from the specified register, in big
        endian byte order."""
        return self.readS16(register, little_endian=False)