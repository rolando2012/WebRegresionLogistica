from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Esta será la página de inicio (menú principal)
    return render_template('main/index.html', titulo="Hola Mundo")
