import pandas as pd
# *** Load in custom waveforms here, if desired
# If you desire to read form an external source, no changes to the code are required. Simply connect the oscilliscopes to the external device. 

data2 = pd.read_csv(f"C:\\Users\\WEDES-1\\Desktop\\ADP-Linux\\Waveforms_Current_65356.csv")

data2vals = pd.to_numeric(data2['Battery current'], downcast='float').to_list()
negatives = [-value for value in data2vals]


newdf = pd.DataFrame(data=negatives)
newdf.to_csv(".\\negative.csv")


