#!/bin/bash

##################################
# Fall Risk Evaluation SE
# Copyright 2015 Singular Logic 
#
# Installation file for CentOS 6.x
# Tested for CentOS 6.3/6.5
##################################


printf "##################################
# Installation file for CentOS 6.x
# Tested for CentOS 6.3/6.5
##################################\n"


# Add groups and users
printf "Add new groups and users\n"
sudo groupadd orion2sql
sudo useradd -g orion2sql -s /bin/bash orion2sql
sudo groupadd restservices
sudo useradd -g restservices -s /bin/bash restservices


# Update yum package
printf "\n\nUpdate yum package...\n"
which yum
sudo yum -y update


# Install mysql server
printf "\n\nInstall MySQL server\n"
sudo yum install mysql-server
sudo yum install gcc python-devel mysql-devel
sudo service mysqld start
sudo /usr/bin/mysql_secure_installation
sudo chkconfig mysqld on


# install apache web server
printf "\n\nInstall Apache web server\n"
sudo yum install httpd mod_wsgi
sudo chkconfig httpd on


# install general packages
printf "\n\nInstall basic packages\n"
sudo yum install epel-release
sudo yum install python-pip
sudo yum install pytz
sudo yum install python-lxml python-requests


#install third-party python modules
printf "\n\nInstall third-party python modules\n\n"
sudo pip install pip==6.0.8
sudo pip install mysql-python
sudo pip install flask flask-api flask-sqlalchemy flask-negotiate
sudo pip install importlib
sudo pip install jsonschema
sudo pip install validictory
sudo pip install pymongo
sudo pip install xlsxwriter


