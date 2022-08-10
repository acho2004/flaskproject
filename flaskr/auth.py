import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flaskr.db import get_db
from werkzeug.security import check_password_hash, generate_password_hash


bp = Blueprint('auth', __name__)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if g.user is not None:
        return(redirect('/'))

    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM hunet_members WHERE emp_no = ?', (id,)
        ).fetchone()

        if user is None:
            error = 'Incorrect id.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'


        if error is None:
            session.clear()
            session['user_id'] = user['id']
            if user['pchanged'] == 0:
                return redirect(url_for('auth.passchange'))
            else:
                return redirect('/')

        flash(error)

    return render_template('login.html')

@bp.route('/passchange', methods=('GET', 'POST'))
def passchange():
    if g.user is None:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        password = request.form['password']
        repassword = request.form['repassword']
        if password != repassword:
            flash("Password and Repeated Password are Different.")
        else:
            db = get_db()
            db.execute(
                'UPDATE hunet_members SET password = ?, pchanged = ?'
                ' WHERE id = ?',
                (generate_password_hash(password), 1, g.user['id'])
            )
            db.commit()
            return redirect('/')
    return render_template('passchange.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM hunet_members WHERE id = ?', (user_id,)
        ).fetchone()