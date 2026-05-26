import psycopg
from psycopg.rows import dict_row
from config import Config

def get_db_connection():
    try:
        conn = psycopg.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            row_factory=dict_row
        )
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
