# Memora — Project Report

**Project Title:** Memora: A Virtual Memory Simulator for Page Replacement Algorithm Analysis

**Course:** Operating Systems

**Degree:** B.Tech, Computer Science and Engineering

**Date:** November 2026

---

## Abstract

Memora is a command-line-based educational tool designed to simulate and compare page replacement algorithms used in virtual memory management. The simulator implements three algorithms — FIFO (First In, First Out), LRU (Least Recently Used), and Optimal (Bélády's Algorithm) — and provides step-by-step execution traces, performance metrics, and visual comparisons. The tool is built in Python with Bash integration for Windows (Git Bash) and aims to help students understand the trade-offs between different page replacement strategies through interactive simulation and analysis.

---

## 1. Introduction

### 1.1 Background

Virtual memory is a fundamental concept in modern operating systems that allows processes to use more memory than is physically available. The operating system manages a mapping between virtual pages and physical memory frames. When a process accesses a page not currently in physical memory, a **page fault** occurs, and the OS must load the page from secondary storage.

When all physical frames are occupied, the OS must decide which existing page to **replace**. This decision is governed by a **page replacement algorithm**. The choice of algorithm directly affects system performance — a poor algorithm leads to excessive page faults (thrashing), while a good algorithm minimizes unnecessary I/O.

### 1.2 Motivation

Understanding page replacement algorithms is a core learning objective in Operating Systems courses. Students typically study FIFO, LRU, and Optimal algorithms by manually tracing them on paper with small reference strings. This manual process is:

- **Time-consuming** for longer sequences.
- **Error-prone** when tracking frame states across many steps.
- **Difficult to compare** across algorithms without automation.

A simulator like Memora bridges this gap by automating the trace, computing metrics, and presenting visual comparisons — allowing students to focus on understanding *why* algorithms behave differently rather than *how* to track frame states.

---

## 2. Problem Statement

Design and implement a command-line tool that:

1. Accepts a page reference string and a number of memory frames.
2. Simulates FIFO, LRU, and Optimal page replacement algorithms.
3. Tracks memory state changes at each step.
4. Calculates performance metrics (hits, faults, hit ratio, fault ratio).
5. Compares algorithm performance on identical inputs.
6. Generates charts and reports for analysis.

---

## 3. Objectives

1. Implement correct simulations of FIFO, LRU, and Optimal page replacement.
2. Provide clear, step-by-step simulation history for educational purposes.
3. Calculate and display performance metrics for each algorithm.
4. Enable side-by-side comparison of all three algorithms.
5. Generate visual charts using Matplotlib.
6. Export results in CSV format for further analysis.
7. Provide a Bash-based launcher compatible with Git Bash on Windows.
8. Maintain modular, well-documented code suitable for academic review.

---

## 4. Scope

### In Scope

- Simulation of FIFO, LRU, and Optimal page replacement algorithms.
- Page-by-page memory frame state tracking.
- Performance metrics: hits, faults, hit ratio, fault ratio.
- Algorithm comparison on identical input.
- Bar chart visualization of results.
- CSV export of results.
- JSON-based sample datasets.
- Bash scripts for Git Bash on Windows.
- Input validation with clear error messages.
- Application logging.

### Out of Scope

- Real operating system memory management or kernel-level simulation.
- Demand paging, TLB simulation, or multi-level page tables.
- Clock, Second-Chance, LFU, or MFU algorithms (beyond the three specified).
- GUI or web-based interface.
- Database integration.
- Network communication.
- Multi-user or authentication features.

---

## 5. Proposed Methodology

### 5.1 Development Approach

The project follows a **three-phase incremental development** approach:

| Phase | Focus                              | Deliverables                        |
|-------|------------------------------------|-------------------------------------|
| 1     | System Design & Foundation         | Architecture, structure, docs       |
| 2     | Core Implementation & Integration  | Algorithms, CLI, charts, reports    |
| 3     | Testing, Analysis & Submission     | Tests, analysis, final report       |

### 5.2 Architecture

The system uses a **layered modular architecture**:

- **Algorithm Layer:** Pure algorithm implementations with no side effects.
- **Core Layer:** Simulation orchestration, metrics, and validation.
- **Analysis Layer:** Comparison and visualization.
- **Utility Layer:** File I/O and logging.
- **Interface Layer:** CLI and Bash scripts.

For detailed architecture, see [architecture.md](architecture.md).

### 5.3 Technology Stack

- **Python 3.8+** for simulation logic.
- **Matplotlib** for chart generation.
- **JSON** for input datasets.
- **CSV** for output reports.
- **Bash** (Git Bash) for execution scripts.
- **unittest/pytest** for testing.

---

## 6. System Design

### 6.1 Input Format

Users provide:
- A **page reference string**: a sequence of non-negative integers representing page accesses.
- A **frame count**: a positive integer representing available physical memory frames.

### 6.2 Output Format

For each algorithm, the system produces:
- Step-by-step frame state history.
- Total hits and faults.
- Hit ratio and fault ratio.

For comparisons, the system produces:
- Tabulated results across all three algorithms.
- Bar charts (PNG) saved to disk.
- CSV report saved to disk.

### 6.3 Algorithm Interface Contract

All algorithms share an identical function signature and return structure, enabling uniform comparison. See [architecture.md](architecture.md) Section 4 for the complete specification.

---

## 7. Expected Outcomes

Upon completion, Memora will:

1. Correctly simulate FIFO, LRU, and Optimal page replacement.
2. Demonstrate that Optimal always produces the fewest (or tied fewest) page faults.
3. Show how FIFO and LRU differ in their replacement decisions.
4. Provide educational value through step-by-step traces.
5. Generate publication-quality comparison charts.
6. Serve as a practical tool for Operating Systems lab demonstrations.

---

## 8. Future Work

Potential extensions beyond the current scope:

- **Additional algorithms:** Clock, Second-Chance, LFU, MFU.
- **Variable frame count analysis:** Run the same sequence across different frame counts to visualize Bélády's anomaly (FIFO can have more faults with more frames).
- **Interactive web interface:** A browser-based frontend for wider accessibility.
- **Real workload traces:** Use page reference patterns from real applications.
- **Performance benchmarking:** Measure algorithm execution time for large inputs.

---

## 9. Results and Analysis

*To be completed after Phase 2 implementation and Phase 3 testing.*

---

## 10. Conclusion

*To be completed after project finalization.*

---

## References

1. Silberschatz, A., Galvin, P. B., & Gagne, G. — *Operating System Concepts* (10th Edition).
2. Tanenbaum, A. S., & Bos, H. — *Modern Operating Systems* (4th Edition).
3. Stallings, W. — *Operating Systems: Internals and Design Principles* (9th Edition).
4. Bélády, L. A. (1966). "A Study of Replacement Algorithms for Virtual Storage Computers." *IBM Systems Journal*, 5(2), 78–101.
