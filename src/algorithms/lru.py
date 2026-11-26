"""
LRU (Least Recently Used) Page Replacement Algorithm.

Algorithm Specification:
    - On a page HIT: The page remains in memory. Its "last accessed"
      timestamp is updated to the current step. Increment hit count.
    - On a page FAULT with empty frame available: Load the page into the
      first available empty frame. Set its "last accessed" timestamp to
      the current step. Increment fault count.
    - On a page FAULT with all frames full: Replace the page whose
      "last accessed" timestamp is the OLDEST (the page not used for
      the longest time in the past). Load the new page and set its
      timestamp to the current step.
    - Memory history: After each page access, record the current state
      of all frames.

Replacement Strategy:
    Tracks the most recent access step for every page currently in
    memory. On replacement, the page with the smallest (oldest) access
    timestamp is evicted.
"""

from src.core.metrics import calculate_metrics


def run_lru(page_sequence, frame_count):
    """
    Simulate LRU page replacement.

    Args:
        page_sequence (list[int]): Sequence of page numbers to access.
        frame_count (int): Number of available memory frames (positive integer).

    Returns:
        dict: Simulation result with the following structure:
            {
                "algorithm": "LRU",
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
    last_used = {}
    history = []

    for step, page in enumerate(page_sequence):
        if page in frames:
            is_hit = True
            evicted = None
            last_used[page] = step
        else:
            is_hit = False
            if None in frames:
                slot_idx = frames.index(None)
                frames[slot_idx] = page
                evicted = None
                last_used[page] = step
            else:
                # Find the page in memory with the oldest access step
                lru_page = min(frames, key=lambda p: last_used[p])
                slot_idx = frames.index(lru_page)
                evicted = lru_page
                del last_used[lru_page]
                frames[slot_idx] = page
                last_used[page] = step

        history.append({
            "step": step,
            "page": page,
            "frames": list(frames),
            "is_hit": is_hit,
            "evicted": evicted,
        })

    result = {
        "algorithm": "LRU",
        "page_sequence": list(page_sequence),
        "frame_count": frame_count,
        "history": history,
    }

    return calculate_metrics(result)
