from flask import Flask
from flask_session import Session


def create_app():
    app = Flask(__name__ , instance_relative_config=True)
    app.config.from_object('app.config.Config')
    app.config['DEBUG'] = True
    Session(app)

    # Registrar blueprints
    from app.main.routes import main
    app.register_blueprint(main)

    return app