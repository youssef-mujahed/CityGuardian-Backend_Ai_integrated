from dotenv import load_dotenv
import os

load_dotenv()

print("SMS_EMAIL:", os.getenv("SMS_SENDER_EMAIL"))
print("SMS_PASSWORD:", os.getenv("SMS_SENDER_PASSWORD"))