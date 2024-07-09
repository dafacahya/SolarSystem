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

def find_csv_file(directory):
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    if csv_files:
        return csv_files[0]  # Pilih file pertama yang ditemukan
    else:
        raise FileNotFoundError("No CSV file found in the directory.")

if __name__ == "__main__":
    try:
        # Temukan file CSV di direktori Main_Folder
        directory = 'Main_Folder'  # Ganti dengan direktori yang sesuai
        csv_file = find_csv_file(directory)
        print(f"Using CSV file: {csv_file}")

        while True:
            # Baca data prediksi dari file CSV
            timestamps, azimuths, altitudes = read_predicted_data(os.path.join(directory, csv_file))

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
