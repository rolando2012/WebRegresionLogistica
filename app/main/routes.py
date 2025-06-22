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
    """Exportar resultados a PDF"""
    try:
        from flask import session
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics.charts.piecharts import Pie
        from reportlab.graphics.charts.linecharts import HorizontalLineChart
        from reportlab.lib.colors import HexColor
        import io
        import base64
        from datetime import datetime
        
        # Obtener resultados de la sesión
        resultados = session.get('resultados_prediccion')
        if not resultados:
            return redirect(url_for('main.analisis_masivo'))
        
        # Crear buffer para el PDF
        buffer = io.BytesIO()
        
        # Crear documento PDF
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
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
        story.append(Spacer(1, 20))
        
        # Gráfico de distribución (simulado con tabla)
        story.append(Paragraph("DISTRIBUCIÓN POR RIESGO", subtitle_style))
        
        pie_data = [
            ['Estado del Cliente', 'Cantidad', 'Representación Visual'],
            ['Clientes Fieles', str(resultados['datos_torta']['fieles']['cantidad']), 
             '█' * int(resultados['datos_torta']['fieles']['porcentaje'] / 5) + f" ({resultados['datos_torta']['fieles']['porcentaje']}%)"],
            ['Posibles Desertores', str(resultados['datos_torta']['desertores']['cantidad']), 
             '█' * int(resultados['datos_torta']['desertores']['porcentaje'] / 5) + f" ({resultados['datos_torta']['desertores']['porcentaje']}%)"]
        ]
        
        pie_table = Table(pie_data, colWidths=[2*inch, 1*inch, 3*inch])
        pie_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (0, 1), colors.lightgreen),
            ('BACKGROUND', (0, 2), (0, 2), colors.lightcoral),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        story.append(pie_table)
        story.append(Spacer(1, 20))
        
        # Tabla de resultados detallados
        story.append(Paragraph("RESULTADOS DETALLADOS", subtitle_style))
        
        # Preparar datos para la tabla (primeros 20 registros)
        table_data = [['ID', 'Calidad Servicio', 'Tasa Interés', 'Edad', 'Probabilidad', 'Riesgo']]
        
        for i, cliente in enumerate(resultados['datos_detallados'][:20]):  # Mostrar solo primeros 20
            table_data.append([
                cliente['id'],
                str(cliente['calidad_servicio']),
                f"{cliente['tasa_interes']:.1f}%",
                str(cliente['edad']),
                f"{cliente['probabilidad']*100:.1f}%",
                cliente['riesgo']
            ])
        
        # Si hay más de 20 registros, agregar nota
        if len(resultados['datos_detallados']) >20:
            table_data.append(['...', '...', '...', '...', '...', '...'])
            table_data.append([f"Total: {len(resultados['datos_detallados'])} registros", '', '', '', '', ''])
        
        detail_table = Table(table_data, colWidths=[0.8*inch, 1.2*inch, 1*inch, 0.8*inch, 1*inch, 0.8*inch])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        # Colorear filas según el riesgo
        for i, cliente in enumerate(resultados['datos_detallados'][:20], 1):
            if cliente['riesgo'] == 'ALTO':
                detail_table.setStyle(TableStyle([
                    ('BACKGROUND', (5, i), (5, i), colors.lightcoral),
                ]))
            else:
                detail_table.setStyle(TableStyle([
                    ('BACKGROUND', (5, i), (5, i), colors.lightgreen),
                ]))
        
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
        
        from flask import make_response
        response = make_response(buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=reporte_prediccion_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        
        buffer.close()
        
        return response
        
    except Exception as e:
        from flask import flash
        flash(f'Error al generar PDF: {str(e)}', 'error')
        return redirect(url_for('main.resultados_masivos'))