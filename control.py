import smbus
import time
from math import atan2, degrees, sin, cos
import pandas as pd
import numpy as np
import os
from pyA20.gpio import gpio
from pyA20.gpio import port

# Inisialisasi SMBus untuk komunikasi I2C dengan MPU-6050
bus = smbus.SMBus(1)  # Jika menggunakan Orange Pi, gunakan SMBus(0)

# Alamat I2C dari MPU-6050
MPU6050_ADDR = 0x68

# Register MPU-6050 untuk data akselerometer dan gyroscope
MPU6050_REG_ACCEL_XOUT_H = 0x3B
MPU6050_REG_ACCEL_YOUT_H = 0x3D
MPU6050_REG_ACCEL_ZOUT_H = 0x3F

# Konfigurasi pin GPIO untuk relay
RELAY_PIN_1 = port.PI1  # Ganti dengan pin GPIO yang sesuai
RELAY_PIN_2 = port.PI4  # Ganti dengan pin GPIO yang sesuai
RELAY_PIN_3 = port.PI2  # Ganti dengan pin GPIO yang sesuai
RELAY_PIN_4 = port.PC12  # Ganti dengan pin GPIO yang sesuai

# Inisialisasi pin relay sebagai output
gpio.init()
gpio.setcfg(RELAY_PIN_1, gpio.OUTPUT)
gpio.setcfg(RELAY_PIN_2, gpio.OUTPUT)
gpio.setcfg(RELAY_PIN_3, gpio.OUTPUT)
gpio.setcfg(RELAY_PIN_4, gpio.OUTPUT)

# Fungsi untuk membaca data dari MPU-6050
def read_mpu6050_data():
    def read_word(reg):
        high = bus.read_byte_data(MPU6050_ADDR, reg)
        low = bus.read_byte_data(MPU6050_ADDR, reg + 1)
        value = (high << 8) + low
        if value >= 0x8000:
            value = -((65535 - value) + 1)
        return value

    accel_x = read_word(MPU6050_REG_ACCEL_XOUT_H)
    accel_y = read_word(MPU6050_REG_ACCEL_YOUT_H)
    accel_z = read_word(MPU6050_REG_ACCEL_ZOUT_H)

    return accel_x, accel_y, accel_z

# Fungsi untuk menggerakkan relay berdasarkan azimuth dan altitude
def control_relay(predicted_azimuth, predicted_altitude):
    if predicted_azimuth < 90:
        gpio.output(RELAY_PIN_1, gpio.HIGH)
        time.sleep(1)
        gpio.output(RELAY_PIN_1, gpio.LOW)
    elif predicted_azimuth < 180:
        gpio.output(RELAY_PIN_2, gpio.HIGH)
        time.sleep(1)
        gpio.output(RELAY_PIN_2, gpio.LOW)
    elif predicted_azimuth < 270:
        gpio.output(RELAY_PIN_3, gpio.HIGH)
        time.sleep(1)
        gpio.output(RELAY_PIN_3, gpio.LOW)
    else:
        gpio.output(RELAY_PIN_4, gpio.HIGH)
        time.sleep(1)
        gpio.output(RELAY_PIN_4, gpio.LOW)

# Fungsi untuk menghitung azimuth dan altitude berdasarkan data MPU-6050
def calculate_azimuth_altitude(accel_x, accel_y, accel_z):
    roll = atan2(accel_y, accel_z)
    pitch = atan2(-accel_x, (accel_y * sin(roll) + accel_z * cos(roll)))
    azimuth = degrees(roll)
    altitude = degrees(pitch)
    return azimuth, altitude

# Fungsi untuk membaca data prediksi dari file CSV
def read_predicted_data(csv_file):
    df = pd.read_csv(csv_file, sep=';')
    timestamps = pd.to_datetime(df['Timestamp'], format='%Y-%m-%d %H:%M:%S')
    azimuths = df['Azimuth'].apply(lambda x: float(x[:-1])).values  # Hapus karakter ° dan ubah ke float
    altitudes = df['Altitude'].apply(lambda x: float(x[:-1])).values  # Hapus karakter ° dan ubah ke float
    return timestamps, azimuths, altitudes

# Fungsi untuk mendapatkan data prediksi untuk waktu sekarang
def get_predicted_data_now(timestamps, azimuths, altitudes, current_time):
    # Temukan data prediksi terdekat dengan waktu sekarang
    idx = np.abs((timestamps - current_time)).argmin()
    return azimuths[idx], altitudes[idx]

# Fungsi untuk menemukan file CSV di direktori tertentu
def find_csv_file(directory):
    csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
    if csv_files:
        return csv_files[0]  # Pilih file pertama yang ditemukan
    else:
        raise FileNotFoundError("No CSV file found in the directory.")

if __name__ == "__main__":
    try:
        # Temukan file CSV di direktori saat ini
        directory = '.'  # Ganti dengan direktori yang sesuai jika perlu
        csv_file = find_csv_file(directory)
        print(f"Using CSV file: {csv_file}")

        # Baca data prediksi dari file CSV
        timestamps, azimuths, altitudes = read_predicted_data(csv_file)

        while True:
            # Baca data dari MPU-6050
            accel_x, accel_y, accel_z = read_mpu6050_data()

            # Hitung azimuth dan altitude dari data MPU-6050
            azimuth, altitude = calculate_azimuth_altitude(accel_x, accel_y, accel_z)

            # Dapatkan data prediksi untuk waktu sekarang
            current_time = pd.Timestamp.now()  # Waktu sekarang dalam format pandas Timestamp
            predicted_azimuth, predicted_altitude = get_predicted_data_now(timestamps, azimuths, altitudes, current_time)

            # Kontrol relay berdasarkan azimuth dan altitude yang diprediksi
            control_relay(predicted_azimuth, predicted_altitude)

            time.sleep(1)  # Tunggu sebelum pembacaan data berikutnya

    except KeyboardInterrupt:
        print("Program stopped by user")
    except FileNotFoundError as e:
        print(e)
    finally:
        # Matikan semua relay dan atur pin GPIO ke kondisi awal
        gpio.output(RELAY_PIN_1, gpio.LOW)
        gpio.output(RELAY_PIN_2, gpio.LOW)
        gpio.output(RELAY_PIN_3, gpio.LOW)
        gpio.output(RELAY_PIN_4, gpio.LOW)
        gpio.cleanup()
