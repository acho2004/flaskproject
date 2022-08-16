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
                return redirect(url_for('auth.change_password'))
            else:
                return redirect('/')

        flash(error)

    return render_template('login.html')

@bp.route('/change_password', methods=('GET', 'POST'))
def change_password():
    if g.user is None:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        password = request.form['password']
        repassword = request.form['repassword']
        if password != repassword:
            flash("패스워드가 동일하지 않습니다. 다시한번 확인해주세요.")
        else:
            db = get_db()
            db.execute(
                'UPDATE hunet_members SET password = ?, pchanged = ?'
                ' WHERE id = ?',
                (generate_password_hash(password), 1, g.user['id'])
            )
            db.commit()
            return redirect('/')
    return render_template('change_password.html')


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