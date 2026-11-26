"""
Memora — Virtual Memory Simulator for Page Replacement Algorithm Analysis

Entry point for the Memora application.
Provides an interactive menu and CLI for simulating, analyzing,
and comparing FIFO, LRU, and Optimal page replacement algorithms.
"""

import argparse
import os
import sys

from src.core.simulator import run_simulation, run_all_simulations, ALGORITHM_REGISTRY
from src.analysis.comparison import compare_algorithms
from src.analysis.visualization import (
    plot_fault_comparison,
    plot_hit_ratio_comparison,
    plot_comparison_chart,
    HAS_MATPLOTLIB,
)
from src.utils.file_handler import (
    load_dataset,
    export_results_csv,
    ensure_output_directories,
    DATASETS_DIR,
)
from src.core.validator import validate_page_sequence, validate_frame_count


# Standard textbook reference test sequence
REFERENCE_SEQUENCE = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
REFERENCE_FRAMES = 3


def print_banner():
    """Print the application welcome banner."""
    print("=" * 66)
    print("        MEMORA — VIRTUAL MEMORY SIMULATOR")
    print("      Page Replacement Algorithm Analysis (Phase 2)")
    print("=" * 66)


def print_simulation_table(result):
    """
    Print a formatted step-by-step memory state table for a simulation result.

    Args:
        result (dict): Simulation result dictionary.
    """
    algo = result.get("algorithm", "Unknown")
    frame_count = result.get("frame_count", 0)
    history = result.get("history", [])

    print("\n" + "-" * 66)
    print(f"  SIMULATION EXECUTION TRACE: {algo} (Frames = {frame_count})")
    print("-" * 66)

    # Build header
    header = f"{'Step':<6}{'Page':<8}"
    for f in range(frame_count):
        header += f"{'Frame ' + str(f):<10}"
    header += f"{'Status':<10}{'Evicted':<8}"
    print(header)
    print("-" * len(header))

    # Print each step
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
    """
    Print a side-by-side comparison table of algorithm performance.

    Args:
        comparison_result (dict): Output from compare_algorithms().
    """
    results = comparison_result.get("results", [])
    summary = comparison_result.get("summary", {})
    frame_count = comparison_result.get("frame_count", 0)
    total_accesses = len(comparison_result.get("page_sequence", []))

    print("\n" + "=" * 66)
    print(f"  ALGORITHM COMPARISON SUMMARY (Frames = {frame_count}, Accesses = {total_accesses})")
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
    """Prompt the user to enter a page reference sequence."""
    while True:
        raw = input("\nEnter page sequence (comma or space separated, e.g. 7, 0, 1, 2): ").strip()
        if not raw:
            print("  [Error] Page sequence cannot be empty.")
            continue
        # Split by comma or whitespace
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
    """Prompt the user to enter memory frame count."""
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
    """Workflow to run and display a single algorithm simulation."""
    print(f"\n--- Running {algo_name} Simulation ---")
    pages = prompt_page_sequence()
    fc = prompt_frame_count()

    result = run_simulation(algo_name, pages, fc)
    print_simulation_table(result)
    return result


def run_comparison_flow(pages=None, fc=None):
    """Workflow to run all three algorithms, compare, and offer charts/CSV."""
    print("\n--- Running Algorithm Comparison (FIFO vs. LRU vs. Optimal) ---")
    if pages is None:
        pages = prompt_page_sequence()
    if fc is None:
        fc = prompt_frame_count()

    comparison = compare_algorithms(pages, fc)
    print_comparison_table(comparison)

    # Prompt for chart generation
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

    # Prompt for CSV export
    exp_csv = input("  Export results to CSV? (y/n) [default: y]: ").strip().lower()
    if exp_csv != "n":
        csv_path = export_results_csv(comparison)
        print(f"  [OK] Saved CSV report:        {csv_path}")

    return comparison


def load_dataset_flow():
    """Workflow to load predefined sample datasets."""
    sample_file = os.path.join(DATASETS_DIR, "sample_input.json")
    try:
        data = load_dataset(sample_file)
        datasets = data.get("datasets", [])
    except Exception as e:
        print(f"  [Error] Could not load datasets: {e}")
        return

    print("\n--- Available Predefined Datasets ---")
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
    print("\n--- Running Reference Test Case ---")
    print(f"  Page Sequence : {REFERENCE_SEQUENCE}")
    print(f"  Frame Count   : {REFERENCE_FRAMES}")
    print("\nSimulating all three algorithms...")

    comparison = compare_algorithms(REFERENCE_SEQUENCE, REFERENCE_FRAMES)

    # Print individual traces
    for r in comparison["results"]:
        print_simulation_table(r)

    # Print comparison
    print_comparison_table(comparison)

    # Auto-generate charts and CSV for the reference case
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


def interactive_menu():
    """Display interactive menu loop."""
    ensure_output_directories()

    while True:
        print_banner()
        print("  MAIN MENU:")
        print("    1. Run FIFO Page Replacement")
        print("    2. Run LRU Page Replacement")
        print("    3. Run Optimal Page Replacement")
        print("    4. Compare All Three Algorithms (Side-by-Side)")
        print("    5. Load Predefined Sample Dataset")
        print("    6. Run Standard Reference Test Case (Viva Demo)")
        print("    7. Exit")
        print("=" * 66)

        try:
            choice = input("Enter choice (1-7): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting Memora. Goodbye!")
            return 0

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
            print("\nExiting Memora. Goodbye!")
            return 0
        else:
            print("\n  [Invalid Selection] Please choose a number between 1 and 7.")

        input("\nPress Enter to return to main menu...")


def main():
    """Application entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Memora: A Virtual Memory Simulator for Page Replacement Algorithm Analysis"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run the standard reference demonstration non-interactively",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Run simulations across all sample datasets and export batch results",
    )
    parser.add_argument(
        "--algo",
        choices=["FIFO", "LRU", "Optimal", "all"],
        help="Run a specific algorithm or 'all' for comparison",
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

    # Non-interactive modes
    if args.demo:
        print_banner()
        run_reference_case_flow()
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

    # Default to interactive menu
    return interactive_menu()


if __name__ == "__main__":
    sys.exit(main())
