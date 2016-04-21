
from flask import Flask, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.api import status
from datetime import datetime, date
from sqlalchemy import exc, ForeignKey
from sqlalchemy.orm import relationship
import json
import logging
import logging.handlers
#from model import *
from notifier import *
import pytz
from math import ceil
from ConfigParser import SafeConfigParser
import sys
sys.path.append("/opt/fre_package/")
from model import *

# package version
__version__ = '0.4'


# logger settings
parser = SafeConfigParser()
parser.read('/etc/sysconfig/fallRiskEvaluation/fallRiskEvaluation.conf')

LOG_FILENAME = parser.get('logs', 'PATH')
my_logger = logging.getLogger('datahandler:orion2sql')
my_logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=parser.get('logs', 'LOGS_FILE_SIZE'), backupCount=parser.get('logs', 'LOG_FILES_NUMBER'))
my_logger.addHandler(handler)

@app.route('/testing', methods=['GET'])
def unitTesting():
    try:
        if request.headers['Accept'] =='application/json':
            resp = jsonify(response={"status": {"code": 200, "reason": "OK", "details": "Used only for unit testing."}})
            resp.status_code = 200
            return resp
        elif request.headers['Accept'] == 'text/html':
            resp = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><title>It works!</title><h1>Orion Context Broker to mysql broker works!</h1><p>Used only for unit testing.</p>'
            return resp
        else:
            resp = jsonify(error={"code": 415, "reason": "Unsupported Media Type"})
            resp.status_code = 415
            return resp
    except NameError, n:
        resp = jsonify(error={"code": 400, "reason": n.args[0]})
        resp.status_code = 400
        return resp


@app.route('/orion2mysql', methods=['POST'])
def mediator():
    """ 
    Receive a notification from the Orion context broker GE and store measurements into MySQL tables 
    """

    flag = False
    debug = False
    systemTimestamp = systemDateTime()

    if request.method == 'POST':
        try:           
            #======================
            # Validate JSON object
            #======================
            payload = request.get_json()
            jsonData = jsonEncode(payload)

            #=====================
            # Check status code
            #=====================
            code = payload["contextResponses"][0]["statusCode"]["code"];
            if code not in ["200", "201"]:
                raise Exception("Invalid response status.")

            #=====================
            # Validate user uid
            #=====================
            user = getUser(str(payload["contextResponses"][0]["contextElement"]["id"]))            
            if user["id"] == None:
                raise Exception("None user found")
            userID = user["id"]
            userEmailAccount = user["email"]
            timestamp = None

            #===============================
            # Retrieve uploading timestamp
            #===============================
            attributes = payload["contextResponses"][0]["contextElement"]["attributes"]            
            for j in attributes:
                if j["name"] == "timestamp":
                    timestamp = j["value"]
            if timestamp == None:
                raise Exception("No timestamp found")

            #=======================
            #   Set .xlsx filename
            #=======================
            #filename = "notification.xlsx"
            filename = str(payload["contextResponses"][0]["contextElement"]["id"]) 
            filename += ".xlsx"

            #=====================================
            # Prepare structure for attcahed file
            #=====================================
            emailBody = []
            
            #=========================================
            # Run through the list of the measurements
            #=========================================
            list = payload["contextResponses"][0]["contextElement"]["attributes"]
            for i in list:
                # prevent from timestamp parameter
                if i["name"] == "timestamp":
                    continue

                # declare an empty dictionary
                data = dict()

                biologicParamID = getBiologicParameter(i['name'])
                if biologicParamID == None:
                    continue;

                # filter Null values
                if i["value"] == "null" or i["value"] == None:
                    continue

                # get measurement instance ID
                measurementID = insertMeasurement(userID, biologicParamID, i['value'], timestamp) 
                if measurementID < 0:
                    my_logger.debug(systemTimestamp +" WARNING: " + i['name']+ "-> Invalid measurement ID")
                    continue
                my_logger.debug(systemTimestamp + " INFO: " + i['name'] + "-> A new measurement instance was inserted.")
                
                # append data in dictionary
                data["user"] = userID
                data["biologic_param"] = biologicParamID
                data["measurement"] = measurementID
                data["value"] = i["value"]
                
                # insert a new comparisons instance
                comparisonFeedback = insertComparisonInstance(data, timestamp)
                if comparisonFeedback == None:
                    my_logger.debug(systemTimestamp +" WARNING: " + i['name']+ "-> No comparison!")
                    # append measurement with no risk info
                    emailBody.append(dict(parameter=i['name'], value=i['value'], risk=-1, timestamp=str(timestamp)))
                    continue
                my_logger.debug(systemTimestamp + " INFO: " + i['name'] + "-> A new Comparison instance was inserted.")
                
                # fall risk evaluation
                fallRiskEvaluator(comparisonFeedback, timestamp)   

                # prepare the email body
                if comparisonFeedback['status'] >= 50:
                    flag = True
                emailBody.append(dict(parameter=i['name'], value=i['value'], risk=comparisonFeedback['status'],timestamp=timestamp))

            #=================================
            # We send an email, if flag true
            #=================================
            if flag:
                # create a .xls file
                createXlsxFile(emailBody, filename)
                #attach file to email
                if notification(emailBody, userEmailAccount, filename) < 0:
                    my_logger.debug(systemTimestamp +" WARNING: None email notification was sent.")
                my_logger.debug(systemTimestamp +" INFO: A new email notification was sent.")

            #======================
            # Web service response
            #======================
            return jsonify({"message":"OK"}), status.HTTP_200_OK

        except Exception, e:
            my_logger.debug(systemTimestamp +" ERROR: " + e.args[0])
        except:
            import traceback
            traceback.print_exc()
            my_logger.debug(systemTimestamp +" ERROR: " + traceback.print_exc())


def jsonEncode(payload):
    """ Encode JSON object """
    try:

        return json.dumps(payload)
    except:
        import traceback
        traceback.print_exc()

def getUser(id):
    """
    Retrieve user.id based on unique key uid existed on table users
    """
    try:
        response = None

        # keep the decimal prefix
        _uid = id.replace("Patient", '')
        
        # find user based on unique ID
        users = Users.query.filter_by(uid=_uid)
        
        # normally 1 loop
        response = dict()
        for user in users:
            response["id"] = user.id
            response["email"] = user.email
            response["timezone"] = user.timezone

        # return user ID
        return response

    except:
        import traceback
        traceback.print_exc()
    
def getBiologicParameter(bName):
    """ Retrieve the id of biologic parameter based on its name, if exists """

    try:        
        # get biological name
        list = BiologicParameters.query.filter_by(name=bName).limit(1)

        # initiate the variable
        bp_id = None

        # get the id 
        for param in list:
            bp_id = param.id

        return bp_id

    except:
        import traceback
        traceback.print_exc()
    
def insertMeasurement(user_id, bp_id, value, timestamp):
    """ Insert a new measurement """

    systemTimestamp = systemDateTime()
    try:
        msr = Measurements.query.filter_by(user_id=user_id).\
            filter_by(biological_parameter_id=bp_id).\
            filter_by(timestamp=timestamp).\
            count()
        if msr:
            return -1

        # insert record
        measurement = Measurements(user_id, bp_id, timestamp, value)
        db.session.add(measurement)
        db.session.commit()        
        return measurement.id

    except:
        import traceback
        traceback.print_exc()
        return -1

def insertComparisonInstance (dataset, timestamp):
    """ Evaluate the measurement using the correponding rule instance """
        
    systemTimestamp = systemDateTime()
    
    try:
        response = dict()
        
        # retrieve rule based on biologic parameter
        rules = Rules.query.filter_by(biological_parameter_id=dataset['biologic_param']).limit(1)    
        
        for rule in rules:
            # initiate the possibility
            state = 0
            
            # validate measurement's value
            try:
                value = float(dataset['value'])
            except ValueError:
                return None

            #================================
            # Fall risk evaluation algorithm 
            #================================

            # possibility around the optimal value
            a = 0.5     
            # possibility out of acceptable thresholds range
            b = 1 - a

            # Count the possibility of falling
            if value == rule.optimal_value:
                # possibility:= 0
                state = 0
            elif value > rule.optimal_value:

                # validate high acceptable threshold                          
                try:
                    float(rule.acceptable_high_threshold)
                except ValueError, v:
                    raise Exception("insertComparisonInstance(): acceptable_high_threshold-> " + v.args[0])

                # validate high critical threshold 
                try:
                    float(rule.critical_high_threshold)
                except ValueError, v:
                    raise Exception("insertComparisonInstance(): critical_high_threshold-> " + v.args[0])

                # right side
                if value <= rule.acceptable_high_threshold:
                    # interpolation plot of possibility [0, 0.5]
                    ratio = abs(value - rule.optimal_value)/(rule.acceptable_high_threshold - rule.optimal_value)
                    state = pow(ratio, 6) * a
                else:
                    # linear plot of possibility (0.5, 1]
                    ratio = abs(value - rule.acceptable_high_threshold)/(rule.critical_high_threshold - rule.acceptable_high_threshold)
                    state = ratio * b + a
            else:
                # validate high acceptable threshold                          
                try:
                    float(rule.acceptable_low_threshold)
                except ValueError, v:
                    raise Exception("insertComparisonInstance(): acceptable_low_threshold-> " + v.args[0])

                # validate high critical threshold 
                try:
                    float(rule.critical_low_threshold)
                except ValueError, v:
                    raise Exception("insertComparisonInstance(): critical_low_threshold-> " + v.args[0])

                # left side
                if value >= rule.acceptable_low_threshold:
                    # interpolation plot of possibility [0, 0.5]
                    ratio = abs(value - rule.optimal_value)/abs(rule.acceptable_low_threshold - rule.optimal_value)
                    state = pow(ratio, 6) * a
                else:
                    # linear plot of possibility (0.5, 1]
                    ratio = abs(value - rule.acceptable_low_threshold)/abs(rule.critical_low_threshold - rule.acceptable_low_threshold)
                    state = ratio * b + a 

            # Normalize the falling possibility on range [0, 1]
            if state < 0:
                state = 0
            elif state > 1:
                state = 1

            fre = ceil(state*100)

            # add instance in Comparisons table
            comparison = Comparisons(dataset["measurement"], rule.id, None, fre, systemTimestamp)
            db.session.add(comparison)
            db.session.commit()            

            response["comparison_id"] = comparison.id
            response["status"] = fre
        return response

    except Exception, e:
        my_logger.debug(systemTimestamp + " WARNING: " + e.args[0])
        return None
    except:
        import traceback
        traceback.print_exc()
        return None

def fallRiskEvaluator(input, timestamp):
    """ 
    Consider if the current value of measurement trigger a rule and send a email notification.

    Arguments 
        input: a dictionary that contains the user ID, the measurement ID, the related biologic parameter ID and the related rule status
        contact: a email account 
    """
    systemTimestamp = systemDateTime()
    notifyThreshold = 50.0

    try:
        risk = Risk(input["comparison_id"], float(input["status"]),timestamp)
        db.session.add(risk)
        db.session.commit()

        if risk.id > 0:
            my_logger.debug(systemTimestamp +" INFO: " + " A new risk instance was inserted.")

    except Exception, e:
        import traceback
        traceback.print_exc()
    except:
        import traceback
        traceback.print_exc()

def notification(data, destination, filename):
    """
    Send a real-time mail notification 
    """

    mail = Email.default_settings()
    receiver = list()
    receiver.append(destination)
    attachment = "/home/orion2sql/"+filename

    text = "Dear user,<br><br>"
    text += "One of the measurements (at least) causes a high falling possibility. See the following table or find it attached:<br><br>"

    table ="<html><head><style>table, th, td {border: 1px solid black;}</style></head><body><table cellpadding='20'><thead><tr><th>onTime</th><th>Parameter</th><th>Falling Risk (%)</th><th>Measurement</th></tr></thead><tbody>"; 
    
    for k, d in enumerate(data):
        for i, (value, params) in enumerate(d.items()):
            if i == 0:
                table += "<tr>"

            if value == 'risk':
                if params >= 50:
                    table += "<center><td style='color: red'>" + str(params) + '</td></center>'
                elif params < 0:
                    table += "<center><td>Not calculated</td></center>"
                else:
                    table += "<center><td>" + str(params) + '</td></center>'
            else:
                table += "<center><td>" + str(params) + '</td></center>'
        
            if i == 3:
                table += "</tr>"
            
    text += table
    text += '</tbody></table></body></html>'

    text += "<br><br>"
    text += "Sincerely,<br>" 
    text += "The Angel team"

    # attach .xlsx file in email notification
    return mail.send_email_xls_attachment(destination, text, attachment)
    
def createXlsxFile(data, filename):
    """
    Create a .xlsx file included the incoming measurements and the calculated falling risk per one
    """
    import xlsxwriter
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet("Falling risk evaluation")
    # format bold
    bold = workbook.add_format({'bold': True})
    bold.set_border(2)
    # colorized cell
    red_cell = workbook.add_format()
    red_cell.set_pattern(1)  # This is optional when using a solid fill.
    red_cell.set_bg_color('red')
    red_cell.set_border(2)
    # border
    genFormat = workbook.add_format()
    genFormat.set_border(2)

    # add headers
    worksheet.write("A1","Biologic parameters", bold)
    worksheet.write("B1", "Calculated falling possibility", bold)
    worksheet.write("C1", "Measurements", bold)
    worksheet.write("D1", "Datetime", bold)

    # Some data we want to write to the worksheet.
    for k, d in enumerate(data):
        for i, (value, params) in enumerate(d.items()):
            if value == "parameter":
                worksheet.write(k+1, 0, params, genFormat)
            elif value == "risk":
                if params < 0:
                    worksheet.write(k+1, 1, "Not calculated", genFormat)
                elif params >= 50:
                    worksheet.write(k+1, 1, float(params), red_cell)
                else:
                    worksheet.write(k+1, 1, float(params), genFormat)
            elif value == "value":
                worksheet.write(k+1, 2, float(params), genFormat)
            else:
                worksheet.write(k+1, 3, params, genFormat)
    workbook.close()


def systemDateTime():
    """
    Get the date & time of virtual machine
    Usage on logs
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")



if __name__ == '__main__':
     my_logger.debug(" INFO: " + " testing")

