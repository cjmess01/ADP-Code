from ctypes import c_int, c_ulong, byref
import time 

def turnOnLight(hdwf, dwf, dio):
    # Create new output map. Output doesn't turn on LED, but allows them to be on and off
    enabled_map = c_int()
    dwf.FDwfDigitalIOOutputEnableGet(hdwf, byref(enabled_map))
    enable_addition_map = c_int(2**dio)
    enable_mask = enabled_map.value | enable_addition_map.value
    dwf.FDwfDigitalIOOutputEnableSet(hdwf, c_int(enable_mask))

    high_low_map = c_int()
    dwf.FDwfDigitalIOOutputGet(hdwf, byref(high_low_map))
    addition_map = c_int(2**dio)
    new_map = high_low_map.value | addition_map.value
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(new_map)) # DIO-1 high

    dwf.FDwfDigitalIOConfigure(hdwf)

    time.sleep(.1)


def turnOffLight(hdwf, dwf, dio):

    enabled_map = c_int()
    dwf.FDwfDigitalIOOutputEnableGet(hdwf, byref(enabled_map))
    enable_subtract_map = c_int(0xffff - (2**dio))
    enable_mask = enabled_map.value & enable_subtract_map.value
    dwf.FDwfDigitalIOOutputEnableSet(hdwf, c_int(enable_mask))

    high_low_map = c_int()
    dwf.FDwfDigitalIOOutputGet(hdwf, byref(high_low_map))
    subtract_map = c_int(0xffff - (2**dio))
    new_map = high_low_map.value & subtract_map.value
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(new_map)) # DIO-1 high

    dwf.FDwfDigitalIOConfigure(hdwf)

    time.sleep(.1)

def forceLightsOff(hdwf, dwf):
    print("Fatal error occured. Blinking error light for 20 seconds and shutting off others")
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x0000)) 
    dwf.FDwfDigitalIOOutputEnableSet(hdwf, c_int(0x0008))
    dwf.FDwfDigitalIOConfigure(hdwf)
    for i in range(10):
        dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x0008)) 
        dwf.FDwfDigitalIOConfigure(hdwf)
        time.sleep(1)
        dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x0000)) 
        dwf.FDwfDigitalIOConfigure(hdwf)
        time.sleep(1)

    return



# DIO 0 is 0. DIO 1 is 1. Etc.
def lightLed(dio : int, purpose : str):

    def decorator(func):
        def inner(*argv, **kwargs):
            try:
                turnOnLight(argv[0], argv[1], dio)
                buffer1, buffer2 = func(*argv)
                turnOffLight(argv[0], argv[1], dio)
                return buffer1, buffer2
            except Exception as e:
                print(f"Error while performing the function: {purpose}")
                print(e)
                forceLightsOff(argv[0], argv[1])
                exit()
        return inner
    return decorator

def flashSuccess(hdwf,dwf):
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x0000)) 
    dwf.FDwfDigitalIOOutputEnableSet(hdwf, c_int(0x0010))
    dwf.FDwfDigitalIOConfigure(hdwf)
    for i in range(10):
        dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x0010)) 
        dwf.FDwfDigitalIOConfigure(hdwf)
        time.sleep(1)
        dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x0000)) 
        dwf.FDwfDigitalIOConfigure(hdwf)
        time.sleep(1)

    return

