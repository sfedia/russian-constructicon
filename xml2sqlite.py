#!/usr/bin/python3

import itertools
import json
import lxml
import sqlite3
from konstruktikon_browser import *


class SQLAgent:
    def __init__(self, sqlite_filename="newBase.sqlite3"):
        self.sqlite_filename = sqlite_filename
        self.connector = sqlite3.connect(self.sqlite_filename)
        #self.connector.enable_load_extension(True)
        #self.connector.load_extension("./json1")
        self.cursor = self.connector.cursor()

    """konstruktikon_xml (entry_id text, field_type text, field_content text)"""

    def add_fields(self, fields, rewrite=False):
        for arg1 in fields:
            self.add_field(arg1, rewrite)

    def change_entry_id(self, id1, id2):
        self.cursor.execute(
            "UPDATE konstruktikon_xml SET entry_id='%s' WHERE entry_id='%s'" % (id1, id2))

    def add_field(self, field_in_list, rewrite=False):
        print(field_in_list)
        entry_id, field_type, field_content = field_in_list
        if rewrite:
            self.cursor.execute(
                "DELETE FROM konstruktikon_xml WHERE entry_id='%s' AND field_type='%s'" % (entry_id, field_type,))

        self.cursor.execute("INSERT INTO konstruktikon_xml VALUES (?, ?, ?)", field_in_list)

        return True

    def stop_session(self):
        self.connector.commit()
        self.connector.close()

    def get_entries(self, selector):
        u_selector = "SELECT * FROM konstruktikon_xml WHERE entry_id IN (%s)" % selector
        results = self.cursor.execute(u_selector).fetchall()
        return itertools.groupby(results, key=lambda x: x[0])


class SQLiteFieldsFrom:
    def __init__(self, lexical_entry):
        self.entry_ = lexical_entry
        #if self.sense_id:
        self.entry = self.entry_.xpath("Sense")[0]
        self.karp_ns = dict(namespaces={
            "karp": "http://spraakbanken.gu.se/eng/research/infrastructure/karp/karp"
        })
        self.my_fields = []

    def build_fields(self):
        # create table konstruktikon_xml (entry_id text, field_type text, field_content text)
        if self.language:
            self.my_fields.append(
                [self.sense_id, "language", self.language]
            )
        if self.cee:
            self.my_fields.append(
                [self.sense_id, "cee", self.py2sqlt(self.cee)]
            )
        if self.cefr_level:
            self.my_fields.append(
                [self.sense_id, "cefr", self.cefr_level]
            )
        if self.definition_json:
            self.my_fields.append(
                [self.sense_id, "definition", self.py2sqlt(self.definition_json)]
            )
        if self.examples_json:
            self.my_fields.append(
                [self.sense_id, "examples", self.py2sqlt(self.examples_json)]
            )
        if self.syntax:
            self.my_fields.append(
                [self.sense_id, "syntax", self.py2sqlt(self.syntax)]
            )
        if self.illustration:
            self.my_fields.append(
                [self.sense_id, "illustration", self.illustration]
            )
        if self.last_modified:
            self.my_fields.append(
                [self.sense_id, "lastModified", self.last_modified]
            )
        if self.last_modified_by:
            self.my_fields.append(
                [self.sense_id, "lastModifiedBy", self.last_modified_by]
            )
        if self.structures:
            self.my_fields.append(
                [self.sense_id, "Structures", self.py2sqlt(self.structures)]
            )
        for (level, value) in self.sem_types:
            if value:
                self.my_fields.append(
                    [self.sense_id, "Sem" + ("Sub" if level[1] > 0 else "") + "Type" + str(level[0]),
                     value]
                )

        return self.my_fields

    @staticmethod
    def py2sqlt(raw):
        if type(raw) == str:
            return raw
        elif type(raw) == list:
            if raw and type(raw[0]) == dict:
                return json.dumps(raw)
            else:
                return json.dumps(raw)
        elif raw:
            return json.dumps(raw)

    @property
    def sense_id(self):
        try:
            return self.entry_.xpath("Sense")[0].attrib["id"]
        except IndexError:
            return None

    @property
    def sem_types(self):
        return [
            ((1, 0), self.caught_feat("SemType1")),
            ((1, 1), self.caught_feat("SemSubType1")),
            ((2, 0), self.caught_feat("SemType2")),
            ((2, 1), self.caught_feat("SemSubType2"))
        ]

    def caught_feat(self, att, from_=None):
        from_ = from_ if from_ else self.entry
        try:
            return from_.xpath("feat[@att='{0}']".format(att))[0].attrib["val"]
        except IndexError:
            return None

    def caught_multi_feat(self, att):
        get = self.entry.xpath("feat[@att='{0}']".format(att))
        return None if not get else [t.attrib["val"] for t in get]

    @property
    def language(self):
        for (attr, val) in self.entry_.attrib.items():
            if attr.endswith("lang"):
                return val
        return None

    @staticmethod
    def nsfree(tag_name):
        ns, tag = tag_name.split("}")
        return tag

    @property
    def example_tags(self):
        tags = self.entry.xpath("karp:example", **self.karp_ns)
        return tags if tags else None

    def parse_example(self, example_tag):
        linear = example_tag.xpath("karp:e|karp:text|karp:g", **self.karp_ns)
        json_f = []
        for element in linear:
            if self.nsfree(element.tag) in ["text", "g"]:
                obj = {
                    "type": "SimpleType",
                    "cat": self.nsfree(element.tag),
                    "content": element.text
                }
                for attr in ["name", "n"]:
                    if attr in element.attrib:
                        obj[attr] = element.attrib[attr]
                json_f.append(obj)
            elif self.nsfree(element.tag) == "e":
                json_f.append({
                    "type": "ETag",
                    "children": self.process_e(element),
                    "name": element.attrib["name"]
                })

        return json_f

    def process_e(self, e_tag):
        sub_linear = e_tag.xpath("karp:e|karp:text|karp:g", **self.karp_ns)
        json_f = []
        for element in sub_linear:
            obj = {
                "type": "InsideETag",
                "cat": self.nsfree(element.tag),
                "content": element.text
            }
            for attr in ["name", "n"]:
                if attr in element.attrib:
                    obj[attr] = element.attrib[attr]
            json_f.append(obj)

        return json_f

    @property
    def definition_json(self):
        defs = self.entry.xpath("definition", **self.karp_ns)
        if not len(defs):
            return {}
        my_def = defs[0]
        in_def = my_def.xpath("karp:e|karp:text|karp:g", **self.karp_ns)
        json_f = []
        for element in in_def:
            obj = {
                "type": "InsideDefinition",
                "cat": self.nsfree(element.tag),
                "content": element.text
            }
            for attr in ["name", "n"]:
                if attr in element.attrib:
                    obj[attr] = element.attrib[attr]
            json_f.append(obj)

        return dict(definition=json_f)

    @property
    def const_objects_json(self):
        return {}

    @property
    def examples_json(self):
        array = []
        if self.example_tags:
            for example in self.example_tags:
                array.append(self.parse_example(example))
            return {"examples": array}
        else:
            return {"examples": []}

    @property
    def last_modified(self):
        return self.caught_feat("lastmodified", self.entry_)

    @property
    def last_modified_by(self):
        return self.caught_feat("lastmodifiedBy", self.entry_)

    @property
    def name(self):
        if self.sense_id:
            pref, nme = self.sense_id.split("--")
            return nme

    @property
    def illustration(self):
        return self.caught_feat("illustration")

    @property
    def cefr_level(self):
        return self.caught_feat("cefr")

    @property
    def _type_(self):
        return self.caught_feat("type")

    @property
    def syntax(self):
        res = self.caught_feat("Syntax")
        if not res:
            return res
        return res.split(",")

    @property
    def cee(self):
        return self.caught_multi_feat("cee")

    @property
    def structures(self):
        return self.caught_multi_feat("structure")


if __name__ == "__main__":
    konst2 = Browser("konstruktikon2.xml")
    lex = konst2.lex
    agent = SQLAgent()
    sqlt_bases = []
    lengths = []

    print(len(lex.xpath("//LexicalEntry")))
    for j, entry in enumerate(lex.xpath("//LexicalEntry")):
        q = SQLiteFieldsFrom(entry)
        agent.add_fields(q.build_fields())
        print(q.build_fields())

    agent.stop_session()