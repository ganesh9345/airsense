from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .models import City, AirQualityRecord, AirQualityPrediction, AlertSubscription
from .fetch_data import fetch_air_quality
from .ml_model import train_model, predict_aqi
from .alerts import send_aqi_alert, send_welcome_email
from django.utils import timezone
from datetime import timedelta


# ─────────────────────────────────────────
# PAGE VIEWS
# ─────────────────────────────────────────
def home_page(request):
    return render(request, 'airquality/home.html')

def dashboard_page(request):
    return render(request, 'airquality/dashboard.html')

def subscribe_page(request):
    return render(request, 'airquality/subscribe.html')


# ─────────────────────────────────────────
# 1. FETCH CURRENT AIR QUALITY
# ─────────────────────────────────────────
@api_view(['GET'])
def get_air_quality(request, city_name):
    result = fetch_air_quality(city_name)

    if "error" in result:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    # Trigger alert check
    send_aqi_alert(city_name, result['aqi'])

    return Response(result, status=status.HTTP_200_OK)


# ─────────────────────────────────────────
# 2. TRAIN ML MODEL
# ─────────────────────────────────────────
@api_view(['POST'])
def train_ml_model(request):
    result = train_model()
    return Response(result, status=status.HTTP_200_OK)


# ─────────────────────────────────────────
# 3. PREDICT FUTURE AQI
# ─────────────────────────────────────────
@api_view(['POST'])
def predict_future_aqi(request):
    data = request.data

    result = predict_aqi(
        pm25=data.get('pm25', 0),
        pm10=data.get('pm10', 0),
        co=data.get('co', 0),
        no2=data.get('no2', 0),
        hour=data.get('hour', 12),
        day=data.get('day', 1),
        month=data.get('month', 1)
    )

    # Save prediction to DB
    if "predicted_aqi" in result:
        city_name = data.get('city', '')
        try:
            city = City.objects.get(name=city_name)
            AirQualityPrediction.objects.create(
                city=city,
                predicted_aqi=result['predicted_aqi'],
                predicted_status=result['predicted_status'],
                predicted_for=timezone.now() + timedelta(hours=24)
            )
        except City.DoesNotExist:
            pass

    return Response(result, status=status.HTTP_200_OK)


# ─────────────────────────────────────────
# 4. SUBSCRIBE TO ALERTS
# ─────────────────────────────────────────
@api_view(['POST'])
def subscribe_alert(request):
    email = request.data.get('email')
    city_name = request.data.get('city')
    threshold = request.data.get('threshold_aqi', 100)

    try:
        city = City.objects.get(name=city_name)
    except City.DoesNotExist:
        return Response(
            {"error": "City not found. Please fetch city data first."},
            status=status.HTTP_400_BAD_REQUEST
        )

    subscription, created = AlertSubscription.objects.get_or_create(
        email=email,
        city=city,
        defaults={'threshold_aqi': threshold}
    )

    # Send welcome email
    send_welcome_email(email, city_name, threshold)

    return Response({
        "message": f"Successfully subscribed to alerts for {city_name}!",
        "email": email,
        "threshold_aqi": threshold
    }, status=status.HTTP_200_OK)


# ─────────────────────────────────────────
# 5. GET HISTORY OF A CITY
# ─────────────────────────────────────────
@api_view(['GET'])
def get_history(request, city_name):
    try:
        city = City.objects.get(name=city_name)
        records = AirQualityRecord.objects.filter(
            city=city
        ).order_by('-recorded_at')[:20]

        data = [{
            "aqi": r.aqi,
            "pm25": r.pm25,
            "pm10": r.pm10,
            "status": r.status,
            "recorded_at": r.recorded_at
        } for r in records]

        return Response(data, status=status.HTTP_200_OK)

    except City.DoesNotExist:
        return Response(
            {"error": "City not found"},
            status=status.HTTP_404_NOT_FOUND
        )


# ─────────────────────────────────────────
# 6. DASHBOARD DATA
# ─────────────────────────────────────────
@api_view(['GET'])
def dashboard_data(request):
    records = AirQualityRecord.objects.all()

    total = records.count()
    good = records.filter(status='Good').count()
    moderate = records.filter(status='Moderate').count()
    unhealthy = records.filter(status='Unhealthy').count()
    hazardous = records.filter(status='Hazardous').count()

    return Response({
        "total_records": total,
        "good": good,
        "moderate": moderate,
        "unhealthy": unhealthy,
        "hazardous": hazardous
    }, status=status.HTTP_200_OK)


# ─────────────────────────────────────────
# 7. SEND MANUAL ALERT (TESTING)
# ─────────────────────────────────────────
@api_view(['POST'])
def trigger_alert(request):
    city_name = request.data.get('city')
    aqi = request.data.get('aqi')

    if not city_name or not aqi:
        return Response(
            {"error": "Please provide city and aqi"},
            status=status.HTTP_400_BAD_REQUEST
        )

    result = send_aqi_alert(city_name, float(aqi))
    return Response(result, status=status.HTTP_200_OK)