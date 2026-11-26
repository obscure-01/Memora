"""
Visualization Module.

Generates performance charts for:
    - Virtual Memory Page Replacement Algorithms (Faults, Hit Ratios, Grouped Comparison)
    - CPU Scheduling Algorithms (Gantt Chart timeline, Performance Comparison)

All charts are saved as PNG files in results/charts/ by default using Matplotlib.
"""

import os
import tempfile

# Set MPLCONFIGDIR to avoid permission warnings on Windows temp directories
os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())

try:
    import matplotlib
    matplotlib.use("Agg")  # Non-interactive backend suitable for headless scripts/CI
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from src.utils.file_handler import CHARTS_DIR, ensure_output_directories


def _check_matplotlib():
    """Raise ImportError if matplotlib is not installed."""
    if not HAS_MATPLOTLIB:
        raise ImportError(
            "Matplotlib is required for chart generation. "
            "Please install it using: pip install matplotlib"
        )


def plot_fault_comparison(comparison_result, output_path=None):
    """
    Generate a bar chart comparing page faults across algorithms.

    Args:
        comparison_result (dict): Output from compare_algorithms().
        output_path (str, optional): Destination PNG path.
            Defaults to results/charts/fault_comparison.png.

    Returns:
        str: Path to the generated chart image.
    """
    _check_matplotlib()
    ensure_output_directories()

    if output_path is None:
        output_path = os.path.join(CHARTS_DIR, "fault_comparison.png")

    results = comparison_result.get("results", [])
    if not results:
        raise ValueError("comparison_result contains no algorithm results to plot.")

    algorithms = [r["algorithm"] for r in results]
    faults = [r["faults"] for r in results]
    frame_count = comparison_result.get("frame_count", "?")

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#4A90E2", "#50E3C2", "#F5A623"][:len(algorithms)]

    bars = ax.bar(algorithms, faults, color=colors, width=0.5, edgecolor="#333333", linewidth=1.2)

    # Annotate bar heights
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{int(height)}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    ax.set_title(
        f"Page Faults by Algorithm (Frames = {frame_count})",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax.set_xlabel("Algorithm", fontsize=12, labelpad=10)
    ax.set_ylabel("Total Page Faults", fontsize=12, labelpad=10)
    ax.set_ylim(0, max(faults) * 1.2 if max(faults) > 0 else 5)
    ax.grid(axis="y", linestyle="--", alpha=0.6)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path


def plot_hit_ratio_comparison(comparison_result, output_path=None):
    """
    Generate a bar chart comparing hit ratios across algorithms.

    Args:
        comparison_result (dict): Output from compare_algorithms().
        output_path (str, optional): Destination PNG path.
            Defaults to results/charts/hit_ratio_comparison.png.

    Returns:
        str: Path to the generated chart image.
    """
    _check_matplotlib()
    ensure_output_directories()

    if output_path is None:
        output_path = os.path.join(CHARTS_DIR, "hit_ratio_comparison.png")

    results = comparison_result.get("results", [])
    if not results:
        raise ValueError("comparison_result contains no algorithm results to plot.")

    algorithms = [r["algorithm"] for r in results]
    hit_ratios = [r["hit_ratio"] * 100 for r in results]
    frame_count = comparison_result.get("frame_count", "?")

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#4A90E2", "#50E3C2", "#F5A623"][:len(algorithms)]

    bars = ax.bar(algorithms, hit_ratios, color=colors, width=0.5, edgecolor="#333333", linewidth=1.2)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.1f}%",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    ax.set_title(
        f"Hit Ratio (%) by Algorithm (Frames = {frame_count})",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax.set_xlabel("Algorithm", fontsize=12, labelpad=10)
    ax.set_ylabel("Hit Ratio (%)", fontsize=12, labelpad=10)
    ax.set_ylim(0, 110)
    ax.grid(axis="y", linestyle="--", alpha=0.6)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path


def plot_comparison_chart(comparison_result, output_path=None):
    """
    Generate a grouped bar chart showing Hits vs. Faults side-by-side.

    Args:
        comparison_result (dict): Output from compare_algorithms().
        output_path (str, optional): Destination PNG path.
            Defaults to results/charts/comparison_summary.png.

    Returns:
        str: Path to the generated chart image.
    """
    _check_matplotlib()
    ensure_output_directories()

    if output_path is None:
        output_path = os.path.join(CHARTS_DIR, "comparison_summary.png")

    results = comparison_result.get("results", [])
    if not results:
        raise ValueError("comparison_result contains no algorithm results to plot.")

    algorithms = [r["algorithm"] for r in results]
    hits = [r["hits"] for r in results]
    faults = [r["faults"] for r in results]
    frame_count = comparison_result.get("frame_count", "?")

    import numpy as np
    x = np.arange(len(algorithms))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 5.5))

    rects1 = ax.bar(x - width / 2, hits, width, label="Hits", color="#50E3C2", edgecolor="#333333", linewidth=1.2)
    rects2 = ax.bar(x + width / 2, faults, width, label="Faults", color="#E74C3C", edgecolor="#333333", linewidth=1.2)

    for rect in list(rects1) + list(rects2):
        height = rect.get_height()
        ax.annotate(
            f"{int(height)}",
            xy=(rect.get_x() + rect.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    ax.set_title(
        f"Memora: Hits vs. Faults Comparison (Frames = {frame_count})",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(algorithms, fontsize=12)
    ax.set_ylabel("Count", fontsize=12, labelpad=10)
    max_val = max(max(hits), max(faults)) if hits and faults else 5
    ax.set_ylim(0, max_val * 1.25)
    ax.legend(frameon=True)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path


def plot_cpu_gantt_chart(schedule_result, output_path=None):
    """
    Generate a visual Gantt chart for CPU scheduling execution timeline.

    Args:
        schedule_result (dict): Output from run_fcfs, run_sjf, or run_round_robin.
        output_path (str, optional): Destination PNG path.
            Defaults to results/charts/cpu_gantt_chart.png.

    Returns:
        str: Path to the generated chart image.
    """
    _check_matplotlib()
    ensure_output_directories()

    if output_path is None:
        algo = schedule_result.get("algorithm", "cpu").lower()
        output_path = os.path.join(CHARTS_DIR, f"{algo}_gantt_chart.png")

    gantt = schedule_result.get("gantt_chart", [])
    if not gantt:
        raise ValueError("schedule_result contains no gantt_chart segments.")

    algo_name = schedule_result.get("algorithm_name", schedule_result.get("algorithm", "CPU Scheduler"))

    fig, ax = plt.subplots(figsize=(10, 3.5))

    palette = ["#3b82f6", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6", "#06b6d4"]
    proc_colors = {}
    p_idx = 0

    for seg in gantt:
        p = seg["process"]
        if p == "IDLE":
            color = "#64748b"
        elif p not in proc_colors:
            proc_colors[p] = palette[p_idx % len(palette)]
            p_idx += 1
            color = proc_colors[p]
        else:
            color = proc_colors[p]

        start = seg["start"]
        duration = seg["end"] - seg["start"]
        ax.barh(0, duration, left=start, height=0.5, color=color, edgecolor="#1e293b", linewidth=1.2)

        # Label in center of bar
        label_text = p if p == "IDLE" else f"{p} ({duration})"
        ax.text(
            start + duration / 2, 0,
            label_text,
            ha="center", va="center",
            color="#ffffff" if p != "IDLE" else "#e2e8f0",
            fontsize=10, fontweight="bold",
        )

    # Time ticks at all segment boundaries
    time_points = sorted(list(set([seg["start"] for seg in gantt] + [seg["end"] for seg in gantt])))
    ax.set_xticks(time_points)
    ax.set_yticks([])
    ax.set_xlabel("Timeline (Clock Cycles / Time Units)", fontsize=11, labelpad=8)
    ax.set_title(f"CPU Execution Timeline (Gantt Chart) — {algo_name}", fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis="x", linestyle=":", alpha=0.6)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path


def plot_cpu_comparison_chart(comparison_result, output_path=None):
    """
    Generate a grouped bar chart comparing CPU scheduling algorithms:
    Average Waiting Time (AWT), Average Turnaround Time (ATAT), Average Response Time (ART).

    Args:
        comparison_result (dict): Output from compare_cpu_schedulers().
        output_path (str, optional): Destination PNG path.

    Returns:
        str: Path to the generated chart image.
    """
    _check_matplotlib()
    ensure_output_directories()

    if output_path is None:
        output_path = os.path.join(CHARTS_DIR, "cpu_scheduling_comparison.png")

    rows = comparison_result.get("comparison_table", [])
    if not rows:
        raise ValueError("comparison_result contains no table rows.")

    algos = [r["algorithm"] for r in rows]
    awt = [r["avg_waiting_time"] for r in rows]
    atat = [r["avg_turnaround_time"] for r in rows]
    art = [r["avg_response_time"] for r in rows]

    import numpy as np
    x = np.arange(len(algos))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 5))

    rects1 = ax.bar(x - width, awt, width, label="Avg Waiting Time (AWT)", color="#3b82f6", edgecolor="#1e293b")
    rects2 = ax.bar(x, atat, width, label="Avg Turnaround Time (ATAT)", color="#10b981", edgecolor="#1e293b")
    rects3 = ax.bar(x + width, art, width, label="Avg Response Time (ART)", color="#f59e0b", edgecolor="#1e293b")

    for rect_group in [rects1, rects2, rects3]:
        for rect in rect_group:
            h = rect.get_height()
            ax.annotate(
                f"{h:.1f}",
                xy=(rect.get_x() + rect.get_width() / 2, h),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center", va="bottom",
                fontsize=9, fontweight="bold",
            )

    ax.set_title("CPU Scheduling Algorithms Performance Comparison", fontsize=13, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(algos, fontsize=11, fontweight="bold")
    ax.set_ylabel("Time Units", fontsize=11)
    max_h = max(max(awt), max(atat), max(art)) if awt and atat and art else 5
    ax.set_ylim(0, max_h * 1.25)
    ax.legend(frameon=True)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path
