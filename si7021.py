import time                     #import time library
import machine                  #micropython esp8266
from time import sleep_ms       #import sleep function
from machine import Pin, I2C    #connection to i2c pin of esp8266

#slave address for connection with host controller esp8266 (from datasheet)
SI7021_I2C_DEFAULT_ADDR = 64 #7-bit slave address (hex 0x40)

#initialising command codes (from datasheet) 
CMD_MEASURE_RELATIVE_HUMIDITY_HOLD_MASTER_MODE = b'\xE5'
CMD_MEASURE_RELATIVE_HUMIDITY = b'\xF5'
CMD_MEASURE_TEMPERATURE_HOLD_MASTER_MODE = b'\xE3'
CMD_MEASURE_TEMPERATURE = b'\xF3'
CMD_READ_TEMPERATURE_VALUE_FROM_PREVIOUS_RH_MEASUREMENT = b'\xE0'
CMD_RESET = b'\xFE'
CMD_WRITE_RH_T_USER_REGISTER_1 = b'\xE6'
CMD_READ_RH_T_USER_REGISTER_1 = b'\xE7'
CMD_WRITE_HEATER_CONTROL_REGISTER = b'\x51'
CMD_READ_HEATER_CONTROL_REGISTER = b'\x11'

class Si7021(object):
    
    #initialising sensor
    def __init__(self, i2c_addr = SI7021_I2C_DEFAULT_ADDR):
        self.addr = i2c_addr
        self.i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
   
    #read temperature from sensor
    def readTemp(self):
        self.i2c.writeto(SI7021_I2C_DEFAULT_ADDR,CMD_MEASURE_TEMPERATURE)   #command si7021 to measure temperature
        time.sleep_ms(20)                                                   #get readings every 20ms
        buf = bytearray(2)                                                  #create a 2 byte-array buffer
        self.i2c.readfrom_into(SI7021_I2C_DEFAULT_ADDR, buf)                #read data from address and put into buffer
        temp_code = buf[0]<< 8 | buf[1]                                     #generate 16-bit word return by si7021
        return (temp_code*175.72/65536) - 46.85                             #conversion of raw data into temperature celcius scale

    #read relative humidity from sensor
    def readRH(self):
        self.i2c.writeto(SI7021_I2C_DEFAULT_ADDR, CMD_MEASURE_RELATIVE_HUMIDITY)    #command si7021 to measure relative humidity
        time.sleep_ms(20)                                                           #get readings every 20ms                                  
        buf = bytearray(2)                                                          #create a 2 byte-array buffer                    
        self.i2c.readfrom_into(SI7021_I2C_DEFAULT_ADDR, buf)                        #read data from address and put into buffer
        humidity_code = buf[0]<< 8 | buf[1]                                         #generate 16-bit word return by si7021
        return  (humidity_code*125 /65536) - 6                                      #conversion of raw data into % scale
