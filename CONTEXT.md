---
last-updated: 2025-08-13
last-commit-at-writing: f5ea521800
---

### Project Genesis and Parsing Strategy

The project, "Spaceup," was defined as a Markdown alternative where document structure (headings, paragraphs) is determined by relative indentation rather than symbols like `#`. The initial discussion established the core parsing rules, including how indentation, blank lines, and `//` comments dictate the hierarchy.

After exploring formal grammars, we concluded that a standard Context-Free Grammar (CFG) was ill-suited due to Spaceup's context-sensitive nature (requiring lookahead and state to track indentation). We decided on a more practical approach: a **hand-written recursive descent parser**. This strategy was chosen for its simplicity and, crucially, its ability to delegate the parsing of standard Markdown features (like bold, lists, and links) to existing, trusted libraries, thereby minimizing implementation effort. An initial Python prototype validated this approach but also highlighted the need for a more robust internal representation to handle complex cases correctly.

### The Shift to AST and a Centralized Language Server (LSP)

To enable powerful static analysis features—a key goal for making Spaceup a usable language—we determined that the parser must produce an **Abstract Syntax Tree (AST)**. This structured representation is a prerequisite for the desired functionalities:
* **Error Highlighting**: Squiggly lines for syntax errors (e.g., invalid indentation).
* **Auto-Formatting**: Automatically correcting indentation.
* **Syntax Highlighting**: Applying colors to different language elements.
* **Intelligent Auto-Indentation**: Smart cursor placement, similar to Python editors.

To avoid duplicating the analysis logic across different editors (VS Code, PyCharm) and platforms (CLI, potential plugins), we decided the core of the project would be a **Language Server Protocol (LSP) server**. This server will act as the single "analysis engine," built in Python, which is your preferred language.

### Dual-Parser Approach: Python for Power, JS for Simplicity

A key concern was providing simple, lightweight syntax highlighting for web browsers (e.g., via a CDN script) without the overhead of the full LSP or a Python runtime. We settled on a pragmatic, two-pronged approach:

1.  **Python-based AST and LSP (The Core Engine)**: The primary implementation will be in Python. This includes the full parser that generates a detailed AST and the LSP server that provides all advanced static analysis features.
2.  **Lightweight JavaScript Library (For Browsers)**: A separate, minimal, pure-JS parser will be created for simple browser use cases. This library will focus solely on basic syntax highlighting and will not initially build a full AST, ensuring it remains small and fast. It is completely independent of the LSP.

This strategy allows for both a feature-rich editing experience in IDEs and a simple, performant solution for web pages, while keeping the development efforts for each use case separate and manageable.

### Selecting the Right Markdown Library for AST Integration

The final decision point was choosing a Python library to parse the Markdown content within Spaceup paragraphs. The goal was to find a library that could provide a Markdown AST (or a token stream) that could be embedded directly into the main Spaceup AST. This avoids the need to define custom AST nodes for Markdown features like `Bold` or `OrderedList`.

To minimize the friction of a potential future port to JavaScript, the chosen library needed a direct, API-compatible counterpart in the JS ecosystem.

After evaluating alternatives, **`markdown-it-py`** was selected as the ideal tool.
* It provides a **token stream** that can be directly embedded into the Spaceup AST nodes.
* It has an **identical JavaScript twin, `markdown-it`**, which will make a future JS implementation of the parser a straightforward translation.

This choice perfectly aligns with the project's core principle of reusing existing tools and planning for cross-language consistency to curb redundant effort.

---


### Decision-making Framework

A few core principles designed to maximize progress for a solo developer on a side project

* **Conservative, High-Impact Prioritization:** Every decision is weighed against a framework of **"high impact x sensible to do now x low effort as a tie-breaker."** This ensures that work is focused and avoids premature optimization or overly ambitious features.
* **Aggressive Effort Deduplication:** A central tenet is to **"collapse branches"** of potential work by finding the one effort that would serve multiple purposes, thus avoiding having to do one thing in multiple ways. This applies both to building things and to broader strategic decisions. This is a conscious strategy to curb the "combinatorial explosion" of tasks and avoid having to do something over and over in small variations.
* **Leverage Proven Tools:** A strong preference was shown for learning from and **reusing trusted, existing libraries** (like established Markdown parsers) rather than reinventing the wheel. This lowers the implementation burden and builds on battle-tested solutions.
* **Plan for Future Portability:** Decisions are made with an eye toward minimizing the friction of future reimplementations in other languages (specifically JavaScript). This involves choosing tools and designing structures (like the AST) that have clear, API-compatible counterparts in other ecosystems.

Decisions in line with this framework:
- delegating all in-paragraph Markdown parsing to an existing library.
- writing an AST+LSP in Python, which is language-agnostic. An example of "collapsing branches." Instead of creating separate plugins for VS Code, PyCharm, a CLI, etc., one LSP server is built to "serve them all widely," embodying the principle of aggressive effort deduplication.
- when time comes, we'll render Spaceup by converting to HTML first, then render the HTML, thus avoiding the sprawling rabbit hole of trying to render Spaceup directly.
- A Pragmatic Dual-Parser Approach for Python and JS: A two-pronged strategy was chosen: implementing the feature-rich AST + LSP server in Python, treating it as the core engine, and having a separate minimal pure JavaScript library for the browser client, despite the on-paper duplication.
- Chosen `markdown-it-py` to build the Python AST, because it plans for future portability. `markdown-it-py` has an identical JavaScript counterpart (`markdown-it`), which makes a future port of the parser a simple translation, once again **deduplicating effort** across the project's lifecycle.

