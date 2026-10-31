import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    APP_NAME = "TRUSTLAYER AI"
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trustlayer.db")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "")
    PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", "")
    PAYPAL_BASE_URL = os.getenv("PAYPAL_BASE_URL", "https://api-m.sandbox.paypal.com")
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    DEMO_USER_ID = "demo-user"

settings = Settings()
