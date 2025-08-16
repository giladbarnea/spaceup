---
title: Integrations
description: This document lists all planned integrations with Spaceup, grouped by environment (Browser, Node.js, Python). Within each environment, integrations are further grouped by the expected language definition format. Ultimately, bespoke adaptors will be written for each integration.
---

# Browser

## Full-Featured Code Editors (All features: highlighting, autocomplete, error squiggles, formatting)

### 1. Monaco Editor
- What it is: The code editor that powers VS Code
- Features: Syntax highlighting, IntelliSense/autocomplete, error markers, code formatting, code folding, find/replace
- Popularity: Very high (Microsoft-backed, enterprise adoption)
- Language Interface: Language services via TypeScript-like interfaces

### 2. CodeMirror 6 
- What it is: Modern, modular code editor
- Features: Syntax highlighting, autocomplete, linting/error display, formatting, extensive plugin system
- Popularity: Very high (used by GitHub, Observable, etc.)
- Language Interface: Lezer parser system + language packages

## Syntax Highlighting Only

### 3. Highlight.js
- What it is: Automatic syntax highlighting
- Features: Only syntax highlighting, 190+ languages, theme support
- Popularity: Very high (~23k GitHub stars)
- Language Interface: Simple grammar definitions

### 4. Prism.js
- What it is: Lightweight syntax highlighter
- Features: Syntax highlighting, plugins for line numbers/copy button
- Popularity: Very high (~12k GitHub stars)
- Language Interface: Grammar-based language definitions

### 5. Shiki
- What it is: Syntax highlighter using VS Code themes/grammars
- Features: High-fidelity syntax highlighting, VS Code theme compatibility
- Popularity: High (~9k GitHub stars, growing rapidly)
- Language Interface: TextMate/VS Code grammar format

## Rich Text Editors with Code Support

### 6. CKEditor 5
- What it is: Rich text editor with code block support
- Features: Rich text editing, code block highlighting, collaborative editing
- Popularity: High (enterprise WYSIWYG standard)
- Language Interface: Plugin-based code block languages

### 7. TinyMCE
- What it is: Rich text editor with code highlighting plugins
- Features: Rich text editing, code highlighting via plugins
- Popularity: High (enterprise adoption)
- Language Interface: Plugin-based integration with highlight.js/Prism

## Specialized/Emerging

### 8. Starry-Night (by GitHub/Wooorm)
- What it is: GitHub's syntax highlighter
- Features: Syntax highlighting, uses TextMate grammars
- Popularity: Moderate but growing (~3k GitHub stars)
- Language Interface: TextMate grammar format

### 9. LDT (Lightweight Decorator for Textareas)
- What it is: Minimalist syntax highlighting overlay
- Features: Live syntax highlighting for textareas
- Popularity: Moderate (niche but solid)
- Language Interface: Simple pattern-based

## Summary by Capability

| Library | Highlighting | Autocomplete | Error Squiggles | Formatting | Popularity |
|---------|-------------|-------------|----------------|------------|------------|
| Monaco Editor | ✅ | ✅ | ✅ | ✅ | Very High |
| CodeMirror 6 | ✅ | ✅ | ✅ | ✅ | Very High |
| Highlight.js | ✅ | ❌ | ❌ | ❌ | Very High |
| Prism.js | ✅ | ❌ | ❌ | ❌ | Very High |
| Shiki | ✅ | ❌ | ❌ | ❌ | High |
| CKEditor 5 | ✅* | ❌ | ❌ | ❌ | High |
| TinyMCE | ✅* | ❌ | ❌ | ❌ | High |
| Starry-Night | ✅ | ❌ | ❌ | ❌ | Moderate |

*Code blocks only, not full documents

## LSP vs. Non-LSP Libraries

### Libraries That CAN Use LSP (but don't require it):

#### 1. Monaco Editor
- LSP Support: ✅ Yes, via `monaco-languageclient`
- Default: Uses built-in language services (TypeScript-like interfaces)
- What it consumes without LSP: Language configuration JSON + tokenization rules

#### 2. CodeMirror 6 
- LSP Support: ✅ Yes, via community extensions
- Default: Uses Lezer parser system
- What it consumes without LSP: Lezer grammar files + language packages

### Libraries That DON'T Use LSP:

#### 3. Highlight.js
- LSP Support: ❌ No
- What it consumes: JavaScript language definition objects with regex patterns

#### 4. Prism.js
- LSP Support: ❌ No  
- What it consumes: JavaScript grammar objects with token definitions

#### 5. Shiki
- LSP Support: ❌ No
- What it consumes: TextMate grammar files (.tmLanguage.json)

#### 6. CKEditor 5 / TinyMCE
- LSP Support: ❌ No
- What they consume: Plugin-based integration with other highlighters

#### 7. Starry-Night
- LSP Support: ❌ No
- What it consumes: TextMate grammar files

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

## Strategic Implications for Spaceup

### Target Priorities Based on Format Standardization:

#### Tier 1: TextMate Grammar (Best ROI)
- Libraries: Shiki, Starry-Night, Monaco Editor
- Effort: Medium (one grammar file)
- Reach: High (VS Code ecosystem compatibility)

#### Tier 2: Simple Token Adapters 
- Libraries: Highlight.js, Prism.js  
- Effort: Low (simple adapters from AST)
- Reach: Very High (most popular)

#### Tier 3: Parser Integration
- Libraries: CodeMirror 6
- Effort: High (Lezer grammar)
- Reach: Medium-High

#### Tier 4: LSP 
- Libraries: Monaco Editor, CodeMirror 6
- Effort: Very High (full language server)
- Reach: Medium (but high-value users)

---

# Formatters and Linters

## Node.js


## Python