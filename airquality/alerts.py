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
            "advice": "Stay indoors! Keep windows closed. Use air purifier."
        }


def send_aqi_alert(city_name, current_aqi):
    try:
        city = City.objects.get(name=city_name)

        # Get all active subscriptions where AQI crossed threshold
        subscriptions = AlertSubscription.objects.filter(
            city=city,
            is_active=True,
            threshold_aqi__lte=current_aqi
        )

        if not subscriptions:
            return {"message": "No subscriptions to alert"}

        advice = get_aqi_advice(current_aqi)
        alert_count = 0

        for sub in subscriptions:
            email_subject = f"⚠️ AirSense Alert — {city_name} Air Quality Warning!"

            email_body = f"""
Hello,

AirSense AI has detected dangerous air quality levels in {city_name}.

━━━━━━━━━━━━━━━━━━━━━━
📍 City        : {city_name}
💨 Current AQI : {current_aqi}
🚦 Status      : {advice['level']}
⚡ Your Limit  : {sub.threshold_aqi}
━━━━━━━━━━━━━━━━━━━━━━

💡 What You Should Do:
{advice['advice']}

General Precautions:
- Avoid outdoor exercise
- Keep doors and windows closed
- Use an air purifier indoors
- Wear N95 mask if going outside
- Keep children and elderly indoors

━━━━━━━━━━━━━━━━━━━━━━
Stay Safe & Healthy! 💚
AirSense Team
Powered by AI & Django
━━━━━━━━━━━━━━━━━━━━━━
            """

            send_mail(
                subject=email_subject,
                message=email_body,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[sub.email],
                fail_silently=False
            )
            alert_count += 1

        return {
            "message": f"Alerts sent successfully!",
            "alerts_sent": alert_count,
            "city": city_name,
            "aqi": current_aqi
        }

    except City.DoesNotExist:
        return {"error": f"City {city_name} not found"}
    except Exception as e:
        return {"error": str(e)}


def send_welcome_email(email, city_name, threshold):
    try:
        send_mail(
            subject="✅ AirSense — Alert Subscription Confirmed!",
            message=f"""
Hello,

You have successfully subscribed to AirSense air quality alerts!

━━━━━━━━━━━━━━━━━━━━━━
📍 City         : {city_name}
🔔 Alert Threshold : AQI {threshold}
━━━━━━━━━━━━━━━━━━━━━━

You will receive an alert whenever the AQI in {city_name}
crosses {threshold}.

Thank you for using AirSense! 💚
Stay Safe!

AirSense Team
━━━━━━━━━━━━━━━━━━━━━━
            """,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False
        )
        return {"message": "Welcome email sent!"}
    except Exception as e:
        return {"error": str(e)}