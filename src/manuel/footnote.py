import re

import manuel

FOOTNOTE_REFERENCE_LINE_RE = re.compile(r"^.*\[([^\]]+)]_.*$", re.MULTILINE)
FOOTNOTE_REFERENCE_RE = re.compile(r"\[([^\]]+)]_")
FOOTNOTE_DEFINITION_RE = re.compile(r"^\.\.\s*\[\s*([^\]]+)\s*\].*$", re.MULTILINE)
END_OF_FOOTNOTE_RE = re.compile(r"^\S.*$", re.MULTILINE)


class FootnoteReference(object):
    def __init__(self, names):
        self.names = names


class FootnoteDefinition(object):
    def __init__(self, name):
        self.name = name


@manuel.timing(manuel.EARLY)
def find_footnote_references(document):
    # find the markers that show where footnotes have been defined.
    footnote_names = []
    for region in document.find_regions(FOOTNOTE_DEFINITION_RE):
        name = region.start_match.group(1)
        document.claim_region(region)
        region.parsed = FootnoteDefinition(name)
        footnote_names.append(name)

    # find the markers that show where footnotes have been referenced.
    for region in document.find_regions(FOOTNOTE_REFERENCE_LINE_RE):
        assert region.source.count("\n") == 1
        names = FOOTNOTE_REFERENCE_RE.findall(region.source)
        for name in names:
            if name not in footnote_names:
                raise RuntimeError("Unknown footnote: %r" % name)

        assert names
        document.claim_region(region)
        region.parsed = FootnoteReference(names)


@manuel.timing(manuel.LATE)
def do_footnotes(document):
    """Copy footnoted items into their appropriate position."""
    # first find all the regions that are in footnotes
    footnotes = {}
    name = None
    for region in list(document):
        if isinstance(region.parsed, FootnoteDefinition):
            name = region.parsed.name
            footnotes[name] = []
            document.remove_region(region)
            continue

        if END_OF_FOOTNOTE_RE.search(region.source):
            name = None

        if name is not None:
            footnotes[name].append(region)
            document.remove_region(region)

    # now make copies of the footnotes in the right places
    for region in list(document):
        if not isinstance(region.parsed, FootnoteReference):
            continue
        names = region.parsed.names
        for name in names:
            for footnoted in footnotes[name]:
                document.insert_region_before(region, footnoted.copy())
        document.remove_region(region)


class Manuel(manuel.Manuel):
    def __init__(self):
        manuel.Manuel.__init__(self, [find_footnote_references, do_footnotes])
