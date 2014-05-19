.. _theory-of-operation:

Theory of Operation
===================

.. XXX this really wants to be a "How To Write a Plug-in" tutorial.

Manuel parses documents (tests), evaluates their contents, then formats the
result of the evaluation.  The functionality is accessed via the :mod:`manuel`
package.

    >>> import manuel

Parsing
-------

Manuel operates on Documents.  Each Document is created from a string
containing one or more lines.

    >>> source = """\
    ... This is our document, it has several lines.
    ... one: 1, 2, 3
    ... two: 4, 5, 7
    ... three: 3, 5, 1
    ... """
    >>> document = manuel.Document(source)

For example purposes we will create a type of test that consists of a sequence
of numbers. Lets create a NumbersTest object to represent the parsed list.

    >>> class NumbersTest(object):
    ...     def __init__(self, description, numbers):
    ...         self.description = description
    ...         self.numbers = numbers

The Document is divided into one or more regions.  Each region is a distinct
"chunk" of the document and will be acted uppon in later (post-parsing) phases.
Initially the Document is made up of a single element, the source string.

    >>> [region.source for region in document]
    ['This is our document, it has several lines.\none: 1, 2, 3\ntwo: 4, 5, 7\nthree: 3, 5, 1\n']

The Document offers a "find_regions" method to assist in locating the portions
of the document a particular parser is interested in.  Given a regular
expression (either as a string, or compiled), it will return "region" objects
that contain the matched source text, the line number (1 based) the region
begins at, as well as the associated re.Match object.

    >>> import re
    >>> numbers_test_finder = re.compile(
    ...     r'^(?P<description>.*?): (?P<numbers>(\d+,?[ ]?)+)$', re.MULTILINE)
    >>> regions = document.find_regions(numbers_test_finder)
    >>> regions
    [<manuel.Region object at 0x...>,
     <manuel.Region object at 0x...>,
     <manuel.Region object at 0x...>]
    >>> regions[0].lineno
    2
    >>> regions[0].source
    'one: 1, 2, 3\n'
    >>> regions[0].start_match.group('description')
    'one'
    >>> regions[0].start_match.group('numbers')
    '1, 2, 3'

If given two regular expressions find_regions will use the first to identify
the begining of a region and the second to identify the end.

    >>> region = document.find_regions(
    ...     re.compile('^one:.*$', re.MULTILINE),
    ...     re.compile('^three:.*$', re.MULTILINE),
    ...     )[0]
    >>> region.lineno
    2
    >>> six.print_(region.source)
    one: 1, 2, 3
    two: 4, 5, 7
    three: 3, 5, 1

Also, instead of just a "start_match" attribute, the region will have
start_match and end_match attributes.

    >>> region.start_match
    <..._sre.SRE_Match object...>
    >>> region.end_match
    <..._sre.SRE_Match object...>


Regions must always consist of whole lines.

    >>> document.find_regions('1, 2, 3')
    Traceback (most recent call last):
        ...
    ValueError: Regions must start at the begining of a line.

.. more "whole-line" tests.

    >>> document.find_regions(
    ...     re.compile('ne:.*$', re.MULTILINE),
    ...     re.compile('^one:.*$', re.MULTILINE),
    ...     )
    Traceback (most recent call last):
        ...
    ValueError: Regions must start at the begining of a line.

Now we can register a parser that will identify the regions we're interested in
and create NumbersTest objects from the source text.

    >>> def parse(document):
    ...     for region in document.find_regions(numbers_test_finder):
    ...         description = region.start_match.group('description')
    ...         numbers = list(map(
    ...             int, region.start_match.group('numbers').split(',')))
    ...         test = NumbersTest(description, numbers)
    ...         document.claim_region(region)
    ...         region.parsed = test

    >>> parse(document)
    >>> [region.source for region in document]
    ['This is our document, it has several lines.\n',
     'one: 1, 2, 3\n',
     'two: 4, 5, 7\n',
     'three: 3, 5, 1\n']
    >>> [region.parsed for region in document]
    [None,
     <NumbersTest object at 0x...>,
     <NumbersTest object at 0x...>,
     <NumbersTest object at 0x...>]


Evaluation
----------

After a document has been parsed the resulting tests are evaluated.  Unlike
parsing and formatting, evaluation is done one region at a time, in the order
that the regions appear in the document.  Lets define a function to evaluate
NumberTests.  The function determines whether or not the numbers are in sorted
order and records the result along with the description of the list of numbers.

.. code-block:: python

   class NumbersResult(object):
       def __init__(self, test, passed):
           self.test = test
           self.passed = passed

   def evaluate(region, document, globs):
       if not isinstance(region.parsed, NumbersTest):
           return
       test = region.parsed
       passed = sorted(test.numbers) == test.numbers
       region.evaluated = NumbersResult(test, passed)

.. a test of the above

    >>> for region in document:
    ...     evaluate(region, document, {})
    >>> [region.evaluated for region in document]
    [None,
     <NumbersResult object at 0x...>,
     <NumbersResult object at 0x...>,
     <NumbersResult object at 0x...>]


Formatting
----------

Once the evaluation phase is completed the results are formatted.  You guessed
it: Manuel provides a method for formatting results.  We'll build one to format
a message about whether or not our lists of numbers are sorted properly.  A
formatting function returns None when it has no output, or a string otherwise.

.. code-block:: python

    def format(document):
        for region in document:
            if not isinstance(region.evaluated, NumbersResult):
                continue
            result = region.evaluated
            if not result.passed:
                region.formatted = (
                    "the numbers aren't in sorted order: %s\n"
                    % ', '.join(map(str, result.test.numbers)))

Since one of the test cases failed we get an appropriate message out of the
formatter.

    >>> format(document)
    >>> [region.formatted for region in document]
    [None, None, None, "the numbers aren't in sorted order: 3, 5, 1\n"]


Manuel Objects
--------------

We'll want to use these parse, evaluate, and format functions later, so we
bundle them together into a Manuel object.

    >>> sorted_numbers_manuel = manuel.Manuel(
    ...     parsers=[parse], evaluaters=[evaluate], formatters=[format])


Doctests
--------

We can use Manuel to run doctests.  Let's create a simple doctest to
demonstrate with.

    >>> source = """This is my
    ... doctest.
    ...
    ...     >>> 1 + 1
    ...     2
    ... """
    >>> document = manuel.Document(source)

The :mod:`manuel.doctest` module has handlers for the various phases.  First
we'll look at parsing.

    >>> import manuel.doctest
    >>> m = manuel.doctest.Manuel()
    >>> document.parse_with(m)
    >>> for region in document:
    ...     print((region.lineno, region.parsed or region.source))
    (1, 'This is my\ndoctest.\n\n')
    (4, <doctest.Example ...>)

Now we can evaluate the examples.

    >>> document.evaluate_with(m, globs={})
    >>> for region in document:
    ...     print((region.lineno, region.evaluated or region.source))
    (1, 'This is my\ndoctest.\n\n')
    (4, <manuel.doctest.DocTestResult ...>)

And format the results.

    >>> document.format_with(m)
    >>> document.formatted()
    ''

Oh, we didn't have any failing tests, so we got no output.  Let's try again
with a failing test.  This time we'll use the "process_with" function to
simplify things.

    >>> document = manuel.Document("""This is my
    ... doctest.
    ...
    ...     >>> 1 + 1
    ...     42
    ... """)
    >>> document.process_with(m, globs={})
    >>> six.print_(document.formatted(), end='')
    File "<memory>", line 4, in <memory>
    Failed example:
        1 + 1
    Expected:
        42
    Got:
        2

Alternate doctest parsers
~~~~~~~~~~~~~~~~~~~~~~~~~

You can pass an alternate doctest parser to manuel.doctest.Manuel to
customize how examples are parsed.  Here's an example that changes the
example start string from ">>>" to "py>":

    >>> import doctest
    >>> class DocTestPyParser(doctest.DocTestParser):
    ...    _EXAMPLE_RE = re.compile(r'''
    ...        (?P<source>
    ...             (?:^(?P<indent> [ ]*) py>    .*)    # PS1 line
    ...            (?:\n           [ ]*  \.\.\. .*)*)  # PS2 lines
    ...        \n?
    ...        (?P<want> (?:(?![ ]*$)    # Not a blank line
    ...                     (?![ ]*py>)  # Not a line starting with PS1
    ...                     .*$\n?       # But any other line
    ...                  )*)
    ...        ''', re.MULTILINE | re.VERBOSE)

    >>> m = manuel.doctest.Manuel(parser=DocTestPyParser())
    >>> document = manuel.Document("""This is my
    ... doctest.
    ...
    ...     py> 1 + 1
    ...     42
    ... """)
    >>> document.process_with(m, globs={})
    >>> six.print_(document.formatted(), end='')
    File "<memory>", line 4, in <memory>
    Failed example:
        1 + 1
    Expected:
        42
    Got:
        2

Multiple doctest parsers
~~~~~~~~~~~~~~~~~~~~~~~~

You may use several doctest parsers in the same session, for example,
to support shell commands and Python code in the same document.

    >>> m = (manuel.doctest.Manuel(parser=DocTestPyParser()) +
    ...      manuel.doctest.Manuel())

    >>> document = manuel.Document("""
    ...
    ...     py> i = 0
    ...     py> i += 1
    ...     py> i
    ...     1
    ...
    ...     >>> j = 0
    ...     >>> j += 1
    ...     >>> j
    ...     1
    ...
    ... """)
    >>> document.process_with(m, globs={})
    >>> six.print_(document.formatted(), end='')

Globals
-------

Even though each region is parsed into its own object, state is still shared
between them.  Each region of the document is executed in order so state
changes made by earlier evaluaters are available to the current evaluator.


    >>> document = manuel.Document("""
    ...     >>> x = 1
    ...
    ... A little prose to separate the examples.
    ...
    ...     >>> x
    ...     1
    ... """)
    >>> document.process_with(m, globs={})
    >>> six.print_(document.formatted(), end='')

Imported modules are added to the global namespace as well.

    >>> document = manuel.Document("""
    ...     >>> import string
    ...
    ... A little prose to separate the examples.
    ...
    ...     >>> string.digits
    ...     '0123456789'
    ...
    ... """)
    >>> document.process_with(m, globs={})
    >>> six.print_(document.formatted(), end='')


Combining Test Types
--------------------

Now that we have both doctests and the silly "sorted numbers" tests, let's
create a single document that has both.

    >>> document = manuel.Document("""
    ... We can have a list of numbers...
    ...
    ...     a very nice list: 3, 6, 2
    ...
    ... ... and we can test Python.
    ...
    ...     >>> 1 + 1
    ...     42
    ...
    ... """)

Obviously both of those tests will fail, but first we have to configure Manuel
to understand both test types.  We'll start with a doctest configuration and add
the number list testing on top.

    >>> m = manuel.doctest.Manuel()

Since we already have a Manuel instance configured for our "sorted numbers"
tests, we can extend the built-in doctest configuration with it.

    >>> m += sorted_numbers_manuel

Now we can process our source that combines both types of tests and see what
we get.

    >>> document.process_with(m, globs={})

The document was parsed and has a mixture of prose and parsed doctests and
number tests.

    >>> for region in document:
    ...     print((region.lineno, region.parsed or region.source))
    (1, '\nWe can have a list of numbers...\n\n')
    (4, <NumbersTest object at 0x...>)
    (5, '\n... and we can test Python.\n\n')
    (8, <doctest.Example ...>)
    (10, '\n')

We can look at the formatted output to see that each of the two tests failed.

    >>> for region in document:
    ...     if region.formatted:
    ...         six.print_('-'*70)
    ...         six.print_(region.formatted, end='')
    ----------------------------------------------------------------------
    the numbers aren't in sorted order: 3, 6, 2
    ----------------------------------------------------------------------
    File "<memory>", line 8, in <memory>
    Failed example:
        1 + 1
    Expected:
        42
    Got:
        2


Priorities
----------

Some functionality requires that code be called early or late in a phase.  The
"timing" decorator allows either EARLY or LATE to be specified.

Early functions are run first (in arbitrary order), then functions with no
specified timing, then the late functions are called (again in arbitrary
order).  This function also demonstrates the "copy" method of Region objects
and the "insert_region_before" and "insert_region_after" methods of Documents.

    >>> @manuel.timing(manuel.LATE)
    ... def cloning_parser(document):
    ...     to_be_cloned = None
    ...     # find the region to clone
    ...     document_iter = iter(document)
    ...     for region in document_iter:
    ...         if region.parsed:
    ...             continue
    ...         if region.source.strip().endswith('my clone:'):
    ...             to_be_cloned = six.advance_iterator(document_iter).copy()
    ...             break
    ...     # if we found the region to cloned, do so
    ...     if to_be_cloned:
    ...         # make a copy since we'll be mutating the document
    ...         for region in list(document):
    ...             if region.parsed:
    ...                 continue
    ...             if 'clone before *here*' in region.source:
    ...                 clone = to_be_cloned.copy()
    ...                 clone.provenance = 'cloned to go before'
    ...                 document.insert_region_before(region, clone)
    ...             if 'clone after *here*' in region.source:
    ...                 clone = to_be_cloned.copy()
    ...                 clone.provenance = 'cloned to go after'
    ...                 document.insert_region_after(region, clone)

    >>> m.add_parser(cloning_parser)

    >>> source = """\
    ... This is my clone:
    ...
    ... clone: 1, 2, 3
    ...
    ... I want some copies of my clone.
    ...
    ... For example, I'd like a clone before *here*.
    ...
    ... I'd also like a clone after *here*.
    ... """
    >>> document = manuel.Document(source)
    >>> document.process_with(m, globs={})
    >>> [(r.source, r.provenance) for r in document]
    [('This is my clone:\n\n', None),
     ('clone: 1, 2, 3\n', None),
     ('clone: 1, 2, 3\n', 'cloned to go before'),
     ("\nI want some copies of my clone.\n\nFor example, I'd like a clone before *here*.\n\nI'd also like a clone after *here*.\n", None),
     ('clone: 1, 2, 3\n', 'cloned to go after')]


Enhancing Existing Manuels
--------------------------

Lets say that you'd like failed doctest examples to give more information about
what went wrong.

First we'll create an evaluater that includes pertinant variable binding
information on failures.

.. code-block:: python

    import doctest

    def informative_evaluater(region, document, globs):
        if not isinstance(region.parsed, doctest.Example):
            return
        if region.evaluated.getvalue():
            info = ''
            for name in sorted(globs):
                if name in region.parsed.source:
                    info += '\n    ' + name + ' = ' + repr(globs[name])

            if info:
                region.evaluated.write('Additional Information:')
                region.evaluated.write(info)

To do that we'll start with an instance of :mod:`manuel.doctest.Manuel` and add
in our additional functionality.

    >>> m = manuel.doctest.Manuel()
    >>> m.add_evaluater(informative_evaluater)

Now we'll create a document that includes a failing test.

    >>> document = manuel.Document("""
    ... Set up some variable bindings:
    ...
    ...     >>> a = 1
    ...     >>> b = 2
    ...     >>> c = 3
    ...
    ... Make an assertion:
    ...
    ...     >>> a + b
    ...     5
    ... """)

When we run the document through our Manuel instance, we see the additional
information.

    >>> document.process_with(m, globs={})
    >>> six.print_(document.formatted(), end='')
    File "<memory>", line 10, in <memory>
    Failed example:
        a + b
    Expected:
        5
    Got:
        3
    Additional Information:
        a = 1
        b = 2

Note how only the referenced variable bindings are displayed (i.e., "c" is not
listed).  That's pretty nice, but the way interesting variables are identified
is a bit of a hack.  For example, if a variable's name just happens to appear
in the source (in a comment for example), it will be included in the output:

    >>> document = manuel.Document("""
    ... Set up some variable bindings:
    ...
    ...     >>> a = 1
    ...     >>> b = 2
    ...     >>> c = 3
    ...
    ... Make an assertion:
    ...
    ...     >>> a + b # doesn't mention "c"
    ...     5
    ... """)

    >>> document.process_with(m, globs={})
    >>> six.print_(document.formatted(), end='')
    File "<memory>", line 10, in <memory>
    Failed example:
        a + b # doesn't mention "c"
    Expected:
        5
    Got:
        3
    Additional Information:
        a = 1
        b = 2
        c = 3

Instead of a text-based apprach, let's use the built-in tokenize module to more
robustly identify referenced variables.

    >>> from six import StringIO
    >>> import token
    >>> import tokenize

    >>> def informative_evaluater_2(region, document, globs):
    ...     if not isinstance(region.parsed, doctest.Example):
    ...         return
    ...
    ...     if region.evaluated.getvalue():
    ...         vars = set()
    ...         reader = StringIO(region.source).readline
    ...         for ttype, tval, _, _, _ in tokenize.generate_tokens(reader):
    ...             if ttype == token.NAME:
    ...                 vars.add(tval)
    ...
    ...         info = ''
    ...         for name in sorted(globs):
    ...             if name in vars:
    ...                 info += '\n    ' + name + ' = ' + repr(globs[name])
    ...
    ...         if info:
    ...             region.evaluated.write('Additional Information:')
    ...             region.evaluated.write(info)

    >>> m = manuel.doctest.Manuel()
    >>> m.add_evaluater(informative_evaluater_2)

Now when we have a failure, only the genuinely referenced variables will be
included in the debugging information.

    >>> document = manuel.Document(document.source)
    >>> document.process_with(m, globs={})
    >>> six.print_(document.formatted(), end='')
    File "<memory>", line 10, in <memory>
    Failed example:
        a + b # doesn't mention "c"
    Expected:
        5
    Got:
        3
    Additional Information:
        a = 1
        b = 2


Defining Test Cases
-------------------

If you want parts of a document to be accessable individually as test cases (to
be able to run just a particular part of a document, for example), a parser can
create a region that marks the beginning of a new test case.

.. code-block:: python

    new_test_case_regex = re.compile(r'^.. new-test-case: \w+', re.MULTILINE)

    def parse(document):
        for region in document.find_regions(new_test_case_regex):
            document.claim_region(region)
            id = region.start_match.group(1)
            region.parsed = manuel.testing.TestCaseMarker(id)

XXX finish this section
