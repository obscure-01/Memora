"""
Deadlock Management Input Validator.

Validates Available vector, Allocation matrix, and Maximum demand matrix
for the Banker's Algorithm.
"""


def validate_bankers_input(available, allocation, max_matrix, process_names=None, resource_names=None):
    """
    Validate input data for Banker's Algorithm.

    Args:
        available (list[int]): Available vector of length m.
        allocation (list[list[int]]): Allocation matrix of dimension n x m.
        max_matrix (list[list[int]]): Maximum demand matrix of dimension n x m.
        process_names (list[str], optional): Process labels.
        resource_names (list[str], optional): Resource labels.

    Returns:
        tuple[bool, str]: (is_valid, error_message).
    """
    if available is None or not isinstance(available, (list, tuple)):
        return False, "Available resources must be a list of non-negative integers."

    if len(available) == 0:
        return False, "Available resource vector cannot be empty."

    num_resources = len(available)

    # Validate Available vector
    for j, val in enumerate(available):
        if isinstance(val, bool):
            return False, f"Available resource at index {j} cannot be a boolean."
        if not isinstance(val, int):
            return False, f"Available resource at index {j} must be an integer, got {type(val).__name__}."
        if val < 0:
            return False, f"Available resource at index {j} must be non-negative (>= 0), got {val}."

    # Validate Allocation matrix
    if allocation is None or not isinstance(allocation, (list, tuple)):
        return False, "Allocation matrix must be a 2D list."

    num_processes = len(allocation)
    if num_processes == 0:
        return False, "Allocation matrix must contain at least one process."

    for i, row in enumerate(allocation):
        if not isinstance(row, (list, tuple)):
            return False, f"Allocation row for process {i} must be a list."
        if len(row) != num_resources:
            return False, (
                f"Allocation row for process {i} has length {len(row)}, "
                f"expected {num_resources} (matching Available vector)."
            )
        for j, val in enumerate(row):
            if isinstance(val, bool):
                return False, f"Allocation[{i}][{j}] cannot be a boolean."
            if not isinstance(val, int):
                return False, f"Allocation[{i}][{j}] must be an integer, got {type(val).__name__}."
            if val < 0:
                return False, f"Allocation[{i}][{j}] must be non-negative (>= 0), got {val}."

    # Validate Maximum matrix
    if max_matrix is None or not isinstance(max_matrix, (list, tuple)):
        return False, "Maximum demand matrix must be a 2D list."

    if len(max_matrix) != num_processes:
        return False, (
            f"Maximum matrix has {len(max_matrix)} rows, expected {num_processes} "
            f"(matching Allocation matrix)."
        )

    for i, row in enumerate(max_matrix):
        if not isinstance(row, (list, tuple)):
            return False, f"Maximum demand row for process {i} must be a list."
        if len(row) != num_resources:
            return False, (
                f"Maximum demand row for process {i} has length {len(row)}, "
                f"expected {num_resources} (matching Available vector)."
            )
        for j, val in enumerate(row):
            if isinstance(val, bool):
                return False, f"Maximum[{i}][{j}] cannot be a boolean."
            if not isinstance(val, int):
                return False, f"Maximum[{i}][{j}] must be an integer, got {type(val).__name__}."
            if val < 0:
                return False, f"Maximum[{i}][{j}] must be non-negative (>= 0), got {val}."

    # Cross-check: Allocation cannot exceed Maximum demand
    for i in range(num_processes):
        for j in range(num_resources):
            if allocation[i][j] > max_matrix[i][j]:
                p_label = process_names[i] if process_names and i < len(process_names) else f"P{i}"
                r_label = resource_names[j] if resource_names and j < len(resource_names) else f"R{j}"
                return False, (
                    f"Process '{p_label}' has Allocation ({allocation[i][j]}) "
                    f"exceeding Maximum demand ({max_matrix[i][j]}) for resource '{r_label}'."
                )

    return True, ""


def validate_resource_request(request_vector, process_idx, need_matrix, available_vector, process_name=None):
    """
    Validate a single process's resource request vector.

    Args:
        request_vector (list[int]): Requested instances for each resource type.
        process_idx (int): Index of requesting process.
        need_matrix (list[list[int]]): Need matrix.
        available_vector (list[int]): Current available vector.
        process_name (str, optional): Name of process.

    Returns:
        tuple[bool, str]: (is_valid, error_message).
    """
    p_label = process_name or f"P{process_idx}"

    if request_vector is None or not isinstance(request_vector, (list, tuple)):
        return False, "Request vector must be a list of integers."

    if len(request_vector) != len(available_vector):
        return False, f"Request vector has length {len(request_vector)}, expected {len(available_vector)}."

    for j, val in enumerate(request_vector):
        if isinstance(val, bool) or not isinstance(val, int):
            return False, f"Request[{j}] must be an integer."
        if val < 0:
            return False, f"Request[{j}] must be non-negative (>= 0), got {val}."

    # Rule 1: Request <= Need
    for j in range(len(request_vector)):
        if request_vector[j] > need_matrix[process_idx][j]:
            return False, (
                f"Process '{p_label}' request exceeds its declared remaining need: "
                f"Requested {request_vector[j]} > Need {need_matrix[process_idx][j]} for resource index {j}."
            )

    # Rule 2: Request <= Available
    for j in range(len(request_vector)):
        if request_vector[j] > available_vector[j]:
            return False, (
                f"Process '{p_label}' must wait: insufficient available resources. "
                f"Requested {request_vector[j]} > Available {available_vector[j]} for resource index {j}."
            )

    return True, ""
