import time
from math import atan2, degrees
from pyA20.i2c import i2c

# Alamat I2C dari MPU-6050
MPU6050_ADDR = 0x68

# Register MPU-6050 untuk data akselerometer dan gyroscope
MPU6050_REG_ACCEL_XOUT_H = 0x3B
MPU6050_REG_ACCEL_YOUT_H = 0x3D
MPU6050_REG_ACCEL_ZOUT_H = 0x3F

def read_mpu6050_data():
    def read_word(reg):
        high = i2c.read_u8(reg)
        low = i2c.read_u8(reg + 1)
        value = (high << 8) + low
        if value >= 0x8000:
            value = -((65535 - value) + 1)
        return value

    i2c.init("/dev/i2c-0")
    i2c.open(MPU6050_ADDR)
    accel_x = read_word(MPU6050_REG_ACCEL_XOUT_H)
    accel_y = read_word(MPU6050_REG_ACCEL_YOUT_H)
    accel_z = read_word(MPU6050_REG_ACCEL_ZOUT_H)
    return accel_x, accel_y, accel_z

def calculate_azimuth(accel_x, accel_y, accel_z):
    roll = atan2(accel_y, accel_z)
    azimuth = degrees(roll)
    return azimuth
