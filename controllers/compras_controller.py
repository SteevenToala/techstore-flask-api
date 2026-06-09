from flask import jsonify, request
from models.compra_model import CompraModel
from models.usuario_model import UsuarioModel
import os
import requests
from requests.auth import HTTPBasicAuth

def verificar_pago_paypal(order_id):
    """
    Se conecta a la API de PayPal para verificar que la orden especificada
    haya sido pagada y completada correctamente.
    """
    client_id = os.environ.get('PAYPAL_CLIENT_ID')
    secret = os.environ.get('PAYPAL_SECRET')
    environment = os.environ.get('PAYPAL_ENV', 'sandbox')
    
    # URL dependiendo si estamos en desarrollo (sandbox) o producción
    base_url = "https://api-m.sandbox.paypal.com" if environment == 'sandbox' else "https://api-m.paypal.com"
    
    try:
        # 1. Obtener token de acceso de PayPal
        token_url = f"{base_url}/v1/oauth2/token"
        token_response = requests.post(
            token_url,
            auth=HTTPBasicAuth(client_id, secret),
            data={"grant_type": "client_credentials"},
            headers={"Accept": "application/json", "Accept-Language": "en_US"}
        )
        
        if token_response.status_code != 200:
            return False, "Error de autenticación con PayPal (Verifica tus credenciales en el .env)"
            
        access_token = token_response.json()['access_token']
        
        # 2. Capturar el pago (verificar que el usuario pagó)
        capture_url = f"{base_url}/v2/checkout/orders/{order_id}/capture"
        capture_response = requests.post(
            capture_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        )
        
        # 201 significa que fue capturada exitosamente, 200 si ya había sido capturada o info de orden.
        if capture_response.status_code in (200, 201):
            data = capture_response.json()
            if data.get('status') == 'COMPLETED':
                return True, "Pago completado"
                
        return False, "El pago no pudo ser procesado o no fue completado en PayPal."
    except Exception as e:
        return False, f"Error al conectar con PayPal: {str(e)}"

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
    paypal_order_id = data.get('paypal_order_id') # Obtenemos el ID de PayPal desde el frontend
    direccion_origen = data.get('direccion_origen')
    direccion_destino = data.get('direccion_destino')
    latitud_origen = data.get('latitud_origen')
    longitud_origen = data.get('longitud_origen')
    latitud_destino = data.get('latitud_destino')
    longitud_destino = data.get('longitud_destino')
    metodo_entrega = data.get('metodo_entrega', 'ENTREGA') # Por defecto es entrega a domicilio

    if not detalles:
        return jsonify({"success": False, "message": "La compra debe tener detalles"}), 400

    estado_compra = 'PENDIENTE'
    # Si se envía un ID de PayPal, verificamos el pago antes de registrar la compra
    if paypal_order_id:
        pago_exitoso, mensaje_paypal = verificar_pago_paypal(paypal_order_id)
        if not pago_exitoso:
            return jsonify({"success": False, "message": mensaje_paypal}), 400
        estado_compra = 'PAGADA'

    try:
        usuario = UsuarioModel.obtener_por_firebase_uid(usuario_uid)
        if not usuario:
            return jsonify({"success": False, "message": "Usuario no registrado en la BD local"}), 404
        
        usuario_id = usuario['id']
        subtotal = sum(d['cantidad'] * d['precio_unitario'] for d in detalles)
        iva = subtotal * 0.15 # IVA 15%
        total = subtotal + iva

        # Crear compra y detalles localmente en la base de datos
        compra_id = CompraModel.crear_compra_y_detalles(
            usuario_id, subtotal, iva, total, detalles, 
            direccion_origen, direccion_destino,
            latitud_origen, longitud_origen,
            latitud_destino, longitud_destino,
            metodo_entrega, estado_compra
        )

        return jsonify({
            "success": True, 
            "message": "Compra registrada exitosamente", 
            "compra_id": compra_id
        }), 201
            
    except Exception as e:
        return jsonify({"success": False, "message": "Error al registrar compra", "error": str(e)}), 500

def eliminar_compra(id):
    try:
        eliminado = CompraModel.eliminar(id)
        if eliminado:
            return jsonify({"success": True, "message": "Compra eliminada exitosamente"}), 200
        return jsonify({"success": False, "message": "Compra no encontrada"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": "Error al eliminar compra", "error": str(e)}), 500
