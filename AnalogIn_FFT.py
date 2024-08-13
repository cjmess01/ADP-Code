"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2022-08-01

   Requires:                       
       Python 2.7, 3
"""
import digilent_system_functions as dig_open
import digilent_scope as dig_scope
import tms_communication as tms_communication
from structure_node import DataNode
import helper_graph as graph
from ctypes import *
from dwfconstants import *
import math
import time
import matplotlib.pyplot as plt
import sys
import numpy
show_graphs = 'display'

if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")


version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

# prevent temperature drift
dwf.FDwfParamSet(DwfParamOnClose, c_int(0)) # 0 = run, 1 = stop, 2 = shutdown

hdwf = c_int()
print("Opening first device")
if dwf.FDwfDeviceOpen(-1, byref(hdwf)) != 1 or hdwf.value == hdwfNone.value:
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(szerr.value)
    print("failed to open device")
    quit()

dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(0)) # 0 = the device will only be configured when FDwf###Configure is called

print("Wavegen source selected...")
print("Loading csv...")
from helpercsv import read_csv_column
data1 = read_csv_column(f".\\negative_volt.csv", 'Negative')
data2 = read_csv_column(f".\\Waveforms_Current_65356.csv", 'Battery current')
datas = [data1, data2]

from WF_SDK import wavegen
print("[REPLACE WITH BATTERY] Beginning wavegen to simulate battery wave...")
wavegen.simultaneous_generate(hdwf, 1, wavegen.function.custom,0,100,amplitudes=[1,1], data = datas)

print("[REPLACE WITH BATTERY] Waves generated...")
from time import sleep
sleep(1)


print("Preparing to read frequency "+ str(100) + "Hz...")
sampling_frequency, time_to_sample, buffer_size = dig_scope.get_recommended_presets(100)
print(f"Minimum sample time is {time_to_sample} seconds...")
print(f"Sampling frequency is {sampling_frequency}...")
print(f"Buffer size is {buffer_size}")
try: 
    buffer1, buffer2 = dig_scope.perform_simultaneous_reading(hdwf, dwf, time_to_sample, sampling_frequency, buffer_size)
    graph.raw_signal(f"{100}Hz_raw_signal", [buffer1, buffer2], show_graphs)
except Exception as e:
    print(f"Read failed for reason: {e}")
    print("Fatal error. Ending process")
    
nSamples = buffer_size

hzRate = c_double()


rgdSamples1 = buffer1
rgdSamples2 = buffer2




plt.title("raw data")
plt.plot(numpy.fromiter(rgdSamples1, dtype = float), color='orange', label='C1')
plt.show()
plt.title("raw data")
plt.plot(numpy.fromiter(rgdSamples2, dtype = float), color='orange', label='C1')
plt.show()


hzTop = sampling_frequency / 2
print(hzTop)
rgdWindow = (c_double*nSamples)()
vBeta = c_double(1.0) # used only for Kaiser window
vNEBW = c_double() # noise equivalent bandwidth
dwf.FDwfSpectrumWindow(byref(rgdWindow), c_int(nSamples), DwfWindowFlatTop, vBeta, byref(vNEBW))

for i in range(nSamples):
    rgdSamples1[i] = rgdSamples1[i]*rgdWindow[i]
    rgdSamples2[i] = rgdSamples2[i]*rgdWindow[i]

plt.title("window and windowed data")
plt.plot(numpy.fromiter(rgdSamples1, dtype = float), color='orange', label='C1')
plt.plot(numpy.fromiter(rgdWindow, dtype = float), color='blue', label='W')
plt.show()
plt.plot(numpy.fromiter(rgdSamples2, dtype = float), color='orange', label='C1')
plt.plot(numpy.fromiter(rgdWindow, dtype = float), color='blue', label='W')
plt.show()


# requires power of two number of samples and BINs of samples/2+1
nBins = int(nSamples/2+1)
rgdBins1 = (c_double*nBins)()
rgdPhase1 = (c_double*nBins)()
rgdBins2 = (c_double*nBins)()
rgdPhase2 = (c_double*nBins)()
dwf.FDwfSpectrumFFT(byref(rgdSamples1), nSamples, byref(rgdBins1), byref(rgdPhase1), nBins)
dwf.FDwfSpectrumFFT(byref(rgdSamples2), nSamples, byref(rgdBins2), byref(rgdPhase2), nBins)



for i in range(nBins): 
    if rgdBins1[i]<.002 : rgdPhase1[i] = 0  # mask phase at low magnitude
    else: rgdPhase1[i] = rgdPhase1[i]*(180.0/math.pi) # radian to degree
    if rgdPhase1[i] < 0 : rgdPhase1[i] = 180.0+rgdPhase1[i] 
for i in range(nBins): 
    if rgdBins2[i]<.002 : rgdPhase2[i] = 0  # mask phase at low magnitude
    else: rgdPhase2[i] = rgdPhase2[i]*(180.0/math.pi) # radian to degree
    if rgdPhase2[i] < 0 : rgdPhase2[i] = 180.0+rgdPhase2[i] 

rgMHz = []
for i in range(nBins): 
    rgMHz.append(hzTop*i/(nBins-1)/1e6)

rgBins1 = numpy.fromiter(rgdBins1, dtype = float)
rgPhase1 = numpy.fromiter(rgdPhase1, dtype = float)
rgBins2 = numpy.fromiter(rgdBins2, dtype = float)
rgPhase2 = numpy.fromiter(rgdPhase2, dtype = float)

plt.title("FFT dBV-deg / MHz")
plt.xlim([0, hzTop/1e6])
plt.ylim([-180.0, 180.0])
#plt.xticks(numpy.arange(0, hzTop/1e6, hzTop/2e7))
plt.plot(rgMHz, rgBins1, color='orange', label='dBV')
plt.plot(rgMHz, rgPhase1, color='blue', label='deg')
plt.show()
plt.title("FFT dBV-deg / MHz")
plt.xlim([0, hzTop/1e6])
plt.ylim([-180.0, 180.0])
#plt.xticks(numpy.arange(0, hzTop/1e6, hzTop/2e7))
plt.plot(rgMHz, rgBins2, color='orange', label='dBV')
plt.plot(rgMHz, rgPhase2, color='blue', label='deg')
plt.show()





