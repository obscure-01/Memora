"""
Unit Tests for Memora Deadlock Management Module (Banker's Algorithm).

Tests safety algorithm, resource request algorithm, validation, and REST API endpoints.
"""

import unittest
from src.deadlock.validator import (
    validate_bankers_input,
    validate_resource_request,
)
from src.deadlock.bankers import (
    compute_need_matrix,
    check_safety,
    simulate_resource_request,
)
from app import create_app


class TestDeadlockValidator(unittest.TestCase):
    """Test validation of Banker's Algorithm inputs and resource requests."""

    def setUp(self):
        self.available = [3, 2]
        self.allocation = [[0, 1], [1, 0], [1, 1]]
        self.max_matrix = [[2, 1], [2, 0], [1, 2]]
        self.processes = ["P0", "P1", "P2"]
        self.resources = ["A", "B"]

    def test_valid_input_passes(self):
        is_valid, err = validate_bankers_input(
            self.available, self.allocation, self.max_matrix, self.processes, self.resources
        )
        self.assertTrue(is_valid)
        self.assertEqual(err, "")

    def test_allocation_exceeds_max(self):
        bad_alloc = [[3, 1], [1, 0], [1, 1]]  # P0 Alloc A=3 > Max A=2
        is_valid, err = validate_bankers_input(
            self.available, bad_alloc, self.max_matrix, self.processes, self.resources
        )
        self.assertFalse(is_valid)
        self.assertIn("exceeding Maximum demand", err)

    def test_negative_available(self):
        bad_avail = [-1, 2]
        is_valid, err = validate_bankers_input(
            bad_avail, self.allocation, self.max_matrix
        )
        self.assertFalse(is_valid)
        self.assertIn("non-negative", err)

    def test_dimension_mismatch(self):
        bad_alloc = [[0, 1], [1, 0]]  # 2 rows instead of 3
        is_valid, err = validate_bankers_input(
            self.available, bad_alloc, self.max_matrix
        )
        self.assertFalse(is_valid)
        self.assertIn("expected 2", err)

    def test_valid_resource_request(self):
        need = [[2, 0], [1, 0], [0, 1]]
        is_valid, err = validate_resource_request(
            request_vector=[1, 0],
            process_idx=0,
            need_matrix=need,
            available_vector=[3, 2],
            process_name="P0",
        )
        self.assertTrue(is_valid)
        self.assertEqual(err, "")

    def test_request_exceeds_need(self):
        need = [[2, 0], [1, 0], [0, 1]]
        is_valid, err = validate_resource_request(
            request_vector=[3, 0],  # Need is 2
            process_idx=0,
            need_matrix=need,
            available_vector=[3, 2],
            process_name="P0",
        )
        self.assertFalse(is_valid)
        self.assertIn("exceeds its declared remaining need", err)

    def test_request_exceeds_available(self):
        need = [[2, 0], [1, 0], [0, 1]]
        is_valid, err = validate_resource_request(
            request_vector=[2, 0],
            process_idx=0,
            need_matrix=need,
            available_vector=[1, 2],  # Available is only 1
            process_name="P0",
        )
        self.assertFalse(is_valid)
        self.assertIn("insufficient available resources", err)


class TestBankersAlgorithm(unittest.TestCase):
    """Test Banker's safety and resource request algorithms."""

    def setUp(self):
        # Classic Silberschatz 5-process, 3-resource safe state
        self.classic_safe = {
            "process_names": ["P0", "P1", "P2", "P3", "P4"],
            "resource_names": ["A", "B", "C"],
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
        }

    def test_compute_need_matrix(self):
        need = compute_need_matrix(
            self.classic_safe["allocation"], self.classic_safe["max"]
        )
        self.assertEqual(need[0], [7, 4, 3])  # P0
        self.assertEqual(need[1], [1, 2, 2])  # P1
        self.assertEqual(need[2], [6, 0, 0])  # P2
        self.assertEqual(need[3], [0, 1, 1])  # P3
        self.assertEqual(need[4], [4, 3, 1])  # P4

    def test_classic_safe_state(self):
        result = check_safety(
            available=self.classic_safe["available"],
            allocation=self.classic_safe["allocation"],
            max_matrix=self.classic_safe["max"],
            process_names=self.classic_safe["process_names"],
            resource_names=self.classic_safe["resource_names"],
        )
        self.assertTrue(result["is_safe"])
        self.assertEqual(len(result["safe_sequence"]), 5)
        self.assertEqual(result["safe_sequence"][0], "P1")
        self.assertEqual(result["safe_sequence"][1], "P3")
        self.assertEqual(len(result["steps"]), 5)

    def test_unsafe_state(self):
        # System where no process can ever be satisfied
        result = check_safety(
            available=[0, 0],
            allocation=[[1, 0], [0, 1]],
            max_matrix=[[2, 1], [1, 2]],
            process_names=["P0", "P1"],
            resource_names=["R1", "R2"],
        )
        self.assertFalse(result["is_safe"])
        self.assertEqual(result["safe_sequence"], [])
        self.assertIn("UNSAFE STATE", result["explanation"])

    def test_resource_request_grantable(self):
        # In classic state, P1 (index 1) requests [1, 0, 2] -> should be granted
        result = simulate_resource_request(
            available=self.classic_safe["available"],
            allocation=self.classic_safe["allocation"],
            max_matrix=self.classic_safe["max"],
            process_idx=1,
            request_vector=[1, 0, 2],
            process_names=self.classic_safe["process_names"],
            resource_names=self.classic_safe["resource_names"],
        )
        self.assertTrue(result["approved"])
        self.assertTrue(result["can_grant"])
        self.assertTrue(result["safety_result"]["is_safe"])
        self.assertIn("P1", result["safety_result"]["safe_sequence"])

    def test_resource_request_must_wait_exceeds_available(self):
        # P0 requests [4, 0, 0], but Available is [3, 3, 2]
        result = simulate_resource_request(
            available=self.classic_safe["available"],
            allocation=self.classic_safe["allocation"],
            max_matrix=self.classic_safe["max"],
            process_idx=0,
            request_vector=[4, 0, 0],
            process_names=self.classic_safe["process_names"],
            resource_names=self.classic_safe["resource_names"],
        )
        self.assertFalse(result["approved"])
        self.assertIn("insufficient available resources", result["reason"])

    def test_resource_request_denied_due_to_unsafe_future_state(self):
        # Craft a state where request is <= Available and <= Need, but granting it leads to unsafe state
        result = simulate_resource_request(
            available=[2],
            allocation=[[1], [2]],
            max_matrix=[[5], [3]],
            process_idx=0,
            request_vector=[2],
            process_names=["P0", "P1"],
            resource_names=["R1"],
        )
        self.assertFalse(result["approved"])
        self.assertIn("UNSAFE STATE", result["reason"])


class TestDeadlockAPI(unittest.TestCase):
    """Test Flask REST API routes for Deadlock Management."""

    def setUp(self):
        self.app = create_app().test_client()
        self.classic_safe = {
            "process_names": ["P0", "P1", "P2", "P3", "P4"],
            "resource_names": ["A", "B", "C"],
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
        }

    def test_api_deadlock_safety_endpoint(self):
        response = self.app.post("/api/deadlock/safety", json=self.classic_safe)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["is_safe"])
        self.assertEqual(data["safe_sequence"][0], "P1")

    def test_api_deadlock_safety_invalid_input(self):
        invalid_data = dict(self.classic_safe)
        invalid_data["available"] = [-1, 0, 0]
        response = self.app.post("/api/deadlock/safety", json=invalid_data)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

    def test_api_deadlock_request_endpoint_granted(self):
        payload = {
            **self.classic_safe,
            "process_index": 1,
            "request": [1, 0, 2],
        }
        response = self.app.post("/api/deadlock/request", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["approved"])
        self.assertTrue(data["can_grant"])


if __name__ == "__main__":
    unittest.main()
