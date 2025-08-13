import mistune


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
    
    def render_inline_markdown(text: str) -> str:
        html = mistune.html(text).strip()
        if html.startswith('<p>') and html.endswith('</p>'):
            html = html[3:-4]
        return html

    def emit_paragraph(text_lines):
        if not text_lines:
            return
        output.append('<p>')
        for item in text_lines:
            if isinstance(item, tuple):
                text, comment = item
                rendered = render_inline_markdown(text)
                if comment:
                    output.append(f'{rendered}  <!-- {comment} --><br>')
                else:
                    output.append(f'{rendered}<br>')
            else:
                output.append(f'{render_inline_markdown(str(item))}<br>')
        output.append('</p>')

    def emit_list(items):
        if not items:
            return
        lis = '\n'.join(f'<li>{render_inline_markdown(text)}</li>' for text in items)
        output.append('<ul>')
        output.append(lis)
        output.append('</ul>')

    def split_content_and_inline_comment(text):
        stripped = text.lstrip()
        search_start = 0
        while True:
            idx = stripped.find('//', search_start)
            if idx == -1:
                break
            if idx == 0:
                # Comment-only lines are handled elsewhere; skip here
                search_start = idx + 2
                continue
            if stripped[idx - 1].isspace():
                return stripped[:idx].rstrip(), stripped[idx + 2 :].strip()
            search_start = idx + 2
        return stripped.strip(), None

    def extract_comment_only(text):
        stripped = text.lstrip()
        if stripped.startswith('//'):
            return stripped[2:].strip()
        return None

    def parse_element(current_indent):
        nonlocal pos
        nonlocal previous_non_whitespace_indent
        while pos < len(lines):
            # Skip blanks, but emit comment-only lines as HTML comments
            while pos < len(lines):
                stripped = lines[pos].lstrip()
                if not stripped:
                    pos += 1
                    continue
                if stripped.startswith('//'):
                    comment_text = stripped[2:].strip()
                    if comment_text:
                        output.append(f'<!-- {comment_text} -->')
                    pos += 1
                    continue
                break
            
            if pos >= len(lines):
                return
            
            line = lines[pos]
            indent = compute_indent(line)
            if indent < current_indent:
                return  # Dedent
            
            # Extract content and inline comment (if present)
            content, inline_comment = split_content_and_inline_comment(line)
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
                rendered_heading = render_inline_markdown(content)
                output.append(f'<h{heading_level}>{rendered_heading}</h{heading_level}>')
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
                        ncontent, ncomment = split_content_and_inline_comment(lines[pos])
                        if ncontent:
                            forced_para_lines.append((ncontent, ncomment))
                            previous_non_whitespace_indent = indent
                        pos += 1
                    emit_paragraph(forced_para_lines)
                parse_element(indent + 1)  # Recurse for content with greater indent
                indent_stack.pop()
            else:
                # Paragraph: collect consecutive lines at same indent
                # But first, detect unordered list starting with "- "
                if content.startswith('- '):
                    items = [content[2:].strip()]
                    pos += 1
                    while pos < len(lines):
                        next_line_indent = compute_indent(lines[pos])
                        if next_line_indent != indent:
                            break
                        next_content, _next_comment = split_content_and_inline_comment(lines[pos])
                        if not next_content.startswith('- '):
                            break
                        items.append(next_content[2:].strip())
                        pos += 1
                    emit_list(items)
                    previous_non_whitespace_indent = indent
                    continue

                para_lines = [(content, inline_comment)]
                pos += 1
                while pos < len(lines):
                    next_line_indent = compute_indent(lines[pos])
                    if next_line_indent != indent:
                        break
                    next_content, next_comment = split_content_and_inline_comment(lines[pos])
                    if not next_content:
                        pos += 1
                        continue
                    para_lines.append((next_content, next_comment))
                    previous_non_whitespace_indent = indent
                    pos += 1
                emit_paragraph(para_lines)
                previous_non_whitespace_indent = indent
    
    parse_element(0)
    return '\n'.join(output)


