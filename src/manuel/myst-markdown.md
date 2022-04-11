# MyST markdown

`manuel` is originally written for restructuredText.
Starting with the codeblock module, `manuel` will successivly be extendend also for MyST, a markdown flavor.
For more information about MyST see [myst-parser.readthedocs.io](https://myst-parser.readthedocs.io/en/latest/).

## Code Blocks

Sphinx and other docutils extensions provide a “code-block” directive, which allows inlined snippets of code in MyST documents.

Several plug-ins are included that provide new test syntax (see
{ref}`functionality`).
You can also create your own plug-ins.

For example, if you've ever wanted to include a large chunk of Python in a
doctest but were irritated by all the ">>>" and "..." prompts required, you'd
like the {mod}`manuel.codeblock` module.
It lets you execute code using MyST-style "``` python" directives.
The markup looks like this:

    ```python
    import foo

    def my_func(bar):
        return foo.baz(bar)
    ```


To see how to get `manuel` wired up see {ref}`getting-started`.


The scope of variables spans across the complete document.

```python
a = 3

# another variable
b = 2 * 3
```

The variables a and b can be used in the following code block.

```python
assert b == 6
```

You can even write code in invisible code blocks. Invisible code blocks do not show up in the rendered documentation. In fact they are comments as their lines start with "%".

    % invisible-code-block: python
    %
    % assert a + b == 9
    %
    % assert 7 * a == 21


% invisible-code-block: python
%
% assert a + b == 9
%
% assert 7 * a == 21

Happy hacking!
