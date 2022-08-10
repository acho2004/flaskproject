import time

import sqlite3

from mbti_analyzer.main import main

db = sqlite3.connect(
    '../instance/flaskr.sqlite',
    detect_types=sqlite3.PARSE_DECLTYPES,
    isolation_level=None
)
db.row_factory = sqlite3.Row


def keeprunning():
    while True:
        time.sleep(5)

        responses = ""
        users = db.execute(
            'SELECT * FROM hunet_members WHERE updated = 0'
        ).fetchall()

        if len(users) == 0:
            print("EMPTY")
            continue

        for user in users:
            print(user['name'])
            tests = db.execute(f'''SELECT * FROM ptest WHERE target_id = '{user['emp_no']}' ORDER BY created DESC''').fetchall()
            counter = 0
            for test in tests:
                if counter == 3:
                    break
                else:
                    counter += 1
                responses += (test['sresp1'] + " " + test['sresp2'] + " " + test['sresp3'] + " " + test['sresp4'] + " " + test['sresp5'] + " / ")
            print(responses)
            analysis = main(responses, str(user['emp_no']))
            print(analysis)
            #db.execute(
            #    'UPDATE hunet_members SET updated = 1 WHERE emp_no = ?',
            #    (user['emp_no'],)
            #)
            #db.commit()

keeprunning()


