# Spaceup

Spaceup is Markdown with comments and indentation for structure.

The document hierarchy is clear at a glance, both when editing and when viewing the rendered version.
Thus, scrolling up to count hashes is no longer needed.

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