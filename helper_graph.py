import matplotlib.pyplot as plt
import os

def raw_signal(filename : str, data, showGraph): 
    if(not filename.endswith(".png")):
        filename = filename + ".png"
    plt.clf() 
    plt.plot(data[0], color="blue")
 
    plt.plot(data[1], color="red")
 
    plt.title("Raw signal, channel 1 in blue, channel 2 in red")

    file_path = os.path.join(".", "graphs", filename)
    plt.savefig(file_path)
    if(showGraph == 'display'):
        plt.show()
    plt.clf()
    
