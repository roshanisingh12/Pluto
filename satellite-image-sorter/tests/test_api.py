"""
tests/test_api.py

Comprehensive test suite verifying all REST API endpoints of the
Satellite Image Sorter & Organizer FastAPI backend.
"""

import io
import os
import unittest
from PIL import Image
from fastapi.testclient import TestClient

from main import app
from services.catalog import catalog_service


class TestSatelliteAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        # Reset catalog before each test
        catalog_service.clear()

    def tearDown(self):
        catalog_service.clear()

    # --------------------------------------------------------------------------
    # 1. Health & Root
    # --------------------------------------------------------------------------
    def test_health_check(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["app"], "Satellite Image Sorter & Organizer")
        self.assertEqual(data["version"], "1.0.0")
        self.assertIn("catalog_count", data)

    def test_root_redirect(self):
        response = self.client.get("/", follow_redirects=False)
        self.assertIn(response.status_code, [307, 308, 302])
        self.assertEqual(response.headers.get("location"), "/docs")

    # --------------------------------------------------------------------------
    # 2. Dataset & Sample Loading
    # --------------------------------------------------------------------------
    def test_dataset_info(self):
        response = self.client.get("/api/dataset")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("available_classes", data)
        self.assertIn("Forest", data["available_classes"])
        self.assertIn("Water", data["available_classes"])

    def test_dataset_load_all(self):
        response = self.client.post("/api/dataset/load", json={"land_type": None})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertGreater(data["loaded_count"], 0)
        self.assertEqual(data["total_catalog_count"], data["loaded_count"])
        self.assertGreaterEqual(catalog_service.get_count(), 5)

    def test_dataset_load_filtered_class(self):
        response = self.client.post("/api/dataset/load", json={"land_type": "Forest"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertGreater(data["loaded_count"], 0)

        # Verify only Forest images were loaded
        records = catalog_service.get_all()
        for r in records:
            self.assertEqual(r.land_type, "Forest")

    # --------------------------------------------------------------------------
    # 3. Image Listing, Fetch by ID & Metadata Editing
    # --------------------------------------------------------------------------
    def test_images_list_and_pagination(self):
        # Load sample dataset first
        catalog_service.load_samples()
        total_items = catalog_service.get_count()

        response = self.client.get("/api/images")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], total_items)
        self.assertEqual(len(data["items"]), total_items)

        # Test limit and skip
        response_paged = self.client.get("/api/images?skip=0&limit=5")
        self.assertEqual(response_paged.status_code, 200)
        paged_data = response_paged.json()
        self.assertEqual(len(paged_data["items"]), min(5, total_items))

        # Test page and page_size
        response_page_size = self.client.get("/api/images?page=1&page_size=3")
        self.assertEqual(response_page_size.status_code, 200)
        page_data = response_page_size.json()
        self.assertEqual(len(page_data["items"]), min(3, total_items))
        self.assertEqual(page_data["total"], total_items)

        # Test search query
        first_img = catalog_service.get_all()[0]
        search_res = self.client.get(f"/api/images?search={first_img.image_id}")
        self.assertEqual(search_res.status_code, 200)
        search_data = search_res.json()
        self.assertGreaterEqual(search_data["total"], 1)
        self.assertTrue(any(item["image_id"] == first_img.image_id for item in search_data["items"]))

    def test_images_filter_by_land_type_and_format(self):
        catalog_service.load_samples()
        response = self.client.get("/api/images?land_type=Water")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for item in data["items"]:
            self.assertEqual(item["land_type"], "Water")

    def test_get_image_by_id_and_not_found(self):
        catalog_service.load_samples()
        records = catalog_service.get_all()
        target = records[0]

        # Valid ID lookup
        response = self.client.get(f"/api/images/{target.image_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["image_id"], target.image_id)
        self.assertEqual(data["image_name"], target.image_name)

        # Invalid ID lookup
        res_404 = self.client.get("/api/images/NONEXISTENT_999")
        self.assertEqual(res_404.status_code, 404)

    def test_update_image_metadata(self):
        catalog_service.load_samples()
        records = catalog_service.get_all()
        target = records[0]

        update_payload = {
            "date": "2026-05-20",
            "time": "15-30",
            "land_type": "Urban",
        }
        response = self.client.put(f"/api/images/{target.image_id}", json=update_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["date"], "2026-05-20")
        self.assertEqual(data["time"], "15-30")
        self.assertEqual(data["datetime"], "2026-05-20 15:30")
        self.assertEqual(data["land_type"], "Urban")

        # Verify change persisted in catalog service & hash table
        fetched = catalog_service.get_by_id(target.image_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.land_type, "Urban")
        self.assertEqual(fetched.datetime, "2026-05-20 15:30")

    def test_get_image_file_preview(self):
        catalog_service.load_samples()
        records = catalog_service.get_all()
        target = records[0]

        response = self.client.get(f"/api/images/{target.image_id}/file")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.content) > 0)
        self.assertIn("image/", response.headers["content-type"])

    def test_delete_image(self):
        catalog_service.load_samples()
        initial_count = catalog_service.get_count()
        records = catalog_service.get_all()
        target_id = records[0].image_id

        del_res = self.client.delete(f"/api/images/{target_id}")
        self.assertEqual(del_res.status_code, 200)
        self.assertEqual(catalog_service.get_count(), initial_count - 1)
        self.assertIsNone(catalog_service.get_by_id(target_id))

    # --------------------------------------------------------------------------
    # 4. Upload & Security Validation
    # --------------------------------------------------------------------------
    def test_upload_valid_image(self):
        # Create small test image
        img = Image.new("RGB", (100, 100), color="blue")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        image_bytes = buf.getvalue()

        filename = "2026-04-12_14-00_Water.jpg"
        files = {
            "files": (filename, image_bytes, "image/jpeg"),
        }
        response = self.client.post("/api/upload", files=files)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["uploaded_count"], 1)
        uploaded_record = data["images"][0]
        self.assertEqual(uploaded_record["date"], "2026-04-12")
        self.assertEqual(uploaded_record["time"], "14-00")
        self.assertEqual(uploaded_record["land_type"], "Water")
        self.assertEqual(uploaded_record["width"], 100)
        self.assertEqual(uploaded_record["height"], 100)

        # Check it is in catalog and hash table
        found = catalog_service.get_by_id(uploaded_record["image_id"])
        self.assertIsNotNone(found)

    def test_upload_corrupt_file_rejected(self):
        # Corrupt non-image payload
        bad_bytes = b"NOT_A_REAL_IMAGE_DATA_123456"
        files = {
            "files": ("malicious.jpg", bad_bytes, "image/jpeg"),
        }
        response = self.client.post("/api/upload", files=files)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["uploaded_count"], 0)
        self.assertGreater(len(data["errors"]), 0)

    def test_upload_disallowed_extension(self):
        fake_exe = b"MZ\x90\x00\x03\x00\x00\x00"
        files = {
            "files": ("script.exe", fake_exe, "application/octet-stream"),
        }
        response = self.client.post("/api/upload", files=files)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("Unsupported file extension", data["errors"][0])

    # --------------------------------------------------------------------------
    # 5. Sorting (Merge Sort, Quick Sort, Bubble Sort)
    # --------------------------------------------------------------------------
    def test_sorting_merge_quick_bubble(self):
        catalog_service.load_samples()
        algorithms = ["Merge Sort", "Quick Sort", "Bubble Sort"]
        fields = ["image_name", "land_type", "file_size"]

        for algo in algorithms:
            for fld in fields:
                sort_payload = {
                    "algorithm": algo,
                    "field": fld,
                    "ascending": True,
                }
                res = self.client.post("/api/sort", json=sort_payload)
                self.assertEqual(res.status_code, 200, f"Failed for {algo} on {fld}")
                data = res.json()
                self.assertEqual(data["algorithm"], algo)
                self.assertEqual(data["field"], fld)
                self.assertGreater(data["total_count"], 0)
                self.assertGreaterEqual(data["comparisons"], 0)
                self.assertGreater(data["time_ms"], 0.0)
                self.assertEqual(len(data["results"]), data["total_count"])

    def test_sorting_empty_catalog(self):
        res = self.client.post("/api/sort", json={"algorithm": "Merge Sort", "field": "datetime"})
        self.assertEqual(res.status_code, 400)

    # --------------------------------------------------------------------------
    # 6. Searching (Linear Search, Binary Search)
    # --------------------------------------------------------------------------
    def test_searching_linear_and_binary(self):
        catalog_service.load_samples()
        records = catalog_service.get_all()
        target_name = records[0].image_name

        for algo in ["Linear Search", "Binary Search"]:
            search_payload = {
                "algorithm": algo,
                "field": "image_name",
                "query": target_name,
                "find_all": True,
            }
            res = self.client.post("/api/search", json=search_payload)
            self.assertEqual(res.status_code, 200, f"Failed for {algo}")
            data = res.json()
            self.assertEqual(data["algorithm"], algo)
            self.assertGreaterEqual(data["matches_count"], 1)
            self.assertGreaterEqual(data["comparisons"], 1)
            self.assertEqual(data["results"][0]["image_name"], target_name)

    def test_searching_not_found(self):
        catalog_service.load_samples()
        search_payload = {
            "algorithm": "Linear Search",
            "field": "image_name",
            "query": "NONEXISTENT_IMAGE_FILE.xyz",
            "find_all": True,
        }
        res = self.client.post("/api/search", json=search_payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["matches_count"], 0)
        self.assertEqual(len(data["results"]), 0)

    # --------------------------------------------------------------------------
    # 7. Filtering
    # --------------------------------------------------------------------------
    def test_multi_criteria_filter(self):
        catalog_service.load_samples()
        payload = {
            "land_type": "Forest",
            "image_format": "JPG",
        }
        res = self.client.post("/api/filter", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["matches_count"], 1)
        for r in data["results"]:
            self.assertEqual(r["land_type"], "Forest")
            self.assertEqual(r["image_format"].lower(), "jpg")

    # --------------------------------------------------------------------------
    # 8. Statistics
    # --------------------------------------------------------------------------
    def test_statistics(self):
        catalog_service.load_samples()
        res = self.client.get("/api/statistics")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(data["total_images"], 0)
        self.assertIn("land_type_counts", data)
        self.assertIn("format_counts", data)
        self.assertIn("storage_stats", data)
        self.assertGreater(data["storage_stats"]["total_bytes"], 0)

    # --------------------------------------------------------------------------
    # 9. Benchmarking
    # --------------------------------------------------------------------------
    def test_benchmark_endpoint(self):
        catalog_service.load_samples()
        res = self.client.post("/api/benchmark", json={"field": "image_name", "ascending": True})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["results"]), 3)
        algo_names = [r["algorithm"] for r in data["results"]]
        self.assertIn("Bubble Sort", algo_names)
        self.assertIn("Merge Sort", algo_names)
        self.assertIn("Quick Sort", algo_names)

        for r in data["results"]:
            self.assertGreaterEqual(r["comparisons"], 0)
            self.assertGreater(r["time_ms"], 0.0)

    # --------------------------------------------------------------------------
    # 10. CSV Export
    # --------------------------------------------------------------------------
    def test_csv_export(self):
        catalog_service.load_samples()
        res_get = self.client.get("/api/export/csv")
        self.assertEqual(res_get.status_code, 200)
        self.assertIn("text/csv", res_get.headers["content-type"])
        self.assertTrue(res_get.text.startswith("Image ID,Image Name,Date,Time"))

        res_post = self.client.post("/api/export/csv")
        self.assertEqual(res_post.status_code, 200)
        self.assertIn("text/csv", res_post.headers["content-type"])

    # --------------------------------------------------------------------------
    # 11. Folder Organization
    # --------------------------------------------------------------------------
    def test_organize_images(self):
        catalog_service.load_samples()
        test_org_dir = os.path.abspath("test_organized_temp")
        payload = {"output_dir": test_org_dir}

        try:
            res = self.client.post("/api/organize", json=payload)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertTrue(data["success"])
            self.assertGreater(data["total_copied"], 0)
            self.assertTrue(os.path.exists(test_org_dir))
        finally:
            import shutil
            if os.path.exists(test_org_dir):
                shutil.rmtree(test_org_dir, ignore_errors=True)

    # --------------------------------------------------------------------------
    # 12. DSA Specifications & Viva Questions
    # --------------------------------------------------------------------------
    def test_dsa_specifications(self):
        res = self.client.get("/api/dsa")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("sorting", data)
        self.assertIn("searching", data)
        self.assertIn("hashing", data)
        self.assertIn("viva_questions", data)
        self.assertGreaterEqual(len(data["viva_questions"]), 10)


if __name__ == "__main__":
    unittest.main()
