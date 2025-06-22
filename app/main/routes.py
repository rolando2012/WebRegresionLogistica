from flask import Blueprint, redirect, render_template, jsonify, request, url_for
import json
import os
from flask import current_app
from app.services.prediccion_service import PrediccionService
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
from flask import send_file

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
    
@main.route('/api/coeficientes')
def api_coeficientes():
    """Endpoint para obtener los coeficientes del modelo"""
    try:
        if prediccion_service.modelo is None:
            return jsonify({'error': 'Modelo no cargado'}), 500
        
        # Accede al paso de regresión logística
        logreg = prediccion_service.modelo.named_steps["regresion_logistica"]
        
        # Coeficientes e intercepto
        intercepto = logreg.intercept_[0]
        coeficientes = logreg.coef_.ravel()
        
        # Nombres de las variables
        columnas_caracteristicas = [
            "edad",
            "tasa_interes", 
            "porcentaje_pago",
            "dias_de_mora",
            "plazo_credito_meses",
            "num_microseguros",
            "n_productos_vigentes",
            "n_creditos_vigentes",
            "calidad_servicio",
            "estado_ahorro_activo"
        ]
        
        # Crear lista de coeficientes
        coeficientes_data = []
        for i, variable in enumerate(columnas_caracteristicas):
            coeficientes_data.append({
                'variable': variable,
                'coeficiente_beta': float(coeficientes[i])
            })
        
        # Ordenar por valor absoluto del coeficiente (mayor impacto primero)
        coeficientes_data.sort(key=lambda x: abs(x['coeficiente_beta']), reverse=True)
        
        return jsonify({
            'intercepto': float(intercepto),
            'coeficientes': coeficientes_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@main.route('/plot/boxplots.png')
def boxplots_png():
    """Endpoint para generar boxplots de variables continuas"""
    try:
        json_path = os.path.join(current_app.root_path, 'data', 'results_microfinanzas.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            res = json.load(f)
        
        cont = res['cont_grouped']
        num_vars = list(cont.keys())
        
        # Reconstruimos un DataFrame para seaborn
        rows = []
        for var in num_vars:
            for cls, vals in cont[var].items():
                for v in vals:
                    rows.append({'variable': var, 'desercion': cls, 'valor': v})
        df = pd.DataFrame(rows)
        
        fig, axes = plt.subplots(5, 2, figsize=(15, 12))
        axes = axes.flatten()
        
        for ax, var in zip(axes, num_vars):
            sns.boxplot(x='desercion', y='valor',
                       data=df[df['variable']==var],
                       dodge=False, ax=ax)
            ax.set_title(f"{var} por deserción")
            ax.set_xlabel("Deserción")
            ax.set_ylabel(var)
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100)
        plt.close(fig)
        buf.seek(0)
        
        return send_file(buf, mimetype='image/png')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/plot/corr.png')
def corr_png():
    """Endpoint para generar heatmap de correlaciones"""
    try:
        json_path = os.path.join(current_app.root_path, 'data', 'results_microfinanzas.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            res = json.load(f)
        
        corr = pd.DataFrame(res['corr_matrix'])
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr, annot=True, cmap="coolwarm", center=0, ax=ax)
        ax.set_title("Mapa de calor de correlaciones")
        plt.tight_layout()
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100)
        plt.close(fig)
        buf.seek(0)
        
        return send_file(buf, mimetype='image/png')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@main.route('/api/procesar-lote', methods=['POST'])
def procesar_lote():
    """API para procesar lote de datos CSV"""
    try:
        # Obtener datos del request
        data = request.get_json()
        
        if not data or 'csv_data' not in data:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron datos CSV'
            }), 400
        
        # Importar el servicio
        from app.services.prediccion_masiva_service import PrediccionMasivaService
        
        # Procesar datos
        service = PrediccionMasivaService()
        resultado = service.procesar_csv_data(data['csv_data'])
        
        if not resultado['success']:
            return jsonify(resultado), 400
        
        # Guardar resultados en sesión para la página de resultados
        from flask import session
        session['resultados_prediccion'] = resultado
        
        
        return jsonify({
            'success': True,
            'message': f'Se procesaron {resultado["total_procesados"]} registros exitosamente',
            'redirect_url': url_for('main.resultados_masivos') 
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error procesando datos: {str(e)}'
        }), 500

@main.route('/resultados-masivos')
def resultados_masivos():
    """Página para mostrar resultados del análisis masivo"""
    from flask import session
    
    resultados = session.get('resultados_prediccion')
    if not resultados:
        return redirect(url_for('main.analisis_masivo'))
    
    return render_template('main/resultados_masivos.html', 
                         titulo="Resultados del Análisis", 
                         resultados=resultados)