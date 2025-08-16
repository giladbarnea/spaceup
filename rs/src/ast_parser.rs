use pulldown_cmark::{Options, Parser as MdParser, html};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Document {
	pub children: Vec<Node>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Node {
	Heading { level: usize, content: String },
	Paragraph { lines: Vec<ParagraphLine> },
	Comment { text: String },
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ParagraphLine {
	pub content: String,
	pub inline_comment: Option<String>,
}

pub fn parse_spaceup_ast(input: &str) -> Document {
	let lines: Vec<String> = input.lines().map(|l| l.trim_end().to_string()).collect();
	let mut children: Vec<Node> = Vec::new();
	let mut indent_stack: Vec<usize> = vec![0];
	let mut pos: usize = 0;
	let mut previous_non_ws_indent: usize = 0;

	fn compute_indent(line: &str) -> Option<usize> {
		let stripped = line.trim_start();
		if stripped.is_empty() { return None; }
		if stripped.starts_with("//") { return None; }
		Some(line.len() - stripped.len())
	}
	fn next_non_ws_indent(lines: &[String], idx: usize) -> isize {
		for i in idx+1..lines.len() {
			if let Some(ind) = compute_indent(&lines[i]) { return ind as isize; }
		}
		-1
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

	fn parse_block(lines: &[String], pos: &mut usize, current_indent: usize, indent_stack: &mut Vec<usize>, previous_non_ws_indent: &mut usize, children: &mut Vec<Node>) {
		while *pos < lines.len() {
			while *pos < lines.len() {
				let stripped = lines[*pos].trim_start();
				if stripped.is_empty() { *pos += 1; continue; }
				if stripped.starts_with("//") {
					let comment_text = stripped[2..].trim();
					if !comment_text.is_empty() { children.push(Node::Comment { text: comment_text.to_string() }); }
					*pos += 1; continue;
				}
				break;
			}
			if *pos >= lines.len() { return; }
			let line = &lines[*pos];
			let indent = match compute_indent(line) { Some(v) => v, None => { *pos += 1; continue; } };
			if indent < current_indent { return; }

			let (content_text, inline_comment) = split_content_and_inline_comment(line);
			if content_text.is_empty() { *pos += 1; continue; }

			let nxt_indent = next_non_ws_indent(lines, *pos);
			let mut has_blank_before_next = false;
			for i in *pos + 1..lines.len() {
				if compute_indent(&lines[i]).is_some() { break; }
				if !lines[i].trim().is_empty() { has_blank_before_next = true; }
			}
			let ambiguous_decrease = *previous_non_ws_indent > indent && nxt_indent == indent as isize && !has_blank_before_next;
			let is_heading = nxt_indent > indent as isize || (nxt_indent == indent as isize && has_blank_before_next) || ambiguous_decrease;
			let heading_level = indent_stack.len();
			if is_heading {
				children.push(Node::Heading { level: heading_level, content: content_text });
				*previous_non_ws_indent = indent;
				indent_stack.push(indent);
				*pos += 1;
				if ambiguous_decrease {
					let mut lines_accum: Vec<ParagraphLine> = Vec::new();
					while *pos < lines.len() {
						let nindent = compute_indent(&lines[*pos]);
						if nindent.is_none() || nindent.unwrap() != indent { break; }
						let (ncontent, ncomment) = split_content_and_inline_comment(&lines[*pos]);
						if !ncontent.is_empty() {
							lines_accum.push(ParagraphLine { content: ncontent, inline_comment: ncomment });
							*previous_non_ws_indent = indent;
						}
						*pos += 1;
					}
					if !lines_accum.is_empty() { children.push(Node::Paragraph { lines: lines_accum }); }
				}
				parse_block(lines, pos, indent + 1, indent_stack, previous_non_ws_indent, children);
				indent_stack.pop();
			} else {
				let mut lines_accum: Vec<ParagraphLine> = vec![ParagraphLine { content: content_text, inline_comment }];
				*pos += 1;
				while *pos < lines.len() {
					let nindent = compute_indent(&lines[*pos]);
					if nindent != Some(indent) { break; }
					let (ncontent, ncomment) = split_content_and_inline_comment(&lines[*pos]);
					if !ncontent.is_empty() {
						lines_accum.push(ParagraphLine { content: ncontent, inline_comment: ncomment });
						*previous_non_ws_indent = indent;
					}
					*pos += 1;
				}
				children.push(Node::Paragraph { lines: lines_accum });
				*previous_non_ws_indent = indent;
			}
		}
	}

	parse_block(&lines, &mut pos, 0, &mut indent_stack, &mut previous_non_ws_indent, &mut children);
	Document { children }
}

fn render_inline_md(text: &str) -> String {
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

pub fn render_ast_to_html(ast: &Document) -> String {
	let mut output: Vec<String> = Vec::new();
	for node in &ast.children {
		match node {
			Node::Heading { level, content } => {
				let rendered = render_inline_md(content);
				output.push(format!("<h{level}>{rendered}</h{level}>"));
			}
			Node::Paragraph { lines } => {
				// simple unordered list detection: all lines start with "- "
				if !lines.is_empty() && lines.iter().all(|l| l.content.trim_start().starts_with("- ")) {
					output.push("<ul>".to_string());
					for line in lines {
						let item_text = line.content.trim_start()[2..].trim().to_string();
						output.push(format!("    <li>{}</li>", render_inline_md(&item_text)));
					}
					output.push("</ul>".to_string());
					continue;
				}
				output.push("<p>".to_string());
				for line in lines {
					let rendered = render_inline_md(&line.content);
					if let Some(c) = &line.inline_comment {
						output.push(format!("    {}  <!-- {} --><br>", rendered, c));
					} else {
						output.push(format!("    {}<br>", rendered));
					}
				}
				output.push("</p>".to_string());
			}
			Node::Comment { text } => {
				if !text.is_empty() { output.push(format!("<!-- {} -->", text)); }
			}
		}
	}
	output.join("\n")
}