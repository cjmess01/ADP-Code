from ctypes import *
from dwfconstants import *
from digilent_system_functions import check_error
from time import sleep

import matplotlib.pyplot as plt
import numpy as np

import digilent_led as dig_led

'''
Main function that opens, reads, and closes from osc.
'''
@dig_led.lightLed(0, "oscilliscope reading")
def perform_simultaneous_reading(hdwf, dwf, time_to_sample, sampling_frequency, buffer_size):
    openScope(hdwf, dwf, time_to_sample, sampling_frequency)
    sleep(1)
    buff1, buff2 = readChannels(hdwf, dwf, buffer_size)

    return buff1, buff2





def get_recommended_presets(incoming_freq):
    freq = 1000000
    time_to_sample = 20
    buffer_size = 10000000

    if(incoming_freq >= 1):
        freq = 1000000
        time_to_sample = 10
        buffer_size = 10000000
    if(incoming_freq >=10):
        freq = 1000000
        time_to_sample = 2
        buffer_size = 1000000
  

    return freq, time_to_sample, buffer_size






'''
Opens scope, channels 1 and 2
'''
def openScope(hdwf, dwf, recording_time_in_seconds, sampling_rate):
    hzAcq = c_double(sampling_rate)

    dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(0)) # 0 = the device will only be configured when FDwf###Configure is called

    # Configure scopes
    dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_int(1))
    dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(1), c_int(1))
    dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(0), c_double(5))
    dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(1), c_double(5))

    # Set modes
    dwf.FDwfAnalogInAcquisitionModeSet(hdwf, acqmodeRecord)
    dwf.FDwfAnalogInFrequencySet(hdwf, hzAcq)
    dwf.FDwfAnalogInRecordLengthSet(hdwf, c_double(recording_time_in_seconds)) # -1 infinite record length
    

   
    # Notice that the third parameter below, fStart, is 0 (false)
    dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(0))
    
    sleep(3)



def readChannels(hdwf, dwf, num_samples):
    rgdSamples1 = (c_double * num_samples)()
    rgdSamples2 = (c_double * num_samples)()

    sts = c_byte()
    cAvailable = c_int()
    cLost = c_int()
    cCorrupted = c_int()
    fLost = 0
    fCorrupted = 0

    dwf.FDwfAnalogInConfigure(hdwf, c_int(0), c_int(1))

    cSamples = 0
    
    while cSamples < num_samples:
        dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))
        if cSamples == 0 and (sts == DwfStateConfig or sts == DwfStatePrefill or sts == DwfStateArmed) :
            # Acquisition not yet started.
            
            continue

        dwf.FDwfAnalogInStatusRecord(hdwf, byref(cAvailable), byref(cLost), byref(cCorrupted))
        
        cSamples += cLost.value

        if cLost.value :
            fLost = 1
        if cCorrupted.value :
            fCorrupted = 1

        if cAvailable.value==0 :
            continue

        if cSamples+cAvailable.value > num_samples :
            cAvailable = c_int(num_samples-cSamples)
    
        dwf.FDwfAnalogInStatusData(hdwf, c_int(0), byref(rgdSamples1, sizeof(c_double)*cSamples), cAvailable) # get channel 1 data

        dwf.FDwfAnalogInStatusData(hdwf, c_int(1), byref(rgdSamples2, sizeof(c_double)*cSamples), cAvailable) # get channel 2 data
        cSamples += cAvailable.value
  

    #print(len(rgdSamples))

    dwf.FDwfAnalogOutReset(hdwf, c_int(0))



    #print("Recording done")
    if fLost:
        print("Samples were lost! Reduce frequency")
    if  fCorrupted:
        print("Samples could be corrupted! Reduce frequency")

    return rgdSamples1, rgdSamples2





