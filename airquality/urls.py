from django.urls import path
from . import views

urlpatterns = [
    # Page URLs
    path('', views.home_page, name='home'),
    path('dashboard/', views.dashboard_page, name='dashboard'),
    path('subscribe/', views.subscribe_page, name='subscribe'),

    # API URLs
    path('api/air-quality/<str:city_name>/',
         views.get_air_quality, name='get_air_quality'),
    path('api/train/',
         views.train_ml_model, name='train_model'),
    path('api/predict/',
         views.predict_future_aqi, name='predict_aqi'),
    path('api/subscribe/',
         views.subscribe_alert, name='subscribe_alert'),
    path('api/history/<str:city_name>/',
         views.get_history, name='get_history'),
    path('api/dashboard/',
         views.dashboard_data, name='dashboard_data'),
    path('api/trigger-alert/',
         views.trigger_alert, name='trigger_alert'),
     path("test-email/", views.test_email),
]