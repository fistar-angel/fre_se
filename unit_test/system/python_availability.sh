#!/bin/bash

# python package
printf "\nSearching for python...\n"
printf "PATH: "
which python
printf "Version: "
python --version

# modules
printf "\nSearching python modules\n"
which pip
pip freeze | grep Flask*
pip freeze | grep Werkzeug 
pip freeze | grep validictory 
pip freeze | grep jsonschema 
pip freeze | grep importlib 
pip freeze | grep MySQL-python
pip freeze | grep XlsxWriter
