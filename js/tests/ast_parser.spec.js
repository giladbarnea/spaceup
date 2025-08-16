import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import path, { join } from "node:path";
import { JSDOM } from "jsdom";
import { fileURLToPath } from "node:url";

import ast from "../ast_parser.js";

const {
  parseSpaceupAst,
  renderAstToHtml,
  Document,
  Heading,
  Paragraph,
  MarkdownInline,
  ParagraphLine,
  Comment,
} = ast;

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

describe("ast_parser parity", () => {
  it("basic example", () => {
    const input = readData("basic_example.txt");
    const parsed = parseSpaceupAst(input);
    const expectedAst = Document([
      Heading(1, MarkdownInline("text with 0 indentation", [])),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know.",
            []
          ),
          null
        ),
        ParagraphLine(MarkdownInline("another line with more text with 1 indentation.", []), null),
      ]),
    ]);
    expect(parsed).toEqual(expectedAst);

    const expectedHtml = readData("basic_example.html");
    const actualHtml = renderAstToHtml(parsed);
    expect(soupAst(actualHtml)).toEqual(soupAst(expectedHtml));
  });

  it("end of document paragraph", () => {
    const input = readData("end_of_document_paragraph.txt");
    const parsed = parseSpaceupAst(input);
    const expectedAst = Document([
      Heading(1, MarkdownInline("text with 0 indentation", [])),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "text with 1 indentation. 1 is greater than the preceding 0, and that's the last element in the document (next is EOF) --> this text is a paragraph opener, and the preceding element is an h1.",
            []
          ),
          null
        ),
      ]),
    ]);
    expect(parsed).toEqual(expectedAst);

    const expectedHtml = readData("end_of_document_paragraph.html");
    const actualHtml = renderAstToHtml(parsed);
    expect(soupAst(actualHtml)).toEqual(soupAst(expectedHtml));
  });

  it("two indentation levels", () => {
    const input = readData("two_indentation_levels.txt");
    const parsed = parseSpaceupAst(input);
    const expectedAst = Document([
      Heading(1, MarkdownInline("text with 0 indentation", [])),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know.",
            []
          ),
          null
        ),
        ParagraphLine(MarkdownInline("another line with more text with 1 indentation.", []), null),
      ]),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "even some more text with 1 indentation, preceded by a blank line, and next non-whitespace, non-comment element has indentation LOWER OR EQUAL to this one  --> this is a paragraph open.",
            []
          ),
          null
        ),
      ]),
      Heading(
        2,
        MarkdownInline(
          "here is a new line with 1 indentation, preceded by a blank line, BUT, next non-WS non comment element has a greater indentation level. Therefore, this is a H2.",
          []
        )
      ),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "Some paragraph opener under the H2 heading from before, with an indentation level of 2.",
            []
          ),
          null
        ),
        ParagraphLine(
          MarkdownInline(
            "Lorem ipsum a new div in the same paragraph because no blank line before it and indent level is also 2.",
            []
          ),
          null
        ),
      ]),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "Foo text after a blank line with same indentation (2) as the preceding text; it is another paragraph opener under the H2 from before.",
            []
          ),
          null
        ),
      ]),
    ]);
    expect(parsed).toEqual(expectedAst);

    const expectedHtml = readData("two_indentation_levels.html");
    const actualHtml = renderAstToHtml(parsed);
    expect(soupAst(actualHtml)).toEqual(soupAst(expectedHtml));
  });

  it("unambiguous decreasing indentation level", () => {
    const input = readData("unambiguous_decreasing_indentation_level.txt");
    const parsed = parseSpaceupAst(input);
    const expectedAst = Document([
      Heading(1, MarkdownInline("text with 0 indentation", [])),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know.",
            []
          ),
          null
        ),
        ParagraphLine(MarkdownInline("another line with more text with 1 indentation.", []), null),
      ]),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "even some more text with 1 indentation, preceded by a blank line, and next non-whitespace, non-comment element has indentation LOWER OR EQUAL to this one  --> this is a paragraph open.",
            []
          ),
          null
        ),
      ]),
      Heading(
        2,
        MarkdownInline(
          "here is a new line with 1 indentation, preceded by a blank line, BUT, next non-WS non comment element has a greater indentation level. Therefore, this is a H2.",
          []
        )
      ),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "Some paragraph opener under the H2 heading from before, with an indentation level of 2.",
            []
          ),
          null
        ),
        ParagraphLine(
          MarkdownInline(
            "Lorem ipsum a new div in the same paragraph because no blank line before it and indent level is also 2.",
            []
          ),
          null
        ),
      ]),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "Foo text after a blank line with same indentation (2) as the preceding text; it is another paragraph opener under the H2 from before.",
            []
          ),
          null
        ),
      ]),
      Heading(
        2,
        MarkdownInline(
          "Back to indentation level 1. Note that the next line has a greater indentation than the current one. This necessarily makes this line a heading.",
          []
        )
      ),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "This line has indentation level 2. Because 1 is LOWER THAN 2, the previous line is a heading (h2), and since this is the end of the document, this is a paragraph start with a single div.",
            []
          ),
          null
        ),
      ]),
    ]);
    expect(parsed).toEqual(expectedAst);

    const expectedHtml = readData("unambiguous_decreasing_indentation_level.html");
    const actualHtml = renderAstToHtml(parsed);
    expect(soupAst(actualHtml)).toEqual(soupAst(expectedHtml));
  });

  it("ambiguous decreasing indentation level", () => {
    const input = readData("ambiguous_decreasing_indentation_level.txt");
    const parsed = parseSpaceupAst(input);
    const expectedAst = Document([
      Heading(1, MarkdownInline("text with 0 indentation", [])),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know.",
            []
          ),
          null
        ),
        ParagraphLine(MarkdownInline("another line with more text with 1 indentation.", []), null),
      ]),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "even some more text with 1 indentation, preceded by a blank line, and next non-whitespace, non-comment element has indentation LOWER OR EQUAL to this one  --> this is a paragraph open.",
            []
          ),
          null
        ),
      ]),
      Heading(
        2,
        MarkdownInline(
          "here is a new line with 1 indentation, preceded by a blank line, BUT, next non-WS non comment element has a greater indentation level. Therefore, this is a H2.",
          []
        )
      ),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "Some paragraph opener under the H2 heading from before, with an indentation level of 2.",
            []
          ),
          null
        ),
        ParagraphLine(
          MarkdownInline(
            "Lorem ipsum a new div in the same paragraph because no blank line before it and indent level is also 2.",
            []
          ),
          null
        ),
      ]),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "Foo text after a blank line with same indentation (2) as the preceding text; it is another paragraph opener under the H2 from before.",
            []
          ),
          null
        ),
      ]),
      Heading(
        2,
        MarkdownInline(
          "Back to indentation level 1. Note that the next line has a greater indentation than the current one. This necessarily makes this line a heading.",
          []
        )
      ),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "This line has indentation level 2. Because 1 is LOWER THAN 2, the previous line is a heading (h2), and since the next element has a LOWER indentation level, this is a paragraph start with a single div.",
            []
          ),
          null
        ),
      ]),
      Heading(2, MarkdownInline("Back to indentation level 1. Next line has the same indentation.", [])),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "Here is another line, right afterwards, with the SAME indentation level (1). This is a special case; read the comment below.",
            []
          ),
          null
        ),
      ]),
    ]);
    expect(parsed).toEqual(expectedAst);

    const expectedHtml = readData("ambiguous_decreasing_indentation_level.html");
    const actualHtml = renderAstToHtml(parsed);
    expect(soupAst(actualHtml)).toEqual(soupAst(expectedHtml));
  });

  it("comments sanity", () => {
    const input = readData("comments_sanity.txt");
    const parsed = parseSpaceupAst(input);
    const expectedAst = Document([
      Heading(1, MarkdownInline("text with 0 indentation", [])),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know.",
            []
          ),
          "hint: the following non-WS, non-comment element's indentation level is LOWER OR EQUAL to this one; therefore, this line is a paragraph open."
        ),
        ParagraphLine(MarkdownInline("another line with more text with 1 indentation.", []), null),
      ]),
    ]);
    expect(parsed).toEqual(expectedAst);

    const expectedHtml = readData("comments_sanity.html");
    const actualHtml = renderAstToHtml(parsed);
    expect(soupAst(actualHtml)).toEqual(soupAst(expectedHtml));
  });

  it("full example", () => {
    const input = readData("full_example.txt");
    const parsed = parseSpaceupAst(input);
    const expectedAst = Document([
      Heading(1, MarkdownInline("text with 0 indentation", [])),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know.",
            []
          ),
          "hint: the following non-WS, non-comment element's indentation level is LOWER OR EQUAL to this one; therefore, this line is a paragraph open."
        ),
        ParagraphLine(MarkdownInline("another line with more text with 1 indentation.", []), null),
      ]),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "even some more text with 1 indentation, preceded by a blank line, and next non-whitespace, non-comment element has indentation LOWER OR EQUAL to this one  --> this is a paragraph open.",
            []
          ),
          null
        ),
      ]),
      Heading(
        2,
        MarkdownInline(
          "here is a new line with 1 indentation, preceded by a blank line, BUT, next non-WS non comment element has a greater indentation level. Therefore, this is a H2.",
          []
        )
      ),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "Some paragraph opener under the H2 heading from before, with an indentation level of 2.",
            []
          ),
          null
        ),
        ParagraphLine(
          MarkdownInline(
            "Lorem ipsum a new div in the same paragraph because no blank line before it and indent level is also 2.",
            []
          ),
          null
        ),
      ]),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "Foo text after a blank line with same indentation (2) as the preceding text; it is another paragraph opener under the H2 from before.",
            []
          ),
          null
        ),
      ]),
      Heading(
        2,
        MarkdownInline(
          "Back to indentation level 1. Note that the next line has a greater indentation than the current one. This necessarily makes this line a heading.",
          []
        )
      ),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "This line has indentation level 2. Because 1 is LOWER THAN 2, the previous line is a heading (h2), and since the next element has a LOWER indentation level, this is a paragraph start with a single div.",
            []
          ),
          null
        ),
      ]),
      Heading(2, MarkdownInline("Back to indentation level 1. Next line has the same indentation.", [])),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "Here is another line, right afterwards, with the SAME indentation level (1). This is a special case; read the comment below.",
            []
          ),
          null
        ),
      ]),
      Comment("This text block is the first example where the two following conditions occur:"),
      Comment("1. indentation went DOWN (previous non-ws non-comment element was 2; now it's 1), and"),
      Comment(
        "2. Two consecutive elements have the same indentation level (1), and going by rules, the first line of this block — 'Back to indentation level 1' — shouldn't be a heading. But we have to make an exception here."
      ),
      Comment(
        "In such an ambiguous, decreased-indentation case, where it's unclear how to parse the first line because the line which follows it shares the same indentation level, the first line is FORCED to become a heading. Subsequent lines in this block are forced to be indented. In effect, this makes this block with exactly the same structure as the one before it; an h2 line, followed by a paragraph starter."
      ),
    ]);
    expect(parsed).toEqual(expectedAst);

    const expectedHtml = readData("full_example.html");
    const actualHtml = renderAstToHtml(parsed);
    expect(soupAst(actualHtml)).toEqual(soupAst(expectedHtml));
  });

  it("markdown features", () => {
    const input = readData("markdown_features.txt");
    const parsed = parseSpaceupAst(input);
    const expectedAst = Document([
      Heading(1, MarkdownInline("My Favorite Recipe", [])),
      Heading(2, MarkdownInline("Ingredients", [])),
      Paragraph([
        ParagraphLine(MarkdownInline("- 2 cups flour", []), null),
        ParagraphLine(MarkdownInline("- 1 cup sugar", []), null),
        ParagraphLine(MarkdownInline("- **1 tsp** baking powder", []), null),
      ]),
      Paragraph([ParagraphLine(MarkdownInline("Mix them well.", []), null)]),
      Heading(2, MarkdownInline("Instructions", [])),
      Paragraph([
        ParagraphLine(MarkdownInline("Preheat oven to 350°F.", []), null),
        ParagraphLine(MarkdownInline("Bake for 20 minutes.", []), null),
      ]),
      Paragraph([ParagraphLine(MarkdownInline("Enjoy your [cake](https://example.com/recipe)!", []), null)]),
    ]);
    expect(parsed).toEqual(expectedAst);

    const expectedHtml = readData("markdown_features.html");
    const actualHtml = renderAstToHtml(parsed);
    expect(soupAst(actualHtml)).toEqual(soupAst(expectedHtml));
  });

  it("markdown features and comments", () => {
    const input = readData("markdown_features_and_comments.txt");
    const parsed = parseSpaceupAst(input);
    const expectedAst = Document([
      Heading(1, MarkdownInline("My Favorite Recipe", [])),
      Heading(2, MarkdownInline("Ingredients", [])),
      Paragraph([
        ParagraphLine(MarkdownInline("- 2 cups flour", []), null),
        ParagraphLine(MarkdownInline("- 1 cup sugar", []), null),
        ParagraphLine(MarkdownInline("- **1 tsp** baking powder", []), null),
      ]),
      Paragraph([
        ParagraphLine(MarkdownInline("Mix them well.", []), "note: whisk thoroughly"),
      ]),
      Heading(2, MarkdownInline("Instructions", [])),
      Paragraph([
        ParagraphLine(MarkdownInline("Preheat oven to 350°F.", []), "oven temperature"),
        ParagraphLine(MarkdownInline("Bake for 20 minutes.", []), null),
      ]),
      Paragraph([
        ParagraphLine(
          MarkdownInline("Enjoy your [cake](https://example.com/recipe)!", []),
          "bon appetit"
        ),
      ]),
    ]);
    expect(parsed).toEqual(expectedAst);

    const expectedHtml = readData("markdown_features_and_comments.html");
    const actualHtml = renderAstToHtml(parsed);
    expect(soupAst(actualHtml)).toEqual(soupAst(expectedHtml));
  });

  it("full example and markdown in paragraphs", () => {
    const input = readData("full_example_and_markdown_in_paragraphs.txt");
    const parsed = parseSpaceupAst(input);
    const expectedAst = Document([
      Heading(1, MarkdownInline("text with 0 indentation", [])),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "text with 1 indentation, with **bold** and a link to [site](https://example.com).",
            []
          ),
          null
        ),
        ParagraphLine(
          MarkdownInline("another line with more text with 1 indentation and some *emphasis*.", []),
          null
        ),
      ]),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "even some more text with 1 indentation, preceded by a blank line, and next non-whitespace, non-comment element has indentation LOWER OR EQUAL to this one  --> this is a paragraph open.",
            []
          ),
          null
        ),
      ]),
      Heading(
        2,
        MarkdownInline(
          "here is a new line with 1 indentation, preceded by a blank line, BUT, next non-WS non comment element has a greater indentation level. Therefore, this is a H2.",
          []
        )
      ),
      Paragraph([
        ParagraphLine(MarkdownInline("- First step: mix ingredients", []), null),
        ParagraphLine(
          MarkdownInline("- Use **butter** and [sugar](https://example.com/sugar)", []),
          null
        ),
      ]),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "Some paragraph opener under the H2 heading from before, with an indentation level of 2, and a link to [docs](https://example.com/docs).",
            []
          ),
          null
        ),
        ParagraphLine(
          MarkdownInline(
            "Lorem ipsum a new div in the same paragraph because no blank line before it and indent level is also 2 with **strong** text.",
            []
          ),
          null
        ),
      ]),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "Foo text after a blank line with same indentation (2) as the preceding text; it is another paragraph opener under the H2 from before with a [link](https://example.com/foo).",
            []
          ),
          null
        ),
      ]),
      Heading(
        2,
        MarkdownInline(
          "Back to indentation level 1. Note that the next line has a greater indentation than the current one. This necessarily makes this line a heading.",
          []
        )
      ),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "This line has indentation level 2. Because 1 is LOWER THAN 2, the previous line is a heading (h2), and since the next element has a LOWER indentation level, this is a paragraph start with a single div.",
            []
          ),
          null
        ),
      ]),
      Heading(
        2,
        MarkdownInline(
          "Back to indentation level 1. Next line has the same indentation with *italic* and a link to [spec](https://example.com/spec).",
          []
        )
      ),
      Paragraph([
        ParagraphLine(
          MarkdownInline(
            "Here is another line, right afterwards, with the SAME indentation level (1). This is a special case; read the comment below.",
            []
          ),
          null
        ),
      ]),
      Comment("This text block is the first example where the two following conditions occur:"),
      Comment("1. indentation went DOWN (previous non-ws non-comment element was 2; now it's 1), and"),
      Comment(
        "2. Two consecutive elements have the same indentation level (1), and going by rules, the first line of this block — 'Back to indentation level 1' — shouldn't be a heading. But we have to make an exception here."
      ),
      Comment(
        "In such an ambiguous, decreased-indentation case, where it's unclear how to parse the first line because the line which follows it shares the same indentation level, the first line is FORCED to become a heading. Subsequent lines in this block are forced to be indented. In effect, this makes this block with exactly the same structure as the one before it; an h2 line, followed by a paragraph starter."
      ),
    ]);
    expect(parsed).toEqual(expectedAst);

    const expectedHtml = readData("full_example_and_markdown_in_paragraphs.html");
    const actualHtml = renderAstToHtml(parsed);
    expect(soupAst(actualHtml)).toEqual(soupAst(expectedHtml));
  });
});