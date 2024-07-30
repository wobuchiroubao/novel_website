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
import psycopg2 as db
from psycopg2.extras import DictCursor
import db_query


app = Flask(__name__) # create application instance
app.config.from_envvar('CONFIG')


@app.route('/', methods=['GET', 'POST'])
def main_page():
  return render_template('main_page.html')


@app.route('/novel/<int:novel_id>')
def novel(novel_id):
  dbQuery = db_query.DB(app.config)
  return render_template(
    'novel.html',
    novel=dbQuery.get_novel_info_by_novel_id(novel_id),
    genres=dbQuery.get_genres_info_by_novel_id(novel_id)
  )


@app.route('/search_results', methods=['POST'])
def search_results():
  dbQuery = db_query.DB(app.config)
  recs = []
  if 'novel_name' in request.form:
    recs = dbQuery.get_novels_by_novel_name(request.form['novel_name'])
  else:
    pass # TODO: return advanced search
  data = []
  for rec in recs:
    data.append((
      dbQuery.get_novel_info_by_novel_id(rec['id']),
      dbQuery.get_genres_info_by_novel_id(rec['id'])
    ))
  return render_template('search_results.html', data=data)


@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    if request.form['password'] != request.form['password_rep']:
      return jsonify(url=None, err='Passwords don\'t match.')
    dbQuery = db_query.DB(app.config)
    try:
      dbQuery.add_user(
        rights=session.get('user_rights') or 'user_',
        nickname=request.form['nickname'],
        password=bcrypt.hashpw(request.form['password'].encode(), bcrypt.gensalt()).decode(),
        e_mail=request.form['e_mail']
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
    if session.get('user_rights') == 'admin_':
      return jsonify(url=url_for('administration_settings'), err=None)
    else:
      return jsonify(url=url_for('login'), err=None)
  return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    dbQuery = db_query.DB(app.config)
    info = dbQuery.get_user_info_by_nickname(nickname=request.form['login'])
    if info is None:
      return jsonify(
        url=None, err='User with this nickname doesn\'t exist.'
      )
    if not bcrypt.checkpw(
      request.form['password'].encode(), info['password'].encode()
    ):
      return jsonify(url=None, err='Wrong password.')
    session['user_id'] = info['id']
    session['user_rights'] = info['rights']
    return jsonify(url=url_for('main_page'), err=None)
  return render_template('login.html')


@app.route('/logout')
def logout():
  session.pop('user_id', None)
  session.pop('user_rights', None)
  return redirect(url_for('main_page'))


@app.route('/account_settings', methods=['GET', 'POST'])
def account_settings():
  dbQuery = db_query.DB(app.config)
  if request.method == 'POST':
    password = None
    if 'new_password' in request.form:
      if request.form['new_password'] != request.form['new_password_rep']:
        abort(400)
      password = bcrypt.hashpw(request.form['new_password'].encode(), bcrypt.gensalt()).decode()
    dbQuery.update_user(
      id=session['user_id'],
      nickname=request.form.get('new_login'),
      password=password,
      e_mail=request.form.get('new_e_mail')
    )
  nickname = dbQuery.get_user_info_by_user_id(id=session['user_id'])['nickname']
  return render_template('account_settings.html', nickname=nickname)


@app.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
  dbQuery = db_query.DB(app.config)
  if request.method == 'POST':
    try:
      dbQuery.add_novel(
        name=request.form['name'],
        description=request.form['description'],
        user_id=session['user_id'],
        genres=request.form.getlist('genre')
      )
    except db.errors.DatabaseError:
      abort(400)
  nickname = dbQuery.get_user_info_by_user_id(id=session['user_id'])['nickname']
  novels = dbQuery.get_novels_by_author_id(session['user_id'])
  data = []
  for novel, in novels:
    data.append((
      dbQuery.get_novel_info_by_novel_id(novel),
      dbQuery.get_genres_info_by_novel_id(novel)
    ))
  return render_template('user_profile.html', nickname=nickname, data=data)


@app.route('/administration_settings', methods=['GET', 'POST'])
def administration_settings():
  dbQuery = db_query.DB(app.config)
  if request.method == 'POST':
    if 'genre' in request.form:
      if request.form['action'] == 'save':
        dbQuery.update_genre(genre_id=request.form['genre'], genre=request.form['edit_genre'])
      elif request.form['action'] == 'delete':
        dbQuery.delete_genre(genre_id=request.form['genre'])
    else:
      try:
        dbQuery.add_genre(request.form['add_genre'])
      except db.errors.UniqueViolation:
        return jsonify(
          url=None,
          err='Genre "{}" already exists.'.format(request.form['add_genre'])
        )
      return jsonify(url=url_for('administration_settings'), err=None)
  return render_template('administration_settings.html', genres=dbQuery.get_genres_info())


@app.route('/search')
def search():
  dbQuery = db_query.DB(app.config)
  return render_template('search_novel.html', genres=dbQuery.get_genres_info())


if __name__ == '__main__':
  app.run()
