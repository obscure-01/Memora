"""
Round Robin (RR) CPU Scheduling Algorithm.

Preemptive scheduling where each ready process is allocated a fixed time quantum.
If a process does not complete within its quantum, it is preempted and re-queued.
"""

from collections import deque
from src.cpu.metrics import compute_schedule_metrics


def run_round_robin(processes, time_quantum=2):
    """
    Simulate Round Robin (RR) CPU scheduling with a specified time quantum.

    Args:
        processes (list[dict]): Process definitions with 'id', 'arrival_time', 'burst_time'.
        time_quantum (int): Time slice quantum (strictly positive integer).

    Returns:
        dict: Standardized CPU scheduling result dictionary.
    """
    if time_quantum <= 0:
        raise ValueError(f"Time quantum must be strictly positive, got {time_quantum}.")

    # Deep copy and initialize tracking fields
    unallocated = sorted(
        [
            {
                "id": str(p["id"]),
                "arrival_time": p["arrival_time"],
                "burst_time": p["burst_time"],
                "remaining_burst": p["burst_time"],
            }
            for p in processes
        ],
        key=lambda x: (x["arrival_time"], str(x["id"]))
    )

    current_time = 0
    ready_queue = deque()
    gantt_chart = []
    completed_records = []
    first_start_times = {}

    # If the earliest arrival is in the future (> 0), start with IDLE
    if unallocated and unallocated[0]["arrival_time"] > 0:
        first_arrival = unallocated[0]["arrival_time"]
        gantt_chart.append({
            "process": "IDLE",
            "start": 0,
            "end": first_arrival,
        })
        current_time = first_arrival

    # Enqueue processes arrived at or before initial current_time
    i = 0
    while i < len(unallocated) and unallocated[i]["arrival_time"] <= current_time:
        ready_queue.append(unallocated[i])
        i += 1
    unallocated = unallocated[i:]

    while ready_queue or unallocated:
        if not ready_queue:
            # CPU is idle waiting for the next arriving process
            next_arrival = unallocated[0]["arrival_time"]
            gantt_chart.append({
                "process": "IDLE",
                "start": current_time,
                "end": next_arrival,
            })
            current_time = next_arrival

            # Enqueue all processes arrived by new current_time
            i = 0
            while i < len(unallocated) and unallocated[i]["arrival_time"] <= current_time:
                ready_queue.append(unallocated[i])
                i += 1
            unallocated = unallocated[i:]

        # Pop the next ready process
        curr = ready_queue.popleft()
        p_id = curr["id"]

        # Record first CPU allocation time for response time
        if p_id not in first_start_times:
            first_start_times[p_id] = current_time

        # Run for either the full quantum or remaining burst time
        run_duration = min(time_quantum, curr["remaining_burst"])
        start_time = current_time
        end_time = start_time + run_duration
        current_time = end_time

        # Update Gantt timeline (merge with previous segment if same process continues)
        if gantt_chart and gantt_chart[-1]["process"] == p_id and gantt_chart[-1]["end"] == start_time:
            gantt_chart[-1]["end"] = end_time
        else:
            gantt_chart.append({
                "process": p_id,
                "start": start_time,
                "end": end_time,
            })

        curr["remaining_burst"] -= run_duration

        # Textbook order: Check for newly arrived processes during this time slice
        # BEFORE re-queuing the current process.
        arrived_during_slice = []
        i = 0
        while i < len(unallocated) and unallocated[i]["arrival_time"] <= current_time:
            arrived_during_slice.append(unallocated[i])
            i += 1
        unallocated = unallocated[i:]

        # Append newly arrived processes to ready queue
        for new_p in arrived_during_slice:
            ready_queue.append(new_p)

        # If current process is not finished, re-enqueue at the end
        if curr["remaining_burst"] > 0:
            ready_queue.append(curr)
        else:
            # Process finished
            completed_records.append({
                "id": p_id,
                "arrival_time": curr["arrival_time"],
                "burst_time": curr["burst_time"],
                "completion_time": current_time,
                "first_start_time": first_start_times[p_id],
            })

    metrics = compute_schedule_metrics(completed_records, gantt_chart, current_time)

    return {
        "algorithm": "RR",
        "algorithm_name": f"Round Robin (Quantum = {time_quantum})",
        "is_preemptive": True,
        "time_quantum": time_quantum,
        "processes": metrics["processes"],
        "gantt_chart": gantt_chart,
        "metrics": metrics,
    }
