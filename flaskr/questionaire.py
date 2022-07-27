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
        'SELECT p.id, created, author_id, u.username, route, new_tag, guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP'
        ' FROM stest p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    peerassessments = db.execute(
        'SELECT p.id, created, author_id, u.username, target_username, route, new_tagp, new_tags, guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP'
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
        q21 = request.form['q21']
        q22 = request.form['q22']
        q23 = request.form['q23']
        q24 = request.form['q24']
        q25 = request.form['q25']
        q26 = request.form['q26']
        q27 = request.form['q27']
        q28 = request.form['q28']
        q29 = request.form['q29']
        q30 = request.form['q30']
        q31 = request.form['q31']
        q32 = request.form['q32']

        x = ""
        error = None
        db = get_db()
        if not q1 or not q2 or not q3 or not q4 or not q5 or not q6 or not q7 or not q8 or not q9 or not q10 or not q11 or not q12 or not q13 or not q14 or not q15 or not q16 or not q17 or not q18 or not q19 or not q20 or not q21 or not q22 or not q23 or not q24 or not q25 or not q26 or not q27 or not q28 or not q29 or not q30 or not q31 or not q32:
            error = 'All questions are required.'

        if error is not None:
            flash(error)
        else:
            while (not obtainedUnique):
                try:
                    x = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(24))
                    db.execute(
                        'INSERT INTO stest (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, q21, q22, q23, q24, q25, q26, q27, q28, q29, q30, q31, q32, author_id, username, route, new_tag, guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP)'
                        ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, q21, q22, q23, q24, q25, q26, q27, q28, q29, q30, q31, q32,
                         g.user['id'], g.user['username'], x, 1, -999, -999, -999, -999)
                    )
                    db.commit()
                    obtainedUnique = True
                except db.IntegrityError:
                    obtainedUnique = False
            db.execute(
                'UPDATE stest SET guess_MBTI_EI = ?, guess_MBTI_SN = ?, guess_MBTI_TF = ?, guess_MBTI_JP = ?'
                ' WHERE route = ?',
                (sguesser(x)[0], sguesser(x)[1], sguesser(x)[2], sguesser(x)[3], x)
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
        q21 = request.form['q21']
        q22 = request.form['q22']
        q23 = request.form['q23']
        q24 = request.form['q24']
        q25 = request.form['q25']
        q26 = request.form['q26']
        q27 = request.form['q27']
        q28 = request.form['q28']
        q29 = request.form['q29']
        q30 = request.form['q30']
        q31 = request.form['q31']
        q32 = request.form['q32']

        sresp1 = request.form['sresp1']
        sresp2 = request.form['sresp2']
        sresp3 = request.form['sresp3']
        sresp4 = request.form['sresp4']
        sresp5 = request.form['sresp5']
        x = ""

        target_username = request.form['target_username']
        error = None
        db = get_db()
        if not q1 or not q2 or not q3 or not q4 or not q5 or not q6 or not q7 or not q8 or not q9 or not q10 or not q11 or not q12 or not q13 or not q14 or not q15 or not q16 or not q17 or not q18 or not q19 or not q20 or not q21 or not q22 or not q23 or not q24 or not q25 or not q26 or not q27 or not q28 or not q29 or not q30 or not q31 or not q32 or not sresp1 or not sresp2 or not sresp3 or not sresp4 or not sresp5 or not target_username:
            error = 'All questions are required.'

        if target_username == g.user['username']:
            error = "You can't submit a form for yourself."

        if error is not None:
            flash(error)
        else:
            while (not obtainedUnique):
                try:
                    x = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(24))
                    db.execute(
                        'INSERT INTO ptest (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, q21, q22, q23, q24, q25, q26, q27, q28, q29, q30, q31, q32, sresp1, sresp2, sresp3, sresp4, sresp5, author_id, username, target_username, route, new_tags, new_tagp, guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP)'
                        ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, q21, q22, q23, q24, q25, q26, q27, q28, q29, q30, q31, q32, sresp1, sresp2, sresp3, sresp4, sresp5,
                         g.user['id'], g.user['username'], target_username, x, 1,
                         1, -999, -999, -999, -999)
                    )
                    db.commit()
                    obtainedUnique = True
                except db.IntegrityError:
                    obtainedUnique = False
            db.execute(
                'UPDATE ptest SET guess_MBTI_EI = ?, guess_MBTI_SN = ?, guess_MBTI_TF = ?, guess_MBTI_JP = ?'
                ' WHERE route = ?',
                (pguesser(x)[0], pguesser(x)[1], pguesser(x)[2], pguesser(x)[3], x)
            )
            db.commit()
            return redirect(url_for('questionaire.profile'))

    return render_template('/peertest.html')






@bp.route('/addsample', methods=('GET', 'POST'))
@login_required
def addsample():
    if g.user is None:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        obtainedUnique = False
        q1 = random.randrange(0, 7)
        q2 = random.randrange(0, 7)
        q3 = random.randrange(0, 7)
        q4 = random.randrange(0, 7)
        q5 = random.randrange(0, 7)
        q6 = random.randrange(0, 7)
        q7 = random.randrange(0, 7)
        q8 = random.randrange(0, 7)
        q9 = random.randrange(0, 7)
        q10 = random.randrange(0, 7)
        q11 = random.randrange(0, 7)
        q12 = random.randrange(0, 7)
        q13 = random.randrange(0, 7)
        q14 = random.randrange(0, 7)
        q15 = random.randrange(0, 7)
        q16 = random.randrange(0, 7)
        q17 = random.randrange(0, 7)
        q18 = random.randrange(0, 7)
        q19 = random.randrange(0, 7)
        q20 = random.randrange(0, 7)
        q21 = random.randrange(0, 7)
        q22 = random.randrange(0, 7)
        q23 = random.randrange(0, 7)
        q24 = random.randrange(0, 7)
        q25 = random.randrange(0, 7)
        q26 = random.randrange(0, 7)
        q27 = random.randrange(0, 7)
        q28 = random.randrange(0, 7)
        q29 = random.randrange(0, 7)
        q30 = random.randrange(0, 7)
        q31 = random.randrange(0, 7)
        q32 = random.randrange(0, 2)
        db = get_db()
        x = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(24))
        while (not obtainedUnique):
            try:
                db.execute(
                    'INSERT INTO stest (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, q21, q22, q23, q24, q25, q26, q27, q28, q29, q30, q31, q32, author_id, username, route, new_tag, guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP)'
                    ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, q21, q22, q23, q24, q25, q26, q27, q28, q29, q30, q31, q32,
                     g.user['id'], g.user['username'], x, 1, -999, -999, -999, -999 )
                )
                db.commit()
                obtainedUnique = True
            except db.IntegrityError:
                obtainedUnique = False
        db.execute(
            'UPDATE stest SET guess_MBTI_EI = ?, guess_MBTI_SN = ?, guess_MBTI_TF = ?, guess_MBTI_JP = ?'
            ' WHERE route = ?',
            (sguesser(x)[0], sguesser(x)[1], sguesser(x)[2], sguesser(x)[3], x)
        )
        db.commit()
    return render_template('/addsample.html')


def sguesser(title):
    db = get_db()
    route = db.execute(
        'SELECT * FROM stest WHERE route = ?', (title,)
    ).fetchone()

    EImeter = -2 * (route['q3'] - 3) + 2 * (route['q15'] - 3) + 2 * (route['q20'] - 3) + (route['q23'] - 3) - (route['q24'] - 3) - (route['q30'] - 3)
    SNmeter = 2 * (route['q2'] - 3) - (route['q5'] - 3) + 2 * (route['q19'] - 3) + (route['q26'] - 3) - (route['q28'] - 3)
    TFmeter = 2 * (route['q21'] - 3) + (route['q27'] - 3) - (route['q29'] - 3) - 2 * (route['q31'] - 3)
    JPmeter = 2 * (route['q1'] - 3) - (route['q7'] - 3) - 2 * (route['q16'] - 3) + (route['q17'] - 3) - (route['q18'] - 3) + (route['q25'] - 3)
    if route['q4'] - 3 > 0:
        TFmeter -= (route['q4'] - 3)
    else:
        TFmeter -= 2 * (route['q4'] - 3)

    if route['q6'] - 3 > 0:
        EImeter -= (route['q6'] - 3)
    else:
        EImeter -= 2 * (route['q6'] - 3)

    if route['q8'] - 3 > 0:
        JPmeter += (route['q8'] - 3)
    else:
        JPmeter += 2 * (route['q8'] - 3)

    if route['q9'] - 3 > 0:
        EImeter -= (route['q9'] - 3)
    else:
        EImeter -= 2 * (route['q9'] - 3)

    if route['q10'] - 3 > 0:
        JPmeter -= (route['q10'] - 3)
    else:
        JPmeter -= 2 * (route['q10'] - 3)

    if route['q11'] - 3 > 0:
        SNmeter -= 2 * (route['q11'] - 3)
    else:
        SNmeter -= (route['q11'] - 3)

    if route['q12'] - 3 > 0:
        EImeter += (route['q12'] - 3)
    else:
        EImeter += 2 * (route['q12'] - 3)

    if route['q13'] - 3 > 0:
        TFmeter += 2 * (route['q13'] - 3)
    else:
        TFmeter += (route['q13'] - 3)

    if not (route['q14'] - 3 > 0):
        SNmeter -= (route['q14'] - 3)

    if route['q22'] - 3 > 0:
        SNmeter += 2 * (route['q22'] - 3)
    else:
        SNmeter += (route['q22'] - 3)

    if route['q32'] == 0:
        SNmeter += 2
    else:
        SNmeter -= 4

    return [EImeter, SNmeter, TFmeter, JPmeter]


def pguesser(title):
    db = get_db()
    route = db.execute(
        'SELECT * FROM ptest WHERE route = ?', (title,)
    ).fetchone()

    EImeter = -2 * (route['q3'] - 3) + 2 * (route['q15'] - 3) + 2 * (route['q20'] - 3) + (route['q23'] - 3) - (route['q24'] - 3) - (route['q30'] - 3)
    SNmeter = 2 * (route['q2'] - 3) - (route['q5'] - 3) + 2 * (route['q19'] - 3) + (route['q26'] - 3) - (route['q28'] - 3)
    TFmeter = 2 * (route['q21'] - 3) + (route['q27'] - 3) - (route['q29'] - 3) - 2 * (route['q31'] - 3)
    JPmeter = 2 * (route['q1'] - 3) - (route['q7'] - 3) - 2 * (route['q16'] - 3) + (route['q17'] - 3) - (route['q18'] - 3) + (route['q25'] - 3)
    if route['q4'] - 3 > 0:
        TFmeter -= (route['q4'] - 3)
    else:
        TFmeter -= 2 * (route['q4'] - 3)

    if route['q6'] - 3 > 0:
        EImeter -= (route['q6'] - 3)
    else:
        EImeter -= 2 * (route['q6'] - 3)

    if route['q8'] - 3 > 0:
        JPmeter += (route['q8'] - 3)
    else:
        JPmeter += 2 * (route['q8'] - 3)

    if route['q9'] - 3 > 0:
        EImeter -= (route['q9'] - 3)
    else:
        EImeter -= 2 * (route['q9'] - 3)

    if route['q10'] - 3 > 0:
        JPmeter -= (route['q10'] - 3)
    else:
        JPmeter -= 2 * (route['q10'] - 3)

    if route['q11'] - 3 > 0:
        SNmeter -= 2 * (route['q11'] - 3)
    else:
        SNmeter -= (route['q11'] - 3)

    if route['q12'] - 3 > 0:
        EImeter += (route['q12'] - 3)
    else:
        EImeter += 2 * (route['q12'] - 3)

    if route['q13'] - 3 > 0:
        TFmeter += 2 * (route['q13'] - 3)
    else:
        TFmeter += (route['q13'] - 3)

    if not (route['q14'] - 3 > 0):
        SNmeter -= (route['q14'] - 3)

    if route['q22'] - 3 > 0:
        SNmeter += 2 * (route['q22'] - 3)
    else:
        SNmeter += (route['q22'] - 3)

    if route['q32'] == 0:
        SNmeter += 2
    else:
        SNmeter -= 4

    return [EImeter, SNmeter, TFmeter, JPmeter]