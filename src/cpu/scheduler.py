"""
CPU Scheduling Orchestrator & Comparison Module.

Coordinates execution across FCFS, SJF, and Round Robin algorithms
and generates comparative performance summaries.
"""

from src.cpu.validator import validate_processes, validate_time_quantum
from src.cpu.fcfs import run_fcfs
from src.cpu.sjf import run_sjf
from src.cpu.round_robin import run_round_robin

CPU_ALGORITHM_REGISTRY = {
    "FCFS": run_fcfs,
    "SJF": run_sjf,
    "RR": run_round_robin,
    "ROUND_ROBIN": run_round_robin,
}


def _resolve_cpu_algorithm(name):
    """Normalize algorithm name case-insensitively."""
    if not isinstance(name, str):
        return None
    normalized = name.strip().upper()
    for key in CPU_ALGORITHM_REGISTRY:
        if key == normalized:
            return key
    return None


def run_cpu_scheduler(algorithm, processes, time_quantum=2):
    """
    Run a single CPU scheduling algorithm simulation with validation.

    Args:
        algorithm (str): Name of algorithm ("FCFS", "SJF", "RR").
        processes (list[dict]): Process list with 'id', 'arrival_time', 'burst_time'.
        time_quantum (int): Quantum for Round Robin (default: 2).

    Returns:
        dict: Standardized CPU scheduling result.

    Raises:
        ValueError: If validation fails or algorithm is unrecognized.
    """
    valid, err = validate_processes(processes)
    if not valid:
        raise ValueError(f"Invalid processes: {err}")

    canonical_key = _resolve_cpu_algorithm(algorithm)
    if canonical_key is None:
        supported = "FCFS, SJF, RR"
        raise ValueError(f"Unknown CPU algorithm '{algorithm}'. Supported: {supported}")

    if canonical_key in ("RR", "ROUND_ROBIN"):
        q_valid, q_err = validate_time_quantum(time_quantum)
        if not q_valid:
            raise ValueError(f"Invalid time quantum: {q_err}")
        return run_round_robin(processes, time_quantum=time_quantum)

    run_func = CPU_ALGORITHM_REGISTRY[canonical_key]
    return run_func(processes)


def compare_cpu_schedulers(processes, time_quantum=2):
    """
    Run FCFS, SJF, and Round Robin on identical process inputs and compare performance.

    Args:
        processes (list[dict]): Process list.
        time_quantum (int): Quantum for Round Robin.

    Returns:
        dict: Multi-algorithm comparison dictionary.
    """
    valid, err = validate_processes(processes)
    if not valid:
        raise ValueError(f"Invalid processes: {err}")

    q_valid, q_err = validate_time_quantum(time_quantum)
    if not q_valid:
        raise ValueError(f"Invalid time quantum: {q_err}")

    res_fcfs = run_fcfs(processes)
    res_sjf = run_sjf(processes)
    res_rr = run_round_robin(processes, time_quantum=time_quantum)

    results_map = {
        "FCFS": res_fcfs,
        "SJF": res_sjf,
        "RR": res_rr,
    }

    comparison_rows = []
    for key in ["FCFS", "SJF", "RR"]:
        res = results_map[key]
        m = res["metrics"]
        comparison_rows.append({
            "algorithm": key,
            "algorithm_name": res["algorithm_name"],
            "avg_waiting_time": m["avg_waiting_time"],
            "avg_turnaround_time": m["avg_turnaround_time"],
            "avg_response_time": m["avg_response_time"],
            "cpu_utilization": m["cpu_utilization"],
            "throughput": m["throughput"],
            "total_time": m["total_time"],
        })

    # Best algorithm is typically judged by minimum average waiting time
    min_awt = min(row["avg_waiting_time"] for row in comparison_rows)
    best_wt_algos = [row["algorithm"] for row in comparison_rows if row["avg_waiting_time"] == min_awt]

    min_atat = min(row["avg_turnaround_time"] for row in comparison_rows)
    best_tat_algos = [row["algorithm"] for row in comparison_rows if row["avg_turnaround_time"] == min_atat]

    return {
        "processes": processes,
        "time_quantum": time_quantum,
        "results": results_map,
        "comparison_table": comparison_rows,
        "summary": {
            "best_waiting_time_algorithm": ", ".join(best_wt_algos),
            "lowest_avg_waiting_time": min_awt,
            "best_turnaround_time_algorithm": ", ".join(best_tat_algos),
            "lowest_avg_turnaround_time": min_atat,
        },
    }
