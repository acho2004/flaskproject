import random
import string
from notification import Curl
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from flaskr.auth import login_required
from flaskr.db import get_db


bp = Blueprint('survey', __name__)


@bp.route('/self_test', methods=('GET', 'POST'))
@login_required
def self_test():
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
    return render_template('/self_test.html', questions=questions)


@bp.route('/peer_test', methods=('GET', 'POST'))
@login_required
def peer_test():
    if g.user is None:
        return redirect(url_for('auth.login'))
    db = get_db()
    chosen_questions = []
    eis = db.execute(
        f'''SELECT question_number FROM questionlist WHERE question_worth LIKE 'E%' OR question_worth LIKE 'I%' ''').fetchall()
    sns = db.execute(
        f'''SELECT question_number FROM questionlist WHERE question_worth LIKE 'S%' OR question_worth LIKE 'N%' ''').fetchall()
    tfs = db.execute(
        f'''SELECT question_number FROM questionlist WHERE question_worth LIKE 'T%' OR question_worth LIKE 'F%' ''').fetchall()
    jps = db.execute(
        f'''SELECT question_number FROM questionlist WHERE question_worth LIKE 'J%' OR question_worth LIKE 'P%' ''').fetchall()
    x = 0
    while len(chosen_questions) < 16:
        x = random.randint(1, 39)
        if x in chosen_questions:
            continue
        if len(list(set(chosen_questions) & set(eis))) == 4 and x in eis:
            continue
        if len(list(set(chosen_questions) & set(sns))) == 4 and x in sns:
            continue
        if len(list(set(chosen_questions) & set(tfs))) == 4 and x in tfs:
            continue
        if len(list(set(chosen_questions) & set(jps))) == 4 and x in jps:
            continue

        chosen_questions.append(x)
        print(x)


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

        for i in range(1, 40):
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
                        query2 += "'" + item + "' ,"
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
            try:
                Curl().curl_request(
                    url="https://h-support.hunet.name/api/webhook",
                    request_type="POST",
                    json_info={
                        "targets": [t_emp_no],
                        "message": "누군가 나의 MBTI를 평가해 줬네요! 아래의 링크를 통해서 확인해 보세요. \n https://mbti.hunet.name"
                    }
                )
            except Exception as e:
                print(e)

            return redirect(url_for('index'))

    return render_template('/peer_test.html', deptlist=deptlist, people=people, questions=questions, chosen_questions=chosen_questions)


@bp.route('/add_sample', methods=('GET', 'POST'))
@login_required
def add_sample():
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
    return render_template('/add_sample.html')


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

                    query += 'author_emp_no, route, new_tag_testee, new_tag_tester, '
                    query += 'guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP, target_emp_no)'
                    query2 += "'" + str(g.user['emp_no']) + "', '" + x + "', '1', '1', '-999', '-999', " \
                                                                         "'-999', '-999', '" + str(t_emp_no) + "')"
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
    return render_template('/add_peer_sample.html')


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


