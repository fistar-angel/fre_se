############################################
#
# LICENSE
#
# Copyright @ 2015 Singular Logic
#
############################################

from flask import Flask, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.api import status
from datetime import datetime, date
from sqlalchemy import exc, ForeignKey
from sqlalchemy.orm import relationship


__version__ = "1.0"


# sqlalchemy and database settings
app = Flask(__name__)
db = SQLAlchemy(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://takis:t@k!s@localhost/test'


import sys
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('/etc/sysconfig/fallRiskEvaluation/fallRiskEvaluation.conf')

sql_property = 'mysql://'
sql_property += parser.get("mysql", "USER")
sql_property += ":"
sql_property += parser.get("mysql", "PASSWORD")
sql_property += "@"
sql_property += parser.get("mysql", "HOST")
sql_property += "/"
sql_property += parser.get("mysql", "DATABASE_NAME")
app.config['SQLALCHEMY_DATABASE_URI'] = sql_property





class Groups(db.Model):
    """
    Describe the data model of Groups table
    """

    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key = True)
    role = db.Column(db.String(30), nullable = False)
    permissions = db.Column(db.Integer, nullable = False)
    users = relationship("Users")


class Doctors(db.Model):
    """
    Describe the data model of Doctors table
    """

    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(50), nullable = False)
    surname = db.Column(db.String(50), nullable = False)
    username = db.Column(db.String(100), unique = True)
    speciality = db.Column(db.String(100), nullable = False, default="General")
    birth_date = db.Column(db.DateTime)
    email = db.Column(db.String(35))
    phone = db.Column(db.String(15))
    last_login = db.Column(db.DateTime)
    registration = db.Column(db.DateTime)

    def __init__(self, name, surname, username, speciality, birth_date, email, phone, last_login):
        self.name = name
        self.surname = surname
        self.username = username
        self.speciality = speciality
        self.birth_date = birth_date
        self.email = email
        self.phone = phone
        self.last_login = last_login
        self.registration =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')



class Users(db.Model):
    """
    Describe the data model of Users table
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    group_id = db.Column(db.Integer, ForeignKey("groups.id"), nullable = False)
    doctor_id = db.Column(db.Integer, ForeignKey("doctors.id"), nullable = False)
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    uid = db.Column(db.String(50), unique = True)
    birth_date = db.Column(db.DateTime)
    email = db.Column(db.String(35))
    phone = db.Column(db.String(15))
    timezone = db.Column(db.String(100))
    profile = db.Column(db.String(300), nullable = False)
    treatment = db.Column(db.String(300), nullable = False)
    registration_date = db.Column(db.DateTime)

    def __init__(self, name, surname, uid, group_id, birth_date, email, phone, timezone, doctor_id, profile, treatment):
        self.name = name
        self.surname = surname
        self.uid = uid
        self.group_id = group_id
        self.doctor_id = doctor_id
        self.birth_date = birth_date
        self.email = email
        self.phone = phone
        self.timezone = timezone
        self.profile = profile
        self.treatment = treatment
        self.registration_date =  datetime.now().strftime('%Y-%m-%d %H:%M:%S') 



class Measurements(db.Model):
    __tablename__ = 'measurements'

    id = db.Column(db.BigInteger, primary_key = True)
    user_id = db.Column(db.Integer)
    biological_parameter_id = db.Column(db.BigInteger, ForeignKey("biological_parameters.id", onupdate="CASCADE", ondelete="CASCADE"), nullable = False)
    timestamp = db.Column(db.DateTime)
    value = db.Column(db.Float(6))

    def __init__(self, user_id, biological_parameter_id, timestamp, value):
        self.user_id = user_id
        self.biological_parameter_id = biological_parameter_id
        self.timestamp = timestamp
        self.value = value



class BiologicParameters(db.Model):
    __tablename__ = 'biological_parameters'

    id = db.Column(db.BigInteger, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    type = db.Column(db.String(50), nullable = True)
    unit = db.Column(db.String(50), nullable = False)
    #rules = relationship("Rules", backref="biological_parameters")

    def __init__(self, name, type, unit):
        self.name = name
        self.type = type
        self.unit = unit


class Rules(db.Model):
    __tablename__ = 'rules'

    id = db.Column(db.BigInteger, primary_key = True)
    biological_parameter_id = db.Column(db.BigInteger, ForeignKey("biological_parameters.id", onupdate="CASCADE", ondelete="CASCADE"), nullable = False)
    optimal_value = db.Column(db.Float, nullable = False)
    critical_low_threshold = db.Column(db.Float, nullable = True)
    critical_high_threshold = db.Column(db.Float, nullable = True)
    acceptable_low_threshold = db.Column(db.Float, nullable = True)
    acceptable_high_threshold = db.Column(db.Float, nullable = True)
    #time_window = db.Column(db.Integer, nullable = True)

    def __init__(self, biological_parameter_id, optimal_value, critical_low_threshold, critical_high_threshold, acceptable_low_threshold, acceptable_high_threshold):
        self.biological_parameter_id = biological_parameter_id
        self.optimal_value = optimal_value
        self.critical_low_threshold = critical_low_threshold
        self.critical_high_threshold = critical_high_threshold
        self.acceptable_low_threshold = acceptable_low_threshold
        self.acceptable_high_threshold = acceptable_high_threshold
        #self.time_window = time_window



class Comparisons(db.Model):
    __tablename__ = 'comparisons'

    id = db.Column(db.BigInteger, primary_key = True, nullable = False)
    measurement_id = db.Column(db.BigInteger, ForeignKey("measurements.id", onupdate="CASCADE", ondelete="CASCADE"), nullable = False)
    rule_id = db.Column(db.BigInteger, ForeignKey("rules.id", onupdate="CASCADE", ondelete="CASCADE"), nullable = False)
    parameter = db.Column(db.String(150), nullable = True)
    status = db.Column(db.Integer, nullable = False, default = 0)
    timestamp = db.Column(db.DateTime, nullable = False, default = '0000-00-00 00:00:00')

    def __init__(self, measurement_id, rule_id, parameter, status, timestamp):
        self.measurement_id = measurement_id
        self.rule_id = rule_id
        self.parameter = parameter
        self.status = status
        self.timestamp = timestamp



class Risk(db.Model):
    __tablename__ = 'risk'

    id = db.Column(db.BigInteger, primary_key = True, nullable = False)
    comparison_id = db.Column(db.BigInteger, ForeignKey("comparisons.id", onupdate="CASCADE", ondelete="CASCADE"), nullable = False)
    possibility = db.Column(db.Float, nullable = False)
    timestamp = db.Column(db.DateTime, nullable = False, default = '0000-00-00 00:00:00')

    def __init__(self, comparison_id, possibility, timestamp):
        self.comparison_id = comparison_id
        self.possibility = possibility
        self.timestamp = timestamp
  

class Profiles(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.BigInteger, primary_key = True, nullable = False)
    name = db.Column(db.String(50), nullable = False)
    description = db.Column(db.String(300), nullable = True)
    ontime = db.Column(db.DateTime)

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.ontime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')



class Treatments(db.Model):
    __tablename__ = 'treatments'
    id = db.Column(db.BigInteger, primary_key = True, nullable = False)
    name = db.Column(db.String(50), nullable = False)
    description = db.Column(db.String(300), nullable = True)
    ontime = db.Column(db.DateTime)

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.ontime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class History(db.Model):
    __tablename__ = 'profile_treatment'
    id = db.Column(db.BigInteger, primary_key = True, nullable = False)
    user_id = db.Column(db.BigInteger, ForeignKey("users.id"), nullable = False)
    profile_id = db.Column(db.BigInteger, ForeignKey("profiles.id"), nullable = False)
    treatment_id = db.Column(db.BigInteger, ForeignKey("treatments.id"), nullable = False)

    def __init__(self, user_id, profile_id, treatment_id):
        self.user_id = user_id
        self.profile_id = profile_id
        self.treatment_id = treatment_id


class Subscription(db.Model):
    __tablename__ = 'subscription'

    id = db.Column(db.BigInteger, primary_key = True, nullable = False)
    key = db.Column(db.String(150), nullable = False)
    ontime = db.Column(db.DateTime, nullable = False)

    def __init__(self, key):
        self.key = key
        self.ontime =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')


