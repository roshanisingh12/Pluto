"""
tests/test_export_and_organizer.py

Unit tests for Phase 10 CSV Export and Filesystem Image Organization:
- Metadata CSV export with all 10 required columns
- Safe physical folder organization by Land Type (Forest, Water, Agriculture, Urban, Barren_Land, Other)
- Preservation of original uploaded files
- Duplicate filename collision resolution
"""

import os
import csv
import io
import shutil
import tempfile
import unittest
from PIL import Image

from models.image_record import ImageRecord
from services.organizer import (
    generate_metadata_csv,
    organize_images_by_land_type,
    CSV_COLUMNS,
    ORGANIZED_CATEGORIES,
)


class TestExportAndOrganizer(unittest.TestCase):
    """Test suite for CSV export and physical folder organization."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.src_dir = os.path.join(self.temp_dir, "sources")
        self.org_dir = os.path.join(self.temp_dir, "Organized")
        os.makedirs(self.src_dir, exist_ok=True)

        # Create physical dummy image files
        self.file1 = os.path.join(self.src_dir, "2026-01-15_10-30_Forest.jpg")
        self.file2 = os.path.join(self.src_dir, "2026-02-20_14-45_Water.png")
        self.file3 = os.path.join(self.src_dir, "2025-12-05_09-20_Urban.tiff")
        self.file4 = os.path.join(self.src_dir, "2026-03-10_16-15_Agriculture.jpeg")
        self.file5 = os.path.join(self.src_dir, "2026-03-12_11-20_Barren_Land.webp")

        for fpath in [self.file1, self.file2, self.file3, self.file4, self.file5]:
            img = Image.new("RGB", (100, 100), color=(10, 20, 30))
            img.save(fpath)

        self.records = [
            ImageRecord(
                image_id="SAT001",
                image_name="2026-01-15_10-30_Forest.jpg",
                file_path=self.file1,
                date="2026-01-15",
                time="10-30",
                datetime="2026-01-15 10:30",
                land_type="Forest",
                image_format="jpg",
                width=100,
                height=100,
                file_size=1500,
            ),
            ImageRecord(
                image_id="SAT002",
                image_name="2026-02-20_14-45_Water.png",
                file_path=self.file2,
                date="2026-02-20",
                time="14-45",
                datetime="2026-02-20 14:45",
                land_type="Water",
                image_format="png",
                width=100,
                height=100,
                file_size=2500,
            ),
            ImageRecord(
                image_id="SAT003",
                image_name="2025-12-05_09-20_Urban.tiff",
                file_path=self.file3,
                date="2025-12-05",
                time="09-20",
                datetime="2025-12-05 09:20",
                land_type="Urban",
                image_format="tiff",
                width=100,
                height=100,
                file_size=3500,
            ),
            ImageRecord(
                image_id="SAT004",
                image_name="2026-03-10_16-15_Agriculture.jpeg",
                file_path=self.file4,
                date="2026-03-10",
                time="16-15",
                datetime="2026-03-10 16:15",
                land_type="Agriculture",
                image_format="jpeg",
                width=100,
                height=100,
                file_size=1800,
            ),
            ImageRecord(
                image_id="SAT005",
                image_name="2026-03-12_11-20_Barren_Land.webp",
                file_path=self.file5,
                date="2026-03-12",
                time="11-20",
                datetime="2026-03-12 11:20",
                land_type="Barren_Land",
                image_format="webp",
                width=100,
                height=100,
                file_size=2200,
            ),
        ]

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    # ------------------------------------------------------------------
    # 1. CSV Export Verification
    # ------------------------------------------------------------------
    def test_generate_metadata_csv(self):
        """Verify CSV contains all 10 required headers and proper row values."""
        csv_text = generate_metadata_csv(self.records)
        reader = list(csv.reader(io.StringIO(csv_text)))

        # Header check
        self.assertEqual(len(reader), 6)  # 1 header + 5 rows
        expected_header = [
            "Image ID",
            "Image Name",
            "Date",
            "Time",
            "Land Type",
            "Format",
            "Width",
            "Height",
            "File Size",
            "File Path",
        ]
        self.assertEqual(reader[0], expected_header)

        # Row 1 check
        row1 = reader[1]
        self.assertEqual(row1[0], "SAT001")
        self.assertEqual(row1[1], "2026-01-15_10-30_Forest.jpg")
        self.assertEqual(row1[2], "2026-01-15")
        self.assertEqual(row1[3], "10-30")
        self.assertEqual(row1[4], "Forest")
        self.assertEqual(row1[5], "JPG")
        self.assertEqual(row1[6], "100")
        self.assertEqual(row1[7], "100")
        self.assertEqual(row1[8], "1500")
        self.assertEqual(row1[9], self.file1)

    def test_generate_empty_csv(self):
        """Verify CSV generation on empty records list."""
        csv_text = generate_metadata_csv([])
        reader = list(csv.reader(io.StringIO(csv_text)))
        self.assertEqual(len(reader), 1)
        self.assertEqual(reader[0], CSV_COLUMNS)

    # ------------------------------------------------------------------
    # 2. Filesystem Organization by Land Type
    # ------------------------------------------------------------------
    def test_organize_images_by_land_type(self):
        """Verify images are safely copied into Land Type subfolders."""
        summary = organize_images_by_land_type(self.records, output_root=self.org_dir)

        self.assertTrue(summary["success"])
        self.assertEqual(summary["total_copied"], 5)

        # Verify all category folders exist
        for cat in ORGANIZED_CATEGORIES:
            cat_path = os.path.join(self.org_dir, cat)
            self.assertTrue(os.path.isdir(cat_path), f"Missing category directory {cat}")

        # Verify file locations
        self.assertTrue(os.path.exists(os.path.join(self.org_dir, "Forest", "2026-01-15_10-30_Forest.jpg")))
        self.assertTrue(os.path.exists(os.path.join(self.org_dir, "Water", "2026-02-20_14-45_Water.png")))
        self.assertTrue(os.path.exists(os.path.join(self.org_dir, "Urban", "2025-12-05_09-20_Urban.tiff")))
        self.assertTrue(os.path.exists(os.path.join(self.org_dir, "Agriculture", "2026-03-10_16-15_Agriculture.jpeg")))
        self.assertTrue(os.path.exists(os.path.join(self.org_dir, "Barren_Land", "2026-03-12_11-20_Barren_Land.webp")))

        # CRITICAL: Verify original source images are untouched
        for fpath in [self.file1, self.file2, self.file3, self.file4, self.file5]:
            self.assertTrue(os.path.exists(fpath), f"Original file was modified or deleted: {fpath}")

    # ------------------------------------------------------------------
    # 3. Duplicate Filename Collision Handling
    # ------------------------------------------------------------------
    def test_duplicate_filename_handling(self):
        """Verify that files with identical names are copied without collision or data loss."""
        # Create second file with identical name in a subfolder
        sub_src = os.path.join(self.temp_dir, "sub_sources")
        os.makedirs(sub_src, exist_ok=True)
        dup_file = os.path.join(sub_src, "2026-01-15_10-30_Forest.jpg")
        img = Image.new("RGB", (50, 50), color=(255, 0, 0))
        img.save(dup_file)

        dup_record = ImageRecord(
            image_id="SAT006",
            image_name="2026-01-15_10-30_Forest.jpg",
            file_path=dup_file,
            land_type="Forest",
        )

        test_records = [self.records[0], dup_record]
        summary = organize_images_by_land_type(test_records, output_root=self.org_dir)

        self.assertEqual(summary["total_copied"], 2)
        forest_dir = os.path.join(self.org_dir, "Forest")
        files_in_forest = os.listdir(forest_dir)
        self.assertEqual(len(files_in_forest), 2)
        # Should have original name and safe suffix name
        self.assertIn("2026-01-15_10-30_Forest.jpg", files_in_forest)
        self.assertTrue(any("SAT006" in f for f in files_in_forest))


if __name__ == "__main__":
    unittest.main(verbosity=2)
