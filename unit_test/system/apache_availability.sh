#!/bin/bash

# check the existance of apache web server
printf "\nChecking for apache web server...\n"
rpm -qa | grep httpd

# apache information
printf "\nApache information...\n"
httpd -v

# check ports
printf "\nChecking the status of apache ports 80, 5000, 5999...\n"
netstat -tulnp | grep 80
netstat -tulnp | grep 5000
netstat -tulnp | grep 5999

# apache path of binary
printf "\nPath of apache binary..\n"
which httpd

# status
printf "\nRetrieving the Apache web server status...\n"
sudo service httpd status
