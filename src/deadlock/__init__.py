"""
Deadlock Management Module.

Provides Banker's Algorithm for deadlock avoidance, safety checking,
and dynamic resource request simulation.
"""

from src.deadlock.bankers import (
    compute_need_matrix,
    check_safety,
    simulate_resource_request,
)
from src.deadlock.validator import (
    validate_bankers_input,
    validate_resource_request,
)

__all__ = [
    "compute_need_matrix",
    "check_safety",
    "simulate_resource_request",
    "validate_bankers_input",
    "validate_resource_request",
]
