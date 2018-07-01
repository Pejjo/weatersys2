from smbus2 import SMBus, i2c_msg
import time

class SHT21:
    """Class to read temperature and humidity from SHT21.
    Ressources: 
      http://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/Humidity/Sensirion_Humidity_SHT21_Datasheet_V3.pdf
      https://github.com/jaques/sht21_python/blob/master/sht21.py
      Martin Steppuhn's code from http://www.emsystech.de/raspi-sht21"""

    #control constants
    _SOFTRESET = 0xFE
    _I2C_ADDRESS = 0x40
    _TRIGGER_TEMPERATURE_NO_HOLD = 0xF3
    _TRIGGER_HUMIDITY_NO_HOLD = 0xF5
    _READ_USER_REG = 0xE7

    def __init__(self, bus):
        """According to the datasheet the soft reset takes less than 15 ms."""
        self.classname="sht21"
        self.bus = bus
        self.bus.write_byte(self._I2C_ADDRESS, self._SOFTRESET)
        time.sleep(0.015)

    def read_temperature(self):    
        """Reads the temperature from the sensor.  Not that this call blocks
	for 250ms to allow the sensor to return the data"""
        data = []
        self.bus.write_byte(self._I2C_ADDRESS, self._TRIGGER_TEMPERATURE_NO_HOLD)
        time.sleep(0.250)

        read = i2c_msg.read(self._I2C_ADDRESS, 3)
        self.bus.i2c_rdwr(read)
        data=list(read)

	if (self._calculate_checksum(data,3)!=0):
            return(float('nan'))
        else:
            return self._get_temperature_from_buffer(data)
        

    def read_humidity(self):    
        """Reads the humidity from the sensor.  Not that this call blocks 
	for 250ms to allow the sensor to return the data"""
        data = []
        self.bus.write_byte(self._I2C_ADDRESS, self._TRIGGER_HUMIDITY_NO_HOLD)
        time.sleep(0.250)

        read = i2c_msg.read(self._I2C_ADDRESS, 3)
        self.bus.i2c_rdwr(read)
        data=list(read)
        if (self._calculate_checksum(data,3)!=0):
            return(float('nan'))
        else:
            return self._get_humidity_from_buffer(data)    

    def read_userreg(self):
        """Reads the user register"""
        data=self.bus.read_word_data(self._I2C_ADDRESS, self._READ_USER_REG)
        if(self._calculate_checksum([(data&0x00ff),(data>>8)],2)!=0):
            return -1
        else:
            return (data&0x00ff)


    def getSerialNumber(self):
        """Reads the serial number from the sensor."""

        serialNumber = []
	err=0
        write = i2c_msg.write(self._I2C_ADDRESS, [0xFA, 0x0F])
        read = i2c_msg.read(self._I2C_ADDRESS, 8)

        self.bus.i2c_rdwr(write, read)

        readlistb=list(read)
	err+=self._calculate_checksum(readlistb[0:2],2)
        err+=self._calculate_checksum(readlistb[2:4],2)
        err+=self._calculate_checksum(readlistb[4:6],2)
        err+=self._calculate_checksum(readlistb[6:8],2)

        write = i2c_msg.write(self._I2C_ADDRESS, [0xFC, 0xC9])
        read = i2c_msg.read(self._I2C_ADDRESS, 7)

        self.bus.i2c_rdwr(write, read)

        readlistac=list(read)

        err+=self._calculate_checksum(readlistac[0:3],3)
        err+=self._calculate_checksum(readlistac[3:6],3)


        serialNumber[0:2]=readlistac[3:5]
        serialNumber[2:5]=readlistb[0:8:2]
        serialNumber[6:8]=readlistac[0:2]


        if err!=0:
            serialNumber=[-1]

        return serialNumber

    def _calculate_checksum(self, data, number_of_bytes):
        """5.7 CRC Checksum using the polynomial given in the datasheet"""
        # CRC
        POLYNOMIAL = 0x131  # //P(x)=x^8+x^5+x^4+1 = 100110001
        crc = 0
        # calculates 8-Bit checksum with given polynomial
        for byteCtr in range(number_of_bytes):
            crc ^= (data[byteCtr])
            for bit in range(8, 0, -1):
                if crc & 0x80:
                    crc = (crc << 1) ^ POLYNOMIAL
                else:
                    crc = (crc << 1)
        return crc

    def _get_temperature_from_buffer(self, data):
        """This function reads the first two bytes of data and 
        returns the temperature in C by using the following function:        T = =46.82 + (172.72 * (ST/2^16))
        where ST is the value from the sensor
        """
        unadjusted = ((data[0] << 8) + data[1]) & 0xFFFC
        unadjusted *= 175.72
        unadjusted /= 1 << 16 # divide by 2^16
        unadjusted -= 46.85
        return unadjusted
    
    def _get_humidity_from_buffer(self, data):
        """This function reads the first two bytes of data and returns 
        the relative humidity in percent by using the following function:
        RH = -6 + (125 * (SRH / 2 ^16))
        where SRH is the value read from the sensor
        """
        unadjusted = ((data[0] << 8) + data[1]) & 0xFFFC
        unadjusted *= 125.0
#        print(unadjusted)
        unadjusted /= 1 << 16 # divide by 2^16
        unadjusted -= 6
        return unadjusted
        
    def get_digest(self):
        retval={'token':'', 'class':self.classname}

        retval['temp']=self.read_temperature()
        retval['humi']=self.read_humidity()
        retval['status']=self.read_userreg()
        sern=':'
	retval['serial']=sern.join(format(x,'02x') for x in self.getSerialNumber())
        return(retval)

    def close(self):
        """Closes the i2c connection"""
        self.bus.close()


    def __enter__(self):
        """used to enable python's with statement support"""
        return self
        

    def __exit__(self, type, value, traceback):
        """with support"""
        self.close()


if __name__ == "__main__":
    try:
        bus = SMBus(1)
        with SHT21(bus) as sht21:
            print "User: "
            print sht21.read_userreg()
            print "Temperature: %s"%sht21.read_temperature()
            print "Humidity: %s"%sht21.read_humidity()
            for x in sht21.getSerialNumber():
                print(hex(x))
#            while True:
#                print "Temperature: %s"%sht21.read_temperature()
#                print "Humidity: %s"%sht21.read_humidity()
#                time.sleep(1)
    except IOError, e:
        print e
        print 'Error creating connection to i2c.'
