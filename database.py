import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
