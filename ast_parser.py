from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Union

try:
    # Imported for type hints only; tests won't depend on concrete token values
    from markdown_it.token import Token  # type: ignore
except Exception:  # pragma: no cover - fallback for environments without markdown-it
    Token = object  # type: ignore


@dataclass
class MarkdownInline:
    text: str
    tokens: List[Token] = field(default_factory=list)


@dataclass
class Div:
    content: MarkdownInline
    inline_comment: Optional[str] = None


@dataclass
class Paragraph:
    divs: List[Div]


@dataclass
class Heading:
    level: int
    content: MarkdownInline


@dataclass
class MarkdownBlock:
    text: str
    tokens: List[Token] = field(default_factory=list)


@dataclass
class Comment:
    text: str


Node = Union[Heading, Paragraph, MarkdownBlock, Comment]


@dataclass
class Document:
    children: List[Node]


def parse_spaceup_ast(input_str: str) -> Document:
    lines = [line.rstrip() for line in input_str.splitlines()]

    def compute_indent(line: str) -> Optional[int]:
        stripped = line.lstrip()
        if stripped == "" or stripped.startswith("//"):
            return None
        return len(line) - len(stripped)

    def next_non_ws_indent(idx: int) -> int:
        for i in range(idx + 1, len(lines)):
            ind = compute_indent(lines[i])
            if ind is not None:
                return ind
        return -1

    def split_content_and_inline_comment(text: str) -> tuple[str, Optional[str]]:
        stripped = text.lstrip()
        search_start = 0
        while True:
            pos = stripped.find("//", search_start)
            if pos == -1:
                break
            if pos == 0:
                search_start = pos + 2
                continue
            if stripped[pos - 1].isspace():
                return stripped[:pos].rstrip(), stripped[pos + 2 :].strip()
            search_start = pos + 2
        return stripped.strip(), None

    children: List[Node] = []
    indent_stack: List[int] = [0]
    pos = 0
    previous_non_ws_indent = 0

    def parse_block(current_indent: int) -> None:
        nonlocal pos, previous_non_ws_indent
        while pos < len(lines):
            # Skip blanks and pure comment lines entirely for AST v1
            while pos < len(lines):
                stripped = lines[pos].lstrip()
                if stripped == "":
                    pos += 1
                    continue
                if stripped.startswith("//"):
                    pos += 1
                    continue
                break

            if pos >= len(lines):
                return

            line = lines[pos]
            indent = compute_indent(line)
            if indent is None:
                pos += 1
                continue
            if indent < current_indent:
                return

            content_text, inline_comment = split_content_and_inline_comment(line)
            if content_text == "":
                pos += 1
                continue

            nxt_indent = next_non_ws_indent(pos)

            has_blank_before_next = False
            for i in range(pos + 1, len(lines)):
                if compute_indent(lines[i]) is not None:
                    break
                if lines[i].strip():
                    has_blank_before_next = True
            is_heading = False
            ambiguous_decrease = (
                previous_non_ws_indent > indent and nxt_indent == indent and not has_blank_before_next
            )
            if nxt_indent > indent or (nxt_indent == indent and has_blank_before_next) or ambiguous_decrease:
                is_heading = True

            heading_level = len(indent_stack)
            if is_heading:
                children.append(
                    Heading(level=heading_level, content=MarkdownInline(text=content_text, tokens=[]))
                )
                previous_non_ws_indent = indent
                indent_stack.append(indent)
                pos += 1
                if ambiguous_decrease:
                    # Force subsequent same-indented lines as paragraph content
                    divs: List[Div] = []
                    while pos < len(lines):
                        nindent = compute_indent(lines[pos])
                        if nindent is None or nindent != indent:
                            break
                        ncontent, ncomment = split_content_and_inline_comment(lines[pos])
                        if ncontent:
                            divs.append(
                                Div(content=MarkdownInline(text=ncontent, tokens=[]), inline_comment=ncomment)
                            )
                            previous_non_ws_indent = indent
                        pos += 1
                    if divs:
                        children.append(Paragraph(divs=divs))
                # Recurse into deeper content
                parse_block(indent + 1)
                indent_stack.pop()
            else:
                # Paragraph block: gather same-indented lines
                divs: List[Div] = [
                    Div(content=MarkdownInline(text=content_text, tokens=[]), inline_comment=inline_comment)
                ]
                pos += 1
                while pos < len(lines):
                    nindent = compute_indent(lines[pos])
                    if nindent != indent:
                        break
                    ncontent, ncomment = split_content_and_inline_comment(lines[pos])
                    if ncontent:
                        divs.append(
                            Div(content=MarkdownInline(text=ncontent, tokens=[]), inline_comment=ncomment)
                        )
                        previous_non_ws_indent = indent
                    pos += 1
                children.append(Paragraph(divs=divs))
                previous_non_ws_indent = indent

    parse_block(0)
    return Document(children=children)


def render_ast_to_html(ast: Document) -> str:
    raise NotImplementedError


