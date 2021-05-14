#!/usr/bin/env python3
import os.path as op
from getpass import getpass
from flask import Config
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
    admin_name = input("""Enter admin's nickname: """)
    admin_passwd = getpass(prompt='Enter password: ')
    if getpass(prompt='Repeat password: ') != admin_passwd:
        print("""Error: Password and its repetition don't match.""")
        exit()
    admin_e_mail = input('Enter email: ')
    dbc = connect_db()
    cur = dbc.cursor()
    cur.execute(
        """INSERT INTO "user" (nickname, password, e_mail, rights) \
        VALUES (%s, %s, %s, 'admin_')""",
        (admin_name, admin_passwd, admin_e_mail)
    )
    dbc.commit()
    dbc.close()
