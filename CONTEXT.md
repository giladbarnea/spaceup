---
last-updated: 2025-08-16
last-commit-at-writing: f5ea521800
---

### Project Genesis and Parsing Strategy

Spaceup is a Markdown alternative where **document structure** (headings, paragraphs) is determined by **relative indentation**, not symbols like `#`. Blank lines and `//` comments participate in the hierarchy rules.

We explored formal grammars and found a vanilla CFG ill-suited because Spaceup’s indentation requires look-ahead and state. We therefore adopted a **hand-written recursive-descent approach**.

Spaceup intentionally has **two** parsing implementations that accept the same language and must produce the **same HTML**:

- **Lightweight Parser (`parser.py`)** — a practical, manual parser (recursive descent with string/regex matching). This is the basis for tiny/browser use cases (e.g., syntax highlighting with Prism/Highlight.js via a CDN). It does **not** build a full AST.
- **AST Parser (`ast_parser.py`)** — a robust, AST-first implementation that underpins advanced tooling (LSP, formatting, diagnostics, preview, etc.).

Both parsers are language-identical and must round-trip to **the same HTML**.

### Markdown Inside Spaceup Paragraphs

We reuse proven Markdown tooling for inline/block features **inside paragraphs** rather than reinventing them.

- In the **lightweight parser**, we use **mistune** for inline Markdown.
- In the **AST parser**, we use **`markdown-it-py`**, whose token stream is embedded directly into Spaceup AST nodes. Its JavaScript twin (**`markdown-it`**) keeps future parity straightforward.

**Unsupported on purpose (to avoid ambiguity with Spaceup’s indentation semantics):**
- `#`-style Markdown headings are **not recognized** by Spaceup.
- **Indented code blocks** (the old 4-space style) are **not recognized**.
(Use fenced code blocks in Markdown segments if/when needed; structure still comes from Spaceup indentation.)

### AST, LSP, and the Editing Experience

To enable serious editor features, the AST parser produces a structured **AST** consumed by a **Language Server Protocol (LSP)** server (Python, likely via `pygls`). The LSP is the single “analysis engine” used by VS Code, PyCharm, a CLI, and other clients.

Planned capabilities (AST/LSP-driven):
- **Diagnostics**: syntax errors with squigglies (e.g., invalid indentation).
- **Formatting**: canonical indentation and **application of “forced indents”** where the parser disambiguates.
- **Syntax Highlighting** and **Auto-Indent on Enter**.
- **Autocomplete** and **intelligent cursor motions** where applicable.
- **Preview/Rendering** similar to Markdown preview.
- **Plugin hooks** for common linters/formatters in both ecosystems.

### Browser Support (Tiny JS)

For web pages, we’ll ship a **small, pure-JS library** that mirrors the **lightweight parser** to power simple highlighting (non-AST) from a CDN. It’s independent of the LSP. A future bridge to advanced features is optional.

### Converters and Output Strategy

Spaceup is converted to **HTML** first. HTML is the intermediate representation we rely on for rendering and for further conversions (e.g., to Markdown/other formats) as needed. Rendering HTML is a solved problem.

### Decision-Making Framework

Principles optimized for solo, part-time development:

- **Conservative, High-Impact Prioritization**: Do the high-impact thing that’s sensible now; break ties by low effort.
- **Aggressive Effort Deduplication**: Collapse branches—build one thing that serves many surfaces (e.g., one LSP feeds many editors).
- **Leverage Proven Tools**: Reuse trusted Markdown parsers (mistune, markdown-it-py/markdown-it).
- **Plan for Portability**: Maintain a shared AST spec to make a future JS port low-friction.

Examples:
- Delegate all in-paragraph Markdown parsing to existing libraries.
- Keep Python as the **source of truth** for CLI, server, and LSP.
- Two parsers, one language: lightweight for browsers; AST for tooling—same HTML result.
- Convert Spaceup → HTML, then go anywhere.

### Shared Specification & Tests

To guarantee parity and portability:
- A **shared AST spec** (documented shapes/types).
- **Common fixtures**: input Spaceup → expected AST (JSON) → expected HTML.
- Cross-runner tests to keep Python and future JS implementations aligned.

### Distribution & Tooling

- **Python**: package and publish on **PyPI**; CLI and LSP server live here.
- **JavaScript**: package on **npm**; ship a **CDN** build for the lightweight browser parser.
- Editor clients (e.g., VS Code) are thin wrappers over the LSP.

### Development

- Package management and executables use **[uv](https://docs.astral.sh/uv/)** (not pip/poetry/venv).
- Run tests via `./test.sh`, a wrapper for `uv run pytest tests` (supports normal pytest args like `-x` or `-k "keyword").
- Python **3.13**; use modern features tastefully.

## Roadmap

> Order of operations; no dates. Each step should keep HTML parity between parsers and advance shared test coverage.

1. **Spec & Fixtures**
   - Finalize the **shared AST spec** and publish JSON/HTML fixtures.

2. **Core Engine (Python)**
   - Implement/solidify **AST parser** and **LSP** (diagnostics, formatting incl. forced indents, highlighting, auto-indent, autocomplete, preview).
   - Ship **CLI** and **server** surfaces that use the same core.

3. **Lightweight Parser Parity**
   - Ensure the **lightweight parser** matches language semantics and **emits identical HTML** to the AST path.

4. **Editors**
   - VS Code extension (standard LSP client); add PyCharm/others as needed.

5. **Browser Library**
   - Publish the **tiny JS parser** (non-AST) for highlighting; integrate easily with Prism/Highlight.js; CDN build.

6. **Shared Tests Across Runtimes**
   - Reuse fixtures to validate Python and JS builds against the same inputs/outputs.

7. **Converters & Packaging**
   - Treat **Spaceup → HTML** as canonical; add ancillary conversions from HTML as needed.
   - Publish to **PyPI**/**npm**/**CDN**.

8. **Optional**
   - Explore a **JS LSP** port (e.g., `vscode-languageserver-node`) if demand warrants; reuse AST spec and fixtures.