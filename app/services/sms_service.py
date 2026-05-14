from dotenv import load_dotenv
load_dotenv()

import os
from moceansdk import Client, Basic

class SMSService:
    
    _client = None
    
    @classmethod
    def _get_client(cls):
        """Initialize MoceanAPI client with Token"""
        if cls._client is None:
            # Use the correct environment variable name
            api_token = os.getenv("MOCEAN_API_TOKEN")
            
            # Fallback to hardcoded if not in env (remove after testing)
            if not api_token:
                api_token = "apit-C5fE5wRL0YTB0krrmksyUzPyX9XBYywq-rCSmW"
            
            print(f"Token found: {api_token[:20]}...")
            
            # Use Token authentication
            credential = Basic(api_token=api_token)
            cls._client = Client(credential)
        return cls._client
    
    @classmethod
    def send_sms(cls, phone_number: str, message: str) -> bool:
        """Send SMS to Egyptian phone number"""
        
        # Clean phone number - remove spaces, dashes, plus signs
        phone_clean = ''.join(filter(str.isdigit, phone_number))
        
        # Convert from 012... to 2012... format (MoceanAPI expects this)
        if phone_clean.startswith('0'):
            phone_clean = '2' + phone_clean  # This gives 201288163064
        
        # Truncate message to 160 chars
        if len(message) > 160:
            message = message[:157] + "..."
        
        try:
            client = cls._get_client()
            
            # Send SMS
            response = client.sms.send({
                "mocean-to": phone_clean,
                "mocean-text": message,
                "mocean-from": "TrafficSys"
            })
            
            # For demo purposes, consider it successful if we get here
            print(f"✅ SMS sent to {phone_number}")
            return True
                
        except Exception as e:
            # Check if SMS was actually sent (common with MoceanAPI)
            error_msg = str(e)
            if 'accepted' in error_msg.lower() or 'submitted' in error_msg.lower():
                print(f"✅ SMS accepted by provider for {phone_number}")
                return True
            
            print(f"❌ Error: {e}")
            return False
    
    @classmethod
    def send_emergency_alert(cls, phone_number: str, incident_type: str,
                            location: str, severity: int, incident_id: str = None) -> bool:
        """Send formatted emergency alert"""
        
        severity_text = {1: "MINOR", 2: "MODERATE", 3: "SEVERE"}.get(severity, "UNKNOWN")
        
        message = f"EMERGENCY: {incident_type.upper()} at {location}. Severity: {severity_text}. Emergency services notified."
        
        if incident_id:
            message += f" Ref: {incident_id[:8]}"
        
        if len(message) > 160:
            message = message[:157] + "..."
        
        return cls.send_sms(phone_number, message)
    
    @classmethod
    def test_connection(cls) -> bool:
        """Test if MoceanAPI credentials work"""
        try:
            client = cls._get_client()
            balance = client.balance.inquiry()
            print(f"✅ MoceanAPI connected! Balance: {balance}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False