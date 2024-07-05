import csv
from datetime import datetime
import time
from gpiozero import DigitalOutputDevice
import smbus
import math

# Konfigurasi pin GPIO untuk relay azimuth (pan) dan altitude (tilt)
RELAY_PIN_AZIMUTH_UP = 20
RELAY_PIN_AZIMUTH_DOWN = 22
RELAY_PIN_ALTITUDE_UP = 23
RELAY_PIN_ALTITUDE_DOWN = 25

# Inisialisasi GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN_AZIMUTH_UP, GPIO.OUT)
GPIO.setup(RELAY_PIN_AZIMUTH_DOWN, GPIO.OUT)
GPIO.setup(RELAY_PIN_ALTITUDE_UP, GPIO.OUT)
GPIO.setup(RELAY_PIN_ALTITUDE_DOWN, GPIO.OUT)

# Alamat I2C dari MPU-6050
MPU6050_ADDR = 0x68

# Register MPU-6050 untuk data akselerometer
MPU6050_REG_ACCEL_XOUT_H = 0x3B
MPU6050_REG_ACCEL_YOUT_H = 0x3D
MPU6050_REG_ACCEL_ZOUT_H = 0x3F

# Inisialisasi I2C bus
bus = smbus.SMBus(1)

# Fungsi untuk membaca data dari MPU-6050
def read_mpu6050_data():
    accel_x = read_word_2c(MPU6050_REG_ACCEL_XOUT_H)
    accel_y = read_word_2c(MPU6050_REG_ACCEL_YOUT_H)
    accel_z = read_word_2c(MPU6050_REG_ACCEL_ZOUT_H)
    return accel_x, accel_y, accel_z

# Fungsi pembantu untuk membaca nilai signed 16-bit dari MPU-6050
def read_word_2c(reg):
    high = bus.read_byte_data(MPU6050_ADDR, reg)
    low = bus.read_byte_data(MPU6050_ADDR, reg+1)
    val = (high << 8) + low
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

# Fungsi untuk menghitung azimuth (pan) berdasarkan data MPU-6050
def calculate_azimuth(accel_x, accel_y, accel_z):
    roll = math.atan2(accel_y, accel_z)
    azimuth = math.degrees(roll)
    if azimuth < 0:
        azimuth += 360.0
    return azimuth

# Fungsi untuk menghitung altitude (tilt) berdasarkan data MPU-6050
def calculate_altitude(accel_x, accel_y, accel_z):
    pitch = math.atan2(-accel_x, math.sqrt(accel_y * accel_y + accel_z * accel_z))
    altitude = math.degrees(pitch)
    if altitude < 0:
        altitude += 360.0
    return altitude

# Fungsi untuk membaca prediksi dari file CSV
def read_predictions_from_csv(filename):
    predictions = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 4:
                date_str, time_str, predict_azimuth, predict_altitude = row
                try:
                    timestamp = datetime.strptime(f'{date_str} {time_str}', '%Y-%m-%d %H:%M:%S')
                    predictions.append({
                        'timestamp': timestamp,
                        'azimuth': float(predict_azimuth),
                        'altitude': float(predict_altitude)
                    })
                except ValueError as e:
                    print(f"Error parsing line: {row}, Error: {e}")
    return predictions

# Fungsi untuk mendapatkan waktu saat ini dalam timestamp
def get_current_time():
    return datetime.now()

# Fungsi untuk menggerakkan relay azimuth (pan) berdasarkan azimuth yang diprediksi
def control_azimuth_relay(predicted_azimuth, current_azimuth):
    if abs(predicted_azimuth - current_azimuth) > 5:  # Contoh threshold perubahan sudut
        if predicted_azimuth < current_azimuth:
            GPIO.output(RELAY_PIN_AZIMUTH_UP, False)
            GPIO.output(RELAY_PIN_AZIMUTH_DOWN, True)
        else:
            GPIO.output(RELAY_PIN_AZIMUTH_UP, True)
            GPIO.output(RELAY_PIN_AZIMUTH_DOWN, False)
    else:
        GPIO.output(RELAY_PIN_AZIMUTH_UP, False)
        GPIO.output(RELAY_PIN_AZIMUTH_DOWN, False)

# Fungsi untuk menggerakkan relay altitude (tilt) berdasarkan altitude yang diprediksi
def control_altitude_relay(predicted_altitude, current_altitude):
    if abs(predicted_altitude - current_altitude) > 5:  # Contoh threshold perubahan sudut
        if predicted_altitude < current_altitude:
            GPIO.output(RELAY_PIN_ALTITUDE_UP, False)
            GPIO.output(RELAY_PIN_ALTITUDE_DOWN, True)
        else:
            GPIO.output(RELAY_PIN_ALTITUDE_UP, True)
            GPIO.output(RELAY_PIN_ALTITUDE_DOWN, False)
    else:
        GPIO.output(RELAY_PIN_ALTITUDE_UP, False)
        GPIO.output(RELAY_PIN_ALTITUDE_DOWN, False)

if __name__ == "__main__":
    try:
        # Baca prediksi dari CSV
        predictions = read_predictions_from_csv('predictions.csv')

        # Loop utama untuk membandingkan data dari MPU-6050 dengan prediksi dari CSV
        while True:
            accel_x, accel_y, accel_z = read_mpu6050_data()
            current_azimuth = calculate_azimuth(accel_x, accel_y, accel_z)
            current_altitude = calculate_altitude(accel_x, accel_y, accel_z)
            current_time = get_current_time()

            # Cari prediksi terdekat berdasarkan waktu saat ini
            closest_prediction = None
            for prediction in predictions:
                if prediction['timestamp'] <= current_time:
                    closest_prediction = prediction
                else:
                    break

            if closest_prediction:
                predicted_azimuth = closest_prediction['azimuth']
                predicted_altitude = closest_prediction['altitude']

                # Kendalikan relay berdasarkan prediksi
                control_azimuth_relay(predicted_azimuth, current_azimuth)
                control_altitude_relay(predicted_altitude, current_altitude)

            time.sleep(1)  # Tunggu sebelum membaca data berikutnya

    except KeyboardInterrupt:
        print("Program dihentikan secara manual")
    finally:
        GPIO.cleanup()  # Bersihkan GPIO saat program berhenti
