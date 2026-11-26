"""
File Handler.

Manages reading input datasets and exporting simulation results.

Responsibilities:
    - Load JSON dataset files from the datasets/ directory.
    - Export simulation results to CSV in results/reports/.
    - Ensure output directories exist before writing.

Supported Formats:
    - Input:  JSON (.json)
    - Output: CSV (.csv)
"""

import csv
import json
import os

# Project root is two levels up from this file (src/utils/file_handler.py)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASETS_DIR = os.path.join(PROJECT_ROOT, "datasets")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "results", "reports")
CHARTS_DIR = os.path.join(PROJECT_ROOT, "results", "charts")
LOGS_DIR = os.path.join(PROJECT_ROOT, "results", "logs")


def ensure_output_directories():
    """
    Create output directories if they do not exist.

    Creates:
        - results/reports/
        - results/charts/
        - results/logs/
    """
    for directory in [REPORTS_DIR, CHARTS_DIR, LOGS_DIR]:
        os.makedirs(directory, exist_ok=True)


def load_dataset(filepath):
    """
    Load a JSON dataset file.

    If filepath is not found as a relative/absolute path, attempts
    to look inside the datasets/ directory.

    Args:
        filepath (str): Path or filename of the JSON dataset file.

    Returns:
        dict: Parsed dataset contents.

    Raises:
        FileNotFoundError: If the file cannot be located.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    target_path = filepath
    if not os.path.isabs(target_path) and not os.path.exists(target_path):
        candidate = os.path.join(DATASETS_DIR, filepath)
        if os.path.exists(candidate):
            target_path = candidate

    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Dataset file not found: {filepath}")

    with open(target_path, "r", encoding="utf-8") as f:
        return json.load(f)


def export_results_csv(results, output_path=None):
    """
    Export simulation or comparison results to a CSV file.

    Args:
        results (dict or list[dict]): Single result dict, comparison dict,
            or list of simulation result dicts.
        output_path (str, optional): Destination CSV file path.
            Defaults to results/reports/simulation_results.csv.

    Returns:
        str: Absolute or resolved path to the written CSV file.
    """
    ensure_output_directories()

    if output_path is None:
        output_path = os.path.join(REPORTS_DIR, "simulation_results.csv")

    # Normalize input to a list of algorithm result dicts
    result_list = []
    if isinstance(results, dict):
        if "results" in results and isinstance(results["results"], list):
            result_list = results["results"]
        elif "algorithm" in results:
            result_list = [results]
    elif isinstance(results, list):
        result_list = results

    fieldnames = [
        "Algorithm",
        "Frame Count",
        "Total Accesses",
        "Page Hits",
        "Page Faults",
        "Hit Ratio",
        "Fault Ratio",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for r in result_list:
            history = r.get("history", [])
            total_accesses = len(history) if history else len(r.get("page_sequence", []))
            writer.writerow({
                "Algorithm": r.get("algorithm", "Unknown"),
                "Frame Count": r.get("frame_count", 0),
                "Total Accesses": total_accesses,
                "Page Hits": r.get("hits", 0),
                "Page Faults": r.get("faults", 0),
                "Hit Ratio": f"{r.get('hit_ratio', 0.0):.4f}",
                "Fault Ratio": f"{r.get('fault_ratio', 0.0):.4f}",
            })

    return output_path
