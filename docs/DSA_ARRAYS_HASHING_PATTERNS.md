# Arrays & Hashing patterns: the exhaustive target list

The target list of every Arrays & Hashing pattern that can come up on LeetCode, for the Arrays & Hashing pattern lesson. It follows the same rule as [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md) and decision 32 in [DSA.md](DSA.md): a topic's patterns section is exhaustive, patterns without a NeetCode problem get **example problems** from LeetCode, and variants of one pattern (chaining / open addressing, Counter / array of 26) are **tabs** of one lesson.

Status: documented only. Today `content/dsa/lessons/arrays-hashing.toml` has 15 techniques (simulation, seen-set, counting, complement, string-match, signature, majority-vote, design-hash, sorting, top-k, encoding, prefix, consecutive, prefix-map, index-marks). The list below has 18 groups and 98 patterns. Building the rest needs the tabs mockup first (the same one as for graphs), then lessons and picked example problems. The example problems below come only from `content/dsa/problems.json` and `content/dsa/practice.json`; a number or title that is not in those files is never listed.

Items separated by semicolons are separate patterns. Inside one pattern, *a / b* names variants that become tabs of the same lesson.

1. **Frequency counting.** Hash-map counting (Counter / dict); Fixed-alphabet count array (26 slots); Frequency of frequencies / parity of counts; Multiset comparison / containment; Sliding-window frequency match; Top K by frequency (heap / bucket).
2. **Two-sum family.** Complement lookup in a map; Pair counting with a transformed key (nums[i] - i, digit reversal); Sorted two pointers / k-sum; Pair existence by relation (double, difference); Two sum on a non-array structure.
3. **Grouping by canonical key.** Sorted-string / count-tuple key (anagrams); Normalized shape key (shift, pattern, isomorphism); Bitmask key for letter sets; Group records by an owner or first-use key; Reverse / complement keys (palindrome pairs).
4. **Prefix sums with a map.** Count subarrays with sum k; Longest subarray by first-seen index (balance / zero-sum); Remainder classes (sum divisible by k); Prefix XOR with a map; Prefix parity counts (odd / even sums); 2-D prefix sums collapsed to 1-D (submatrix sum).
5. **Difference arrays.** 1-D range add, read once at the end; Event counting / sweep over start and end points; Range add on a grid (2-D difference array); Bookings and flight-style range updates.
6. **In-place manipulation (cyclic sort, index as hash).** Cyclic sort (value v goes to index v - 1); Sign-flip marking as a visited set; In-place state encoding (extra bits per cell); Read / write pointer compaction; In-place reverse / rotate; Array as a functional graph (index to value).
7. **Partition and rearrangement.** Three-way partition (Dutch national flag); Partition by parity or predicate; Wiggle / alternating order; Interleave and shuffle; Order by a custom key or given order; Quickselect partition.
8. **Matrix traversal and transform.** Spiral / layer-by-layer walk; Diagonal and anti-diagonal walks; Transpose / rotate / reshape; Rows / columns / boxes as hash sets (grid validity); Marker row and column (set zeroes); Direction vectors and boundary checks.
9. **Simulation.** Follow the rules, build the result; Queue simulation (turns, ticks, waiting); Cellular update (grid or array steps); Run scanning (longest or counted runs); String formatting / layout; Digit and number construction.
10. **Majority element.** Boyer-Moore voting; Count with a map / sort and take the middle; Majority on a prefix and a suffix (valid split); Randomized majority.
11. **Prefix / suffix products and aggregates.** Product of everything except self; Prefix and suffix maxima / minima; Prefix-sum balance (pivot, split); Left versus right cost (split score, rob the bank); Static range queries (1-D, 2-D); Mutable range queries (Fenwick / segment tree).
12. **Counting and bucket tricks.** Counting sort over a small value range; Bucket by frequency; Bucket by value range / pigeonhole (max gap); Count array indexed by value.
13. **Coordinate compression.** Rank by sorted order (map value to rank); Compress before a Fenwick / segment tree; Compress sparse coordinates to grid indices.
14. **Duplicate detection.** Seen set (first repeat); Duplicate within a window (distance or value); Sort and compare neighbours; Index marking / Floyd for one duplicate in 1..n; Fixed-size sets for rule checks.
15. **Missing and extra number.** Sum / XOR identities; Cyclic sort or sign marking; Set difference; Smallest missing value (MEX); Missing and repeated pair in a grid.
16. **Design with hash maps.** Array plus map for O(1) random access and delete; Time-bucketed counters and rate limiting; Id to record maps (check-in / check-out, ratings, leaderboards); Map plus heap with lazy deletion; Cache design (LRU / LFU); Counters for game or board state; Sparse data and iterators; Time-versioned key-value store.
17. **Hashing structures.** Chaining / open addressing (build a HashSet / HashMap); Rolling (polynomial) hash; Prefix function / Z-function matching; Hashing composite values (tuples, paths, trees); Encode / serialize to a hashable key; Skip list and probabilistic structures; Bloom filter, cuckoo hashing, consistent hashing.
18. **Sorting-based approaches.** Custom comparator; Sort, then scan neighbours; Sort plus two pointers; Sort plus sweep (intervals, events); Stable multi-key sort; Implement a sort (merge / quick / heap / counting).

## Coverage today

The data has 175 Arrays & Hashing problems in `problems.json` (18 must-learn, 157 practice) and 60 more in `practice.json`, so 235 in all. Difficulty in `problems.json`: 81 easy, 86 medium, 8 hard.

Problems of `problems.json` by technique (the 15 rows are this topic's lessons):

| Technique | Problems | Must-learn | Group of this doc |
|---|---|---|---|
| Direct simulation (`simulation`) | 35 | Concatenation of Array | 9 Simulation |
| Hash set for membership (`seen-set`) | 10 | Contains Duplicate | 14 Duplicate detection |
| Counting with a hash map or array (`counting`) | 22 | Valid Anagram | 1 Frequency counting |
| Complement lookup in a hash map (`complement`) | 6 | Two Sum | 2 Two-sum family |
| String matching and rolling hash (`string-match`) | 5 | String Matching in an Array | 17 Hashing structures |
| Group by a canonical key (`signature`) | 6 | Group Anagrams | 3 Grouping by canonical key |
| Boyer-Moore majority vote (`majority-vote`) | 3 | Majority Element | 10 Majority element |
| Designing with hash maps and queues (`design-hash`) | 20 | Design HashSet | 16 Design with hash maps |
| Sorting with a custom order (`sorting`) | 13 | Sort an Array | 18 Sorting-based approaches |
| Top K by frequency (bucket sort) (`top-k`) | 2 | Top K Frequent Elements | 1 Frequency counting, 12 Counting and bucket tricks |
| Length-prefix encoding (`encoding`) | 1 | Encode and Decode Strings | 17 Hashing structures |
| Prefix and suffix products or sums (`prefix`) | 15 | Product of Array Except Self | 11 Prefix / suffix products, 5 Difference arrays (range updates) |
| Start of a sequence in a set (`consecutive`) | 1 | Longest Consecutive Sequence | 14 Duplicate detection (set of sequence starts) |
| Prefix sums with a hash map (`prefix-map`) | 8 | Subarray Sum Equals K | 4 Prefix sums with a map |
| Using the array's indices as markers (`index-marks`) | 5 | First Missing Positive | 6 In-place manipulation, 15 Missing and extra number |
| techniques of other topics (Greedy, Two Pointers, Graphs, Stack, Intervals and others) | 23 | none | spread over groups 5, 6, 7, 8, 14 |

Tags in the 175 problems of `problems.json` (a problem has several): Array 127, Hash Table 91, String 74, Sorting 30, Design 25, Prefix Sum 22, Counting 21, Matrix 14, Two Pointers 14, Greedy 14, Simulation 12, Math 12, Queue 10, Bit Manipulation 9.

Of the 98 patterns of this list, 42 have four or more example problems in the data, 51 have one to three, and 5 have none. Counting examples from every topic of the data, not only Arrays & Hashing.

What the 15 lessons do not cover as patterns of their own: difference arrays (5), coordinate compression (13), cyclic sort as its own tab (6), partition and rearrangement (7), matrix traversal and transform (8, today a Math & Geometry topic), prefix XOR and prefix parity inside prefix-map (4), and most of the hashing structures (17).

## Example problems per pattern

Up to four per pattern, picked only from the data (`problems.json` and `practice.json`), as `LeetCode <number> <title> (<difficulty>; <lists>)`. A problem can appear under several patterns, and an example can live in another topic of the data (for example Two Pointers or Intervals) when the pattern is the same. Where the data has none, the line says so.

### 1. Frequency counting

- **Hash-map counting (Counter / dict)**
    - LeetCode 242 Valid Anagram (easy; blind75, neetcode150, neetcode250, all)
    - LeetCode 383 Ransom Note (easy; all)
    - LeetCode 1189 Maximum Number of Balloons (easy; all)
    - LeetCode 1394 Find Lucky Integer in an Array (easy; all)
- **Fixed-alphabet count array (26 slots)**
    - LeetCode 1160 Find Words That Can Be Formed by Characters (easy; all)
    - LeetCode 1002 Find Common Characters (easy; all)
    - LeetCode 387 First Unique Character in a String (easy; all)
    - LeetCode 916 Word Subsets (medium; all)
- **Frequency of frequencies / parity of counts**
    - LeetCode 2206 Divide Array Into Equal Pairs (easy; all)
    - LeetCode 409 Longest Palindrome (easy; all)
    - LeetCode 266 Palindrome Permutation (easy; all)
    - LeetCode 2870 Minimum Number of Operations to Make Array Empty (medium; all)
- **Multiset comparison / containment**
    - LeetCode 350 Intersection of Two Arrays II (easy; practice)
    - LeetCode 2248 Intersection of Multiple Arrays (easy; practice)
    - LeetCode 2287 Rearrange Characters to Make Target String (easy; practice)
    - LeetCode 1897 Redistribute Characters to Make All Strings Equal (easy; all)
- **Sliding-window frequency match**
    - LeetCode 438 Find All Anagrams in a String (medium; all)
    - LeetCode 567 Permutation in String (medium; neetcode150, neetcode250, all)
    - LeetCode 76 Minimum Window Substring (hard; blind75, neetcode150, neetcode250, all)
- **Top K by frequency (heap / bucket)**
    - LeetCode 347 Top K Frequent Elements (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 451 Sort Characters By Frequency (medium; all)
    - LeetCode 692 Top K Frequent Words (medium; practice)
    - LeetCode 2404 Most Frequent Even Element (easy; practice)

### 2. Two-sum family

- **Complement lookup in a map**
    - LeetCode 1 Two Sum (easy; blind75, neetcode150, neetcode250, all)
    - LeetCode 1512 Number of Good Pairs (easy; all)
    - LeetCode 2001 Number of Pairs of Interchangeable Rectangles (medium; all)
    - LeetCode 1624 Largest Substring Between Two Equal Characters (easy; all)
- **Pair counting with a transformed key (nums[i] - i, digit reversal)**
    - LeetCode 2364 Count Number of Bad Pairs (medium; all)
    - LeetCode 1814 Count Nice Pairs in an Array (medium; practice)
    - LeetCode 2006 Count Number of Pairs With Absolute Difference K (easy; practice)
    - LeetCode 2023 Number of Pairs of Strings With Concatenation Equal to Target (medium; practice)
- **Sorted two pointers / k-sum**
    - LeetCode 167 Two Sum II - Input Array Is Sorted (medium; neetcode150, neetcode250, all)
    - LeetCode 15 3Sum (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 18 4Sum (medium; neetcode250, all)
    - LeetCode 1679 Max Number of K-Sum Pairs (medium; practice)
- **Pair existence by relation (double, difference)**
    - LeetCode 1346 Check If N and Its Double Exist (easy; practice)
    - LeetCode 825 Friends Of Appropriate Ages (medium; practice)
    - LeetCode 1426 Counting Elements (easy; all)
- **Two sum on a non-array structure**
    - LeetCode 653 Two Sum IV - Input is a BST (easy; practice)

### 3. Grouping by canonical key

- **Sorted-string / count-tuple key (anagrams)**
    - LeetCode 49 Group Anagrams (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 2273 Find Resultant Array After Removing Anagrams (easy; practice)
    - LeetCode 2744 Find Maximum Number of String Pairs (easy; practice)
    - LeetCode 2514 Count Anagrams (hard; practice)
- **Normalized shape key (shift, pattern, isomorphism)**
    - LeetCode 249 Group Shifted Strings (medium; all)
    - LeetCode 205 Isomorphic Strings (easy; all)
    - LeetCode 290 Word Pattern (easy; all)
    - LeetCode 890 Find and Replace Pattern (medium; practice)
- **Bitmask key for letter sets**
    - LeetCode 2506 Count Pairs Of Similar Strings (easy; practice)
    - LeetCode 1684 Count the Number of Consistent Strings (easy; all)
    - LeetCode 2306 Naming a Company (hard; all)
- **Group records by an owner or first-use key**
    - LeetCode 929 Unique Email Addresses (easy; all)
    - LeetCode 1152 Analyze User Website Visit Pattern (medium; all)
    - LeetCode 2284 Sender With Largest Word Count (medium; practice)
- **Reverse / complement keys (palindrome pairs)**
    - LeetCode 336 Palindrome Pairs (hard; practice)
    - LeetCode 2744 Find Maximum Number of String Pairs (easy; practice)

### 4. Prefix sums with a map

- **Count subarrays with sum k**
    - LeetCode 560 Subarray Sum Equals K (medium; neetcode250, all)
    - LeetCode 930 Binary Subarrays With Sum (medium; all)
    - LeetCode 1248 Count Number of Nice Subarrays (medium; all)
    - LeetCode 437 Path Sum III (medium; practice)
- **Longest subarray by first-seen index (balance / zero-sum)**
    - LeetCode 525 Contiguous Array (medium; all)
    - LeetCode 523 Continuous Subarray Sum (medium; all)
    - LeetCode 1371 Find the Longest Substring Containing Vowels in Even Counts (medium; all)
- **Remainder classes (sum divisible by k)**
    - LeetCode 974 Subarray Sums Divisible by K (medium; all)
    - LeetCode 523 Continuous Subarray Sum (medium; all)
    - LeetCode 1590 Make Sum Divisible by P (medium; all)
    - LeetCode 2845 Count of Interesting Subarrays (medium; practice)
- **Prefix XOR with a map**
    - LeetCode 1371 Find the Longest Substring Containing Vowels in Even Counts (medium; all)
    - LeetCode 1442 Count Triplets That Can Form Two Arrays of Equal XOR (medium; all)
    - LeetCode 2588 Count the Number of Beautiful Subarrays (medium; practice)
- **Prefix parity counts (odd / even sums)**
    - LeetCode 1524 Number of Sub-arrays With Odd Sum (medium; all)
    - LeetCode 2845 Count of Interesting Subarrays (medium; practice)
- **2-D prefix sums collapsed to 1-D (submatrix sum)**
    - LeetCode 1074 Number of Submatrices That Sum to Target (hard; all)

### 5. Difference arrays

- **1-D range add, read once at the end**
    - LeetCode 2381 Shifting Letters II (medium; all)
    - LeetCode 2772 Apply Operations to Make All Array Elements Equal to Zero (medium; practice)
- **Event counting / sweep over start and end points**
    - LeetCode 1094 Car Pooling (medium; neetcode250, all)
    - LeetCode 2021 Brightest Position on Street (medium; all)
    - LeetCode 253 Meeting Rooms II (medium; blind75, neetcode150, neetcode250, all)
- **Range add on a grid (2-D difference array)**
    - no problem in the data: needs one from LeetCode
- **Bookings and flight-style range updates**
    - no problem in the data: needs one from LeetCode

### 6. In-place manipulation (cyclic sort, index as hash)

- **Cyclic sort (value v goes to index v - 1)**
    - LeetCode 41 First Missing Positive (hard; neetcode250, all)
    - LeetCode 448 Find All Numbers Disappeared in an Array (easy; all)
    - LeetCode 442 Find All Duplicates in an Array (medium; all)
    - LeetCode 645 Set Mismatch (easy; all)
- **Sign-flip marking as a visited set**
    - LeetCode 442 Find All Duplicates in an Array (medium; all)
    - LeetCode 448 Find All Numbers Disappeared in an Array (easy; all)
    - LeetCode 41 First Missing Positive (hard; neetcode250, all)
- **In-place state encoding (extra bits per cell)**
    - LeetCode 289 Game of Life (medium; practice)
    - LeetCode 73 Set Matrix Zeroes (medium; blind75, neetcode150, neetcode250, all)
- **Read / write pointer compaction**
    - LeetCode 27 Remove Element (easy; neetcode250, all)
    - LeetCode 26 Remove Duplicates from Sorted Array (easy; neetcode250, all)
    - LeetCode 80 Remove Duplicates from Sorted Array II (medium; all)
    - LeetCode 283 Move Zeroes (easy; all)
- **In-place reverse / rotate**
    - LeetCode 189 Rotate Array (medium; neetcode250, all)
    - LeetCode 186 Reverse Words in a String II (medium; all)
    - LeetCode 48 Rotate Image (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 1089 Duplicate Zeros (easy; practice)
- **Array as a functional graph (index to value)**
    - LeetCode 287 Find the Duplicate Number (medium; neetcode150, neetcode250, all)
    - LeetCode 2965 Find Missing and Repeated Values (easy; all)

### 7. Partition and rearrangement

- **Three-way partition (Dutch national flag)**
    - LeetCode 75 Sort Colors (medium; neetcode250, all)
- **Partition by parity or predicate**
    - LeetCode 905 Sort Array By Parity (easy; all)
    - LeetCode 922 Sort Array By Parity II (easy; practice)
- **Wiggle / alternating order**
    - LeetCode 280 Wiggle Sort (medium; all)
    - LeetCode 324 Wiggle Sort II (medium; practice)
- **Interleave and shuffle**
    - LeetCode 1470 Shuffle the Array (easy; all)
    - LeetCode 1768 Merge Strings Alternately (easy; neetcode250, all)
- **Order by a custom key or given order**
    - LeetCode 791 Custom Sort String (medium; all)
    - LeetCode 1122 Relative Sort Array (easy; all)
    - LeetCode 179 Largest Number (medium; all)
    - LeetCode 2191 Sort the Jumbled Numbers (medium; all)
- **Quickselect partition**
    - LeetCode 215 Kth Largest Element in an Array (medium; neetcode150, neetcode250, all)
    - LeetCode 973 K Closest Points to Origin (medium; neetcode150, neetcode250, all)
    - LeetCode 324 Wiggle Sort II (medium; practice)

### 8. Matrix traversal and transform

- **Spiral / layer-by-layer walk**
    - LeetCode 54 Spiral Matrix (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 59 Spiral Matrix II (medium; all)
    - LeetCode 885 Spiral Matrix III (medium; all)
- **Diagonal and anti-diagonal walks**
    - LeetCode 498 Diagonal Traverse (medium; practice)
    - LeetCode 1424 Diagonal Traverse II (medium; practice)
    - LeetCode 1572 Matrix Diagonal Sum (easy; all)
    - LeetCode 766 Toeplitz Matrix (easy; practice)
- **Transpose / rotate / reshape**
    - LeetCode 48 Rotate Image (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 867 Transpose Matrix (easy; neetcode250, all)
    - LeetCode 566 Reshape the Matrix (easy; practice)
    - LeetCode 2022 Convert 1D Array Into 2D Array (easy; all)
- **Rows / columns / boxes as hash sets (grid validity)**
    - LeetCode 36 Valid Sudoku (medium; neetcode150, neetcode250, all)
    - LeetCode 2133 Check if Every Row and Column Contains All Numbers (easy; practice)
    - LeetCode 1380 Lucky Numbers in a Matrix (easy; all)
    - LeetCode 531 Lonely Pixel I (medium; all)
- **Marker row and column (set zeroes)**
    - LeetCode 73 Set Matrix Zeroes (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 289 Game of Life (medium; practice)
- **Direction vectors and boundary checks**
    - LeetCode 723 Candy Crush (medium; all)
    - LeetCode 2257 Count Unguarded Cells in the Grid (medium; all)
    - LeetCode 999 Available Captures for Rook (easy; practice)

### 9. Simulation

- **Follow the rules, build the result**
    - LeetCode 1929 Concatenation of Array (easy; neetcode250, all)
    - LeetCode 1822 Sign of the Product of an Array (easy; all)
    - LeetCode 3110 Score of a String (easy; all)
    - LeetCode 2490 Circular Sentence (easy; all)
- **Queue simulation (turns, ticks, waiting)**
    - LeetCode 2073 Time Needed to Buy Tickets (easy; all)
    - LeetCode 1700 Number of Students Unable to Eat Lunch (easy; all)
    - LeetCode 1701 Average Waiting Time (medium; all)
    - LeetCode 2534 Time Taken to Cross the Door (hard; all)
- **Cellular update (grid or array steps)**
    - LeetCode 723 Candy Crush (medium; all)
    - LeetCode 1243 Array Transformation (easy; all)
    - LeetCode 289 Game of Life (medium; practice)
    - LeetCode 838 Push Dominoes (medium; all)
- **Run scanning (longest or counted runs)**
    - LeetCode 485 Max Consecutive Ones (easy; all)
    - LeetCode 896 Monotonic Array (easy; all)
    - LeetCode 1800 Maximum Ascending Subarray Sum (easy; all)
    - LeetCode 3105 Longest Strictly Increasing or Strictly Decreasing Subarray (easy; all)
- **String formatting / layout**
    - LeetCode 68 Text Justification (hard; all)
    - LeetCode 14 Longest Common Prefix (easy; neetcode250, all)
    - LeetCode 58 Length of Last Word (easy; all)
    - LeetCode 161 One Edit Distance (medium; all)
- **Digit and number construction**
    - LeetCode 1056 Confusing Number (easy; all)
    - LeetCode 1291 Sequential Digits (medium; all)
    - LeetCode 66 Plus One (easy; neetcode150, neetcode250, all)

### 10. Majority element

- **Boyer-Moore voting**
    - LeetCode 169 Majority Element (easy; neetcode250, all)
    - LeetCode 229 Majority Element II (medium; neetcode250, all)
- **Count with a map / sort and take the middle**
    - LeetCode 169 Majority Element (easy; neetcode250, all)
    - LeetCode 3527 Find the Most Common Response (medium; practice)
    - LeetCode 2404 Most Frequent Even Element (easy; practice)
- **Majority on a prefix and a suffix (valid split)**
    - LeetCode 2780 Minimum Index of a Valid Split (medium; all)
- **Randomized majority**
    - no problem in the data: needs one from LeetCode

### 11. Prefix / suffix products and aggregates

- **Product of everything except self**
    - LeetCode 238 Product of Array Except Self (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 2906 Construct Product Matrix (medium; practice)
    - LeetCode 152 Maximum Product Subarray (medium; blind75, neetcode150, neetcode250, all)
- **Prefix and suffix maxima / minima**
    - LeetCode 1299 Replace Elements with Greatest Element on Right Side (easy; all)
    - LeetCode 42 Trapping Rain Water (hard; neetcode150, neetcode250, all)
    - LeetCode 135 Candy (hard; neetcode250, all)
    - LeetCode 624 Maximum Distance in Arrays (medium; all)
- **Prefix-sum balance (pivot, split)**
    - LeetCode 724 Find Pivot Index (easy; all)
    - LeetCode 1991 Find the Middle Index in Array (easy; practice)
    - LeetCode 2574 Left and Right Sum Differences (easy; practice)
    - LeetCode 2270 Number of Ways to Split Array (medium; all)
- **Left versus right cost (split score, rob the bank)**
    - LeetCode 1422 Maximum Score After Splitting a String (easy; all)
    - LeetCode 2483 Minimum Penalty for a Shop (medium; all)
    - LeetCode 2017 Grid Game (medium; all)
    - LeetCode 2100 Find Good Days to Rob the Bank (medium; practice)
- **Static range queries (1-D, 2-D)**
    - LeetCode 303 Range Sum Query - Immutable (easy; all)
    - LeetCode 304 Range Sum Query 2D - Immutable (medium; neetcode250, all)
    - LeetCode 2559 Count Vowel Strings in Ranges (medium; all)
    - LeetCode 1685 Sum of Absolute Differences in a Sorted Array (medium; all)
- **Mutable range queries (Fenwick / segment tree)**
    - LeetCode 307 Range Sum Query - Mutable (medium; practice)
    - LeetCode 308 Range Sum Query 2D - Mutable (medium; all)

### 12. Counting and bucket tricks

- **Counting sort over a small value range**
    - LeetCode 1051 Height Checker (easy; all)
    - LeetCode 75 Sort Colors (medium; neetcode250, all)
    - LeetCode 1122 Relative Sort Array (easy; all)
    - LeetCode 274 H-Index (medium; practice)
- **Bucket by frequency**
    - LeetCode 347 Top K Frequent Elements (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 451 Sort Characters By Frequency (medium; all)
    - LeetCode 692 Top K Frequent Words (medium; practice)
- **Bucket by value range / pigeonhole (max gap)**
    - LeetCode 523 Continuous Subarray Sum (medium; all)
- **Count array indexed by value**
    - LeetCode 1394 Find Lucky Integer in an Array (easy; all)
    - LeetCode 1426 Counting Elements (easy; all)
    - LeetCode 2206 Divide Array Into Equal Pairs (easy; all)

### 13. Coordinate compression

- **Rank by sorted order (map value to rank)**
    - LeetCode 506 Relative Ranks (easy; practice)
    - LeetCode 493 Reverse Pairs (hard; practice)
- **Compress before a Fenwick / segment tree**
    - LeetCode 493 Reverse Pairs (hard; practice)
- **Compress sparse coordinates to grid indices**
    - no problem in the data: needs one from LeetCode

### 14. Duplicate detection

- **Seen set (first repeat)**
    - LeetCode 217 Contains Duplicate (easy; blind75, neetcode150, neetcode250, all)
    - LeetCode 349 Intersection of Two Arrays (easy; all)
    - LeetCode 929 Unique Email Addresses (easy; all)
    - LeetCode 1436 Destination City (easy; all)
- **Duplicate within a window (distance or value)**
    - LeetCode 219 Contains Duplicate II (easy; neetcode250, all)
    - LeetCode 220 Contains Duplicate III (hard; practice)
- **Sort and compare neighbours**
    - LeetCode 217 Contains Duplicate (easy; blind75, neetcode150, neetcode250, all)
    - LeetCode 2971 Find Polygon With the Largest Perimeter (medium; all)
    - LeetCode 2966 Divide Array Into Arrays With Max Difference (medium; all)
- **Index marking / Floyd for one duplicate in 1..n**
    - LeetCode 287 Find the Duplicate Number (medium; neetcode150, neetcode250, all)
    - LeetCode 442 Find All Duplicates in an Array (medium; all)
- **Fixed-size sets for rule checks**
    - LeetCode 36 Valid Sudoku (medium; neetcode150, neetcode250, all)
    - LeetCode 2133 Check if Every Row and Column Contains All Numbers (easy; practice)

### 15. Missing and extra number

- **Sum / XOR identities**
    - LeetCode 268 Missing Number (easy; blind75, neetcode150, neetcode250, all)
    - LeetCode 136 Single Number (easy; neetcode150, neetcode250, all)
    - LeetCode 260 Single Number III (medium; all)
    - LeetCode 137 Single Number II (medium; practice)
- **Cyclic sort or sign marking**
    - LeetCode 41 First Missing Positive (hard; neetcode250, all)
    - LeetCode 448 Find All Numbers Disappeared in an Array (easy; all)
    - LeetCode 645 Set Mismatch (easy; all)
- **Set difference**
    - LeetCode 2215 Find the Difference of Two Arrays (easy; all)
    - LeetCode 1436 Destination City (easy; all)
    - LeetCode 3289 The Two Sneaky Numbers of Digitville (easy; practice)
- **Smallest missing value (MEX)**
    - LeetCode 2598 Smallest Missing Non-negative Integer After Operations (medium; practice)
    - LeetCode 2996 Smallest Missing Integer Greater Than Sequential Prefix Sum (easy; practice)
    - LeetCode 2554 Maximum Number of Integers to Choose From a Range I (medium; practice)
- **Missing and repeated pair in a grid**
    - LeetCode 2965 Find Missing and Repeated Values (easy; all)

### 16. Design with hash maps

- **Array plus map for O(1) random access and delete**
    - LeetCode 380 Insert Delete GetRandom O(1) (medium; all)
    - LeetCode 379 Design Phone Directory (medium; all)
    - LeetCode 1429 First Unique Number (medium; all)
- **Time-bucketed counters and rate limiting**
    - LeetCode 359 Logger Rate Limiter (easy; all)
    - LeetCode 362 Design Hit Counter (medium; all)
    - LeetCode 346 Moving Average from Data Stream (easy; all)
    - LeetCode 1348 Tweet Counts Per Frequency (medium; practice)
- **Id to record maps (check-in / check-out, ratings, leaderboards)**
    - LeetCode 1396 Design Underground System (medium; all)
    - LeetCode 1244 Design A Leaderboard (medium; all)
    - LeetCode 2043 Simple Bank System (medium; practice)
    - LeetCode 2353 Design a Food Rating System (medium; all)
- **Map plus heap with lazy deletion**
    - LeetCode 2353 Design a Food Rating System (medium; all)
    - LeetCode 2349 Design a Number Container System (medium; practice)
    - LeetCode 2034 Stock Price Fluctuation (medium; practice)
- **Cache design (LRU / LFU)**
    - LeetCode 146 LRU Cache (medium; neetcode150, neetcode250, all)
    - LeetCode 460 LFU Cache (hard; neetcode250, all)
    - LeetCode 1797 Design Authentication Manager (medium; practice)
- **Counters for game or board state**
    - LeetCode 348 Design Tic-Tac-Toe (medium; all)
    - LeetCode 353 Design Snake Game (medium; all)
- **Sparse data and iterators**
    - LeetCode 1570 Dot Product of Two Sparse Vectors (medium; all)
    - LeetCode 281 Zigzag Iterator (medium; all)
    - LeetCode 604 Design Compressed String Iterator (easy; all)
    - LeetCode 284 Peeking Iterator (medium; practice)
- **Time-versioned key-value store**
    - LeetCode 981 Time Based Key-Value Store (medium; neetcode150, neetcode250, all)
    - LeetCode 1146 Snapshot Array (medium; practice)

### 17. Hashing structures

- **Chaining / open addressing (build a HashSet / HashMap)**
    - LeetCode 705 Design HashSet (easy; neetcode250, all)
    - LeetCode 706 Design HashMap (easy; neetcode250, all)
- **Rolling (polynomial) hash**
    - LeetCode 187 Repeated DNA Sequences (medium; all)
    - LeetCode 1461 Check If a String Contains All Binary Codes of Size K (medium; all)
    - LeetCode 28 Find the Index of the First Occurrence in a String (easy; all)
    - LeetCode 214 Shortest Palindrome (hard; all)
- **Prefix function / Z-function matching**
    - LeetCode 28 Find the Index of the First Occurrence in a String (easy; all)
    - LeetCode 459 Repeated Substring Pattern (easy; practice)
    - LeetCode 214 Shortest Palindrome (hard; all)
    - LeetCode 1408 String Matching in an Array (easy; all)
- **Hashing composite values (tuples, paths, trees)**
    - LeetCode 1496 Path Crossing (easy; all)
    - LeetCode 652 Find Duplicate Subtrees (medium; all)
    - LeetCode 297 Serialize and Deserialize Binary Tree (hard; blind75, neetcode150, neetcode250, all)
    - LeetCode 2564 Substring XOR Queries (medium; practice)
- **Encode / serialize to a hashable key**
    - LeetCode 271 Encode and Decode Strings (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 535 Encode and Decode TinyURL (medium; all)
    - LeetCode 38 Count and Say (medium; practice)
- **Skip list and probabilistic structures**
    - LeetCode 1206 Design Skiplist (hard; practice)
- **Bloom filter, cuckoo hashing, consistent hashing**
    - no problem in the data: needs one from LeetCode

### 18. Sorting-based approaches

- **Custom comparator**
    - LeetCode 179 Largest Number (medium; all)
    - LeetCode 791 Custom Sort String (medium; all)
    - LeetCode 1636 Sort Array by Increasing Frequency (easy; all)
    - LeetCode 2418 Sort the People (easy; all)
- **Sort, then scan neighbours**
    - LeetCode 2971 Find Polygon With the Largest Perimeter (medium; all)
    - LeetCode 2966 Divide Array Into Arrays With Max Difference (medium; all)
    - LeetCode 1913 Maximum Product Difference Between Two Pairs (easy; all)
    - LeetCode 217 Contains Duplicate (easy; blind75, neetcode150, neetcode250, all)
- **Sort plus two pointers**
    - LeetCode 15 3Sum (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 18 4Sum (medium; neetcode250, all)
    - LeetCode 167 Two Sum II - Input Array Is Sorted (medium; neetcode150, neetcode250, all)
    - LeetCode 455 Assign Cookies (easy; all)
- **Sort plus sweep (intervals, events)**
    - LeetCode 56 Merge Intervals (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 435 Non-overlapping Intervals (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 252 Meeting Rooms (easy; blind75, neetcode150, neetcode250, all)
    - LeetCode 253 Meeting Rooms II (medium; blind75, neetcode150, neetcode250, all)
- **Stable multi-key sort**
    - LeetCode 1636 Sort Array by Increasing Frequency (easy; all)
    - LeetCode 2545 Sort the Students by Their Kth Score (medium; practice)
    - LeetCode 1152 Analyze User Website Visit Pattern (medium; all)
- **Implement a sort (merge / quick / heap / counting)**
    - LeetCode 912 Sort an Array (medium; neetcode250, all)
    - LeetCode 148 Sort List (medium; all)
    - LeetCode 75 Sort Colors (medium; neetcode250, all)
    - LeetCode 1051 Height Checker (easy; all)

## Gaps

Patterns with no problem in the data (5); each needs example problems picked and checked on LeetCode, never from memory:

- 5. Range add on a grid (2-D difference array)
- 5. Bookings and flight-style range updates
- 10. Randomized majority
- 13. Compress sparse coordinates to grid indices
- 17. Bloom filter, cuckoo hashing, consistent hashing

Patterns with only one to three problems in the data (51), with how many exist:

- 1. Sliding-window frequency match (3)
- 2. Pair existence by relation (double, difference) (3)
- 2. Two sum on a non-array structure (1)
- 3. Bitmask key for letter sets (3)
- 3. Group records by an owner or first-use key (3)
- 3. Reverse / complement keys (palindrome pairs) (2)
- 4. Longest subarray by first-seen index (balance / zero-sum) (3)
- 4. Prefix XOR with a map (3)
- 4. Prefix parity counts (odd / even sums) (2)
- 4. 2-D prefix sums collapsed to 1-D (submatrix sum) (1)
- 5. 1-D range add, read once at the end (2)
- 5. Event counting / sweep over start and end points (3)
- 6. Sign-flip marking as a visited set (3)
- 6. In-place state encoding (extra bits per cell) (2)
- 6. Array as a functional graph (index to value) (2)
- 7. Three-way partition (Dutch national flag) (1)
- 7. Partition by parity or predicate (2)
- 7. Wiggle / alternating order (2)
- 7. Interleave and shuffle (2)
- 7. Quickselect partition (3)
- 8. Spiral / layer-by-layer walk (3)
- 8. Marker row and column (set zeroes) (2)
- 8. Direction vectors and boundary checks (3)
- 9. Digit and number construction (3)
- 10. Boyer-Moore voting (2)
- 10. Count with a map / sort and take the middle (3)
- 10. Majority on a prefix and a suffix (valid split) (1)
- 11. Product of everything except self (3)
- 11. Mutable range queries (Fenwick / segment tree) (2)
- 12. Bucket by frequency (3)
- 12. Bucket by value range / pigeonhole (max gap) (1)
- 12. Count array indexed by value (3)
- 13. Rank by sorted order (map value to rank) (2)
- 13. Compress before a Fenwick / segment tree (1)
- 14. Duplicate within a window (distance or value) (2)
- 14. Sort and compare neighbours (3)
- 14. Index marking / Floyd for one duplicate in 1..n (2)
- 14. Fixed-size sets for rule checks (2)
- 15. Cyclic sort or sign marking (3)
- 15. Set difference (3)
- 15. Smallest missing value (MEX) (3)
- 15. Missing and repeated pair in a grid (1)
- 16. Array plus map for O(1) random access and delete (3)
- 16. Map plus heap with lazy deletion (3)
- 16. Cache design (LRU / LFU) (3)
- 16. Counters for game or board state (2)
- 16. Time-versioned key-value store (2)
- 17. Chaining / open addressing (build a HashSet / HashMap) (2)
- 17. Encode / serialize to a hashable key (3)
- 17. Skip list and probabilistic structures (1)
- 18. Stable multi-key sort (3)

Other gaps:

- Lessons: only the 15 techniques above exist, so most of the 98 patterns of this list have no lesson, signals, template or pitfalls yet.
- Tabs: the variants written *a / b* need the tabs mockup (rule 13 of the working rules) before any lesson is built.
- Many examples are filed under another topic in the data (Two Pointers, Intervals, Math & Geometry, Bit Manipulation, Linked List, Binary Search). Decide whether the Arrays & Hashing lesson links to them or whether those techniques stay where they are.
- The data is the NeetCode lists plus the practice set; frequently asked problems outside both are not in it, so a pattern with few examples may still have good ones on LeetCode.
