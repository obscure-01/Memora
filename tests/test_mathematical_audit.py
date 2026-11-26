"""
Independent Mathematical Correctness and Invariant Verification Test Suite.

Contains independent, hand-calculated reference test cases for:
    1. Virtual Memory Management (FIFO, LRU, Optimal, Bélády's Anomaly, Invariants)
    2. CPU Scheduling (FCFS, SJF, Round Robin, Idle Gaps, Gantt Timelines, Invariants)
    3. Deadlock Management (Banker's Algorithm, Safety, Need Matrix, Request Simulation, State Immutability)
"""

import unittest
from src.algorithms.fifo import run_fifo
from src.algorithms.lru import run_lru
from src.algorithms.optimal import run_optimal
from src.cpu.fcfs import run_fcfs
from src.cpu.sjf import run_sjf
from src.cpu.round_robin import run_round_robin
from src.cpu.scheduler import compare_cpu_schedulers
from src.deadlock.bankers import (
    compute_need_matrix,
    check_safety,
    simulate_resource_request,
)


class TestMemoryMathematicalCorrectness(unittest.TestCase):
    """Independent mathematical verification for page replacement algorithms."""

    def test_case_1_repeated_page(self):
        """Case 1: Repeated page [1, 1, 1, 1, 1] with 3 frames yields 1 fault, 4 hits."""
        seq = [1, 1, 1, 1, 1]
        frames = 3

        for algo_func in [run_fifo, run_lru, run_optimal]:
            res = algo_func(seq, frames)
            self.assertEqual(res["faults"], 1)
            self.assertEqual(res["hits"], 4)
            self.assertEqual(res["hits"] + res["faults"], len(seq))
            self.assertAlmostEqual(res["hit_ratio"] + res["fault_ratio"], 1.0, places=4)
            # Final frames should contain 1 and None for remaining slots
            final_frames = res["history"][-1]["frames"]
            self.assertEqual(final_frames, [1, None, None])

    def test_case_2_frames_greater_than_references(self):
        """Case 2: References [1, 2, 3] with 5 frames yields 3 faults, 0 hits and no phantom frames."""
        seq = [1, 2, 3]
        frames = 5

        for algo_func in [run_fifo, run_lru, run_optimal]:
            res = algo_func(seq, frames)
            self.assertEqual(res["faults"], 3)
            self.assertEqual(res["hits"], 0)
            self.assertEqual(res["hits"] + res["faults"], len(seq))
            final_frames = res["history"][-1]["frames"]
            self.assertEqual(final_frames, [1, 2, 3, None, None])
            self.assertEqual(len(final_frames), 5)

    def test_case_3_standard_comparison(self):
        """Case 3: Textbook 20-access sequence with 3 frames produces known theoretical outcomes."""
        seq = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
        frames = 3

        fifo_res = run_fifo(seq, frames)
        self.assertEqual(fifo_res["faults"], 15)
        self.assertEqual(fifo_res["hits"], 5)
        self.assertAlmostEqual(fifo_res["hit_ratio"], 0.25, places=4)
        self.assertAlmostEqual(fifo_res["fault_ratio"], 0.75, places=4)

        lru_res = run_lru(seq, frames)
        self.assertEqual(lru_res["faults"], 12)
        self.assertEqual(lru_res["hits"], 8)
        self.assertAlmostEqual(lru_res["hit_ratio"], 0.40, places=4)
        self.assertAlmostEqual(lru_res["fault_ratio"], 0.60, places=4)

        opt_res = run_optimal(seq, frames)
        self.assertEqual(opt_res["faults"], 9)
        self.assertEqual(opt_res["hits"], 11)
        self.assertAlmostEqual(opt_res["hit_ratio"], 0.55, places=4)
        self.assertAlmostEqual(opt_res["fault_ratio"], 0.45, places=4)

        # Invariant check across all algorithms
        for res in [fifo_res, lru_res, opt_res]:
            self.assertEqual(res["hits"] + res["faults"], len(seq))
            self.assertAlmostEqual(res["hit_ratio"] + res["fault_ratio"], 1.0, places=4)

    def test_case_4_beladys_anomaly(self):
        """Case 4: Bélády's Anomaly sequence [1,2,3,4,1,2,5,1,2,3,4,5] on 3 vs 4 frames."""
        seq = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]

        # 3 Frames
        fifo_3 = run_fifo(seq, 3)
        lru_3 = run_lru(seq, 3)
        opt_3 = run_optimal(seq, 3)

        self.assertEqual(fifo_3["faults"], 9)
        self.assertEqual(lru_3["faults"], 10)
        self.assertEqual(opt_3["faults"], 7)

        # 4 Frames
        fifo_4 = run_fifo(seq, 4)
        lru_4 = run_lru(seq, 4)
        opt_4 = run_optimal(seq, 4)

        # Anomaly verification: FIFO faults increase from 9 to 10!
        self.assertEqual(fifo_4["faults"], 10)
        self.assertGreater(fifo_4["faults"], fifo_3["faults"])

        # Stack algorithm verification: LRU and Optimal faults decrease!
        self.assertEqual(lru_4["faults"], 8)
        self.assertLess(lru_4["faults"], lru_3["faults"])

        self.assertEqual(opt_4["faults"], 6)
        self.assertLess(opt_4["faults"], opt_3["faults"])


class TestCPUMathematicalCorrectness(unittest.TestCase):
    """Independent mathematical verification for CPU scheduling algorithms."""

    def test_simultaneous_arrival_at_time_zero(self):
        """Test FCFS, SJF, and Round Robin when all processes arrive at time 0."""
        # P1(BT=4), P2(BT=3), P3(BT=1), P4(BT=2)
        procs = [
            {"id": "P1", "arrival_time": 0, "burst_time": 4},
            {"id": "P2", "arrival_time": 0, "burst_time": 3},
            {"id": "P3", "arrival_time": 0, "burst_time": 1},
            {"id": "P4", "arrival_time": 0, "burst_time": 2},
        ]

        # FCFS: P1(0..4), P2(4..7), P3(7..8), P4(8..10)
        # CT: P1=4, P2=7, P3=8, P4=10
        # WT: P1=0, P2=4, P3=7, P4=8 -> Sum=19, AWT=4.75
        # TAT: P1=4, P2=7, P3=8, P4=10 -> Sum=29, ATAT=7.25
        fcfs = run_fcfs(procs)
        self.assertEqual(fcfs["metrics"]["total_time"], 10)
        self.assertEqual(fcfs["metrics"]["busy_time"], 10)
        self.assertEqual(fcfs["metrics"]["idle_time"], 0)
        self.assertAlmostEqual(fcfs["metrics"]["avg_waiting_time"], 4.75, places=2)
        self.assertAlmostEqual(fcfs["metrics"]["avg_turnaround_time"], 7.25, places=2)

        # SJF: Shortest first -> P3(BT=1, 0..1), P4(BT=2, 1..3), P2(BT=3, 3..6), P1(BT=4, 6..10)
        # CT: P3=1, P4=3, P2=6, P1=10
        # WT: P3=0, P4=1, P2=3, P1=6 -> Sum=10, AWT=2.50
        # TAT: P3=1, P4=3, P2=6, P1=10 -> Sum=20, ATAT=5.00
        sjf = run_sjf(procs)
        self.assertAlmostEqual(sjf["metrics"]["avg_waiting_time"], 2.50, places=2)
        self.assertAlmostEqual(sjf["metrics"]["avg_turnaround_time"], 5.00, places=2)
        self.assertLess(sjf["metrics"]["avg_waiting_time"], fcfs["metrics"]["avg_waiting_time"])

        # Round Robin (q=2):
        # t=0: [P1, P2, P3, P4]
        # P1 runs 0..2 (rem=2) -> queue: [P2, P3, P4, P1]
        # P2 runs 2..4 (rem=1) -> queue: [P3, P4, P1, P2]
        # P3 runs 4..5 (finishes, CT=5) -> queue: [P4, P1, P2]
        # P4 runs 5..7 (finishes, CT=7) -> queue: [P1, P2]
        # P1 runs 7..9 (finishes, CT=9) -> queue: [P2]
        # P2 runs 9..10 (finishes, CT=10)
        rr = run_round_robin(procs, time_quantum=2)
        proc_map = {p["id"]: p for p in rr["metrics"]["processes"]}
        self.assertEqual(proc_map["P3"]["completion_time"], 5)
        self.assertEqual(proc_map["P4"]["completion_time"], 7)
        self.assertEqual(proc_map["P1"]["completion_time"], 9)
        self.assertEqual(proc_map["P2"]["completion_time"], 10)

        # Response times: P1=0, P2=2, P3=4, P4=5 -> Sum=11, ART=11/4=2.75
        self.assertEqual(proc_map["P1"]["response_time"], 0)
        self.assertEqual(proc_map["P2"]["response_time"], 2)
        self.assertEqual(proc_map["P3"]["response_time"], 4)
        self.assertEqual(proc_map["P4"]["response_time"], 5)
        self.assertAlmostEqual(rr["metrics"]["avg_response_time"], 2.75, places=2)

    def test_cpu_benchmark_simultaneous_arrival_bursts_5_3_8_6(self):
        """
        Regression Test: Benchmark workload with simultaneous arrival at t=0.
        P1(AT=0, BT=5), P2(AT=0, BT=3), P3(AT=0, BT=8), P4(AT=0, BT=6), quantum=2.

        Mathematical Invariants:
        1. FCFS:
           - Schedule order: P1, P2, P3, P4
           - Completion Times: P1=5, P2=8, P3=16, P4=22
           - Turnaround Times (CT - 0): P1=5, P2=8, P3=16, P4=22 (Sum=51, ATAT = 12.75)
           - Waiting Times (TAT - BT): P1=0, P2=5, P3=8, P4=16 (Sum=29, AWT = 7.25)
           - Response Times: P1=0, P2=5, P3=8, P4=16 (Sum=29, ART = 7.25)

        2. Non-preemptive SJF:
           - Shortest burst order: P2(3), P1(5), P4(6), P3(8)
           - Schedule order: P2, P1, P4, P3
           - Completion Times: P2=3, P1=8, P4=14, P3=22
           - Turnaround Times: P2=3, P1=8, P4=14, P3=22 (Sum=47, ATAT = 11.75)
           - Waiting Times: P2=0, P1=3, P4=8, P3=14 (Sum=25, AWT = 6.25)
           - Response Times: P2=0, P1=3, P4=8, P3=14 (Sum=25, ART = 6.25)

        3. Round Robin (quantum=2):
           - Hand Trace:
             [0, 2]:   P1 runs (rem 3) -> queue: [P2, P3, P4, P1]
             [2, 4]:   P2 runs (rem 1) -> queue: [P3, P4, P1, P2]
             [4, 6]:   P3 runs (rem 6) -> queue: [P4, P1, P2, P3]
             [6, 8]:   P4 runs (rem 4) -> queue: [P1, P2, P3, P4]
             [8, 10]:  P1 runs (rem 1; gets 2 units of burst, total executed = 4 of 5.
                       Cannot finish at 10 because remaining burst is 1. Appended to queue tail)
                       -> queue: [P2, P3, P4, P1]
             [10, 11]: P2 runs (rem 0 -> FINISHES at t=11) -> queue: [P3, P4, P1]
             [11, 13]: P3 runs (rem 4) -> queue: [P4, P1, P3]
             [13, 15]: P4 runs (rem 2) -> queue: [P1, P3, P4]
             [15, 16]: P1 runs (rem 0 -> FINISHES at t=16) -> queue: [P3, P4]
             [16, 18]: P3 runs (rem 2) -> queue: [P4, P3]
             [18, 20]: P4 runs (rem 0 -> FINISHES at t=20) -> queue: [P3]
             [20, 22]: P3 runs (rem 0 -> FINISHES at t=22)
           - Completion Times: P1=16, P2=11, P3=22, P4=20
           - Turnaround Times: P1=16, P2=11, P3=22, P4=20 (Sum=69, ATAT = 17.25)
           - Waiting Times: P1=11, P2=8, P3=14, P4=14 (Sum=47, AWT = 11.75)
           - Response Times: P1=0, P2=2, P3=4, P4=6 (Sum=12, ART = 3.00)
        """
        procs = [
            {"id": "P1", "arrival_time": 0, "burst_time": 5},
            {"id": "P2", "arrival_time": 0, "burst_time": 3},
            {"id": "P3", "arrival_time": 0, "burst_time": 8},
            {"id": "P4", "arrival_time": 0, "burst_time": 6},
        ]

        # 1. Verify FCFS
        fcfs = run_fcfs(procs)
        self.assertAlmostEqual(fcfs["metrics"]["avg_waiting_time"], 7.25, places=2)
        self.assertAlmostEqual(fcfs["metrics"]["avg_turnaround_time"], 12.75, places=2)
        self.assertAlmostEqual(fcfs["metrics"]["avg_response_time"], 7.25, places=2)
        fcfs_order = [s["process"] for s in fcfs["gantt_chart"]]
        self.assertEqual(fcfs_order, ["P1", "P2", "P3", "P4"])
        fcfs_p_map = {p["id"]: p for p in fcfs["metrics"]["processes"]}
        self.assertEqual(fcfs_p_map["P1"]["completion_time"], 5)
        self.assertEqual(fcfs_p_map["P2"]["completion_time"], 8)
        self.assertEqual(fcfs_p_map["P3"]["completion_time"], 16)
        self.assertEqual(fcfs_p_map["P4"]["completion_time"], 22)

        # 2. Verify SJF
        sjf = run_sjf(procs)
        self.assertAlmostEqual(sjf["metrics"]["avg_waiting_time"], 6.25, places=2)
        self.assertAlmostEqual(sjf["metrics"]["avg_turnaround_time"], 11.75, places=2)
        self.assertAlmostEqual(sjf["metrics"]["avg_response_time"], 6.25, places=2)
        sjf_order = [s["process"] for s in sjf["gantt_chart"]]
        self.assertEqual(sjf_order, ["P2", "P1", "P4", "P3"])
        sjf_p_map = {p["id"]: p for p in sjf["metrics"]["processes"]}
        self.assertEqual(sjf_p_map["P2"]["completion_time"], 3)
        self.assertEqual(sjf_p_map["P1"]["completion_time"], 8)
        self.assertEqual(sjf_p_map["P4"]["completion_time"], 14)
        self.assertEqual(sjf_p_map["P3"]["completion_time"], 22)

        # 3. Verify Round Robin (q=2)
        rr = run_round_robin(procs, time_quantum=2)
        rr_p_map = {p["id"]: p for p in rr["metrics"]["processes"]}
        self.assertEqual(rr_p_map["P1"]["completion_time"], 16)
        self.assertEqual(rr_p_map["P2"]["completion_time"], 11)
        self.assertEqual(rr_p_map["P4"]["completion_time"], 20)
        self.assertEqual(rr_p_map["P3"]["completion_time"], 22)

        self.assertAlmostEqual(rr["metrics"]["avg_response_time"], 3.00, places=2)
        self.assertAlmostEqual(rr["metrics"]["avg_waiting_time"], 11.75, places=2)
        self.assertAlmostEqual(rr["metrics"]["avg_turnaround_time"], 17.25, places=2)

        # Invariant checks across all algorithms
        for res in [fcfs, sjf, rr]:
            for p in res["metrics"]["processes"]:
                self.assertEqual(p["turnaround_time"], p["waiting_time"] + p["burst_time"])
            self.assertEqual(res["metrics"]["total_time"], 22)
            self.assertEqual(res["metrics"]["busy_time"], 22)
            self.assertEqual(res["metrics"]["idle_time"], 0)
            self.assertAlmostEqual(res["metrics"]["cpu_utilization"], 100.0, places=2)

        # 4. Verify Comparator
        comp = compare_cpu_schedulers(procs, time_quantum=2)
        self.assertEqual(comp["summary"]["best_waiting_time_algorithm"], "SJF")
        self.assertAlmostEqual(comp["summary"]["lowest_avg_waiting_time"], 6.25, places=2)
        self.assertEqual(comp["summary"]["best_turnaround_time_algorithm"], "SJF")
        self.assertAlmostEqual(comp["summary"]["lowest_avg_turnaround_time"], 11.75, places=2)

    def test_gantt_chart_and_invariants(self):
        """Verify Gantt chart segment durations match total busy time and no gaps exist."""
        procs = [
            {"id": "P1", "arrival_time": 0, "burst_time": 5},
            {"id": "P2", "arrival_time": 2, "burst_time": 3},
            {"id": "P3", "arrival_time": 8, "burst_time": 2},  # Idle between 5 and 8
        ]
        res = run_fcfs(procs)
        gantt = res["gantt_chart"]

        # Segments: [P1: 0..5], [P2: 5..8], [P3: 8..10]
        self.assertEqual(len(gantt), 3)
        self.assertEqual(gantt[0]["start"], 0)
        self.assertEqual(gantt[0]["end"], 5)
        self.assertEqual(gantt[1]["start"], 5)
        self.assertEqual(gantt[1]["end"], 8)
        self.assertEqual(gantt[2]["start"], 8)
        self.assertEqual(gantt[2]["end"], 10)

        # Invariant check: for every process, TAT = WT + BT
        for p in res["metrics"]["processes"]:
            self.assertEqual(p["turnaround_time"], p["waiting_time"] + p["burst_time"])

        # Segment durations sum to total simulation time
        total_duration = sum(seg["end"] - seg["start"] for seg in gantt)
        self.assertEqual(total_duration, res["metrics"]["total_time"])

    def test_round_robin_arrival_at_quantum_boundary(self):
        """Newly arrived process at quantum boundary t is enqueued BEFORE preempted process."""
        procs = [
            {"id": "P1", "arrival_time": 0, "burst_time": 4},
            {"id": "P2", "arrival_time": 2, "burst_time": 2},
        ]
        # Quantum = 2
        # At t=0: P1 runs 0..2.
        # At t=2: P2 arrives. P1 is preempted.
        # Silberschatz rule: P2 is enqueued before P1.
        # Ready queue: [P2, P1]
        # P2 runs 2..4 (finishes).
        # P1 runs 4..6 (finishes).
        rr = run_round_robin(procs, time_quantum=2)
        gantt_pids = [seg["process"] for seg in rr["gantt_chart"]]
        self.assertEqual(gantt_pids, ["P1", "P2", "P1"])
        self.assertEqual(rr["gantt_chart"][1]["start"], 2)
        self.assertEqual(rr["gantt_chart"][1]["end"], 4)
        self.assertEqual(rr["gantt_chart"][2]["start"], 4)
        self.assertEqual(rr["gantt_chart"][2]["end"], 6)


class TestDeadlockMathematicalCorrectness(unittest.TestCase):
    """Independent mathematical verification for Banker's Algorithm."""

    def setUp(self):
        self.classic_safe = {
            "available": [3, 3, 2],
            "allocation": [
                [0, 1, 0],
                [2, 0, 0],
                [3, 0, 2],
                [2, 1, 1],
                [0, 0, 2],
            ],
            "max": [
                [7, 5, 3],
                [3, 2, 2],
                [9, 0, 2],
                [2, 2, 2],
                [4, 3, 3],
            ],
            "process_names": ["P0", "P1", "P2", "P3", "P4"],
            "resource_names": ["A", "B", "C"],
        }

    def test_need_matrix_formula(self):
        """Need[i][j] = Max[i][j] - Allocation[i][j]."""
        need = compute_need_matrix(self.classic_safe["allocation"], self.classic_safe["max"])
        expected_need = [
            [7, 4, 3],  # P0
            [1, 2, 2],  # P1
            [6, 0, 0],  # P2
            [0, 1, 1],  # P3
            [4, 3, 1],  # P4
        ]
        self.assertEqual(need, expected_need)

    def test_safe_sequence_validity(self):
        """Verify discovered safe sequence includes all processes and maintains Work invariants."""
        res = check_safety(
            available=self.classic_safe["available"],
            allocation=self.classic_safe["allocation"],
            max_matrix=self.classic_safe["max"],
            process_names=self.classic_safe["process_names"],
            resource_names=self.classic_safe["resource_names"],
        )
        self.assertTrue(res["is_safe"])
        self.assertEqual(len(res["safe_sequence"]), 5)
        # Every process appears exactly once
        self.assertEqual(set(res["safe_sequence"]), {"P0", "P1", "P2", "P3", "P4"})

        # Independent trace invariant verification
        work = list(self.classic_safe["available"])
        alloc_map = {self.classic_safe["process_names"][i]: self.classic_safe["allocation"][i] for i in range(5)}
        need_map = {self.classic_safe["process_names"][i]: res["need"][i] for i in range(5)}

        for pid in res["safe_sequence"]:
            # Need must be <= Work
            self.assertTrue(all(need_map[pid][j] <= work[j] for j in range(3)))
            # Work increases by Allocation
            for j in range(3):
                work[j] += alloc_map[pid][j]

        # Final Work must equal sum of Available + all Allocations
        total_allocated = [sum(row[j] for row in self.classic_safe["allocation"]) for j in range(3)]
        expected_final_work = [self.classic_safe["available"][j] + total_allocated[j] for j in range(3)]
        self.assertEqual(work, expected_final_work)

    def test_single_resource_type_system(self):
        """Test Banker's Algorithm with a single resource type (m = 1)."""
        res = check_safety(
            available=[2],
            allocation=[[1], [2]],
            max_matrix=[[3], [4]],
            process_names=["P0", "P1"],
            resource_names=["R1"],
        )
        # P0 need: 2 <= 2 -> P0 finishes, returns 1, Work=3. P1 need: 2 <= 3 -> P1 finishes.
        self.assertTrue(res["is_safe"])
        self.assertEqual(res["safe_sequence"], ["P0", "P1"])

    def test_resource_request_does_not_mutate_state(self):
        """simulate_resource_request must be purely hypothetical and NOT mutate original inputs."""
        orig_avail = [3, 3, 2]
        orig_alloc = [
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2],
            [2, 1, 1],
            [0, 0, 2],
        ]
        orig_max = [
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2],
            [2, 2, 2],
            [4, 3, 3],
        ]

        avail_copy = list(orig_avail)
        alloc_copy = [list(r) for r in orig_alloc]

        req_res = simulate_resource_request(
            available=avail_copy,
            allocation=alloc_copy,
            max_matrix=orig_max,
            process_idx=1,
            request_vector=[1, 0, 2],
        )
        self.assertTrue(req_res["approved"])

        # Assert original vectors and matrices were NOT mutated
        self.assertEqual(avail_copy, orig_avail)
        self.assertEqual(alloc_copy, orig_alloc)


if __name__ == "__main__":
    unittest.main()
