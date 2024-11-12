CHANGES
=======

1.13.0 (2024-11-12)
-------------------

- Include*.md files in wheel
  These are needed by the test suite, which is also included in the wheel.
- Fix tests on python3.11
- Update some web links
- Update pyinstaller to 6.1.0 for python >= 3.11 support
- doctest: use outputchecker argument also in debug mode.
  Fixes #38
- Remove references to old "six" module


1.12.4 (2022-06-24)
-------------------

- Remove silly PyPI version badge.


1.12.3 (2022-06-24)
-------------------

- Modernize internal project structure; drop tox; no user-visible changes (hopefully).
- Rework coverage badge generation.
- Drop Travis CI badge (the project is using GitHub for CI now)


1.11.2 (2022-05-15)
-------------------

Fix missing file in release.


1.11.1 (2022-05-14)
-------------------

Fix brown-bag release.


1.11.0 (2022-05-14)
-------------------

- Fix test detection in Python 2 which was broken since 1.10.0.
  (`#20 <https://github.com/benji-york/manuel/issues/20>`_)
- Add Python 3.9 and 3.10 to tox config.
- Add a Makefile to centeralized development activities.


1.10.1 (2018-11-15)
-------------------

- Add support for PyPy3.


1.10.0 (2018-11-14)
-------------------

- Fix DeprecationWarning about 'U' mode under Python 3.
- Drop Python 2.6 and 3.3 support. Add testing and support for Python 3.6 and
  3.7.


1.9.0 (2017-11-20)
------------------

- You can now use Manuel with the `nose
  <http://nose.readthedocs.io/en/latest/>`_ and `pytest
  <https://docs.pytest.org/en/latest/>`_ test runners by defining
  Manuel tests inside `unittest.TestCase` classes.
- Added support for Python 3.5 and Python 3.6.
- Dropped support for Python 2.6


1.8.0 (2014-07-15)
------------------

- Fixed ResourceWarnings under Python 3.
- Added support for PyPy and Python 3.4.
- Drop official support for Python 3.1 and 3.2.
- Fix odd ImportError problems when used with tox and coverage.
- Fix parsing of reST codeblock options with hyphens.


1.7.2 (2013-03-16)
------------------

- Fixed release issues.
- Updated copyright and license to reflect recent Zope Foundation release of
  claim on the project.


1.7.1 (2013-02-13)
------------------

- Fix brown-bag release.


1.7.0 (2013-02-13)
------------------

- Added support for docutils-style code blocks and options there-of.


1.6.1 (2013-01-24)
------------------

- Fixed a bug that made doctests fail if sys.argv contained the string "-v".


1.6.0 (2012-04-16)
------------------

- Ported to Python 3, still works in 2.6 and up.


1.5.0 (2011-03-08)
------------------

- Removed the dependency on zope.testrunner
- Added the ability to run the tests using "setup.py test".


1.4.1 (2011-01-25)
------------------

- Fixed a bug that caused extra example evaluation if multiple doctest
  manuels were used at once (e.g. to execute Python and shell code in
  the same document).


1.4.0 (2011-01-11)
------------------

- Added a ``parser`` keyword argument to manuel.doctest.Manuel to
  allow a custom doctest parser to be passed in.  This allows easily
  adding support for other languages or other (but similar) example
  syntaxes.


1.3.0 (2010-09-02)
------------------

- Respect test runner reporting switches (e.g., zope.testrunner's --ndiff
  switch)
- Fixed a bug that caused post-mortem debugging to not work most of the
  time.
- Made manuel.testing.TestCase.id return a sensible textual value
  at all times.  This keeps Twisted's trial testrunner happy.


1.2.0 (2010-06-10)
------------------

- Conform to repository policy.
- Switch to using zope.testrunner instead of zope.testing due to API changes.
  zope.testing is now only required for testing.


1.1.1 (2010-05-20)
------------------

- fix the way globs are handled; fixes
  https://bugs.launchpad.net/manuel/+bug/582482


1.1.0 (2010-05-18)
------------------

- fix a SyntaxError when running the tests under Python 2.5
- improved error message for improperly indented capture directive
- Manuel no longer uses the now depricated zope.testing.doctest (requires
  zope.testing 3.9.1 or newer)


1.0.5 (2010-01-29)
------------------

- fix a bug that caused Manuel to choke on empty documents (patch submitted by
  Bjorn Tillenius)
- add a pointer to Manuel's Subversion repo on the PyPI page
- add an optional parameter that allows a custom TestCase class to be passed to
  TestSuite() (patch submitted by Bjorn Tillenius)


1.0.4 (2010-01-06)
------------------

- use newer setuptools (one compatible with Subversion 1.6) so built
  distributions include all files


1.0.3 (2010-01-06)
------------------

- fix a small doc thinko
- fix the code-block handler to allow :linenos:
- open files in universal newlines mode


1.0.2 (2009-12-07)
------------------

- fix a bug that caused instances of zope.testing.doctest.Example (and
  instances of subclasses of the same) to be silently ignored.


1.0.1 (2009-08-31)
------------------

- fix line number reporting for test failures


1.0.0 (2009-08-09)
------------------

- Python 2.4 compatability fix


1.0.0b2 (2009-07-10)
--------------------

- add the ability to identify and run subsets of documents (using the -t switch
  of zope.testing's testrunner for example)


1.0.0b1 (2009-06-24)
--------------------

- major docs improvements
- added several new plug-ins


1.0.0a8 (2009-05-01)
--------------------

- add a larger example of using Manuel (table-example.txt)
- make the test suite factory function try harder to find the calling
  module
- fix a bug in the order regions are evaluated
- add a Manuel object that can evaluate Python code in
  ".. code-block:: python" regions of a reST document

1.0.0a4 (2009-05-01)
--------------------

- make the global state ("globs") shared between all evaluators, not just
  doctest


1.0.0a3 (2009-05-01)
--------------------

- make zope.testing's testrunner recognized the enhanced, doctest-style
  errors generated by Manuel
- rework the evaluaters to work region-by-region instead of on the
  entire document
- switch to using regular Python classes for Manuel objects instead of
  previous prototype-y style


1.0.0a2 (2008-10-17)
--------------------

- first release
