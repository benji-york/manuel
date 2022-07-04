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

    Many problems lend themselves to addition, but addition is hard, so we built Addly.

    Using Addly is as easy as importing the library and calling the add() function::

        >>> import addly
        >>> addly.add(2, 2)
        5

.. -> readme

.. code-block: python

    # Before we go any further, we need to get some Manuel machinery ready to process
    # all of the embedded documents (like the above README).

    from tests.helpers import checker
    import manuel
    import manuel.doctest
    def run_manuel(source):
        m = manuel.doctest.Manuel(checker=checker)
        document = manuel.Document(readme)
        document.process_with(m, globs={})
        result = document.formatted()
        return result

Even simple documentation like the above makes your communication much more powerful.
Conversely, having errors in your documentation impedes your user's progress and
reflects poorly on your project.

You may have noticed the error in the example above.  What if you had a way to ensure
that errors in documentation like that don't slip through?  That's where Manuel comes
in.  If you were using Manuel to validate your docs, it would inform you of the problem,
like so:

.. >>> print(result := run_manuel(readme), end='')
::
    File "README.txt", line 2, in README.txt
    Failed example:
        addly.add(2, 2)
    Expected:
        5
    Got:
        42
