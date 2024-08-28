import matplotlib.pyplot as plt
import os

def raw_signal(filename : str, data, showGraph): 
    if(not filename.endswith(".png")):
        filename = filename + ".png"
 #   print("MY")
    plt.plot(data[0], color="blue")
  #  print("MOTHER")
    plt.plot(data[1], color="red")
   # print("FREAKING")
    plt.title("Raw signal, channel 1 in blue, channel 2 in red")

    file_path = os.path.join(".", "graphs", filename)
    plt.savefig(file_path)
    print("GOODNESS")
    if(showGraph == 'display'):
        plt.show()
    plt.clf()
    
