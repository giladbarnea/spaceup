"""
Read SPEC.md to understand the purpose of each test.

Note that when comparing HTML, whitespace does NOT matter.
Hence it is normalized before comparison.
"""

from pathlib import Path
import textwrap

from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString, Comment

from parser import parse_spaceup


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


def _soup_ast(soup):
    ast_children = []
    for child in soup.contents:
        norm = _normalize_node(child)
        if norm is not None:
            ast_children.append(norm)
    return tuple(ast_children)


def test_parser_with_basic_example():
    basic_input = Path("tests/data/basic_example.txt").read_text()
    expected_html = Path("tests/data/basic_example.html").read_text()
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(basic_input)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_parser_with_end_of_document_paragraph():
    end_of_document_paragraph_input = Path("tests/data/end_of_document_paragraph.txt").read_text()
    expected_html = Path("tests/data/end_of_document_paragraph.html").read_text()
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(end_of_document_paragraph_input)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_parser_with_two_indentation_levels():
    full_input = Path("tests/data/two_indentation_levels.txt").read_text()
    expected_html = Path("tests/data/two_indentation_levels.html").read_text()
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(full_input)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_parser_with_unambiguous_decreasing_indentation_level():
    full_input = Path("tests/data/unambiguous_decreasing_indentation_level.txt").read_text()
    expected_html = Path("tests/data/unambiguous_decreasing_indentation_level.html").read_text()
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(full_input)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_parser_with_ambiguous_decreasing_indentation_level():
    """Tests resolving the ambiguity created by the first line of a block with a decreasing indentation level by forcing it to be treated as a heading."""

    full_input = Path("tests/data/ambiguous_decreasing_indentation_level.txt").read_text()
    expected_html = Path("tests/data/ambiguous_decreasing_indentation_level.html").read_text()
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(full_input)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_parser_with_comments_sanity():
    full_input = Path("tests/data/comments_sanity.txt").read_text()
    expected_html = Path("tests/data/comments_sanity.html").read_text()
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(full_input)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_parser_with_full_example():
    full_input = Path("tests/data/full_example.txt").read_text()
    expected_html = Path("tests/data/full_example.html").read_text()
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(full_input)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_parser_with_markdown_features():
    full_input = Path("tests/data/markdown_features.txt").read_text()
    expected_html = Path("tests/data/markdown_features.html").read_text()
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(full_input)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_parser_with_markdown_features_and_comments():
    full_input = Path("tests/data/markdown_features_and_comments.txt").read_text()
    expected_html = Path("tests/data/markdown_features_and_comments.html").read_text()
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(full_input)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_parser_with_full_example_and_markdown_in_paragraphs():
    full_input = Path("tests/data/full_example_and_markdown_in_paragraphs.txt").read_text()
    expected_html = Path("tests/data/full_example_and_markdown_in_paragraphs.html").read_text()
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(full_input)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)
