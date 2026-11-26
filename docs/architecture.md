# Memora — System Architecture & Technical Specifications

## 1. System Overview

Memora is an integrated, modular Operating Systems resource-management simulation suite. It models, simulates, and benchmarks three foundational operating system control functions:
1. **Virtual Memory Management:** Page replacement algorithms (FIFO, LRU, Optimal) under demand paging.
2. **CPU Scheduling:** Process scheduling algorithms (FCFS, Non-Preemptive SJF, Round Robin) with Gantt timeline generation.
3. **Deadlock Management:** Banker's Algorithm for deadlock avoidance (safety algorithm and resource request evaluation).

The architecture follows strict separation of concerns across presentation, API routing, simulation dispatching, algorithm execution, mathematical metrics calculation, and data validation.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                                │
│    Multi-Module Web Dashboard (HTML5 / CSS3 / ES6 JS / Canvas Charts)       │
│             Command-Line Interface (main.py)  ·  Bash Scripts               │
├─────────────────────────────────────────────────────────────────────────────┤
│                          API & ROUTING LAYER                                │
│         Flask 3.0 REST Blueprint (src/api/routes.py, src/api/app.py)        │
│    /api/health · /api/simulate · /api/compare · /api/cpu/* · /api/deadlock/*│
├─────────────────────────────────────────────────────────────────────────────┤
│                   RESOURCE MANAGEMENT CORE SUBSYSTEMS                       │
│                                                                             │
│  [1. VIRTUAL MEMORY]        [2. CPU SCHEDULING]       [3. DEADLOCK MGMT]   │
│  • src/core/simulator.py    • src/cpu/scheduler.py    • src/deadlock/      │
│  • src/core/metrics.py      • src/cpu/metrics.py        bankers.py         │
│  • src/core/validator.py    • src/cpu/validator.py    • src/deadlock/      │
│  • src/algorithms/          • src/cpu/fcfs.py           validator.py       │
│    (fifo, lru, optimal)     • src/cpu/sjf.py                               │
│                             • src/cpu/round_robin.py                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                       ANALYSIS & VISUALIZATION LAYER                        │
│   src/analysis/comparison.py  ·  src/analysis/visualization.py (Matplotlib) │
├─────────────────────────────────────────────────────────────────────────────┤
│                         SHARED UTILITIES LAYER                              │
│         src/utils/file_handler.py (JSON/CSV)  ·  src/utils/logger.py        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Subsystem Architecture & Responsibilities

### 2.1 Virtual Memory Management (`src/algorithms/`, `src/core/`)

- **`src/algorithms/fifo.py`:** First-In, First-Out queue-based replacement.
- **`src/algorithms/lru.py`:** Least Recently Used timestamp-based replacement.
- **`src/algorithms/optimal.py`:** Bélády's lookahead scan with deterministic tie-breaking.
- **`src/core/simulator.py`:** Dispatches simulation requests and compiles step-by-step memory frame traces.
- **`src/core/metrics.py`:** Calculates $H, F, HR, FR$, and asserts the invariant $HR + FR = 100\%$.
- **`src/core/validator.py`:** Validates non-negative integer pages and $1 \le frames \le 8$.

### 2.2 CPU Scheduling Subsystem (`src/cpu/`)

- **`src/cpu/validator.py`:** Validates process lists ($PID \ne \emptyset$, $AT \ge 0$, $BT > 0$) and time quantum ($q > 0$).
- **`src/cpu/metrics.py`:**
  - $TAT = CT - AT$
  - $WT = TAT - BT$
  - $RT = \text{first\_start} - AT$
  - $U\% = (\text{busy\_time} / \text{total\_time}) \times 100$
  - $Throughput = \text{completed\_processes} / \text{total\_time}$
- **`src/cpu/fcfs.py`:** First-Come First-Served non-preemptive queue scheduling with idle gap insertion.
- **`src/cpu/sjf.py`:** Non-preemptive Shortest Job First scheduling. Picks process with minimum burst from ready pool; breaks ties using arrival time, then process ID.
- **`src/cpu/round_robin.py`:** Preemptive time-sliced execution using quantum $q$. Newly arrived processes at time $t$ are enqueued *before* a process preempted at $t$.
- **`src/cpu/scheduler.py`:** Dispatcher and multi-algorithm comparison engine returning comparative metrics.

### 2.3 Deadlock Management Subsystem (`src/deadlock/`)

- **`src/deadlock/validator.py`:**
  - Validates dimension match ($n \times m$ matrices for Allocation and Max).
  - Validates Available vector of length $m$.
  - Enforces invariant: $Allocation[i][j] \le Max[i][j]$ for all $i, j$.
  - Validates resource request vectors ($Request \le Need$, $Request \le Available$).
- **`src/deadlock/bankers.py`:**
  - `compute_need_matrix()`: Computes $Need[i][j] = Max[i][j] - Allocation[i][j]$.
  - `check_safety()`: Runs the Banker's Safety Algorithm to locate a safe sequence $\langle P_1, P_2, \dots, P_n \rangle$. Returns safe status, safe sequence, step-by-step trace, and academic explanation.
  - `simulate_resource_request()`: Tests hypothetical resource allocations without side effects.

---

## 3. Data Contracts & JSON Schemas

### 3.1 Memory Simulation Schema (`POST /api/simulate`)
```json
{
  "algorithm": "LRU",
  "frame_count": 3,
  "total_pages": 4,
  "hits": 1,
  "faults": 3,
  "hit_ratio": 0.25,
  "fault_ratio": 0.75,
  "sequence": [1, 2, 3, 1],
  "history": [
    {
      "step": 0,
      "page": 1,
      "frames": [1, null, null],
      "is_hit": false,
      "evicted": null
    }
  ]
}
```

### 3.2 CPU Scheduling Schema (`POST /api/cpu/schedule`)
```json
{
  "algorithm": "RR",
  "algorithm_name": "Round Robin",
  "time_quantum": 2,
  "processes": [
    {
      "id": "P1",
      "arrival_time": 0,
      "burst_time": 4,
      "completion_time": 7,
      "turnaround_time": 7,
      "waiting_time": 3,
      "response_time": 0
    }
  ],
  "gantt_chart": [
    {"process": "P1", "start": 0, "end": 2},
    {"process": "P2", "start": 2, "end": 4},
    {"process": "P1", "start": 4, "end": 6}
  ],
  "metrics": {
    "total_time": 7,
    "busy_time": 7,
    "idle_time": 0,
    "cpu_utilization": 100.0,
    "throughput": 0.2857,
    "avg_waiting_time": 3.0,
    "avg_turnaround_time": 7.0,
    "avg_response_time": 0.0
  }
}
```

### 3.3 Deadlock Safety Evaluation Schema (`POST /api/deadlock/safety`)
```json
{
  "is_safe": true,
  "safe_sequence": ["P1", "P3", "P4", "P0", "P2"],
  "available": [3, 3, 2],
  "allocation": [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]],
  "max": [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]],
  "need": [[7, 4, 3], [1, 2, 2], [6, 0, 0], [0, 1, 1], [4, 3, 1]],
  "steps": [
    {
      "step": 1,
      "process": "P1",
      "work_before": [3, 3, 2],
      "need": [1, 2, 2],
      "allocation": [2, 0, 0],
      "work_after": [5, 3, 2],
      "status": "Granted & Completed"
    }
  ],
  "explanation": "System is in a SAFE STATE. A valid safe execution sequence exists: P1 -> P3 -> P0 -> P2 -> P4."
}
```

---

## 4. Error Handling & Invariants

All subsystems implement defensive validation:
1. **Type & Value Enforcement:** All inputs are strictly type-checked. Booleans are rejected where integers are required.
2. **Deterministic Tie-Breaking:**
   - In Optimal page replacement, ties for pages never seen again are broken by lowest frame index.
   - In SJF CPU scheduling, burst ties are broken by arrival time, then PID.
   - In Banker's algorithm, scanning restarts from $P_0$ after each successful allocation.
3. **Idempotence & Statelessness:** API routes do not persist mutable state between requests, guaranteeing reproducible simulation runs.
