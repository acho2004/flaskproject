import time

import sqlite3

db = sqlite3.connect(
    '../instance/flaskr.sqlite',
    detect_types=sqlite3.PARSE_DECLTYPES,
    isolation_level=None
)
db.row_factory = sqlite3.Row


def keeprunning():
    while True:
        time.sleep(5)

        x = ""
        users = db.execute(
            'SELECT * FROM hunet_members WHERE updated = 0'
        ).fetchall()
        if len(users) == 0:
            print("EMPTY")
            continue

        for user in users:

            print(user['name'])
            tests = db.execute(f'''SELECT * FROM ptest WHERE target_id = '{user['emp_no']}' ''')

            for test in tests:
                x += (test['sresp1'] + " " + test['sresp2'] + " " + test['sresp3'] + " " + test['sresp4'] + " " + test['sresp5'] + " / ")
            print(x)

keeprunning()


