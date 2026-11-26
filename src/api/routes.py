"""
Flask API Routes for Memora.

Endpoints:
    - GET  /api/health   : Health check endpoint
    - POST /api/simulate : Execute single page replacement algorithm simulation
    - POST /api/compare  : Compare FIFO, LRU, and Optimal algorithms on identical input
"""

from flask import Blueprint, jsonify, request
from src.core.simulator import run_simulation
from src.analysis.comparison import compare_algorithms
from src.core.validator import validate_page_sequence, validate_frame_count
from src.cpu.scheduler import run_cpu_scheduler, compare_cpu_schedulers
from src.deadlock.bankers import check_safety, simulate_resource_request


api_bp = Blueprint("api", __name__)

SUPPORTED_ALGORITHMS = {
    "FIFO": "FIFO",
    "LRU": "LRU",
    "OPTIMAL": "Optimal",
    "OPT": "Optimal",
}


def _error_response(message, details, status_code=400):
    """Format a consistent JSON error response."""
    return jsonify({
        "error": {
            "message": message,
            "details": details,
        }
    }), status_code


@api_bp.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.

    Returns:
        JSON with status: 'ok' and application name.
    """
    return jsonify({
        "status": "ok",
        "application": "Memora",
    }), 200


@api_bp.route("/simulate", methods=["POST"])
def simulate():
    """
    Run one page replacement algorithm simulation.

    Expected JSON body:
        {
            "sequence": [7, 0, 1, 2, ...],
            "frames": 3,
            "algorithm": "FIFO" | "LRU" | "OPTIMAL"
        }

    Returns:
        JSON with simulation result, metrics, and step-by-step history.
    """
    if not request.is_json:
        return _error_response(
            "Invalid input",
            "Request body must be valid JSON with Content-Type: application/json.",
            400,
        )

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error_response("Invalid input", "Request body must be a JSON object.", 400)

    # Check required fields
    for field in ["sequence", "frames", "algorithm"]:
        if field not in data:
            return _error_response("Invalid input", f"Missing required field: '{field}'.", 400)

    sequence = data["sequence"]
    frames = data["frames"]
    algorithm = data["algorithm"]

    # Validate sequence
    seq_valid, seq_err = validate_page_sequence(sequence)
    if not seq_valid:
        return _error_response("Invalid input", seq_err, 400)

    # Validate frame count
    fc_valid, fc_err = validate_frame_count(frames)
    if not fc_valid:
        return _error_response("Invalid input", fc_err, 400)

    # Validate algorithm
    if not isinstance(algorithm, str):
        return _error_response("Invalid input", "Algorithm must be a string.", 400)

    algo_key = algorithm.strip().upper()
    if algo_key not in SUPPORTED_ALGORITHMS:
        supported_str = "FIFO, LRU, Optimal"
        return _error_response(
            "Invalid input",
            f"Invalid algorithm '{algorithm}'. Supported algorithms: {supported_str}.",
            400,
        )

    canonical_algo = SUPPORTED_ALGORITHMS[algo_key]

    try:
        result = run_simulation(canonical_algo, sequence, frames)
    except Exception as e:
        return _error_response("Simulation error", str(e), 500)

    response_data = {
        "algorithm": result["algorithm"],
        "sequence": result["page_sequence"],
        "frame_count": result["frame_count"],
        "total_pages": len(result["page_sequence"]),
        "hits": result["hits"],
        "faults": result["faults"],
        "hit_ratio": result["hit_ratio"],
        "fault_ratio": result["fault_ratio"],
        "history": result["history"],
    }

    return jsonify(response_data), 200


@api_bp.route("/compare", methods=["POST"])
def compare():
    """
    Compare FIFO, LRU, and Optimal algorithms on identical input.

    Expected JSON body:
        {
            "sequence": [7, 0, 1, 2, ...],
            "frames": 3
        }

    Returns:
        JSON with per-algorithm metrics and comparison summary.
    """
    if not request.is_json:
        return _error_response(
            "Invalid input",
            "Request body must be valid JSON with Content-Type: application/json.",
            400,
        )

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error_response("Invalid input", "Request body must be a JSON object.", 400)

    for field in ["sequence", "frames"]:
        if field not in data:
            return _error_response("Invalid input", f"Missing required field: '{field}'.", 400)

    sequence = data["sequence"]
    frames = data["frames"]

    seq_valid, seq_err = validate_page_sequence(sequence)
    if not seq_valid:
        return _error_response("Invalid input", seq_err, 400)

    fc_valid, fc_err = validate_frame_count(frames)
    if not fc_valid:
        return _error_response("Invalid input", fc_err, 400)

    try:
        comp_result = compare_algorithms(sequence, frames)
    except Exception as e:
        return _error_response("Comparison error", str(e), 500)

    # Format results as dictionary mapping algorithm names to their metrics
    results_map = {}
    for r in comp_result["results"]:
        algo_name = r["algorithm"]
        key = algo_name.upper()  # "FIFO", "LRU", "OPTIMAL"
        results_map[key] = {
            "algorithm": algo_name,
            "hits": r["hits"],
            "faults": r["faults"],
            "hit_ratio": r["hit_ratio"],
            "fault_ratio": r["fault_ratio"],
            "history": r.get("history", []),
        }

    response_data = {
        "sequence": comp_result["page_sequence"],
        "frame_count": comp_result["frame_count"],
        "total_pages": len(comp_result["page_sequence"]),
        "results": results_map,
        "summary": comp_result["summary"],
    }

    return jsonify(response_data), 200


# =============================================================================
# CPU Scheduling Routes
# =============================================================================

@api_bp.route("/cpu/schedule", methods=["POST"])
def cpu_schedule():
    """
    Run one CPU scheduling algorithm simulation (FCFS, SJF, or RR).

    Expected JSON body:
        {
            "algorithm": "FCFS" | "SJF" | "RR",
            "processes": [
                {"id": "P1", "arrival_time": 0, "burst_time": 5},
                ...
            ],
            "time_quantum": 2  # Required for RR
        }
    """
    if not request.is_json:
        return _error_response("Invalid input", "Request body must be valid JSON.", 400)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error_response("Invalid input", "Request body must be a JSON object.", 400)

    algo = data.get("algorithm")
    processes = data.get("processes")
    time_quantum = data.get("time_quantum", 2)

    if not algo:
        return _error_response("Invalid input", "Missing required field: 'algorithm'.", 400)
    if processes is None:
        return _error_response("Invalid input", "Missing required field: 'processes'.", 400)

    try:
        result = run_cpu_scheduler(algo, processes, time_quantum=time_quantum)
    except ValueError as ve:
        return _error_response("Validation error", str(ve), 400)
    except Exception as e:
        return _error_response("Scheduling error", str(e), 500)

    return jsonify(result), 200


@api_bp.route("/cpu/compare", methods=["POST"])
def cpu_compare():
    """
    Compare FCFS, SJF, and Round Robin on identical process inputs.

    Expected JSON body:
        {
            "processes": [
                {"id": "P1", "arrival_time": 0, "burst_time": 5},
                ...
            ],
            "time_quantum": 2
        }
    """
    if not request.is_json:
        return _error_response("Invalid input", "Request body must be valid JSON.", 400)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error_response("Invalid input", "Request body must be a JSON object.", 400)

    processes = data.get("processes")
    time_quantum = data.get("time_quantum", 2)

    if processes is None:
        return _error_response("Invalid input", "Missing required field: 'processes'.", 400)

    try:
        comparison = compare_cpu_schedulers(processes, time_quantum=time_quantum)
    except ValueError as ve:
        return _error_response("Validation error", str(ve), 400)
    except Exception as e:
        return _error_response("Comparison error", str(e), 500)

    return jsonify(comparison), 200


# =============================================================================
# Deadlock Management Routes (Banker's Algorithm)
# =============================================================================

@api_bp.route("/deadlock/safety", methods=["POST"])
def deadlock_safety():
    """
    Execute Banker's Safety Algorithm to determine safe state and safe sequence.

    Expected JSON body:
        {
            "available": [3, 3, 2],
            "allocation": [[0, 1, 0], [2, 0, 0], ...],
            "max": [[7, 5, 3], [3, 2, 2], ...],
            "process_names": ["P0", "P1", ...],    # optional
            "resource_names": ["A", "B", ...]      # optional
        }
    """
    if not request.is_json:
        return _error_response("Invalid input", "Request body must be valid JSON.", 400)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error_response("Invalid input", "Request body must be a JSON object.", 400)

    for field in ["available", "allocation", "max"]:
        if field not in data:
            return _error_response("Invalid input", f"Missing required field: '{field}'.", 400)

    available = data["available"]
    allocation = data["allocation"]
    max_matrix = data["max"]
    process_names = data.get("process_names")
    resource_names = data.get("resource_names")

    try:
        safety_eval = check_safety(
            available=available,
            allocation=allocation,
            max_matrix=max_matrix,
            process_names=process_names,
            resource_names=resource_names,
        )
    except ValueError as ve:
        return _error_response("Validation error", str(ve), 400)
    except Exception as e:
        return _error_response("Safety check error", str(e), 500)

    return jsonify(safety_eval), 200


@api_bp.route("/deadlock/request", methods=["POST"])
def deadlock_request():
    """
    Evaluate a process resource request using Banker's Resource-Request Algorithm.

    Expected JSON body:
        {
            "available": [3, 3, 2],
            "allocation": [[0, 1, 0], ...],
            "max": [[7, 5, 3], ...],
            "process_index": 1,
            "request": [1, 0, 2],
            "process_names": ["P0", "P1", ...],    # optional
            "resource_names": ["A", "B", ...]      # optional
        }
    """
    if not request.is_json:
        return _error_response("Invalid input", "Request body must be valid JSON.", 400)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error_response("Invalid input", "Request body must be a JSON object.", 400)

    for field in ["available", "allocation", "max", "process_index", "request"]:
        if field not in data:
            return _error_response("Invalid input", f"Missing required field: '{field}'.", 400)

    available = data["available"]
    allocation = data["allocation"]
    max_matrix = data["max"]
    process_idx = data["process_index"]
    req_vector = data["request"]
    process_names = data.get("process_names")
    resource_names = data.get("resource_names")

    if not isinstance(process_idx, int) or isinstance(process_idx, bool):
        return _error_response("Invalid input", "Field 'process_index' must be an integer.", 400)

    try:
        req_eval = simulate_resource_request(
            available=available,
            allocation=allocation,
            max_matrix=max_matrix,
            process_idx=process_idx,
            request_vector=req_vector,
            process_names=process_names,
            resource_names=resource_names,
        )
    except ValueError as ve:
        return _error_response("Validation error", str(ve), 400)
    except Exception as e:
        return _error_response("Request simulation error", str(e), 500)

    return jsonify(req_eval), 200

