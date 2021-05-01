from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
import os
import psycopg2 as dbc
from psycopg2.extras import DictCursor

app = Flask(__name__) # create application instance
#app.config.from_object('.default_config')
app.config.from_envvar('CONFIG')

def connect_db():
    """Connects to the database"""
    return dbc.connect(
        dbname=app.config['DBNAME'], user=app.config['USER'],
        password=app.config['PASSWORD'], host=app.config['HOST'],
        #cursor_factory=DictCursor
    )

def get_dbc():
    """Opens a new database connection if there is none yet for the
    current application context. Otherwise returns the existing connection.
    """
    if not hasattr(g, 'sql_dbc'):
        g.sql_dbc = connect_db()
    return g.sql_dbc

def init_db():
    dbc = get_dbc()
    with app.open_resource('schema.sql', mode='r') as f:
        # open_resource() opens files from website/website
        # (but what's the difference with open()?)
        dbc.cursor().execute(f.read())
    dbc.commit()

# wrapper on init_dbc to make a CLI command: $ flask initdbc
@app.cli.command('initdb')
def initdbc_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.route('/')
def main_page():
    dbc = get_dbc()
    cur = dbc.cursor()
    cur.execute('SELECT title, text FROM entries ORDER BY id DESC')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    dbc = get_dbc()
    dbc.cursor().execute('insert into entries (title, text) values (%s, %s)',
                 [request.form['title'], request.form['text']])
    dbc.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    # second parameter means that pop() will do nothing
    # if key was not in dict session
    flash('You were logged out')
    return redirect(url_for('show_entries'))

# decorator app.teardown_appcontext registers a function to be called
# when the application context ends.
@app.teardown_appcontext
def close_dbc(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sql_dbc'):
        g.sql_dbc.close()
