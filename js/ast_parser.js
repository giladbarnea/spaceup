"use strict";

const MarkdownIt = require("markdown-it");
const md = new MarkdownIt();

function MarkdownInline(text, tokens) {
  return { text, tokens: tokens || [] };
}

function ParagraphLine(content, inline_comment) {
  return { content, inline_comment: inline_comment ?? null };
}

function Paragraph(lines) {
  return { lines };
}

function Heading(level, content) {
  return { level, content };
}

function Comment(text) {
  return { text };
}

function Document(children) {
  return { children };
}

function parseSpaceupAst(inputStr) {
  const lines = inputStr.split(/\r?\n/).map((line) => line.replace(/\s+$/, ""));

  function computeIndent(line) {
    const stripped = line.replace(/^\s+/, "");
    if (stripped === "" || stripped.startsWith("//")) {
      return null;
    }
    return line.length - stripped.length;
  }

  function nextNonWsIndent(idx) {
    for (let i = idx + 1; i < lines.length; i += 1) {
      const ind = computeIndent(lines[i]);
      if (ind !== null) {
        return ind;
      }
    }
    return -1;
  }

  function splitContentAndInlineComment(text) {
    const stripped = text.replace(/^\s+/, "");
    let searchStart = 0;
    while (true) {
      const pos = stripped.indexOf("//", searchStart);
      if (pos === -1) break;
      if (pos === 0) {
        searchStart = pos + 2;
        continue;
      }
      const before = stripped.charAt(pos - 1);
      if (/\s/.test(before)) {
        const content = stripped.slice(0, pos).replace(/\s+$/, "");
        const comment = stripped.slice(pos + 2).trim();
        return [content, comment.length ? comment : null];
      }
      searchStart = pos + 2;
    }
    return [stripped.trim(), null];
  }

  const children = [];
  const indentStack = [0];
  let pos = 0;
  let previousNonWsIndent = 0;

  function parseBlock(currentIndent) {
    while (pos < lines.length) {
      while (pos < lines.length) {
        const stripped = lines[pos].replace(/^\s+/, "");
        if (stripped === "") {
          pos += 1;
          continue;
        }
        if (stripped.startsWith("//")) {
          const commentText = stripped.slice(2).trim();
          if (commentText) {
            children.push(Comment(commentText));
          }
          pos += 1;
          continue;
        }
        break;
      }

      if (pos >= lines.length) return;

      const line = lines[pos];
      const indent = computeIndent(line);
      if (indent === null) {
        pos += 1;
        continue;
      }
      if (indent < currentIndent) {
        return;
      }

      const [contentText, inlineComment] = splitContentAndInlineComment(line);
      if (contentText === "") {
        pos += 1;
        continue;
      }

      const nxtIndent = nextNonWsIndent(pos);

      let hasBlankBeforeNext = false;
      for (let i = pos + 1; i < lines.length; i += 1) {
        if (computeIndent(lines[i]) !== null) {
          break;
        }
        if (lines[i].trim()) {
          hasBlankBeforeNext = true;
        }
      }

      const ambiguousDecrease = previousNonWsIndent > indent && nxtIndent === indent && !hasBlankBeforeNext;
      let isHeading = false;
      if (nxtIndent > indent || (nxtIndent === indent && hasBlankBeforeNext) || ambiguousDecrease) {
        isHeading = true;
      }

      const headingLevel = indentStack.length;
      if (isHeading) {
        children.push(Heading(headingLevel, MarkdownInline(contentText, [])));
        previousNonWsIndent = indent;
        indentStack.push(indent);
        pos += 1;

        if (ambiguousDecrease) {
          const linesAccum = [];
          while (pos < lines.length) {
            const nindent = computeIndent(lines[pos]);
            if (nindent === null || nindent !== indent) break;
            const [ncontent, ncomment] = splitContentAndInlineComment(lines[pos]);
            if (ncontent) {
              linesAccum.push(ParagraphLine(MarkdownInline(ncontent, []), ncomment));
              previousNonWsIndent = indent;
            }
            pos += 1;
          }
          if (linesAccum.length) {
            children.push(Paragraph(linesAccum));
          }
        }

        parseBlock(indent + 1);
        indentStack.pop();
      } else {
        const linesAccum = [ParagraphLine(MarkdownInline(contentText, []), inlineComment)];
        pos += 1;
        while (pos < lines.length) {
          const nindent = computeIndent(lines[pos]);
          if (nindent !== indent) break;
          const [ncontent, ncomment] = splitContentAndInlineComment(lines[pos]);
          if (ncontent) {
            linesAccum.push(ParagraphLine(MarkdownInline(ncontent, []), ncomment));
            previousNonWsIndent = indent;
          }
          pos += 1;
        }
        children.push(Paragraph(linesAccum));
        previousNonWsIndent = indent;
      }
    }
  }

  parseBlock(0);
  return Document(children);
}

function renderAstToHtml(ast) {
  function renderInlineMd(text) {
    return md.renderInline(text).trim();
  }

  const output = [];

  for (const node of ast.children) {
    if (node && typeof node.level === "number" && node.content) {
      const rendered = renderInlineMd(node.content.text);
      output.push(`<h${node.level}>${rendered}</h${node.level}>`);
    } else if (node && Array.isArray(node.lines)) {
      if (node.lines.length > 0 && node.lines.every((line) => line.content.text.replace(/^\s+/, "").startsWith("- "))) {
        output.push("<ul>");
        for (const line of node.lines) {
          const itemText = line.content.text.replace(/^\s+/, "").slice(2).trim();
          output.push(`    <li>${renderInlineMd(itemText)}</li>`);
        }
        output.push("</ul>");
        continue;
      }

      output.push("<p>");
      for (const line of node.lines) {
        const rendered = renderInlineMd(line.content.text);
        if (line.inline_comment) {
          output.push(`    ${rendered}  <!-- ${line.inline_comment} --><br>`);
        } else {
          output.push(`    ${rendered}<br>`);
        }
      }
      output.push("</p>");
    } else if (node && typeof node.text === "string") {
      if (node.text) {
        output.push(`<!-- ${node.text} -->`);
      }
    }
  }

  return output.join("\n");
}

module.exports = {
  // factories
  Document,
  Heading,
  Paragraph,
  MarkdownInline,
  ParagraphLine,
  Comment,
  // api
  parseSpaceupAst,
  renderAstToHtml,
};