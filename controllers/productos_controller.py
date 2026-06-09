from flask import jsonify, request
from models.producto_model import ProductoModel

def obtener_productos(admin=False):
    try:
        if admin:
            productos = ProductoModel.obtener_todos()
        else:
            productos = ProductoModel.obtener_activos()
        return jsonify({"success": True, "data": productos}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Error al consultar productos", "error": str(e)}), 500

def crear_producto():
    data = request.get_json()
    nombre = data.get('nombre')
    descripcion = data.get('descripcion', '')
    precio = data.get('precio')
    stock = data.get('stock', 0)
    imagen_url = data.get('imagen_url', '')

    if not nombre or precio is None:
        return jsonify({"success": False, "message": "Faltan datos obligatorios (nombre, precio)"}), 400

    try:
        nuevo_producto = ProductoModel.crear(nombre, descripcion, precio, stock, imagen_url)
        return jsonify({"success": True, "message": "Producto creado", "data": nuevo_producto}), 201
    except Exception as e:
        return jsonify({"success": False, "message": "Error al crear producto", "error": str(e)}), 500

def actualizar_producto(id):
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No se proporcionaron datos para actualizar"}), 400

    campos_a_actualizar = {}
    for campo in ['nombre', 'descripcion', 'precio', 'stock', 'imagen_url', 'activo']:
        if campo in data:
            campos_a_actualizar[campo] = data[campo]

    if not campos_a_actualizar:
        return jsonify({"success": False, "message": "No se proporcionaron campos válidos para actualizar"}), 400

    try:
        actualizado = ProductoModel.actualizar(id, campos_a_actualizar)
        if actualizado:
            return jsonify({"success": True, "message": "Producto actualizado exitosamente"}), 200
        return jsonify({"success": False, "message": "Producto no encontrado"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": "Error al actualizar producto", "error": str(e)}), 500

def eliminar_producto(id):
    try:
        eliminado = ProductoModel.eliminar(id)
        if eliminado:
            return jsonify({"success": True, "message": "Producto eliminado exitosamente"}), 200
        return jsonify({"success": False, "message": "Producto no encontrado o en uso"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": "Error al eliminar producto", "error": str(e)}), 500
