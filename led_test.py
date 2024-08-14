import digilent_system_functions as dig_open
try:
    print("Opening Digilent...")
    dwf, hdwf = dig_open.open()
except Exception as e:
    print(f"Failed to connect to ADP3450 for reason: {e}")
    print("Fatal error encountered. Ending process")
    
from digilent_led import lightLed
import time

@lightLed(0,"0")
def in1(dwf,hdwf):
    time.sleep(1)
    return 1,2

@lightLed(1,"2")
def in2(dwf,hdwf):
    time.sleep(2)
    return 3,4

@lightLed(2,"2")
def in3(dwf,hdwf):
    time.sleep(3)
    return 5,6

@lightLed(15,"main")
def main(dwf,hdwf):
    time.sleep(1)
    in1(dwf,hdwf)
    in2(dwf,hdwf)
    in3(dwf,hdwf)
    return 0,0
main(hdwf, dwf)
