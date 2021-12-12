import datetime
from business.asUsers import asUsers
from flask import Blueprint, g, session, request, redirect, url_for, render_template

# Creamos un blueprint para exportarlo
users = Blueprint('users', __name__)

# ****************************************************************************************************************************************
# ****************************************************************************************************************************************
# ****************************************************************************************************************************************

@users.before_request
def check_logged():
    # Si el usuario no está registrado le redirigimos al inicio de sesión.
    if g.user is None: return url_for('visitors.signin')

# ****************************************************************************************************************************************
# ****************************************************************************************************************************************
# ****************************************************************************************************************************************

@users.route('/profile', methods=['GET'])
def profile():
    return render_template('profile.html', pagetitle = 'Perfil', pagename = 'Perfil de usuario'), 200

# ****************************************************************************************************************************************

@users.route('/logout', methods=['GET'])
def logout():
    # Vacía el contenido de la cookie de sesión.
    session.clear()
    # Redirige al usuario a la página de inicio de sesión.
    return redirect(url_for('visitors.signin'))

# ****************************************************************************************************************************************

@users.route('/purchases', methods=['GET', 'POST'])
def purchases():
    if request.method == 'GET':
        return render_template('purchases.html', pagetitle = 'Compras', pagename = 'Mis compras', sysdate = datetime.date.today()), 200
    elif request.method == 'POST':
        purchases = asUsers().getUserPurchasesOf(request.form.to_dict())
        return render_template('purchases.html', pagetitle = 'Compras', pagename = 'Mis compras', purchases = purchases, sysdate = datetime.date.today()), 200

# ****************************************************************************************************************************************

@users.route('/products', methods=['GET'])
def products():
    products = asUsers().getProducts()
    return render_template('products.html', pagetitle = 'Catálogo', pagename = 'Catalogo de productos', products = products), 200

@users.route('/buyProducts/<id_user>/<id>', methods=['GET'])
def buyProducts(id, id_user):
    mess = asUsers().buyProducts(request.args.to_dict(), id_user, id)
    return render_template('products_buy.html', pagetitle = "Compra realizada", pagename = mess), 200

# ****************************************************************************************************************************************
# ****************************************************************************************************************************************
# ****************************************************************************************************************************************
