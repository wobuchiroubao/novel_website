import psycopg2 as db
from psycopg2.extras import DictCursor


class DB:
  def __init__(self, config):
    self.config = config
    self.conn = db.connect(
      dbname=self.config['DBNAME'], user=self.config['USER'],
      password=self.config['PASSWORD'], host=self.config['HOST'],
      cursor_factory=DictCursor
    )


  def __del__(self):
    self.conn.close()


# ---------------------user---------------------

  def get_user_info_by_user_id(self, id):
    with self.conn:
      with self.conn.cursor() as cur:
        cur.execute(
          'SELECT * FROM "user" WHERE id = %s',
          [id]
        )
        res = cur.fetchone()
    return res


  def get_user_info_by_nickname(self, nickname):
    with self.conn:
      with self.conn.cursor() as cur:
        cur.execute(
          'SELECT * FROM "user" WHERE nickname = %s',
          [nickname]
        )
        res = cur.fetchone()
    return res


  def add_user(self, rights, nickname, password, e_mail):
    with self.conn:
      with self.conn.cursor() as cur:
        cur.execute(
          'INSERT INTO "user" (rights, nickname, password, e_mail) VALUES (%s, %s, %s, %s)',
          [rights, nickname, password, e_mail]
        )


  def update_user(self, id, nickname=None, password=None, e_mail=None):
    with self.conn:
      with self.conn.cursor() as cur:
        if nickname is not None:
          cur.execute(
            'UPDATE "user" SET nickname = %s WHERE id = %s',
            [nickname, id]
          )
        if password is not None:
          cur.execute(
            'UPDATE "user" SET password = %s WHERE id = %s',
            [password, id]
          )
        if e_mail is not None:
          cur.execute(
            'UPDATE "user" SET e_mail = %s WHERE id = %s',
            [e_mail, id]
          )


# ---------------------genre---------------------
  
  def get_genres_info(self):
    with self.conn:
      with self.conn.cursor() as cur:
        cur.execute(
          'SELECT * FROM "genre" WHERE genre_type = \'genre_\' ORDER BY genre'
        )
        res = cur.fetchall()
    return res


  def get_genres_info_by_novel_id(self, novel_id):
    with self.conn:
      with self.conn.cursor() as cur:
        cur.execute(
          'SELECT * FROM "genre" \
          JOIN "genre_aux" ON "genre".id = "genre_aux".id_genre \
          WHERE "genre_aux".id_novel = %s ORDER BY "genre".genre',
          [novel_id]
        )
        res = cur.fetchall()
    return res


  def add_genre(self, genre):
    with self.conn:
      with self.conn.cursor() as cur:
        cur.execute(
          'INSERT INTO "genre" (genre, genre_type) VALUES (%s, %s)',
          [genre, 'genre_']
        )


  def update_genre(self, genre_id, genre):
    with self.conn:
      with self.conn.cursor() as cur:
        cur.execute(
          'UPDATE "genre" SET genre = %s WHERE id = %s',
          [genre, genre_id]
        )


  def delete_genre(self, genre_id):
    with self.conn:
      with self.conn.cursor() as cur:
        cur.execute(
          'DELETE FROM "genre" WHERE id = %s',
          [genre_id]
        )


# ---------------------novel---------------------

  def get_novels_by_novel_name(self, name):
    with self.conn:
      with self.conn.cursor() as cur:
        cur.execute(
          'SELECT id FROM "novel" \
          WHERE LOWER(name) LIKE \'%%\' || TRIM(both ' ' FROM LOWER(%s)) || \'%%\' \
          ORDER BY rating DESC, name',
          [name]
        )
        res = cur.fetchall()
    return res


  def get_novels_by_author_id(self, author_id):
    with self.conn:
      with self.conn.cursor() as cur:
        cur.execute(
          'SELECT id FROM "novel" WHERE id_user = %s ORDER BY name',
          [author_id]
        )
        res = cur.fetchall()
    return res


  def get_novel_info_by_novel_id(self, id):
    with self.conn:
      with self.conn.cursor() as cur:
        cur.execute(
          'SELECT "novel".id, name, description, rating, votes, "user".nickname AS author FROM "novel" \
          JOIN "user" ON "novel".id_user = "user".id WHERE "novel".id = %s',
          [id]
        )
        res = cur.fetchone()
    return res


  def add_novel(self, name, description, user_id, genres):
    with self.conn:
      with self.conn.cursor() as cur:
        cur.execute(
          'INSERT INTO "novel" (name, description, id_user) VALUES (%s, %s, %s) RETURNING id',
          [name, description, user_id]
        )
        novel_id, = cur.fetchone()
        for genre_id in genres:
          cur.execute(
            'INSERT INTO "genre_aux" (id_genre, id_novel) VALUES (%s, %s)',
            [genre_id, novel_id]
          )


# ---------------------review---------------------

  def get_reviews_info_by_novel_id(self, novel_id):
    with self.conn:
      with self.conn.cursor() as cur:
        cur.execute(
          'SELECT "review".id, rating, text, "user".nickname AS username FROM "review" \
          JOIN "user" ON "review".id_user = "user".id WHERE id_novel = %s',
          [novel_id]
        )
        res = cur.fetchall()
    return res


  def get_review_info_by_novel_id_user_id(self, novel_id, user_id):
    with self.conn:
      with self.conn.cursor() as cur:
        cur.execute(
          'SELECT * FROM "review" WHERE (id_novel = %s AND id_user = %s)',
          [novel_id, user_id]
        )
        res = cur.fetchone()
    return res


  def add_review(self, user_id, novel_id, rating, text=None):
    with self.conn:
      with self.conn.cursor() as cur:
        cur.execute(
          'INSERT INTO "review" (rating, text, id_novel, id_user) VALUES (%s, %s, %s, %s)',
          [rating, text, novel_id, user_id]
        )
