# Sliding window patterns: the exhaustive target list

The target list of every sliding-window pattern that can come up on LeetCode, for the Sliding Window pattern lesson. The rule is in
[DSA.md](DSA.md), decision 32: a topic's patterns section is exhaustive, patterns without a NeetCode problem get **example problems**
from LeetCode, and variants of one pattern are **tabs** of one lesson. The model is [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md).

Status: documented only. Today `content/dsa/lessons/sliding-window.toml` has 9 techniques (running-best, fixed-sum, window-max,
fixed-window, at-most-k, window-sort, count-windows, window-min, mono-deque). Building the rest needs a mockup of the tabs first
(rule 13 of the working rules), then lessons and picked example problems, each checked against LeetCode and never written from memory.

Items written *a / b* in a group are variants for tabs where one lesson covers both. A group's items are the patterns in the
"Example problems" section below, one for one.

1. **Fixed-size window.** Fixed-size sum / average; Fixed-size count of a property (vowels, ones); Fixed-size minimise changes (recolours, swaps, flips); Fixed-size with a set / count map of distinct values; Fixed-size rule between neighbours (consecutive, sorted, alternating); Running best so far (one-pass buy / sell).
2. **Variable window, longest valid.** Shrink while invalid (no repeats, frequency limit); At most K distinct; Non-shrinking window (slide instead of shrink); Longest with one deletion / one flip allowed; Longest with a per-character count condition (try each distinct-count target); Longest run: reset the window when a neighbour rule breaks; Window over a bitwise rule (bit counts).
3. **Variable window, shortest valid.** Shrink while still valid (sum at least a target); Shortest window containing everything required; Take from both ends = keep a middle window of the complement; Shortest with a tie-break (lexicographic, earliest).
4. **Counting windows (atMost(k) - atMost(k-1)).** Subarrays ending at right (count += right - left + 1); Exactly K as atMost(K) - atMost(K-1); At least K: once valid, every longer window is valid (count += left, or n - right); Counting with last-seen positions (bounds, no shrinking); Counting good pairs inside the window.
5. **Frequency (need / have) windows.** Need / have counts with a satisfied counter (cover a target); Fixed-size anagram / permutation match; Word-level window (slide by word length, several offsets); Cover every distinct kind; Per-value count cap inside the window.
6. **Windows over two sequences.** Cover elements from K sorted lists (merge into one sequence); Common subarray of two arrays (slide one against the other); Rolling hash of fixed windows (repeats, pattern in text); Window over a text against a target pattern; Two-pointer windows across two sorted sequences (interval lists).
7. **Circular arrays.** Double the array (index modulo n); Circular maximum subarray (total minus minimum, or prefix sums plus deque); Infinite repeated array (whole copies plus a window); Circular groups with wrap-around windows.
8. **Monotonic-queue windows.** Window maximum / minimum (decreasing deque of indices); Two deques (max and min) for a range limit; Deque-optimised DP (best of the last K states); Prefix sums plus deque (shortest subarray with sum at least K); Deque inside a budget window (max cost + K * sum).
9. **Ordered-set / heap windows.** Two heaps with lazy deletion (window median); Ordered set / multiset (nearest value in the window); Heap with lazy deletion (window maximum); Counting array over a small value range (K-th smallest in the window); Bucket by value range (near-duplicate detection); Sorted window with a binary-searched edge.
10. **Negative numbers (when windows fail: prefix sums).** Why shrinking fails: the sum is not monotone; Prefix sums + hash map (count subarrays with sum K); Prefix sums + monotonic deque; Kadane / best window ending here; Prefix sums + binary search (non-negative values only).
11. **Binary search on window size.** Binary search the answer, check feasibility with one window pass; Binary search the left edge on a sorted array; Binary search over prefix sums (non-negative values).
12. **Character-budget windows.** Replacement budget (window size - max frequency <= K); Flip budget (at most K zeros); Cost budget (sum of per-position costs <= budget); Operation budget on sorted values (size x max - sum <= K); Swap budget around a median.
13. **2-D windows.** Fixed-size submatrix sums (2-D prefix sums); Collapse row pairs to 1-D, then window or hash; Largest square / rectangle (grow the window in two directions); Maximum-sum rectangle no larger than K; K x K maximum by two passes of 1-D deques.
14. **Sorted-input windows (sort first, then slide).** Sort, then a window of K; Sort, then a range (max - min <= limit); Consecutive-values window (distinct count in a range of n); Gap windows (stones, points by position).
15. **Window as a helper for DP and greedy.** Several non-overlapping windows (best left + best right); Greedy flips with a queue or difference array; DP with a running window sum; Windows over derived sequences (positions, intervals, gaps).
16. **Core implementation patterns.** Left / right pointers with a window that is inclusive on both ends (size = right - left + 1); count map with delete-at-zero; need / have with a satisfied counter; running window sum; last-seen index map (jump left past a repeat); decreasing deque of indices (pop the front when it leaves, pop the back while dominated); init the first window, then slide; an atMost(k) helper called twice; doubling the array or index modulo n; prefix-sum array and prefix-sum hash map; lazy deletion in a heap; guard k > n and k = 0; do not shrink on invalid (record only a larger size); choose the loop shape (for right in range, while left) and the order: add right, shrink left, then record.

## Coverage today

- `problems.json` and `practice.json` hold 77 problems whose pattern is Sliding Window (9 must-learn, 68 practice;
  9 easy, 56 medium, 12 hard). Another 17 problems carry the "Sliding Window" tag but belong to
  other patterns (Greedy 7, 1-D Dynamic Programming 3, Arrays & Hashing 2, Bit Manipulation 2, Heap / Priority Queue 2, Stack 1, Binary Search 1, 2-D Dynamic Programming 1); 94 problems carry the tag in all.
- NeetCode 150 has 6 sliding-window problems: LeetCode 3, 76, 121, 239, 424 and 567. NeetCode 250 adds 209, 219 and 658.
- Problems per technique today: fixed-window 12, count-windows 11, fixed-sum 10, window-min 9,
  window-sort 9, at-most-k 8, window-max 7, mono-deque 6, running-best 5.
- The 9 techniques map to the groups like this: running-best and fixed-sum to group 1; window-max (longest valid) to group 2;
  window-min (shortest valid) to group 3; count-windows to group 4; fixed-window (anagram match) to group 5; at-most-k to group 2 (at most K distinct);
  window-sort (a window on sorted input, K closest) to groups 11 and 14; mono-deque to group 8.
- Groups 6, 7, 9, 10, 12 (except the replacement budget), 13 and 15 have no lesson at all, and group 11 has no binary-search-on-size lesson.
- Every group has at least one problem in the data; the 3 patterns with none are listed in Gaps.


## Example problems per pattern

Up to 4 per pattern, taken only from `problems.json` and `practice.json` (blind75 and neetcode150 first, then neetcode250, all, practice). Format: `LeetCode <number> <title> (<difficulty>; <lists>)`. The core implementation group has no problems of its own. A problem may appear under several patterns when it teaches both.

### 1. Fixed-size window

- **Fixed-size sum / average**
    - LeetCode 1052 Grumpy Bookstore Owner (medium; all)
    - LeetCode 1343 Number of Sub-arrays of Size K and Average Greater than or Equal to Threshold (medium; all)
    - LeetCode 2461 Maximum Sum of Distinct Subarrays With Length K (medium; all)
    - LeetCode 643 Maximum Average Subarray I (easy; practice)
- **Fixed-size count of a property (vowels, ones)**
    - LeetCode 1456 Maximum Number of Vowels in a Substring of Given Length (medium; all)
- **Fixed-size minimise changes (recolours, swaps, flips)**
    - LeetCode 1888 Minimum Number of Flips to Make the Binary String Alternating (medium; all)
    - LeetCode 2134 Minimum Swaps to Group All 1's Together II (medium; all)
    - LeetCode 2379 Minimum Recolors to Get K Consecutive Black Blocks (easy; all)
- **Fixed-size with a set / count map of distinct values**
    - LeetCode 219 Contains Duplicate II (easy; neetcode250, all)
    - LeetCode 1100 Find K-Length Substrings With No Repeated Characters (medium; all)
    - LeetCode 2461 Maximum Sum of Distinct Subarrays With Length K (medium; all)
    - LeetCode 2653 Sliding Subarray Beauty (medium; practice)
- **Fixed-size rule between neighbours (consecutive, sorted, alternating)**
    - LeetCode 3208 Alternating Groups II (medium; all)
    - LeetCode 3254 Find the Power of K-Size Subarrays I (medium; all)
    - LeetCode 3255 Find the Power of K-Size Subarrays II (medium; practice)
- **Running best so far (one-pass buy / sell)**
    - LeetCode 121 Best Time to Buy and Sell Stock (easy; blind75, neetcode150, neetcode250, all)

### 2. Variable window, longest valid

- **Shrink while invalid (no repeats, frequency limit)**
    - LeetCode 3 Longest Substring Without Repeating Characters (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 2958 Length of Longest Subarray With at Most K Frequency (medium; all)
    - LeetCode 1695 Maximum Erasure Value (medium; practice)
    - LeetCode 3090 Maximum Length Substring With Two Occurrences (easy; practice)
- **At most K distinct**
    - LeetCode 159 Longest Substring with At Most Two Distinct Characters (medium; all)
    - LeetCode 340 Longest Substring with At Most K Distinct Characters (medium; all)
    - LeetCode 904 Fruit Into Baskets (medium; all)
- **Non-shrinking window (slide instead of shrink)**
    - LeetCode 424 Longest Repeating Character Replacement (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 1004 Max Consecutive Ones III (medium; all)
    - LeetCode 2024 Maximize the Confusion of an Exam (medium; practice)
- **Longest with one deletion / one flip allowed**
    - LeetCode 487 Max Consecutive Ones II (medium; all)
    - LeetCode 1156 Swap For Longest Repeated Character Substring (medium; practice)
    - LeetCode 1493 Longest Subarray of 1's After Deleting One Element (medium; practice)
- **Longest with a per-character count condition (try each distinct-count target)**
    - LeetCode 395 Longest Substring with At Least K Repeating Characters (medium; practice)
- **Longest run: reset the window when a neighbour rule breaks**
    - LeetCode 978 Longest Turbulent Subarray (medium; neetcode250, all)
    - LeetCode 413 Arithmetic Slices (medium; practice)
    - LeetCode 1839 Longest Substring Of All Vowels in Order (medium; practice)
    - LeetCode 2760 Longest Even Odd Subarray With Threshold (easy; practice)
- **Window over a bitwise rule (bit counts)**
    - LeetCode 2401 Longest Nice Subarray (medium; all)
    - LeetCode 3097 Shortest Subarray With OR at Least K II (medium; all)

### 3. Variable window, shortest valid

- **Shrink while still valid (sum at least a target)**
    - LeetCode 209 Minimum Size Subarray Sum (medium; neetcode250, all)
    - LeetCode 3097 Shortest Subarray With OR at Least K II (medium; all)
    - LeetCode 2904 Shortest and Lexicographically Smallest Beautiful String (medium; practice)
- **Shortest window containing everything required**
    - LeetCode 76 Minimum Window Substring (hard; blind75, neetcode150, neetcode250, all)
    - LeetCode 632 Smallest Range Covering Elements from K Lists (hard; all)
    - LeetCode 2904 Shortest and Lexicographically Smallest Beautiful String (medium; practice)
- **Take from both ends = keep a middle window of the complement**
    - LeetCode 1423 Maximum Points You Can Obtain from Cards (medium; all)
    - LeetCode 1658 Minimum Operations to Reduce X to Zero (medium; all)
    - LeetCode 2516 Take K of Each Character From Left and Right (medium; all)
- **Shortest with a tie-break (lexicographic, earliest)**
    - LeetCode 2904 Shortest and Lexicographically Smallest Beautiful String (medium; practice)

### 4. Counting windows (atMost(k) - atMost(k-1))

- **Subarrays ending at right (count += right - left + 1)**
    - LeetCode 713 Subarray Product Less Than K (medium; all)
    - LeetCode 2110 Number of Smooth Descent Periods of a Stock (medium; practice)
    - LeetCode 2302 Count Subarrays With Score Less Than K (hard; practice)
    - LeetCode 2762 Continuous Subarrays (medium; practice)
- **Exactly K as atMost(K) - atMost(K-1)**
    - LeetCode 930 Binary Subarrays With Sum (medium; all)
    - LeetCode 992 Subarrays with K Different Integers (hard; all)
    - LeetCode 1248 Count Number of Nice Subarrays (medium; all)
- **At least K: once valid, every longer window is valid (count += left, or n - right)**
    - LeetCode 1358 Number of Substrings Containing All Three Characters (medium; all)
    - LeetCode 2962 Count Subarrays Where Max Element Appears at Least K Times (medium; all)
    - LeetCode 3306 Count of Substrings Containing Every Vowel and K Consonants II (medium; all)
    - LeetCode 2799 Count Complete Subarrays in an Array (medium; practice)
- **Counting with last-seen positions (bounds, no shrinking)**
    - LeetCode 2444 Count Subarrays With Fixed Bounds (hard; practice)
- **Counting good pairs inside the window**
    - LeetCode 2537 Count the Number of Good Subarrays (medium; practice)

### 5. Frequency (need / have) windows

- **Need / have counts with a satisfied counter (cover a target)**
    - LeetCode 76 Minimum Window Substring (hard; blind75, neetcode150, neetcode250, all)
    - LeetCode 1358 Number of Substrings Containing All Three Characters (medium; all)
    - LeetCode 3297 Count Substrings That Can Be Rearranged to Contain a String I (medium; practice)
- **Fixed-size anagram / permutation match**
    - LeetCode 567 Permutation in String (medium; neetcode150, neetcode250, all)
    - LeetCode 438 Find All Anagrams in a String (medium; all)
- **Word-level window (slide by word length, several offsets)**
    - LeetCode 30 Substring with Concatenation of All Words (hard; practice)
- **Cover every distinct kind**
    - LeetCode 1358 Number of Substrings Containing All Three Characters (medium; all)
    - LeetCode 3306 Count of Substrings Containing Every Vowel and K Consonants II (medium; all)
    - LeetCode 2799 Count Complete Subarrays in an Array (medium; practice)
- **Per-value count cap inside the window**
    - LeetCode 2958 Length of Longest Subarray With at Most K Frequency (medium; all)

### 6. Windows over two sequences

- **Cover elements from K sorted lists (merge into one sequence)**
    - LeetCode 632 Smallest Range Covering Elements from K Lists (hard; all)
- **Common subarray of two arrays (slide one against the other)**
    - LeetCode 718 Maximum Length of Repeated Subarray (medium; practice)
- **Rolling hash of fixed windows (repeats, pattern in text)**
    - LeetCode 187 Repeated DNA Sequences (medium; all)
    - LeetCode 30 Substring with Concatenation of All Words (hard; practice)
    - LeetCode 718 Maximum Length of Repeated Subarray (medium; practice)
- **Window over a text against a target pattern**
    - LeetCode 76 Minimum Window Substring (hard; blind75, neetcode150, neetcode250, all)
    - LeetCode 567 Permutation in String (medium; neetcode150, neetcode250, all)
    - LeetCode 438 Find All Anagrams in a String (medium; all)
- **Two-pointer windows across two sorted sequences (interval lists)**: no problem in the data: needs one from LeetCode.

### 7. Circular arrays

- **Double the array (index modulo n)**
    - LeetCode 1652 Defuse the Bomb (easy; all)
    - LeetCode 1888 Minimum Number of Flips to Make the Binary String Alternating (medium; all)
    - LeetCode 2134 Minimum Swaps to Group All 1's Together II (medium; all)
    - LeetCode 3208 Alternating Groups II (medium; all)
- **Circular maximum subarray (total minus minimum, or prefix sums plus deque)**
    - LeetCode 918 Maximum Sum Circular Subarray (medium; neetcode250, all)
- **Infinite repeated array (whole copies plus a window)**
    - LeetCode 2875 Minimum Size Subarray in Infinite Array (medium; practice)
- **Circular groups with wrap-around windows**
    - LeetCode 3208 Alternating Groups II (medium; all)
    - LeetCode 3206 Alternating Groups I (easy; practice)

### 8. Monotonic-queue windows

- **Window maximum / minimum (decreasing deque of indices)**
    - LeetCode 239 Sliding Window Maximum (hard; neetcode150, neetcode250, all)
    - LeetCode 1438 Longest Continuous Subarray With Absolute Diff Less Than or Equal to Limit (medium; all)
    - LeetCode 2762 Continuous Subarrays (medium; practice)
- **Two deques (max and min) for a range limit**
    - LeetCode 1438 Longest Continuous Subarray With Absolute Diff Less Than or Equal to Limit (medium; all)
    - LeetCode 2762 Continuous Subarrays (medium; practice)
    - LeetCode 3578 Count Partitions With Max-Min Difference at Most K (medium; practice)
- **Deque-optimised DP (best of the last K states)**
    - LeetCode 1425 Constrained Subsequence Sum (hard; all)
    - LeetCode 1696 Jump Game VI (medium; practice)
    - LeetCode 3578 Count Partitions With Max-Min Difference at Most K (medium; practice)
- **Prefix sums plus deque (shortest subarray with sum at least K)**
    - LeetCode 862 Shortest Subarray with Sum at Least K (hard; all)
- **Deque inside a budget window (max cost + K * sum)**
    - LeetCode 2398 Maximum Number of Robots Within Budget (hard; practice)

### 9. Ordered-set / heap windows

- **Two heaps with lazy deletion (window median)**
    - LeetCode 480 Sliding Window Median (hard; practice)
- **Ordered set / multiset (nearest value in the window)**
    - LeetCode 1438 Longest Continuous Subarray With Absolute Diff Less Than or Equal to Limit (medium; all)
    - LeetCode 220 Contains Duplicate III (hard; practice)
- **Heap with lazy deletion (window maximum)**
    - LeetCode 239 Sliding Window Maximum (hard; neetcode150, neetcode250, all)
    - LeetCode 1438 Longest Continuous Subarray With Absolute Diff Less Than or Equal to Limit (medium; all)
- **Counting array over a small value range (K-th smallest in the window)**
    - LeetCode 2653 Sliding Subarray Beauty (medium; practice)
- **Bucket by value range (near-duplicate detection)**
    - LeetCode 220 Contains Duplicate III (hard; practice)
- **Sorted window with a binary-searched edge**
    - LeetCode 658 Find K Closest Elements (medium; neetcode250, all)

### 10. Negative numbers (when windows fail: prefix sums)

- **Why shrinking fails: the sum is not monotone**
    - LeetCode 560 Subarray Sum Equals K (medium; neetcode250, all)
    - LeetCode 862 Shortest Subarray with Sum at Least K (hard; all)
- **Prefix sums + hash map (count subarrays with sum K)**
    - LeetCode 560 Subarray Sum Equals K (medium; neetcode250, all)
    - LeetCode 523 Continuous Subarray Sum (medium; all)
    - LeetCode 930 Binary Subarrays With Sum (medium; all)
    - LeetCode 974 Subarray Sums Divisible by K (medium; all)
- **Prefix sums + monotonic deque**
    - LeetCode 862 Shortest Subarray with Sum at Least K (hard; all)
- **Kadane / best window ending here**
    - LeetCode 53 Maximum Subarray (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 918 Maximum Sum Circular Subarray (medium; neetcode250, all)
- **Prefix sums + binary search (non-negative values only)**
    - LeetCode 209 Minimum Size Subarray Sum (medium; neetcode250, all)
    - LeetCode 713 Subarray Product Less Than K (medium; all)
    - LeetCode 1208 Get Equal Substrings Within Budget (medium; all)

### 11. Binary search on window size

- **Binary search the answer, check feasibility with one window pass**
    - LeetCode 718 Maximum Length of Repeated Subarray (medium; practice)
    - LeetCode 2398 Maximum Number of Robots Within Budget (hard; practice)
    - LeetCode 2528 Maximize the Minimum Powered City (hard; practice)
- **Binary search the left edge on a sorted array**
    - LeetCode 658 Find K Closest Elements (medium; neetcode250, all)
    - LeetCode 1838 Frequency of the Most Frequent Element (medium; all)
- **Binary search over prefix sums (non-negative values)**
    - LeetCode 209 Minimum Size Subarray Sum (medium; neetcode250, all)
    - LeetCode 713 Subarray Product Less Than K (medium; all)
    - LeetCode 1208 Get Equal Substrings Within Budget (medium; all)

### 12. Character-budget windows

- **Replacement budget (window size - max frequency <= K)**
    - LeetCode 424 Longest Repeating Character Replacement (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 2024 Maximize the Confusion of an Exam (medium; practice)
- **Flip budget (at most K zeros)**
    - LeetCode 487 Max Consecutive Ones II (medium; all)
    - LeetCode 1004 Max Consecutive Ones III (medium; all)
    - LeetCode 1493 Longest Subarray of 1's After Deleting One Element (medium; practice)
- **Cost budget (sum of per-position costs <= budget)**
    - LeetCode 1208 Get Equal Substrings Within Budget (medium; all)
    - LeetCode 2398 Maximum Number of Robots Within Budget (hard; practice)
- **Operation budget on sorted values (size x max - sum <= K)**
    - LeetCode 1838 Frequency of the Most Frequent Element (medium; all)
    - LeetCode 2779 Maximum Beauty of an Array After Applying Operation (medium; all)
    - LeetCode 3346 Maximum Frequency of an Element After Performing Operations I (medium; practice)
- **Swap budget around a median**
    - LeetCode 1703 Minimum Adjacent Swaps for K Consecutive Ones (hard; practice)

### 13. 2-D windows

- **Fixed-size submatrix sums (2-D prefix sums)**
    - LeetCode 304 Range Sum Query 2D - Immutable (medium; neetcode250, all)
- **Collapse row pairs to 1-D, then window or hash**
    - LeetCode 1074 Number of Submatrices That Sum to Target (hard; all)
- **Largest square / rectangle (grow the window in two directions)**
    - LeetCode 221 Maximal Square (medium; all)
    - LeetCode 85 Maximal Rectangle (hard; practice)
- **Maximum-sum rectangle no larger than K**: no problem in the data: needs one from LeetCode.
- **K x K maximum by two passes of 1-D deques**: no problem in the data: needs one from LeetCode.

### 14. Sorted-input windows (sort first, then slide)

- **Sort, then a window of K**
    - LeetCode 1984 Minimum Difference Between Highest and Lowest of K Scores (easy; all)
- **Sort, then a range (max - min <= limit)**
    - LeetCode 2009 Minimum Number of Operations to Make Array Continuous (hard; all)
    - LeetCode 2779 Maximum Beauty of an Array After Applying Operation (medium; all)
    - LeetCode 3346 Maximum Frequency of an Element After Performing Operations I (medium; practice)
    - LeetCode 3634 Minimum Removals to Balance Array (medium; practice)
- **Consecutive-values window (distinct count in a range of n)**
    - LeetCode 2009 Minimum Number of Operations to Make Array Continuous (hard; all)
- **Gap windows (stones, points by position)**
    - LeetCode 1040 Moving Stones Until Consecutive II (medium; practice)

### 15. Window as a helper for DP and greedy

- **Several non-overlapping windows (best left + best right)**
    - LeetCode 689 Maximum Sum of 3 Non-Overlapping Subarrays (hard; all)
- **Greedy flips with a queue or difference array**
    - LeetCode 995 Minimum Number of K Consecutive Bit Flips (hard; all)
    - LeetCode 3191 Minimum Operations to Make Binary Array Elements Equal to One I (medium; all)
- **DP with a running window sum**
    - LeetCode 1871 Jump Game VII (medium; neetcode250, all)
    - LeetCode 837 New 21 Game (medium; all)
- **Windows over derived sequences (positions, intervals, gaps)**
    - LeetCode 1703 Minimum Adjacent Swaps for K Consecutive Ones (hard; practice)
    - LeetCode 3413 Maximum Coins From K Consecutive Bags (medium; practice)
    - LeetCode 3439 Reschedule Meetings for Maximum Free Time I (medium; practice)
    - LeetCode 3652 Best Time to Buy and Sell Stock using Strategy (medium; practice)

## Gaps

- 3 patterns have no problem in the data and need one from LeetCode (picked and checked against LeetCode, never from memory):
    - Two-pointer windows across two sorted sequences (interval lists)
    - Maximum-sum rectangle no larger than K
    - K x K maximum by two passes of 1-D deques
- 26 patterns have exactly one problem in the data (for example the word-level window, window median, the circular maximum and 2-D prefix sums), so a lesson would lean on a single example. Adding a second from LeetCode would help each.
- Groups with no lesson yet: 6 (two sequences), 7 (circular), 9 (ordered-set and heap), 10 (negative numbers), 11 (binary search on size), 13 (2-D) and 15 (DP and greedy helpers). Group 10 is the
  important one: the "why windows fail" lesson is what stops learners from forcing a window onto sums that are not monotone.
- Data to note: the NeetCode lists carry only 6 (150) and 9 (250) of these problems, so groups 4 to 15 are almost all example material from the larger lists. Problems whose own pattern is elsewhere
  (for example 862 in Stack, 480 in Heap, 918 and 1423 in Greedy, 2398 in Binary Search) are used as examples here, so the lesson links across topics.
- Not used as examples: LeetCode 1297 Maximum Number of Occurrences of a Substring, LeetCode 2090 K Radius Subarray Averages, LeetCode 2781 Length of the Longest Valid Substring. They fit the patterns "fixed-size with a count map", "sum of the window" and "shrink while invalid" and can replace an example if needed.
- Open before building: how the tabs look (needs a mockup), whether groups 14 and 15 stay in the Sliding Window topic or move to Greedy, Binary Search and Prefix Sums, and the example problems for the three empty patterns.
