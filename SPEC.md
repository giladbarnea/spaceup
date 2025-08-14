# Spaceup Spec

Spaceup is Markdown with `//` comments and indentation for document structure, replacing `#` headings.

## Examples

### Example 1: Basic Structure

```sup
text with 0 indentation
    text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know.
    another line with more text with 1 indentation.
```

Equivalent to:

```html
<h1>text with 0 indentation</h1>
<p>
text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know.<br>
another line with more text with 1 indentation.<br>
</p>
```

### Example 2: End of Document Paragraph

```sup
text with 0 indentation
    text with 1 indentation. 1 is greater than the preceding 0, and that's the last element in the document (next is EOF) --> this text is a paragraph opener, and the preceding element is an h1.
```

Equivalent to:

```html
<h1>text with 0 indentation</h1>
<p>
text with 1 indentation. 1 is greater than the preceding 0, and that's the last element in the document (next is EOF) --> this text is a paragraph opener, and the preceding element is an h1.<br>
</p>
```

### Example 3: Multiple Paragraphs and Headings

```sup
text with 0 indentation

    text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know. // hint: the following non-WS, non-comment element's indentation level is LOWER OR EQUAL to this one; therefore, this line is a paragraph open.
    another line with more text with 1 indentation.

    even some more text with 1 indentation, preceded by a blank line, and next non-whitespace, non-comment element has indentation LOWER OR EQUAL to this one  --> this is a paragraph open.
        
    here is a new line with 1 indentation, preceded by a blank line, BUT, next non-WS non comment element has a greater indentation level. Therefore, this is a H2. 

        Some paragraph opener under the H2 heading from before, with an indentation level of 2.
        Lorem ipsum a new div in the same paragraph because no blank line before it and indent level is also 2.

        Foo text after a blank line with same indentation (2) as the preceding text; it is another paragraph opener under the H2 from before.

    Back to indentation level 1. Note that the next line has increased indentation.
        This line has indentation level 2. Because 1 is LOWER THAN 2, the previous line is a heading (h2), and since the next element has a LOWER indentation level, this is a paragraph start with a single div.

    Back to indentation level 1. Next line has the same indentation.
    Here is another line, right afterwards, with the SAME indentation level (1). This is a special case; read the comment below.
    // This text block is the first example where the two following conditions occur:
    // 1. indentation went DOWN (previous non-ws non-comment element was 2; now it's 1), and
    // 2. Two consecutive elements have the same indentation level (1), and going by rules above, the first line of this block — 'Back to indentation level 1' — shouldn't be a heading. But we have to make an exception here.
    // In such an ambiguous, decreased-indentation case, where it's unclear how to parse the first line because the line which follows it shares the same indentation level, the first line is FORCED to become a heading. Subsequent lines in this block are forced to be indented. In effect, this makes this block with exactly the same structure as the one before it; an h2 line, followed by a paragraph starter.
```

Equivalent to:

```html
<h1>text with 0 indentation</h1>
<p>
  text with 1 indentation. 1 is greater than the preceding 0, but we need to parse the next element before we know.  <!-- hint: the following non-WS, non-comment element's indentation level is LOWER OR EQUAL to this one; therefore this line is a paragraph open. --><br>
  another line with more text with 1 indentation.<br>
</p>
<p>
  even some more text with 1 indentation, preceded by a blank line, and next non-whitespace, non-comment element has indentation LOWER OR EQUAL to this one  --> this is a paragraph open.<br>
</p>
<h2>here is a new line with 1 indentation, preceded by a blank line, BUT, next non-WS non comment element has a greater indentation level. Therefore, this is a H2.</h2>
<p>
  Some paragraph opener under the H2 heading from before, with an indentation level of 2.<br>
  Lorem ipsum a new div in the same paragraph because no blank line before it and indent level is also 2.<br>
</p>
<p>
  Foo text after a blank line with same indentation (2) as the preceding text; it is another paragraph opener under the H2 from before.<br>
</p>
<h2>Back to indentation level 1. Note that the next line has increased indentation.</h2>
<p>
  This line has indentation level 2. Because 1 is LOWER THAN 2, the previous line is a heading (h2), and since the next element has a LOWER indentation level, this is a paragraph start with a single div.<br>
</p>
<h2>Back to indentation level 1. Next line has the same indentation.</h2>
<p>
  Here is another line, right afterwards, with the SAME indentation level (1). This is a special case; read the comment below.<br>
</p>
<!-- This text block is the first example where the two following conditions occur: -->
<!-- 1. indentation went DOWN (previous non-ws non-comment element was 2; now it's 1), and -->
<!-- 2. Two consecutive elements have the same indentation level (1), and going by rules above, the first line of this block — 'Back to indentation level 1' — shouldn't be a heading. But we have to make an exception here. -->
<!-- In such an ambiguous, decreased-indentation case, where it's unclear how to parse the first line because the line which follows it shares the same indentation level, the first line is FORCED to become a heading. Subsequent lines in this block are forced to be indented. In effect, this makes this block with exactly the same structure as the one before it; an h2 line, followed by a paragraph starter. -->
```

### Toy Example: With Markdown Features

```sup
My Favorite Recipe

    Ingredients

        - 2 cups flour
        - 1 cup sugar
        - **1 tsp** baking powder

        Mix them well. // note: whisk thoroughly

    Instructions

        Preheat oven to 350°F. // oven temperature
        Bake for 20 minutes.

        Enjoy your [cake](https://example.com/recipe)! // bon appetit

```

Equivalent to:

```html
<h1>My Favorite Recipe</h1>
<h2>Ingredients</h2>
<ul>
    <li>2 cups flour</li>
    <li>1 cup sugar</li>
    <li><strong>1 tsp</strong> baking powder</li>
</ul>
<p>
    Mix them well.  <!-- note: whisk thoroughly --><br>
</p>
<h2>Instructions</h2>
<p>
    Preheat oven to 350°F.  <!-- oven temperature --><br>
    Bake for 20 minutes.<br>
</p>
<p>
    Enjoy your <a href="https://example.com/recipe">cake</a>!  <!-- bon appetit --><br>
</p>
```

## Spaceup is a Markdown Superset\*

All Markdown features are supported, except for `#` headings and indented blocks.








