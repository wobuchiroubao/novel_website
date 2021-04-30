from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
import os
import psycopg2 as db
from psycopg2.extras import DictCursor

app = Flask(__name__) # create application instance
app.config.from_object('.default_config') # load config from dict-like object config

def connect_db():
    """Connects to the database"""
    return db.connect(
        dbname=app.config['DBNAME'], user=app.config['USER'],
        password=app.config['PASSWORD'], host=app.config['HOST']
        #cursor_factory=DictCursor
    )

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context. Otherwise returns the existing connection.
    """
    if not hasattr(g, 'sql_db'):
        g.sql_db = connect_db()
    return g.sql_db

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        # open_resource('res') opens the file 'res'
        # located in the folder ./website/website

        # create the empty database with script from schema.sql
        db.cursor().execute(f.read())
    db.commit()

# what this thing is for???
@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

# decorator app.teardown_appcontext registers a function to be called
# when the application context ends.
@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sql_db'):
        g.sql_db.close()
