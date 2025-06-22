import joblib
import pandas as pd
from pathlib import Path

class PrediccionService:
    def __init__(self):
        self.modelo = None
        self.cargar_modelo()

    def cargar_modelo(self):
        """Cargar el modelo desde el archivo joblib"""
        try:
            # 1) Dirección del directorio donde está este fichero:
            base_dir = Path(__file__).resolve().parent
            # 2) Subimos un nivel: de .../app/services → .../app
            project_dir = base_dir.parent
            # 3) Apuntamos a la carpeta data y al .joblib
            modelo_path = project_dir / 'data' / 'modelo_desercion.joblib'

            # Carga
            self.modelo = joblib.load(modelo_path)
            print(f"Modelo cargado exitosamente desde {modelo_path}")

        except Exception as e:
            print(f"Error al cargar el modelo: {e}")
            self.modelo = None
    
    def predecir_desercion(self, datos_cliente):
        """
        Predecir la probabilidad de deserción para un cliente
        
        Args:
            datos_cliente (dict): Diccionario con los datos del cliente
            
        Returns:
            dict: Resultado de la predicción con probabilidad, z_score, etc.
        """
        if self.modelo is None:
            raise Exception("Modelo no está cargado")
        
        try:
            # Convertir datos a DataFrame
            df_cliente = pd.DataFrame([datos_cliente])
            
            # Realizar predicción
            probabilidad = self.modelo.predict_proba(df_cliente)[:, 1][0]
            prediccion = self.modelo.predict(df_cliente)[0]
            
            # Calcular z-score para el gráfico
            z_score = self._calcular_z_score(df_cliente)
            
            return {
                'probabilidad': float(probabilidad),
                'prediccion': int(prediccion),
                'z_score': float(z_score),
                'datos_cliente': datos_cliente
            }
            
        except Exception as e:
            raise Exception(f"Error en la predicción: {str(e)}")
    
    def _calcular_z_score(self, df_cliente):
        """
        Calcular el z-score (score lineal) para el gráfico de la sigmoide
        """
        try:
            # Obtener intercepto y coeficientes del modelo
            intercept = self.modelo.named_steps["regresion_logistica"].intercept_[0]
            coef = self.modelo.named_steps["regresion_logistica"].coef_.ravel()
            
            # Transformar los datos usando el escalador del modelo
            X_scaled = self.modelo.named_steps["escalador"].transform(df_cliente)
            
            # Calcular z-score
            z_score = intercept + X_scaled.dot(coef)
            
            return z_score[0]
            
        except Exception as e:
            print(f"Error calculando z-score: {e}")
            # Retornar un valor por defecto si hay error
            return 0.0
    
    def validar_datos(self, datos):
        """
        Validar que los datos del cliente estén completos y en el rango correcto
        
        Args:
            datos (dict): Datos del cliente a validar
            
        Returns:
            tuple: (es_valido, lista_errores)
        """
        errores = []
        
        # Campos requeridos
        campos_requeridos = [
            'edad', 'tasa_interes', 'porcentaje_pago', 'dias_de_mora',
            'plazo_credito_meses', 'num_microseguros', 'n_productos_vigentes',
            'n_creditos_vigentes', 'calidad_servicio', 'estado_ahorro_activo'
        ]
        
        # Verificar campos requeridos
        for campo in campos_requeridos:
            if campo not in datos or datos[campo] is None:
                errores.append(f"El campo '{campo}' es requerido")
                continue
                
            # Convertir a numérico si es string
            try:
                datos[campo] = float(datos[campo])
            except (ValueError, TypeError):
                errores.append(f"El campo '{campo}' debe ser un número válido")
                continue
        
        # Validaciones de rango si no hay errores básicos
        if not errores:
            # Edad
            if not (18 <= datos['edad'] <= 80):
                errores.append("La edad debe estar entre 18 y 80 años")
            
            # Tasa de interés
            if not (0 <= datos['tasa_interes'] <= 12):
                errores.append("La tasa de interés debe estar entre 0% y 50%")
            
            # Porcentaje de pago
            if not (0 <= datos['porcentaje_pago'] <= 100):
                errores.append("El porcentaje de pago debe estar entre 0% y 100%")
            
            # Días de mora
            if not (0 <= datos['dias_de_mora'] <= 365):
                errores.append("Los días de mora deben estar entre 0 y 365")
            
            # Plazo
            if not (1 <= datos['plazo_credito_meses'] <= 120):
                errores.append("El plazo debe estar entre 1 y 60 meses")
            
            # Microseguros
            if not (0 <= datos['num_microseguros'] <= 5):
                errores.append("El número de microseguros debe estar entre 0 y 10")
            
            # Productos vigentes
            if not (0 <= datos['n_productos_vigentes'] <= 10):
                errores.append("El número de productos vigentes debe estar entre 0 y 20")
            
            # Créditos vigentes
            if not (0 <= datos['n_creditos_vigentes'] <= 5):
                errores.append("El número de créditos vigentes debe estar entre 0 y 10")
            
            # Calidad de servicio
            if not (0 <= datos['calidad_servicio'] <= 100):
                errores.append("La calidad de servicio debe estar entre 1 y 5")
            
            # Estado de ahorro (debe ser 0 o 1)
            if datos['estado_ahorro_activo'] not in [0, 1]:
                errores.append("El estado de ahorro debe ser 0 o 1")
        
        return len(errores) == 0, errores