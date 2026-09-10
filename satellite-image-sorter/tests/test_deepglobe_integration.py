"""
tests/test_deepglobe_integration.py

Integration tests for the real DeepGlobe satellite dataset:
- Verifies loading from sample_images/ with metadata.csv
- Checks 5 classes (Forest, Water, Agriculture, Urban, Barren)
- Verifies DSA sorting, searching, and filtering on the 100 real images
"""

import os
import unittest
from pathlib import Path
import csv

from models.image_record import ImageRecord
from services.image_reader import read_image
from services.statistics import get_overall_summary, get_land_type_counts
from dsa.sorting import merge_sort, quick_sort, bubble_sort
from dsa.searching import linear_search, binary_search, filter_records
from services.organizer import generate_metadata_csv

class TestDeepGlobeIntegration(unittest.TestCase):
    """Test suite verifying end-to-end DeepGlobe dataset integration."""

    @classmethod
    def setUpClass(cls):
        cls.base_dir = Path(__file__).resolve().parent.parent
        cls.sample_dir = cls.base_dir / "sample_images"
        cls.metadata_file = cls.sample_dir / "metadata.csv"
        cls.classes = ["Forest", "Water", "Agriculture", "Urban", "Barren"]

    def test_metadata_file_exists_and_valid(self):
        """Ensure sample_images/metadata.csv exists with 100 authentic rows."""
        self.assertTrue(self.metadata_file.exists(), "metadata.csv must exist in sample_images/")
        with open(self.metadata_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 100, "Must have exactly 100 curated sample rows.")
            
            # Check class distribution
            class_counts = {}
            for r in rows:
                c = r["land_type"]
                class_counts[c] = class_counts.get(c, 0) + 1
            
            for c in self.classes:
                self.assertEqual(class_counts.get(c), 20, f"Class {c} must have 20 images in metadata.csv")

    def test_sample_image_files_exist_and_readable(self):
        """Ensure all 20 image files per class exist on disk and have valid dimensions."""
        records = []
        for c in self.classes:
            folder = self.sample_dir / c
            self.assertTrue(folder.is_dir(), f"Folder for class {c} must exist.")
            img_files = list(folder.glob("*.jpg"))
            self.assertEqual(len(img_files), 20, f"Folder {c} must contain exactly 20 jpg files.")
            
            for img_p in img_files:
                rec = ImageRecord(
                    image_id=img_p.stem.replace("_sat", ""),
                    image_name=img_p.name,
                    file_path=str(img_p),
                    land_type=c,
                )
                res = read_image(str(img_p), record=rec)
                self.assertTrue(res.success, f"Failed to read image {img_p}")
                self.assertEqual(rec.width, 2448, "DeepGlobe images must be 2448 px wide.")
                self.assertEqual(rec.height, 2448, "DeepGlobe images must be 2448 px high.")
                self.assertIn(rec.image_format, ["jpg", "jpeg"])
                self.assertGreater(rec.file_size, 100000, "File size must be positive and non-trivial.")
                records.append(rec)

        self.assertEqual(len(records), 100, "Total loaded records must be 100.")

        # Test DSA Sorting across all 100 records
        sorted_merge, comps_m = merge_sort(records, key="image_name")
        self.assertEqual(len(sorted_merge), 100)
        self.assertTrue(sorted_merge[0].image_name <= sorted_merge[-1].image_name)

        sorted_quick, comps_q = quick_sort(records, key="file_size")
        self.assertEqual(len(sorted_quick), 100)
        self.assertTrue(sorted_quick[0].file_size <= sorted_quick[-1].file_size)

        sorted_bubble, comps_b = bubble_sort(records[:20], key="image_id")
        self.assertEqual(len(sorted_bubble), 20)

        # Test DSA Searching
        matches, comps = linear_search(records, target="Forest", key="land_type", find_all=True)
        self.assertEqual(len(matches), 20)

        # Test DSA Filtering
        f_water, _ = filter_records(records, land_type="Water")
        self.assertEqual(len(f_water), 20)

        f_urban, _ = filter_records(records, land_type="Urban")
        self.assertEqual(len(f_urban), 20)

        # Test Metadata CSV Generation
        csv_text = generate_metadata_csv(records)
        self.assertIn("711893", csv_text)
        self.assertIn("Forest", csv_text)
        self.assertIn("Water", csv_text)


if __name__ == "__main__":
    unittest.main()
