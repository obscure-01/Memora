"""
First-Come, First-Served (FCFS) CPU Scheduling Algorithm.

Non-preemptive scheduling where the CPU is allocated to processes in
strict order of their arrival in the ready queue.
"""

from src.cpu.metrics import compute_schedule_metrics


def run_fcfs(processes):
    """
    Simulate First-Come, First-Served (FCFS) CPU scheduling.

    Args:
        processes (list[dict]): Process definitions with 'id', 'arrival_time', 'burst_time'.

    Returns:
        dict: Standardized CPU scheduling result dictionary containing:
            "algorithm": "FCFS",
            "gantt_chart": list[dict],
            "metrics": dict
    """
    # Create sorted copy: arrival time ascending, deterministic tie-breaking on process ID
    proc_list = sorted(
        [dict(p) for p in processes],
        key=lambda x: (x["arrival_time"], str(x["id"]))
    )

    current_time = 0
    gantt_chart = []
    completed_records = []

    for p in proc_list:
        p_id = str(p["id"])
        at = p["arrival_time"]
        bt = p["burst_time"]

        # If CPU is idle before process arrives
        if current_time < at:
            gantt_chart.append({
                "process": "IDLE",
                "start": current_time,
                "end": at,
            })
            current_time = at

        first_start = current_time
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
            "first_start_time": first_start,
        })

    metrics = compute_schedule_metrics(completed_records, gantt_chart, current_time)

    return {
        "algorithm": "FCFS",
        "algorithm_name": "First Come First Serve",
        "is_preemptive": False,
        "processes": metrics["processes"],
        "gantt_chart": gantt_chart,
        "metrics": metrics,
    }
