from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from library.auth import admin_access
from library.auth import admin_login_required
from library.db import get_db
import pandas as pd
import email_validator

bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('/')
@admin_login_required
def index():
    id_admin = g.admin['id']
    db = get_db()

    users = db.execute(
        'SELECT * FROM user_up WHERE id_admin = ? and status = 1', (id_admin,)
    ).fetchall()

    if len(users) == 0:
        users = 0

    return render_template('users/index.html', users = users)

@bp.route('/disabled', methods=('GET', 'POST'))
@admin_login_required
def users_dis():
    if request.method == 'POST':
        return request.form.getlist('id')

    id_admin = g.admin['id']
    db = get_db()
    users = db.execute(
        'SELECT * FROM user_up WHERE id_admin = ? and status = 0', (id_admin,)
    ).fetchall()

    if len(users) == 0:
        users = 0

    return render_template('users/index.html', users = users)



@bp.route('/add', methods=('GET', 'POST'))
@admin_login_required
def add_users():
    total_errors = 0
    email_fail = []
    alert = None

    if request.method == 'POST':
        if request.form['type'] == 'user':
            enrollments = request.form.getlist('enrollment')
            emails = request.form.getlist('email')

            if None in emails:
                alert = 'Falta email(s)'
            if None in enrollments:
                alert = 'Falta matricula(s)'
            if len(enrollments) != len(emails):
                alert = 'Datos incompletos'

            if alert is None:
                for i in range (len(emails)):
                    enrollment, email = enrollments[i], emails[i]

                    if not comprobate_add_user(enrollment, email):
                        email_fail.append (email)
                        total_errors += 1


        elif request.form['type'] == 'file':
            try:
                list_user_read = pd.read_excel(request.files['file']).values.tolist()
                for enr, email in list_user_read:

                    # try:
                    #   if not email_validator.validate_email(email):
                    # except EmailUndeliverableError:
                    #   alert 'el dominio no existe'

                    if not comprobate_add_user (enr, email):
                        email_fail.append (email)
                        total_errors += 1
            except:
                alert = 'Ha ocurrido un error al leer el archivo'


        if alert is not None:
            type_alert = 'danger'
            alert = alert
        elif total_errors == 0:
            type_alert = 'success'
            alert = 'Usuarios registrado correctamente'
        elif total_errors > 0:
            type_alert = 'warning'
            alert = f"Terminado, uno o más datos registrados {email_fail}."

        session['type_alert'] = type_alert
        flash(alert)
    return render_template ('users/add_user.html')


def comprobate_add_user(enrollment, email):
    admin_access()
    if type (email) != str:
        return True

    skip = ['', 'nan', None]

    if enrollment in skip or email in skip:
        return True


    count_arr = email.count ('@')
    count_point = email.count ('.')

    if count_arr != 1 or count_point < 1:
        return False

    db = get_db()
    id_admin = g.admin['id']

    try:
        db.execute (
            'INSERT INTO user_up (enrollment, email, id_admin, status)'
            ' VALUES (?, ?, ?, ?)',
            (enrollment, email, id_admin, 1)
        )
        db.commit ()
        return True
    except db.IntegrityError:
        return False


@bp.route('/change_status', methods=('GET', 'POST'))
@admin_login_required
def change_status():
    db = get_db()
    total_errors = 0
    alert = None

    try:
        if request.method == 'POST':
            ids = request.form.getlist ('id')
        elif request.method == 'GET':
            ids = [request.args.get ('id')]
    except:
        ids = [None]

    if None in ids or len (ids) == 0:
        alert = 'No ha seleccionado ningún usuario'
    else:
        for id in ids:
            com_user = comprobate_user (id)
            status = (~com_user['status'] & 1)

            if not change_status_user(id, status):
                total_errors += 1

    if alert is not None:
        type_alert = 'danger'
        alert = alert
    elif total_errors == 0:
        type_alert = 'success'
        alert = 'Usuario(s) Deshabilitado(s) correctamente.'
    else:
        type_alert = 'warning'
        alert = 'Terminado, ha habido errores.'

    session['type_alert'] = type_alert
    flash (alert)
    return redirect (url_for ('users.index'))

def change_status_user(id, status):
    db = get_db()
    admin_access()

    try:
        db.execute(
            'UPDATE user_up SET status = ?'
            ' WHERE id = ?',
            (status, id)
        )
        db.commit()
        return True
    except:
        return False

@bp.route('/delete', methods=('GET', 'POST'))
@admin_login_required
def delete_user():
    db = get_db()
    total_errors = 0
    alert = None

    try:
        if request.method == 'POST':
            ids = request.form.getlist ('id')
        elif request.method == 'GET':
            ids = [request.args.get ('id')]
    except:
        ids = [None]

    if None in ids or len (ids) == 0:
        alert = 'No ha seleccionado ningún usuario'
    else:
        for id in ids:
            comprobate_user(id)
            if not del_user(id):
                total_errors += 1

    if alert is not None:
        type_alert = 'danger'
        alert = alert
    elif total_errors == 0 :
        type_alert = 'success'
        alert = 'Usuario(s) eliminado(s) correctamente.'
    else:
        type_alert = 'warrning'
        alert = 'Terminado, ha habido errores.'

    session['type_alert'] = type_alert
    flash (alert)
    return redirect (url_for ('users.users'))

def comprobate_user(id):
    admin_access()
    db = get_db()
    id_admin = g.admin['id']

    user = db.execute(
        'SELECT * FROM user_up WHERE id = ?',
        (id,)
    ).fetchone()

    if user is None:
        abort(404, f'Usuario inexistente')

    if user['id_admin'] != id_admin:
        abort(403, 'No tiene permisos para acceder a este usuario')

    return user


def del_user(id):
    admin_access()
    db = get_db()
    try:
        db.execute (
            'DELETE FROM user_up WHERE id = ?',
            (id)
        )
        db.commit ()
        return True
    except:
        return False


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@admin_login_required
def update_user(id):
    user = comprobate_user(id)

    if request.method == 'POST':
        enrrolment = request.form['enrrolment']
        email = request.form['email']
        alert = None

        if not enrrolment:
            alert = 'Falta enrrolment'
        if not email:
            alert = 'Falta email'

        if alert is not None:
            session['type_alert'] = 'danger'
            flash(alert)
        else:
            db = get_db()
            db.execute(
                'UPDATE user_up SET enrollment = ?, email = ?'
                ' WHERE id = ?',
                (enrrolment, email, id)
            )
            db.commit()
            alert = 'Actualización correcta'
            session['type_alert'] = 'success'
            flash(alert)
            return redirect(url_for('users.users'))

    return render_template('users.user_update.html', user)














