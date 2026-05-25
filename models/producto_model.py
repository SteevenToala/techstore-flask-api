from database import get_db_connection

class ProductoModel:
    @staticmethod
    def obtener_todos():
        # Para el panel administrativo de React, para ver incluso los inactivos
        conn = get_db_connection()
        if not conn:
            raise Exception("Error de conexión a la BD")
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, nombre, descripcion, precio, stock, imagen_url, activo, created_at FROM productos ORDER BY created_at DESC")
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def obtener_activos():
        # Para Flutter (Clientes)
        conn = get_db_connection()
        if not conn:
            raise Exception("Error de conexión a la BD")
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, nombre, descripcion, precio, stock, imagen_url, activo, created_at FROM productos WHERE activo = TRUE")
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def crear(nombre, descripcion, precio, stock, imagen_url):
        conn = get_db_connection()
        if not conn:
            raise Exception("Error de conexión a la BD")
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO productos (nombre, descripcion, precio, stock, imagen_url)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, nombre;
                """, (nombre, descripcion, precio, stock, imagen_url))
                nuevo_producto = cursor.fetchone()
                conn.commit()
                return nuevo_producto
        finally:
            conn.close()

    @staticmethod
    def actualizar(id, nombre, descripcion, precio, stock, imagen_url, activo):
        conn = get_db_connection()
        if not conn:
            raise Exception("Error de conexión a la BD")
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE productos
                    SET nombre = %s, descripcion = %s, precio = %s, stock = %s, imagen_url = %s, activo = %s, updated_at = NOW()
                    WHERE id = %s
                    RETURNING id;
                """, (nombre, descripcion, precio, stock, imagen_url, activo, id))
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
                # Borrado físico, aunque en e-commerce es mejor actualizar el campo 'activo' a false
                cursor.execute("DELETE FROM productos WHERE id = %s RETURNING id;", (id,))
                eliminado = cursor.fetchone()
                conn.commit()
                return eliminado
        finally:
            conn.close()
