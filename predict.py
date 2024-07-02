import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import ephem

# Custom loss function
@tf.keras.utils.register_keras_serializable()
def mse(y_true, y_pred):
    return tf.keras.losses.mean_squared_error(y_true, y_pred)

# Function to load models from the given folder
def load_models(models_folder):
    years = [2017, 2018, 2019, 2020, 2021, 2022, 2023]
    models = []

    for year in years:
        model_path = os.path.join(models_folder, str(year), f'models_{year}', f'my_model_{year}.h5')
        if os.path.exists(model_path):
            model = load_model(model_path, custom_objects={'mse': mse})
            models.append(model)
        else:
            print(f"Model not found: {model_path}")
            raise FileNotFoundError(f"Model not found: {model_path}")
    return models

# Function to generate timestamp data based on the given time interval
def generate_timestamp_data(start_date, interval_years, interval_minutes, num_years):
    timestamps = []
    current_time = start_date
    end_date = start_date + timedelta(days=num_years * 365)  # Approximation for 365 days in a year

    while current_time <= end_date:
        timestamps.append(current_time)
        current_time += timedelta(minutes=interval_minutes)
        current_time = current_time.replace(year=current_time.year + interval_years)

    return np.array(timestamps)

# Function to preprocess timestamps
def preprocess_timestamps(timestamps):
    timestamps_as_floats = np.array([dt.timestamp() for dt in timestamps]).reshape(-1, 1)
    scaler = MinMaxScaler()
    return scaler.fit_transform(timestamps_as_floats), scaler

# Function to make predictions with loaded models
def predict_with_models(models, X):
    y_pred_sum = np.zeros((X.shape[0], 2))  # Assuming output is 2D: Azimuth and Altitude
    for model in models:
        X_reshaped = np.expand_dims(X, axis=0)  # Add batch dimension
        y_pred = model.predict(X_reshaped)
        y_pred_sum += np.squeeze(y_pred, axis=0)  # Aggregate predictions across models
    y_pred_avg = y_pred_sum / len(models)
    return y_pred_avg

# Function to save predictions to CSV file
def save_predictions_to_csv(timestamps, predictions, ephem_data, output_path):
    df = pd.DataFrame({
        'Timestamp': [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in timestamps],
        'Predicted_Azimuth': predictions[:, 0],
        'Predicted_Altitude': predictions[:, 1],
        'Ephem_Azimuth': ephem_data[:, 0],
        'Ephem_Altitude': ephem_data[:, 1]
    })
    df.to_csv(output_path, index=False, sep=';')

# Function to get ephem data
def get_ephem_data(timestamps, latitude, longitude):
    ephem_data = []
    observer = ephem.Observer()
    observer.lat = str(latitude)
    observer.lon = str(longitude)

    sun = ephem.Sun()
    for timestamp in timestamps:
        observer.date = timestamp
        sun.compute(observer)
        azimuth = np.degrees(sun.az)
        altitude = np.degrees(sun.alt)
        ephem_data.append((azimuth, altitude))

    return np.array(ephem_data)

# Function to validate and adjust predictions
def validate_and_adjust_prediction(predictions, ephem_data):
    # This function can be adjusted based on your specific validation and adjustment needs
    return predictions

# Main function to run the prediction process
def main():
    main_folder = 'Main_Folder'
    models_folder = main_folder

    models = load_models(models_folder)
    latitude = -7.921179 
    longitude = 112.599392  

    current_year = datetime.now().year
    start_date = datetime(current_year, 1, 1)
    num_years_per_interval = 5
    interval_minutes = 5

    current_start_date = start_date
    end_date = datetime(current_year + 5, 1, 1)  # Simulate for the next 5 years
    
    while current_start_date <= end_date:
        timestamps = generate_timestamp_data(current_start_date, num_years_per_interval, interval_minutes, num_years_per_interval)

        X, scaler = preprocess_timestamps(timestamps)
        X = X.reshape((X.shape[0], 1, X.shape[1]))  # Reshape for LSTM input

        predictions = predict_with_models(models, X)
        predictions = scaler.inverse_transform(predictions)

        ephem_data = get_ephem_data(timestamps, latitude, longitude)

        predictions = validate_and_adjust_prediction(predictions, ephem_data)

        output_path = os.path.join(main_folder, f'predictions_{current_start_date.year}_to_{current_start_date.year + num_years_per_interval - 1}.csv')
        save_predictions_to_csv(timestamps, predictions, ephem_data, output_path)

        print(f"Predictions saved to '{output_path}'")

        current_start_date = current_start_date.replace(year=current_start_date.year + num_years_per_interval)

if __name__ == "__main__":
    main()
