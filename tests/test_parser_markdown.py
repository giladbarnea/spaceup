"""
Tests for Markdown features in the Spaceup parser.

These tests focus on how various Markdown features are rendered when used
within Spaceup documents. They are ordered from most common to least common features.
"""

import textwrap
from pprint import pformat
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString, Comment
from pathlib import Path

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


def test_bold_text():
    """Test that **bold** text is rendered as <strong> tags."""
    input_text = (Path(__file__).parent / "data" / "bold_text.txt").read_text()
    
    expected_html = (Path(__file__).parent / "data" / "bold_text.html").read_text()
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    actual_html_ast = _soup_ast(actual_structured_html)
    expected_html_ast = _soup_ast(expected_structured_html)
    actual_html_ast_str = pformat(actual_html_ast, indent=2)
    expected_html_ast_str = pformat(expected_html_ast, indent=2)
    assert actual_html_ast_str == expected_html_ast_str


def test_italic_text():
    """Test that *italic* text is rendered as <em> tags."""
    input_text = (Path(__file__).parent / "data" / "italic_text.txt").read_text()
    
    expected_html = (Path(__file__).parent / "data" / "italic_text.html").read_text()
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    actual_html_ast = _soup_ast(actual_structured_html)
    expected_html_ast = _soup_ast(expected_structured_html)
    actual_html_ast_str = pformat(actual_html_ast, indent=2)
    expected_html_ast_str = pformat(expected_html_ast, indent=2)
    assert actual_html_ast_str == expected_html_ast_str


def test_url_links():
    """Test that [text](url) syntax creates proper links."""
    input_text = (Path(__file__).parent / "data" / "url_links.txt").read_text()
    
    expected_html = (Path(__file__).parent / "data" / "url_links.html").read_text()
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    actual_html_ast = _soup_ast(actual_structured_html)
    expected_html_ast = _soup_ast(expected_structured_html)
    actual_html_ast_str = pformat(actual_html_ast, indent=2)
    expected_html_ast_str = pformat(expected_html_ast, indent=2)
    assert actual_html_ast_str == expected_html_ast_str


def test_inline_code():
    """Test that `code` syntax creates <code> tags."""
    input_text = (Path(__file__).parent / "data" / "inline_code.txt").read_text()
    
    expected_html = (Path(__file__).parent / "data" / "inline_code.html").read_text()
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    actual_html_ast = _soup_ast(actual_structured_html)
    expected_html_ast = _soup_ast(expected_structured_html)
    actual_html_ast_str = pformat(actual_html_ast, indent=2)
    expected_html_ast_str = pformat(expected_html_ast, indent=2)
    assert actual_html_ast_str == expected_html_ast_str


def test_unordered_lists():
    """Test that - creates unordered lists."""
    input_text = (Path(__file__).parent / "data" / "unordered_lists.txt").read_text()
    
    expected_html = (Path(__file__).parent / "data" / "unordered_lists.html").read_text()
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    actual_html_ast = _soup_ast(actual_structured_html)
    expected_html_ast = _soup_ast(expected_structured_html)
    actual_html_ast_str = pformat(actual_html_ast, indent=2)
    expected_html_ast_str = pformat(expected_html_ast, indent=2)
    assert actual_html_ast_str == expected_html_ast_str


def test_ordered_lists():
    """Test that 1. creates ordered lists."""
    input_text = (Path(__file__).parent / "data" / "ordered_lists.txt").read_text()
    
    expected_html = (Path(__file__).parent / "data" / "ordered_lists.html").read_text()
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    actual_html_ast = _soup_ast(actual_structured_html)
    expected_html_ast = _soup_ast(expected_structured_html)
    actual_html_ast_str = pformat(actual_html_ast, indent=2)
    expected_html_ast_str = pformat(expected_html_ast, indent=2)
    assert actual_html_ast_str == expected_html_ast_str


def test_code_blocks():
    """Test that ``` creates code blocks."""
    input_text = (Path(__file__).parent / "data" / "code_blocks.txt").read_text()
    
    expected_html = (Path(__file__).parent / "data" / "code_blocks.html").read_text()
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    actual_html_ast = _soup_ast(actual_structured_html)
    expected_html_ast = _soup_ast(expected_structured_html)
    actual_html_ast_str = pformat(actual_html_ast, indent=2)
    expected_html_ast_str = pformat(expected_html_ast, indent=2)
    assert actual_html_ast_str == expected_html_ast_str


def test_local_file_references():
    """Test that local file paths work in links."""
    input_text = (Path(__file__).parent / "data" / "local_file_references.txt").read_text()
    
    expected_html = (Path(__file__).parent / "data" / "local_file_references.html").read_text()
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    actual_html_ast = _soup_ast(actual_structured_html)
    expected_html_ast = _soup_ast(expected_structured_html)
    actual_html_ast_str = pformat(actual_html_ast, indent=2)
    expected_html_ast_str = pformat(expected_html_ast, indent=2)
    assert actual_html_ast_str == expected_html_ast_str


def test_blockquotes():
    """Test that > creates blockquotes."""
    input_text = (Path(__file__).parent / "data" / "blockquotes.txt").read_text()
    
    expected_html = (Path(__file__).parent / "data" / "blockquotes.html").read_text()
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    actual_html_ast = _soup_ast(actual_structured_html)
    expected_html_ast = _soup_ast(expected_structured_html)
    actual_html_ast_str = pformat(actual_html_ast, indent=2)
    expected_html_ast_str = pformat(expected_html_ast, indent=2)
    assert actual_html_ast_str == expected_html_ast_str


def test_checklists():
    """Test that - [ ] and - [x] create checklists."""
    input_text = (Path(__file__).parent / "data" / "checklists.txt").read_text()
    
    expected_html = (Path(__file__).parent / "data" / "checklists.html").read_text()
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    actual_html_ast = _soup_ast(actual_structured_html)
    expected_html_ast = _soup_ast(expected_structured_html)
    actual_html_ast_str = pformat(actual_html_ast, indent=2)
    expected_html_ast_str = pformat(expected_html_ast, indent=2)
    assert actual_html_ast_str == expected_html_ast_str


def test_tables():
    """Test that | creates tables."""
    input_text = (Path(__file__).parent / "data" / "tables.txt").read_text()
    
    expected_html = (Path(__file__).parent / "data" / "tables.html").read_text()
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    actual_html_ast = _soup_ast(actual_structured_html)
    expected_html_ast = _soup_ast(expected_structured_html)
    actual_html_ast_str = pformat(actual_html_ast, indent=2)
    expected_html_ast_str = pformat(expected_html_ast, indent=2)
    assert actual_html_ast_str == expected_html_ast_str
