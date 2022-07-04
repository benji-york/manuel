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

Even simple documentation like the above makes your communication much more powerful.
Conversely, having errors in your documentation impedes your user's progress and
reflects poorly on your project.


.. code-block: python

    from tests.helpers import checker
    import manuel
    import manuel.doctest
    m = manuel.doctest.Manuel(checker=checker)

You may have noticed the error in the example above.  What if you had a way to ensure
that the documentation you write is correct?  That's where Manuel comes in.  If you were
using Manuel to validate your docs, it would inform you of the problem.

.. >>> print(m(readme), end='')
::
    File "README.txt", line 2, in README.txt
    Failed example:
        addly.add(2, 2)
    Expected:
        5
    Got:
        4


A worked example
================

Let's rewind and walk though the process of writing the README.  First, we want to start
with some introductory prose describing the problem we are solving.

::

    Many problems lend themselves to addition, but addition is hard, so we built Addly.

OK, that's a good start.  Next we need to describe the use of our library.  The first
thing a user needs is to know how to import it.

::

    Many problems lend themselves to addition, but addition is hard, so we built Addly.

    Using Addly is as easy as importing the library and calling the add() function::

        >>> import addly

.. -> readme

Since we want to work in a tight feedback loop, we'll run the above document through
Manuel, which will guide us toward what to do next.

Since we are writing our documentation first, we don't even have an importable module,
so we get an error.

::

    File "<memory>", line 5, in <memory>
    Failed example:
        import addly
    Exception raised:
        Traceback (most recent call last):
          File "/usr/local/Cellar/python@3.9/3.9.12_1/Frameworks/Python.framework/Versions/3.9/lib/python3.9/doctest.py", line 1334, in __run
            exec(compile(example.source, filename, "single",
          File "<doctest <memory>[0]>", line 1, in <module>
            import addly
        ModuleNotFoundError: No module named 'addly'

.. -> example

.. code-block: python

    del sys.modules['addly']  # we're starting over, so remove the module
    document = manuel.Document(readme)
    document.process_with(m, globs={})
    result = document.formatted()
    from tests.helpers import print_diff

..
    >>> print_diff(result, example)

Consequently, we then create the module, and re-run Manuel and no errors are reported.

.. code-block: python

    class EmptyModule:
        pass

    sys.modules['addly'] = EmptyModule()
    document = manuel.Document(readme)
    document.process_with(m, globs={})
    result = document.formatted()
    assert result == ''

Next, we add the first real example to our README.

::

    Many problems lend themselves to addition, but addition is hard, so we built Addley.

    Using Addly is as easy as importing the library and calling the add() function::

        >>> import addly
        >>> addly.add(2, 2)

.. -> readme

Since we haven't written the ``add`` function yet, running Manuel generates an error.

::

    File "<memory>", line 6, in <memory>
    Failed example:
        addly.add(2, 2)
    Exception raised:
        Traceback (most recent call last):
          File "/usr/local/Cellar/python@3.9/3.9.12_1/Frameworks/Python.framework/Versions/3.9/lib/python3.9/doctest.py", line 1334, in __run
            exec(compile(example.source, filename, "single",
          File "<doctest <memory>[0]>", line 1, in <module>
            addly.add(2, 2)
        AttributeError: 'EmptyModule' object has no attribute 'add'

.. -> example

.. XXX make above read better, especially "EmptyModule" bit and "<memory>"

.. code-block: python

    document = manuel.Document(readme)
    document.process_with(m, globs={})
    result = document.formatted()

..
    >>> print_diff(result, example)

In the README we mentioned the ``add`` function, but since it doesn't exist, Manuel
reported the above error.  In response, we go implement that function.

When we re-run Manuel, now we get an error because no output was expected, but output
was generated.

::

    File "<memory>", line 6, in <memory>
    Failed example:
        addly.add(2, 2)
    Expected nothing
    Got:
        4

.. -> example

.. code-block: python

    sys.modules['addly'] = AddlyModule()
    document = manuel.Document(readme)
    document.process_with(m, globs={})
    result = document.formatted()
..
    >>> print_diff(result, example)


That's easy enough to fix, we'll update the README to match what the function produces.

::

    Many problems lend themselves to addition, but addition is hard, so we built Addley.

    Using Addly is as easy as importing the library and calling the add() function::

        >>> import addly
        >>> addly.add(2, 2)
        4

.. -> readme

Now when we run Manuel, no errors are generated.

.. code-block: python

    document = manuel.Document(readme)
    document.process_with(m, globs={})
    result = document.formatted()
    assert result == ''


Summary
=======

To use Manuel in a documentation-driven development cycle you:

1. write a little more documentation that includes an example
2. run Manuel and see how that new example fails
3. add code to your system that makes the new example pass (and doesn't break existing
   examples)
4. repeat the loop
