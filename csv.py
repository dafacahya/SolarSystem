import csv
import subprocess

def read_csv(file_path):
    data = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row)
    return data

# Baca data dari CSV
file_path = 'Main_Folder/predictions_2024_to_2028.csv'
csv_data = read_csv(file_path)

# Kirim data ke program C
for row in csv_data:
    azimuth = row['Predict_Azimuth']
    altitude = row['Predict_Altitude']
    
    # Menjalankan program C dengan mengirim data sebagai argumen
    subprocess.run(['./control', azimuth, altitude])