import time
from mpu6050 import read_mpu6050_data, calculate_azimuth
from relay_control import control_relay
from csv_operations import read_predicted_data, find_csv_file

if __name__ == "__main__":
    try:
        # Temukan file CSV di direktori Main_Folder
        directory = 'Main_Folder'  # Ganti dengan direktori yang sesuai
        csv_file = find_csv_file(directory)
        print(f"Using CSV file: {csv_file}")

        # Baca data prediksi dari file CSV
        timestamps, azimuths = read_predicted_data(os.path.join(directory, csv_file))

        while True:
            # Baca data dari MPU-6050
            accel_x, accel_y, accel_z = read_mpu6050_data()

            # Hitung azimuth dari data MPU-6050
            azimuth = calculate_azimuth(accel_x, accel_y, accel_z)
            print(f"Calculated azimuth: {azimuth}")

            # Kontrol relay berdasarkan azimuth yang diprediksi
            control_relay(azimuth)

            time.sleep(1)  # Tunggu sebelum pembacaan data berikutnya

    except KeyboardInterrupt:
        print("Program stopped by user")
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print("Unexpected error:", e)
    finally:
        # Matikan semua relay
        gpio.output(RELAY_PIN_1, gpio.LOW)
        gpio.output(RELAY_PIN_2, gpio.LOW)
        gpio.output(RELAY_PIN_3, gpio.LOW)
        gpio.output(RELAY_PIN_4, gpio.LOW)