#!/usr/bin/env python3
import bcrypt
from flask import Config
from getpass import getpass
import os.path as op
import psycopg2 as dbc
from sys import exit

cfg = Config(op.dirname(__file__))
cfg.from_envvar('CONFIG')

def connect_db():
    """Connects to the database"""
    return dbc.connect(
        dbname=cfg['DBNAME'], user=cfg['USER'],
        password=cfg['PASSWORD'], host=cfg['HOST']
    )

if __name__ == '__main__':
    name = input("""Enter admin's nickname: """)
    passwd = getpass(prompt='Enter password: ')
    if getpass(prompt='Repeat password: ') != passwd:
        print("""Error: Password and its repetition don't match.""")
        exit()
    passwd_hash = bcrypt.hashpw(passwd.encode(), bcrypt.gensalt()).decode()
    e_mail = input('Enter email: ')
    dbc = connect_db()
    cur = dbc.cursor()
    cur.execute(
        """INSERT INTO "user" (nickname, password, e_mail, rights) \
        VALUES (%s, %s, %s, 'admin_')""",
        (name, passwd_hash, e_mail)
    )
    dbc.commit()
    dbc.close()
