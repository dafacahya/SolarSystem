import smbus
import time

# Alamat I2C dari MPU6050
MPU6050_ADDR = 0x68

# Register dari MPU6050
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47

# Inisialisasi I2C bus
bus = smbus.SMBus(1)

def MPU_Init():
    # Menulis ke register manajemen daya untuk membangunkan sensor
    bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)
    # Mengatur register sample rate divider
    bus.write_byte_data(MPU6050_ADDR, SMPLRT_DIV, 7)
    # Mengatur register konfigurasi
    bus.write_byte_data(MPU6050_ADDR, CONFIG, 0)
    # Mengatur register konfigurasi giroskop
    bus.write_byte_data(MPU6050_ADDR, GYRO_CONFIG, 24)
    # Mengatur register konfigurasi akselerometer
    bus.write_byte_data(MPU6050_ADDR, ACCEL_CONFIG, 0)
    # Mengatur register interrupt enable
    bus.write_byte_data(MPU6050_ADDR, INT_ENABLE, 1)

def read_raw_data(addr):
    # Membaca nilai 16-bit dari register
    high = bus.read_byte_data(MPU6050_ADDR, addr)
    low = bus.read_byte_data(MPU6050_ADDR, addr + 1)
    value = (high << 8) | low
    if value > 32768:
        value = value - 65536
    return value

# Inisialisasi MPU6050
MPU_Init()

try:
    while True:
        # Membaca data akselerometer
        acc_x = read_raw_data(ACCEL_XOUT_H)
        acc_y = read_raw_data(ACCEL_YOUT_H)
        acc_z = read_raw_data(ACCEL_ZOUT_H)

        # Mengonversi data akselerometer menjadi g-force
        Ax = acc_x / 16384.0
        Ay = acc_y / 16384.0
        Az = acc_z / 16384.0

        # Membaca data giroskop
        gyro_x = read_raw_data(GYRO_XOUT_H)
        gyro_y = read_raw_data(GYRO_YOUT_H)
        gyro_z = read_raw_data(GYRO_ZOUT_H)

        # Mengonversi data giroskop menjadi derajat per detik
        Gx = gyro_x / 131.0
        Gy = gyro_y / 131.0
        Gz = gyro_z / 131.0

        # Menampilkan hasil pembacaan
        print(f"Ax={Ax:.2f}g Ay={Ay:.2f}g Az={Az:.2f}g Gx={Gx:.2f}°/s Gy={Gy:.2f}°/s Gz={Gz:.2f}°/s")

        # Tunggu 0.5 detik sebelum membaca lagi
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Program dihentikan oleh pengguna.")
