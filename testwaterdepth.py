
import adafruit_ads1x15.ads1115 as ADS #sudo pip3 install adafruit-circuitpython-ads1x15 --break-system-packages
from adafruit_ads1x15.analog_in import AnalogIn
import board
import busio
import time
#import pizero_2relay as zerorelay  #now controlled directly from Home Assistant using remote_rpi_gpio
from vedirect import Vedirect

# Initialise the BMP280


i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
waterpressure = AnalogIn(ads, ADS.P0)


def waterdepthfromv(v):
    return(1)

waterdepth = waterdepthfromv(waterpressure.voltage)

#waterCURRENT_INIT=0.0049 #// Current @ 0mm (uint: mA)
waterVZERO=0.5863 #v at zero water in tank
waterRANGE=5000 #// Depth measuring range 5000mm (for water)
waterVREF=5000 #// ADC's reference voltage on your Arduino,typical value:5000mV
waterDENSITY_WATER=1  #// Pure water density normalized to 1

data=[]

while True:
    #dataVoltage = analogRead(ANALOG_PIN)/ 1024.0 * VREF;
    #waterCurrent = (waterpressure.voltage) / 120.0 #Sense Resistor:120ohm
    #waterdepth = (waterCurrent - waterCURRENT_INIT) * (waterRANGE/ waterDENSITY_WATER / 16.0) #//Calculate depth from current readings
    waterCurrent = (waterpressure.voltage-waterVZERO) / 120.0 #Sense Resistor:120ohm
    waterdepth = (waterCurrent ) * (waterRANGE/ waterDENSITY_WATER / 16.0) #//Calculate depth from current readings
    
    
    #print(round(waterpressure.value, 2), round(waterpressure.voltage, 2), round(waterCurrent, 2), round(waterdepth, 2))
    data.append(waterpressure.voltage)
    print(round(waterpressure.voltage, 2),  round(waterdepth, 2), sum(data) / len(data), len(data),waterpressure.voltage-waterVZERO )
    
    #time.sleep(0.1)
