#!/usr/bin/env python3
import bcrypt
from flask import (
    Flask,
    request,
    session,
    g,
    redirect,
    url_for,
    abort,
    render_template,
    jsonify
)
import os
import psycopg2 as db
from psycopg2.extras import DictCursor

app = Flask(__name__) # create application instance
app.config.from_envvar('CONFIG')

def connect_db():
    """Connects to the database"""
    return db.connect(
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
    return render_template('main_page.html')

@app.route('/novel/<int:novel_id>')
def novel(novel_id):
    dbc = get_dbc()
    cur = dbc.cursor()
    cur.execute(
        'SELECT name, description, rating, votes, "user".nickname AS author \
        FROM "novel" JOIN "user" ON "novel".id_user = "user".id \
        WHERE "novel".id = %s',
        [novel_id]
    )
    cur_gen = dbc.cursor()
    cur_gen.execute(
        'SELECT "genre".id, "genre".genre \
        FROM "genre" JOIN "genre_aux" ON "genre".id = "genre_aux".id_genre \
        WHERE "genre_aux".id_novel = %s ORDER BY "genre".genre',
        [novel_id]
    )
    return render_template(
        'novel.html', novel=cur.fetchone(), genres=cur_gen.fetchall()
    )

@app.route('/novels_list', methods=['POST'])
def novels_list():
    dbc = get_dbc()
    cur = dbc.cursor()
    recs = None
    if 'novel_name' in request.form:
        recs = find_name(cur)
    else:
        recs = find_advanced(cur)
        #return render_template('try.html', data=recs)
    data = []
    cur_gen = dbc.cursor()
    for rec in recs:
        cur.execute(
            'SELECT "novel".id, name, description, rating, "user".nickname AS author \
            FROM "novel" JOIN "user" ON "novel".id_user = "user".id \
            WHERE "novel".id = %s',
            [rec['id']]
        )
        cur_gen.execute(
            'SELECT id_genre, genre FROM "genre_aux" \
            JOIN "genre" ON "genre_aux".id_genre = "genre".id \
            WHERE id_novel = %s ORDER BY genre',
            [rec['id']]
        )
        data.append((cur.fetchone(), cur_gen.fetchall()))
    return render_template('novels_list.html', data=data)

def find_name(cur):
    cur.execute(
        'SELECT id FROM "novel" \
        WHERE LOWER(name) LIKE \'%%\' || TRIM(both ' ' FROM LOWER(%s)) || \'%%\' \
        ORDER BY rating DESC, name',
        [request.form['novel_name']]
    )
    return cur.fetchall()

def find_advanced(cur):
    str_, param = sql_find_novel_template()
    str_sort = ''
    if request.form['sort_field'] == 'rating':
        str_sort += ' ORDER BY rating'
    elif request.form['sort_field'] == 'chapters':
        str_sort += ' ORDER BY chap_num'
    if request.form['sort_order'] == 'desc':
        str_sort += ' DESC NULLS LAST'
    else:
        str_sort += ' NULLS FIRST'
    str_sort += ', name'
    #return ('WITH dummy AS (1)' + str_ + str_sort, param)
    cur.execute(
        'WITH dummy AS (SELECT 1)' + str_ + str_sort, param
    )
    return cur.fetchall()

def sql_find_chapters_template(func):
    def wrapped():
        if request.form['chapters'] and not (
            request.form['chapters_min_max'] == 'min'
            and request.form['chapters'] == '0'
        ):
            str_, param = func()
            param.append(request.form['chapters'])
            str_add = ' AND (chap_num '
            if request.form['chapters_min_max'] == 'min':
                str_add += '>= %s)'
            else:
                str_add += '<= %s OR chap_num IS NULL)'
            return (str_ + str_add, param)
        return func()
    return wrapped

def sql_find_rating_template(func):
    def wrapped():
        if request.form['rating']:
            str_, param = func()
            param.append(request.form['rating'])
            str_add = ' AND (rating '
            if request.form['rating_min_max'] == 'min':
                str_add += '>= '
            else:
                str_add += '<= '
            str_add += '%s)'
            return (str_ + str_add, param)
        return func()
    return wrapped

def sql_find_genre_template(func):
    def wrapped():
        if 'genre' in request.form:
            str_, param = func()
            num_gen = len(request.form.getlist('genre'))
            str_or = ' OR genre = %s' * (num_gen - 1)
            str_add = ', "genre_id" AS ( \
                SELECT id FROM "genre" WHERE genre = %s' + str_or + ')'
            for genre in request.form.getlist('genre'):
                param.insert(0, genre)
            if request.form['genre_and_or'] == 'and':
                str_add += ', "novel_genre" AS ( \
                    SELECT "genre_aux".id_novel FROM "genre_aux" \
                    JOIN "genre_id" ON "genre_aux".id_genre = "genre_id".id \
                    GROUP BY "genre_aux".id_novel \
                    HAVING COUNT(*) = ' + str(num_gen) + ')'
            else:
                str_add += ', "novel_genre" AS ( \
                SELECT DISTINCT id_novel FROM "genre_aux" \
                WHERE id_genre IN (SELECT id FROM "genre_id"))'
            return (
                str_add + str_ + \
                ' AND (id IN (SELECT id_novel FROM "novel_genre"))', param
            )
        return func()
    return wrapped

@sql_find_genre_template
@sql_find_rating_template
@sql_find_chapters_template
def sql_find_novel_template():
    return (
        ', "chapters" AS ( \
        SELECT COUNT(*) AS chap_num, id_novel FROM "chapter" GROUP BY id_novel \
        ) SELECT id FROM "novel" \
        LEFT JOIN "chapters" ON "novel".id = "chapters".id_novel WHERE TRUE', []
    )

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['password'] != request.form['password_rep']:
            return jsonify(url=None, err='Passwords don\'t match.')
        dbc = get_dbc()
        cur = dbc.cursor()
        try:
            cur.execute(
                'INSERT INTO "user" (rights, nickname, password, e_mail) \
                VALUES (%s, %s, %s, %s)',
                [session.get('user_rights') or 'user_', request.form['nickname'],
                bcrypt.hashpw(
                    request.form['password'].encode(), bcrypt.gensalt()
                ).decode(),
                request.form['e_mail']]
            )
        except db.errors.UniqueViolation as err:
            if 'nickname' in str(err):
                return jsonify(
                    url=None, err='User with this nickname already exists.'
                )
            else:
                return jsonify(
                    url=None, err='User with this email already exists.'
                )
        dbc.commit()
        if session.get('user_rights') == 'admin_':
            return jsonify(url=url_for('administration_settings'), err=None)
        else:
            return jsonify(url=url_for('login'), err=None)
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
            return jsonify(
                url=None, err='User with this nickname doesn\'t exist.'
            )
        if not bcrypt.checkpw(
            request.form['password'].encode(), rec['password'].encode()
        ):
            return jsonify(url=None, err='Wrong password.')
        session['user_id'] = rec['id']
        session['user_rights'] = rec['rights']
        return jsonify(url=url_for('main_page'), err=None)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_rights', None)
    return redirect(url_for('main_page'))

@app.route('/account_settings', methods=['GET', 'POST'])
def account_settings():
    dbc = get_dbc()
    cur = dbc.cursor()
    if request.method == 'POST':
        account_settings_post(dbc, cur)
    cur.execute(
        'SELECT nickname FROM "user" WHERE id = %s', [session['user_id']]
    )
    nickname, = cur.fetchone()
    cur.execute(
        'SELECT name, description FROM "novel" WHERE id_user = %s ORDER BY name',
        [session['user_id']])
    data = cur.fetchall()
    return render_template('account_settings.html', nickname=nickname, data=data)

def account_settings_post(dbc, cur):
    set_var = None
    if 'new_login' in request.form:
        set_var = 'nickname'
    elif 'new_password' in request.form:
        if request.form['new_password'] != request.form['new_password_rep']:
            abort(400)
        set_var = 'password'
    elif 'new_e_mail' in request.form:
        set_var = 'e_mail'
    else:
        abort(300)
    cur.execute(
        'UPDATE "user" SET ' + set_var + ' = %s WHERE id = %s',
        [
            request.form.get('new_login')
            or request.form.get('new_password')
            or request.form.get('new_e_mail'), session['user_id']
        ]
    )
    dbc.commit()

@app.route('/administration_settings', methods=['GET', 'POST'])
def administration_settings():
    if request.method == 'POST':
        dbc = get_dbc()
        cur = dbc.cursor()
        cur.execute(
            'INSERT INTO "genre" (genre, genre_type) \
            VALUES (%s, %s)',
            [request.form['genre'], 'genre_']
        )
        dbc.commit()
    return render_template('administration_settings.html')

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
    cur.execute(
        'SELECT (genre) FROM "genre" \
        WHERE genre_type = \'genre_\' ORDER BY genre'
    )
    return render_template('post_novel.html',genres=cur.fetchall())

@app.route('/search')
def search():
    dbc = get_dbc()
    cur = dbc.cursor()
    cur.execute(
        'SELECT (genre) FROM "genre" \
        WHERE genre_type = \'genre_\' ORDER BY genre'
    )
    return render_template('search_novel.html', genres=cur.fetchall())

# decorator app.teardown_appcontext registers a function to be called
# when the application context ends.
@app.teardown_appcontext
def close_dbc(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'dbc'):
        g.dbc.close()

if __name__ == '__main__':
    app.run()
