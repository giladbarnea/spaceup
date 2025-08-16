"use strict";

function clampHeadingDepth(level) {
  if (level < 1) return 1;
  if (level > 6) return 6;
  return level;
}

function textNode(value) {
  return { type: "text", value: String(value ?? "") };
}

function htmlCommentNode(value) {
  return { type: "html", value: `<!-- ${String(value ?? "")} -->` };
}

function breakNode() {
  return { type: "break" };
}

function inlineTextToChildren(text) {
  if (!text) return [];
  return [textNode(text)];
}

function paragraphLinesAreBulleted(lines) {
  if (!Array.isArray(lines) || lines.length === 0) return false;
  for (const line of lines) {
    const t = (line?.content?.text ?? "").replace(/^\s+/, "");
    if (!t.startsWith("- ")) return false;
  }
  return true;
}

function listFromBulletedParagraph(paragraph) {
  const items = [];
  for (const line of paragraph.lines) {
    const raw = String(line?.content?.text ?? "");
    const itemText = raw.replace(/^\s+/, "").slice(2).trim();
    const paraChildren = inlineTextToChildren(itemText);
    if (line.inline_comment) {
      paraChildren.push(htmlCommentNode(line.inline_comment));
    }
    items.push({
      type: "listItem",
      spread: false,
      children: [{ type: "paragraph", children: paraChildren }],
    });
  }
  return { type: "list", ordered: false, spread: false, children: items };
}

function paragraphToMdast(paragraph) {
  if (paragraphLinesAreBulleted(paragraph.lines)) {
    return listFromBulletedParagraph(paragraph);
  }
  const children = [];
  for (let i = 0; i < paragraph.lines.length; i += 1) {
    const line = paragraph.lines[i];
    children.push(...inlineTextToChildren(line?.content?.text ?? ""));
    if (line.inline_comment) children.push(htmlCommentNode(line.inline_comment));
    if (i < paragraph.lines.length - 1) children.push(breakNode());
  }
  return { type: "paragraph", children };
}

function headingToMdast(heading) {
  const node = {
    type: "heading",
    depth: clampHeadingDepth(Number(heading?.level ?? 1)),
    children: inlineTextToChildren(heading?.content?.text ?? ""),
  };
  if (heading.level > 6) {
    node.data = { spaceupHeadingLevel: heading.level };
  }
  return node;
}

function documentToMdast(document) {
  const children = [];
  for (const node of document.children || []) {
    if (node && typeof node.level === "number" && node.content) {
      children.push(headingToMdast(node));
      continue;
    }
    if (node && Array.isArray(node.lines)) {
      children.push(paragraphToMdast(node));
      continue;
    }
    if (node && typeof node.text === "string") {
      if (node.text) children.push(htmlCommentNode(node.text));
      continue;
    }
    if (node && typeof node.text === "string" && node.tokens) {
      // MarkdownBlock (not used currently) → paragraph fallback
      children.push({ type: "paragraph", children: inlineTextToChildren(node.text) });
    }
  }
  return { type: "root", children };
}

module.exports = {
  documentToMdast,
};


