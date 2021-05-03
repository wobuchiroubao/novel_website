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
        cursor_factory=DictCursor
    )

def get_dbc():
    """Opens a new database connection if there is none yet for the
    current application context. Otherwise returns the existing connection.
    """
    if not hasattr(g, 'dbc'):
        g.dbc = connect_db()
    return g.dbc

@app.route('/', methods=['GET', 'POST'])
def main_page():
    return render_template('main_page.html', logged_in=('user_id' in session))

@app.route('/novels_list', methods=['POST'])
def novels_list():
    dbc = get_dbc()
    cur = dbc.cursor()
    cur.execute(
        'SELECT id FROM "novel" WHERE name LIKE \'%%\' || %s || \'%%\' ORDER BY rating DESC, name',
        [request.form['novel_name']]
    )
    recs = cur.fetchall()
    novel_ids = []
    data = []
    for rec in recs:
        cur.execute(
            'SELECT name, description, rating FROM "novel" WHERE id = %s ORDER BY rating DESC, name',
            [rec['id']]
        )
        data.append(cur.fetchone())
    return render_template('novels_list.html', data=data)

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
    if request.method == 'POST':
        dbc = get_dbc()
        cur = dbc.cursor()
        cur.execute(
            'SELECT * FROM "user" WHERE nickname = %s',
            [request.form['login']]
        )
        rec = cur.fetchone()
        if rec is None:
            abort(400)
        if rec['password'] != request.form['password']:
            abort(400)
        session['user_id'] = rec['id']
        return redirect(url_for('main_page'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main_page'))

@app.route('/account_settings', methods=['GET', 'POST'])
def account_settings():
    dbc = get_dbc()
    cur = dbc.cursor()
    if request.method == 'POST':
        set_var = None
        if 'new_login' in request.form:
            set_var = 'nickname'
        elif 'new_password' in request.form:
            set_var = 'password'
        elif 'new_e_mail' in request.form:
            set_var = 'e_mail'
        else:
            abort(400)
        cur.execute(
            'UPDATE "user" SET ' + set_var + ' = %s WHERE id = %s',
            [request.form['new_login'], session['user_id']]
        )
        dbc.commit()
    cur.execute(
        'SELECT nickname FROM "user" WHERE id = %s', [session['user_id']]
    )
    nickname, = cur.fetchone()
    cur.execute(
        'SELECT name, description FROM "novel" WHERE id_user = %s ORDER BY name',
        [session['user_id']])
    data = cur.fetchall()
    return render_template('account_settings.html', nickname=nickname, data=data)

@app.route('/post_novel', methods=['GET', 'POST'])
def post_novel():
    dbc = get_dbc()
    cur = dbc.cursor()
    if request.method == 'POST':
        cur.execute(
            'INSERT INTO "novel" (name, description, id_user) VALUES (%s, %s, %s) RETURNING id',
            [request.form['name'], request.form['description'],
            session['user_id']]
        )
        novel_id, = cur.fetchone()
        genres = request.form.getlist('genre')
        for genre in genres:
            cur.execute(
                'INSERT INTO "genre_aux" (id_genre, id_novel) VALUES ((SELECT id FROM "genre" WHERE genre = %s), %s)',
                [genre, novel_id]
            )
        dbc.commit()
        return redirect(url_for('account_settings'))
    cur.execute('SELECT (genre) FROM "genre"')
    return render_template('post_novel.html',data=cur.fetchall())

@app.route('/search', methods=['GET', 'POST'])
def search():
    return render_template('search_novel.html')

# decorator app.teardown_appcontext registers a function to be called
# when the application context ends.
@app.teardown_appcontext
def close_dbc(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'dbc'):
        g.dbc.close()

if __name__ == '__main__':
    app.run()
