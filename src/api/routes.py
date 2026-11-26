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
