---
title: Integrations
description: This document lists every technology that consumes Markdown, which Spaceup plans to integrate with. The list is grouped by environment (Browser, Node.js, Python). Within each environment, integrations are further grouped by the expected language definition format. Ultimately, bespoke adaptors will be written for each integration.
---

# Browser

## Full-Featured Code Editors (All features: highlighting, autocomplete, error squiggles, formatting)

### 1. Monaco Editor
- What it is: The code editor that powers VS Code
- Features: Syntax highlighting, IntelliSense/autocomplete, error markers, code formatting, code folding, find/replace
- Popularity: Very high (Microsoft-backed, enterprise adoption) — ⭐ 43.6k
- Language Interface: Language services via TypeScript-like interfaces

### 2. CodeMirror 6 
- What it is: Modern, modular code editor
- Features: Syntax highlighting, autocomplete, linting/error display, formatting, extensive plugin system
- Popularity: Very high (used by GitHub, Observable, etc.) — ⭐ 6.9k
- Language Interface: Lezer parser system + language packages

## Syntax Highlighting Only

### 3. Highlight.js
- What it is: Automatic syntax highlighting
- Features: Only syntax highlighting, 190+ languages, theme support
- Popularity: Very high — ⭐ 24.5k
- Language Interface: Simple grammar definitions

### 4. Prism.js
- What it is: Lightweight syntax highlighter
- Features: Syntax highlighting, plugins for line numbers/copy button
- Popularity: Very high — ⭐ 53.7k
- Language Interface: Grammar-based language definitions

### 5. Shiki
- What it is: Syntax highlighter using VS Code themes/grammars
- Features: High-fidelity syntax highlighting, VS Code theme compatibility
- Popularity: High — ⭐ 12.0k
- Language Interface: TextMate/VS Code grammar format

## Rich Text Editors with Code Support

### 6. CKEditor 5
- What it is: Rich text editor with code block support
- Features: Rich text editing, code block highlighting, collaborative editing
- Popularity: High (enterprise WYSIWYG standard) — ⭐ 10.2k
- Language Interface: Plugin-based code block languages

### 7. TinyMCE
- What it is: Rich text editor with code highlighting plugins
- Features: Rich text editing, code highlighting via plugins
- Popularity: High (enterprise adoption) — ⭐ 15.8k
- Language Interface: Plugin-based integration with highlight.js/Prism

## Specialized/Emerging

### 8. Starry-Night (by GitHub/Wooorm)
- What it is: GitHub's syntax highlighter
- Features: Syntax highlighting, uses TextMate grammars
- Popularity: Moderate but growing — ⭐ 1.6k
- Language Interface: TextMate grammar format

### 9. LDT (Lightweight Decorator for Textareas)
- What it is: Minimalist syntax highlighting overlay
- Features: Live syntax highlighting for textareas
- Popularity: Moderate (niche but solid) — ⭐ 160
- Language Interface: Simple pattern-based

## Summary by Capability

| Library       | Highlighting | Autocomplete | Error Squiggles | Formatting |
| ------------- | ------------ | ------------ | --------------- | ---------- |
| Monaco Editor | ✅            | ✅            | ✅               | ✅          |
| CodeMirror 6  | ✅            | ✅            | ✅               | ✅          |
| Highlight.js  | ✅            | ❌            | ❌               | ❌          |
| Prism.js      | ✅            | ❌            | ❌               | ❌          |
| Shiki         | ✅            | ❌            | ❌               | ❌          |
| CKEditor 5    | ✅*           | ❌            | ❌               | ❌          |
| TinyMCE       | ✅*           | ❌            | ❌               | ❌          |
| Starry-Night  | ✅            | ❌            | ❌               | ❌          |

*Code blocks only, not full documents

## LSP vs. Non-LSP Libraries

### Libraries That CAN Use LSP (but don't require it):

#### 1. Monaco Editor
- LSP Support: ✅ Yes, via `monaco-languageclient`
- Default: Uses built-in language services (TypeScript-like interfaces)
- What it consumes without LSP: Language configuration JSON + tokenization rules
- ⭐ 1.2k (monaco-languageclient)

#### 2. CodeMirror 6 
- LSP Support: ✅ Yes, via community extensions
- Default: Uses Lezer parser system
- What it consumes without LSP: Lezer grammar files + language packages
- ⭐ 6.9k

### Libraries That DON'T Use LSP:

#### 3. Highlight.js
- LSP Support: ❌ No
- What it consumes: JavaScript language definition objects with regex patterns
- ⭐ 24.5k

#### 4. Prism.js
- LSP Support: ❌ No  
- What it consumes: JavaScript grammar objects with token definitions
- ⭐ 53.7k

#### 5. Shiki
- LSP Support: ❌ No
- What it consumes: TextMate grammar files (.tmLanguage.json)
- ⭐ 12.0k

#### 6. CKEditor 5 / TinyMCE
- LSP Support: ❌ No
- What they consume: Plugin-based integration with other highlighters
- ⭐ 10.2k (CKEditor 5)
- ⭐ 15.8k (TinyMCE)

#### 7. Starry-Night
- LSP Support: ❌ No
- What it consumes: TextMate grammar files
- ⭐ 1.6k

## What Non-LSP Libraries Actually Consume

### Format Categories:

#### 1. Regex-Based Language Definitions
Libraries: Highlight.js, Microlight.js
```javascript
// Highlight.js format
{
  keywords: 'function var let const',
  contains: [
    { className: 'string', begin: '"', end: '"' },
    { className: 'comment', begin: '//', end: '$' }
  ]
}
```

#### 2. Token-Based Grammars 
Libraries: Prism.js
```javascript
// Prism.js format
{
  'keyword': /\b(?:function|var|let|const)\b/,
  'string': /"(?:[^"\\]|\\.)*"/,
  'comment': /\/\/.*$/m
}
```

#### 3. TextMate Grammars
Libraries: Shiki, Starry-Night, Monaco Editor (optional), VS Code
```json
{
  "scopeName": "source.spaceup",
  "patterns": [
    {
      "name": "keyword.control.spaceup", 
      "match": "\\b(function|var)\\b"
    }
  ]
}
```

#### 4. Parser-Based Systems
Libraries: CodeMirror 6 (Lezer), Tree-sitter
```javascript
// Lezer grammar (simplified)
@top Program { statement* }
statement { FunctionDecl | VarDecl }
FunctionDecl { "function" identifier "(" ")" Block }
```

## Is There Agreement on Format?

### Answer: NO - But There Are Clusters

#### Most Common Formats:

1. TextMate Grammars (~30% of libraries)
   - Used by: Shiki, Starry-Night, Monaco Editor, VS Code
   - Format: JSON-based scope/pattern definitions
   - Most standardized option

2. Regex/Token Objects (~40% of libraries)  
   - Used by: Highlight.js, Prism.js, Microlight.js
   - Format: JavaScript objects with regex patterns
   - Each has slight variations

3. Parser Systems (~20% of libraries)
   - Used by: CodeMirror 6, Tree-sitter
   - Format: Custom grammar languages
   - Completely different approaches

4. LSP Integration (~10% of libraries)
   - Used by: Monaco Editor, CodeMirror 6 (optional)
   - Format: Language Server Protocol
   - Standardized but limited adoption

---

# Editors (as plugins)

- VS Code
- JetBrains IDEs

---

# Formatters and Linters

## Node.js

### Linting

#### markdownlint
- What it is: Popular Markdown style checker/linter (CLI + Node API)
- Capabilities: Linting, configurable rulesets, JSON output, CI-friendly
- Spaceup integration: Emit Markdown from Spaceup AST (or `mdast`) → run markdownlint → map findings to LSP diagnostics
- ⭐ 5.4k

#### remark-lint (Unified/remark)
- What it is: Linting via remark plugins in the Unified ecosystem
- Capabilities: Extensive rule packs, custom rules, `vfile` messages; works with GFM/frontmatter
- Spaceup integration: Adapt Spaceup AST → `mdast` → run remark + remark-lint → surface diagnostics
- ⭐ 991 (remark-lint)
- ⭐ 1.3k (vfile)

#### textlint
- What it is: Pluggable text/Markdown/HTML linter for prose and style
- Capabilities: Grammar/style rules, custom rule authoring, JSON output
- Spaceup integration: Feed paragraph text (via Markdown emission) to textlint; merge messages into diagnostics
- ⭐ 3.0k

### Formatting

#### Prettier (Markdown)
- What it is: Opinionated formatter with first-class Markdown support
- Capabilities: Canonical formatting for Markdown content and code fences
- Spaceup integration: Emit Markdown from Spaceup AST → Prettier → (optionally) compare/apply formatting suggestions
- ⭐ 50.8k

#### remark + remark-stringify
- What it is: Unified pipeline that can normalize Markdown on stringify
- Capabilities: Structural normalization and consistent spacing via options/plugins
- Spaceup integration: Produce `mdast` from Spaceup AST → stringify with desired options
- ⭐ 8.4k (remark)

#### mdsf
- What it is: Formats fenced code blocks inside Markdown using your configured code formatters
- Capabilities: Keeps embedded code consistent with project formatters
- Spaceup integration: After emitting Markdown, run `mdsf` to format code blocks
- ⭐ 84

### Server-Side Syntax Highlighting

#### Unified + rehype-highlight
- What it is: Markdown → HTML pipeline with server-side code block highlighting
- Capabilities: Highlighting during HTML generation; themeable via highlight.js grammars
- Spaceup integration: Emit Markdown/`mdast` → `remark-rehype` → `rehype-highlight` → HTML
- ⭐ 311 (rehype-highlight)

#### Shiki
- What it is: High-fidelity, VS Code grammar/theme based highlighter (Node runtime)
- Capabilities: Deterministic, theme-accurate highlighting for fenced code blocks
- Spaceup integration: Walk Spaceup AST for code blocks → call Shiki → inject highlighted HTML
- ⭐ 12.0k

### Autocomplete & Error Squiggles (LSP/Services)

#### prosemd-lsp
- What it is: Proofreading/linting Language Server for Markdown
- Capabilities: Diagnostics (error squiggles), style hints, some completions via LSP
- Spaceup integration: Optionally run alongside Spaceup LSP; or ingest its diagnostics for prose/style
- ⭐ 1.3k

#### vscode-markdown-languageservice
- What it is: Embeddable services powering VS Code’s Markdown features
- Capabilities: Link/reference completions, diagnostics, folding, workspace features
- Spaceup integration: Use as a library where helpful; or replicate needed features on Spaceup AST
- ⭐ 425

## Python

### Linting

#### PyMarkdown (pymarkdown)
- What it is: Markdown linter with a comprehensive rule set (CLI and library)
- Capabilities: Style/correctness checks, configurable rules, JSON output
- Spaceup integration: Emit Markdown from Spaceup AST → run pymarkdown → convert results to diagnostics
- ⭐ 861

#### proselint
- What it is: Prose/style linter for English text
- Capabilities: Grammar/style suggestions for natural language inside documents
- Spaceup integration: Feed paragraph text to proselint; surface messages as informational diagnostics
- ⭐ 4.2k

### Formatting

#### mdformat
- What it is: CommonMark-compliant Markdown formatter (built on markdown-it-py)
- Capabilities: Consistent Markdown formatting; plugin ecosystem (e.g., GFM)
- Spaceup integration: Emit Markdown from Spaceup AST → run mdformat → apply or preview changes
- ⭐ 613

### Server-Side Syntax Highlighting

#### Pygments
- What it is: Mature syntax highlighter for many languages (Python library)
- Capabilities: Highlighting for fenced code blocks during HTML generation
- Spaceup integration: Write a dedicated Lexer.
- ⭐ 1.8k

#### Rich
- What it is: Python library for rich text and console output with terminal colors and styles
- Capabilities: Rich text formatting, terminal colors, styles, and more
- Spaceup integration: Write a dedicated Theme and feed Pygments Lexer.
- ⭐ 53.3k

#### markdown-it-py / mistune (with custom highlighter)
- What it is: Markdown parsers that can delegate code block highlighting to Pygments
- Capabilities: Inline Markdown parsing (already used by Spaceup) plus hookable highlighting
- Spaceup integration: Reuse existing markdown-it-py usage; attach a Pygments-based highlighter for code fences
- ⭐ 932 (markdown-it-py)
- ⭐ 2.8k (mistune)

### Autocomplete & Error Squiggles

- LSP wiring via Spaceup core
  - Approach: Use linter outputs (pymarkdown/proselint) to produce LSP diagnostics; offer completions based on Spaceup AST (links, refs) and optionally reuse external services

## Cross-Platform / CLI Tools

#### Vale
- What it is: Syntax-aware prose/style linter that works well with Markdown
- Capabilities: Consistent editorial style enforcement; customizable rule sets
- Spaceup integration: Run on Markdown emitted from Spaceup AST; merge diagnostics
- ⭐ 4.9k

Notes
- In all cases, Spaceup can adapt its AST to the format each tool expects (Markdown string or `mdast`)
- Diagnostics and suggestions from these tools can be surfaced through the Spaceup LSP to provide highlighting, linting, autocomplete, error squiggles, and formatting experiences in editors

---

# Server-Side Runtime Markdown Libraries

## Node.js

### commonmark.js
- What it is: Official JavaScript reference implementation of the CommonMark spec
- Capabilities: Parses to AST and renders HTML/XML; strict spec compliance; predictable positions
- Spaceup integration: Use when strict CommonMark behavior is required or for baseline tests; less extensible than plugin ecosystems
- ⭐ 1.5k

### markdown-it
- What it is: Modern, pluggable CommonMark parser for Node.js
- Capabilities: Fast; rich plugin ecosystem (attrs, anchor, footnote, emoji, containers); token stream with positions; custom renderers; GFM via plugins
- Spaceup integration: Node twin of `markdown-it-py` for parity; parse Markdown segments inside Spaceup paragraphs → HTML or token stream; reuse the same plugin set across runtimes
- ⭐ 20.1k

### remark (Unified)
- What it is: Plugin-based Markdown processor (`remark-parse` → `mdast` → `remark-rehype` → HTML)
- Capabilities: Deep transform pipelines on `mdast`, GFM support, frontmatter, interop with `rehype` (HTML) and broader Unified ecosystem
- Spaceup integration: Convert Spaceup AST → `mdast` or Markdown → run remark pipeline (incl. rehype) → HTML; ideal when structural transforms are desired
- ⭐ 8.4k (remark)
- ⭐ 4.8k (unified)
- ⭐ 1.3k (mdast)

### micromark
- What it is: Low-level CommonMark tokenizer underlying remark/unified
- Capabilities: Concrete tokens with precise positions, extension system for syntax additions, strict compliance
- Spaceup integration: Use where exact token boundaries/positions are needed for LSP features on embedded Markdown; higher effort than high-level parsers
- ⭐ 2.0k

### marked
- What it is: High-performance Markdown parser with GFM support
- Capabilities: Very fast parsing/rendering, simple API, broad adoption
- Spaceup integration: Lightweight option to render embedded Markdown to HTML when minimal dependencies and speed are the priority
- ⭐ 35.3k

## Python

### commonmark.py: deprecated. Won't integrate.
- What it is: Pure Python port of `commonmark.js` adhering to the CommonMark spec (now deprecated)

### paka.cmark
- What it is: Python bindings to the C reference implementation `cmark`
- Capabilities: Fast and strictly compliant; multiple outputs (HTML, XML, CommonMark, man, LaTeX)
- Spaceup integration: Option when strict compliance/performance is critical and C bindings are acceptable in the deployment environment
- ⭐ 72

### mistletoe
- What it is: Pure Python, CommonMark-compliant Markdown parser
- Capabilities: Extensible architecture; supports alternative renderers (e.g., LaTeX); easy installation (no C deps)
- Spaceup integration: Pure-Python CommonMark option when plugin parity with `markdown-it(-py)` isn’t needed
- ⭐ 955

### markdown-it-py
- What it is: Python port of `markdown-it`
- Capabilities: CommonMark-compliant; token stream with positions; ecosystem via `mdit-py-plugins` (tables, anchors, attrs, footnotes, etc.)
- Spaceup integration: Already used by the AST parser; embed token streams in Spaceup AST nodes for editor features; align plugins with Node’s `markdown-it` for cross-runtime parity
- ⭐ 932

### Mistune
- What it is: Fast, extensible Python Markdown parser
- Capabilities: Pluggable architecture, custom renderers, GFM features, easy server-side HTML generation
- Spaceup integration: Used by the lightweight parser; good default for quick server rendering of Markdown segments
- ⭐ 2.8k

### Python-Markdown
- What it is: Mature, widely-used Markdown implementation with an extension system
- Capabilities: Stable API, extensive plugins; pairs well with `pymdown-extensions`
- Spaceup integration: Alternative runtime for rendering emitted Markdown; leverage extension ecosystem where needed
- ⭐ 4.1k

### markdown2
- What it is: Simple, fast Markdown implementation with optional "extras" (e.g., metadata, footnotes)
- Capabilities: Speed and simplicity; toggle features via extras
- Spaceup integration: Minimal-dependency renderer for embedded Markdown when advanced plugins aren’t required
- ⭐ 2.8k

### Notable Extension Packs
- `mdit-py-plugins` (Python): Official/curated plugins for `markdown-it-py` (tables, anchors, attrs, task lists, etc.)
- `pymdown-extensions` (Python): Large extension suite for `Python-Markdown` (e.g., superfences, task lists, tabbed blocks, details)
- Spaceup integration: Choose a consistent plugin set per runtime to keep behavior aligned across Node and Python
- ⭐ 34 (mdit-py-plugins)
- ⭐ 1.2k (pymdown-extensions)

---

Note: this article lists many Markdown parsers which aren't here: https://medium.com/@stereobooster/markdown-parsers-ab83dbb5f5c8