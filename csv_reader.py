import subprocess
import time
import pandas as pd
import os

# Fungsi untuk membaca data prediksi dari file CSV
def read_predicted_data(csv_file):
    df = pd.read_csv(csv_file, sep=';')
    timestamps = pd.to_datetime(df['Timestamp'], format='%Y-%m-%d %H:%M:%S')
    azimuths = df['Azimuth'].apply(lambda x: float(x[:-1])).values  # Hapus karakter ° dan ubah ke float
    altitudes = df['Altitude'].apply(lambda x: float(x[:-1])).values  # Hapus karakter ° dan ubah ke float
    return timestamps, azimuths, altitudes

if __name__ == "__main__":
    try:
        # Tentukan file CSV di direktori Main_Folder
        directory = 'Main_Folder'  # Ganti dengan direktori yang sesuai
        csv_file = 'predictions_2024_to_2026.csv'
        csv_file_path = os.path.join(directory, csv_file)
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"No CSV file found at {csv_file_path}")

        print(f"Using CSV file: {csv_file_path}")

        while True:
            # Baca data prediksi dari file CSV
            timestamps, azimuths, altitudes = read_predicted_data(csv_file_path)

            # Ambil nilai azimuth dan altitude terbaru
            predicted_azimuth = azimuths[-1]
            predicted_altitude = altitudes[-1]

            # Panggil executable C untuk mengendalikan relay
            subprocess.call(["./control_relay"])

            time.sleep(1)  # Tunggu sebelum membaca data berikutnya

    except KeyboardInterrupt:
        print("Program stopped by user")
    except FileNotFoundError as e:
        print(e)
    finally:
        print("Cleaning up...")
        # Lakukan pembersihan jika diperlukan
