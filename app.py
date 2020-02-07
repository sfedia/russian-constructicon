#!/usr/bin/python3

from flask import Flask, url_for, request
import requests
app = Flask(__name__)


@app.route('/<string:route_arg>/')
def route(route_arg):
    message = [
        # route_arg - part of route and argument of our view function
        'route_arg = %s ' % route_arg,
        # we can get route_arg from request
        'route_arg from request = %s ' % request.view_args.get('route_arg'),
        # request.args - parameters after '?' in url
        'userID = %s' % request.args.get('userID'),
        'itemID = %s' % request.args.get('itemID'),
        # example of url
        #'url with args = %s' % url_for('route', **dict(request.args))
    ]
    return '<br/>'.join(message)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
