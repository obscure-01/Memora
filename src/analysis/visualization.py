"""
Visualization Module.

Generates performance charts from algorithm comparison results using Matplotlib.

Charts:
    - Page fault comparison (bar chart)
    - Hit ratio comparison (bar chart)
    - Grouped comparison (hits vs. faults side-by-side)

All charts are saved as PNG files in results/charts/ by default.
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
    hit_percentages = [r["hit_ratio"] * 100 for r in results]
    frame_count = comparison_result.get("frame_count", "?")

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#2ECC71", "#3498DB", "#9B59B6"][:len(algorithms)]

    bars = ax.bar(algorithms, hit_percentages, color=colors, width=0.5, edgecolor="#333333", linewidth=1.2)

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
    ax.set_ylim(0, 105)
    ax.grid(axis="y", linestyle="--", alpha=0.6)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path


def plot_comparison_chart(comparison_result, output_path=None):
    """
    Generate a grouped side-by-side bar chart showing Hits and Faults.

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

    fig, ax = plt.subplots(figsize=(9, 5))
    rects1 = ax.bar(x - width / 2, hits, width, label="Page Hits", color="#2ECC71", edgecolor="#333333")
    rects2 = ax.bar(x + width / 2, faults, width, label="Page Faults", color="#E74C3C", edgecolor="#333333")

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
