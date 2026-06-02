from flask import Blueprint, request
from controllers.compras_controller import obtener_compras, crear_compra, eliminar_compra
from utils.auth import require_auth

compras_bp = Blueprint('compras', __name__)

@compras_bp.route('/', methods=['GET'])
@require_auth
def get_compras():
    admin = request.args.get('admin', 'false').lower() == 'true'
    return obtener_compras(admin=admin)

@compras_bp.route('/', methods=['POST'])
@require_auth
def post_compra():
    return crear_compra()

@compras_bp.route('/<string:id>', methods=['DELETE'])
@require_auth
def delete_compra(id):
    return eliminar_compra(id)
