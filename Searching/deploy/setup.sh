#!/bin/sh

. $(dirname "$0")/base.sh

common_pkgs="vim python3-pip"
mysql_pkgs="mysql-server libmysqlclient-dev mysql-client python3-mysqldb"
django_pkgs="mysqlclient django==3.0.2 django-mysql django-rest_framework django-oauth-toolkit"
scrapy_pkgs="scrapy==1.8.0 scrapyd python-scrapyd-api spidermon[monitoring,validation]"

apt_install() {
    sudo apt-get install $1
}

pip_install() {
    sudo pip3 install $1
}

webserver() {
    apt_install "$mysql_pkgs nginx"
    pip_install "$django_pkgs uwsgi"
    pip_install "-U mysqlclient"

    . $(dirname "$0")/django.sh
    setup_db
    lockrun
}

crawler() {
    apt_install "$mysql_pkgs"
    pip_install "$django_pkgs $scrapy_pkgs"
    pip_install "-U mysqlclient"
    lockrun
}

lockrun() {
    file="lockrun.c"
    if [ -f $file ] ; then
        rm $file
    fi
    binpath="/usr/local/bin/"
    URL="http://www.unixwiz.net/tools/$file"
    wget "${URL}"
    cc ${file} -o lockrun
    sudo cp lockrun ${binpath}
    rm $file
    rm lockrun
}
    
all() {
    webserver
    crawler
    lockrun
}

dev() {
    apt_install "$mysql_pkgs"
    pip_install "$django_pkgs django-debug-toolbar $scrapy_pkgs"
}

main() {
    if [ -z $ENV_SERVER_TYPE ]
    then
        echo "ENV_SERVER_TYPE is not set. all/webserver/crawler/dev"
    else
        apt_install "$common_pkgs"
        $ENV_SERVER_TYPE
    fi
}

main
