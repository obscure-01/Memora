"""
Unit tests for CPU Scheduling Module.

Tests:
    1. FCFS (First Come First Serve) scheduling mechanics and invariants
    2. SJF (Shortest Job First - Non-Preemptive) scheduling and tie-breaking
    3. Round Robin (RR) time quantum preemption and ready-queue ordering
    4. Staggered arrivals and CPU idle gap handling
    5. Simultaneous process arrivals
    6. Process input validation and boundary cases
    7. Multi-algorithm comparative analysis
    8. REST API endpoints (/api/cpu/schedule and /api/cpu/compare)
"""

import unittest
from src.cpu.fcfs import run_fcfs
from src.cpu.sjf import run_sjf
from src.cpu.round_robin import run_round_robin
from src.cpu.scheduler import run_cpu_scheduler, compare_cpu_schedulers
from src.cpu.validator import validate_processes, validate_time_quantum
from src.api.app import create_app


class TestCPUScheduling(unittest.TestCase):
    """Test suite for CPU scheduling algorithms and API integration."""

    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

        # Standard reference process set
        self.ref_processes = [
            {"id": "P1", "arrival_time": 0, "burst_time": 5},
            {"id": "P2", "arrival_time": 1, "burst_time": 3},
            {"id": "P3", "arrival_time": 2, "burst_time": 8},
            {"id": "P4", "arrival_time": 3, "burst_time": 6},
        ]

    # =========================================================================
    # 1. FCFS Tests
    # =========================================================================

    def test_fcfs_execution_order_and_metrics(self):
        """FCFS executes in order of arrival and produces mathematically verified metrics."""
        result = run_fcfs(self.ref_processes)
        self.assertEqual(result["algorithm"], "FCFS")

        proc_map = {p["id"]: p for p in result["metrics"]["processes"]}
        # P1: start 0, run 5 -> CT=5, TAT=5-0=5, WT=5-5=0, RT=0-0=0
        self.assertEqual(proc_map["P1"]["completion_time"], 5)
        self.assertEqual(proc_map["P1"]["turnaround_time"], 5)
        self.assertEqual(proc_map["P1"]["waiting_time"], 0)
        self.assertEqual(proc_map["P1"]["response_time"], 0)

        # P2: arrives 1, waits until 5, runs 3 -> CT=8, TAT=8-1=7, WT=7-3=4, RT=5-1=4
        self.assertEqual(proc_map["P2"]["completion_time"], 8)
        self.assertEqual(proc_map["P2"]["turnaround_time"], 7)
        self.assertEqual(proc_map["P2"]["waiting_time"], 4)
        self.assertEqual(proc_map["P2"]["response_time"], 4)

        # P3: arrives 2, waits until 8, runs 8 -> CT=16, TAT=16-2=14, WT=14-8=6, RT=8-2=6
        self.assertEqual(proc_map["P3"]["completion_time"], 16)
        self.assertEqual(proc_map["P3"]["turnaround_time"], 14)
        self.assertEqual(proc_map["P3"]["waiting_time"], 6)

        # P4: arrives 3, waits until 16, runs 6 -> CT=22, TAT=22-3=19, WT=19-6=13, RT=16-3=13
        self.assertEqual(proc_map["P4"]["completion_time"], 22)
        self.assertEqual(proc_map["P4"]["turnaround_time"], 19)
        self.assertEqual(proc_map["P4"]["waiting_time"], 13)

        # Invariants: Total time = 22, Busy time = 22, Idle time = 0, Utilization = 100%
        m = result["metrics"]
        self.assertEqual(m["total_time"], 22)
        self.assertEqual(m["busy_time"], 22)
        self.assertEqual(m["idle_time"], 0)
        self.assertEqual(m["cpu_utilization"], 100.0)
        # Average Turnaround: (5 + 7 + 14 + 19) / 4 = 45 / 4 = 11.25
        self.assertAlmostEqual(m["avg_turnaround_time"], 11.25, places=2)
        # Average Waiting: (0 + 4 + 6 + 13) / 4 = 23 / 4 = 5.75
        self.assertAlmostEqual(m["avg_waiting_time"], 5.75, places=2)

    def test_fcfs_with_cpu_idle_gap(self):
        """FCFS correctly inserts IDLE segments when no process is ready."""
        procs = [
            {"id": "P1", "arrival_time": 0, "burst_time": 3},
            {"id": "P2", "arrival_time": 6, "burst_time": 4},
        ]
        result = run_fcfs(procs)
        gantt = result["gantt_chart"]

        # Expected Gantt: [P1: 0-3], [IDLE: 3-6], [P2: 6-10]
        self.assertEqual(len(gantt), 3)
        self.assertEqual(gantt[0]["process"], "P1")
        self.assertEqual(gantt[0]["start"], 0)
        self.assertEqual(gantt[0]["end"], 3)

        self.assertEqual(gantt[1]["process"], "IDLE")
        self.assertEqual(gantt[1]["start"], 3)
        self.assertEqual(gantt[1]["end"], 6)

        self.assertEqual(gantt[2]["process"], "P2")
        self.assertEqual(gantt[2]["start"], 6)
        self.assertEqual(gantt[2]["end"], 10)

        self.assertEqual(result["metrics"]["idle_time"], 3)
        self.assertEqual(result["metrics"]["busy_time"], 7)
        self.assertEqual(result["metrics"]["total_time"], 10)
        self.assertAlmostEqual(result["metrics"]["cpu_utilization"], 70.0, places=1)

    # =========================================================================
    # 2. SJF Tests
    # =========================================================================

    def test_sjf_non_preemptive_scheduling(self):
        """Non-preemptive SJF schedules shortest ready job upon completion."""
        # P1 arrives at 0 (runs 0..5). At t=5, P2(bt=3), P3(bt=8), P4(bt=6) are ready.
        # Shortest is P2 (bt=3) -> runs 5..8.
        # At t=8, P4(bt=6) < P3(bt=8) -> P4 runs 8..14.
        # Finally P3(bt=8) runs 14..22.
        result = run_sjf(self.ref_processes)
        self.assertEqual(result["algorithm"], "SJF")

        gantt_order = [seg["process"] for seg in result["gantt_chart"]]
        self.assertEqual(gantt_order, ["P1", "P2", "P4", "P3"])

        proc_map = {p["id"]: p for p in result["metrics"]["processes"]}
        self.assertEqual(proc_map["P1"]["completion_time"], 5)
        self.assertEqual(proc_map["P2"]["completion_time"], 8)
        self.assertEqual(proc_map["P4"]["completion_time"], 14)
        self.assertEqual(proc_map["P3"]["completion_time"], 22)

        # SJF achieves lower average waiting time than FCFS
        # P1 WT=0, P2 WT=5-1=4, P4 WT=8-3=5, P3 WT=14-2=12 -> Total WT = 21 / 4 = 5.25
        self.assertAlmostEqual(result["metrics"]["avg_waiting_time"], 5.25, places=2)

    def test_sjf_deterministic_tie_breaking(self):
        """SJF breaks burst time ties using arrival time, then process ID."""
        procs = [
            {"id": "P1", "arrival_time": 0, "burst_time": 4},
            {"id": "P2", "arrival_time": 0, "burst_time": 4},
        ]
        result = run_sjf(procs)
        gantt_order = [seg["process"] for seg in result["gantt_chart"]]
        self.assertEqual(gantt_order, ["P1", "P2"])

    # =========================================================================
    # 3. Round Robin Tests
    # =========================================================================

    def test_round_robin_preemption_and_ready_queue(self):
        """Round Robin preempts at time quantum and cycles through ready queue."""
        procs = [
            {"id": "P1", "arrival_time": 0, "burst_time": 5},
            {"id": "P2", "arrival_time": 0, "burst_time": 3},
            {"id": "P3", "arrival_time": 0, "burst_time": 1},
        ]
        # Quantum = 2
        # t=0: Queue: [P1, P2, P3]. P1 runs 0..2 (rem=3). Queue: [P2, P3, P1]
        # t=2: P2 runs 2..4 (rem=1). Queue: [P3, P1, P2]
        # t=4: P3 runs 4..5 (rem=0, completes CT=5). Queue: [P1, P2]
        # t=5: P1 runs 5..7 (rem=1). Queue: [P2, P1]
        # t=7: P2 runs 7..8 (rem=0, completes CT=8). Queue: [P1]
        # t=8: P1 runs 8..9 (rem=0, completes CT=9).
        result = run_round_robin(procs, time_quantum=2)
        self.assertEqual(result["algorithm"], "RR")

        gantt_order = [seg["process"] for seg in result["gantt_chart"]]
        self.assertEqual(gantt_order, ["P1", "P2", "P3", "P1", "P2", "P1"])

        proc_map = {p["id"]: p for p in result["metrics"]["processes"]}
        self.assertEqual(proc_map["P3"]["completion_time"], 5)
        self.assertEqual(proc_map["P2"]["completion_time"], 8)
        self.assertEqual(proc_map["P1"]["completion_time"], 9)

        # Verify Response Times: P1 starts at 0, P2 starts at 2, P3 starts at 4
        self.assertEqual(proc_map["P1"]["response_time"], 0)
        self.assertEqual(proc_map["P2"]["response_time"], 2)
        self.assertEqual(proc_map["P3"]["response_time"], 4)

    # =========================================================================
    # 4. Input Validation & Boundaries
    # =========================================================================

    def test_validate_processes_success_and_errors(self):
        """Input validator handles valid and invalid process definitions."""
        valid, _ = validate_processes(self.ref_processes)
        self.assertTrue(valid)

        # Empty
        v, err = validate_processes([])
        self.assertFalse(v)
        self.assertIn("empty", err.lower())

        # Negative arrival time
        v, err = validate_processes([{"id": "P1", "arrival_time": -1, "burst_time": 5}])
        self.assertFalse(v)
        self.assertIn("non-negative", err.lower())

        # Zero burst time
        v, err = validate_processes([{"id": "P1", "arrival_time": 0, "burst_time": 0}])
        self.assertFalse(v)
        self.assertIn("positive", err.lower())

        # Duplicate ID
        v, err = validate_processes([
            {"id": "P1", "arrival_time": 0, "burst_time": 5},
            {"id": "P1", "arrival_time": 1, "burst_time": 3},
        ])
        self.assertFalse(v)
        self.assertIn("duplicate", err.lower())

        # Boolean rejected
        v, err = validate_processes([{"id": "P1", "arrival_time": True, "burst_time": 5}])
        self.assertFalse(v)
        self.assertIn("boolean", err.lower())

    def test_validate_time_quantum(self):
        """Time quantum validation enforces positive integer."""
        v, _ = validate_time_quantum(2)
        self.assertTrue(v)

        v, _ = validate_time_quantum(0)
        self.assertFalse(v)

        v, _ = validate_time_quantum(-2)
        self.assertFalse(v)

        v, _ = validate_time_quantum(True)
        self.assertFalse(v)

    # =========================================================================
    # 5. Multi-Algorithm Comparison & API
    # =========================================================================

    def test_compare_cpu_schedulers(self):
        """Comparison engine returns side-by-side metrics across all algorithms."""
        comp = compare_cpu_schedulers(self.ref_processes, time_quantum=2)
        self.assertIn("FCFS", comp["results"])
        self.assertIn("SJF", comp["results"])
        self.assertIn("RR", comp["results"])
        self.assertEqual(len(comp["comparison_table"]), 3)
        self.assertIn("summary", comp)

    def test_api_cpu_schedule_endpoint(self):
        """POST /api/cpu/schedule returns 200 with Gantt chart and metrics."""
        payload = {
            "algorithm": "FCFS",
            "processes": self.ref_processes,
        }
        res = self.client.post("/api/cpu/schedule", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["algorithm"], "FCFS")
        self.assertIn("gantt_chart", data)
        self.assertIn("metrics", data)

    def test_api_cpu_compare_endpoint(self):
        """POST /api/cpu/compare returns 200 with comparative tables."""
        payload = {
            "processes": self.ref_processes,
            "time_quantum": 3,
        }
        res = self.client.post("/api/cpu/compare", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("results", data)
        self.assertIn("comparison_table", data)
        self.assertIn("summary", data)


if __name__ == "__main__":
    unittest.main()
