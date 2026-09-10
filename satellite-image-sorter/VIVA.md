# 🎓 College Viva Preparation Guide

## 🛰️ Satellite Image Sorter & Organizer
**Data Structures & Algorithms (DSA) Mini-Project**

This document contains 25 common viva examination questions with simple, direct answers designed for a 2nd-year computer science engineering student to explain naturally.

---

### Q1: What is a data structure?
**Answer:**  
A data structure is a specialized format for organizing, storing, and managing data in computer memory so that operations like searching, insertion, deletion, and sorting can be performed efficiently. In our project, we use arrays (lists), hash tables, and custom objects (`ImageRecord`).

---

### Q2: Why did you use an array/list data structure in this project?
**Answer:**  
We used Python lists (which are dynamic arrays under the hood) because satellite image catalog items need to be accessed quickly by index ($O(1)$ random access). Lists also provide contiguous memory layout, making them ideal for passing elements into sorting algorithms like Merge Sort, Quick Sort, and Bubble Sort.

---

### Q3: Why did you use Merge Sort in your project?
**Answer:**  
Merge Sort is a divide-and-conquer algorithm that guarantees $O(n \log n)$ time complexity in all cases (best, average, and worst). It is also a **stable** sorting algorithm, meaning if two satellite images have the exact same acquisition date, their original relative order is preserved after sorting.

---

### Q4: How does Merge Sort work step-by-step?
**Answer:**  
Merge Sort works in three steps:
1. **Divide**: Find the midpoint of the array and split it into two halves.
2. **Conquer**: Recursively divide and sort the left and right halves until sublists have a size of 1 or 0.
3. **Combine (Merge)**: Merge the two sorted halves back together in linear time by comparing their smallest elements one by one.

---

### Q5: How does Quick Sort work step-by-step?
**Answer:**  
Quick Sort is an in-place divide-and-conquer algorithm:
1. **Pivot Selection**: Pick a pivot element (we use the last element via Lomuto partitioning).
2. **Partitioning**: Rearrange the array so all items smaller than the pivot go to its left, and all items larger go to its right.
3. **Recursion**: Recursively apply the same steps to the left sub-array and right sub-array.

---

### Q6: What is the worst-case complexity of Quick Sort, and when does it happen?
**Answer:**  
The worst-case time complexity of Quick Sort is $O(n^2)$. This occurs when the chosen pivot is always the smallest or largest element (for example, when the array is already sorted or reverse-sorted and we pick the last element as pivot without shuffling).

---

### Q7: Why is Bubble Sort slower than Merge Sort and Quick Sort?
**Answer:**  
Bubble Sort compares adjacent elements and swaps them repeatedly. It takes $O(n^2)$ time on average because it makes up to $\frac{n(n-1)}{2}$ comparisons. In contrast, Merge Sort and Quick Sort use divide-and-conquer to reduce the work to $O(n \log n)$, which is exponentially faster for larger datasets.

---

### Q8: What is Linear Search, and when is it useful?
**Answer:**  
Linear Search scans a collection element-by-element from start to end until a match is found. Its time complexity is $O(n)$. It is useful because it requires **no pre-conditions**—it works on completely unsorted and raw dataset collections.

---

### Q9: What is Binary Search, and what is its main prerequisite?
**Answer:**  
Binary Search is a divide-and-conquer search algorithm with logarithmic time complexity $O(\log n)$. Its strict prerequisite is that **the dataset must be pre-sorted** according to the search key before performing the search.

---

### Q10: Why does Binary Search strictly require sorted data?
**Answer:**  
Binary Search eliminates half of the remaining items at each step by comparing the target with the midpoint element. If the array is not sorted, knowing whether the target is greater or smaller than the midpoint tells us nothing about which side the target lives on, causing the algorithm to fail.

---

### Q11: What is hashing?
**Answer:**  
Hashing is a technique that uses a mathematical formula (a hash function) to convert an input key (like a string `'SAT001'`) into an integer index. This index directly points to a slot in a table, enabling average $O(1)$ constant-time insertion, lookup, and deletion.

---

### Q12: What is a hash collision, and how did you resolve it?
**Answer:**  
A hash collision occurs when two different keys generate the exact same hash index from the hash function. In our project, we resolved collisions using **Separate Chaining**, where each bucket in the hash table contains a list (chain) of `(key, value)` pairs that share that bucket index.

---

### Q13: What is time complexity?
**Answer:**  
Time complexity measures how the execution time of an algorithm grows as the size of the input data ($n$) increases. It is expressed using Big-O notation (e.g., $O(1)$, $O(\log n)$, $O(n)$, $O(n \log n)$, $O(n^2)$) to describe upper bounds.

---

### Q14: What is space complexity?
**Answer:**  
Space complexity measures the total amount of auxiliary memory or stack space an algorithm requires relative to the input size ($n$). For example, Merge Sort requires $O(n)$ extra memory to merge arrays, while Bubble Sort requires $O(1)$ auxiliary space (in-place).

---

### Q15: Where exactly is DSA used in this project?
**Answer:**  
DSA is used in four main core modules:
1. **`dsa/sorting.py`**: Manual Merge Sort, Quick Sort, and Bubble Sort for ordering image records by date, format, land type, or file size.
2. **`dsa/searching.py`**: Manual Linear Search and Binary Search for matching queries against image attributes.
3. **`dsa/hashing.py`**: Manual Separate Chaining Hash Table (`ImageHashTable`) for $O(1)$ record indexing by `image_id`.
4. **Predicate Filtering**: Single-pass $O(n)$ multi-attribute filter checking land type, format, and date ranges.

---

### Q16: Why is this project classified as a DSA project?
**Answer:**  
Because all data manipulation logic (sorting, searching, indexing, filtering) was written from first principles in Python without using standard library sort routines (`sorted()`, `list.sort()`) or external database systems. The project actively tracks comparison counters and execution timing to analyze theoretical vs empirical DSA complexity.

---

### Q17: Why didn't you use AI/ML for image land type classification?
**Answer:**  
The focus of this project is fundamental Data Structures & Algorithms. Machine Learning models act as a black box for computer vision, whereas this mini-project highlights deterministic algorithm design, time complexity analysis, partitioning, searching bounds, and memory structures required in core computer science curricula.

---

### Q18: How is the land type obtained for each satellite image?
**Answer:**  
Land type is extracted automatically during upload by parsing standard filename strings (e.g., `2026-01-15_14-30_Forest.jpg` $\rightarrow$ `Forest`). If a file does not follow the convention, it is assigned `"Other"`, and the user can update the land type manually using the UI form.

---

### Q19: How does metadata parsing work?
**Answer:**  
When an image is ingested, `services/metadata_parser.py` uses regular expressions and string split routines to extract date components (`YYYY-MM-DD`), time components (`HH-MM`), and land classification keywords. File size and image dimensions (width $\times$ height) are extracted using Pillow (`PIL.Image`).

---

### Q20: What is algorithm stability, and why does it matter here?
**Answer:**  
An algorithm is stable if it preserves the relative order of elements that have equal key values. For example, if two images have the exact same acquisition date, a stable sort like Merge Sort keeps them in their original upload order, whereas an unstable sort like Quick Sort might swap them.

---

### Q21: What does it mean for an algorithm to sort "in-place"?
**Answer:**  
An in-place sorting algorithm rearranges items directly within the original array without creating full duplicate copies, using only a small constant amount ($O(1)$ or $O(\log n)$ call stack) of extra memory. Quick Sort and Bubble Sort sort in-place, whereas Merge Sort needs $O(n)$ auxiliary array memory.

---

### Q22: What partitioning scheme is used in your Quick Sort?
**Answer:**  
We use **Lomuto Partitioning**. It picks the last element as the pivot, maintains an index `i` for elements smaller than the pivot, iterates through the array with index `j`, swaps smaller elements into position `i`, and finally swaps the pivot to `i + 1`.

---

### Q23: How does your Hash Table handle dynamic resizing (rehashing)?
**Answer:**  
When the load factor ($\frac{\text{size}}{\text{capacity}}$) exceeds $0.75$, `ImageHashTable` automatically doubles its capacity ($2 \times \text{capacity}$), creates a new array of empty bucket chains, and re-hashes all existing key-value pairs into the new table slots.

---

### Q24: How does Binary Search handle multiple records with identical search keys?
**Answer:**  
Once Binary Search locates any matching record at index `mid`, it performs a linear expansion scan to both the left (`mid - 1`, `mid - 2`...) and right (`mid + 1`, `mid + 2`...) to collect all contiguous records sharing the target key.

---

### Q25: How do you measure execution performance in your project?
**Answer:**  
We measure performance using Python's high-resolution timer (`time.perf_counter()`) before and after running each algorithm, calculating elapsed execution time in milliseconds (`ms`) and microseconds (`µs`). We also increment a manual `comparison_count` counter inside each algorithm loop to record exact comparison operations.
