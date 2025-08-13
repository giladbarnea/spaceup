"""
Read SPEC.md to understand the purpose of each test.

Note that when comparing HTML, whitespace does NOT matter.
Hence it is normalized before comparison.
"""

import textwrap

from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString, Comment

from ast_parser import (
    parse_spaceup_ast,
    Document,
    Heading,
    Paragraph,
    Div,
    MarkdownInline,
)


def _normalize_node(node):
    if isinstance(node, Comment):
        text = str(node)
        if text.strip() == "":
            return None
        return ("#comment", " ".join(text.split()))
    if isinstance(node, NavigableString):
        text = str(node)
        if text.strip() == "":
            return None
        return ("#text", " ".join(text.split()))
    if isinstance(node, Tag):
        normalized_children = []
        for child in node.children:
            norm = _normalize_node(child)
            if norm is not None:
                normalized_children.append(norm)
        # Attributes are irrelevant for these tests; include if needed later
        return (node.name, tuple(normalized_children))
    return None


# NOTE: this not sure how this function fits if our ast parser outputs an ast out of the box
def _soup_ast(soup):
    ast_children = []
    for child in soup.contents:
        norm = _normalize_node(child)
        if norm is not None:
            ast_children.append(norm)
    return tuple(ast_children)

def _assert_ast_equal(ast1, ast2):
    return ast1 == ast2

def test_ast_parser_with_basic_example():
    basic_input = textwrap.dedent("""
        text with 0 indentation
            text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know.
            another line with more text with 1 indentation.
    """)
    parsed_spaceup_ast = parse_spaceup_ast(basic_input)
    expected_ast = Document(
        children=[
            Heading(level=1, content=MarkdownInline(text="text with 0 indentation", tokens=[])),
            Paragraph(
                divs=[
                    Div(
                        content=MarkdownInline(
                            text=(
                                "text with 1 indentation. 1 is greater than the preceding 0, "
                                "but we need to parse the next element before we know."
                            ),
                            tokens=[],
                        ),
                        inline_comment=None,
                    ),
                    Div(
                        content=MarkdownInline(
                            text="another line with more text with 1 indentation.", tokens=[]
                        ),
                        inline_comment=None,
                    ),
                ]
            ),
        ]
    )
    assert _assert_ast_equal(parsed_spaceup_ast, expected_ast)
    # expected_html = textwrap.dedent("""
    #     <h1>text with 0 indentation</h1>
    #     <p>
    #         <div>text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know.</div>
    #         <div>another line with more text with 1 indentation.</div>
    #     </p>
    # """)
    # expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    # spaceup_html = render_ast_to_html(parsed_spaceup_ast)
    # actual_structured_html = BeautifulSoup(spaceup_html, "html.parser")
    # assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_ast_parser_with_end_of_document_paragraph():
    end_of_document_paragraph_input = textwrap.dedent("""
        text with 0 indentation
            text with 1 indentation. 1 is greater than the preceding 0, and that's the last element in the document (next is EOF) --> this text is a paragraph opener, and the preceding element is an h1.
    """)
    parsed_spaceup_ast = parse_spaceup_ast(end_of_document_paragraph_input)
    expected_ast = ...
    assert _assert_ast_equal(parsed_spaceup_ast, expected_ast)
    # expected_html = textwrap.dedent("""
    #     <h1>text with 0 indentation</h1>
    #     <p>
    #         <div>text with 1 indentation. 1 is greater than the preceding 0, and that's the last element in the document (next is EOF) --> this text is a paragraph opener, and the preceding element is an h1.</div>
    #     </p>
    # """)
    # expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    # spaceup_html = render_ast_to_html(parsed_spaceup_ast)
    # actual_structured_html = BeautifulSoup(spaceup_html, "html.parser")
    # assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_ast_parser_with_two_indentation_levels():
    full_input = textwrap.dedent("""
        text with 0 indentation

            text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know.
            another line with more text with 1 indentation.

            even some more text with 1 indentation, preceded by a blank line, and next non-whitespace, non-comment element has indentation LOWER OR EQUAL to this one  --> this is a paragraph open.

            here is a new line with 1 indentation, preceded by a blank line, BUT, next non-WS non comment element has a greater indentation level. Therefore, this is a H2. 

                Some paragraph opener under the H2 heading from before, with an indentation level of 2.
                Lorem ipsum a new div in the same paragraph because no blank line before it and indent level is also 2.

                Foo text after a blank line with same indentation (2) as the preceding text; it is another paragraph opener under the H2 from before.
    """)
    parsed_spaceup_ast = parse_spaceup_ast(full_input)
    expected_ast = ...
    assert _assert_ast_equal(parsed_spaceup_ast, expected_ast)
    # expected_html = textwrap.dedent("""
    #     <h1>text with 0 indentation</h1>
    #     <p>
    #         <div>text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know.</div>
    #         <div>another line with more text with 1 indentation.</div>
    #     </p>
    #     <p>
    #         <div>even some more text with 1 indentation, preceded by a blank line, and next non-whitespace, non-comment element has indentation LOWER OR EQUAL to this one  --> this is a paragraph open.</div>
    #     </p>
    #     <h2>here is a new line with 1 indentation, preceded by a blank line, BUT, next non-WS non comment element has a greater indentation level. Therefore, this is a H2.</h2>
    #     <p>
    #         <div>Some paragraph opener under the H2 heading from before, with an indentation level of 2.</div>
    #         <div>Lorem ipsum a new div in the same paragraph because no blank line before it and indent level is also 2.</div>
    #     </p>
    #     <p>
    #         <div>Foo text after a blank line with same indentation (2) as the preceding text; it is another paragraph opener under the H2 from before.</div>
    #     </p>
    # """)
    # expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    # spaceup_html = render_ast_to_html(parsed_spaceup_ast)
    # actual_structured_html = BeautifulSoup(spaceup_html, "html.parser")
    # assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_ast_parser_with_unambiguous_decreasing_indentation_level():
    full_input = textwrap.dedent("""
        text with 0 indentation

            text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know.
            another line with more text with 1 indentation.

            even some more text with 1 indentation, preceded by a blank line, and next non-whitespace, non-comment element has indentation LOWER OR EQUAL to this one  --> this is a paragraph open.

            here is a new line with 1 indentation, preceded by a blank line, BUT, next non-WS non comment element has a greater indentation level. Therefore, this is a H2. 

                Some paragraph opener under the H2 heading from before, with an indentation level of 2.
                Lorem ipsum a new div in the same paragraph because no blank line before it and indent level is also 2.

                Foo text after a blank line with same indentation (2) as the preceding text; it is another paragraph opener under the H2 from before.

            Back to indentation level 1. Note that the next line has a greater indentation than the current one. This necessarily makes this line a heading.
                This line has indentation level 2. Because 1 is LOWER THAN 2, the previous line is a heading (h2), and since this is the end of the document, this is a paragraph start with a single div.
    """)
    parsed_spaceup_ast = parse_spaceup_ast(full_input)
    expected_ast = ...
    assert _assert_ast_equal(parsed_spaceup_ast, expected_ast)
    # expected_html = textwrap.dedent("""
    #     <h1>text with 0 indentation</h1>
    #     <p>
    #         <div>text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know.</div>
    #         <div>another line with more text with 1 indentation.</div>
    #     </p>
    #     <p>
    #         <div>even some more text with 1 indentation, preceded by a blank line, and next non-whitespace, non-comment element has indentation LOWER OR EQUAL to this one  --> this is a paragraph open.</div>
    #     </p>
    #     <h2>here is a new line with 1 indentation, preceded by a blank line, BUT, next non-WS non comment element has a greater indentation level. Therefore, this is a H2.</h2>
    #     <p>
    #         <div>Some paragraph opener under the H2 heading from before, with an indentation level of 2.</div>
    #         <div>Lorem ipsum a new div in the same paragraph because no blank line before it and indent level is also 2.</div>
    #     </p>
    #     <p>
    #         <div>Foo text after a blank line with same indentation (2) as the preceding text; it is another paragraph opener under the H2 from before.</div>
    #     </p>
    #     <h2>Back to indentation level 1. Note that the next line has a greater indentation than the current one. This necessarily makes this line a heading.</h2>
    #     <p>
    #         <div>This line has indentation level 2. Because 1 is LOWER THAN 2, the previous line is a heading (h2), and since this is the end of the document, this is a paragraph start with a single div.</div>
    #     </p>
    # """)
    # expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    # spaceup_html = render_ast_to_html(parsed_spaceup_ast)
    # actual_structured_html = BeautifulSoup(spaceup_html, "html.parser")
    # assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_ast_parser_with_ambiguous_decreasing_indentation_level():
    """Tests resolving the ambiguity created by the first line of a block with a decreasing indentation level by forcing it to be treated as a heading."""

    full_input = textwrap.dedent("""
        text with 0 indentation

            text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know.
            another line with more text with 1 indentation.

            even some more text with 1 indentation, preceded by a blank line, and next non-whitespace, non-comment element has indentation LOWER OR EQUAL to this one  --> this is a paragraph open.

            here is a new line with 1 indentation, preceded by a blank line, BUT, next non-WS non comment element has a greater indentation level. Therefore, this is a H2. 

                Some paragraph opener under the H2 heading from before, with an indentation level of 2.
                Lorem ipsum a new div in the same paragraph because no blank line before it and indent level is also 2.

                Foo text after a blank line with same indentation (2) as the preceding text; it is another paragraph opener under the H2 from before.

            Back to indentation level 1. Note that the next line has a greater indentation than the current one. This necessarily makes this line a heading.
                This line has indentation level 2. Because 1 is LOWER THAN 2, the previous line is a heading (h2), and since the next element has a LOWER indentation level, this is a paragraph start with a single div.

            Back to indentation level 1. Next line has the same indentation.
            Here is another line, right afterwards, with the SAME indentation level (1). This is a special case; read the comment below.
    """)
    parsed_spaceup_ast = parse_spaceup_ast(full_input)
    expected_ast = ...
    assert _assert_ast_equal(parsed_spaceup_ast, expected_ast)
    # expected_html = textwrap.dedent("""
    #     <h1>text with 0 indentation</h1>
    #     <p>
    #         <div>text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know.</div>
    #         <div>another line with more text with 1 indentation.</div>
    #     </p>
    #     <p>
    #         <div>even some more text with 1 indentation, preceded by a blank line, and next non-whitespace, non-comment element has indentation LOWER OR EQUAL to this one  --> this is a paragraph open.</div>
    #     </p>
    #     <h2>here is a new line with 1 indentation, preceded by a blank line, BUT, next non-WS non comment element has a greater indentation level. Therefore, this is a H2.</h2>
    #     <p>
    #         <div>Some paragraph opener under the H2 heading from before, with an indentation level of 2.</div>
    #         <div>Lorem ipsum a new div in the same paragraph because no blank line before it and indent level is also 2.</div>
    #     </p>
    #     <p>
    #         <div>Foo text after a blank line with same indentation (2) as the preceding text; it is another paragraph opener under the H2 from before.</div>
    #     </p>
    #     <h2>Back to indentation level 1. Note that the next line has a greater indentation than the current one. This necessarily makes this line a heading.</h2>
    #     <p>
    #         <div>This line has indentation level 2. Because 1 is LOWER THAN 2, the previous line is a heading (h2), and since the next element has a LOWER indentation level, this is a paragraph start with a single div.</div>
    #     </p>
    #     <h2>Back to indentation level 1. Next line has the same indentation.</h2>
    #     <p>
    #         <div>Here is another line, right afterwards, with the SAME indentation level (1). This is a special case; read the comment below.</div>
    #     </p>
    # """)
    # expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    # spaceup_html = render_ast_to_html(parsed_spaceup_ast)
    # actual_structured_html = BeautifulSoup(spaceup_html, "html.parser")
    # assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_ast_parser_with_comments_sanity():
    full_input = textwrap.dedent("""
        text with 0 indentation
            text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know. // hint: the following non-WS, non-comment element's indentation level is LOWER OR EQUAL to this one; therefore, this line is a paragraph open.
            another line with more text with 1 indentation.
    """)
    parsed_spaceup_ast = parse_spaceup_ast(full_input)
    expected_ast = ...
    assert _assert_ast_equal(parsed_spaceup_ast, expected_ast)
    # expected_html = textwrap.dedent("""
    #     <h1>text with 0 indentation</h1>
    #     <p>
    #         <div>text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know.  <!-- hint: the following non-WS, non-comment element's indentation level is LOWER OR EQUAL to this one; therefore, this line is a paragraph open. --></div>
    #         <div>another line with more text with 1 indentation.</div>
    #     </p>
    # """)
    # expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    # spaceup_html = render_ast_to_html(parsed_spaceup_ast)
    # actual_structured_html = BeautifulSoup(spaceup_html, "html.parser")
    # assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_ast_parser_with_full_example():
    full_input = textwrap.dedent("""
        text with 0 indentation

            text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know. // hint: the following non-WS, non-comment element's indentation level is LOWER OR EQUAL to this one; therefore, this line is a paragraph open.
            another line with more text with 1 indentation.

            even some more text with 1 indentation, preceded by a blank line, and next non-whitespace, non-comment element has indentation LOWER OR EQUAL to this one  --> this is a paragraph open.

            here is a new line with 1 indentation, preceded by a blank line, BUT, next non-WS non comment element has a greater indentation level. Therefore, this is a H2. 

                Some paragraph opener under the H2 heading from before, with an indentation level of 2.
                Lorem ipsum a new div in the same paragraph because no blank line before it and indent level is also 2.

                Foo text after a blank line with same indentation (2) as the preceding text; it is another paragraph opener under the H2 from before.

            Back to indentation level 1. Note that the next line has a greater indentation than the current one. This necessarily makes this line a heading.
                This line has indentation level 2. Because 1 is LOWER THAN 2, the previous line is a heading (h2), and since the next element has a LOWER indentation level, this is a paragraph start with a single div.

            Back to indentation level 1. Next line has the same indentation.
            Here is another line, right afterwards, with the SAME indentation level (1). This is a special case; read the comment below.
            // This text block is the first example where the two following conditions occur:
            // 1. indentation went DOWN (previous non-ws non-comment element was 2; now it's 1), and
            // 2. Two consecutive elements have the same indentation level (1), and going by rules, the first line of this block — 'Back to indentation level 1' — shouldn't be a heading. But we have to make an exception here.
            // In such an ambiguous, decreased-indentation case, where it's unclear how to parse the first line because the line which follows it shares the same indentation level, the first line is FORCED to become a heading. Subsequent lines in this block are forced to be indented. In effect, this makes this block with exactly the same structure as the one before it; an h2 line, followed by a paragraph starter.
    """)
    parsed_spaceup_ast = parse_spaceup_ast(full_input)
    expected_ast = ...
    assert _assert_ast_equal(parsed_spaceup_ast, expected_ast)
    # expected_html = textwrap.dedent("""
    #     <h1>text with 0 indentation</h1>
    #     <p>
    #         <div>text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know.  <!-- hint: the following non-WS, non-comment element's indentation level is LOWER OR EQUAL to this one; therefore, this line is a paragraph open. --></div>
    #         <div>another line with more text with 1 indentation.</div>
    #     </p>
    #     <p>
    #         <div>even some more text with 1 indentation, preceded by a blank line, and next non-whitespace, non-comment element has indentation LOWER OR EQUAL to this one  --> this is a paragraph open.</div>
    #     </p>
    #     <h2>here is a new line with 1 indentation, preceded by a blank line, BUT, next non-WS non comment element has a greater indentation level. Therefore, this is a H2.</h2>
    #     <p>
    #         <div>Some paragraph opener under the H2 heading from before, with an indentation level of 2.</div>
    #         <div>Lorem ipsum a new div in the same paragraph because no blank line before it and indent level is also 2.</div>
    #     </p>
    #     <p>
    #         <div>Foo text after a blank line with same indentation (2) as the preceding text; it is another paragraph opener under the H2 from before.</div>
    #     </p>
    #     <h2>Back to indentation level 1. Note that the next line has a greater indentation than the current one. This necessarily makes this line a heading.</h2>
    #     <p>
    #         <div>This line has indentation level 2. Because 1 is LOWER THAN 2, the previous line is a heading (h2), and since the next element has a LOWER indentation level, this is a paragraph start with a single div.</div>
    #     </p>
    #     <h2>Back to indentation level 1. Next line has the same indentation.</h2>
    #     <p>
    #         <div>Here is another line, right afterwards, with the SAME indentation level (1). This is a special case; read the comment below.</div>
    #     </p>
    #     <!-- This text block is the first example where the two following conditions occur: -->
    #     <!-- 1. indentation went DOWN (previous non-ws non-comment element was 2; now it's 1), and -->
    #     <!-- 2. Two consecutive elements have the same indentation level (1), and going by rules, the first line of this block — 'Back to indentation level 1' — shouldn't be a heading. But we have to make an exception here. -->
    #     <!-- In such an ambiguous, decreased-indentation case, where it's unclear how to parse the first line because the line which follows it shares the same indentation level, the first line is FORCED to become a heading. Subsequent lines in this block are forced to be indented. In effect, this makes this block with exactly the same structure as the one before it; an h2 line, followed by a paragraph starter. -->
    # """)
    # expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    # spaceup_html = render_ast_to_html(parsed_spaceup_ast)
    # actual_structured_html = BeautifulSoup(spaceup_html, "html.parser")
    # assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_ast_parser_with_markdown_features():
    full_input = textwrap.dedent("""
        My Favorite Recipe

            Ingredients

                - 2 cups flour
                - 1 cup sugar
                - **1 tsp** baking powder

                Mix them well.

            Instructions

                Preheat oven to 350°F.
                Bake for 20 minutes.

                Enjoy your [cake](https://example.com/recipe)!
    """)
    parsed_spaceup_ast = parse_spaceup_ast(full_input)
    expected_ast = ...
    assert _assert_ast_equal(parsed_spaceup_ast, expected_ast)
    # spaceup_html = render_ast_to_html(parsed_spaceup_ast)
    # actual_structured_html = BeautifulSoup(spaceup_html, "html.parser")
    # expected_html = textwrap.dedent("""
    #     <h1>My Favorite Recipe</h1>
    #     <h2>Ingredients</h2>
    #     <ul>
    #         <li>2 cups flour</li>
    #         <li>1 cup sugar</li>
    #         <li><strong>1 tsp</strong> baking powder</li>
    #     </ul>
    #     <p>
    #         <div>Mix them well.</div>
    #     </p>
    #     <h2>Instructions</h2>
    #     <p>
    #         <div>Preheat oven to 350°F.</div>
    #         <div>Bake for 20 minutes.</div>
    #     </p>
    #     <p>
    #         <div>Enjoy your <a href="https://example.com/recipe">cake</a>!</div>
    #     </p>
    # """)
    # expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    # assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_ast_parser_with_markdown_features_and_comments():
    full_input = textwrap.dedent(
        """
        My Favorite Recipe

            Ingredients

                - 2 cups flour
                - 1 cup sugar
                - **1 tsp** baking powder

                Mix them well. // note: whisk thoroughly

            Instructions

                Preheat oven to 350°F. // oven temperature
                Bake for 20 minutes.

                Enjoy your [cake](https://example.com/recipe)! // bon appetit
        """
    )
    parsed_spaceup_ast = parse_spaceup_ast(full_input)
    expected_ast = ...
    assert _assert_ast_equal(parsed_spaceup_ast, expected_ast)
    # expected_html = textwrap.dedent(
    #     """
    #     <h1>My Favorite Recipe</h1>
    #     <h2>Ingredients</h2>
    #     <ul>
    #         <li>2 cups flour</li>
    #         <li>1 cup sugar</li>
    #         <li><strong>1 tsp</strong> baking powder</li>
    #     </ul>
    #     <p>
    #         <div>Mix them well.  <!-- note: whisk thoroughly --></div>
    #     </p>
    #     <h2>Instructions</h2>
    #     <p>
    #         <div>Preheat oven to 350°F.  <!-- oven temperature --></div>
    #         <div>Bake for 20 minutes.</div>
    #     </p>
    #     <p>
    #         <div>Enjoy your <a href="https://example.com/recipe">cake</a>!  <!-- bon appetit --></div>
    #     </p>
    #     """
    # )
    # expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    # spaceup_html = render_ast_to_html(parsed_spaceup_ast)
    # actual_structured_html = BeautifulSoup(spaceup_html, "html.parser")
    # assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_ast_parser_with_full_example_and_markdown_in_paragraphs():
    full_input = textwrap.dedent(
        """
        text with 0 indentation

            text with 1 indentation, with **bold** and a link to [site](https://example.com).
            another line with more text with 1 indentation and some *emphasis*.

            even some more text with 1 indentation, preceded by a blank line, and next non-whitespace, non-comment element has indentation LOWER OR EQUAL to this one  --> this is a paragraph open.

            here is a new line with 1 indentation, preceded by a blank line, BUT, next non-WS non comment element has a greater indentation level. Therefore, this is a H2. 

                - First step: mix ingredients
                - Use **butter** and [sugar](https://example.com/sugar)

                Some paragraph opener under the H2 heading from before, with an indentation level of 2, and a link to [docs](https://example.com/docs).
                Lorem ipsum a new div in the same paragraph because no blank line before it and indent level is also 2 with **strong** text.

                Foo text after a blank line with same indentation (2) as the preceding text; it is another paragraph opener under the H2 from before with a [link](https://example.com/foo).

            Back to indentation level 1. Note that the next line has a greater indentation than the current one. This necessarily makes this line a heading.
                This line has indentation level 2. Because 1 is LOWER THAN 2, the previous line is a heading (h2), and since the next element has a LOWER indentation level, this is a paragraph start with a single div.

            Back to indentation level 1. Next line has the same indentation with *italic* and a link to [spec](https://example.com/spec).
            Here is another line, right afterwards, with the SAME indentation level (1). This is a special case; read the comment below.
            // This text block is the first example where the two following conditions occur:
            // 1. indentation went DOWN (previous non-ws non-comment element was 2; now it's 1), and
            // 2. Two consecutive elements have the same indentation level (1), and going by rules, the first line of this block — 'Back to indentation level 1' — shouldn't be a heading. But we have to make an exception here.
            // In such an ambiguous, decreased-indentation case, where it's unclear how to parse the first line because the line which follows it shares the same indentation level, the first line is FORCED to become a heading. Subsequent lines in this block are forced to be indented. In effect, this makes this block with exactly the same structure as the one before it; an h2 line, followed by a paragraph starter.
        """
    )
    parsed_spaceup_ast = parse_spaceup_ast(full_input)
    expected_ast = ...
    assert _assert_ast_equal(parsed_spaceup_ast, expected_ast)
    # expected_html = textwrap.dedent(
    #     """
    #     <h1>text with 0 indentation</h1>
    #     <p>
    #         <div>text with 1 indentation, with <strong>bold</strong> and a link to <a href="https://example.com">site</a>.</div>
    #         <div>another line with more text with 1 indentation and some <em>emphasis</em>.</div>
    #     </p>
    #     <p>
    #         <div>even some more text with 1 indentation, preceded by a blank line, and next non-whitespace, non-comment element has indentation LOWER OR EQUAL to this one  --> this is a paragraph open.</div>
    #     </p>
    #     <h2>here is a new line with 1 indentation, preceded by a blank line, BUT, next non-WS non comment element has a greater indentation level. Therefore, this is a H2.</h2>
    #     <ul>
    #         <li>First step: mix ingredients</li>
    #         <li>Use <strong>butter</strong> and <a href="https://example.com/sugar">sugar</a></li>
    #     </ul>
    #     <p>
    #         <div>Some paragraph opener under the H2 heading from before, with an indentation level of 2, and a link to <a href="https://example.com/docs">docs</a>.</div>
    #         <div>Lorem ipsum a new div in the same paragraph because no blank line before it and indent level is also 2 with <strong>strong</strong> text.</div>
    #     </p>
    #     <p>
    #         <div>Foo text after a blank line with same indentation (2) as the preceding text; it is another paragraph opener under the H2 from before with a <a href="https://example.com/foo">link</a>.</div>
    #     </p>
    #     <h2>Back to indentation level 1. Note that the next line has a greater indentation than the current one. This necessarily makes this line a heading.</h2>
    #     <p>
    #         <div>This line has indentation level 2. Because 1 is LOWER THAN 2, the previous line is a heading (h2), and since the next element has a LOWER indentation level, this is a paragraph start with a single div.</div>
    #     </p>
    #     <h2>Back to indentation level 1. Next line has the same indentation with <em>italic</em> and a link to <a href="https://example.com/spec">spec</a>.</h2>
    #     <p>
    #         <div>Here is another line, right afterwards, with the SAME indentation level (1). This is a special case; read the comment below.</div>
    #     </p>
    #     <!-- This text block is the first example where the two following conditions occur: -->
    #     <!-- 1. indentation went DOWN (previous non-ws non-comment element was 2; now it's 1), and -->
    #     <!-- 2. Two consecutive elements have the same indentation level (1), and going by rules, the first line of this block — 'Back to indentation level 1' — shouldn't be a heading. But we have to make an exception here. -->
    #     <!-- In such an ambiguous, decreased-indentation case, where it's unclear how to parse the first line because the line which follows it shares the same indentation level, the first line is FORCED to become a heading. Subsequent lines in this block are forced to be indented. In effect, this makes this block with exactly the same structure as the one before it; an h2 line, followed by a paragraph starter. -->
    #     """
    # )
    # expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    # spaceup_html = render_ast_to_html(parsed_spaceup_ast)
    # actual_structured_html = BeautifulSoup(spaceup_html, "html.parser")
    # assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)
