

import httplib, urllib
from pymongo import MongoClient
import json
from sqlalchemy import exc
import sys
from ConfigParser import SafeConfigParser
sys.path.append("/opt/fre_package/")
from model import *



class OrionContextBrokerSub(object):

    """ Class related to subscription/unsubscription/update subscription in orion context broker GE """    


    def __init__(self):
        """ 
        Constructor 
        """

        parser = SafeConfigParser()
        parser.read('/etc/sysconfig/fallRiskEvaluation/fallRiskEvaluation.conf')        

        self.attributes = None
    
        # Orion host:port
        self.ip = parser.get('orion', 'HOST')
        self.port = parser.get('orion', 'PORT')

        # APIs host:port
        self.apis_host = parser.get('services', 'HOST')
        self.apis_port = parser.get('services', 'PORT')

        # Subscriber information
        self.reference = "http://" + parser.get('vm', 'PUBLIC_IP') + ':' + parser.get('orion2mysql', 'PORT') + "/orion2mysql"
        self.subID = None


    def getSubscriptionID(self):
        """ Retrieve from mysql	"""

        results = Subscription.query.all()
        ids = list()
        for i in results:
            ids.append(i.key)
        return ids


    def setSubscriptionID(self, subID):
        """ Write to mysql database """

        subscription = Subscription(subID)
        db.session.add(subscription)
        db.session.commit()


    def clearSubscriptionIDs(self):
        """ Delete all instances """

        results = Subscription.query.all()
        for i in results:
            db.session.delete(i)
            db.session.commit()	


    def subscribeContext(self):
        """ Create new subscription """

        # delete orion csubs and mysql instances
        #self.clearSubscriptionIDs()
        self.unsubscribeContext()

        headers = {"Content-type": "application/json","Accept": "application/json"}
        pattern = {"type": "Patient","isPattern": "true","id": ".*"}
        # get attributes list
        self.setAttributesList()
        # prepare npayload
        payload = {"entities":[pattern],"attributes":self.attributes,"reference": self.reference,\
            "duration": "P1Y","notifyConditions": [{"type": "ONCHANGE","condValues": ["timestamp"]}],"throttling": "PT1S"}
        json_payload = json.dumps(payload, separators=(',',':'), indent=4)

        # request
        conn = httplib.HTTPConnection(self.ip, self.port)
        conn.request("POST", "/ngsi10/subscribeContext", json_payload, headers)

        # Handle response and update subscription ID
        response = conn.getresponse()
        r = json.loads(response.read())
        subID = r["subscribeResponse"]["subscriptionId"]
        # Set the sub ID		
        self.setSubscriptionID(subID)


    def updateSubscriptionContext(self):

        self.unsubscribeContext()
        self.subscribeContext()


    def unsubscribeContext(self):
        """ Remove an existing subscription """

        for id in self.getSubscriptionID():
            headers = {"Content-type": "application/json","Accept": "application/json"}
            payload = {"subscriptionId": str(id)}
            json_payload = json.dumps(payload, separators=(',',':'), indent=4)
            conn = httplib.HTTPConnection(self.ip, self.port)
            conn.request("POST", "/ngsi10/unsubscribeContext", json_payload, headers)

            # Handle response and update subscription ID
            response = conn.getresponse()
            r = json.loads(response.read())
            if r["statusCode"]["code"] == "200":
                # delete
                self.clearSubscriptionIDs()
                self.subID = None
                pass
            else:
                #error
                pass


    def setAttributesList(self):
        """
        Retrieve a list of registered biologic parameters as a list
        """

        attributes = []
        attributes.append("timestamp")
        # call a web service
        headers = {"Accept": "application/json"}
        conn = httplib.HTTPConnection(self.apis_host, self.apis_port)
        conn.request("GET", "/biologic_parameters", None, headers)
        response = conn.getresponse()

        if response.status == 200:
            r = json.loads(response.read())
            for i in r["response"]["biologic_parameters"]:
                attributes.append(i["name"])
        else:
            attributes = list()

        self.attributes = attributes

if __name__ == "__main__":
    myObj = OrionContextBrokerSub()
    myObj.updateSubscriptionContext()
