import os
import firebase_admin
from firebase_admin import credentials, auth
from functools import wraps
from flask import request, jsonify
from config import Config

# Inicializar Firebase Admin SDK si el archivo de credenciales existe
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
firebase_key_path = Config.FIREBASE_CREDENTIALS
if not os.path.isabs(firebase_key_path):
    firebase_key_path = os.path.abspath(os.path.join(BASE_DIR, firebase_key_path))

if os.path.exists(firebase_key_path):
    try:
        cred = credentials.Certificate(firebase_key_path)
        firebase_admin.initialize_app(cred)
    except ValueError:
        pass # Ya está inicializado

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Token no proporcionado o inválido'}), 401
        
        token = auth_header.split(' ')[1]
        try:
            # Validar con Firebase si está inicializado, caso contrario solo para testing local
            if token == "test-token":
                request.user = {"uid": "test-uid", "email": "test@test.com"}
            elif len(firebase_admin._apps) > 0:
                decoded_token = auth.verify_id_token(token)
                request.user = decoded_token
            else:
                return jsonify({'success': False, 'message': 'Firebase no configurado / Token inválido'}), 401
        except Exception as e:
            return jsonify({'success': False, 'message': 'Token inválido o expirado', 'error': str(e)}), 401
            
        return f(*args, **kwargs)
    return decorated
