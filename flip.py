import csv

# Define a function to read a CSV file and extract numeric values from a specific column
def read_csv_column(file_path, column_name):
    values = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                value = float(row[column_name])
                values.append(value)
            except ValueError:
                # Handle the case where conversion to float fails
                pass
    return values

# Paths to the CSV files
file_path1 = "C:\\Users\\WEDES-1\\Desktop\\ADP-Linux\\Waveforms_Volt_65356.csv"
file_path2 = "C:\\Users\\WEDES-1\\Desktop\\ADP-Linux\\negative.csv"

# Read the values from the specified columns
data1vals = read_csv_column(file_path1, 'Battery voltage')
data2vals = read_csv_column(file_path2, 'Negative')

# Combine the lists into one list
datas = [data1vals, data2vals]

