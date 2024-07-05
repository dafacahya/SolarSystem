#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <unistd.h>
#include <wiringPi.h>
#include <wiringPiI2C.h>

// Alamat I2C dari MPU-6050
#define MPU6050_ADDR 0x68

// Register MPU-6050 untuk data akselerometer
#define MPU6050_REG_ACCEL_XOUT_H 0x3B
#define MPU6050_REG_ACCEL_YOUT_H 0x3D
#define MPU6050_REG_ACCEL_ZOUT_H 0x3F

// Konfigurasi pin GPIO untuk relay azimuth (pan) dan altitude (tilt)
#define RELAY_PIN_AZIMUTH_UP 15
#define RELAY_PIN_AZIMUTH_DOWN 12
#define RELAY_PIN_ALTITUDE_UP 2
#define RELAY_PIN_ALTITUDE_DOWN 16

// Fungsi untuk membaca data dari MPU-6050
void read_mpu6050_data(int fd, int *accel_x, int *accel_y, int *accel_z) {
    *accel_x = wiringPiI2CReadReg16(fd, MPU6050_REG_ACCEL_XOUT_H);
    *accel_y = wiringPiI2CReadReg16(fd, MPU6050_REG_ACCEL_YOUT_H);
    *accel_z = wiringPiI2CReadReg16(fd, MPU6050_REG_ACCEL_ZOUT_H);
}

// Fungsi untuk menghitung azimuth (pan) berdasarkan data MPU-6050
float calculate_azimuth(int accel_x, int accel_y, int accel_z) {
    float roll = atan2((float)accel_y, (float)accel_z);
    float azimuth = roll * (180.0 / M_PI);  // Konversi radian ke derajat
    if (azimuth < 0) {
        azimuth += 360.0;  // Pastikan azimuth dalam rentang 0-360 derajat
    }
    return azimuth;
}

// Fungsi untuk menghitung altitude (tilt) berdasarkan data MPU-6050
float calculate_altitude(int accel_x, int accel_y, int accel_z) {
    float pitch = atan2((float)-accel_x, sqrt((float)accel_y * accel_y + (float)accel_z * accel_z));
    float altitude = pitch * (180.0 / M_PI);  // Konversi radian ke derajat
    if (altitude < 0) {
        altitude += 360.0;  // Pastikan altitude dalam rentang 0-360 derajat
    }
    return altitude;
}

// Fungsi untuk menggerakkan relay azimuth (pan) berdasarkan azimuth yang diprediksi
void control_azimuth_relay(float predicted_azimuth) {
    if (predicted_azimuth < 180) {
        // Aktifkan relay untuk azimuth naik
        digitalWrite(RELAY_PIN_AZIMUTH_UP, HIGH);
        digitalWrite(RELAY_PIN_AZIMUTH_DOWN, LOW);
    } else {
        // Aktifkan relay untuk azimuth turun
        digitalWrite(RELAY_PIN_AZIMUTH_UP, LOW);
        digitalWrite(RELAY_PIN_AZIMUTH_DOWN, HIGH);
    }
}

// Fungsi untuk menggerakkan relay altitude (tilt) berdasarkan altitude yang diprediksi
void control_altitude_relay(float predicted_altitude) {
    if (predicted_altitude < 180) {
        // Aktifkan relay untuk altitude naik
        digitalWrite(RELAY_PIN_ALTITUDE_UP, HIGH);
        digitalWrite(RELAY_PIN_ALTITUDE_DOWN, LOW);
    } else {
        // Aktifkan relay untuk altitude turun
        digitalWrite(RELAY_PIN_ALTITUDE_UP, LOW);
        digitalWrite(RELAY_PIN_ALTITUDE_DOWN, HIGH);
    }
}

int main() {
    int fd;
    if ((fd = wiringPiI2CSetup(MPU6050_ADDR)) < 0) {
        fprintf(stderr, "Failed to init I2C communication.\n");
        return 1;
    }

    // Setup pin relay
    wiringPiSetup();
    pinMode(RELAY_PIN_AZIMUTH_UP, OUTPUT);
    pinMode(RELAY_PIN_AZIMUTH_DOWN, OUTPUT);
    pinMode(RELAY_PIN_ALTITUDE_UP, OUTPUT);
    pinMode(RELAY_PIN_ALTITUDE_DOWN, OUTPUT);

    while (1) {
        // Baca data dari MPU-6050
        int accel_x, accel_y, accel_z;
        read_mpu6050_data(fd, &accel_x, &accel_y, &accel_z);

        // Hitung azimuth dan altitude
        float azimuth = calculate_azimuth(accel_x, accel_y, accel_z);
        float altitude = calculate_altitude(accel_x, accel_y, accel_z);

        // Kontrol relay azimuth dan altitude
        control_azimuth_relay(azimuth);
        control_altitude_relay(altitude);

        delay(1000);  // Tunggu sebelum membaca data berikutnya
    }

    return 0;
}
