"""
Simulation Engine.

Orchestrates the execution of page replacement algorithm simulations.
Acts as the central coordinator between user input, algorithm modules,
and result processing.

Responsibilities:
    - Validate inputs before simulation.
    - Dispatch to the requested algorithm module.
    - Collect and return structured simulation results.
    - Support running a single algorithm or all algorithms for comparison.
"""

from src.algorithms.fifo import run_fifo
from src.algorithms.lru import run_lru
from src.algorithms.optimal import run_optimal
from src.core.validator import validate_page_sequence, validate_frame_count


# Algorithm registry mapping canonical algorithm names to their run functions.
ALGORITHM_REGISTRY = {
    "FIFO": run_fifo,
    "LRU": run_lru,
    "Optimal": run_optimal,
}


def _resolve_algorithm_name(name):
    """Resolve algorithm name case-insensitively to its canonical key."""
    if not isinstance(name, str):
        return None
    normalized = name.strip().upper()
    for key in ALGORITHM_REGISTRY:
        if key.upper() == normalized:
            return key
    return None


def run_simulation(algorithm_name, page_sequence, frame_count):
    """
    Run a single page replacement algorithm simulation with input validation.

    Args:
        algorithm_name (str): Name of the algorithm ("FIFO", "LRU", or "Optimal").
        page_sequence (list[int]): Page reference sequence.
        frame_count (int): Positive frame count.

    Returns:
        dict: Standardized simulation result dictionary.

    Raises:
        ValueError: If input validation fails or algorithm is unrecognized.
    """
    seq_valid, seq_err = validate_page_sequence(page_sequence)
    if not seq_valid:
        raise ValueError(f"Invalid page sequence: {seq_err}")

    fc_valid, fc_err = validate_frame_count(frame_count)
    if not fc_valid:
        raise ValueError(f"Invalid frame count: {fc_err}")

    canonical_name = _resolve_algorithm_name(algorithm_name)
    if canonical_name is None:
        supported = ", ".join(ALGORITHM_REGISTRY.keys())
        raise ValueError(f"Unknown algorithm '{algorithm_name}'. Supported algorithms: {supported}")

    run_func = ALGORITHM_REGISTRY[canonical_name]
    return run_func(page_sequence, frame_count)


def run_all_simulations(page_sequence, frame_count):
    """
    Run all three algorithms on the same input for comparison.

    Args:
        page_sequence (list[int]): Page reference sequence.
        frame_count (int): Positive frame count.

    Returns:
        list[dict]: List of simulation results (FIFO, LRU, Optimal).

    Raises:
        ValueError: If input validation fails.
    """
    seq_valid, seq_err = validate_page_sequence(page_sequence)
    if not seq_valid:
        raise ValueError(f"Invalid page sequence: {seq_err}")

    fc_valid, fc_err = validate_frame_count(frame_count)
    if not fc_valid:
        raise ValueError(f"Invalid frame count: {fc_err}")

    results = []
    for name in ["FIFO", "LRU", "Optimal"]:
        run_func = ALGORITHM_REGISTRY[name]
        results.append(run_func(page_sequence, frame_count))

    return results
