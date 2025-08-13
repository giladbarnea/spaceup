class IndentationError(ValueError):
    pass

def validate_indentation(text: str):
    """
    Validates the indentation of a given text.

    Args:
        text: The text to validate.

    Raises:
        IndentationError: If the indentation is invalid.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not line.strip():
            continue

        indentation_part = ""
        for char in line:
            if char.isspace():
                indentation_part += char
            else:
                break
        
        if '\t' in indentation_part:
            raise IndentationError(f"Line {i+1}: Tabs are not allowed for indentation.")
        
        if len(indentation_part) % 4 != 0:
            raise IndentationError(f"Line {i+1}: Indentation must be a multiple of 4 spaces.")
