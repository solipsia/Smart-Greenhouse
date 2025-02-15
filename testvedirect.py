
import time
import datetime
import random
from vedirect import Vedirect

def print_data_callback(packet):
    print(packet)

def waterdepthfromv(v):
    return(1)

def cleanfloat(f):
    try:
        number = float(f)
        return(number)
    except ValueError as e:
        return(0.0)

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

shuntport=findShuntPort()
print("shuntport",shuntport)
if shuntport is None:
    print("No Shunt found on USB")
mpptport=findMPPTPort()
print("mppt port",mpptport)
if mpptport is None:
    print("No MPPT found on USB")

smartshunt = Vedirect(shuntport, 60)
shuntpacket=smartshunt.read_data_single()
print("shunt",shuntpacket)
mppt = Vedirect(mpptport, 60)
mpptpacket=mppt.read_data_single()
print("mppt",mpptpacket)

print("-----------")

while True:
    shuntpacket=smartshunt.read_data_single()
    print(shuntpacket)

exit()

while True:
    #print("Reading VE.Direct")
    mpptpacket=mppt.read_data_single()
    
    panelvoltage=cleanfloat(mpptpacket.get("VPV"))/1000.0
    panelpower=mpptpacket.get("PPV")
    batteryvoltage=cleanfloat(mpptpacket.get("V"))/1000.0
    batterycurrent=cleanfloat(mpptpacket.get("I"))/1000.0
    batterypower=batterycurrent*batteryvoltage
    loadcurrent=cleanfloat(mpptpacket.get("IL"))/1000.0
    chargingstate=mpptpacket.get("CS")

    shuntpacket=smartshunt.read_data_single()

    print("MPPT-------------------")
    print(mpptpacket)
    print("VPV","Panel Voltage mV",mpptpacket.get("VPV"))
    print("PPV","Panel Power W",mpptpacket.get("PPV"))
    print("V","Battery Voltage mV",mpptpacket.get("V"))
    print("I","Battery Current mA",mpptpacket.get("I"))
    print(f"I Battery Current mA \033[91m{mpptpacket.get('I')}\033[0m")
    print("IL","Load Current mA",mpptpacket.get("IL"))
    print("H20","Yield Today 0.01 kWh",mpptpacket.get("H20"))
    print("H21","Max Power Today W",mpptpacket.get("H21"))
    print("H22","Yield Yesterday 0.01 kWh",mpptpacket.get("H22"))
    print("H23","Max Power Yesterday W",mpptpacket.get("H23"))
    print("ERR","Error",mpptpacket.get("ERR"))
    print("CS","State of Operation",mpptpacket.get("CS"))
    print("MPPT","Tracker operation mode",mpptpacket.get("MPPT"))
    print("SmartShunt-------------------")
    print(shuntpacket)
    print("SOC","% State of Charge",shuntpacket.get("SOC"))
    print("TTG","Time To Go (m)",shuntpacket.get("TTG"))
    print("V","Battery Voltage mV",shuntpacket.get("V"))
    print("I","Battery Current mA",shuntpacket.get("I"))
    print("H1","Depth of deepest discharge mAh",shuntpacket.get("H1"))
    print("H2","Depth of last discharge",shuntpacket.get("H2"))
    print("H3","Depth of ave discharge",shuntpacket.get("H3"))
    print("H9","Time since full charge (s)",shuntpacket.get("H9"))
    print("H18","Charged energy (0.01 kWh)",shuntpacket.get("H18"))
    #print("","",shuntpacket.get("")) 



    #time.sleep(1)