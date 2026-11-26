"""
CPU Scheduling Metrics Calculator.

Computes standard Operating Systems CPU scheduling performance metrics:
    - Turnaround Time (TAT) = Completion Time (CT) - Arrival Time (AT)
    - Waiting Time (WT)     = Turnaround Time (TAT) - Burst Time (BT)
    - Response Time (RT)    = First CPU Allocation Time - Arrival Time (AT)
    - Average Turnaround Time, Average Waiting Time, Average Response Time
    - CPU Utilization (%)   = (Busy Time / Total Simulation Time) * 100
    - Throughput            = Number of Completed Processes / Total Simulation Time
"""


def compute_schedule_metrics(processes_schedule, gantt_chart, total_simulation_time):
    """
    Compute process-level and aggregate CPU scheduling metrics.

    Args:
        processes_schedule (list[dict]): Process results containing:
            "id", "arrival_time", "burst_time", "completion_time", "first_start_time".
        gantt_chart (list[dict]): Timeline segments [{"process": "P1", "start": 0, "end": 4}, ...].
        total_simulation_time (int): Final simulation clock time.

    Returns:
        dict: Standardized metrics dictionary.
    """
    if not processes_schedule:
        return {
            "processes": [],
            "total_time": 0,
            "busy_time": 0,
            "idle_time": 0,
            "cpu_utilization": 0.0,
            "throughput": 0.0,
            "avg_turnaround_time": 0.0,
            "avg_waiting_time": 0.0,
            "avg_response_time": 0.0,
        }

    total_tat = 0
    total_wt = 0
    total_rt = 0
    total_bt = sum(p["burst_time"] for p in processes_schedule)

    enriched_processes = []

    for p in processes_schedule:
        p_id = str(p["id"])
        at = p["arrival_time"]
        bt = p["burst_time"]
        ct = p["completion_time"]
        first_start = p.get("first_start_time", at)

        tat = ct - at
        wt = tat - bt
        rt = first_start - at

        # Waiting time safety check
        if wt < 0:
            wt = 0

        total_tat += tat
        total_wt += wt
        total_rt += rt

        enriched_processes.append({
            "id": p_id,
            "arrival_time": at,
            "burst_time": bt,
            "completion_time": ct,
            "turnaround_time": tat,
            "waiting_time": wt,
            "response_time": rt,
        })

    # Sort enriched processes consistently by Process ID or Arrival Time
    enriched_processes.sort(key=lambda x: str(x["id"]))

    n = len(processes_schedule)
    idle_time = sum(seg["end"] - seg["start"] for seg in gantt_chart if seg["process"] == "IDLE")
    busy_time = total_bt

    if total_simulation_time > 0:
        cpu_utilization = round((busy_time / total_simulation_time) * 100, 2)
        throughput = round(n / total_simulation_time, 4)
    else:
        cpu_utilization = 100.0
        throughput = 0.0

    return {
        "processes": enriched_processes,
        "total_time": total_simulation_time,
        "busy_time": busy_time,
        "idle_time": idle_time,
        "cpu_utilization": cpu_utilization,
        "throughput": throughput,
        "avg_turnaround_time": round(total_tat / n, 2),
        "avg_waiting_time": round(total_wt / n, 2),
        "avg_response_time": round(total_rt / n, 2),
    }
