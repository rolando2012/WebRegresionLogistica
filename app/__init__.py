from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SECRET_KEY'] = 'tu-clave-secreta-aqui'
    app.config['DEBUG'] = True

    # Registrar blueprints
    from app.main.routes import main
    app.register_blueprint(main)

    return app