#!/usr/bin/env python
"""Test the risk prediction API"""

import requests
import json

BASE_URL = "http://localhost:8000"

# First, login to get token
print("1. Logging in...")
login_response = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    json={"email": "test@example.com", "password": "Test123!"}
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print("Make sure you have a test user created")
    exit()

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✅ Logged in successfully")

# Test risk prediction
print("\n2. Testing risk prediction...")
risk_response = requests.post(
    f"{BASE_URL}/api/v1/risk/predict",
    headers=headers,
    json={
        "latitude": 30.0444,
        "longitude": 31.2357,
        "weather": "rain",
        "traffic_density": "high",
        "road_type": "intersection",
        "speed_limit": 80,
        "estimated_vehicles": 2
    }
)

if risk_response.status_code == 200:
    print("✅ Risk prediction successful:")
    print(json.dumps(risk_response.json(), indent=2))
else:
    print(f"❌ Failed: {risk_response.status_code}")
    print(risk_response.text)

# Test severity prediction
print("\n3. Testing severity prediction...")
severity_response = requests.post(
    f"{BASE_URL}/api/v1/risk/severity",
    headers=headers,
    json={
        "latitude": 30.0444,
        "longitude": 31.2357,
        "speed_limit": 100,
        "estimated_vehicles": 3,
        "weather": "rain",
        "road_type": "highway",
        "traffic_density": "high"
    }
)

if severity_response.status_code == 200:
    print("✅ Severity prediction successful:")
    print(json.dumps(severity_response.json(), indent=2))
else:
    print(f"❌ Failed: {severity_response.status_code}")
    print(severity_response.text)

# Check model health
print("\n4. Checking model health...")
health_response = requests.get(
    f"{BASE_URL}/api/v1/risk/health",
    headers=headers
)

if health_response.status_code == 200:
    print("✅ Model status:")
    print(json.dumps(health_response.json(), indent=2))

print("\n✅ Testing complete!")