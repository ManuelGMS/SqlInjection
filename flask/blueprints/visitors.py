from business.asVisitors import asVisitors
from flask import Blueprint, request, redirect, url_for, render_template

# Creamos un blueprint para exportarlo
visitors = Blueprint('visitors', __name__)

@visitors.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html', pagetitle = 'Registrarse', pagename = 'Creación de nuevo usuario', message = request.args.get('message')), 200

@visitors.route('/signin', methods=['GET'])
def signin():
    return render_template('signin.html', pagetitle = 'Autentificarse', pagename = 'Inicio de sesión', message = request.args.get('message')), 200

@visitors.route('/signinadmin', methods=['GET'])
def signinadmin():
    return render_template('signinadmin.html', pagetitle = 'Autentificarse', pagename = 'Acceso para administradores', message = request.args.get('message')), 200

@visitors.route('/createUser', methods=['POST'])
def createUser():
    msg = asVisitors().createUser(request.form.to_dict())
    return redirect(url_for('visitors.signup', message = msg))

@visitors.route('/checkUser', methods=['POST'])
def checkUser():
    
    transfer = asVisitors().checkUser(request.form.to_dict())

    if transfer['ok']:
        
        return redirect(url_for('users.profile', message = transfer['message']))
    
    else:
        
        return redirect(url_for('visitors.signin', message = transfer['message']))

@visitors.route('/checkAdmin', methods=['POST'])
def checkAdmin():
    
    transfer = asVisitors().checkAdmin(request.form.to_dict())

    if transfer['ok']:
        
        return redirect(url_for('users.profile', message = transfer['message']))
    
    else:
        
        return redirect(url_for('visitors.signinadmin', message = transfer['message']))