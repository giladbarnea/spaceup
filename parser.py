def parse_spaceup(input_str):
    """Parse Spaceup markup into HTML."""
    lines = [line.rstrip() for line in input_str.splitlines()]  # Clean trailing whitespace
    indent_stack = [0]  # Start with root level 0
    output = []
    pos = 0
    previous_non_whitespace_indent = 0
    
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
    
    def emit_paragraph(text_lines):
        if not text_lines:
            return
        divs = '\n'.join(f'<div>{line}</div>' for line in text_lines)
        output.append('<p>')
        output.append(divs)
        output.append('</p>')

    def strip_inline_comment(text):
        return text.lstrip().split('//', 1)[0].strip()

    def parse_element(current_indent):
        nonlocal pos
        nonlocal previous_non_whitespace_indent
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
            content = strip_inline_comment(line)
            if not content:
                pos += 1
                continue  # Skip if no content after stripping
            
            next_indent = peek_next_indent(pos)
            has_blank_before_next = False
            for i in range(pos + 1, len(lines)):
                if compute_indent(lines[i]) is not None:
                    break
                # Only treat comment lines (non-empty) as separators here; pure blank lines do not force a heading
                if lines[i].strip():
                    has_blank_before_next = True
            
            is_heading = False
            ambiguous_decrease = (
                previous_non_whitespace_indent > indent and next_indent == indent and not has_blank_before_next
            )
            if next_indent > indent or (next_indent == indent and has_blank_before_next) or ambiguous_decrease:
                is_heading = True  # Heading if next is greater or same with blank separation
            
            heading_level = len(indent_stack)
            if is_heading:
                output.append(f'<h{heading_level}>{content}</h{heading_level}>')
                previous_non_whitespace_indent = indent
                indent_stack.append(indent)
                pos += 1
                # Handle ambiguous decrease: force subsequent same-indented lines as children
                if ambiguous_decrease:
                    forced_para_lines = []
                    while pos < len(lines):
                        nindent = compute_indent(lines[pos])
                        if nindent is None or nindent != indent:
                            break
                        next_content = strip_inline_comment(lines[pos])
                        if next_content:
                            forced_para_lines.append(next_content)
                            previous_non_whitespace_indent = indent
                        pos += 1
                    emit_paragraph(forced_para_lines)
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
                    next_content = strip_inline_comment(lines[pos])
                    if not next_content:
                        pos += 1
                        continue
                    para_lines.append(next_content)
                    previous_non_whitespace_indent = indent
                    pos += 1
                emit_paragraph(para_lines)
                previous_non_whitespace_indent = indent
    
    parse_element(0)
    return '\n'.join(output)


