.. image:: https://raw.githubusercontent.com/benji-york/manuel/master/badges/coverage-badge.svg
    :target: https://pypi.python.org/pypi/manuel

.. image:: https://img.shields.io/pypi/pyversions/manuel.svg
    :target: https://pypi.python.org/pypi/manuel/

======
Manuel
======

Manuel lets you write strong documentattion and tests in a style that makes your your
library, API, or project understandable to the reader in a way that is difficult to
accomplish with low-context unit tests.

Here's an example of how Manuel works: lets say that you are creating a new Python
library and want to develop it in a
`ducoumentation-driven<https://pyvideo.org/pycon-us-2011/pycon-2011--documentation-driven-development.html>`_
fashion, so you create an introduction for your README

::

    Addly is a library that provides all your adding needs.  Using Addly is as easy as
    importing the library and calling the add() function::

        >>> addly.add(2, 2)
        5

.. -> addly_readme

You may have noticed an error in the documentation above, but some errors are not as
easy to spot.  What if you had a way to ensure that the documentation you wrote is
correct?  That's where Manuel comes in.  If you were using Manuel to validate your docs,
it would inform you of the problem, like so::

    File "<memory>", line 4, in <memory>
    Failed example:
        addly.add(2, 2)
    Expected:
        5
    Got:
        4

.. -> addly_error

.. code-block:: python

    import manuel.doctest
    import manuel

    class AddlyModule:

        @staticmethod
        def add(a: int, b: int) -> int:
            return a + b

    m = manuel.doctest.Manuel()
    document = manuel.Document(addly_readme)
    document.process_with(m, globs={'addly': AddlyModule()})
    error = document.formatted()

..

    >>> if addly_error != error:
    ...     print(''.join(difflib.unified_diff(addly_error.splitlines(keepends=True), error.splitlines(keepends=True))), end='')
