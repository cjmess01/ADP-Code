from time import sleep
import digilent_led as dig_led

from ctypes import *
import time


def open_uart(hdwf, dwf):
    cRX = c_int(0)
    fParity = c_int(0)

    # configure the I2C/TWI, default settings
    dwf.FDwfDigitalUartRateSet(hdwf, c_double(9600)) # 9.6kHz
    dwf.FDwfDigitalUartTxSet(hdwf, c_int(8)) # TX = DIO-15
    dwf.FDwfDigitalUartRxSet(hdwf, c_int(9)) # RX = DIO-14
    dwf.FDwfDigitalUartBitsSet(hdwf, c_int(8)) # 8 bits
    dwf.FDwfDigitalUartParitySet(hdwf, c_int(0)) # 0 no parity, 1 even, 2 odd, 3 mark (high), 4 space (low)
    dwf.FDwfDigitalUartStopSet(hdwf, c_double(1)) # 1 bit stop length
    dwf.FDwfDigitalUartTx(hdwf, None, c_int(0))# initialize TX, drive with idle level
    dwf.FDwfDigitalUartRx(hdwf, None, c_int(0), byref(cRX), byref(fParity))# initialize RX reception
    time.sleep(1)
    
    


# Send message as a python string, ie 'message'
@dig_led.lightLedOneArg(5, "Speaking")
def send_message(hdwf, dwf, message):

    process_string = lambda message : message.encode() + b'\r\n'

    rgTX = create_string_buffer(process_string(message))
    
    #raise Exception("This isn't set up yet. Set tms method to none")
    print("Sending on TX for 10 seconds...")
    dwf.FDwfDigitalUartTx(hdwf, rgTX, c_int(sizeof(rgTX)-1)) # send text, trim zero ending
    time.sleep(1)
    return 1


@dig_led.lightLedOneArg(6, "Listening")
def listen(hdwf, dwf):
    time.sleep(2)
    cRX = c_int(0)
    fParity = c_int(0)
    rgRX = create_string_buffer(8193)
    tsec = time.perf_counter()  + 10 # receive for 10 seconds
    print("Receiving on RX...")
    while time.perf_counter() < tsec:
        time.sleep(0.01)
        dwf.FDwfDigitalUartRx(hdwf, rgRX, c_int(sizeof(rgRX)-1), byref(cRX), byref(fParity)) # read up to 8k chars at once
        if cRX.value > 0:
            rgRX[cRX.value] = 0 # add zero ending
            print(rgRX.value.decode(), end = '', flush=True)
        if fParity.value != 0:
            print("Parity error {}".format(fParity.value))
    return rgRX.value.decode()
        



def send_uart_method(message):
    print("A")



