import serial
from time import sleep




def open_serial(serial_port : str):
    successful_connection = False
    ser = serial.Serial(port = f'COM{serial_port}', baudrate = 9600, timeout=1)
    for x in range(10):
        value = ser.read(1)
        ser.read()
        if(value == b'r'):
            successful_connection = True
            break
        print(f"Failed (Attempt {x+1})...")
        sleep(1)
    if(not successful_connection):
        raise Exception("Failed to connect to TMS after 10 tries.")
    return ser

def open_uart():
    print("This isn't set up yet. Implement this later")
    raise Exception("Uart option selected, but not yet set up. Set to none instead.")
    



def send_message(method):
    print("This isn't set up yet")
    raise Exception("This isn't set up yet. Set tms method to none")





def send_uart_method(message):
    print("A")



