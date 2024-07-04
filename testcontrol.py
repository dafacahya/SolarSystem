import wiringpi
import time
from math import atan2, degrees, sin, cos
import pandas as pd
import numpy as np

# Alamat I2C dari MPU-6050
MPU6050_ADDR = 0x68

# Register MPU-6050 untuk data akselerometer dan gyroscope
MPU6050_REG_ACCEL_XOUT_H = 0x3B
MPU6050_REG_ACCEL_YOUT_H = 0x3D
MPU6050_REG_ACCEL_ZOUT_H = 0x3F

# Konfigurasi pin GPIO untuk relay
RELAY_PIN_1 = 19  # Ganti dengan pin GPIO yang sesuai (misalnya BCM: 17)
RELAY_PIN_2 = 20  # Ganti dengan pin GPIO yang sesuai (misalnya BCM: 18)
RELAY_PIN_3 = 22  # Ganti dengan pin GPIO yang sesuai (misalnya BCM: 27)
RELAY_PIN_4 = 23  # Ganti dengan pin GPIO yang sesuai (misalnya BCM: 22)

# Inisialisasi pin relay sebagai output
wiringpi.pinMode(RELAY_PIN_1, wiringpi.OUTPUT)
wiringpi.pinMode(RELAY_PIN_2, wiringpi.OUTPUT)
wiringpi.pinMode(RELAY_PIN_3, wiringpi.OUTPUT)
wiringpi.pinMode(RELAY_PIN_4, wiringpi.OUTPUT)

# Fungsi untuk membaca data dari MPU-6050
def read_mpu6050_data():
    def read_word(reg):
        high = wiringpi.wiringPiI2CReadReg8(fd, reg)
        low = wiringpi.wiringPiI2CReadReg8(fd, reg + 1)
        value = (high << 8) + low
        if value >= 0x8000:
            value = -((65535 - value) + 1)
        return value

    fd = wiringpi.wiringPiI2CSetup(MPU6050_ADDR)
    accel_x = read_word(MPU6050_REG_ACCEL_XOUT_H)
    accel_y = read_word(MPU6050_REG_ACCEL_YOUT_H)
    accel_z = read_word(MPU6050_REG_ACCEL_ZOUT_H)
    return accel_x, accel_y, accel_z

# Fungsi untuk menggerakkan relay berdasarkan azimuth
def control_relay(predicted_azimuth):
    if predicted_azimuth < 90:
        wiringpi.digitalWrite(RELAY_PIN_1, wiringpi.HIGH)
        time.sleep(1)
        wiringpi.digitalWrite(RELAY_PIN_1, wiringpi.LOW)
    elif predicted_azimuth < 180:
        wiringpi.digitalWrite(RELAY_PIN_2, wiringpi.HIGH)
        time.sleep(1)
        wiringpi.digitalWrite(RELAY_PIN_2, wiringpi.LOW)
    elif predicted_azimuth < 270:
        wiringpi.digitalWrite(RELAY_PIN_3, wiringpi.HIGH)
        time.sleep(1)
        wiringpi.digitalWrite(RELAY_PIN_3, wiringpi.LOW)
    else:
        wiringpi.digitalWrite(RELAY_PIN_4, wiringpi.HIGH)
        time.sleep(1)
        wiringpi.digitalWrite(RELAY_PIN_4, wiringpi.LOW)

# Fungsi untuk menghitung azimuth berdasarkan data MPU-6050
def calculate_azimuth(accel_x, accel_y, accel_z):
    roll = atan2(accel_y, accel_z)
    azimuth = degrees(roll)
    return azimuth

if __name__ == "__main__":
    try:
        while True:
            # Baca data dari MPU-6050
            accel_x, accel_y, accel_z = read_mpu6050_data()

            # Hitung azimuth dari data MPU-6050
            azimuth = calculate_azimuth(accel_x, accel_y, accel_z)

            # Kontrol relay berdasarkan azimuth yang diprediksi
            control_relay(azimuth)

            time.sleep(1)  # Tunggu sebelum pembacaan data berikutnya

    except KeyboardInterrupt:
        print("Program stopped by user")
    finally:
        # Matikan semua relay
        wiringpi.digitalWrite(RELAY_PIN_1, wiringpi.LOW)
        wiringpi.digitalWrite(RELAY_PIN_2, wiringpi.LOW)
        wiringpi.digitalWrite(RELAY_PIN_3, wiringpi.LOW)
        wiringpi.digitalWrite(RELAY_PIN_4, wiringpi.LOW)
