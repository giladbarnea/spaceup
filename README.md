# Spaceup

Spaceup is a semi-structured markup language favoring simplicity and readability of both source code and output.

It supports document structure while having only a single syntactical rule.

## Examples

Structure is driven by indentation.

```
Favorite Books
	Dune by Frank Herbert
	    
		Features an immersive universe and a deep, complex plot.
		Recommended for readers looking for sweeping political intrigue.
		
	Ender's Game by Orson Scott Card
		
		A fast, tactical sci-fi about a child prodigy shaped by relentless war games to defend humanity.
		Recommended for readers looking for high-velocity strategy and thought-provoking ethical dilemmas.

```

This is equivalent to the following markdown:

```markdown
# Favorite Books

## Dune by Frank Herbert

Features an immersive universe and a deep, complex plot.
Recommended for readers looking for sweeping political intrigue.

## Ender's Game by Orson Scott Card

A fast, tactical sci-fi about a child prodigy shaped by relentless war games to defend humanity.
Recommended for readers looking for high-velocity strategy and thought-provoking ethical dilemmas.
```

## Language Features

- Supports all but niche Markdown features, minus `#` headings and indented blocks
- Supports `//` comments

## Implementations

Equivalent implementations of the AST parser and tests exist in `js/` and `rs/` alongside the Python version. We intend to replace the Python core with Rust over time, while the JS version exists to support Node and browser environments.
