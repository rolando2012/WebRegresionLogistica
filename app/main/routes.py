from flask import Blueprint, render_template, jsonify
import json
import os
from flask import current_app

main = Blueprint('main', __name__)

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