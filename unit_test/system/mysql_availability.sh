#!/bin/bash

# check MySQL existance
printf "Checking for the MySQL server...\n"
rpmquery mysql


printf "\nSearching the main part of the package\n"
rpm -ql mysql

printf "\nRetrieving the MySQL status\n"
sudo service mysqld status
