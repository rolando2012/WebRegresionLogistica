import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una-cadena-dificil-de-adivinar'
    DEBUG = True

    # → Configuración de Flask-Session
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.path.dirname(__file__), 'instance', 'sessions')
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=120)
    SESSION_USE_SIGNER = True
    # Número máximo de sesiones antes de limpiar las más antiguas
    SESSION_FILE_THRESHOLD = 500
