from database import get_db_connection, get_mongodb_db, format_datetime, execute_pg_query

class UsuarioModel:
    @staticmethod
    def obtener_todos():
        try:
            return execute_pg_query("SELECT id, firebase_uid, nombres, apellidos, email, rol, telefono, cedula, estado, created_at FROM usuarios WHERE eliminado = FALSE ORDER BY created_at DESC", fetch_all=True)
        except Exception as e:
            print(f"Advertencia: Fallaron bases de datos relacionales para obtener_todos ({e}). Intentando fallback en MongoDB...")
            db = get_mongodb_db()
            if not db:
                raise Exception("Bases de datos PostgreSQL caídas y MongoDB no disponible")
            try:
                usuarios_col = db["usuarios"]
                cursor_mongo = usuarios_col.find({"eliminado": {"$ne": True}}).sort("created_at", -1)
                result = []
                for doc in cursor_mongo:
                    result.append({
                        "id": str(doc.get("id")),
                        "firebase_uid": doc.get("firebase_uid"),
                        "nombres": doc.get("nombres"),
                        "apellidos": doc.get("apellidos"),
                        "email": doc.get("email"),
                        "rol": doc.get("rol"),
                        "telefono": doc.get("telefono"),
                        "cedula": doc.get("cedula"),
                        "estado": doc.get("estado") if doc.get("estado") is not None else True,
                        "created_at": format_datetime(doc.get("created_at"))
                    })
                return result
            except Exception as mongo_err:
                raise Exception(f"Fallo en base de datos principal, réplica y MongoDB: {mongo_err}")

    @staticmethod
    def obtener_por_firebase_uid(firebase_uid):
        try:
            return execute_pg_query("SELECT id, firebase_uid, nombres, apellidos, email, rol, telefono, cedula, estado, eliminado, created_at FROM usuarios WHERE firebase_uid = %s", (firebase_uid,), fetch_all=False)
        except Exception as e:
            print(f"Advertencia: Fallaron bases de datos relacionales para obtener_por_firebase_uid ({e}). Intentando fallback en MongoDB...")
            db = get_mongodb_db()
            if not db:
                raise Exception("Bases de datos PostgreSQL caídas y MongoDB no disponible")
            try:
                usuarios_col = db["usuarios"]
                doc = usuarios_col.find_one({"firebase_uid": firebase_uid})
                if not doc:
                    return None
                return {
                    "id": str(doc.get("id")),
                    "firebase_uid": doc.get("firebase_uid"),
                    "nombres": doc.get("nombres"),
                    "apellidos": doc.get("apellidos"),
                    "email": doc.get("email"),
                    "rol": doc.get("rol"),
                    "telefono": doc.get("telefono"),
                    "cedula": doc.get("cedula"),
                    "estado": doc.get("estado") if doc.get("estado") is not None else True,
                    "eliminado": doc.get("eliminado") if doc.get("eliminado") is not None else False,
                    "created_at": format_datetime(doc.get("created_at"))
                }
            except Exception as mongo_err:
                raise Exception(f"Fallo en base de datos principal, réplica y MongoDB: {mongo_err}")



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
