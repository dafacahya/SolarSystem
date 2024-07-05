#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <unistd.h>
#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <string.h>
#include <time.h>
#include <dirent.h>
#include <errno.h>

// I2C address of MPU-6050
#define MPU6050_ADDR 0x68

// Registers for MPU-6050 accelerometer data
#define MPU6050_REG_ACCEL_XOUT_H 0x3B
#define MPU6050_REG_ACCEL_YOUT_H 0x3D
#define MPU6050_REG_ACCEL_ZOUT_H 0x3F

// GPIO pin configuration for azimuth (pan) and altitude (tilt) relays
#define RELAY_PIN_AZIMUTH_UP 20
#define RELAY_PIN_AZIMUTH_DOWN 22
#define RELAY_PIN_ALTITUDE_UP 23
#define RELAY_PIN_ALTITUDE_DOWN 25

// Struct to store prediction data
typedef struct {
    float azimuth;
    float altitude;
    time_t timestamp; // Timestamp in time_t format
} Prediction;

// Function to read data from MPU-6050
void read_mpu6050_data(int fd, int *accel_x, int *accel_y, int *accel_z) {
    *accel_x = wiringPiI2CReadReg16(fd, MPU6050_REG_ACCEL_XOUT_H);
    *accel_y = wiringPiI2CReadReg16(fd, MPU6050_REG_ACCEL_YOUT_H);
    *accel_z = wiringPiI2CReadReg16(fd, MPU6050_REG_ACCEL_ZOUT_H);
}

// Function to calculate azimuth (pan) based on MPU-6050 data
float calculate_azimuth(int accel_x, int accel_y, int accel_z) {
    float roll = atan2((float)accel_y, (float)accel_z);
    float azimuth = roll * (180.0 / M_PI);  // Convert radians to degrees
    if (azimuth < 0) {
        azimuth += 360.0;  // Ensure azimuth is within range 0-360 degrees
    }
    return azimuth;
}

// Function to calculate altitude (tilt) based on MPU-6050 data
float calculate_altitude(int accel_x, int accel_y, int accel_z) {
    float pitch = atan2((float)-accel_x, sqrt((float)accel_y * accel_y + (float)accel_z * accel_z));
    float altitude = pitch * (180.0 / M_PI);  // Convert radians to degrees
    if (altitude < 0) {
        altitude += 360.0;  // Ensure altitude is within range 0-360 degrees
    }
    return altitude;
}

// Function to read predictions from CSV file
int read_predictions_from_csv(const char *filename, Prediction *predictions, int max_predictions) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "Failed to open CSV file: %s (%s)\n", filename, strerror(errno));
        return 0;
    }

    char line[100];
    int count = 0;
    while (fgets(line, sizeof(line), file) && count < max_predictions) {
        char date[20], time[20];
        float predict_azimuth, predict_altitude;

        // Read data from CSV line
        if (sscanf(line, "%19s %19s %f %f", date, time, &predict_azimuth, &predict_altitude) != 4) {
            fprintf(stderr, "Failed to parse CSV line: %s\n", line);
            continue;
        }

        // Parse date and time
        struct tm *tm_time = gmtime(&timestamp);
        tm_time->tm_year = atoi(date) - 1900;
        tm_time->tm_mon = atoi(strtok(time, "-")) - 1;
        tm_time->tm_mday = atoi(strtok(NULL, "-"));
        tm_time->tm_hour = atoi(strtok(NULL, ":"));
        tm_time->tm_min = atoi(strtok(NULL, ":"));
        tm_time->tm_sec = 0; // If no seconds in format, set to 0
        time_t timestamp = mktime(tm_time);

        // Store prediction data
        predictions[count].azimuth = predict_azimuth;
        predictions[count].altitude = predict_altitude;
        predictions[count].timestamp = timestamp;
        count++;
    }

    fclose(file);
    return count; // Return the number of predictions read
}
// Function to get current time
time_t get_current_time() {
    time_t now;
    time(&now);
    return now;
}

// Function to control azimuth relay based on predicted azimuth
void control_azimuth_relay(float predicted_azimuth) {
    if (predicted_azimuth < 180) {
        // Activate relay for azimuth up
        digitalWrite(RELAY_PIN_AZIMUTH_UP, HIGH);
        digitalWrite(RELAY_PIN_AZIMUTH_DOWN, LOW);
    } else {
        // Activate relay for azimuth down
        digitalWrite(RELAY_PIN_AZIMUTH_UP, LOW);
        digitalWrite(RELAY_PIN_AZIMUTH_DOWN, HIGH);
    }
}

// Function to control altitude relay based on predicted altitude
void control_altitude_relay(float predicted_altitude) {
    if (predicted_altitude < 180) {
        // Activate relay for altitude up
        digitalWrite(RELAY_PIN_ALTITUDE_UP, HIGH);
        digitalWrite(RELAY_PIN_ALTITUDE_DOWN, LOW);
    } else {
        // Activate relay for altitude down
        digitalWrite(RELAY_PIN_ALTITUDE_UP, LOW);
        digitalWrite(RELAY_PIN_ALTITUDE_DOWN, HIGH);
    }
}

// Function to find the next CSV file in a directory
char *find_next_csv_file(const char *dir_path, int *current_year) {
    DIR *dir;
    struct dirent *ent;
    if ((dir = opendir(dir_path)) != NULL) {
        while ((ent = readdir(dir)) != NULL) {
            // Find file with .csv extension matching year order
            if (strstr(ent->d_name, ".csv") != NULL && strstr(ent->d_name, "predictions_") != NULL) {
                int year;
                if (sscanf(ent->d_name, "predictions_%d_to_%*d.csv", &year) == 1 && year >= *current_year) {
                    char *filename = (char *)malloc(strlen(dir_path) + strlen(ent->d_name) + 2);
                    sprintf(filename, "%s/%s", dir_path, ent->d_name);
                    *current_year = year; // Update current year
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

    // Setup relay pins
    wiringPiSetup();
    pinMode(RELAY_PIN_AZIMUTH_UP, OUTPUT);
    pinMode(RELAY_PIN_AZIMUTH_DOWN, OUTPUT);
    pinMode(RELAY_PIN_ALTITUDE_UP, OUTPUT);
    pinMode(RELAY_PIN_ALTITUDE_DOWN, OUTPUT);

    // Max predictions to read
    const int max_predictions = 10; // Adjust as needed

    // Array to store predictions
    Prediction predictions[max_predictions];

    // Directory where CSV files are stored
    const char *csv_dir = "Main_Folder";

    // Initial year from the read file
    int current_year = 2024;

    char *csv_file_path = NULL;

    while (1) {
        // Find next CSV file
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
            // Read data from MPU-6050
            int accel_x, accel_y, accel_z;
            read_mpu6050_data(fd, &accel_x, &accel_y, &accel_z);

            // Calculate azimuth and altitude
            float azimuth = calculate_azimuth(accel_x, accel_y, accel_z);
            float altitude = calculate_altitude(accel_x, accel_y, accel_z);

            // Get current time
            time_t current_time = get_current_time();

            // Find prediction for current time
            float predicted_azimuth = 0.0;
            float predicted_altitude = 0.0;
            for (int i = 0; i < num_predictions; ++i) {
                if (current_time >= predictions[i].timestamp) {
                    predicted_azimuth = predictions[i].azimuth;
                    predicted_altitude = predictions[i].altitude;
                }
            }

            // Control azimuth and altitude relays based on predictions
            control_azimuth_relay(predicted_azimuth);
            control_altitude_relay(predicted_altitude);

            delay(1000);  // Wait before reading next data

            // Check if it's time to switch to the next CSV file
            time_t next_check_time = get_current_time();
            if (next_check_time >= predictions[num_predictions - 1].timestamp) {
                free(csv_file_path);
                csv_file_path = NULL;
                break; // Exit loop and find next CSV file
            }
        }
    }

    return 0;
}
