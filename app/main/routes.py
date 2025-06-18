from flask import Blueprint, render_template

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