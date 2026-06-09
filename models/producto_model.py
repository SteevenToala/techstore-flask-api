from database import get_db_connection, get_mongodb_db, format_datetime, execute_pg_query

class ProductoModel:
    @staticmethod
    def obtener_todos():
        # Para el panel administrativo de React, para ver incluso los inactivos
        try:
            return execute_pg_query("SELECT id, nombre, descripcion, precio, stock, imagen_url, activo, created_at FROM productos WHERE eliminado = FALSE ORDER BY created_at DESC", fetch_all=True)
        except Exception as e:
            print(f"Advertencia: Fallaron bases de datos relacionales para obtener_todos de productos ({e}). Intentando fallback en MongoDB...")
            db = get_mongodb_db()
            if not db:
                raise Exception("Bases de datos PostgreSQL caídas y MongoDB no disponible")
            try:
                productos_col = db["productos"]
                cursor_mongo = productos_col.find({"eliminado": {"$ne": True}}).sort("created_at", -1)
                result = []
                for doc in cursor_mongo:
                    result.append({
                        "id": str(doc.get("id")),
                        "nombre": doc.get("nombre"),
                        "descripcion": doc.get("descripcion"),
                        "precio": float(doc.get("precio")) if doc.get("precio") is not None else 0.0,
                        "stock": int(doc.get("stock")) if doc.get("stock") is not None else 0,
                        "imagen_url": doc.get("imagen_url"),
                        "activo": doc.get("activo") if doc.get("activo") is not None else True,
                        "created_at": format_datetime(doc.get("created_at"))
                    })
                return result
            except Exception as mongo_err:
                raise Exception(f"Fallo en base de datos principal, réplica y MongoDB: {mongo_err}")

    @staticmethod
    def obtener_activos():
        # Para Flutter (Clientes)
        try:
            return execute_pg_query("SELECT id, nombre, descripcion, precio, stock, imagen_url, activo, created_at FROM productos WHERE activo = TRUE AND eliminado = FALSE", fetch_all=True)
        except Exception as e:
            print(f"Advertencia: Fallaron bases de datos relacionales para obtener_activos de productos ({e}). Intentando fallback en MongoDB...")
            db = get_mongodb_db()
            if not db:
                raise Exception("Bases de datos PostgreSQL caídas y MongoDB no disponible")
            try:
                productos_col = db["productos"]
                cursor_mongo = productos_col.find({"activo": True, "eliminado": {"$ne": True}})
                result = []
                for doc in cursor_mongo:
                    result.append({
                        "id": str(doc.get("id")),
                        "nombre": doc.get("nombre"),
                        "descripcion": doc.get("descripcion"),
                        "precio": float(doc.get("precio")) if doc.get("precio") is not None else 0.0,
                        "stock": int(doc.get("stock")) if doc.get("stock") is not None else 0,
                        "imagen_url": doc.get("imagen_url"),
                        "activo": doc.get("activo") if doc.get("activo") is not None else True,
                        "created_at": format_datetime(doc.get("created_at"))
                    })
                return result
            except Exception as mongo_err:
                raise Exception(f"Fallo en base de datos principal, réplica y MongoDB: {mongo_err}")



    @staticmethod
    def crear(nombre, descripcion, precio, stock, imagen_url):
        conn = get_db_connection()
        if not conn:
            raise Exception("Error de conexión a la BD")
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO productos (nombre, descripcion, precio, stock, imagen_url, eliminado)
                    VALUES (%s, %s, %s, %s, %s, FALSE)
                    RETURNING id, nombre;
                """, (nombre, descripcion, precio, stock, imagen_url))
                nuevo_producto = cursor.fetchone()
                conn.commit()
                return nuevo_producto
        finally:
            conn.close()

    @staticmethod
    def actualizar(id, campos):
        conn = get_db_connection()
        if not conn:
            raise Exception("Error de conexión a la BD")
        try:
            with conn.cursor() as cursor:
                set_clauses = []
                values = []
                for campo, valor in campos.items():
                    set_clauses.append(f"{campo} = %s")
                    values.append(valor)
                
                set_clauses.append("updated_at = NOW()")
                query = f"""
                    UPDATE productos
                    SET {', '.join(set_clauses)}
                    WHERE id = %s
                    RETURNING id;
                """
                values.append(id)
                cursor.execute(query, tuple(values))
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
                cursor.execute("UPDATE productos SET eliminado = TRUE, updated_at = NOW() WHERE id = %s RETURNING id;", (id,))
                eliminado = cursor.fetchone()
                conn.commit()
                return eliminado
        finally:
            conn.close()
