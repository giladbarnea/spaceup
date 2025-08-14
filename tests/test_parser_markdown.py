"""
Tests for Markdown features in the Spaceup parser.

These tests focus on how various Markdown features are rendered when used
within Spaceup documents. They are ordered from most common to least common features.
"""

import textwrap
from pathlib import Path

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


def test_bold_text():
    """Test that **bold** text is rendered as <strong> tags."""
    input_text = textwrap.dedent("""
        Bold test
            Here is some **bold** text.
    """)
    Path("tests/data/markdown_bold.txt").write_text(input_text)
    
    expected_html = textwrap.dedent("""
        <h1>Bold test</h1>
        <p>
            Here is some <strong>bold</strong> text.<br>
        </p>
    """)
    Path("tests/data/markdown_bold.html").write_text(expected_html)
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_italic_text():
    """Test that *italic* text is rendered as <em> tags."""
    input_text = textwrap.dedent("""
        Italic test
            Here is some *italic* text.
    """)
    Path("tests/data/markdown_italic.txt").write_text(input_text)
    
    expected_html = textwrap.dedent("""
        <h1>Italic test</h1>
        <p>
            Here is some <em>italic</em> text.<br>
        </p>
    """)
    Path("tests/data/markdown_italic.html").write_text(expected_html)
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_url_links():
    """Test that [text](url) syntax creates proper links."""
    input_text = textwrap.dedent("""
        Links test
            Visit [GitHub](https://github.com) for more info.
    """)
    Path("tests/data/markdown_url_links.txt").write_text(input_text)
    
    expected_html = textwrap.dedent("""
        <h1>Links test</h1>
        <p>
            Visit <a href="https://github.com">GitHub</a> for more info.<br>
        </p>
    """)
    Path("tests/data/markdown_url_links.html").write_text(expected_html)
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_inline_code():
    """Test that `code` syntax creates <code> tags."""
    input_text = textwrap.dedent("""
        Code test
            Use the `print()` function to output text.
    """)
    Path("tests/data/markdown_inline_code.txt").write_text(input_text)
    
    expected_html = textwrap.dedent("""
        <h1>Code test</h1>
        <p>
            Use the <code>print()</code> function to output text.<br>
        </p>
    """)
    Path("tests/data/markdown_inline_code.html").write_text(expected_html)
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_unordered_lists():
    """Test that - creates unordered lists."""
    input_text = textwrap.dedent("""
        Shopping list
            - Apples
            - Bananas
            - Oranges
    """)
    Path("tests/data/markdown_unordered_lists.txt").write_text(input_text)
    
    expected_html = textwrap.dedent("""
        <h1>Shopping list</h1>
        <ul>
            <li>Apples</li>
            <li>Bananas</li>
            <li>Oranges</li>
        </ul>
    """)
    Path("tests/data/markdown_unordered_lists.html").write_text(expected_html)
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_ordered_lists():
    """Test that 1. creates ordered lists."""
    input_text = textwrap.dedent("""
        Steps
            1. First step
            2. Second step
            3. Third step
    """)
    Path("tests/data/markdown_ordered_lists.txt").write_text(input_text)
    
    expected_html = textwrap.dedent("""
        <h1>Steps</h1>
        <ol>
            <li>First step</li>
            <li>Second step</li>
            <li>Third step</li>
        </ol>
    """)
    Path("tests/data/markdown_ordered_lists.html").write_text(expected_html)
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_code_blocks():
    """Test that ``` creates code blocks."""
    input_text = textwrap.dedent("""
        Code example
            ```python
            def hello():
                print("Hello, world!")
            ```
    """)
    Path("tests/data/markdown_code_blocks.txt").write_text(input_text)
    
    expected_html = textwrap.dedent("""
        <h1>Code example</h1>
        <pre><code class="language-python">def hello():
    print("Hello, world!")
</code></pre>
    """)
    Path("tests/data/markdown_code_blocks.html").write_text(expected_html)
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_local_file_references():
    """Test that local file paths work in links."""
    input_text = textwrap.dedent("""
        Documentation
            See [README](./README.md) for details.
    """)
    Path("tests/data/markdown_local_files.txt").write_text(input_text)
    
    expected_html = textwrap.dedent("""
        <h1>Documentation</h1>
        <p>
            See <a href="./README.md">README</a> for details.<br>
        </p>
    """)
    Path("tests/data/markdown_local_files.html").write_text(expected_html)
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_blockquotes():
    """Test that > creates blockquotes."""
    input_text = textwrap.dedent("""
        Quote example
            > This is a blockquote.
            > It can span multiple lines.
    """)
    Path("tests/data/markdown_blockquotes.txt").write_text(input_text)
    
    expected_html = textwrap.dedent("""
        <h1>Quote example</h1>
        <blockquote>
            <p>This is a blockquote.
            It can span multiple lines.</p>
        </blockquote>
    """)
    Path("tests/data/markdown_blockquotes.html").write_text(expected_html)
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_checklists():
    """Test that - [ ] and - [x] create checklists."""
    input_text = textwrap.dedent("""
        Todo list
            - [x] Completed task
            - [ ] Pending task
            - [ ] Another pending task
    """)
    Path("tests/data/markdown_checklists.txt").write_text(input_text)
    
    expected_html = textwrap.dedent("""
        <h1>Todo list</h1>
        <ul>
            <li><input type="checkbox" checked disabled> Completed task</li>
            <li><input type="checkbox" disabled> Pending task</li>
            <li><input type="checkbox" disabled> Another pending task</li>
        </ul>
    """)
    Path("tests/data/markdown_checklists.html").write_text(expected_html)
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)


def test_tables():
    """Test that | creates tables."""
    input_text = textwrap.dedent("""
        Data table
            | Name  | Age | City    |
            |-------|-----|---------|
            | Alice | 30  | New York|
            | Bob   | 25  | Boston  |
    """)
    Path("tests/data/markdown_tables.txt").write_text(input_text)
    
    expected_html = textwrap.dedent("""
        <h1>Data table</h1>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Age</th>
                    <th>City</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Alice</td>
                    <td>30</td>
                    <td>New York</td>
                </tr>
                <tr>
                    <td>Bob</td>
                    <td>25</td>
                    <td>Boston</td>
                </tr>
            </tbody>
        </table>
    """)
    Path("tests/data/markdown_tables.html").write_text(expected_html)
    
    expected_structured_html = BeautifulSoup(expected_html, "html.parser")
    parsed_spaceup = parse_spaceup(input_text)
    actual_structured_html = BeautifulSoup(parsed_spaceup, "html.parser")
    assert _soup_ast(expected_structured_html) == _soup_ast(actual_structured_html)
