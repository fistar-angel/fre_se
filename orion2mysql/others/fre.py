#import packages or modules
from flask import Flask, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.api import status
from datetime import datetime, date
from sqlalchemy import exc, ForeignKey
from sqlalchemy.orm import relationship
from model import *
from notifier import *


class FallRiskEvaluation(object):
    """
    Consider if the current value of mewasurement trigger a rule and send a email notification.


    Arguments
        input: a dictionary that contains the user ID, the measurement ID, the related biologic parameter ID and the related rule status
        contact: a email account
    """


    def __init__(self, userID, biologicParameterID, measurement):
        """ FallRiskEvaluation constructor """

        self.userID = userID
        self.biologicParameterID = biologicParameterID
        self.measurementID = measurement["id"]
        self.measurementValue = measurement["value"]



    def getRuleStatus(self):
        """ Evaluate the measurement using the correponding rule instance """

        try:
            response = dict()

            #rules = Rules.query.filter_by(biological_parameter_id=dataset['biologic_param']).limit(1)
            rules = Rules.query.filter_by(biological_parameter_id=self.biologicParameterID).limit(1)

            for rule in rules:
                state = 0
                value = float(self.measurementValue)

                if rule.down_threshold != "" and value < rule.down_threshold:
                    state = 1

                if rule.up_threshold != "" and value > rule.up_threshold:
                    state = 1

                comparison = Comparisons(self.measurementID, rule.id, None, state)
                db.session.add(comparison)
                db.session.commit()


                if comparison.id > 0:
                    my_logger.debug("A new Comparison instance was inserted.")

                #response["comparison_id"] = comparison.id
                #response["status"] = state
                self.ruleState = state 

            
            #return response


        except Exception, e:
            import traceback
            traceback.print_exc()
        except:
            import traceback
            traceback.print_exc()




    def estimateFallRisk(self):

        try:

            # get rule instance based on 

            
            risk = Risk(input["comparison_id"], float(input["status"]))
            db.session.add(risk)
            db.session.commit()

            if risk.id >0:
                my_logger.debug("A new risk instance was inserted.")



            # send notification email whether risk > 0
            if float(input["status"])>0:
                email = Email.default_settings()
                receiver = list()
                receiver.append(contact)

                text = "Dear user,\n\nThe measurement <A> was out of the border.\nValue:"
                text += str(float(input["status"]))
                text += "\n\n"
                text += "The Angel team"

                email.send_email(receiver, text)

        except Exception, e:
            import traceback
            traceback.print_exc()
        except:
            import traceback
            traceback.print_exc()


