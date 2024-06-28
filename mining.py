import ephem
import pandas as pd
import os
from datetime import datetime, timedelta
def mining(latitude, longitude, date):
    observer = ephem.Observer()
    observer.lat = str(latitude)
    observer.long = str(longitude)
    observer.date = date

    sun = ephem.Sun(observer)

    azimuth = sun.az * 180 / ephem.pi
    altitude = sun.alt * 180 / ephem.pi

    return azimuth, altitude
def main(latitude, longitude, start_date, end_date, time_interval_minutes):
    time_interval = timedelta(minutes=time_interval_minutes)

    data_list = []
    current_date = start_date

    while current_date <= end_date:
        azimuth, altitude = mining(latitude, longitude, current_date)

        data_list.append({
            'Datetime': current_date,
            'Latitude': latitude,
            'Longitude': longitude,
            'Azimuth': azimuth,
            'Altitude': altitude
        })

        current_date += time_interval

    master_directory = 'Main_Folder'
    tahun_directory = os.path.join(master_directory, str(start_date.year))
    raw_tahun_directory = os.path.join(tahun_directory, f'raw_{start_date.year}')
    os.makedirs(raw_tahun_directory, exist_ok=True)

    csv_file_path = os.path.join(raw_tahun_directory, f'raw_file_{start_date.year}.csv')
    df = pd.DataFrame(data_list)
    df.to_csv(csv_file_path, index=False, sep=';')

    print(f"Data saved in: {csv_file_path}")

if __name__ == "__main__":
    latitude = float(input("Enter latitude: "))
    longitude = float(input("Enter longitude: "))

    # Example inputs for datetime
    start_date = datetime.strptime(input("Enter start date (YYYY-MM-DD HH:MM:SS): "), "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime(input("Enter end date (YYYY-MM-DD HH:MM:SS): "), "%Y-%m-%d %H:%M:%S")
    time_interval_minutes = int(input("Enter time interval in minutes: "))

    main(latitude, longitude, start_date, end_date, time_interval_minutes)