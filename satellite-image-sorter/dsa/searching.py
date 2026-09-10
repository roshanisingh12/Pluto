"""
dsa/searching.py

Manual implementations of classic Data Structures & Algorithms (DSA) searching
techniques for ImageRecord collections in a satellite image catalog.

Supported Algorithms:
1. Linear Search (Sequential scan across all elements)
2. Binary Search (Divide and Conquer on pre-sorted datasets)

Supported Search Keys:
- "image_id" / "id"
- "image_name" / "name"
- "land_type" / "land type"
- "image_format" / "format"
- "date" / "datetime"
- Custom callable functions

Note:
- All searching algorithms are manually implemented without using Python's
  built-in search utilities, list.index(), or the 'in' operator as a search algorithm.
- Binary Search mathematically requires the dataset to be sorted by the search key.
- Each algorithm returns a tuple: (matching_records_list, total_comparisons_count).
"""

from typing import List, Tuple, Any, Callable, Union, Optional
import sys
import os

# Ensure the root project directory is on sys.path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.image_record import ImageRecord
from dsa.sorting import merge_sort


# ==============================================================================
# Helper Functions: Search Key Extraction & Value Normalization
# ==============================================================================

def get_search_key(record: ImageRecord, key: Union[str, Callable[[ImageRecord], Any]]) -> Any:
    """
    Extracts the comparable search value from an ImageRecord based on the requested key.

    Supported string keys:
    - "image_id", "id"
    - "image_name", "image name", "name", "filename"
    - "land_type", "land type", "landtype", "type"
    - "image_format", "image format", "format", "ext", "extension"
    - "date"
    - "datetime", "date & time", "date_time"
    - "file_size", "file size", "size", "bytes"

    Or a custom callable: key(record) -> Any
    """
    if callable(key):
        return key(record)

    if not isinstance(key, str):
        raise TypeError(f"Search key must be a string or callable, got {type(key).__name__}")

    normalized = key.strip().lower().replace(" ", "").replace("_", "").replace("&", "")

    if normalized in ("imageid", "id"):
        return str(record.image_id or "")

    elif normalized in ("imagename", "name", "filename"):
        return (record.image_name or "").lower()

    elif normalized in ("landtype", "land", "type"):
        return (record.land_type or "").lower()

    elif normalized in ("imageformat", "format", "ext", "extension"):
        return (record.image_format or "").lower()

    elif normalized == "date":
        return str(record.date or "")

    elif normalized in ("datetime", "dateandtime", "date_time"):
        if record.datetime:
            return record.datetime
        date_part = record.date or ""
        time_part = record.time or ""
        return f"{date_part} {time_part}".strip()

    elif normalized in ("filesize", "size", "bytes"):
        return record.file_size if record.file_size is not None else 0

    # Fallback to direct attribute lookup
    if hasattr(record, key):
        val = getattr(record, key)
        return val if val is not None else ""

    raise ValueError(
        f"Unsupported search key '{key}'. Supported: 'image_id', 'image_name', 'land_type', 'image_format', 'date', 'datetime', 'file_size'."
    )


def normalize_target_value(target: Any, key: Union[str, Callable[[ImageRecord], Any]]) -> Any:
    """
    Normalizes a search query target to match the format produced by get_search_key.
    For string keys like image_name, land_type, image_format, lowercases the target.
    """
    if callable(key) or not isinstance(key, str):
        return target

    normalized_key = key.strip().lower().replace(" ", "").replace("_", "").replace("&", "")

    if normalized_key in ("imagename", "name", "filename", "landtype", "land", "type", "imageformat", "format", "ext", "extension"):
        return str(target).strip().lower()

    if normalized_key in ("imageid", "id", "date", "datetime", "dateandtime", "date_time"):
        return str(target).strip()

    if normalized_key in ("filesize", "size", "bytes"):
        try:
            return int(target)
        except (ValueError, TypeError):
            return target

    return target


# ==============================================================================
# 1. Linear Search
# ==============================================================================

def linear_search(
    records: List[ImageRecord],
    target: Any,
    key: Union[str, Callable[[ImageRecord], Any]] = "image_name",
    find_all: bool = True,
) -> Tuple[List[ImageRecord], int]:
    """
    Performs a manual Linear Search across a list of ImageRecord objects.

    How Linear Search works:
    1. Start from the very first element (index 0) and proceed sequentially to index n - 1.
    2. Extract the key value of each ImageRecord.
    3. Compare the extracted value directly with the normalized target.
    4. If matched, append to results.
    5. If find_all is False, stop immediately upon finding the first match.
    6. Continue until all elements are inspected.

    Time Complexity:
    - Best Case (first element matches, find_all=False): O(1)
    - Average Case: O(n)
    - Worst Case: O(n)

    Space Complexity:
    - O(1) auxiliary space (O(k) where k is the number of matches returned).

    Parameters:
    - records: List of ImageRecord objects to search through.
    - target: The value to search for (e.g., "Forest", "jpg", "2026-01-15").
    - key: The field name or callable extractor to match against.
    - find_all: If True, returns all matching records; if False, stops after first match.

    Returns:
    - Tuple of (matching_records_list, total_comparisons_count)
    """
    comparisons = 0
    matches: List[ImageRecord] = []
    n = len(records)

    if n == 0:
        return matches, comparisons

    target_val = normalize_target_value(target, key)

    # Sequential scan through each element
    for i in range(n):
        current_record = records[i]
        current_val = get_search_key(current_record, key)
        comparisons += 1

        # Check for exact equality match
        if current_val == target_val:
            matches.append(current_record)
            if not find_all:
                break

    return matches, comparisons


# ==============================================================================
# 2. Binary Search
# ==============================================================================

def binary_search(
    records: List[ImageRecord],
    target: Any,
    key: Union[str, Callable[[ImageRecord], Any]] = "image_name",
    is_sorted: bool = False,
    find_all: bool = True,
) -> Tuple[List[ImageRecord], int]:
    """
    Performs a manual Binary Search on an ImageRecord collection.

    CRITICAL PREREQUISITE:
    Binary Search REQUIRES the input records list to be sorted according to
    the chosen search key in ascending order. If 'is_sorted' is False,
    the records will automatically be sorted using manual Merge Sort first.

    How Binary Search works:
    1. Maintain two boundary pointers: 'low' (0) and 'high' (n - 1).
    2. Compute the midpoint index: mid = (low + high) // 2.
    3. Compare the mid element's key with the target value:
       - If mid_val == target: match found!
       - If mid_val < target: search space narrows to the right half (low = mid + 1).
       - If mid_val > target: search space narrows to the left half (high = mid - 1).
    4. Repeat until low > high or a match is located.
    5. When duplicates exist and find_all is True:
       Expand left and right from the match index to gather all contiguous matches.

    Time Complexity:
    - Search Time (on pre-sorted data):
      - Best Case: O(1) (target is at the initial midpoint)
      - Average Case: O(log n)
      - Worst Case: O(log n) (+ O(k) expansion for k duplicates)
    - If sorting is needed first: O(n log n) via Merge Sort.

    Space Complexity:
    - O(1) auxiliary space (O(k) for returned matches list).

    Parameters:
    - records: List of ImageRecord objects.
    - target: The value to search for.
    - key: The field name or callable extractor to match against.
    - is_sorted: Set to True if caller guarantees the input list is already sorted by key.
                 If False, data is sorted via manual merge_sort first.
    - find_all: If True, returns all matching duplicate records; if False, returns the first found.

    Returns:
    - Tuple of (matching_records_list, total_comparisons_count)
    """
    comparisons = 0

    if len(records) == 0:
        return [], comparisons

    # Ensure data is sorted by the search key
    if not is_sorted:
        sorted_records, sort_comps = merge_sort(records, key=key, ascending=True)
    else:
        sorted_records = records

    n = len(sorted_records)
    target_val = normalize_target_value(target, key)

    low = 0
    high = n - 1
    match_index = -1

    # Standard Binary Search loop
    while low <= high:
        mid = (low + high) // 2
        mid_val = get_search_key(sorted_records[mid], key)
        comparisons += 1

        if mid_val == target_val:
            match_index = mid
            break
        elif mid_val < target_val:
            low = mid + 1
        else:
            high = mid - 1

    # No match found
    if match_index == -1:
        return [], comparisons

    # If only one match requested
    if not find_all:
        return [sorted_records[match_index]], comparisons

    # Find boundaries for duplicate values (contiguous in sorted array)
    left_bound = match_index
    while left_bound > 0:
        prev_val = get_search_key(sorted_records[left_bound - 1], key)
        comparisons += 1
        if prev_val == target_val:
            left_bound -= 1
        else:
            break

    right_bound = match_index
    while right_bound < n - 1:
        next_val = get_search_key(sorted_records[right_bound + 1], key)
        comparisons += 1
        if next_val == target_val:
            right_bound += 1
        else:
            break

    matches = sorted_records[left_bound : right_bound + 1]
    return matches, comparisons


# ==============================================================================
# 3. Multi-Criteria Filtering
# ==============================================================================

def filter_records(
    records: List[ImageRecord],
    land_type: Optional[str] = None,
    image_format: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Tuple[List[ImageRecord], int]:
    """
    Manually filters ImageRecord collections by combining multiple criteria:
    - land_type (e.g. "Forest", "Water", "Agriculture", "Urban", "Barren_Land", "Other" or "All")
    - image_format (e.g. "JPG", "JPEG", "PNG", "TIFF", "WEBP" or "All")
    - start_date ("YYYY-MM-DD" or None)
    - end_date ("YYYY-MM-DD" or None)

    All filters work together simultaneously using sequential comparison evaluation.

    Time Complexity:
    - O(n) linear scan across all records.

    Space Complexity:
    - O(k) for returning matching records.

    Returns:
    - Tuple of (filtered_records_list, total_comparisons_count)
    """
    comparisons = 0
    filtered: List[ImageRecord] = []

    norm_land = (
        land_type.strip().lower().replace(" ", "_")
        if land_type and land_type.strip().lower() != "all"
        else None
    )
    norm_fmt = (
        image_format.strip().lower()
        if image_format and image_format.strip().lower() != "all"
        else None
    )
    norm_start = start_date.strip() if start_date else None
    norm_end = end_date.strip() if end_date else None

    for record in records:
        match = True

        # Check Land Type
        if norm_land is not None:
            comparisons += 1
            rec_land = (record.land_type or "").strip().lower().replace(" ", "_")
            if rec_land != norm_land:
                match = False

        # Check Image Format
        if match and norm_fmt is not None:
            comparisons += 1
            rec_fmt = (record.image_format or "").strip().lower()
            if rec_fmt != norm_fmt:
                match = False

        # Check Start Date
        if match and norm_start:
            comparisons += 1
            rec_date = (record.date or "").strip()
            if not rec_date or rec_date < norm_start:
                match = False

        # Check End Date
        if match and norm_end:
            comparisons += 1
            rec_date = (record.date or "").strip()
            if not rec_date or rec_date > norm_end:
                match = False

        if match:
            filtered.append(record)

    return filtered, comparisons

