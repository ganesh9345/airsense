from django.contrib import admin
from .models import City, AirQualityRecord, AirQualityPrediction, AlertSubscription

admin.site.register(City)
admin.site.register(AirQualityRecord)
admin.site.register(AirQualityPrediction)
admin.site.register(AlertSubscription)