"""
CPU Scheduling Input Validator.

Validates process definitions, arrival times, burst times, and algorithm parameters.
"""


def validate_processes(processes):
    """
    Validate a list of processes for CPU scheduling.

    Each process is expected to be a dictionary with:
        - "id" or "name": non-empty string or integer identifier
        - "arrival_time": non-negative integer (>= 0)
        - "burst_time": strictly positive integer (> 0)

    Args:
        processes: List of process dictionaries.

    Returns:
        tuple[bool, str]: (is_valid, error_message).
    """
    if processes is None:
        return False, "Process list cannot be None."

    if not isinstance(processes, (list, tuple)):
        return False, f"Process list must be a list, got {type(processes).__name__}."

    if len(processes) == 0:
        return False, "Process list cannot be empty. Please provide at least one process."

    seen_ids = set()

    for idx, p in enumerate(processes):
        if not isinstance(p, dict):
            return False, f"Process at index {idx} must be a dictionary."

        # Process ID
        p_id = p.get("id", p.get("name"))
        if p_id is None or (isinstance(p_id, str) and not p_id.strip()):
            return False, f"Process at index {idx} missing valid 'id' or 'name'."

        p_id_str = str(p_id).strip()
        if p_id_str in seen_ids:
            return False, f"Duplicate process identifier '{p_id_str}' at index {idx}."
        seen_ids.add(p_id_str)

        # Arrival Time
        at = p.get("arrival_time")
        if at is None:
            return False, f"Process '{p_id_str}' missing required field 'arrival_time'."

        if isinstance(at, bool):
            return False, f"Process '{p_id_str}' arrival_time cannot be a boolean."

        if not isinstance(at, int):
            return False, f"Process '{p_id_str}' arrival_time must be an integer, got {type(at).__name__}."

        if at < 0:
            return False, f"Process '{p_id_str}' arrival_time must be non-negative (>= 0), got {at}."

        # Burst Time
        bt = p.get("burst_time")
        if bt is None:
            return False, f"Process '{p_id_str}' missing required field 'burst_time'."

        if isinstance(bt, bool):
            return False, f"Process '{p_id_str}' burst_time cannot be a boolean."

        if not isinstance(bt, int):
            return False, f"Process '{p_id_str}' burst_time must be an integer, got {type(bt).__name__}."

        if bt <= 0:
            return False, f"Process '{p_id_str}' burst_time must be strictly positive (> 0), got {bt}."

    return True, ""


def validate_time_quantum(quantum):
    """
    Validate a Round Robin time quantum.

    Args:
        quantum: Value to validate as time quantum.

    Returns:
        tuple[bool, str]: (is_valid, error_message).
    """
    if quantum is None:
        return False, "Time quantum cannot be None for Round Robin."

    if isinstance(quantum, bool):
        return False, "Time quantum cannot be a boolean value."

    if not isinstance(quantum, int):
        return False, f"Time quantum must be an integer, got {type(quantum).__name__}."

    if quantum <= 0:
        return False, f"Time quantum must be a strictly positive integer (> 0), got {quantum}."

    return True, ""
