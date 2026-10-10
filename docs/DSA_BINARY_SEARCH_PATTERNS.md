# Binary Search patterns: the exhaustive target list

The target list of every binary-search pattern that can come up on LeetCode, for the Binary Search pattern lessons. The rule is in [DSA.md](DSA.md), decision 32: a topic's patterns section is exhaustive, patterns without a NeetCode problem get **example problems** from LeetCode, and variants of one pattern (lower bound / upper bound) are **tabs** of one lesson. The format follows [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md).

Status: documented only. Today `content/dsa/lessons/binary-search.toml` has 8 techniques (classic, insert-pos, by-count, on-answer, rotated, weighted, partition, peak) and the practice track `p3-binary-search-practice` has 10 problems. Building the rest needs a mockup of the tabs first, then lessons and picked example problems. The example problems below come only from `content/dsa/problems.json` and `practice.json`; where the data has none, the line says so and the problem has to come from LeetCode.

Items written *a / b* in a group are variants for tabs where one lesson covers both (for example "lower bound / upper bound").

1. **Classic boundaries.** exact match (closed range, lo <= hi); lower bound / upper bound (first >= x, first > x); first / last occurrence of a value; floor / ceiling (largest <= x, smallest >= x); count of a value or of a range (upper bound minus lower bound); first true in a monotone yes/no (first bad version); predicate on index against value (a[i] - i, missing numbers); h-index style (n - i against a[i]); nearest value / closest element; insert into a sorted list while keeping order (bisect.insort); membership in a sorted list instead of a hash set.
2. **Rotated arrays.** minimum / rotation point (distinct values); minimum with duplicates (shrink hi by one); search a target (distinct values); search a target with duplicates (worst case O(n)); rotation count (index of the minimum); rotated matrix or circular sorted structure.
3. **Peaks and turning points.** peak in an unsorted array (compare with the neighbour); mountain peak (first descent); search in a mountain array (peak, then two searches); peak in a 2-D matrix (best row or column per step); valley / local minimum; monotone property in an unsorted array (what survives a binary search).
4. **2-D matrices.** rows chained into one sorted list (flatten, i // cols); rows and columns both sorted (staircase / per-row search); count negatives / first one per sorted row; kth smallest in a sorted matrix (search on value, staircase count); smallest common element across sorted rows; peak in a matrix.
5. **Search on the answer (minimise the max / maximise the min).** minimise the maximum (smallest feasible value); maximise the minimum (largest feasible value); smallest speed / rate / capacity that finishes in time; smallest time that completes the work; largest k that still works (length, count, size); split into k groups; greedy feasibility check; DP feasibility check; graph search per guess (BFS / DFS / union-find); sliding window or deque per guess; integer-math answer (square root, perfect square, special array); first time or day a condition breaks (simulate or precompute the order).
6. **Real numbers.** real-valued answer with an epsilon / fixed iteration count; binary search on an average (subtract the guess, check a sum); geometric split (area above equals area below); square root by bisection / Newton; binary search on fractions; ratio optimisation (Dinkelbach, minimum ratio).
7. **Indices of other structures.** timestamp lookup in a per-key sorted list; version / snapshot history; prefix-sum array as the sorted index; interval boundaries / calendar; per-character position lists (next occurrence); sorted keys + offline queries; sorted words / prefixes (autocomplete); BST as an implicit sorted array; monotonic stack as the sorted index (bisect on the stack).
8. **Kth element problems.** kth of two sorted arrays / median; kth smallest in a sorted matrix; kth smallest pair distance; kth smallest product / sum of two sorted arrays; kth smallest subarray sum / range sum; kth missing positive / missing element; kth smallest in a multiplication table / ugly numbers; kth smallest fraction.
9. **Counting-based search.** count of elements <= x decides the side; count of missing numbers before index i; count pairs under a bound; count triples (fix two, search the third); count by blocks (digits, triangular numbers); count nodes by descending a complete tree; count inversion-like pairs while merging; count negatives / positives in sorted data.
10. **Unknown size / exponential search.** sorted array of unknown length (double the index, then bisect); exponential search for the upper bound of the answer; galloping merge of two sorted lists.
11. **Oracle / interactive.** guess higher / lower; hidden matrix behind an API (binary-search each row); comparison API (weighing groups); mountain array with a call budget; region queries on a hidden grid (split until empty); majority / candidate through queries; noisy or lying oracle.
12. **Binary lifting (cross-reference).** k-th ancestor with jump pointers; lowest common ancestor by lifting; jump pointers over an array (doubling next-index tables); first ancestor that satisfies a condition (lifting + monotone test).
13. **Parametric search.** optimisation to decision (fix the answer, check feasibility); fractional programming (maximum average, minimum ratio); bottleneck / minimax path (search the weight, check connectivity); maximin path on a grid with BFS; threshold + union-find connectivity; threshold + DAG shortest-path DP.
14. **Binary search + two pointers.** sorted pair search (two pointers / bisect for the complement); bounded pairs and triples (sort, then bisect or squeeze); left fixed, bisect the right end; window validity on prefix sums or sorted values; match two sorted lists (nearest, intersection); binary search on window length, two pointers as the check; pairs with a difference or a bound.
15. **Ternary search.** unimodal array (up then down); unimodal real function (ternary on doubles, golden section); slope test instead of ternary (compare mid and mid + 1); convex integer cost.
16. **Bisect on tails (LIS).** LIS length, strict (bisect_left on tails); longest non-decreasing / obstacle course (bisect_right); sort one dimension, LIS on the other; LIS from both ends (mountain); DP over sorted intervals, bisect on end times; number of LIS (needs a Fenwick tree).
17. **Weighted random pick.** prefix sums + bisect on a random integer; weights from areas (rectangles); uniform pick with exclusions (blacklist remap); reservoir sampling versus a prefix search; weighted pick with updates (Fenwick descent).
18. **Length, hashing and halves.** binary search on length with a rolling hash; meet in the middle (sort one half, bisect for the other).
19. **Inside data structures and offline.** Fenwick / segment-tree descent; ordered set lower bound (SortedList, TreeMap); persistent / versioned structures; offline queries sorted with a moving pointer; parallel binary search.
20. **Pitfalls.** mid rounding: lo = mid stalls unless mid rounds up; closed versus half-open range (lo <= hi versus lo < hi); non-monotone check (the yes/no flips twice); duplicates break the sorted-half test; float precision and iteration counts; answer bounds too tight or too loose; which index to return (lo versus lo - 1); empty input and a single element; overflow of lo + hi and of the check itself; integer ceiling division.

## Coverage today

- Lesson `binary-search.toml`: 8 techniques. They cover group 1 (classic, insert-pos), 2 (rotated), 3 (peak), 5 (on-answer), 8 (partition), 9 (by-count) and 17 (weighted); group 4 only through `Binary Search:classic` (Search a 2D Matrix), and group 6 only through the integer search over the answer. The other groups have no technique or template of their own.
- Practice track `p3-binary-search-practice`: Fair Split, Find a Peak, Find in a Table, Count in Range, Integer Square Root, Kth of Two Lists, First Bad Build, Running Balance, Rotation Count, Shipping Capacity (searching a flip, the answer, partitions).
- Data: 75 problems have pattern "Binary Search" (8 must-learn, 67 practice) and 78 more carry the tag "Binary Search" under another pattern (Two Pointers, Sliding Window, Intervals, Trees, 1-D Dynamic Programming and others), 152 in all.
- Techniques in the data for the pattern: on-answer 22, classic 13, insert-pos 11, rotated 7, peak 6, by-count 6, partition 5, weighted 5.
- This document lists 20 groups and 131 patterns. 112 of them have at least one problem in the data and 19 have none.
- Some technique labels in the data look off for their problem (only the label, not the problem): 1146 Snapshot Array is labelled rotated; 1552 Magnetic Force Between Two Balls is labelled rotated; 2861 Maximum Number of Alloys is labelled rotated; 1482 Minimum Number of Days to Make m Bouquets is labelled classic; 1228 Missing Number In Arithmetic Progression is labelled classic; 744 Find Smallest Letter Greater Than Target is labelled weighted; 1539 Kth Missing Positive Number is labelled weighted; 3399 Smallest Substring With Identical Characters II is labelled peak; 3639 Minimum Time to Activate String is labelled peak. Worth a pass when the lessons are rebuilt.

## Example problems per pattern

Format: `LeetCode <number> <title> (<difficulty>; <lists>)`, up to 4 per pattern, taken from the data. The NeetCode problems come first where the pattern has any.

### 1. Classic boundaries

- **exact match (closed range, lo <= hi)**
    - LeetCode 704 Binary Search (easy; neetcode150, neetcode250, all)
- **lower bound / upper bound (first >= x, first > x)**
    - LeetCode 35 Search Insert Position (easy; neetcode250, all)
    - LeetCode 34 Find First and Last Position of Element in Sorted Array (medium; all)
    - LeetCode 2089 Find Target Indices After Sorting Array (easy; practice)
    - LeetCode 744 Find Smallest Letter Greater Than Target (easy; practice)
- **first / last occurrence of a value**
    - LeetCode 34 Find First and Last Position of Element in Sorted Array (medium; all)
    - LeetCode 2089 Find Target Indices After Sorting Array (easy; practice)
    - LeetCode 1150 Check If a Number Is Majority Element in a Sorted Array (easy; all)
    - LeetCode 2529 Maximum Count of Positive Integer and Negative Integer (easy; practice)
- **floor / ceiling (largest <= x, smallest >= x)**
    - LeetCode 981 Time Based Key-Value Store (medium; neetcode150, neetcode250, all)
    - LeetCode 744 Find Smallest Letter Greater Than Target (easy; practice)
    - LeetCode 2070 Most Beautiful Item for Each Query (medium; all)
    - LeetCode 436 Find Right Interval (medium; practice)
- **count of a value or of a range (upper bound minus lower bound)**
    - LeetCode 1150 Check If a Number Is Majority Element in a Sorted Array (easy; all)
    - LeetCode 2055 Plates Between Candles (medium; practice)
    - LeetCode 2300 Successful Pairs of Spells and Potions (medium; all)
    - LeetCode 2563 Count the Number of Fair Pairs (medium; all)
- **first true in a monotone yes/no (first bad version)**
    - no problem in the data: needs one from LeetCode
- **predicate on index against value (a[i] - i, missing numbers)**
    - LeetCode 1539 Kth Missing Positive Number (easy; practice)
    - LeetCode 1060 Missing Element in Sorted Array (medium; all)
    - LeetCode 1228 Missing Number In Arithmetic Progression (easy; all)
    - LeetCode 540 Single Element in a Sorted Array (medium; all)
- **h-index style (n - i against a[i])**
    - LeetCode 275 H-Index II (medium; practice)
    - LeetCode 1608 Special Array With X Elements Greater Than or Equal X (easy; all)
- **nearest value / closest element**
    - LeetCode 658 Find K Closest Elements (medium; neetcode250, all)
    - LeetCode 475 Heaters (medium; practice)
    - LeetCode 2476 Closest Nodes Queries in a Binary Search Tree (medium; practice)
    - LeetCode 270 Closest Binary Search Tree Value (easy; all)
- **insert into a sorted list while keeping order (bisect.insort)**
    - LeetCode 35 Search Insert Position (easy; neetcode250, all)
- **membership in a sorted list instead of a hash set**
    - LeetCode 349 Intersection of Two Arrays (easy; all)
    - LeetCode 350 Intersection of Two Arrays II (easy; practice)
    - LeetCode 1214 Two Sum BSTs (medium; all)
    - LeetCode 1346 Check If N and Its Double Exist (easy; practice)

### 2. Rotated arrays

- **minimum / rotation point (distinct values)**
    - LeetCode 153 Find Minimum in Rotated Sorted Array (medium; blind75, neetcode150, neetcode250, all)
- **minimum with duplicates (shrink hi by one)**
    - LeetCode 154 Find Minimum in Rotated Sorted Array II (hard; practice)
- **search a target (distinct values)**
    - LeetCode 33 Search in Rotated Sorted Array (medium; blind75, neetcode150, neetcode250, all)
- **search a target with duplicates (worst case O(n))**
    - LeetCode 81 Search in Rotated Sorted Array II (medium; neetcode250, all)
- **rotation count (index of the minimum)**
    - LeetCode 153 Find Minimum in Rotated Sorted Array (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 154 Find Minimum in Rotated Sorted Array II (hard; practice)
- **rotated matrix or circular sorted structure**
    - no problem in the data: needs one from LeetCode

### 3. Peaks and turning points

- **peak in an unsorted array (compare with the neighbour)**
    - LeetCode 162 Find Peak Element (medium; all)
- **mountain peak (first descent)**
    - LeetCode 852 Peak Index in a Mountain Array (medium; practice)
- **search in a mountain array (peak, then two searches)**
    - LeetCode 1095 Find in Mountain Array (hard; neetcode250, all)
- **peak in a 2-D matrix (best row or column per step)**
    - LeetCode 1901 Find a Peak Element II (medium; practice)
- **valley / local minimum**
    - no problem in the data: needs one from LeetCode
- **monotone property in an unsorted array (what survives a binary search)**
    - LeetCode 1966 Binary Searchable Numbers in an Unsorted Array (medium; all)
    - LeetCode 3639 Minimum Time to Activate String (medium; practice)

### 4. 2-D matrices

- **rows chained into one sorted list (flatten, i // cols)**
    - LeetCode 74 Search a 2D Matrix (medium; neetcode150, neetcode250, all)
- **rows and columns both sorted (staircase / per-row search)**
    - LeetCode 240 Search a 2D Matrix II (medium; practice)
- **count negatives / first one per sorted row**
    - LeetCode 1351 Count Negative Numbers in a Sorted Matrix (easy; practice)
    - LeetCode 1428 Leftmost Column with at Least a One (medium; all)
- **kth smallest in a sorted matrix (search on value, staircase count)**
    - LeetCode 378 Kth Smallest Element in a Sorted Matrix (medium; practice)
- **smallest common element across sorted rows**
    - LeetCode 1198 Find Smallest Common Element in All Rows (medium; all)
- **peak in a matrix**
    - LeetCode 1901 Find a Peak Element II (medium; practice)

### 5. Search on the answer (minimise the max / maximise the min)

- **minimise the maximum (smallest feasible value)**
    - LeetCode 410 Split Array Largest Sum (hard; neetcode250, all)
    - LeetCode 1011 Capacity To Ship Packages Within D Days (medium; neetcode250, all)
    - LeetCode 2439 Minimize Maximum of Array (medium; all)
    - LeetCode 2560 House Robber IV (medium; all)
- **maximise the minimum (largest feasible value)**
    - LeetCode 1231 Divide Chocolate (hard; all)
    - LeetCode 1552 Magnetic Force Between Two Balls (medium; practice)
    - LeetCode 2226 Maximum Candies Allocated to K Children (medium; all)
    - LeetCode 2528 Maximize the Minimum Powered City (hard; practice)
- **smallest speed / rate / capacity that finishes in time**
    - LeetCode 875 Koko Eating Bananas (medium; neetcode150, neetcode250, all)
    - LeetCode 1870 Minimum Speed to Arrive on Time (medium; practice)
    - LeetCode 1283 Find the Smallest Divisor Given a Threshold (medium; practice)
    - LeetCode 1011 Capacity To Ship Packages Within D Days (medium; neetcode250, all)
- **smallest time that completes the work**
    - LeetCode 2187 Minimum Time to Complete Trips (medium; practice)
    - LeetCode 2594 Minimum Time to Repair Cars (medium; all)
    - LeetCode 1482 Minimum Number of Days to Make m Bouquets (medium; practice)
    - LeetCode 3639 Minimum Time to Activate String (medium; practice)
- **largest k that still works (length, count, size)**
    - LeetCode 1891 Cutting Ribbons (medium; all)
    - LeetCode 2861 Maximum Number of Alloys (medium; practice)
    - LeetCode 1898 Maximum Number of Removable Characters (medium; all)
    - LeetCode 2226 Maximum Candies Allocated to K Children (medium; all)
- **split into k groups**
    - LeetCode 410 Split Array Largest Sum (hard; neetcode250, all)
    - LeetCode 1011 Capacity To Ship Packages Within D Days (medium; neetcode250, all)
    - LeetCode 2064 Minimized Maximum of Products Distributed to Any Store (medium; all)
    - LeetCode 1760 Minimum Limit of Balls in a Bag (medium; all)
- **greedy feasibility check**
    - LeetCode 2616 Minimize the Maximum Difference of Pairs (medium; all)
    - LeetCode 2064 Minimized Maximum of Products Distributed to Any Store (medium; all)
    - LeetCode 1760 Minimum Limit of Balls in a Bag (medium; all)
    - LeetCode 1231 Divide Chocolate (hard; all)
- **DP feasibility check**
    - LeetCode 2560 House Robber IV (medium; all)
    - LeetCode 2616 Minimize the Maximum Difference of Pairs (medium; all)
- **graph search per guess (BFS / DFS / union-find)**
    - LeetCode 1631 Path With Minimum Effort (medium; neetcode250, all)
    - LeetCode 1102 Path With Maximum Minimum Value (medium; all)
    - LeetCode 2812 Find the Safest Path in a Grid (medium; all)
    - LeetCode 778 Swim in Rising Water (hard; neetcode150, neetcode250, all)
- **sliding window or deque per guess**
    - LeetCode 2398 Maximum Number of Robots Within Budget (hard; practice)
    - LeetCode 2528 Maximize the Minimum Powered City (hard; practice)
- **integer-math answer (square root, perfect square, special array)**
    - LeetCode 69 Sqrt(x) (easy; neetcode250, all)
    - LeetCode 367 Valid Perfect Square (easy; all)
    - LeetCode 1608 Special Array With X Elements Greater Than or Equal X (easy; all)
    - LeetCode 441 Arranging Coins (easy; all)
- **first time or day a condition breaks (simulate or precompute the order)**
    - LeetCode 1898 Maximum Number of Removable Characters (medium; all)
    - LeetCode 3639 Minimum Time to Activate String (medium; practice)
    - LeetCode 2258 Escape the Spreading Fire (hard; practice)

### 6. Real numbers

- **real-valued answer with an epsilon / fixed iteration count**
    - LeetCode 774 Minimize Max Distance to Gas Station (hard; all)
    - LeetCode 644 Maximum Average Subarray II (hard; all)
- **binary search on an average (subtract the guess, check a sum)**
    - LeetCode 644 Maximum Average Subarray II (hard; all)
- **geometric split (area above equals area below)**
    - LeetCode 3453 Separate Squares I (medium; practice)
- **square root by bisection / Newton**
    - LeetCode 69 Sqrt(x) (easy; neetcode250, all)
    - LeetCode 367 Valid Perfect Square (easy; all)
- **binary search on fractions**
    - no problem in the data: needs one from LeetCode
- **ratio optimisation (Dinkelbach, minimum ratio)**
    - no problem in the data: needs one from LeetCode

### 7. Indices of other structures

- **timestamp lookup in a per-key sorted list**
    - LeetCode 981 Time Based Key-Value Store (medium; neetcode150, neetcode250, all)
    - LeetCode 1348 Tweet Counts Per Frequency (medium; practice)
    - LeetCode 362 Design Hit Counter (medium; all)
- **version / snapshot history**
    - LeetCode 1146 Snapshot Array (medium; practice)
- **prefix-sum array as the sorted index**
    - LeetCode 209 Minimum Size Subarray Sum (medium; neetcode250, all)
    - LeetCode 2055 Plates Between Candles (medium; practice)
    - LeetCode 528 Random Pick with Weight (medium; all)
    - LeetCode 1208 Get Equal Substrings Within Budget (medium; all)
- **interval boundaries / calendar**
    - LeetCode 729 My Calendar I (medium; all)
    - LeetCode 731 My Calendar II (medium; all)
    - LeetCode 352 Data Stream as Disjoint Intervals (hard; all)
    - LeetCode 436 Find Right Interval (medium; practice)
- **per-character position lists (next occurrence)**
    - LeetCode 792 Number of Matching Subsequences (medium; practice)
    - LeetCode 1055 Shortest Way to Form String (medium; all)
- **sorted keys + offline queries**
    - LeetCode 2070 Most Beautiful Item for Each Query (medium; all)
    - LeetCode 826 Most Profit Assigning Work (medium; practice)
    - LeetCode 2300 Successful Pairs of Spells and Potions (medium; all)
    - LeetCode 2251 Number of Flowers in Full Bloom (hard; all)
- **sorted words / prefixes (autocomplete)**
    - LeetCode 1268 Search Suggestions System (medium; all)
- **BST as an implicit sorted array**
    - LeetCode 270 Closest Binary Search Tree Value (easy; all)
    - LeetCode 2476 Closest Nodes Queries in a Binary Search Tree (medium; practice)
- **monotonic stack as the sorted index (bisect on the stack)**
    - LeetCode 2940 Find Building Where Alice and Bob Can Meet (hard; all)
    - LeetCode 2454 Next Greater Element IV (hard; practice)
    - LeetCode 456 132 Pattern (medium; all)
    - LeetCode 1793 Maximum Score of a Good Subarray (hard; all)

### 8. Kth element problems

- **kth of two sorted arrays / median**
    - LeetCode 4 Median of Two Sorted Arrays (hard; neetcode150, neetcode250, all)
- **kth smallest in a sorted matrix**
    - LeetCode 378 Kth Smallest Element in a Sorted Matrix (medium; practice)
- **kth smallest pair distance**
    - LeetCode 719 Find K-th Smallest Pair Distance (hard; all)
- **kth smallest product / sum of two sorted arrays**
    - LeetCode 2040 Kth Smallest Product of Two Sorted Arrays (hard; all)
- **kth smallest subarray sum / range sum**
    - LeetCode 1508 Range Sum of Sorted Subarray Sums (medium; all)
- **kth missing positive / missing element**
    - LeetCode 1539 Kth Missing Positive Number (easy; practice)
    - LeetCode 1060 Missing Element in Sorted Array (medium; all)
- **kth smallest in a multiplication table / ugly numbers**
    - no problem in the data: needs one from LeetCode
- **kth smallest fraction**
    - no problem in the data: needs one from LeetCode

### 9. Counting-based search

- **count of elements <= x decides the side**
    - LeetCode 378 Kth Smallest Element in a Sorted Matrix (medium; practice)
    - LeetCode 719 Find K-th Smallest Pair Distance (hard; all)
    - LeetCode 2040 Kth Smallest Product of Two Sorted Arrays (hard; all)
    - LeetCode 1508 Range Sum of Sorted Subarray Sums (medium; all)
- **count of missing numbers before index i**
    - LeetCode 1539 Kth Missing Positive Number (easy; practice)
    - LeetCode 1060 Missing Element in Sorted Array (medium; all)
- **count pairs under a bound**
    - LeetCode 2563 Count the Number of Fair Pairs (medium; all)
    - LeetCode 2824 Count Pairs Whose Sum is Less than Target (easy; practice)
    - LeetCode 1498 Number of Subsequences That Satisfy the Given Sum Condition (medium; all)
    - LeetCode 611 Valid Triangle Number (medium; practice)
- **count triples (fix two, search the third)**
    - LeetCode 611 Valid Triangle Number (medium; practice)
    - LeetCode 259 3Sum Smaller (medium; all)
    - LeetCode 1498 Number of Subsequences That Satisfy the Given Sum Condition (medium; all)
- **count by blocks (digits, triangular numbers)**
    - LeetCode 400 Nth Digit (medium; practice)
    - LeetCode 441 Arranging Coins (easy; all)
    - LeetCode 754 Reach a Number (medium; practice)
- **count nodes by descending a complete tree**
    - LeetCode 222 Count Complete Tree Nodes (medium; practice)
- **count inversion-like pairs while merging**
    - LeetCode 493 Reverse Pairs (hard; practice)
- **count negatives / positives in sorted data**
    - LeetCode 2529 Maximum Count of Positive Integer and Negative Integer (easy; practice)
    - LeetCode 1351 Count Negative Numbers in a Sorted Matrix (easy; practice)

### 10. Unknown size / exponential search

- **sorted array of unknown length (double the index, then bisect)**
    - no problem in the data: needs one from LeetCode
- **exponential search for the upper bound of the answer**
    - no problem in the data: needs one from LeetCode
- **galloping merge of two sorted lists**
    - no problem in the data: needs one from LeetCode

### 11. Oracle / interactive

- **guess higher / lower**
    - LeetCode 374 Guess Number Higher or Lower (easy; neetcode250, all)
- **hidden matrix behind an API (binary-search each row)**
    - LeetCode 1428 Leftmost Column with at Least a One (medium; all)
- **comparison API (weighing groups)**
    - LeetCode 1533 Find the Index of the Large Integer (medium; all)
- **mountain array with a call budget**
    - LeetCode 1095 Find in Mountain Array (hard; neetcode250, all)
- **region queries on a hidden grid (split until empty)**
    - LeetCode 1274 Number of Ships in a Rectangle (hard; all)
- **majority / candidate through queries**
    - LeetCode 1538 Guess the Majority in a Hidden Array (medium; all)
- **noisy or lying oracle**
    - no problem in the data: needs one from LeetCode

### 12. Binary lifting (cross-reference)

- **k-th ancestor with jump pointers**
    - no problem in the data: needs one from LeetCode
- **lowest common ancestor by lifting**
    - LeetCode 1650 Lowest Common Ancestor of a Binary Tree III (medium; all)
    - LeetCode 236 Lowest Common Ancestor of a Binary Tree (medium; all)
    - LeetCode 235 Lowest Common Ancestor of a Binary Search Tree (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 2096 Step-By-Step Directions From a Binary Tree Node to Another (medium; all)
- **jump pointers over an array (doubling next-index tables)**
    - no problem in the data: needs one from LeetCode
- **first ancestor that satisfies a condition (lifting + monotone test)**
    - no problem in the data: needs one from LeetCode

### 13. Parametric search

- **optimisation to decision (fix the answer, check feasibility)**
    - LeetCode 410 Split Array Largest Sum (hard; neetcode250, all)
    - LeetCode 774 Minimize Max Distance to Gas Station (hard; all)
    - LeetCode 2528 Maximize the Minimum Powered City (hard; practice)
    - LeetCode 3600 Maximize Spanning Tree Stability with Upgrades (hard; practice)
- **fractional programming (maximum average, minimum ratio)**
    - LeetCode 644 Maximum Average Subarray II (hard; all)
- **bottleneck / minimax path (search the weight, check connectivity)**
    - LeetCode 1631 Path With Minimum Effort (medium; neetcode250, all)
    - LeetCode 1102 Path With Maximum Minimum Value (medium; all)
    - LeetCode 778 Swim in Rising Water (hard; neetcode150, neetcode250, all)
    - LeetCode 3419 Minimize the Maximum Edge Weight of Graph (medium; practice)
- **maximin path on a grid with BFS**
    - LeetCode 2812 Find the Safest Path in a Grid (medium; all)
    - LeetCode 1102 Path With Maximum Minimum Value (medium; all)
- **threshold + union-find connectivity**
    - LeetCode 3613 Minimize Maximum Component Cost (medium; practice)
    - LeetCode 3600 Maximize Spanning Tree Stability with Upgrades (hard; practice)
    - LeetCode 3532 Path Existence Queries in a Graph I (medium; practice)
- **threshold + DAG shortest-path DP**
    - LeetCode 3620 Network Recovery Pathways (hard; practice)

### 14. Binary search + two pointers

- **sorted pair search (two pointers / bisect for the complement)**
    - LeetCode 167 Two Sum II - Input Array Is Sorted (medium; neetcode150, neetcode250, all)
    - LeetCode 1099 Two Sum Less Than K (easy; all)
    - LeetCode 633 Sum of Square Numbers (medium; all)
    - LeetCode 2824 Count Pairs Whose Sum is Less than Target (easy; practice)
- **bounded pairs and triples (sort, then bisect or squeeze)**
    - LeetCode 259 3Sum Smaller (medium; all)
    - LeetCode 611 Valid Triangle Number (medium; practice)
    - LeetCode 1498 Number of Subsequences That Satisfy the Given Sum Condition (medium; all)
    - LeetCode 2563 Count the Number of Fair Pairs (medium; all)
- **left fixed, bisect the right end**
    - LeetCode 209 Minimum Size Subarray Sum (medium; neetcode250, all)
    - LeetCode 713 Subarray Product Less Than K (medium; all)
    - LeetCode 1208 Get Equal Substrings Within Budget (medium; all)
    - LeetCode 1838 Frequency of the Most Frequent Element (medium; all)
- **window validity on prefix sums or sorted values**
    - LeetCode 2302 Count Subarrays With Score Less Than K (hard; practice)
    - LeetCode 1004 Max Consecutive Ones III (medium; all)
    - LeetCode 2779 Maximum Beauty of an Array After Applying Operation (medium; all)
    - LeetCode 3634 Minimum Removals to Balance Array (medium; practice)
- **match two sorted lists (nearest, intersection)**
    - LeetCode 475 Heaters (medium; practice)
    - LeetCode 349 Intersection of Two Arrays (easy; all)
    - LeetCode 350 Intersection of Two Arrays II (easy; practice)
    - LeetCode 1214 Two Sum BSTs (medium; all)
- **binary search on window length, two pointers as the check**
    - LeetCode 2024 Maximize the Confusion of an Exam (medium; practice)
    - LeetCode 2398 Maximum Number of Robots Within Budget (hard; practice)
    - LeetCode 2528 Maximize the Minimum Powered City (hard; practice)
- **pairs with a difference or a bound**
    - LeetCode 532 K-diff Pairs in an Array (medium; practice)
    - LeetCode 825 Friends Of Appropriate Ages (medium; practice)
    - LeetCode 1346 Check If N and Its Double Exist (easy; practice)
    - LeetCode 1099 Two Sum Less Than K (easy; all)

### 15. Ternary search

- **unimodal array (up then down)**
    - LeetCode 852 Peak Index in a Mountain Array (medium; practice)
    - LeetCode 1095 Find in Mountain Array (hard; neetcode250, all)
- **unimodal real function (ternary on doubles, golden section)**
    - no problem in the data: needs one from LeetCode
- **slope test instead of ternary (compare mid and mid + 1)**
    - LeetCode 162 Find Peak Element (medium; all)
    - LeetCode 852 Peak Index in a Mountain Array (medium; practice)
- **convex integer cost**
    - no problem in the data: needs one from LeetCode

### 16. Bisect on tails (LIS)

- **LIS length, strict (bisect_left on tails)**
    - LeetCode 300 Longest Increasing Subsequence (medium; blind75, neetcode150, neetcode250, all)
- **longest non-decreasing / obstacle course (bisect_right)**
    - LeetCode 1964 Find the Longest Valid Obstacle Course at Each Position (hard; all)
- **sort one dimension, LIS on the other**
    - LeetCode 354 Russian Doll Envelopes (hard; all)
- **LIS from both ends (mountain)**
    - LeetCode 1671 Minimum Number of Removals to Make Mountain Array (hard; all)
- **DP over sorted intervals, bisect on end times**
    - LeetCode 1235 Maximum Profit in Job Scheduling (hard; all)
    - LeetCode 1751 Maximum Number of Events That Can Be Attended II (hard; practice)
    - LeetCode 2008 Maximum Earnings From Taxi (medium; practice)
- **number of LIS (needs a Fenwick tree)**
    - no problem in the data: needs one from LeetCode

### 17. Weighted random pick

- **prefix sums + bisect on a random integer**
    - LeetCode 528 Random Pick with Weight (medium; all)
- **weights from areas (rectangles)**
    - LeetCode 497 Random Point in Non-overlapping Rectangles (medium; practice)
- **uniform pick with exclusions (blacklist remap)**
    - LeetCode 710 Random Pick with Blacklist (hard; practice)
- **reservoir sampling versus a prefix search**
    - LeetCode 382 Linked List Random Node (medium; practice)
    - LeetCode 497 Random Point in Non-overlapping Rectangles (medium; practice)
- **weighted pick with updates (Fenwick descent)**
    - no problem in the data: needs one from LeetCode

### 18. Length, hashing and halves

- **binary search on length with a rolling hash**
    - LeetCode 718 Maximum Length of Repeated Subarray (medium; practice)
- **meet in the middle (sort one half, bisect for the other)**
    - LeetCode 2035 Partition Array Into Two Arrays to Minimize Sum Difference (hard; practice)
    - LeetCode 805 Split Array With Same Average (hard; all)

### 19. Inside data structures and offline

- **Fenwick / segment-tree descent**
    - LeetCode 2940 Find Building Where Alice and Bob Can Meet (hard; all)
    - LeetCode 1964 Find the Longest Valid Obstacle Course at Each Position (hard; all)
    - LeetCode 493 Reverse Pairs (hard; practice)
- **ordered set lower bound (SortedList, TreeMap)**
    - LeetCode 729 My Calendar I (medium; all)
    - LeetCode 731 My Calendar II (medium; all)
    - LeetCode 352 Data Stream as Disjoint Intervals (hard; all)
    - LeetCode 220 Contains Duplicate III (hard; practice)
- **persistent / versioned structures**
    - LeetCode 1146 Snapshot Array (medium; practice)
- **offline queries sorted with a moving pointer**
    - LeetCode 2251 Number of Flowers in Full Bloom (hard; all)
    - LeetCode 1851 Minimum Interval to Include Each Query (hard; neetcode150, neetcode250, all)
    - LeetCode 2070 Most Beautiful Item for Each Query (medium; all)
- **parallel binary search**
    - no problem in the data: needs one from LeetCode

### 20. Pitfalls

- **mid rounding: lo = mid stalls unless mid rounds up**
    - LeetCode 441 Arranging Coins (easy; all)
    - LeetCode 69 Sqrt(x) (easy; neetcode250, all)
    - LeetCode 367 Valid Perfect Square (easy; all)
    - LeetCode 754 Reach a Number (medium; practice)
- **closed versus half-open range (lo <= hi versus lo < hi)**
    - LeetCode 704 Binary Search (easy; neetcode150, neetcode250, all)
    - LeetCode 35 Search Insert Position (easy; neetcode250, all)
    - LeetCode 34 Find First and Last Position of Element in Sorted Array (medium; all)
- **non-monotone check (the yes/no flips twice)**
    - LeetCode 1966 Binary Searchable Numbers in an Unsorted Array (medium; all)
    - LeetCode 1011 Capacity To Ship Packages Within D Days (medium; neetcode250, all)
    - LeetCode 2560 House Robber IV (medium; all)
- **duplicates break the sorted-half test**
    - LeetCode 81 Search in Rotated Sorted Array II (medium; neetcode250, all)
    - LeetCode 154 Find Minimum in Rotated Sorted Array II (hard; practice)
- **float precision and iteration counts**
    - LeetCode 644 Maximum Average Subarray II (hard; all)
    - LeetCode 774 Minimize Max Distance to Gas Station (hard; all)
- **answer bounds too tight or too loose**
    - LeetCode 875 Koko Eating Bananas (medium; neetcode150, neetcode250, all)
    - LeetCode 1011 Capacity To Ship Packages Within D Days (medium; neetcode250, all)
    - LeetCode 2187 Minimum Time to Complete Trips (medium; practice)
    - LeetCode 1231 Divide Chocolate (hard; all)
- **which index to return (lo versus lo - 1)**
    - LeetCode 744 Find Smallest Letter Greater Than Target (easy; practice)
    - LeetCode 35 Search Insert Position (easy; neetcode250, all)
    - LeetCode 2529 Maximum Count of Positive Integer and Negative Integer (easy; practice)
- **empty input and a single element**
    - LeetCode 704 Binary Search (easy; neetcode150, neetcode250, all)
    - LeetCode 35 Search Insert Position (easy; neetcode250, all)
- **overflow of lo + hi and of the check itself**
    - LeetCode 69 Sqrt(x) (easy; neetcode250, all)
    - LeetCode 367 Valid Perfect Square (easy; all)
- **integer ceiling division**
    - LeetCode 875 Koko Eating Bananas (medium; neetcode150, neetcode250, all)
    - LeetCode 1011 Capacity To Ship Packages Within D Days (medium; neetcode250, all)

## Gaps

- Patterns with no problem in the data (19): first true in a monotone yes/no (first bad version) (group 1); rotated matrix or circular sorted structure (group 2); valley / local minimum (group 3); binary search on fractions (group 6); ratio optimisation (Dinkelbach, minimum ratio) (group 6); kth smallest in a multiplication table / ugly numbers (group 8); kth smallest fraction (group 8); sorted array of unknown length (double the index, then bisect) (group 10); exponential search for the upper bound of the answer (group 10); galloping merge of two sorted lists (group 10); noisy or lying oracle (group 11); k-th ancestor with jump pointers (group 12); jump pointers over an array (doubling next-index tables) (group 12); first ancestor that satisfies a condition (lifting + monotone test) (group 12); unimodal real function (ternary on doubles, golden section) (group 15); convex integer cost (group 15); number of LIS (needs a Fenwick tree) (group 16); weighted pick with updates (Fenwick descent) (group 17); parallel binary search (group 19). Each needs one problem picked from LeetCode and checked there, not from memory.
- Patterns with exactly one problem (43), thin for a lesson with tabs: exact match (closed range, lo <= hi) (704); insert into a sorted list while keeping order (bisect.insort) (35); minimum / rotation point (distinct values) (153); minimum with duplicates (shrink hi by one) (154); search a target (distinct values) (33); search a target with duplicates (worst case O(n)) (81); peak in an unsorted array (compare with the neighbour) (162); mountain peak (first descent) (852); search in a mountain array (peak, then two searches) (1095); peak in a 2-D matrix (best row or column per step) (1901); rows chained into one sorted list (flatten, i // cols) (74); rows and columns both sorted (staircase / per-row search) (240); kth smallest in a sorted matrix (search on value, staircase count) (378); smallest common element across sorted rows (1198); peak in a matrix (1901); binary search on an average (subtract the guess, check a sum) (644); geometric split (area above equals area below) (3453); version / snapshot history (1146); sorted words / prefixes (autocomplete) (1268); kth of two sorted arrays / median (4); kth smallest in a sorted matrix (378); kth smallest pair distance (719); kth smallest product / sum of two sorted arrays (2040); kth smallest subarray sum / range sum (1508); count nodes by descending a complete tree (222); count inversion-like pairs while merging (493); guess higher / lower (374); hidden matrix behind an API (binary-search each row) (1428); comparison API (weighing groups) (1533); mountain array with a call budget (1095); region queries on a hidden grid (split until empty) (1274); majority / candidate through queries (1538); fractional programming (maximum average, minimum ratio) (644); threshold + DAG shortest-path DP (3620); LIS length, strict (bisect_left on tails) (300); longest non-decreasing / obstacle course (bisect_right) (1964); sort one dimension, LIS on the other (354); LIS from both ends (mountain) (1671); prefix sums + bisect on a random integer (528); weights from areas (rectangles) (497); uniform pick with exclusions (blacklist remap) (710); binary search on length with a rolling hash (718); persistent / versioned structures (1146).
- Groups 10 (unknown size / exponential search) and 12 (binary lifting, which belongs with the tree algorithms in [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md) group 10) have little or no support in the data. Group 12 lists only problems that carry the tag Binary Lifting (lowest common ancestor ones), and some of them do not need lifting.
- Groups 5 and 13 overlap on purpose (search on the answer versus parametric search over a graph or a ratio): a lesson should say when the check is a graph or union-find pass rather than a greedy loop.
- Many problems tagged Binary Search live in other patterns (Two Pointers, Sliding Window, Intervals, 1-D Dynamic Programming, Advanced Graphs). The lesson should link to them rather than copy them, and the Problems tab should decide which pattern owns each.
- Group 16 (bisect on tails) is taught today under 1-D Dynamic Programming (`lis`); the Binary Search lesson would cross-reference it.
- The pitfalls group (20) is spread through the `pitfalls` lines of the 8 existing techniques today. A pitfalls tab per lesson, or a shared checklist, needs a decision with the mockup.
- Not yet decided: whether the extra patterns become more techniques inside Binary Search or new groups, how the tabs look (rule 13, needs a mockup), and the final example problems per pattern (to be checked against LeetCode).
