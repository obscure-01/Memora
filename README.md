# Memora

**Memora: A Virtual Memory Simulator for Page Replacement Algorithm Analysis**

An interactive virtual memory simulator for understanding, demonstrating, and comparing fundamental page-replacement algorithms in Operating Systems.

---

## 1. Overview

In virtual memory operating systems, physical RAM is divided into fixed-size units called **page frames**, and virtual address spaces are partitioned into equal-sized **pages**. Because physical memory is typically smaller than the total virtual memory demanded by active processes, operating systems employ **demand paging**. When a process references a page not currently resident in physical memory, the Memory Management Unit (MMU) triggers a hardware trap known as a **page fault**.

If physical memory has free frames, the requested page is simply brought in from secondary storage. However, when all available frames are occupied, a **page replacement algorithm** must determine which resident page to evict (the "victim" page) to make room for the incoming page.

Different page replacement algorithms employ different heuristic strategies, resulting in stark differences in page fault frequencies. Manually tracing these algorithms step-by-step on paper is tedious, time-consuming, and prone to calculation errors.

**Memora** automates this process for students, educators, and system researchers. It executes page reference sequences across algorithms, renders step-by-step hardware memory frame states, calculates standard performance metrics, and conducts comparative performance evaluations through both an interactive web dashboard and a command-line interface.

---

## 2. Features

### Simulation & Analysis
- **Three Core Algorithms:** Faithful implementations of First-In, First-Out (**FIFO**), Least Recently Used (**LRU**), and Bélády's **Optimal** page replacement algorithms.
- **Configurable Frame Count:** Supports arbitrary page reference sequences with physical memory allocations ranging from 1 to 8 frames.
- **Deterministic State Tracking:** Explicit step-by-step tracking of page arrivals, frame residency, hit/fault outcomes, and victim evictions.

### Interactive Web Dashboard
- **Hardware Memory Rack:** Real-time visual representation of physical memory slots, highlighting page hits (`HIT`), new allocations (`NEWLY LOADED`), and page evictions (`REPLACED P<id>`).
- **Playback Controls:** Step-forward, step-backward, jump to start/end, and continuous automated playback with speed adjustments ($0.5\times$, $1\times$, $2\times$).
- **Keyboard Shortcuts:** Ergonomic playback via keyboard (`Spacebar` to toggle play/pause, `Left Arrow` for previous step, `Right Arrow` for next step).
- **Execution Trace Table:** Interactive tabular execution log highlighting active steps and auto-scrolling with playback.
- **Dynamic Invalidation Warnings:** Immediate visual notices if page sequences or frame counts are modified after a run, preventing stale metric analysis.

### Multi-Algorithm Comparison
- **Simultaneous Evaluation:** Evaluates FIFO, LRU, and Optimal on identical inputs under identical conditions.
- **Performance Ranking:** Identifies top-performing algorithms based on fewest page faults and cleanly reports tied winners without arbitrary selection.
- **High-Precision Charts:** Responsive client-side HTML5 Canvas bar charts comparing faults vs. hits and hit ratios (%) side-by-side without external CDN dependencies.
- **Headless Matplotlib Generation:** Matplotlib chart generation for command-line batch exports to `results/charts/`.

### Defensive Validation & Tooling
- **Strict Input Validation:** Rejects empty sequences, non-integers, negative page numbers, invalid frame counts, and explicit boolean values (`True`/`False`).
- **REST API:** Modular Flask API backend serving health checks, simulation payloads, and comparison matrices with standardized JSON schemas.
- **CSV Data Export:** Automated structured tabular export of simulation history and comparison summaries to `results/reports/`.
- **Predefined Academic Datasets:** Preloaded reference strings including standard textbook cases, Bélády's anomaly sequences, sequential workloads, and high-locality loops.

---

## 3. Algorithms

| Algorithm | Type | Strategy | Academic Significance |
|:---|:---:|:---|:---|
| **FIFO** | Practical | Evicts the page loaded earliest into memory (queue discipline) | Simple implementation; susceptible to Bélády's Anomaly |
| **LRU** | Practical | Evicts the page not accessed for the longest time in the past | Exploits temporal locality; stack algorithm immune to Bélády's Anomaly |
| **Optimal** | Theoretical | Evicts the page whose next use occurs farthest in the future (or never) | Theoretical upper bound benchmark; unrealizable in general-purpose OS |

### First-In, First-Out (FIFO)
The FIFO algorithm treats physical memory frames as a strict queue. When a page must be replaced, the page that has resided in memory the longest (the oldest loaded page) is selected for eviction.
- **Hit Condition:** If the requested page is already resident in any frame, it is counted as a page hit. Crucially, a hit does **not** update the page's position in the FIFO queue.
- **Fault Condition:** If an empty frame exists, the page is loaded into the lowest-indexed available frame and appended to the queue. If all frames are occupied, the page at the head of the queue is evicted and the new page is appended to the tail.

### Least Recently Used (LRU)
The LRU algorithm approximates optimal replacement by relying on the principle of **temporal locality**: pages referenced in the recent past are likely to be referenced again in the near future.
- **Hit Condition:** When a resident page is accessed, its last-used timestamp is updated to the current step index, moving it away from eviction candidacy.
- **Fault Condition:** If memory is full, LRU scans all resident pages, identifies the page with the minimum (oldest) access step, evicts it, and registers the new page with the current timestamp.

### Optimal (Bélády's Algorithm)
Proposed by László Bélády in 1966, the Optimal algorithm achieves the lowest possible page fault rate for any fixed sequence of memory accesses.
- **Replacement Rule:** When a page fault occurs and all frames are full, the algorithm scans the *future* portion of the reference string for each resident page. The page whose next occurrence is farthest in the future—or which is never referenced again—is selected as the victim.
- **Tie-Breaking:** If multiple pages in memory will never be referenced again, Memora breaks ties deterministically by selecting the page residing in the lowest frame index.
- **Academic Benchmark:** Optimal is strictly an offline theoretical benchmark. Because real-world operating systems cannot predict future memory references of arbitrary programs, Optimal cannot be implemented in general-purpose OS schedulers.

---

## 4. Performance Metrics

Memora computes standard academic virtual memory metrics across all simulation runs:

### Definitions & Formulas

$$\text{Total Page References } (N) = \text{Page Hits } (H) + \text{Page Faults } (F)$$

$$\text{Hit Ratio } (HR) = \left( \frac{\text{Page Hits } (H)}{\text{Total References } (N)} \right) \times 100\%$$

$$\text{Fault Ratio } (FR) = \left( \frac{\text{Page Faults } (F)}{\text{Total References } (N)} \right) \times 100\%$$

$$\text{Invariant: } HR + FR = 100.00\%$$

These ratios are defined for all non-empty page reference sequences ($N \ge 1$).

---

## 5. Demonstration Results

### Standard Reference Case

Using the classic Operating Systems textbook reference sequence (Silberschatz, Galvin & Gagne):

```text
Sequence: 7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1
Length:   20 page accesses
Frames:   3 physical frames
```

| Algorithm | Page Faults | Page Hits | Hit Ratio (%) | Fault Ratio (%) | Invariant Check ($H+F=N$) |
|:---|:---:|:---:|:---:|:---:|:---:|
| **FIFO** | **15** | **5** | 25.00% | 75.00% | $5 + 15 = 20$ |
| **LRU** | **12** | **8** | 40.00% | 60.00% | $8 + 12 = 20$ |
| **Optimal** | **9** | **11** | 55.00% | 45.00% | $11 + 9 = 20$ |

**Why Results Differ:**
- **Optimal (9 faults):** Exploits complete lookahead knowledge, avoiding evictions of pages 2 and 0 when they will be needed shortly thereafter.
- **LRU (12 faults):** Preserves frequently cycled pages (0, 2, 3) because their recent hits keep them protected.
- **FIFO (15 faults):** Blindly evicts Page 0 during step 5 because it arrived first, even though Page 0 is accessed again immediately at step 6, resulting in immediate thrashing.

---

## 6. Bélády’s Anomaly

One of the most counterintuitive phenomena in Operating Systems is **Bélády's Anomaly**: for certain page reference sequences, increasing the number of physical memory frames can actually result in an *increase* in the number of page faults under FIFO replacement.

### Verified Anomaly Demonstration

Consider the reference sequence:

```text
Sequence: 1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5
Length:   12 page accesses
```

Evaluating FIFO with 3 frames versus 4 frames:

| Allocation | Algorithm | Page Faults | Page Hits | Outcome |
|:---|:---:|:---:|:---:|:---|
| **3 Frames** | FIFO | **9** | **3** | Baseline memory allocation |
| **4 Frames** | FIFO | **10** | **2** | **Page faults INCREASE despite adding physical memory!** |

### Why Bélády's Anomaly Occurs
FIFO is **not a stack algorithm**. A page replacement algorithm is classified as a *stack algorithm* if the set of pages in memory for $m$ frames is always a subset of the pages in memory for $m+1$ frames:

$$S_m(t) \subseteq S_{m+1}(t)$$

Stack algorithms (such as **LRU** and **Optimal**) strictly satisfy this inclusion property, guaranteeing that increasing memory frames will never increase page faults:
- **LRU with 3 frames:** 10 faults $\rightarrow$ **LRU with 4 frames:** 8 faults (faults decrease)
- **Optimal with 3 frames:** 7 faults $\rightarrow$ **Optimal with 4 frames:** 6 faults (faults decrease)

Because FIFO tracks insertion timestamps rather than access patterns, adding a 4th frame alters the eviction order such that pages needed in subsequent steps are prematurely removed.

---

## 7. Operating Systems Syllabus Alignment

Memora is mapped directly to undergraduate **Operating Systems (CSE316 / CS301)** curricula:

### Unit 3 — Virtual Memory Management

| Syllabus Topic | Academic Concept | Memora Implementation |
|:---|:---|:---|
| **Demand Paging** | Loading pages into memory on demand; handling cold-start page faults vs. page hits. | Simulation engine explicitly models cold frame allocation (`None -> page`) and records step-by-step hit/fault transitions. |
| **Page Replacement Algorithms** | Mechanics of evicting resident pages when frames are exhausted. | Direct comparative implementations of FIFO, LRU, and Optimal on identical inputs. |
| **Allocation of Frames** | Impact of physical frame pool sizing ($m$) on system throughput and fault rates. | Interactive frame selector ($1 \le m \le 8$) and automated demonstration of Bélády's Anomaly. |

*Note: Memora focuses specifically on page replacement algorithm mechanics and performance analysis. It does not model hardware TLBs, MMU address translation tables, or disk I/O scheduling.*

---

## 8. Application Preview

### Interactive Dashboard Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│  MEMORA — Virtual Memory Simulator              [● Backend Online]    │
├────────────────────────┬───────────────────────────────────────────────┤
│ INPUT & CONFIGURATION  │ PHYSICAL MEMORY FRAMES (RAM)                  │
│                        │ ┌───────────┐ ┌───────────┐ ┌───────────┐     │
│ Page Sequence:         │ │  Frame 0  │ │  Frame 1  │ │  Frame 2  │     │
│ [7, 0, 1, 2, 0, 3...]  │ │     2     │ │     0     │ │     1     │     │
│                        │ │ [PAGE HIT]│ │[STATIONARY│ │[REPLACED] │     │
│ Physical Frames: [3]   │ └───────────┘ └───────────┘ └───────────┘     │
│ Stepper: [-] [3] [+]   │ Step 4 / 20: Page 0 -> HIT (In physical RAM)  │
│                        ├───────────────────────────────────────────────┤
│ Algorithm Selection:   │ PLAYBACK TIMELINE CONTROLS                    │
│ (•) FIFO ( ) LRU ( )Opt│ [|<] [<<] [ ▶ Play ] [>>] [>|]  Speed: 1x     │
│                        ├───────────────────────────────────────────────┤
│ [ Run Simulation ]     │ EXECUTION HISTORY TRACE TABLE                 │
│ [ Compare Algorithms ] │ Step | Page | Frame 0 | Frame 1 | Frame 2 ... │
└────────────────────────┴───────────────────────────────────────────────┘
│ ALGORITHM COMPARISON & HIGH-PRECISION CHARTS                           │
│ Winner: 🏆 Best: Optimal (9 Faults)                                    │
│ [Comparison Table: FIFO (15) | LRU (12) | Optimal (9)]                 │
│ [Chart 1: Faults vs. Hits]        [Chart 2: Hit Ratio (%)]             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Technology Stack

| Layer | Component | Description |
|:---|:---|:---|
| **Language** | Python 3.8+ (3.10+ recommended) | Core simulation engines, data structures, and CLI |
| **Backend Framework** | Flask 3.0+ & Flask-CORS 4.0+ | Lightweight REST API and static asset router |
| **Frontend Presentation** | HTML5 & CSS3 | Semantic layout with responsive engineering dark theme |
| **Frontend Behavior** | Vanilla JavaScript (ES6+) | Modular client (`api.js`, `charts.js`, `visualizer.js`, `app.js`) |
| **Client-Side Charts** | HTML5 Canvas API | High-DPI responsive bar charts rendered without external CDNs |
| **Server-Side Charts** | Matplotlib 3.7+ | Headless PNG generation for CLI batch comparison exports |
| **Data Serialization** | JSON & CSV | API payloads, sample datasets, and report exports |
| **Test Framework** | Python `unittest` | 58 comprehensive unit, integration, and regression tests |
| **Shell Integration** | Bash (Git Bash on Windows / POSIX) | Automated startup, batch execution, and system inspection |

---

## 10. Project Architecture

```text
Memora/
├── app.py                     # Flask web server entry point (127.0.0.1:5000)
├── main.py                    # Command-line interface entry point
├── requirements.txt           # Python package dependencies
├── README.md                  # Master project documentation
├── .gitignore                 # Git ignore rules for virtualenvs, caches, logs
│
├── templates/
│   └── index.html             # Interactive simulation dashboard template
│
├── static/
│   ├── css/
│   │   └── style.css          # Engineering dark theme and responsive layout
│   └── js/
│       ├── api.js             # REST API asynchronous client module
│       ├── charts.js          # Pure HTML5 Canvas comparison chart renderer
│       ├── visualizer.js      # Memory frame rack & timeline playback controller
│       └── app.js             # Application coordinator and UI event orchestrator
│
├── src/
│   ├── algorithms/            # Page replacement algorithm modules
│   │   ├── fifo.py            #   FIFO algorithm implementation
│   │   ├── lru.py             #   LRU algorithm implementation
│   │   └── optimal.py         #   Optimal (Bélády's) algorithm implementation
│   │
│   ├── core/                  # Core simulation and validation logic
│   │   ├── simulator.py       #   Central dispatcher and execution engine
│   │   ├── metrics.py         #   Hit/fault metrics and comparison analyzer
│   │   └── validator.py       #   Input validation for sequences and frames
│   │
│   ├── analysis/              # Comparative analysis and reporting
│   │   ├── comparison.py      #   Multi-algorithm comparative evaluation
│   │   └── visualization.py   #   Headless Matplotlib chart generator
│   │
│   ├── api/                   # REST API backend layer
│   │   ├── app.py             #   Flask application factory & blueprint registration
│   │   └── routes.py          #   API endpoint handlers (/simulate, /compare, /health)
│   │
│   └── utils/                 # Shared utilities
│       ├── file_handler.py    #   JSON dataset loading & CSV report generation
│       └── logger.py          #   Standard logging configuration
│
├── datasets/                  # Preloaded academic reference sequences
│   ├── sample_input.json      #   8 curated workload datasets
│   └── test_cases.json        #   Precomputed verification test cases
│
├── docs/                      # Architectural specifications & reports
│   ├── architecture.md        #   Technical specifications and data contracts
│   ├── project_report.md      #   Academic project report
│   └── screenshots/           #   Project demonstration visual assets
│
├── bash/                      # Automated shell scripts (Git Bash / Linux)
│   ├── run.sh                 #   Main application launcher script
│   ├── batch_simulation.sh    #   Batch simulation over all datasets
│   └── system_info.sh         #   Runtime environment and dependency diagnostics
│
├── results/                   # Generated output directories
│   ├── charts/                #   Exported Matplotlib PNG figures
│   ├── logs/                  #   Execution log files
│   └── reports/               #   Exported CSV simulation reports
│
└── tests/                     # Automated test suite
    ├── __init__.py
    ├── test_api.py            #   Flask API endpoint & static asset tests
    ├── test_fifo.py           #   FIFO unit tests & invariant verification
    ├── test_lru.py            #   LRU unit tests & recency updates
    ├── test_optimal.py        #   Optimal lookahead & tie-breaking tests
    ├── test_metrics.py        #   Mathematical formula & summary tests
    ├── test_simulator.py      #   Simulation engine dispatcher tests
    ├── test_validator.py      #   Defensive input validation boundary tests
    ├── test_datasets.py       #   Dataset schema and integrity tests
    └── test_utils.py          #   File handling and logger tests
```

---

## 11. Installation and Setup

### Prerequisites
- **Python:** Version 3.8 or higher (Python 3.10+ recommended)
- **Git:** For repository cloning
- **Operating System:** Windows, Linux, or macOS

### 1. Clone the Repository
```bash
git clone https://github.com/obscure-01/Memora.git
cd Memora
```

### 2. Set Up Virtual Environment

**On Windows (PowerShell or Command Prompt):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**On Windows (Git Bash):**
```bash
python -m venv venv
source venv/Scripts/activate
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the Web Application
```bash
python app.py
```
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

### 5. Launch the Command-Line Interface (Alternative)
```bash
python main.py
```
Or via Git Bash:
```bash
bash bash/run.sh
```

---

## 12. Usage Guide

### Web Dashboard Workflow
1. **Configure Sequence:** Enter comma-separated page numbers into the sequence textarea, select a preset button (e.g. *Reference Case*, *Belady's Anomaly*, *Locality*), or generate random numbers via *🎲 Random*.
2. **Set Frame Count:** Adjust physical memory frames between 1 and 8 using the stepper buttons (`+` / `-`) or chip presets.
3. **Select Algorithm:** Choose FIFO, LRU, or Optimal via the algorithm selector.
4. **Execute Simulation:** Click **Run Simulation**. The physical memory rack and KPI metrics update immediately.
5. **Step-by-Step Playback:** Use the playback bar to step through page accesses, inspect hits/faults, or press **Play** for animated transitions.
6. **Compare All Algorithms:** Click **Compare All Algorithms** to evaluate FIFO, LRU, and Optimal simultaneously, view the winner banner, and analyze Canvas charts.

### Command-Line Interface (CLI)
```bash
# Run interactive menu:
python main.py

# Run quick reference demonstration:
python main.py --demo

# Run specific algorithm on custom input:
python main.py --pages 7 0 1 2 0 3 0 4 2 3 --frames 3 --algo LRU

# Run comparison on custom input:
python main.py --pages 1 2 3 4 1 2 5 1 2 3 4 5 --frames 3 --compare

# Run batch simulation across all preloaded datasets:
python main.py --batch
```

---

## 13. API Documentation

Memora exposes a RESTful JSON API powered by Flask under the `/api` prefix.

### 1. Health Check
- **Route:** `GET /api/health`
- **Description:** Verifies backend connectivity and server availability.
- **Response `(200 OK)`:**
  ```json
  {
    "application": "Memora",
    "status": "ok"
  }
  ```

### 2. Run Simulation
- **Route:** `POST /api/simulate`
- **Description:** Executes a single page replacement algorithm simulation.
- **Request Body:**
  ```json
  {
    "sequence": [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1],
    "frames": 3,
    "algorithm": "FIFO"
  }
  ```
- **Response `(200 OK)`:**
  ```json
  {
    "algorithm": "FIFO",
    "frame_count": 3,
    "total_pages": 20,
    "hits": 5,
    "faults": 15,
    "hit_ratio": 0.25,
    "fault_ratio": 0.75,
    "sequence": [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1],
    "history": [
      {
        "step": 0,
        "page": 7,
        "frames": [7, null, null],
        "is_hit": false,
        "evicted": null
      },
      {
        "step": 3,
        "page": 2,
        "frames": [2, 0, 1],
        "is_hit": false,
        "evicted": 7
      }
    ]
  }
  ```

### 3. Compare Algorithms
- **Route:** `POST /api/compare`
- **Description:** Runs FIFO, LRU, and Optimal on identical inputs and returns comparative metrics.
- **Request Body:**
  ```json
  {
    "sequence": [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1],
    "frames": 3
  }
  ```
- **Response `(200 OK)`:**
  ```json
  {
    "sequence": [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1],
    "frame_count": 3,
    "total_pages": 20,
    "results": {
      "FIFO": {
        "algorithm": "FIFO",
        "hits": 5,
        "faults": 15,
        "hit_ratio": 0.25,
        "fault_ratio": 0.75
      },
      "LRU": {
        "algorithm": "LRU",
        "hits": 8,
        "faults": 12,
        "hit_ratio": 0.4,
        "fault_ratio": 0.6
      },
      "OPTIMAL": {
        "algorithm": "Optimal",
        "hits": 11,
        "faults": 9,
        "hit_ratio": 0.55,
        "fault_ratio": 0.45
      }
    },
    "summary": {
      "best_algorithm": "Optimal",
      "best_algorithms": ["Optimal"],
      "fewest_faults": 9
    }
  }
  ```

### Error Responses
All endpoints enforce input validation and return consistent error structures:
```json
{
  "error": {
    "message": "Invalid input",
    "details": "Invalid page value '-1' at index 4: page numbers must be non-negative (>= 0)."
  }
}
```

---

## 14. Testing

Memora includes an automated test suite executed with Python's built-in `unittest` runner.

### Running the Test Suite
```bash
python -m unittest discover -s tests -v
```

### Test Suite Structure (58 Tests, 100% Passing)
- **`test_api.py` (21 tests):** HTTP status codes, JSON response schemas, regression checks on reference sequences, Bélády anomaly sequence validation, 400/404/405 error handlers, dashboard delivery, and static asset serving.
- **`test_fifo.py` (6 tests):** Queue eviction order, reference sequence accuracy, single-frame edge cases, repeated pages, and frame residency invariants.
- **`test_lru.py` (4 tests):** Temporal recency updates on hits, eviction of least recently accessed pages, and reference sequence regression.
- **`test_optimal.py` (3 tests):** Lookahead distance calculation, eviction of pages never referenced again, and deterministic tie-breaking.
- **`test_metrics.py` (4 tests):** Hit/fault derivations, ratio precision, single-winner identification, and tied-winner reporting.
- **`test_simulator.py` (5 tests):** Central dispatcher coordination, case-insensitive algorithm names, and error handling.
- **`test_validator.py` (9 tests):** Boundary checks, non-negative assertions, float rejection, and explicit boolean rejection (`True`/`False`).
- **`test_datasets.py` (2 tests):** Schema integrity of `datasets/sample_input.json` and mathematical verification of `datasets/test_cases.json`.
- **`test_utils.py` (4 tests):** Directory creation, logger configuration, and CSV export file handling.

---

## 15. Limitations

For academic transparency and viva defense, note the following architectural boundaries:
1. **Logical Simulation Scope:** Memora simulates page replacement algorithms at the logical reference level. It does not interface with host kernel paging tables, secondary disk drivers, or MMU hardware caches.
2. **Optimal Realizability:** The Optimal algorithm requires complete offline knowledge of all future memory accesses. It is implemented purely as a performance benchmark and cannot be deployed in general-purpose operating system schedulers.
3. **Fixed Allocation Model:** The simulator models local fixed-frame allocation where a single process has a static allocation of frames ($1 \le m \le 8$) throughout execution, rather than global or dynamic working-set allocations.

---

## 16. Future Improvements

- **Additional Replacement Heuristics:** Implement Second-Chance (Clock), Not Recently Used (NRU), and Least Frequently Used (LFU).
- **Working-Set Dynamic Allocation:** Simulate page-fault frequency (PFF) algorithms with dynamically expanding and contracting frame pools.
- **Direct CSV Import:** Enable direct browser drag-and-drop uploading of real-world application memory address traces.

---

## 17. Author & Repository

- **Project:** Memora — Virtual Memory Simulator for Page Replacement Algorithm Analysis
- **Coursework:** B.Tech Computer Science & Engineering, Operating Systems
- **GitHub Repository:** [https://github.com/obscure-01/Memora](https://github.com/obscure-01/Memora)
- **License:** Academic Educational License
