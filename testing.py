import os
import re
import pandas as pd
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.metrics import mean_squared_error, r2_score
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

def plot_parabola_3d(X_test, y_test, predicted_values):
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Plot actual data
    ax.scatter(X_test[:, 1], X_test[:, 2], X_test[:, 0], c='r', marker='o', label='Actual Values')

    # Plot predicted data
    ax.scatter(predicted_values[:, 0], predicted_values[:, 1], X_test[:, 0], c='b', marker='^', label='Predicted Values')

    ax.set_xlabel('Azimuth')
    ax.set_ylabel('Altitude')
    ax.set_zlabel('Timestamp')
    ax.set_title('Comparison of Azimuth and Altitude')
    ax.legend()

    plt.show()

def main():
    main_folder = 'Main_Folder'

    year_folder = input('Enter the year folder (e.g., 2020):')

    data_folder = os.path.join(main_folder, year_folder, f'cleaned_{year_folder}')
    models_folder = os.path.join(main_folder, year_folder, f'models_{year_folder}')
    model_path = os.path.join(models_folder, f'my_model_{year_folder}.keras')

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No model found at: {model_path}")

    # Load the model
    loaded_model = tf.keras.models.load_model(model_path)

    # Select CSV file from the cleaned data folder
    csv_path = select_csv_file_from_folder(data_folder)

    # Load the dataset
    X_test, y_test, df_test = load_dataset(csv_path)

    # Scale the data
    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()

    X_test_scaled = scaler_X.fit_transform(X_test)
    y_test_scaled = scaler_y.fit_transform(y_test)

    # Reshape the data for LSTM
    timesteps = 1
    X_test_reshaped = X_test_scaled.reshape((X_test_scaled.shape[0], timesteps, X_test_scaled.shape[1]))

    # Predict using the loaded model
    predicted_values_scaled = loaded_model.predict(X_test_reshaped)
    predicted_values = scaler_y.inverse_transform(predicted_values_scaled)

    # Calculate metrics
    mse = mean_squared_error(y_test, predicted_values)
    r2 = r2_score(y_test, predicted_values)

    print(f"Mean Squared Error on Test Data: {mse}")
    print(f"R-squared on Test Data: {r2}")

    # Plot 3D visualization
    plot_parabola_3d(X_test, y_test, predicted_values)

if __name__ == "__main__":
    main()
