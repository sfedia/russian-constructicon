#!/usr/bin/python3

from sqlite_browser import *


browser = BaseBrowser()

f = browser.generate_filter({
    "syntax": ["Clause", "Cause"],
    "cefr": ["B1", "C2"],
    "language": ["rus"]
})

e = browser.get_entries(f)
for _id, data in e:
    print(_id)
    print(data)
    print()

browser.stop_session()