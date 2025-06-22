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

@main.route('/exportar-pdf')
def exportar_pdf():
    """Exportar resultados a PDF con gráficos"""
    try:
        from flask import session
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics.charts.piecharts import Pie
        from reportlab.graphics.charts.linecharts import HorizontalLineChart
        from reportlab.graphics.charts.lineplots import LinePlot
        from reportlab.graphics.widgets.markers import makeMarker
        from reportlab.lib.colors import HexColor
        import io
        import base64
        from datetime import datetime
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')  # Para evitar problemas con GUI
        import numpy as np
        
        # Obtener resultados de la sesión
        resultados = session.get('resultados_prediccion')
        if not resultados:
            return jsonify({'success': False, 'error': 'No hay datos para exportar'}), 400
        
        # Crear buffer para el PDF
        buffer = io.BytesIO()
        
        # Crear documento PDF
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                              rightMargin=50, leftMargin=50,
                              topMargin=50, bottomMargin=50)
        
        # Contenido del PDF
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Centrado
            textColor=colors.darkblue
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.darkgreen
        )
        
        # Título principal
        story.append(Paragraph("REPORTE DE ANÁLISIS MASIVO", title_style))
        story.append(Paragraph("Predicción de Deserción de Clientes Bancarios", styles['Heading3']))
        story.append(Spacer(1, 12))
        
        # Información del reporte
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        story.append(Paragraph(f"<b>Fecha de generación:</b> {fecha_actual}", styles['Normal']))
        story.append(Paragraph(f"<b>Total de clientes analizados:</b> {resultados['estadisticas']['total_clientes']}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Resumen ejecutivo
        story.append(Paragraph("RESUMEN EJECUTIVO", subtitle_style))
        
        # Tabla de estadísticas principales
        stats_data = [
            ['Métrica', 'Cantidad', 'Porcentaje'],
            ['Total de Clientes', str(resultados['estadisticas']['total_clientes']), '100%'],
            ['Clientes Fieles', str(resultados['estadisticas']['clientes_fieles']), 
             f"{resultados['estadisticas']['pct_fieles']}%"],
            ['Posibles Desertores', str(resultados['estadisticas']['posibles_desertores']), 
             f"{resultados['estadisticas']['pct_desertores']}%"],
            ['Clientes de Riesgo Alto', str(resultados['estadisticas']['riesgo_alto']), 
             f"{round(resultados['estadisticas']['riesgo_alto'] / resultados['estadisticas']['total_clientes'] * 100, 1)}%"]
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 30))
        
        # === GRÁFICO DE TORTA ===
        story.append(Paragraph("DISTRIBUCIÓN POR RIESGO", subtitle_style))
        
        # Crear gráfico de torta con matplotlib
        fig, ax = plt.subplots(figsize=(6, 6))
        labels = ['Clientes Fieles', 'Posibles Desertores']
        sizes = [resultados['datos_torta']['fieles']['cantidad'], 
                resultados['datos_torta']['desertores']['cantidad']]
        colors_pie = ['#10B981', '#EF4444']
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%',
                                         startangle=90, textprops={'fontsize': 10})
        ax.set_title('Distribución de Clientes por Riesgo de Deserción', fontsize=12, fontweight='bold')
        
        # Guardar gráfico como imagen
        pie_buffer = io.BytesIO()
        plt.savefig(pie_buffer, format='png', dpi=300, bbox_inches='tight')
        pie_buffer.seek(0)
        
        # Agregar imagen al PDF
        pie_image = Image(pie_buffer, width=4*inch, height=4*inch)
        story.append(pie_image)
        plt.close()
        story.append(Spacer(1, 20))
        
        # === GRÁFICO SIGMOIDE ===
        story.append(Paragraph("RELACIÓN ENTRE Z-SCORE   VS PROBABILIDAD DE DESERCIÓN", subtitle_style))
        
        # Crear gráfico sigmoide
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Extraer datos
        z_scores = [item['z_score'] for item in resultados['datos_sigmoide']]
        sigmoides = [item['sigmoide'] for item in resultados['datos_sigmoide']]
        predicciones = [item['prediccion'] for item in resultados['datos_sigmoide']]
        
        # Separar por predicción
        z_fieles = [z for z, p in zip(z_scores, predicciones) if p == 0]
        s_fieles = [s for s, p in zip(sigmoides, predicciones) if p == 0]
        z_desertores = [z for z, p in zip(z_scores, predicciones) if p == 1]
        s_desertores = [s for s, p in zip(sigmoides, predicciones) if p == 1]
        
        # Plotear puntos
        ax.scatter(z_fieles, s_fieles, c='#10B981', alpha=0.6, label='Clientes Fieles', s=30)
        ax.scatter(z_desertores, s_desertores, c='#EF4444', alpha=0.6, label='Posibles Desertores', s=30)
        
        # Crear línea sigmoide suave
        z_range = np.linspace(min(z_scores), max(z_scores), 100)
        sigmoid_line = 1 / (1 + np.exp(-z_range))
        ax.plot(z_range, sigmoid_line, 'k--', alpha=0.5, linewidth=2, label='Función Sigmoide')
        
        ax.set_xlabel('Z-Score', fontsize=10)
        ax.set_ylabel('Probabilidad (Sigmoide)', fontsize=10)
        ax.set_title('Relación entre Z-Score y Probabilidad de Deserción', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Guardar gráfico
        sigmoid_buffer = io.BytesIO()
        plt.savefig(sigmoid_buffer, format='png', dpi=300, bbox_inches='tight')
        sigmoid_buffer.seek(0)
        
        # Agregar imagen al PDF
        sigmoid_image = Image(sigmoid_buffer, width=6*inch, height=4.5*inch)
        story.append(sigmoid_image)
        plt.close()
        story.append(PageBreak())
        
        # === TABLA COMPLETA DE RESULTADOS ===
        story.append(Paragraph("RESULTADOS DETALLADOS COMPLETOS", subtitle_style))
        story.append(Paragraph(f"Tabla completa con {len(resultados['datos_detallados'])} registros", styles['Normal']))
        story.append(Spacer(1, 10))
        
        # Preparar datos para la tabla (TODOS los registros)
        table_data = [['ID', 'Cal. Serv.', 'Tasa Int.', 'Est. Ahorro', 'Prod. Vig.', 'Edad', 'Probabilidad', 'Riesgo']]
        
        # Ordenar los datos por Riesgo (ALTO primero)
        resultados['datos_detallados'].sort(key=lambda x: x['riesgo'] == 'ALTO', reverse=True)

        for cliente in resultados['datos_detallados']:  # TODOS los registros
            table_data.append([
                cliente['id'],
                str(cliente['calidad_servicio']),
                f"{cliente['tasa_interes']:.1f}%",
                'Activo' if cliente['estado_ahorro_activo'] == 1 else 'Inactivo',  # NUEVA LÍNEA
                str(cliente['n_productos_vigentes']),  # NUEVA LÍNEA
                str(cliente['edad']),
                f"{cliente['probabilidad']*100:.1f}%",
                cliente['riesgo']
            ])
        
        # Crear tabla con todos los datos
        detail_table = Table(table_data, colWidths=[0.6*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.7*inch, 0.6*inch, 0.9*inch, 0.6*inch])
        
        # Estilo base de la tabla
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]
        
        # Colorear filas según el riesgo
        for i, cliente in enumerate(resultados['datos_detallados'], 1):
            if cliente['riesgo'] == 'ALTO':
                table_style.append(('BACKGROUND', (7, i), (7, i), colors.lightcoral))  # Cambiar de 5 a 7
            else:
                table_style.append(('BACKGROUND', (7, i), (7, i), colors.lightgreen))  # Cambiar de 5 a 7
        
        detail_table.setStyle(TableStyle(table_style))
        story.append(detail_table)
        story.append(Spacer(1, 20))
        
        # Conclusiones y recomendaciones
        story.append(Paragraph("CONCLUSIONES Y RECOMENDACIONES", subtitle_style))
        
        conclusiones = [
            f"• El análisis procesó {resultados['estadisticas']['total_clientes']} clientes con éxito.",
            f"• {resultados['estadisticas']['clientes_fieles']} clientes ({resultados['estadisticas']['pct_fieles']}%) se clasifican como fieles.",
            f"• {resultados['estadisticas']['posibles_desertores']} clientes ({resultados['estadisticas']['pct_desertores']}%) tienen alta probabilidad de deserción.",
            f"• {resultados['estadisticas']['riesgo_alto']} clientes requieren atención inmediata por riesgo muy alto.",
            "• Se recomienda implementar estrategias de retención para clientes de alto riesgo.",
            "• Monitorear continuamente los indicadores de satisfacción del cliente.",
            "• Desarrollar programas de fidelización personalizados."
        ]
        
        for conclusion in conclusiones:
            story.append(Paragraph(conclusion, styles['Normal']))
            story.append(Spacer(1, 6))
        
        # Pie de página
        story.append(Spacer(1, 30))
        story.append(Paragraph("Reporte generado por Sistema de Predicción de Deserción", 
                              ParagraphStyle('Footer', parent=styles['Normal'], 
                                           fontSize=8, alignment=1, textColor=colors.grey)))
        
        # Construir PDF
        doc.build(story)
        
        # Preparar respuesta
        buffer.seek(0)
        pdf_data = buffer.read()
        buffer.close()
        
        from flask import make_response
        response = make_response(pdf_data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=reporte_prediccion_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        
        return response
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error al generar PDF: {str(e)}'}), 500