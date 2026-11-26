"""
Performance Metrics Calculator.

Calculates and derives performance metrics from raw simulation results.

Responsibilities:
    - Count total page hits and page faults from simulation history.
    - Calculate hit ratio (hits / total accesses).
    - Calculate fault ratio (faults / total accesses).
    - Provide summary statistics for comparison across algorithms.

All ratios are returned as floats rounded to 4 decimal places.
"""


def calculate_metrics(simulation_result):
    """
    Calculate performance metrics from a simulation result.

    Derives hits, faults, hit_ratio, and fault_ratio from the "history" list.

    Args:
        simulation_result (dict): Result from an algorithm run,
            containing at minimum a "history" list of step records.

    Returns:
        dict: The simulation result dictionary updated with:
            - "hits" (int): Total page hits
            - "faults" (int): Total page faults
            - "hit_ratio" (float): hits / total_accesses (rounded to 4 decimal places)
            - "fault_ratio" (float): faults / total_accesses (rounded to 4 decimal places)

    Raises:
        ValueError: If simulation_result is not a dict or lacks a 'history' list.
    """
    if not isinstance(simulation_result, dict):
        raise ValueError(f"simulation_result must be a dict, got {type(simulation_result).__name__}")

    history = simulation_result.get("history")
    if not isinstance(history, list):
        raise ValueError("simulation_result must contain a 'history' list")

    total_accesses = len(history)
    hits = sum(1 for step in history if step.get("is_hit", False))
    faults = total_accesses - hits

    if total_accesses > 0:
        hit_ratio = round(hits / total_accesses, 4)
        fault_ratio = round(faults / total_accesses, 4)
    else:
        hit_ratio = 0.0
        fault_ratio = 0.0

    simulation_result["hits"] = hits
    simulation_result["faults"] = faults
    simulation_result["hit_ratio"] = hit_ratio
    simulation_result["fault_ratio"] = fault_ratio

    return simulation_result


def compare_metrics(results):
    """
    Generate a comparison summary across multiple algorithm results.

    Identifies the algorithm(s) with the minimum number of page faults.
    If multiple algorithms tie, reports all tied algorithms.

    Args:
        results (list[dict]): List of simulation results from different algorithms.

    Returns:
        dict: Comparison summary with:
            - "best_algorithm" (str): Name(s) of algorithm(s) with fewest faults
            - "best_algorithms" (list[str]): List of top-performing algorithm names
            - "fewest_faults" (int): Lowest fault count achieved
            - "comparison_table" (list[dict]): Per-algorithm metric rows

    Raises:
        ValueError: If results is empty or invalid.
    """
    if not results or not isinstance(results, list):
        raise ValueError("results must be a non-empty list of simulation result dictionaries")

    comparison_table = []
    min_faults = None

    for r in results:
        faults = r.get("faults", 0)
        hits = r.get("hits", 0)
        hit_ratio = r.get("hit_ratio", 0.0)
        fault_ratio = r.get("fault_ratio", 0.0)
        algo_name = r.get("algorithm", "Unknown")

        if min_faults is None or faults < min_faults:
            min_faults = faults

        comparison_table.append({
            "algorithm": algo_name,
            "hits": hits,
            "faults": faults,
            "hit_ratio": hit_ratio,
            "fault_ratio": fault_ratio,
        })

    best_algorithms = [
        r["algorithm"] for r in results if r.get("faults") == min_faults
    ]
    best_algorithm_str = ", ".join(best_algorithms) if len(best_algorithms) > 1 else best_algorithms[0]

    return {
        "best_algorithm": best_algorithm_str,
        "best_algorithms": best_algorithms,
        "fewest_faults": min_faults,
        "comparison_table": comparison_table,
    }
