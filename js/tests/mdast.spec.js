import { describe, it, expect } from "vitest";
import { unified } from "unified";
import { readFileSync } from "node:fs";
import path, { join } from "node:path";
import { fileURLToPath } from "node:url";
import { JSDOM } from "jsdom";
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

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function normalizeText(s) {
  return s.split(/\s+/).filter(Boolean).join(" ");
}

function normalizeNode(node) {
  const NodeType = node.nodeType;
  if (NodeType === 8) {
    const text = String(node.nodeValue || "");
    if (text.trim() === "") return null;
    return ["#comment", normalizeText(text)];
  }
  if (NodeType === 3) {
    const text = String(node.nodeValue || "");
    if (text.trim() === "") return null;
    return ["#text", normalizeText(text)];
  }
  if (NodeType === 1) {
    const children = [];
    for (const child of node.childNodes) {
      const norm = normalizeNode(child);
      if (norm != null) children.push(norm);
    }
    return [node.tagName.toLowerCase(), children];
  }
  return null;
}

function soupAst(html) {
  const frag = JSDOM.fragment(html);
  const astChildren = [];
  for (const child of frag.childNodes) {
    const norm = normalizeNode(child);
    if (norm != null) astChildren.push(norm);
  }
  return astChildren;
}

function readData(name) {
  return readFileSync(join(__dirname, "data", name), "utf8");
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

  // Parity tests with fixtures: Spaceup AST → MDAST → HAST → HTML ≈ expected HTML
  it("basic example (fixtures)", () => {
    const input = readData("basic_example.txt");
    const expectedHtml = readData("basic_example.html");
    const parsed = ast.parseSpaceupAst(input);
    const mdast = documentToMdast(parsed);
    const actualHtml = renderMdastToHtml(mdast);
    expect(soupAst(actualHtml)).toEqual(soupAst(expectedHtml));
  });

  it("end of document paragraph (fixtures)", () => {
    const input = readData("end_of_document_paragraph.txt");
    const expectedHtml = readData("end_of_document_paragraph.html");
    const parsed = ast.parseSpaceupAst(input);
    const mdast = documentToMdast(parsed);
    const actualHtml = renderMdastToHtml(mdast);
    expect(soupAst(actualHtml)).toEqual(soupAst(expectedHtml));
  });

  it("two indentation levels (fixtures)", () => {
    const input = readData("two_indentation_levels.txt");
    const expectedHtml = readData("two_indentation_levels.html");
    const parsed = ast.parseSpaceupAst(input);
    const mdast = documentToMdast(parsed);
    const actualHtml = renderMdastToHtml(mdast);
    expect(soupAst(actualHtml)).toEqual(soupAst(expectedHtml));
  });

  it("unambiguous decreasing indentation level (fixtures)", () => {
    const input = readData("unambiguous_decreasing_indentation_level.txt");
    const expectedHtml = readData("unambiguous_decreasing_indentation_level.html");
    const parsed = ast.parseSpaceupAst(input);
    const mdast = documentToMdast(parsed);
    const actualHtml = renderMdastToHtml(mdast);
    expect(soupAst(actualHtml)).toEqual(soupAst(expectedHtml));
  });

  it("ambiguous decreasing indentation level (fixtures)", () => {
    const input = readData("ambiguous_decreasing_indentation_level.txt");
    const expectedHtml = readData("ambiguous_decreasing_indentation_level.html");
    const parsed = ast.parseSpaceupAst(input);
    const mdast = documentToMdast(parsed);
    const actualHtml = renderMdastToHtml(mdast);
    expect(soupAst(actualHtml)).toEqual(soupAst(expectedHtml));
  });

  it("comments sanity (fixtures)", () => {
    const input = readData("comments_sanity.txt");
    const expectedHtml = readData("comments_sanity.html");
    const parsed = ast.parseSpaceupAst(input);
    const mdast = documentToMdast(parsed);
    const actualHtml = renderMdastToHtml(mdast);
    expect(soupAst(actualHtml)).toEqual(soupAst(expectedHtml));
  });

  it("full example (fixtures)", () => {
    const input = readData("full_example.txt");
    const expectedHtml = readData("full_example.html");
    const parsed = ast.parseSpaceupAst(input);
    const mdast = documentToMdast(parsed);
    const actualHtml = renderMdastToHtml(mdast);
    expect(soupAst(actualHtml)).toEqual(soupAst(expectedHtml));
  });

  it("markdown features (fixtures)", () => {
    const input = readData("markdown_features.txt");
    const expectedHtml = readData("markdown_features.html");
    const parsed = ast.parseSpaceupAst(input);
    const mdast = documentToMdast(parsed);
    const actualHtml = renderMdastToHtml(mdast);
    expect(soupAst(actualHtml)).toEqual(soupAst(expectedHtml));
  });

  it("markdown features and comments (fixtures)", () => {
    const input = readData("markdown_features_and_comments.txt");
    const expectedHtml = readData("markdown_features_and_comments.html");
    const parsed = ast.parseSpaceupAst(input);
    const mdast = documentToMdast(parsed);
    const actualHtml = renderMdastToHtml(mdast);
    expect(soupAst(actualHtml)).toEqual(soupAst(expectedHtml));
  });

  it("full example and markdown in paragraphs (fixtures)", () => {
    const input = readData("full_example_and_markdown_in_paragraphs.txt");
    const expectedHtml = readData("full_example_and_markdown_in_paragraphs.html");
    const parsed = ast.parseSpaceupAst(input);
    const mdast = documentToMdast(parsed);
    const actualHtml = renderMdastToHtml(mdast);
    expect(soupAst(actualHtml)).toEqual(soupAst(expectedHtml));
  });
});


