import re
import textwrap

import manuel

CODEBLOCK_START_RST = re.compile(
    r"(^\.\.\s*(invisible-)?code(-block)?::?\s*python\b(?:\s*\:[\w-]+\:.*\n)*)",
    re.MULTILINE,
)
CODEBLOCK_END_RST = re.compile(r"(\n\Z|\n(?=\S))")

CODEBLOCK_START_MYST = re.compile(
    r"((^```python)|(^% invisible-code-block:\s+python)$)",
    re.MULTILINE,
)
CODEBLOCK_END_MYST = re.compile(r"(\n(?=```\n))|((?:% [\S ]*)\n(?=\n))")


class CodeBlock(object):
    def __init__(self, code, source):
        self.code = code
        self.source = source


def find_code_blocks(document):
    CODEBLOCK_START = (
        document.location.endswith(".md")
        and CODEBLOCK_START_MYST
        or CODEBLOCK_START_RST
    )
    CODEBLOCK_END = (
        document.location.endswith(".md") and CODEBLOCK_END_MYST or CODEBLOCK_END_RST
    )
    for region in document.find_regions(CODEBLOCK_START, CODEBLOCK_END):
        start_end = CODEBLOCK_START.search(region.source).end()
        source = textwrap.dedent(region.source[start_end:])
        # MyST comments
        source = re.sub(r'\n%[ ]?', '\n', source)
        source_location = "%s:%d" % (document.location, region.lineno)
        code = compile(source, source_location, "exec", 0, True)
        document.claim_region(region)
        region.parsed = CodeBlock(code, source)


def execute_code_block(region, document, globs):
    if not isinstance(region.parsed, CodeBlock):
        return

    exec(region.parsed.code, globs)
    del globs["__builtins__"]  # exec adds __builtins__, we don't want it


class Manuel(manuel.Manuel):
    def __init__(self):
        manuel.Manuel.__init__(self, [find_code_blocks], [execute_code_block])
