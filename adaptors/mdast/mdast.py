from __future__ import annotations

from typing import Any, Dict, List

from ast_parser import Document, Heading, Paragraph, ParagraphLine, Comment, MarkdownBlock, Node


def document_to_mdast(document: Document) -> Dict[str, Any]:
    """Convert a Spaceup Document into an mdast-compatible dict tree."""

    def clamp_heading_depth(level: int) -> int:
        return 6 if level > 6 else 1 if level < 1 else level

    def text_node(value: str) -> Dict[str, Any]:
        return {"type": "text", "value": value}

    def html_comment_node(value: str) -> Dict[str, Any]:
        return {"type": "html", "value": f"<!-- {value} -->"}

    def break_node() -> Dict[str, Any]:
        return {"type": "break"}

    def inline_text_to_children(text: str) -> List[Dict[str, Any]]:
        # Minimal mapping: treat entire inline Markdown as plain text.
        # Future: parse markdown-it tokens and map to mdast phrasing nodes.
        if not text:
            return []
        return [text_node(text)]

    def paragraph_lines_are_bulleted(lines: List[ParagraphLine]) -> bool:
        if not lines:
            return False
        for line in lines:
            if not line.content.text.lstrip().startswith("- "):
                return False
        return True

    def list_from_bulleted_paragraph(paragraph: Paragraph) -> Dict[str, Any]:
        items: List[Dict[str, Any]] = []
        for line in paragraph.lines:
            # Strip a single leading bullet "- "
            text = line.content.text.lstrip()[2:].strip()
            item_children: List[Dict[str, Any]] = []
            para_children = inline_text_to_children(text)
            if line.inline_comment:
                para_children.append(html_comment_node(line.inline_comment))
            item_children.append({"type": "paragraph", "children": para_children})
            items.append({"type": "listItem", "children": item_children})
        return {"type": "list", "ordered": False, "spread": False, "children": items}

    def paragraph_to_mdast(paragraph: Paragraph) -> Dict[str, Any]:
        # Special-case: simple unordered list using "- " prefix on all lines
        if paragraph_lines_are_bulleted(paragraph.lines):
            return list_from_bulleted_paragraph(paragraph)

        children: List[Dict[str, Any]] = []
        for idx, line in enumerate(paragraph.lines):
            children.extend(inline_text_to_children(line.content.text))
            if line.inline_comment:
                children.append(html_comment_node(line.inline_comment))
            # Insert a soft break between lines (not after the last)
            if idx < len(paragraph.lines) - 1:
                children.append(break_node())
        return {"type": "paragraph", "children": children}

    def heading_to_mdast(heading: Heading) -> Dict[str, Any]:
        children = inline_text_to_children(heading.content.text)
        node: Dict[str, Any] = {
            "type": "heading",
            "depth": clamp_heading_depth(heading.level),
            "children": children,
        }
        if heading.level > 6:
            node["data"] = {"spaceupHeadingLevel": heading.level}
        return node

    def node_to_mdast(node: Node) -> Dict[str, Any] | None:
        if isinstance(node, Heading):
            return heading_to_mdast(node)
        if isinstance(node, Paragraph):
            return paragraph_to_mdast(node)
        if isinstance(node, Comment):
            if not node.text:
                return None
            return html_comment_node(node.text)
        if isinstance(node, MarkdownBlock):
            # Treat as a plain paragraph for now.
            return {"type": "paragraph", "children": inline_text_to_children(node.text)}
        return None

    children: List[Dict[str, Any]] = []
    for child in document.children:
        converted = node_to_mdast(child)
        if converted is None:
            continue
        children.append(converted)

    return {"type": "root", "children": children}


