from flask import make_response, jsonify
import random, string

def json_response(json_object={}, status_code=200):
    '''
    CUSTOM: json_response
    ---------------------

    Returns jsonified response object using 'jsonify' and 'make_response' functions in flask.
    Here is the quick example::

        from utils import json_response
        json_response(json_object={'name': 'mohit'}, status_code=200)

    :param json_object: serializable object which will be returned as response.
    :param status_code: status code which should be returned with response.
    '''

    response = make_response(
        jsonify(
            json_object
        ),
        status_code
    )
    response.headers["Content-Type"] = "application/json"
    return response

def get_random_string(size=8, chars=(string.ascii_letters + string.digits)):
    return ''.join(random.choice(chars) for _ in range(size))