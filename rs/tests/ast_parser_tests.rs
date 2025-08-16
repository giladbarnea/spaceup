use std::fs;
use std::path::Path;

use kuchiki::traits::*;
use kuchiki::{NodeData, NodeRef};

use rs::ast_parser::{parse_spaceup_ast, render_ast_to_html};

fn compress_ws(s: &str) -> String {
	let mut result = String::new();
	let mut prev_space = false;
	for ch in s.chars() {
		if ch.is_whitespace() {
			if !prev_space { result.push(' '); prev_space = true; }
		} else { result.push(ch); prev_space = false; }
	}
	result.trim().to_string()
}

fn normalize_node(node: &NodeRef) -> Option<String> {
	match node.data() {
		NodeData::Comment(ref c) => {
			let text = c.borrow();
			let s = compress_ws(&text);
			if s.is_empty() { None } else { Some(format!("(#comment,{})", s)) }
		}
		NodeData::Text(ref t) => {
			let text = t.borrow();
			let s = compress_ws(&text);
			if s.is_empty() { None } else { Some(format!("(#text,{})", s)) }
		}
		NodeData::Element(ref e) => {
			let name = e.name.local.to_string();
			let mut children_norm: Vec<String> = Vec::new();
			for child in node.children() {
				if let Some(n) = normalize_node(&child) { children_norm.push(n); }
			}
			Some(format!("({},{})", name, format!("[{}]", children_norm.join(","))))
		}
		_ => None,
	}
}

fn normalize_html(html: &str) -> String {
	let document = kuchiki::parse_html().one(html);
	let mut parts: Vec<String> = Vec::new();
	if let Ok(body) = document.select_first("body") {
		for child in body.as_node().children() {
			if let Some(n) = normalize_node(&child) { parts.push(n); }
		}
	} else {
		for child in document.children() {
			if let Some(n) = normalize_node(&child) { parts.push(n); }
		}
	}
	format!("[{}]", parts.join(","))
}

fn read(path: &str) -> String {
	fs::read_to_string(Path::new(path)).expect("failed to read file")
}

#[test]
fn ast_parser_basic_example() {
	let input = read("tests/data/basic_example.txt");
	let ast = parse_spaceup_ast(&input);
	let html = render_ast_to_html(&ast);
	let expected_html = read("tests/data/basic_example.html");
	assert_eq!(normalize_html(&expected_html), normalize_html(&html));
}

#[test]
fn ast_parser_end_of_document_paragraph() {
	let input = read("tests/data/end_of_document_paragraph.txt");
	let ast = parse_spaceup_ast(&input);
	let html = render_ast_to_html(&ast);
	let expected_html = read("tests/data/end_of_document_paragraph.html");
	assert_eq!(normalize_html(&expected_html), normalize_html(&html));
}

#[test]
fn ast_parser_two_indentation_levels() {
	let input = read("tests/data/two_indentation_levels.txt");
	let ast = parse_spaceup_ast(&input);
	let html = render_ast_to_html(&ast);
	let expected_html = read("tests/data/two_indentation_levels.html");
	assert_eq!(normalize_html(&expected_html), normalize_html(&html));
}

#[test]
fn ast_parser_unambiguous_decreasing_indentation_level() {
	let input = read("tests/data/unambiguous_decreasing_indentation_level.txt");
	let ast = parse_spaceup_ast(&input);
	let html = render_ast_to_html(&ast);
	let expected_html = read("tests/data/unambiguous_decreasing_indentation_level.html");
	assert_eq!(normalize_html(&expected_html), normalize_html(&html));
}

#[test]
fn ast_parser_ambiguous_decreasing_indentation_level() {
	let input = read("tests/data/ambiguous_decreasing_indentation_level.txt");
	let ast = parse_spaceup_ast(&input);
	let html = render_ast_to_html(&ast);
	let expected_html = read("tests/data/ambiguous_decreasing_indentation_level.html");
	assert_eq!(normalize_html(&expected_html), normalize_html(&html));
}

#[test]
fn ast_parser_comments_sanity() {
	let input = read("tests/data/comments_sanity.txt");
	let ast = parse_spaceup_ast(&input);
	let html = render_ast_to_html(&ast);
	let expected_html = read("tests/data/comments_sanity.html");
	assert_eq!(normalize_html(&expected_html), normalize_html(&html));
}

#[test]
fn ast_parser_full_example() {
	let input = read("tests/data/full_example.txt");
	let ast = parse_spaceup_ast(&input);
	let html = render_ast_to_html(&ast);
	let expected_html = read("tests/data/full_example.html");
	assert_eq!(normalize_html(&expected_html), normalize_html(&html));
}

#[test]
fn ast_parser_markdown_features() {
	let input = read("tests/data/markdown_features.txt");
	let ast = parse_spaceup_ast(&input);
	let html = render_ast_to_html(&ast);
	let expected_html = read("tests/data/markdown_features.html");
	assert_eq!(normalize_html(&expected_html), normalize_html(&html));
}

#[test]
fn ast_parser_markdown_features_and_comments() {
	let input = read("tests/data/markdown_features_and_comments.txt");
	let ast = parse_spaceup_ast(&input);
	let html = render_ast_to_html(&ast);
	let expected_html = read("tests/data/markdown_features_and_comments.html");
	assert_eq!(normalize_html(&expected_html), normalize_html(&html));
}

#[test]
fn ast_parser_full_example_and_markdown_in_paragraphs() {
	let input = read("tests/data/full_example_and_markdown_in_paragraphs.txt");
	let ast = parse_spaceup_ast(&input);
	let html = render_ast_to_html(&ast);
	let expected_html = read("tests/data/full_example_and_markdown_in_paragraphs.html");
	assert_eq!(normalize_html(&expected_html), normalize_html(&html));
}