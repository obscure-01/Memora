"""
CPU Scheduling Module.

Provides FCFS, SJF (Non-preemptive), and Round Robin CPU scheduling algorithms.
"""

from src.cpu.fcfs import run_fcfs
from src.cpu.sjf import run_sjf
from src.cpu.round_robin import run_round_robin
from src.cpu.scheduler import run_cpu_scheduler, compare_cpu_schedulers
from src.cpu.validator import validate_processes, validate_time_quantum
from src.cpu.metrics import compute_schedule_metrics

__all__ = [
    "run_fcfs",
    "run_sjf",
    "run_round_robin",
    "run_cpu_scheduler",
    "compare_cpu_schedulers",
    "validate_processes",
    "validate_time_quantum",
    "compute_schedule_metrics",
]
