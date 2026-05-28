import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from routes.usuarios_routes import usuarios_bp
from routes.productos_routes import productos_bp
from routes.compras_routes import compras_bp

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# =========================
# RUTAS (BLUEPRINTS)
# =========================
app.register_blueprint(usuarios_bp, url_prefix='/api/usuarios')
app.register_blueprint(productos_bp, url_prefix='/api/productos')
app.register_blueprint(compras_bp, url_prefix='/api/compras')

# =========================
# RUTA RAIZ
# =========================
@app.route("/")
def home():
    return jsonify({
        "success": True,
        "message": "API REST TechStore 360 funcionando correctamente",
        "endpoints_disponibles": [
            "/api/usuarios",
            "/api/productos",
            "/api/compras"
        ]
    })

# =========================
# MANEJO DE ERRORES
# =========================
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Recurso no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
