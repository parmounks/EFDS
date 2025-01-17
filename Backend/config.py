#Add configuration

#https://wvs.earthdata.nasa.gov/api/v1/snapshot?REQUEST=GetSnapshot&LAYERS=VIIRS_SNPP_CorrectedReflectance_TrueColor,VIIRS_SNPP_Thermal_Anomalies_375m_Day,Coastlines_15m,Reference_Features_15m&CRS=EPSG:4326&TIME=2024-11-15&WRAP=DAY,DAY,X,X&BBOX=40.921,-96.201,57.619,-73.299&FORMAT=image/jpeg&WORLDFILE=true&WIDTH=2606&HEIGHT=1900&AUTOSCALE=TRUE&ts=1731722051995

# NASA GIBS WMS endpoint for high-resolution imagery
BASE_URL = 'https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi'
#LAYER = 'MODIS_Terra_CorrectedReflectance_TrueColor'
LAYER = 'VIIRS_SNPP_CorrectedReflectance_TrueColor'
FORMAT = 'image/jpeg'
CRS = 'EPSG:4326'  # coordinates type: long and lat
WIDTH = 7600  # in pixels
HEIGHT = 7600  # in pixels

# Default bounding box (Ontario)
BBOX = '40.9210,-96.2010,57.6190,-73.2990'

# Dictionary of city-specific bounding boxes - 
# Coordinates format : "city":"south_latitude,west_longitude,north_latitude,east_longitude"

CITY_BBOX = {
    "ontario": "40.9210,-96.2010,57.6190,-73.2990",
    "toronto": "43.5810,-79.6393,43.8554,-79.1169",
    "ottawa": "45.2488,-75.9270,45.5368,-75.4465",
    "mississauga": "43.5041,-79.7115,43.6860,-79.5794",
    "brampton": "43.6056,-79.8486,43.7928,-79.6846",
    "hamilton": "43.1300,-80.0201,43.2758,-79.7245",
    "london": "42.8500,-81.3642,43.1000,-81.1964",
    "markham": "43.8257,-79.3962,43.9504,-79.2293",
    "vaughan": "43.7350,-79.6101,43.8605,-79.3656",
    "kitchener": "43.3708,-80.5206,43.4857,-80.3894",
    "windsor": "42.2250,-83.0700,42.3367,-82.9111",
    "richmond hill": "43.8201,-79.4850,43.9206,-79.3621",
    "burlington": "43.2826,-79.9357,43.5005,-79.6972",
    "oshawa": "43.8201,-78.9200,43.9958,-78.7640",
    "greater sudbury": "46.3900,-81.2000,47.1400,-80.6500",
    "barrie": "44.3000,-79.7600,44.4500,-79.5900",
    "guelph": "43.4600,-80.3300,43.5700,-80.2100",
    "cambridge": "43.3200,-80.4000,43.4500,-80.2800",
    "st. catharines": "43.1100,-79.3100,43.2100,-79.1700",
    "waterloo": "43.4200,-80.5700,43.4900,-80.4900",
    "thunder bay": "48.3100,-89.4600,48.4500,-89.1500",
    "brantford": "43.1200,-80.3000,43.2500,-80.1500",
    "pickering": "43.7900,-79.1300,43.9100,-78.9300",
    "niagara falls": "43.0200,-79.1500,43.1200,-79.0100",
    "peterborough": "44.2500,-78.3900,44.3600,-78.2600",
    "sault ste. marie": "46.4500,-84.4100,46.5500,-84.2700",
    "sarnia": "42.9500,-82.5000,43.0500,-82.3500",
    "norfolk county": "42.7000,-80.5800,43.0300,-80.0500",
    "welland": "43.0100,-79.3100,43.0500,-79.1900",
    "belleville": "44.0900,-77.4200,44.2000,-77.3000",
    "north bay": "46.2400,-79.5200,46.3600,-79.3800",
}


# Function to update BBOX dynamically
def set_bbox(city):
    global BBOX
    city_lower = city.lower()
    if city_lower in CITY_BBOX:
        BBOX = CITY_BBOX[city_lower]
        print(f"BBOX updated to {BBOX} for city: {city.title()}")
    else:
        print(f"City {city} not found. Using default BBOX: {BBOX}")
