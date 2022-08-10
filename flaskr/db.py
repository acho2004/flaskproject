import click
from flask import current_app, g
from flask.cli import with_appcontext
import sqlite3
from werkzeug.security import generate_password_hash
import os, shutil
from os.path import exists

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES,
            isolation_level = None
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    for filename in os.listdir(os.getcwd() + "/flaskr/static/output"):
        file_path = os.path.join(os.getcwd() + "/flaskr/static/output", filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

@click.command('hasher')
@with_appcontext
def hasher():
    """Run this once after importing hunet members to hash their IDs!"""
    db = get_db()
    x = db.execute('SELECT * FROM hunet_members').fetchall()
    for item in x:
        y = generate_password_hash(item['password'])
        db.execute(
            'UPDATE hunet_members SET password = ?'
            ' WHERE id = ?',
            (y, item['id'])
        )
        db.commit()
        click.echo('FINISHED HASHING PASSWORD #' + str(item['id']))
    click.echo('FINISHED HASHING PASSWORD')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(hasher)