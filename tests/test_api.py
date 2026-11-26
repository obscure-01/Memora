"""
Unit tests for Memora Flask REST API.

Tests:
    1. Health check endpoint (GET /api/health)
    2. Simulation endpoint (POST /api/simulate) for FIFO, LRU, Optimal
    3. Comparison endpoint (POST /api/compare)
    4. Input validation and error handling (400, 404, 405)
    5. Regression checks against textbook reference sequence:
       [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1] with 3 frames
"""

import json
import unittest
from src.api.app import create_app


class TestMemoraAPI(unittest.TestCase):
    """Test suite for Flask API endpoints."""

    def setUp(self):
        """Set up Flask test client with test configuration."""
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

        # Standard reference sequence (20 accesses, 3 frames)
        self.ref_sequence = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
        self.ref_frames = 3

    # =========================================================================
    # 1. Health Check Endpoint Tests
    # =========================================================================

    def test_health_check_returns_ok(self):
        """GET /api/health returns 200 OK with application name."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")

        data = response.get_json()
        self.assertEqual(data.get("status"), "ok")
        self.assertEqual(data.get("application"), "Memora")

    def test_root_index_endpoint(self):
        """GET / returns API metadata and endpoint overview."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("application"), "Memora")
        self.assertIn("endpoints", data)

    # =========================================================================
    # 2. Simulation Endpoint Tests (POST /api/simulate)
    # =========================================================================

    def test_simulate_fifo_reference_case(self):
        """POST /api/simulate with FIFO produces known reference results (15 faults, 5 hits)."""
        payload = {
            "sequence": self.ref_sequence,
            "frames": self.ref_frames,
            "algorithm": "FIFO",
        }
        response = self.client.post("/api/simulate", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["algorithm"], "FIFO")
        self.assertEqual(data["sequence"], self.ref_sequence)
        self.assertEqual(data["frame_count"], 3)
        self.assertEqual(data["total_pages"], 20)
        self.assertEqual(data["hits"], 5)
        self.assertEqual(data["faults"], 15)
        self.assertAlmostEqual(data["hit_ratio"], 0.25, places=4)
        self.assertAlmostEqual(data["fault_ratio"], 0.75, places=4)
        self.assertEqual(data["hits"] + data["faults"], data["total_pages"])
        self.assertAlmostEqual(data["hit_ratio"] + data["fault_ratio"], 1.0, places=4)

        # Verify history schema
        self.assertEqual(len(data["history"]), 20)
        first_step = data["history"][0]
        self.assertEqual(first_step["step"], 0)
        self.assertEqual(first_step["page"], 7)
        self.assertEqual(first_step["is_hit"], False)
        self.assertEqual(first_step["evicted"], None)
        self.assertEqual(len(first_step["frames"]), 3)

        # Verify eviction step (Step 3: page 2 arrives, evicts 7)
        step_3 = data["history"][3]
        self.assertEqual(step_3["page"], 2)
        self.assertEqual(step_3["is_hit"], False)
        self.assertEqual(step_3["evicted"], 7)

    def test_simulate_lru_reference_case(self):
        """POST /api/simulate with LRU produces known reference results (12 faults, 8 hits)."""
        payload = {
            "sequence": self.ref_sequence,
            "frames": self.ref_frames,
            "algorithm": "LRU",
        }
        response = self.client.post("/api/simulate", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["algorithm"], "LRU")
        self.assertEqual(data["hits"], 8)
        self.assertEqual(data["faults"], 12)
        self.assertAlmostEqual(data["hit_ratio"], 0.40, places=4)
        self.assertAlmostEqual(data["fault_ratio"], 0.60, places=4)

    def test_simulate_optimal_reference_case(self):
        """POST /api/simulate with Optimal produces known reference results (9 faults, 11 hits)."""
        payload = {
            "sequence": self.ref_sequence,
            "frames": self.ref_frames,
            "algorithm": "OPTIMAL",
        }
        response = self.client.post("/api/simulate", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["algorithm"], "Optimal")
        self.assertEqual(data["hits"], 11)
        self.assertEqual(data["faults"], 9)
        self.assertAlmostEqual(data["hit_ratio"], 0.55, places=4)
        self.assertAlmostEqual(data["fault_ratio"], 0.45, places=4)

    def test_simulate_case_insensitive_algorithm(self):
        """Algorithm names should be accepted case-insensitively."""
        for name in ["fifo", "Fifo", "FIFO", "lru", "Lru", "optimal", "Optimal", "OPTIMAL"]:
            res = self.client.post("/api/simulate", json={
                "sequence": [1, 2, 3],
                "frames": 2,
                "algorithm": name,
            })
            self.assertEqual(res.status_code, 200)

    # =========================================================================
    # 3. Comparison Endpoint Tests (POST /api/compare)
    # =========================================================================

    def test_compare_reference_case(self):
        """POST /api/compare runs all algorithms and returns consistent metrics."""
        payload = {
            "sequence": self.ref_sequence,
            "frames": self.ref_frames,
        }
        response = self.client.post("/api/compare", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertEqual(data["sequence"], self.ref_sequence)
        self.assertEqual(data["frame_count"], 3)
        self.assertEqual(data["total_pages"], 20)

        results = data["results"]
        self.assertIn("FIFO", results)
        self.assertIn("LRU", results)
        self.assertIn("OPTIMAL", results)

        self.assertEqual(results["FIFO"]["faults"], 15)
        self.assertEqual(results["FIFO"]["hits"], 5)
        self.assertEqual(results["LRU"]["faults"], 12)
        self.assertEqual(results["LRU"]["hits"], 8)
        self.assertEqual(results["OPTIMAL"]["faults"], 9)
        self.assertEqual(results["OPTIMAL"]["hits"], 11)

        summary = data["summary"]
        self.assertEqual(summary["fewest_faults"], 9)
        self.assertEqual(summary["best_algorithm"], "Optimal")

    def test_compare_belady_anomaly_sequence(self):
        """POST /api/compare with Bélády sequence [1,2,3,4,1,2,5,1,2,3,4,5] (3 frames).

        Verifies exact algorithm counts:
          - FIFO: 9 faults, 3 hits (hit_ratio 25.0%)
          - LRU: 10 faults, 2 hits (hit_ratio 16.67%)
          - Optimal: 7 faults, 5 hits (hit_ratio 41.67%)
          - Best: Optimal (7 faults)
        This ensures API output structure is consistent with comparison table & chart expectations.
        """
        belady_seq = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
        response = self.client.post("/api/compare", json={"sequence": belady_seq, "frames": 3})
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        results = data["results"]
        self.assertEqual(results["FIFO"]["faults"], 9)
        self.assertEqual(results["FIFO"]["hits"], 3)
        self.assertEqual(results["LRU"]["faults"], 10)
        self.assertEqual(results["LRU"]["hits"], 2)
        self.assertEqual(results["OPTIMAL"]["faults"], 7)
        self.assertEqual(results["OPTIMAL"]["hits"], 5)

        summary = data["summary"]
        self.assertEqual(summary["fewest_faults"], 7)
        self.assertEqual(summary["best_algorithm"], "Optimal")
        self.assertEqual(summary["best_algorithms"], ["Optimal"])

        # Also verify Bélády's anomaly for FIFO (3 frames -> 9 faults, 4 frames -> 10 faults)
        res_4 = self.client.post("/api/compare", json={"sequence": belady_seq, "frames": 4})
        self.assertEqual(res_4.status_code, 200)
        self.assertEqual(res_4.get_json()["results"]["FIFO"]["faults"], 10)

    # =========================================================================
    # 4. Input Validation & Error Handling Tests
    # =========================================================================

    def test_missing_request_body_or_non_json(self):
        """Non-JSON or empty body returns 400 Bad Request."""
        res = self.client.post("/api/simulate", data="not json", content_type="text/plain")
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn("error", data)

    def test_missing_required_fields(self):
        """Missing required fields in /api/simulate return 400."""
        # Missing algorithm
        res1 = self.client.post("/api/simulate", json={"sequence": [1, 2], "frames": 2})
        self.assertEqual(res1.status_code, 400)
        self.assertIn("algorithm", res1.get_json()["error"]["details"].lower())

        # Missing frames
        res2 = self.client.post("/api/simulate", json={"sequence": [1, 2], "algorithm": "FIFO"})
        self.assertEqual(res2.status_code, 400)
        self.assertIn("frames", res2.get_json()["error"]["details"].lower())

        # Missing sequence
        res3 = self.client.post("/api/simulate", json={"frames": 2, "algorithm": "FIFO"})
        self.assertEqual(res3.status_code, 400)
        self.assertIn("sequence", res3.get_json()["error"]["details"].lower())

    def test_invalid_algorithm_name(self):
        """Unrecognized algorithm names are rejected with 400."""
        res = self.client.post("/api/simulate", json={
            "sequence": [1, 2, 3],
            "frames": 2,
            "algorithm": "UNKNOWN_ALGO",
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("Supported algorithms", res.get_json()["error"]["details"])

    def test_empty_sequence_rejected(self):
        """Empty page sequence is rejected with 400."""
        res = self.client.post("/api/simulate", json={
            "sequence": [],
            "frames": 2,
            "algorithm": "FIFO",
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("empty", res.get_json()["error"]["details"].lower())

    def test_negative_page_number_rejected(self):
        """Negative page numbers are rejected with 400."""
        res = self.client.post("/api/simulate", json={
            "sequence": [1, -2, 3],
            "frames": 2,
            "algorithm": "FIFO",
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("non-negative", res.get_json()["error"]["details"].lower())

    def test_boolean_values_rejected(self):
        """Booleans (True/False) must be rejected for both frames and pages."""
        # Boolean page
        res1 = self.client.post("/api/simulate", json={
            "sequence": [1, True, 3],
            "frames": 2,
            "algorithm": "FIFO",
        })
        self.assertEqual(res1.status_code, 400)
        self.assertIn("boolean", res1.get_json()["error"]["details"].lower())

        # Boolean frame
        res2 = self.client.post("/api/simulate", json={
            "sequence": [1, 2, 3],
            "frames": True,
            "algorithm": "FIFO",
        })
        self.assertEqual(res2.status_code, 400)
        self.assertIn("boolean", res2.get_json()["error"]["details"].lower())

    def test_invalid_frame_counts(self):
        """Zero, negative, or non-integer frame counts are rejected."""
        # Zero
        res0 = self.client.post("/api/simulate", json={
            "sequence": [1, 2, 3],
            "frames": 0,
            "algorithm": "FIFO",
        })
        self.assertEqual(res0.status_code, 400)

        # Negative
        res_neg = self.client.post("/api/simulate", json={
            "sequence": [1, 2, 3],
            "frames": -1,
            "algorithm": "FIFO",
        })
        self.assertEqual(res_neg.status_code, 400)

        # Float
        res_flt = self.client.post("/api/simulate", json={
            "sequence": [1, 2, 3],
            "frames": 3.5,
            "algorithm": "FIFO",
        })
        self.assertEqual(res_flt.status_code, 400)

    def test_compare_validation_errors(self):
        """Invalid inputs on /api/compare are rejected with 400."""
        # Missing fields
        res1 = self.client.post("/api/compare", json={"sequence": [1, 2]})
        self.assertEqual(res1.status_code, 400)

        # Invalid sequence
        res2 = self.client.post("/api/compare", json={"sequence": [], "frames": 3})
        self.assertEqual(res2.status_code, 400)

    def test_unknown_route_returns_404(self):
        """Unknown route returns custom 404 JSON."""
        res = self.client.get("/api/unknown_route")
        self.assertEqual(res.status_code, 404)
        self.assertIn("error", res.get_json())
        self.assertEqual(res.get_json()["error"]["message"], "Resource not found")

    def test_method_not_allowed_returns_405(self):
        """Unsupported method returns custom 405 JSON."""
        res = self.client.get("/api/simulate")  # GET on POST endpoint
        self.assertEqual(res.status_code, 405)
        self.assertIn("error", res.get_json())
        self.assertEqual(res.get_json()["error"]["message"], "Method not allowed")

    # =========================================================================
    # 5. Frontend & Static Assets Tests (Phase 2)
    # =========================================================================

    def test_frontend_dashboard_served_on_html_accept(self):
        """GET / with Accept: text/html serves the interactive HTML frontend."""
        res = self.client.get("/", headers={"Accept": "text/html,application/xhtml+xml"})
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.content_type)
        html = res.get_data(as_text=True)
        self.assertIn("Memora", html)
        self.assertIn("Virtual Memory Simulator", html)
        self.assertIn("memory-frames-rack", html)

    def test_frontend_dashboard_direct_route(self):
        """GET /dashboard serves the interactive HTML frontend."""
        res = self.client.get("/dashboard")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.content_type)
        html = res.get_data(as_text=True)
        self.assertIn("Memora", html)

    def test_static_assets_served(self):
        """Static CSS and JavaScript files are served correctly."""
        # CSS
        res_css = self.client.get("/static/css/style.css")
        self.assertEqual(res_css.status_code, 200)
        self.assertIn("text/css", res_css.content_type)
        res_css.close()

        # JavaScript files
        for js_file in ["api.js", "charts.js", "visualizer.js", "app.js"]:
            res_js = self.client.get(f"/static/js/{js_file}")
            self.assertEqual(res_js.status_code, 200, f"Failed to serve /static/js/{js_file}")
            res_js.close()


if __name__ == "__main__":
    unittest.main()
