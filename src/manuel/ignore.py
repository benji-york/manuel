import re
import textwrap

import manuel

IGNORE_START = re.compile(r"^\.\.\s*ignore-next-block\s*$", re.MULTILINE)
IGNORE_END = re.compile(r"(?<!ignore-next-block)\n\n(?=\S)|\Z")

baseline = {}


def find_ignores(document):
    for region in document.find_regions(IGNORE_START, IGNORE_END):
        document.claim_region(region)
        region.parsed = object()
        document.remove_region(region)


class Manuel(manuel.Manuel):
    def __init__(self):
        manuel.Manuel.__init__(self, [find_ignores])
