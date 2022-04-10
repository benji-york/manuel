import re
import textwrap

import manuel

RESET = re.compile(r"^\.\.\s*reset-globs\s*$", re.MULTILINE)
CAPTURE = re.compile(r"^\.\.\s*capture-globs\s*$", re.MULTILINE)

baseline = {}


class Reset(object):
    pass


def find_reset(document):
    for region in document.find_regions(RESET):
        document.claim_region(region)
        region.parsed = Reset()


def execute_reset(region, document, globs):
    if not isinstance(region.parsed, Reset):
        return

    globs.clear()
    globs.update(baseline)


class Capture(object):
    pass


def find_baseline(document):
    # clear the baseline globs at the begining of a run (a bit of a hack)
    baseline.clear()

    for region in document.find_regions(CAPTURE):
        document.claim_region(region)
        region.parsed = Capture()


def execute_baseline(region, document, globs):
    if not isinstance(region.parsed, Capture):
        return

    baseline.clear()
    baseline.update(globs)


class Manuel(manuel.Manuel):
    def __init__(self):
        manuel.Manuel.__init__(
            self, [find_reset, find_baseline], [execute_reset, execute_baseline]
        )
