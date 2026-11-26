"""
Banker's Algorithm for Deadlock Avoidance and Safety Checking.

Implements:
    1. Need Matrix Computation (Need = Maximum - Allocation)
    2. Safety Algorithm (Determines safe state and sequence)
    3. Resource-Request Algorithm (Evaluates dynamic resource requests)
"""

from src.deadlock.validator import validate_bankers_input, validate_resource_request


def compute_need_matrix(allocation, max_matrix):
    """
    Compute the Need matrix where Need[i][j] = Maximum[i][j] - Allocation[i][j].

    Args:
        allocation (list[list[int]]): Current allocation matrix.
        max_matrix (list[list[int]]): Maximum demand matrix.

    Returns:
        list[list[int]]: Need matrix.
    """
    num_processes = len(allocation)
    num_resources = len(allocation[0])
    need = []
    for i in range(num_processes):
        need.append([max_matrix[i][j] - allocation[i][j] for j in range(num_resources)])
    return need


def check_safety(available, allocation, max_matrix, process_names=None, resource_names=None):
    """
    Execute the Banker's Safety Algorithm to determine if the system is in a safe state.

    Args:
        available (list[int]): Available vector of length m.
        allocation (list[list[int]]): Current allocation matrix of dimension n x m.
        max_matrix (list[list[int]]): Maximum claim matrix of dimension n x m.
        process_names (list[str], optional): Custom process identifiers.
        resource_names (list[str], optional): Custom resource identifiers.

    Returns:
        dict: Standardized safety evaluation dictionary.
    """
    is_valid, err = validate_bankers_input(available, allocation, max_matrix, process_names, resource_names)
    if not is_valid:
        raise ValueError(f"Invalid Banker's input: {err}")

    num_processes = len(allocation)
    num_resources = len(available)

    # Default labels
    p_names = list(process_names) if process_names else [f"P{i}" for i in range(num_processes)]
    r_names = list(resource_names) if resource_names else [chr(ord('A') + j) for j in range(num_resources)]

    need_matrix = compute_need_matrix(allocation, max_matrix)

    # Work = Available, Finish = [False] * n
    work = list(available)
    finish = [False] * num_processes

    safe_sequence = []
    steps = []
    iteration = 1

    while len(safe_sequence) < num_processes:
        found_in_iteration = False

        for i in range(num_processes):
            if not finish[i]:
                # Check if Need[i] <= Work
                can_allocate = all(need_matrix[i][j] <= work[j] for j in range(num_resources))

                if can_allocate:
                    work_before = list(work)
                    # Work = Work + Allocation[i]
                    for j in range(num_resources):
                        work[j] += allocation[i][j]

                    finish[i] = True
                    safe_sequence.append(p_names[i])
                    found_in_iteration = True

                    steps.append({
                        "step": iteration,
                        "process": p_names[i],
                        "process_index": i,
                        "work_before": work_before,
                        "need": list(need_matrix[i]),
                        "allocation": list(allocation[i]),
                        "work_after": list(work),
                        "status": "Granted & Completed",
                        "description": (
                            f"{p_names[i]} satisfied (Need {need_matrix[i]} <= Work {work_before}). "
                            f"Process completes and releases {allocation[i]} -> New Work: {work}."
                        ),
                    })
                    iteration += 1
                    break  # Restart scan from the beginning of process list for consistency

        if not found_in_iteration:
            # No process could be allocated: Unsafe state
            break

    is_safe = (len(safe_sequence) == num_processes)

    if is_safe:
        seq_str = " -> ".join(safe_sequence)
        explanation = (
            f"System is in a SAFE STATE. A valid safe execution sequence exists: {seq_str}. "
            f"All {num_processes} processes can successfully finish without deadlocking."
        )
    else:
        unfinished = [p_names[i] for i in range(num_processes) if not finish[i]]
        unfinished_str = ", ".join(unfinished)
        explanation = (
            f"System is in an UNSAFE STATE. Remaining processes ({unfinished_str}) cannot "
            f"be satisfied with current available resources. Note: An unsafe state is not identical "
            f"to deadlock; rather, the operating system cannot guarantee avoidance of deadlock if "
            f"processes request their maximum declared claims."
        )

    return {
        "is_safe": is_safe,
        "safe_sequence": safe_sequence,
        "process_names": p_names,
        "resource_names": r_names,
        "available": list(available),
        "allocation": [list(row) for row in allocation],
        "max": [list(row) for row in max_matrix],
        "need": need_matrix,
        "steps": steps,
        "explanation": explanation,
    }


def simulate_resource_request(available, allocation, max_matrix, process_idx, request_vector, process_names=None, resource_names=None):
    """
    Simulate a resource request by a process using the Banker's Resource-Request Algorithm.

    Args:
        available: Current available vector.
        allocation: Current allocation matrix.
        max_matrix: Current maximum demand matrix.
        process_idx: Index of requesting process.
        request_vector: Resources requested by process_idx.
        process_names: Optional process labels.
        resource_names: Optional resource labels.

    Returns:
        dict: Evaluation containing approval status, hypothetical state, and safety evaluation.
    """
    is_valid, err = validate_bankers_input(available, allocation, max_matrix, process_names, resource_names)
    if not is_valid:
        raise ValueError(f"Invalid Banker's state: {err}")

    need_matrix = compute_need_matrix(allocation, max_matrix)
    p_name = process_names[process_idx] if process_names and process_idx < len(process_names) else f"P{process_idx}"

    req_valid, req_err = validate_resource_request(request_vector, process_idx, need_matrix, available, p_name)
    if not req_valid:
        return {
            "approved": False,
            "can_grant": False,
            "reason": req_err,
            "safety_result": None,
        }

    num_resources = len(available)

    # Create hypothetical state
    hypo_available = [available[j] - request_vector[j] for j in range(num_resources)]
    hypo_allocation = [list(row) for row in allocation]
    for j in range(num_resources):
        hypo_allocation[process_idx][j] += request_vector[j]

    # Run safety algorithm on hypothetical state
    safety_result = check_safety(
        available=hypo_available,
        allocation=hypo_allocation,
        max_matrix=max_matrix,
        process_names=process_names,
        resource_names=resource_names,
    )

    if safety_result["is_safe"]:
        seq_str = " -> ".join(safety_result["safe_sequence"])
        return {
            "approved": True,
            "can_grant": True,
            "reason": f"Request can be safely granted immediately. Safe sequence remains: {seq_str}.",
            "hypothetical_available": hypo_available,
            "hypothetical_allocation": hypo_allocation,
            "safety_result": safety_result,
        }
    else:
        return {
            "approved": False,
            "can_grant": False,
            "reason": (
                f"Request cannot be granted: Granting resources to {p_name} leads to an UNSAFE STATE. "
                f"Process must wait to avoid deadlock."
            ),
            "hypothetical_available": hypo_available,
            "hypothetical_allocation": hypo_allocation,
            "safety_result": safety_result,
        }
