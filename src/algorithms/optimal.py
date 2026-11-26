"""
Optimal (Bélády's) Page Replacement Algorithm.

Algorithm Specification:
    - On a page HIT: No change to memory frames. Increment hit count.
    - On a page FAULT with empty frame available: Load the page into the
      first available empty frame. Increment fault count.
    - On a page FAULT with all frames full: Look AHEAD in the remaining
      page reference sequence. Replace the page whose next use is
      FARTHEST in the future. If a page in memory will NEVER be used
      again, it is the ideal replacement candidate.
    - If multiple pages tie (e.g., multiple pages never used again),
      replace the one that appears earliest in the frame list
      (deterministic tie-breaking).
    - Memory history: After each page access, record the current state
      of all frames.

Replacement Strategy:
    For each page currently in memory, scan the future portion of the
    page reference sequence to determine the distance to its next occurrence.
    Pages never referenced again receive an effective distance of infinity.
    The page with the greatest distance is evicted.
"""

from src.core.metrics import calculate_metrics


def run_optimal(page_sequence, frame_count):
    """
    Simulate Optimal page replacement.

    Args:
        page_sequence (list[int]): Sequence of page numbers to access.
        frame_count (int): Number of available memory frames (positive integer).

    Returns:
        dict: Simulation result with the following structure:
            {
                "algorithm": "Optimal",
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
    history = []
    total_steps = len(page_sequence)

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
            else:
                # Find page with farthest next occurrence in the future
                victim_slot = -1
                farthest_dist = -1
                future_sequence = page_sequence[step + 1:]

                for slot_idx, current_page in enumerate(frames):
                    try:
                        next_use = future_sequence.index(current_page)
                    except ValueError:
                        next_use = float("inf")

                    if next_use == float("inf"):
                        # If page never used again, select immediately (deterministic first-frame tie-break)
                        victim_slot = slot_idx
                        break

                    if next_use > farthest_dist:
                        farthest_dist = next_use
                        victim_slot = slot_idx

                evicted = frames[victim_slot]
                frames[victim_slot] = page

        history.append({
            "step": step,
            "page": page,
            "frames": list(frames),
            "is_hit": is_hit,
            "evicted": evicted,
        })

    result = {
        "algorithm": "Optimal",
        "page_sequence": list(page_sequence),
        "frame_count": frame_count,
        "history": history,
    }

    return calculate_metrics(result)
