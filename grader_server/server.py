import os
from datetime import timedelta  
from flask import Flask, make_response, request, current_app  
from functools import update_wrapper

def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):  
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

def load_matches():
    d = {}
    with open('matches.csv') as f:
        for line in f:
            line_sp = line.split(',')
            sunet = line_sp[0].strip()
            if "@" in sunet:
                sunet = sunet.split('@')[0]
            grader = line_sp[1].strip()
            d[sunet] = grader
    return d
    

app = Flask(__name__)
graders = load_matches()

@app.route('/')
def hello():
    return 'use: /grader?sunet=your_sunet'

@app.route('/grader')
@crossdomain(origin="*")
def grader():
    sunet = request.args.get('sunet','').lower()
    if len(sunet) < 0 or len(sunet) > 100:
        return "Bad sunet"
    grader = graders.get(sunet,None)
    if grader:
        return "Your grader is %s. You can now answer Question 0! Congrats!" % grader
    else:
        return "We do not have you in our spreadsheet yet, so send us an email!"

