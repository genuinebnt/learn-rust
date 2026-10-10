# Two Pointers patterns: the exhaustive target list

The target list of every two-pointers pattern that can come up on LeetCode, for the Two Pointers pattern lessons. The rule is in [DSA.md](DSA.md), decision 32: a topic's patterns section is exhaustive, patterns without a NeetCode problem get **example problems** from LeetCode, and variants of one pattern are **tabs** of one lesson. The format follows [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md).

Status: documented only. Today `content/dsa/lessons/two-pointers.toml` has 8 techniques (in-place, opposite, merge-sorted, simulate, ksum, pair-count, greedy-pair, running-max). Building the rest needs a mockup of the tabs first, then lessons and picked example problems. The example problems below come from the data in `content/dsa/problems.json` and `content/dsa/practice.json` only; where the data has none, the pattern says so and needs a problem from LeetCode (checked there, never from memory).

Items written *a / b* in a group are variants for tabs where one lesson covers both (for example "Reverse the whole thing, then each word" next to "Reverse words or tokens"). Several groups overlap on purpose: the same problem can show an idea from two sides (for example 2Sum on a sorted array is both an opposite-end walk and the base of k-sum).

1. **Opposite-end pointers.** Converging pair on a sorted array / palindrome check / palindrome with one deletion / move the shorter side / fill the output from both ends / trapping water with a left and right max / shrink matching ends / farthest pair / swap ends inward (in-place reverse).
2. **Same-direction pointers (reader / writer, fast / slow).** Reader and writer / fast scans a run, slow marks its start / fast and slow on an array as a functional graph / two cursors on two sequences / backward fill / lagging pointer holding the last seen position / lead and lag as a window.
3. **K-sum on sorted arrays.** 2Sum on sorted / 3Sum with duplicate skipping / 3Sum closest / count pairs or triples under a bound / 4Sum and kSum recursion / fix the largest side (triangle count) / pair difference or complement test / fixed-offset triplets / 4Sum II.
4. **Merge-like walks.** Merge two sorted sequences / interleave / intersection of sorted arrays / overlap scan over interval lists / merge by key / lockstep over string parts / sparse dot product / greedy match of two sorted lists / k-way merge / count while merging.
5. **Linked-list pointers (cross-reference: the Linked List track).** Fast / slow midpoint / Floyd cycle detection and entry / gap pointer / two heads that swap lists (intersection) / split, reverse the half, compare / partition with two dummy heads / rotate by k / merge sorted lists.
6. **String pointers.** Subsequence test / lockstep compare with skip rules / compare tokens or runs / relative order of movable pieces / reverse words / rebuild a target from a reusable source / wildcard matching with a star backtrack pointer / insert at planned positions / count swaps with a next-open-slot pointer / next lexicographic arrangement.
7. **Partition pointers.** Dutch national flag / two-way partition by a predicate / stable partition around a pivot / quickselect and quicksort partition (Lomuto / Hoare) / wiggle and alternating arrangements.
8. **Pointer + binary search.** Count pairs under a bound / nearest element on the other side / binary search the answer with a two-pointer check / binary search the window edge, then expand / two pointers over two BST in-order streams / bounded search for a sum of squares.
9. **Rotation and reversal.** Three-reversal rotation / matrix rotation by transpose and reversal / reverse a prefix or every 2k block / reverse the whole, then each word / next permutation / reverse a sublist in a linked list / several shifts as one rotation / cyclic replacement.
10. **In-place dedupe and compaction.** Sorted dedupe / keep at most k copies / remove a value / compress runs / sorted linked-list dedupe / unsorted input / shift and fill / remove adjacent duplicates with the writer as a stack top.
11. **Center expansion.** Longest palindromic substring (odd and even centers) / count palindromic substrings / disjoint palindromes chosen greedily / Manacher / expand across runs / expand from each peak / expand a window from a located center.
12. **Pointers and greedy.** Pair lightest with heaviest / sorted match / spend at one end, gain at the other / move the weaker side / earliest-finish scan / extend the block to its farthest reach / prefix and suffix pointers around the part that must change / merge into the lexicographically largest result.

## Coverage today

The data holds 1550 problems in all (problems.json plus practice.json). 75 of them have `pattern = Two Pointers`; another 70 carry the tag "Two Pointers" but sit in another pattern (Linked List, Arrays & Hashing, Binary Search, Greedy, Sliding Window and others), so 145 problems mention two pointers in all. Of the 75 filed under the pattern, 3 are on blind75, 5 are on neetcode150, 13 are on neetcode250, 43 are on all, 32 are on practice (a problem can be on several lists). The lesson techniques, with the problems the data files under each:

- `Two Pointers:in-place`: In-place read and write pointers (must-learn LeetCode 27 Remove Element; 16 problems filed under it)
- `Two Pointers:opposite`: Pointers from both ends (must-learn LeetCode 125 Valid Palindrome; 22 problems filed under it)
- `Two Pointers:merge-sorted`: Merging two sorted arrays (must-learn LeetCode 1768 Merge Strings Alternately; 12 problems filed under it)
- `Two Pointers:simulate`: Two-pointer simulation (must-learn LeetCode 2109 Adding Spaces to a String; 8 problems filed under it)
- `Two Pointers:ksum`: Sort, fix one, two pointers (must-learn LeetCode 15 3Sum; 6 problems filed under it)
- `Two Pointers:pair-count`: Counting pairs in a sorted array (must-learn LeetCode 1498 Number of Subsequences That Satisfy the Given Sum Condition; 5 problems filed under it)
- `Two Pointers:greedy-pair`: Greedy pairing from both ends (must-learn LeetCode 881 Boats to Save People; 8 problems filed under it)
- `Two Pointers:running-max`: Two pointers with a running maximum (must-learn LeetCode 42 Trapping Rain Water; 5 problems filed under it)

How the 95 patterns of the 12 groups line up with those techniques:

- **Opposite-end pointers**: `opposite` (converging pair, palindromes, container, reverse), `running-max` (trapping water). Covered; the sub-ideas (one deletion, shrink ends, fill from both ends) are examples inside it, not separate pages.
- **Same-direction pointers (reader / writer, fast / slow)**: `in-place` covers the reader / writer. Run scanning, backward fill and lagging-pointer ideas have no page. Fast / slow on linked lists lives in the Linked List track (`Linked List:fast-slow`, `Linked List:gap`) and Floyd on arrays under Linked List (`Linked List:fast-slow`) and Math & Geometry (`Math & Geometry:number-cycle`).
- **K-sum on sorted arrays**: `ksum` (3Sum, 4Sum) and `pair-count`. Covered for the sorted case; closest and smaller-than variants have no page.
- **Merge-like walks**: `merge-sorted` (merge arrays, alternate merge, interval overlap). Covered; k-way merge sits in Linked List (`Linked List:kway-merge`), merge-and-count has no page.
- **Linked-list pointers (cross-reference: the Linked List track)**: Not in this lesson; the Linked List track covers fast-slow, gap, splice and reverse. The Two Pointers page should link to it, not repeat it.
- **String pointers**: Spread over `merge-sorted` (subsequence), `simulate` and `opposite`; no page of its own. Lockstep comparison with skip rules and wildcard matching are not taught.
- **Partition pointers**: Not in this lesson. Sort Colors is under Arrays & Hashing (`Arrays & Hashing:sorting`); only the parity partition and pivot partition are filed here.
- **Pointer + binary search**: `pair-count` covers counting; the binary-search side lives under Binary Search (`insert-pos`, `on-answer`). No page links the two.
- **Rotation and reversal**: No page. Rotate Array and the reverse-string family are filed under `opposite`; Next Permutation is under Greedy (`Greedy:swap-greedy`).
- **In-place dedupe and compaction**: `in-place`. Covered; the keep-at-most-k generalization is one example inside it.
- **Center expansion**: Not in this lesson. Longest Palindromic Substring and Palindromic Substrings are under 1-D Dynamic Programming (`1-D Dynamic Programming:expand`). Manacher is only a tag.
- **Pointers and greedy**: `greedy-pair` (boats, cookies, tokens, teams). Covered for sorted pairing; the move-the-weaker-side proof is inside `opposite` and `running-max`.

Filing in the data that does not match the idea (worth fixing when the lessons are rebuilt):

- LeetCode 779 K-th Symbol in Grammar: filed under `simulate`; it is recursion and bit counting.
- LeetCode 917 Reverse Only Letters: filed under `ksum`; it is a skip-and-swap from both ends.
- LeetCode 925 Long Pressed Name: filed under `ksum`; it is a lockstep run comparison.
- LeetCode 777 Swap Adjacent in LR String: filed under `ksum`; it is the relative order of two strings.
- LeetCode 795 Number of Subarrays with Bounded Maximum: filed under `in-place`; it is a one-pass count.
- LeetCode 611 Valid Triangle Number: filed under `merge-sorted`; it is fix the largest, then two pointers.
- LeetCode 1877 Minimize Maximum Pair Sum in Array: filed under `merge-sorted`; it is pair lightest with heaviest.
- LeetCode 2592 Maximize Greatness of an Array: filed under `merge-sorted`; it is a sorted greedy match.
- LeetCode 1968 Array With Elements Not Equal to Average of Neighbors: filed under `simulate`; it is a wiggle arrangement.
- LeetCode 1578 Minimum Time to Make Rope Colorful: filed under `simulate`; it is a run scan.

## Example problems per pattern

Up to four per pattern, picked from the problems in the data (the lists are the ones the data gives; `all` is the full catalogue, `practice` the extra pool). A problem can appear under more than one pattern.

### 1. Opposite-end pointers

- **Converging pair on a sorted array (sum too small: move left; too big: move right)**
  - LeetCode 167 Two Sum II - Input Array Is Sorted (medium; neetcode150, neetcode250, all)
  - LeetCode 1099 Two Sum Less Than K (easy; all)
  - LeetCode 633 Sum of Square Numbers (medium; all)
- **Palindrome check (compare the ends, move inward)**
  - LeetCode 125 Valid Palindrome (easy; blind75, neetcode150, neetcode250, all)
  - LeetCode 2108 Find First Palindromic String in the Array (easy; all)
  - LeetCode 246 Strobogrammatic Number (easy; all)
- **Palindrome with one deletion allowed (branch once on the first mismatch)**
  - LeetCode 680 Valid Palindrome II (easy; neetcode250, all)
- **Move the shorter side (area maximization, exchange argument)**
  - LeetCode 11 Container With Most Water (medium; blind75, neetcode150, neetcode250, all)
- **Fill the output from both ends (sorted squares, sorted quadratic)**
  - LeetCode 977 Squares of a Sorted Array (easy; all)
  - LeetCode 360 Sort Transformed Array (medium; all)
- **Trapping water with a left max and a right max (move the lower side)**
  - LeetCode 42 Trapping Rain Water (hard; neetcode150, neetcode250, all)
- **Shrink matching ends (strip a common prefix and suffix)**
  - LeetCode 1750 Minimum Length of String After Deleting Similar Ends (medium; all)
  - LeetCode 1813 Sentence Similarity III (medium; all)
  - LeetCode 1574 Shortest Subarray to be Removed to Make Array Sorted (medium; all)
- **Farthest pair by scanning inward from both ends**
  - LeetCode 2078 Two Furthest Houses With Different Colors (easy; practice)
- **Swap ends inward (in-place reverse)**
  - LeetCode 344 Reverse String (easy; neetcode250, all)
  - LeetCode 345 Reverse Vowels of a String (easy; practice)
  - LeetCode 917 Reverse Only Letters (easy; practice)

### 2. Same-direction pointers (reader / writer, fast / slow)

- **Reader and writer (the reader tests each item, the writer marks the kept prefix)**
  - LeetCode 27 Remove Element (easy; neetcode250, all)
  - LeetCode 283 Move Zeroes (easy; all)
  - LeetCode 2460 Apply Operations to an Array (easy; all)
- **Fast pointer scans a run, slow pointer marks where it starts**
  - LeetCode 443 String Compression (medium; all)
  - LeetCode 1578 Minimum Time to Make Rope Colorful (medium; all)
  - LeetCode 696 Count Binary Substrings (easy; practice)
  - LeetCode 845 Longest Mountain in Array (medium; practice)
- **Fast / slow on an array as a functional graph (index jumps, Floyd)**
  - LeetCode 287 Find the Duplicate Number (medium; neetcode150, neetcode250, all)
- **Two cursors on two sequences, each advanced independently**
  - LeetCode 1662 Check If Two String Arrays are Equivalent (easy; all)
- **Backward fill (read from the front, write from the back so nothing is overwritten)**
  - LeetCode 88 Merge Sorted Array (easy; neetcode250, all)
  - LeetCode 1089 Duplicate Zeros (easy; practice)
  - LeetCode 1861 Rotating the Box (medium; all)
- **Lagging pointer holding the last seen position (nearest-X distances)**
  - LeetCode 821 Shortest Distance to a Character (easy; practice)
  - LeetCode 2200 Find All K-Distant Indices in an Array (easy; practice)
- **Lead and lag as a window (see Sliding Window)**
  - LeetCode 2110 Number of Smooth Descent Periods of a Stock (medium; practice)
  - LeetCode 658 Find K Closest Elements (medium; neetcode250, all)

### 3. K-sum on sorted arrays

- **2Sum on a sorted array / count K-sum pairs after sorting**
  - LeetCode 167 Two Sum II - Input Array Is Sorted (medium; neetcode150, neetcode250, all)
  - LeetCode 1099 Two Sum Less Than K (easy; all)
  - LeetCode 1679 Max Number of K-Sum Pairs (medium; practice)
- **3Sum: sort, fix one, 2Sum on the rest, skip duplicates**
  - LeetCode 15 3Sum (medium; blind75, neetcode150, neetcode250, all)
- **3Sum closest (track the best distance)**
  - LeetCode 16 3Sum Closest (medium; practice)
- **Count pairs or triples under a bound (add r - l answers at once)**
  - LeetCode 259 3Sum Smaller (medium; all)
  - LeetCode 2824 Count Pairs Whose Sum is Less than Target (easy; practice)
- **4Sum / kSum (recursive reduction to 2Sum)**
  - LeetCode 18 4Sum (medium; neetcode250, all)
- **Fix the largest side, count pairs below it (triangle count)**
  - LeetCode 611 Valid Triangle Number (medium; practice)
- **Pair difference or complement test on sorted data**
  - LeetCode 532 K-diff Pairs in an Array (medium; practice)
  - LeetCode 2441 Largest Positive Integer That Exists With Its Negative (easy; practice)
  - LeetCode 1346 Check If N and Its Double Exist (easy; practice)
- **Fixed-offset triplets**
  - LeetCode 2367 Number of Arithmetic Triplets (easy; practice)
- **4Sum II (two arrays hashed against two arrays)**
  - no problem in the data: needs one from LeetCode

### 4. Merge-like walks

- **Merge two sorted sequences (compare heads, advance one)**
  - LeetCode 88 Merge Sorted Array (easy; neetcode250, all)
  - LeetCode 21 Merge Two Sorted Lists (easy; blind75, neetcode150, neetcode250, all)
- **Interleave two sequences**
  - LeetCode 1768 Merge Strings Alternately (easy; neetcode250, all)
- **Intersection of two sorted arrays / multisets**
  - LeetCode 349 Intersection of Two Arrays (easy; all)
  - LeetCode 350 Intersection of Two Arrays II (easy; practice)
- **Overlap scan over two sorted interval lists**
  - LeetCode 986 Interval List Intersections (medium; all)
  - LeetCode 1229 Meeting Scheduler (medium; all)
- **Merge by key and combine values (sums, run-length products)**
  - LeetCode 2570 Merge Two 2D Arrays by Summing Values (easy; all)
  - LeetCode 1868 Product of Two Run-Length Encoded Arrays (medium; all)
- **Lockstep over the parts of two strings (version numbers)**
  - LeetCode 165 Compare Version Numbers (medium; practice)
- **Dot product of sparse vectors (walk two index lists)**
  - LeetCode 1570 Dot Product of Two Sparse Vectors (medium; all)
  - LeetCode 244 Shortest Word Distance II (medium; all)
- **Match two sorted lists greedily (smallest that can serve)**
  - LeetCode 2410 Maximum Matching of Players With Trainers (medium; practice)
  - LeetCode 2592 Maximize Greatness of an Array (medium; practice)
- **K-way merge (generalize the two-way merge)**
  - LeetCode 23 Merge k Sorted Lists (hard; blind75, neetcode150, neetcode250, all)
  - LeetCode 1508 Range Sum of Sorted Subarray Sums (medium; all)
- **Count while merging (merge-sort pass)**
  - LeetCode 493 Reverse Pairs (hard; practice)

### 5. Linked-list pointers (cross-reference: the Linked List track)

- **Fast / slow to the midpoint**
  - LeetCode 876 Middle of the Linked List (easy; all)
  - LeetCode 2130 Maximum Twin Sum of a Linked List (medium; all)
  - LeetCode 2095 Delete the Middle Node of a Linked List (medium; practice)
- **Cycle detection and cycle entry (Floyd)**
  - LeetCode 141 Linked List Cycle (easy; blind75, neetcode150, neetcode250, all)
  - LeetCode 142 Linked List Cycle II (medium; practice)
- **Gap pointer (n-th from the end, swap k-th from both ends)**
  - LeetCode 19 Remove Nth Node From End of List (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 1721 Swapping Nodes in a Linked List (medium; all)
- **Two heads that swap lists at the end (intersection)**
  - LeetCode 160 Intersection of Two Linked Lists (easy; all)
- **Split, reverse the half, compare or interleave**
  - LeetCode 143 Reorder List (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 234 Palindrome Linked List (easy; all)
- **Partition or splice with two dummy heads**
  - LeetCode 86 Partition List (medium; all)
  - LeetCode 328 Odd Even Linked List (medium; practice)
  - LeetCode 82 Remove Duplicates from Sorted List II (medium; practice)
  - LeetCode 83 Remove Duplicates from Sorted List (easy; all)
- **Rotate by k with length and a gap**
  - LeetCode 61 Rotate List (medium; all)
- **Merge two sorted lists / merge sort on a list**
  - LeetCode 21 Merge Two Sorted Lists (easy; blind75, neetcode150, neetcode250, all)
  - LeetCode 148 Sort List (medium; all)

### 6. String pointers

- **Subsequence test (one greedy pass over the longer string)**
  - LeetCode 392 Is Subsequence (easy; all)
  - LeetCode 2486 Append Characters to String to Make Subsequence (medium; all)
  - LeetCode 2825 Make String a Subsequence Using Cyclic Increments (medium; practice)
  - LeetCode 3302 Find the Lexicographically Smallest Valid Sequence (medium; practice)
- **Lockstep compare with skip rules (backspace, abbreviation, long press)**
  - LeetCode 844 Backspace String Compare (easy; all)
  - LeetCode 408 Valid Word Abbreviation (easy; all)
  - LeetCode 925 Long Pressed Name (easy; practice)
- **Compare tokens or runs of two strings**
  - LeetCode 165 Compare Version Numbers (medium; practice)
  - LeetCode 1662 Check If Two String Arrays are Equivalent (easy; all)
  - LeetCode 161 One Edit Distance (medium; all)
- **Relative order of movable pieces**
  - LeetCode 2337 Move Pieces to Obtain a String (medium; practice)
  - LeetCode 777 Swap Adjacent in LR String (medium; practice)
- **Reverse words or tokens**
  - LeetCode 151 Reverse Words in a String (medium; practice)
  - LeetCode 186 Reverse Words in a String II (medium; all)
  - LeetCode 557 Reverse Words in a String III (easy; all)
- **Rebuild a target from a reusable source (restart the source pointer)**
  - LeetCode 1055 Shortest Way to Form String (medium; all)
- **Wildcard matching with a star backtrack pointer**
  - LeetCode 44 Wildcard Matching (hard; practice)
- **Insert at planned positions during one pass**
  - LeetCode 2109 Adding Spaces to a String (medium; all)
- **Count swaps with a pointer to the next open slot**
  - LeetCode 1963 Minimum Number of Swaps to Make the String Balanced (medium; all)
  - LeetCode 2938 Separate Black and White Balls (medium; all)
  - LeetCode 942 DI String Match (easy; practice)
- **Next lexicographic arrangement of a digit string**
  - LeetCode 556 Next Greater Element III (medium; practice)

### 7. Partition pointers

- **Dutch national flag (three-way partition: low / mid / high)**
  - LeetCode 75 Sort Colors (medium; neetcode250, all)
- **Two-way partition by a predicate (parity, sign)**
  - LeetCode 905 Sort Array By Parity (easy; all)
  - LeetCode 922 Sort Array By Parity II (easy; practice)
  - LeetCode 2149 Rearrange Array Elements by Sign (medium; all)
- **Partition around a pivot while keeping order**
  - LeetCode 2161 Partition Array According to Given Pivot (medium; all)
  - LeetCode 86 Partition List (medium; all)
- **Quickselect and quicksort partition (Lomuto / Hoare)**
  - LeetCode 215 Kth Largest Element in an Array (medium; neetcode150, neetcode250, all)
  - LeetCode 912 Sort an Array (medium; neetcode250, all)
- **Wiggle and alternating arrangements**
  - LeetCode 280 Wiggle Sort (medium; all)
  - LeetCode 1968 Array With Elements Not Equal to Average of Neighbors (medium; all)

### 8. Pointer + binary search

- **Count pairs under a bound (sort, then two pointers or a binary search per item)**
  - LeetCode 2563 Count the Number of Fair Pairs (medium; all)
  - LeetCode 1498 Number of Subsequences That Satisfy the Given Sum Condition (medium; all)
  - LeetCode 3814 Maximum Capacity Within Budget (medium; practice)
- **Nearest element on the other side (binary search for each item)**
  - LeetCode 475 Heaters (medium; practice)
  - LeetCode 2300 Successful Pairs of Spells and Potions (medium; all)
  - LeetCode 826 Most Profit Assigning Work (medium; practice)
  - LeetCode 825 Friends Of Appropriate Ages (medium; practice)
- **Binary search the answer, check feasibility with two pointers**
  - LeetCode 719 Find K-th Smallest Pair Distance (hard; all)
  - LeetCode 1898 Maximum Number of Removable Characters (medium; all)
- **Binary search the window edge, then expand outward**
  - LeetCode 658 Find K Closest Elements (medium; neetcode250, all)
- **Two pointers over two BST in-order streams**
  - LeetCode 653 Two Sum IV - Input is a BST (easy; practice)
  - LeetCode 1214 Two Sum BSTs (medium; all)
  - LeetCode 272 Closest Binary Search Tree Value II (hard; all)
- **Bounded search for a sum of squares**
  - LeetCode 633 Sum of Square Numbers (medium; all)

### 9. Rotation and reversal

- **Rotate by three reversals**
  - LeetCode 189 Rotate Array (medium; neetcode250, all)
- **Rotate a matrix (transpose, then reverse each row)**
  - LeetCode 48 Rotate Image (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 1886 Determine Whether Matrix Can Be Obtained By Rotation (easy; practice)
- **Reverse a prefix or every 2k block**
  - LeetCode 2000 Reverse Prefix of Word (easy; practice)
  - LeetCode 541 Reverse String II (easy; practice)
- **Reverse the whole thing, then each word**
  - LeetCode 186 Reverse Words in a String II (medium; all)
  - LeetCode 151 Reverse Words in a String (medium; practice)
  - LeetCode 557 Reverse Words in a String III (easy; all)
- **Next permutation (find the pivot, swap, reverse the suffix)**
  - LeetCode 31 Next Permutation (medium; all)
- **Reverse a sublist or groups of a linked list**
  - LeetCode 92 Reverse Linked List II (medium; neetcode250, all)
  - LeetCode 206 Reverse Linked List (easy; blind75, neetcode150, neetcode250, all)
  - LeetCode 25 Reverse Nodes in k-Group (hard; neetcode150, neetcode250, all)
- **Several cyclic shifts as one net rotation**
  - LeetCode 1427 Perform String Shifts (easy; all)
  - LeetCode 1752 Check if Array Is Sorted and Rotated (easy; all)
- **Cyclic replacement (follow each cycle, gcd of n and k)**
  - no problem in the data: needs one from LeetCode

### 10. In-place dedupe and compaction

- **Sorted array, keep one copy**
  - LeetCode 26 Remove Duplicates from Sorted Array (easy; neetcode250, all)
  - LeetCode 83 Remove Duplicates from Sorted List (easy; all)
- **Keep at most k copies (compare with the item k places behind the writer)**
  - LeetCode 80 Remove Duplicates from Sorted Array II (medium; all)
- **Remove a given value**
  - LeetCode 27 Remove Element (easy; neetcode250, all)
- **Compress runs in place**
  - LeetCode 443 String Compression (medium; all)
- **Sorted linked list, drop every duplicated value**
  - LeetCode 82 Remove Duplicates from Sorted List II (medium; practice)
- **Unsorted input (needs a set or a sort first)**
  - LeetCode 1836 Remove Duplicates From an Unsorted Linked List (medium; all)
- **Shift and fill (move zeroes, duplicate zeros, apply operations)**
  - LeetCode 283 Move Zeroes (easy; all)
  - LeetCode 1089 Duplicate Zeros (easy; practice)
  - LeetCode 2460 Apply Operations to an Array (easy; all)
- **Remove adjacent duplicates (the writer acts as a stack top)**
  - LeetCode 1047 Remove All Adjacent Duplicates In String (easy; practice)
  - LeetCode 1209 Remove All Adjacent Duplicates in String II (medium; all)

### 11. Center expansion

- **Longest palindromic substring (odd and even centers)**
  - LeetCode 5 Longest Palindromic Substring (medium; blind75, neetcode150, neetcode250, all)
- **Count palindromic substrings (every center, every radius)**
  - LeetCode 647 Palindromic Substrings (medium; blind75, neetcode150, neetcode250, all)
- **Disjoint palindromes chosen greedily after expansion**
  - LeetCode 2472 Maximum Number of Non-overlapping Palindrome Substrings (hard; practice)
- **Manacher's algorithm (linear time, mirror radius)**
  - LeetCode 5 Longest Palindromic Substring (medium; blind75, neetcode150, neetcode250, all)
- **Expand across runs of equal characters**
  - LeetCode 696 Count Binary Substrings (easy; practice)
- **Expand left and right from each peak**
  - LeetCode 845 Longest Mountain in Array (medium; practice)
- **Expand a window outward from a located center until it holds k**
  - LeetCode 658 Find K Closest Elements (medium; neetcode250, all)

### 12. Pointers and greedy

- **Pair the lightest with the heaviest (sort, then two ends)**
  - LeetCode 881 Boats to Save People (medium; neetcode250, all)
  - LeetCode 1877 Minimize Maximum Pair Sum in Array (medium; practice)
  - LeetCode 2491 Divide Players Into Teams of Equal Skill (medium; all)
- **Sorted match: the smallest item that can serve**
  - LeetCode 455 Assign Cookies (easy; all)
  - LeetCode 2410 Maximum Matching of Players With Trainers (medium; practice)
  - LeetCode 2592 Maximize Greatness of an Array (medium; practice)
- **Spend at one end, gain at the other (token game)**
  - LeetCode 948 Bag of Tokens (medium; all)
- **Move the weaker side (the exchange argument for two-pointer maxima)**
  - LeetCode 11 Container With Most Water (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 42 Trapping Rain Water (hard; neetcode150, neetcode250, all)
- **Earliest-finish scan over two sorted options**
  - LeetCode 3633 Earliest Finish Time for Land and Water Rides I (easy; practice)
- **Extend the current block to its farthest reach**
  - LeetCode 763 Partition Labels (medium; neetcode150, neetcode250, all)
- **Prefix and suffix pointers around the part that must change**
  - LeetCode 581 Shortest Unsorted Continuous Subarray (medium; practice)
  - LeetCode 1574 Shortest Subarray to be Removed to Make Array Sorted (medium; all)
- **Merge two sequences into the lexicographically largest result**
  - LeetCode 321 Create Maximum Number (hard; practice)

## Gaps

- **2 of 95 patterns have no problem in the data** and need one picked from LeetCode and checked there: 4Sum II (group: k-sum on sorted arrays); Cyclic replacement (group: rotation and reversal).
- **41 patterns have exactly one problem**, so the lesson has a must-learn problem and nothing to practise on: Palindrome with one deletion allowed (LeetCode 680); Move the shorter side (LeetCode 11); Trapping water with a left max and a right max (LeetCode 42); Farthest pair by scanning inward from both ends (LeetCode 2078); Fast / slow on an array as a functional graph (LeetCode 287); Two cursors on two sequences, each advanced independently (LeetCode 1662); 3Sum: sort, fix one, 2Sum on the rest, skip duplicates (LeetCode 15); 3Sum closest (LeetCode 16); 4Sum / kSum (LeetCode 18); Fix the largest side, count pairs below it (LeetCode 611); Fixed-offset triplets (LeetCode 2367); Interleave two sequences (LeetCode 1768); Lockstep over the parts of two strings (LeetCode 165); Count while merging (LeetCode 493); Two heads that swap lists at the end (LeetCode 160); Rotate by k with length and a gap (LeetCode 61); Rebuild a target from a reusable source (LeetCode 1055); Wildcard matching with a star backtrack pointer (LeetCode 44); Insert at planned positions during one pass (LeetCode 2109); Next lexicographic arrangement of a digit string (LeetCode 556); Dutch national flag (LeetCode 75); Binary search the window edge, then expand outward (LeetCode 658); Bounded search for a sum of squares (LeetCode 633); Rotate by three reversals (LeetCode 189); Next permutation (LeetCode 31); Keep at most k copies (LeetCode 80); Remove a given value (LeetCode 27); Compress runs in place (LeetCode 443); Sorted linked list, drop every duplicated value (LeetCode 82); Unsorted input (LeetCode 1836); Longest palindromic substring (LeetCode 5); Count palindromic substrings (LeetCode 647); Disjoint palindromes chosen greedily after expansion (LeetCode 2472); Manacher's algorithm (LeetCode 5); Expand across runs of equal characters (LeetCode 696); Expand left and right from each peak (LeetCode 845); Expand a window outward from a located center until it holds k (LeetCode 658); Spend at one end, gain at the other (LeetCode 948); Earliest-finish scan over two sorted options (LeetCode 3633); Extend the current block to its farthest reach (LeetCode 763); Merge two sequences into the lexicographically largest result (LeetCode 321).
- **Pattern groups with no page today:** linked-list pointers (kept in the Linked List track), string pointers, partition pointers, rotation and reversal, center expansion, and the pointer + binary-search bridge. The existing lesson covers 8 techniques; the target has 12 groups and 95 patterns.
- **Techniques the data files elsewhere:** Dutch national flag (Arrays & Hashing), center expansion (1-D Dynamic Programming), next permutation (Greedy), partition and splice (Linked List). Decide whether the Two Pointers page repeats them as tabs or cross-links to the owning track.
- **Mis-filed problems** (see the list under Coverage today) make the technique counts misleading until the techniques are rebuilt.
- **Tabs need a mockup** (rule 13 in the working rules) before any of this is built: which groups become one lesson with tabs (for example reverse words and rotate by reversal) and which stay separate lessons.
- **Free or premium:** the example problems are not checked for access; prefer free ones when choosing the final four per pattern.
