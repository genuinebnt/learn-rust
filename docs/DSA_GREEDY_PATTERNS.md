# Greedy patterns: the exhaustive target list

The target list (2026-10-10) of every greedy pattern that can come up on LeetCode, for the Greedy pattern lessons. It follows the rule in [DSA.md](DSA.md), decision 32, the same way [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md) does for graphs: a topic's patterns section is **exhaustive**, patterns without a NeetCode problem get **example problems** from LeetCode, and variants of one pattern (for example "interval cover: sort by start / as a jump game") are **tabs** of one lesson.

Status: documented only. Today `content/dsa/lessons/greedy.toml` has 13 techniques (scan-balance, sort-pick, swap-greedy, count-greedy, flip-window, kadane, reach, surplus, group-smallest, simulate-greedy, filter, last-seen, paren-range). The list below has 22 groups and 151 patterns. Building the rest needs a mockup of the tabs first, then lessons and picked example problems. Nothing here is built.

Items written *a / b* in a group are variants for tabs where one lesson covers both. Text in parentheses names the key idea or the alternative implementations. Groups 1 to 18 are the owner's list; groups 19 to 22 are my addition so that every technique the lessons teach today has a home (running-state scans, window flips and grouping, greedy simulation, core implementation patterns). The owner decides whether to keep them.

1. **Sorting-based greedy.** sort ascending and take while the budget lasts; sort and take the k best (largest / smallest); sort by one key, then sweep; sort both sides and match rank to rank; sort and pair smallest with largest; custom comparator order (concatenation order); fractional knapsack by value ratio; sort the gains and take the k largest differences; counting sort when the values are small.
2. **Interval scheduling and covering.** merge overlapping intervals; insert into a sorted interval list; intersect two interval lists / find free time; remove covered intervals (start ascending, end descending); fewest removals so the rest do not overlap (earliest end first); fewest points that stab every interval; fewest intervals or taps to cover a range; minimum rooms or groups (sweep / min-heap of ends); attend the most events (earliest deadline first).
3. **Jump game family.** furthest reachable position; minimum jumps by BFS layers (current end / next end); jump with a window of allowed distances (prefix counts / deque); jump as graph search (BFS on indices); cover a range with the fewest segments (jump game in disguise); jump with costs (DP, greedy fails); reach a target by exact steps (math on the sum).
4. **Gas station.** circular route with a total and a running surplus (reset the start); split point where the prefix sum equals a target part; refuel from a heap of passed stations; spend the scarcest resource only when stuck (bricks and ladders); smallest starting energy so the running total never drops below zero.
5. **Two-pointer greedy.** pair the lightest with the heaviest; match each item with the smallest sufficient partner; spend low, gain high (two ends of a sorted list); move the shorter side inward; one skip allowed, then check the rest; greedy subsequence matching (advance only on a match); pairs summing to a target, taken from both ends.
6. **Heap-assisted greedy.** take the best available, which unlocks more (project selection); heap of the k best by a sorted key (ratio / efficiency); regret: undo the worst earlier choice; most frequent first with a cooldown or spacing; largest marginal gain each step; merge the two smallest; earliest deadline first; largest letter first with a repeat limit.
7. **Exchange arguments.** adjacent-swap ordering with a comparator; deadline ordering, replacing the largest taken job; order by cost difference; stay-ahead proof (the greedy is never behind an optimal solution); exchange on an assignment or matching; minimise maximum lateness / weighted completion time (sort by ratio).
8. **Stack-based greedy.** monotone stack for the smallest number after k removals; smallest subsequence with every distinct letter once; lexicographically smallest output from a stack and counts; bracket repair by counting opens (stack / counter); remove pairs in order of highest score; chunks through a monotone stack of maxima; visible elements (ocean view); rebuild a sequence from a pattern with a stack.
9. **Number construction.** swap once for the largest value; next permutation / next greater number with the same digits; largest odd or best-looking result from the same digits; smallest or largest number from an I / D pattern; merge two digit lists into the largest number; change one character to break a palindrome; fewest additions to reach a digit-sum target; smallest number from a product (divide by 9 down to 2); sort digits by parity and place them back; smallest array or string with swaps inside components.
10. **Partition labels.** partition by last occurrence; chunks where the prefix maximum equals the index; start a new group when a seen set resets; partition into equal-sum parts; partition by a digit requirement (deci-binary: the largest digit); fewest groups under a size or count constraint.
11. **Candy two-pass.** left pass, then right pass on ratings; prefix maximum and suffix maximum (two passes); lengths of increasing and decreasing runs; remove the shortest middle so prefix and suffix are sorted.
12. **Stock problems.** one transaction: running minimum; unlimited transactions: sum of the rises; unlimited transactions with a fee (cash / hold); with a cooldown (state machine; greedy fails); at most two or k transactions (prefix / suffix split or DP); stock with one change of strategy; best pair with a distance penalty (running best of a[i] + i).
13. **Activity selection.** most non-overlapping activities by earliest finish; most events attended on distinct days; fewest resources for all activities; weighted activity selection (DP, not greedy); two activities, earliest combined finish; choose k non-overlapping jobs for the largest total.
14. **Huffman.** merge the two smallest repeatedly (connect sticks / optimal merge); Huffman coding tree and expected code length; merge many sorted files at least total cost.
15. **Greedy on graphs.** Kruskal: sort edges, union-find; Prim: grow one tree with a min-heap; Dijkstra's settled-node argument; greedy on node degrees and weights; leaf-first removal in trees; greedy graph colouring by degree order; topological order with a priority queue (smallest label first).
16. **Counting greedy.** palindromes from letter counts; make frequencies distinct or equal; split a count into groups of 2 and 3; redistribute characters among strings; count the mismatches, then pair them up; bucket by frequency instead of sorting; count across lines (laser beams); smallest missing value from residue counts.
17. **Bit greedy.** build the answer from the highest bit down; maximum XOR by prefix / trie greedy; fewest operations to reduce a number to zero (look at the low bits); flip rows, then columns, by bit weight; per-bit decision (flips to make a OR b equal c); place the bits for the largest odd binary number.
18. **When greedy fails.** coin change with arbitrary denominations; 0/1 knapsack and subset sum; weighted interval scheduling; stocks with a cooldown; longest increasing subsequence (patience tails vs DP); wildcard matching; palindrome partitioning; minimum cost to cut a stick (interval DP).
19. **Running-state scans.** Kadane: best contiguous sum; Kadane variants (circular, turbulent); running bracket balance; range of possible open counts (wildcard brackets); running cash balance with deposits and withdrawals; running best partner (best sightseeing pair); increments as the sum of positive differences; filter the candidates by constraints, then combine.
20. **Window flips and grouping.** flip a window of k, left to right (queue / difference array); group the sorted values into runs of k; pair each value with its double; buy in threes with the cheapest free; assign the largest tasks to the earliest-free processors; zero out an array with window subtractions.
21. **Greedy simulation.** simulate a game with the best local move; make two sums equal by replacing wildcards; lexicographically best array from counts and a queue; remove pieces under a neighbour rule; order the events by arrival time.
22. **Core implementation patterns.** sort by a key tuple; heap with a (priority, payload) entry; running counters and sentinels; prefix and suffix arrays; difference array for range updates; two-pass scan (left to right, then back); brute-force checker to test a greedy on small inputs; proof sketch: exchange / stay-ahead / invariant.

## Coverage today

The data (`content/dsa/problems.json` plus `content/dsa/practice.json`, 1550 problems) has **119** problems with `pattern = "Greedy"` (12 must-learn, 107 practice; 18 easy, 88 medium, 13 hard) and **103** more tagged `Greedy` that live in other patterns (Heap / Priority Queue 22, Arrays & Hashing 20, Two Pointers 14, Intervals 12, Stack 9, Math & Geometry 7, Binary Search 5, Sliding Window 5, 1-D Dynamic Programming 3, 2-D Dynamic Programming 2, Backtracking 1, Bit Manipulation 1, Trees 1, Advanced Graphs 1). Lists of the Greedy pattern: all 67, practice 52, neetcode250 14, neetcode150 8, blind75 2.

The 13 techniques in `content/dsa/lessons/greedy.toml`, with the problems filed under each (by the `technique` field of the data):

- **Greedy:scan-balance** (One pass with a running balance; must-learn `lc-best-time-to-buy-and-sell-stock-ii`): 15 problems filed.
- **Greedy:sort-pick** (Sort, then take greedily; must-learn `lc-buy-two-chocolates`): 15 problems filed.
- **Greedy:swap-greedy** (Greedy swaps and digit rearrangement; must-learn `lc-maximum-odd-binary-number`): 8 problems filed.
- **Greedy:count-greedy** (Greedy from counts; must-learn `lc-check-if-one-string-swap-can-make-strings-equal`): 14 problems filed.
- **Greedy:flip-window** (Greedy flips with a difference array; must-learn `lc-minimum-operations-to-make-binary-array-elements-equal-to-one-i`): 6 problems filed.
- **Greedy:kadane** (Kadane's algorithm; must-learn `lc-maximum-subarray`): 9 problems filed.
- **Greedy:reach** (Furthest reachable; must-learn `lc-jump-game`): 7 problems filed.
- **Greedy:surplus** (Running surplus and reset; must-learn `lc-gas-station`): 5 problems filed.
- **Greedy:group-smallest** (Group the smallest first; must-learn `lc-hand-of-straights`): 5 problems filed.
- **Greedy:simulate-greedy** (Greedy simulation of a game; must-learn `lc-dota2-senate`): 6 problems filed.
- **Greedy:filter** (Filter by constraints; must-learn `lc-merge-triplets-to-form-target-triplet`): 5 problems filed.
- **Greedy:last-seen** (Greedy with last occurrence; must-learn `lc-partition-labels`): 5 problems filed.
- **Greedy:paren-range** (Range of open counts; must-learn `lc-valid-parenthesis-string`): 6 problems filed.

13 more Greedy-pattern problems are filed under techniques of other patterns: `Binary Search:on-answer` 1, `Graphs:dsu` 1, `Heap / Priority Queue:greedy-heap` 2, `Heap / Priority Queue:pool` 1, `Intervals:by-end` 1, `Sliding Window:fixed-sum` 2, `Stack:mono-contrib` 1, `Stack:mono-stack` 2, `Stack:simulate-stack` 1, `Two Pointers:opposite` 1.

What the lessons teach directly: the running balance (stock II, brackets), sort-then-take, greedy swaps and digit rearrangement, counting, window flips with a difference array, Kadane, furthest reach, the gas-station surplus, grouping the smallest first, game simulation, filtering by constraints, last occurrence (partition labels) and the parenthesis range. Not taught by any Greedy lesson yet: the comparator sort and fractional knapsack, interval scheduling and covering (the lessons live under Intervals), minimum jumps and the jump-game variants, stack-based lexicographic construction (Stack), heap-assisted greedy (Heap / Priority Queue), exchange arguments as a method, the candy two-pass, stock variants beyond II, Huffman, greedy on graphs (Advanced Graphs), bit greedy, and the page on when greedy fails (coin change, weighted scheduling, 0/1 knapsack).

## Example problems per pattern

Each entry is `LeetCode <number> <title> (<difficulty>; <lists>)`, taken from `content/dsa/problems.json` and `content/dsa/practice.json` only, up to 4 per pattern. Where the data holds no problem for a pattern the line says so: the pattern needs an example picked from LeetCode, checked on the site and never from memory. A problem can appear under several patterns when it teaches both. Premium problems are marked in the data (`premium`), not here.

### 1. Sorting-based greedy

- **sort ascending and take while the budget lasts**
    - LeetCode 1196 How Many Apples Can You Put into the Basket (easy; all)
    - LeetCode 2706 Buy Two Chocolates (easy; all)
    - LeetCode 2554 Maximum Number of Integers to Choose From a Range I (medium; practice)
- **sort and take the k best (largest / smallest)**
    - LeetCode 2600 K Items With the Maximum Sum (easy; practice)
    - LeetCode 2587 Rearrange Array to Maximize Prefix Score (medium; practice)
    - LeetCode 1509 Minimum Difference Between Largest and Smallest Value in Three Moves (medium; all)
- **sort by one key, then sweep**
    - LeetCode 1710 Maximum Units on a Truck (easy; practice)
    - LeetCode 1846 Maximum Element After Decreasing and Rearranging (medium; all)
    - LeetCode 945 Minimum Increment to Make Array Unique (medium; all)
- **sort both sides and match rank to rank**
    - LeetCode 2037 Minimum Number of Moves to Seat Everyone (easy; all)
    - LeetCode 2592 Maximize Greatness of an Array (medium; practice)
    - LeetCode 2410 Maximum Matching of Players With Trainers (medium; practice)
    - LeetCode 826 Most Profit Assigning Work (medium; practice)
- **sort and pair smallest with largest**
    - LeetCode 1877 Minimize Maximum Pair Sum in Array (medium; practice)
    - LeetCode 881 Boats to Save People (medium; neetcode250, all)
    - LeetCode 2491 Divide Players Into Teams of Equal Skill (medium; all)
- **custom comparator order (concatenation order)**
    - LeetCode 179 Largest Number (medium; all)
- **fractional knapsack by value ratio**
    - LeetCode 857 Minimum Cost to Hire K Workers (hard; all)
    - LeetCode 1710 Maximum Units on a Truck (easy; practice)
- **sort the gains and take the k largest differences**
    - LeetCode 1029 Two City Scheduling (medium; all)
    - LeetCode 2611 Mice and Cheese (medium; practice)
    - LeetCode 2551 Put Marbles in Bags (hard; all)
- **counting sort when the values are small**
    - LeetCode 2037 Minimum Number of Moves to Seat Everyone (easy; all)
    - LeetCode 945 Minimum Increment to Make Array Unique (medium; all)

### 2. Interval scheduling and covering

- **merge overlapping intervals**
    - LeetCode 56 Merge Intervals (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 57 Insert Interval (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 252 Meeting Rooms (easy; blind75, neetcode150, neetcode250, all)
- **insert into a sorted interval list**
    - LeetCode 57 Insert Interval (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 986 Interval List Intersections (medium; all)
- **intersect two interval lists / find free time**
    - LeetCode 986 Interval List Intersections (medium; all)
    - LeetCode 759 Employee Free Time (hard; all)
- **remove covered intervals (start ascending, end descending)**
    - LeetCode 1288 Remove Covered Intervals (medium; all)
- **fewest removals so the rest do not overlap (earliest end first)**
    - LeetCode 435 Non-overlapping Intervals (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 646 Maximum Length of Pair Chain (medium; all)
- **fewest points that stab every interval**
    - LeetCode 452 Minimum Number of Arrows to Burst Balloons (medium; all)
- **fewest intervals or taps to cover a range**
    - LeetCode 1326 Minimum Number of Taps to Open to Water a Garden (hard; practice)
- **minimum rooms or groups (sweep / min-heap of ends)**
    - LeetCode 253 Meeting Rooms II (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 2406 Divide Intervals Into Minimum Number of Groups (medium; all)
    - LeetCode 2402 Meeting Rooms III (hard; neetcode250, all)
- **attend the most events (earliest deadline first)**
    - LeetCode 1353 Maximum Number of Events That Can Be Attended (medium; practice)

### 3. Jump game family

- **furthest reachable position**
    - LeetCode 55 Jump Game (medium; blind75, neetcode150, neetcode250, all)
- **minimum jumps by BFS layers (current end / next end)**
    - LeetCode 45 Jump Game II (medium; neetcode150, neetcode250, all)
- **jump with a window of allowed distances (prefix counts / deque)**
    - LeetCode 1871 Jump Game VII (medium; neetcode250, all)
    - LeetCode 1696 Jump Game VI (medium; practice)
- **jump as graph search (BFS on indices)**
    - LeetCode 1306 Jump Game III (medium; practice)
    - LeetCode 1345 Jump Game IV (hard; practice)
- **cover a range with the fewest segments (jump game in disguise)**
    - LeetCode 1326 Minimum Number of Taps to Open to Water a Garden (hard; practice)
- **jump with costs (DP, greedy fails)**
    - LeetCode 2770 Maximum Number of Jumps to Reach the Last Index (medium; practice)
- **reach a target by exact steps (math on the sum)**
    - LeetCode 754 Reach a Number (medium; practice)

### 4. Gas station

- **circular route with a total and a running surplus (reset the start)**
    - LeetCode 134 Gas Station (medium; neetcode150, neetcode250, all)
- **split point where the prefix sum equals a target part**
    - LeetCode 1013 Partition Array Into Three Parts With Equal Sum (easy; practice)
- **refuel from a heap of passed stations**
    - LeetCode 871 Minimum Number of Refueling Stops (hard; practice)
- **spend the scarcest resource only when stuck (bricks and ladders)**
    - LeetCode 1642 Furthest Building You Can Reach (medium; all)
- **smallest starting energy so the running total never drops below zero**
    - LeetCode 1665 Minimum Initial Energy to Finish Tasks (hard; practice)

### 5. Two-pointer greedy

- **pair the lightest with the heaviest**
    - LeetCode 881 Boats to Save People (medium; neetcode250, all)
    - LeetCode 2491 Divide Players Into Teams of Equal Skill (medium; all)
    - LeetCode 1877 Minimize Maximum Pair Sum in Array (medium; practice)
- **match each item with the smallest sufficient partner**
    - LeetCode 455 Assign Cookies (easy; all)
    - LeetCode 2410 Maximum Matching of Players With Trainers (medium; practice)
    - LeetCode 2592 Maximize Greatness of an Array (medium; practice)
- **spend low, gain high (two ends of a sorted list)**
    - LeetCode 948 Bag of Tokens (medium; all)
- **move the shorter side inward**
    - LeetCode 11 Container With Most Water (medium; blind75, neetcode150, neetcode250, all)
- **one skip allowed, then check the rest**
    - LeetCode 680 Valid Palindrome II (easy; neetcode250, all)
- **greedy subsequence matching (advance only on a match)**
    - LeetCode 2486 Append Characters to String to Make Subsequence (medium; all)
    - LeetCode 1055 Shortest Way to Form String (medium; all)
    - LeetCode 3302 Find the Lexicographically Smallest Valid Sequence (medium; practice)
- **pairs summing to a target, taken from both ends**
    - LeetCode 1679 Max Number of K-Sum Pairs (medium; practice)

### 6. Heap-assisted greedy

- **take the best available, which unlocks more (project selection)**
    - LeetCode 502 IPO (hard; neetcode250, all)
    - LeetCode 2530 Maximal Score After Applying K Operations (medium; all)
- **heap of the k best by a sorted key (ratio / efficiency)**
    - LeetCode 857 Minimum Cost to Hire K Workers (hard; all)
    - LeetCode 1383 Maximum Performance of a Team (hard; all)
    - LeetCode 2542 Maximum Subsequence Score (medium; all)
- **regret: undo the worst earlier choice**
    - LeetCode 630 Course Schedule III (hard; practice)
    - LeetCode 871 Minimum Number of Refueling Stops (hard; practice)
    - LeetCode 1642 Furthest Building You Can Reach (medium; all)
- **most frequent first with a cooldown or spacing**
    - LeetCode 621 Task Scheduler (medium; neetcode150, neetcode250, all)
    - LeetCode 767 Reorganize String (medium; neetcode250, all)
    - LeetCode 1054 Distant Barcodes (medium; practice)
    - LeetCode 358 Rearrange String k Distance Apart (hard; all)
- **largest marginal gain each step**
    - LeetCode 1792 Maximum Average Pass Ratio (medium; practice)
    - LeetCode 1962 Remove Stones to Minimize the Total (medium; practice)
    - LeetCode 2208 Minimum Operations to Halve Array Sum (medium; practice)
- **merge the two smallest**
    - LeetCode 1167 Minimum Cost to Connect Sticks (medium; all)
- **earliest deadline first**
    - LeetCode 1353 Maximum Number of Events That Can Be Attended (medium; practice)
- **largest letter first with a repeat limit**
    - LeetCode 2182 Construct String With Repeat Limit (medium; all)
    - LeetCode 1405 Longest Happy String (medium; neetcode250, all)

### 7. Exchange arguments

- **adjacent-swap ordering with a comparator**
    - LeetCode 179 Largest Number (medium; all)
    - LeetCode 1665 Minimum Initial Energy to Finish Tasks (hard; practice)
- **deadline ordering, replacing the largest taken job**
    - LeetCode 630 Course Schedule III (hard; practice)
- **order by cost difference**
    - LeetCode 1029 Two City Scheduling (medium; all)
    - LeetCode 2611 Mice and Cheese (medium; practice)
- **stay-ahead proof (the greedy is never behind an optimal solution)**
    - LeetCode 435 Non-overlapping Intervals (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 55 Jump Game (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 452 Minimum Number of Arrows to Burst Balloons (medium; all)
- **exchange on an assignment or matching**
    - LeetCode 2037 Minimum Number of Moves to Seat Everyone (easy; all)
    - LeetCode 455 Assign Cookies (easy; all)
- **minimise maximum lateness / weighted completion time (sort by ratio)**: no problem in the data: needs one from LeetCode

### 8. Stack-based greedy

- **monotone stack for the smallest number after k removals**
    - LeetCode 402 Remove K Digits (medium; all)
- **smallest subsequence with every distinct letter once**
    - LeetCode 316 Remove Duplicate Letters (medium; practice)
    - LeetCode 1081 Smallest Subsequence of Distinct Characters (medium; practice)
- **lexicographically smallest output from a stack and counts**
    - LeetCode 2434 Using a Robot to Print the Lexicographically Smallest String (medium; practice)
    - LeetCode 3170 Lexicographically Minimum String After Removing Stars (medium; practice)
- **bracket repair by counting opens (stack / counter)**
    - LeetCode 921 Minimum Add to Make Parentheses Valid (medium; all)
    - LeetCode 1963 Minimum Number of Swaps to Make the String Balanced (medium; all)
    - LeetCode 1541 Minimum Insertions to Balance a Parentheses String (medium; practice)
- **remove pairs in order of highest score**
    - LeetCode 1717 Maximum Score From Removing Substrings (medium; all)
- **chunks through a monotone stack of maxima**
    - LeetCode 768 Max Chunks To Make Sorted II (hard; practice)
    - LeetCode 769 Max Chunks To Make Sorted (medium; all)
- **visible elements (ocean view)**
    - LeetCode 1762 Buildings With an Ocean View (medium; all)
- **rebuild a sequence from a pattern with a stack**
    - LeetCode 484 Find Permutation (medium; all)
    - LeetCode 2375 Construct Smallest Number From DI String (medium; all)

### 9. Number construction

- **swap once for the largest value**
    - LeetCode 670 Maximum Swap (medium; all)
- **next permutation / next greater number with the same digits**
    - LeetCode 31 Next Permutation (medium; all)
    - LeetCode 556 Next Greater Element III (medium; practice)
- **largest odd or best-looking result from the same digits**
    - LeetCode 2864 Maximum Odd Binary Number (easy; all)
    - LeetCode 1903 Largest Odd Number in String (easy; all)
    - LeetCode 2259 Remove Digit From Number to Maximize Result (easy; practice)
- **smallest or largest number from an I / D pattern**
    - LeetCode 942 DI String Match (easy; practice)
    - LeetCode 484 Find Permutation (medium; all)
    - LeetCode 2375 Construct Smallest Number From DI String (medium; all)
- **merge two digit lists into the largest number**
    - LeetCode 321 Create Maximum Number (hard; practice)
- **change one character to break a palindrome**
    - LeetCode 1328 Break a Palindrome (medium; practice)
- **fewest additions to reach a digit-sum target**
    - LeetCode 2457 Minimum Addition to Make Integer Beautiful (medium; practice)
- **smallest number from a product (divide by 9 down to 2)**
    - LeetCode 625 Minimum Factorization (medium; all)
- **sort digits by parity and place them back**
    - LeetCode 2231 Largest Number After Digit Swaps by Parity (easy; practice)
- **smallest array or string with swaps inside components**
    - LeetCode 2948 Make Lexicographically Smallest Array by Swapping Elements (medium; all)
    - LeetCode 1202 Smallest String With Swaps (medium; practice)

### 10. Partition labels

- **partition by last occurrence**
    - LeetCode 763 Partition Labels (medium; neetcode150, neetcode250, all)
- **chunks where the prefix maximum equals the index**
    - LeetCode 769 Max Chunks To Make Sorted (medium; all)
    - LeetCode 768 Max Chunks To Make Sorted II (hard; practice)
- **start a new group when a seen set resets**
    - LeetCode 2405 Optimal Partition of String (medium; all)
- **partition into equal-sum parts**
    - LeetCode 1013 Partition Array Into Three Parts With Equal Sum (easy; practice)
- **partition by a digit requirement (deci-binary: the largest digit)**
    - LeetCode 1689 Partitioning Into Minimum Number Of Deci-Binary Numbers (medium; practice)
- **fewest groups under a size or count constraint**
    - LeetCode 2910 Minimum Number of Groups to Create a Valid Assignment (medium; practice)
    - LeetCode 1282 Group the People Given the Group Size They Belong To (medium; practice)

### 11. Candy two-pass

- **left pass, then right pass on ratings**
    - LeetCode 135 Candy (hard; neetcode250, all)
- **prefix maximum and suffix maximum (two passes)**
    - LeetCode 42 Trapping Rain Water (hard; neetcode150, neetcode250, all)
    - LeetCode 581 Shortest Unsorted Continuous Subarray (medium; practice)
- **lengths of increasing and decreasing runs**
    - LeetCode 845 Longest Mountain in Array (medium; practice)
    - LeetCode 978 Longest Turbulent Subarray (medium; neetcode250, all)
- **remove the shortest middle so prefix and suffix are sorted**
    - LeetCode 1574 Shortest Subarray to be Removed to Make Array Sorted (medium; all)

### 12. Stock problems

- **one transaction: running minimum**
    - LeetCode 121 Best Time to Buy and Sell Stock (easy; blind75, neetcode150, neetcode250, all)
- **unlimited transactions: sum of the rises**
    - LeetCode 122 Best Time to Buy and Sell Stock II (medium; neetcode250, all)
- **unlimited transactions with a fee (cash / hold)**
    - LeetCode 714 Best Time to Buy and Sell Stock with Transaction Fee (medium; practice)
- **with a cooldown (state machine; greedy fails)**
    - LeetCode 309 Best Time to Buy and Sell Stock with Cooldown (medium; neetcode150, neetcode250, all)
- **at most two or k transactions (prefix / suffix split or DP)**
    - LeetCode 123 Best Time to Buy and Sell Stock III (hard; practice)
    - LeetCode 3573 Best Time to Buy and Sell Stock V (medium; practice)
- **stock with one change of strategy**
    - LeetCode 3652 Best Time to Buy and Sell Stock using Strategy (medium; practice)
- **best pair with a distance penalty (running best of a[i] + i)**
    - LeetCode 1014 Best Sightseeing Pair (medium; all)

### 13. Activity selection

- **most non-overlapping activities by earliest finish**
    - LeetCode 646 Maximum Length of Pair Chain (medium; all)
    - LeetCode 435 Non-overlapping Intervals (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 452 Minimum Number of Arrows to Burst Balloons (medium; all)
- **most events attended on distinct days**
    - LeetCode 1353 Maximum Number of Events That Can Be Attended (medium; practice)
- **fewest resources for all activities**
    - LeetCode 253 Meeting Rooms II (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 2406 Divide Intervals Into Minimum Number of Groups (medium; all)
- **weighted activity selection (DP, not greedy)**
    - LeetCode 1235 Maximum Profit in Job Scheduling (hard; all)
    - LeetCode 1751 Maximum Number of Events That Can Be Attended II (hard; practice)
- **two activities, earliest combined finish**
    - LeetCode 3633 Earliest Finish Time for Land and Water Rides I (easy; practice)
- **choose k non-overlapping jobs for the largest total**: no problem in the data: needs one from LeetCode

### 14. Huffman

- **merge the two smallest repeatedly (connect sticks / optimal merge)**
    - LeetCode 1167 Minimum Cost to Connect Sticks (medium; all)
- **Huffman coding tree and expected code length**: no problem in the data: needs one from LeetCode
- **merge many sorted files at least total cost**: no problem in the data: needs one from LeetCode

### 15. Greedy on graphs

- **Kruskal: sort edges, union-find**
    - LeetCode 1584 Min Cost to Connect All Points (medium; neetcode150, neetcode250, all)
    - LeetCode 3600 Maximize Spanning Tree Stability with Upgrades (hard; practice)
- **Prim: grow one tree with a min-heap**
    - LeetCode 1584 Min Cost to Connect All Points (medium; neetcode150, neetcode250, all)
- **Dijkstra's settled-node argument**
    - LeetCode 743 Network Delay Time (medium; neetcode150, neetcode250, all)
    - LeetCode 778 Swim in Rising Water (hard; neetcode150, neetcode250, all)
    - LeetCode 1631 Path With Minimum Effort (medium; neetcode250, all)
- **greedy on node degrees and weights**
    - LeetCode 2285 Maximum Total Importance of Roads (medium; all)
    - LeetCode 1557 Minimum Number of Vertices to Reach All Nodes (medium; all)
    - LeetCode 277 Find the Celebrity (medium; all)
- **leaf-first removal in trees**
    - LeetCode 2603 Collect Coins in a Tree (hard; practice)
    - LeetCode 1443 Minimum Time to Collect All Apples in a Tree (medium; all)
- **greedy graph colouring by degree order**: no problem in the data: needs one from LeetCode
- **topological order with a priority queue (smallest label first)**: no problem in the data: needs one from LeetCode

### 16. Counting greedy

- **palindromes from letter counts**
    - LeetCode 409 Longest Palindrome (easy; all)
    - LeetCode 2131 Longest Palindrome by Concatenating Two Letter Words (medium; practice)
    - LeetCode 2384 Largest Palindromic Number (medium; practice)
    - LeetCode 1400 Construct K Palindrome Strings (medium; all)
- **make frequencies distinct or equal**
    - LeetCode 1647 Minimum Deletions to Make Character Frequencies Unique (medium; all)
    - LeetCode 3085 Minimum Deletions to Make String K-Special (medium; practice)
- **split a count into groups of 2 and 3**
    - LeetCode 2870 Minimum Number of Operations to Make Array Empty (medium; all)
- **redistribute characters among strings**
    - LeetCode 1897 Redistribute Characters to Make All Strings Equal (easy; all)
    - LeetCode 3035 Maximum Palindromes After Operations (medium; practice)
- **count the mismatches, then pair them up**
    - LeetCode 1790 Check if One String Swap Can Make Strings Equal (easy; all)
    - LeetCode 1460 Make Two Arrays Equal by Reversing Subarrays (easy; all)
- **bucket by frequency instead of sorting**
    - LeetCode 3016 Minimum Number of Pushes to Type Word II (medium; all)
    - LeetCode 1481 Least Number of Unique Integers after K Removals (medium; all)
- **count across lines (laser beams)**
    - LeetCode 2125 Number of Laser Beams in a Bank (medium; all)
- **smallest missing value from residue counts**
    - LeetCode 2598 Smallest Missing Non-negative Integer After Operations (medium; practice)

### 17. Bit greedy

- **build the answer from the highest bit down**
    - LeetCode 2429 Minimize XOR (medium; all)
    - LeetCode 2939 Maximum Xor Product (medium; practice)
    - LeetCode 2680 Maximum OR (medium; practice)
- **maximum XOR by prefix / trie greedy**
    - LeetCode 421 Maximum XOR of Two Numbers in an Array (medium; practice)
- **fewest operations to reduce a number to zero (look at the low bits)**
    - LeetCode 2571 Minimum Operations to Reduce an Integer to 0 (medium; practice)
    - LeetCode 397 Integer Replacement (medium; practice)
    - LeetCode 1404 Number of Steps to Reduce a Number in Binary Representation to One (medium; practice)
- **flip rows, then columns, by bit weight**
    - LeetCode 861 Score After Flipping Matrix (medium; all)
- **per-bit decision (flips to make a OR b equal c)**
    - LeetCode 1318 Minimum Flips to Make a OR b Equal to c (medium; practice)
    - LeetCode 2220 Minimum Bit Flips to Convert Number (easy; all)
- **place the bits for the largest odd binary number**
    - LeetCode 2864 Maximum Odd Binary Number (easy; all)

### 18. When greedy fails

- **coin change with arbitrary denominations**
    - LeetCode 322 Coin Change (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 518 Coin Change II (medium; neetcode150, neetcode250, all)
    - LeetCode 3592 Inverse Coin Change (medium; practice)
- **0/1 knapsack and subset sum**
    - LeetCode 416 Partition Equal Subset Sum (medium; neetcode150, neetcode250, all)
    - LeetCode 879 Profitable Schemes (hard; all)
- **weighted interval scheduling**
    - LeetCode 1235 Maximum Profit in Job Scheduling (hard; all)
    - LeetCode 1751 Maximum Number of Events That Can Be Attended II (hard; practice)
- **stocks with a cooldown**
    - LeetCode 309 Best Time to Buy and Sell Stock with Cooldown (medium; neetcode150, neetcode250, all)
- **longest increasing subsequence (patience tails vs DP)**
    - LeetCode 300 Longest Increasing Subsequence (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 673 Number of Longest Increasing Subsequence (medium; all)
- **wildcard matching**
    - LeetCode 44 Wildcard Matching (hard; practice)
- **palindrome partitioning**
    - LeetCode 131 Palindrome Partitioning (medium; neetcode150, neetcode250, all)
- **minimum cost to cut a stick (interval DP)**
    - LeetCode 1547 Minimum Cost to Cut a Stick (hard; all)

### 19. Running-state scans

- **Kadane: best contiguous sum**
    - LeetCode 53 Maximum Subarray (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 918 Maximum Sum Circular Subarray (medium; neetcode250, all)
    - LeetCode 1749 Maximum Absolute Sum of Any Subarray (medium; all)
- **Kadane variants (circular, turbulent)**
    - LeetCode 918 Maximum Sum Circular Subarray (medium; neetcode250, all)
    - LeetCode 978 Longest Turbulent Subarray (medium; neetcode250, all)
- **running bracket balance**
    - LeetCode 1614 Maximum Nesting Depth of the Parentheses (easy; all)
    - LeetCode 1653 Minimum Deletions to Make String Balanced (medium; all)
    - LeetCode 2914 Minimum Number of Changes to Make Binary String Beautiful (medium; all)
- **range of possible open counts (wildcard brackets)**
    - LeetCode 678 Valid Parenthesis String (medium; neetcode150, neetcode250, all)
    - LeetCode 2116 Check if a Parentheses String Can Be Valid (medium; all)
- **running cash balance with deposits and withdrawals**
    - LeetCode 860 Lemonade Change (easy; neetcode250, all)
- **running best partner (best sightseeing pair)**
    - LeetCode 1014 Best Sightseeing Pair (medium; all)
- **increments as the sum of positive differences**
    - LeetCode 1526 Minimum Number of Increments on Subarrays to Form a Target Array (hard; all)
- **filter the candidates by constraints, then combine**
    - LeetCode 1899 Merge Triplets to Form Target Triplet (medium; neetcode150, neetcode250, all)
    - LeetCode 3487 Maximum Unique Subarray Sum After Deletion (easy; practice)

### 20. Window flips and grouping

- **flip a window of k, left to right (queue / difference array)**
    - LeetCode 995 Minimum Number of K Consecutive Bit Flips (hard; all)
    - LeetCode 3191 Minimum Operations to Make Binary Array Elements Equal to One I (medium; all)
- **group the sorted values into runs of k**
    - LeetCode 846 Hand of Straights (medium; neetcode150, neetcode250, all)
    - LeetCode 1296 Divide Array in Sets of K Consecutive Numbers (medium; practice)
- **pair each value with its double**
    - LeetCode 2007 Find Original Array From Doubled Array (medium; practice)
- **buy in threes with the cheapest free**
    - LeetCode 2144 Minimum Cost of Buying Candies With Discount (easy; practice)
- **assign the largest tasks to the earliest-free processors**
    - LeetCode 2895 Minimum Processing Time (medium; practice)
- **zero out an array with window subtractions**
    - LeetCode 2772 Apply Operations to Make All Array Elements Equal to Zero (medium; practice)

### 21. Greedy simulation

- **simulate a game with the best local move**
    - LeetCode 649 Dota2 Senate (medium; neetcode250, all)
    - LeetCode 950 Reveal Cards In Increasing Order (medium; all)
    - LeetCode 2126 Destroying Asteroids (medium; practice)
- **make two sums equal by replacing wildcards**
    - LeetCode 2918 Minimum Equal Sum of Two Arrays After Replacing Zeros (medium; practice)
- **lexicographically best array from counts and a queue**
    - LeetCode 3948 Lexicographically Maximum MEX Array (hard; practice)
- **remove pieces under a neighbour rule**
    - LeetCode 2038 Remove Colored Pieces if Both Neighbors are the Same Color (medium; all)
- **order the events by arrival time**
    - LeetCode 1921 Eliminate Maximum Number of Monsters (medium; all)

### 22. Core implementation patterns

- **sort by a key tuple**
    - LeetCode 1710 Maximum Units on a Truck (easy; practice)
- **heap with a (priority, payload) entry**
    - LeetCode 502 IPO (hard; neetcode250, all)
- **running counters and sentinels**
    - LeetCode 860 Lemonade Change (easy; neetcode250, all)
- **prefix and suffix arrays**
    - LeetCode 581 Shortest Unsorted Continuous Subarray (medium; practice)
- **difference array for range updates**
    - LeetCode 995 Minimum Number of K Consecutive Bit Flips (hard; all)
- **two-pass scan (left to right, then back)**
    - LeetCode 135 Candy (hard; neetcode250, all)
- **brute-force checker to test a greedy on small inputs**: no problem in the data: needs one from LeetCode
- **proof sketch: exchange / stay-ahead / invariant**: no problem in the data: needs one from LeetCode

## Gaps

**Patterns with no problem in the data** (8 of the 151 patterns). Each needs one example picked from LeetCode and checked on the site:

- 7. minimise maximum lateness / weighted completion time (sort by ratio)
- 13. choose k non-overlapping jobs for the largest total
- 14. Huffman coding tree and expected code length
- 14. merge many sorted files at least total cost
- 15. greedy graph colouring by degree order
- 15. topological order with a priority queue (smallest label first)
- 22. brute-force checker to test a greedy on small inputs
- 22. proof sketch: exchange / stay-ahead / invariant

**Patterns with one problem only** (74). Thin: a second example should come from LeetCode:

- 1. custom comparator order (concatenation order)
- 2. remove covered intervals (start ascending, end descending)
- 2. fewest points that stab every interval
- 2. fewest intervals or taps to cover a range
- 2. attend the most events (earliest deadline first)
- 3. furthest reachable position
- 3. minimum jumps by BFS layers (current end / next end)
- 3. cover a range with the fewest segments (jump game in disguise)
- 3. jump with costs (DP, greedy fails)
- 3. reach a target by exact steps (math on the sum)
- 4. circular route with a total and a running surplus (reset the start)
- 4. split point where the prefix sum equals a target part
- 4. refuel from a heap of passed stations
- 4. spend the scarcest resource only when stuck (bricks and ladders)
- 4. smallest starting energy so the running total never drops below zero
- 5. spend low, gain high (two ends of a sorted list)
- 5. move the shorter side inward
- 5. one skip allowed, then check the rest
- 5. pairs summing to a target, taken from both ends
- 6. merge the two smallest
- 6. earliest deadline first
- 7. deadline ordering, replacing the largest taken job
- 8. monotone stack for the smallest number after k removals
- 8. remove pairs in order of highest score
- 8. visible elements (ocean view)
- 9. swap once for the largest value
- 9. merge two digit lists into the largest number
- 9. change one character to break a palindrome
- 9. fewest additions to reach a digit-sum target
- 9. smallest number from a product (divide by 9 down to 2)
- 9. sort digits by parity and place them back
- 10. partition by last occurrence
- 10. start a new group when a seen set resets
- 10. partition into equal-sum parts
- 10. partition by a digit requirement (deci-binary: the largest digit)
- 11. left pass, then right pass on ratings
- 11. remove the shortest middle so prefix and suffix are sorted
- 12. one transaction: running minimum
- 12. unlimited transactions: sum of the rises
- 12. unlimited transactions with a fee (cash / hold)
- 12. with a cooldown (state machine; greedy fails)
- 12. stock with one change of strategy
- 12. best pair with a distance penalty (running best of a[i] + i)
- 13. most events attended on distinct days
- 13. two activities, earliest combined finish
- 14. merge the two smallest repeatedly (connect sticks / optimal merge)
- 15. Prim: grow one tree with a min-heap
- 16. split a count into groups of 2 and 3
- 16. count across lines (laser beams)
- 16. smallest missing value from residue counts
- 17. maximum XOR by prefix / trie greedy
- 17. flip rows, then columns, by bit weight
- 17. place the bits for the largest odd binary number
- 18. stocks with a cooldown
- 18. wildcard matching
- 18. palindrome partitioning
- 18. minimum cost to cut a stick (interval DP)
- 19. running cash balance with deposits and withdrawals
- 19. running best partner (best sightseeing pair)
- 19. increments as the sum of positive differences
- 20. pair each value with its double
- 20. buy in threes with the cheapest free
- 20. assign the largest tasks to the earliest-free processors
- 20. zero out an array with window subtractions
- 21. make two sums equal by replacing wildcards
- 21. lexicographically best array from counts and a queue
- 21. remove pieces under a neighbour rule
- 21. order the events by arrival time
- 22. sort by a key tuple
- 22. heap with a (priority, payload) entry
- 22. running counters and sentinels
- 22. prefix and suffix arrays
- 22. difference array for range updates
- 22. two-pass scan (left to right, then back)

**Where the examples come from.** Of the 193 distinct problems used above, 80 are in the Greedy pattern, 64 are filed under other patterns but tagged `Greedy`, and 49 are in other patterns without the tag (classic problems such as Merge Intervals, Coin Change or the stock variants). Only 80 of the 119 Greedy-pattern problems are used as examples, because the techniques are coarse: `Greedy:sort-pick` and `Greedy:scan-balance` hold 15 problems each across many different ideas.

**Premium problems.** 11 of the examples are premium and so are not free to read: 252, 253, 277, 358, 484, 625, 759, 1055, 1167, 1196, 1762. A free alternative is wanted where a lesson leans on them.

**Data filed under Greedy that is a loose fit** (owner decides whether to re-file; nothing is changed here):

- LeetCode 44 Wildcard Matching (hard; practice): wildcard matching is DP; filed under `Greedy:flip-window`
- LeetCode 2389 Longest Subsequence With Limited Sum (easy; practice): prefix sums and binary search; filed under `Greedy:flip-window`
- LeetCode 2680 Maximum OR (medium; practice): prefix and suffix OR; filed under `Greedy:flip-window`
- LeetCode 3413 Maximum Coins From K Consecutive Bags (medium; practice): sliding window over sorted segments; filed under `Greedy:flip-window`
- LeetCode 2259 Remove Digit From Number to Maximize Result (easy; practice): enumerate each digit removal; filed under `Greedy:kadane`
- LeetCode 2600 K Items With the Maximum Sum (easy; practice): arithmetic on counts; filed under `Greedy:kadane`
- LeetCode 2800 Shortest String That Contains Three Strings (medium; practice): enumerate merge orders; filed under `Greedy:kadane`
- LeetCode 3434 Maximum Frequency After Subarray Operation (medium; all): Kadane variant with counts, but DP-flavoured; filed under `Greedy:kadane`
- LeetCode 3440 Reschedule Meetings for Maximum Free Time II (medium; practice): gap enumeration; filed under `Greedy:kadane`

**Proof habit.** Each lesson should state the exchange or stay-ahead argument behind its template and give one small counter-example where the obvious greedy fails (group 18 collects them). Not written.

**Proposal (the owner decides, nothing is built).** Keep the 13 techniques as the spine. Add technique lessons with tabs for the variants, one per row of the groups above, and link to the Intervals, Heap, Stack and Advanced Graphs lessons instead of copying them where a group overlaps (groups 2, 6, 8, 14, 15); mock the tabs first (rule 13) and pick the missing examples from LeetCode.
