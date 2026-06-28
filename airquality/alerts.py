from django.core.mail import send_mail
from django.conf import settings
from .models import AlertSubscription, City


def get_aqi_advice(aqi):
    if aqi <= 50:
        return {
            "level": "Good ✅",
            "advice": "Air quality is great! Perfect for outdoor activities."
        }
    elif aqi <= 100:
        return {
            "level": "Moderate ⚠️",
            "advice": "Sensitive people should limit prolonged outdoor activity."
        }
    elif aqi <= 200:
        return {
            "level": "Unhealthy 🔴",
            "advice": "Avoid outdoor activities. Wear a mask if going outside."
        }
    else:
        return {
            "level": "Hazardous ☠️",
            "advice": "Stay indoors! Keep windows closed. Use an air purifier."
        }


def send_aqi_alert(city_name, current_aqi):
    try:
        city = City.objects.get(name__iexact=city_name)

        subscriptions = AlertSubscription.objects.filter(
            city=city,
            is_active=True,
            threshold_aqi__lte=current_aqi
        )

        if not subscriptions.exists():
            return {"message": "No subscriptions found."}

        advice = get_aqi_advice(current_aqi)
        alert_count = 0

        for sub in subscriptions:

            subject = f"⚠️ AirSense Alert - {city_name}"

            message = f"""
Hello,

AirSense AI detected poor air quality.

City: {city_name}
Current AQI: {current_aqi}
Status: {advice['level']}
Your Threshold: {sub.threshold_aqi}

Advice:
{advice['advice']}

Stay Safe.

AirSense Team
"""

            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[sub.email],
                    fail_silently=True
                )
                alert_count += 1

            except Exception as e:
                print(f"Alert email failed: {e}")

        return {
            "message": "Alert process completed.",
            "alerts_sent": alert_count
        }

    except Exception as e:
        print(f"send_aqi_alert error: {e}")
        return {"error": str(e)}


def send_welcome_email(email, city_name, threshold):
    """
    Safe welcome email.
    Never crashes the API.
    """

    subject = "✅ AirSense - Subscription Confirmed"

    message = f"""
Hello,

Thank you for subscribing to AirSense!

City: {city_name}
Alert Threshold: AQI {threshold}

You will receive alerts whenever the AQI exceeds your threshold.

Stay Safe!

AirSense Team
"""

    try:

        print(f"Sending welcome email to {email}")

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False
        )

        print("Welcome email sent.")

        return {
            "success": True,
            "message": "Welcome email sent."
        }

    except Exception as e:

        print("Email sending failed:", e)

        return {
            "success": False,
            "message": str(e)
        }