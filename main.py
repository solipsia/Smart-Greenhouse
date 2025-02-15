
from PIL import Image, ImageDraw, ImageFont
#sudo pip install pillow  --break-system-packages
import time
import datetime
from collections import defaultdict
import subprocess
print("Importing MQTT")
import paho.mqtt.client as mqtt #sudo pip install paho-mqtt==2.1.0  --break-system-packages
#sudo pip install paho-mqtt==1.6.1  --break-system-packages
#sudo pip uninstall paho-mqtt   --break-system-packages
from smbus2 import SMBus
from bmp280 import BMP280 #sudo -H pip install bmp280 --break-system-packages

import adafruit_ads1x15.ads1115 as ADS #sudo pip3 install adafruit-circuitpython-ads1x15 --break-system-packages
from adafruit_ads1x15.analog_in import AnalogIn
import board
import busio
#import pizero_2relay as zerorelay  #now controlled directly from Home Assistant using remote_rpi_gpio
from vedirect import Vedirect

# Initialise the BMP280
bus = SMBus(1)
bmp280 = BMP280(i2c_dev=bus)
#pumprelay = zerorelay.relay("R1")
#lightrelay = zerorelay.relay("R2")
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
waterpressure = AnalogIn(ads, ADS.P0)
#waterCURRENT_INIT=0.0049 #// Current @ 0mm (uint: mA)
waterVZERO=0.5863 #v at zero water in tank
waterRANGE=5000 #// Depth measuring range 5000mm (for water)
waterVREF=5000 #// ADC's reference voltage on your Arduino,typical value:5000mV
waterDENSITY_WATER=1  #// Pure water density normalized to 1
data_points = defaultdict(list)

def print_data_callback(packet):
    print(packet)

def on_mqttconnect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("$SYS/#")

def on_mqttmessage(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def connectmqtt():
    try:
        mqttc.connect(mqtthostname, mqttbroker_port, 60)
        return True
    except:
        return False

def waterdepthfromv(v):
    #voltage at empty tank = 0.5863v
    waterCurrent = (waterpressure.voltage-waterVZERO) / 120.0 #Sense Resistor:120ohm
    waterdepth = (waterCurrent ) * (waterRANGE/ waterDENSITY_WATER / 16.0) #//Calculate depth from current readings
    #print(waterpressure.value, waterpressure.voltage, waterCurrent, waterdepth)
    return(waterdepth)

def cleanfloat(f):
    try:
        number = float(f)
        return(number)
    except ValueError as e:
        return(0.0)

def createoverlay(averages):
    image_size = (4608, 2592)
    font_size = 50
    text_color = "white"
    # Get the current date and time
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Attempt to load the specified font and size
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    image = Image.new("RGBA", image_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    # Calculate the text size and position
    text_size = draw.textbbox((0, 0), current_time, font=font)
    text_position = (10, image_size[1] - text_size[3] - 10)
    draw.text(text_position, current_time, font=font, fill=text_color)

    text_position = (10, image_size[1] - text_size[3]*2 - 10)
    #print(averages['temperature'])
    
    str = f"Temp {averages['temperature']:.1f}"
    #print(str) 
    draw.text(text_position, str, font=font, fill=text_color)


    # Save the image, overwrite if exists
    image_path = "/mnt/synology/public/greenhouse/sensoroverlay.png"
    image.save(image_path)
    image.close()
    #print(f"Overlay saved to {image_path}")

def read_sensors():
    try:
        waterdepth = waterdepthfromv(waterpressure.voltage)
        temperature = bmp280.get_temperature()
        pressure = bmp280.get_pressure()
        mpptpacket = mppt.read_data_single() # read via USB cable from MQTT device
        shuntpacket = smartshunt.read_data_single() # read via USB cable from MQTT device
        panelvoltage = cleanfloat(mpptpacket.get("VPV")) / 1000.0
        panelpower = cleanfloat(mpptpacket.get("PPV"))
        batteryvoltage = cleanfloat(mpptpacket.get("V")) / 1000.0
        batterycurrent = cleanfloat(mpptpacket.get("I")) / 1000.0
        batterypower = batterycurrent * batteryvoltage
        loadcurrent = cleanfloat(mpptpacket.get("IL")) / 1000.0
        chargingstate = mpptpacket.get("CS")
        maxpowertoday=cleanfloat(mpptpacket.get("H21"))
        maxpoweryesterday=cleanfloat(mpptpacket.get("H23"))
        yieldtoday=cleanfloat(mpptpacket.get("H20"))*10.0 # wH, original units are 0.01 kWh
        yieldyesterday=cleanfloat(mpptpacket.get("H22"))*10.0 #0.01 kWh
        # SmartShunt
        stateofcharge = cleanfloat(shuntpacket.get("SOC"))/10.0
        minsremaining = cleanfloat(shuntpacket.get("TTG"))
        minssincefull = cleanfloat(shuntpacket.get("H9"))/60.0
        chargedenergy = cleanfloat(shuntpacket.get("H18"))/0.01 #kWh
    except Exception  as e:
        print(f"Error reading Victron USB : {e}")
        print(shuntpacket)
        minssincefull=0.0
        chargedenergy=0.0
        stateofcharge=0.0
        minsremaining=0.0
    #print("V","Battery Voltage mV",shuntpacket.get("V"))
    #print("I","Battery Current mA",shuntpacket.get("I"))
    #print("H1","Depth of deepest discharge mAh",shuntpacket.get("H1"))
    #print("H2","Depth of last discharge",shuntpacket.get("H2"))
    #print("H3","Depth of ave discharge",shuntpacket.get("H3"))
    #print("H9","Time since full charge (s)",shuntpacket.get("H9"))
    #print("H18","Charged energy (0.01 kWh)",shuntpacket.get("H18"))

    #wifiinfo = subprocess.run(['wpa_cli', 'scan_results'], stdout=subprocess.PIPE).stdout.decode('ascii').split('\t')
    #signalstrength=cleanfloat(wifiinfo[2])

    #wifiinfo = subprocess.run(['wpa_cli', 'scan_results'], stdout=subprocess.PIPE).stdout.decode('ascii').split('\n')
    try:
        link_quality = subprocess.run(["iwconfig", "wlan0"], capture_output=True, text=True).stdout.split("Link Quality=")[1].split("/")[0]
    except Exception  as e:
        #at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        print(f"A link quality error occurred : {e}")
        link_quality = 0
    signalstrength=cleanfloat(link_quality)
    

 

    #print("VPV","Panel Voltage mV",vepacket.get("VPV"))
    #print("PPV","Panel Power W",vepacket.get("PPV"))
    #print("V","Battery Voltage mV",vepacket.get("V"))
    #print("I","Battery Current mA",vepacket.get("I"))
    #print(f"I Battery Current mA \033[91m{vepacket.get('I')}\033[0m")
    #print("IL","Load Current mA",vepacket.get("IL"))
    #print("H20","Yield Today 0.01 kWh",vepacket.get("H20"))
    #print("H21","Max Power Today W",vepacket.get("H21"))
    #print("H22","Yield Yesterday 0.01 kWh",vepacket.get("H22"))
    #print("H23","Max Power Yesterday W",vepacket.get("H23"))
    #print("ERR","Error",vepacket.get("ERR"))
    #print("CS","State of Operation",vepacket.get("CS"))
    #print("MPPT","Tracker operation mode",vepacket.get("MPPT"))

    data_points['waterdepth'].append(waterdepth)
    data_points['temperature'].append(temperature)
    data_points['pressure'].append(pressure)
    data_points['panelvoltage'].append(panelvoltage)
    data_points['panelpower'].append(panelpower)
    data_points['batteryvoltage'].append(batteryvoltage)
    data_points['batterycurrent'].append(batterycurrent)
    data_points['batterypower'].append(batterypower)
    data_points['loadcurrent'].append(loadcurrent)
    data_points['chargingstate'].append(chargingstate)
    data_points['maxpowertoday'].append(maxpowertoday)
    data_points['maxpoweryesterday'].append(maxpoweryesterday)
    data_points['yieldtoday'].append(yieldtoday)
    data_points['yieldyesterday'].append(yieldyesterday)
    data_points['signalstrength'].append(signalstrength)
    data_points['stateofcharge'].append(stateofcharge)
    data_points['minsremaining'].append(minsremaining)
    data_points['minssincefull'].append(minssincefull)
    data_points['chargedenergy'].append(chargedenergy)

def print_sensors():
    for key, values in data_points.items():
        print(key,values)

def calculate_averages():
    averages = {}
    for key, values in data_points.items():
        if key == 'chargingstate':
            # For non-numeric states, you might want to handle it differently
            averages[key] = max(set(values), key=values.count)  # Most common state
        else:
            #print(key)
            averages[key] = sum(values) / len(values) if values else 0
    return averages

def send_data_via_mqtt(averages):
    mqttc.publish("greenhouse/temperature", averages['temperature'])
    mqttc.publish("greenhouse/pressure", averages['pressure'])
    mqttc.publish("greenhouse/waterdepth", averages['waterdepth'])
    mqttc.publish("greenhouse/panelvoltage", averages['panelvoltage'])
    mqttc.publish("greenhouse/panelpower", averages['panelpower'])
    mqttc.publish("greenhouse/batteryvoltage", averages['batteryvoltage'])
    mqttc.publish("greenhouse/batterycurrent", averages['batterycurrent'])
    mqttc.publish("greenhouse/batterypower", averages['batterypower'])
    mqttc.publish("greenhouse/loadcurrent", averages['loadcurrent'])
    mqttc.publish("greenhouse/chargingstate", averages['chargingstate'])
    mqttc.publish("greenhouse/maxpowertoday", averages['maxpowertoday'])
    mqttc.publish("greenhouse/maxpoweryesterday", averages['maxpoweryesterday'])
    mqttc.publish("greenhouse/yieldtoday", averages['yieldtoday'])
    mqttc.publish("greenhouse/yieldyesterday", averages['yieldyesterday'])
    mqttc.publish("greenhouse/latest", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    mqttc.publish("greenhouse/signalstrength", averages['signalstrength'])
    mqttc.publish("greenhouse/stateofcharge", averages['stateofcharge'])
    mqttc.publish("greenhouse/minsremaining", averages['minsremaining'])
    mqttc.publish("greenhouse/minssincefull", averages['minssincefull'])
    mqttc.publish("greenhouse/chargedenergy", averages['chargedenergy'])

def findShuntPort():
    timeout=60
    shuntport=None
    port="/dev/ttyUSB0"
    testport = Vedirect(port, timeout)
    testpacket= testport.read_data_single()
    print(testpacket)
    shuntvalue1=testpacket.get("H18")
    shuntvalue2=testpacket.get("SOC")
    testport.close() 
    if shuntvalue1 is not None or shuntvalue2 is not None:
        shuntport=port

    port="/dev/ttyUSB1"
    testport = Vedirect(port, timeout)
    testpacket= testport.read_data_single()
    print(testpacket)
    shuntvalue1=testpacket.get("H18")
    shuntvalue2=testpacket.get("SOC")
    testport.close() 
    if shuntvalue1 is not None or shuntvalue2 is not None:
        shuntport=port
    print("shunt on port", shuntport)
    return shuntport

def findMPPTPort():
    mpptport=None
    port="/dev/ttyUSB0"
    testport = Vedirect(port, 60)
    testpacket= testport.read_data_single()
    mpptvalue1=testpacket.get("H20")
    mpptvalue2=testpacket.get("VPV")
    testport.close() 
    if mpptvalue1 is not None or mpptvalue2 is not None:
        mpptport=port

    port="/dev/ttyUSB1"
    testport = Vedirect(port, 60)
    testpacket= testport.read_data_single()
    mpptvalue1=testpacket.get("H20")
    mpptvalue2=testpacket.get("VPV")
    testport.close() 
    if mpptvalue1 is not None or mpptvalue2 is not None:
        mpptport=port
    print("MPPT on port", mpptport)
    return mpptport

mqtthostname = "192.168.1.193" #MQTT server on Home Assistant
mqttbroker_port = 1883 
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_mqttconnect
mqttc.on_message = on_mqttmessage
mqttc.username_pw_set("mqtt", "mqtt")

#temperature = bmp280.get_temperature()
#pressure = bmp280.get_pressure()
#print(f"{temperature:05.2f}deg {pressure:05.2f}hPa")
#pumprelay.on()
#pumprelay.off()
#lightrelay.on()
#lightrelay.off()
print(waterpressure.value, waterpressure.voltage)

shuntport=findShuntPort()
if shuntport is None:
    print("No Shunt found on USB")
    exit()
mpptport=findMPPTPort()
if mpptport is None:
    print("No MPPT found on USB")
    exit()

smartshunt = Vedirect(shuntport, 60)
mppt = Vedirect(mpptport, 60)

while not connectmqtt():
    print("error connecting to MQTT, retrying")

start_time = time.time()
mqttc.loop_start()
while True:
    read_sensors()
    #print_sensors()
    current_time = time.time()
    elapsed_time = current_time - start_time

    if elapsed_time >= 5:
        averages = calculate_averages()
        send_data_via_mqtt(averages)
        try:
            createoverlay(averages)
            #print("created overlay")
        except Exception  as e:
            print(f"Couldn't save overlay : {e}")
        # Clear data points for the next averaging period
        data_points = defaultdict(list)
        
        start_time = current_time

    time.sleep(0.1)
mqttc.loop_stop()