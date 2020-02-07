#!/usr/bin/python3

from flask import Flask, jsonify, Markup, render_template, request, send_file, make_response
from lxml import etree
from lxml.html import fromstring
import html
import json
import konstruktikon_browser
import login
import math
import os
import re
import sqlite_browser
import urllib.parse

browser = konstruktikon_browser.Browser("konstruktikon2.xml")
app = Flask(__name__)


@app.route('/<page>?<context>', methods=["GET", "POST"])
def redirect(page, context):
    return context


if __name__ == "__main__":
    app.run(host="0.0.0.0")
