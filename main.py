"""
Memora — Integrated Operating Systems Resource Management Simulator

Provides an interactive CLI and command-line interface for simulating,
analyzing, and evaluating three foundational OS resource-management functions:
    1. Virtual Memory Management (FIFO, LRU, Optimal Page Replacement)
    2. CPU Scheduling (FCFS, Non-Preemptive SJF, Round Robin with Time Quantum)
    3. Deadlock Management (Banker's Algorithm: Safety Check & Resource Requests)
"""

import argparse
import json
import os
import sys

# Module 1: Virtual Memory imports
from src.core.simulator import run_simulation, run_all_simulations, ALGORITHM_REGISTRY
from src.analysis.comparison import compare_algorithms
from src.analysis.visualization import (
    plot_fault_comparison,
    plot_hit_ratio_comparison,
    plot_comparison_chart,
    plot_cpu_gantt_chart,
    plot_cpu_comparison_chart,
    HAS_MATPLOTLIB,
)
from src.utils.file_handler import (
    load_dataset,
    export_results_csv,
    ensure_output_directories,
    DATASETS_DIR,
)
from src.core.validator import validate_page_sequence, validate_frame_count

# Module 2: CPU Scheduling imports
from src.cpu.scheduler import run_cpu_scheduler, compare_cpu_schedulers
from src.cpu.validator import validate_processes

# Module 3: Deadlock Management imports
from src.deadlock.bankers import (
    check_safety,
    simulate_resource_request,
    compute_need_matrix,
)
from src.deadlock.validator import validate_bankers_input

# Standard textbook reference test sequences
REFERENCE_SEQUENCE = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
REFERENCE_FRAMES = 3


def print_banner():
    """Print the unified application banner."""
    print("=" * 72)
    print("        MEMORA — OPERATING SYSTEMS RESOURCE-MANAGEMENT SIMULATOR")
    print("   Memory Management  |  CPU Scheduling  |  Deadlock Avoidance")
    print("=" * 72)


# =============================================================================
# MODULE 1: VIRTUAL MEMORY CLI FLOWS
# =============================================================================

def print_simulation_table(result):
    """Print formatted step-by-step memory state table for a simulation result."""
    algo = result.get("algorithm", "Unknown")
    frame_count = result.get("frame_count", 0)
    history = result.get("history", [])

    print("\n" + "-" * 66)
    print(f"  SIMULATION EXECUTION TRACE: {algo} (Frames = {frame_count})")
    print("-" * 66)

    header = f"{'Step':<6}{'Page':<8}"
    for f in range(frame_count):
        header += f"{'Frame ' + str(f):<10}"
    header += f"{'Status':<10}{'Evicted':<8}"
    print(header)
    print("-" * len(header))

    for item in history:
        step = item.get("step", 0)
        page = item.get("page", 0)
        frames = item.get("frames", [])
        is_hit = item.get("is_hit", False)
        evicted = item.get("evicted")

        status_str = "HIT" if is_hit else "FAULT"
        evicted_str = str(evicted) if evicted is not None else "-"

        row = f"{step:<6}{page:<8}"
        for f in range(frame_count):
            val = frames[f] if f < len(frames) and frames[f] is not None else "-"
            row += f"{str(val):<10}"
        row += f"{status_str:<10}{evicted_str:<8}"
        print(row)

    print("-" * len(header))
    print(f"  Total Accesses : {len(history)}")
    print(f"  Page Hits      : {result.get('hits', 0)}")
    print(f"  Page Faults    : {result.get('faults', 0)}")
    print(f"  Hit Ratio      : {result.get('hit_ratio', 0.0) * 100:.2f}%")
    print(f"  Fault Ratio    : {result.get('fault_ratio', 0.0) * 100:.2f}%")
    print("-" * 66)


def print_comparison_table(comparison_result):
    """Print side-by-side comparison table of algorithm performance."""
    results = comparison_result.get("results", [])
    summary = comparison_result.get("summary", {})
    frame_count = comparison_result.get("frame_count", 0)
    total_accesses = len(comparison_result.get("page_sequence", []))

    print("\n" + "=" * 66)
    print(f"  PAGE REPLACEMENT COMPARISON (Frames = {frame_count}, Accesses = {total_accesses})")
    print("=" * 66)

    header = f"{'Algorithm':<14}{'Hits':<10}{'Faults':<10}{'Hit Ratio':<14}{'Fault Ratio':<14}"
    print(header)
    print("-" * len(header))

    for r in results:
        algo = r.get("algorithm", "Unknown")
        hits = r.get("hits", 0)
        faults = r.get("faults", 0)
        hit_ratio = r.get("hit_ratio", 0.0) * 100
        fault_ratio = r.get("fault_ratio", 0.0) * 100
        print(f"{algo:<14}{hits:<10}{faults:<10}{hit_ratio:>6.2f}%{' ':>7}{fault_ratio:>6.2f}%{' ':>7}")

    print("-" * len(header))
    best_algo = summary.get("best_algorithm", "Unknown")
    fewest = summary.get("fewest_faults", 0)
    print(f"  Best Algorithm(s) (Fewest Faults): {best_algo} ({fewest} faults)")
    print("=" * 66)


def prompt_page_sequence():
    """Prompt user to enter a page reference sequence."""
    while True:
        raw = input("\nEnter page sequence (comma or space separated, e.g. 7, 0, 1, 2): ").strip()
        if not raw:
            print("  [Error] Page sequence cannot be empty.")
            continue
        parts = raw.replace(",", " ").split()
        try:
            pages = [int(p) for p in parts]
        except ValueError:
            print("  [Error] All page values must be integers.")
            continue

        valid, err = validate_page_sequence(pages)
        if not valid:
            print(f"  [Error] {err}")
            continue

        return pages


def prompt_frame_count():
    """Prompt user to enter memory frame count."""
    while True:
        raw = input("Enter number of memory frames (positive integer, e.g. 3): ").strip()
        try:
            fc = int(raw)
        except ValueError:
            print("  [Error] Frame count must be an integer.")
            continue

        valid, err = validate_frame_count(fc)
        if not valid:
            print(f"  [Error] {err}")
            continue

        return fc


def run_single_algorithm_flow(algo_name):
    """Workflow to run and display a single memory algorithm simulation."""
    print(f"\n--- Running {algo_name} Simulation ---")
    pages = prompt_page_sequence()
    fc = prompt_frame_count()

    result = run_simulation(algo_name, pages, fc)
    print_simulation_table(result)
    return result


def run_comparison_flow(pages=None, fc=None):
    """Workflow to run all three page replacement algorithms and compare."""
    print("\n--- Running Algorithm Comparison (FIFO vs. LRU vs. Optimal) ---")
    if pages is None:
        pages = prompt_page_sequence()
    if fc is None:
        fc = prompt_frame_count()

    comparison = compare_algorithms(pages, fc)
    print_comparison_table(comparison)

    print("\nVisualization & Export Options:")
    gen_charts = input("  Generate Matplotlib comparison charts? (y/n) [default: y]: ").strip().lower()
    if gen_charts != "n":
        try:
            f_chart = plot_fault_comparison(comparison)
            s_chart = plot_comparison_chart(comparison)
            h_chart = plot_hit_ratio_comparison(comparison)
            print(f"  [OK] Saved fault chart:       {f_chart}")
            print(f"  [OK] Saved summary chart:     {s_chart}")
            print(f"  [OK] Saved hit ratio chart:   {h_chart}")
        except Exception as e:
            print(f"  [Notice] Chart generation unavailable: {e}")

    exp_csv = input("  Export results to CSV? (y/n) [default: y]: ").strip().lower()
    if exp_csv != "n":
        csv_path = export_results_csv(comparison)
        print(f"  [OK] Saved CSV report:        {csv_path}")

    return comparison


def load_dataset_flow():
    """Workflow to load predefined sample datasets for memory."""
    sample_file = os.path.join(DATASETS_DIR, "sample_input.json")
    try:
        data = load_dataset(sample_file)
        datasets = data.get("datasets", [])
    except Exception as e:
        print(f"  [Error] Could not load datasets: {e}")
        return

    print("\n--- Available Memory Datasets ---")
    for idx, ds in enumerate(datasets, 1):
        name = ds.get("name", "Unknown")
        fc = ds.get("frame_count", "?")
        pages = ds.get("page_sequence", [])
        purpose = ds.get("purpose", "")
        print(f"  {idx}. {name:<26} (Frames: {fc}, Length: {len(pages)}) — {purpose}")

    choice = input("\nSelect dataset number to simulate (or press Enter to cancel): ").strip()
    if not choice:
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(datasets):
            selected = datasets[idx]
            pages = selected["page_sequence"]
            fc = selected["frame_count"]
            print(f"\n[Loaded] {selected['name']}: {pages} (Frames: {fc})")
            run_comparison_flow(pages, fc)
        else:
            print("  [Error] Selection out of range.")
    except ValueError:
        print("  [Error] Please enter a valid number.")


def run_reference_case_flow():
    """Workflow to run the standard reference test case and demonstrate all 3 algorithms."""
    print("\n--- Running Reference Memory Case ---")
    print(f"  Page Sequence : {REFERENCE_SEQUENCE}")
    print(f"  Frame Count   : {REFERENCE_FRAMES}")
    print("\nSimulating all three algorithms...")

    comparison = compare_algorithms(REFERENCE_SEQUENCE, REFERENCE_FRAMES)

    for r in comparison["results"]:
        print_simulation_table(r)

    print_comparison_table(comparison)

    try:
        f_chart = plot_fault_comparison(comparison)
        s_chart = plot_comparison_chart(comparison)
        csv_path = export_results_csv(comparison)
        print(f"\n[Auto-Generated Demonstration Artifacts]")
        print(f"  - Chart (Faults):  {f_chart}")
        print(f"  - Chart (Summary): {s_chart}")
        print(f"  - Report (CSV):    {csv_path}")
    except Exception as e:
        print(f"  [Notice] Visualization notice: {e}")


def memory_module_menu():
    """Interactive submenu for Virtual Memory Management."""
    while True:
        print("\n" + "=" * 66)
        print("     MODULE 1: VIRTUAL MEMORY MANAGEMENT (PAGE REPLACEMENT)")
        print("=" * 66)
        print("  1. Run FIFO Page Replacement")
        print("  2. Run LRU Page Replacement")
        print("  3. Run Optimal Page Replacement")
        print("  4. Compare All Three Algorithms (Side-by-Side)")
        print("  5. Load Predefined Sample Dataset")
        print("  6. Run Reference Test Case (Standard Viva Demo)")
        print("  7. Return to Top-Level Menu")
        print("=" * 66)

        choice = input("Enter choice (1-7): ").strip()
        if choice == "1":
            run_single_algorithm_flow("FIFO")
        elif choice == "2":
            run_single_algorithm_flow("LRU")
        elif choice == "3":
            run_single_algorithm_flow("Optimal")
        elif choice == "4":
            run_comparison_flow()
        elif choice == "5":
            load_dataset_flow()
        elif choice == "6":
            run_reference_case_flow()
        elif choice == "7":
            break
        else:
            print("  [Invalid Selection] Please choose between 1 and 7.")


# =============================================================================
# MODULE 2: CPU SCHEDULING CLI FLOWS
# =============================================================================

def print_cpu_gantt_text(gantt_chart):
    """Print ASCII Gantt timeline representation."""
    print("\n  Gantt Chart Timeline:")
    timeline_top = "  +"
    timeline_mid = "  |"
    timeline_bot = "  0"

    for seg in gantt_chart:
        pid = seg.get("process") or seg.get("process_id") or "IDLE"
        start = seg.get("start") if "start" in seg else seg.get("start_time", 0)
        end = seg.get("end") if "end" in seg else seg.get("end_time", 0)
        width = max(len(pid) + 2, (end - start) * 2)

        timeline_top += "-" * width + "+"
        timeline_mid += f"{pid:^{width}}|"
        timeline_bot += f"{end:>{width + 1}}"

    print(timeline_top)
    print(timeline_mid)
    print(timeline_top)
    print(timeline_bot)


def print_cpu_schedule_table(result):
    """Print detailed CPU schedule execution table and summary metrics."""
    algo = result.get("algorithm_name") or result.get("algorithm", "Unknown")
    processes = result.get("processes", [])
    gantt = result.get("gantt_chart", [])
    metrics = result.get("metrics", {})

    print("\n" + "=" * 68)
    print(f"  CPU SCHEDULING SIMULATION: {algo}")
    print("=" * 68)

    print_cpu_gantt_text(gantt)

    print("\n  Process Metrics Table:")
    header = f"  {'PID':<8}{'Arrival':<10}{'Burst':<10}{'Completion':<14}{'TAT':<8}{'WT':<8}{'RT':<8}"
    print(header)
    print("  " + "-" * (len(header) - 2))

    for p in processes:
        pid = p["id"]
        at = p["arrival_time"]
        bt = p["burst_time"]
        ct = p["completion_time"]
        tat = p["turnaround_time"]
        wt = p["waiting_time"]
        rt = p["response_time"]
        print(f"  {pid:<8}{at:<10}{bt:<10}{ct:<14}{tat:<8}{wt:<8}{rt:<8}")

    print("  " + "-" * (len(header) - 2))
    print(f"  Average Waiting Time (AWT)       : {metrics.get('avg_waiting_time', 0):.2f}")
    print(f"  Average Turnaround Time (ATAT)   : {metrics.get('avg_turnaround_time', 0):.2f}")
    print(f"  Average Response Time (ART)      : {metrics.get('avg_response_time', 0):.2f}")
    print(f"  CPU Utilization                  : {metrics.get('cpu_utilization', 0):.2f}%")
    print(f"  System Throughput                : {metrics.get('throughput', 0):.4f} proc/unit time")
    print("=" * 68)


def print_cpu_comparison_table(comparison_result):
    """Print side-by-side comparison of CPU scheduling algorithms."""
    results = comparison_result.get("results", {})
    summary = comparison_result.get("summary", {})

    print("\n" + "=" * 70)
    print("  CPU SCHEDULING ALGORITHM COMPARISON SUMMARY")
    print("=" * 70)

    header = f"  {'Algorithm':<14}{'AWT':<10}{'ATAT':<10}{'ART':<10}{'CPU Util (%)':<14}{'Throughput':<12}"
    print(header)
    print("  " + "-" * (len(header) - 2))

    for algo_name, res in results.items():
        m = res.get("metrics", {})
        awt = m.get("avg_waiting_time", 0.0)
        atat = m.get("avg_turnaround_time", 0.0)
        art = m.get("avg_response_time", 0.0)
        util = m.get("cpu_utilization", 0.0)
        tp = m.get("throughput", 0.0)
        print(f"  {algo_name:<14}{awt:<10.2f}{atat:<10.2f}{art:<10.2f}{util:<14.2f}{tp:<12.4f}")

    print("  " + "-" * (len(header) - 2))
    best_wt_algo = summary.get("best_waiting_time_algorithm", "Unknown")
    min_awt = summary.get("lowest_avg_waiting_time", 0.0)
    best_tat_algo = summary.get("best_turnaround_time_algorithm", "Unknown")
    min_atat = summary.get("lowest_avg_turnaround_time", 0.0)
    print(f"  Lowest Waiting Time (Best AWT)    : {best_wt_algo} ({min_awt:.2f})")
    print(f"  Lowest Turnaround Time (Best ATAT): {best_tat_algo} ({min_atat:.2f})")
    print("=" * 70)


def prompt_cpu_processes():
    """Prompt user to input CPU process list."""
    print("\nEnter processes (format: ID Arrival Burst, e.g. 'P1 0 5'). Enter blank line when done:")
    processes = []
    idx = 1
    while True:
        line = input(f"  Process {idx} [or press Enter to finish]: ").strip()
        if not line:
            if processes:
                break
            print("  [Error] At least one process is required.")
            continue
        parts = line.split()
        if len(parts) == 2:
            # Assume ID is auto P{idx}
            pid = f"P{idx}"
            try:
                at = int(parts[0])
                bt = int(parts[1])
            except ValueError:
                print("  [Error] Arrival and burst times must be integers.")
                continue
        elif len(parts) >= 3:
            pid = parts[0]
            try:
                at = int(parts[1])
                bt = int(parts[2])
            except ValueError:
                print("  [Error] Arrival and burst times must be integers.")
                continue
        else:
            print("  [Error] Enter either 'Arrival Burst' or 'PID Arrival Burst'.")
            continue

        processes.append({"id": pid, "arrival_time": at, "burst_time": bt})
        idx += 1

    return processes


def load_cpu_dataset_flow():
    """Load CPU scheduling workloads from dataset."""
    cpu_file = os.path.join(DATASETS_DIR, "cpu_scheduling_samples.json")
    if not os.path.exists(cpu_file):
        print("  [Error] CPU sample dataset not found.")
        return None, 2

    with open(cpu_file, "r") as f:
        data = json.load(f)

    workloads = data.get("workloads", [])
    print("\n--- Available CPU Workload Datasets ---")
    for idx, wl in enumerate(workloads, 1):
        name = wl.get("name", "Unknown")
        tq = wl.get("time_quantum", 2)
        desc = wl.get("description", "")
        procs = len(wl.get("processes", []))
        print(f"  {idx}. {name:<32} (Procs: {procs}, TQ: {tq}) — {desc}")

    choice = input("\nSelect workload number (or press Enter to cancel): ").strip()
    if not choice:
        return None, 2

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(workloads):
            selected = workloads[idx]
            return selected["processes"], selected.get("time_quantum", 2)
        else:
            print("  [Error] Selection out of range.")
            return None, 2
    except ValueError:
        print("  [Error] Please enter a valid number.")
        return None, 2


def cpu_module_menu():
    """Interactive submenu for CPU Scheduling."""
    while True:
        print("\n" + "=" * 66)
        print("     MODULE 2: CPU SCHEDULING ALGORITHMS (FCFS, SJF, RR)")
        print("=" * 66)
        print("  1. Run First-Come First-Served (FCFS)")
        print("  2. Run Shortest Job First (SJF - Non-Preemptive)")
        print("  3. Run Round Robin (RR)")
        print("  4. Compare All Three CPU Schedulers")
        print("  5. Load Predefined Workload Dataset")
        print("  6. Return to Top-Level Menu")
        print("=" * 66)

        choice = input("Enter choice (1-6): ").strip()
        if choice in ["1", "2", "3"]:
            algo_map = {"1": "FCFS", "2": "SJF", "3": "RR"}
            algo = algo_map[choice]
            processes = prompt_cpu_processes()
            tq = 2
            if algo == "RR":
                try:
                    raw_tq = input("Enter Time Quantum (positive integer, e.g. 2): ").strip()
                    tq = int(raw_tq) if raw_tq else 2
                except ValueError:
                    tq = 2
            try:
                res = run_cpu_scheduler(algo, processes, time_quantum=tq)
                print_cpu_schedule_table(res)
            except Exception as e:
                print(f"  [Error] Simulation failed: {e}")

        elif choice == "4":
            processes = prompt_cpu_processes()
            try:
                raw_tq = input("Enter Round Robin Time Quantum [default 2]: ").strip()
                tq = int(raw_tq) if raw_tq else 2
            except ValueError:
                tq = 2
            try:
                comp = compare_cpu_schedulers(processes, time_quantum=tq)
                print_cpu_comparison_table(comp)

                gen_charts = input("\n  Generate Matplotlib comparison & Gantt charts? (y/n) [default: y]: ").strip().lower()
                if gen_charts != "n":
                    g_chart = plot_cpu_gantt_chart(comp["results"]["FCFS"])
                    c_chart = plot_cpu_comparison_chart(comp)
                    print(f"  [OK] Saved CPU Gantt chart:       {g_chart}")
                    print(f"  [OK] Saved CPU Comparison chart:  {c_chart}")
            except Exception as e:
                print(f"  [Error] Comparison failed: {e}")

        elif choice == "5":
            procs, tq = load_cpu_dataset_flow()
            if procs:
                comp = compare_cpu_schedulers(procs, time_quantum=tq)
                print_cpu_comparison_table(comp)
        elif choice == "6":
            break
        else:
            print("  [Invalid Selection] Please choose between 1 and 6.")


# =============================================================================
# MODULE 3: DEADLOCK MANAGEMENT CLI FLOWS
# =============================================================================

def print_bankers_matrices(available, allocation, max_matrix, need_matrix, process_names, resource_names):
    """Print Allocation, Max, Need matrices and Available vector side-by-side."""
    p_names = process_names or [f"P{i}" for i in range(len(allocation))]
    r_names = resource_names or [chr(ord('A') + j) for j in range(len(available))]

    res_header = " ".join(f"{r:>2}" for r in r_names)
    print("\n" + "=" * 70)
    print(f"  BANKER'S SYSTEM STATE SNAPSHOT")
    print("=" * 70)
    print(f"  Available Resources: {'  '.join(f'{r_names[j]}={available[j]}' for j in range(len(available)))}")
    print("-" * 70)
    print(f"  {'Process':<10} | {'Allocation':<14} | {'Maximum':<14} | {'Need':<14}")
    print(f"  {'':<10} | {res_header:<14} | {res_header:<14} | {res_header:<14}")
    print("  " + "-" * 66)

    for i in range(len(allocation)):
        alloc_str = " ".join(f"{allocation[i][j]:>2}" for j in range(len(available)))
        max_str = " ".join(f"{max_matrix[i][j]:>2}" for j in range(len(available)))
        need_str = " ".join(f"{need_matrix[i][j]:>2}" for j in range(len(available)))
        print(f"  {p_names[i]:<10} | {alloc_str:<14} | {max_str:<14} | {need_str:<14}")

    print("=" * 70)


def print_bankers_safety_result(safety_eval):
    """Print Banker's safety trace and execution order."""
    is_safe = safety_eval.get("is_safe", False)
    seq = safety_eval.get("safe_sequence", [])
    steps = safety_eval.get("steps", [])
    exp = safety_eval.get("explanation", "")

    print("\n" + "=" * 70)
    if is_safe:
        print("  STATUS: [SAFE STATE] — System is verified to be in a SAFE state.")
        print(f"  Safe Execution Sequence: {' -> '.join(seq)}")
    else:
        print("  STATUS: [UNSAFE STATE] — Deadlock avoidance cannot be guaranteed.")
    print("=" * 70)

    print("\n  Step-by-Step Allocation Trace:")
    header = f"  {'Step':<6}{'Process':<10}{'Work Before':<16}{'Need':<14}{'Allocation':<14}{'Work After':<16}"
    print(header)
    print("  " + "-" * (len(header) - 2))

    for s in steps:
        step_num = s["step"]
        proc = s["process"]
        wb = str(s["work_before"])
        nd = str(s["need"])
        al = str(s["allocation"])
        wa = str(s["work_after"])
        print(f"  {step_num:<6}{proc:<10}{wb:<16}{nd:<14}{al:<14}{wa:<16}")

    print("  " + "-" * (len(header) - 2))
    print(f"\n  Academic Explanation:\n  {exp}")
    print("=" * 70)


def load_deadlock_dataset_flow():
    """Load Deadlock scenarios from dataset."""
    dl_file = os.path.join(DATASETS_DIR, "deadlock_samples.json")
    if not os.path.exists(dl_file):
        print("  [Error] Deadlock sample dataset not found.")
        return None

    with open(dl_file, "r") as f:
        data = json.load(f)

    scenarios = data.get("scenarios", [])
    print("\n--- Available Deadlock Scenarios ---")
    for idx, sc in enumerate(scenarios, 1):
        name = sc.get("name", "Unknown")
        expected = sc.get("expected_state", "")
        desc = sc.get("description", "")
        print(f"  {idx}. {name:<36} [{expected}] — {desc}")

    choice = input("\nSelect scenario number (or press Enter to cancel): ").strip()
    if not choice:
        return None

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(scenarios):
            return scenarios[idx]
        else:
            print("  [Error] Selection out of range.")
            return None
    except ValueError:
        print("  [Error] Please enter a valid number.")
        return None


def deadlock_module_menu():
    """Interactive submenu for Deadlock Management."""
    while True:
        print("\n" + "=" * 66)
        print("     MODULE 3: DEADLOCK MANAGEMENT (BANKER'S ALGORITHM)")
        print("=" * 66)
        print("  1. Run Safety Algorithm on Predefined Scenario")
        print("  2. Simulate Dynamic Resource Request")
        print("  3. Run Textbook Reference Safe State (Silberschatz)")
        print("  4. Return to Top-Level Menu")
        print("=" * 66)

        choice = input("Enter choice (1-4): ").strip()
        if choice == "1":
            sc = load_deadlock_dataset_flow()
            if sc:
                avail = sc["available"]
                alloc = sc["allocation"]
                max_m = sc["max"]
                p_names = sc.get("process_names")
                r_names = sc.get("resource_names")
                need = compute_need_matrix(alloc, max_m)
                print_bankers_matrices(avail, alloc, max_m, need, p_names, r_names)
                eval_res = check_safety(avail, alloc, max_m, p_names, r_names)
                print_bankers_safety_result(eval_res)

        elif choice == "2":
            sc = load_deadlock_dataset_flow()
            if sc:
                avail = sc["available"]
                alloc = sc["allocation"]
                max_m = sc["max"]
                p_names = sc.get("process_names") or [f"P{i}" for i in range(len(alloc))]
                r_names = sc.get("resource_names") or [chr(ord('A') + j) for j in range(len(avail))]
                need = compute_need_matrix(alloc, max_m)
                print_bankers_matrices(avail, alloc, max_m, need, p_names, r_names)

                print("\nSimulate Resource Request:")
                print(f"  Available Processes: {', '.join(f'{i}: {p_names[i]}' for i in range(len(p_names)))}")
                try:
                    p_idx = int(input("  Enter requesting process index (e.g. 1): ").strip())
                    req_raw = input(f"  Enter requested vector for {len(r_names)} resources (e.g. '1, 0, 2'): ").strip()
                    req_vec = [int(x) for x in req_raw.replace(",", " ").split()]
                    sim_res = simulate_resource_request(
                        available=avail,
                        allocation=alloc,
                        max_matrix=max_m,
                        process_idx=p_idx,
                        request_vector=req_vec,
                        process_names=p_names,
                        resource_names=r_names,
                    )
                    print("\n" + "=" * 68)
                    print(f"  RESOURCE REQUEST RESULT FOR {p_names[p_idx]}: {req_vec}")
                    print("=" * 68)
                    print(f"  Decision: {'GRANTED' if sim_res['approved'] else 'DENIED / MUST WAIT'}")
                    print(f"  Reason  : {sim_res['reason']}")
                    if sim_res["approved"] and sim_res.get("safety_result"):
                        print_bankers_safety_result(sim_res["safety_result"])
                    print("=" * 68)
                except Exception as e:
                    print(f"  [Error] Request simulation failed: {e}")

        elif choice == "3":
            # Silberschatz reference
            avail = [3, 3, 2]
            alloc = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]
            max_m = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]
            p_names = ["P0", "P1", "P2", "P3", "P4"]
            r_names = ["A", "B", "C"]
            need = compute_need_matrix(alloc, max_m)
            print_bankers_matrices(avail, alloc, max_m, need, p_names, r_names)
            eval_res = check_safety(avail, alloc, max_m, p_names, r_names)
            print_bankers_safety_result(eval_res)

        elif choice == "4":
            break
        else:
            print("  [Invalid Selection] Please choose between 1 and 4.")


# =============================================================================
# OPTION 4: FULL CAPSTONE INTEGRATED VIVA DEMO
# =============================================================================

def run_full_capstone_demo():
    """
    Run an end-to-end demonstration covering all 3 major OS subsystems:
        Part 1: Virtual Memory Management (FIFO, LRU, Optimal on 20-ref sequence)
        Part 2: CPU Scheduling (FCFS, SJF, RR on 4-process workload)
        Part 3: Deadlock Management (Banker's Algorithm safe check & request test)
    """
    print("\n" + "#" * 72)
    print("      MEMORA — FULL INTEGRATED CAPSTONE DEMONSTRATION")
    print("   Operating Systems Resource-Management Simulation Suite")
    print("#" * 72)

    # ---------------------------------------------------------
    # PART 1: Virtual Memory Management
    # ---------------------------------------------------------
    print("\n" + "=" * 72)
    print("  [PART 1 / 3] VIRTUAL MEMORY MANAGEMENT — PAGE REPLACEMENT")
    print("=" * 72)
    print(f"  Reference Page String : {REFERENCE_SEQUENCE}")
    print(f"  Allocated Frames      : {REFERENCE_FRAMES}")
    print("  Simulating FIFO, LRU, and Optimal algorithms...")

    mem_comp = compare_algorithms(REFERENCE_SEQUENCE, REFERENCE_FRAMES)
    print_comparison_table(mem_comp)

    # ---------------------------------------------------------
    # PART 2: CPU Scheduling
    # ---------------------------------------------------------
    print("\n" + "=" * 72)
    print("  [PART 2 / 3] CPU SCHEDULING — WORKLOAD SIMULATION")
    print("=" * 72)
    cpu_procs = [
        {"id": "P1", "arrival_time": 0, "burst_time": 5},
        {"id": "P2", "arrival_time": 1, "burst_time": 3},
        {"id": "P3", "arrival_time": 2, "burst_time": 8},
        {"id": "P4", "arrival_time": 3, "burst_time": 6},
    ]
    tq = 2
    print(f"  Workload Processes : {[(p['id'], f'AT={p['arrival_time']}', f'BT={p['burst_time']}') for p in cpu_procs]}")
    print(f"  Round Robin Quantum: {tq}")

    cpu_comp = compare_cpu_schedulers(cpu_procs, time_quantum=tq)
    print_cpu_comparison_table(cpu_comp)
    print_cpu_gantt_text(cpu_comp["results"]["FCFS"]["gantt_chart"])

    # ---------------------------------------------------------
    # PART 3: Deadlock Avoidance (Banker's Algorithm)
    # ---------------------------------------------------------
    print("\n" + "=" * 72)
    print("  [PART 3 / 3] DEADLOCK AVOIDANCE — BANKER'S SAFETY CHECK")
    print("=" * 72)
    avail = [3, 3, 2]
    alloc = [
        [0, 1, 0],
        [2, 0, 0],
        [3, 0, 2],
        [2, 1, 1],
        [0, 0, 2],
    ]
    max_m = [
        [7, 5, 3],
        [3, 2, 2],
        [9, 0, 2],
        [2, 2, 2],
        [4, 3, 3],
    ]
    p_names = ["P0", "P1", "P2", "P3", "P4"]
    r_names = ["A", "B", "C"]
    need = compute_need_matrix(alloc, max_m)
    print_bankers_matrices(avail, alloc, max_m, need, p_names, r_names)
    safety_eval = check_safety(avail, alloc, max_m, p_names, r_names)
    print_bankers_safety_result(safety_eval)

    # Simulate grantable request
    print("\n  Testing Dynamic Resource Request: P1 requests [1, 0, 2]...")
    req_grant = simulate_resource_request(avail, alloc, max_m, 1, [1, 0, 2], p_names, r_names)
    print(f"  -> Decision: {'GRANTED' if req_grant['approved'] else 'DENIED'}")
    print(f"  -> Reason  : {req_grant['reason']}")

    print("\n" + "#" * 72)
    print("      CAPSTONE DEMONSTRATION COMPLETE: ALL 3 SUBSYSTEMS VERIFIED")
    print("#" * 72)


# =============================================================================
# TOP-LEVEL INTERACTIVE MENU & CLI ARGUMENTS
# =============================================================================

def interactive_menu():
    """Top-level unified interactive menu."""
    ensure_output_directories()

    while True:
        print_banner()
        print("  TOP-LEVEL OS RESOURCE MANAGEMENT MENU:")
        print("    1. Virtual Memory Management (FIFO, LRU, Optimal)")
        print("    2. CPU Scheduling (FCFS, SJF, Round Robin, Gantt)")
        print("    3. Deadlock Management (Banker's Safety & Request)")
        print("    4. Full Capstone Viva Demonstration (All 3 Modules)")
        print("    5. Exit")
        print("=" * 72)

        try:
            choice = input("Enter module selection (1-5): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting Memora. Goodbye!")
            return 0

        if choice == "1":
            memory_module_menu()
        elif choice == "2":
            cpu_module_menu()
        elif choice == "3":
            deadlock_module_menu()
        elif choice == "4":
            run_full_capstone_demo()
        elif choice == "5":
            print("\nExiting Memora. Goodbye!")
            return 0
        else:
            print("\n  [Invalid Selection] Please choose a number between 1 and 5.")

        input("\nPress Enter to return to main menu...")


def main():
    """Application entry point supporting interactive mode and CLI flags."""
    parser = argparse.ArgumentParser(
        description="Memora: Integrated OS Resource-Management Simulator (Memory, CPU, Deadlock)"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run the standard virtual memory demonstration non-interactively",
    )
    parser.add_argument(
        "--demo-all",
        action="store_true",
        help="Run the complete 3-module Capstone Viva demonstration non-interactively",
    )
    parser.add_argument(
        "--module",
        choices=["memory", "cpu", "deadlock"],
        help="Launch directly into a specific subsystem module",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Run simulations across all memory sample datasets and export batch results",
    )
    parser.add_argument(
        "--algo",
        choices=["FIFO", "LRU", "Optimal", "all"],
        help="Run a specific memory algorithm or 'all' for comparison",
    )
    parser.add_argument(
        "--pages",
        type=str,
        help="Comma or space separated page reference string (e.g. '7,0,1,2')",
    )
    parser.add_argument(
        "--frames",
        type=int,
        help="Number of memory frames",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        help="Name of sample dataset from sample_input.json to run",
    )

    args = parser.parse_args()

    if args.demo_all:
        print_banner()
        run_full_capstone_demo()
        return 0

    if args.demo:
        print_banner()
        run_reference_case_flow()
        return 0

    if args.module == "memory":
        memory_module_menu()
        return 0
    elif args.module == "cpu":
        cpu_module_menu()
        return 0
    elif args.module == "deadlock":
        deadlock_module_menu()
        return 0

    if args.batch:
        print_banner()
        sample_file = os.path.join(DATASETS_DIR, "sample_input.json")
        data = load_dataset(sample_file)
        datasets = data.get("datasets", [])
        print(f"\n--- Running Batch Simulation on {len(datasets)} Datasets ---")

        all_batch_results = []
        for ds in datasets:
            name = ds.get("name", "Unknown")
            pages = ds["page_sequence"]
            fc = ds["frame_count"]
            print(f"\nSimulating dataset '{name}' (pages={len(pages)}, frames={fc})...")
            comp = compare_algorithms(pages, fc)
            for r in comp["results"]:
                r["dataset_name"] = name
                all_batch_results.append(r)
            best = comp["summary"]["best_algorithm"]
            fewest = comp["summary"]["fewest_faults"]
            print(f"  -> Best: {best} with {fewest} faults")

        batch_csv = os.path.join(DATASETS_DIR, "..", "results", "reports", "batch_simulation_results.csv")
        batch_csv = os.path.abspath(batch_csv)
        export_results_csv(all_batch_results, batch_csv)
        print(f"\n[OK] Batch simulation complete. Report exported to:\n     {batch_csv}")
        return 0

    if args.dataset:
        print_banner()
        sample_file = os.path.join(DATASETS_DIR, "sample_input.json")
        data = load_dataset(sample_file)
        matching = [ds for ds in data.get("datasets", []) if ds.get("name") == args.dataset]
        if not matching:
            print(f"[Error] Dataset '{args.dataset}' not found in {sample_file}")
            return 1
        ds = matching[0]
        print(f"[Loaded Dataset: {ds['name']}]")
        run_comparison_flow(ds["page_sequence"], ds["frame_count"])
        return 0

    if args.pages and args.frames:
        print_banner()
        parts = args.pages.replace(",", " ").split()
        try:
            pages = [int(p) for p in parts]
        except ValueError:
            print("[Error] All page values must be integers.")
            return 1

        fc = args.frames
        algo = args.algo if args.algo else "all"

        if algo.lower() == "all":
            run_comparison_flow(pages, fc)
        else:
            res = run_simulation(algo, pages, fc)
            print_simulation_table(res)
        return 0

    return interactive_menu()


if __name__ == "__main__":
    sys.exit(main())
