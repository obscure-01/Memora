"""
Algorithm Comparison Module.

Runs all three page replacement algorithms on the same input dataset
and produces a structured comparison of their performance.

Responsibilities:
    - Execute FIFO, LRU, and Optimal on identical page sequences.
    - Collect results into a unified comparison structure.
    - Identify the best-performing algorithm(s) (fewest page faults).
    - Support tied algorithms without arbitrarily selecting a single winner.
    - Prepare data in a format suitable for visualization and CSV export.
"""

from src.core.simulator import run_all_simulations
from src.core.metrics import compare_metrics


def compare_algorithms(page_sequence, frame_count):
    """
    Run all algorithms on the same input and return comparison results.

    Args:
        page_sequence (list[int]): Page reference sequence.
        frame_count (int): Number of memory frames.

    Returns:
        dict: Comparison result with structure:
            {
                "page_sequence": list[int],
                "frame_count": int,
                "results": [
                    { ... FIFO result ... },
                    { ... LRU result ... },
                    { ... Optimal result ... },
                ],
                "summary": {
                    "best_algorithm": str,
                    "best_algorithms": list[str],
                    "fewest_faults": int,
                    "comparison_table": list[dict]
                }
            }
    """
    results = run_all_simulations(page_sequence, frame_count)
    summary = compare_metrics(results)

    return {
        "page_sequence": list(page_sequence),
        "frame_count": frame_count,
        "results": results,
        "summary": summary,
    }
