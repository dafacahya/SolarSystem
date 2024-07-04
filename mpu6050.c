#include <stdio.h>
#include <wiringPiI2C.h>
#include <wiringPi.h>
#include <unistd.h>

// Alamat I2C dari MPU6050
#define MPU6050_ADDR 0x68

// Register dari MPU6050
#define PWR_MGMT_1   0x6B
#define SMPLRT_DIV   0x19
#define CONFIG       0x1A
#define GYRO_CONFIG  0x1B
#define ACCEL_CONFIG 0x1C
#define INT_ENABLE   0x38
#define ACCEL_XOUT_H 0x3B
#define ACCEL_YOUT_H 0x3D
#define ACCEL_ZOUT_H 0x3F
#define GYRO_XOUT_H  0x43
#define GYRO_YOUT_H  0x45
#define GYRO_ZOUT_H  0x47

int fd;

void MPU_Init() {
    // Inisialisasi I2C bus
    fd = wiringPiI2CSetup(MPU6050_ADDR);
    
    // Menulis ke register manajemen daya untuk membangunkan sensor
    wiringPiI2CWriteReg8(fd, PWR_MGMT_1, 0);
    // Mengatur register sample rate divider
    wiringPiI2CWriteReg8(fd, SMPLRT_DIV, 7);
    // Mengatur register konfigurasi
    wiringPiI2CWriteReg8(fd, CONFIG, 0);
    // Mengatur register konfigurasi giroskop
    wiringPiI2CWriteReg8(fd, GYRO_CONFIG, 24);
    // Mengatur register konfigurasi akselerometer
    wiringPiI2CWriteReg8(fd, ACCEL_CONFIG, 0);
    // Mengatur register interrupt enable
    wiringPiI2CWriteReg8(fd, INT_ENABLE, 1);
}

int read_raw_data(int addr) {
    // Membaca nilai 16-bit dari register
    int high = wiringPiI2CReadReg16(fd, addr);
    int low = wiringPiI2CReadReg16(fd, addr + 1);
    int value = (high << 8) | low;
    if (value > 32768) {
        value = value - 65536;
    }
    return value;
}

int main() {
    // Inisialisasi WiringPi
    wiringPiSetup();

    // Inisialisasi MPU6050
    MPU_Init();

    printf("Reading MPU6050 data...\n");

    while (1) {
        // Membaca data akselerometer
        int acc_x = read_raw_data(ACCEL_XOUT_H);
        int acc_y = read_raw_data(ACCEL_YOUT_H);
        int acc_z = read_raw_data(ACCEL_ZOUT_H);

        // Mengonversi data akselerometer menjadi g-force
        float Ax = (float)acc_x / 16384.0;
        float Ay = (float)acc_y / 16384.0;
        float Az = (float)acc_z / 16384.0;

        // Membaca data giroskop
        int gyro_x = read_raw_data(GYRO_XOUT_H);
        int gyro_y = read_raw_data(GYRO_YOUT_H);
        int gyro_z = read_raw_data(GYRO_ZOUT_H);

        // Mengonversi data giroskop menjadi derajat per detik
        float Gx = (float)gyro_x / 131.0;
        float Gy = (float)gyro_y / 131.0;
        float Gz = (float)gyro_z / 131.0;

        // Menampilkan hasil pembacaan
        printf("Ax=%.2fg Ay=%.2fg Az=%.2fg Gx=%.2f°/s Gy=%.2f°/s Gz=%.2f°/s\n", Ax, Ay, Az, Gx, Gy, Gz);

        // Tunggu 0.5 detik sebelum membaca lagi
        delay(500);
    }

    return 0;
}
