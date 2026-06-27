import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from .models import AirQualityRecord
import pickle
import os

# Path to save trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'aqi_model.pkl')

def prepare_data():
    # Fetch all records from database
    records = AirQualityRecord.objects.all().values(
        'aqi', 'pm25', 'pm10', 'co', 'no2', 'recorded_at'
    )

    if len(records) < 10:
        return None, None

    df = pd.DataFrame(list(records))

    # Extract time features
    df['hour'] = pd.to_datetime(df['recorded_at']).dt.hour
    df['day'] = pd.to_datetime(df['recorded_at']).dt.day
    df['month'] = pd.to_datetime(df['recorded_at']).dt.month

    # Features and Target
    features = ['pm25', 'pm10', 'co', 'no2', 'hour', 'day', 'month']
    X = df[features]
    y = df['aqi']

    return X, y


def train_model():
    X, y = prepare_data()

    if X is None:
        return {"error": "Not enough data to train. Fetch more records first."}

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train Random Forest model
    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )
    model.fit(X_train, y_train)

    # Check accuracy
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)

    # Save model to file
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)

    return {
        "status": "Model trained successfully!",
        "mean_absolute_error": round(mae, 2),
        "total_records_used": len(X)
    }


def predict_aqi(pm25, pm10, co, no2, hour, day, month):
    # Load saved model
    if not os.path.exists(MODEL_PATH):
        return {"error": "Model not trained yet. Please train first."}

    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)

    # Prepare input
    input_data = pd.DataFrame([{
        'pm25': pm25,
        'pm10': pm10,
        'co': co,
        'no2': no2,
        'hour': hour,
        'day': day,
        'month': month
    }])

    predicted_aqi = model.predict(input_data)[0]

    # Get status
    if predicted_aqi <= 50:
        status = "Good"
    elif predicted_aqi <= 100:
        status = "Moderate"
    elif predicted_aqi <= 200:
        status = "Unhealthy"
    else:
        status = "Hazardous"

    return {
        "predicted_aqi": round(predicted_aqi, 2),
        "predicted_status": status
    }