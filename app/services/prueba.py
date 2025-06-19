import joblib
import pandas as pd

# 1) Cargar el modelo exportado
# Asegúrate de que 'modelo_churn.joblib' esté en el mismo directorio o ajusta la ruta.
modelo = joblib.load("modelo_churn.joblib")

# 2) Definir 2 ejemplos nuevos SIN la columna 'desercion'
#    - Ejemplo A: perfil muy cumplidor y vinculado → esperamos baja probabilidad de fuga (~0.1)
#    - Ejemplo B: perfil de riesgo alto → esperamos alta probabilidad de fuga (~0.8)

ejemplos = pd.DataFrame([
    {
        "edad": 33,
        "tasa_interes": 8.0,
        "porcentaje_pago": 98.0,
        "dias_de_mora": 0,
        "plazo_credito_meses": 24,
        "num_microseguros": 3,
        "n_productos_vigentes": 5,
        "n_creditos_vigentes": 1,
        "calidad_servicio": 90.0,
        "estado_ahorro_activo": 1
    },
    {
        "edad": 27,
        "tasa_interes": 16.0,
        "porcentaje_pago": 45.0,
        "dias_de_mora": 40,
        "plazo_credito_meses": 60,
        "num_microseguros": 0,
        "n_productos_vigentes": 1,
        "n_creditos_vigentes": 3,
        "calidad_servicio": 50.0,
        "estado_ahorro_activo": 0
    }
])

# 3) Predecir probabilidades y clases
probabilidades = modelo.predict_proba(ejemplos)[:, 1]
predicciones   = modelo.predict(ejemplos)

# 4) Mostrar resultados
for i, (prob, pred) in enumerate(zip(probabilidades, predicciones), start=1):
    print(f"Ejemplo {i}:")
    print(f"  • Probabilidad de deserción: {prob:.2f}")
    print(f"  • Predicción (0=fiel, 1=desertor): {pred}")
    print()

# --- Comentarios sobre resultados esperados ---
# Para el Ejemplo 1, al tener alto porcentaje de pago, cero días de mora,
# varios productos y microseguros, esperamos algo como:
#   Probabilidad ≈ 0.10, Predicción = 0
#
# Para el Ejemplo 2, con baja tasa de pago, muchos días de mora,
# pocos productos y sin ahorro, esperamos algo como:
#   Probabilidad ≈ 0.80, Predicción = 1
