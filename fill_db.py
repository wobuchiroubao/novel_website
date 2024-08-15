#!/usr/bin/env python3
import bcrypt
from flask import Config
import os.path as op
import psycopg2 as db
import db_query
import AO3
import requests
import sys
import time

cfg = Config(op.dirname(__file__))
cfg.from_envvar('CONFIG')


if __name__ == '__main__':
  if len(sys.argv) != 2:
    sys.exit()
  username = sys.argv[1]
  dbQuery = db_query.DB(cfg)

  loaded_works = []
  try:
    user_id = dbQuery.add_user(
      rights='user_',
      nickname=username,
      password=bcrypt.hashpw(username.encode(), bcrypt.gensalt()).decode(),
      e_mail='{}@gmail.com'.format(username),
    )
  except db.errors.UniqueViolation as err:
    print('Failed to add user:', err)
    user_id = dbQuery.get_user_info_by_nickname(username)['id']
    loaded_works = [
      dbQuery.get_novel_info_by_novel_id(novel_id)['name']
      for novel_id, in dbQuery.get_novels_by_author_id(user_id)
    ]

  user = AO3.User(username)
  for work in user.get_works():
    if work.title in loaded_works:
      print('Work already downloaded, skip:', work)
      continue
    print('Downloading work:', work)
    while True:
      try:
        work.reload()
        break
      except requests.exceptions.RequestException as exc:
        print('Failure while downloading, retrying in 5s:', exc)
        time.sleep(5)

    novel_id = dbQuery.add_novel(
      name=work.title,
      description=work.summary,
      user_id=user_id,
      genres=[],
      chapters=[chapter.text for chapter in work.chapters]
    )
