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

    # MongoDB Fallback
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://alexander:k61TcuAxk58R32rb@cluster0.idsrzjx.mongodb.net/?retryWrites=true&w=majority")
    MONGO_DB = os.getenv("MONGO_DB", "distribuidas")

    # Render PostgreSQL Replica Fallback
    REPLICA_DB_HOST = os.getenv("REPLICA_DB_HOST", "dpg-d8c6rupkh4rs738khcmg-a.oregon-postgres.render.com")
    REPLICA_DB_PORT = os.getenv("REPLICA_DB_PORT", "5432")
    REPLICA_DB_NAME = os.getenv("REPLICA_DB_NAME", "db_replica_distribuidas")
    REPLICA_DB_USER = os.getenv("REPLICA_DB_USER", "db_replica_distribuidas_user")
    REPLICA_DB_PASSWORD = os.getenv("REPLICA_DB_PASSWORD", "EP0q6FXg0dgJ9j7tF1vZFbPxjSd9QJzO")


