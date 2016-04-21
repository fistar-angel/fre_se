#!/bin/bash

#################################
# Fall Risk Evaluation SE
# Copyright 2015 - Singular Logic
#
# Allow traffic in specific ports
#   - 5000
#   - 5999
#################################

printf "Allow traffic in ports 5000, 5999\n"

sudo iptables -I INPUT -p tcp --dport 5000 -j ACCEPT
sudo iptables -I INPUT -p tcp --dport 5999 -j ACCEPT
sudo service iptables save

