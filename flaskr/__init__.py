import os
from flask import Flask
from flask import g
from flask import render_template
from flask import redirect
from flask import url_for


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
    def home():
        return render_template('home.html')

    @app.route('/index')
    def index():
        if g.user is None:
            return redirect(url_for('home'))
        db = auth.get_db()
        selfassessments = db.execute(
            'SELECT author_id, guess_MBTI_EI, guess_MBTI_SN, guess_MBTI_TF, guess_MBTI_JP'
            ' FROM stest'
            ' ORDER BY created DESC'
        ).fetchall()
        found = False
        selfguess = ""
        for x in selfassessments:
            if(str(x[0]) == str(g.user['emp_no'])):
                found = True
                break
        if not found:
            selfguess = "N/A"
        else:
            selfguess = selfguess + "E" if x[1] > 0 else selfguess + "I"
            selfguess = selfguess + "S" if x[2] > 0 else selfguess + "N"
            selfguess = selfguess + "T" if x[3] > 0 else selfguess + "F"
            selfguess = selfguess + "J" if x[4] > 0 else selfguess + "P"


        return render_template('index.html', selfguess=selfguess)

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import questionaire
    app.register_blueprint(questionaire.bp)

    return app
