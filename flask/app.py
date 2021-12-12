import sys
from instance.config import Config
from blueprints.users import users
from blueprints.visitors import visitors
from flask import Flask, redirect, url_for, session, g

# Inicia el objeto de la aplicación.
app = Flask(__name__)

# Actualiza la configuración de la aplicación.
app.config.from_object(Config)

# Este manejador se ejecuta el primero de todos ante cualquier petición.
@app.before_request
def check_session():
    '''
    session --> Cookie de sesión, está asociada a quien realiza la petición.
    g --> Es una variable especial que persiste datos hasta que acaba la petición.
    '''
    g.user = session['user'] if 'user' in session else None

# Página principal
@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('visitors.signup'))

# Registramos los Blueprints
app.register_blueprint(visitors, url_prefix='/visitors')
app.register_blueprint(users, url_prefix='/users')

# Página no encontrada
@app.errorhandler(404)
def page_not_found(error):
    return 'Error 404', 404

# Error interno
@app.errorhandler(500)
def internal_server_error(error):
    return 'Error 500', 500