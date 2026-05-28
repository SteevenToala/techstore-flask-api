from flask import Blueprint
from controllers.usuarios_controller import obtener_usuarios, crear_usuario, actualizar_usuario, eliminar_usuario
from utils.auth import require_auth

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/', methods=['GET'])
@require_auth
def get_usuarios():
    return obtener_usuarios()

@usuarios_bp.route('/', methods=['POST'])
def post_usuario():
    return crear_usuario()

@usuarios_bp.route('/me', methods=['GET'])
@require_auth
def get_mi_perfil():
    from controllers.usuarios_controller import obtener_mi_perfil
    return obtener_mi_perfil()

@usuarios_bp.route('/<string:id>', methods=['PUT'])
@require_auth
def put_usuario(id):
    return actualizar_usuario(id)

@usuarios_bp.route('/<string:id>', methods=['DELETE'])
@require_auth
def delete_usuario(id):
    return eliminar_usuario(id)

