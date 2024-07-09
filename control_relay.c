#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// Define pin relay yang digunakan
#define RELAY_PIN_1 19
#define RELAY_PIN_2 20
#define RELAY_PIN_3 22
#define RELAY_PIN_4 23

// MPU-6050 I2C address
#define MPU6050_ADDR 0x68

// MPU-6050 registers
#define MPU6050_REG_ACCEL_XOUT_H 0x3B
#define MPU6050_REG_ACCEL_YOUT_H 0x3D
#define MPU6050_REG_ACCEL_ZOUT_H 0x3F

int fd;

void init_mpu6050() {
    fd = wiringPiI2CSetup(MPU6050_ADDR);
    wiringPiI2CWriteReg8(fd, 0x6B, 0x00); // Wake up MPU-6050
}

short read_word_2c(int addr) {
    short high = wiringPiI2CReadReg8(fd, addr);
    short low = wiringPiI2CReadReg8(fd, addr + 1);
    short value = (high << 8) + low;
    if (value >= 0x8000)
        value = -(65535 - value + 1);
    return value;
}

void read_mpu6050_data(float *ax, float *ay, float *az) {
    *ax = read_word_2c(MPU6050_REG_ACCEL_XOUT_H) / 16384.0;
    *ay = read_word_2c(MPU6050_REG_ACCEL_YOUT_H) / 16384.0;
    *az = read_word_2c(MPU6050_REG_ACCEL_ZOUT_H) / 16384.0;
}

void calculate_orientation(float ax, float ay, float az, float *azimuth, float *altitude) {
    *azimuth = atan2(ay, az) * 180 / M_PI;
    if (*azimuth < 0) *azimuth += 360;

    *altitude = atan2(-ax, sqrt(ay * ay + az * az)) * 180 / M_PI;
}

void control_relay(float azimuth, float altitude) {
    // Inisialisasi WiringPi
    if (wiringPiSetup() == -1) {
        printf("WiringPi initialization failed.\n");
        return;
    }

    // Set pin relay sebagai output
    pinMode(RELAY_PIN_1, OUTPUT);
    pinMode(RELAY_PIN_2, OUTPUT);
    pinMode(RELAY_PIN_3, OUTPUT);
    pinMode(RELAY_PIN_4, OUTPUT);

    // Kontrol relay berdasarkan azimuth
    if (azimuth < 180) {
        digitalWrite(RELAY_PIN_1, HIGH);
        digitalWrite(RELAY_PIN_2, LOW);
    } else {
        digitalWrite(RELAY_PIN_2, HIGH);
        digitalWrite(RELAY_PIN_1, LOW);
    }

    // Kontrol relay berdasarkan altitude
    if (altitude < 90) {
        digitalWrite(RELAY_PIN_3, HIGH);
        digitalWrite(RELAY_PIN_4, LOW);
    } else {
        digitalWrite(RELAY_PIN_4, HIGH);
        digitalWrite(RELAY_PIN_3, LOW);
    }
}

int main() {
    float ax, ay, az;
    float azimuth, altitude;

    init_mpu6050();

    while (1) {
        read_mpu6050_data(&ax, &ay, &az);
        calculate_orientation(ax, ay, az, &azimuth, &altitude);
        control_relay(azimuth, altitude);
        delay(1000); // Tunggu sebelum pembacaan data berikutnya
    }

    return 0;
}
