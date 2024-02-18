from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from library.auth import admin_access
from library.auth import admin_login_required
from library.db import get_db
import pandas as pd

bp = Blueprint ('book', __name__, url_prefix='/books')


@bp.route ('/')
@admin_login_required
def index():
    db = get_db ()

    books = db.execute (
        'SELECT * FROM book'
    ).fetchall ()

    return render_template ('books.index.html', books=books)


@bp.route ('/add')
@admin_login_required
def add():
    total_errors = 0
    books_fail = []

    if request.method == 'POST':
        alert = None
        if request.form['type'] == 'book':
            isbns = request.form.getlist ('isbn')
            titles = request.form.getlist ('title')
            authors = request.form.getlist ('author')
            genres = request.form.getlist ('genre')
            years = request.form.getlist ('year_publiation')

            if None in titles:
                alert = 'Faltan Titulo(s)'
            if alert is None:
                for i in range (len (titles)):
                    isbn, title, author, genre, year = isbns[i], titles[i], authors[i], genres[i], years[i]
                    if not comprobate_add (isbn, title, author, genre, year):
                        total_errors += 1
                        books_fail.append (title)

        elif request.form['type'] == 'file':
            list_book_read = pd.read_excel (request.files['file']).values.tolist ()

            for isbn, title, author, genre, year in list_book_read:
                if not comprobate_add (isbn, title, author, genre, year):
                    total_errors += 1
                    books_fail.append (title)

        if total_errors == 0:
            g.type_alert = 'success'
            alert = 'Libro(s) registrado(s) correctamente'
            return redirect (url_for ('books.index'))
        elif total_errors > 0:
            g.type_alert = 'warning'
            alert = f"Terminado, error en {books_fail}."

    render_template ('books.add_book.html')


@admin_login_required
def comprobate_add(isbn, title, author, genre, year):
    if type (title) != str:
        return True
    skip = ['', 'nan', None]

    if title in skip:
        return True

    db = get_db ()
    id_admin = g.admin['id']

    try:
        db.execute (
            'INSERT INTO book (isbn, title, author, genre, year_publication, up_for)'
            'VALUES (?, ?, ?, ?, ?, ?)',
            (isbn, title, author, genre, year, id_admin)
        )
        db.commit ()
        return True
    except:
        return False


@bp.route ('/delete', methods=('GET', 'POST'))
@admin_login_required
def delete():
    alert = None
    try:
        if request.method == 'POST':
            ids = request.form.getlist ('id')

        elif request.method == 'GET':
            ids = [request.args.get ('id')]
    except:
        ids = [None]

    if len (ids) == 0 or None in ids:
        alert = 'No se ha seleccionado ningún libro'
    else:
        for id in ids:
            comprobate_book (id)
            comprobate_delete (id)


@admin_login_required
def comprobate_delete(id):
    db = get_db ()
    try:
        db.execute (
            'DELETE FROM book WHERE id = ?',
            (id)
        )
        db.commit ()
        return True
    except:
        return False


@admin_login_required
def comprobate_book(id):
    id_admin = g.admin['admin']

    db = get_db ()

    book = db.execute (
        'SELECT * FROM book WHERE id = ?',
        (id,)
    ).fetchone ()

    if book is None:
        abort (f"Libro inexistente")
    if book['up_for'] != id_admin:
        abort (403, 'No tienes permiso para acceder a este libro')

    return book
