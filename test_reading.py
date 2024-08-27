
import digilent_scope as dig_scope
import digilent_system_functions as dig_open
import helper_graph as graph

show_graphs = 'display'
try:
    print("Opening Digilent...")
    dwf, hdwf = dig_open.open()
except Exception as e:
    print(f"Failed to connect to ADP3450 for reason: {e}")
    print("Fatal error encountered. Ending process")
    

list_of_frequencies = [.1,1,5,10,100,1000,5000]


for i in range(0, len(list_of_frequencies)):
    input("Enter to go")
    sampling_frequency, time_to_sample, buffer_size = dig_scope.new_presets(list_of_frequencies[i])
    print(f"Minimum sample time is {time_to_sample} seconds...")
    print(f"Sampling frequency is {sampling_frequency}...")
    print(f"Buffer size is {buffer_size}")
    try: 
        buffer1, buffer2 = dig_scope.perform_simultaneous_reading(hdwf, dwf, time_to_sample, sampling_frequency, buffer_size)
        graph.raw_signal(f"{list_of_frequencies[i]}Hz_raw_signal", [buffer1, buffer2], show_graphs)
    except Exception as e:
        print(f"Read failed for reason: {e}")
        print("Fatal error. Ending process")