import os
import requests
from PIL import Image as plimg
from io import BytesIO
import datetime

# Define base directory
base_dir = base_directory

# Bounding box for region of interest
min_lat, max_lat = 57.5653, 67.6473
min_lon, max_lon = -124.2212, -109.9602

def create_dirs(base_path):
    """Creates common Unprocessed and Processed directory structure under Fires"""
    dirs = {
        'unprocessed': os.path.join(base_path, 'Fires', 'Unprocessed'),
        'processed': os.path.join(base_path, 'Fires', 'Processed')
    }
    for subdir in dirs.values():
        if not os.path.exists(subdir):
            os.makedirs(subdir)
    return dirs

def download_combined_image(start_date, end_date, dirs):
    currentdate = start_date
    while currentdate <= end_date:
        date_str = currentdate.strftime('%Y-%m-%d')
        print(f"Downloading combined image for {date_str} (fire)...")

        # Define bounding box and URL for combined layers
        bbox = f"{min_lat},{min_lon},{max_lat},{max_lon}"
        url = f'https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?\
version=1.3.0&service=WMS&request=GetMap&\
format=image/png&STYLE=default&bbox={bbox}&CRS=EPSG:4326&\
HEIGHT=512&WIDTH=512&TIME={currentdate}&\
layers=VIIRS_SNPP_CorrectedReflectance_TrueColor,MODIS_Combined_Thermal_Anomalies_All&transparent=True'

        # Download the combined image
        try:
            response = requests.get(url)
            if response.status_code == 200:
                img = plimg.open(BytesIO(response.content))
                img_path = os.path.join(dirs['unprocessed'], f'combined_{date_str}.png')
                img.save(img_path)
                print(f"Saved combined image for {date_str}")
            else:
                print(f"Failed to download combined image on {date_str}: HTTP {response.status_code}")
        except Exception as e:
            print(f"Error downloading combined image for {date_str}: {e}")

        currentdate += datetime.timedelta(1)

# Set date range for fire testing
fires_start = datetime.date(2023, 7, 12)
fires_end = datetime.date(2023, 8, 16)

# Create common directories for fires
dirs = create_dirs(base_dir)

# Download combined images for fire dates
download_combined_image(fires_start, fires_end, dirs)

print("Combined image download completed.")
