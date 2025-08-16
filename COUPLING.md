# Coupling in the project

This document lists the points where the developer or AI agent should ensure that a change in one location is synchronized with the corresponding point.
Because of the project's multi-language nature, some of these points are unavoidable. But this doc also lists points of "regular" coupling that should be kept in mind.

## Tests

ast_parser:
- js/tests/ast_parser.spec.js
- tests/test_ast_parser.py
- rs/tests/ast_parser_tests.rs

mdast:
- js/tests/mdast.spec.js
- tests/test_mdast.py
- rs/tests/mdast_tests.rs


## Docs

Information about the project:
- CONTEXT.md
- SPEC.md
- README.md
Each of them overlaps a bit and covers a different aspect of the project in more detail. CONTEXT.md is the source of truth. Secondarily, SPEC.md; and then README.md, which is dictated by other docs.