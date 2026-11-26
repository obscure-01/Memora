"""
Page replacement algorithm implementations.

Each module implements a single page replacement algorithm with a consistent
interface. All algorithms accept a page reference sequence and frame count,
and return a standardized SimulationResult.

Modules:
    fifo: First In, First Out page replacement
    lru: Least Recently Used page replacement
    optimal: Optimal (Bélády's) page replacement
"""
