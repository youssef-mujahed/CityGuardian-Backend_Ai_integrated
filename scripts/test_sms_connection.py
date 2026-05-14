import os
from dotenv import load_dotenv
from moceansdk import Client, Basic

load_dotenv()

token = os.getenv("MOCEAN_API_TOKEN")
print(f"Token found: {token[:20]}..." if token else "❌ No token found")

if token:
    try:
        credential = Basic(api_token=token)
        client = Client(credential)
        balance = client.balance.inquiry()
        print(f"✅ Connection successful! Balance: {balance}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")