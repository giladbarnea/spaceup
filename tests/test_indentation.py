import pytest
from indentation import validate_indentation, IndentationError

ONE_INDENT = " " * 4
TWO_INDENTS = ONE_INDENT * 2
def test_valid_indentation():
    text = f"line1\n{ONE_INDENT}line2\n{TWO_INDENTS}line3\n{ONE_INDENT}line4"
    validate_indentation(text)

def test_invalid_indentation_with_tabs():
    text = "line1\n\tline2"
    with pytest.raises(IndentationError, match="Line 2: Tabs are not allowed for indentation."):
        validate_indentation(text)

def test_invalid_indentation_with_mixed_tabs_and_spaces():
    text = f"line1\n{ONE_INDENT}\tline2"
    with pytest.raises(IndentationError, match="Line 2: Tabs are not allowed for indentation."):
        validate_indentation(text)

def test_invalid_indentation_with_non_multiple_of_4_spaces():
    text = "line1\n  line2"
    with pytest.raises(IndentationError, match="Line 2: Indentation must be a multiple of 4 spaces."):
        validate_indentation(text)

def test_valid_indentation_with_blank_lines():
    text = f"line1\n\n{ONE_INDENT}line2\n\n{TWO_INDENTS}line3\n\n{ONE_INDENT}line4"
    validate_indentation(text)

def test_invalid_indentation_on_specific_line():
    text = f"line1\n{ONE_INDENT}line2\n{ONE_INDENT}  line3\n{ONE_INDENT}line4"
    with pytest.raises(IndentationError, match="Line 3: Indentation must be a multiple of 4 spaces."):
        validate_indentation(text)