#!/usr/bin/env python3
import bcrypt
from flask import Config
import os.path as op
import psycopg2 as db
import db_query
import AO3
from sys import exit


cfg = Config(op.dirname(__file__))
cfg.from_envvar('CONFIG')


if __name__ == '__main__':
  username = input("""Enter username: """)
  dbQuery = db_query.DB(cfg)

  try:
    user_id = dbQuery.add_user(
      rights='user_',
      nickname=username,
      password=bcrypt.hashpw(username.encode(), bcrypt.gensalt()).decode(),
      e_mail='{}@gmail.com'.format(username),
    )
  except db.errors.UniqueViolation as err:
    print(err)
    exit()

  user = AO3.User(username)
  works = user.get_works()
  for novel_num in range(len(works)):
    novel_id = dbQuery.add_novel(
      name=works[novel_num].title,
      description=works[novel_num].summary,
      user_id=user_id,
      genres=[],
    )

    if novel_id == None:
      continue

    works[novel_num].reload()
    for chap_num in range(len(works[novel_num].chapters)):
      dbQuery.add_chapter(
        chapter_num=(chap_num + 1),
        novel_id=novel_id,
        description=works[novel_num].chapters[chap_num].text,
      )
