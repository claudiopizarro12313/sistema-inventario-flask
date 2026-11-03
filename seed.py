from werkzeug.security import generate_password_hash
from db import conexion

USUARIOS = [
    ("admin@local.cl", "admin123"),
    ("vendedor@local.cl", "vendedor123")
]

def poblar_claves():
    try:
        with conexion() as conn:
            cursor = conn.cursor()
            for email, clave in USUARIOS:
                hash_clave = generate_password_hash(clave)
                cursor.execute(
                    "UPDATE usuarios SET password_hash = :1 WHERE email = :2",
                    (hash_clave, email)
                )
            conn.commit()
            print("✅ Claves de demostración actualizadas correctamente.")
    except Exception as e:
        print(f"❌ Error al actualizar claves: {e}")

if __name__ == "__main__":
    poblar_claves()