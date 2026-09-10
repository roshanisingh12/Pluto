"""
tests/test_sorting.py

Unit tests for manual DSA sorting algorithms in dsa/sorting.py:
- Bubble Sort
- Merge Sort
- Quick Sort

Scenarios tested for each algorithm:
- Empty list ([])
- Single-element list
- Multiple elements
- Duplicate values
- Ascending & descending order
- Key: Date & Time
- Key: Image Format
- Key: Land Type
- Key: Image Name
- Key: File Size
- Preservation/immutability of original list
- Accurate comparison counts
"""

import unittest
import copy
from models.image_record import ImageRecord
from dsa.sorting import bubble_sort, merge_sort, quick_sort, get_record_key

SORTING_ALGORITHMS = [
    ("Bubble Sort", bubble_sort),
    ("Merge Sort", merge_sort),
    ("Quick Sort", quick_sort),
]


class TestSortingAlgorithms(unittest.TestCase):
    """Comprehensive test suite for manual DSA sorting algorithms."""

    def setUp(self):
        """Create sample ImageRecord test fixtures with varied attributes."""
        self.record1 = ImageRecord(
            image_name="2026-03-01_12-00_Forest.png",
            date="2026-03-01",
            time="12-00",
            datetime="2026-03-01 12:00",
            image_format="png",
            land_type="Forest",
            file_size=204800,
        )
        self.record2 = ImageRecord(
            image_name="2026-01-15_09-30_Water.jpg",
            date="2026-01-15",
            time="09-30",
            datetime="2026-01-15 09:30",
            image_format="jpg",
            land_type="Water",
            file_size=512000,
        )
        self.record3 = ImageRecord(
            image_name="2026-02-20_18-45_Urban.tiff",
            date="2026-02-20",
            time="18-45",
            datetime="2026-02-20 18:45",
            image_format="tiff",
            land_type="Urban",
            file_size=102400,
        )
        self.record4 = ImageRecord(
            image_name="2026-01-10_06-00_Agriculture.jpeg",
            date="2026-01-10",
            time="06-00",
            datetime="2026-01-10 06:00",
            image_format="jpeg",
            land_type="Agriculture",
            file_size=307200,
        )
        self.record5 = ImageRecord(
            image_name="2026-04-05_15-15_Barren_Land.png",
            date="2026-04-05",
            time="15-15",
            datetime="2026-04-05 15:15",
            image_format="png",
            land_type="Barren_Land",
            file_size=409600,
        )
        self.records = [self.record1, self.record2, self.record3, self.record4, self.record5]

    # ------------------------------------------------------------------
    # 1. Edge Case: Empty List
    # ------------------------------------------------------------------
    def test_empty_list(self):
        """Ensure all sorting algorithms handle an empty input list correctly."""
        for name, sort_fn in SORTING_ALGORITHMS:
            with self.subTest(algorithm=name):
                result, comparisons = sort_fn([])
                self.assertEqual(result, [])
                self.assertEqual(comparisons, 0)

    # ------------------------------------------------------------------
    # 2. Edge Case: Single Element List
    # ------------------------------------------------------------------
    def test_single_element(self):
        """Ensure all sorting algorithms handle a 1-element list correctly."""
        for name, sort_fn in SORTING_ALGORITHMS:
            with self.subTest(algorithm=name):
                single = [self.record1]
                result, comparisons = sort_fn(single)
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0].image_name, self.record1.image_name)
                self.assertEqual(comparisons, 0)

    # ------------------------------------------------------------------
    # 3. Multiple Elements & Default Sorting (Date/Time Ascending)
    # ------------------------------------------------------------------
    def test_multiple_elements_datetime_ascending(self):
        """Verify ascending sort on datetime for multiple elements."""
        expected_dates = [
            "2026-01-10 06:00",
            "2026-01-15 09:30",
            "2026-02-20 18:45",
            "2026-03-01 12:00",
            "2026-04-05 15:15",
        ]
        for name, sort_fn in SORTING_ALGORITHMS:
            with self.subTest(algorithm=name):
                result, comparisons = sort_fn(self.records, key="datetime", ascending=True)
                actual_dates = [r.datetime for r in result]
                self.assertEqual(actual_dates, expected_dates)
                self.assertGreater(comparisons, 0)

    # ------------------------------------------------------------------
    # 4. Descending Sorting
    # ------------------------------------------------------------------
    def test_datetime_descending(self):
        """Verify descending sort on datetime."""
        expected_dates = [
            "2026-04-05 15:15",
            "2026-03-01 12:00",
            "2026-02-20 18:45",
            "2026-01-15 09:30",
            "2026-01-10 06:00",
        ]
        for name, sort_fn in SORTING_ALGORITHMS:
            with self.subTest(algorithm=name):
                # Test ascending=False
                result, comparisons = sort_fn(self.records, key="date & time", ascending=False)
                actual_dates = [r.datetime for r in result]
                self.assertEqual(actual_dates, expected_dates)
                self.assertGreater(comparisons, 0)

                # Test reverse=True alias
                result_rev, _ = sort_fn(self.records, key="datetime", reverse=True)
                self.assertEqual([r.datetime for r in result_rev], expected_dates)

    # ------------------------------------------------------------------
    # 5. Duplicate Values
    # ------------------------------------------------------------------
    def test_duplicate_values(self):
        """Verify sorting when multiple records have identical key values."""
        dup1 = ImageRecord(image_name="A.jpg", land_type="Forest", file_size=100)
        dup2 = ImageRecord(image_name="B.jpg", land_type="Forest", file_size=100)
        dup3 = ImageRecord(image_name="C.jpg", land_type="Water", file_size=300)
        dup4 = ImageRecord(image_name="D.jpg", land_type="Agriculture", file_size=200)
        dup_list = [dup1, dup3, dup2, dup4]

        for name, sort_fn in SORTING_ALGORITHMS:
            with self.subTest(algorithm=name):
                result, _ = sort_fn(dup_list, key="land_type", ascending=True)
                land_types = [r.land_type.lower() for r in result]
                self.assertEqual(land_types, ["agriculture", "forest", "forest", "water"])

                # File size with duplicates
                result_size, _ = sort_fn(dup_list, key="file_size", ascending=True)
                sizes = [r.file_size for r in result_size]
                self.assertEqual(sizes, [100, 100, 200, 300])

    # ------------------------------------------------------------------
    # 6. Sorting by Image Format
    # ------------------------------------------------------------------
    def test_sort_by_format(self):
        """Verify sorting by image format (e.g. jpeg, jpg, png, tiff)."""
        expected_formats = ["jpeg", "jpg", "png", "png", "tiff"]
        for name, sort_fn in SORTING_ALGORITHMS:
            with self.subTest(algorithm=name):
                result, _ = sort_fn(self.records, key="image_format", ascending=True)
                actual_formats = [r.image_format.lower() for r in result]
                self.assertEqual(actual_formats, expected_formats)

    # ------------------------------------------------------------------
    # 7. Sorting by Land Type
    # ------------------------------------------------------------------
    def test_sort_by_land_type(self):
        """Verify sorting by land classification type."""
        expected_lands = ["agriculture", "barren_land", "forest", "urban", "water"]
        for name, sort_fn in SORTING_ALGORITHMS:
            with self.subTest(algorithm=name):
                result, _ = sort_fn(self.records, key="land type", ascending=True)
                actual_lands = [r.land_type.lower() for r in result]
                self.assertEqual(actual_lands, expected_lands)

    # ------------------------------------------------------------------
    # 8. Sorting by File Size
    # ------------------------------------------------------------------
    def test_sort_by_file_size(self):
        """Verify sorting by file size in bytes."""
        expected_sizes_asc = [102400, 204800, 307200, 409600, 512000]
        expected_sizes_desc = [512000, 409600, 307200, 204800, 102400]

        for name, sort_fn in SORTING_ALGORITHMS:
            with self.subTest(algorithm=name):
                # Ascending
                result_asc, _ = sort_fn(self.records, key="file_size", ascending=True)
                self.assertEqual([r.file_size for r in result_asc], expected_sizes_asc)

                # Descending
                result_desc, _ = sort_fn(self.records, key="size", ascending=False)
                self.assertEqual([r.file_size for r in result_desc], expected_sizes_desc)

    # ------------------------------------------------------------------
    # 9. Sorting by Image Name
    # ------------------------------------------------------------------
    def test_sort_by_image_name(self):
        """Verify sorting by image filename."""
        expected_names = [
            "2026-01-10_06-00_Agriculture.jpeg",
            "2026-01-15_09-30_Water.jpg",
            "2026-02-20_18-45_Urban.tiff",
            "2026-03-01_12-00_Forest.png",
            "2026-04-05_15-15_Barren_Land.png",
        ]
        for name, sort_fn in SORTING_ALGORITHMS:
            with self.subTest(algorithm=name):
                result, _ = sort_fn(self.records, key="image_name", ascending=True)
                self.assertEqual([r.image_name for r in result], expected_names)

    # ------------------------------------------------------------------
    # 10. Original List Immutability / Preservation
    # ------------------------------------------------------------------
    def test_original_list_not_corrupted(self):
        """Verify that sorting operations never mutate the caller's input list."""
        for name, sort_fn in SORTING_ALGORITHMS:
            with self.subTest(algorithm=name):
                original_order = [r.image_name for r in self.records]
                shallow_copy_records = list(self.records)

                # Execute sort
                result, _ = sort_fn(shallow_copy_records, key="file_size", ascending=True)

                # Original list order must remain unchanged
                current_order = [r.image_name for r in shallow_copy_records]
                self.assertEqual(current_order, original_order, f"{name} modified the input list in-place!")
                self.assertIsNot(result, shallow_copy_records, f"{name} returned the same list instance instead of a sorted copy.")

    # ------------------------------------------------------------------
    # 11. Custom Callable Key Support
    # ------------------------------------------------------------------
    def test_custom_callable_key(self):
        """Verify sorting with a custom key extractor callable."""
        for name, sort_fn in SORTING_ALGORITHMS:
            with self.subTest(algorithm=name):
                # Sort by reverse length of image name
                result, _ = sort_fn(self.records, key=lambda r: len(r.image_name), ascending=True)
                lengths = [len(r.image_name) for r in result]
                # Verify non-decreasing order of lengths
                for i in range(len(lengths) - 1):
                    self.assertLessEqual(lengths[i], lengths[i + 1])

    # ------------------------------------------------------------------
    # 12. Key Extractor Helper
    # ------------------------------------------------------------------
    def test_key_extractor_helper(self):
        """Test get_record_key error handling and alias resolution."""
        rec = ImageRecord(
            datetime="2026-01-01 10:00",
            image_format="PNG",
            land_type="Forest",
            file_size=5000,
            image_name="test.png",
        )
        self.assertEqual(get_record_key(rec, "datetime"), "2026-01-01 10:00")
        self.assertEqual(get_record_key(rec, "format"), "png")
        self.assertEqual(get_record_key(rec, "land type"), "forest")
        self.assertEqual(get_record_key(rec, "file size"), 5000)
        self.assertEqual(get_record_key(rec, "name"), "test.png")

        # Invalid key type and name
        with self.assertRaises(TypeError):
            get_record_key(rec, 12345)
        with self.assertRaises(ValueError):
            get_record_key(rec, "invalid_nonexistent_field")


if __name__ == "__main__":
    unittest.main(verbosity=2)
