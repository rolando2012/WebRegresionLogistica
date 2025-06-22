import joblib
import pandas as pd
import numpy as np
import os
from pathlib import Path

class PrediccionMasivaService:
    def __init__(self):
        # 1) Directorio base y ruta al joblib
        base_dir   = Path(__file__).resolve().parent
        project_dir= base_dir.parent
        modelo_path= project_dir / 'data' / 'modelo_desercion.joblib'

        if not modelo_path.exists():
            raise FileNotFoundError(f"Modelo no encontrado en {modelo_path}")
        
        # 2) Carga del pipeline completo (escalador + regresión)
        self.pipeline = joblib.load(modelo_path)

        # 3) Define aquí las columnas en el mismo orden que el modelo espera
        self.expected_columns = [
            "edad", "tasa_interes", "porcentaje_pago",
            "dias_de_mora", "plazo_credito_meses",
            "num_microseguros", "n_productos_vigentes",
            "n_creditos_vigentes", "calidad_servicio",
            "estado_ahorro_activo"
        ]

    def procesar_csv_data(self, csv_data):
        """
        Procesar datos CSV y realizar predicciones
        
        Args:
            csv_data: Lista de diccionarios con los datos del CSV
        Returns:
            dict: Resultados de la predicción con estadísticas y datos detallados
        """
        try:
            # 1) Convertir a DataFrame
            df = pd.DataFrame(csv_data)

            # 2) Validar columnas
            missing = [c for c in self.expected_columns if c not in df.columns]
            if missing:
                raise ValueError(f"Faltan columnas: {missing}")

            # 3) Construir X en el orden correcto
            X = df[self.expected_columns].astype(float)

            # 4) Predecir
            probs = self.pipeline.predict_proba(X)[:, 1]
            preds = self.pipeline.predict(X)

            # 5) Extraer intercepto y coeficientes para z-scores
            logreg = self.pipeline.named_steps["regresion_logistica"]
            scaler = self.pipeline.named_steps["escalador"]
            intercept = logreg.intercept_[0]
            coef      = logreg.coef_.ravel()

            # 6) Calcular score lineal y sigmoide
            Xs = scaler.transform(X)
            zs = intercept + Xs.dot(coef)
            sig = 1 / (1 + np.exp(-zs))

            # 7) Añadir columnas al df original
            df["prob_desercion"]       = probs
            df["prediccion_desercion"] = preds
            df["z_score"]              = zs
            df["sigmoide"]             = sig

            # 8) Estadísticas generales
            total       = len(df)
            fieles      = int((preds == 0).sum())
            desertores  = int((preds == 1).sum())
            riesgo_alto = int(((preds == 1) & (probs >= 0.8)).sum())
            pct_fieles     = round(fieles    / total * 100, 1)
            pct_desertores = round(desertores/ total * 100, 1)

            datos_torta = {
                "fieles":     {"cantidad": fieles,      "porcentaje": pct_fieles},
                "desertores": {"cantidad": desertores,  "porcentaje": pct_desertores}
            }

            datos_sigmoide = [
                {"z_score": float(zs[i]), "sigmoide": float(sig[i]), "prediccion": int(preds[i])}
                for i in range(total)
            ]

            datos_detallados = []
            for i in range(total):
                datos_detallados.append({
                    "id":              f"{i+1:03d}",
                    "edad":            int(df.iloc[i]["edad"]),
                    "probabilidad":    float(probs[i]),
                    "prediccion":      int(preds[i]),
                    "riesgo":          "ALTO" if preds[i] == 1 else "BAJO",
                    "z_score":         float(zs[i]),
                    "sigmoide":        float(sig[i])
                })

            return {
                "success": True,
                "estadisticas": {
                    "total_clientes":    total,
                    "clientes_fieles":    fieles,
                    "posibles_desertores":desertores,
                    "riesgo_alto":        riesgo_alto,
                    "pct_fieles":         pct_fieles,
                    "pct_desertores":     pct_desertores
                },
                "datos_torta":      datos_torta,
                "datos_sigmoide":   datos_sigmoide,
                "datos_detallados": datos_detallados,
                "total_procesados": total
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
