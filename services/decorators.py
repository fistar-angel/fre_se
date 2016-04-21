from flask import Flask, Response, request, jsonify, abort
from functools import wraps
from fiwareAuthentication import *


def authenticate(username=None, password=None):
    """ This function is called to check if the username and password combination is valid. """
 
    isValidUser = fiwareAuthentication()    
    state = isValidUser.credentials(username, password)
    return state


def login_required():
    """ Sends a 401 response that enables basic auth """

    return Response(
        'The authentication proccess of your credentials failed.\n'
        'You have to type the proper FI-WARE credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )
    


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not authenticate(auth.username, auth.password):
            return login_required()
        return f(*args, **kwargs)
    return decorated
