# Memora — Academic Capstone Project Report

**Project Title:** Memora: An Integrated Operating Systems Resource-Management Simulator  
**Course:** Operating Systems (CSE316 / CS301)  
**Degree:** Bachelor of Technology in Computer Science and Engineering  
**Date:** November 2026  

---

## Abstract

Operating systems manage hardware resources through three critical functions: virtual memory management, CPU scheduling, and deadlock avoidance. **Memora** is an integrated educational and analytical resource-management simulator developed in Python and Bash, featuring a Flask REST API backend and an interactive multi-module web dashboard.

Memora provides complete implementations of:
1. **Virtual Memory Management:** Simulates FIFO, LRU, and Bélády's Optimal page replacement algorithms, displaying hardware memory frame racks, step-by-step playback, and verifying Bélády's Anomaly.
2. **CPU Scheduling:** Simulates FCFS, Non-Preemptive SJF, and Round Robin scheduling algorithms, generating interactive Gantt charts, computing turnaround, waiting, and response times, and evaluating CPU utilization and throughput.
3. **Deadlock Management:** Implements the Banker's Algorithm for deadlock avoidance, computing the Need matrix, discovering safe execution sequences, generating step-by-step allocation audit trails, and simulating dynamic resource requests.

The system is validated by an automated test suite of **96 unit and integration tests** (100% pass rate), adhering to standard Operating Systems textbooks (Silberschatz, Galvin & Gagne).

---

## 1. Introduction & Background

### 1.1 The Operating System Resource Challenge
An operating system acts as an intermediary between user applications and system hardware. Its three primary resource-management duties include:
- **Primary Memory (RAM):** Managing limited physical frames among multiple competing processes using demand paging and page replacement.
- **Processing Units (CPU):** Allocating CPU execution time slices to processes in the ready queue to minimize latency and maximize throughput.
- **Non-Preemptible Resources:** Ensuring that sequential allocations of shared devices and data structures avoid circular wait conditions that trigger deadlocks.

### 1.2 Motivation
Manual paper-and-pencil tracing of these algorithms in undergraduate curricula is tedious, error-prone, and obscures higher-level architectural insights. Memora provides automated, reproducible simulation and comparative visualization across all three domains in a single cohesive tool.

---

## 2. Problem Statement & Objectives

### 2.1 Objectives
1. **Core Resource-Management Modules:** Implement accurate simulations for:
   - Memory Management: FIFO, LRU, Optimal.
   - CPU Scheduling: FCFS, Non-Preemptive SJF, Round Robin (configurable time quantum $q$).
   - Deadlock Avoidance: Banker's Algorithm (safety check and resource-request algorithm).
2. **Comparative Analysis:** Provide side-by-side performance benchmarks (hit ratio, AWT, ATAT, CPU utilization, throughput).
3. **Interactive & Visual Interfaces:** Build both an interactive multi-module web dashboard (HTML5, CSS3, JavaScript, Canvas) and an interactive command-line interface (CLI).
4. **Defensive Validation & Testing:** Ensure 100% deterministic reproducibility with strict validation and automated unit testing.

---

## 3. System Architecture & Methodology

### 3.1 Layered Architectural Structure
Memora is built around a layered modular architecture:
- **Presentation Layer:** Multi-tab responsive web interface (`templates/index.html`, `static/css/style.css`, `static/js/`) and interactive terminal CLI (`main.py`).
- **Service/API Layer:** Flask REST API (`src/api/routes.py`) providing standardized JSON endpoints.
- **Engine Layer:** Independent subsystems for Memory (`src/core/`), CPU (`src/cpu/`), and Deadlock (`src/deadlock/`).
- **Utility Layer:** File handlers for datasets, CSV reports, and Matplotlib headless figure generation (`src/analysis/visualization.py`).

---

## 4. Subsystem Details & Theoretical Foundations

### 4.1 Virtual Memory Management
- **FIFO:** Replaces the page loaded earliest into memory. Susceptible to **Bélády's Anomaly** (where allocating more physical frames increases page faults).
- **LRU:** Replaces the page not accessed for the longest time in the past. Strictly satisfies the inclusion property ($S_m(t) \subseteq S_{m+1}(t)$), guaranteeing immunity to Bélády's Anomaly.
- **Optimal (Bélády's Algorithm):** Evicts the resident page whose next reference occurs farthest in the future or never. Serves as an unachievable theoretical benchmark.

### 4.2 CPU Scheduling
- **FCFS:** Non-preemptive execution based strictly on arrival order. Vulnerable to the Convoy Effect.
- **SJF (Non-Preemptive):** Schedules the ready process with the shortest burst time. Mathematically minimizes Average Waiting Time ($AWT$).
- **Round Robin:** Preemptive execution giving each process a fixed quantum $q$. Newly arriving processes at time $t$ are queued *before* the preempted process running during that slice.

### 4.3 Deadlock Management (Banker's Algorithm)
- **Need Matrix:** $Need[i][j] = Max[i][j] - Allocation[i][j]$.
- **Safety Algorithm:** Iteratively identifies a process whose remaining need can be satisfied by current Available resources ($Need[i] \le Work$), releases its allocation upon simulated completion, and verifies that all processes can finish.
- **Resource-Request Algorithm:** Tests whether a requested vector can be granted immediately without transitioning the system into an unsafe state.

---

## 5. Experimental Results & Verification

### 5.1 Virtual Memory Benchmark (Silberschatz Reference Sequence)
Reference sequence: `[7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]` ($N=20$), 3 frames:
- **FIFO:** 15 faults, 5 hits, 25.00% hit ratio.
- **LRU:** 12 faults, 8 hits, 40.00% hit ratio.
- **Optimal:** 9 faults, 11 hits, 55.00% hit ratio (Winner).

### 5.2 CPU Scheduling Benchmark (4-Process Staggered Workload)
Workload: $P_1(0, 5), P_2(1, 3), P_3(2, 8), P_4(3, 6)$, $q = 2$:
- **FCFS:** $AWT = 5.75\text{ ms}$, $ATAT = 11.25\text{ ms}$, $ART = 5.75\text{ ms}$, $U = 100\%$.
- **SJF:** $AWT = 5.25\text{ ms}$, $ATAT = 10.75\text{ ms}$, $ART = 5.25\text{ ms}$, $U = 100\%$ (Lowest AWT).
- **Round Robin ($q=2$):** $AWT = 9.75\text{ ms}$, $ATAT = 15.25\text{ ms}$, $ART = 2.00\text{ ms}$, $U = 100\%$ (Optimal Responsiveness).

### 5.3 Deadlock Safety Benchmark (5 Processes, 3 Resource Types)
- **Available:** $[3, 3, 2]$
- **System State:** Verified **SAFE STATE**.
- **Discovered Safe Sequence:** $P_1 \rightarrow P_3 \rightarrow P_0 \rightarrow P_2 \rightarrow P_4$.
- **Dynamic Request Test:** $P_1$ requests $[1, 0, 2] \rightarrow$ Granted (system remains safe). $P_0$ requests $[0, 2, 0] \rightarrow$ Denied (leaves system in unsafe state).

---

## 6. Software Quality & Testing

The project includes an automated test suite executed with Python's standard `unittest` framework:
- **96 Total Tests** executed across 11 test modules.
- **100% Pass Rate** in under 1 second.
- **Key Test Areas:**
  - Algorithm invariants (e.g. $Hit\ Ratio + Fault\ Ratio = 100\%$).
  - Mathematical correctness of $CT, TAT, WT, RT$.
  - Tie-breaking rules for SJF and Optimal.
  - Banker's safe sequence discovery and request rejection.
  - Defensive type rejection (booleans, floats, strings, negative values).
  - Flask REST API routes, status codes, and error formatting.

---

## 7. Conclusion

Memora successfully fulfills all five phases of the Operating Systems Capstone rubric:
1. **System Design & Planning:** Clear modular architecture with comprehensive technical documentation.
2. **Core Resource-Management Modules:** Accurate, verified implementations of Virtual Memory, CPU Scheduling, and Deadlock Management.
3. **Analysis & Comparison:** Side-by-side tables, metrics, interactive Gantt charts, and Canvas visualizers.
4. **Testing & Reliability:** 96 passing unit tests and defensive validation.
5. **Documentation & Demonstration:** Interactive web dashboard, CLI menu with `--demo-all` viva flags, and automated Bash scripts.

Memora provides students and evaluators with a trustworthy, evidence-based simulation platform for Operating Systems concepts.
