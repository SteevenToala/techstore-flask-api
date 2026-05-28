from flask import jsonify, request
from models.compra_model import CompraModel
from models.usuario_model import UsuarioModel

def obtener_compras(admin=False):
    usuario_uid = request.user.get('uid')
    
    try:
        if admin:
            compras = CompraModel.obtener_todas()
            return jsonify({"success": True, "data": compras}), 200
        else:
            usuario = UsuarioModel.obtener_por_firebase_uid(usuario_uid)
            if not usuario:
                return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

            compras = CompraModel.obtener_por_usuario(usuario['id'])
            return jsonify({"success": True, "data": compras}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Error al consultar compras", "error": str(e)}), 500

def crear_compra():
    usuario_uid = request.user.get('uid')
    data = request.get_json()
    detalles = data.get('detalles', [])

    if not detalles:
        return jsonify({"success": False, "message": "La compra debe tener detalles"}), 400

    try:
        usuario = UsuarioModel.obtener_por_firebase_uid(usuario_uid)
        if not usuario:
            return jsonify({"success": False, "message": "Usuario no registrado en la BD local"}), 404
        
        usuario_id = usuario['id']
        subtotal = sum(d['cantidad'] * d['precio_unitario'] for d in detalles)
        iva = subtotal * 0.15 # IVA 15%
        total = subtotal + iva

        # Crear compra y detalles localmente en la base de datos
        compra_id = CompraModel.crear_compra_y_detalles(usuario_id, subtotal, iva, total, detalles)

        return jsonify({
            "success": True, 
            "message": "Compra registrada exitosamente", 
            "compra_id": compra_id
        }), 201
            
    except Exception as e:
        return jsonify({"success": False, "message": "Error al registrar compra", "error": str(e)}), 500
