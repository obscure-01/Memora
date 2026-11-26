# Memora — System Architecture

## 1. System Overview

Memora is a modular, command-line-based virtual memory simulator that implements and compares three page replacement algorithms. The system follows a layered architecture with clear separation of concerns.

```
┌──────────────────────────────────────────────┐
│              User Interface Layer             │
│         main.py  ·  bash/run.sh               │
├──────────────────────────────────────────────┤
│            Analysis Layer                     │
│     comparison.py  ·  visualization.py        │
├──────────────────────────────────────────────┤
│              Core Layer                       │
│  simulator.py  ·  metrics.py  ·  validator.py │
├──────────────────────────────────────────────┤
│           Algorithm Layer                     │
│      fifo.py  ·  lru.py  ·  optimal.py        │
├──────────────────────────────────────────────┤
│            Utility Layer                      │
│      file_handler.py  ·  logger.py            │
└──────────────────────────────────────────────┘
```

### Data Flow

```
User Input (pages, frames)
        │
        ▼
   validator.py ──── invalid? ──→ Error message
        │ valid
        ▼
   simulator.py ──→ fifo.py / lru.py / optimal.py
        │
        ▼
   metrics.py (calculate ratios)
        │
        ▼
   comparison.py (tabulate results)
        │
        ├──→ visualization.py (charts → results/charts/)
        ├──→ file_handler.py  (CSV   → results/reports/)
        └──→ Console output
```

---

## 2. Module Responsibilities

### 2.1 Algorithm Layer (`src/algorithms/`)

Each module implements exactly one page replacement algorithm. Algorithm modules:
- Receive a validated page sequence and frame count.
- Return a standardized result dictionary.
- Do NOT perform I/O, validation, or visualization.

| Module       | Algorithm | Replacement Rule                           |
|--------------|-----------|-------------------------------------------|
| `fifo.py`    | FIFO      | Evict the page loaded earliest             |
| `lru.py`     | LRU       | Evict the page not accessed for the longest |
| `optimal.py` | Optimal   | Evict the page used farthest in the future |

### 2.2 Core Layer (`src/core/`)

| Module          | Responsibility                                    |
|-----------------|---------------------------------------------------|
| `simulator.py`  | Dispatches to algorithms, collects results        |
| `metrics.py`    | Calculates hits, faults, ratios from history      |
| `validator.py`  | Validates page sequences, frame counts, datasets  |

### 2.3 Analysis Layer (`src/analysis/`)

| Module              | Responsibility                                |
|---------------------|-----------------------------------------------|
| `comparison.py`     | Runs all algorithms on same input, tabulates  |
| `visualization.py`  | Generates Matplotlib bar charts               |

### 2.4 Utility Layer (`src/utils/`)

| Module            | Responsibility                       |
|-------------------|--------------------------------------|
| `file_handler.py` | Loads JSON datasets, exports CSV     |
| `logger.py`       | Configures console and file logging  |

### 2.5 Interface Layer

| File            | Responsibility                            |
|-----------------|-------------------------------------------|
| `main.py`       | Menu-driven CLI entry point               |
| `bash/run.sh`   | Bash launcher (venv activation + launch)  |

---

## 3. Algorithm Specifications

### 3.1 FIFO — First In, First Out

**Concept:** Pages are replaced in the order they were loaded into memory, like a queue.

| Event              | Action                                                        |
|--------------------|---------------------------------------------------------------|
| Page HIT           | No change to frames. Increment hit count.                     |
| Fault + empty slot | Load page into first empty frame. Increment fault count.      |
| Fault + full       | Replace the page at the front of the queue (loaded earliest). |

**Key property:** A page hit does NOT reset its position in the queue. FIFO only tracks insertion order, not access recency.

**Data structure hint:** `collections.deque` or list used as a FIFO queue.

---

### 3.2 LRU — Least Recently Used

**Concept:** Replace the page that has gone the longest without being accessed.

| Event              | Action                                                            |
|--------------------|-------------------------------------------------------------------|
| Page HIT           | Update the page's last-access timestamp. Increment hit count.     |
| Fault + empty slot | Load page, set timestamp to current step. Increment fault count.  |
| Fault + full       | Replace the page with the oldest (smallest) last-access timestamp.|

**Key property:** A page hit DOES update its recency, moving it away from the eviction candidate position. This is what distinguishes LRU from FIFO.

**Data structure hint:** Dictionary mapping page → last-access step index, or `collections.OrderedDict` with move-to-end on access.

---

### 3.3 Optimal — Bélády's Algorithm

**Concept:** Replace the page whose next use is farthest in the future. This is the theoretical best — it produces the minimum possible page faults.

| Event              | Action                                                                |
|--------------------|-----------------------------------------------------------------------|
| Page HIT           | No change to frames. Increment hit count.                             |
| Fault + empty slot | Load page into first empty frame. Increment fault count.              |
| Fault + full       | For each page in memory, find its next occurrence in the future.      |
|                    | Replace the page with the farthest next use (or never used again).    |

**Tie-breaking:** If multiple pages will never be used again, replace the one appearing first in the frame list (index 0 before index 1, etc.).

**Key property:** Requires knowledge of the entire future reference string. Not implementable in real OS schedulers — serves purely as a performance benchmark.

---

## 4. Input/Output Contract

### 4.1 Algorithm Input

All three algorithms receive identical input:

```python
page_sequence: list[int]   # e.g., [7, 0, 1, 2, 0, 3, 0, 4]
frame_count: int            # e.g., 3
```

**Pre-conditions (enforced by validator):**
- `page_sequence` is a non-empty list of non-negative integers.
- `frame_count` is a positive integer (≥ 1).

### 4.2 Algorithm Output

All three algorithms return an identical structure:

```python
{
    "algorithm": str,           # "FIFO", "LRU", or "Optimal"
    "page_sequence": list[int], # Echo of the input sequence
    "frame_count": int,         # Echo of the input frame count
    "hits": int,                # Total page hits
    "faults": int,              # Total page faults
    "hit_ratio": float,         # hits / len(page_sequence), rounded to 4 decimals
    "fault_ratio": float,       # faults / len(page_sequence), rounded to 4 decimals
    "history": [                # One entry per page access
        {
            "step": int,        # 0-based step index
            "page": int,        # Page accessed at this step
            "frames": list,     # State of all frames AFTER this access
                                # (None for empty frames)
            "is_hit": bool,     # True if page was already in memory (HIT), False otherwise (FAULT)
            "evicted": int | None # Page evicted from memory on fault when full, or None
        },
        ...
    ]
}
```

**Post-conditions:**
- `hits + faults == len(page_sequence)`
- `hit_ratio + fault_ratio == 1.0` (within floating-point tolerance)
- `len(history) == len(page_sequence)`

### 4.3 Comparison Output

```python
{
    "page_sequence": list[int],
    "frame_count": int,
    "results": [
        { ... FIFO result ... },
        { ... LRU result ... },
        { ... Optimal result ... }
    ],
    "summary": {
        "best_algorithm": str,  # Algorithm with fewest faults
        "fewest_faults": int
    }
}
```

---

## 5. Validation Rules

### 5.1 Page Reference Sequence

| Rule                    | Valid Example     | Invalid Example   | Error Message                              |
|-------------------------|-------------------|-------------------|--------------------------------------------|
| Must not be empty       | `[1, 2, 3]`      | `[]`              | "Page reference sequence cannot be empty." |
| Must be a list          | `[1, 2]`         | `"1,2,3"`         | "Page sequence must be a list of integers."|
| Elements must be int    | `[1, 2, 3]`      | `[1, "a", 3]`     | "All page values must be integers."        |
| Elements must be ≥ 0    | `[0, 1, 2]`      | `[1, -2, 3]`      | "Page values must be non-negative."        |

### 5.2 Frame Count

| Rule                 | Valid Example | Invalid Example | Error Message                              |
|----------------------|---------------|-----------------|--------------------------------------------|
| Must be an integer   | `3`           | `3.5`           | "Frame count must be an integer."          |
| Must be positive     | `1`           | `0`             | "Frame count must be at least 1."          |
| Must not be negative | `4`           | `-1`            | "Frame count must be at least 1."          |

### 5.3 Dataset File

| Rule                        | Error Message                                    |
|-----------------------------|--------------------------------------------------|
| File must exist             | "Dataset file not found: {path}"                 |
| File must be valid JSON     | "Invalid JSON format in dataset file."           |
| Must have `page_sequence`   | "Dataset missing required field: page_sequence." |
| Must have `frame_count`     | "Dataset missing required field: frame_count."   |
| Field types must be correct | "Field '{name}' has invalid type."               |

### 5.4 General Policy

- Invalid input is **never silently modified** or coerced.
- Validation functions return `(is_valid: bool, error_message: str)` tuples.
- An empty error message string indicates valid input.

---

## 6. Python–Bash Integration

### Design

| Script                 | Purpose                                      | Windows Compatibility     |
|------------------------|----------------------------------------------|---------------------------|
| `bash/run.sh`          | Activate venv, launch `main.py`              | Git Bash on Windows       |
| `bash/system_info.sh`  | Display system info for debugging/docs       | Git Bash + CMD fallbacks  |
| `bash/batch_simulation.sh` | Automate simulations over all datasets   | Git Bash on Windows       |

### Project Root Detection

All Bash scripts use reliable project-root detection:

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
```

This works regardless of where the script is called from.

### Virtual Environment Activation

Scripts look for the Windows venv activation script:

```bash
source "$PROJECT_ROOT/venv/Scripts/activate"
```

Note: On Windows, the activation script is at `venv/Scripts/activate`, not `venv/bin/activate` (which is Linux/macOS).

---

## 7. Design Decisions

| Decision                              | Rationale                                               |
|---------------------------------------|---------------------------------------------------------|
| Plain dictionaries over dataclasses   | Simpler for students, JSON-serializable, easy to debug  |
| No abstract base class for algorithms | Three algorithms with identical signatures don't need it |
| `NotImplementedError` for stubs       | Clear signal that code is planned, not broken            |
| `(bool, str)` validation return       | Simple, explicit, no custom exception classes needed     |
| Matplotlib only for visualization     | Lightweight, well-known, available via pip               |
| JSON for input datasets               | Human-readable, Python stdlib support, no extra deps     |
| CSV for output reports                | Universal format, Python stdlib `csv` module             |
| unittest for tests                    | Standard library, no extra dependency; pytest compatible |
| Logging via `logging` module          | Standard library, configurable, no external dependency   |
