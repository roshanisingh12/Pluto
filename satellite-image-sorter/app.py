"""
app.py

🛰️ Satellite Image Sorter & Organizer
Phase 13: Final UI Polish & Sidebar Navigation

Provides a clean, modern, professional Streamlit interface for college viva demonstrations,
project evaluations, and live DSA performance benchmarks.
"""

import os
import sys
import time
import csv
from pathlib import Path
from typing import List, Optional, Dict, Any
import streamlit as st
from PIL import Image

# Ensure project root is available on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from models.image_record import ImageRecord
from services.image_reader import process_uploaded_image, read_image
from services.metadata_parser import parse_filename
from services.statistics import (
    get_land_type_counts,
    get_format_counts,
    get_timeline_counts,
    get_storage_stats,
    get_overall_summary,
)
from services.organizer import generate_metadata_csv, organize_images_by_land_type
from services.benchmark import benchmark_sorting_algorithms
from dsa.sorting import merge_sort, quick_sort, bubble_sort
from dsa.searching import linear_search, binary_search, filter_records

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = str(BASE_DIR / "uploads")
SAMPLE_DIR = str(BASE_DIR / "sample_images")
ORGANIZED_DIR = str(BASE_DIR / "Organized")
os.makedirs(UPLOAD_DIR, exist_ok=True)

DEEPGLOBE_LAND_TYPES = ["Forest", "Water", "Agriculture", "Urban", "Barren"]
LAND_TYPE_OPTIONS = ["Forest", "Water", "Agriculture", "Urban", "Barren", "Barren_Land", "Other"]
FILTER_LAND_OPTIONS = ["All", "Forest", "Water", "Agriculture", "Urban", "Barren", "Barren_Land", "Other"]
FILTER_FORMAT_OPTIONS = ["All", "JPG", "JPEG", "PNG", "TIFF", "WEBP"]

SORT_FIELD_MAP = {
    "Image Name": "image_name",
    "Land Type": "land_type",
    "File Size": "file_size",
    "Image Format": "image_format",
    "Image ID": "image_id",
    "Date & Time": "datetime",
}

SEARCH_FIELD_MAP = {
    "Image ID": "image_id",
    "Image Name": "image_name",
    "Land Type": "land_type",
    "Image Format": "image_format",
    "Date": "date",
}


def load_sample_images(target_land_type: Optional[str] = None) -> None:
    """
    Load real satellite imagery from sample_images/ directory and its class subfolders
    (Forest, Water, Agriculture, Urban, Barren), referencing metadata.csv.
    """
    sample_path = Path(SAMPLE_DIR)
    if not sample_path.exists():
        st.warning("Sample images directory not found.")
        return

    # 1. Read metadata.csv if available
    metadata_map: Dict[str, Dict[str, str]] = {}
    metadata_file = sample_path / "metadata.csv"
    if metadata_file.exists():
        try:
            with open(metadata_file, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    fname = row.get("original_filename", "").strip()
                    if fname:
                        metadata_map[fname] = row
        except Exception as exc:
            st.warning(f"Could not parse sample metadata.csv: {exc}")

    # 2. Gather image files from class subdirectories and root
    class_folders = ["Forest", "Water", "Agriculture", "Urban", "Barren"]
    image_candidates = []

    for folder_name in class_folders:
        folder_dir = sample_path / folder_name
        if folder_dir.is_dir():
            if target_land_type and target_land_type not in ("All", "All Classes") and folder_name.lower() != target_land_type.lower():
                continue
            for img_file in sorted(folder_dir.iterdir()):
                if img_file.is_file() and img_file.suffix.lower() in (".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp"):
                    image_candidates.append((img_file, folder_name))

    # Fallback to root sample_images folder only if class subdirectories are empty
    if not image_candidates:
        for img_file in sorted(sample_path.iterdir()):
            if img_file.is_file() and img_file.suffix.lower() in (".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp"):
                image_candidates.append((img_file, None))

    loaded_count = 0
    for file_p, default_land_type in image_candidates:
        filename = file_p.name
        if any(r.image_name == filename for r in st.session_state.records):
            continue

        meta = metadata_map.get(filename, {})
        img_id = meta.get("image_id") or get_next_image_id()
        land_type = meta.get("land_type") or default_land_type
        if not land_type:
            parsed = parse_filename(filename)
            land_type = parsed.record.land_type or "Other"

        record = ImageRecord(
            image_id=str(img_id),
            image_name=filename,
            file_path=str(file_p.resolve()),
            land_type=land_type,
            dominant_percentage=meta.get("dominant_percentage"),
            source=meta.get("source", "DeepGlobe Land Cover Challenge (DigitalGlobe)"),
            date=None,
            time=None,
            datetime=None,
        )

        read_res = read_image(str(file_p.resolve()), record=record)
        if read_res.success:
            st.session_state.records.append(record)
            loaded_count += 1

    if loaded_count > 0:
        st.session_state.sorted_records = None
        st.session_state.sort_stats = None
        st.session_state.search_results = None
        st.session_state.search_stats = None
        st.session_state.filter_results = None
        st.session_state.filter_stats = None
        st.session_state.benchmark_results = None
        st.session_state.organization_summary = None
        target_info = f" ({target_land_type})" if target_land_type and target_land_type not in ("All", "All Classes") else ""
        st.success(f"✓ Successfully loaded {loaded_count} real satellite images{target_info} from DeepGlobe dataset!")
        st.rerun()
    else:
        st.info("The selected satellite images are already loaded in the catalog.")

SORT_ALGO_INFO = {
    "Merge Sort": {
        "purpose": "Divide-and-conquer sorting technique designed for guaranteed O(n log n) time complexity and stable element ordering.",
        "working": (
            "1. **Divide**: Recursively halves the list around the midpoint until sublists contain 0 or 1 element.\n"
            "2. **Conquer**: Recursively sorts the left and right sublists.\n"
            "3. **Combine (Merge)**: Merges the two sorted halves in linear time by repeatedly comparing their smallest elements."
        ),
        "best_time": "O(n log n)",
        "avg_time": "O(n log n)",
        "worst_time": "O(n log n)",
        "space": "O(n) auxiliary",
        "stability": "Stable (preserves relative order of duplicate keys)",
    },
    "Quick Sort": {
        "purpose": "High-efficiency divide-and-conquer algorithm that sorts elements in-place using pivot partitioning.",
        "working": (
            "1. **Pivot Selection**: Selects a pivot element (last element via Lomuto partitioning).\n"
            "2. **Partitioning**: Reorganizes the array so all items smaller than the pivot precede it and larger items follow it.\n"
            "3. **Recursion**: Recursively applies the partition step to the left and right subarrays."
        ),
        "best_time": "O(n log n)",
        "avg_time": "O(n log n)",
        "worst_time": "O(n²)",
        "space": "O(log n) recursive call stack",
        "stability": "Unstable",
    },
    "Bubble Sort": {
        "purpose": "Classic comparison-based sorting technique that bubbles elements to their correct position through adjacent swaps.",
        "working": (
            "1. **Passes**: Iterates through the list n - 1 times.\n"
            "2. **Adjacent Comparison**: Compares adjacent elements arr[j] and arr[j + 1].\n"
            "3. **Swapping**: Swaps out-of-order adjacent elements.\n"
            "4. **Early Exit**: If a full pass completes with 0 swaps, the algorithm halts early in O(n) time."
        ),
        "best_time": "O(n) (when already sorted)",
        "avg_time": "O(n²)",
        "worst_time": "O(n²)",
        "space": "O(1) auxiliary",
        "stability": "Stable",
    },
}

SEARCH_ALGO_INFO = {
    "Linear Search": {
        "purpose": "Sequential scan examining elements one-by-one from index 0 to n - 1.",
        "working": (
            "1. Iterates through the collection element by element.\n"
            "2. Compares each element's key directly with the target value.\n"
            "3. Collects all matching items.\n"
            "4. Does not require the list to be sorted beforehand."
        ),
        "best_time": "O(1) (first item matches)",
        "avg_time": "O(n)",
        "worst_time": "O(n)",
        "space": "O(1) auxiliary",
        "requirement": "None (Works on unsorted data)",
    },
    "Binary Search": {
        "purpose": "Logarithmic divide-and-conquer search halving the remaining search space with each comparison.",
        "working": (
            "1. **Prerequisite**: Dataset must be sorted according to the search key.\n"
            "2. Computes midpoint index: mid = (low + high) // 2.\n"
            "3. Compares target with arr[mid] and narrows boundaries to left or right half.\n"
            "4. Expands to left and right neighbors to gather all contiguous duplicates."
        ),
        "best_time": "O(1) (target at initial midpoint)",
        "avg_time": "O(log n)",
        "worst_time": "O(log n)",
        "space": "O(1) auxiliary",
        "requirement": "Strictly requires dataset sorted by search key",
    },
}


def init_session_state() -> None:
    """Initialize session state variables."""
    if "records" not in st.session_state:
        st.session_state.records = []  # List[ImageRecord]
    if "sorted_records" not in st.session_state:
        st.session_state.sorted_records = None
    if "sort_stats" not in st.session_state:
        st.session_state.sort_stats = None
    if "search_results" not in st.session_state:
        st.session_state.search_results = None
    if "search_stats" not in st.session_state:
        st.session_state.search_stats = None
    if "filter_results" not in st.session_state:
        st.session_state.filter_results = None
    if "filter_stats" not in st.session_state:
        st.session_state.filter_stats = None
    if "benchmark_results" not in st.session_state:
        st.session_state.benchmark_results = None
    if "organization_summary" not in st.session_state:
        st.session_state.organization_summary = None
    if "next_id_num" not in st.session_state:
        st.session_state.next_id_num = 1
    if "processed_upload_keys" not in st.session_state:
        st.session_state.processed_upload_keys = set()


def get_next_image_id() -> str:
    """Generate sequential image IDs like SAT001, SAT002, SAT003."""
    img_id = f"SAT{st.session_state.next_id_num:03d}"
    st.session_state.next_id_num += 1
    return img_id


def format_file_size(size_in_bytes: Optional[int]) -> str:
    """Format file size in bytes to human-readable string."""
    if size_in_bytes is None:
        return "N/A"
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"


def run_manual_sort(algorithm_name: str, sort_field_label: str, ascending: bool) -> None:
    """Execute manual DSA sorting without using any library or built-in sort."""
    if not st.session_state.records:
        st.warning("No images to sort. Please upload or load images first.")
        return

    key_field = SORT_FIELD_MAP[sort_field_label]
    input_records = list(st.session_state.records)

    start_time = time.perf_counter()

    if algorithm_name == "Merge Sort":
        sorted_list, comps = merge_sort(input_records, key=key_field, ascending=ascending)
    elif algorithm_name == "Quick Sort":
        sorted_list, comps = quick_sort(input_records, key=key_field, ascending=ascending)
    elif algorithm_name == "Bubble Sort":
        sorted_list, comps = bubble_sort(input_records, key=key_field, ascending=ascending)
    else:
        st.error(f"Unknown algorithm '{algorithm_name}'")
        return

    elapsed_time = time.perf_counter() - start_time
    elapsed_ms = elapsed_time * 1000.0

    st.session_state.sorted_records = sorted_list
    st.session_state.search_results = None
    st.session_state.filter_results = None
    st.session_state.sort_stats = {
        "algorithm": algorithm_name,
        "field": sort_field_label,
        "order": "Ascending" if ascending else "Descending",
        "comparisons": comps,
        "time_ms": elapsed_ms,
        "count": len(sorted_list),
    }


def run_manual_search(algorithm_name: str, search_field_label: str, query: str) -> None:
    """Execute manual DSA search (Linear or Binary Search)."""
    if not st.session_state.records:
        st.warning("No images in catalog to search.")
        return

    if not query.strip():
        st.warning("Please enter a search query.")
        return

    key_field = SEARCH_FIELD_MAP[search_field_label]
    input_records = list(st.session_state.records)

    start_time = time.perf_counter()

    if algorithm_name == "Linear Search":
        matches, comps = linear_search(input_records, target=query.strip(), key=key_field, find_all=True)
    elif algorithm_name == "Binary Search":
        matches, comps = binary_search(input_records, target=query.strip(), key=key_field, is_sorted=False, find_all=True)
    else:
        st.error(f"Unknown search algorithm '{algorithm_name}'")
        return

    elapsed_time = time.perf_counter() - start_time
    elapsed_ms = elapsed_time * 1000.0

    st.session_state.search_results = matches
    st.session_state.sorted_records = None
    st.session_state.filter_results = None
    st.session_state.search_stats = {
        "algorithm": algorithm_name,
        "field": search_field_label,
        "query": query.strip(),
        "comparisons": comps,
        "matches_count": len(matches),
        "time_ms": elapsed_ms,
    }


def run_manual_filter(land_type: str, image_format: str, start_date: Optional[str], end_date: Optional[str]) -> None:
    """Execute multi-criteria filtering."""
    if not st.session_state.records:
        st.warning("No images in catalog to filter.")
        return

    input_records = list(st.session_state.records)
    start_time = time.perf_counter()

    results, comps = filter_records(
        input_records,
        land_type=land_type if land_type != "All" else None,
        image_format=image_format if image_format != "All" else None,
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None,
    )

    elapsed_time = time.perf_counter() - start_time
    elapsed_ms = elapsed_time * 1000.0

    st.session_state.filter_results = results
    st.session_state.sorted_records = None
    st.session_state.search_results = None
    st.session_state.filter_stats = {
        "land_type": land_type,
        "format": image_format,
        "start_date": start_date or "Any",
        "end_date": end_date or "Any",
        "comparisons": comps,
        "matches_count": len(results),
        "time_ms": elapsed_ms,
    }


def render_image_gallery(records: List[ImageRecord], context_prefix: str = "main") -> None:
    """Renders the image collection in Card Grid or Table layout."""
    if not records:
        st.info("No matching satellite images found.")
        return

    view_col1, view_col2 = st.columns([3, 1])
    with view_col1:
        st.write(f"Displaying **{len(records)}** satellite image(s)")
    with view_col2:
        view_mode = st.radio(
            "Display Layout",
            ["Card Grid View", "Table View"],
            horizontal=True,
            key=f"layout_{context_prefix}",
            label_visibility="collapsed",
        )

    if view_mode == "Card Grid View":
        cols_per_row = 3
        for row_idx in range(0, len(records), cols_per_row):
            cols = st.columns(cols_per_row)
            for col_idx in range(cols_per_row):
                item_idx = row_idx + col_idx
                if item_idx < len(records):
                    record = records[item_idx]
                    with cols[col_idx]:
                        with st.container(border=True):
                            header_col1, header_col2 = st.columns([1, 1])
                            with header_col1:
                                st.markdown(f'<span class="badge-id">{record.image_id}</span>', unsafe_allow_html=True)
                            with header_col2:
                                fmt_str = (record.image_format or "N/A").upper()
                                st.markdown(f'<div style="text-align:right"><span class="badge-format">{fmt_str}</span></div>', unsafe_allow_html=True)

                            if record.file_path and os.path.exists(record.file_path):
                                try:
                                    st.image(record.file_path, use_container_width=True)
                                except Exception as exc:
                                    st.warning(f"Could not render preview: {exc}")
                            else:
                                st.warning("Image file path not accessible.")

                            st.markdown(f"**Filename:** `{record.image_name}`")

                            date_display = record.date if record.date else "_Unavailable (DeepGlobe Benchmark)_"
                            time_display = record.time if record.time else "_Unavailable (DeepGlobe Benchmark)_"
                            dims_display = f"{record.width} × {record.height} px" if record.width and record.height else "N/A"
                            size_display = format_file_size(record.file_size)
                            land_display = record.land_type or "Other"
                            land_slug = land_display.lower().replace(" ", "_")

                            coverage_line = f"\n- **Dominant Purity:** `{record.dominant_percentage}`" if record.dominant_percentage else ""
                            source_line = f"\n- **Source:** `{record.source}`" if record.source else ""

                            st.markdown(f"""
                            - **Land Type:** <span class="badge-land-{land_slug}">{land_display}</span>{coverage_line}{source_line}
                            - **Date:** {date_display}
                            - **Time:** {time_display}
                            - **Dimensions:** {dims_display}
                            - **File Size:** {size_display}
                            """, unsafe_allow_html=True)

                            with st.expander("✏️ View / Edit Details", expanded=False):
                                with st.form(key=f"form_{context_prefix}_{record.image_id}_{item_idx}"):
                                    new_date = st.text_input("Date (YYYY-MM-DD)", value=record.date or "")
                                    new_time = st.text_input("Time (HH-MM)", value=record.time or "")

                                    current_land = record.land_type if record.land_type in LAND_TYPE_OPTIONS else "Other"
                                    land_idx = LAND_TYPE_OPTIONS.index(current_land) if current_land in LAND_TYPE_OPTIONS else 0
                                    new_land = st.selectbox("Land Type", options=LAND_TYPE_OPTIONS, index=land_idx)

                                    save_btn = st.form_submit_button("💾 Save Metadata", use_container_width=True)
                                    if save_btn:
                                        record.date = new_date.strip() if new_date.strip() else None
                                        record.time = new_time.strip() if new_time.strip() else None
                                        if record.date and record.time:
                                            record.datetime = f"{record.date} {record.time.replace('-', ':')}"
                                        else:
                                            record.datetime = None
                                        record.land_type = new_land
                                        st.success("Metadata updated successfully!")
                                        st.rerun()

    else:
        table_data = []
        for r in records:
            table_data.append({
                "Image ID": r.image_id,
                "Image Name": r.image_name,
                "Land Type": r.land_type or "Other",
                "Dominance": r.dominant_percentage or "N/A",
                "Source": r.source or "DeepGlobe",
                "Date": r.date or "Unavailable",
                "Time": r.time or "Unavailable",
                "Format": (r.image_format or "").upper(),
                "Dimensions": f"{r.width}x{r.height}" if r.width and r.height else "N/A",
                "File Size": format_file_size(r.file_size),
                "File Path": r.file_path,
            })
        st.dataframe(table_data, use_container_width=True)


def main():
    st.set_page_config(
        page_title="Satellite Image Sorter & Organizer",
        page_icon="🛰️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    init_session_state()

    # --- Custom CSS Styling ---
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.1rem;
            font-weight: 700;
            color: #1E3A8A;
            margin-bottom: 0.1rem;
        }
        .sub-header {
            font-size: 1.02rem;
            color: #4B5563;
            margin-bottom: 1.2rem;
        }
        .badge-id {
            background-color: #1D4ED8;
            color: white;
            font-weight: bold;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.85rem;
            display: inline-block;
        }
        .badge-format {
            background-color: #6B7280;
            color: white;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.82rem;
            display: inline-block;
        }
        .stat-highlight {
            background-color: #EFF6FF;
            border: 1px solid #BFDBFE;
            border-radius: 8px;
            padding: 14px 18px;
            margin-bottom: 14px;
        }
        .badge-land-forest { background-color: #059669; color: white; padding: 2px 6px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; }
        .badge-land-water { background-color: #0284C7; color: white; padding: 2px 6px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; }
        .badge-land-agriculture { background-color: #D97706; color: white; padding: 2px 6px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; }
        .badge-land-urban { background-color: #7C3AED; color: white; padding: 2px 6px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; }
        .badge-land-barren { background-color: #EA580C; color: white; padding: 2px 6px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; }
        .badge-land-barren_land { background-color: #EA580C; color: white; padding: 2px 6px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; }
        .badge-land-other { background-color: #64748B; color: white; padding: 2px 6px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; }
        </style>
    """, unsafe_allow_html=True)

    # --- Sidebar Navigation & Controls ---
    with st.sidebar:
        st.title("🛰️ Satellite Sorter")
        st.caption("DeepGlobe Satellite Imagery Catalog")
        st.markdown("---")

        nav_page = st.radio(
            "Navigation",
            options=[
                "🏠 Dashboard",
                "📤 Upload Images",
                "🔄 Sort Images",
                "🔎 Search Images",
                "🎛️ Filters",
                "📊 Statistics",
                "📦 Export",
                "🧠 DSA Information",
            ],
            key="main_sidebar_nav",
        )

        st.markdown("---")
        st.subheader("🛰️ Catalog Summary")
        total_records = len(st.session_state.records)
        st.metric("Total Catalog Images", total_records)

        st.markdown("---")
        st.subheader("📥 DeepGlobe Dataset")
        sel_class_option = st.selectbox(
            "Select Class to Load",
            options=[
                "All 5 Classes (100 Images)",
                "Forest (20 Images)",
                "Water (20 Images)",
                "Agriculture (20 Images)",
                "Urban (20 Images)",
                "Barren (20 Images)",
            ],
            key="sb_dataset_class_select",
        )

        if st.button("📥 Load Dataset Images", use_container_width=True, type="primary"):
            target_class = None
            if "Forest" in sel_class_option:
                target_class = "Forest"
            elif "Water" in sel_class_option:
                target_class = "Water"
            elif "Agriculture" in sel_class_option:
                target_class = "Agriculture"
            elif "Urban" in sel_class_option:
                target_class = "Urban"
            elif "Barren" in sel_class_option:
                target_class = "Barren"
            load_sample_images(target_land_type=target_class)

        if total_records > 0:
            if st.button("🗑️ Clear Catalog", use_container_width=True):
                st.session_state.records = []
                st.session_state.sorted_records = None
                st.session_state.sort_stats = None
                st.session_state.search_results = None
                st.session_state.search_stats = None
                st.session_state.filter_results = None
                st.session_state.filter_stats = None
                st.session_state.benchmark_results = None
                st.session_state.organization_summary = None
                st.session_state.processed_upload_keys = set()
                st.session_state.next_id_num = 1
                st.success("Catalog cleared.")
                st.rerun()

    # --- Main Header Title ---
    st.markdown('<div class="main-header">🛰️ Satellite Image Sorter & Organizer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Organizes, searches, sorts, and analyzes real satellite imagery using custom Data Structures & Algorithms (DSA).</div>',
        unsafe_allow_html=True,
    )

    # ==========================================================================
    # SIDEBAR PAGE NAVIGATION SWITCH
    # ==========================================================================

    # --------------------------------------------------------------------------
    # PAGE 1: 🏠 Dashboard
    # --------------------------------------------------------------------------
    if nav_page == "🏠 Dashboard":
        st.markdown("## 🏠 Dashboard & Catalog Overview")
        st.write(
            "Overview of current catalog metrics, sorting & searching states, land classification distribution, and storage size."
        )

        records = st.session_state.records
        summary = get_overall_summary(records)
        lc = summary["land_type_counts"]
        stg = summary["storage_stats"]

        st.markdown("### 📊 Quick Metrics")
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.metric("Total Catalog Images", summary["total_images"])
        with m2:
            sort_status = st.session_state.sort_stats["algorithm"] if st.session_state.sort_stats else "Default Order"
            st.metric("Current Sorting", sort_status)
        with m3:
            search_status = f"{st.session_state.search_stats['matches_count']} matches" if st.session_state.search_stats else "None"
            st.metric("Active Search", search_status)
        with m4:
            filter_status = f"{st.session_state.filter_stats['matches_count']} matches" if st.session_state.filter_stats else "None"
            st.metric("Active Filters", filter_status)
        with m5:
            st.metric("Total Storage", format_file_size(stg["total_bytes"]))

        st.markdown("---")
        st.markdown("### 🌲 Images by Land Classification")
        lc_cols = st.columns(6)
        with lc_cols[0]:
            st.metric("Forest", lc.get("Forest", 0))
        with lc_cols[1]:
            st.metric("Water", lc.get("Water", 0))
        with lc_cols[2]:
            st.metric("Agriculture", lc.get("Agriculture", 0))
        with lc_cols[3]:
            st.metric("Urban", lc.get("Urban", 0))
        with lc_cols[4]:
            st.metric("Barren Land", lc.get("Barren_Land", 0) + lc.get("Barren", 0))
        with lc_cols[5]:
            st.metric("Other", lc.get("Other", 0))

        st.markdown("---")
        st.markdown("### 🖼️ Catalog Preview & Land-Type Selector")
        if not records:
            st.info("No satellite images loaded in catalog yet.")
            st.caption("Click below to load the curated 100-image DeepGlobe satellite dataset (20 images per class):")
            c_btn1, c_btn2 = st.columns([1.5, 2.5])
            with c_btn1:
                if st.button("📥 Load All 100 DeepGlobe Images", type="primary", use_container_width=True, key="dash_init_load_all"):
                    load_sample_images()
        else:
            land_categories = ["All Classes", "Forest", "Water", "Agriculture", "Urban", "Barren"]
            
            sel_land_col1, sel_land_col2 = st.columns([3, 1])
            with sel_land_col1:
                selected_land_view = st.radio(
                    "Select Land Classification to Explore",
                    options=land_categories,
                    horizontal=True,
                    key="dash_radio_land_selector",
                )
            with sel_land_col2:
                if st.button("📥 Load More / Refresh", use_container_width=True, key="btn_dash_reload_samples"):
                    load_sample_images()

            display_records = records
            if selected_land_view and selected_land_view != "All Classes":
                if selected_land_view == "Barren":
                    display_records = [r for r in records if (r.land_type or "").lower() in ("barren", "barren_land")]
                else:
                    display_records = [r for r in records if (r.land_type or "").lower() == selected_land_view.lower()]

            if st.session_state.sorted_records is not None:
                st.caption(f"Showing sorted results via **{st.session_state.sort_stats['algorithm']}** ({st.session_state.sort_stats['order']})")
                render_image_gallery(st.session_state.sorted_records, context_prefix="dash_sorted")
            elif st.session_state.search_results is not None:
                st.caption("Showing active search matches")
                render_image_gallery(st.session_state.search_results, context_prefix="dash_search")
            elif st.session_state.filter_results is not None:
                st.caption("Showing active filter matches")
                render_image_gallery(st.session_state.filter_results, context_prefix="dash_filter")
            else:
                if selected_land_view != "All Classes":
                    st.caption(f"Showing **{len(display_records)}** satellite images for **{selected_land_view}**")
                render_image_gallery(display_records, context_prefix="dash_default")

    # --------------------------------------------------------------------------
    # PAGE 2: 📤 Upload Images
    # --------------------------------------------------------------------------
    elif nav_page == "📤 Upload Images":
        st.markdown("## 📤 Upload Satellite Imagery")
        st.write(
            "Supported file formats: **JPG, JPEG, PNG, TIFF, WEBP**. Metadata is automatically parsed from standard "
            "filenames formatted as `YYYY-MM-DD_HH-MM_LandType.ext`."
        )

        uploaded_files = st.file_uploader(
            "Select satellite images to upload",
            type=["jpg", "jpeg", "png", "tiff", "tif", "webp"],
            accept_multiple_files=True,
            help="Upload satellite images to process metadata.",
            key="page_file_uploader",
        )

        if uploaded_files:
            newly_processed = 0
            error_messages = []

            for uploaded_file in uploaded_files:
                upload_key = f"{uploaded_file.name}_{uploaded_file.size}"
                if upload_key in st.session_state.processed_upload_keys:
                    continue

                if any(r.image_name == uploaded_file.name for r in st.session_state.records):
                    st.session_state.processed_upload_keys.add(upload_key)
                    continue

                image_id = get_next_image_id()
                record, error = process_uploaded_image(
                    uploaded_file,
                    upload_dir=UPLOAD_DIR,
                    image_id=image_id,
                )

                if record is not None:
                    st.session_state.records.append(record)
                    st.session_state.processed_upload_keys.add(upload_key)
                    newly_processed += 1
                else:
                    error_messages.append(f"⚠ Unable to process the selected image '{uploaded_file.name}': {error}")

            if newly_processed > 0:
                st.session_state.sorted_records = None
                st.session_state.sort_stats = None
                st.session_state.search_results = None
                st.session_state.filter_results = None
                st.session_state.benchmark_results = None
                st.session_state.organization_summary = None
                st.success(f"✓ Images uploaded successfully. ({newly_processed} image(s) added)")
                st.rerun()

            for err in error_messages:
                st.error(err)

        st.markdown("---")
        st.markdown(f"### 📋 Cataloged Images ({len(st.session_state.records)} total)")
        if not st.session_state.records:
            st.info("No images uploaded yet.")
        else:
            render_image_gallery(st.session_state.records, context_prefix="upload_page")

    # --------------------------------------------------------------------------
    # PAGE 3: 🔄 Sort Images
    # --------------------------------------------------------------------------
    elif nav_page == "🔄 Sort Images":
        st.markdown("## 🔄 Manual DSA Sorting Engine")
        st.write("Sort satellite images using pure from-scratch DSA algorithms with real-time performance tracking.")

        sort_tab1, sort_tab2 = st.tabs(["⚡ Single Sort Engine", "⚔️ Benchmark Comparison"])

        with sort_tab1:
            if not st.session_state.records:
                st.info("No sorted images available.")
                st.caption("Please upload images or load sample images first.")
            else:
                s_col1, s_col2, s_col3 = st.columns([1.2, 1.2, 1.2])
                with s_col1:
                    sort_field = st.selectbox(
                        "Sort By Field",
                        options=["Date & Time", "Image Format", "Land Type", "Image Name", "File Size"],
                        key="p_sort_select_field",
                    )
                with s_col2:
                    sort_algo = st.selectbox(
                        "Sorting Algorithm",
                        options=["Merge Sort", "Quick Sort", "Bubble Sort"],
                        key="p_sort_select_algo",
                    )
                with s_col3:
                    sort_dir = st.radio(
                        "Sort Direction",
                        options=["Ascending", "Descending"],
                        horizontal=True,
                        key="p_sort_select_order",
                    )

                s_btn_col1, s_btn_col2 = st.columns([1.5, 1.5])
                with s_btn_col1:
                    if st.button("🚀 Run Sorting", use_container_width=True, type="primary", key="p_btn_run_sort"):
                        run_manual_sort(sort_algo, sort_field, (sort_dir == "Ascending"))
                        st.rerun()
                with s_btn_col2:
                    if st.session_state.sorted_records is not None:
                        if st.button("🔄 Reset Sort", use_container_width=True, key="p_btn_reset_sort"):
                            st.session_state.sorted_records = None
                            st.session_state.sort_stats = None
                            st.rerun()

                if st.session_state.sort_stats:
                    st.markdown("#### Execution Performance")
                    st.markdown('<div class="stat-highlight">', unsafe_allow_html=True)
                    m1, m2, m3, m4 = st.columns(4)
                    with m1:
                        st.metric("Algorithm", st.session_state.sort_stats["algorithm"])
                    with m2:
                        st.metric("Field", f"{st.session_state.sort_stats['field']} ({st.session_state.sort_stats['order']})")
                    with m3:
                        st.metric("Comparisons", f"{st.session_state.sort_stats['comparisons']:,}")
                    with m4:
                        st.metric("Time Elapsed", f"{st.session_state.sort_stats['time_ms']:.3f} ms")
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown("#### Sorted Results")
                    render_image_gallery(st.session_state.sorted_records, context_prefix="sort_results_page")

                info = SORT_ALGO_INFO[sort_algo]
                with st.expander(f"ℹ️ **Algorithm Information: {sort_algo}**", expanded=False):
                    st.markdown(f"**Purpose**: {info['purpose']}")
                    st.markdown(f"**How It Works**:\n{info['working']}")
                    st.markdown("#### Complexity Analysis")
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        st.metric("Best Case", info["best_time"])
                    with c2:
                        st.metric("Average Case", info["avg_time"])
                    with c3:
                        st.metric("Worst Case", info["worst_time"])
                    with c4:
                        st.metric("Space", info["space"])
                    st.caption(f"**Stability**: {info['stability']}")

        with sort_tab2:
            st.markdown("### ⚔️ Head-to-Head Algorithm Comparison")
            if not st.session_state.records:
                st.info("No sorted images available.")
                st.caption("Please upload images or load sample images first.")
            else:
                b_col1, b_col2, b_col3 = st.columns([1.5, 1.5, 1.0])
                with b_col1:
                    benchmark_field = st.selectbox(
                        "Benchmark Field",
                        options=["Date & Time", "Image Format", "Land Type", "Image Name", "File Size"],
                        key="bm_field_select_page",
                    )
                with b_col2:
                    benchmark_dir = st.radio(
                        "Sort Direction",
                        options=["Ascending", "Descending"],
                        horizontal=True,
                        key="bm_dir_select_page",
                    )
                with b_col3:
                    st.write("")
                    run_bm_btn = st.button("🚀 Run Benchmark", type="primary", use_container_width=True, key="btn_run_bm_page")

                if run_bm_btn or st.session_state.benchmark_results is not None:
                    if run_bm_btn:
                        key_field = SORT_FIELD_MAP[benchmark_field]
                        is_asc = (benchmark_dir == "Ascending")
                        bm_res = benchmark_sorting_algorithms(
                            st.session_state.records,
                            key=key_field,
                            ascending=is_asc,
                        )
                        st.session_state.benchmark_results = {
                            "results": bm_res,
                            "field": benchmark_field,
                            "order": benchmark_dir,
                            "dataset_size": len(st.session_state.records),
                        }

                    bm_data = st.session_state.benchmark_results
                    results_list = bm_data["results"]

                    st.markdown("---")
                    st.markdown(f"#### 📊 Benchmark Results ({bm_data['dataset_size']} items, Field: {bm_data['field']} - {bm_data['order']})")

                    card_cols = st.columns(3)
                    for idx, r in enumerate(results_list):
                        with card_cols[idx]:
                            with st.container(border=True):
                                st.markdown(f"#### 🏆 {r['algorithm']}")
                                st.metric("Comparisons", f"{r['comparisons']:,}")
                                st.metric("Execution Time", f"{r['time_ms']:.4f} ms ({r['time_us']:.1f} µs)")

                    st.markdown("##### 📋 Summary Table")
                    table_display = [
                        {
                            "Algorithm": r["algorithm"],
                            "Execution Time (ms)": f"{r['time_ms']:.4f} ms",
                            "Execution Time (µs)": f"{r['time_us']:.1f} µs",
                            "Comparisons": r["comparisons"],
                            "Items Sorted": r["item_count"],
                        }
                        for r in results_list
                    ]
                    st.table(table_display)

                    chart_c1, chart_c2 = st.columns(2)
                    with chart_c1:
                        st.markdown("##### ⏱️ Execution Time Comparison (ms)")
                        time_chart_data = {r["algorithm"]: r["time_ms"] for r in results_list}
                        st.bar_chart(time_chart_data, color="#2563EB")
                    with chart_c2:
                        st.markdown("##### 🔢 Total Comparisons Comparison")
                        comps_chart_data = {r["algorithm"]: r["comparisons"] for r in results_list}
                        st.bar_chart(comps_chart_data, color="#DC2626")

    # --------------------------------------------------------------------------
    # PAGE 4: 🔎 Search Images
    # --------------------------------------------------------------------------
    elif nav_page == "🔎 Search Images":
        st.markdown("## 🔎 Manual DSA Searching Engine")
        st.write("Search satellite imagery using Linear Search or pre-sorted Binary Search algorithms.")

        if not st.session_state.records:
            st.info("No matching images found.")
            st.caption("Please upload images or load sample images first.")
        else:
            srch_col1, srch_col2, srch_col3 = st.columns([1.2, 1.2, 2.0])
            with srch_col1:
                search_field = st.selectbox(
                    "Search Field",
                    options=["Image ID", "Image Name", "Land Type", "Image Format", "Date"],
                    key="p_search_select_field",
                )
            with srch_col2:
                search_algo = st.selectbox(
                    "Search Algorithm",
                    options=["Linear Search", "Binary Search"],
                    key="p_search_select_algo",
                )
            with srch_col3:
                placeholder_text = {
                    "Image ID": "e.g. SAT001",
                    "Image Name": "e.g. Forest.jpg",
                    "Land Type": "e.g. Forest, Water, Urban",
                    "Image Format": "e.g. jpg, png, tiff, webp",
                    "Date": "e.g. 2026-01-15",
                }.get(search_field, "Enter query...")
                search_query = st.text_input("Query", placeholder=placeholder_text, key="p_search_text_input")

            srch_btn1, srch_btn2 = st.columns([1.5, 1.5])
            with srch_btn1:
                if st.button("🔎 Search", use_container_width=True, type="primary", key="p_btn_run_search"):
                    run_manual_search(search_algo, search_field, search_query)
                    st.rerun()
            with srch_btn2:
                if st.session_state.search_results is not None:
                    if st.button("🔄 Clear Search", use_container_width=True, key="p_btn_clear_search"):
                        st.session_state.search_results = None
                        st.session_state.search_stats = None
                        st.rerun()

            if st.session_state.search_stats:
                st.markdown("#### Search Performance & Metrics")
                s_stat = st.session_state.search_stats
                st.markdown('<div class="stat-highlight">', unsafe_allow_html=True)
                sm1, sm2, sm3, sm4 = st.columns(4)
                with sm1:
                    st.metric("Algorithm", s_stat["algorithm"])
                with sm2:
                    st.metric("Query Target", f"{s_stat['field']}: '{s_stat['query']}'")
                with sm3:
                    st.metric("Comparisons", f"{s_stat['comparisons']:,}")
                with sm4:
                    st.metric("Matches Found", s_stat["matches_count"])
                st.markdown('</div>', unsafe_allow_html=True)

                if s_stat["matches_count"] == 0:
                    st.info("No matching images found.")
                else:
                    st.markdown("##### Matching Images")
                    render_image_gallery(st.session_state.search_results, context_prefix="p_search_tab")

            s_info = SEARCH_ALGO_INFO[search_algo]
            with st.expander(f"ℹ️ **Algorithm Information: {search_algo}**", expanded=False):
                st.markdown(f"**Purpose**: {s_info['purpose']}")
                st.markdown(f"**How It Works**:\n{s_info['working']}")
                st.markdown("#### Complexity Analysis")
                sc1, sc2, sc3, sc4 = st.columns(4)
                with sc1:
                    st.metric("Best Case", s_info["best_time"])
                with sc2:
                    st.metric("Average Case", s_info["avg_time"])
                with sc3:
                    st.metric("Worst Case", s_info["worst_time"])
                with sc4:
                    st.metric("Space", s_info["space"])
                st.caption(f"**Prerequisite**: {s_info['requirement']}")

    # --------------------------------------------------------------------------
    # PAGE 5: 🎛️ Filters
    # --------------------------------------------------------------------------
    elif nav_page == "🎛️ Filters":
        st.markdown("## 🎛️ Multi-Criteria Filters")
        st.write("Filter satellite images across Land Type, Image Format, and Acquisition Date Range.")

        if not st.session_state.records:
            st.info("No matching images found.")
            st.caption("Please upload images or load sample images first.")
        else:
            f_col1, f_col2, f_col3, f_col4 = st.columns([1.2, 1.2, 1.2, 1.2])
            with f_col1:
                filter_land = st.selectbox("Land Type", options=FILTER_LAND_OPTIONS, index=0, key="p_filter_land_select")
            with f_col2:
                filter_fmt = st.selectbox("Format", options=FILTER_FORMAT_OPTIONS, index=0, key="p_filter_fmt_select")
            with f_col3:
                start_d = st.text_input("Start Date (YYYY-MM-DD)", placeholder="e.g. 2026-01-01", key="p_filter_start_date")
            with f_col4:
                end_d = st.text_input("End Date (YYYY-MM-DD)", placeholder="e.g. 2026-12-31", key="p_filter_end_date")

            f_btn1, f_btn2 = st.columns([1.5, 1.5])
            with f_btn1:
                if st.button("🎯 Apply Filters", use_container_width=True, type="primary", key="p_btn_apply_filter"):
                    run_manual_filter(filter_land, filter_fmt, start_d, end_d)
                    st.rerun()
            with f_btn2:
                if st.session_state.filter_results is not None:
                    if st.button("🔄 Reset Filters", use_container_width=True, key="p_btn_reset_filter"):
                        st.session_state.filter_results = None
                        st.session_state.filter_stats = None
                        st.rerun()

            if st.session_state.filter_stats:
                st.markdown("#### Filter Performance & Metrics")
                f_stat = st.session_state.filter_stats
                st.markdown('<div class="stat-highlight">', unsafe_allow_html=True)
                fm1, fm2, fm3, fm4 = st.columns(4)
                with fm1:
                    st.metric("Land Type Filter", f_stat["land_type"])
                with fm2:
                    st.metric("Format Filter", f_stat["format"])
                with fm3:
                    st.metric("Total Comparisons", f"{f_stat['comparisons']:,}")
                with fm4:
                    st.metric("Matching Records", f_stat["matches_count"])
                st.markdown('</div>', unsafe_allow_html=True)

                if f_stat["matches_count"] == 0:
                    st.info("No matching images found.")
                else:
                    st.markdown("##### Filtered Images")
                    render_image_gallery(st.session_state.filter_results, context_prefix="p_filter_tab")

    # --------------------------------------------------------------------------
    # PAGE 6: 📊 Statistics
    # --------------------------------------------------------------------------
    elif nav_page == "📊 Statistics":
        st.markdown("## 📊 Satellite Imagery Statistics & Analytics")
        st.write("Comprehensive visual analytics detailing catalog breakdown, formats, timeline distributions, and storage size.")

        records = st.session_state.records
        if not records:
            st.info("No statistics available yet.")
            st.caption("Upload satellite imagery or load sample images from the sidebar to generate catalog statistics.")
        else:
            summary = get_overall_summary(records)
            lc = summary["land_type_counts"]
            fc = summary["format_counts"]
            stg = summary["storage_stats"]

            st.markdown("### 📊 Metric Overview")
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Total Catalog Images", summary["total_images"])
            with m2:
                st.metric("Total Catalog Storage", format_file_size(stg["total_bytes"]))
            with m3:
                st.metric("Average File Size", format_file_size(int(stg["avg_bytes"])))
            with m4:
                st.metric("Complete Metadata Rate", f"{summary['complete_metadata_count']} / {summary['total_images']}")

            st.markdown("---")
            c_col1, c_col2 = st.columns(2)

            with c_col1:
                st.markdown("#### 🌲 Images by Land Classification")
                land_chart_data = {
                    "Forest": lc.get("Forest", 0),
                    "Water": lc.get("Water", 0),
                    "Agriculture": lc.get("Agriculture", 0),
                    "Urban": lc.get("Urban", 0),
                    "Barren Land": lc.get("Barren_Land", 0),
                    "Other": lc.get("Other", 0),
                }
                st.bar_chart(land_chart_data, color="#059669")

            with c_col2:
                st.markdown("#### 📁 Images by Format")
                fmt_chart_data = {
                    "JPG": fc.get("JPG", 0),
                    "JPEG": fc.get("JPEG", 0),
                    "PNG": fc.get("PNG", 0),
                    "TIFF": fc.get("TIFF", 0),
                    "WEBP": fc.get("WEBP", 0),
                }
                st.bar_chart(fmt_chart_data, color="#2563EB")

            st.markdown("---")
            st.markdown("#### 📅 Acquisition Timeline (Images Over Time)")
            timeline_data = summary["timeline_counts"]
            if timeline_data:
                st.line_chart(timeline_data, color="#7C3AED")
            else:
                st.caption("No dated imagery available to render acquisition timeline.")

    # --------------------------------------------------------------------------
    # PAGE 7: 📦 Export
    # --------------------------------------------------------------------------
    elif nav_page == "📦 Export":
        st.markdown("## 📦 Export & Filesystem Organization")
        st.write("Export satellite metadata as structured CSV or physically organize satellite files into land classification folders.")

        if not st.session_state.records:
            st.info("No export data available.")
            st.caption("Please upload images or load sample images first.")
        else:
            exp_col1, exp_col2 = st.columns(2)

            with exp_col1:
                with st.container(border=True):
                    st.markdown("### 📄 Metadata CSV Export")
                    st.write(f"Generate a CSV report for **{len(st.session_state.records)}** cataloged satellite records.")
                    csv_data = generate_metadata_csv(st.session_state.records)

                    st.download_button(
                        label="📥 Download Metadata CSV",
                        data=csv_data,
                        file_name="satellite_imagery_metadata.csv",
                        mime="text/csv",
                        use_container_width=True,
                        type="primary",
                        key="p_btn_download_csv",
                    )

                    with st.expander("👁️ CSV Preview", expanded=False):
                        st.code(csv_data[:1200] + ("\n... [truncated]" if len(csv_data) > 1200 else ""), language="csv")

            with exp_col2:
                with st.container(border=True):
                    st.markdown("### 📁 Filesystem Folder Organization")
                    st.write("Organizes images physically into subdirectories by land classification:")
                    st.code(
                        "Organized/\n├── Forest/\n├── Water/\n├── Agriculture/\n├── Urban/\n├── Barren_Land/\n└── Other/",
                        language="text",
                    )

                    if st.button("🚀 Organize Images into Folders", use_container_width=True, key="p_btn_run_organize"):
                        summary = organize_images_by_land_type(
                            st.session_state.records,
                            output_root=ORGANIZED_DIR,
                        )
                        st.session_state.organization_summary = summary
                        st.rerun()

            if st.session_state.organization_summary:
                org_summary = st.session_state.organization_summary
                st.markdown("---")
                st.markdown("#### 📁 Folder Organization Summary")
                st.success(f"✓ Successfully organized **{org_summary['total_copied']}** satellite images into `{org_summary['output_dir']}`!")

                counts = org_summary["category_counts"]
                c_cols = st.columns(6)
                for idx, (cat_name, cat_count) in enumerate(counts.items()):
                    with c_cols[idx]:
                        st.metric(f"📁 {cat_name}", cat_count)

                if org_summary["errors"]:
                    st.warning("Some files could not be copied:")
                    for err in org_summary["errors"]:
                        st.write(f"• {err}")

    # --------------------------------------------------------------------------
    # PAGE 8: 🧠 DSA Information
    # --------------------------------------------------------------------------
    elif nav_page == "🧠 DSA Information":
        st.markdown("## 🧠 DSA Information & Algorithm Specifications")
        st.write(
            "Comprehensive theoretical and practical reference explaining the Data Structures & Algorithms "
            "used in this project. Designed for college viva examinations and DSA presentations."
        )

        st.markdown("""
        <div class="stat-highlight">
        <b>💡 Implementation Architecture:</b><br>
        All sorting algorithms (Merge Sort, Quick Sort, Bubble Sort), searching algorithms (Linear Search, Binary Search), 
        and filtering algorithms in this application are <b>manually implemented from scratch</b> in Python without relying on 
        built-in <code>sorted()</code>, <code>list.sort()</code>, or external library routines.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🔄 1. Sorting Algorithms")

        dsa_sort_col1, dsa_sort_col2, dsa_sort_col3 = st.columns(3)

        with dsa_sort_col1:
            with st.container(border=True):
                st.markdown("#### 🟢 Merge Sort")
                st.markdown("**Algorithm Type:** Divide and Conquer")
                st.markdown("**Stability:** Stable")
                st.markdown("**Time Complexity:**")
                st.write("• Best: `O(n log n)`\n• Average: `O(n log n)`\n• Worst: `O(n log n)`")
                st.markdown("**Space Complexity:** `O(n)` auxiliary")
                st.markdown("**How It Works:**")
                st.write(
                    "1. Recursively halves the array around midpoint.\n"
                    "2. Sorts left and right halves independently.\n"
                    "3. Merges sorted halves in linear `O(n)` time."
                )
                st.markdown("**Project Use:** Guaranteed predictable sorting of satellite records regardless of dataset order.")

        with dsa_sort_col2:
            with st.container(border=True):
                st.markdown("#### 🔵 Quick Sort")
                st.markdown("**Algorithm Type:** Partition-based Divide & Conquer")
                st.markdown("**Stability:** Unstable")
                st.markdown("**Time Complexity:**")
                st.write("• Best: `O(n log n)`\n• Average: `O(n log n)`\n• Worst: `O(n²)`")
                st.markdown("**Space Complexity:** `O(log n)` call stack")
                st.markdown("**How It Works:**")
                st.write(
                    "1. Selects a pivot element (last item via Lomuto).\n"
                    "2. Partitions elements smaller than pivot to left, larger to right.\n"
                    "3. Recursively applies to sub-arrays."
                )
                st.markdown("**Project Use:** High-speed in-place sorting for memory-efficient catalog processing.")

        with dsa_sort_col3:
            with st.container(border=True):
                st.markdown("#### 🟡 Bubble Sort")
                st.markdown("**Algorithm Type:** Adjacent Comparison & Swapping")
                st.markdown("**Stability:** Stable")
                st.markdown("**Time Complexity:**")
                st.write("• Best: `O(n)` (with early exit)\n• Average: `O(n²)`\n• Worst: `O(n²)`")
                st.markdown("**Space Complexity:** `O(1)` auxiliary")
                st.markdown("**How It Works:**")
                st.write(
                    "1. Iterates through list n - 1 times.\n"
                    "2. Compares adjacent elements and swaps out-of-order pairs.\n"
                    "3. Early exit halts if 0 swaps occur in a full pass."
                )
                st.markdown("**Project Use:** Educational baseline to compare O(n²) performance against O(n log n) algorithms.")

        st.markdown("---")
        st.markdown("### 🔎 2. Searching Algorithms")

        dsa_srch_col1, dsa_srch_col2 = st.columns(2)

        with dsa_srch_col1:
            with st.container(border=True):
                st.markdown("#### 🔍 Linear Search")
                st.markdown("**Algorithm Type:** Sequential Scan")
                st.markdown("**Prerequisites:** None (Works on unsorted lists)")
                st.markdown("**Time Complexity:** Best `O(1)`, Average `O(n)`, Worst `O(n)`")
                st.markdown("**Space Complexity:** `O(1)` auxiliary")
                st.markdown("**How It Works:**")
                st.write(
                    "1. Scans record list element by element from index 0 to n - 1.\n"
                    "2. Compares key with target query string/number.\n"
                    "3. Collects all matching items."
                )
                st.markdown("**Project Use:** General query search across unsorted catalog attributes.")

        with dsa_srch_col2:
            with st.container(border=True):
                st.markdown("#### 🎯 Binary Search")
                st.markdown("**Algorithm Type:** Logarithmic Divide & Conquer")
                st.markdown("**Prerequisites:** Dataset must be pre-sorted by target key")
                st.markdown("**Time Complexity:** Best `O(1)`, Average `O(log n)`, Worst `O(log n)`")
                st.markdown("**Space Complexity:** `O(1)` auxiliary")
                st.markdown("**How It Works:**")
                st.write(
                    "1. Evaluates midpoint element `mid = (low + high) // 2`.\n"
                    "2. Halves search interval based on target comparison.\n"
                    "3. Scans adjacent left/right neighbors to collect duplicate key occurrences."
                )
                st.markdown("**Project Use:** Ultra-fast logarithmic lookup on pre-sorted satellite records.")

        st.markdown("---")
        st.markdown("### 🎛️ 3. Multi-Criteria Filtering & Data Structure")

        dsa_misc_col1, dsa_misc_col2 = st.columns(2)

        with dsa_misc_col1:
            with st.container(border=True):
                st.markdown("#### 🎯 Predicate Filtering")
                st.markdown("**Algorithm Type:** Single-pass multi-predicate evaluator")
                st.markdown("**Time Complexity:** `O(n)` linear time scan")
                st.markdown("**Space Complexity:** `O(1)` auxiliary space")
                st.markdown("**How It Works:**")
                st.write(
                    "Evaluates boolean predicate conditions (Land Type match AND Format match AND Date range match) "
                    "for each record in a single linear pass."
                )

        with dsa_misc_col2:
            with st.container(border=True):
                st.markdown("#### 📦 ImageRecord Data Structure")
                st.markdown("**Class:** `ImageRecord` (`models/image_record.py`)")
                st.markdown("**Attributes:** `image_id`, `image_name`, `date`, `time`, `datetime`, `land_type`, `image_format`, `width`, `height`, `file_size`, `file_path`")
                st.markdown("**Design:** Encapsulates metadata, validation, and comparative key extractions for all DSA algorithms.")


if __name__ == "__main__":
    main()
