use pulldown_cmark::{Options, Parser as MdParser, html};
use regex::Regex;

pub fn parse_spaceup(input: &str) -> String {
	let lines: Vec<String> = input.lines().map(|l| l.trim_end().to_string()).collect();
	let mut output: Vec<String> = Vec::new();
	let mut pos: usize = 0;
	let mut indent_stack: Vec<usize> = vec![0];
	let mut previous_non_ws_indent: usize = 0;

	fn compute_indent(line: &str) -> Option<usize> {
		let stripped = line.trim_start();
		if stripped.is_empty() { return None; }
		if stripped.starts_with("//") { return None; }
		Some(line.len() - stripped.len())
	}

	fn peek_next_indent(lines: &[String], current_pos: usize) -> isize {
		for i in current_pos+1..lines.len() {
			if let Some(ind) = compute_indent(&lines[i]) { return ind as isize; }
		}
		-1
	}

	fn render_inline_markdown(text: &str) -> String {
		let mut options = Options::empty();
		options.insert(Options::ENABLE_TABLES);
		options.insert(Options::ENABLE_TASKLISTS);
		let parser = MdParser::new_ext(text, options);
		let mut html_output = String::new();
		html::push_html(&mut html_output, parser);
		let html_output = html_output.trim().to_string();
		if html_output.starts_with("<p>") && html_output.ends_with("</p>") {
			html_output[3..html_output.len()-4].to_string()
		} else {
			html_output
		}
	}

	fn emit_paragraph(output: &mut Vec<String>, text_lines: &[(String, Option<String>)]) {
		if text_lines.is_empty() { return; }
		output.push("<p>".to_string());
		for (text, comment) in text_lines.iter() {
			let rendered = render_inline_markdown(text);
			if let Some(c) = comment {
				output.push(format!("    {}  <!-- {} --><br>", rendered, c));
			} else {
				output.push(format!("    {}<br>", rendered));
			}
		}
		output.push("</p>".to_string());
	}

	fn emit_list(output: &mut Vec<String>, items: &[String]) {
		if items.is_empty() { return; }
		output.push("<ul>".to_string());
		for item in items {
			let mut text = item.as_str();
			let line = if let Some(rest) = text.strip_prefix("[ ] ") {
				format!("    <li><input type=\"checkbox\" disabled> {}</li>", render_inline_markdown(rest))
			} else if let Some(rest) = text.strip_prefix("[x] ") {
				format!("    <li><input type=\"checkbox\" checked disabled> {}</li>", render_inline_markdown(rest))
			} else {
				format!("    <li>{}</li>", render_inline_markdown(text))
			};
			output.push(line);
		}
		output.push("</ul>".to_string());
	}

	fn emit_ordered_list(output: &mut Vec<String>, items: &[String]) {
		if items.is_empty() { return; }
		output.push("<ol>".to_string());
		for item in items {
			output.push(format!("    <li>{}</li>", render_inline_markdown(item)));
		}
		output.push("</ol>".to_string());
	}

	fn emit_code_block(output: &mut Vec<String>, language: Option<&str>, code_lines: &[String]) {
		if code_lines.is_empty() { return; }
		let code_content = code_lines.join("\n");
		let lang = language.unwrap_or("");
		output.push(format!("<pre><code class=\"language-{}\">{}</code></pre>", lang, code_content));
	}

	fn emit_blockquote(output: &mut Vec<String>, lines: &[String]) {
		if lines.is_empty() { return; }
		let combined = lines.join("\n");
		let mut options = Options::empty();
		let parser = MdParser::new_ext(&combined, options);
		let mut html_output = String::new();
		html::push_html(&mut html_output, parser);
		output.push(html_output);
	}

	fn emit_table(output: &mut Vec<String>, rows: &[String]) {
		if rows.len() < 3 { return; }
		output.push("<table>".to_string());
		output.push("<thead><tr>".to_string());
		for cell in rows[0].split('|').skip(1).take_while(|c| !c.is_empty()) {
			output.push(format!("<th>{}</th>", cell.trim()));
		}
		output.push("</tr></thead>".to_string());
		output.push("<tbody>".to_string());
		for row in rows.iter().skip(2) {
			output.push("<tr>".to_string());
			for cell in row.split('|').skip(1).take_while(|c| !c.is_empty()) {
				output.push(format!("<td>{}</td>", cell.trim()));
			}
			output.push("</tr>".to_string());
		}
		output.push("</tbody>".to_string());
		output.push("</table>".to_string());
	}

	fn split_content_and_inline_comment(text: &str) -> (String, Option<String>) {
		let stripped = text.trim_start();
		let mut search_start = 0usize;
		let bytes = stripped.as_bytes();
		while let Some(idx) = stripped[search_start..].find("//") {
			let i = search_start + idx;
			if i == 0 { search_start = i + 2; continue; }
			if bytes[i-1].is_ascii_whitespace() {
				let content = stripped[..i].trim_end().to_string();
				let comment = stripped[i+2..].trim().to_string();
				return (content, if comment.is_empty() { None } else { Some(comment) });
			}
			search_start = i + 2;
		}
		(stripped.trim().to_string(), None)
	}

	fn extract_comment_only(text: &str) -> Option<String> {
		let stripped = text.trim_start();
		if stripped.starts_with("//") {
			Some(stripped[2..].trim().to_string())
		} else { None }
	}

	fn parse_element(lines: &[String], pos_ref: &mut usize, current_indent: usize, indent_stack: &mut Vec<usize>, previous_non_ws_indent: &mut usize, output: &mut Vec<String>) {
		while *pos_ref < lines.len() {
			// skip blanks and emit comment-only lines
			while *pos_ref < lines.len() {
				let stripped = lines[*pos_ref].trim_start();
				if stripped.is_empty() { *pos_ref += 1; continue; }
				if stripped.starts_with("//") {
					let comment_text = stripped[2..].trim();
					if !comment_text.is_empty() { output.push(format!("<!-- {} -->", comment_text)); }
					*pos_ref += 1;
					continue;
				}
				break;
			}
			if *pos_ref >= lines.len() { return; }
			let line = &lines[*pos_ref];
			let indent = match compute_indent(line) { Some(v) => v, None => { *pos_ref += 1; continue } };
			if indent < current_indent { return; }

			let (content, inline_comment) = split_content_and_inline_comment(line);
			if content.is_empty() { *pos_ref += 1; continue; }

			// fenced code block
			if content.starts_with("```") {
				let language = content[3..].trim();
				let language = if language.is_empty() { None } else { Some(language) };
				let mut code_lines: Vec<String> = Vec::new();
				*pos_ref += 1;
				while *pos_ref < lines.len() {
					let next_line = &lines[*pos_ref];
					if next_line.trim().starts_with("```") { *pos_ref += 1; break; }
					code_lines.push(next_line[indent..].to_string());
					*pos_ref += 1;
				}
				// dedent
				if !code_lines.is_empty() {
					let min_indent = code_lines.iter()
						.filter(|l| !l.trim().is_empty())
						.map(|l| l.len() - l.trim_start().len())
						.min().unwrap_or(0);
					for l in code_lines.iter_mut() { if l.len() >= min_indent { *l = l[min_indent..].to_string(); } }
				}
				emit_code_block(output, language, &code_lines);
				*previous_non_ws_indent = indent;
				continue;
			}

			let next_indent = peek_next_indent(lines, *pos_ref);
			let mut has_blank_before_next = false;
			let mut is_followed_by_code_block = false;
			for i in *pos_ref + 1..lines.len() {
				let stripped = lines[i].trim_start();
				if stripped.is_empty() || stripped.starts_with("//") {
					if !stripped.is_empty() { has_blank_before_next = true; }
					continue;
				}
				if stripped.starts_with("```") { is_followed_by_code_block = true; }
				break;
			}
			let ambiguous_decrease = *previous_non_ws_indent > indent && next_indent == indent as isize && !has_blank_before_next;
			let is_heading = next_indent > indent as isize
				|| (next_indent == indent as isize && has_blank_before_next)
				|| ambiguous_decrease
				|| is_followed_by_code_block
				|| (next_indent == -1 && *pos_ref < lines.len() - 1);

			let heading_level = indent_stack.len();
			if is_heading {
				let rendered_heading = render_inline_markdown(&content);
				output.push(format!("<h{}>{}</h{}>", heading_level, rendered_heading, heading_level));
				*previous_non_ws_indent = indent;
				indent_stack.push(indent);
				*pos_ref += 1;
				if ambiguous_decrease {
					let mut forced_para_lines: Vec<(String, Option<String>)> = Vec::new();
					while *pos_ref < lines.len() {
						let nindent = compute_indent(&lines[*pos_ref]);
						if nindent.is_none() || nindent.unwrap() != indent { break; }
						let (ncontent, ncomment) = split_content_and_inline_comment(&lines[*pos_ref]);
						if !ncontent.is_empty() {
							forced_para_lines.push((ncontent, ncomment));
							*previous_non_ws_indent = indent;
						}
						*pos_ref += 1;
					}
					emit_paragraph(output, &forced_para_lines);
				}
				parse_element(lines, pos_ref, indent + 1, indent_stack, previous_non_ws_indent, output);
				indent_stack.pop();
			} else {
				// paragraph block or other structures at same indent
				let stripped = content.trim_start();
				if stripped.starts_with("- ") {
					let mut items = vec![stripped[2..].trim().to_string()];
					*pos_ref += 1;
					while *pos_ref < lines.len() {
						let next_line_indent = compute_indent(&lines[*pos_ref]);
						if next_line_indent != Some(indent) { break; }
						let (next_content, _) = split_content_and_inline_comment(&lines[*pos_ref]);
						if !next_content.trim_start().starts_with("- ") { break; }
						items.push(next_content.trim_start()[2..].trim().to_string());
						*pos_ref += 1;
					}
					emit_list(output, &items);
					*previous_non_ws_indent = indent;
					continue;
				} else if Regex::new(r"^\d+\.\s").unwrap().is_match(stripped) {
					let mut items: Vec<String> = Vec::new();
					if let Some(cap) = Regex::new(r"^\d+\.\s(.*)").unwrap().captures(stripped) {
						items.push(cap.get(1).unwrap().as_str().trim().to_string());
					}
					*pos_ref += 1;
					while *pos_ref < lines.len() {
						let next_line_indent = compute_indent(&lines[*pos_ref]);
						if next_line_indent != Some(indent) { break; }
						let (next_content, _) = split_content_and_inline_comment(&lines[*pos_ref]);
						if !Regex::new(r"^\d+\.\s").unwrap().is_match(next_content.trim_start()) { break; }
						if let Some(cap) = Regex::new(r"^\d+\.\s(.*)").unwrap().captures(next_content.trim_start()) {
							items.push(cap.get(1).unwrap().as_str().trim().to_string());
						}
						*pos_ref += 1;
					}
					emit_ordered_list(output, &items);
					*previous_non_ws_indent = indent;
					continue;
				} else if stripped.starts_with("> ") {
					let mut quote_lines = vec![content.clone()];
					*pos_ref += 1;
					while *pos_ref < lines.len() {
						let next_line_indent = compute_indent(&lines[*pos_ref]);
						if next_line_indent != Some(indent) { break; }
						let (next_content, _) = split_content_and_inline_comment(&lines[*pos_ref]);
						if !next_content.starts_with("> ") { break; }
						quote_lines.push(next_content);
						*pos_ref += 1;
					}
					emit_blockquote(output, &quote_lines);
					*previous_non_ws_indent = indent;
					continue;
				} else if stripped.starts_with('|') && stripped[1..].contains('|') {
					let mut table_lines = vec![content.clone()];
					*pos_ref += 1;
					while *pos_ref < lines.len() {
						let next_line_indent = compute_indent(&lines[*pos_ref]);
						if next_line_indent != Some(indent) { break; }
						let (next_content, _) = split_content_and_inline_comment(&lines[*pos_ref]);
						if !(next_content.starts_with('|') && next_content[1..].contains('|')) { break; }
						table_lines.push(next_content);
						*pos_ref += 1;
					}
					emit_table(output, &table_lines);
					*previous_non_ws_indent = indent;
					continue;
				} else {
					let mut para_lines: Vec<(String, Option<String>)> = vec![(content, inline_comment)];
					*pos_ref += 1;
					while *pos_ref < lines.len() {
						let next_line_indent = compute_indent(&lines[*pos_ref]);
						if next_line_indent != Some(indent) { break; }
						let (next_content, next_comment) = split_content_and_inline_comment(&lines[*pos_ref]);
						if next_content.is_empty() { *pos_ref += 1; continue; }
						para_lines.push((next_content, next_comment));
						*previous_non_ws_indent = indent;
						*pos_ref += 1;
					}
					emit_paragraph(output, &para_lines);
					*previous_non_ws_indent = indent;
				}
			}
		}
	}

	parse_element(&lines, &mut pos, 0, &mut indent_stack, &mut previous_non_ws_indent, &mut output);
	output.join("\n")
}