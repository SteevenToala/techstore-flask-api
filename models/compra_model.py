from database import get_db_connection

class CompraModel:
    @staticmethod
    def obtener_todas():
        # Para el panel administrativo (React)
        conn = get_db_connection()
        if not conn:
            raise Exception("Error de conexión a la BD")
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT c.id, c.usuario_id, to_char(c.fecha_compra, 'YYYY-MM-DD"T"HH24:MI:SS"Z"') as fecha_compra, c.subtotal, c.iva, c.total, c.estado, c.clave_acceso, 
                           c.direccion_origen, c.direccion_destino, c.latitud_origen, c.longitud_origen, c.latitud_destino, c.longitud_destino, c.metodo_entrega,
                           u.email as usuario_email, u.nombres as usuario_nombres
                    FROM compras c
                    JOIN usuarios u ON c.usuario_id = u.id
                    WHERE c.eliminado = FALSE
                    ORDER BY c.fecha_compra DESC
                """)
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def obtener_por_usuario(usuario_id):
        # Para la App Móvil (Flutter)
        conn = get_db_connection()
        if not conn:
            raise Exception("Error de conexión a la BD")
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, to_char(fecha_compra, 'YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"') as fecha_compra, subtotal, iva, total, estado, clave_acceso, direccion_origen, direccion_destino, latitud_origen, longitud_origen, latitud_destino, longitud_destino, metodo_entrega FROM compras WHERE usuario_id = %s AND eliminado = FALSE ORDER BY fecha_compra DESC", (usuario_id,))
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def crear_compra_y_detalles(usuario_id, subtotal, iva, total, detalles, 
                                direccion_origen=None, direccion_destino=None,
                                latitud_origen=None, longitud_origen=None,
                                latitud_destino=None, longitud_destino=None,
                                metodo_entrega='ENTREGA', estado='PENDIENTE'):
        conn = get_db_connection()
        if not conn:
            raise Exception("Error de conexión a la BD")
        try:
            with conn.cursor() as cursor:
                # Insertar compra principal
                cursor.execute("""
                    INSERT INTO compras (usuario_id, subtotal, iva, total, estado, eliminado, 
                                         direccion_origen, direccion_destino, 
                                         latitud_origen, longitud_origen, 
                                         latitud_destino, longitud_destino, metodo_entrega)
                    VALUES (%s, %s, %s, %s, %s, FALSE, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                """, (usuario_id, subtotal, iva, total, estado,
                      direccion_origen, direccion_destino, 
                      latitud_origen, longitud_origen, 
                      latitud_destino, longitud_destino, metodo_entrega))
                compra_id = cursor.fetchone()['id']


                for d in detalles:
                    cursor.execute("""
                        SELECT stock, nombre, activo, eliminado 
                        FROM productos 
                        WHERE id = %s 
                        FOR UPDATE;
                    """, (d['producto_id'],))
                    producto = cursor.fetchone()
                    
                    if not producto:
                        raise Exception("Producto no encontrado o no existe")
                    if producto['eliminado'] or not producto['activo']:
                        raise Exception(f"El producto '{producto['nombre']}' ya no está disponible")
                    if producto['stock'] < d['cantidad']:
                        raise Exception(f"Stock insuficiente para '{producto['nombre']}'. Disponible: {producto['stock']}, Solicitado: {d['cantidad']}")

                    cursor.execute("""
                        UPDATE productos 
                        SET stock = stock - %s, updated_at = NOW() 
                        WHERE id = %s;
                    """, (d['cantidad'], d['producto_id']))

                    subtotal_detalle = d['cantidad'] * d['precio_unitario']
                    cursor.execute("""
                        INSERT INTO detalle_compra (compra_id, producto_id, cantidad, precio_unitario, subtotal)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (compra_id, d['producto_id'], d['cantidad'], d['precio_unitario'], subtotal_detalle))
                
                conn.commit()
                return compra_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def actualizar_factura(compra_id, clave_acceso, factura_xml):
        conn = get_db_connection()
        if not conn:
            raise Exception("Error de conexión a la BD")
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE compras SET estado = 'FACTURADA', clave_acceso = %s, factura_xml = %s
                    WHERE id = %s
                """, (clave_acceso, factura_xml, compra_id))
                conn.commit()
        finally:
            conn.close()

    @staticmethod
    def eliminar(id):
        conn = get_db_connection()
        if not conn:
            raise Exception("Error de conexión a la BD")
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE compras SET eliminado = TRUE WHERE id = %s RETURNING id;", (id,))
                eliminado = cursor.fetchone()
                conn.commit()
                return eliminado
        finally:
            conn.close()
