.. image:: https://raw.githubusercontent.com/benji-york/manuel/master/badges/coverage-badge.svg
    :target: https://pypi.python.org/pypi/manuel

.. image:: https://img.shields.io/pypi/pyversions/manuel.svg
    :target: https://pypi.python.org/pypi/manuel/

======
Manuel
======

Manuel helps you write strong documentation that makes your your library, API, or
project understandable to the reader in a way that is hard to accomplish otherwise.

Here's an example of how Manuel works: lets say that you are creating a new Python
library and want to develop it in a
`documentation-driven <https://pyvideo.org/pycon-us-2011/pycon-2011--documentation-driven-development.html>`_
fashion, so you create an introduction to the module as a README.


.. code-block: python

    # Behind-the-scenese code to build a fake module so the below example works.
    import sys

    class AddlyModule:

        @staticmethod
        def add(a: int, b: int) -> int:
            return a + b

    sys.modules['addly'] = AddlyModule()

::

    Addly is a library that provides all your adding needs.  Using Addly is as easy as
    importing the library and calling the add() function::

        >>> import addly
        >>> addly.add(2, 2)
        5

.. -> addly_readme

Even simple documentation like the above makes your communication much more powerful.
Conversely, having errors in your documentation impedes your user's progress and
reflects poorly on your project.

You may have noticed the error in the example above.  What if you had a way to ensure
that the documentation you write is correct?  That's where Manuel comes in.  If you were
using Manuel to validate your docs, it would inform you of the problem, like so::

    File "<memory>", line 5, in <memory>
    Failed example:
        addly.add(2, 2)
    Expected:
        5
    Got:
        4

.. -> addly_error

.. XXX make above 'File "<memory>"' bit nicer.

.. code-block: python

    # Run the above README (addly_readme) through Maneul and capture the error.
    from tests.helpers import checker
    import manuel
    import manuel.doctest
    m = manuel.doctest.Manuel(checker=checker)
    document = manuel.Document(addly_readme)
    document.process_with(m, globs={})
    error = document.formatted()

..
    Verify that the error is actually generated.
    >>> from tests.helpers import print_diff
    >>> print_diff(addly_error, error)
