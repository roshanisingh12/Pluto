"""
tests/test_statistics.py

Unit tests for services/statistics.py:
- Land type counts calculation
- Format counts calculation
- Timeline aggregation
- Storage size statistics
- Empty state handling
"""

import unittest
from models.image_record import ImageRecord
from services.statistics import (
    get_land_type_counts,
    get_format_counts,
    get_timeline_counts,
    get_storage_stats,
    get_overall_summary,
)


class TestStatisticsService(unittest.TestCase):
    """Test suite for statistics calculation functions."""

    def setUp(self):
        self.records = [
            ImageRecord(
                image_id="SAT001",
                land_type="Forest",
                image_format="jpg",
                date="2026-01-15",
                file_size=200000,
            ),
            ImageRecord(
                image_id="SAT002",
                land_type="Forest",
                image_format="png",
                date="2026-01-15",
                file_size=300000,
            ),
            ImageRecord(
                image_id="SAT003",
                land_type="Water",
                image_format="jpeg",
                date="2026-02-20",
                file_size=150000,
            ),
            ImageRecord(
                image_id="SAT004",
                land_type="Urban",
                image_format="tiff",
                date="2026-03-01",
                file_size=500000,
            ),
            ImageRecord(
                image_id="SAT005",
                land_type="Barren_Land",
                image_format="webp",
                date="2026-03-12",
                file_size=250000,
            ),
        ]

    def test_land_type_counts(self):
        """Verify frequency calculation of land classifications."""
        counts = get_land_type_counts(self.records)
        self.assertEqual(counts["Forest"], 2)
        self.assertEqual(counts["Water"], 1)
        self.assertEqual(counts["Urban"], 1)
        self.assertEqual(counts["Barren_Land"], 1)
        self.assertEqual(counts["Agriculture"], 0)
        self.assertEqual(counts["Other"], 0)

    def test_format_counts(self):
        """Verify frequency calculation of image formats."""
        counts = get_format_counts(self.records)
        self.assertEqual(counts["JPG"], 1)
        self.assertEqual(counts["PNG"], 1)
        self.assertEqual(counts["JPEG"], 1)
        self.assertEqual(counts["TIFF"], 1)
        self.assertEqual(counts["WEBP"], 1)

    def test_timeline_counts(self):
        """Verify chronological grouping of dates."""
        timeline = get_timeline_counts(self.records)
        self.assertEqual(timeline["2026-01-15"], 2)
        self.assertEqual(timeline["2026-02-20"], 1)
        self.assertEqual(timeline["2026-03-01"], 1)
        self.assertEqual(timeline["2026-03-12"], 1)
        # Ensure chronological ordering of keys
        keys = list(timeline.keys())
        self.assertEqual(keys, sorted(keys))

    def test_storage_stats(self):
        """Verify storage calculations."""
        stats = get_storage_stats(self.records)
        self.assertEqual(stats["total_bytes"], 1400000)
        self.assertEqual(stats["count_with_size"], 5)
        self.assertEqual(stats["min_bytes"], 150000)
        self.assertEqual(stats["max_bytes"], 500000)
        self.assertEqual(stats["avg_bytes"], 280000)

    def test_empty_records(self):
        """Verify behavior on empty catalog list."""
        self.assertEqual(get_land_type_counts([]), {"Forest": 0, "Water": 0, "Agriculture": 0, "Urban": 0, "Barren_Land": 0, "Other": 0})
        self.assertEqual(get_format_counts([]), {"JPG": 0, "JPEG": 0, "PNG": 0, "TIFF": 0, "WEBP": 0})
        self.assertEqual(get_timeline_counts([]), {})
        stats = get_storage_stats([])
        self.assertEqual(stats["total_bytes"], 0)
        summary = get_overall_summary([])
        self.assertEqual(summary["total_images"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
