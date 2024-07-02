import smbus
import OPi.GPIO as GPIO
import time
from math import atan2, degrees
import pandas as pd
import numpy as np

# Inisialisasi SMBus untuk komunikasi I2C dengan MPU-6050
bus = smbus.SMBus(1)  # Jika menggunakan Orange Pi, gunakan SMBus(0)

# Alamat I2C dari MPU-6050
MPU6050_ADDR = 0x68

# Register MPU-6050 untuk data akselerometer dan gyroscope
MPU6050_REG_ACCEL_XOUT_H = 0x3B
MPU6050_REG_ACCEL_YOUT_H = 0x3D
MPU6050_REG_ACCEL_ZOUT_H = 0x3F

MPU6050_REG_GYRO_XOUT_H = 0x43
MPU6050_REG_GYRO_YOUT_H = 0x45
MPU6050_REG_GYRO_ZOUT_H = 0x47

# Konfigurasi pin GPIO untuk relay PWM 4 channel
GPIO.setmode(GPIO.BOARD)  # Gunakan penomoran pin fisik
PWM_PIN_1 = 11  # Ganti dengan pin GPIO yang sesuai
PWM_PIN_2 = 12  # Ganti dengan pin GPIO yang sesuai
PWM_PIN_3 = 13  # Ganti dengan pin GPIO yang sesuai
PWM_PIN_4 = 15  # Ganti dengan pin GPIO yang sesuai

# Atur frekuensi PWM (dalam Hz)
PWM_FREQUENCY = 50  # Contoh frekuensi 50 Hz

# Inisialisasi saluran PWM
GPIO.setup(PWM_PIN_1, GPIO.OUT)
GPIO.setup(PWM_PIN_2, GPIO.OUT)
GPIO.setup(PWM_PIN_3, GPIO.OUT)
GPIO.setup(PWM_PIN_4, GPIO.OUT)

pwm1 = GPIO.PWM(PWM_PIN_1, PWM_FREQUENCY)
pwm2 = GPIO.PWM(PWM_PIN_2, PWM_FREQUENCY)
pwm3 = GPIO.PWM(PWM_PIN_3, PWM_FREQUENCY)
pwm4 = GPIO.PWM(PWM_PIN_4, PWM_FREQUENCY)

# Fungsi untuk membaca data dari MPU-6050
def read_mpu6050_data():
    def read_word(reg):
        high = bus.read_byte_data(MPU6050_ADDR, reg)
        low = bus.read_byte_data(MPU6050_ADDR, reg + 1)
        value = (high << 8) + low
        return value

    accel_x = read_word(MPU6050_REG_ACCEL_XOUT_H)
    accel_y = read_word(MPU6050_REG_ACCEL_YOUT_H)
    accel_z = read_word(MPU6050_REG_ACCEL_ZOUT_H)

    gyro_x = read_word(MPU6050_REG_GYRO_XOUT_H)
    gyro_y = read_word(MPU6050_REG_GYRO_YOUT_H)
    gyro_z = read_word(MPU6050_REG_GYRO_ZOUT_H)

    return accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z

# Fungsi untuk menggerakkan aktuator pada saluran PWM tertentu
def move_actuator_pwm(pwm_channel, duty_cycle):
    pwm_channel.start(duty_cycle)
    time.sleep(1)  # Durasi gerakan
    pwm_channel.stop()

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

# Fungsi untuk mendapatkan data prediksi untuk waktu sekarang (contoh sederhana)
def get_predicted_data_now(timestamps, azimuths, altitudes, current_time):
    # Temukan data prediksi terdekat dengan waktu sekarang
    idx = np.abs((timestamps - current_time)).argmin()
    return azimuths[idx], altitudes[idx]

if __name__ == "__main__":
    try:
        # Baca data prediksi dari file CSV
        csv_file = 'predictions_2025.csv'  # Ganti dengan nama file CSV Anda
        timestamps, azimuths, altitudes = read_predicted_data(csv_file)

        while True:
            # Baca data dari MPU-6050
            accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z = read_mpu6050_data()

            # Hitung azimuth dan altitude dari data MPU-6050
            azimuth, altitude = calculate_azimuth_altitude(accel_x, accel_y, accel_z)

            # Dapatkan data prediksi untuk waktu sekarang
            current_time = time.time()  # Waktu sekarang dalam format UNIX timestamp
            predicted_azimuth, predicted_altitude = get_predicted_data_now(timestamps, azimuths, altitudes, current_time)

            # Koreksi gerakan berdasarkan data azimuth dan altitude
            # Misalnya, sesuaikan nilai duty cycle PWM berdasarkan nilai azimuth dan altitude
            # Contoh: Gerakkan aktuator pada saluran PWM 1 dengan siklus tugas 50%
            move_actuator_pwm(pwm1, 50)

            time.sleep(5)  # Tunggu sebelum menggerakkan aktuator berikutnya

    except KeyboardInterrupt:
        print("Program stopped by user")
    finally:
        # Matikan PWM dan atur pin GPIO ke kondisi awal
        pwm1.stop()
        pwm2.stop()
        pwm3.stop()
        pwm4.stop()
        GPIO.cleanup()
