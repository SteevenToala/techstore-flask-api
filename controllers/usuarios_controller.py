from flask import jsonify, request
from models.usuario_model import UsuarioModel

def obtener_usuarios():
    try:
        usuarios = UsuarioModel.obtener_todos()
        return jsonify({"success": True, "data": usuarios}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Error al consultar usuarios", "error": str(e)}), 500

def crear_usuario():
    data = request.get_json()
    firebase_uid = data.get('firebase_uid')
    nombres = data.get('nombres')
    apellidos = data.get('apellidos')
    email = data.get('email')
    rol = data.get('rol', 'CLIENTE')
    telefono = data.get('telefono', '')

    if not all([firebase_uid, nombres, apellidos, email]):
        return jsonify({"success": False, "message": "Faltan datos obligatorios"}), 400

    try:
        nuevo_usuario = UsuarioModel.crear(firebase_uid, nombres, apellidos, email, rol, telefono)
        return jsonify({"success": True, "message": "Usuario creado", "data": nuevo_usuario}), 201
    except Exception as e:
        return jsonify({"success": False, "message": "Error al crear usuario", "error": str(e)}), 500

def actualizar_usuario(id):
    data = request.get_json()
    nombres = data.get('nombres')
    apellidos = data.get('apellidos')
    rol = data.get('rol')
    telefono = data.get('telefono')
    estado = data.get('estado')

    try:
        actualizado = UsuarioModel.actualizar(id, nombres, apellidos, rol, telefono, estado)
        if actualizado:
            return jsonify({"success": True, "message": "Usuario actualizado exitosamente"}), 200
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": "Error al actualizar usuario", "error": str(e)}), 500

def eliminar_usuario(id):
    try:
        eliminado = UsuarioModel.eliminar(id)
        if eliminado:
            return jsonify({"success": True, "message": "Usuario eliminado exitosamente"}), 200
        return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": "Error al eliminar usuario", "error": str(e)}), 500
