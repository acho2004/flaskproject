from flask import (
    Response, Blueprint, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.db import get_db


bp = Blueprint('result_handler', __name__)


@bp.route("/results/self/<string:title>")
def show_self_test(title: str):
    db = get_db()
    questions = db.execute('SELECT * FROM questionlist')
    route = db.execute(
        'SELECT * FROM stest WHERE route = ?', (title,)
    ).fetchone()
    tester = db.execute(
        'SELECT name FROM hunet_members WHERE emp_no = ?', (route['author_emp_no'],)
    ).fetchone()
    if route is None:
        abort(404)
    if (not (g.user is None)) and str(route['author_emp_no']) == str(g.user['emp_no']):
        db.execute(
            'UPDATE stest SET new_tag = ?'
            ' WHERE id = ?',
            (0, route['id'])
        )
        db.commit()
        return render_template('view_self_result.html', route=route, tester=tester, questions=questions)
    return redirect("/")


@bp.route("/update_testee", methods=['POST'])
def update_testee_viewed_tag():
    """MARKS A PEER TEST AS VIEWED BY THE TEST RECEIVER"""
    db = get_db()
    user = request.form.to_dict()

    db.execute(f'''UPDATE ptest SET new_tag_testee = 0 WHERE id = {user['data']}''')
    db.commit()
    response = Response(status=200)
    return response


@bp.route("/update_tester", methods=['POST'])
def update_tester_viewed_tag():
    """MARKS A PEER TEST AS VIEWED BY THE TEST TAKER"""
    db = get_db()
    temp = request.form.to_dict()

    db.execute(f'''UPDATE ptest SET new_tag_tester = 0 WHERE id = {temp['data']}''')
    db.commit()
    response = Response(status=200)
    return response


@bp.route('/self_results')
def display_self_results():
    if g.user is None:
        return redirect(url_for('auth.login'))
    db = get_db()
    selfassessments = db.execute(
        'SELECT created, author_emp_no, route, new_tag,' 
        ' guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP'
        ' FROM stest'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('/self_results.html',
                           selfassessments=list(map(lambda row: dict(row), selfassessments)))


@bp.route('/results_by_me')
def display_peer_tests_by_me():
    if g.user is None:
        return redirect(url_for('auth.login'))
    db = get_db()
    peerassessments = db.execute(
        'SELECT created, author_emp_no, target_emp_no, id, route, new_tag_tester,' 
        ' guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP'
        ' FROM ptest'
        ' ORDER BY created DESC'
    ).fetchall()
    testee = []
    for item in peerassessments:
        testee.append(db.execute('SELECT name FROM hunet_members WHERE emp_no = ?', (item['target_emp_no'],)).fetchone())
    return render_template('/results_by_me.html',
                           peerassessments=list(map(lambda row: dict(row), peerassessments)), testee=testee)


@bp.route('/results_for_me')
def display_peer_tests_for_me():
    if g.user is None:
        return redirect(url_for('auth.login'))
    db = get_db()
    peerassessments = db.execute(
        'SELECT created, author_emp_no, target_emp_no, id, route, new_tag_testee,'
        ' guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP'
        ' FROM ptest'
        ' ORDER BY created DESC'
    ).fetchall()
    tester = []
    for item in peerassessments:
        tester.append(db.execute('SELECT name FROM hunet_members WHERE emp_no = ?', (item['author_emp_no'],)).fetchone())
    return render_template('/results_for_me.html',
                           peerassessments=list(map(lambda row: dict(row), peerassessments)), tester=tester)