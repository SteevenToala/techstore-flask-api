from database import get_db_connection, get_mongodb_db, format_datetime, execute_pg_query

class CompraModel:
    @staticmethod
    def obtener_todas():
        # Para el panel administrativo (React)
        try:
            return execute_pg_query("""
                SELECT c.id, c.usuario_id, to_char(c.fecha_compra, 'YYYY-MM-DD"T"HH24:MI:SS"Z"') as fecha_compra, c.subtotal, c.iva, c.total, c.estado, c.clave_acceso, 
                       c.direccion_origen, c.direccion_destino, c.latitud_origen, c.longitud_origen, c.latitud_destino, c.longitud_destino, c.metodo_entrega,
                       u.email as usuario_email, u.nombres as usuario_nombres
                FROM compras c
                JOIN usuarios u ON c.usuario_id = u.id
                WHERE c.eliminado = FALSE
                ORDER BY c.fecha_compra DESC
            """, fetch_all=True)
        except Exception as e:
            print(f"Advertencia: Fallaron bases de datos relacionales para obtener_todas de compras ({e}). Intentando fallback en MongoDB...")
            db = get_mongodb_db()
            if not db:
                raise Exception("Bases de datos PostgreSQL caídas y MongoDB no disponible")
            try:
                compras_col = db["compras"]
                usuarios_col = db["usuarios"]
                
                cursor_mongo = compras_col.find({"eliminado": {"$ne": True}}).sort("fecha_compra", -1)
                result = []
                for doc in cursor_mongo:
                    user_id = doc.get("usuario_id")
                    user_doc = None
                    if user_id:
                        user_doc = usuarios_col.find_one({"$or": [{"id": user_id}, {"id": str(user_id)}]})
                    
                    lat_o = float(doc.get("latitud_origen")) if doc.get("latitud_origen") is not None else None
                    lon_o = float(doc.get("longitud_origen")) if doc.get("longitud_origen") is not None else None
                    lat_d = float(doc.get("latitud_destino")) if doc.get("latitud_destino") is not None else None
                    lon_d = float(doc.get("longitud_destino")) if doc.get("longitud_destino") is not None else None

                    result.append({
                        "id": str(doc.get("id")),
                        "usuario_id": str(user_id) if user_id else None,
                        "fecha_compra": format_datetime(doc.get("fecha_compra")),
                        "subtotal": float(doc.get("subtotal")) if doc.get("subtotal") is not None else 0.0,
                        "iva": float(doc.get("iva")) if doc.get("iva") is not None else 0.0,
                        "total": float(doc.get("total")) if doc.get("total") is not None else 0.0,
                        "estado": doc.get("estado") if doc.get("estado") is not None else "PENDIENTE",
                        "clave_acceso": doc.get("clave_acceso"),
                        "direccion_origen": doc.get("direccion_origen"),
                        "direccion_destino": doc.get("direccion_destino"),
                        "latitud_origen": lat_o,
                        "longitud_origen": lon_o,
                        "latitud_destino": lat_d,
                        "longitud_destino": lon_d,
                        "metodo_entrega": doc.get("metodo_entrega") if doc.get("metodo_entrega") is not None else "ENTREGA",
                        "usuario_email": user_doc.get("email") if user_doc else None,
                        "usuario_nombres": user_doc.get("nombres") if user_doc else None
                    })
                return result
            except Exception as mongo_err:
                raise Exception(f"Fallo en base de datos principal, réplica y MongoDB: {mongo_err}")

    @staticmethod
    def obtener_por_usuario(usuario_id):
        # Para la App Móvil (Flutter)
        try:
            return execute_pg_query("SELECT id, to_char(fecha_compra, 'YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"') as fecha_compra, subtotal, iva, total, estado, clave_acceso, direccion_origen, direccion_destino, latitud_origen, longitud_origen, latitud_destino, longitud_destino, metodo_entrega FROM compras WHERE usuario_id = %s AND eliminado = FALSE ORDER BY fecha_compra DESC", (usuario_id,), fetch_all=True)
        except Exception as e:
            print(f"Advertencia: Fallaron bases de datos relacionales para obtener_por_usuario ({e}). Intentando fallback en MongoDB...")
            db = get_mongodb_db()
            if not db:
                raise Exception("Bases de datos PostgreSQL caídas y MongoDB no disponible")
            try:
                compras_col = db["compras"]
                
                import uuid
                u_str = str(usuario_id)
                try:
                    u_uuid = uuid.UUID(u_str)
                except ValueError:
                    u_uuid = None

                query = {
                    "$or": [
                        {"usuario_id": u_str},
                        {"usuario_id": u_uuid}
                    ] if u_uuid else [{"usuario_id": u_str}],
                    "eliminado": {"$ne": True}
                }
                
                cursor_mongo = compras_col.find(query).sort("fecha_compra", -1)
                result = []
                for doc in cursor_mongo:
                    lat_o = float(doc.get("latitud_origen")) if doc.get("latitud_origen") is not None else None
                    lon_o = float(doc.get("longitud_origen")) if doc.get("longitud_origen") is not None else None
                    lat_d = float(doc.get("latitud_destino")) if doc.get("latitud_destino") is not None else None
                    lon_d = float(doc.get("longitud_destino")) if doc.get("longitud_destino") is not None else None

                    result.append({
                        "id": str(doc.get("id")),
                        "fecha_compra": format_datetime(doc.get("fecha_compra")),
                        "subtotal": float(doc.get("subtotal")) if doc.get("subtotal") is not None else 0.0,
                        "iva": float(doc.get("iva")) if doc.get("iva") is not None else 0.0,
                        "total": float(doc.get("total")) if doc.get("total") is not None else 0.0,
                        "estado": doc.get("estado") if doc.get("estado") is not None else "PENDIENTE",
                        "clave_acceso": doc.get("clave_acceso"),
                        "direccion_origen": doc.get("direccion_origen"),
                        "direccion_destino": doc.get("direccion_destino"),
                        "latitud_origen": lat_o,
                        "longitud_origen": lon_o,
                        "latitud_destino": lat_d,
                        "longitud_destino": lon_d,
                        "metodo_entrega": doc.get("metodo_entrega") if doc.get("metodo_entrega") is not None else "ENTREGA"
                    })
                return result
            except Exception as mongo_err:
                raise Exception(f"Fallo en base de datos principal, réplica y MongoDB: {mongo_err}")



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
