#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <unistd.h>
#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <string.h>
#include <time.h>
#include <dirent.h>

// Alamat I2C dari MPU-6050
#define MPU6050_ADDR 0x68

// Register MPU-6050 untuk data akselerometer
#define MPU6050_REG_ACCEL_XOUT_H 0x3B
#define MPU6050_REG_ACCEL_YOUT_H 0x3D
#define MPU6050_REG_ACCEL_ZOUT_H 0x3F

// Konfigurasi pin GPIO untuk relay azimuth (pan) dan altitude (tilt)
#define RELAY_PIN_AZIMUTH_UP 20
#define RELAY_PIN_AZIMUTH_DOWN 22
#define RELAY_PIN_ALTITUDE_UP 23
#define RELAY_PIN_ALTITUDE_DOWN 25

// Struct untuk menyimpan data prediksi
typedef struct {
    float azimuth;
    float altitude;
    time_t timestamp; // Waktu dalam format time_t
} Prediction;

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

// Fungsi untuk membaca prediksi dari file CSV
int read_predictions_from_csv(const char *filename, Prediction *predictions, int max_predictions) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "Failed to open CSV file: %s\n", filename);
        return 0;
    }

    char line[100];
    int count = 0;
    while (fgets(line, sizeof(line), file) && count < max_predictions) {
        char date[20], time[20];
        float predict_azimuth, predict_altitude;

        if (sscanf(line, "%19[^,],%19[^,],%f,%f", date, time, &predict_azimuth, &predict_altitude) == 4) {
            struct tm tm_time;
            memset(&tm_time, 0, sizeof(struct tm));
            strftime(date, "%Y-%m-%d", &tm_time); // Format tanggal yang diharapkan
            strftime(time, "%H:%M:%S", &tm_time); // Format waktu yang diharapkan
            time_t timestamp = mktime(&tm_time);

            predictions[count].azimuth = predict_azimuth;
            predictions[count].altitude = predict_altitude;
            predictions[count].timestamp = timestamp;
            count++;
        }
    }

    fclose(file);
    return count; // Return the number of predictions read
}

// Fungsi untuk mendapatkan waktu saat ini
time_t get_current_time() {
    time_t now;
    time(&now);
    return now;
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

// Fungsi untuk mencari file CSV berikutnya di direktori tertentu
char *find_next_csv_file(const char *dir_path, int *current_year) {
    DIR *dir;
    struct dirent *ent;
    if ((dir = opendir(dir_path)) != NULL) {
        while ((ent = readdir(dir)) != NULL) {
            // Cari file dengan ekstensi .csv yang sesuai urutan tahun
            if (strstr(ent->d_name, ".csv") != NULL && strstr(ent->d_name, "predictions_") != NULL) {
                int year;
                if (sscanf(ent->d_name, "predictions_%d_to_%*d.csv", &year) == 1 && year >= *current_year) {
                    char *filename = (char *)malloc(strlen(dir_path) + strlen(ent->d_name) + 2);
                    sprintf(filename, "%s/%s", dir_path, ent->d_name);
                    *current_year = year; // Update tahun saat ini
                    closedir(dir);
                    return filename;
                }
            }
        }
        closedir(dir);
    } else {
        fprintf(stderr, "Failed to open directory: %s\n", dir_path);
    }
    return NULL;
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

    // Max predictions to read
    const int max_predictions = 10; // Adjust this as needed

    // Array to store predictions
    Prediction predictions[max_predictions];

    // Direktori di mana file CSV disimpan
    const char *csv_dir = "Main_Folder";

    // Tahun awal dari file yang dibaca
    int current_year = 2024;

    char *csv_file_path = NULL;

    while (1) {
        // Cari file CSV berikutnya
        if (!csv_file_path) {
            csv_file_path = find_next_csv_file(csv_dir, &current_year);
            if (!csv_file_path) {
                fprintf(stderr, "No CSV file found in directory: %s\n", csv_dir);
                return 1;
            }
        }

        int num_predictions = read_predictions_from_csv(csv_file_path, predictions, max_predictions);
        if (num_predictions == 0) {
            fprintf(stderr, "Failed to read predictions from CSV: %s\n", csv_file_path);
            free(csv_file_path);
            csv_file_path = NULL;
            continue;
        }

        while (1) {
            // Baca data dari MPU-6050
            int accel_x, accel_y, accel_z;
            read_mpu6050_data(fd, &accel_x, &accel_y, &accel_z);

            // Hitung azimuth dan altitude
            float azimuth = calculate_azimuth(accel_x, accel_y, accel_z);
            float altitude = calculate_altitude(accel_x, accel_y, accel_z);

            // Dapatkan waktu saat ini
            time_t current_time = get_current_time();

            // Cari prediksi untuk waktu saat ini
            float predicted_azimuth = 0.0;
            float predicted_altitude = 0.0;
            for (int i = 0; i < num_predictions; ++i) {
                if (current_time >= predictions[i].timestamp) {
                    predicted_azimuth = predictions[i].azimuth;
                    predicted_altitude = predictions[i].altitude;
                }
            }

            // Kontrol relay azimuth dan altitude berdasarkan prediksi
            control_azimuth_relay(predicted_azimuth);
            control_altitude_relay(predicted_altitude);

            delay(1000);  // Tunggu sebelum membaca data berikutnya

            // Cek apakah sudah waktunya untuk beralih ke file CSV berikutnya
            time_t next_check_time = get_current_time();
            if (next_check_time >= predictions[num_predictions - 1].timestamp) {
                free(csv_file_path);
                csv_file_path = NULL;
                break; // Keluar dari loop dan mencari file CSV berikutnya
            }
        }
    }

    return 0;
}
