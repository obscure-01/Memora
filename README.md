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
| Language          | Python 3.8+             |
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
├── main.py                    # Application entry point
├── README.md                  # This file
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
├── tests/                     # Unit tests
│   ├── test_fifo.py
│   ├── test_lru.py
│   ├── test_optimal.py
│   ├── test_metrics.py
│   ├── test_validator.py
│   ├── test_utils.py
│   └── test_datasets.py
│
└── docs/                      # Documentation
    ├── architecture.md        #   System architecture
    ├── project_report.md      #   Academic project report
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

| Phase | Focus                              | Status         |
|-------|------------------------------------|----------------|
| 1     | System Design & Project Foundation | ✅ Complete     |
| 2     | Core Implementation & Integration  | ✅ Complete     |
| 3     | Extended Analysis & Viva Submission| 🔲 Planned     |

---

## Algorithms Overview

| Algorithm | Strategy                        | Type        |
|-----------|---------------------------------|-------------|
| FIFO      | Replace the oldest page         | Practical   |
| LRU       | Replace the least recently used | Practical   |
| Optimal   | Replace the farthest future use | Theoretical |

For detailed algorithm specifications, see [docs/architecture.md](docs/architecture.md).

---

## License

This project is developed as a B.Tech Operating Systems capstone project for academic purposes.

---

## Author

B.Tech CSE Student — Operating Systems Capstone Project
