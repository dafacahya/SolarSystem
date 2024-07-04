import pandas as pd
import os

def read_predicted_data(csv_file):
    df = pd.read_csv(csv_file, sep=';')
    timestamps = pd.to_datetime(df['Timestamp'], format='%Y-%m-%d %H:%M:%S')
    azimuths = df['Azimuth'].apply(lambda x: float(x[:-1])).values  # Hapus karakter ° dan ubah ke float
    return timestamps, azimuths

def find_csv_file(directory):
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    if csv_files:
        return csv_files[0]  # Pilih file pertama yang ditemukan
    else:
        raise FileNotFoundError("No CSV file found in the directory.")
