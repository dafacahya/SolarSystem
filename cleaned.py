import os
import pandas as pd

def clean_data(year_folder):
    # Tentukan folder yang berisi data mentah
    data_folder = os.path.join('Main_Folder', year_folder, f'raw_{year_folder}')
    files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]

    if not files:
        raise FileNotFoundError(f"Tidak ada file CSV ditemukan di folder {data_folder}")

    # Loop melalui setiap file dan proses data
    for file_name in files:
        # Baca file CSV
        file_path = os.path.join(data_folder, file_name)
        df = pd.read_csv(file_path, sep=';', parse_dates=['Datetime'])

        # Proses data seperti sebelumnya
        df_cleaned = df.dropna()
        df_cleaned['Datetime'] = pd.to_datetime(df_cleaned['Datetime'])
        df_cleaned['Timestamp'] = df_cleaned['Datetime'].apply(lambda x: x.timestamp())
        df_cleaned = df_cleaned.drop(columns=['Datetime'])
        df_cleaned = df_cleaned[['Timestamp'] + [col for col in df_cleaned.columns if col != 'Timestamp']]

        df_cleaned['Timestamp'] = pd.to_numeric(df_cleaned['Timestamp'], errors='coerce')
        df_cleaned['Latitude'] = pd.to_numeric(df_cleaned['Latitude'], errors='coerce')
        df_cleaned['Longitude'] = pd.to_numeric(df_cleaned['Longitude'], errors='coerce')
        df_cleaned['Azimuth'] = round(pd.to_numeric(df_cleaned['Azimuth'], errors='coerce'), 6)
        df_cleaned['Altitude'] = round(pd.to_numeric(df_cleaned['Altitude'], errors='coerce'), 6)

        # Buat folder cleaned_tahun jika belum ada
        cleaned_folder = os.path.join('Main_Folder', year_folder, f'cleaned_{year_folder}')
        if not os.path.exists(cleaned_folder):
            os.makedirs(cleaned_folder)

        # Simpan data yang sudah dibersihkan
        cleaned_data_path = os.path.join(cleaned_folder, f"{year_folder}.csv")
        df_cleaned.to_csv(cleaned_data_path, index=False, sep=';')

        print(f"Data dari file {file_name} sudah dibersihkan dan disimpan di: {cleaned_data_path}")

# Input folder tahun yang akan dibersihkan
year_to_clean = input("Masukkan nama folder tahun yang ingin dibersihkan (contoh: 2020): ")
clean_data(year_to_clean)
