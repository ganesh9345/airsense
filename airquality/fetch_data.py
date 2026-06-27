import requests
from .models import City, AirQualityRecord
from django.utils import timezone

API_KEY = "4d5c187ee2f680d42e17855d9f5f0df1"  

def get_aqi_status(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 200:
        return "Unhealthy"
    else:
        return "Hazardous"

def fetch_air_quality(city_name):
    try:
        # Step 1: Get coordinates of the city
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={API_KEY}"
        geo_response = requests.get(geo_url).json()

        if not geo_response:
            return {"error": "City not found"}

        lat = geo_response[0]['lat']
        lon = geo_response[0]['lon']
        country = geo_response[0]['country']

        # Step 2: Get air quality data
        aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        aqi_response = requests.get(aqi_url).json()

        components = aqi_response['list'][0]['components']
        aqi_value = aqi_response['list'][0]['main']['aqi'] * 50

        # Step 3: Save city to DB if not exists
        city, created = City.objects.get_or_create(
            name=city_name,
            defaults={
                'country': country,
                'latitude': lat,
                'longitude': lon
            }
        )

        # Step 4: Save air quality record
        record = AirQualityRecord.objects.create(
            city=city,
            aqi=aqi_value,
            pm25=components.get('pm2_5', 0),
            pm10=components.get('pm10', 0),
            co=components.get('co', 0),
            no2=components.get('no2', 0),
            status=get_aqi_status(aqi_value),
            recorded_at=timezone.now()
        )

        return {
            "city": city_name,
            "country": country,
            "aqi": aqi_value,
            "pm25": components.get('pm2_5', 0),
            "pm10": components.get('pm10', 0),
            "co": components.get('co', 0),
            "no2": components.get('no2', 0),
            "status": get_aqi_status(aqi_value),
        }

    except Exception as e:
        return {"error": str(e)}