
from time import sleep
import numpy as np

import serial
import digilent_system_functions as dig_open
import digilent_scope as dig_scope
import tms_communication as tms_communication
from structure_node import DataNode
import helper_graph as graph
import digilent_led as digilent_led

import gc

def main():
    # Set constants here
    '''
    List of frequencies to perturbed at
    Keep frequencies between 1-5000
    At 5000, only use 5 harmonics, max. Minimum harmonics is always 1
    '''
    list_of_frequencies = [.1, 1, 10,100]
    '''
    Number of harmonics per frequency
    '''
    num_harmonics = 9

    '''
    TMS communication method
    Options:
    'serial' - communicate through the usb of the computer. Ensure that the tms is connected through USB to the host pc
    'uart'   - communicate through the uart pins of the digilent. Ensure the read is pin X and the write is pin X
    '''
    tms_communication_method = 'none'
    # If tms_communication_method is serial, set a port number. If uart, you can ignore
    serial_port = '1'

    '''
    Signal source
    note: Voltage source goes to port 1, Current to port 2
    Options:
    'external' - receive both signals from an external source. Ensure that cables are connected to osc. ports 1 & 2 of the Digilent
    'wavegen'  - generate source from the wavegen feature of digilent. Ensure that wavegen ports are hooked to osciliscope ports
    '''
    signal_source = 'wavegen'
    # If signal_source is wavegen, include the name of the csv to read from
    wavegen_csv_source = ""

    '''
    Show graphs
    note: regardless of setting, graphs will always be saved to graph folder
    note: Graphs will be overwritten in that folder, so make sure to save them to somewhere else if desired
    Options:
    'display' - enable plt.show commands to see graphs as they are generated
    'silent'  - do not display graphs
    '''
    show_graphs = 'display'

    print("Beginning Process...")
    # Initializing Digilent communication
    try:
        print("Opening Digilent...")
        dwf, hdwf = dig_open.open()
    except Exception as e:
        print(f"Failed to connect to ADP3450 for reason: {e}")
        print("Fatal error encountered. Ending process")
        return
    # Process light
    digilent_led.turnOnLight(hdwf, dwf, 15)

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

    # Create data array
    list_of_harmonics = [(x*2)+1 for x in range(num_harmonics)]
    print(f"Frequencies: {list_of_frequencies}")
    print(f"Harmonics: {list_of_harmonics}")
    print("Printing shape of harmonic matrix. Ensure correct:")
    harmonic_matrix = np.ndarray(shape=(len(list_of_frequencies),len(list_of_harmonics)), dtype=DataNode, order='F')
    print(harmonic_matrix)

    # Send signal to begin pertubation

    sleep(2)



    print("Beginning data readings...")
    for i in range(0, len(list_of_frequencies)):
        if(signal_source == 'wavegen'):
            print("Wavegen source selected...")
            print("Loading csv...")
            from helpercsv import read_csv_column
            data1 = read_csv_column(f"./Waveforms_Volt_65356.csv", 'Battery voltage')
            data2 = read_csv_column(f"./negative_current.csv", 'Negative')
            datas = [data1, data2]

            from WF_SDK import wavegen
            print("[REPLACE WITH BATTERY] Beginning wavegen to simulate battery wave...")
            wavegen.simultaneous_generate(hdwf, 1, wavegen.function.custom,0,list_of_frequencies[i],amplitudes=[1,1], data = datas)
            print("[REPLACE WITH BATTERY] Waves generated...")
            sleep(1)

        print("Preparing to read frequency "+ str(list_of_frequencies[i]) + "Hz...")
        sampling_frequency, time_to_sample, buffer_size, sample_multiplier = dig_scope.new_presets(list_of_frequencies[i])
        print(f"Minimum sample time is {time_to_sample} seconds...")
        print(f"Sampling frequency is {sampling_frequency}...")
        print(f"Buffer size is {buffer_size}")
        try:
            buffer1, buffer2 = dig_scope.perform_simultaneous_reading(hdwf, dwf, time_to_sample, sampling_frequency, buffer_size)
            print("HEY")
            graph.raw_signal(f"{list_of_frequencies[i]}Hz_raw_signal", [buffer1, buffer2], show_graphs)
        except Exception as e:
            print(f"Read failed for reason: {e}")
            print("Fatal error. Ending process")
            digilent_led.forceLightsOff(hdwf,dwf)
            return




        print("Creating fft...")
        #import alt_fft as fft
        import helper_fft as fft
        ch1_amp, ch1_phz = fft.fft(hdwf, dwf, sampling_frequency, buffer_size, buffer1, list_of_frequencies[i], 1, show_graphs)
        ch2_amp, ch2_phz = fft.fft(hdwf, dwf, sampling_frequency, buffer_size, buffer2, list_of_frequencies[i], 2, show_graphs)

        print(f"Len of buffer: {len(ch1_amp)}")

        # Process harmonics
        digilent_led.turnOnLight(hdwf, dwf, 2)
        for j in range(0, len(list_of_harmonics)):

            curr_harmonic = list_of_harmonics[j] * list_of_frequencies[i]
            print(f"Searching for harmonic: {curr_harmonic}")

            from helper_process_harmonic import process_harmonic
            harmonic_v_magnitude, harmonic_v_phase = process_harmonic(ch1_amp, ch1_phz, curr_harmonic, list_of_frequencies[i], sample_multiplier)
            harmonic_i_magnitude, harmonic_i_phase = process_harmonic(ch2_amp, ch2_phz, curr_harmonic, list_of_frequencies[i], sample_multiplier)


            curr_node = DataNode()
            curr_node.name(list_of_frequencies[i], curr_harmonic)
            curr_node.set_data(harmonic_v_magnitude, harmonic_v_phase, harmonic_i_magnitude, harmonic_i_phase)
            harmonic_matrix[i,j] = curr_node
        digilent_led.turnOffLight(hdwf, dwf, 2)

        # Send sig nal to begin pertubation

        # input("Next pertubation")
        del ch1_amp
        del ch1_phz
        del ch2_amp
        del ch2_phz
        del data1
        del data2
        del datas
        del buffer1
        del buffer2
        gc.collect()

        print("Sending message to MCU if connected and sleeping...")
        if(connected_to_mcu):
            ser.write(b'n')
        sleep(2)


    print("Beginning data processing...")
    from helper_linkedlist import HarmonicList
    import matplotlib.pyplot as plt
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
    # print(x)
    # print(y)
    plt.plot(x,y, '-o')
    plt.show()
    ls.export("./mydata.csv")
    print("Saved to mydata.csv. Process completed. ")
    digilent_led.turnOffLight(hdwf, dwf, 15)


    digilent_led.flashSuccess(hdwf,dwf)


    return




if __name__ == '__main__':

    main()

