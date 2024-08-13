from WF_SDK import device, scope, wavegen, tools, error   # import instruments

def create_FFT(buffer, frequency_start, frequency_stop,samplingFreq):

    spectrum_buff = tools.spectrum(buffer, tools.window.rectangular, samplingFreq, frequency_start, frequency_stop) #voltage amplitude spectrum
    spectrum_p_buff = tools.spectrumphase(buffer, tools.window.rectangular, scope.data.sampling_frequency, frequency_start, frequency_stop)   #voltage phase spectrum
    return spectrum_buff, spectrum_p_buff

from dwfconstants import * 
from ctypes import *
import matplotlib.pyplot as plt
import numpy
def fft(dwf, hzRate, nSamples, data, incomingFreq, channelNumber, showGraph):
    hzTop = hzRate/2.0
    rgdWindow = (c_double*nSamples)()
    vBeta = c_double(1.0) # used only for Kaiser window
    vNEBW = c_double() # noise equivalent bandwidth
    dwf.FDwfSpectrumWindow(byref(rgdWindow), c_int(nSamples), DwfWindowFlatTop, vBeta, byref(vNEBW))
    
    rgdSamples1 = data

    
    for i in range(nSamples):
        rgdSamples1[i] = rgdSamples1[i]*rgdWindow[i]

    # plt.title("windowed data")
    # plt.plot(numpy.fromiter(rgdSamples1, dtype = float), color='orange', label='C1')
    # plt.show()

    iFirst = 0.0
    iLast = 1
    nBins = int(nSamples/2+1)
    rgdBins1 = (c_double*nBins)()
    rgdBins1_phase = (c_double*nBins)()
    dwf.FDwfSpectrumTransform(byref(rgdSamples1), nSamples, byref(rgdBins1), byref(rgdBins1_phase), nBins, c_double(iFirst), c_double(iLast))
    import math

    # plt.plot(rgdBins1)
    # plt.show()
  

    # for i in range(nBins): 
    #     rgdBins1[i] = 20.0*math.log10(rgdBins1[i]/sqrt2) # to dBV
    

    threshold = .003
    print(threshold)
    for i in range(nBins): 
        if rgdBins1[i]<threshold: rgdBins1_phase[i] = 0  # mask phase at low magnitude
        else: rgdBins1_phase[i] = rgdBins1_phase[i]*180.0/math.pi # radian to degree
        if rgdBins1_phase[i] < 0 : rgdBins1_phase[i] = 180.0+rgdBins1_phase[i] 
        
    rgMHz = []
    MHzFirst = hzTop*iFirst/1e6
    MHzLast = hzTop*iLast/1e6
    MHzStep = hzTop*(iLast-iFirst)/(nBins-1)/1e6
    for i in range(nBins): 
        rgMHz.append(MHzFirst + MHzStep*i)


    rgBins1 = numpy.fromiter(rgdBins1, dtype = float)
    rgBins1_phase = numpy.fromiter(rgdBins1_phase, dtype = float)

    plt.title(f"FFT-{incomingFreq}")
    plt.xlim([MHzFirst, MHzLast])
    plt.ylim([-180.0, 180.0])
    plt.plot(rgMHz, rgBins1, color='orange', label='dBV')
    plt.plot(rgMHz, rgBins1_phase, color='blue', label='deg')

    import os
    file_path = os.path.join(".", "graphs", f"{channelNumber}-FFTPhase&Mag-{incomingFreq}.png")
    plt.savefig(file_path)
    if(showGraph == 'display'):
        plt.show()
    plt.clf()


    return rgBins1, rgBins1_phase

    