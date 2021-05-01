#!/usr/bin/env python3
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
    if not hasattr(g, 'dbc'):
        g.dbc = connect_db()
    return g.dbc

@app.route('/')
def main_page():
    return render_template('main_page.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['password'] != request.form['password_rep']:
            abort(400)
        dbc = get_dbc()
        cur = dbc.cursor()
        cur.execute(
            'INSERT INTO "user" (nickname, password, e_mail) VALUES (%s, %s, %s)',
            [request.form['nickname'], request.form['password'],
            request.form['e_mail']]
        )
        dbc.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/search')
def search():
    dbc = get_dbc()
    cur = dbc.cursor()
    cur.execute(
        'SELECT name, description, rating FROM "novel" WHERE name = %s ORDER BY rating DESC',
        [request.form['novel_name']])
    data = cur.fetchall()
    return render_template('novels_list.html', data=data)

# decorator app.teardown_appcontext registers a function to be called
# when the application context ends.
@app.teardown_appcontext
def close_dbc(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'dbc'):
        g.dbc.close()

if __name__ == '__main__':
    app.run()
