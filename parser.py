import mistune

def parse_spaceup(input_str):
    lines = [line.rstrip() for line in input_str.splitlines()]  # Clean trailing whitespace
    indent_stack = [0]  # Start with root level 0
    output = []
    pos = 0
    prev_non_ws_indent = 0
    
    def compute_indent(line):
        stripped = line.lstrip()
        if not stripped or stripped.startswith('//'):  # Ignore blank or pure comment lines for structure
            return None
        return len(line) - len(stripped)
    
    def peek_next_indent(current_pos):
        for i in range(current_pos + 1, len(lines)):
            indent = compute_indent(lines[i])
            if indent is not None:
                return indent
        return -1  # EOF, use -1 to indicate
    
    def parse_element(current_indent):
        nonlocal pos
        nonlocal prev_non_ws_indent
        while pos < len(lines):
            while pos < len(lines) and compute_indent(lines[pos]) is None:
                pos += 1  # Skip blanks and comments
            
            if pos >= len(lines):
                return
            
            line = lines[pos]
            indent = compute_indent(line)
            if indent < current_indent:
                return  # Dedent
            
            # Extract content, ignoring trailing comments
            content_parts = line.lstrip().split('//', 1)
            content = content_parts[0].strip()
            if not content:
                pos += 1
                continue  # Skip if no content after stripping
            
            next_indent = peek_next_indent(pos)
            has_blank_before_next = False
            for i in range(pos + 1, len(lines)):
                if compute_indent(lines[i]) is not None:
                    break
                if lines[i].strip():  # If there's a non-blank but comment, treat as blank for separation
                    has_blank_before_next = True
            
            is_heading = False
            ambiguous_decrease = (
                prev_non_ws_indent > indent and next_indent == indent and not has_blank_before_next
            )
            if next_indent > indent or (next_indent == indent and has_blank_before_next) or ambiguous_decrease:
                is_heading = True  # Heading if next is greater or same with blank separation
            
            heading_level = len(indent_stack)
            if is_heading:
                output.append(f'<h{heading_level}>{content}</h{heading_level}>')
                prev_non_ws_indent = indent
                indent_stack.append(indent)
                pos += 1
                # Handle ambiguous decrease: force subsequent same-indented lines as children
                if ambiguous_decrease:
                    forced_para_lines = []
                    while pos < len(lines):
                        nindent = compute_indent(lines[pos])
                        if nindent is None or nindent != indent:
                            break
                        next_content = lines[pos].lstrip().split('//', 1)[0].strip()
                        if next_content:
                            forced_para_lines.append(next_content)
                            prev_non_ws_indent = indent
                        pos += 1
                    if forced_para_lines:
                        divs = '\n'.join(f'<div>{line}</div>' for line in forced_para_lines)
                        output.append('<p>')
                        output.append(divs)
                        output.append('</p>')
                parse_element(indent + 1)  # Recurse for content with greater indent
                indent_stack.pop()
            else:
                # Paragraph: collect consecutive lines at same indent
                para_lines = [content]
                pos += 1
                while pos < len(lines):
                    next_line_indent = compute_indent(lines[pos])
                    if next_line_indent != indent:
                        break
                    next_content = lines[pos].lstrip().split('//', 1)[0].strip()
                    if not next_content:
                        pos += 1
                        continue
                    para_lines.append(next_content)
                    prev_non_ws_indent = indent
                    pos += 1
                if para_lines:
                    divs = '\n'.join(f'<div>{line}</div>' for line in para_lines)
                    output.append('<p>')
                    output.append(divs)
                    output.append('</p>')
                    prev_non_ws_indent = indent
    
    parse_element(0)
    return '\n'.join(output)

# Test with full example
full_input = """text with 0 indentation

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
    // In such an ambiguous, decreased-indentation case, where it's unclear how to parse the first line because the line which follows it shares the same indentation level, the first line is FORCED to become a heading. Subsequent lines in this block are forced to be indented. In effect, this makes this block with exactly the same structure as the one before it; an h2 line, followed by a paragraph starter."""

print(parse_spaceup(full_input))
