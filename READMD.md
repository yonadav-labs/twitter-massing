1. install postgresql
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

2. set password for postgres user
sudo -u postgres psql
\password postgres
\q
/etc/postgresql/9.3/main/pg_hba.conf

change the line 

# Database administrative login by Unix domain socket
local   all             postgres                                peer

to

# Database administrative login by Unix domain socket
local   all             postgres                                md5

sudo service postgresql restart

3. install redis server 

$ sudo add-apt-repository ppa:chris-lea/redis-server

$ sudo apt-get update

$ sudo apt-get install redis-server

4.install releative package

sudo apt-get install python-pip

sudo apt-get install python-dev libffi-dev

sudo apt-get install postgresql-server-dev-X.Y

sudo apt-get install virtualenvwrapper

sudo apt-get install libxml2-dev libxslt1-dev

5. set virtualenv

$ virtualenv massing_env
$ source massing_env/bin/activate