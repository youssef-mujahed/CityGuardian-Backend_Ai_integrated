import joblib
import pandas as pd
import warnings
import json
from datetime import datetime

# Suppress sklearn warnings about feature names
warnings.filterwarnings("ignore", category=UserWarning)

class AccidentAlertSystem:
    def __init__(self, model_path='accident_severity_rf_model.pkl', pipeline_path='pipeline_data.pkl'):
        """Initializes the Alert System by loading the trained ML model."""
        try:
            self.model = joblib.load(model_path)
            pipeline_data = joblib.load(pipeline_path)
            self.label_encoders = pipeline_data['label_encoders']
            self.feature_names = pipeline_data['feature_names']
            print("Successfully loaded the AI Prediction Model.")
        except FileNotFoundError:
            print("Error: Could not find model files. Have you trained the model yet?")
            self.model = None
            
    def _preprocess_live_data(self, event_data: dict) -> pd.DataFrame:
        """Converts raw live JSON sensor data into the numerical format the ML model expects."""
        df_event = pd.DataFrame([event_data])
        
        for col, le in self.label_encoders.items():
            if col in df_event.columns:
                try:
                    df_event[col] = le.transform(df_event[col].astype(str))
                except ValueError:
                    # If dealing with an entirely new city or weather condition we've never seen
                    df_event[col] = 0
                    
        # Ensure we send the columns in the exact order the model was trained on
        return df_event[self.feature_names]

    def evaluate_live_risk(self, event_data: dict, severity_3_threshold=0.35, severity_4_threshold=0.20) -> dict:
        """
        Evaluates the current road/weather conditions and generates an Alert if it meets the criteria.
        
        Args:
            event_data (dict): The live sensor/weather data for a specific road segment.
            severity_3_threshold (float): Only trigger Severe Alerts if ML confidence exceeds this (e.g. 35%)
            severity_4_threshold (float): Only trigger Critical Alerts if ML confidence exceeds this (e.g. 20%)
        """
        if not self.model: return None
        
        # 1. Prepare data
        processed_data = self._preprocess_live_data(event_data)
        
        # 2. Get AI Prediction
        predicted_severity = self.model.predict(processed_data)[0]
        # Get the probability array: [Prob(Sev 1), Prob(Sev 2), Prob(Sev 3), Prob(Sev 4)]
        probabilities = self.model.predict_proba(processed_data)[0]
        
        prob_sev3 = probabilities[2]
        prob_sev4 = probabilities[3]
        
        # 3. Decision Logic for Alerts
        alert = None
        
        # Check for Critical System Alert (Severity 4)
        if prob_sev4 >= severity_4_threshold:
            alert = {
                "alert_uuid": f"ALERT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "level": "CRITICAL",
                "message": f"CRITICAL ACCIDENT PREDICTED. Rapid response likely required. {event_data['Weather_Condition']} conditions identified.",
                "location": f"{event_data['City']}, {event_data['State']} [GPS: {event_data['Start_Lat']}, {event_data['Start_Lng']}]",
                "ai_confidence": round(prob_sev4 * 100, 1),
                "recommended_action": "Deploy preliminary traffic control and alert nearest emergency units."
            }
        # Check for Severe Alert (Severity 3)
        elif prob_sev3 >= severity_3_threshold:
            alert = {
                "alert_uuid": f"ALERT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "level": "HIGH",
                "message": f"HIGH RISK OF SEVERE ACCIDENT. Increased caution advised due to {event_data['Weather_Condition']}.",
                "location": f"{event_data['City']}, {event_data['State']} [GPS: {event_data['Start_Lat']}, {event_data['Start_Lng']}]",
                "ai_confidence": round(prob_sev3 * 100, 1),
                "recommended_action": "Enable digital warning signs and monitor cameras at this junction."
            }
            
        # Return the generated alert object, or None if conditions are safe
        return alert

def main():
    print("--- Predictive Early Warning Alert System (Simulated Dashboard Test) ---\n")
    
    alert_system = AccidentAlertSystem()
    
    # Let's simulate a stream of incoming live data from sensors around the city
    live_traffic_events = [
        # Event 1: Normal sunny day, no major risk
        {
            'Start_Lat': 34.0522, 'Start_Lng': -118.2437, 'City': 'Los Angeles', 'State': 'CA',
            'Temperature(F)': 75.0, 'Humidity(%)': 40.0, 'Visibility(mi)': 10.0, 'Wind_Speed(mph)': 8.0, 
            'Precipitation(in)': 0.0, 'Weather_Condition': 'Clear', 'Traffic_Signal': True, 
            'Crossing': True, 'Junction': False, 'Sunrise_Sunset': 'Day'
        },
        # Event 2: Dangerous condition: Heavy rain at night at a tricky junction
        {
            'Start_Lat': 40.7128, 'Start_Lng': -74.0060, 'City': 'New York', 'State': 'NY',
            'Temperature(F)': 35.0, 'Humidity(%)': 95.0, 'Visibility(mi)': 1.0, 'Wind_Speed(mph)': 25.0, 
            'Precipitation(in)': 2.5, 'Weather_Condition': 'Heavy Rain', 'Traffic_Signal': False, 
            'Crossing': False, 'Junction': True, 'Sunrise_Sunset': 'Night'
        },
        # Event 3: Bad condition: Snowing on a highway 
        {
            'Start_Lat': 41.8781, 'Start_Lng': -87.6298, 'City': 'Chicago', 'State': 'IL',
            'Temperature(F)': 20.0, 'Humidity(%)': 80.0, 'Visibility(mi)': 0.5, 'Wind_Speed(mph)': 30.0, 
            'Precipitation(in)': 1.0, 'Weather_Condition': 'Snow', 'Traffic_Signal': False, 
            'Crossing': False, 'Junction': False, 'Sunrise_Sunset': 'Night'
        }
    ]
    
    print("Beginning live monitoring scan...\n" + "="*50)
    
    generated_alerts = []
    
    for i, event in enumerate(live_traffic_events):
        print(f"Scanning Event {i+1}... Location: {event['City']}, {event['State']} | Weather: {event['Weather_Condition']}")
        
        # Evaluate Risk
        alert = alert_system.evaluate_live_risk(event)
        
        if alert:
            print(f"🚨 ALERT TRIGGERED -> Level: {alert['level']} (Confidence: {alert['ai_confidence']}%)")
            print(f"   Message: {alert['message']}")
            print(f"   Action: {alert['recommended_action']}")
            generated_alerts.append(alert)
        else:
            print("✅ Status Safe. No critical risks detected.")
        print("-" * 50)
        
    print(f"\nScan complete. Total active alerts generated: {len(generated_alerts)}")
    
    # Export the alerts as JSON to simulate sending them to a Web Dashboard via API
    with open('active_alerts_feed.json', 'w') as f:
        json.dump(generated_alerts, f, indent=4)
    print("Saved active alerts stream to 'active_alerts_feed.json'")

if __name__ == '__main__':
    main()
