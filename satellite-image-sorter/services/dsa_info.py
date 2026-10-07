"""
services/dsa_info.py

Educational specifications and Viva reference data for all Data Structures & Algorithms
implemented in the Satellite Image Sorter & Organizer.
"""

from typing import Dict, Any, List

SORTING_SPECIFICATIONS: Dict[str, Any] = {
    "Merge Sort": {
        "name": "Merge Sort",
        "category": "Divide and Conquer",
        "stability": "Stable (preserves relative order of equal keys)",
        "in_place": False,
        "best_time": "O(n log n)",
        "avg_time": "O(n log n)",
        "worst_time": "O(n log n)",
        "space_complexity": "O(n) auxiliary",
        "purpose": "Divide-and-conquer sorting technique designed for guaranteed O(n log n) time complexity and stable element ordering.",
        "steps": [
            "Divide: Recursively halves the list around the midpoint until sublists contain 0 or 1 element.",
            "Conquer: Recursively sorts the left and right sublists.",
            "Combine (Merge): Merges the two sorted halves in linear time by repeatedly comparing their smallest elements.",
        ],
        "project_application": "Guarantees predictable sorting performance on large satellite catalogs regardless of initial data order.",
    },
    "Quick Sort": {
        "name": "Quick Sort",
        "category": "Partition-based Divide and Conquer",
        "stability": "Unstable (may rearrange equal elements during partitioning)",
        "in_place": True,
        "best_time": "O(n log n)",
        "avg_time": "O(n log n)",
        "worst_time": "O(n²)",
        "space_complexity": "O(log n) call stack (O(n) worst case)",
        "purpose": "High-efficiency divide-and-conquer algorithm that sorts elements in-place using pivot partitioning.",
        "steps": [
            "Pivot Selection: Selects a pivot element (last element via Lomuto partitioning).",
            "Partitioning: Reorganizes the array so all items smaller than or equal to the pivot precede it, and larger items follow it.",
            "Recursion: Recursively applies the partition step to the left and right subarrays.",
        ],
        "project_application": "Provides maximum in-memory sorting throughput when auxiliary RAM is limited.",
    },
    "Bubble Sort": {
        "name": "Bubble Sort",
        "category": "Comparison-based Adjacent Element Swapping",
        "stability": "Stable",
        "in_place": True,
        "best_time": "O(n) (when already sorted with early exit)",
        "avg_time": "O(n²)",
        "worst_time": "O(n²)",
        "space_complexity": "O(1) auxiliary",
        "purpose": "Classic comparison-based sorting technique that bubbles elements to their correct position through adjacent swaps.",
        "steps": [
            "Passes: Iterates through the list n - 1 times.",
            "Adjacent Comparison: Compares adjacent elements arr[j] and arr[j + 1].",
            "Swapping: Swaps out-of-order adjacent elements.",
            "Early Exit Optimization: If a full pass completes with 0 swaps, halts early in O(n) time.",
        ],
        "project_application": "Serves as an educational baseline demonstrating quadratic O(n²) behavior against O(n log n) algorithms.",
    },
}

SEARCHING_SPECIFICATIONS: Dict[str, Any] = {
    "Linear Search": {
        "name": "Linear Search",
        "category": "Sequential Scan",
        "prerequisite": "None (Works on unsorted data)",
        "best_time": "O(1) (target at index 0)",
        "avg_time": "O(n)",
        "worst_time": "O(n)",
        "space_complexity": "O(1) auxiliary",
        "purpose": "Sequential scan examining elements one-by-one from index 0 to n - 1.",
        "steps": [
            "Iterates through the collection sequentially from index 0 to n - 1.",
            "Extracts key from current ImageRecord and compares with normalized query target.",
            "Collects all matching items (or stops early if find_all is False).",
        ],
        "project_application": "Universal attribute search across newly ingested or unsorted satellite imagery.",
    },
    "Binary Search": {
        "name": "Binary Search",
        "category": "Logarithmic Divide and Conquer",
        "prerequisite": "Strictly requires dataset sorted by search key in ascending order",
        "best_time": "O(1) (target at initial midpoint)",
        "avg_time": "O(log n)",
        "worst_time": "O(log n)",
        "space_complexity": "O(1) auxiliary",
        "purpose": "Logarithmic divide-and-conquer search halving the remaining search space with each comparison.",
        "steps": [
            "Maintains low and high pointers.",
            "Computes midpoint: mid = (low + high) // 2.",
            "Compares mid value to target; narrows search window to left or right half.",
            "Upon match, linearly expands left and right to gather all contiguous duplicate keys.",
        ],
        "project_application": "Sub-millisecond lookup on indexed or pre-sorted satellite collections.",
    },
}

HASHING_SPECIFICATIONS: Dict[str, Any] = {
    "name": "ImageHashTable",
    "structure": "Hash Table with Separate Chaining",
    "hash_function": "Polynomial rolling hash: hash = (hash * 31 + ord(char)) % capacity",
    "collision_resolution": "Separate Chaining (linked bucket chains of (key, value) pairs)",
    "load_factor_threshold": 0.75,
    "resizing_strategy": "Dynamic resizing: doubles capacity (2 * capacity) and rehashes all elements",
    "time_complexity": {
        "insert": {"average": "O(1)", "worst": "O(n)"},
        "search": {"average": "O(1)", "worst": "O(n)"},
        "delete": {"average": "O(1)", "worst": "O(n)"},
    },
    "space_complexity": "O(n + m) where n is elements count and m is bucket capacity",
    "project_application": "Instant O(1) random access retrieval of ImageRecord objects by image_id (e.g. 'SAT001').",
}

FILTERING_SPECIFICATIONS: Dict[str, Any] = {
    "name": "Multi-Criteria Predicate Filtering",
    "time_complexity": "O(n) linear scan",
    "space_complexity": "O(k) where k is matches returned",
    "purpose": "Filters catalog simultaneously by Land Type, Image Format, Start Date, and End Date in a single pass.",
}

VIVA_QUESTIONS: List[Dict[str, str]] = [
    {
        "q": "Q1: What is a data structure?",
        "a": "A data structure is a specialized format for organizing, storing, and managing data in memory so that operations like searching, insertion, deletion, and sorting can be performed efficiently. In our project, we use dynamic arrays (lists), hash tables (ImageHashTable), and custom ImageRecord objects.",
    },
    {
        "q": "Q2: Why did you use Merge Sort in your project?",
        "a": "Merge Sort provides guaranteed O(n log n) time complexity across all cases (best, average, worst). It is also stable, ensuring that two images with the exact same date maintain their relative upload ordering.",
    },
    {
        "q": "Q3: How does Merge Sort work step-by-step?",
        "a": "1. Divide: Halve array around midpoint. 2. Conquer: Recursively divide and sort both halves until sublists are size 0 or 1. 3. Combine (Merge): Linearly merge sorted halves by comparing smallest remaining elements.",
    },
    {
        "q": "Q4: How does Quick Sort work step-by-step?",
        "a": "1. Pivot Selection: Choose pivot (last item via Lomuto partitioning). 2. Partitioning: Rearrange array so all items smaller than pivot are left, larger are right. 3. Recursion: Recursively apply Quick Sort to left and right subarrays.",
    },
    {
        "q": "Q5: What is the worst-case complexity of Quick Sort, and when does it happen?",
        "a": "Worst-case is O(n²). It occurs when the pivot chosen is always the extreme minimum or maximum element, such as sorting an already sorted or reverse-sorted list without pivot randomization.",
    },
    {
        "q": "Q6: Why is Bubble Sort slower than Merge Sort and Quick Sort?",
        "a": "Bubble Sort compares adjacent elements and swaps them, resulting in up to n(n-1)/2 comparisons and O(n²) time. Merge Sort and Quick Sort use divide-and-conquer to achieve O(n log n), which is exponentially faster on larger collections.",
    },
    {
        "q": "Q7: What is Linear Search, and when is it useful?",
        "a": "Linear Search sequentially inspects elements from index 0 to n - 1. Time complexity is O(n). It requires no prerequisites and works on completely unsorted datasets.",
    },
    {
        "q": "Q8: What is Binary Search, and what is its main prerequisite?",
        "a": "Binary Search is a divide-and-conquer search with O(log n) time complexity. Its strict prerequisite is that the dataset MUST be pre-sorted according to the search key.",
    },
    {
        "q": "Q9: What is hashing?",
        "a": "Hashing transforms an arbitrary search key (like string 'SAT001') into an integer bucket index using a mathematical hash function, providing O(1) average constant-time insertion, lookup, and deletion.",
    },
    {
        "q": "Q10: What is a hash collision, and how did you resolve it?",
        "a": "A collision occurs when two distinct keys produce the same bucket index. In our project, ImageHashTable uses Separate Chaining, storing a list of (key, value) pairs in each bucket.",
    },
    {
        "q": "Q11: How does your Hash Table handle dynamic resizing?",
        "a": "When the load factor (size / capacity) exceeds 0.75, ImageHashTable automatically doubles capacity (2 * capacity) and rehashes all existing entries into new buckets.",
    },
    {
        "q": "Q12: Why is this project classified as a pure DSA project?",
        "a": "All sorting, searching, indexing, and filtering algorithms were implemented manually from scratch in Python without using standard library routines (sorted(), list.sort()) or database engines. Comparison counters and high-resolution timing are actively measured.",
    },
    {
        "q": "Q13: What is algorithm stability?",
        "a": "An algorithm is stable if it preserves the relative order of elements that have equal key values. Merge Sort is stable, while Quick Sort is unstable.",
    },
    {
        "q": "Q14: How does Binary Search handle multiple records with identical keys?",
        "a": "Upon finding a match at index mid, it expands outward linearly to both left and right adjacent slots to collect all contiguous records sharing the target key.",
    },
    {
        "q": "Q15: How do you measure execution performance in your project?",
        "a": "Using time.perf_counter() before and after execution to measure elapsed milliseconds and microseconds, and tracking an integer comparison counter inside each algorithm loop.",
    },
]


def get_all_dsa_info() -> Dict[str, Any]:
    """Returns the complete educational DSA specifications dictionary."""
    return {
        "sorting": SORTING_SPECIFICATIONS,
        "searching": SEARCHING_SPECIFICATIONS,
        "hashing": HASHING_SPECIFICATIONS,
        "filtering": FILTERING_SPECIFICATIONS,
        "viva_questions": VIVA_QUESTIONS,
    }
