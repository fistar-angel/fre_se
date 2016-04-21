#############################
#   Quick documentation     #
#############################


This directory services/ handles restful http request related to the MysQL database (Angel project).

- venv directory: it is used for virtual environment
	=> activation: . venv/bin/activate
	=> disable: deactivation

- measurements.py: file that contains a model for each one database table and methods used for RESTful request 

- measurements.wsgi: our flask application (measurements.py) is accessable on the intrnet via httpd (apache) service
	=> there is the desirable configuration on the file /etc/httpd/conf/httpd.conf (see virtualhost that listens at port 5000)


I use a cron job to update the subscription period or attributes list:
Check it: crontab -e
