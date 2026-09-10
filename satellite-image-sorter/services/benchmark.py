"""
services/benchmark.py

Service to benchmark and compare the performance of manual DSA sorting algorithms
(Bubble Sort, Merge Sort, Quick Sort) on identical datasets.
"""

import time
from typing import List, Dict, Any, Union, Callable
import sys
import os

# Ensure root directory is on sys.path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.image_record import ImageRecord
from dsa.sorting import bubble_sort, merge_sort, quick_sort

ALGORITHMS = [
    ("Bubble Sort", bubble_sort),
    ("Merge Sort", merge_sort),
    ("Quick Sort", quick_sort),
]


def benchmark_sorting_algorithms(
    records: List[ImageRecord],
    key: Union[str, Callable[[ImageRecord], Any]] = "datetime",
    ascending: bool = True,
) -> List[Dict[str, Any]]:
    """
    Runs Bubble Sort, Merge Sort, and Quick Sort on identical copies of the
    dataset, tracking execution time and total comparisons for each.

    Returns:
    - List of dictionaries containing:
      - 'algorithm': name of algorithm
      - 'comparisons': total comparison count
      - 'time_ms': execution time in milliseconds
      - 'time_us': execution time in microseconds
      - 'item_count': number of elements sorted
    """
    results: List[Dict[str, Any]] = []

    for name, sort_fn in ALGORITHMS:
        # Create fresh copy to ensure identical input state and avoid caching
        input_copy = list(records)

        start_time = time.perf_counter()
        sorted_list, comps = sort_fn(input_copy, key=key, ascending=ascending)
        elapsed_sec = time.perf_counter() - start_time

        time_ms = elapsed_sec * 1000.0
        time_us = elapsed_sec * 1000000.0

        results.append({
            "algorithm": name,
            "comparisons": comps,
            "time_ms": time_ms,
            "time_us": time_us,
            "item_count": len(sorted_list),
        })

    return results
