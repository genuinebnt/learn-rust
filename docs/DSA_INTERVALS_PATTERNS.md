# Interval patterns: the exhaustive target list

The target list (2026-10-10) of every interval pattern that can come up on LeetCode, for the Intervals pattern lessons. It follows the rule in
[DSA.md](DSA.md), decision 32, the same way [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md) does for graphs: a topic's patterns section is
**exhaustive**, patterns without a NeetCode problem get **example problems** from LeetCode, and variants of one pattern (for example
"minimum rooms: heap / two pointers") are **tabs** of one lesson.

Status: documented only. Today `content/dsa/lessons/intervals.toml` has 4 techniques (merge, by-end, calendar, sweep). The list below has 19 groups and 86 patterns. Building the rest needs a mockup of the tabs first, then lessons and picked example problems.

Items written *a / b* in a group are variants for tabs where one lesson covers both (for example "intersection of two lists / of k lists"). Text in parentheses names the key idea or the alternative implementations of the item.

1. **Merge and combine.** merge overlapping intervals (closed / half-open touching rule); insert interval (linear three-phase scan / binary search for the window); remove covered intervals (sort by start, end descending); count groups of overlapping ranges (components of the overlap graph); merge k sorted interval lists (flatten and sort / heap of list heads).
2. **Intersection and subtraction.** intersection of two sorted interval lists (two pointers) / of k lists (running overlap count); common slot of a given length (two pointers over two sorted lists); remove (subtract) an interval from a set / difference of two interval sets.
3. **Selection by earliest end (non-overlapping).** minimum removals to leave non-overlapping intervals (sort by end / DP); maximum non-overlapping intervals (activity selection) / longest chain of pairs.
4. **Covering points and ranges.** minimum points that stab every interval (arrows, sort by end); at least two (k) points per interval (stabbing with multiplicity); minimum intervals to cover a range (sort by start, furthest reach) / as a jump game; is every integer of a range covered (merge / difference array).
5. **Meeting rooms.** can attend all meetings (sort, compare neighbours); minimum rooms (min-heap of ends / sorted starts and ends with two pointers / events / difference array); which room or chair (lowest free id, two heaps); capacity over time (running load, car pooling).
6. **Line sweep.** events: start +1 and end -1, with the tie order at equal times; maximum overlap and where it happens (busiest point, brightest position); sweep with an active set (heap / ordered multiset) while events stream; sparse coordinates (sorted map of deltas / coordinate compression).
7. **Range updates with difference arrays.** 1-D difference array (add on ranges, one prefix pass); 2-D difference array (rectangle adds); sliding difference (apply flips on the fly, expire them); difference array inside a binary search on the answer; online range add (lazy segment tree / Fenwick tree with range add); range assign or paint (union-find skip pointers / interval map).
8. **Interval scheduling: weighted, bounded and deadline.** weighted interval scheduling (sort by end, DP with binary search for the last compatible job); weighted with at most k picks (dp over index and picks left); position DP over coordinates (rides along a line); attend the most events, one per day (sort by start, min-heap of ends); deadline scheduling (sort by deadline, max-heap, evict the longest); two non-overlapping events with the best sum (prefix max + binary search).
9. **Calendar booking.** no double booking (sorted starts and bisect on neighbours / ordered map / segment tree); up to k overlaps allowed (two lists / map of deltas / lazy segment tree); interval set with add, remove and query (merge on insert); disjoint intervals from a stream (ordered map of starts / union-find on values); time-bucketed counts and log ranges (sorted timestamps + bisect).
10. **Gaps and free time.** missing ranges / complement within a range (sweep with a cursor); free time in the union of busy intervals (merge, then read the gaps); employee free time (k sorted lists: flatten and sort / heap / sweep counting zero); free time after moving meetings (gap list + sliding window / best gap).
11. **Interval tree and stabbing queries.** count intervals containing a point (sorted starts and ends, two binary searches); list intervals containing a point (interval tree: max end per node); next interval at or after a point (sort + binary search / ordered map ceiling); stabbing count under updates (segment tree over compressed coordinates).
12. **Skyline problem.** skyline by sweep (max-heap with lazy deletion / ordered multiset of heights); skyline by divide and conquer (merge two skylines); range assign and max (falling squares: segment tree over compressed coordinates).
13. **Interval DP (cross-reference to 2-D Dynamic Programming).** interval DP over [l, r] (split point, lengths ascending); game and palindrome DP over ranges (stone games, palindromic subsequence).
14. **Union length and area.** union length of 1-D intervals (merge, sum the pieces); union area of rectangles (sweep + segment tree with cover counts); overlap of two rectangles (clamp min / max, inclusion-exclusion); projection to the axes (merge the x-ranges and the y-ranges of shapes); sampling by length or area (prefix sums + binary search over disjoint ranges); new area painted per day (skip pointers / ordered set).
15. **Queries on intervals (offline sort + heap).** smallest interval containing each query (sort both, min-heap by size, pop the expired); count of intervals containing each query (two sorted arrays + bisect); sorted queries with items pushed into a heap as they become eligible; offline with union-find (process by size, paint, skip painted).
16. **Circular intervals.** unroll the circle (double the array or take indices mod n); wrap-around interval split into two (start > end); circular time differences (sort, then close the circle with the wrap gap); cover a circle with arcs (cut at a point, then a linear cover); circular difference array.
17. **Interval graphs and matching.** overlap number = colours = rooms (interval-graph colouring) / independent set = activity selection / stabbing = disjoint count; assign points or days to intervals (sort, heap by end); greedy match of two sorted sequences (two pointers).
18. **Intervals built from other data.** runs from sorted values (summary ranges); occurrence spans (first and last index, then merge); marked positions in a string (bold tags); reach windows [i - r, i + r] (taps, lamps); projections of 2-D shapes; smallest range covering one element from each of k lists (sort events + sliding window / heap of heads).
19. **Core implementation patterns.** sort key choice (start / end / start then end descending); closed versus half-open endpoints, and the touching rule; event encoding and tie order at equal times; last-kept end pointer / merged-list tail; bisect on sorted starts / heap of ends / ordered map; sentinel intervals and empty input; coordinate compression; difference array / prefix sum on dense coordinates; segment tree / Fenwick tree over compressed coordinates; union-find skip pointers.

## Coverage today

The four techniques in `content/dsa/lessons/intervals.toml`, and what each one teaches:

- **Intervals:merge** (must-learn: LeetCode 57 Insert Interval): sort by start, extend the last merged interval or open a new one; the pitfalls cover the touching rule and the three-phase insert.
- **Intervals:by-end** (must-learn: LeetCode 435 Non-overlapping Intervals): sort by end, keep what fits, count the rest as removals.
- **Intervals:calendar** (must-learn: LeetCode 729 My Calendar I): sorted starts and bisect on the two neighbours, half-open intervals.
- **Intervals:sweep** (must-learn: LeetCode 1851 Minimum Interval to Include Each Query): events and a min-heap of ends for minimum rooms; the signals name the per-query smallest containing range.

Of the 86 patterns above, counted against those four lessons:

- **Covered (11)**: the template and pitfalls of a lesson teach it directly.
    - 1. merge overlapping intervals (closed / half-open touching rule) (Intervals:merge)
    - 1. insert interval (linear three-phase scan / binary search for the window) (Intervals:merge)
    - 3. minimum removals to leave non-overlapping intervals (sort by end / DP) (Intervals:by-end)
    - 3. maximum non-overlapping intervals (activity selection) / longest chain of pairs (Intervals:by-end)
    - 4. minimum points that stab every interval (arrows, sort by end) (Intervals:by-end)
    - 5. minimum rooms (min-heap of ends / sorted starts and ends with two pointers / events / difference array) (Intervals:sweep)
    - 6. events: start +1 and end -1, with the tie order at equal times (Intervals:sweep)
    - 9. no double booking (sorted starts and bisect on neighbours / ordered map / segment tree) (Intervals:calendar)
    - 15. smallest interval containing each query (sort both, min-heap by size, pop the expired) (Intervals:sweep)
    - 19. event encoding and tie order at equal times (Intervals:sweep)
    - 19. last-kept end pointer / merged-list tail (Intervals:merge)
- **Partly (23)**: the lesson's idea applies, but the variant, the data structure or the check is not taught.
    - 1. remove covered intervals (sort by start, end descending) (Intervals:merge)
    - 1. count groups of overlapping ranges (components of the overlap graph) (Intervals:merge)
    - 4. minimum intervals to cover a range (sort by start, furthest reach) / as a jump game (Intervals:by-end)
    - 5. can attend all meetings (sort, compare neighbours) (Intervals:merge)
    - 5. which room or chair (lowest free id, two heaps) (Intervals:sweep)
    - 5. capacity over time (running load, car pooling) (Intervals:sweep)
    - 6. maximum overlap and where it happens (busiest point, brightest position) (Intervals:sweep)
    - 6. sweep with an active set (heap / ordered multiset) while events stream (Intervals:sweep)
    - 9. up to k overlaps allowed (two lists / map of deltas / lazy segment tree) (Intervals:calendar)
    - 9. disjoint intervals from a stream (ordered map of starts / union-find on values) (Intervals:calendar)
    - 9. time-bucketed counts and log ranges (sorted timestamps + bisect) (Intervals:calendar)
    - 10. missing ranges / complement within a range (sweep with a cursor) (Intervals:merge)
    - 10. free time in the union of busy intervals (merge, then read the gaps) (Intervals:merge)
    - 10. employee free time (k sorted lists: flatten and sort / heap / sweep counting zero) (Intervals:merge)
    - 11. next interval at or after a point (sort + binary search / ordered map ceiling) (Intervals:calendar)
    - 14. union length of 1-D intervals (merge, sum the pieces) (Intervals:merge)
    - 14. projection to the axes (merge the x-ranges and the y-ranges of shapes) (Intervals:merge)
    - 18. marked positions in a string (bold tags) (Intervals:merge)
    - 18. reach windows [i - r, i + r] (taps, lamps) (Intervals:by-end)
    - 18. projections of 2-D shapes (Intervals:merge)
    - 19. sort key choice (start / end / start then end descending) (Intervals:merge)
    - 19. closed versus half-open endpoints, and the touching rule (Intervals:merge)
    - 19. bisect on sorted starts / heap of ends / ordered map (Intervals:calendar)
- **Cross-reference (2)**: belongs to the 2-D Dynamic Programming track (technique `2-D Dynamic Programming:interval`); the Intervals lessons only link to it.
    - 13. interval DP over [l, r] (split point, lengths ascending)
    - 13. game and palindrome DP over ranges (stone games, palindromic subsequence)
- **Not covered (50)**: no lesson yet.
    - 1. Merge and combine: merge k sorted interval lists (flatten and sort / heap of list heads).
    - 2. Intersection and subtraction: intersection of two sorted interval lists (two pointers) / of k lists (running overlap count); common slot of a given length (two pointers over two sorted lists); remove (subtract) an interval from a set / difference of two interval sets.
    - 4. Covering points and ranges: at least two (k) points per interval (stabbing with multiplicity); is every integer of a range covered (merge / difference array).
    - 6. Line sweep: sparse coordinates (sorted map of deltas / coordinate compression).
    - 7. Range updates with difference arrays: 1-D difference array (add on ranges, one prefix pass); 2-D difference array (rectangle adds); sliding difference (apply flips on the fly, expire them); difference array inside a binary search on the answer; online range add (lazy segment tree / Fenwick tree with range add); range assign or paint (union-find skip pointers / interval map).
    - 8. Interval scheduling: weighted, bounded and deadline: weighted interval scheduling (sort by end, DP with binary search for the last compatible job); weighted with at most k picks (dp over index and picks left); position DP over coordinates (rides along a line); attend the most events, one per day (sort by start, min-heap of ends); deadline scheduling (sort by deadline, max-heap, evict the longest); two non-overlapping events with the best sum (prefix max + binary search).
    - 9. Calendar booking: interval set with add, remove and query (merge on insert).
    - 10. Gaps and free time: free time after moving meetings (gap list + sliding window / best gap).
    - 11. Interval tree and stabbing queries: count intervals containing a point (sorted starts and ends, two binary searches); list intervals containing a point (interval tree: max end per node); stabbing count under updates (segment tree over compressed coordinates).
    - 12. Skyline problem: skyline by sweep (max-heap with lazy deletion / ordered multiset of heights); skyline by divide and conquer (merge two skylines); range assign and max (falling squares: segment tree over compressed coordinates).
    - 14. Union length and area: union area of rectangles (sweep + segment tree with cover counts); overlap of two rectangles (clamp min / max, inclusion-exclusion); sampling by length or area (prefix sums + binary search over disjoint ranges); new area painted per day (skip pointers / ordered set).
    - 15. Queries on intervals (offline sort + heap): count of intervals containing each query (two sorted arrays + bisect); sorted queries with items pushed into a heap as they become eligible; offline with union-find (process by size, paint, skip painted).
    - 16. Circular intervals: unroll the circle (double the array or take indices mod n); wrap-around interval split into two (start > end); circular time differences (sort, then close the circle with the wrap gap); cover a circle with arcs (cut at a point, then a linear cover); circular difference array.
    - 17. Interval graphs and matching: overlap number = colours = rooms (interval-graph colouring) / independent set = activity selection / stabbing = disjoint count; assign points or days to intervals (sort, heap by end); greedy match of two sorted sequences (two pointers).
    - 18. Intervals built from other data: runs from sorted values (summary ranges); occurrence spans (first and last index, then merge); smallest range covering one element from each of k lists (sort events + sliding window / heap of heads).
    - 19. Core implementation patterns: sentinel intervals and empty input; coordinate compression; difference array / prefix sum on dense coordinates; segment tree / Fenwick tree over compressed coordinates; union-find skip pointers.

## Example problems per pattern

Each entry is `LeetCode <number> <title> (<difficulty>; <lists>)`, taken from `content/dsa/problems.json` and `content/dsa/practice.json` only. Where the data holds no problem for a pattern the line says so: the pattern needs an example picked from LeetCode, checked on the site and never from memory. A problem can appear under several patterns when it teaches both. Premium problems are marked in the data (`premium`), not here.

### 1. Merge and combine

- **merge overlapping intervals (closed / half-open touching rule)**
    - LeetCode 56 Merge Intervals (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 616 Add Bold Tag in String (medium; all)
    - LeetCode 3394 Check if Grid can be Cut into Sections (medium; all)
    - LeetCode 3169 Count Days Without Meetings (medium; all)
- **insert interval (linear three-phase scan / binary search for the window)**
    - LeetCode 57 Insert Interval (medium; blind75, neetcode150, neetcode250, all)
- **remove covered intervals (sort by start, end descending)**
    - LeetCode 1288 Remove Covered Intervals (medium; all)
- **count groups of overlapping ranges (components of the overlap graph)**
    - LeetCode 2580 Count Ways to Group Overlapping Ranges (medium; practice)
- **merge k sorted interval lists (flatten and sort / heap of list heads)**
    - LeetCode 759 Employee Free Time (hard; all)

### 2. Intersection and subtraction

- **intersection of two sorted interval lists (two pointers) / of k lists (running overlap count)**
    - LeetCode 986 Interval List Intersections (medium; all)
- **common slot of a given length (two pointers over two sorted lists)**
    - LeetCode 1229 Meeting Scheduler (medium; all)
- **remove (subtract) an interval from a set / difference of two interval sets**
    - LeetCode 1272 Remove Interval (medium; all)

### 3. Selection by earliest end (non-overlapping)

- **minimum removals to leave non-overlapping intervals (sort by end / DP)**
    - LeetCode 435 Non-overlapping Intervals (medium; blind75, neetcode150, neetcode250, all)
- **maximum non-overlapping intervals (activity selection) / longest chain of pairs**
    - LeetCode 646 Maximum Length of Pair Chain (medium; all)
    - LeetCode 2472 Maximum Number of Non-overlapping Palindrome Substrings (hard; practice)

### 4. Covering points and ranges

- **minimum points that stab every interval (arrows, sort by end)**
    - LeetCode 452 Minimum Number of Arrows to Burst Balloons (medium; all)
- **at least two (k) points per interval (stabbing with multiplicity)**
    - no problem in the data: needs one from LeetCode
- **minimum intervals to cover a range (sort by start, furthest reach) / as a jump game**
    - LeetCode 1326 Minimum Number of Taps to Open to Water a Garden (hard; practice)
    - LeetCode 45 Jump Game II (medium; neetcode150, neetcode250, all)
- **is every integer of a range covered (merge / difference array)**
    - no problem in the data: needs one from LeetCode

### 5. Meeting rooms

- **can attend all meetings (sort, compare neighbours)**
    - LeetCode 252 Meeting Rooms (easy; blind75, neetcode150, neetcode250, all)
- **minimum rooms (min-heap of ends / sorted starts and ends with two pointers / events / difference array)**
    - LeetCode 253 Meeting Rooms II (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 2406 Divide Intervals Into Minimum Number of Groups (medium; all)
- **which room or chair (lowest free id, two heaps)**
    - LeetCode 2402 Meeting Rooms III (hard; neetcode250, all)
    - LeetCode 1942 The Number of the Smallest Unoccupied Chair (medium; all)
- **capacity over time (running load, car pooling)**
    - LeetCode 1094 Car Pooling (medium; neetcode250, all)

### 6. Line sweep

- **events: start +1 and end -1, with the tie order at equal times**
    - LeetCode 253 Meeting Rooms II (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 2021 Brightest Position on Street (medium; all)
    - LeetCode 1094 Car Pooling (medium; neetcode250, all)
- **maximum overlap and where it happens (busiest point, brightest position)**
    - LeetCode 2021 Brightest Position on Street (medium; all)
    - LeetCode 731 My Calendar II (medium; all)
- **sweep with an active set (heap / ordered multiset) while events stream**
    - LeetCode 218 The Skyline Problem (hard; practice)
    - LeetCode 1353 Maximum Number of Events That Can Be Attended (medium; practice)
    - LeetCode 759 Employee Free Time (hard; all)
- **sparse coordinates (sorted map of deltas / coordinate compression)**
    - LeetCode 731 My Calendar II (medium; all)

### 7. Range updates with difference arrays

- **1-D difference array (add on ranges, one prefix pass)**
    - LeetCode 2381 Shifting Letters II (medium; all)
    - LeetCode 1094 Car Pooling (medium; neetcode250, all)
- **2-D difference array (rectangle adds)**
    - no problem in the data: needs one from LeetCode
- **sliding difference (apply flips on the fly, expire them)**
    - LeetCode 995 Minimum Number of K Consecutive Bit Flips (hard; all)
- **difference array inside a binary search on the answer**
    - LeetCode 2528 Maximize the Minimum Powered City (hard; practice)
- **online range add (lazy segment tree / Fenwick tree with range add)**
    - LeetCode 731 My Calendar II (medium; all)
- **range assign or paint (union-find skip pointers / interval map)**
    - no problem in the data: needs one from LeetCode

### 8. Interval scheduling: weighted, bounded and deadline

- **weighted interval scheduling (sort by end, DP with binary search for the last compatible job)**
    - LeetCode 1235 Maximum Profit in Job Scheduling (hard; all)
- **weighted with at most k picks (dp over index and picks left)**
    - LeetCode 1751 Maximum Number of Events That Can Be Attended II (hard; practice)
- **position DP over coordinates (rides along a line)**
    - LeetCode 2008 Maximum Earnings From Taxi (medium; practice)
- **attend the most events, one per day (sort by start, min-heap of ends)**
    - LeetCode 1353 Maximum Number of Events That Can Be Attended (medium; practice)
- **deadline scheduling (sort by deadline, max-heap, evict the longest)**
    - LeetCode 630 Course Schedule III (hard; practice)
- **two non-overlapping events with the best sum (prefix max + binary search)**
    - no problem in the data: needs one from LeetCode

### 9. Calendar booking

- **no double booking (sorted starts and bisect on neighbours / ordered map / segment tree)**
    - LeetCode 729 My Calendar I (medium; all)
- **up to k overlaps allowed (two lists / map of deltas / lazy segment tree)**
    - LeetCode 731 My Calendar II (medium; all)
- **interval set with add, remove and query (merge on insert)**
    - no problem in the data: needs one from LeetCode
- **disjoint intervals from a stream (ordered map of starts / union-find on values)**
    - LeetCode 352 Data Stream as Disjoint Intervals (hard; all)
- **time-bucketed counts and log ranges (sorted timestamps + bisect)**
    - LeetCode 1348 Tweet Counts Per Frequency (medium; practice)
    - LeetCode 635 Design Log Storage System (medium; all)

### 10. Gaps and free time

- **missing ranges / complement within a range (sweep with a cursor)**
    - LeetCode 163 Missing Ranges (easy; all)
    - LeetCode 1637 Widest Vertical Area Between Two Points Containing No Points (easy; all)
- **free time in the union of busy intervals (merge, then read the gaps)**
    - LeetCode 3169 Count Days Without Meetings (medium; all)
    - LeetCode 759 Employee Free Time (hard; all)
- **employee free time (k sorted lists: flatten and sort / heap / sweep counting zero)**
    - LeetCode 759 Employee Free Time (hard; all)
- **free time after moving meetings (gap list + sliding window / best gap)**
    - LeetCode 3439 Reschedule Meetings for Maximum Free Time I (medium; practice)
    - LeetCode 3440 Reschedule Meetings for Maximum Free Time II (medium; practice)

### 11. Interval tree and stabbing queries

- **count intervals containing a point (sorted starts and ends, two binary searches)**
    - LeetCode 2251 Number of Flowers in Full Bloom (hard; all)
- **list intervals containing a point (interval tree: max end per node)**
    - no problem in the data: needs one from LeetCode
- **next interval at or after a point (sort + binary search / ordered map ceiling)**
    - LeetCode 436 Find Right Interval (medium; practice)
- **stabbing count under updates (segment tree over compressed coordinates)**
    - LeetCode 729 My Calendar I (medium; all)
    - LeetCode 731 My Calendar II (medium; all)

### 12. Skyline problem

- **skyline by sweep (max-heap with lazy deletion / ordered multiset of heights)**
    - LeetCode 218 The Skyline Problem (hard; practice)
- **skyline by divide and conquer (merge two skylines)**
    - LeetCode 218 The Skyline Problem (hard; practice)
- **range assign and max (falling squares: segment tree over compressed coordinates)**
    - no problem in the data: needs one from LeetCode

### 13. Interval DP (cross-reference to 2-D Dynamic Programming)

- **interval DP over [l, r] (split point, lengths ascending)**
    - LeetCode 312 Burst Balloons (hard; neetcode150, neetcode250, all)
    - LeetCode 1547 Minimum Cost to Cut a Stick (hard; all)
    - LeetCode 1000 Minimum Cost to Merge Stones (hard; practice)
    - LeetCode 664 Strange Printer (hard; practice)
- **game and palindrome DP over ranges (stone games, palindromic subsequence)**
    - LeetCode 486 Predict the Winner (medium; practice)
    - LeetCode 877 Stone Game (medium; neetcode250, all)
    - LeetCode 516 Longest Palindromic Subsequence (medium; all)
    - LeetCode 1563 Stone Game V (hard; practice)

### 14. Union length and area

- **union length of 1-D intervals (merge, sum the pieces)**
    - LeetCode 3169 Count Days Without Meetings (medium; all)
- **union area of rectangles (sweep + segment tree with cover counts)**
    - no problem in the data: needs one from LeetCode
- **overlap of two rectangles (clamp min / max, inclusion-exclusion)**
    - LeetCode 223 Rectangle Area (medium; practice)
- **projection to the axes (merge the x-ranges and the y-ranges of shapes)**
    - LeetCode 3394 Check if Grid can be Cut into Sections (medium; all)
- **sampling by length or area (prefix sums + binary search over disjoint ranges)**
    - LeetCode 497 Random Point in Non-overlapping Rectangles (medium; practice)
- **new area painted per day (skip pointers / ordered set)**
    - no problem in the data: needs one from LeetCode

### 15. Queries on intervals (offline sort + heap)

- **smallest interval containing each query (sort both, min-heap by size, pop the expired)**
    - LeetCode 1851 Minimum Interval to Include Each Query (hard; neetcode150, neetcode250, all)
- **count of intervals containing each query (two sorted arrays + bisect)**
    - LeetCode 2251 Number of Flowers in Full Bloom (hard; all)
- **sorted queries with items pushed into a heap as they become eligible**
    - LeetCode 2503 Maximum Number of Points From Grid Queries (hard; all)
    - LeetCode 2070 Most Beautiful Item for Each Query (medium; all)
- **offline with union-find (process by size, paint, skip painted)**
    - no problem in the data: needs one from LeetCode

### 16. Circular intervals

- **unroll the circle (double the array or take indices mod n)**
    - LeetCode 918 Maximum Sum Circular Subarray (medium; neetcode250, all)
    - LeetCode 134 Gas Station (medium; neetcode150, neetcode250, all)
- **wrap-around interval split into two (start > end)**
    - no problem in the data: needs one from LeetCode
- **circular time differences (sort, then close the circle with the wrap gap)**
    - LeetCode 539 Minimum Time Difference (medium; all)
- **cover a circle with arcs (cut at a point, then a linear cover)**
    - no problem in the data: needs one from LeetCode
- **circular difference array**
    - no problem in the data: needs one from LeetCode

### 17. Interval graphs and matching

- **overlap number = colours = rooms (interval-graph colouring) / independent set = activity selection / stabbing = disjoint count**
    - LeetCode 253 Meeting Rooms II (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 2406 Divide Intervals Into Minimum Number of Groups (medium; all)
- **assign points or days to intervals (sort, heap by end)**
    - LeetCode 1353 Maximum Number of Events That Can Be Attended (medium; practice)
- **greedy match of two sorted sequences (two pointers)**
    - LeetCode 2410 Maximum Matching of Players With Trainers (medium; practice)
    - LeetCode 2037 Minimum Number of Moves to Seat Everyone (easy; all)

### 18. Intervals built from other data

- **runs from sorted values (summary ranges)**
    - no problem in the data: needs one from LeetCode
- **occurrence spans (first and last index, then merge)**
    - LeetCode 763 Partition Labels (medium; neetcode150, neetcode250, all)
- **marked positions in a string (bold tags)**
    - LeetCode 616 Add Bold Tag in String (medium; all)
- **reach windows [i - r, i + r] (taps, lamps)**
    - LeetCode 1326 Minimum Number of Taps to Open to Water a Garden (hard; practice)
- **projections of 2-D shapes**
    - LeetCode 3394 Check if Grid can be Cut into Sections (medium; all)
- **smallest range covering one element from each of k lists (sort events + sliding window / heap of heads)**
    - LeetCode 632 Smallest Range Covering Elements from K Lists (hard; all)

### 19. Core implementation patterns

- **sort key choice (start / end / start then end descending)**: implementation note, no problem of its own (it appears in every pattern above).
- **closed versus half-open endpoints, and the touching rule**: implementation note, no problem of its own (it appears in every pattern above).
- **event encoding and tie order at equal times**: implementation note, no problem of its own (it appears in every pattern above).
- **last-kept end pointer / merged-list tail**: implementation note, no problem of its own (it appears in every pattern above).
- **bisect on sorted starts / heap of ends / ordered map**: implementation note, no problem of its own (it appears in every pattern above).
- **sentinel intervals and empty input**: implementation note, no problem of its own (it appears in every pattern above).
- **coordinate compression**: implementation note, no problem of its own (it appears in every pattern above).
- **difference array / prefix sum on dense coordinates**: implementation note, no problem of its own (it appears in every pattern above).
- **segment tree / Fenwick tree over compressed coordinates**: implementation note, no problem of its own (it appears in every pattern above).
- **union-find skip pointers**: implementation note, no problem of its own (it appears in every pattern above).

## Gaps

**Patterns with no problem in the data.** 15 of the 76 problem patterns have none (the 10 implementation notes in group 19 are not problems). Each needs one example picked from LeetCode and checked on the site:

- 4. at least two (k) points per interval (stabbing with multiplicity)
- 4. is every integer of a range covered (merge / difference array)
- 7. 2-D difference array (rectangle adds)
- 7. range assign or paint (union-find skip pointers / interval map)
- 8. two non-overlapping events with the best sum (prefix max + binary search)
- 9. interval set with add, remove and query (merge on insert)
- 11. list intervals containing a point (interval tree: max end per node)
- 12. range assign and max (falling squares: segment tree over compressed coordinates)
- 14. union area of rectangles (sweep + segment tree with cover counts)
- 14. new area painted per day (skip pointers / ordered set)
- 15. offline with union-find (process by size, paint, skip painted)
- 16. wrap-around interval split into two (start > end)
- 16. cover a circle with arcs (cut at a point, then a linear cover)
- 16. circular difference array
- 18. runs from sorted values (summary ranges)

**Patterns whose only data is a loose fit.** These have a problem, but it teaches the idea only partly, so a closer example is still worth picking from LeetCode:

- Range updates, online range add: LeetCode 731 My Calendar II is listed because one approach uses a lazy segment tree; the pattern is a general range-add and range-max tree, which the data does not hold.
- 1-D difference arrays: LeetCode 2381 and 1094 are the only direct ones; the 2-D, paint and sliding forms are missing or sit in other topics (995 is filed under Greedy, 2528 under Sliding Window).
- Interval tree (list the containing intervals): only counting queries exist in the data (2251, 1851).
- Skyline: a single problem (218), filed under Heap / Priority Queue, practice only; the divide and conquer tab and the segment tree tab share it.
- Union area of rectangles: only the two-rectangle case (223, Math & Geometry, practice only).
- Circular intervals: 539, 918 and 134 are circular but not interval problems in the strict sense; the true wrap-around interval and circular cover have no example.
- Interval DP: the Intervals lessons would only cross-reference the 2-D DP track, so no new problems are needed there.

**Data filed under the Intervals pattern that is not an interval problem.** Of the 37 problems with `pattern = "Intervals"` (4 must-learn, 33 practice), these 10 are mapped to an Intervals technique but the idea is not an interval one. The owner decides whether to re-file them; nothing is changed here:

- LeetCode 334 Increasing Triplet Subsequence (medium; practice), technique `Intervals:by-end`
- LeetCode 1169 Invalid Transactions (medium; practice), technique `Intervals:sweep`
- LeetCode 1200 Minimum Absolute Difference (easy; practice), technique `Intervals:sweep`
- LeetCode 1262 Greatest Sum Divisible by Three (medium; practice), technique `Intervals:by-end`
- LeetCode 1665 Minimum Initial Energy to Finish Tasks (hard; practice), technique `Intervals:sweep`
- LeetCode 1824 Minimum Sideway Jumps (medium; practice), technique `Intervals:by-end`
- LeetCode 1889 Minimum Space Wasted From Packaging (hard; practice), technique `Intervals:calendar`
- LeetCode 2086 Minimum Number of Food Buckets to Feed the Hamsters (medium; practice), technique `Intervals:sweep`
- LeetCode 2410 Maximum Matching of Players With Trainers (medium; practice), technique `Intervals:merge`
- LeetCode 3613 Minimize Maximum Component Cost (medium; practice), technique `Intervals:calendar`

**Technique mapping is coarse.** 17 of the 37 Intervals problems sit under `Intervals:merge`, including DP (1751), heaps with room assignment (2402) and the greedy matching 2410; the lessons would split them across the new groups. Two problems filed under other patterns already point at an Intervals technique: LeetCode 646 Maximum Length of Pair Chain (Greedy, `Intervals:by-end`) and LeetCode 2021 Brightest Position on Street (Arrays & Hashing, `Intervals:sweep`).

**Free access.** Six of the 37 Intervals problems are premium (163, 252, 253, 616, 759, 1272), so a free alternative is wanted for the lessons that lean on them: meeting rooms (252, 253), missing ranges and employee free time (163, 759), remove interval (1272) and bold tags (616).

**Proposal (the owner decides, nothing is built).** Keep the four techniques as the spine and add technique lessons with tabs for the variants: intersection and subtraction; covering and stabbing; interval scheduling (weighted, bounded, deadline); range updates with difference arrays; gaps and free time; interval tree and stabbing queries; skyline; union length and area; offline queries; and circular intervals. Interval DP stays in the 2-D DP track with a link. Per rule 13 in DSA.md the new screens (tabs inside a technique) need an HTML mockup approved first.
