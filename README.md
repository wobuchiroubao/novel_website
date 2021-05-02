## Novel website - application for websites containing novels or frankly speaking writings of any sorts

### Preparing the server
On a server where the database will be stored (for the current version of installation manual it should be the same with the one where the application is run...) create the postgres database:
```
$ createdb -O rolename dbname
$ psql -d dbname
# ALTER USER rolename WITH PASSWORD 'passwd';
# quit;
```
where `rolename` stands for existing UNIX system account, `dbname` and `passwd` are kind of self explanatory (something like `novel_website_db` will do for `dbname`)

### Building from source
Create a configuration file `novel_website_config.py` (or choose any other appropriate name) with the contents:
```
DBNAME='dbname'
USER='rolename'
PASSWORD='passwd'
```
Change the current directory to the target one (the one where you're storing application files), set the environment variable `CONFIG` to the path to your configuration and then load the database configuration `schema.sql`:
```
$ export CONFIG='/path/to/config/file'
$ psql -d dbname < schema.sql
```

### Running
Just type the following command in the target directory:
```
$ ./app.py
```
