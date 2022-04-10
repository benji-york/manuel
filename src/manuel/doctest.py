from __future__ import absolute_import

import doctest
import os.path

import six

import manuel

DocTestRunner = doctest.DocTestRunner
DebugRunner = doctest.DebugRunner


class DocTestResult(six.StringIO):
    pass


def parse(m, document, parser):
    for region in list(document):
        if region.parsed:
            continue
        region_start = region.lineno
        region_end = region.lineno + region.source.count("\n")
        for chunk in parser.parse(region.source):
            # If the chunk contains prose (as opposed to and example), skip it.
            if isinstance(chunk, str):
                continue

            chunk._manual = m
            chunk_line_count = chunk.source.count("\n") + chunk.want.count("\n")

            split_line_1 = region_start + chunk.lineno
            split_line_2 = split_line_1 + chunk_line_count

            # if there is some source we need to trim off the front...
            if split_line_1 > region.lineno:
                _, region = document.split_region(region, split_line_1)

            if split_line_2 < region_end:
                found, region = document.split_region(region, split_line_2)
            else:
                found = region

            document.claim_region(found)

            # Since we're treating each example as a stand-alone thing, we need
            # to reset its line number to zero.
            chunk.lineno = 0
            found.parsed = chunk

            assert region in document


class DocTest(doctest.DocTest):
    def __init__(self, examples, globs, name, filename, lineno, docstring):
        # do everything like regular doctests, but don't make a copy of globs
        doctest.DocTest.__init__(
            self, examples, globs, name, filename, lineno, docstring
        )
        self.globs = globs


def evaluate(m, region, document, globs):
    # If the parsed object is not a doctest Example then we don't need to
    # handle it.

    if getattr(region.parsed, "_manual", None) is not m:
        return

    result = DocTestResult()
    test_name = os.path.split(document.location)[1]
    if m.debug:
        runner = m.debug_runner
        out = None
    else:
        runner = m.runner
        out = result.write

    # Use the testrunner-set option flags when running these tests.
    old_optionflags = runner.optionflags
    runner.optionflags |= doctest._unittest_reportflags
    runner.DIVIDER = ""  # disable unwanted result formatting

    # Here's where everything happens.
    example = region.parsed
    runner.run(
        DocTest(
            [example], globs, test_name, document.location, region.lineno - 1, None
        ),
        out=out,
        clear_globs=False,
    )

    runner.optionflags = old_optionflags  # Reset the option flags.
    region.evaluated = result


def format(document):
    for region in document:
        if not isinstance(region.evaluated, DocTestResult):
            continue
        region.formatted = region.evaluated.getvalue().lstrip()


class Manuel(manuel.Manuel):
    def __init__(self, optionflags=0, checker=None, parser=None):
        self.runner = DocTestRunner(
            optionflags=optionflags, checker=checker, verbose=False
        )
        self.debug_runner = DebugRunner(optionflags=optionflags, verbose=False)

        def evaluate_closure(region, document, globs):
            # capture "self"
            evaluate(self, region, document, globs)

        parser = parser or doctest.DocTestParser()
        manuel.Manuel.__init__(
            self,
            [lambda document: parse(self, document, parser)],
            [evaluate_closure],
            [format],
        )
