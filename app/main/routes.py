from flask import Blueprint, render_template, jsonify, request
import json
import os
from flask import current_app
from app.services.prediccion_service import PrediccionService

main = Blueprint('main', __name__)

# Instancia del servicio de predicción
prediccion_service = PrediccionService()

@main.route('/')
def index():
    """Página principal del menú"""
    return render_template('main/index.html', titulo="Predictor de Deserción")

@main.route('/visualizar-datos')
def visualizar_datos():
    """Página para visualizar datos"""
    return render_template('main/visualizar_datos.html', titulo="Visualizar Datos")

@main.route('/prediccion-individual')
def prediccion_individual():
    """Página para predicción individual"""
    return render_template('main/prediccion_individual.html', titulo="Predicción Individual")

@main.route('/analisis-masivo')
def analisis_masivo():
    """Página para análisis masivo"""
    return render_template('main/analisis_masivo.html', titulo="Análisis Masivo")

@main.route('/api/predecir-desercion', methods=['POST'])
def api_predecir_desercion():
    """
    API endpoint para predecir deserción de un cliente individual
    """
    try:
        # Obtener datos del request
        datos = request.get_json()
        
        if not datos:
            return jsonify({
                'error': 'No se recibieron datos',
                'codigo': 'DATOS_FALTANTES'
            }), 400
        
        # Validar datos
        es_valido, errores = prediccion_service.validar_datos(datos)
        
        if not es_valido:
            return jsonify({
                'error': 'Datos inválidos',
                'errores': errores,
                'codigo': 'DATOS_INVALIDOS'
            }), 400
        
        # Realizar predicción
        resultado = prediccion_service.predecir_desercion(datos)
        
        return jsonify({
            'success': True,
            'probabilidad': resultado['probabilidad'],
            'prediccion': resultado['prediccion'],
            'z_score': resultado['z_score'],
            'mensaje': 'Predicción realizada exitosamente'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error interno del servidor: {str(e)}',
            'codigo': 'ERROR_INTERNO'
        }), 500

@main.route('/api/health', methods=['GET'])
def api_health():
    """
    Endpoint para verificar el estado de la aplicación y el modelo
    """
    try:
        modelo_cargado = prediccion_service.modelo is not None
        
        return jsonify({
            'status': 'ok',
            'modelo_cargado': modelo_cargado,
            'timestamp': json.dumps(None, default=str)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@main.route('/data')
def data():
    """Endpoint para obtener datos del JSON"""
    json_path = os.path.join(current_app.root_path, 'data', 'results_microfinanzas.json')
    if not os.path.isfile(json_path):
        return jsonify({'error': 'JSON not found'}), 404
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500