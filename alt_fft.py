"""
   DWF Python Example
   Author:  Digilent, Inc.
   Revision:  2022-08-01

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

def fft(dwf, hzRate, nSamples, data, incomingFreq, channelNumber, showGraph):

    rgdSamples1 = (c_double*nSamples)()



    hzTop = hzRate/2.0
    rgdWindow = (c_double*nSamples)()
    vBeta = c_double(1.0) # used only for Kaiser window
    vNEBW = c_double() # noise equivalent bandwidth
    dwf.FDwfSpectrumWindow(byref(rgdWindow), c_int(nSamples), DwfWindowFlatTop, vBeta, byref(vNEBW))
    rgdSamples1 = data

    for i in range(nSamples):
        rgdSamples1[i] = rgdSamples1[i]*rgdWindow[i]

    plt.title("window and windowed data")
    plt.plot(numpy.fromiter(rgdSamples1, dtype = float), color='orange', label='C1')
    plt.plot(numpy.fromiter(rgdWindow, dtype = float), color='blue', label='W')
    plt.show()


    # requires power of two number of samples and BINs of samples/2+1
    nBins = int(nSamples/2+1)
    rgdBins1 = (c_double*nBins)()
    rgdPhase1 = (c_double*nBins)()
    dwf.FDwfSpectrumFFT(byref(rgdSamples1), nSamples, byref(rgdBins1), byref(rgdPhase1), nBins)



    for i in range(nBins): 
        if rgdBins1[i]<.001 : rgdPhase1[i] = 0  # mask phase at low magnitude
        else: rgdPhase1[i] = rgdPhase1[i]*(180.0/math.pi) # radian to degree
        if rgdPhase1[i] < 0 : rgdPhase1[i] = 180.0+rgdPhase1[i] 

    rgMHz = []
    for i in range(nBins): 
        rgMHz.append(hzTop*i/(nBins-1)/1e6)

    rgBins1 = numpy.fromiter(rgdBins1, dtype = float)
    rgPhase1 = numpy.fromiter(rgdPhase1, dtype = float)

    plt.title("FFT dBV-deg / MHz")
    plt.xlim([0, hzTop/1e6])
    plt.ylim([-180.0, 180.0])
    #plt.xticks(numpy.arange(0, hzTop/1e6, hzTop/2e7))
    plt.plot(rgMHz, rgBins1, color='orange', label='dBV')
    plt.plot(rgMHz, rgPhase1, color='blue', label='deg')
    plt.show()


    return rgBins1, rgPhase1


