#!/usr/bin/python3

import csv
import konstruktikon_browser
from lxml import etree

fname = "konstruktikon2.xml"
st = ["SemType1", "SemSubType1", "SemType2", "SemSubType2"]
synt = ["Syntactic tag_Old version", "Clause", "Biclausal", "Matrix", "Praedic", "Parenth", "Adj", "Adv", "Conj", "Prep", "Part", "Verb pattern", "Light verb (tag dismissed)", "Nominal pattern"]
karp = "http://spraakbanken.gu.se/eng/research/infrastructure/karp/karp"


class FileUpdate(konstruktikon_browser.Browser):
    def __init__(self, konst_file, base):
        super().__init__(konst_file)
        r_entries = self.lex.xpath("//LexicalEntry")
        bv = list(base.keys())
        for entry in r_entries:
            name = entry.xpath("Sense")[0].attrib["id"].replace("konstruktikon-rus--", "").replace("_", " ")
            if name in base:
                le = VirtualLE(entry, base[name])
                print(name)
                try:
                    bv.remove(name)
                except ValueError:
                    pass
        for name in bv:
            attrs = base[name]
            attrs["name"] = name
            le = VirtualLE(add_attrs=attrs)
            self.lex.addnext(le.entry)

        with open(fname, "wb") as kkn:
            kkn.write(etree.tostring(self.konst_xml, pretty_print=True))
            kkn.close()


class VirtualLE:
    def __init__(self, entry=None, add_attrs=None):
        if add_attrs is None:
            add_attrs = {}
        if entry is not None:
            self.entry = entry
        else:
            self.entry = etree.Element("LexicalEntry")
        if entry is None:
            #self.entry.set("xml:lang", "rus")
            etree.SubElement(self.entry, "feat", attrib={
                "att": "lastmodified",
                "val": "2019-11-28T02:00:00"
            })
            etree.SubElement(self.entry, "feat", attrib={
                "att": "lastmodifiedBy",
                "val": "f.sizov@yandex.ru"
            })
            etree.SubElement(self.entry, "Lemma")
            sense = etree.SubElement(self.entry, "Sense", attrib={
                "id": "konstruktikon-rus--%s" % "_".join(add_attrs["name"].split())
            })
            defn = etree.SubElement(sense, "definition",
                                    namespaces="http://spraakbanken.gu.se/eng/research/infrastructure/karp/karp")
            karp_text = etree.SubElement(defn, etree.QName(karp, "text"), attrib={
                "n": "0"
            })
            karp_text.text = "-"

            etree.SubElement(sense, "feat", attrib={
                "att": "illustration",
                "val": "" if "illustration" not in add_attrs else add_attrs["illustration"]
            })
            etree.SubElement(sense, "feat", attrib={
                "att": "cefr",
                "val": "" if "cefr" not in add_attrs else add_attrs["cefr"]
            })
            etree.SubElement(sense, "feat", attrib={
                "att": "type",
                "val": "konstruktikon"
            })
            etree.SubElement(sense, "feat", attrib={
                "att": "cee",
                "val": "" if "cee" not in add_attrs else add_attrs["cee"]
            })
        else:
            sense = self.entry.xpath("Sense")[0]

        for cat in ["SemType1", "SemSubType1", "SemType2", "SemSubType2"]:
            etree.SubElement(sense, "feat", attrib={
                "att": cat,
                "val": add_attrs[cat]
            })

        etree.SubElement(sense, "feat", attrib={
            "att": "Syntax",
            "val": ",".join(add_attrs["Syntax"])
        })


with open('synt-n-sem.csv', newline='\n', encoding='utf-8') as synt_n_sem:
    w = csv.reader(synt_n_sem, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    base = {}
    for k, row in enumerate(w):
        if k < 2:
            continue
        attribs = {
            "Syntax": []
        }
        for n, k in enumerate(range(8, 12)):
            attribs[st[n]] = row[k]
        for n, k in enumerate(range(15, 15 + 14)):
            if row[k] != "":
                attribs["Syntax"].append(row[k])
        base[row[3]] = attribs


print(base)
fu = FileUpdate(fname, base)

#print(fu)


