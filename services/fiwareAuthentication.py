import httplib, urllib
import json
import sys


class fiwareAuthentication(object):
    """
    Authenticate a user based on his credentials in FI-WARE (idM GE)
    """

    def __init__(self):
        """
        Constructor
        """
        self.url = "http://cloud.lab.fi-ware.org:4730/v2.0/tokens"
        self.ip = "130.206.82.10"
        self.host = "cloud.lab.fi-ware.org"
        self.port = 4730
        self.path = "/v2.0/tokens"
        self.headers = {"Content-Type": "application/json","Accept": "application/json"}


    def credentials(self, email, password):
        """ Check if the incoming credentials are valid. """
        
        try:
            # payload as JSON structure
            _payload = {"auth": {"passwordCredentials": {"username": email, "password": password}}}
            payload = json.dumps(_payload, separators=(',',':'), indent=4)

            # create a connection
            conn = httplib.HTTPConnection(self.ip, self.port)    
            conn.request("POST", "/v2.0/tokens", payload, self.headers)

            try:
                # handle response
                response = conn.getresponse()
                if response.status == 200:
                    return True
                raise Exception("Reponse error")
            except:
                raise Exception("Reponse error")


        except Exception, e:
            return False
        except:
            import traceback
            traceback.print_exc()
            raise Exception("Reponse error")


if __name__ == "__main__":
    obj = fiwareAuthentication()
    obj.credentials("aaaa", "bbbbb")
