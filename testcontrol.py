import smbus
import time
from pyA20.gpio import gpio
from pyA20.gpio import port

# Inisialisasi SMBus untuk komunikasi I2C dengan MPU-6050
bus = smbus.SMBus(1)  # Jika menggunakan Orange Pi, gunakan SMBus(0)

# Alamat I2C dari MPU-6050
MPU6050_ADDR = 0x68

# Register MPU-6050 untuk data akselerometer
MPU6050_REG_ACCEL_XOUT_H = 0x3B
MPU6050_REG_ACCEL_YOUT_H = 0x3D
MPU6050_REG_ACCEL_ZOUT_H = 0x3F

# Konfigurasi pin GPIO untuk relay
RELAY_PIN_1 = port.PI0  # Ganti dengan pin GPIO yang sesuai

# Inisialisasi GPIO
gpio.init()
gpio.setcfg(RELAY_PIN_1, gpio.OUTPUT)

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

if __name__ == "__main__":
    try:
        while True:
            accel_x, accel_y, accel_z = read_mpu6050_data()
            print(f"Accel X: {accel_x}, Accel Y: {accel_y}, Accel Z: {accel_z}")

            gpio.output(RELAY_PIN_1, gpio.HIGH)
            time.sleep(1)
            gpio.output(RELAY_PIN_1, gpio.LOW)
            time.sleep(1)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        gpio.output(RELAY_PIN_1, gpio.LOW)
        gpio.cleanup()
