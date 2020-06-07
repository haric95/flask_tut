import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """
    Returns the database connection. Reuses existing if it is present.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
        current_app.config['DATABASE'],
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """
    Closes the connection to the database.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# These are python decorators.
# https://realpython.com/primer-on-python-decorators/
# click is the command line interface creation kit.
@click.command('init-db')
# for info on with_appcontext flask.cli decorator
# https://flask.palletsprojects.com/en/1.1.x/cli/
@with_appcontext
def init_db_command():
    """
    Clear the existing data and create new tables.
    """
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """
    Takes in an instance of a flask app and registers the teardown function
    and the init_command_command that can be called with the flask command.

    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)