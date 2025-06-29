pip freeze > requirements.txt
deactivate
# 📊 Predictor de Deserción de Clientes Microfinancieros

Este proyecto es una aplicación web desarrollada con Flask que permite **predecir la probabilidad de deserción de clientes microfinancieros** a través de un modelo de regresión logística. Ofrece interfaces para predicciones individuales, análisis masivos de datos y visualización de resultados.

---

## ✨ Características Principales

* **Página de Inicio**: Un menú intuitivo para navegar por las diferentes funcionalidades.
* **Visualización de Datos**: Explore el modelo de predicción a través de gráficos interactivos (distribución de deserción, estado de ahorro, variables continuas, matriz de correlaciones, curva ROC, matriz de confusión, función sigmoide, coeficientes beta).
* **Predicción Individual**: Ingrese los datos de un cliente específico para obtener su probabilidad de deserción y una interpretación visual.
* **Análisis Masivo**: Cargue un archivo CSV con datos de múltiples clientes para procesar predicciones en lote.
* **Resultados Detallados**: Visualice estadísticas resumen, gráficos de distribución y una tabla interactiva con las predicciones para cada cliente del análisis masivo.
* **Exportación a PDF**: Genere informes PDF completos con estadísticas, gráficos y tablas de los resultados del análisis masivo.
* **Modal de Personalización**: Herramienta interactiva para seleccionar y filtrar clientes para análisis personalizados y exportación de reportes.

---

## 🛠️ Tecnologías Utilizadas

* **Backend**: Python, Flask
* **Gestión de Sesiones**: Flask-Session
* **Modelos de ML**: Scikit-learn (cargados con `joblib`)
* **Análisis de Datos**: Pandas, NumPy
* **Visualización de Datos**: Matplotlib, Seaborn
* **Generación de PDFs**: ReportLab
* **Frontend**: HTML5, Tailwind CSS
* **Motor de Plantillas**: Jinja2
* **Servicios Web**: Fetch API (para interacciones asíncronas)

---

## 🚀 Configuración y Ejecución Local

Sigue estos pasos para poner en marcha el proyecto en tu máquina local.

### **Requisitos Previos**

* Python 3.8+
* pip (gestor de paquetes de Python)

### **Pasos**

1.  **Clonar el Repositorio**:
    ```bash
    git clone https://github.com/rolando2012/WebRegresionLogistica.git
    cd WebRegresionLogistica
    ```

2.  **Crear y Activar un Entorno Virtual**:
    Es una buena práctica trabajar en un entorno virtual para aislar las dependencias del proyecto.

    * **En Windows**:
        ```bash
        python -m venv env
        .\env\Scripts\activate
        ```
    * **En macOS/Linux**:
        ```bash
        python3 -m venv env
        source env/bin/activate
        ```

3.  **Instalar Dependencias**:
    Una vez activado el entorno virtual, instala todas las librerías necesarias:
    ```bash
    pip install -r requirements.txt
    ```
    *(Si aún no tienes un `requirements.txt`, ejecuta `pip freeze > requirements.txt` después de instalar todas las dependencias manualmente, o usa las listadas en este README.)*

    **Dependencias clave que deberías tener en `requirements.txt`:**
    ```
    Flask
    Flask-Session
    pandas
    numpy
    scikit-learn
    joblib
    matplotlib
    seaborn
    reportlab
    ```

4.  **Ejecutar la Aplicación**:
    ```bash
    python app.py
    ```
    La aplicación se ejecutará en `http://127.0.0.1:5000/` (o un puerto similar). Abre esta URL en tu navegador web.

---

## 📚 Uso

* **Página Principal**: Accede a las diferentes secciones desde el menú principal.
* **Visualizar Datos**: Explora los gráficos pre-generados y la información del modelo.
* **Predicción Individual**: Introduce los datos de un cliente en el formulario y haz clic en "Predecir Deserción" para obtener el resultado.
* **Análisis Masivo**:
    1.  Carga un archivo CSV que cumpla con el formato especificado en la página (ver las columnas requeridas).
    2.  Previsualiza los datos cargados.
    3.  Haz clic en "Predecir Lote" para procesar el análisis.
    4.  Los resultados se mostrarán en una nueva página, desde donde podrás exportar un informe PDF.

---

## 📂 Estructura del Proyecto
```

WebRegresionLogistica/
├── app/
│   ├── init.py           # Inicialización de la aplicación Flask
│   ├── config.py             # Configuración de la aplicación (ej. SESSION_TYPE)
│   ├── main/
│   │   ├── init.py       # Blueprint para las rutas principales
│   │   └── routes.py         # Definición de las rutas y lógica de la vista
│   ├── services/
│   │   ├── init.py       # Inicialización del módulo de servicios
│   │   ├── prediccion_service.py # Lógica para predicción individual
│   │   └── prediccion_masiva_service.py # Lógica para predicción masiva
│   ├── data/
│   │   └── modelo_desercion.joblib # Modelo de ML pre-entrenado (ej. un pipeline)
│   └── templates/
│       └── main/
│           ├── index.html
│           ├── visualizar_datos.html
│           ├── prediccion_individual.html
│           ├── analisis_masivo.html
│           └── # Otros templates para el modal, etc.
├── app.py                    # Punto de entrada de la aplicación
├── requirements.txt          # Dependencias del proyecto
└── README.md                 # Este archivo

```
---
