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
    cedula = data.get('cedula')
    if not cedula:
        cedula = None

    if not all([firebase_uid, nombres, apellidos, email]):
        return jsonify({"success": False, "message": "Faltan datos obligatorios"}), 400

    try:
        nuevo_usuario = UsuarioModel.crear(firebase_uid, nombres, apellidos, email, rol, telefono, cedula)
        return jsonify({"success": True, "message": "Usuario creado", "data": nuevo_usuario}), 201
    except Exception as e:
        return jsonify({"success": False, "message": "Error al crear usuario", "error": str(e)}), 500

def actualizar_usuario(id):
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No se proporcionaron datos para actualizar"}), 400

    campos_a_actualizar = {}
    for campo in ['nombres', 'apellidos', 'rol', 'telefono', 'cedula', 'estado']:
        if campo in data:
            val = data[campo]
            if campo == 'cedula' and not val:
                val = None
            campos_a_actualizar[campo] = val

    if not campos_a_actualizar:
        return jsonify({"success": False, "message": "No se proporcionaron campos válidos para actualizar"}), 400

    try:
        actualizado = UsuarioModel.actualizar(id, campos_a_actualizar)
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

def obtener_mi_perfil():
    firebase_uid = request.user.get('uid')
    try:
        usuario = UsuarioModel.obtener_por_firebase_uid(firebase_uid)
        if not usuario:
            return jsonify({"success": False, "message": "Usuario no registrado en la BD local"}), 404
        if usuario.get('eliminado', False):
            return jsonify({"success": False, "message": "Esta cuenta ha sido eliminada"}), 403
        if not usuario.get('estado', True):
            return jsonify({"success": False, "message": "Usuario inactivo o suspendido"}), 403
        return jsonify({"success": True, "data": usuario}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Error al obtener perfil", "error": str(e)}), 500
