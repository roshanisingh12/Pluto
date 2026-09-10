"""
tests/test_benchmark_comparison.py

Unit tests for Phase 11 Algorithm Comparison and Benchmarking service:
- Small dataset (5 elements)
- Medium dataset (60 elements)
- Duplicate values
- Already sorted data (validates Bubble Sort early-exit)
- Reverse sorted data (validates worst-case quadratic behavior)
"""

import unittest
from models.image_record import ImageRecord
from services.benchmark import benchmark_sorting_algorithms


class TestBenchmarkComparison(unittest.TestCase):
    """Test suite for benchmarking sorting algorithms."""

    def _create_dataset(self, size: int, mode: str = "random") -> list:
        records = []
        if mode == "random":
            # Deterministic pseudo-random pattern
            for i in range(size):
                val = (i * 37) % size
                records.append(ImageRecord(
                    image_id=f"SAT{i:03d}",
                    image_name=f"2026-01-{(val % 28) + 1:02d}_12-00_Forest.jpg",
                    date=f"2026-01-{(val % 28) + 1:02d}",
                    file_size=val * 1000,
                ))
        elif mode == "sorted":
            for i in range(size):
                records.append(ImageRecord(
                    image_id=f"SAT{i:03d}",
                    image_name=f"2026-01-{(i % 28) + 1:02d}_12-00_Forest.jpg",
                    date=f"2026-01-{(i % 28) + 1:02d}",
                    file_size=i * 1000,
                ))
        elif mode == "reverse":
            for i in range(size):
                val = size - i
                records.append(ImageRecord(
                    image_id=f"SAT{i:03d}",
                    image_name=f"2026-01-{(val % 28) + 1:02d}_12-00_Forest.jpg",
                    date=f"2026-01-{(val % 28) + 1:02d}",
                    file_size=val * 1000,
                ))
        elif mode == "duplicates":
            for i in range(size):
                records.append(ImageRecord(
                    image_id=f"SAT{i:03d}",
                    image_name="2026-01-15_12-00_Forest.jpg",
                    date="2026-01-15",
                    file_size=5000,
                ))
        return records

    def test_small_dataset(self):
        """Test benchmark on small dataset (5 items)."""
        records = self._create_dataset(5, "random")
        results = benchmark_sorting_algorithms(records, key="file_size", ascending=True)

        self.assertEqual(len(results), 3)
        algo_names = [r["algorithm"] for r in results]
        self.assertEqual(algo_names, ["Bubble Sort", "Merge Sort", "Quick Sort"])
        for r in results:
            self.assertEqual(r["item_count"], 5)
            self.assertGreater(r["comparisons"], 0)
            self.assertGreaterEqual(r["time_ms"], 0.0)

    def test_medium_dataset(self):
        """Test benchmark on medium dataset (50 items)."""
        records = self._create_dataset(50, "random")
        results = benchmark_sorting_algorithms(records, key="file_size", ascending=True)

        self.assertEqual(len(results), 3)
        for r in results:
            self.assertEqual(r["item_count"], 50)
            self.assertGreater(r["comparisons"], 0)

    def test_duplicate_values(self):
        """Test benchmark when all keys are identical."""
        records = self._create_dataset(20, "duplicates")
        results = benchmark_sorting_algorithms(records, key="file_size", ascending=True)

        self.assertEqual(len(results), 3)
        for r in results:
            self.assertEqual(r["item_count"], 20)

    def test_already_sorted_data(self):
        """Test benchmark on already sorted data (Bubble Sort should have n - 1 comparisons)."""
        records = self._create_dataset(15, "sorted")
        results = benchmark_sorting_algorithms(records, key="file_size", ascending=True)

        bubble_res = next(r for r in results if r["algorithm"] == "Bubble Sort")
        # Optimized bubble sort completes in 1 pass = n - 1 comparisons = 14
        self.assertEqual(bubble_res["comparisons"], 14)

    def test_reverse_sorted_data(self):
        """Test benchmark on reverse sorted data (worst-case for Bubble Sort: n*(n-1)/2)."""
        records = self._create_dataset(10, "reverse")
        results = benchmark_sorting_algorithms(records, key="file_size", ascending=True)

        bubble_res = next(r for r in results if r["algorithm"] == "Bubble Sort")
        # Worst case for 10 elements: 9 + 8 + ... + 1 = 45 comparisons
        self.assertEqual(bubble_res["comparisons"], 45)


if __name__ == "__main__":
    unittest.main(verbosity=2)
