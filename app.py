#!/usr/bin/python3

from flask import Flask, url_for, request
import requests
app = Flask(__name__)


@app.route('/<string:route_arg>/', methods=["GET", "POST"])
def route(route_arg):
    return url_for("route", **dict(request.args))


if __name__ == "__main__":
    app.run(host="0.0.0.0")
