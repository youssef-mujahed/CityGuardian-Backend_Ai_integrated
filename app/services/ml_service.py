import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

# Paths to your model files
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models_ml')

class MLService:
    
    _severity_model = None
    _pipeline = None
    
    @classmethod
    def load_models(cls):
        """Load your trained model and pipeline on startup"""
        
        try:
            # Load your Random Forest model
            model_path = os.path.join(MODEL_PATH, 'accident_severity_rf_model.pkl')
            if os.path.exists(model_path):
                cls._severity_model = joblib.load(model_path)
                print("✅ Severity prediction model loaded")
            else:
                print(f"⚠️ Model not found at {model_path}")
            
            # Load your preprocessing pipeline
            pipeline_path = os.path.join(MODEL_PATH, 'pipeline_data.pkl')
            if os.path.exists(pipeline_path):
                cls._pipeline = joblib.load(pipeline_path)
                print("✅ Preprocessing pipeline loaded")
            else:
                print(f"⚠️ Pipeline not found at {pipeline_path}")
                
        except Exception as e:
            print(f"Error loading models: {e}")
    
    @classmethod
    def predict_severity(cls, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict accident severity (1-3) using your trained model
        """
        
        if cls._severity_model is None:
            return cls._fallback_severity(incident_data)
        
        try:
            # Prepare features for prediction
            features = cls._prepare_features(incident_data)
            
            # Make prediction
            prediction = cls._severity_model.predict([features])[0]
            
            # Get confidence if available
            confidence = 0.7
            if hasattr(cls._severity_model, 'predict_proba'):
                proba = cls._severity_model.predict_proba([features])[0]
                confidence = float(max(proba))
            
            # Ensure severity is between 1 and 3
            severity = int(round(prediction))
            severity = max(1, min(3, severity))
            
            return {
                "predicted_severity": severity,
                "confidence": confidence,
                "severity_level": cls._get_severity_level(severity),
                "recommended_response": cls._get_response_recommendation(severity),
                "model_used": "Random Forest"
            }
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return cls._fallback_severity(incident_data)
    
    @classmethod
    def predict_risk(cls, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict risk score (0-1) for a location
        """
        
        # Get severity prediction as base
        severity_result = cls.predict_severity(location_data)
        base_risk = severity_result["predicted_severity"] / 3.0
        
        # Adjust risk based on time and weather
        risk_score = base_risk
        factors = {}
        
        # Time factor
        hour = location_data.get('hour', datetime.now().hour)
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            risk_score += 0.15
            factors["time"] = "Rush hour"
        elif 22 <= hour or hour <= 5:
            risk_score += 0.05
            factors["time"] = "Night time"
        
        # Weather factor
        weather = location_data.get('weather', 'clear')
        if weather in ['rain', 'rainy', 'storm']:
            risk_score += 0.2
            factors["weather"] = "Rainy conditions"
        elif weather in ['fog', 'foggy', 'mist']:
            risk_score += 0.15
            factors["weather"] = "Fog - low visibility"
        elif weather in ['snow', 'sleet']:
            risk_score += 0.25
            factors["weather"] = "Snow/Icy conditions"
        
        # Traffic factor
        traffic = location_data.get('traffic_density', 'medium')
        if traffic == 'high':
            risk_score += 0.15
            factors["traffic"] = "Heavy traffic"
        elif traffic == 'low':
            risk_score -= 0.05
        
        # Road type factor
        road = location_data.get('road_type', 'urban')
        if road == 'intersection':
            risk_score += 0.1
            factors["road"] = "Intersection"
        elif road == 'highway':
            risk_score += 0.05
            factors["road"] = "Highway"
        
        # Cap at 1.0
        risk_score = min(1.0, max(0.0, risk_score))
        
        return {
            "risk_score": round(risk_score, 2),
            "risk_level": cls._get_risk_level(risk_score),
            "is_high_risk": risk_score > 0.5,
            "factors": factors,
            "base_severity": severity_result
        }
    
    @classmethod
    def _prepare_features(cls, data: Dict[str, Any]) -> List:
        """
        Prepare features in the order your model expects.
        
        IMPORTANT: You need to adjust this based on YOUR train_model.py!
        
        Common features in accident prediction:
        - Hour of day
        - Day of week  
        - Month
        - Weather condition (encoded)
        - Road type (encoded)
        - Speed limit
        - Number of vehicles involved
        - Traffic density
        """
        
        # Time features
        hour = data.get('hour', datetime.now().hour)
        day_of_week = data.get('day_of_week', datetime.now().weekday())
        month = data.get('month', datetime.now().month)
        
        # Location features
        speed_limit = data.get('speed_limit', 60)
        num_vehicles = data.get('estimated_vehicles', 2)
        
        # Encode categorical features
        weather = data.get('weather', 'clear')
        weather_encoded = cls._encode_weather(weather)
        
        road_type = data.get('road_type', 'urban')
        road_encoded = cls._encode_road_type(road_type)
        
        traffic = data.get('traffic_density', 'medium')
        traffic_encoded = cls._encode_traffic(traffic)
        
        # Return features in the SAME ORDER as training
        # YOU MUST MATCH YOUR train_model.py FEATURE ORDER
        return [
            hour,
            day_of_week,
            month,
            speed_limit,
            num_vehicles,
            weather_encoded,
            road_encoded,
            traffic_encoded
        ]
    
    @classmethod
    def _encode_weather(cls, weather: str) -> int:
        """Encode weather condition to integer"""
        weather_map = {
            'clear': 0, 'sunny': 0,
            'cloudy': 1, 'overcast': 1, 'partly cloudy': 1,
            'rain': 2, 'rainy': 2, 'drizzle': 2, 'storm': 2,
            'fog': 3, 'foggy': 3, 'mist': 3, 'haze': 3,
            'snow': 4, 'sleet': 4, 'ice': 4
        }
        return weather_map.get(weather.lower(), 0)
    
    @classmethod
    def _encode_road_type(cls, road_type: str) -> int:
        """Encode road type to integer"""
        road_map = {
            'highway': 0, 'motorway': 0, 'freeway': 0,
            'intersection': 1, 'crossroads': 1, 'junction': 1,
            'urban': 2, 'city': 2, 'street': 2,
            'residential': 3,
            'rural': 4
        }
        return road_map.get(road_type.lower(), 2)
    
    @classmethod
    def _encode_traffic(cls, traffic: str) -> int:
        """Encode traffic density to integer"""
        traffic_map = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'heavy': 3
        }
        return traffic_map.get(traffic.lower(), 2)
    
    @classmethod
    def _get_risk_level(cls, score: float) -> str:
        if score < 0.3:
            return "LOW"
        elif score < 0.6:
            return "MEDIUM"
        else:
            return "HIGH"
    
    @classmethod
    def _get_severity_level(cls, severity: int) -> str:
        levels = {
            1: "MINOR",
            2: "MODERATE",
            3: "SEVERE"
        }
        return levels.get(severity, "MODERATE")
    
    @classmethod
    def _get_response_recommendation(cls, severity: int) -> str:
        if severity == 1:
            return "Standard ambulance response. No immediate life-threatening injuries."
        elif severity == 2:
            return "Priority response. Advanced life support and paramedics required."
        else:
            return "CRITICAL response. Multiple ambulances, trauma team, and air evacuation if needed."
    
    @classmethod
    def _fallback_severity(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback rule-based severity when model unavailable"""
        
        severity = 2  # Start at moderate
        
        # Speed factor
        speed = data.get('speed_limit', 60)
        if speed > 80:
            severity = 3
        elif speed < 40:
            severity = 1
        
        # Vehicle factor
        vehicles = data.get('estimated_vehicles', 2)
        if vehicles >= 3:
            severity = min(3, severity + 1)
        
        # Weather factor
        weather = data.get('weather', 'clear')
        if weather in ['rain', 'fog', 'snow', 'storm']:
            severity = min(3, severity + 1)
        
        return {
            "predicted_severity": severity,
            "confidence": 0.5,
            "severity_level": cls._get_severity_level(severity),
            "recommended_response": cls._get_response_recommendation(severity),
            "model_used": "Rule-based (fallback)"
        }