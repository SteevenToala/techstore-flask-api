import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Supabase
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "postgres")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

    # Firebase
    FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS", "firebase-key.json")

    # SOAP Service URL
    SOAP_SERVICE_URL = os.getenv("SOAP_SERVICE_URL", "http://localhost:8000/soap")
