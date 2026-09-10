"""
tests/test_searching.py

Unit tests for manual DSA searching algorithms in dsa/searching.py:
- Linear Search
- Binary Search

Scenarios tested:
- Found item
- Item not found
- First item (index 0)
- Last item (index n - 1)
- Duplicate values (multiple matches)
- Empty list ([])
- Single item (found & not found)
- Search keys:
  - image ID
  - image name
  - land type
  - image format
  - date
- Binary Search sorted requirement verification
- Comparison count tracking
"""

import unittest
from models.image_record import ImageRecord
from dsa.searching import linear_search, binary_search, get_search_key
from dsa.sorting import merge_sort

SEARCHING_ALGORITHMS = [
    ("Linear Search", linear_search),
    ("Binary Search", binary_search),
]


class TestSearchingAlgorithms(unittest.TestCase):
    """Comprehensive test suite for manual DSA searching algorithms."""

    def setUp(self):
        """Create structured sample ImageRecord fixtures."""
        self.record1 = ImageRecord(
            image_id="id-001",
            image_name="2026-01-10_06-00_Agriculture.jpeg",
            date="2026-01-10",
            time="06-00",
            datetime="2026-01-10 06:00",
            image_format="jpeg",
            land_type="Agriculture",
            file_size=307200,
        )
        self.record2 = ImageRecord(
            image_id="id-002",
            image_name="2026-01-15_09-30_Water.jpg",
            date="2026-01-15",
            time="09-30",
            datetime="2026-01-15 09:30",
            image_format="jpg",
            land_type="Water",
            file_size=512000,
        )
        self.record3 = ImageRecord(
            image_id="id-003",
            image_name="2026-02-20_18-45_Urban.tiff",
            date="2026-02-20",
            time="18-45",
            datetime="2026-02-20 18:45",
            image_format="tiff",
            land_type="Urban",
            file_size=102400,
        )
        self.record4 = ImageRecord(
            image_id="id-004",
            image_name="2026-03-01_12-00_Forest.png",
            date="2026-03-01",
            time="12-00",
            datetime="2026-03-01 12:00",
            image_format="png",
            land_type="Forest",
            file_size=204800,
        )
        self.record5 = ImageRecord(
            image_id="id-005",
            image_name="2026-04-05_15-15_Forest.png",
            date="2026-04-05",
            time="15-15",
            datetime="2026-04-05 15:15",
            image_format="png",
            land_type="Forest",
            file_size=409600,
        )
        self.records = [self.record1, self.record2, self.record3, self.record4, self.record5]

    # ------------------------------------------------------------------
    # 1. Edge Case: Empty List
    # ------------------------------------------------------------------
    def test_empty_list(self):
        """Ensure search on an empty list returns empty results and 0 comparisons."""
        for name, search_fn in SEARCHING_ALGORITHMS:
            with self.subTest(algorithm=name):
                matches, comps = search_fn([], target="Forest", key="land_type")
                self.assertEqual(matches, [])
                self.assertEqual(comps, 0)

    # ------------------------------------------------------------------
    # 2. Edge Case: Single Item (Found & Not Found)
    # ------------------------------------------------------------------
    def test_single_item_found(self):
        """Ensure searching a 1-element list for an existing item succeeds."""
        for name, search_fn in SEARCHING_ALGORITHMS:
            with self.subTest(algorithm=name):
                matches, comps = search_fn([self.record1], target="jpeg", key="image_format")
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0].image_id, self.record1.image_id)
                self.assertGreater(comps, 0)

    def test_single_item_not_found(self):
        """Ensure searching a 1-element list for a non-existing item returns empty."""
        for name, search_fn in SEARCHING_ALGORITHMS:
            with self.subTest(algorithm=name):
                matches, comps = search_fn([self.record1], target="png", key="image_format")
                self.assertEqual(matches, [])
                self.assertGreater(comps, 0)

    # ------------------------------------------------------------------
    # 3. Found Item & Item Not Found
    # ------------------------------------------------------------------
    def test_found_item_and_not_found(self):
        """Verify successful search for an existing element and failure for nonexistent element."""
        for name, search_fn in SEARCHING_ALGORITHMS:
            with self.subTest(algorithm=name):
                # Found
                matches, comps = search_fn(self.records, target="Urban", key="land_type")
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0].image_id, "id-003")
                self.assertGreater(comps, 0)

                # Not found
                matches_nf, comps_nf = search_fn(self.records, target="NonExistentLand", key="land_type")
                self.assertEqual(matches_nf, [])
                self.assertGreater(comps_nf, 0)

    # ------------------------------------------------------------------
    # 4. First Item & Last Item Boundaries
    # ------------------------------------------------------------------
    def test_first_item_search(self):
        """Verify search finds the first item in the list."""
        for name, search_fn in SEARCHING_ALGORITHMS:
            with self.subTest(algorithm=name):
                # Search by image_id (id-001 is first in our fixture)
                matches, comps = search_fn(self.records, target="id-001", key="image_id")
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0].image_id, "id-001")
                self.assertGreater(comps, 0)

    def test_last_item_search(self):
        """Verify search finds the last item in the list."""
        for name, search_fn in SEARCHING_ALGORITHMS:
            with self.subTest(algorithm=name):
                # Search by image_id (id-005 is last in our fixture)
                matches, comps = search_fn(self.records, target="id-005", key="image_id")
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0].image_id, "id-005")
                self.assertGreater(comps, 0)

    # ------------------------------------------------------------------
    # 5. Duplicate Values (Multiple Matching Records)
    # ------------------------------------------------------------------
    def test_duplicate_values(self):
        """Verify returning all matching records when duplicate keys exist."""
        # record4 and record5 both have land_type="Forest"
        for name, search_fn in SEARCHING_ALGORITHMS:
            with self.subTest(algorithm=name):
                matches, comps = search_fn(self.records, target="forest", key="land_type", find_all=True)
                self.assertEqual(len(matches), 2)
                matched_ids = {m.image_id for m in matches}
                self.assertEqual(matched_ids, {"id-004", "id-005"})

    # ------------------------------------------------------------------
    # 6. Searching by Specific Keys
    # ------------------------------------------------------------------
    def test_search_by_image_id(self):
        """Search by Image ID."""
        for name, search_fn in SEARCHING_ALGORITHMS:
            with self.subTest(algorithm=name):
                matches, _ = search_fn(self.records, target="id-002", key="image_id")
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0].image_name, "2026-01-15_09-30_Water.jpg")

    def test_search_by_image_name(self):
        """Search by Image Name."""
        target_name = "2026-02-20_18-45_Urban.tiff"
        for name, search_fn in SEARCHING_ALGORITHMS:
            with self.subTest(algorithm=name):
                matches, _ = search_fn(self.records, target=target_name, key="image_name")
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0].land_type, "Urban")

    def test_search_by_land_type(self):
        """Search by Land Type."""
        for name, search_fn in SEARCHING_ALGORITHMS:
            with self.subTest(algorithm=name):
                matches, _ = search_fn(self.records, target="Water", key="land_type")
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0].image_id, "id-002")

    def test_search_by_image_format(self):
        """Search by Image Format."""
        for name, search_fn in SEARCHING_ALGORITHMS:
            with self.subTest(algorithm=name):
                matches, _ = search_fn(self.records, target="png", key="image_format")
                self.assertEqual(len(matches), 2)
                self.assertTrue(all(m.image_format == "png" for m in matches))

    def test_search_by_date(self):
        """Search by Date (YYYY-MM-DD)."""
        for name, search_fn in SEARCHING_ALGORITHMS:
            with self.subTest(algorithm=name):
                matches, _ = search_fn(self.records, target="2026-01-10", key="date")
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0].image_id, "id-001")

    # ------------------------------------------------------------------
    # 7. Binary Search Sorted Pre-requisite Verification
    # ------------------------------------------------------------------
    def test_binary_search_with_presorted_data(self):
        """Verify Binary Search when is_sorted=True is explicitly provided on pre-sorted list."""
        sorted_records, _ = merge_sort(self.records, key="date", ascending=True)
        matches, comps = binary_search(sorted_records, target="2026-03-01", key="date", is_sorted=True)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].image_id, "id-004")
        self.assertGreater(comps, 0)

    # ------------------------------------------------------------------
    # 8. Key Extractor & Validation
    # ------------------------------------------------------------------
    def test_key_validation(self):
        """Verify key extraction errors on invalid key."""
        with self.assertRaises(ValueError):
            get_search_key(self.record1, "non_existent_key")
        with self.assertRaises(TypeError):
            get_search_key(self.record1, 999)

    # ------------------------------------------------------------------
    # 9. Multi-Criteria Filtering
    # ------------------------------------------------------------------
    def test_multi_criteria_filtering(self):
        """Verify combined multi-criteria manual filtering."""
        from dsa.searching import filter_records

        # Filter by Land Type + Format + Date Range
        # Forest + PNG + between 2026-02-01 and 2026-03-31 -> should only match id-004
        results, comps = filter_records(
            self.records,
            land_type="Forest",
            image_format="png",
            start_date="2026-02-01",
            end_date="2026-03-31",
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].image_id, "id-004")
        self.assertGreater(comps, 0)

        # Filter All matching
        res_all, _ = filter_records(self.records, land_type="All", image_format="All")
        self.assertEqual(len(res_all), len(self.records))


if __name__ == "__main__":
    unittest.main(verbosity=2)


