from structure_node import DataNode

class ListNode:
    def __init__(self, obj) -> None:
        self.node = obj
        self.next = None

class HarmonicList:
    def __init__(self):
        self.head = None
        self.size = 0

    '''
    Inserts in order
    Returns
        0 - Insert successful
        1 - Node already exists in list, so discarding
    '''
    def insert_in_order(self, node : DataNode):
        if(self.size == 0):
            item = ListNode(node)
            self.head = item
            
            self.size = self.size + 1
            return 0
        else:
            current = self.head
            previous = None
            while(current != None and node.harmonic > current.node.harmonic):
                previous = current
                current = current.next
            if(current != None and node.harmonic == current.node.harmonic):
                print(f"Throwing out {node.frequency},{node.harmonic}")
                return 1
            else:
                item = ListNode(node)
                previous.next = item
                item.next = current

                self.size = self.size + 1
                return 0
            

        

    def print_list(self):
        print(f"Size is {self.size}")
        current = self.head
        print("f,h")
        while(current != None):
            print(current.node)
            
            current = current.next
        print("End of list")



    def export(self, filename : str):
        if not filename.endswith(".csv"):
            filename += ".csv"


        print(f"saving to {filename}")

        current = self.head
        # Headers
        data = [['Frequency', 'Harmonic', 'Voltage Magnitude',' Voltage Phase',' Current Magnitude', 'Current Phase', 'Impedance Magnitude', 'Impedance Phase', 'Z Real', 'Z Imaginary']]

        while(current != None):
            node = current.node
            row = [node.frequency, node.harmonic, node.voltage_magnitude, node.voltage_phase, node.current_magnitude, node.current_phase,node.z_mag, node.z_ph, node.z_real, node.z_img]
            data.append(row)

            current = current.next
        
        with open(filename, 'w') as file:
            for row in data:
                file.write(','.join(map(str,row)) + '\n')
                
        
        


    def get_impedance_lists(self):
        imp_mag = []
        imp_phz = []
        current = self.head
       
        while(current != None):
            imp_mag.append(current.node.z_mag)
            imp_phz.append(current.node.z_ph)

            current = current.next
        return imp_mag, imp_phz

    # returns [z_reals, z_imgs]
    def z_lists(self):
        z_r = []
        z_i = []
        current = self.head
       
        while(current != None):
            z_r.append(current.node.z_real)
            z_i.append(current.node.z_img)

            current = current.next
        return z_r, z_i
    
    def get_freqs_and_harmonics(self):
        freqs = []
        harms = []
        current = self.head
       
        while(current != None):
            freqs.append(current.node.frequency)
            harms.append(current.node.harmonic)

            current = current.next
        return freqs,harms


         
            


    
        