"""
API REST con Flask para Sistema de Predicción de Precios
Para usar con cualquier frontend (React, Vue, Angular, etc.)
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from api_predictor import PredictorPreciosAPI
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde cualquier frontend

# Inicializar API
predictor = PredictorPreciosAPI()


# ============================================================
# ENDPOINTS DE LA API
# ============================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verifica que el servicio está funcionando"""
    return jsonify({
        "status": "ok",
        "service": "Predictor de Precios API",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/productos', methods=['GET'])
def obtener_productos():
    """
    GET /api/productos
    
    Retorna lista completa de productos disponibles
    
    Response:
    {
        "success": true,
        "total": 87,
        "productos": ["Arroz", "Frijol", ...]
    }
    """
    try:
        productos = predictor.obtener_productos_disponibles()
        return jsonify({
            "success": True,
            "total": len(productos),
            "productos": productos
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/productos/buscar', methods=['GET'])
def buscar_producto():
    """
    GET /api/productos/buscar?q=leche
    
    Busca productos por nombre (exacto o similar)
    
    Query params:
    - q: nombre del producto a buscar
    
    Response:
    {
        "success": true,
        "encontrado": false,
        "producto_exacto": null,
        "sugerencias": ["Leche Pasteurizada Y Fresca", ...]
    }
    """
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({
            "success": False,
            "error": "Parámetro 'q' requerido"
        }), 400
    
    try:
        resultado = predictor.buscar_producto(query)
        return jsonify({
            "success": True,
            **resultado
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/predicciones', methods=['POST'])
def generar_predicciones():
    """
    POST /api/predicciones
    
    Genera predicciones para una lista de productos
    
    Request Body:
    {
        "productos": ["Tortilla de maíz", "Arroz", "Huevo"],
        "fecha_inicio": "2026-01-01",
        "fecha_fin": "2026-01-31",
        "generar_graficas": true
    }
    
    Response:
    {
        "success": true,
        "fecha_consulta": "2025-11-25 10:30:00",
        "periodo": {
            "inicio": "2026-01-01",
            "fin": "2026-01-31"
        },
        "total_productos": 3,
        "productos": [...]
    }
    """
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        if not data:
            return jsonify({
                "success": False,
                "error": "Body JSON requerido"
            }), 400
        
        productos = data.get('productos', [])
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        generar_graficas = data.get('generar_graficas', True)
        
        if not productos:
            return jsonify({
                "success": False,
                "error": "Lista de productos requerida"
            }), 400
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({
                "success": False,
                "error": "Fechas de inicio y fin requeridas"
            }), 400
        
        # Validar formato de fechas
        try:
            datetime.strptime(fecha_inicio, '%Y-%m-%d')
            datetime.strptime(fecha_fin, '%Y-%m-%d')
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Formato de fecha inválido. Use YYYY-MM-DD"
            }), 400
        
        # Generar predicciones
        resultado = predictor.generar_predicciones(
            productos=productos,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            generar_graficas=generar_graficas
        )
        
        return jsonify({
            "success": True,
            **resultado
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/graficas/<path:filename>', methods=['GET'])
def obtener_grafica(filename):
    """
    GET /api/graficas/tortilla_de_maiz_2026-01-01_a_2026-01-31.png
    
    Retorna la imagen de una gráfica generada
    """
    try:
        ruta = os.path.join('graficas', filename)
        if not os.path.exists(ruta):
            return jsonify({
                "success": False,
                "error": "Gráfica no encontrada"
            }), 404
        
        return send_file(ruta, mimetype='image/png')
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/predicciones/<path:filename>', methods=['GET'])
def obtener_json_prediccion(filename):
    """
    GET /api/predicciones/predicciones_2026-01-01_a_2026-01-31.json
    
    Retorna el archivo JSON de una predicción generada
    """
    try:
        ruta = os.path.join('predicciones', filename)
        if not os.path.exists(ruta):
            return jsonify({
                "success": False,
                "error": "Predicción no encontrada"
            }), 404
        
        return send_file(ruta, mimetype='application/json')
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================
# MANEJO DE ERRORES
# ============================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint no encontrado"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Error interno del servidor"
    }), 500


# ============================================================
# INICIAR SERVIDOR
# ============================================================

if __name__ == '__main__':
    print("="*60)
    print("🚀 Iniciando API de Predicción de Precios")
    print("="*60)
    print("\nEndpoints disponibles:")
    print("  GET  /api/health")
    print("  GET  /api/productos")
    print("  GET  /api/productos/buscar?q=<nombre>")
    print("  POST /api/predicciones")
    print("  GET  /api/graficas/<filename>")
    print("  GET  /api/predicciones/<filename>")
    print("\n" + "="*60)
    
    # Obtener puerto de variable de entorno o usar 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    
    # Modo desarrollo local
    app.run(host='0.0.0.0', port=port, debug=True)
