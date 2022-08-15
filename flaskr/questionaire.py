import random, string

from flask import (
    Response, Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db


bp = Blueprint('questionaire', __name__)


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
        return render_template('viewselfresult.html', route=route, tester=tester, questions=questions)
    return redirect("/")


@bp.route("/update_testee", methods=['POST'])
def update_testee_viewed_tag():
    """MARKS A PEER TEST AS VIEWED BY THE TEST RECEIVER"""
    db = get_db()
    user = request.form.to_dict()

    db.execute(f'''UPDATE ptest SET new_tag_testee = 0 WHERE id = {user['data']}''')
    db.commit()
    print("HELLO")
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
    return render_template('/selfresults.html',
                           selfassessments=list(map(lambda row: dict(row), selfassessments)))

@bp.route('/results_by_me')
def display_peertests_by_me():
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
    return render_template('/resultsbyme.html',
                           peerassessments=list(map(lambda row: dict(row), peerassessments)), testee=testee)


@bp.route('/results_for_me')
def display_peertests_for_me():
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
    return render_template('/resultsforme.html',
                           peerassessments=list(map(lambda row: dict(row), peerassessments)), tester=tester)


@bp.route('/self_test', methods=('GET', 'POST'))
@login_required
def selftest():
    if g.user is None:
        return redirect(url_for('auth.login'))
    db = get_db()
    questions = db.execute('SELECT * FROM questionlist').fetchall()
    if request.method == 'POST':
        got_unique = False
        answers = []
        for i in range(1, 40):
            answers.append(request.form["q" + str(i)])

        x = ""
        error = None

        
        for i in range(0, 39):
            if not answers[i]:
                error = 'All questions are required.'

        if error is not None:
            flash(error)
        else:
            while not got_unique:
                try:
                    x = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(24))
                    query = "INSERT INTO stest ("
                    query2 = "VALUES ("
                    counter = 1
                    for item in answers:
                        query += 'q' + str(counter) + ', '
                        query2 += "'" + item + "' ,"
                        counter += 1

                    query += 'author_emp_no, route, new_tag, guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF,'
                    query += ' guess_MBTI_JP)'
                    query2 += "'" + str(g.user['emp_no']) + "', '" + x + "', '1', '-999', '-999', '-999', '-999')"
                    query += query2
                    db.execute(query)
                    db.commit()
                    got_unique = True
                except db.IntegrityError:
                    got_unique = False
            db.execute(
                'UPDATE stest SET guess_MBTI_EI = ?, guess_MBTI_SN = ?, guess_MBTI_TF = ?, guess_MBTI_JP = ?'
                ' WHERE route = ?',
                (mbti_grader(x, "self")[0], mbti_grader(x, "self")[1], mbti_grader(x, "self")[2],
                    mbti_grader(x, "self")[3], x)
            )
            db.commit()
            return redirect(url_for('index'))
    return render_template('/stest.html', questions=questions)


@bp.route('/peer_test', methods=('GET', 'POST'))
@login_required
def peertest():
    if g.user is None:
        return redirect(url_for('auth.login'))
    db = get_db()
    questions = db.execute('SELECT * FROM questionlist').fetchall()
    people = db.execute(
        'SELECT name, emp_no, dept_name'
        ' FROM hunet_members'
    ).fetchall()
    deptlist = []
    for item in people:
        if item['dept_name'] not in deptlist:
            deptlist.append(item['dept_name'])

    if request.method == 'POST':
        got_unique = False
        answers = []
        for i in range (1,40):
            answers.append(request.form["q" + str(i)])

        sresp1 = request.form['sresp1']
        sresp2 = request.form['sresp2']
        sresp3 = request.form['sresp3']
        sresp4 = request.form['sresp4']
        sresp5 = request.form['sresp5']
        x = ""

        t_emp_no = (request.form['name'].split())[1]

        error = None

        for i in range(0,39):
            if not answers[i]:
                error = 'All questions are required.'

        if not sresp1 or not sresp2 or not sresp3 or not sresp4 or not sresp5 or not t_emp_no:
            error = 'All questions are required.'

        if t_emp_no == g.user['emp_no']:
            error = "자기 자신을 테스트 하시려면 '나를 위한 시험지' 를 사용해주세요."



        if error is not None:
            flash(error)
        else:
            db.execute(
                'UPDATE hunet_members SET updated = 0 WHERE emp_no = ?',
                (t_emp_no,)
            )
            db.commit()
            d = db.execute(
                'SELECT * FROM hunet_members WHERE emp_no = ?',
                (t_emp_no,)
            ).fetchone()
            print(d['updated'])
            while not got_unique:
                try:
                    x = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(24))

                    query = "INSERT INTO ptest ("
                    query2 = "VALUES ("
                    counter = 1
                    for item in answers:
                        query += 'q' + str(counter) + ', '
                        query2 += "'"  + item + "' ,"
                        counter += 1

                    query += 'sresp1, sresp2, sresp3, sresp4, sresp5, author_emp_no, target_emp_no, route,'
                    query += 'new_tag_tester, new_tag_testee, guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF,'
                    query += ' guess_MBTI_JP)'
                    query2 += "'" + sresp1.replace("'", '').replace("/", '').rstrip('\n') + "', '" + \
                        sresp2.replace("'", '').replace("/", '').rstrip('\n') + "', '" + \
                        sresp3.replace("'", '').replace("/", '').rstrip('\n') + "', '" + \
                        sresp4.replace("'", '').replace("/", '').rstrip('\n') + "', '" + \
                        sresp5.replace("'", '').replace("/", '').rstrip('\n') \
                        + "', '" + str(g.user['emp_no']) + "', '" + t_emp_no + "', '" + x + \
                        "', '1', '1', '-999', '-999', '-999', '-999')"
                    query += query2
                    db.execute(query)
                    db.commit()
                    got_unique = True

                except db.IntegrityError:
                    got_unique = False
            db.execute(
                'UPDATE ptest SET guess_MBTI_EI = ?, guess_MBTI_SN = ?, guess_MBTI_TF = ?, guess_MBTI_JP = ?'
                ' WHERE route = ?',
                (mbti_grader(x, "peer")[0], mbti_grader(x, "peer")[1], mbti_grader(x, "peer")[2], mbti_grader(x, "peer")[3], x)
            )
            db.commit()

            return redirect(url_for('index'))

    return render_template('/ptest.html', deptlist=deptlist, people=people, questions=questions)


@bp.route('/add_sample', methods=('GET', 'POST'))
@login_required
def addsample():
    if g.user is None:
        return redirect(url_for('auth.login'))
    db = get_db()
    questions = db.execute('SELECT * FROM questionlist').fetchall()
    if request.method == 'POST':
        got_unique = False
        answers = []
        for question in questions:
            if question['self_test_question'] == ".":
                continue
            if question['question_worth'][0] == "D":
                answers.append(random.randrange(0, 2))
            else:answers.append(random.randrange(0, 7))

        while not got_unique:
            try:
                x = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(24))
                query = "INSERT INTO stest ("
                query2 = "VALUES ("
                counter = 1

                for item in answers:
                    query += 'q' + str(counter) + ', '
                    query2 += "'" + str(item) + "' ,"
                    counter += 1

                query += 'author_emp_no, route, new_tag, guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP)'
                query2 += "'" + str(g.user['emp_no']) + "', '" + x + "', '1', '-999', '-999', '-999', '-999')"
                query += query2
                db.execute(query)
                db.commit()
                got_unique = True
            except db.IntegrityError:
                got_unique = False
        db.execute(
            'UPDATE stest SET guess_MBTI_EI = ?, guess_MBTI_SN = ?, guess_MBTI_TF = ?, guess_MBTI_JP = ?'
            ' WHERE route = ?',
            (mbti_grader(x, "self")[0], mbti_grader(x, "self")[1], mbti_grader(x, "self")[2],
                mbti_grader(x, "self")[3], x)
        )
        db.commit()
    return render_template('/addsample.html')


@bp.route('/add_peer_sample', methods=('GET', 'POST'))
@login_required
def add_peer_sample():
    if g.user is None:
        return redirect(url_for('auth.login'))
    db = get_db()
    questions = db.execute('SELECT * FROM questionlist').fetchall()


    if request.method == 'POST':
        got_unique = False
        answers = []
        for question in questions:
            if question['self_test_question'] == ".":
                answers.append(request.form[question['question_number']])
            if question['question_worth'][0] == "D":
                answers.append(random.randrange(0, 2))
            else:
                answers.append(random.randrange(0, 7))

        t_emp_no = request.form["t_emp_no"]
        d = db.execute(
            'SELECT * FROM hunet_members WHERE emp_no = ?',
            (t_emp_no,)
        ).fetchone()
        error = None
        if t_emp_no == g.user['emp_no']:
            error = "자기 자신을 테스트 하시려면 '나를 위한 시험지' 를 사용해주세요."
        if d is None:
            error = "주어진 사원 아이디를 가진 사원은 없습니다."
        if error is not None:
            flash(error)
        else:
            while not got_unique:
                try:
                    x = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(24))
                    query = "INSERT INTO ptest ("
                    query2 = "VALUES ("
                    counter = 1
                    sresp_counter = 0
                    for question in questions:
                        if question['self_test_question'] == ".":
                            query2 += "'" + str(answers[counter - sresp_counter - 1]) + "' ,"
                            query += question['question_number'] + ', '
                            sresp_counter += 1
                        else:
                            query += 'q' + str(counter - sresp_counter) + ', '
                            query2 += "'" + str(answers[counter - sresp_counter - 1]) + "' ,"
                        counter += 1


                    query += 'author_emp_no, route, new_tag_testee, new_tag_tester, guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP, target_emp_no)'
                    query2 += "'" + str(g.user['emp_no']) + "', '" + x + "', '1', '1', '-999', '-999', '-999', '-999', '" + str(t_emp_no) + "')"
                    query += query2
                    db.execute(query)
                    db.commit()
                    got_unique = True
                except db.IntegrityError:
                    got_unique = False
            db.execute(
                'UPDATE ptest SET guess_MBTI_EI = ?, guess_MBTI_SN = ?, guess_MBTI_TF = ?, guess_MBTI_JP = ?'
                ' WHERE route = ?',
                (mbti_grader(x, "peer")[0], mbti_grader(x, "peer")[1], mbti_grader(x, "peer")[2],
                    mbti_grader(x, "peer")[3], x)
            )
            db.commit()
            db.execute(
                'UPDATE hunet_members SET updated = 0 WHERE emp_no = ?',
                (t_emp_no,)
            )
            db.commit()
    return render_template('/addsample_p.html')


def mbti_grader(pathway, target):
    db = get_db()
    questions = db.execute('SELECT * FROM questionlist').fetchall()
    if target == "self":
        route = db.execute(
            'SELECT * FROM stest WHERE route = ?', (pathway,)
        ).fetchone()
    else:
        route = db.execute(
            'SELECT * FROM ptest WHERE route = ?', (pathway,)
        ).fetchone()
    counter = 0

    EItotal = 0
    SNtotal = 0
    TFtotal = 0
    JPtotal = 0

    EImeter = 0
    SNmeter = 0
    TFmeter = 0
    JPmeter = 0

    for question in questions:
        counter += 1
        if question['self_test_question'] == ".":
            counter -= 1
            continue
        if question['question_worth'][0] == 'E':
            EImeter -= int(question['question_worth'][1]) * (float(route['q' + str(counter)]) - 3)
            EItotal += int(question['question_worth'][1])
        elif question['question_worth'][0] == 'I':
            EImeter += int(question['question_worth'][1]) * (float(route['q' + str(counter)]) - 3)
            EItotal += int(question['question_worth'][1])
        elif question['question_worth'][0] == 'S':
            SNmeter -= int(question['question_worth'][1]) * (float(route['q' + str(counter)]) - 3)
            SNtotal += int(question['question_worth'][1])
        elif question['question_worth'][0] == 'N':
            SNmeter += int(question['question_worth'][1]) * (float(route['q' + str(counter)]) - 3)
            SNtotal += int(question['question_worth'][1])
        elif question['question_worth'][0] == 'T':
            TFmeter -= int(question['question_worth'][1]) * (float(route['q' + str(counter)]) - 3)
            TFtotal += int(question['question_worth'][1])
        elif question['question_worth'][0] == 'F':
            TFmeter += int(question['question_worth'][1]) * (float(route['q' + str(counter)]) - 3)
            TFtotal += int(question['question_worth'][1])
        elif question['question_worth'][0] == 'J':
            JPmeter -= int(question['question_worth'][1]) * (float(route['q' + str(counter)]) - 3)
            JPtotal += int(question['question_worth'][1])
        elif question['question_worth'][0] == 'P':
            JPmeter += int(question['question_worth'][1]) * (float(route['q' + str(counter)]) - 3)
            JPtotal += int(question['question_worth'][1])
        elif question['question_worth'][0] == 'D':
            if question['question_worth'][1] == 'E':
                EItotal += 1
                EImeter -= 2 * (float(route['q' + str(counter)]) - .5)
            elif question['question_worth'][1] == 'I':
                EItotal += 1
                EImeter += 2 * (float(route['q' + str(counter)]) - .5)
            elif question['question_worth'][1] == 'S':
                SNtotal += 1
                SNmeter -= 2 * (float(route['q' + str(counter)]) - .5)
            elif question['question_worth'][1] == 'N':
                SNtotal += 1
                SNmeter += 2 * (float(route['q' + str(counter)]) - .5)
            elif question['question_worth'][1] == 'T':
                TFtotal += 1
                TFmeter -= 2 * (float(route['q' + str(counter)]) - .5)
            elif question['question_worth'][1] == 'F':
                TFtotal += 1
                TFmeter += 2 * (float(route['q' + str(counter)]) - .5)
            elif question['question_worth'][1] == 'J':
                JPtotal += 1
                JPmeter -= 2 * (float(route['q' + str(counter)]) - .5)
            elif question['question_worth'][1] == 'P':
                JPtotal += 1
                JPmeter += 2 * (float(route['q' + str(counter)]) - .5)


    EImeter += EItotal * 3
    EImeter = 5 * EImeter / (EItotal * 6)
    SNmeter += SNtotal * 3
    SNmeter = 5 * SNmeter / (SNtotal * 6)
    TFmeter += TFtotal * 3
    TFmeter = 5 * TFmeter / (TFtotal * 6)
    JPmeter += JPtotal * 3
    JPmeter = 5 * JPmeter / (JPtotal * 6)

    return [EImeter, SNmeter, TFmeter, JPmeter]


