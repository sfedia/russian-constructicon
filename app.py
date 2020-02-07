#!/usr/bin/python3

from flask import Flask, jsonify, Markup, render_template, request, send_file, make_response
import requests
app = Flask(__name__)


@app.route('/<url>', methods=["GET", "POST"])
def redirect(url):
    return requests.get(url, params=request.args)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
