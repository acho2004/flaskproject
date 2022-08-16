import os
from flask import Flask
from flask import g
from flask import render_template
from flask import redirect
from flask import url_for
from pathlib import Path


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True, static_folder='./static/',static_url_path='')

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        if g.user is None:
            return redirect(url_for('auth.login'))
        path = Path("../../flaskr/static/output/" + g.user['emp_no'] + "_radarchart.png")
        imageExists = path.is_file()
        db = auth.get_db()
        self_tests = db.execute(
            'SELECT author_emp_no, guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP, new_tag'
            ' FROM stest WHERE author_emp_no = ?'
            ' ORDER BY created DESC', (g.user['emp_no'],)
        ).fetchall()
        peer_tests = db.execute(
            'SELECT target_emp_no, guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP'
            ' FROM ptest WHERE target_emp_no = ?'
            ' ORDER BY created DESC', (g.user['emp_no'],)
        ).fetchall()
        selfguess = ""
        peerguess = ""
        sumE = 0
        sumS = 0
        sumT = 0
        sumJ = 0

        if len(self_tests) == 0:
            selfguess = "결과 없음"
        else:
            selfguess = selfguess + "E" if self_tests[0][1] > 2.5 else selfguess + "I"
            selfguess = selfguess + "S" if self_tests[0][2] > 2.5 else selfguess + "N"
            selfguess = selfguess + "T" if self_tests[0][3] > 2.5 else selfguess + "F"
            selfguess = selfguess + "J" if self_tests[0][4] > 2.5 else selfguess + "P"

        if len(peer_tests) == 0:
            peerguess = "결과 없음"
        else:
            counter = 0
            for item in peer_tests:
                if counter == 5:
                    break
                counter += 1
                sumE += item['guess_MBTI_EI']
                sumS += item['guess_MBTI_SN']
                sumT += item['guess_MBTI_TF']
                sumJ += item['guess_MBTI_JP']
            sumE /= counter
            sumS /= counter
            sumT /= counter
            sumJ /= counter
            peerguess = peerguess + "E" if sumE > 2.5 else peerguess + "I"
            peerguess = peerguess + "S" if sumS > 2.5 else peerguess + "N"
            peerguess = peerguess + "T" if sumT > 2.5 else peerguess + "F"
            peerguess = peerguess + "J" if sumJ > 2.5 else peerguess + "P"

        return render_template('index.html', selfguess=selfguess, peerguess=peerguess, imageExists=imageExists)

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import survey
    app.register_blueprint(survey.bp)

    from . import result_handler
    app.register_blueprint(result_handler.bp)

    return app