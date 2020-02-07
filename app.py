#!/usr/bin/python3

from flask import Flask, url_for, request, redirect
import requests
app = Flask(__name__)


@app.route('/<string:param>', strict_slashes=False)
def route(param=None, **kwargs):
    return redirect("http://84.201.175.184:5000/", code=302)


@app.route('/', strict_slashes=False)
def main_f():
    return redirect("http://84.201.175.184:5000/", code=302)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
