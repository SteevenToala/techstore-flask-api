from flask import Blueprint, request
from controllers.productos_controller import obtener_productos, crear_producto, actualizar_producto, eliminar_producto
from utils.auth import require_auth

productos_bp = Blueprint('productos', __name__)

@productos_bp.route('/', methods=['GET'])
def get_productos():
    admin = request.args.get('admin', 'false').lower() == 'true'
    return obtener_productos(admin=admin)

@productos_bp.route('/', methods=['POST'])
@require_auth
def post_producto():
    return crear_producto()

@productos_bp.route('/<string:id>', methods=['PUT'])
@require_auth
def put_producto(id):
    return actualizar_producto(id)

@productos_bp.route('/<string:id>', methods=['DELETE'])
@require_auth
def delete_producto(id):
    return eliminar_producto(id)
