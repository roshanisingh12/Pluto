"""
tests/test_metadata_parser.py

Unit tests for services/metadata_parser.py.

Covers:
- Valid filenames (all supported land types and formats)
- Invalid filenames (wrong pattern, bad date, bad time, unknown format)
- Edge-cases: Barren_Land vs Barren Land, case-insensitivity, extra spaces
"""

import sys
import os
import unittest

# Allow imports from the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.metadata_parser import parse_filename, ParseResult


# ═══════════════════════════════════════════════════════════════════════════ #
# Helper                                                                       #
# ═══════════════════════════════════════════════════════════════════════════ #

def _parse(filename: str) -> ParseResult:
    return parse_filename(filename)


# ═══════════════════════════════════════════════════════════════════════════ #
# 1. Valid filenames                                                           #
# ═══════════════════════════════════════════════════════════════════════════ #

class TestValidFilenames(unittest.TestCase):

    # ---------- basic land types ---------- #

    def test_forest_jpg(self):
        r = _parse("2026-01-15_10-30_Forest.jpg")
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.record.date, "2026-01-15")
        self.assertEqual(r.record.time, "10-30")
        self.assertEqual(r.record.datetime, "2026-01-15 10:30")
        self.assertEqual(r.record.land_type, "Forest")
        self.assertEqual(r.record.image_format, "jpg")
        self.assertEqual(r.record.image_name, "2026-01-15_10-30_Forest.jpg")

    def test_water_png(self):
        r = _parse("2026-02-20_14-45_Water.png")
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.record.land_type, "Water")
        self.assertEqual(r.record.image_format, "png")
        self.assertEqual(r.record.date, "2026-02-20")
        self.assertEqual(r.record.time, "14-45")

    def test_urban_tiff(self):
        r = _parse("2025-12-05_09-20_Urban.tiff")
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.record.land_type, "Urban")
        self.assertEqual(r.record.image_format, "tiff")

    def test_agriculture_jpeg(self):
        r = _parse("2026-03-10_16-15_Agriculture.jpeg")
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.record.land_type, "Agriculture")
        self.assertEqual(r.record.image_format, "jpeg")

    def test_barren_land_underscore(self):
        r = _parse("2026-03-12_11-20_Barren_Land.jpg")
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.record.land_type, "Barren_Land")

    def test_other_land_type(self):
        r = _parse("2026-04-01_08-00_Other.jpg")
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.record.land_type, "Other")

    # ---------- datetime combination ---------- #

    def test_datetime_combined(self):
        r = _parse("2026-06-15_23-59_Forest.jpg")
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.record.datetime, "2026-06-15 23:59")

    # ---------- full path passthrough ---------- #

    def test_full_path(self):
        r = _parse(r"C:\images\2026-01-15_10-30_Urban.png")
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.record.date, "2026-01-15")
        self.assertEqual(r.record.image_format, "png")

    # ---------- different formats ---------- #

    def test_bmp_format(self):
        r = _parse("2026-05-20_08-00_Forest.bmp")
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.record.image_format, "bmp")

    def test_webp_format(self):
        r = _parse("2026-05-20_08-00_Water.webp")
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.record.image_format, "webp")

    def test_tif_format(self):
        r = _parse("2026-05-20_08-00_Urban.tif")
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.record.image_format, "tif")


# ═══════════════════════════════════════════════════════════════════════════ #
# 2. Invalid filenames – pattern mismatch                                     #
# ═══════════════════════════════════════════════════════════════════════════ #

class TestInvalidFilenames(unittest.TestCase):

    def test_completely_wrong_name(self):
        r = _parse("satellite.jpg")
        self.assertFalse(r.success)
        self.assertIn("date", r.missing_fields)
        self.assertIn("time", r.missing_fields)
        self.assertIn("land_type", r.missing_fields)
        self.assertGreater(len(r.errors), 0)

    def test_missing_extension(self):
        r = _parse("2026-01-15_10-30_Forest")
        self.assertFalse(r.success)

    def test_missing_time_segment(self):
        r = _parse("2026-01-15_Forest.jpg")
        self.assertFalse(r.success)

    def test_empty_string(self):
        r = _parse("")
        self.assertFalse(r.success)

    def test_only_extension(self):
        r = _parse(".jpg")
        self.assertFalse(r.success)


# ═══════════════════════════════════════════════════════════════════════════ #
# 3. Invalid date values                                                       #
# ═══════════════════════════════════════════════════════════════════════════ #

class TestInvalidDate(unittest.TestCase):

    def test_month_out_of_range(self):
        r = _parse("2026-13-01_10-30_Forest.jpg")
        self.assertFalse(r.success)
        self.assertIn("date", r.missing_fields)

    def test_day_out_of_range(self):
        r = _parse("2026-01-32_10-30_Forest.jpg")
        self.assertFalse(r.success)
        self.assertIn("date", r.missing_fields)

    def test_february_invalid_day(self):
        # 2026 is not a leap year
        r = _parse("2026-02-29_10-30_Forest.jpg")
        self.assertFalse(r.success)
        self.assertIn("date", r.missing_fields)

    def test_zero_month(self):
        r = _parse("2026-00-15_10-30_Forest.jpg")
        self.assertFalse(r.success)
        self.assertIn("date", r.missing_fields)

    def test_zero_day(self):
        r = _parse("2026-01-00_10-30_Forest.jpg")
        self.assertFalse(r.success)
        self.assertIn("date", r.missing_fields)


# ═══════════════════════════════════════════════════════════════════════════ #
# 4. Invalid time values                                                       #
# ═══════════════════════════════════════════════════════════════════════════ #

class TestInvalidTime(unittest.TestCase):

    def test_hour_out_of_range(self):
        r = _parse("2026-01-15_24-00_Forest.jpg")
        self.assertFalse(r.success)
        self.assertIn("time", r.missing_fields)

    def test_minute_out_of_range(self):
        r = _parse("2026-01-15_10-60_Forest.jpg")
        self.assertFalse(r.success)
        self.assertIn("time", r.missing_fields)

    def test_negative_hour(self):
        # Regex won't match negative numbers (no sign in pattern), so it
        # fails at the pattern-match level.
        r = _parse("2026-01-15_-1-30_Forest.jpg")
        self.assertFalse(r.success)


# ═══════════════════════════════════════════════════════════════════════════ #
# 5. Land type handling                                                        #
# ═══════════════════════════════════════════════════════════════════════════ #

class TestLandTypes(unittest.TestCase):

    def test_known_types_produce_success(self):
        known = [
            ("Forest", "Forest"),
            ("Water", "Water"),
            ("Agriculture", "Agriculture"),
            ("Urban", "Urban"),
            ("Barren_Land", "Barren_Land"),
            ("Other", "Other"),
        ]
        for raw, expected in known:
            with self.subTest(raw=raw):
                r = _parse(f"2026-01-15_10-30_{raw}.jpg")
                self.assertTrue(r.success, r.errors)
                self.assertEqual(r.record.land_type, expected)

    def test_unknown_land_type_becomes_other(self):
        r = _parse("2026-01-15_10-30_Desert.jpg")
        # Still successful (date/time/format are valid), but land_type→Other
        self.assertTrue(r.success)
        self.assertEqual(r.record.land_type, "Other")

    def test_error_message_for_unknown_land_type(self):
        r = _parse("2026-01-15_10-30_Volcano.jpg")
        # Errors list should mention the unrecognised type
        combined = " ".join(r.errors)
        self.assertIn("Volcano", combined)

    def test_case_insensitive_forest(self):
        r = _parse("2026-01-15_10-30_FOREST.jpg")
        self.assertTrue(r.success, r.errors)
        self.assertEqual(r.record.land_type, "Forest")


# ═══════════════════════════════════════════════════════════════════════════ #
# 6. Image format handling                                                     #
# ═══════════════════════════════════════════════════════════════════════════ #

class TestImageFormats(unittest.TestCase):

    def test_supported_formats(self):
        fmts = ["jpg", "jpeg", "png", "tiff", "tif", "bmp", "webp"]
        for fmt in fmts:
            with self.subTest(fmt=fmt):
                r = _parse(f"2026-01-15_10-30_Forest.{fmt}")
                self.assertTrue(r.success, r.errors)
                self.assertEqual(r.record.image_format, fmt)

    def test_unsupported_format(self):
        r = _parse("2026-01-15_10-30_Forest.xyz")
        self.assertFalse(r.success)
        self.assertIn("image_format", r.missing_fields)


# ═══════════════════════════════════════════════════════════════════════════ #
# 7. ParseResult attributes                                                    #
# ═══════════════════════════════════════════════════════════════════════════ #

class TestParseResultAttributes(unittest.TestCase):

    def test_success_has_no_missing_fields(self):
        r = _parse("2026-01-15_10-30_Forest.jpg")
        self.assertTrue(r.success)
        self.assertEqual(r.missing_fields, [])

    def test_failed_result_has_missing_fields(self):
        r = _parse("not_a_valid_filename.jpg")
        self.assertFalse(r.success)
        self.assertGreater(len(r.missing_fields), 0)

    def test_record_image_name_preserved(self):
        r = _parse("2026-01-15_10-30_Water.png")
        self.assertEqual(r.record.image_name, "2026-01-15_10-30_Water.png")

    def test_record_has_unique_image_id(self):
        r1 = _parse("2026-01-15_10-30_Forest.jpg")
        r2 = _parse("2026-01-15_10-30_Forest.jpg")
        self.assertNotEqual(r1.record.image_id, r2.record.image_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
