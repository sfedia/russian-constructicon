#!/usr/bin/python3

from flask import Flask, jsonify, Markup, render_template, request, send_file, make_response
app = Flask(__name__)


@app.route('/<page>?<context>', methods=["GET", "POST"])
def redirect(page, context):
    return context


if __name__ == "__main__":
    app.run(host="0.0.0.0")
