#include <iostream>
#include <cmath>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <unistd.h>
#include <vector>   // Added for std::vector
#include <dirent.h> // Added for directory operations

// Alamat I2C dari MPU-6050
#define MPU6050_ADDR 0x68

// Register MPU-6050 untuk data akselerometer dan gyroscope
#define MPU6050_REG_ACCEL_XOUT_H 0x3B
#define MPU6050_REG_ACCEL_YOUT_H 0x3D
#define MPU6050_REG_ACCEL_ZOUT_H 0x3F

// Konfigurasi pin GPIO untuk relay azimuth (pan) dan altitude (tilt)
#define RELAY_PIN_AZIMUTH_UP 19
#define RELAY_PIN_AZIMUTH_DOWN 20
#define RELAY_PIN_ALTITUDE_UP 22
#define RELAY_PIN_ALTITUDE_DOWN 23

// Fungsi untuk membaca data dari MPU-6050
void read_mpu6050_data(int &accel_x, int &accel_y, int &accel_z) {
    // Kode untuk membaca data dari MPU-6050 menggunakan I2C
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
        std::cout << "Activate RELAY_PIN_AZIMUTH_UP" << std::endl;
    } else {
        // Aktifkan relay untuk azimuth turun
        std::cout << "Activate RELAY_PIN_AZIMUTH_DOWN" << std::endl;
    }
}

// Fungsi untuk menggerakkan relay altitude (tilt) berdasarkan altitude yang diprediksi
void control_altitude_relay(float predicted_altitude) {
    if (predicted_altitude < 180) {
        // Aktifkan relay untuk altitude naik
        std::cout << "Activate RELAY_PIN_ALTITUDE_UP" << std::endl;
    } else {
        // Aktifkan relay untuk altitude turun
        std::cout << "Activate RELAY_PIN_ALTITUDE_DOWN" << std::endl;
    }
}

// Fungsi untuk membaca data prediksi dari file CSV
void read_predicted_data(const std::string &csv_file, std::vector<int> &timestamps, std::vector<float> &azimuths, std::vector<float> &altitudes) {
    std::ifstream file(csv_file);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open CSV file");
    }

    std::string line;
    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string timestamp_str, azimuth_str, altitude_str;
        if (std::getline(ss, timestamp_str, ';') && std::getline(ss, azimuth_str, ';') && std::getline(ss, altitude_str, ';')) {
            timestamps.push_back(std::stoi(timestamp_str));
            azimuths.push_back(std::stof(azimuth_str));
            altitudes.push_back(std::stof(altitude_str));
        }
    }

    file.close();
}

// Fungsi untuk mencari file CSV di direktori tertentu
std::string find_csv_file(const std::string &directory) {
    std::string csv_file;
    DIR *dir;
    struct dirent *ent;
    if ((dir = opendir(directory.c_str())) != NULL) {
        while ((ent = readdir(dir)) != NULL) {
            std::string filename = ent->d_name;
            if (filename.length() > 4 && filename.substr(filename.length() - 4) == ".csv") {
                csv_file = filename;
                break;
            }
        }
        closedir(dir);
    } else {
        throw std::runtime_error("Failed to open directory");
    }

    if (csv_file.empty()) {
        throw std::runtime_error("No CSV file found in directory");
    }

    return csv_file;
}

int main() {
    try {
        // Temukan file CSV di direktori Main_Folder
        std::string directory = "Main_Folder";  // Ganti dengan direktori yang sesuai
        std::string csv_file = find_csv_file(directory);
        std::cout << "Using CSV file: " << csv_file << std::endl;

        // Baca data prediksi dari file CSV
        std::vector<int> timestamps;
        std::vector<float> azimuths;
        std::vector<float> altitudes;
        read_predicted_data(directory + "/" + csv_file, timestamps, azimuths, altitudes);

        while (true) {
            // Baca data dari MPU-6050
            int accel_x, accel_y, accel_z;
            read_mpu6050_data(accel_x, accel_y, accel_z);

            // Hitung azimuth dan altitude
            float azimuth = calculate_azimuth(accel_x, accel_y, accel_z);
            float altitude = calculate_altitude(accel_x, accel_y, accel_z);

            // Kontrol relay azimuth dan altitude
            control_azimuth_relay(azimuth);
            control_altitude_relay(altitude);

            sleep(1);  // Tunggu sebelum membaca data berikutnya
        }
    } catch (const std::exception &e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }

    return 0;
}
