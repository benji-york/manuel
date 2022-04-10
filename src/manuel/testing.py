from __future__ import absolute_import

import doctest as real_doctest
import functools
import inspect
import io
import itertools
import os.path
import re
import sys
import types
import unittest

import manuel

__all__ = ["TestSuite", "TestFactory"]


class TestCaseMarker(object):
    def __init__(self, id=""):
        self.id = id


class TestCase(unittest.TestCase):
    def __init__(self, m, regions, globs, setUp=None, tearDown=None):
        unittest.TestCase.__init__(self)
        self.manuel = m
        self.regions = regions
        self.globs = globs
        self.setUp_func = setUp
        self.tearDown_func = tearDown

    def setUp(self):
        if self.setUp_func is not None:
            self.setUp_func(self)

    def tearDown(self):
        if self.tearDown_func is not None:
            self.tearDown_func(self)

    def runTest(self):
        self.regions.evaluate_with(self.manuel, self.globs)
        self.regions.format_with(self.manuel)
        results = [r.formatted for r in self.regions if r.formatted]
        if results:
            DIVIDER = "-" * 70 + "\n"
            raise real_doctest.DocTestCase.failureException(
                "\n" + DIVIDER + DIVIDER.join(results)
            )

    def debug(self):
        self.setUp()
        self.manuel.debug = True
        self.regions.evaluate_with(self.manuel, self.globs)
        self.tearDown()

    def countTestCases(self):
        return len([r for r in self.regions if r.parsed])

    def shortDescription(self):
        if self.regions.id:
            return self.regions.location + ":" + self.regions.id
        else:
            return self.regions.location

    __str__ = __repr__ = id = shortDescription


def group_regions_by_test_case(document):
    """Generate groups of regions according to which testcase they belong"""
    document_iter = iter(document)
    marker = None
    while True:
        accumulated_regions = manuel.RegionContainer()
        while True:
            region = None  # being defensive
            try:
                region = next(document_iter)
            except StopIteration:
                if not accumulated_regions:
                    break
            else:
                accumulated_regions.append(region)

                if not isinstance(region.parsed, TestCaseMarker):
                    continue

            # we just found a test case marker or hit the end of the
            # document

            # figure out what this test case's ID is
            accumulated_regions.location = document.location
            if marker is not None and marker.parsed.id:
                accumulated_regions.id = marker.parsed.id

            yield accumulated_regions
            marker = region
            break

        # if there are no more regions, stop
        try:
            region = next(document_iter)
        except StopIteration:
            break

        # put the region we peeked at back so the inner loop can consume it
        document_iter = itertools.chain([region], document_iter)


# copied from zope.testing.doctest
def _module_relative_path(module, path):
    if not inspect.ismodule(module):
        raise TypeError("Expected a module: %r" % module)
    if path.startswith("/"):
        raise ValueError("Module-relative files may not have absolute paths")

    # Find the base directory for the path.
    if hasattr(module, "__file__"):
        # A normal module/package
        basedir = os.path.split(module.__file__)[0]
    elif module.__name__ == "__main__":
        # An interactive session.
        if len(sys.argv) > 0 and sys.argv[0] != "":
            basedir = os.path.split(sys.argv[0])[0]
        else:
            basedir = os.curdir
    else:
        # A module w/o __file__ (this includes builtins)
        raise ValueError(
            "Can't resolve paths relative to the module "
            + module
            + " (it has no __file__)"
        )

    # Combine the base directory and the path.
    return os.path.join(basedir, *(path.split("/")))


def TestSuite(m, *paths, **kws):
    """A unittest suite that processes files with Manuel

    The path to each document file is given as a string.

    A number of options may be provided as keyword arguments:

    `setUp`
      A set-up function.  This is called before running the tests in each file.
      The setUp function will be passed a TestCase object.  The setUp function
      can access the test globals as the `globs` attribute of the instance
      passed.

    `tearDown`
      A tear-down function.  This is called after running the tests in each
      file.  The tearDown function will be passed a Manuel object.  The
      tearDown function can access the test globals as the `globs` attribute of
      the instance passed.

    `globs`
      A dictionary containing initial global variables for the tests.

    `TestCase`
      The TestCase class to be used instead of manuel.testing.TestCase.

    """

    suite = unittest.TestSuite()
    globs = kws.pop("globs", {})
    TestCase_class = kws.pop("TestCase", TestCase)

    # walk up the stack frame to find the module that called this function
    for depth in range(1, 5):
        try:
            calling_module = sys.modules[
                sys._getframe(depth).f_globals["__name__"]
            ]
        except KeyError:
            continue
        else:
            break

    for path in paths:
        if os.path.isabs(path):
            abs_path = os.path.normpath(path)
        else:
            abs_path = os.path.abspath(_module_relative_path(calling_module, path))

        with io.open(abs_path, "rt", newline=None) as fp:
            contents = fp.read()
            if not isinstance(contents, str):
                # Python 2, we read unicode, but we really need a str
                contents = contents.encode("utf-8")
            # TODO
            document = manuel.Document(contents, location=abs_path)
        document.parse_with(m)

        for regions in group_regions_by_test_case(document):
            suite.addTest(TestCase_class(m, regions, globs, **kws))

    return suite


_not_word = re.compile(r"\W")


class TestFactory:
    def __init__(self, m):
        self.m = m

    def __call__(self, path):
        base = os.path.dirname(os.path.abspath(sys._getframe(2).f_globals["__file__"]))
        path = os.path.join(base, path)
        with open(path) as f:
            test = f.read()

        m = self.m

        def test_file(self, setup=lambda i: None):
            if isinstance(self, types.FunctionType):
                # We're being used as a decorator. `self` is a setup method.
                f = functools.wraps(self)(lambda inst: test_file(inst, self))
                f.filepath = path
                f.filename = os.path.basename(path)
                return f

            setup(self)
            globs = dict(getattr(self, "globs", ()))
            globs["test"] = self
            document = manuel.Document(test, location=path)
            document.parse_with(m)
            [regions] = group_regions_by_test_case(document)
            TestCase(m, regions, globs).runTest()

        test_file.filepath = path
        test_file.filename = filename = os.path.basename(path)
        name = _not_word.sub("_", os.path.splitext(filename)[0])
        if not name.startswith("test"):
            name = "test_" + name

        test_file.__name__ = name

        return test_file
