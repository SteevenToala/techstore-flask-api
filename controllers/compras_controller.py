from flask import jsonify, request
from zeep import Client
from models.compra_model import CompraModel
from models.usuario_model import UsuarioModel
from config import Config
import xml.etree.ElementTree as ET

def invocar_soap_facturacion(compra_id, total, usuario, detalles):
    # Genera un string XML básico con la información de la factura
    detalles_xml = ""
    for d in detalles:
        detalles_xml += f"""
        <Producto>
            <Id>{d['producto_id']}</Id>
            <Cantidad>{d['cantidad']}</Cantidad>
            <Precio>{d['precio_unitario']}</Precio>
        </Producto>"""

    xml_factura_str = f"""<Factura>
        <IdCompra>{compra_id}</IdCompra>
        <Cliente>
            <Nombre>{usuario['nombres']} {usuario['apellidos']}</Nombre>
            <Email>{usuario['email']}</Email>
        </Cliente>
        <Detalles>{detalles_xml}</Detalles>
        <Total>{total}</Total>
    </Factura>"""

    try:
        # Se conecta al servicio independiente mediante el protocolo SOAP estandarizado y lee su WSDL
        wsdl_url = Config.SOAP_SERVICE_URL + "?wsdl"
        cliente_soap = Client(wsdl=wsdl_url)
        
        # Invoca la operación 'ValidarFactura' nativamente definida en el WSDL
        respuesta = cliente_soap.service.ValidarFactura(xmlFactura=xml_factura_str)
        
        if respuesta.Estado == 'VALIDADA':
            return {"success": True, "clave_acceso": respuesta.ClaveAcceso, "xml": xml_factura_str}
        else:
            return {"success": False, "message": f"SOAP Respondió: {respuesta.Mensaje}"}

    except Exception as e:
        return {"success": False, "message": f"Fallo al invocar SOAP: {str(e)}"}

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

        # Crear compra y detalles localmente
        compra_id = CompraModel.crear_compra_y_detalles(usuario_id, subtotal, iva, total, detalles)

        # Invocar cliente SOAP real (Zeep)
        soap_res = invocar_soap_facturacion(compra_id, total, usuario, detalles)
        
        if soap_res['success']:
            clave_acceso = soap_res.get('clave_acceso')
            factura_xml = soap_res.get('xml')
            CompraModel.actualizar_factura(compra_id, clave_acceso, factura_xml)
            return jsonify({"success": True, "message": "Compra registrada y Facturada (SOAP)", "clave_acceso": clave_acceso, "compra_id": compra_id}), 201
        else:
            return jsonify({"success": True, "message": "Compra registrada, pero error en facturación SOAP", "soap_error": soap_res['message'], "compra_id": compra_id}), 201
            
    except Exception as e:
        return jsonify({"success": False, "message": "Error al registrar compra", "error": str(e)}), 500
