"""
FIFO (First In, First Out) Page Replacement Algorithm.

Algorithm Specification:
    - On a page HIT: No change to memory frames. Increment hit count.
    - On a page FAULT with empty frame available: Load the page into the
      first available empty frame. Increment fault count.
    - On a page FAULT with all frames full: Replace the page that was
      loaded into memory EARLIEST (longest time ago). The replacement
      order follows a strict queue discipline (first in, first out).
    - Memory history: After each page access, record the current state
      of all frames.

Replacement Strategy:
    Uses a FIFO queue to track the insertion order of pages currently
    in memory. The page at the front of the queue is always the oldest
    and is replaced first.
"""

from collections import deque
from src.core.metrics import calculate_metrics


def run_fifo(page_sequence, frame_count):
    """
    Simulate FIFO page replacement.

    Args:
        page_sequence (list[int]): Sequence of page numbers to access.
        frame_count (int): Number of available memory frames (positive integer).

    Returns:
        dict: Simulation result with the following structure:
            {
                "algorithm": "FIFO",
                "page_sequence": list[int],
                "frame_count": int,
                "hits": int,
                "faults": int,
                "hit_ratio": float,
                "fault_ratio": float,
                "history": list[dict]
                    Each entry: {
                        "step": int,
                        "page": int,
                        "frames": list[int | None],
                        "is_hit": bool,
                        "evicted": int | None
                    }
            }
    """
    frames = [None] * frame_count
    load_queue = deque()
    history = []

    for step, page in enumerate(page_sequence):
        if page in frames:
            is_hit = True
            evicted = None
        else:
            is_hit = False
            if None in frames:
                slot_idx = frames.index(None)
                frames[slot_idx] = page
                evicted = None
                load_queue.append(page)
            else:
                oldest_page = load_queue.popleft()
                slot_idx = frames.index(oldest_page)
                evicted = oldest_page
                frames[slot_idx] = page
                load_queue.append(page)

        history.append({
            "step": step,
            "page": page,
            "frames": list(frames),
            "is_hit": is_hit,
            "evicted": evicted,
        })

    result = {
        "algorithm": "FIFO",
        "page_sequence": list(page_sequence),
        "frame_count": frame_count,
        "history": history,
    }

    return calculate_metrics(result)
