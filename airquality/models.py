from django.db import models

class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.name}, {self.country}"


class AirQualityRecord(models.Model):
    STATUS_CHOICES = [
        ('Good', 'Good'),
        ('Moderate', 'Moderate'),
        ('Unhealthy', 'Unhealthy'),
        ('Hazardous', 'Hazardous'),
    ]

    city = models.ForeignKey(City, on_delete=models.CASCADE)
    aqi = models.FloatField()              # Air Quality Index
    pm25 = models.FloatField()             # Fine particles
    pm10 = models.FloatField()             # Coarse particles
    co = models.FloatField()               # Carbon Monoxide
    no2 = models.FloatField()              # Nitrogen Dioxide
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.city.name} - AQI {self.aqi} at {self.recorded_at}"


class AirQualityPrediction(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    predicted_aqi = models.FloatField()
    predicted_status = models.CharField(max_length=20)
    predicted_for = models.DateTimeField()   # Future time
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.city.name} - Predicted AQI {self.predicted_aqi}"


class AlertSubscription(models.Model):
    email = models.EmailField()
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    threshold_aqi = models.FloatField(default=100)  # Alert if AQI crosses this
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.city.name}"