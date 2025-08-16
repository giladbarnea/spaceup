import { describe, it, expect } from "vitest";
import { unified } from "unified";
import { toHast } from "mdast-util-to-hast";
import { toHtml } from "hast-util-to-html";
import ast from "../ast_parser.js";
import mdastAdaptor from "../adaptors/mdast/mdast.js";

const { Document, Heading, Paragraph, ParagraphLine, MarkdownInline, Comment } = ast;
const { documentToMdast } = mdastAdaptor;

function renderMdastToHtml(mdastTree) {
  // mdast → hast → html
  const hast = toHast(mdastTree, { allowDangerousHtml: true });
  return toHtml(hast, { allowDangerousHtml: true });
}

describe("mdast adaptor", () => {
  it("heading + paragraph", () => {
    const doc = Document([
      Heading(1, MarkdownInline("Hello", [])),
      Paragraph([
        ParagraphLine(MarkdownInline("This is a line.", []), null),
        ParagraphLine(MarkdownInline("Another line.", []), null),
      ]),
    ]);
    const mdast = documentToMdast(doc);
    expect(mdast.type).toBe("root");
    expect(mdast.children[0]).toMatchObject({ type: "heading", depth: 1 });
    expect(mdast.children[1]).toMatchObject({ type: "paragraph" });
    const html = renderMdastToHtml(mdast);
    expect(html).toContain("<h1>");
    expect(html).toContain("<p>");
  });

  it("unordered list detection from paragraph lines starting with - ", () => {
    const doc = Document([
      Paragraph([
        ParagraphLine(MarkdownInline("- item one", []), null),
        ParagraphLine(MarkdownInline("- item two", []), null),
      ]),
    ]);
    const mdast = documentToMdast(doc);
    expect(mdast.children[0]).toMatchObject({ type: "list", ordered: false });
    const html = renderMdastToHtml(mdast);
    expect(html).toContain("<ul>");
    expect(html).toContain("<li>");
  });

  it("inline comment becomes html node", () => {
    const doc = Document([
      Paragraph([
        ParagraphLine(MarkdownInline("Text", []), "note: test"),
      ]),
    ]);
    const mdast = documentToMdast(doc);
    const para = mdast.children[0];
    expect(para.type).toBe("paragraph");
    const hasHtml = para.children.some((c) => c.type === "html" && /note: test/.test(c.value));
    expect(hasHtml).toBe(true);
  });
});


