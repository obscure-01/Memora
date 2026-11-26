# Memora

**Memora: A Virtual Memory Simulator for Page Replacement Algorithm Analysis**

A command-line-based educational simulator for Operating Systems coursework that demonstrates how page replacement algorithms manage limited memory frames.

---

## Problem Statement

In operating systems, virtual memory management requires deciding which pages to keep in limited physical memory frames. When a page fault occurs and all frames are occupied, a **page replacement algorithm** selects which existing page to evict. Different algorithms make different decisions, leading to varying numbers of page faults.

Understanding these algorithms — their mechanics, trade-offs, and performance characteristics — is essential for Computer Science students. However, manually tracing algorithms on paper is tedious and error-prone.

**Memora** automates this process by simulating page replacement, tracking every step, and comparing algorithm performance with clear metrics and visualizations.

---

## Objectives

1. Simulate three fundamental page replacement algorithms: **FIFO**, **LRU**, and **Optimal**.
2. Provide step-by-step memory state history for each page access.
3. Calculate performance metrics: page hits, page faults, hit ratio, and fault ratio.
4. Compare all three algorithms on identical input to highlight their differences.
5. Generate visual performance charts using Matplotlib.
6. Export results to CSV for further analysis.
7. Provide a Bash-based launcher compatible with Git Bash on Windows.

---

## Features

### ✅ Completed (Phase 1 & Phase 2)
- **FIFO Page Replacement:** Simulates strict first-in, first-out replacement order with stationary frame slots and eviction tracking.
- **LRU Page Replacement:** Simulates least recently used page replacement by tracking most recent access steps.
- **Optimal Page Replacement:** Simulates Bélády's optimal algorithm looking ahead in the reference string, with deterministic tie-breaking.
- **Simulation Engine:** Central dispatcher in `src/core/simulator.py` supporting single-algorithm execution and multi-algorithm batch comparison.
- **Performance Metrics:** Derived hit/fault counts, hit ratio, and fault ratio ($H/N$, $F/N$, satisfying $H + F = N$).
- **Interactive & CLI Interface:** Menu-driven console interface with argument parsing (`--demo`, `--batch`, `--pages`, `--frames`, `--algo`, `--dataset`).
- **Algorithm Comparison:** Side-by-side comparison tables identifying top-performing algorithms and handling tied winners without arbitrary selection.
- **Visual Performance Charts:** Matplotlib-generated fault comparison bars, hit ratio charts, and side-by-side hits vs. faults summaries.
- **CSV Data Export:** Automated export of single, comparison, and batch simulation runs to `results/reports/`.
- **Predefined Datasets:** 8 representative datasets for demonstrations, edge cases, and comparisons in `datasets/sample_input.json`.
- **Defensive Validation:** Strict checking for empty sequences, negative pages, invalid frame counts, and explicit boolean rejection.
- **Bash Automation:** Windows Git Bash launchers (`run.sh`, `system_info.sh`, `batch_simulation.sh`) with auto-detection of `venv`/`.venv`.

### 🔲 Planned (Phase 3 — Extended Analysis & Submission)
- Extended multi-sequence empirical analysis
- Formal academic project report and slide deck
- Final viva demonstration scripts and screenshots

---

## Technology Stack

| Component         | Technology              |
|-------------------|-------------------------|
| Language          | Python 3.8+ (3.10+ recommended) |
| Backend API       | Flask, Flask-CORS       |
| Visualization     | Matplotlib              |
| Data Formats      | JSON (input), CSV (output) |
| Shell Integration | Bash (Git Bash on Windows) |
| Version Control   | Git & GitHub            |
| Testing           | unittest / pytest       |
| Editor            | Visual Studio Code      |

---

## Project Architecture

```
Memora/
├── app.py                     # Flask backend entry point (REST API)
├── main.py                    # CLI application entry point
├── README.md                  # Master documentation
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git exclusion rules
│
├── src/                       # Source code
│   ├── algorithms/            # Page replacement algorithms
│   │   ├── fifo.py            #   FIFO implementation
│   │   ├── lru.py             #   LRU implementation
│   │   └── optimal.py         #   Optimal implementation
│   │
│   ├── core/                  # Core simulation modules
│   │   ├── simulator.py       #   Simulation orchestrator
│   │   ├── metrics.py         #   Performance metrics calculator
│   │   └── validator.py       #   Input validation
│   │
│   ├── analysis/              # Analysis and reporting
│   │   ├── comparison.py      #   Algorithm comparison
│   │   └── visualization.py   #   Chart generation (Matplotlib)
│   │
│   ├── api/                   # Flask REST API Layer
│   │   ├── app.py             #   Flask app factory & CORS configuration
│   │   └── routes.py          #   API route handlers (/api/health, /api/simulate, /api/compare)
│   │
│   └── utils/                 # Shared utilities
│       ├── file_handler.py    #   JSON/CSV file operations
│       └── logger.py          #   Logging configuration
│
├── bash/                      # Bash scripts (Git Bash compatible)
│   ├── run.sh                 #   Main launcher
│   ├── system_info.sh         #   System information display
│   └── batch_simulation.sh    #   Batch dataset simulation
│
├── datasets/                  # Input datasets
│   ├── sample_input.json      #   Sample simulation datasets
│   └── test_cases.json        #   Verified test cases
│
├── results/                   # Generated output (not committed)
│   ├── reports/               #   CSV reports
│   ├── charts/                #   PNG charts
│   └── logs/                  #   Application logs
│
├── tests/                     # Unit tests (54 passing tests)
│   ├── test_fifo.py
│   ├── test_lru.py
│   ├── test_optimal.py
│   ├── test_metrics.py
│   ├── test_validator.py
│   ├── test_simulator.py
│   ├── test_utils.py
│   ├── test_datasets.py
│   └── test_api.py            #   Flask API endpoint tests
│
└── docs/                      # Documentation
    ├── architecture.md        #   System architecture
    ├── project_report.md      #   Academic project report
    ├── phase1_audit_report.md #   Quality audit report
    └── screenshots/           #   Demonstration screenshots
```

---

## Installation (Windows)

### Prerequisites
- **Python 3.8 or later** — [Download](https://www.python.org/downloads/)
- **Git** — [Download](https://git-scm.com/downloads) (includes Git Bash)
- **Visual Studio Code** (recommended) — [Download](https://code.visualstudio.com/)

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/<your-username>/Memora.git
   cd Memora
   ```

2. **Create a Python virtual environment:**
   ```cmd
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   **Command Prompt (CMD):**
   ```cmd
   venv\Scripts\activate
   ```

   **Git Bash:**
   ```bash
   source venv/Scripts/activate
   ```

   **PowerShell:**
   ```powershell
   venv\Scripts\Activate.ps1
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Verify the installation:**
   ```bash
   python main.py
   ```

---

## Usage

### Run via Python (CMD or PowerShell)
```cmd
python main.py
```

### Run via Bash (Git Bash)
```bash
bash bash/run.sh
```

### View System Information (Git Bash)
```bash
bash bash/system_info.sh
```

### Run Tests
```bash
python -m pytest tests/
```
or
```bash
python -m unittest discover -s tests
```

> **Note:** All simulation, comparison, CLI, batch, and visualization features are fully operational.

---

## Project Phases

| Phase | Focus                                                | Status         |
|-------|------------------------------------------------------|----------------|
| 1     | Flask Backend/API Integration                        | ✅ Complete     |
| 2     | Interactive Frontend                                 | 🔲 Planned     |
| 3     | Integration, Comparison, Polish, and Final Submission| 🔲 Planned     |

---

## Algorithms Overview

| Algorithm | Strategy                        | Type        |
|-----------|---------------------------------|-------------|
| FIFO      | Replace the oldest page         | Practical   |
| LRU       | Replace the least recently used | Practical   |
| Optimal   | Replace the farthest future use | Theoretical |

For detailed algorithm specifications, see [docs/architecture.md](docs/architecture.md).

---

## Flask Backend & REST API

Memora includes a lightweight Flask REST backend that exposes the simulation engine for web clients and future frontend integration (planned for Phase 2).

### Start the Flask Backend Server
```bash
python app.py
```
Server runs locally on `http://127.0.0.1:5000`.

### API Endpoints

#### 1. Health Check
- **Route:** `GET /api/health`
- **Description:** Verifies that the API backend is running.
- **Response:**
  ```json
  {
    "status": "ok",
    "application": "Memora"
  }
  ```

#### 2. Run Simulation
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
- **Supported Algorithms:** `"FIFO"`, `"LRU"`, `"OPTIMAL"` (or `"Optimal"`, case-insensitive).
- **Response:**
  ```json
  {
    "algorithm": "FIFO",
    "sequence": [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1],
    "frame_count": 3,
    "total_pages": 20,
    "hits": 5,
    "faults": 15,
    "hit_ratio": 0.25,
    "fault_ratio": 0.75,
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

#### 3. Compare Algorithms
- **Route:** `POST /api/compare`
- **Description:** Runs FIFO, LRU, and Optimal algorithms on identical input and returns comparative metrics.
- **Request Body:**
  ```json
  {
    "sequence": [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1],
    "frames": 3
  }
  ```
- **Response:**
  ```json
  {
    "sequence": [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1],
    "frame_count": 3,
    "total_pages": 20,
    "results": {
      "FIFO": {
        "hits": 5,
        "faults": 15,
        "hit_ratio": 0.25,
        "fault_ratio": 0.75
      },
      "LRU": {
        "hits": 8,
        "faults": 12,
        "hit_ratio": 0.4,
        "fault_ratio": 0.6
      },
      "OPTIMAL": {
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

### Run Backend Unit Tests
```bash
python -m unittest tests/test_api.py -v
```

---

## License

This project is developed as a B.Tech Operating Systems capstone project for academic purposes.

---

## Author

B.Tech CSE Student — Operating Systems Capstone Project
