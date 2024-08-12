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

