'''
This file creates 2 waves simultaneously from the Digilent, out of channels 1 and 2.
These can be any type of wave, sine, square, etc. It can also be custom, but you must load the custom waves in.
To find where to load in data, go to the comment marks with ***

IMPORTANT NOTE If you want it to read from an external source, simply hook up the scopes to the external source. The code can remain unchanged.
It will still say generating a wave, but since the wavegen is not hooked up to the scopes, it won't read it.  

It then reads in scopes 1 & 2 and graphs the raw signals. Then, it performs an Magnitudew and Phase FFT for the channels and plots them separately. 
It then cycles through a number of harmonics (Set in the section 1, User input/settings constants within this file) and finds the local maximum in that area. 
Finally, it saveas that data and finds the impedance magnitude and phase. It saves that data in the current directory in a file called manual.csv.  
'''

from WF_SDK import device, scope, wavegen, tools, error   # import instruments
import numpy as np
from time import sleep
import pandas as pd
    
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


'''
- 1. User input/setting constants
'''
# Get the list of frequencies, low_range hz - top_range hz
# bottom_range = int(input("Bottom frequency inclusive: "))
# top_range = int(input("Top frequency, not inclusive: "))
# interval = int(input("How much distance between each one in Hz: ")) # assume intervals are equal
# num_harmonics = int(input("Number of harmonics: "))

# Pertubances
bottom_range = 100
top_range = 200
interval = 100
num_harmonics = 5

# List of all frequencies to expect
list_of_frequencies = []
current_frequency = bottom_range
while(current_frequency < top_range):
    list_of_frequencies.append(current_frequency)
    current_frequency += interval

# List of all harmonics 
list_of_harmonics = []
current_harmonic = 1
while(len(list_of_harmonics) < num_harmonics):
    list_of_harmonics.append(current_harmonic)
    current_harmonic += 2

print("Frequency Range: " + str(list_of_frequencies) + " all in Hz")
print("Harmonics: " + str(list_of_harmonics))




'''
- 2. Creating Data table
This creates the frequency/harmonic data table that will eventually be filled with fft information
 
'''
from structure_node import DataNode
harmonic_matrix = np.ndarray(shape=(len(list_of_frequencies),len(list_of_harmonics)), dtype=DataNode, order='F')
print(harmonic_matrix)



'''
- 3. Connecting to device
'''
print("Connecting to device...")
# connect to the device
device_data = device.open()
print("Connected...")




'''
- 4. For each frequency, create the frequency on the digilent (in leui of a battery) and record from both channels simultaneously.
Then, generate an fft over that data. In the nested for loop, cycle through the harmonics and find peaks. 
'''
for i in range(0, len(list_of_frequencies)):
    print("Listening for pertubation at frequency " + str(list_of_frequencies[i]) + "Hz...")



    print("Recording and trimming 2 waves...")
    # initialize the scope with default settings
    num_samples = 2000000
    scope.open(device_data,buffer_size=num_samples,sampling_frequency=2000000)
    # set up triggering on scope channel 1 & 2
    scope.trigger(device_data, enable=True, source=scope.trigger_source.none, channel=1, level=0)
    scope.trigger(device_data, enable=True, source=scope.trigger_source.none, channel=2, level=0)
    channel1, channel2 = scope.recordtwo(device_data, channel1=1, channel2=2)
    scope.close(device_data)

    print("Multiplying channel2 values by 10")
    channel2 = [x * 10 for x in channel2]
    
    

    # Set up the size of the buffer, or the number of samples
    buffer_size = 2000000
    def trim_buff(buffer, buffer_size):
        return buffer[0:(buffer_size*1)]
    buffer1 = trim_buff(channel1, buffer_size)
    buffer2 = trim_buff(channel2, buffer_size)
    # Plot raw signal 
    print("Printing graphs, make sure that they are superimposed...")
    import matplotlib.pyplot as plt
    plt.plot(buffer1, color='blue')
    plt.plot(buffer2, color='red')
    plt.title("Raw signal, Channel 1 in blue, Channel 2 in red")
    #plt.show()

    # Create and plot FFTs
    print("Create both FFT on BOTH these signals...")
    frequency_start = 0
    frequency_stop = 2000000
    frequency_range = frequency_stop - frequency_start
    
    from helper_fft import create_FFT
    spectrum_buff1, spectrum_p_buff1 = create_FFT(buffer1, frequency_start, frequency_stop)
    spectrum_buff2, spectrum_p_buff2 = create_FFT(buffer2, frequency_start, frequency_stop)
    # plt.plot(spectrum_buff1)
    # plt.title("Buffer 1 mag")
    # #plt.show()
    # plt.plot(spectrum_p_buff1)
    # plt.title("Buffer 1 phz")
    # #plt.show()
    # plt.plot(spectrum_buff2)
    # plt.title("Buffer 2 mag")
    # #plt.show()
    # plt.plot(spectrum_p_buff2)
    # plt.title("Buffer 2 phz")
    # #plt.show()

    
    # Creates location to store the peaks at harmonics
    print("Data for plotting...")
    frequency_at_n_hz = []
    v_mags = []
    v_ph = []
    i_mags = []
    i_ph = []



    # Sample multiplier - I need to look into this???
    print("Get sample multiplier")
    sample_multiplier_1 = round(len(spectrum_buff1) / frequency_range)
    sample_multiplier_2 = round(len(spectrum_buff2) / frequency_range)
    print("Sample multiplier: " + str(sample_multiplier_1) + "...")

    
    '''
    - 5. For each harmonic, search the fft and find the relative peak in the area. 
    '''
    for j in range(0, len(list_of_harmonics)):
        curr_harmonic = list_of_harmonics[j] * list_of_frequencies[i]
        curr_frequency= list_of_frequencies[i]

        from helper_process_harmonic import process_harmonic
        harmonic_v_magnitude, harmonic_v_phase = process_harmonic(spectrum_buff1, spectrum_p_buff1, curr_harmonic, curr_frequency, sample_multiplier_1)
        harmonic_i_magnitude, harmonic_i_phase = process_harmonic(spectrum_buff2, spectrum_p_buff2, curr_harmonic, curr_frequency, sample_multiplier_2)

        print("Searching harmonic " + str(curr_harmonic))

        curr_node = DataNode()
        curr_node.name(list_of_frequencies[i], curr_harmonic)
        curr_node.set_data(harmonic_v_magnitude, harmonic_v_phase, harmonic_i_magnitude, harmonic_i_phase)
        harmonic_matrix[i,j] = curr_node

        frequency_at_n_hz.append(curr_harmonic)
        v_mags.append(harmonic_v_magnitude)
        v_ph.append(harmonic_v_phase)
        i_mags.append(harmonic_i_magnitude)
        i_ph.append(harmonic_i_phase)
    
    '''Data for plotting'''
    frequencies_to_plot = [x for x in range(100000)]
    v_amps_to_plot = [0] * 100000
    v_ph_to_plot = [0] * 100000
    i_amps_to_plot = [0] * 100000
    i_ph_to_plot = [0] * 100000
    for i in range(0,len(frequency_at_n_hz)):
        v_amps_to_plot[frequency_at_n_hz[i]] = v_mags[i]
        v_ph_to_plot[frequency_at_n_hz[i]] = v_ph[i]
        i_amps_to_plot[frequency_at_n_hz[i]] = i_mags[i]
        i_ph_to_plot[frequency_at_n_hz[i]] = i_ph[i]

    '''
    - 6. Create an fft graph
    '''
    fig = plt.figure()
    gs = gridspec.GridSpec(2, 1, height_ratios=[2, 1]) 
    
    # the first subplot
    ax0 = plt.subplot(gs[0])
    line0, = ax0.plot(frequencies_to_plot, v_amps_to_plot, color='r')
    # the second subplot
    ax1 = plt.subplot(gs[1], sharex = ax0)
    line1, = ax1.plot(frequencies_to_plot, v_ph_to_plot, color='b')
    plt.setp(ax0.get_xticklabels(), visible=False)
    # remove last tick label for the second subplot
    yticks = ax1.yaxis.get_major_ticks()
    yticks[-1].label1.set_visible(False)
    # put legend on first subplot
    ax0.legend((line0, line1), ('amplitude [V]', 'phase [deg]'), loc='upper right')
    plt.subplots_adjust(hspace=.0)
    plt.title("Voltage (ch1) FFT Plot, magnitude and phase vs. frequency", loc= 'center', pad = float(190))
    #plt.show()

    fig = plt.figure()
    gs = gridspec.GridSpec(2, 1, height_ratios=[2, 1]) 
    # the first subplot
    ax0 = plt.subplot(gs[0])
    line0, = ax0.plot(frequencies_to_plot, i_amps_to_plot, color='r')
    # the second subplot
    ax1 = plt.subplot(gs[1], sharex = ax0)
    line1, = ax1.plot(frequencies_to_plot, i_ph_to_plot, color='b')
    plt.setp(ax0.get_xticklabels(), visible=False)
    # remove last tick label for the second subplot
    yticks = ax1.yaxis.get_major_ticks()
    yticks[-1].label1.set_visible(False)
    # put legend on first subplot
    ax0.legend((line0, line1), ('amplitude [V]', 'phase [deg]'), loc='upper right')
    plt.subplots_adjust(hspace=.0)
    plt.title("Current (ch2) FFT Plot, magnitude and phase vs. frequency", loc= 'center', pad = float(190))
    #plt.show()



    # Sending UART stuff
    print("SEND A SIGNAL")
    input("Has the thing started")




#print(harmonic_matrix.shape)

for col in range(0, harmonic_matrix.shape[1]):
    for node in harmonic_matrix[:, col]:
        print(node.harmonic)


harmonics = []
spectrum_1_mag= []
spectrum_1_ph= []
spectrum_2_mag= []
spectrum_2_ph = []


for node in harmonic_matrix.flatten():
    spectrum_1_mag.append(node.voltage_magnitude)
    spectrum_1_ph.append(node.voltage_phase)
    spectrum_2_mag.append(node.current_magnitude)
    spectrum_2_ph.append(node.current_phase)
    harmonics.append(node.harmonic)
    # print(node.harmonic)
    
print(spectrum_1_mag)
print(spectrum_1_ph)
print(spectrum_2_mag)
print(spectrum_2_ph)


z_mag = [spectrum_1_mag[i] / spectrum_2_mag[i] for i in range( len(spectrum_1_mag))]
z_phase = [spectrum_1_ph[i] - spectrum_2_ph[i] for i in range( len(spectrum_1_ph))]
print(z_mag)
print(z_phase)

plt.title("Impedance Mag")
plt.plot(z_mag)
#plt.show()

plt.title("Impedance Phz")
plt.plot(z_phase)
#plt.show()


import math
def degreeCosine(degrees : float):
    radians = degrees * math.pi / 180.0
    return math.cos(radians)

def degreeSine(degrees : float):
    radians = degrees * math.pi / 180.0
    return math.sin(radians)
    

z_real = [z_mag[i] * degreeCosine(z_phase[i]) for i in range(len(z_mag))]
z_img = [-z_mag[i] * degreeSine(z_phase[i]) for i in range(len(z_mag))]

print(z_real)
print(z_img)

points = list(zip(z_real, z_img))


plt.show()
print("POINTS")
print(points)
x,y = zip(*points)
plt.plot(x,y, '-o')
plt.show()

# frequencies_to_plot = [x for x in range(100000)]
# imp_mag_to_plot = [0] * 100000
# imp_ph_to_plot = [0] * 100000

# for x in range(len(harmonics)):
#     imp_mag_to_plot[harmonics[x]] = z_mag[x]
#     imp_ph_to_plot[harmonics[x]] = z_phase[x]



# plt.title("")
# plt.plot(frequencies_to_plot, imp_mag_to_plot, color="red")
# #plt.show()
# plt.plot(frequencies_to_plot, imp_ph_to_plot, color="blue")
# #plt.show()

data = {
    "Current_mag": spectrum_1_mag,
    "Current_phz": spectrum_1_ph,
    "Voltage_mag": spectrum_2_mag,
    "Voltage_phase": spectrum_2_ph,
    "Impedance_magnitude": z_mag,
    "Impedance_phase": z_phase


}
mydf = pd.DataFrame(data=data)
mydf.to_csv(".\\manual.csv")


import serial
from time import sleep 

ser = serial.Serial(port = 'COM1', baudrate = 9600)
i=0


numbers=[0x40]

numbers=bytes(numbers)    
ser.write(numbers)


