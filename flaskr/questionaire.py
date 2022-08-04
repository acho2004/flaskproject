import sys
import random
import string
from flask_json import FlaskJSON, JsonError, json_response, as_json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('questionaire', __name__)

@bp.route("/results/self/<string:title>")
def display_spost(title: str):
    db = get_db()
    route = db.execute(
        'SELECT * FROM stest WHERE route = ?', (title,)
    ).fetchone()
    tester = db.execute(
        'SELECT name FROM hunet_members WHERE id = ?', (route['author_id'],)
    ).fetchone()
    if route is None:
        abort(404)
    if (not (g.user is None)) and str(route['author_id']) == str(g.user['emp_no']):
        db.execute(
            'UPDATE stest SET new_tag = ?'
            ' WHERE id = ?',
            (0, route['id'])
        )
        db.commit()
    return render_template('sresults.html', route=route, tester=tester)


@bp.route("/results/peer/<string:title>")
def display_ppost(title: str):
    db = get_db()
    route = db.execute(
        'SELECT * FROM ptest WHERE route = ?', (title,)
    ).fetchone()
    tester = db.execute(
        'SELECT name FROM hunet_members WHERE emp_no = ?', (route['author_id'],)
    ).fetchone()
    testee = db.execute(
        'SELECT name FROM hunet_members WHERE emp_no = ?', (route['target_id'],)
    ).fetchone()
    error = None
    if route is None:
        abort(404)
    if testee is None:
        error = "There is no account associated with the email this test is targetted for."
    if not (g.user is None) and str(route['target_id']) == str(g.user['emp_no']):
        db.execute(
            'UPDATE ptest SET new_tagp = ?'
            ' WHERE id = ?',
            (0, route['id'])
        )
        db.commit()
    if not (g.user is None) and str(route['author_id']) == str(g.user['emp_no']):
        db.execute(
            'UPDATE ptest SET new_tags = ?'
            ' WHERE id = ?',
            (0, route['id'])
        )
        db.commit()
    if error is None:
        return render_template('presults.html', route=route, tester=tester, testee=testee)
    else:
        flash(error)
        return redirect(url_for('home'))



@bp.route('/srlist')
def srlist():
    if g.user is None:
        return redirect(url_for('auth.login'))
    db = get_db()
    selfassessments = db.execute(
        'SELECT created, author_id, route, new_tag,' 
        ' guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP'
        ' FROM stest'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('/srlist.html',
                           selfassessments=list(map(lambda row: dict(row), selfassessments)))

@bp.route('/pslist')
def pslist():
    if g.user is None:
        return redirect(url_for('auth.login'))
    db = get_db()
    peerassessments = db.execute(
        'SELECT created, author_id, target_id, id, route, new_tags,' 
        ' guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP'
        ' FROM ptest'
        ' ORDER BY created DESC'
    ).fetchall()
    testee = []
    for item in peerassessments:
        testee.append(db.execute('SELECT name FROM hunet_members WHERE emp_no = ?', (item['target_id'],)).fetchone())
    return render_template('/pslist.html',
                           peerassessments=list(map(lambda row: dict(row), peerassessments)), testee=testee)

@bp.route('/splist')
def splist():
    if g.user is None:
        return redirect(url_for('auth.login'))
    db = get_db()
    peerassessments = db.execute(
        'SELECT created, author_id, target_id, id, route, new_tagp,'
        ' guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP'
        ' FROM ptest'
        ' ORDER BY created DESC'
    ).fetchall()
    tester = []
    for item in peerassessments:
        tester.append(db.execute('SELECT name FROM hunet_members WHERE emp_no = ?', (item['author_id'],)).fetchone())
    return render_template('/splist.html',
                           peerassessments=list(map(lambda row: dict(row), peerassessments)), tester=tester)




@bp.route('/selftest', methods=('GET', 'POST'))
@login_required
def selftest():
    if g.user is None:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':

        obtainedUnique = False
        questions = []
        for i in range(1,40):
            questions.append(request.form["q" + str(i)])

        x = ""
        error = None
        db = get_db()
        for i in range(0,39):
            if not questions[i]:
                error = 'All questions are required.'

        if error is not None:
            flash(error)
        else:
            while (not obtainedUnique):
                try:
                    x = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(24))
                    query = "INSERT INTO stest ("
                    query2 = "VALUES ("
                    counter = 1
                    for item in questions:
                        query += 'q' + str(counter) + ', '
                        query2 += "'"  + item + "' ,"
                        counter += 1

                    query += 'author_id, route, new_tag, guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP)'
                    query2 += "'" + str(g.user['emp_no']) + "', '" + x + "', '1', '-999', '-999', '-999', '-999')"
                    query += query2
                    db.execute(query)
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
            return redirect(url_for('index'))
    return render_template('/stest.html')



@bp.route('/peertest', methods=('GET', 'POST'))
@login_required
def peertest():
    if g.user is None:
        return redirect(url_for('auth.login'))
    db = get_db()
    people = db.execute(
        'SELECT name, emp_no, dept_name'
        ' FROM hunet_members'
    ).fetchall()
    deptlist = []
    for item in people:
        if item['dept_name'] not in deptlist:
            deptlist.append(item['dept_name'])


    if request.method == 'POST':
        obtainedUnique = False
        questions = []
        for i in range (1,40):
            questions.append(request.form["q" + str(i)])

        sresp1 = request.form['sresp1']
        sresp2 = request.form['sresp2']
        sresp3 = request.form['sresp3']
        sresp4 = request.form['sresp4']
        sresp5 = request.form['sresp5']
        x = ""

        target_id = request.form['target_id']
        error = None

        for i in range(0,39):
            if not questions[i]:
                error = 'All questions are required.'

        if not sresp1 or not sresp2 or not sresp3 or not sresp4 or not sresp5 or not target_id:
            error = 'All questions are required.'

        if target_id == g.user['emp_no']:
            error = "You can't submit a form for yourself."

        if error is not None:
            flash(error)
        else:
            while (not obtainedUnique):
                try:
                    x = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(24))

                    query = "INSERT INTO ptest ("
                    query2 = "VALUES ("
                    counter = 1
                    for item in questions:
                        query += 'q' + str(counter) + ', '
                        query2 += "'"  + item + "' ,"
                        counter += 1

                    query += 'sresp1, sresp2, sresp3, sresp4, sresp5, author_id, target_id, route, new_tags,'
                    query += 'new_tagp, guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP)'
                    query2 += "'" +sresp1 + "', '" + sresp2 + "', '" + sresp3 + "', '" + sresp4 + "', '" + sresp5 \
                    + "', '" + str(g.user['emp_no']) + "', '" + target_id + "', '" + x + \
                    "', '1', '1', '-999', '-999', '-999', '-999')"
                    query += query2
                    db.execute(query)
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
            return redirect(url_for('index'))

    return render_template('/ptest.html', deptlist=deptlist, people=people)


@bp.route('/addsample', methods=('GET', 'POST'))
@login_required
def addsample():
    if g.user is None:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        obtainedUnique = False
        questions = []
        for i in range (0,38):
            questions.append(random.randrange(0, 7))
        questions.append(random.randrange(0, 2))
        db = get_db()
        while (not obtainedUnique):
            try:
                x = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(24))
                query = "INSERT INTO stest ("
                query2 = "VALUES ("
                counter = 1
                for item in questions:
                    query += 'q' + str(counter) + ', '
                    query2 += "'" + str(item) + "' ,"
                    counter += 1

                query += 'author_id, route, new_tag, guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP)'
                query2 += "'" + str(g.user['emp_no']) + "', '" + x + "', '1', '-999', '-999', '-999', '-999')"
                query += query2
                db.execute(query)
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

    EImeter = -2 * (route['q3'] - 3) + 2 * (route['q15'] - 3) + 2 * (route['q20'] - 3) + (route['q23'] - 3) - \
    (route['q24'] - 3) - (route['q30'] - 3) - (route['q36'] - 3) - (route['q38'] - 3)
    SNmeter = 2 * (route['q2'] - 3) - (route['q5'] - 3) + 2 * (route['q19'] - 3) + (route['q26'] - 3) - \
    (route['q28'] - 3)
    TFmeter = 2 * (route['q21'] - 3) + (route['q27'] - 3) - (route['q29'] - 3) - 2 * (route['q31'] - 3) - \
    (route['q33'] - 3) + (route['q34'] - 3) - (route['q35'] - 3)
    JPmeter = 2 * (route['q1'] - 3) - (route['q7'] - 3) - 2 * (route['q16'] - 3) + (route['q17'] - 3) - \
    (route['q18'] - 3) + (route['q25'] - 3) + (route['q32'] - 3) + (route['q37'] - 3)
    TFmeter = TFmeter - (route['q4'] - 3) if route['q4'] - 3 > 0 else TFmeter - 2 * (route['q4'] - 3)
    EImeter = EImeter - (route['q6'] - 3) if route['q6'] - 3 > 0 else EImeter - 2 * (route['q6'] - 3)
    JPmeter = JPmeter + (route['q8'] - 3) if route['q8'] - 3 > 0 else JPmeter + 2 * (route['q8'] - 3)
    EImeter = EImeter - (route['q9'] - 3) if route['q9'] - 3 > 0 else EImeter - 2 * (route['q9'] - 3)
    JPmeter = JPmeter - (route['q10'] - 3) if route['q10'] - 3 > 0 else JPmeter - 2 * (route['q10'] - 3)
    SNmeter = SNmeter - 2 * (route['q11'] - 3) if route['q11'] - 3 > 0 else SNmeter - (route['q11'] - 3)
    EImeter = EImeter + (route['q12'] - 3) if route['q12'] - 3 > 0 else EImeter + 2 * (route['q12'] - 3)
    TFmeter = TFmeter + 2 * (route['q13'] - 3) if route['q13'] - 3 > 0 else TFmeter + (route['q13'] - 3)
    SNmeter = SNmeter + 2 * (route['q22'] - 3) if route['q22'] - 3 > 0 else SNmeter + (route['q22'] - 3)
    SNmeter = SNmeter + 2 if route['q39'] == 0 else SNmeter - 4

    if not (route['q14'] - 3 > 0):
        SNmeter -= (route['q14'] - 3)

    return [EImeter, SNmeter, TFmeter, JPmeter]


def pguesser(title):
    db = get_db()
    route = db.execute(
        'SELECT * FROM ptest WHERE route = ?', (title,)
    ).fetchone()

    EImeter = -2 * (route['q3'] - 3) + 2 * (route['q15'] - 3) + 2 * (route['q20'] - 3) + (route['q23'] - 3) - \
    (route['q24'] - 3) - (route['q30'] - 3) - (route['q36'] - 3) - (route['q38'] - 3)
    SNmeter = 2 * (route['q2'] - 3) - (route['q5'] - 3) + 2 * (route['q19'] - 3) + (route['q26'] - 3) - \
    (route['q28'] - 3)
    TFmeter = 2 * (route['q21'] - 3) + (route['q27'] - 3) - (route['q29'] - 3) - 2 * (route['q31'] - 3) - \
    (route['q33'] - 3) + (route['q34'] - 3) - (route['q35'] - 3)
    JPmeter = 2 * (route['q1'] - 3) - (route['q7'] - 3) - 2 * (route['q16'] - 3) + (route['q17'] - 3) - \
    (route['q18'] - 3) + (route['q25'] - 3) + (route['q32'] - 3) + (route['q37'] - 3)
    TFmeter = TFmeter - (route['q4'] - 3) if route['q4'] - 3 > 0 else TFmeter - 2 * (route['q4'] - 3)
    EImeter = EImeter - (route['q6'] - 3) if route['q6'] - 3 > 0 else EImeter - 2 * (route['q6'] - 3)
    JPmeter = JPmeter + (route['q8'] - 3) if route['q8'] - 3 > 0 else JPmeter + 2 * (route['q8'] - 3)
    EImeter = EImeter - (route['q9'] - 3) if route['q9'] - 3 > 0 else EImeter - 2 * (route['q9'] - 3)
    JPmeter = JPmeter - (route['q10'] - 3) if route['q10'] - 3 > 0 else JPmeter - 2 * (route['q10'] - 3)
    SNmeter = SNmeter - 2 * (route['q11'] - 3) if route['q11'] - 3 > 0 else SNmeter - (route['q11'] - 3)
    EImeter = EImeter + (route['q12'] - 3) if route['q12'] - 3 > 0 else EImeter + 2 * (route['q12'] - 3)
    TFmeter = TFmeter + 2 * (route['q13'] - 3) if route['q13'] - 3 > 0 else TFmeter + (route['q13'] - 3)
    SNmeter = SNmeter + 2 * (route['q22'] - 3) if route['q22'] - 3 > 0 else SNmeter + (route['q22'] - 3)
    SNmeter = SNmeter + 2 if route['q39'] == 0 else SNmeter - 4

    return [EImeter, SNmeter, TFmeter, JPmeter]