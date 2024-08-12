from dwfconstants import *
import sys
'''
Opens the device
Return values:
    dwf : Waveforms cdll handle
    hdwf: Device handler  
'''

def open():
    # Load dwf library
    if sys.platform.startswith("win"):
        dwf = cdll.dwf
    elif sys.platform.startswith("darwin"):
        dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
    else:
        dwf = cdll.LoadLibrary("libdwf.so")
    version = create_string_buffer(16)
    dwf.FDwfGetVersion(version)
    print("DWF Version: "+str(version.value))


    dwf.FDwfParamSet(DwfParamOnClose, c_int(0)) # 0 = run, 1 = stop, 2 = shutdown
    
    hdwf = c_int()
    if dwf.FDwfDeviceOpen(-1, byref(hdwf)) != 1 or hdwf.value == hdwfNone.value:
        szerr = create_string_buffer(512)
        dwf.FDwfGetLastErrorMsg(szerr)
        raise Exception(szerr.value)
    
    return dwf, hdwf
    
import ctypes
from dwfconstants import *
import inspect
def check_error(dwf):
    """
        check for errors
    """
    print("Error func")
    err_msg = ctypes.create_string_buffer(512)        # variable for the error message
    dwf.FDwfGetLastErrorMsg(err_msg)                  # get the error message
    err_msg = err_msg.value.decode("ascii")           # format the message
    if err_msg != "":
        err_func = inspect.stack()[1].function        # get caller function
        err_inst = inspect.stack()[1].filename        # get caller file name
        # delete the extension
        err_inst = err_inst.split('.')[0]
        # delete the path
        path_list = err_inst.split('/')
        err_inst = path_list[-1]
        path_list = err_inst.split('\\')
        err_inst = path_list[-1]
        raise Exception(err_msg, err_func, err_inst)
    return