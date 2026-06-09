from database import get_db_connection, get_mongodb_db, format_datetime, execute_pg_query

class CompraModel:
    @staticmethod
    def obtener_todas():
        # Para el panel administrativo (React)
        try:
            compras = execute_pg_query("""
                SELECT c.id, c.usuario_id, to_char(c.fecha_compra, 'YYYY-MM-DD"T"HH24:MI:SS"Z"') as fecha_compra, c.subtotal, c.iva, c.total, c.estado, c.clave_acceso, 
                       c.direccion_origen, c.direccion_destino, c.latitud_origen, c.longitud_origen, c.latitud_destino, c.longitud_destino, c.metodo_entrega,
                       u.email as usuario_email, u.nombres as usuario_nombres
                FROM compras c
                JOIN usuarios u ON c.usuario_id = u.id
                WHERE c.eliminado = FALSE
                ORDER BY c.fecha_compra DESC
            """, fetch_all=True)

            if compras:
                compra_ids = [c['id'] for c in compras]
                detalles = execute_pg_query("""
                    SELECT dc.compra_id, dc.producto_id, dc.cantidad, dc.precio_unitario, dc.subtotal, p.nombre as producto_nombre
                    FROM detalle_compra dc
                    JOIN productos p ON dc.producto_id = p.id
                    WHERE dc.compra_id = ANY(%s)
                """, (compra_ids,), fetch_all=True)

                from collections import defaultdict
                detalles_por_compra = defaultdict(list)
                for d in detalles:
                    detalles_por_compra[str(d['compra_id'])].append({
                        "producto_id": str(d['producto_id']),
                        "producto_nombre": d['producto_nombre'],
                        "cantidad": d['cantidad'],
                        "precio_unitario": float(d['precio_unitario']),
                        "subtotal": float(d['subtotal'])
                    })

                for c in compras:
                    c['detalles'] = detalles_por_compra[str(c['id'])]

            return compras
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

                    # MongoDB might have details embedded or not, let's load them if present
                    detalles_raw = doc.get("detalles") or doc.get("details") or []
                    detalles_list = []
                    for item in detalles_raw:
                        detalles_list.append({
                            "producto_id": str(item.get("producto_id")),
                            "producto_nombre": item.get("producto_nombre") or item.get("nombre") or "",
                            "cantidad": item.get("cantidad") or 0,
                            "precio_unitario": float(item.get("precio_unitario") or 0.0),
                            "subtotal": float(item.get("subtotal") or 0.0)
                        })

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
                        "usuario_nombres": user_doc.get("nombres") if user_doc else None,
                        "detalles": detalles_list
                    })
                return result
            except Exception as mongo_err:
                raise Exception(f"Fallo en base de datos principal, réplica y MongoDB: {mongo_err}")

    @staticmethod
    def obtener_por_usuario(usuario_id):
        # Para la App Móvil (Flutter)
        try:
            compras = execute_pg_query("""
                SELECT c.id, c.usuario_id, to_char(c.fecha_compra, 'YYYY-MM-DD"T"HH24:MI:SS"Z"') as fecha_compra, c.subtotal, c.iva, c.total, c.estado, c.clave_acceso, 
                       c.direccion_origen, c.direccion_destino, c.latitud_origen, c.longitud_origen, c.latitud_destino, c.longitud_destino, c.metodo_entrega,
                       u.email as usuario_email, u.nombres as usuario_nombres
                FROM compras c
                JOIN usuarios u ON c.usuario_id = u.id
                WHERE c.usuario_id = %s AND c.eliminado = FALSE
                ORDER BY c.fecha_compra DESC
            """, (usuario_id,), fetch_all=True)

            if compras:
                compra_ids = [c['id'] for c in compras]
                detalles = execute_pg_query("""
                    SELECT dc.compra_id, dc.producto_id, dc.cantidad, dc.precio_unitario, dc.subtotal, p.nombre as producto_nombre
                    FROM detalle_compra dc
                    JOIN productos p ON dc.producto_id = p.id
                    WHERE dc.compra_id = ANY(%s)
                """, (compra_ids,), fetch_all=True)

                from collections import defaultdict
                detalles_por_compra = defaultdict(list)
                for d in detalles:
                    detalles_por_compra[str(d['compra_id'])].append({
                        "producto_id": str(d['producto_id']),
                        "producto_nombre": d['producto_nombre'],
                        "cantidad": d['cantidad'],
                        "precio_unitario": float(d['precio_unitario']),
                        "subtotal": float(d['subtotal'])
                    })

                for c in compras:
                    c['detalles'] = detalles_por_compra[str(c['id'])]

            return compras
        except Exception as e:
            print(f"Advertencia: Fallaron bases de datos relacionales para obtener_por_usuario ({e}). Intentando fallback en MongoDB...")
            db = get_mongodb_db()
            if not db:
                raise Exception("Bases de datos PostgreSQL caídas y MongoDB no disponible")
            try:
                compras_col = db["compras"]
                usuarios_col = db["usuarios"]
                
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
                
                user_doc = usuarios_col.find_one({"$or": [{"id": u_str}, {"id": u_uuid}] if u_uuid else [{"id": u_str}]})
                user_email = user_doc.get("email") if user_doc else None
                user_nombres = user_doc.get("nombres") if user_doc else None

                result = []
                for doc in cursor_mongo:
                    lat_o = float(doc.get("latitud_origen")) if doc.get("latitud_origen") is not None else None
                    lon_o = float(doc.get("longitud_origen")) if doc.get("longitud_origen") is not None else None
                    lat_d = float(doc.get("latitud_destino")) if doc.get("latitud_destino") is not None else None
                    lon_d = float(doc.get("longitud_destino")) if doc.get("longitud_destino") is not None else None

                    detalles_raw = doc.get("detalles") or doc.get("details") or []
                    detalles_list = []
                    for item in detalles_raw:
                        detalles_list.append({
                            "producto_id": str(item.get("producto_id")),
                            "producto_nombre": item.get("producto_nombre") or item.get("nombre") or "",
                            "cantidad": item.get("cantidad") or 0,
                            "precio_unitario": float(item.get("precio_unitario") or 0.0),
                            "subtotal": float(item.get("subtotal") or 0.0)
                        })

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
                        "metodo_entrega": doc.get("metodo_entrega") if doc.get("metodo_entrega") is not None else "ENTREGA",
                        "usuario_email": user_email,
                        "usuario_nombres": user_nombres,
                        "detalles": detalles_list
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


                # 1. Agrupar cantidades de productos duplicados en la misma solicitud
                from collections import defaultdict
                detalles_agrupados = defaultdict(lambda: {'cantidad': 0, 'precio_unitario': 0.0})
                for d in detalles:
                    p_id = str(d['producto_id'])
                    detalles_agrupados[p_id]['cantidad'] += d['cantidad']
                    detalles_agrupados[p_id]['precio_unitario'] = float(d['precio_unitario'])

                # 2. Ordenar detalles por ID de producto (Previene Deadlocks por bloqueo cruzado)
                detalles_ordenados = sorted(detalles_agrupados.items(), key=lambda x: x[0])

                for prod_id, info in detalles_ordenados:
                    cursor.execute("""
                        SELECT stock, nombre, activo, eliminado 
                        FROM productos 
                        WHERE id = %s 
                        FOR UPDATE;
                    """, (prod_id,))
                    producto = cursor.fetchone()
                    
                    if not producto:
                        raise Exception("Producto no encontrado o no existe")
                    if producto['eliminado'] or not producto['activo']:
                        raise Exception(f"El producto '{producto['nombre']}' ya no está disponible")
                    if producto['stock'] < info['cantidad']:
                        raise Exception(f"Stock insuficiente para '{producto['nombre']}'. Disponible: {producto['stock']}, Solicitado: {info['cantidad']}")

                    cursor.execute("""
                        UPDATE productos 
                        SET stock = stock - %s, updated_at = NOW() 
                        WHERE id = %s;
                    """, (info['cantidad'], prod_id))

                    subtotal_detalle = info['cantidad'] * info['precio_unitario']
                    cursor.execute("""
                        INSERT INTO detalle_compra (compra_id, producto_id, cantidad, precio_unitario, subtotal)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (compra_id, prod_id, info['cantidad'], info['precio_unitario'], subtotal_detalle))
                
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
