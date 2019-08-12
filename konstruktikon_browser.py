#!/usr/bin/python3

from lxml import etree
import re


class Browser:
    def __init__(self, konst_file):
        self.konst_file = konst_file
        self.konst_xml = etree.parse(konst_file)
        self.lex = self.konst_xml.xpath("/LexicalResource/Lexicon")[0]


class StructureParser:
    def __init__(self, q):
        q = re.sub("\[(\w+)\]", "<\g<1>/>", q)
        q = re.sub("\[(\w+)", "<\g<1>>", q)
        q = q.replace(" ", "")
        tag_groups = []

        for group in re.split("\]+", q):
            if not group:
                continue
            tag_groups.append(re.findall("<\w+>", group))

        g = -1
        b = False
        for e, char in enumerate(q):
            if not b and char == "]":
                b = True
                g += 1
            if char == "]":
                try:
                    q = q.replace("]", "</" + tag_groups[g].pop()[1:], 1)
                except IndexError:
                    pass
            else:
                b = False

        for group in reversed(tag_groups):
            for tag in reversed(group):
                q = q.replace("]", "</" + tag[1:], 1)

        self.tree = etree.fromstring(q)

    @staticmethod
    def between_tags(tag1, tag2, same_level=True):
        query = "//*["
        query += "preceding::" + tag1 + " and following::" + tag2
        if same_level:
            query += " and count(ancestor::*) = count(" + tag1 + "/ancestor::*)"
        query += "]"

        return query

    @staticmethod
    def test(filt):
        # TODO
        return True


class LexicalEntry:
    def __init__(self, entry_tag):
        self.entry_tag = entry_tag

    def test_entry(self, filter_dict):
        return  self.name_prefix(filter_dict["prefix"]) or \
                self.cefr(filter_dict["cefr"]) or \
                self.language(filter_dict["language"]) or \
                self.toksem_and_filsem(filter_dict["sem_search"]) or \
                self.structure_contains(filter_dict["structure"])

    def name_prefix(self, prefix):
        try:
            name_elem = self.entry_tag.xpath("Sense/feat[@att='illustration']")[0]
        except IndexError:
            return False

        prefix = " ".join(prefix.lower().split())
        try:
            return " ".join(name_elem.attrib["val"].lower().split()).startswith(prefix)
        except KeyError:
            return False

    def cefr(self, cefr_options):
        try:
            cefr_elem = self.entry_tag.xpath("Sense/feat[@att='cefr']")[0]
        except IndexError:
            return False

        try:
            return cefr_elem.attrib["val"] in cefr_options
        except KeyError:
            return False

    @staticmethod
    def language(language_options):
        # TODO
        return True

    def toksem_and_filsem(self, filsem):
        try:
            first_def = self.entry_tag.xpath("Sense/definition")[0]
        except IndexError:
            return False

        for karp_tag in first_def.xpath("*"):
            if "name" in karp_tag.attrib and karp_tag.attrib["name"].strip("., ") in filsem:
                return True

        return False

    def structure_contains(self, struct_filter):
        structures = self.entry_tag.xpath("Sense/feat[@att='structure']")
        for struct in structures:
            parser = StructureParser(struct)
            if parser.test(struct_filter):
                return True

        return False


browser = Browser("konstruktikon.xml")
entry1 = browser.lex.xpath("LexicalEntry")[0]
entry1 = LexicalEntry(entry1)

print(entry1.toksem_and_filsem(["Theme"]))

