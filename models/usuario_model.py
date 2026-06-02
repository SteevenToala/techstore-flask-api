from database import get_db_connection

class UsuarioModel:
    @staticmethod
    def obtener_todos():
        conn = get_db_connection()
        if not conn:
            raise Exception("Error de conexión a la BD")
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, firebase_uid, nombres, apellidos, email, rol, telefono, cedula, estado, created_at FROM usuarios WHERE eliminado = FALSE ORDER BY created_at DESC")
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def obtener_por_firebase_uid(firebase_uid):
        conn = get_db_connection()
        if not conn:
            raise Exception("Error de conexión a la BD")
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, firebase_uid, nombres, apellidos, email, rol, telefono, cedula, estado, eliminado, created_at FROM usuarios WHERE firebase_uid = %s", (firebase_uid,))
                return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def crear(firebase_uid, nombres, apellidos, email, rol, telefono, cedula):
        conn = get_db_connection()
        if not conn:
            raise Exception("Error de conexión a la BD")
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO usuarios (firebase_uid, nombres, apellidos, email, rol, telefono, cedula, eliminado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE)
                    RETURNING id, nombres, email, cedula;
                """, (firebase_uid, nombres, apellidos, email, rol, telefono, cedula))
                nuevo_usuario = cursor.fetchone()
                conn.commit()
                return nuevo_usuario
        finally:
            conn.close()

    @staticmethod
    def actualizar(id, nombres, apellidos, rol, telefono, cedula, estado):
        conn = get_db_connection()
        if not conn:
            raise Exception("Error de conexión a la BD")
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE usuarios 
                    SET nombres = %s, apellidos = %s, rol = %s, telefono = %s, cedula = %s, estado = %s, updated_at = NOW()
                    WHERE id = %s
                    RETURNING id;
                """, (nombres, apellidos, rol, telefono, cedula, estado, id))
                actualizado = cursor.fetchone()
                conn.commit()
                return actualizado
        finally:
            conn.close()

    @staticmethod
    def eliminar(id):
        conn = get_db_connection()
        if not conn:
            raise Exception("Error de conexión a la BD")
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE usuarios SET eliminado = TRUE, updated_at = NOW() WHERE id = %s RETURNING id;", (id,))
                eliminado = cursor.fetchone()
                conn.commit()
                return eliminado
        finally:
            conn.close()
