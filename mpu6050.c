#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>

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

int i2c_fd;

void MPU_Init() {
    // Menulis ke register manajemen daya untuk membangunkan sensor
    i2c_smbus_write_byte_data(i2c_fd, PWR_MGMT_1, 0);
    // Mengatur register sample rate divider
    i2c_smbus_write_byte_data(i2c_fd, SMPLRT_DIV, 7);
    // Mengatur register konfigurasi
    i2c_smbus_write_byte_data(i2c_fd, CONFIG, 0);
    // Mengatur register konfigurasi giroskop
    i2c_smbus_write_byte_data(i2c_fd, GYRO_CONFIG, 24);
    // Mengatur register konfigurasi akselerometer
    i2c_smbus_write_byte_data(i2c_fd, ACCEL_CONFIG, 0);
    // Mengatur register interrupt enable
    i2c_smbus_write_byte_data(i2c_fd, INT_ENABLE, 1);
}

int16_t read_raw_data(uint8_t addr) {
    int16_t high = i2c_smbus_read_byte_data(i2c_fd, addr);
    int16_t low = i2c_smbus_read_byte_data(i2c_fd, addr + 1);
    int16_t value = (high << 8) | low;
    if (value > 32768) {
        value = value - 65536;
    }
    return value;
}

int main() {
    char *i2c_bus = "/dev/i2c-1";

    if ((i2c_fd = open(i2c_bus, O_RDWR)) < 0) {
        printf("Gagal membuka bus I2C\n");
        return 1;
    }

    if (ioctl(i2c_fd, I2C_SLAVE, MPU6050_ADDR) < 0) {
        printf("Gagal menghubungkan ke MPU6050\n");
        close(i2c_fd);
        return 1;
    }

    MPU_Init();

    while (1) {
        // Membaca data akselerometer
        int16_t acc_x = read_raw_data(ACCEL_XOUT_H);
        int16_t acc_y = read_raw_data(ACCEL_YOUT_H);
        int16_t acc_z = read_raw_data(ACCEL_ZOUT_H);

        // Mengonversi data akselerometer menjadi g-force
        float Ax = acc_x / 16384.0;
        float Ay = acc_y / 16384.0;
        float Az = acc_z / 16384.0;

        // Membaca data giroskop
        int16_t gyro_x = read_raw_data(GYRO_XOUT_H);
        int16_t gyro_y = read_raw_data(GYRO_YOUT_H);
        int16_t gyro_z = read_raw_data(GYRO_ZOUT_H);

        // Mengonversi data giroskop menjadi derajat per detik
        float Gx = gyro_x / 131.0;
        float Gy = gyro_y / 131.0;
        float Gz = gyro_z / 131.0;

        // Menampilkan hasil pembacaan
        printf("Ax=%.2fg Ay=%.2fg Az=%.2fg Gx=%.2f°/s Gy=%.2f°/s Gz=%.2f°/s\n", Ax, Ay, Az, Gx, Gy, Gz);

        // Tunggu 0.5 detik sebelum membaca lagi
        usleep(500000);
    }

    close(i2c_fd);
    return 0;
}
