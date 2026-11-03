import os
import oracledb
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()

def get_connection():
    try:
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        dsn = os.getenv("DB_DSN")
        
        connection = oracledb.connect(
            user=user,
            password=password,
            dsn=dsn
        )
        return connection
    except Exception as e:
        print(f"Error de conexión a Oracle: {e}")
        return None

@contextmanager
def conexion():
    conn = get_connection()
    if conn is None:
        raise RuntimeError("Sin conexión a la base de datos")
    try:
        yield conn
    finally:
        conn.close()