"""
Input Validator.

Validates all user-supplied and file-loaded inputs before they reach
the simulation engine.

Validation Rules:
    Page Reference Sequence:
        - Must not be empty.
        - Must be a list (or iterable convertible to a list) of integers.
        - Booleans (True/False) are strictly rejected (not treated as 1/0).
        - Each page number must be a non-negative integer (>= 0).
        - Non-integer or negative values are rejected with a clear message.

    Frame Count:
        - Must be an integer (booleans rejected).
        - Must be a positive integer (>= 1).
        - Zero, negative, or non-integer values are rejected.

    Dataset Files / Dictionaries:
        - Must be a dictionary.
        - Must contain required fields: "page_sequence" and "frame_count".
        - Field values must satisfy the page sequence and frame count rules.

    General:
        - Invalid input is NEVER silently modified or coerced.
        - Every validation function returns a (is_valid, error_message) tuple.
"""


def validate_page_sequence(page_sequence):
    """
    Validate a page reference sequence.

    Args:
        page_sequence: Input to validate as a page reference sequence.

    Returns:
        tuple[bool, str]: (True, "") if valid, or (False, error_message) if invalid.
    """
    if page_sequence is None:
        return False, "Page reference sequence cannot be None."

    if not isinstance(page_sequence, (list, tuple)):
        return False, "Page reference sequence must be a list or tuple of integers."

    if len(page_sequence) == 0:
        return False, "Page reference sequence cannot be empty."

    for index, page in enumerate(page_sequence):
        # In Python, bool is a subclass of int (isinstance(True, int) is True).
        # We must explicitly check and reject booleans.
        if isinstance(page, bool):
            return False, f"Invalid page value at index {index}: boolean values (True/False) are not allowed."

        if not isinstance(page, int):
            return False, f"Invalid page value '{page}' at index {index}: all page numbers must be integers."

        if page < 0:
            return False, f"Invalid page value {page} at index {index}: page numbers must be non-negative (>= 0)."

    return True, ""


def validate_frame_count(frame_count):
    """
    Validate a memory frame count.

    Args:
        frame_count: Input to validate as a frame count.

    Returns:
        tuple[bool, str]: (True, "") if valid, or (False, error_message) if invalid.
    """
    if frame_count is None:
        return False, "Frame count cannot be None."

    if isinstance(frame_count, bool):
        return False, "Frame count cannot be a boolean value."

    if not isinstance(frame_count, int):
        return False, f"Frame count must be an integer, got {type(frame_count).__name__}."

    if frame_count < 1:
        return False, f"Frame count must be a positive integer (>= 1), got {frame_count}."

    return True, ""


def validate_dataset(dataset):
    """
    Validate a loaded dataset dictionary.

    Args:
        dataset (dict): Dataset to validate, expected to contain
            "page_sequence" and "frame_count" keys.

    Returns:
        tuple[bool, str]: (True, "") if valid, or (False, error_message) if invalid.
    """
    if not isinstance(dataset, dict):
        return False, f"Dataset must be a dictionary, got {type(dataset).__name__}."

    if "page_sequence" not in dataset:
        return False, "Dataset missing required field: 'page_sequence'."

    if "frame_count" not in dataset:
        return False, "Dataset missing required field: 'frame_count'."

    seq_valid, seq_err = validate_page_sequence(dataset["page_sequence"])
    if not seq_valid:
        return False, f"Dataset 'page_sequence' invalid: {seq_err}"

    fc_valid, fc_err = validate_frame_count(dataset["frame_count"])
    if not fc_valid:
        return False, f"Dataset 'frame_count' invalid: {fc_err}"

    return True, ""
