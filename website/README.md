Sorry, but you ought to create database yourself
and the only thing made automatically will be the filling of the database.
So, to create the proper database ask your system administrator to do smth like this:
```$ psql -d postgres
CREATE DATABASE novel_website;
quit;
```
Set the environment variable `CONFIG` to the path to your configuration.
Like this: `$ export CONFIG='/path/to/config/file'`
You should provide your configuration file with variables:
Example file's guts (config.py):
```
DBNAME='postgres'
USER='postgres'
PASSWORD='my_password'
```
within the project directory website/ run:
```
$ pip install --editable .
$ export FLASK_APP=website
$ export FLASK_DEBUG=true
$ flask initdb
$ flask run
```
