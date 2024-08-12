"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2018-07-19

   Requires:                       
       Python 2.7, 3
"""

from ctypes import *
from dwfconstants import *
import math
import time
import matplotlib.pyplot as plt
import sys
import numpy

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

#declare ctype variables
hdwf = c_int()
sts = c_byte()

incomingFreq = 1.0 # incoming freq in hz
maxBuffer = 32000.0
numRevs = 2.0
timeSample = numRevs / incomingFreq
samplingRate = maxBuffer / (numRevs / incomingFreq)
print(f"Time to sample: {timeSample}")
print(f"Sampling freq: {samplingRate}")


hzAcq = c_double(100000)
nSamples = 200000
rgdSamples = (c_double*nSamples)()
cAvailable = c_int()
cLost = c_int()
cCorrupted = c_int()
fLost = 0
fCorrupted = 0

#print(DWF version
version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

#open device
print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == hdwfNone.value:
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    print("failed to open device")
    quit()

dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(0)) # 0 = the device will only be configured when FDwf###Configure is called

print(c_double(nSamples/hzAcq.value))


#set up acquisition
dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_int(1))
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(0), c_double(5))
dwf.FDwfAnalogInAcquisitionModeSet(hdwf, acqmodeRecord)
dwf.FDwfAnalogInFrequencySet(hdwf, hzAcq)
dwf.FDwfAnalogInRecordLengthSet(hdwf, c_double(nSamples/hzAcq.value)) # -1 infinite record length
dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(0))

sizeBuffer = c_int()
dwf.FDwfAnalogInBufferSizeGet(hdwf, byref(sizeBuffer))
print(f"Buffersize: {sizeBuffer}")
dwf.FDwfAnalogInBufferSizeSet(hdwf, sizeBuffer)
print(hzAcq)
print(c_double(nSamples/hzAcq.value))
#wait at least 2 seconds for the offset to stabilize
time.sleep(2)

print("Starting oscilloscope")
dwf.FDwfAnalogInConfigure(hdwf, c_int(0), c_int(1))

cSamples = 0

while cSamples < nSamples:
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

    if cSamples+cAvailable.value > nSamples :
        cAvailable = c_int(nSamples-cSamples)
    

    dwf.FDwfAnalogInStatusData(hdwf, c_int(0), byref(rgdSamples, sizeof(c_double)*cSamples), cAvailable) # get channel 1 data
    print(cAvailable)
    #dwf.FDwfAnalogInStatusData(hdwf, c_int(1), byref(rgdSamples, sizeof(c_double)*cSamples), cAvailable) # get channel 2 data
    cSamples += cAvailable.value

print(len(rgdSamples))



# continue running after device close, prevent temperature drifts
dwf.FDwfParamSet(DwfParamOnClose, c_int(1)) # 0 = run, 1 = stop, 2 = shutdown
# enable output for DIO 1 and 2
dwf.FDwfDigitalIOOutputEnableSet(hdwf, c_int(0x0006)) # 1<<1
# set value on enabled IO pins
dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x0000)) # DIO-1 low
dwf.FDwfDigitalIOConfigure(hdwf)

if(len(rgdSamples) == 200000):
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x0002)) # DIO-1 high
    dwf.FDwfDigitalIOConfigure(hdwf)
    time.sleep(3) # wait a second
    dwf.FDwfDigitalIOOutputSet(hdwf, c_int(0x0000)) # DIO-1 low
    dwf.FDwfDigitalIOConfigure(hdwf)

time.sleep(3) # wait a second

dwf.FDwfAnalogOutReset(hdwf, c_int(0))
dwf.FDwfDeviceCloseAll()

print("Recording done")
if fLost:
    print("Samples were lost! Reduce frequency")
if fCorrupted:
    print("Samples could be corrupted! Reduce frequency")

f = open("record.csv", "w")
for v in rgdSamples:
    f.write("%s\n" % v)
f.close()
  

plt.plot(numpy.fromiter(rgdSamples, dtype = float))
plt.show()


