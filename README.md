# Memora

**Memora: An Integrated Operating Systems Resource-Management Simulator**

An educational, interactive, and analytical Operating Systems simulator for understanding, demonstrating, and evaluating foundational OS resource-management functions:
1. **Virtual Memory Management:** Page replacement algorithms (FIFO, LRU, Optimal) & Bélády's Anomaly analysis.
2. **CPU Scheduling:** Process execution, interactive Gantt charts, and comparative performance (FCFS, Non-Preemptive SJF, Round Robin with configurable time quantum).
3. **Deadlock Management:** Banker's Algorithm for deadlock avoidance (Available, Allocation, Max, Need matrices, safety check, safe execution sequence, and dynamic resource-request simulation).

---

## 1. Executive Summary & Project Context

Operating systems manage hardware resources through three critical control subsystems:
- **Memory Management:** Allocating memory to processes and swapping pages between physical RAM and backing store via demand paging.
- **CPU Scheduling:** Deciding which ready process is assigned the CPU core to optimize turnaround, waiting time, and system throughput.
- **Deadlock Management:** Ensuring that dynamic resource allocations never lead to circular wait conditions where processes block indefinitely.

**Memora** brings these three resource-management functions into a unified, interactive platform designed for undergraduate Operating Systems education (B.Tech CSE Capstone / Lab coursework). It features:
- A responsive, multi-module web dashboard with hardware memory rack, Canvas charts, interactive CPU Gantt charts, and Banker's matrix inspection.
- A RESTful Flask API providing endpoints for simulation, comparative benchmarking, and safety evaluation.
- An interactive command-line interface (CLI) and automated shell scripts for headless batch execution and viva demonstrations.
- An automated test suite containing **96 passing unit tests** covering mathematical invariants, edge cases, and API contracts.

---

## 2. Core Modules & Capabilities

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MEMORA SYSTEM ARCHITECTURE                         │
├───────────────────────┬─────────────────────────────┬───────────────────────┤
│    VIRTUAL MEMORY     │       CPU SCHEDULING        │  DEADLOCK MANAGEMENT  │
│  (Page Replacement)   │   (Process & Gantt Charts)  │  (Banker's Algorithm) │
├───────────────────────┼─────────────────────────────┼───────────────────────┤
│ • FIFO                │ • FCFS                      │ • Safety Algorithm    │
│ • LRU                 │ • Non-Preemptive SJF        │ • Need Matrix Calc    │
│ • Bélády's Optimal    │ • Round Robin (Quantum q)   │ • Safe Sequence Trace │
│ • 1 to 8 Frame Pools  │ • Gantt Chart Timeline      │ • Dynamic Requests    │
│ • Hit / Fault Ratios  │ • CT, TAT, WT, RT Metrics   │ • Safe vs Unsafe State│
│ • Bélády's Anomaly    │ • CPU Utilization %         │ • Multi-Resource Avoid│
└───────────────────────┴─────────────────────────────┴───────────────────────┘
```

### Module 1: Virtual Memory Management
- **Algorithms:** First-In First-Out (**FIFO**), Least Recently Used (**LRU**), and Bélády's **Optimal** algorithm.
- **Configurable Frame Count:** Allocations from 1 to 8 physical memory frames.
- **Hardware Memory Rack:** Real-time visual display showing cold-start loads, resident hits, and victim evictions.
- **Step-by-Step Playback:** Automated playback with variable speed ($0.5\times$, $1\times$, $2\times$), step forward/back, and keyboard navigation (`Space`, `←`, `→`).
- **Bélády’s Anomaly Demonstration:** Automated comparison demonstrating that FIFO can yield more page faults when allocated additional frames.

### Module 2: CPU Scheduling
- **Algorithms:** First-Come First-Served (**FCFS**), Non-Preemptive Shortest Job First (**SJF**), and **Round Robin (RR)** with configurable time quantum $q$.
- **Process Workload Editor:** Dynamic addition and deletion of processes with arrival times ($AT \ge 0$) and burst times ($BT > 0$).
- **Interactive Gantt Chart:** Visual horizontal timeline detailing execution intervals, process switches, and CPU idle gaps.
- **Standard Process Metrics:** Turnaround Time ($TAT$), Waiting Time ($WT$), Response Time ($RT$), Completion Time ($CT$), Average Waiting Time ($AWT$), Average Turnaround Time ($ATAT$), Average Response Time ($ART$), CPU Utilization ($U\%$), and System Throughput.
- **Multi-Algorithm Comparison:** Simultaneous evaluation ranking algorithms by AWT and ATAT.

### Module 3: Deadlock Management (Banker's Algorithm)
- **Safety Algorithm:** Formally verifies whether the system is in a **Safe State** where all processes can run to completion under maximum declared claims.
- **Matrix Calculations:** Computes the Need matrix ($Need[i][j] = Max[i][j] - Allocation[i][j]$) and verifies state invariants ($\text{Allocation} \le \text{Max}$, $\sum \text{Alloc} + \text{Available} = \text{Total}$).
- **Safe Execution Sequence:** Discovers and outputs a valid topological execution sequence (e.g. $P_1 \rightarrow P_3 \rightarrow P_4 \rightarrow P_0 \rightarrow P_2$).
- **Step-by-Step Allocation Trace:** Tabular audit trail showing `Work_before`, `Need`, `Allocation`, `Work_after`, and process completion status.
- **Resource-Request Simulation:** Evaluates dynamic requests using the two-phase safety test: ensures $Request \le Need$ and $Request \le Available$, grants hypothetical allocation, and checks safety before deciding whether to approve the request or force the process to wait.

---

## 3. Mathematical Foundations & Metric Definitions

### Virtual Memory Formulas
$$\text{Total Accesses } (N) = \text{Page Hits } (H) + \text{Page Faults } (F)$$
$$\text{Hit Ratio } (HR) = \left( \frac{H}{N} \right) \times 100\%, \quad \text{Fault Ratio } (FR) = \left( \frac{F}{N} \right) \times 100\%$$
$$\text{Mathematical Invariant: } HR + FR = 100.00\%$$

### CPU Scheduling Formulas
$$\text{Turnaround Time } (TAT) = \text{Completion Time } (CT) - \text{Arrival Time } (AT)$$
$$\text{Waiting Time } (WT) = \text{Turnaround Time } (TAT) - \text{Burst Time } (BT)$$
$$\text{Response Time } (RT) = \text{First CPU Start Time } - \text{Arrival Time } (AT)$$
$$\text{CPU Utilization } (U) = \left( \frac{\text{Total Busy Time}}{\text{Total Simulation Time}} \right) \times 100\%$$
$$\text{Throughput } (TP) = \frac{\text{Number of Completed Processes}}{\text{Total Simulation Time}}$$

### Deadlock Avoidance Formulas (Banker's Algorithm)
$$Need[i][j] = Max[i][j] - Allocation[i][j] \quad \forall i \in [0, n-1], j \in [0, m-1]$$
$$\text{Allocation Invariant: } Allocation[i][j] \le Max[i][j]$$
$$\text{Safety Condition: } \exists \text{ sequence } \langle P_1, P_2, \dots, P_n \rangle \text{ such that } Need[i] \le Work \text{ at each step}$$
$$\text{Academic Distiction: } \text{Unsafe State} \neq \text{Deadlock}. \text{ An unsafe state implies the OS cannot guarantee avoidance of deadlock.}$$

---

## 4. Academic Demonstration Results

### Part 1: Virtual Memory Reference Case
Using the standard Operating Systems textbook reference sequence (Silberschatz, Galvin & Gagne):
- **Page String:** `[7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]` ($N=20$)
- **Frame Allocation:** $m = 3$ frames

| Algorithm | Page Faults | Page Hits | Hit Ratio (%) | Fault Ratio (%) | Outcome |
|:---|:---:|:---:|:---:|:---:|:---|
| **FIFO** | **15** | 5 | 25.00% | 75.00% | High thrashing; evicts Page 0 right before next reference |
| **LRU** | **12** | 8 | 40.00% | 60.00% | Exploits temporal locality; protects active working set |
| **Optimal** | **9** | 11 | 55.00% | 45.00% | Theoretical maximum hit ratio benchmark (Bélády) |

### Part 2: CPU Scheduling Workload
Using a standard 4-process staggered workload with Round Robin quantum $q = 2$:
- $P_1: AT=0, BT=5$
- $P_2: AT=1, BT=3$
- $P_3: AT=2, BT=8$
- $P_4: AT=3, BT=6$

| Algorithm | Avg Waiting Time (AWT) | Avg Turnaround Time (ATAT) | Avg Response Time (ART) | CPU Utilization | Throughput |
|:---|:---:|:---:|:---:|:---:|:---:|
| **FCFS** | 5.75 ms | 11.25 ms | 5.75 ms | 100.00% | 0.1818 p/ms |
| **SJF (Non-Preemptive)** | **5.25 ms** | **10.75 ms** | **5.25 ms** | 100.00% | 0.1818 p/ms |
| **Round Robin ($q=2$)** | 9.75 ms | 15.25 ms | **2.00 ms** | 100.00% | 0.1818 p/ms |

**Key Academic Findings:**
- **SJF minimizes AWT and ATAT:** Prioritizing short jobs reduces waiting time across the ready queue.
- **Round Robin optimizes ART:** Interactive response time drops to 2.00 ms (best for multi-user OS) at the expense of higher context-switch overhead and turnaround time.

### Part 3: Deadlock Management (Silberschatz Reference Case)
- **Processes:** 5 processes ($P_0$ through $P_4$)
- **Resource Types:** 3 resource types ($A, B, C$)
- **Available Vector:** $[3, 3, 2]$
- **Allocation Matrix:** $P_0=[0,1,0], P_1=[2,0,0], P_2=[3,0,2], P_3=[2,1,1], P_4=[0,0,2]$
- **Max Claim Matrix:** $P_0=[7,5,3], P_1=[3,2,2], P_2=[9,0,2], P_3=[2,2,2], P_4=[4,3,3]$

**Results:**
- **System Verdict:** `SAFE STATE`
- **Safe Execution Sequence:** $P_1 \rightarrow P_3 \rightarrow P_0 \rightarrow P_2 \rightarrow P_4$
- **Resource Request Test 1:** $P_1$ requests $[1, 0, 2] \rightarrow$ **GRANTED** (safe sequence remains valid).
- **Resource Request Test 2:** $P_0$ requests $[0, 2, 0] \rightarrow$ **DENIED / MUST WAIT** (granting leaves system unable to guarantee completion).

---

## 5. Technology Stack

| Layer | Component | Description |
|:---|:---|:---|
| **Programming Language** | Python 3.8+ (3.10+ recommended) | Core engines, data structures, and CLI |
| **Backend Framework** | Flask 3.0+ & Flask-CORS 4.0+ | REST API, validation middleware, and static asset router |
| **Frontend Presentation** | Semantic HTML5 & CSS3 | Responsive engineering dark theme, custom tabs, Gantt layout |
| **Frontend Dynamics** | Vanilla JavaScript (ES6+) | Modular client (`api.js`, `charts.js`, `visualizer.js`, `app.js`) |
| **Client-Side Charts** | HTML5 Canvas API | High-DPI bar charts without third-party dependencies |
| **Server-Side Charts** | Matplotlib 3.7+ | Headless PNG generation for CLI exports (Gantt and comparison) |
| **Data Formats** | JSON & CSV | API payloads, workload datasets, and report exports |
| **Testing Engine** | Python `unittest` | 96 comprehensive tests across all modules (100% passing) |
| **Shell Scripting** | Bash (Git Bash / Linux / WSL) | Interactive launcher and automated batch execution |

---

## 6. Project Architecture

```text
Memora/
├── app.py                         # Flask web application entry point (127.0.0.1:5000)
├── main.py                        # Unified interactive CLI & command-line interface
├── requirements.txt               # Python package dependencies
├── README.md                      # Comprehensive project documentation
├── .gitignore                     # Git ignore rules
│
├── templates/
│   └── index.html                 # Multi-module interactive web dashboard
│
├── static/
│   ├── css/
│   │   └── style.css              # Technical dark theme, module tabs & Gantt styling
│   └── js/
│       ├── api.js                 # REST API client for Memory, CPU, and Deadlock
│       ├── charts.js              # HTML5 Canvas chart renderer
│       ├── visualizer.js          # Memory frame rack & playback controller
│       └── app.js                 # Full-stack UI orchestrator for all 3 modules
│
├── src/
│   ├── algorithms/                # Memory page replacement algorithms
│   │   ├── fifo.py                #   FIFO implementation
│   │   ├── lru.py                 #   LRU implementation
│   │   └── optimal.py             #   Optimal (Bélády) implementation
│   │
│   ├── core/                      # Memory core engine
│   │   ├── simulator.py           #   Dispatcher and execution tracker
│   │   ├── metrics.py             #   Memory hits/faults formulas
│   │   └── validator.py           #   Memory sequence and frame validator
│   │
│   ├── cpu/                       # CPU Scheduling Subsystem
│   │   ├── fcfs.py                #   First-Come First-Served scheduler
│   │   ├── sjf.py                 #   Non-preemptive Shortest Job First scheduler
│   │   ├── round_robin.py         #   Preemptive Round Robin scheduler
│   │   ├── metrics.py             #   CT, TAT, WT, RT, utilization, throughput
│   │   ├── scheduler.py           #   CPU dispatcher & multi-algorithm comparison
│   │   └── validator.py           #   Process definition & quantum validation
│   │
│   ├── deadlock/                  # Deadlock Management Subsystem
│   │   ├── bankers.py             #   Safety algorithm & resource request engine
│   │   └── validator.py           #   Matrix dimensions & claim validation
│   │
│   ├── analysis/                  # Comparison & visual plotting
│   │   ├── comparison.py          #   Memory comparative analysis
│   │   └── visualization.py       #   Matplotlib charts (Memory & CPU Gantt)
│   │
│   ├── api/                       # Flask REST API backend
│   │   ├── app.py                 #   Application factory
│   │   └── routes.py              #   REST routes for all 3 subsystems
│   │
│   └── utils/                     # Utility services
│       ├── file_handler.py        #   Dataset and CSV file handlers
│       └── logger.py              #   Standard system logger
│
├── datasets/                      # Preloaded academic datasets
│   ├── sample_input.json          #   8 Virtual Memory datasets
│   ├── test_cases.json            #   Precomputed verification cases
│   ├── cpu_scheduling_samples.json # 4 CPU workload configurations
│   └── deadlock_samples.json      #   3 Banker's Algorithm test scenarios
│
├── bash/                          # Automated shell scripts
│   ├── run.sh                     #   Interactive launcher menu & flag forwarder
│   ├── batch_simulation.sh        #   Automated batch simulation runner
│   └── system_info.sh             #   Environment diagnostic utility
│
├── results/                       # Generated artifacts
│   ├── charts/                    #   PNG comparison figures & Gantt charts
│   ├── logs/                      #   Execution trace logs
│   └── reports/                   #   CSV export reports
│
└── tests/                         # Automated unit test suite (96 tests)
    ├── test_api.py                #   Flask API endpoint & static route tests
    ├── test_cpu_scheduling.py     #   CPU scheduling algorithms, Gantt & metrics
    ├── test_deadlock.py           #   Banker's safety & request algorithm tests
    ├── test_mathematical_audit.py #   Independent mathematical verification & benchmark regressions
    ├── test_fifo.py               #   FIFO eviction logic & anomaly tests
    ├── test_lru.py                #   LRU recency updates & cache hit tests
    ├── test_optimal.py            #   Optimal future lookahead tests
    ├── test_metrics.py            #   Memory metric invariant calculations
    ├── test_simulator.py          #   Memory simulation dispatcher tests
    ├── test_validator.py          #   Defensive input validation tests
    ├── test_datasets.py           #   Dataset schema integrity tests
    └── test_utils.py              #   File I/O and logger verification tests
```

---

## 7. Installation and Setup

### Prerequisites
- **Python:** Version 3.8+ (3.10+ recommended)
- **Operating System:** Windows, Linux, or macOS

### 1. Clone the Repository
```bash
git clone https://github.com/obscure-01/Memora.git
cd Memora
```

### 2. Set Up Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Windows (Git Bash) / Linux / macOS:**
```bash
python -m venv venv
source venv/Scripts/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the Web Dashboard
```bash
python app.py
```
Open your browser at `http://127.0.0.1:5000` to interact with all three modules.

### 5. Launch the Command-Line Interface (CLI)
```bash
# Interactive menu:
python main.py

# Or via Bash launcher:
bash bash/run.sh
```

---

## 8. CLI Commands & Demonstration Flags

| Command | Subsystem | Action |
|:---|:---:|:---|
| `python main.py --demo-all` | **All 3** | **Full Capstone Viva Demonstration:** Runs Memory reference case, CPU scheduling workload, and Banker's safety check non-interactively. |
| `python main.py --demo` | Memory | Runs the classic textbook memory reference case (FIFO, LRU, Optimal). |
| `python main.py --module cpu` | CPU | Opens CPU scheduling interactive submenu. |
| `python main.py --module deadlock` | Deadlock | Opens Deadlock Management interactive submenu. |
| `python main.py --batch` | Memory | Executes batch simulations across all 8 datasets in `sample_input.json`. |
| `python main.py --pages 7,0,1,2 --frames 3 --algo LRU` | Memory | Runs specific memory algorithm from command-line arguments. |

---

## 9. REST API Reference

All API routes return standardized JSON schemas with HTTP 200 on success and HTTP 400/404/405/500 on errors.

### 1. Backend Health Check
- `GET /api/health`
- **Response:** `{"application": "Memora", "status": "ok"}`

### 2. Virtual Memory Simulation & Comparison
- `POST /api/simulate`: Body `{"sequence": [7,0,1,2], "frames": 3, "algorithm": "LRU"}`
- `POST /api/compare`: Body `{"sequence": [7,0,1,2], "frames": 3}`

### 3. CPU Scheduling Simulation & Comparison
- `POST /api/cpu/schedule`:
  ```json
  {
    "algorithm": "RR",
    "processes": [
      {"id": "P1", "arrival_time": 0, "burst_time": 5},
      {"id": "P2", "arrival_time": 1, "burst_time": 3}
    ],
    "time_quantum": 2
  }
  ```
- `POST /api/cpu/compare`: Compares FCFS, SJF, and Round Robin on identical workload.

### 4. Deadlock Management (Banker's Algorithm)
- `POST /api/deadlock/safety`:
  ```json
  {
    "available": [3, 3, 2],
    "allocation": [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]],
    "max": [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]],
    "process_names": ["P0", "P1", "P2", "P3", "P4"],
    "resource_names": ["A", "B", "C"]
  }
  ```
- `POST /api/deadlock/request`:
  ```json
  {
    "available": [3, 3, 2],
    "allocation": [[0, 1, 0], ...],
    "max": [[7, 5, 3], ...],
    "process_index": 1,
    "request": [1, 0, 2]
  }
  ```

---

## 10. Automated Testing & Verification

Run the complete test suite containing **96 passing tests**:

```bash
python -m unittest discover -s tests -v
```

### Test Coverage Summary:
- **`test_api.py` (21 tests):** Memory REST API routes, error handlers, static assets.
- **`test_cpu_scheduling.py` (10 tests):** FCFS arrival ordering, non-preemptive SJF tie-breaking, Round Robin time slicing, CPU idle periods, process validation, and `/api/cpu/*` endpoints.
- **`test_deadlock.py` (16 tests):** Banker's Safety Algorithm, classic safe state verification, unsafe state detection, resource request granting vs. rejection, matrix validation, and `/api/deadlock/*` endpoints.
- **`test_mathematical_audit.py` (12 tests):** Cross-subsystem mathematical invariants, simultaneous/staggered CPU benchmark regressions, Bélády's anomaly, and Banker's request immutability.
- **`test_fifo.py` (6 tests):** FIFO queue eviction and Bélády anomaly validation.
- **`test_lru.py` (4 tests):** Temporal recency preservation and hit updates.
- **`test_optimal.py` (3 tests):** Lookahead distance calculation and deterministic tie-breaking.
- **`test_metrics.py` (4 tests):** Memory formula consistency and invariant checks ($H+F=N$).
- **`test_simulator.py` (5 tests):** Memory central dispatcher coordination.
- **`test_validator.py` (9 tests):** Defensive boundary checks and type validation.
- **`test_datasets.py` (2 tests):** Predefined JSON dataset schema integrity.
- **`test_utils.py` (4 tests):** Directory creation, logger configuration, CSV exports.

---

## 11. Viva Defense & Examination Guide

### Q1: Why does Bélády's Anomaly occur in FIFO but never in LRU?
> **Answer:** FIFO is not a stack algorithm. A stack algorithm satisfies the inclusion property $S_m(t) \subseteq S_{m+1}(t)$, meaning the resident pages with $m$ frames are always a subset of those with $m+1$ frames. In FIFO, adding a frame shifts the order of page evictions such that pages needed in the near future are evicted prematurely, causing more faults. LRU and Optimal strictly satisfy the inclusion property and are mathematically immune to Bélády's Anomaly.

### Q2: Why is Non-Preemptive SJF optimal for Average Waiting Time?
> **Answer:** Shortest Job First schedules processes in increasing order of CPU burst. By executing shorter tasks first, subsequent jobs spend less total time queued behind large CPU bursts (avoiding the Convoy Effect), mathematically minimizing the arithmetic mean of waiting times.

### Q3: What is the difference between an Unsafe State and Deadlock in Banker's Algorithm?
> **Answer:** An **unsafe state is NOT a deadlock**. An unsafe state simply means the operating system cannot guarantee that all processes will finish if every process simultaneously requests its maximum declared claims. The system may continue running without deadlocking if processes do not invoke their maximum demands; however, to strictly avoid deadlock, the OS avoids transitions into unsafe states.

### Q4: How does Round Robin ready queue management work upon time slice expiration?
> **Answer:** When a process completes its quantum slice at time $t$, if another process arrives at the exact same clock tick $t$, the newly arriving process must be enqueued into the ready queue *before* the preempted process is re-enqueued. Memora strictly adheres to this standard Silberschatz convention.

---

## 12. Author & Repository

- **Project Title:** Memora — An Integrated Operating Systems Resource-Management Simulator
- **Coursework:** B.Tech Computer Science & Engineering, Operating Systems Capstone
- **GitHub Repository:** [https://github.com/obscure-01/Memora](https://github.com/obscure-01/Memora)
- **Project Nature:** Academic Educational Capstone Project
