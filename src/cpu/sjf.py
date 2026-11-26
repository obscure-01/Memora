"""
Shortest Job First (SJF) CPU Scheduling Algorithm (Non-Preemptive).

Selects the waiting process with the smallest CPU burst time.
Once scheduled, the process runs to completion without preemption.
"""

from src.cpu.metrics import compute_schedule_metrics


def run_sjf(processes):
    """
    Simulate Non-Preemptive Shortest Job First (SJF) scheduling.

    Args:
        processes (list[dict]): Process definitions with 'id', 'arrival_time', 'burst_time'.

    Returns:
        dict: Standardized CPU scheduling result dictionary.
    """
    remaining = [dict(p) for p in processes]
    current_time = 0
    gantt_chart = []
    completed_records = []

    while remaining:
        # Find all processes that have arrived by current_time
        ready_pool = [p for p in remaining if p["arrival_time"] <= current_time]

        if not ready_pool:
            # CPU is idle until the next earliest arrival
            next_arrival = min(p["arrival_time"] for p in remaining)
            gantt_chart.append({
                "process": "IDLE",
                "start": current_time,
                "end": next_arrival,
            })
            current_time = next_arrival
            ready_pool = [p for p in remaining if p["arrival_time"] <= current_time]

        # Select process with shortest burst time.
        # Deterministic tie-breaking: burst_time ASC, arrival_time ASC, id ASC
        selected = min(
            ready_pool,
            key=lambda x: (x["burst_time"], x["arrival_time"], str(x["id"]))
        )

        remaining.remove(selected)

        p_id = str(selected["id"])
        at = selected["arrival_time"]
        bt = selected["burst_time"]

        start_time = current_time
        end_time = start_time + bt
        current_time = end_time

        gantt_chart.append({
            "process": p_id,
            "start": start_time,
            "end": end_time,
        })

        completed_records.append({
            "id": p_id,
            "arrival_time": at,
            "burst_time": bt,
            "completion_time": end_time,
            "first_start_time": start_time,
        })

    metrics = compute_schedule_metrics(completed_records, gantt_chart, current_time)

    return {
        "algorithm": "SJF",
        "algorithm_name": "Shortest Job First (Non-Preemptive)",
        "is_preemptive": False,
        "processes": metrics["processes"],
        "gantt_chart": gantt_chart,
        "metrics": metrics,
    }
