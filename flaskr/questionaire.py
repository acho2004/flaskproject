import sys
import random
import string

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

sys.path.append("../../")

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('questionaire', __name__)

@bp.route("/results/self/<string:title>")
def display_spost(title: str):
    db = get_db()
    route = db.execute(
        'SELECT * FROM stest WHERE route = ?', (title,)
    ).fetchone()
    if route is None:
        abort(404)
    if not(g.user is None) and route['author_id'] == g.user['id']:
        db.execute(
            'UPDATE stest SET new_tag = ?'
            ' WHERE id = ?',
            (0, route['id'])
        )
        db.commit()
    return render_template('sresults.html', route=route)


@bp.route("/results/peer/<string:title>")
def display_ppost(title: str):
    db = get_db()
    route = db.execute(
        'SELECT * FROM ptest WHERE route = ?', (title,)
    ).fetchone()
    if route is None:
        abort(404)
    if not (g.user is None) and route['target_username'] == g.user['username']:
        db.execute(
            'UPDATE ptest SET new_tagp = ?'
            ' WHERE id = ?',
            (0, route['id'])
        )
        db.commit()
    if not (g.user is None) and route['username'] == g.user['username']:
        db.execute(
            'UPDATE ptest SET new_tags = ?'
            ' WHERE id = ?',
            (0, route['id'])
        )
        db.commit()
    return render_template('presults.html', route=route)


@bp.route('/profile')
def profile():
    if g.user is None:
        return redirect(url_for('auth.login'))
    db = get_db()
    selfassessments = db.execute(
        'SELECT p.id, created, author_id, u.username, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, route, new_tag'
        ' FROM stest p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    peerassessments = db.execute(
        'SELECT p.id, created, author_id, u.username, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, target_username, route, new_tagp, new_tags'
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
        obtainedUnique = False
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
            while (not obtainedUnique):
                try:
                    db.execute(
                        'INSERT INTO stest (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, author_id, username, route, new_tag)'
                        ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20,
                         g.user['id'], g.user['username'], ''.join(
                            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(24)), 1)
                    )
                    db.commit()
                    obtainedUnique = True
                except db.IntegrityError:
                    obtainedUnique = False
            return redirect(url_for('questionaire.profile'))
    return render_template('/selftest.html')



@bp.route('/peertest', methods=('GET', 'POST'))
@login_required
def peertest():
    if g.user is None:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        obtainedUnique = False
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

        if target_username == g.user['username']:
            error = "You can't submit a form for yourself."

        if error is not None:
            flash(error)
        else:
            while (not obtainedUnique):
                try:
                    db.execute(
                        'INSERT INTO ptest (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, author_id, username, target_username, route, new_tags, new_tagp)'
                        ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20,
                         g.user['id'], g.user['username'], target_username, ''.join(
                            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(24)), 1,
                         1)
                    )
                    db.commit()
                    obtainedUnique = True
                except db.IntegrityError:
                    obtainedUnique = False

            return redirect(url_for('questionaire.profile'))

    return render_template('/peertest.html')






@bp.route('/addsample', methods=('GET', 'POST'))
@login_required
def addsample():
    if g.user is None:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        obtainedUnique = False
        mbti = request.form['MBTI']
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
        if not q1 or not q2 or not q3 or not q4 or not q5 or not q6 or not q7 or not q8 or not q9 or not q10 or not q11 or not q12 or not q13 or not q14 or not q15 or not q16 or not q17 or not q18 or not q19 or not q20 or not mbti:
            error = 'All questions are required.'

        if error is not None:
            flash(error)
        else:
            while (not obtainedUnique):
                try:
                    db.execute(
                        'INSERT INTO samples (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, author_id, username, route, real_MBTI)'
                        ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20,
                         g.user['id'], g.user['username'], ''.join(
                            random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(24)), mbti)
                    )
                    db.commit()
                    obtainedUnique = True
                except db.IntegrityError:
                    obtainedUnique = False
            return redirect(url_for('questionaire.profile'))
    return render_template('/addsample.html')