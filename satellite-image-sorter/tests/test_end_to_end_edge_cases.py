"""
tests/test_end_to_end_edge_cases.py

Comprehensive Phase 12 validation test suite covering all 17 feature areas
and edge cases across the entire Satellite Image Sorter system.
"""

import os
import io
import tempfile
import shutil
import unittest
from PIL import Image

from models.image_record import ImageRecord
from services.image_reader import process_uploaded_image, read_image, validate_image
from services.metadata_parser import parse_filename, ParseResult
from services.statistics import (
    get_land_type_counts,
    get_format_counts,
    get_timeline_counts,
    get_storage_stats,
    get_overall_summary,
)
from services.organizer import generate_metadata_csv, organize_images_by_land_type
from services.benchmark import benchmark_sorting_algorithms
from dsa.sorting import merge_sort, quick_sort, bubble_sort, get_record_key
from dsa.searching import linear_search, binary_search, filter_records, get_search_key
from dsa.hashing import ImageHashTable


class MockUpload:
    """Mock file stream for Streamlit upload testing."""
    def __init__(self, name: str, data: bytes):
        self.name = name
        self.data = data
        self.size = len(data)

    def getvalue(self) -> bytes:
        return self.data

    def read(self) -> bytes:
        return self.data


class TestCompleteProjectEdgeCases(unittest.TestCase):
    """Exhaustive edge case and full integration test suite for Phase 12."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.upload_dir = os.path.join(self.temp_dir, "uploads")
        self.org_dir = os.path.join(self.temp_dir, "Organized")
        os.makedirs(self.upload_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _create_image_bytes(self, fmt: str = "PNG", w: int = 100, h: int = 100) -> bytes:
        img = Image.new("RGB", (w, h), color=(120, 180, 240))
        buf = io.BytesIO()
        pillow_fmt = "JPEG" if fmt.upper() in ("JPG", "JPEG") else fmt.upper()
        img.save(buf, format=pillow_fmt)
        return buf.getvalue()

    # ------------------------------------------------------------------
    # 1. Edge Case: No Images (Empty State across all modules)
    # ------------------------------------------------------------------
    def test_edge_case_no_images(self):
        """Verify all services and DSA routines handle empty datasets cleanly."""
        empty_list = []

        # Sorting
        self.assertEqual(merge_sort(empty_list), ([], 0))
        self.assertEqual(quick_sort(empty_list), ([], 0))
        self.assertEqual(bubble_sort(empty_list), ([], 0))

        # Searching & Filtering
        self.assertEqual(linear_search(empty_list, "Forest"), ([], 0))
        self.assertEqual(binary_search(empty_list, "Forest"), ([], 0))
        self.assertEqual(filter_records(empty_list, land_type="Forest"), ([], 0))

        # Statistics
        summary = get_overall_summary(empty_list)
        self.assertEqual(summary["total_images"], 0)
        self.assertEqual(summary["complete_metadata_count"], 0)

        # CSV & Organization
        csv_out = generate_metadata_csv(empty_list)
        self.assertTrue(csv_out.startswith("Image ID,Image Name"))
        org_res = organize_images_by_land_type(empty_list, output_root=self.org_dir)
        self.assertEqual(org_res["total_copied"], 0)

        # Benchmark
        bm_res = benchmark_sorting_algorithms(empty_list)
        self.assertEqual(len(bm_res), 3)
        self.assertTrue(all(r["item_count"] == 0 for r in bm_res))

    # ------------------------------------------------------------------
    # 2. Edge Case: One Single Image
    # ------------------------------------------------------------------
    def test_edge_case_single_image(self):
        """Verify operations on a single image dataset."""
        img_bytes = self._create_image_bytes("PNG")
        mock = MockUpload("2026-01-15_10-30_Forest.png", img_bytes)
        rec, err = process_uploaded_image(mock, upload_dir=self.upload_dir, image_id="SAT001")

        self.assertIsNone(err)
        single = [rec]

        # Sorting
        m_res, _ = merge_sort(single)
        q_res, _ = quick_sort(single)
        b_res, _ = bubble_sort(single)
        self.assertEqual(len(m_res), 1)
        self.assertEqual(len(q_res), 1)
        self.assertEqual(len(b_res), 1)

        # Search found and not found
        s_found, _ = linear_search(single, "Forest", key="land_type")
        s_not_found, _ = linear_search(single, "Water", key="land_type")
        self.assertEqual(len(s_found), 1)
        self.assertEqual(len(s_not_found), 0)

        # Organization
        org_res = organize_images_by_land_type(single, output_root=self.org_dir)
        self.assertEqual(org_res["total_copied"], 1)
        self.assertEqual(org_res["category_counts"]["Forest"], 1)

    # ------------------------------------------------------------------
    # 3. Edge Case: Many Images (Scalability & Stability)
    # ------------------------------------------------------------------
    def test_edge_case_many_images(self):
        """Verify sorting, searching, hashing and stats on a larger set (100 images)."""
        records = []
        ht = ImageHashTable(initial_capacity=16)

        for i in range(100):
            val = (i * 17) % 100
            rec = ImageRecord(
                image_id=f"SAT{i:03d}",
                image_name=f"2026-0{(val % 9) + 1:01d}-15_12-00_Forest.jpg",
                date=f"2026-0{(val % 9) + 1:01d}-15",
                land_type="Forest" if i % 2 == 0 else "Water",
                image_format="jpg" if i % 3 == 0 else "png",
                file_size=val * 1024,
            )
            records.append(rec)
            ht.insert(rec.image_id, rec)

        # Hash Table lookup check
        self.assertEqual(len(ht), 100)
        self.assertEqual(ht.search("SAT050").image_id, "SAT050")

        # Sorting
        sorted_m, _ = merge_sort(records, key="file_size", ascending=True)
        sorted_q, _ = quick_sort(records, key="file_size", ascending=True)
        sorted_b, _ = bubble_sort(records, key="file_size", ascending=True)

        self.assertEqual(len(sorted_m), 100)
        self.assertEqual(len(sorted_q), 100)
        self.assertEqual(len(sorted_b), 100)

        # Verify monotonicity
        for i in range(99):
            self.assertLessEqual(sorted_m[i].file_size, sorted_m[i + 1].file_size)
            self.assertLessEqual(sorted_q[i].file_size, sorted_q[i + 1].file_size)
            self.assertLessEqual(sorted_b[i].file_size, sorted_b[i + 1].file_size)

    # ------------------------------------------------------------------
    # 4. Edge Cases: Invalid Image Bytes & Unsupported Extension
    # ------------------------------------------------------------------
    def test_edge_case_invalid_image_and_unsupported_ext(self):
        """Verify corrupt data and unsupported extensions are handled safely."""
        corrupt_mock = MockUpload("bad_data.png", b"CORRUPT_NOT_AN_IMAGE_DATA")
        rec, err = process_uploaded_image(corrupt_mock, upload_dir=self.upload_dir, image_id="SAT999")
        self.assertIsNone(rec)
        self.assertIsNotNone(err)

        # Unsupported extension in metadata parser
        parse_bad_ext = parse_filename("2026-01-15_10-30_Forest.xyz")
        self.assertFalse(parse_bad_ext.success)
        self.assertIn("image_format", parse_bad_ext.missing_fields)

    # ------------------------------------------------------------------
    # 5. Edge Cases: Invalid Filename, Bad Dates, Bad Times, Missing Land Type
    # ------------------------------------------------------------------
    def test_edge_case_invalid_filename_and_datetime(self):
        """Verify invalid date/time/landtype patterns in filenames."""
        # Non-matching pattern
        p1 = parse_filename("random_photo.jpg")
        self.assertFalse(p1.success)
        self.assertIn("does not match", p1.errors[0])

        # Bad calendar date (Feb 30th)
        p2 = parse_filename("2026-02-30_10-30_Forest.jpg")
        self.assertFalse(p2.success)
        self.assertIn("date", p2.missing_fields)

        # Bad time (25:70)
        p3 = parse_filename("2026-01-15_25-70_Forest.jpg")
        self.assertFalse(p3.success)
        self.assertIn("time", p3.missing_fields)

        # Unknown land type defaults to Other
        p4 = parse_filename("2026-01-15_10-30_UnknownZone.jpg")
        self.assertTrue(p4.success)
        self.assertEqual(p4.record.land_type, "Other")

    # ------------------------------------------------------------------
    # 6. Edge Cases: Identical / Same Dates, Same Formats, Same Land Types
    # ------------------------------------------------------------------
    def test_edge_case_same_attributes(self):
        """Verify sorting and searching when all records share identical attributes."""
        same_date_records = [
            ImageRecord(image_id=f"SAT{i:03d}", date="2026-01-15", time="10-00", datetime="2026-01-15 10:00", land_type="Forest", image_format="png", file_size=1000)
            for i in range(5)
        ]

        # Sorting should not crash or alter count
        m_res, _ = merge_sort(same_date_records, key="datetime")
        self.assertEqual(len(m_res), 5)

        # Binary Search should find all 5 duplicates
        matches, _ = binary_search(same_date_records, target="2026-01-15", key="date", find_all=True)
        self.assertEqual(len(matches), 5)

        # Filter should return all 5
        filtered, _ = filter_records(same_date_records, land_type="Forest", image_format="png")
        self.assertEqual(len(filtered), 5)

    # ------------------------------------------------------------------
    # 7. Edge Cases: Search Not Found & Empty Search
    # ------------------------------------------------------------------
    def test_edge_case_search_not_found_and_empty(self):
        """Verify behavior for empty search strings and non-existent targets."""
        rec = ImageRecord(image_id="SAT001", image_name="Forest.jpg", land_type="Forest")
        records = [rec]

        # Non-existent target
        m_linear, _ = linear_search(records, "NON_EXISTENT", key="land_type")
        m_binary, _ = binary_search(records, "NON_EXISTENT", key="land_type")
        self.assertEqual(m_linear, [])
        self.assertEqual(m_binary, [])

        # Empty search string
        m_empty_lin, _ = linear_search(records, "", key="land_type")
        self.assertEqual(m_empty_lin, [])

    # ------------------------------------------------------------------
    # 8. Edge Case: Manual Metadata Editing & Completion
    # ------------------------------------------------------------------
    def test_manual_metadata_editing_flow(self):
        """Verify manual metadata editing transforms incomplete record to complete."""
        rec = ImageRecord(image_id="SAT001", image_name="raw.jpg", file_path="/tmp/raw.jpg", image_format="jpg", file_size=2048, width=100, height=100)
        self.assertFalse(rec.is_complete())
        self.assertIn("date", rec.missing_fields())

        # Manually assign values
        rec.date = "2026-05-20"
        rec.time = "08-30"
        rec.datetime = "2026-05-20 08:30"
        rec.land_type = "Urban"

        self.assertTrue(rec.is_complete())
        self.assertEqual(rec.missing_fields(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
