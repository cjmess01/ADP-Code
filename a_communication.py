import serial 
from time import sleep
import numpy as np
import matplotlib.pyplot as plt

from WF_SDK import device, scope

from structure_node import DataNode
from helper_linkedlist import HarmonicList


def main():
   
    
    '''
    1. Setup Device Communication
    '''
    # Connect to MCU
    connected_to_mcu = False
    try:
        ser = serial.Serial(port = 'COM13', baudrate = 9600)
        while True:
            value = ser.read(1)
            print(value)
            if(value == b'r'):
                connected_to_mcu = True
                print("CONNECTED TO MCU")
                break
            sleep(1)
    except Exception as e:
        print(f"Failed to connect serial for reason: {e}")

    # Connect to digilent
    try:
        device_data = device.open()
    except Exception as e:
        print(f"Failed to connect to ADP3450 for reason: {e}")


    '''
    2. Setup of Data Storage
    '''
    # Pertubances
    starting_freq = 1000
    num_frequencies = 1
    interval_between_frequencies = 100
    # Harmonics
    num_harmonics = 5
    # Create Matrix
    list_of_frequencies = [(interval_between_frequencies*x)+starting_freq for x in range(num_frequencies)]
    list_of_harmonics = [(x*2)+1 for x in range(num_harmonics)]
    print(f"Frequencies: {list_of_frequencies}")
    print(f"Harmonics: {list_of_harmonics}")
    harmonic_matrix = np.ndarray(shape=(len(list_of_frequencies),len(list_of_harmonics)), dtype=DataNode, order='F')
    print(harmonic_matrix)


    '''
    3. Data Collection
    '''
    for i in range(0, len(list_of_frequencies)):
        '''
        3.1 Reading from scope
        '''
        print("Listening at frequency "+ str(list_of_frequencies[i]) + "Hz...")
        num_samples = 2000000
        scope.open(device_data,buffer_size=num_samples,sampling_frequency=2000000)
        scope.trigger(device_data, enable=True, source=scope.trigger_source.none, channel=1, level=0)
        scope.trigger(device_data, enable=True, source=scope.trigger_source.none, channel=2, level=0)
        channel1, channel2 = scope.recordtwo(device_data, channel1=1, channel2=2)
        scope.close(device_data)
        print("Multiplying channel2 values by 10")
        channel2 = [x * 10 for x in channel2]

        '''
        3.2 Trim Buffer and create FFT
        '''
        buffer_size = 2000000
        buffer1 = channel1[0:buffer_size]
        buffer2 = channel2[0:buffer_size]
        
        # Plot raw signal 
        print("Printing graphs, make sure that they are superimposed...")
        plt.plot(buffer1, color='blue')
        plt.plot(buffer2, color='red')
        plt.title("Raw signal, Channel 1 in blue, Channel 2 in red")
        plt.show()

        print("Create both FFT on BOTH these signals...")
        frequency_start = 0
        frequency_stop = 2000000
        frequency_range = frequency_stop - frequency_start
        from helper_fft import create_FFT
        spectrum_buff1, spectrum_p_buff1 = create_FFT(buffer1, frequency_start, frequency_stop,list_of_frequencies[i])
        spectrum_buff2, spectrum_p_buff2 = create_FFT(buffer2, frequency_start, frequency_stop, list_of_frequencies[i])
        # plt.plot(spectrum_buff1)
        # plt.title("Buffer 1 mag")
        # plt.show()
        # plt.plot(spectrum_p_buff1)
        # plt.title("Buffer 1 phz")
        # plt.show()
        # plt.plot(spectrum_buff2)
        # plt.title("Buffer 2 mag")
        # plt.show()
        # plt.plot(spectrum_p_buff2)
        # plt.title("Buffer 2 phz")
        # plt.show()

        '''
        3.3 Processing Harmonics
        '''
        # Sample multiplier - I need to look into this???
       
        sample_multiplier_1 = round(len(spectrum_buff1) / frequency_range)
        sample_multiplier_2 = round(len(spectrum_buff2) / frequency_range)
        print("Sample multiplier: " + str(sample_multiplier_1) + "...")
        for j in range(0, len(list_of_harmonics)):
            curr_harmonic = list_of_harmonics[j] * list_of_frequencies[i]
            print("Searching harmonic " + str(curr_harmonic))

            from helper_process_harmonic import process_harmonic
            harmonic_v_magnitude, harmonic_v_phase = process_harmonic(spectrum_buff1, spectrum_p_buff1, curr_harmonic, list_of_frequencies[i], sample_multiplier_1)
            harmonic_i_magnitude, harmonic_i_phase = process_harmonic(spectrum_buff2, spectrum_p_buff2, curr_harmonic, list_of_frequencies[i], sample_multiplier_2)
            
            
            curr_node = DataNode()
            curr_node.name(list_of_frequencies[i], curr_harmonic)
            curr_node.set_data(harmonic_v_magnitude, harmonic_v_phase, harmonic_i_magnitude, harmonic_i_phase)
            harmonic_matrix[i,j] = curr_node
        
        '''
        3.4 Send Signal for next, then sleep
        '''
        print("Sending message to MCU if connected and sleeping...")
        if(connected_to_mcu):
            ser.write(b'n')
       
    print("Finished Data Acquisition")
    '''
    4 Data Cleansing
    '''

    
    ls = HarmonicList()
    # Insert the nodes into the list, which will automatically sort them
    # Notice that we are iterating through the transpose
    # This ensures that, in the case of duplicates, the one originating in the lower frequency goes in
    for i in range(0,len(list_of_harmonics)):
        for j in range(0, len(list_of_frequencies)):
            ls.insert_in_order(harmonic_matrix.T[i,j])
    ls.print_list()
    

    # Just clearing the plt buffer
    plt.show()

    _, harmonics = ls.get_freqs_and_harmonics()
    imp_mag, imp_pz = ls.get_impedance_lists()
    
    plt.title("impedance magnitude")
    plt.plot(harmonics,imp_mag,'-o')
    plt.show()
    plt.title("impedance phase")
    plt.plot(harmonics,imp_pz,'-o')
    plt.show()

    
    
    
    z_reals, z_imgs = ls.z_lists()
    points = list(zip(z_reals, z_imgs))
    x,y = zip(*points)
    print(x)
    print(y)
    plt.plot(x,y, '-o')
    plt.show()
    ls.export(".\\mydata.csv")

    return



if __name__ == '__main__':
    main()