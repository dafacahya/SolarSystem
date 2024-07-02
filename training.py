import os
import re
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

def load_dataset(csv_path):
    df = pd.read_csv(csv_path, sep=';')
    required_columns = ['Azimuth', 'Altitude', 'Timestamp']

    if not all(col in df.columns for col in required_columns):
        raise ValueError("Required columns are not present in the DataFrame.")

    X = df[['Timestamp', 'Azimuth', 'Altitude']].values
    y = df[['Azimuth', 'Altitude']].values

    return X, y, df

def select_csv_file_from_folder(folder):
    files = [f for f in os.listdir(folder) if f.endswith('.csv')]
    if not files:
        raise FileNotFoundError(f"No CSV files found in folder: {folder}")

    print("Available CSV files:")
    for idx, file in enumerate(files, start=1):
        print(f"{idx}. {file}")

    file_choice = int(input("Enter the number of the CSV file you want to use: "))
    selected_file = files[file_choice - 1]

    return os.path.join(folder, selected_file)

def extract_year_from_filename(filename):
    match = re.search(r'\d{4}', filename)
    if match:
        return match.group(0)
    return None

def main():
    # Main folder where data and models are stored
    main_folder = 'Main_Folder'

    # Ask user for the year folder
    year_folder = input("Enter the year folder (e.g., 2020): ")

    # Paths to data and models folders for the selected year
    data_folder = os.path.join(main_folder, year_folder, f'cleaned_{year_folder}')
    models_folder = os.path.join(main_folder, year_folder, f'models_{year_folder}')

    # Create models directory if it does not exist
    if not os.path.exists(models_folder):
        os.makedirs(models_folder)

    # Select CSV file from the cleaned data folder
    csv_path = select_csv_file_from_folder(data_folder)

    # Load dataset
    X, y, df = load_dataset(csv_path)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()

    X_train_scaled = scaler_X.fit_transform(X_train)
    y_train_scaled = scaler_y.fit_transform(y_train)
    X_test_scaled = scaler_X.transform(X_test)
    y_test_scaled = scaler_y.transform(y_test)

    timesteps = 1
    X_train_reshaped = X_train_scaled.reshape((X_train_scaled.shape[0], timesteps, X_train_scaled.shape[1]))
    X_test_reshaped = X_test_scaled.reshape((X_test_scaled.shape[0], timesteps, X_test_scaled.shape[1]))

    model = Sequential()
    model.add(LSTM(units=128, input_shape=(timesteps, X_train_scaled.shape[1]), return_sequences=True))
    model.add(LSTM(units=64, return_sequences=True))
    model.add(LSTM(units=32, return_sequences=True))
    model.add(LSTM(units=16, return_sequences=True))
    model.add(LSTM(units=8))
    model.add(Dense(units=2))

    optimizer = Adam(learning_rate=0.0001)
    model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])

    epochs = int(input("Enter the number of epochs: "))

    history = model.fit(X_train_reshaped, y_train_scaled, epochs=epochs, batch_size=1024, validation_data=(X_test_reshaped, y_test_scaled))

    model_filename = f'my_model_{year_folder}.h5'
    model_path = os.path.join(models_folder, model_filename)
    model.save(model_path)

    print(f"Model saved as '{model_path}'")

if __name__ == "__main__":
    main()
