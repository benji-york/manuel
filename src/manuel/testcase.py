import re
import string
import textwrap

import manuel
import manuel.testing

punctuation = re.escape(string.punctuation)
SECTION_TITLE = re.compile(r"^.+$", re.MULTILINE)
SECTION_UNDERLINE = re.compile("^[" + punctuation + "]+\s*$", re.MULTILINE)
MARKER = re.compile(r"^.. test-case: (\S+)", re.MULTILINE)


def find_section_headers(document):
    for region in document.find_regions(SECTION_TITLE, SECTION_UNDERLINE):
        # regions that represent titles will have two lines
        if region.source.count("\n") != 2:
            continue

        title, underline = region.source.splitlines()

        # the underline has to be the same length as or longer than the title
        if len(underline) < len(title):
            continue

        # ok, this is a region we want
        document.claim_region(region)

        test_case_name = title.strip()
        region.parsed = manuel.testing.TestCaseMarker(test_case_name)


def find_markers(document):
    for region in document.find_regions(MARKER):
        document.claim_region(region)
        test_case_name = region.start_match.group(1)
        region.parsed = manuel.testing.TestCaseMarker(test_case_name)


class SectionManuel(manuel.Manuel):
    def __init__(self):
        manuel.Manuel.__init__(self, [find_section_headers])


class MarkerManuel(manuel.Manuel):
    def __init__(self):
        manuel.Manuel.__init__(self, [find_markers])
