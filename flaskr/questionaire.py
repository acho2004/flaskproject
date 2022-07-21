import sys


from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

sys.path.append("../../")

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('questionaire', __name__)


@bp.route('/profile')
def profile():
    if g.user is None:
        return redirect(url_for('auth.login'))
    db = get_db()
    selfassessments = db.execute(
        'SELECT p.id, created, author_id, username, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20'
        ' FROM stest p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    peerassessments = db.execute(
        'SELECT p.id, created, author_id, username, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, target_username'
        ' FROM ptest p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('/profile.html',
                           selfassessments=list(map(lambda row: dict(row), selfassessments)),
                           peerassessments=list(map(lambda row: dict(row), peerassessments)))


@bp.route('/selftest', methods=('GET', 'POST'))
@login_required
def selftest():
    if g.user is None:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        q1 = request.form['q1']
        q2 = request.form['q2']
        q3 = request.form['q3']
        q4 = request.form['q4']
        q5 = request.form['q5']
        q6 = request.form['q6']
        q7 = request.form['q7']
        q8 = request.form['q8']
        q9 = request.form['q9']
        q10 = request.form['q10']
        q11 = request.form['q11']
        q12 = request.form['q12']
        q13 = request.form['q13']
        q14 = request.form['q14']
        q15 = request.form['q15']
        q16 = request.form['q16']
        q17 = request.form['q17']
        q18 = request.form['q18']
        q19 = request.form['q19']
        q20 = request.form['q20']
        error = None
        db = get_db()
        if not q1 or not q2 or not q3 or not q4 or not q5 or not q6 or not q7 or not q8 or not q9 or not q10 or not q11 or not q12 or not q13 or not q14 or not q15 or not q16 or not q17 or not q18 or not q19 or not q20:
            error = 'All questions are required.'

        if error is not None:
            flash(error)
        else:
            db.execute(
                'INSERT INTO stest (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, author_id)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, g.user['id'])
            )
            db.commit()
            return redirect(url_for('questionaire.profile'))

    return render_template('/selftest.html')



@bp.route('/peertest', methods=('GET', 'POST'))
@login_required
def peertest():
    if g.user is None:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        q1 = request.form['q1']
        q2 = request.form['q2']
        q3 = request.form['q3']
        q4 = request.form['q4']
        q5 = request.form['q5']
        q6 = request.form['q6']
        q7 = request.form['q7']
        q8 = request.form['q8']
        q9 = request.form['q9']
        q10 = request.form['q10']
        q11 = request.form['q11']
        q12 = request.form['q12']
        q13 = request.form['q13']
        q14 = request.form['q14']
        q15 = request.form['q15']
        q16 = request.form['q16']
        q17 = request.form['q17']
        q18 = request.form['q18']
        q19 = request.form['q19']
        q20 = request.form['q20']
        target_username = request.form['target_username']
        error = None
        db = get_db()
        if not q1 or not q2 or not q3 or not q4 or not q5 or not q6 or not q7 or not q8 or not q9 or not q10 or not q11 or not q12 or not q13 or not q14 or not q15 or not q16 or not q17 or not q18 or not q19 or not q20 or not target_username:
            error = 'All questions are required.'

        if error is not None:
            flash(error)
        else:
            db.execute(
                'INSERT INTO ptest (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, author_id, target_username)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, g.user['id'], target_username)
            )
            db.commit()
            return redirect(url_for('questionaire.profile'))

    return render_template('/peertest.html')