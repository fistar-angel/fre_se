from flask.ext.api import status
from datetime import datetime, date
from sqlalchemy import exc, ForeignKey
from sqlalchemy.orm import relationship
from jsonschema import Draft4Validator
import validictory
from flask_negotiate import consumes, produces
from updateOrionSubService import *
from model import *

# fiware security (idM GE)
from decorators import *

# import notifier module
import sys
sys.path.append("/opt/fre_package/orion2mysql/")
from notifier import *


__version__ = "1.0"


@app.errorhandler(400)
def bad_request(msg):
    resp = jsonify(error={"code": 400, "reason": "Bad request"})
    resp.status_code = 400
    return resp

@app.errorhandler(404)
def not_found(msg):
    resp = jsonify(error={"code": 404, "reason": "Not found"})
    resp.status_code = 404
    return resp

@app.errorhandler(405)
def invalid_method(msg):
    resp = jsonify(error={"code": 405, "reason": "Method not allowed"})
    resp.status_code = 405
    return resp

@app.errorhandler(406)
def invalid_accept_method(msg):
    resp = jsonify(error={"code": 406, "reason": "Not Acceptable", "details": "Use Accept: application/json"})
    resp.status_code = 406
    return resp    

@app.errorhandler(415)
def invalid_method(msg):
    resp = jsonify(error={"code": 415, "reason": "Unsupported Media Type", "details": "Use Content-Type: application/json"})
    resp.status_code = 415
    return resp

@app.errorhandler(500)
def internal_error(msg):
    resp = jsonify(error={"code": 500, "reason": "Internal server error"})
    resp.status_code = 500
    return resp

def sqlalchemy_error_404(message):
    """
    Handle sqlalchemy error
    """
    resp = jsonify(error={"code": 404, "reason": message})
    resp.status_code = 404
    return resp

def key_error(message):
    """
    Handle KeyError exception
    """
    resp = jsonify(error={"code": 400, "reason": message})
    resp.status_code = 400
    return resp

def handle_exception(code, message):
    resp = jsonify(error={"code": code, "reason": message})
    resp.status_code = code
    return resp


@app.route('/medstaff', methods=['POST'])
@produces('application/json')
@requires_auth
def doctors():
    """
    Create a doctor instance 
    """

    if request.method == 'POST':
        try:
            # Check header
            try:
                if request.headers['Content-Type'] != 'application/json':
                    return invalid_accept_method(415)
            except NameError:
                return invalid_accept_method(415)

            # Validate JSON structure
            payload = None
            try:
                payload = request.get_json(force = False) 
            except:
                raise KeyError("Invalid JSON payload: " + request.url)           

            if payload is False:
                raise Exception("Invalid JSON payload: " + request.url)

            if payload is None:
                raise Exception("Empty JSON payload: " + request.url)

            # Payload validation 
            try:
                schema = getValidDoctorSchema()
                validictory.validate(payload,schema)
            except ValueError as v:
                raise Exception(v.args[0])

            # validate group ID
            if validateDoctorUsername(payload["username"]) == False:
                return bad_request("400")


            # add a new doctor 
            doctor = Doctors(payload['name'], payload['surname'], payload['username'], payload['speciality'],\
                payload['birthdate'], payload['email'], payload['phone'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            db.session.add(doctor)
            db.session.commit()

            # retrieve the instance of inserted user
            counter = 0
            results = Doctors.query.filter_by(id=doctor.id)
            for result in results:
                counter += 1
                doctor = {'id': result.id,
                    'name': result.name,
                    'surname': result.surname,
                    'username': result.username,
                    'speciality': result.speciality,
                    'birthdate': result.birth_date.strftime("%Y-%m-%d"),
                    'email': result.email,
                    'phone': result.phone,
                    'last_login': result.last_login.strftime("%Y-%m-%d %H:%M:%S"),
                    'registration': result.registration.strftime("%Y-%m-%d %H:%M:%S")
                }

            # return added user instance
            if counter == 1:
                mail = Email.default_settings()
                receiver = list()
                receiver.append(payload['email'])
                text = 'Dear medical staff member, ' + str(payload["name"]) + ' ' + str(payload["surname"]) + ',\n\n'
                text += 'Your registration in the FRE Platform was completed successfully!\n'
                text += 'Your available username is: ' + str(payload["username"]) + '.\n\n'
                text += 'Sincerely,\nThe administrator team'
                #send notification related to member registration
                mail.send_email(receiver, text)

                resp = jsonify(response={"medstaff": doctor})
                resp.status_code = 201
                return resp
            else:
                return not_found(404)
        except Exception, e:
            return handle_exception(400, e.args[0])
        except KeyError, k:
            return key_error(k.args[0])
        except exc.SQLAlchemyError as k:
            return sqlalchemy_error_404(k.args[0])
        except:
            return internal_error("500")

@app.route('/medstaff/<string:doc_id>', methods=['GET','PUT', 'DELETE'])
@produces('application/json')
@requires_auth
def doctor(doc_id):
    """
    Retrieve/Update/Delete a doctor instance
    """

    if request.headers['Accept'] != 'application/json' or request.headers['Accept'] == None:
        return invalid_accept_method("406")

    try: 
        val = int(doc_id)
        pass
    except ValueError:
        bad_request("Invalid medstaff id/username")


    if request.method == 'GET':
        try:
            rows = Doctors.query.filter_by(username=doc_id).count()
            if rows == 0:
                raise Exception("Not found")

            results = Doctors.query.filter_by(username=doc_id).limit(1)
            for result in results:
                instance = {'id': result.id,
                    'name': result.name,
                    'surname': result.surname,
                    'username': result.username,
                    'speciality': result.speciality,
                    'birthdate': result.birth_date.strftime("%Y-%m-%d"),
                    'email': result.email,
                    'phone': result.phone,
                    'last_login': result.last_login.strftime("%Y-%m-%d %H:%M:%S"),
                    'registration': result.registration.strftime("%Y-%m-%d %H:%M:%S")
                }

            resp = jsonify(response={"medstaff": instance})
            resp.status_code = 200
            return resp

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

    elif request.method == 'PUT':
        try:
            # Check header
            try:
                if request.headers['Content-Type'] != 'application/json':
                    return invalid_method(415)
            except NameError:
                return invalid_method(415)

            # Validate JSON structure
            payload = None
            try:
                payload = request.get_json(force = False) 
            except:
                raise KeyError("Invalid JSON payload: " + request.url)           

            if payload is False:
                raise Exception("Invalid JSON payload: " + request.url)

            if payload is None:
                raise Exception("Empty JSON payload: " + request.url)

            # Payload validation 
            try:
                schema = getValidDoctorSchema()
                validictory.validate(payload,schema)
            except ValueError as v:
                raise Exception(v.args[0]) 

            # validate group ID
            existDoctor = Doctors.query.filter_by(username=doc_id)   
            for i in existDoctor:
                existUsername = i.username
            if validateDoctorUsername(payload["username"]) == False and existUsername != payload["username"]:
                raise Exception("Property username is unique") 
  

            list = dict(name=payload['name'], 
                surname=payload['surname'],
                username=payload['username'],
                speciality=payload['speciality'],
                birth_date=payload['birthdate'], 
                email=payload['email'], 
                phone=payload['phone'],
                last_login=datetime.now().strftime("%Y-%m-%d"))

            user = Doctors.query.filter_by(username=doc_id).update(list)
            db.session.commit()
            
            # return updated user info
            results = Doctors.query.filter_by(username=doc_id).limit(1)
            counter = 0
            for row in results:
                counter += 1
                doc = {'id': row.id,
                    'name': row.name,
                    'surname': row.surname,
                    'username': row.username,
                    'speciality': row.speciality,
                    'birthdate': row.birth_date.strftime("%Y-%m-%d"),
                    'email': row.email,
                    'phone': row.phone,
                    'last_login': row.last_login.strftime("%Y-%m-%d %H:%M:%S"),
                    'registration': row.registration.strftime("%Y-%m-%d %H:%M:%S")
                }

            if counter == 1:
                return jsonify(response={"medstaff": doc}), status.HTTP_200_OK
            else:
                return not_found(404)
        except Exception, e:
            return handle_exception(400, e.args[0])
        except KeyError, k:
            return key_error(k.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

    elif request.method == 'DELETE':
        try:
            if Doctors.query.filter_by(username=doc_id).count() == 0:
                raise Exception("Not found")

            # delete the associated users' instances
            users = db.session.query(Users).\
                filter(Doctors.username == doc_id).\
                filter(Users.doctor_id == Doctors.id).all()
            for instance in users:
                deleteUser(instance.id)

            doc = Doctors.query.filter_by(username=doc_id).first()
            db.session.delete(doc)
            db.session.commit()
            return '', status.HTTP_200_OK

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)


def getValidDoctorSchema():
    """ Retrieve the valid schema of the doctor payload """

    schema = {"$schema": "http://json-schema.org/schema#",
            "type": "object",
            "additionalProperties": False,
            "properties":
            {
                "name": {"pattern": "^([a-zA-Z'\- ]{3,50})$" },
                "surname": {"pattern": "^([a-zA-Z'\- ]{3,50})$" },
                "username": {"pattern": "^(([a-zA-Z0-9\-]){6,100})$"},
                "speciality": {"type": "string"},
                "birthdate": {"pattern": "^(19[0-9]{2}|[2-9][0-9]{3})-((0(1|3|5|7|8)|10|12)-(0[1-9]|1[0-9]|2[0-9]|3[0-1])|(0(4|6|9)|11)-(0[1-9]|1[0-9]|2[0-9]|30)|(02)-(0[1-9]|1[0-9]|2[0-9]))$"},
                "email": {"pattern": "^(([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+)$"},
                "phone": {"pattern": "^([0-9]{10,})$"}
            },
            "required": ["name", "surname", "username", "speciliaty", "birthdate", "email", "phone"]
        }
    return schema 



@app.route('/users', methods=['GET', 'POST'])
@requires_auth
@produces('application/json')
def users():
    """
    Request pattern: http://<host:port>/users

    Supported methods:
    1. GET method: return the list of all users' instances
    2. POST method: create a new user instance and return this instance
    """

    # retrieve a list of users' instances
    if request.method == 'GET':
        try:

            # Check if user's doctor exists. Otherwise, raise an exception
            try:
                for i in request.args:
                    if i not in ["medstaffID"]:
                        return handle_exception(400, "The only query parameter that is allowed (and required) is the medstaffID.")    
                if len(request.args) != 1:
                    return handle_exception(400, "The only query parameter that is allowed (and required) is the medstaffID.")
                
                doctor_username = request.args.get('medstaffID')
                if doctor_username == None:
                    raise Exception("None value of the parameter medstaffID")
                if Doctors.query.filter_by(username=doctor_username).count() != 1:
                    raise Exception("No valid query parameter medstaffID")
            except ValueError, v:
                return bad_request(v.args[0])

            # associate doctor with its patients
            results = db.session.query(Users).\
                filter(Doctors.username == doctor_username).\
                filter(Users.doctor_id == Doctors.id).all()
      
            # retrieve records
            json_results = []
            for result in results:
                d = {'id': result.id,
                'name': result.name,
                'surname': result.surname,
                'uid': result.uid,
                'birthdate': result.birth_date.strftime("%Y-%m-%d"),
                'email': result.email,
                'phone': result.phone,
                'timezone': result.timezone,
                'profile': result.profile,
                'treatment': result.treatment,
                'registration': result.registration_date.strftime("%Y-%m-%d %H:%M:%S")
                }
                json_results.append(d)

            resp = jsonify(response={"users": json_results})
            resp.status_code = 200
            return resp

        except Exception, e:
            return handle_exception(400, e.args[0])
        except exc.SQLAlchemyError as s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error("500")                 

    # create new user instance 
    elif request.method == 'POST':
        try:
            # Check header
            try:
                if request.headers['Content-Type'] != 'application/json':
                    return invalid_accept_method(415)
            except NameError:
                return invalid_accept_method(415)

            # Validate JSON structure
            payload = None
            try:
                payload = request.get_json(force = False) 
            except:
                raise KeyError("Invalid JSON payload: " + request.url)           

            if payload is False:
                raise Exception("Invalid JSON payload: " + request.url)

            if payload is None:
                raise Exception("Empty JSON payload: " + request.url)

            # Payload validation 
            try:
                schema = getValidUserSchema()
                validictory.validate(payload,schema)
            except ValueError as v:
                raise Exception(v.args[0])

            # validate group ID
            if validateUID(payload["uid"]) == False:
                raise Exception("Invalid uid") 

            # retrieve instance
            doctorInstance = Doctors.query.filter_by(username=payload["medstaffID"]).all()
            if len(doctorInstance) !=1: 
                #raise Exception("Invalid medStaffID parameter")
                return not_found(404)

            # add new user 
            group = 2
            user = Users(payload['name'], payload['surname'], payload['uid'], group, payload['birthdate'],\
                payload['email'], payload['phone'], payload['timezone'], doctorInstance[0].id, payload['profile'], payload['treatment'])
            db.session.add(user)
            db.session.commit()

            # retrieve the instance of inserted user
            counter = 0
            results = Users.query.filter_by(id=user.id)
            for result in results:
                counter += 1
                user = {'id': result.id,
                    'name': result.name,
                    'surname': result.surname,
                    'uid': result.uid,
                    'birthdate': result.birth_date.strftime("%Y-%m-%d"),
                    'email': result.email,
                    'phone': result.phone,
                    'timezone': result.timezone,
                    'profile': result.profile,
                    'treatment': result.treatment,
                    'registration': result.registration_date.strftime("%Y-%m-%d %H:%M:%S")
                }

            # return added user instance
            if counter == 1:
                # send notification related to the user registration
                mail = Email.default_settings()
                receiver = list()
                receiver.append(payload['email'])
                text = 'Dear user, ' + str(payload["name"]) + ' ' + str(payload["surname"]) + ',\n\n'
                text += 'Your registration in the FRE Platform was completed successfully!\n'
                text += 'Your available SSN is: ' + str(payload["uid"]) + '.\n\n'
                text += 'Sincerely,\nThe administrator team'
                #send notification related to member registration
                mail.send_email(receiver, text)

                resp = jsonify(response={"user": user})
                resp.status_code = 201
                return resp
            else:
                return not_found(404)
        except Exception, e:
            return handle_exception(400, e.args[0])
        except KeyError, k:
            return key_error(k.args[0])
        except exc.SQLAlchemyError as k:
            return sqlalchemy_error_404(k.args[0])
        except:
            return internal_error("500")

@app.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@requires_auth
@produces('application/json')
def user(user_id):
    """
    Request pattern: http://<host:port>/users/{id}

    Supported methods:
    1. Get method: Return the user instance as JSON structure
    2. PUT method: Update the user instance and return it
    3. DELETE method: Delete the user instance
    """

        # validate Accept header
    if request.headers['Accept'] != 'application/json' or request.headers['Accept'] == None:
        return invalid_accept_method("406")

    try: 
        val = int(user_id)
        pass
    except ValueError:
        bad_request("Invalid user id")

    # Check if user's doctor exists. Otherwise, raise an exception
    try:
        for i in request.args:
            if i not in ["medstaffID"]:
                return handle_exception(400, "The only query parameter that is allowed (and required) is the medstaffID.")
        
        if len(request.args) != 1:
            return handle_exception(400, "The only query parameter that is allowed (and required) is the medstaffID.")    
        
        doctor_username = request.args.get('medstaffID')
        if doctor_username == None:
            raise Exception("None value of the parameter medstaffID")
        if Doctors.query.filter_by(username=doctor_username).count() != 1:
            raise Exception("No valid value of query parameter medstaffID")
    except ValueError, v:
        return bad_request(v.args[0])
    except Exception, e:
        return handle_exception(404, e.args[0])


    if request.method == 'GET':
        try:
            rows = Users.query.filter_by(id=user_id).count()
            if rows == 0:
                raise Exception("Not found")

            # check relationship between doctor and user
            if doctor2UserRelationship(doctor_username, user_id) == False:
                raise Exception("Not found relationship between user and medical staff")

            # retrieve a user instance, if he/she is asociated with doctor
            results = db.session.query(Users).\
                filter(Doctors.username == doctor_username).\
                filter(Users.doctor_id == Doctors.id).\
                filter(Users.id == user_id).all()

            for result in results:
                user = {'id': result.id,
                    'name': result.name,
                    'surname': result.surname,
                    'uid': result.uid,
                    'birthdate': result.birth_date.strftime("%Y-%m-%d"),
                    'email': result.email,
                    'phone': result.phone,
                    'timezone': result.timezone,
                    'profile': result.profile,
                    'treatment': result.treatment,
                    'registration': result.registration_date.strftime("%Y-%m-%d %H:%M:%S")
                }

            resp = jsonify(response={"user": user})
            resp.status_code = 200
            return resp

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

    elif request.method == 'PUT':
        try:
            # Check header
            try:
                if request.headers['Content-Type'] != 'application/json':
                    return invalid_method(415)
            except NameError:
                return invalid_method(415)

            # Validate JSON structure
            payload = None
            try:
                payload = request.get_json(force = False) 
            except:
                raise KeyError("Invalid JSON payload: " + request.url)           

            if payload is False:
                raise Exception("Invalid JSON payload: " + request.url)

            if payload is None:
                raise Exception("Empty JSON payload: " + request.url)

            # Payload validation 
            try:
                schema = getValidUserSchemaB()
                validictory.validate(payload,schema)
            except ValueError as v:
                raise Exception(v.args[0]) 

            # validate group ID
            existUser = Users.query.filter_by(id=user_id)   
            for i in existUser:
                existUID = i.uid
            if validateUID(payload["uid"]) == False and existUID != payload["uid"]:
                raise Exception("Invalid uid") 

            # check relationship between doctor and user
            if doctor2UserRelationship(doctor_username, user_id) == False:
                raise Exception("Not found relationship between user and medical staff")
                     
            # retrieve instance
            doctorInstance = Doctors.query.filter_by(username=doctor_username).first()  

            list = dict(name=payload['name'], 
                surname=payload['surname'],
                uid=payload['uid'],
                group_id=2,
                birth_date=payload['birthdate'], 
                email=payload['email'], 
                phone=payload['phone'],
                timezone=payload['timezone'],
                profile=payload['profile'],
                treatment=payload['treatment'],
                doctor_id=doctorInstance.id
                )

            user = Users.query.filter_by(id=user_id).update(list)
            db.session.commit()
            
            # return updated user info
            results = Users.query.filter_by(id=user_id).limit(1)
            counter = 0
            for row in results:
                counter += 1
                uuser = {'id': row.id,
                    'name': row.name,
                    'surname': row.surname,
                    'uid': row.uid,
                    'birthdate': row.birth_date.strftime("%Y-%m-%d"),
                    'email': row.email,
                    'phone': row.phone,
                    'timezone': row.timezone,
                    'profile': row.profile,
                    'treatment': row.treatment,
                    'registration': row.registration_date.strftime("%Y-%m-%d %H:%M:%S")
                }

            if counter == 1:
                return jsonify(response={"user": uuser}), status.HTTP_200_OK
            else:
                return not_found(404)
        except Exception, e:
            return handle_exception(400, e.args[0])
        except KeyError, k:
            return key_error(k.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

    elif request.method == 'DELETE':
        try:
            if Users.query.filter_by(id=user_id).count() == 0:
                raise Exception("Not found")

            # check relationship between doctor and user
            if doctor2UserRelationship(doctor_username, user_id) == False:
                raise Exception("Not found relationship between user and medical staff")


            # delete the associated measurement instances
            deleteUser(user_id)

            """
            measurements = Measurements.query.filter_by(user_id=user_id).all()
            for i in measurements:
                deleteMeasurement(i)
            user = Users.query.get(user_id)
            db.session.delete(user)
            db.session.commit()
            """

            return '', status.HTTP_200_OK

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

@app.route('/users/schema', methods=['GET'])
@requires_auth
@produces('application/json')
def userSchema():
    if request.method == 'GET':
        schema = getValidUserSchema()
        resp = jsonify(schema)
        resp.status_code = 200
        return resp

def getValidUserSchema():
    """ Retrieve the valid schema of the user payload """

    schema = {"$schema": "http://json-schema.org/schema#",
            "type": "object",
            "additionalProperties": False,
            "properties":
            {
                "name": {"pattern": "^([a-zA-Z'\- ]{3,50})$" },
                "surname": {"pattern": "^([a-zA-Z'\- ]{3,50})$" },
                "uid": {"pattern": "^(([a-zA-Z0-9]){8,50})$"},
                "birthdate": {"pattern": "^(19[0-9]{2}|[2-9][0-9]{3})-((0(1|3|5|7|8)|10|12)-(0[1-9]|1[0-9]|2[0-9]|3[0-1])|(0(4|6|9)|11)-(0[1-9]|1[0-9]|2[0-9]|30)|(02)-(0[1-9]|1[0-9]|2[0-9]))$"},
                "email": {"pattern": "^(([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+)$"},
                "phone": {"pattern": "^([0-9]{10,})$"},
                "timezone": {"pattern": "^(Asia|Africa|Australia|America|Europe|[a-zA-Z]|UTC)\/([a-zA-Z]{3,})$"},
                "medstaffID" : {"pattern": "^(([a-zA-Z0-9\-]){6,100})$"},
                "profile": {"type": "string", "minLength":1, "maxLength":300},
                "treatment": {"type": "string", "minLength":1, "maxLength":300}
            },
            "required": ["name", "surname", "uid", "birthdate", "email", "phone", "timezone", "medstaffID", "profile", "treatment"]
        }
    return schema 

def getValidUserSchemaB():
    """ Retrieve the valid schema of the user payload """

    schema = {"$schema": "http://json-schema.org/schema#",
            "type": "object",
            "additionalProperties": False,
            "properties":
            {
                "name": {"pattern": "^([a-zA-Z'\- ]{3,50})$" },
                "surname": {"pattern": "^([a-zA-Z'\- ]{3,50})$" },
                "uid": {"pattern": "^(([a-zA-Z0-9]){8,50})$"},
                "birthdate": {"pattern": "^(19[0-9]{2}|[2-9][0-9]{3})-((0(1|3|5|7|8)|10|12)-(0[1-9]|1[0-9]|2[0-9]|3[0-1])|(0(4|6|9)|11)-(0[1-9]|1[0-9]|2[0-9]|30)|(02)-(0[1-9]|1[0-9]|2[0-9]))$"},
                "email": {"pattern": "^(([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+)$"},
                "phone": {"pattern": "^([0-9]{10,})$"},
                "timezone": {"pattern": "^(Asia|Africa|Australia|America|Europe|[a-zA-Z]|UTC)\/([a-zA-Z]{3,})$"},
                "profile": {"type": "string", "minLength":1, "maxLength":300},
                "treatment": {"type": "string", "minLength":1, "maxLength":300}
            },
            "required": ["name", "surname", "uid", "birthdate", "email", "phone", "timezone", "profile", "treatment"]
        }
    return schema

def doctor2UserRelationship(doctor_usr, user_id):
    """
    If there is relationship between doctor and user, then return True. Otherwise, return False.
    """

    association = db.session.query(Users).\
        filter(Doctors.username == doctor_usr).\
        filter(Users.doctor_id == Doctors.id).\
        filter(Users.id == user_id).all()
    if len(association) != 1:
        return False    
    return True


@app.route('/biologic_parameters', methods=['GET', 'POST'])
@requires_auth
@produces('application/json')
def biologicParameters():
    if request.method == 'GET':
        try:
            results = BiologicParameters.query.all()

            json_results = []
            counter = 0
            for result in results:
                counter += 1
                d = {'id': result.id,
                    'type': result.type,
                    'name': result.name,
                    'unit': result.unit
                }
                json_results.append(d)

            resp = jsonify(response={"biologic_parameters": json_results})
            resp.status_code = 200
            return resp

        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

    elif request.method == 'POST':
        try:
            # Check header
            try:
                if request.headers['Content-Type'] != 'application/json':
                    return invalid_method(415)
            except NameError:
                return invalid_method(415)

            # Validate JSON structure
            payload = None
            try:
                payload = request.get_json(force = False) 
            except:
                raise KeyError("Invalid JSON payload: " + request.url)           

            if payload is False:
                raise Exception("Invalid JSON payload: " + request.url)

            if payload is None:
                raise Exception("Empty JSON payload: " + request.url)

            # Payload validation 
            try:
                schema = getValidBiologicParameterSchema()
                validictory.validate(payload,schema)
            except ValueError as v:
                raise Exception(v.args[0])


            # unique parameter name constraint
            uniqueNameFlag = BiologicParameters.query.filter_by(name=payload['name']).count()
            if uniqueNameFlag > 0:
                raise Exception("Name property is unique")

            bParam = BiologicParameters(payload['name'], payload['type'], payload['unit'])
            # add new biologic parameter (get id)
            db.session.add(bParam)
            db.session.commit()

            # retrieve the instance of inserted biologic parameter
            results = BiologicParameters.query.filter_by(id=bParam.id).limit(1)
            json_results = []
            counter = 0
            for result in results:
                counter += 1
                d = {'id': result.id,
                    'name': result.name,
                    'type': result.type,
                    'unit': result.unit
                    }

                json_results.append(d)

            # update orion context broker GE subscription
            subObj = OrionContextBrokerSub()
            subObj.updateSubscriptionContext()

            if counter == 1:
                resp = jsonify(response={"biologic_parameter": json_results})
                resp.status_code = 201
                return resp
            else:
                return not_found(404)
        except Exception, e:
            return handle_exception(400, e.args[0])
        except KeyError, k:
            return key_error(k.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

@app.route('/biologic_parameters/<int:param_id>', methods=['GET', 'PUT', 'DELETE'])
@requires_auth
@produces('application/json')
def biologicParameter(param_id):

    if isInteger(param_id) == False:
        return bad_request(400)
   
    if request.method == 'GET':
        try:
            # retrieve URI resource
            if BiologicParameters.query.filter_by(id=param_id).count() == 0:
                raise Exception("Not found")
            results = BiologicParameters.query.filter_by(id=param_id).limit(1)

            json_results = []
            for result in results:
                biologic_parameter = {
                    'id': result.id,
                    'type': result.type,
                    'name': result.name,
                    'unit': result.unit
                }

            resp = jsonify(response={"biologic_parameter": biologic_parameter})
            resp.status_code = 200
            return resp

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

    elif request.method == 'PUT':
        try:
            # Check header
            try:
                if request.headers['Content-Type'] != 'application/json':
                    return invalid_method(415)
            except NameError:
                return invalid_method(415)

            # Validate JSON structure
            payload = None
            try:
                payload = request.get_json(force = False) 
            except:
                raise KeyError("Invalid JSON payload: " + request.url)           

            if payload is False:
                raise Exception("Invalid JSON payload: " + request.url)

            if payload is None:
                raise Exception("Empty JSON payload: " + request.url)

            # Payload validation 
            try:
                schema = getValidBiologicParameterSchema()
                validictory.validate(payload,schema)
            except ValueError as v:
                raise Exception(v.args[0])

            # check name constraint
            instances = BiologicParameters.query.filter_by(name=payload['name']).all()
            if len(instances) == 0:
                pass
            elif len(instances) == 1:
                for instance in instances:
                    if instance.id != param_id:
                        raise Exception("Name property is unique")        
            else:
                raise Exception("Name property is unique")
        
            # update query
            b_param = BiologicParameters.query.filter_by(id=param_id).update(payload)
            db.session.commit()

            # return updated user info
            results = BiologicParameters.query.filter_by(id=param_id).limit(1)

            counter = 0
            for result in results:
                counter += 1
                biologic_parameter = {
                    'id': result.id,
                    'type': result.type,
                    'name': result.name,
                    'unit': result.unit
                }

            # update orion context broker GE subscription
            subObj = OrionContextBrokerSub()
            subObj.updateSubscriptionContext()

            if counter == 1:
                return jsonify(response={"biologic_parameter": biologic_parameter}), status.HTTP_200_OK
            else:
                return not_found(404)
        except Exception, e:
            return handle_exception(400, e.args[0])
        except KeyError, k:
            return key_error(k.args[0])
        except exc.SQLAlchemyError, k:
            return sqlalchemy_error_404(k.args[0])
        except:
            return internal_error(500)

    elif request.method == 'DELETE':
        try:

            if BiologicParameters.query.filter_by(id=param_id).count() == 0:
                raise Exception("Not found")

            # delete a parameter
            deleteParameter(param_id)

            """
            measurements = Measurements.query.filter_by(biological_parameter_id=param_id).all()
            for i in measurements:
                deleteMeasurement(i)
                #db.session.delete(i)
                #db.session.commit()

            # delete parameter instance
            b_param = BiologicParameters.query.get(param_id)
            db.session.delete(b_param)
            db.session.commit()
            """

            # update orion context broker GE subscription
            subObj = OrionContextBrokerSub()
            subObj.updateSubscriptionContext()

            return '', status.HTTP_200_OK

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

@app.route('/biologic_parameters/schema', methods=['GET'])
@requires_auth
@produces('application/json')
def biologicParameterSchema():
    if request.method == 'GET':
        schema = getValidBiologicParameterSchema()
        resp = jsonify(schema)
        resp.status_code = 200
        return resp

def getValidBiologicParameterSchema():
    """ Retrieve the valid schema of the biologic parameter payload """

    schema = {"$schema": "http://json-schema.org/schema#",
            "type": "object",
            "additionalProperties": False,
            "properties":
            {
                "name": {"pattern": "^([a-zA-Z ]+)$" },
                "type": {"pattern": "^((null)|([a-zA-Z0-9'\- ]+))$"},
                "unit": {"type": "string", "minLength":1, "maxLength": 50}
            },
            "required": ["name", "unit"]
        }

    return schema    


@app.route('/rules', methods=['GET', 'POST'])
@requires_auth
@produces('application/json')
def rules():
    if request.method == 'GET':
        try:
            results = Rules.query.all()

            json_results = []
            counter = 0
            for result in results:
                counter += 1

                # load info related to the current biological_parameter_id
                biologic_param = BiologicParameters.query.get(result.biological_parameter_id)

                d = {'id': result.id,
                    'biological_parameter_id': result.biological_parameter_id,
                    'biological_parameter_name': biologic_param.name,
                    'optimal_value': result.optimal_value,
                    'acceptable_low_threshold': result.critical_low_threshold,
                    'acceptable_high_threshold': result.critical_high_threshold,
                    'normal_low_threshold': result.acceptable_low_threshold,
                    'normal_high_threshold': result.acceptable_high_threshold,
                    'unit': biologic_param.unit
                   }
                json_results.append(d)

            resp = jsonify(response={"rules": json_results})
            resp.status_code = 200
            return resp

        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

    elif request.method == 'POST':
        try:
            # Check header
            try:
                if request.headers['Content-Type'] != 'application/json':
                    return invalid_method(415)
            except NameError:
                return invalid_method(415)

            # Validate JSON structure
            payload = None
            try:
                payload = request.get_json(force = False) 
            except:
                raise KeyError("Invalid JSON payload: " + request.url)           

            if payload is False:
                raise Exception("Invalid JSON payload: " + request.url)

            if payload is None:
                raise Exception("Empty JSON payload: " + request.url)

            # Payload validation 
            try:
                schema = getValidRuleSchema()
                validictory.validate(payload,schema)
            except ValueError as v:
                raise Exception(v.args[0])


            rule = Rules(payload['biological_parameter_id'], payload['optimal_value'], payload['acceptable_low_threshold'], payload['acceptable_high_threshold'], 
                    payload['normal_low_threshold'], payload['normal_high_threshold'])
            # add new rule (get id)
            db.session.add(rule)
            db.session.commit()

            # retrieve the instance of inserted user
            results = Rules.query.filter_by(id=rule.id).limit(1)
            json_results = []
            counter = 0
            for result in results:
                counter += 1
                # load info related to the current biological_parameter_id
                biologic_param = BiologicParameters.query.get(result.biological_parameter_id)
                d = {'id': result.id,
                    'biological_parameter_id': result.biological_parameter_id,
                    'biological_parameter_name': biologic_param.name,
                    'optimal_value': result.optimal_value,
                    'acceptable_low_threshold': result.critical_low_threshold,
                    'acceptable_high_threshold': result.critical_high_threshold,
                    'normal_low_threshold': result.acceptable_low_threshold,
                    'normal_high_threshold': result.acceptable_high_threshold,
                    'unit': biologic_param.unit
                    }

                json_results.append(d)

            if counter == 1:
                resp = jsonify(response={"rule": json_results})
                resp.status_code = 201
                return resp
            else:
                return not_found(404)
        except Exception, e:
            return handle_exception(400, e.args[0])
        except KeyError, k:
            return key_error(k.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

@app.route('/rules/<int:rule_id>', methods=['GET', 'PUT', 'DELETE'])
@requires_auth
@produces('application/json')
def rule(rule_id):

    if isInteger(rule_id) == False:
        return bad_request(400)
   
    if request.method == 'GET':
        try:
            # retrieve URI resource

            if Rules.query.filter_by(id=rule_id).count() == 0:
                raise Exception("Not found")
            results = Rules.query.filter_by(id=rule_id).limit(1)

            json_results = []
            for result in results:
                # load info related to the current biological_parameter_id
                biologic_param = BiologicParameters.query.get(result.biological_parameter_id)
                d = {'id': result.id,
                    'biological_parameter_id': result.biological_parameter_id,
                    'biological_parameter_name': biologic_param.name,
                    'optimal_value': result.optimal_value,
                    'acceptable_low_threshold': result.critical_low_threshold,
                    'acceptable_high_threshold': result.critical_high_threshold,
                    'normal_low_threshold': result.acceptable_low_threshold,
                    'normal_high_threshold': result.acceptable_high_threshold,
                    'unit': biologic_param.unit
                   }
                json_results.append(d)

            resp = jsonify(response={"rule": json_results})
            resp.status_code = 200
            return resp

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

    elif request.method == 'PUT':
        try:
            # Check header
            try:
                if request.headers['Content-Type'] != 'application/json':
                    return invalid_method(415)
            except NameError:
                return invalid_method(415)

            # Validate JSON structure
            payload = None
            try:
                payload = request.get_json(force = False) 
            except:
                raise KeyError("Invalid JSON payload: " + request.url)           

            if payload is False:
                raise Exception("Invalid JSON payload: " + request.url)

            if payload is None:
                raise Exception("Empty JSON payload: " + request.url)

            # Payload validation 
            try:
                schema = getValidRuleSchema()
                validictory.validate(payload,schema)
            except ValueError as v:
                raise Exception(v.args[0])

            # update query
            list = dict(optimal_value=payload['optimal_value'], critical_high_threshold=payload['acceptable_high_threshold'],
                critical_low_threshold=payload['acceptable_low_threshold'], biological_parameter_id = payload["biological_parameter_id"],
                acceptable_low_threshold = payload["normal_low_threshold"], acceptable_high_threshold = payload["normal_high_threshold"])
            rule = Rules.query.filter_by(id=rule_id).update(list)
            db.session.commit()

            # return updated user info
            results = Rules.query.filter_by(id=rule_id).limit(1)

            json_results = []
            counter = 0
            for result in results:
                counter += 1
                # load info related to the current biological_parameter_id
                biologic_param = BiologicParameters.query.get(result.biological_parameter_id)
                d = {'id': result.id,
                    'biological_parameter_id': result.biological_parameter_id,
                    'biological_parameter_name': biologic_param.name,
                    'optimal_value': result.optimal_value,
                    'acceptable_low_threshold': result.critical_low_threshold,
                    'acceptable_high_threshold': result.critical_high_threshold,
                    'normal_low_threshold': result.acceptable_low_threshold,
                    'normal_high_threshold': result.acceptable_high_threshold,
                    'unit': biologic_param.unit
                    }

                json_results.append(d)

            if counter == 1:
                return jsonify(response={"rule": json_results}), status.HTTP_200_OK
            else:
                return not_found(404)
        except Exception, e:
            return handle_exception(400, e.args[0])
        except KeyError, k:
            return key_error(k.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

    elif request.method == 'DELETE':
        try:

            if Rules.query.filter_by(id=rule_id).count() == 0:
                raise Exception("Not found")

            rule = Rules.query.get(rule_id)
            deleteRule(rule)

            return '', status.HTTP_200_OK

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

@app.route('/rules/schema', methods=['GET'])
@requires_auth
@produces('application/json')
def ruleShcema():
    if request.method == 'GET':
        schema = getValidRuleSchema()
        resp = jsonify(schema)
        resp.status_code = 200
        return resp

def getValidRuleSchema():
    """ Retrieve the valid schema of the rule payload """

    schema = {"$schema": "http://json-schema.org/schema#",
            "type": "object",
            "additionalProperties": False,
            "properties":
            {
                "biological_parameter_id": {"pattern": "^([0-9]+)$" },
                "optimal_value": {"pattern": "^([-+]?[0-9]*\.?[0-9]*)$"},
                "acceptable_low_threshold": {"pattern": "^([-+]?[0-9]*\.?[0-9]*)$"},
                "acceptable_high_threshold": {"pattern": "^([-+]?[0-9]*\.?[0-9]*)$"},
                "normal_low_threshold": {"pattern": "^null|([-+]?[0-9]*\.?[0-9]*)$"},
                "normal_high_threshold": {"pattern": "^(null|[-+]?[0-9]*\.?[0-9]*)$"}
            },
            "required": ["biological_parameter_id", "optimal_value", "critical_low_threshold", "critical_high_threshold"]
        }

    return schema    


@app.route('/users/<int:user_id>/measurements', methods=['GET'])
@requires_auth
@produces('application/json')
def measurements(user_id):
    """
    Supported endpoint pattern: /users/{id}/measurements?medstaffID={username}
    """

    if request.method == 'GET':
        try:

            # Check if user's doctor exists. Otherwise, raise an exception
            try:
                if len(request.args) != 1:
                    return handle_exception(400, "The only query parameter that is allowed (and required) is the medstaffID.")
                
                doctor_username = request.args.get('medstaffID')
                if doctor_username == None:
                    raise Exception("None value of the parameter medstaffID")
                if Doctors.query.filter_by(username=doctor_username).count() != 1:
                    raise Exception("No valid query parameter medstaffID")
            except ValueError, v:
                return bad_request(v.args[0])


            if checkUserExistance(user_id) == 0:
                raise Exception("Not found")

            # check relationship between doctor and user
            if doctor2UserRelationship(doctor_username, user_id) == False:
                raise Exception("Not found relationship between user and medical staff")

            # query
            results = db.session.query(Measurements).\
                filter(Doctors.username == doctor_username).\
                filter(Users.doctor_id == Doctors.id).\
                filter(Users.id == Measurements.user_id).\
                filter(Users.id == user_id).\
                order_by(Measurements.timestamp.asc())

            json_results = []
            counter = 0
            for result in results:
                counter += 1

                biologic_param = BiologicParameters.query.get(result.biological_parameter_id)

                d = {'id': result.id,
                    'user_id': result.user_id,
                    'biological_parameter_id': result.biological_parameter_id,
                    'biological_parameter_name': biologic_param.name,
                    'unit': biologic_param.unit,
        	        'ontime': result.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    'value': round(result.value, 2)
                }
                json_results.append(d)

            return jsonify(response={'measurements': json_results}), status.HTTP_200_OK

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

@app.route('/users/<int:user_id>/measurements/recent', methods=['GET'])
@requires_auth
@produces('application/json')
def recentMeasurements(user_id):
    """
    Supported endpoint pattern: /users/{id}/measurements/recent?medstaffID={username}
    """

    if request.method == 'GET':
        try:

            # Check if user's doctor exists. Otherwise, raise an exception
            try:
                if len(request.args) != 1:
                    return handle_exception(400, "The only query parameter that is allowed (and required) is the medstaffID.")
                
                doctor_username = request.args.get('medstaffID')
                if doctor_username == None:
                    raise Exception("None value of the parameter medstaffID")
                if Doctors.query.filter_by(username=doctor_username).count() != 1:
                    raise Exception("No valid query parameter medstaffID")
            except ValueError, v:
                return bad_request(v.args[0])


            if checkUserExistance(user_id) == 0:
                raise Exception("Not found")

            # check relationship between doctor and user
            if doctor2UserRelationship(doctor_username, user_id) == False:
                raise Exception("Not found relationship between user and medical staff")

            results = db.session.query(Measurements).\
                filter(Doctors.username == doctor_username).\
                filter(Users.doctor_id == Doctors.id).\
                filter(Users.id == Measurements.user_id).\
                filter(Users.id == user_id).\
                order_by(Measurements.timestamp.desc()).limit(1)

            json_results = []
            counter = 0
            for result in results:
                counter += 1

                # retrieve biological parameter info
                biologic_param = BiologicParameters.query.get(result.biological_parameter_id)

                d = {'id': result.id,
                   'user_id': result.user_id,
                   'biological_parameter_id': result.biological_parameter_id,
                   'biological_parameter_name': biologic_param.name,
                   'unit': biologic_param.unit,
                   'timestamp': result.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                   'value': round(result.value, 2)
                   }
                json_results.append(d)

            return jsonify(response={'measurement': json_results}), status.HTTP_200_OK

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

@app.route('/users/<int:user_id>/measurements/<int:year_start>/<int:month_start>/<int:day_start>/<int:year_end>/<int:month_end>/<int:day_end>/', methods=['GET'])
@requires_auth
@produces('application/json')
def measurementsRange(user_id,year_start,month_start,day_start,year_end,month_end,day_end):
    """
    Supported endpoint pattern: /users/{id}/measurements/yyyy/mm/dd/yyyy/mm/dd/?medstaffID={username}
    """

    if request.method == 'GET':
        try:
            if not validateYear(year_start):
                raise Exception("year error")
            if not validateMonth(month_start):
                raise Exception("month error")
            if not validateDay(day_start):
                raise Exception("day error")

            if not validateYear(year_end):
                raise Exception("year error")
            if not validateMonth(month_end):
                raise Exception("month error")
            if not validateDay(day_end):
                raise Exception("day error")

            if checkUserExistance(user_id) == 0:
                raise Exception("Not user found")

           # Check if user's doctor exists. Otherwise, raise an exception
            try:
                if len(request.args) != 1:
                    return handle_exception(400, "The only query parameter that is allowed (and required) is the medstaffID.")
                
                doctor_username = request.args.get('medstaffID')
                if doctor_username == None:
                    raise Exception("None value of the parameter medstaffID")
                if Doctors.query.filter_by(username=doctor_username).count() != 1:
                    raise Exception("No valid query parameter medstaffID")
            except ValueError, v:
                return bad_request(v.args[0]) 

            start_date = datetime(year_start, month_start, day_start, 00, 00, 00).isoformat()
            end_date = datetime(year_end, month_end, day_end, 23, 59, 59).isoformat()

            # check relationship between doctor and user
            if doctor2UserRelationship(doctor_username, user_id) == False:
                raise Exception("Not found relationship between user and medical staff")

            # query
            results = db.session.query(Measurements).\
                filter(Doctors.username == doctor_username).\
                filter(Users.doctor_id == Doctors.id).\
                filter(Users.id == Measurements.user_id).\
                filter(Users.id == user_id).\
                filter(Measurements.timestamp >= start_date).\
                filter(Measurements.timestamp <= end_date).\
                order_by(Measurements.timestamp.asc())

            json_results = []
            counter = 0
            for result in results:
                counter += 1

                # retrieve biological parameter info
                biologic_param = BiologicParameters.query.get(result.biological_parameter_id)

                d = {'id': result.id,
                    'user_id': result.user_id,
                    'biological_parameter_id': result.biological_parameter_id,
                    'biological_parameter_name': biologic_param.name,
                    'unit': biologic_param.unit,
                    'timestamp': result.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    'value': result.value
                    }
                json_results.append(d)

            return jsonify(response={'measurements': json_results}), status.HTTP_200_OK

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

@app.route('/users/<int:user_id>/measurements/<int:biologic_param_id>', methods=['GET'])
@requires_auth
@produces('application/json')
def biologicParameterMeasurements(user_id, biologic_param_id):
    if request.method == 'GET':
        try:
            if checkUserExistance(user_id) == 0:
                raise Exception("Not found")

            if checkBiologicParameterExistance(biologic_param_id) == 0:
                raise Exception("Not found")
 
            # Check if user's doctor exists. Otherwise, raise an exception
            try:
                if len(request.args) != 1:
                    return handle_exception(400, "The only query parameter that is allowed (and required) is the medstaffID.")
                
                doctor_username = request.args.get('medstaffID')
                if doctor_username == None:
                    raise Exception("None value of the parameter medstaffID")
                if Doctors.query.filter_by(username=doctor_username).count() != 1:
                    raise Exception("No valid query parameter medstaffID")
            except ValueError, v:
                return bad_request(v.args[0])

            # check relationship between doctor and user
            if doctor2UserRelationship(doctor_username, user_id) == False:
                raise Exception("Not found relationship between user and medical staff")

            # query
            results = db.session.query(Measurements).\
                filter(Doctors.username == doctor_username).\
                filter(Users.doctor_id == Doctors.id).\
                filter(Users.id == user_id).\
                filter(Users.id == Measurements.user_id).\
                filter(Measurements.biological_parameter_id == biologic_param_id)

            json_results = []
            counter = 0
            for result in results:
                counter += 1
                # retrieve biological parameter info
                biologic_param = BiologicParameters.query.get(result.biological_parameter_id)

                d = {'id': result.id,
                   'user_id': result.user_id,
                   'biological_parameter_id': result.biological_parameter_id,
                   'biological_parameter_name': biologic_param.name,
                   'unit': biologic_param.unit,
                   'timestamp': result.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                   'value': result.value
                   }
                json_results.append(d)

            return jsonify(response={"measurements": json_results}), status.HTTP_200_OK

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

@app.route('/users/<int:user_id>/measurements/<int:biologic_param_id>/recent', methods=['GET'])
@requires_auth
@produces('application/json')
def recentBiologicParameterMeasurement(user_id, biologic_param_id):
    if request.method == 'GET':
        try:
            if checkUserExistance(user_id) == 0:
                raise Exception("Not found")

            if checkBiologicParameterExistance(biologic_param_id) == 0:
                raise Exception("Not found")

            # Check if user's doctor exists. Otherwise, raise an exception
            try:
                if len(request.args) != 1:
                    return handle_exception(400, "The only query parameter that is allowed (and required) is the medstaffID.")
                
                doctor_username = request.args.get('medstaffID')
                if doctor_username == None:
                    raise Exception("None value of the parameter medstaffID")
                if Doctors.query.filter_by(username=doctor_username).count() != 1:
                    raise Exception("No valid query parameter medstaffID")
            except ValueError, v:
                return bad_request(v.args[0])

            # check relationship between doctor and user
            if doctor2UserRelationship(doctor_username, user_id) == False:
                raise Exception("Not found relationship between user and medical staff")

            # query
            results = db.session.query(Measurements).\
                filter(Doctors.username == doctor_username).\
                filter(Users.doctor_id == Doctors.id).\
                filter(Users.id == Measurements.user_id).\
                filter(Users.id == user_id).\
                filter(Measurements.biological_parameter_id == biologic_param_id).\
                order_by(Measurements.timestamp.desc()).\
                limit(1)

            json_results = []
            counter = 0
            for result in results:
                counter += 1

                # retrieve biological parameter info
                biologic_param = BiologicParameters.query.get(result.biological_parameter_id)

                d = {'id': result.id,
                   'user_id': result.user_id,
                   'biological_parameter_id': result.biological_parameter_id,
                   'biological_parameter_name': biologic_param.name,
                   'unit': biologic_param.unit,
                   'timestamp': result.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                   'value': result.value
                   }
                json_results.append(d)

            return jsonify(response={"measurement": json_results}), status.HTTP_200_OK

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

@app.route('/users/<int:user_id>/measurements/<int:biologic_param_id>/<int:year_start>/<int:month_start>/<int:day_start>/<int:year_end>/<int:month_end>/<int:day_end>/', methods=['GET'])
@requires_auth
@produces('application/json')
def biologicParameterMeasurementsRange(user_id, biologic_param_id,year_start,month_start,day_start,year_end,month_end,day_end):
    if request.method == 'GET':
        try:
            if checkUserExistance(user_id) == 0:
                raise Exception("Not found")

            if checkBiologicParameterExistance(biologic_param_id) == 0:
                raise Exception("Not found")

            if not validateYear(year_start):
                raise Exception("year error")
            if not validateMonth(month_start):
                raise Exception("month error")
            if not validateDay(day_start):
                raise Exception("day error")

            if not validateYear(year_end):
                raise Exception("year error")
            if not validateMonth(month_end):
                raise Exception("month error")
            if not validateDay(day_end):
                raise Exception("day error")

            # define start and end datetimes
            start_date = datetime(year_start, month_start, day_start, 00, 00, 00).isoformat()
            end_date = datetime(year_end, month_end, day_end, 23, 59, 59).isoformat()

            # Check if user's doctor exists. Otherwise, raise an exception
            try:
                if len(request.args) != 1:
                    return handle_exception(400, "The only query parameter that is allowed (and required) is the medstaffID.")
                
                doctor_username = request.args.get('medstaffID')
                if doctor_username == None:
                    raise Exception("None value of the parameter medstaffID")
                if Doctors.query.filter_by(username=doctor_username).count() != 1:
                    raise Exception("No valid query parameter medstaffID")
            except ValueError, v:
                return bad_request(v.args[0])

            # check relationship between doctor and user
            if doctor2UserRelationship(doctor_username, user_id) == False:
                raise Exception("Not found relationship between user and medical staff")

            # query
            results = db.session.query(Measurements).\
                filter(Doctors.username == doctor_username).\
                filter(Users.doctor_id == Doctors.id).\
                filter(Users.id == Measurements.user_id).\
                filter(Users.id == user_id).\
                filter(Measurements.biological_parameter_id == biologic_param_id).\
                filter(Measurements.timestamp >= start_date).\
                filter(Measurements.timestamp <= end_date).\
                order_by(Measurements.timestamp.asc())

            json_results = []
            counter = 0
            for result in results:
                counter += 1

                # retrieve biological parameter info
                biologic_param = BiologicParameters.query.get(result.biological_parameter_id)

                d = {'id': result.id,
                   'user_id': result.user_id,
                   'biological_parameter_id': result.biological_parameter_id,
                   'biological_parameter_name': biologic_param.name,
                   'unit': biologic_param.unit,
                   'timestamp': result.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                   'value': result.value
                   }
                json_results.append(d)

            return jsonify(response={"measurements": json_results}), status.HTTP_200_OK

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)



@app.route('/users/<int:user_id>/risk', methods=['GET'])
@requires_auth
@produces('application/json')
def risk(user_id):
    """
    Retrieve a set of risk instances using as extra criterion the threshold value
    pattern: /users/{id}/risk?threshold=<value>
    """
    if request.method == 'GET':
        try:   
            if checkUserExistance(user_id) == 0:
                raise Exception("Not found")

            # Validate the query parameters, if exists
            try:
                for i in request.args:
                    if i not in ["threshold", "medstaffID"]:
                        return handle_exception(400, "Two query parameters are supported: the medstaffID parameter (mandatory) and the threshold one (optional)")


                if request.args.get('threshold') == None:
                    q = 0 
                else:
                    q = float(request.args.get('threshold'))
                    if q < 0 or q > 100:
                        return bad_request('threshold error')

                doctor_username = request.args.get('medstaffID')
                if doctor_username == None:
                    raise Exception("None value of the parameter medstaffID")
                if Doctors.query.filter_by(username=doctor_username).count() != 1:
                    raise Exception("No valid query parameter medstaffID")
            except ValueError, v:
                return bad_request(v.args[0])

            # check relationship between doctor and user
            if doctor2UserRelationship(doctor_username, user_id) == False:
                raise Exception("Not found relationship between user and medical staff")

            # query
            results = db.session.query(Risk, Measurements.biological_parameter_id).\
                filter(Doctors.username == doctor_username).\
                filter(Users.doctor_id == Doctors.id).\
                filter(Users.id == Measurements.user_id).\
                filter(Users.id == user_id).\
                filter(Comparisons.measurement_id == Measurements.id).\
                filter(Risk.comparison_id == Comparisons.id).\
                filter(Risk.possibility >= q).all()

            json_results = []
            counter = 0
            for result, parameter in results:
                counter += 1
                d = {'id': result.id,
                    'biologic_parameter_id': parameter,
                    'value': result.possibility,
                    'timestamp': result.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                }
                json_results.append(d)

            resp = jsonify(response={"risk": json_results})
            resp.status_code = 200
            return resp

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

@app.route('/users/<int:user_id>/risk/recent', methods=['GET'])
@requires_auth
@produces('application/json')
def latestRisk(user_id):
    """
    Retrieve the the latest risk instance based on threshold value
    pattern: /users/{id}/risk/recent?medstaffID=<username>[&threshold=<value>]
    """
    if request.method == 'GET':
        try:   
            if checkUserExistance(user_id) == 0:
                raise Exception("Not found")
        
            # Validate the query parameters, if exists
            try:
                for i in request.args:
                    if i not in ["threshold", "medstaffID"]:
                        return handle_exception(400, "Two query parameters are supported: the medstaffID parameter (mandatory) and the threshold one (optional)")


                if request.args.get('threshold') == None:
                    q = 0 
                else:
                    q = float(request.args.get('threshold'))
                    if q < 0 or q > 100:
                        return bad_request('threshold error')

                doctor_username = request.args.get('medstaffID')
                if doctor_username == None:
                    raise Exception("None value of the parameter medstaffID")
                if Doctors.query.filter_by(username=doctor_username).count() != 1:
                    raise Exception("No valid query parameter medstaffID")
            except ValueError, v:
                return bad_request(v.args[0])

            # check relationship between doctor and user
            if doctor2UserRelationship(doctor_username, user_id) == False:
                raise Exception("Not found relationship between user and medical staff")

            # query
            results = db.session.query(Risk, Measurements.biological_parameter_id).\
                filter(Doctors.username == doctor_username).\
                filter(Users.doctor_id == Doctors.id).\
                filter(Users.id == Measurements.user_id).\
                filter(Users.id == user_id).\
                filter(Comparisons.measurement_id == Measurements.id).\
                filter(Risk.comparison_id == Comparisons.id).\
                filter(Risk.possibility >= q).\
                order_by(Risk.id.desc()).\
                limit(1)

            json_results = []
            counter = 0
            for result, parameter in results:
                counter += 1
                d = {'id': result.id,
                    'biologic_parameter_id': parameter,
                    'value': result.possibility,
                    'timestamp': result.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                }
                json_results.append(d)

            resp = jsonify(response={"risk": json_results})
            resp.status_code = 200
            return resp

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

@app.route('/users/<int:user_id>/risk/<int:year_start>/<int:month_start>/<int:day_start>/<int:year_end>/<int:month_end>/<int:day_end>/', methods=['GET'])
@requires_auth
@produces('application/json')
def periodRisk(user_id,year_start,month_start,day_start,year_end,month_end,day_end):
    """
    Supported endpoint pattern: /users/{user_id}/risk/yyyy/mm/dd/yyyy/mm/dd/?medstaffID=<username>[&threshold=<num>]
    """

    if request.method == 'GET':
        try:   
            if checkUserExistance(user_id) == 0:
                raise Exception("Not found")
        
            if not validateYear(year_start):
                raise Exception("year error")
            if not validateMonth(month_start):
                raise Exception("month error")
            if not validateDay(day_start):
                raise Exception("day error")

            if not validateYear(year_end):
                raise Exception("year error")
            if not validateMonth(month_end):
                raise Exception("month error")
            if not validateDay(day_end):
                raise Exception("day error")

            start_date = datetime(year_start, month_start, day_start, 00, 00, 00).isoformat()
            end_date = datetime(year_end, month_end, day_end, 23, 59, 59).isoformat()
     

            # Validate the query parameters, if exists
            try:
                for i in request.args:
                    if i not in ["threshold", "medstaffID"]:
                        return handle_exception(400, "Two query parameters are supported: the medstaffID parameter (mandatory) and the threshold one (optional)")

                if request.args.get('threshold') == None:
                    q = 0 
                else:
                    q = float(request.args.get('threshold'))
                    if q < 0 or q > 100:
                        return bad_request('threshold error')

                doctor_username = request.args.get('medstaffID')
                if doctor_username == None:
                    raise Exception("None value of the parameter medstaffID")
                if Doctors.query.filter_by(username=doctor_username).count() != 1:
                    raise Exception("No valid query parameter medstaffID")
            except ValueError, v:
                return bad_request(v.args[0])

            # check relationship between doctor and user
            if doctor2UserRelationship(doctor_username, user_id) == False:
                raise Exception("Not found relationship between user and medical staff")

            # query
            results = db.session.query(Risk, Measurements.biological_parameter_id).\
                filter(Doctors.username == doctor_username).\
                filter(Users.doctor_id == Doctors.id).\
                filter(Users.id == Measurements.user_id).\
                filter(Users.id == user_id).\
                filter(Comparisons.measurement_id == Measurements.id).\
                filter(Risk.comparison_id == Comparisons.id).\
                filter(Risk.possibility >= q).\
                filter(Risk.timestamp >= start_date).\
                filter(Risk.timestamp <= end_date).all()

            json_results = []
            counter = 0
            for result, parameter in results:
                counter += 1
                d = {'id': result.id,
                    'biologic_parameter_id': parameter,
                    'value': result.possibility,
                    'timestamp': result.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                }
                json_results.append(d)

            resp = jsonify(response={"risk": json_results})
            resp.status_code = 200
            return resp
            
        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)


@app.route('/users/<int:user_id>/biologic_parameter/<int:biologic_parameter_id>/risk', methods=['GET'])
@requires_auth
@produces('application/json')
def enhancedRisk(user_id, biologic_parameter_id):
    """ 
    Retrieve the falling risk for a user per biologic parameter 
    Optionally, define the low possibility threshold using query prameter ?threshold=x
    """

    if request.method == 'GET':
        try:   
            if checkUserExistance(user_id) == 0:
                raise Exception("Not found")
            if checkBiologicParameterExistance(biologic_parameter_id) == 0:
                raise Exception("Not found")

            # Validate the query parameters, if exists
            try:
                for i in request.args:
                    if i not in ["threshold", "medstaffID"]:
                        return handle_exception(400, "Two query parameters are supported: the medstaffID parameter (mandatory) and the threshold one (optional)")

                if request.args.get('threshold') == None:
                    q = 0 
                else:
                    q = float(request.args.get('threshold'))
                    if q < 0 or q > 100:
                        return bad_request('threshold error')

                doctor_username = request.args.get('medstaffID')
                if doctor_username == None:
                    raise Exception("None value of the parameter medstaffID")
                if Doctors.query.filter_by(username=doctor_username).count() != 1:
                    raise Exception("No valid query parameter medstaffID")
            except ValueError, v:
                return bad_request(v.args[0])

            # check relationship between doctor and user
            if doctor2UserRelationship(doctor_username, user_id) == False:
                raise Exception("Not found relationship between user and medical staff")

            # query
            results = db.session.query(Risk).\
                filter(Doctors.username == doctor_username).\
                filter(Users.doctor_id == Doctors.id).\
                filter(Users.id == Measurements.user_id).\
                filter(Users.id == user_id).\
                filter(Measurements.biological_parameter_id == biologic_parameter_id).\
                filter(Comparisons.measurement_id == Measurements.id).\
                filter(Risk.comparison_id == Comparisons.id).\
                filter(Risk.possibility >= q).all()
            
            json_results = []
            counter = 0
            for result in results:
                counter += 1
                d = {'id': result.id,
                    'value': result.possibility,
                    'timestamp': result.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                }
                json_results.append(d)

            resp = jsonify(response={"risk": json_results})
            resp.status_code = 200
            return resp

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

@app.route('/users/<int:user_id>/biologic_parameter/<int:biologic_parameter_id>/risk/recent', methods=['GET'])
@requires_auth
@produces('application/json')
def enhancedLatestRisk(user_id, biologic_parameter_id):
    """
    Retrieve the latest falling risk for a user per biologic parameter 
    Optionally, define the low possibility threshold using query prameter ?threshold=x

    Supported endpoint pattern: /users/{user_id}/biologic_parameter/{bp_id}/risk/recent?medstaffID=<username>[&trheshold=<num>]
    """

    if request.method == 'GET':
        try:   
            if checkUserExistance(user_id) == 0:
                raise Exception("Not found")
            if checkBiologicParameterExistance(biologic_parameter_id) == 0:
                raise Exception("Not found")
        
            # Validate the query parameters, if exists
            try:
                for i in request.args:
                    if i not in ["threshold", "medstaffID"]:
                        return handle_exception(400, "Two query parameters are supported: the medstaffID parameter (mandatory) and the threshold one (optional)")

                if request.args.get('threshold') == None:
                    q = 0 
                else:
                    q = float(request.args.get('threshold'))
                    if q < 0 or q > 100:
                        return bad_request('threshold error')

                doctor_username = request.args.get('medstaffID')
                if doctor_username == None:
                    raise Exception("None value of the parameter medstaffID")
                if Doctors.query.filter_by(username=doctor_username).count() != 1:
                    raise Exception("No valid query parameter medstaffID")
            except ValueError, v:
                return bad_request(v.args[0])

            # check relationship between doctor and user
            if doctor2UserRelationship(doctor_username, user_id) == False:
                raise Exception("Not found relationship between user and medical staff")

            # query
            results = db.session.query(Risk).\
                filter(Doctors.username == doctor_username).\
                filter(Users.doctor_id == Doctors.id).\
                filter(Users.id == Measurements.user_id).\
                filter(Users.id == user_id).\
                filter(Comparisons.measurement_id == Measurements.id).\
                filter(Measurements.biological_parameter_id == biologic_parameter_id).\
                filter(Risk.comparison_id == Comparisons.id).\
                filter(Risk.possibility >= q).\
                order_by(Risk.id.desc()).\
                limit(1)
            
            json_results = []
            counter = 0
            for result in results:
                counter += 1
                d = {'id': result.id,
                    'value': result.possibility,
                    'timestamp': result.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                }
                json_results.append(d)

            resp = jsonify(response={"risk": json_results})
            resp.status_code = 200
            return resp

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

@app.route('/users/<int:user_id>/biologic_parameter/<int:biologic_parameter_id>/risk/<int:year_start>/<int:month_start>/<int:day_start>/<int:year_end>/<int:month_end>/<int:day_end>/', methods=['GET'])
@requires_auth
@produces('application/json')
def enhancedPeriodRisk(user_id,year_start,month_start,day_start,year_end,month_end,day_end, biologic_parameter_id):
    """
    Retrieve a list of falling risk for a user per biologic parameter at the predefined time period
    Optionally, define the low possibility threshold using query prameter ?threshold=x
    """
    if request.method == 'GET':
        try:   
            if checkUserExistance(user_id) == 0:
                raise Exception("Not found")
            if checkBiologicParameterExistance(biologic_parameter_id) == 0:
                raise Exception("Not found")
        
            if not validateYear(year_start):
                raise Exception("year error")
            if not validateMonth(month_start):
                raise Exception("month error")
            if not validateDay(day_start):
                raise Exception("day error")

            if not validateYear(year_end):
                raise Exception("year error")
            if not validateMonth(month_end):
                raise Exception("month error")
            if not validateDay(day_end):
                raise Exception("day error")

            start_date = datetime(year_start, month_start, day_start, 00, 00, 00).isoformat()
            end_date = datetime(year_end, month_end, day_end, 23, 59, 59).isoformat()
     

            # Validate the query parameters, if exists
            try:
                for i in request.args:
                    if i not in ["threshold", "medstaffID"]:
                        return handle_exception(400, "Two query parameters are supported: the medstaffID parameter (mandatory) and the threshold one (optional)")

                if request.args.get('threshold') == None:
                    q = 0 
                else:
                    q = float(request.args.get('threshold'))
                    if q < 0 or q > 100:
                        return bad_request('threshold error')

                doctor_username = request.args.get('medstaffID')
                if doctor_username == None:
                    raise Exception("None value of the parameter medstaffID")
                if Doctors.query.filter_by(username=doctor_username).count() != 1:
                    raise Exception("No valid query parameter medstaffID")
            except ValueError, v:
                return bad_request(v.args[0])

            # check relationship between doctor and user
            if doctor2UserRelationship(doctor_username, user_id) == False:
                raise Exception("Not found relationship between user and medical staff")

            # query
            results = db.session.query(Risk).\
                filter(Doctors.username == doctor_username).\
                filter(Users.doctor_id == Doctors.id).\
                filter(Users.id == Measurements.user_id).\
                filter(Users.id == user_id).\
                filter(Comparisons.measurement_id == Measurements.id).\
                filter(Measurements.biological_parameter_id == biologic_parameter_id).\
                filter(Risk.comparison_id == Comparisons.id).\
                filter(Risk.possibility >= q).\
                filter(Risk.timestamp >= start_date).\
                filter(Risk.timestamp <= end_date).all()

            json_results = []
            counter = 0
            for result in results:
                counter += 1
                d = {'id': result.id,
                    'value': result.possibility,
                    'timestamp': result.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                }
                json_results.append(d)

            resp = jsonify(response={"risk": json_results})
            resp.status_code = 200
            return resp
            
        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)



def deleteUser(user_id):
    """
    Delete a user instance. This action triggers the deletetion of associated measurement instances.

    Input:      users.id
    Output:     None
    Operation:  Delete the measurements instances included this user_id
                Delete the user instance
    """

    # retrieve associated measurements list
    measurements = Measurements.query.filter_by(user_id=user_id).all()
    for measurement in measurements:
        deleteMeasurement(measurement)

    # delete user
    user = Users.query.get(user_id)
    db.session.delete(user)
    db.session.commit()

def deleteParameter(parameter_id):
    """
    Delete a parameter instance. This action triggers the deletetion of associated measurement and rule instances.

    Input:      biological_parameters.id
    Output:     None
    Operation:  Delete the measurements instances included this id
                Delete the rules instances included this id
                Delete the biological paramter instance
    """

    # retrieve associated measurements list
    measurements = Measurements.query.filter_by(biological_parameter_id=parameter_id).all()
    for instance in measurements:
        deleteMeasurement(instance)

    # retrieve associated rules list
    rules = Rules.query.filter_by(biological_parameter_id=parameter_id).all()
    for rule in rules:
        deleteRule(rule)

    # delete parameter
    b_param = BiologicParameters.query.get(parameter_id)
    db.session.delete(b_param)
    db.session.commit()

def deleteMeasurement(measurement):
    """
    Delete a measurement instance. Leaf of deletion process

    Input:  Measurement object
    Output: None
    Operation:  Delete a measurement instance
    """

    db.session.delete(measurement)
    db.session.commit()

def deleteRule(rule):
    """
    Delete a rule instance. Leaf of deletion process

    Input:  Rule object
    Output: None
    Operation:  Delete a rule instance
    """

    db.session.delete(rule)
    db.session.commit()



#@app.route('/treatments', methods=['GET', 'POST'])
#@produces('application/json')
def treatments():
    """
    Retrieve a collection of treatments or create a new one.
    """

    if request.method == 'GET':
        try:
            results = Treatments.query.all()

            json_results = []
            counter = 0
            for result in results:
                counter += 1
                d = {'id': result.id,
                    'name': result.name,
                    'description': result.description,
                    'ontime': result.ontime.strftime("%Y-%m-%d %H:%M:%S")
                }
                json_results.append(d)

            resp = jsonify(response={"treatments": json_results})
            resp.status_code = 200
            return resp

        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

    elif request.method == 'POST':
        try:
            # Check header
            try:
                if request.headers['Content-Type'] != 'application/json':
                    return invalid_accept_method(415)
            except NameError:
                return invalid_accept_method(415)

            # Validate JSON structure
            payload = None
            try:
                payload = request.get_json(force = False) 
            except:
                raise KeyError("Invalid JSON payload: " + request.url)           

            if payload is False:
                raise Exception("Invalid JSON payload: " + request.url)

            if payload is None:
                raise Exception("Empty JSON payload: " + request.url)

            # Payload validation 
            try:
                schema = getValidTreatmentProfileSchema()
                validictory.validate(payload,schema)
            except ValueError as v:
                raise Exception(v.args[0])


            # add new user 
            treatment = Treatments(payload['name'], payload['description'])
            db.session.add(treatment)
            db.session.commit()

            # retrieve the instance of inserted user
            counter = 0
            results = Treatments.query.filter_by(id=treatment.id)
            for result in results:
                counter += 1
                treatment = {'id': result.id,
                    'name': result.name,
                    'description': result.description,
                    'ontime': result.ontime.strftime("%Y-%m-%d %H:%M:%S")
                }

            # return added user instance
            if counter == 1:
                resp = jsonify(response={"treatment": treatment})
                resp.status_code = 201
                return resp
            else:
                return not_found(404)
        except Exception, e:
            return handle_exception(400, e.args[0])
        except KeyError, k:
            return key_error(k.args[0])
        except exc.SQLAlchemyError as k:
            return sqlalchemy_error_404(k.args[0])
        except:
            return internal_error("500")

#@app.route('/treatments/<int:treat_id>', methods=['GET', 'PUT', 'DELETE'])
#@produces('application/json')
def treatment(treat_id):
    """ Retrieve/Update/Delete a treatement instance """

    if request.method == 'GET':
        try:
            rows = Treatments.query.filter_by(id=treat_id).count()
            if rows == 0:
                raise Exception("Not found")

            results = Treatments.query.filter_by(id=treat_id).limit(1)
            for result in results:
                treatment = {'id': result.id,
                    'name': result.name,
                    'description': result.description,
                    'ontime': result.ontime.strftime("%Y-%m-%d %H:%M:%S")
                }

            resp = jsonify(response={"treatment": treatment})
            resp.status_code = 200
            return resp

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)   

    elif request.method == 'PUT':
        try:
            # Check header
            try:
                if request.headers['Content-Type'] != 'application/json':
                    return invalid_method(415)
            except NameError:
                return invalid_method(415)

            # Validate JSON structure
            payload = None
            try:
                payload = request.get_json(force = False) 
            except:
                raise KeyError("Invalid JSON payload: " + request.url)           

            if payload is False:
                raise Exception("Invalid JSON payload: " + request.url)

            if payload is None:
                raise Exception("Empty JSON payload: " + request.url)

            # Payload validation 
            try:
                schema = getValidTreatmentProfileSchema()
                validictory.validate(payload,schema)
            except ValueError as v:
                raise Exception(v.args[0]) 
  

            list = dict(name=payload['name'], description=payload['description'])

            tt = Treatments.query.filter_by(id=treat_id).update(list)
            db.session.commit()
            
            # return updated user info
            results = Treatments.query.filter_by(id=treat_id).limit(1)
            counter = 0
            for row in results:
                counter += 1
                ttreat_id = {'id': row.id,
                    'name': row.name,
                    'description': row.description,
                    'ontime': row.ontime.strftime("%Y-%m-%d %H:%M:%S")
                }

            if counter == 1:
                return jsonify(response={"treatment": ttreat_id}), status.HTTP_200_OK
            else:
                return not_found(404)
        except Exception, e:
            return handle_exception(400, e.args[0])
        except KeyError, k:
            return key_error(k.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

    elif request.method == 'DELETE':
        try:
            if Treatments.query.filter_by(id=treat_id).count() == 0:
                raise Exception("Not found")

            # delete the associated measurement instances
            historyList = History.query.filter_by(treatment_id=treat_id).all()
            for i in historyLists:
                db.session.delete(i)
                db.session.commit()

            treatment = Treatments.query.get(treat_id)
            db.session.delete(treatment)
            db.session.commit()
            return '', status.HTTP_200_OK

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

#@app.route('/treatments/schema', methods=['GET'])
#@produces('application/json')
def treatmentSchema():
    if request.method == 'GET':
        schema = getValidTreatmentProfileSchema()
        resp = jsonify(schema)
        resp.status_code = 200
        return resp


#@app.route('/profiles', methods=['GET', 'POST'])
#@produces('application/json')
def profiles():
    """
    Retrieve a collection of profiles or create a new one.
    """

    if request.method == 'GET':
        try:
            results = Profiles.query.all()

            json_results = []
            counter = 0
            for result in results:
                counter += 1
                d = {'id': result.id,
                    'name': result.name,
                    'description': result.description,
                    'ontime': result.ontime.strftime("%Y-%m-%d %H:%M:%S")
                }
                json_results.append(d)

            resp = jsonify(response={"profiles": json_results})
            resp.status_code = 200
            return resp

        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

    elif request.method == 'POST':
        try:
            # Check header
            try:
                if request.headers['Content-Type'] != 'application/json':
                    return invalid_accept_method(415)
            except NameError:
                return invalid_accept_method(415)

            # Validate JSON structure
            payload = None
            try:
                payload = request.get_json(force = False) 
            except:
                raise KeyError("Invalid JSON payload: " + request.url)           

            if payload is False:
                raise Exception("Invalid JSON payload: " + request.url)

            if payload is None:
                raise Exception("Empty JSON payload: " + request.url)

            # Payload validation 
            try:
                schema = getValidTreatmentProfileSchema()
                validictory.validate(payload,schema)
            except ValueError as v:
                raise Exception(v.args[0])


            # add new user 
            profile = Profiles(payload['name'], payload['description'])
            db.session.add(profile)
            db.session.commit()

            # retrieve the instance of inserted user
            counter = 0
            results = Profiles.query.filter_by(id=profile.id)
            for result in results:
                counter += 1
                profile = {'id': result.id,
                    'name': result.name,
                    'description': result.description,
                    'ontime': result.ontime.strftime("%Y-%m-%d %H:%M:%S")
                }

            # return added user instance
            if counter == 1:
                resp = jsonify(response={"profile": profile})
                resp.status_code = 201
                return resp
            else:
                return not_found(404)
        except Exception, e:
            return handle_exception(400, e.args[0])
        except KeyError, k:
            return key_error(k.args[0])
        except exc.SQLAlchemyError as k:
            return sqlalchemy_error_404(k.args[0])
        except:
            return internal_error("500")

#@app.route('/profiles/<int:profile_id>', methods=['GET', 'PUT', 'DELETE'])
#@produces('application/json')
def profile(profile_id):
    """ Retrieve/Update/Delete a profile instance """

    if request.method == 'GET':
        try:
            rows = Profiles.query.filter_by(id=profile_id).count()
            if rows == 0:
                raise Exception("Not found")

            results = Profiles.query.filter_by(id=profile_id).limit(1)
            for result in results:
                profile = {'id': result.id,
                    'name': result.name,
                    'description': result.description,
                    'ontime': result.ontime.strftime("%Y-%m-%d %H:%M:%S")
                }

            resp = jsonify(response={"profile": profile})
            resp.status_code = 200
            return resp

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)   

    elif request.method == 'PUT':
        try:
            # Check header
            try:
                if request.headers['Content-Type'] != 'application/json':
                    return invalid_method(415)
            except NameError:
                return invalid_method(415)

            # Validate JSON structure
            payload = None
            try:
                payload = request.get_json(force = False) 
            except:
                raise KeyError("Invalid JSON payload: " + request.url)           

            if payload is False:
                raise Exception("Invalid JSON payload: " + request.url)

            if payload is None:
                raise Exception("Empty JSON payload: " + request.url)

            # Payload validation 
            try:
                schema = getValidTreatmentProfileSchema()
                validictory.validate(payload,schema)
            except ValueError as v:
                raise Exception(v.args[0]) 
  

            list = dict(name=payload['name'], description=payload['description'])

            pp = Profiles.query.filter_by(id=profile_id).update(list)
            db.session.commit()
            
            # return updated user info
            results = Profiles.query.filter_by(id=profile_id).limit(1)
            counter = 0
            for row in results:
                counter += 1
                profile_ = {'id': row.id,
                    'name': row.name,
                    'description': row.description,
                    'ontime': row.ontime.strftime("%Y-%m-%d %H:%M:%S")
                }

            if counter == 1:
                return jsonify(response={"profile": profile_}), status.HTTP_200_OK
            else:
                return not_found(404)
        except Exception, e:
            return handle_exception(400, e.args[0])
        except KeyError, k:
            return key_error(k.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

    elif request.method == 'DELETE':
        try:
            if Profiles.query.filter_by(id=profile_id).count() == 0:
                raise Exception("Not found")

            # delete the associated measurement instances
            historyList = History.query.filter_by(profile_id=profile_id).all()
            for i in historyLists:
                db.session.delete(i)
                db.session.commit()

            profile = Profiles.query.get(profile_id)
            db.session.delete(profile)
            db.session.commit()
            return '', status.HTTP_200_OK

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

#@app.route('/profiles/schema', methods=['GET'])
#@produces('application/json')
def profileSchema():
    if request.method == 'GET':
        schema = getValidTreatmentProfileSchema()
        resp = jsonify(schema)
        resp.status_code = 200
        return resp

def getValidTreatmentProfileSchema():
    """ Retrieve the valid schema of the treatment payload """

    schema = {"$schema": "http://json-schema.org/schema#",
            "type": "object",
            "additionalProperties": False,
            "properties":
            {
                "name": {"type" : "string" },
                "description": {"type": "string", "minLength":1, "maxLength":300}
            },
            "required": ["name", "description"]
        }

    return schema 

#@app.route('/users/<int:user_id>/history', methods=['GET', 'POST'])
#@produces('application/json')
def historyList(user_id):
    """
    pattern /users/{user_id}/history?medstaffID={username} 
    """

    # Check if user's doctor exists. Otherwise, raise an exception
    try:
        for i in request.args:
            if i not in ["medstaffID"]:
                return handle_exception(400, "The only query parameter that is allowed (and required) is the medstaffID.")
        if len(request.args) == 0:
            return handle_exception(400, "The only query parameter that is allowed (and required) is the medstaffID.")

        doctor_username = request.args.get('medstaffID')
        if doctor_username == None:
            raise Exception("None value of the parameter medstaffID")
        if Doctors.query.filter_by(username=doctor_username).count() != 1:
            raise Exception("No valid query parameter medstaffID")
    except ValueError, v:
        return bad_request(v.args[0])
    except Exception, e:
        return handle_exception(400, e.args[0])
    except:
        return internal_error("500")


    if request.method == 'GET':
        try:
            if doctor2UserRelationship(doctor_username, user_id) == False:
                raise Exception("Not found relationship between user and medical staff")

            results = db.session.query(History).\
                filter(Doctors.username == doctor_username).\
                filter(Users.doctor_id == Doctors.id).\
                filter(Users.id == History.user_id).\
                filter(History.user_id == user_id).all()

            json_results = []
            counter = 0
            for result in results:
                counter += 1
                d = {'id': result.id,
                    'profile_id': result.profile_id,
                    'treatment_id': result.treatment_id
                }
                json_results.append(d)

            resp = jsonify(response={"history": json_results})
            resp.status_code = 200
            return resp

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

    elif request.method == 'POST':
        try:
            # Check header
            try:
                if request.headers['Content-Type'] != 'application/json':
                    return invalid_accept_method(415)
            except NameError:
                return invalid_accept_method(415)

            if doctor2UserRelationship(doctor_username, user_id) == False:
                raise Exception("Not found relationship between user and medical staff")

            # Validate JSON structure
            payload = None
            try:
                payload = request.get_json(force = False) 
            except:
                raise KeyError("Invalid JSON payload: " + request.url)           

            if payload is False:
                raise Exception("Invalid JSON payload: " + request.url)

            if payload is None:
                raise Exception("Empty JSON payload: " + request.url)

            # Payload validation 
            try:
                schema = getValidHistorySchema()
                validictory.validate(payload,schema)
            except ValueError as v:
                raise Exception(v.args[0])


            # add new user 
            history = History(user_id, payload['profile_id'], payload['treatment_id'])
            db.session.add(history)
            db.session.commit()

            # retrieve the instance of inserted user
            results = History.query.filter_by(id=history.id)
            for result in results:
                h = {'id': result.id,
                    'user_id': result.user_id,
                    'profile_id': result.profile_id,
                    'treatment_id': result.treatment_id
                }

            # return added user instance
            resp = jsonify(response={"history": h})
            resp.status_code = 201
            return resp

        except Exception, e:
            return handle_exception(400, e.args[0])
        except KeyError, k:
            return key_error(k.args[0])
        except exc.SQLAlchemyError as k:
            return sqlalchemy_error_404(k.args[0])
        except:
            return internal_error("500")

#@app.route('/history/<int:history_id>', methods=['GET', 'DELETE'])
#@produces('application/json')
def historyInstance(user_id):
    """
    pattern /history/{id}?medstaffID={username}
    """

    # Check if user's doctor exists. Otherwise, raise an exception
    try:
        for i in request.args:
            if i not in ["medstaffID"]:
                return handle_exception(400, "The only query parameter that is allowed (and required) is the medstaffID.")
        if len(request.args) == 0:
            return handle_exception(400, "The only query parameter that is allowed (and required) is the medstaffID.")

        doctor_username = request.args.get('medstaffID')
        if doctor_username == None:
            raise Exception("None value of the parameter medstaffID")
        if Doctors.query.filter_by(username=doctor_username).count() != 1:
            raise Exception("No valid query parameter medstaffID")
    except ValueError, v:
        return bad_request(v.args[0])
    except Exception, e:
        return handle_exception(400, e.args[0])
    except:
        return internal_error("500")


    if request.method == 'GET':
        try:
            if doctor2UserRelationship(doctor_username, user_id) == False:
                raise Exception("Not found relationship between user and medical staff")

            results = db.session.query(History).\
                filter(Doctors.username == doctor_username).\
                filter(Users.doctor_id == Doctors.id).\
                filter(Users.id == History.user_id).\
                filter(History.user_id == user_id).\
                filter(History.id == history_id).all()

            json_results = []
            counter = 0
            for result in results:
                counter += 1
                d = {'id': result.id,
                    'profile_id': result.profile_id,
                    'treatment_id': result.treatment_id
                }
                json_results.append(d)

            resp = jsonify(response={"history": json_results})
            resp.status_code = 200
            return resp

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

    elif request.method == 'DELETE':
        try:
            if doctor2UserRelationship(doctor_username, user_id) == False:
                raise Exception("Not found relationship between user and medical staff")

            results = db.session.query(History).\
                filter(Doctors.username == doctor_username).\
                filter(Users.doctor_id == Doctors.id).\
                filter(Users.id == History.user_id).\
                filter(History.user_id == user_id).\
                filter(History.id == history_id).all()

            json_results = []
            counter = 0
            for result in results:
                counter += 1
                d = {'id': result.id,
                    'profile_id': result.profile_id,
                    'treatment_id': result.treatment_id
                }
                json_results.append(d)

            resp = jsonify(response={"history": json_results})
            resp.status_code = 200
            return resp

        except Exception, e:
            return handle_exception(404, e.args[0])
        except exc.SQLAlchemyError, s:
            return sqlalchemy_error_404(s.args[0])
        except:
            return internal_error(500)

def getValidHistorySchema():
    """ Retrieve the valid schema of the history payload """

    schema = {"$schema": "http://json-schema.org/schema#",
            "type": "object",
            "additionalProperties": False,
            "properties":
            {
                "profile_id": {"type" : "integer" },
                "treatment_id": {"type": "integer"}
            },
            "required": ["profile_id", "treatment_id"]
        }

    return schema 



def validateGroupID(group_id):

    if group_id is None or group_id == "":
        return False
    rows = Groups.query.filter_by(id=group_id).count()
    if rows == 0:
        return False
    return True

def validateUID(uid):
    
    if uid is None or uid == "":
        return False
    userNo = Users.query.filter_by(uid=uid).count()
    if userNo >0:
        return False
    return True

def validateDoctorUsername(username):
    
    if username is None or username == "":
        return False
    instances = Doctors.query.filter_by(username=username).count()
    if instances > 0: 
        return False
    return True

def checkUserExistance(user_id):
    """ 
    Find the number of rows based on user.id
    """
    rows = Users.query.filter_by(id=user_id).count()
    return rows

def checkBiologicParameterExistance(parameter):
    """ 
    Find the number of rows based on biologic_parameters.id
    """
    rows = BiologicParameters.query.filter_by(id=parameter).count()
    return rows

def validateYear(year):
    """ Validate the year value """
    if year < 0:
        return False
    if len(str(year)) < 4:
        return False
    return True

def validateMonth(month):
    """ Validate the month value """
    if month not in range(1, 13):
        return False
    #if len(str(month)) != 2:
    #    return False
    return True

def validateDay(day):
    """ Validate the day value """
    if day not in range(1, 32):
        return False
    #if len(str(day)) != 2:
    #    return False
    return True

def isInteger(value):
    """ Validate if a value is integer or not """    
    try: 
        val = int(value)
        return True
    except ValueError:
        return False

def isFloat(value):
    """ Validate if value is float """
    try:
        val = float(value)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    app.run(debug=True);



