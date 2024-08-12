from math import sin, cos, pi
class DataNode:
    def __init__(self):
        self.frequency : int =0
        self.harmonic : int =0
        
        self.voltage_magnitude : float = 0.0
        self.voltage_phase : float = 0.0
        self.current_magnitude : float = 0.0
        self.current_phase : float = 0.0

        self.z_mag : float = 0.0
        self.z_ph : float = 0.0
        self.z_real : float = 0.0
        self.z_img : float = 0.0

        self.test = 0

    def __str__(self):
        return(f"({self.frequency},{self.harmonic})")
   

    def name(self, freq, harm):
        self.frequency = freq
        self.harmonic  = harm

    def set_data(self, volt_mag :float, volt_phase: float, curr_mag:float, curr_phase:float):
        self.voltage_magnitude=volt_mag
        self.voltage_phase=volt_phase
        self.current_magnitude=curr_mag
        self.current_phase=curr_phase

        self.z_mag = self.voltage_magnitude / self.current_magnitude
        self.z_ph = self.voltage_phase - self.current_phase
        self.z_real = self.z_mag * self.degreeCosine(self.z_ph)
        self.z_img = (-self.z_mag) * self.degreeSine(self.z_ph)

    def degreeCosine(self, degrees : float):
        radians = degrees * pi / 180.0
        return cos(radians)

    def degreeSine(self, degrees : float):
        radians = degrees * pi / 180.0
        return sin(radians)
        

        


    
        