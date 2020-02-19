# Searching
To crawl google sites and provide information about the keyword seached.

# Table of contents

   1. [Table of contents](#table-of-contents)
   1. [Production](#production)
      1. [Setup](#setup)
      1. [Install](#install)
      1. [Create Admin](#create-admin)
      1. [Cronjob](#cronjob)
      1. [Https](#https)
   1. [Release](#release)
   1. [Development](#development)
      1. [Setup](#dev-setup)
      1. [Database](#database)
      1. [Create Admin](#create-dev-admin)
      1. [Run Server](#run-server)
      1. [Testing](#testing)
      1. [Run Spider](#run-spider)
      1. [Guidelines](#guidelines)

## Production

### Setup
For Ubuntu bionic - 18.04

-> Create user, say *appuser*
 ```
 ssh root@<ip>
 adduser <user>
 usermod -aG sudo <user>
 exit
 ```
-> Initialize and Install pre-requisites
 ```
 ssh <user>@<ip>
 mkdir releases
 exit

 scp -r <release>.tgz <user>@<ip>:~/releases/
 ssh <user>@<ip>

 sudo apt-get upgrade
 sudo apt-get update

 # Add the below lines to ~/.bashrc.
   export ENV_HOME=~
   export ENV_PROJECT=<project>

   export ENV_SERVER_TYPE=<all/webserver/crawler/dev>

   #For ENV_SERVER_TYPE all/webserver
   export ENV_SITES=<site>.headrun.com
   export ENV_NUM_PROCESSES=<int>

   #For ENV_SERVER_TYPE all/crawler
   export ENV_CONCURRENT_REQUESTS=<int>

   export SITE=<sites/name>

   #For HTTPS and PROD 
   export ENV_HTTPS=True
    
   export MYSQL_DATABASE=<db_name>#optional
   export MYSQL_USER=<user>
   export MYSQL_PASSWORD=<password>
   export MYSQL_HOST=<hostname>#optional
   export MYSQL_PORT=<port>#optional

 source ~/.bashrc

 tar -xzf releases/<release>.tgz
 cd <release>
 sh deploy/setup.sh
 sh deploy/upgrade.sh
 if ENV_SERVER_TYPE=<all/webserver/dev>
    sh deploy/django.sh createsuperuser
 if ENV_SERVER_TYPE=<webserver>
    Grant acess of DB to ENV_SERVER_TYPE=<crawler>
    Comment bind_ip_address from mysqld.conf and restart mysql service
 exit
 ```

### Install
Install the project/application.

 ```
 scp -r <release>.tgz <user>@<ip>:~/releases/
 ssh <user>@<ip>
 sh <project>/deploy/install.sh releases/<release>.tgz

 If installation fails because of third party packages, then
 sh <release>/deploy/setup.sh
 continue installation as above
 ```

### Cronjob
Schedule the below command in crontab or django celery etc., Use Lockrun or something similar to make sure only one process is running.
 ```
 export SITE=<site>; export SCRAPY_PROJECT=$SITE; export CMD_HOME=/home/<user>/<project>; cd $CMD_HOME; python3 crawl/scrapy/process.py 2>&1 >> $CMD_HOME/process.log
 ```
 
### Https
Installing key and certificate files for Https.
 ```
 create a directory <site>.headrun.com with ssl.crt and ssl.key
 scp -r <site>.headrun.com <user>@<ip>:~/
 ssh <user>@<ip>
 sudo mv <site>.headrun.com /etc/ssl/private/
 cd /etc/ssl/private
 chown -R root:root <site>.headrun.com
 cd <site>.headrun.com
 chmod 640 ssl.key
 chmod 644 ssl.crt
 exit
 ```
 
## Release
Should always be done in a clean git clone, which is only used for making releases and not for development.
 ```
 cd <new_dir>
 git clone https://github.com/headrun/<project_dir> --depth 1
 cd <project_dir>
 mkdir -p ../releases # if not exists releases
 git pull
 sh deploy/release.sh ../releases
 ```
 
## Development

### Dev Setup

Install the pre-requisites
 ```
 cd <project_dir>
 export ENV_SERVER_TYPE=dev; sh deploy/setup.sh
 ```

### Database

 ```
 # Add the below lines to ~/.bashrc.
   export MYSQL_USER=<user>/root
   export MYSQL_PASSWORD=<password>

 source ~/.bashrc
 cd <project_dir>
 sh deploy/django.sh dev
 ```

### Create Dev Admin
Create Admin User

 ```
 sh deploy/django.sh createsuperuser
 ```

### Run server

Django server
 ```
 cd <project_dir>
 export SITE=<site>; export DEBUG=1; python3 manage.py runserver
 Go to http://127.0.0.1:8000/ in browser
 ```
### Testing
Django unit tests
 ```
 cd <project_dir>
 export SITE=<site>; python3 manage.py test <app>
 ```

### Run Spider
 ```
 cd <project_dir>;
 export SITE=<site>; export SCRAPY_PROJECT=$SITE; python3 crawl/scrapy/process.py -s <spider>
 ```

### Guidelines

1. For vim/gvim editors, Add the below lines in ~/.vimrc or ~/.gvimrc
 ```
 set expandtab
 set sw=4
 set ts=4
 ```
2. Commit
 ```
 git diff file # Verify you changes. Diff should show only necessary changes, No empty lines, unwanted comments etc.,
 git add file # Add only the files you need to commit. No file should be added by mistake. usernames/passwords should not be commited.
 git status # Verify if the files added completes the changes for the task.
 git commit -m "#<issue_no> <msg>" # Always add #<issue_no> in the beginning and valid description of the commit in the msg
 git push # If fails, do "git merge", test it and then "git push".
 # Be responsible, understand and commit meaningful and correct commits as per the design of the project.
 ```
