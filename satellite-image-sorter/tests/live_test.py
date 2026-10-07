"""
tests/live_test.py

Executes real HTTP requests against the live running FastAPI server on http://127.0.0.1:8000
verifying all 14 checkpoints specified in Phase 11.
"""

import io
import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
import shutil
import requests
from PIL import Image

BASE_URL = "http://127.0.0.1:8000"


def run_live_tests():
    print(f"--- STARTING LIVE TESTS AGAINST {BASE_URL} ---")

    # 1. Health check
    print("\n[Check 1/14] Testing GET /api/health...")
    r = requests.get(f"{BASE_URL}/api/health")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    health = r.json()
    print(f"✓ Health OK: {health}")

    # Load dataset
    print("\n[Prep] Loading DeepGlobe dataset via POST /api/dataset/load...")
    r = requests.post(f"{BASE_URL}/api/dataset/load", json={"land_type": None})
    assert r.status_code == 200
    load_res = r.json()
    print(f"✓ Loaded {load_res['loaded_count']} images (Total in catalog: {load_res['total_catalog_count']})")

    # 2. Image listing
    print("\n[Check 2/14] Testing GET /api/images...")
    r = requests.get(f"{BASE_URL}/api/images?limit=10")
    assert r.status_code == 200
    images_data = r.json()
    print(f"✓ Image listing OK: Total = {images_data['total']}, Retrieved = {len(images_data['items'])}")
    sample_img = images_data["items"][0]
    sample_id = sample_img["image_id"]

    # Test GET single image by ID
    r = requests.get(f"{BASE_URL}/api/images/{sample_id}")
    assert r.status_code == 200
    print(f"✓ Single image lookup OK for ID {sample_id}: {r.json()['image_name']}")

    # 3. Test Upload
    print("\n[Check 3/14] Testing POST /api/upload (valid image)...")
    buf = io.BytesIO()
    test_img = Image.new("RGB", (256, 256), color=(34, 139, 34))
    test_img.save(buf, format="JPEG")
    buf.seek(0)

    files = {
        "files": ("2026-06-15_11-30_Forest.jpg", buf, "image/jpeg"),
    }
    r = requests.post(f"{BASE_URL}/api/upload", files=files)
    assert r.status_code == 200, f"Upload failed: {r.text}"
    up_res = r.json()
    assert up_res["success"] is True
    assert up_res["uploaded_count"] == 1
    uploaded_record = up_res["images"][0]
    print(f"✓ Upload succeeded: ID = {uploaded_record['image_id']}, File = {uploaded_record['image_name']}")

    # 4. Test Metadata Extraction
    print("\n[Check 4/14] Testing metadata extraction verification...")
    assert uploaded_record["date"] == "2026-06-15", f"Expected date 2026-06-15, got {uploaded_record['date']}"
    assert uploaded_record["time"] == "11-30", f"Expected time 11-30, got {uploaded_record['time']}"
    assert uploaded_record["land_type"] == "Forest", f"Expected Forest, got {uploaded_record['land_type']}"
    assert uploaded_record["width"] == 256, f"Expected 256, got {uploaded_record['width']}"
    assert uploaded_record["height"] == 256, f"Expected 256, got {uploaded_record['height']}"
    assert uploaded_record["file_size"] > 0
    print(f"✓ Metadata extracted accurately: Date={uploaded_record['date']}, Time={uploaded_record['time']}, Land={uploaded_record['land_type']}, Dims={uploaded_record['width']}x{uploaded_record['height']}")

    # 5. Test Image Preview / File serving
    print("\n[Check 5/14] Testing GET /api/images/{id}/file for streaming preview...")
    r = requests.get(f"{BASE_URL}/api/images/{uploaded_record['image_id']}/file")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image/")
    assert len(r.content) > 0
    print(f"✓ Image stream OK: received {len(r.content)} bytes with content-type {r.headers['content-type']}")

    # 6. Test Sorting
    print("\n[Check 6/14] Testing POST /api/sort (Merge, Quick, Bubble sort)...")
    for algo in ["Merge Sort", "Quick Sort", "Bubble Sort"]:
        payload = {
            "algorithm": algo,
            "field": "image_name",
            "ascending": True,
        }
        r = requests.post(f"{BASE_URL}/api/sort", json=payload)
        assert r.status_code == 200, f"Sort {algo} failed: {r.text}"
        sort_res = r.json()
        assert sort_res["algorithm"] == algo
        assert sort_res["comparisons"] > 0
        assert sort_res["time_ms"] >= 0
        # Verify ordering
        names = [item["image_name"].lower() for item in sort_res["results"]]
        assert names == sorted(names), f"Items not properly sorted by {algo}"
        print(f"✓ {algo} passed: {sort_res['total_count']} items sorted, {sort_res['comparisons']} comparisons in {sort_res['time_ms']:.3f} ms")

    # 7. Test Searching
    print("\n[Check 7/14] Testing POST /api/search (Linear & Binary search)...")
    for algo in ["Linear Search", "Binary Search"]:
        target_name = uploaded_record["image_name"]
        payload = {
            "algorithm": algo,
            "field": "image_name",
            "query": target_name,
            "find_all": True,
        }
        r = requests.post(f"{BASE_URL}/api/search", json=payload)
        assert r.status_code == 200, f"Search {algo} failed: {r.text}"
        search_res = r.json()
        assert search_res["matches_count"] >= 1
        assert search_res["results"][0]["image_name"] == target_name
        assert search_res["comparisons"] >= 1
        print(f"✓ {algo} passed: found {search_res['matches_count']} match(es) with {search_res['comparisons']} comparisons in {search_res['time_ms']:.3f} ms")

    # 8. Test Filtering
    print("\n[Check 8/14] Testing POST /api/filter...")
    filter_payload = {
        "land_type": "Water",
        "image_format": "JPG",
    }
    r = requests.post(f"{BASE_URL}/api/filter", json=filter_payload)
    assert r.status_code == 200, f"Filter failed: {r.text}"
    filter_res = r.json()
    assert filter_res["matches_count"] > 0
    for item in filter_res["results"]:
        assert item["land_type"] == "Water"
        assert item["image_format"].lower() == "jpg"
    print(f"✓ Filtering passed: {filter_res['matches_count']} items matched criteria (comparisons: {filter_res['comparisons']})")

    # 9. Test Statistics
    print("\n[Check 9/14] Testing GET /api/statistics...")
    r = requests.get(f"{BASE_URL}/api/statistics")
    assert r.status_code == 200
    stats = r.json()
    assert stats["total_images"] > 0
    assert "Forest" in stats["land_type_counts"]
    assert "JPG" in stats["format_counts"]
    assert stats["storage_stats"]["total_bytes"] > 0
    print(f"✓ Statistics passed: {stats['total_images']} images, storage = {stats['storage_stats']['total_bytes']} bytes")

    # 10. Test Benchmarking
    print("\n[Check 10/14] Testing POST /api/benchmark...")
    bm_payload = {"field": "image_name", "ascending": True}
    r = requests.post(f"{BASE_URL}/api/benchmark", json=bm_payload)
    assert r.status_code == 200
    bm_res = r.json()
    assert len(bm_res["results"]) == 3
    print("✓ Benchmarking passed: Head-to-head results:")
    for b in bm_res["results"]:
        print(f"   • {b['algorithm']:<12}: {b['comparisons']:>6} comparisons, {b['time_ms']:.4f} ms")

    # 11. Test CSV Export
    print("\n[Check 11/14] Testing GET & POST /api/export/csv...")
    r_get = requests.get(f"{BASE_URL}/api/export/csv")
    assert r_get.status_code == 200
    assert "text/csv" in r_get.headers["content-type"]
    assert "Image ID,Image Name" in r_get.text

    r_post = requests.post(f"{BASE_URL}/api/export/csv")
    assert r_post.status_code == 200
    assert "text/csv" in r_post.headers["content-type"]
    print(f"✓ CSV export passed: Generated CSV ({len(r_get.text.splitlines())} lines)")

    # 12. Test Organization
    print("\n[Check 12/14] Testing POST /api/organize...")
    temp_org_dir = os.path.abspath("live_test_organized")
    org_payload = {"output_dir": temp_org_dir}
    try:
        r = requests.post(f"{BASE_URL}/api/organize", json=org_payload)
        assert r.status_code == 200, f"Organize failed: {r.text}"
        org_res = r.json()
        assert org_res["success"] is True
        assert org_res["total_copied"] > 0
        assert os.path.isdir(temp_org_dir)
        print(f"✓ Filesystem organization passed: {org_res['total_copied']} files copied into {temp_org_dir}")
        for cat, cnt in org_res["category_counts"].items():
            if cnt > 0:
                print(f"   • {cat}: {cnt} images")
    finally:
        if os.path.exists(temp_org_dir):
            shutil.rmtree(temp_org_dir, ignore_errors=True)

    # 13. Test DSA Information
    print("\n[Check 13/14] Testing GET /api/dsa...")
    r = requests.get(f"{BASE_URL}/api/dsa")
    assert r.status_code == 200
    dsa_data = r.json()
    assert "sorting" in dsa_data
    assert "searching" in dsa_data
    assert "hashing" in dsa_data
    assert "viva_questions" in dsa_data
    assert len(dsa_data["viva_questions"]) >= 15
    print(f"✓ DSA info passed: {len(dsa_data['sorting'])} sorting algorithms, {len(dsa_data['viva_questions'])} viva questions loaded")

    # 14. Verify Manual DSA algorithm correctness
    print("\n[Check 14/14] Verifying manual DSA sorting & searching correctness...")
    # Test reverse sorting
    r_rev = requests.post(f"{BASE_URL}/api/sort", json={"algorithm": "Merge Sort", "field": "image_name", "ascending": False})
    assert r_rev.status_code == 200
    rev_names = [item["image_name"].lower() for item in r_rev.json()["results"]]
    assert rev_names == sorted(rev_names, reverse=True)
    print("✓ Manual DSA sorting correctness verified on descending direction")

    print("\n=======================================================")
    print(" ALL 14 LIVE ENDPOINT TESTS PASSED WITH 100% SUCCESS! ")
    print("=======================================================")


if __name__ == "__main__":
    run_live_tests()
