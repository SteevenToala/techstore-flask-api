import psycopg
from psycopg.rows import dict_row
from config import Config
from pymongo import MongoClient

_mongo_client = None

def get_db_connection(read_only=False):
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
        print(f"Error al conectar a la base de datos principal (PostgreSQL): {e}")
        if not read_only:
            return None
        
        # Intentar conectar a la réplica en Render (solo para SELECTs)
        try:
            print("Intentando conexión a la réplica en Render (PostgreSQL)...")
            conn = psycopg.connect(
                host=Config.REPLICA_DB_HOST,
                port=Config.REPLICA_DB_PORT,
                dbname=Config.REPLICA_DB_NAME,
                user=Config.REPLICA_DB_USER,
                password=Config.REPLICA_DB_PASSWORD,
                row_factory=dict_row
            )
            conn.readonly = True
            return conn
        except Exception as replica_err:
            print(f"Error al conectar a la réplica en Render (PostgreSQL): {replica_err}")
            return None

def execute_pg_query(query, params=None, fetch_all=True):
    # 1. Intentar en la base de datos principal
    try:
        conn = psycopg.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            row_factory=dict_row
        )
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall() if fetch_all else cursor.fetchone()
        finally:
            conn.close()
    except Exception as primary_err:
        print(f"Error al ejecutar query en la BD principal (PostgreSQL): {primary_err}")
        
        # 2. Intentar en la réplica en Render
        try:
            print("Intentando ejecutar query en la réplica en Render (PostgreSQL)...")
            conn = psycopg.connect(
                host=Config.REPLICA_DB_HOST,
                port=Config.REPLICA_DB_PORT,
                dbname=Config.REPLICA_DB_NAME,
                user=Config.REPLICA_DB_USER,
                password=Config.REPLICA_DB_PASSWORD,
                row_factory=dict_row
            )
            conn.readonly = True
            try:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    return cursor.fetchall() if fetch_all else cursor.fetchone()
            finally:
                conn.close()
        except Exception as replica_err:
            print(f"Error al ejecutar query en la réplica en Render (PostgreSQL): {replica_err}")
            raise Exception("Tanto la base de datos principal como la réplica de PostgreSQL han fallado.")

def get_mongodb_db():

    global _mongo_client
    if not _mongo_client:
        try:
            _mongo_client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
        except Exception as e:
            print(f"Error al conectar a MongoDB: {e}")
            return None
    try:
        return _mongo_client[Config.MONGO_DB]
    except Exception as e:
        print(f"Error al obtener base de datos MongoDB: {e}")
        return None

def format_datetime(val):
    from datetime import datetime
    if not val:
        return None
    if isinstance(val, datetime):
        return val.strftime('%Y-%m-%dT%H:%M:%SZ')
    if isinstance(val, (int, float)):
        # Si el timestamp está en milisegundos
        if val > 1e11:
            val = val / 1000.0
        try:
            # Usar utcfromtimestamp y formatear
            dt = datetime.utcfromtimestamp(val)
            return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        except Exception:
            pass
    if isinstance(val, str):
        # Si ya es un string, lo devolvemos
        return val
    return str(val)


