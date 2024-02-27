import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, abort
)
from werkzeug.security import check_password_hash, generate_password_hash
from library.db import get_db


bp = Blueprint('auth', __name__, url_prefix='/')

@bp.route('/')
def index():
    return render_template('auth/index.html')

@bp.route('admin/register', methods=('GET', 'POST'))
def admin_register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None


        if not email:
            error = 'Correo Electronico requerido.'
        elif not password:
            error = 'Contraseña requerida'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO users (email, password) VALUES (?, ?)",
                    (email, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Email {email} ya esta registrado."
            else:
                g.type_alert = 'success'
                alert = 'Usuario registrado correctamente'
                flash(alert)

                return redirect(url_for("auth.admin_login"))


        g.type_alert = 'warning'
        flash(error)

    return render_template('auth/admin/register.html')



@bp.route('/admin/login', methods=('GET', 'POST'))
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM admin WHERE email = ?', (email,)
        ).fetchone()

        if user is None:
            error = 'Correo Electronico incorrecto'
        elif not check_password_hash(user['password'], password):
            error = 'Contraseña incorrecta'

        if error is None:
            session.clear()
            session['type_user'] = 1
            session['admin_id'] = user['id']
            return redirect(url_for('users.index'))
        g.type_alert = 'warning'
        flash(error)
    return render_template('auth/admin/login.html')


@bp.before_app_request
def load_logged_in_user():

    type_user = session.get('type_user')

    if type_user == 1:
        g.type_user = type_user
        admin_id = session.get('admin_id')

        g.admin = get_db().execute(
            'SELECT * FROM admin WHERE id = ?', (admin_id,)
        ).fetchone()

    elif type_user == 2:
        g.type_user = type_user
        admin_id = session.get('user_id')

        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (admin_id,)
        ).fetchone()

    elif type_user is None:
        g.user = None


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.admin_login'))


def admin_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.admin is None or g.type_user != 1:
            return redirect(url_for('auth.admin_login'))
        
        return view(**kwargs)

    return wrapped_view

def admin_access():
    if g.type_user != 1:
        abort(403, 'No tienes acceso')








