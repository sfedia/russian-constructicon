#!/usr/bin/python3

from flask import Flask, jsonify, Markup, render_template, request
from lxml import etree
import json
import konstruktikon_browser
import math
import re
import urllib.parse

browser = konstruktikon_browser.Browser("konstruktikon2.xml")
app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template("main_page.html")


def karp_example2html(example_tag):
    inner_html = etree.tostring(example_tag, pretty_print=True, encoding="unicode")
    x = re.sub(r"</?karp:example.*>", "", inner_html)
    x = re.sub(r"</?definition>", "", x) # if 'definition' tag was passed in args2
    x = re.sub(r'<karp:e\s+.*name="([^"]+)"[^>]*>', '<font color="red"><small>\g<1>[</small></font>', x)
    x = re.sub(r'</karp:e>(?=[\n\s\t]*<karp:[^g])', '<font color="red"></small>]</small></font>&nbsp;', x)
    x = re.sub(r'</karp:e>', '<font color="red"></small>]</small></font>', x)
    x = re.sub(r'<karp:g[^>]*>', '', x)
    x = re.sub(r'</*karp:text[^>]*/*\s*>', '', x)
    return Markup(x)


def karp_example2cats(example_tag):
    inner_html = etree.tostring(example_tag, pretty_print=True, encoding="unicode")
    x = re.sub(r"</?karp:example.*>", "", inner_html)
    x = re.sub(r"</?definition>", "", x)  # if 'definition' tag was passed in args2
    cats = [mth.group(1) for mth in re.finditer(r'<karp:e\s+.*name="([^"]+)"[^>]*>', x)]
    return cats


@app.route("/hints")
def ajax_hints():
    if "prefix" not in request.args:
        return jsonify(
            {"error": "Prefix expected, but was not found"}
        )

    limit = 5 if "limit" not in request.args else int(request.args["limit"])
    hints = []

    for entry in browser.entries_walk({
        "prefix": request.args["prefix"]
    }):
        name = entry.xpath("Sense")[0].attrib["id"]
        meta, name = name.split("--")
        hints.append(" ".join(name.split("_")))
        limit -= 1
        if not limit:
            break

    return jsonify(
        {"hints": hints}
    )


SEARCH_URL = "/search"


@app.route(SEARCH_URL)
def browser_search():
    if "q" not in request.args:
        return "Invalid request"

    offset = 0 if "offset" not in request.args else int(request.args["offset"])
    selected_index = 1 if "index" not in request.args else int(request.args["index"])

    try:
        query = json.loads(request.args["q"])
        if type(query) != dict:
            raise json.decoder.JSONDecodeError
    except json.decoder.JSONDecodeError:
        return "Invalid request"

    results = browser.entries_walk(query)
    max_on_page = 5
    max_offsets = 20

    basic_url = SEARCH_URL + "?q=" + urllib.parse.quote(request.args["q"])
    index_url = [basic_url]

    if len(results) < max_on_page * max_offsets:
        page_indexes = list(range(1, math.ceil(len(results) / max_on_page) + 1))
        pages_count = max_on_page
        for index in page_indexes:
            index_url.append(basic_url + "&offset=" + str(max_on_page * index) + "&index=" + str(index + 1))
    else:
        page_indexes = list(range(1, max_offsets + 1))
        rest = math.ceil(len(results) / max_offsets)
        pages_count = rest
        for n in range(1, max_offsets):
            index_url.append(basic_url + "&offset=" + str(rest * n) + "&index=" + str(n + 1))

    query = json.loads(request.args["q"])
    found = browser.entries_walk(query)
    entries = []

    for tag in found:
        entry_dict = {}
        name = tag.xpath("Sense")[0].attrib["id"]
        entry_dict["ID"] = name
        meta, name = name.split("--")
        entry_dict["name"] = " ".join(name.split("_"))

        for param in ["cefr", "illustration", "structure"]:
            try:
                entry_dict[param] = tag.xpath("Sense/feat[@att='{0}']".format(param))[0].attrib["val"]
            except IndexError:
                entry_dict[param] = "?"

        entry_dict["definition"] = karp_example2html(tag.xpath("Sense/definition")[0])
        entry_dict["content_cats"] = karp_example2cats(tag.xpath("Sense/definition")[0])
        entry_dict["content_cats"] = Markup(",&nbsp;".join([
            ('<a href="{1}" class="__field__ccat"><font color="red" class="ccat"><small class="ccat">{0}</small>' +
            '</font></a>').format(
                cat, '/search?q=%s' % urllib.parse.quote('{"sem_search":["%s"]}' % cat)
            )
            for cat in set(entry_dict["content_cats"])
            if not re.search(r'[А-Яа-я]', cat)
        ]))

        karp = dict(namespaces={
            "karp": "http://spraakbanken.gu.se/eng/research/infrastructure/karp/karp"
        })
        examples = tag.xpath("Sense/karp:example", **karp)
        entry_dict["examples"] = []

        for examp in examples:
            try:
                examp_name = examp.xpath("karp:e", **karp)[0].attrib["name"]
            except IndexError:
                continue
            entry_dict["examples"].append({
                "name": examp_name,
                "sentence": karp_example2html(examp)
            })

        entries.append(entry_dict)

    return render_template(
        "search_results.html",
        count=len(entries),
        entries=entries[offset:offset+pages_count],
        index_url=index_url,
        page_indexes=page_indexes,
        selected_index=selected_index
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0")
