import os
from flask import Flask
from flask import g
from flask import render_template
from flask import redirect
from flask import url_for
import time
import threading


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

    # a simple page that says hello

    @app.route('/')
    def index():
        if g.user is None:
            return redirect(url_for('auth.login'))
        db = auth.get_db()
        selfassessments = db.execute(
            'SELECT author_id, guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP, new_tag'
            ' FROM stest WHERE author_id = ?'
            ' ORDER BY created DESC', (g.user['emp_no'],)
        ).fetchall()
        peerassessments = db.execute(
            'SELECT target_id, guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP'
            ' FROM ptest WHERE target_id = ?'
            ' ORDER BY created DESC', (g.user['emp_no'],)
        ).fetchall()
        selfguess = ""
        peerguess = ""
        sumE = 0
        sumS = 0
        sumT = 0
        sumJ = 0

        if len(selfassessments) == 0:
            selfguess = "N/A"
        else:
            selfguess = selfguess + "E" if selfassessments[0][1] > 2.5 else selfguess + "I"
            selfguess = selfguess + "S" if selfassessments[0][2] > 2.5 else selfguess + "N"
            selfguess = selfguess + "T" if selfassessments[0][3] > 2.5 else selfguess + "F"
            selfguess = selfguess + "J" if selfassessments[0][4] > 2.5 else selfguess + "P"

        if len(peerassessments) == 0:
            peerguess = "N/A"
        else:
            counter = 0
            for item in peerassessments:
                if counter == 5:
                    break
                counter+=1
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


        return render_template('index.html', selfassessments=selfassessments, selfguess=selfguess, peerguess=peerguess)

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import questionaire
    app.register_blueprint(questionaire.bp)



    return app