import mistune
import re


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
        lis = ''
        for text in items:
            if text.startswith('[ ] '):
                lis += '<li><input type="checkbox" disabled> ' + render_inline_markdown(text[4:]) + '</li>\n'
            elif text.startswith('[x] '):
                lis += '<li><input type="checkbox" checked disabled> ' + render_inline_markdown(text[4:]) + '</li>\n'
            else:
                lis += '<li>' + render_inline_markdown(text) + '</li>\n'
        output.append('<ul>')
        output.append(lis)
        output.append('</ul>')

    def emit_ordered_list(items):
        if not items:
            return
        lis = '\n'.join(f'<li>{render_inline_markdown(text)}</li>' for text in items)
        output.append('<ol>')
        output.append(lis)
        output.append('</ol>')

    def emit_code_block(language, code_lines):
        if not code_lines:
            return
        code_content = '\n'.join(code_lines)
        output.append(f'<pre><code class="language-{language or ""}">{code_content}</code></pre>')

    def emit_blockquote(lines):
        if not lines:
            return
        combined = '\n'.join(line for line in lines)
        html = mistune.html(combined)
        output.append(html)

    def emit_table(rows):
        if not rows or len(rows) < 3:  # Min header, separator, one row
            return
        output.append('<table>')
        # Header
        output.append('<thead><tr>')
        for cell in rows[0].split('|')[1:-1]:
            output.append('<th>' + cell.strip() + '</th>')
        output.append('</tr></thead>')
        # Body
        output.append('<tbody>')
        for row in rows[2:]:
            output.append('<tr>')
            for cell in row.split('|')[1:-1]:
                output.append('<td>' + cell.strip() + '</td>')
            output.append('</tr>')
        output.append('</tbody>')
        output.append('</table>')

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
            
            # Detect fenced code blocks early, before heading/paragraph logic
            if content.startswith('```'):
                # Extract language if present
                language = content[3:].strip() or None
                code_lines = []
                pos += 1
                while pos < len(lines):
                    next_line = lines[pos]
                    if next_line.strip().startswith('```'):
                        pos += 1
                        break
                    code_lines.append(next_line[indent:])  # Trim exactly to the opening indent level
                    pos += 1
                # Dedent the code block
                if code_lines:
                    min_indent = min(len(l) - len(l.lstrip()) for l in code_lines if l.strip())
                    code_lines = [l[min_indent:] for l in code_lines]
                emit_code_block(language, code_lines)
                previous_non_whitespace_indent = indent
                continue

            next_indent = peek_next_indent(pos)
            has_blank_before_next = False
            is_followed_by_code_block = False
            for i in range(pos + 1, len(lines)):
                stripped = lines[i].lstrip()
                if not stripped or stripped.startswith('//'):
                    if stripped:  # Non-empty blank or comment counts as separator
                        has_blank_before_next = True
                    continue
                if stripped.startswith('```'):
                    is_followed_by_code_block = True
                break
            ambiguous_decrease = (
                previous_non_whitespace_indent > indent and next_indent == indent and not has_blank_before_next
            )
            is_heading = next_indent > indent or (next_indent == indent and has_blank_before_next) or ambiguous_decrease or is_followed_by_code_block or (next_indent == -1 and pos < len(lines) - 1)

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

                elif re.match(r'^\d+\.\s', content):
                    items = []
                    match = re.match(r'^\d+\.\s(.*)', content)
                    if match:
                        items.append(match.group(1).strip())
                    pos += 1
                    while pos < len(lines):
                        next_line_indent = compute_indent(lines[pos])
                        if next_line_indent != indent:
                            break
                        next_content, _next_comment = split_content_and_inline_comment(lines[pos])
                        match = re.match(r'^\d+\.\s(.*)', next_content)
                        if not match:
                            break
                        items.append(match.group(1).strip())
                        pos += 1
                    emit_ordered_list(items)
                    previous_non_whitespace_indent = indent
                    continue

                elif content.startswith('> '):
                    quote_lines = [content]
                    pos += 1
                    while pos < len(lines):
                        next_line_indent = compute_indent(lines[pos])
                        if next_line_indent != indent:
                            break
                        next_content, _ = split_content_and_inline_comment(lines[pos])
                        if not next_content.startswith('> '):
                            break
                        quote_lines.append(next_content)
                        pos += 1
                    emit_blockquote(quote_lines)
                    previous_non_whitespace_indent = indent
                    continue

                elif content.startswith('|') and '|' in content[1:]:
                    table_lines = [content]
                    pos += 1
                    while pos < len(lines):
                        next_line_indent = compute_indent(lines[pos])
                        if next_line_indent != indent:
                            break
                        next_content, _ = split_content_and_inline_comment(lines[pos])
                        if not next_content.startswith('|') or '|' not in next_content[1:]:
                            break
                        table_lines.append(next_content)
                        pos += 1
                    emit_table(table_lines)
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


