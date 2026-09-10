"""
tests/test_sorting_combinations.py

Exhaustive integration test covering all combinations of:
- 3 Algorithms (Merge Sort, Quick Sort, Bubble Sort)
- 5 Sort Keys (Date & Time, Image Format, Land Type, Image Name, File Size)
- 2 Orders (Ascending, Descending)
"""

import unittest
from datetime import datetime as _dt
from models.image_record import ImageRecord
from dsa.sorting import merge_sort, quick_sort, bubble_sort, get_record_key

ALGORITHMS = [
    ("Merge Sort", merge_sort),
    ("Quick Sort", quick_sort),
    ("Bubble Sort", bubble_sort),
]

SORT_KEYS = [
    ("Date & Time", "datetime"),
    ("Image Format", "image_format"),
    ("Land Type", "land_type"),
    ("Image Name", "image_name"),
    ("File Size", "file_size"),
]

ORDERS = [
    ("Ascending", True),
    ("Descending", False),
]


class TestSortingCombinations(unittest.TestCase):
    """Exhaustive test for all 30 sorting parameter combinations."""

    def setUp(self):
        self.records = [
            ImageRecord(image_name="2026-03-01_12-00_Forest.png", date="2026-03-01", time="12-00", datetime="2026-03-01 12:00", image_format="png", land_type="Forest", file_size=200000),
            ImageRecord(image_name="2026-01-15_09-30_Water.jpg", date="2026-01-15", time="09-30", datetime="2026-01-15 09:30", image_format="jpg", land_type="Water", file_size=500000),
            ImageRecord(image_name="2025-12-05_09-20_Urban.tiff", date="2025-12-05", time="09-20", datetime="2025-12-05 09:20", image_format="tiff", land_type="Urban", file_size=100000),
            ImageRecord(image_name="2026-03-10_16-15_Agriculture.jpeg", date="2026-03-10", time="16-15", datetime="2026-03-10 16:15", image_format="jpeg", land_type="Agriculture", file_size=300000),
            ImageRecord(image_name="2026-03-12_11-20_Barren_Land.webp", date="2026-03-12", time="11-20", datetime="2026-03-12 11:20", image_format="webp", land_type="Barren_Land", file_size=400000),
        ]

    def test_all_30_combinations(self):
        """Test all 3 x 5 x 2 = 30 sorting parameter permutations."""
        for algo_name, algo_fn in ALGORITHMS:
            for key_label, key_field in SORT_KEYS:
                for order_label, is_asc in ORDERS:
                    with self.subTest(algorithm=algo_name, field=key_label, order=order_label):
                        sorted_list, comps = algo_fn(self.records, key=key_field, ascending=is_asc)
                        self.assertEqual(len(sorted_list), len(self.records))
                        self.assertGreater(comps, 0)

                        # Validate sorted order
                        extracted_vals = [get_record_key(r, key_field) for r in sorted_list]
                        for i in range(len(extracted_vals) - 1):
                            val_a = extracted_vals[i]
                            val_b = extracted_vals[i + 1]
                            if is_asc:
                                self.assertLessEqual(val_a, val_b, f"Ascending violation in {algo_name} on {key_label}: {val_a} > {val_b}")
                            else:
                                self.assertGreaterEqual(val_a, val_b, f"Descending violation in {algo_name} on {key_label}: {val_a} < {val_b}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
