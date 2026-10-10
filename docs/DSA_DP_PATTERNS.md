# Dynamic programming patterns: the exhaustive target list

The owner's rule (2026-10-09) applied to 1-D Dynamic Programming and 2-D Dynamic Programming: every dynamic-programming pattern that can come up on LeetCode, as the target for the two pattern lessons. The rule is in [DSA.md](DSA.md), decision 32: a topic's patterns section is exhaustive, patterns without a NeetCode problem get **example problems** from LeetCode, and variants of one pattern (top-down / bottom-up, O(n squared) / binary search) are **tabs** of one lesson. The format follows [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md).

Status: documented only. Today `content/dsa/lessons/1-d-dynamic-programming.toml` has 12 techniques (recurrence, take-skip, expand, unbounded, min-max-run, prefix-dp, lis, subset, partition-dp, count-states, game, bitmask) and `2-d-dynamic-programming.toml` has 6 (grid-dp, two-string, pair-dp, state-machine, dfs-memo, interval). Building the rest needs a mockup of the tabs first, then lessons and picked example problems. Where 1-D versus 2-D does not matter (a pattern runs on either), the split between the two topics is still open; this list is by pattern, not by topic.

Items written *a / b* in a group are variants for tabs where one lesson covers both (for example "memo: top-down / bottom-up"). Several groups overlap on purpose (a stock problem is a state machine, a knapsack is a counting table); each pattern keeps its own lesson and cross-references the others.

1. **Linear and sequence DP.** One-step recurrence (Fibonacci, climbing stairs); k-step recurrence (tribonacci, a fixed set of moves); minimum-cost stairs; take or skip along a line (house robber); circular take or skip (first and last are neighbours); take or skip with value buckets (delete and earn reduces to house robber); maximum subarray (Kadane); maximum product subarray (track a max and a min); subarray with one deletion; jump-reach DP; counting decodings of a string; counting compositions of n; dp[i] = best over all j < i (the O(n squared) transition); cut a sequence into groups with a cost (partition DP); word break (dictionary prefix DP); weighted interval scheduling (sort by end, binary search the last compatible job); dp indexed by value instead of position; dp with a hash map as sparse state; Pascal's triangle and other table recurrences; ugly numbers (pointers into earlier answers); integer break and other number-splitting recurrences; define the state, transition, base case, fill order and answer cell before coding.
2. **Knapsack family.** 0/1 knapsack (one array, capacity iterated downward); subset sum (feasibility); partition equal subset sum; target sum / count subsets with a given sum; minimum subset difference; unbounded knapsack (capacity iterated upward); bounded knapsack (binary splitting / monotonic queue); two-budget knapsack (a 2-D capacity); group knapsack (at most one item per group); knapsack with dependencies between items; combinations versus permutations (which loop is outer); exact-fill versus at-most-fill (how dp is initialised); count / min / max / feasibility variants of the same table; knapsack on value instead of weight (swap the dimensions when the capacity is huge); meet in the middle for large n; bitset-accelerated subset sum; knapsack with a greedy contrast (fractional versus 0/1).
3. **Coin change.** Fewest coins for an amount; number of ways as combinations (coins outer); number of ways as ordered sequences (amount outer); unreachable amounts (infinity sentinel); fewest perfect squares; BFS over remaining amount as the alternative to DP; limited number of each coin; at most k coins; canonical coin systems (when greedy is correct); largest unreachable amount (Frobenius, math); inverse coin change (rebuild the coin set from a ways table); coin change with reconstruction; huge amounts (periodicity, matrix power); sums of distinct powers; dice-and-target and stairs problems as coin change in disguise.
4. **Longest increasing subsequence.** LIS: O(n squared) DP / patience sorting with binary search (O(n log n)); strict versus non-strict; count the LIS; reconstruct one LIS (predecessor array); Fenwick / segment tree indexed by value; LIS with a maximum gap between neighbours; 2-D LIS (envelopes: sort one key, tie-break the other, LIS the second); chain problems (pair chain, string chain); largest divisible subset; longest bitonic / mountain subsequence (LIS from both ends); minimum deletions to make sorted (n minus LIS); longest arithmetic subsequence (fixed difference / any difference); longest Fibonacci-like subsequence; weighted LIS (best team with no conflicts, maximum-sum increasing subsequence); longest ideal subsequence (alphabet-indexed); longest decreasing / Dilworth (minimum number of chains); LIS over a circular array.
5. **LCS and edit distance.** Longest common subsequence; reconstruct the LCS; edit distance (insert / delete / replace, weighted costs); delete-only distance and minimum ASCII delete sum; shortest common supersequence; longest common substring (contiguous, resets to 0); distinct subsequences (count the ways t appears in s); interleaving strings; regular-expression matching ('.' and '*'); wildcard matching ('?' and '*'); longest palindromic subsequence as LCS with the reverse; uncrossed lines (LCS on arrays); LCS of three strings (3-D table); linear-space Hirschberg; banded edit distance O(nd); transposition edit distance (Damerau); minimal edit script; sequence alignment with gap penalties; LCS with a bitset; LCS of permutations reduced to LIS.
6. **Interval DP.** Dp[l][r] filled by increasing length; choose the last operation, not the first (burst balloons); matrix chain multiplication; minimum cost to cut a stick; merge stones (k-way merge with prefix sums); optimal binary search tree and Catalan splits; strange printer; remove boxes (an extra dimension for equal neighbours); both-ends games (interval game); minimum insertions / removals to make a palindrome; string compression and encoding by repeats; polygon triangulation; parenthesisation (different ways to add parentheses, boolean evaluation); circular interval DP (double the array); interval DP with an extra count dimension (k pieces); Zuma-style removals; expression and bracket DP.
7. **Palindromic DP.** Boolean table is_pal[i][j]; expand around every centre (2n - 1 centres); Manacher in O(n); longest palindromic substring; count palindromic substrings; longest palindromic subsequence; minimum cuts for a palindrome partition; all palindrome partitions (table + backtracking); minimum insertions to make a palindrome; k-palindrome (valid palindrome III); count distinct palindromic subsequences; count palindromic subsequences of length k (prefix and suffix counts); non-overlapping palindromic substrings (DP or greedy over a table); products of two disjoint palindromic subsequences (bitmask); rolling-hash palindrome checks; palindromic tree (eertree).
8. **Grid and path DP.** Unique paths (counting); unique paths with obstacles; minimum path sum; triangle (bottom-up); falling path (three neighbours, or any other column); dungeon game (fill backward from the goal); maximal square; count square submatrices; maximal rectangle (histogram per row); largest plus sign (four directional passes); cherry pickup (two walkers moving together); k walkers on a grid; memoised DFS on a grid that forms a DAG (increasing paths); moves in four directions; maximum / minimum product path (track both extremes); row-to-row transition cost (min over previous row, prefix-max trick); paint house with k colours; out-of-boundary paths (step count as a dimension); grid with remaining-budget dimension (obstacles removable, turns); submatrix counts with prefix sums; combinatorial shortcut (binomials) versus DP; one-row space optimisation.
9. **Tree DP.** Subtree aggregation (return a tuple per node); take or skip on a tree (house robber III, independent set); maximum path sum (return one chain, update the answer with two); diameter; three-state camera cover / dominating set; largest BST subtree (return min, max, size, validity); counting tree shapes (unique BSTs, full binary trees, Catalan); tree knapsack (distribute a budget among children, O(n squared) merge); rerooting (sum of distances, edge reversals); parent-state DP (colouring a tree); longest univalue / consecutive path; vertex cover and matching on trees; collect-apples style edge cost DP; good leaf pairs (depth array merge); counting paths with a property (parity masks); small-to-large merging of subtree maps; DP on n-ary trees and on parent arrays.
10. **DAG and graph DP.** Longest path in a DAG; number of paths in a DAG; memoised DFS on an implicit DAG; DP in topological order (Kahn: parallel courses, largest colour value); shortest path with an edge-count dimension (Bellman-Ford layers, cheapest flights within k stops); counting shortest paths (Dijkstra with a ways array); Floyd-Warshall as DP over intermediate vertices; DP over strongly connected components; functional-graph DP (chain lengths and cycles); resource-constrained paths (state = node + fuel / time); minimum-cost paths over a state graph; walk counting by adjacency-matrix power; Hamiltonian path and TSP (see bitmask); DP on a graph of subproblems (word ladder as BFS versus DP).
11. **Bitmask DP.** Assign items to buckets by a used-mask (matchsticks to square, k equal-sum subsets, fair cookies, minimum time for jobs); TSP / Hamiltonian path; shortest path visiting all nodes (BFS over (mask, node)); permutation DP via mask (beautiful arrangement, squareful arrays); minimum sufficient set (stickers to spell a word); subset games (can I win); pairing DP (maximise score after n operations); assignment problem; iterating submasks (3 to the n); sum over subsets (SOS) DP; mask over the alphabet; set of distinct values as state (bitwise ORs of subarrays); mask plus remainder (hats, counting arrangements); lowest-set-bit transitions; mask of characters for string problems; meet in the middle on subsets; knapsack over subsets of items; account balancing (debt settlement by subset).
12. **Digit DP.** Count numbers up to N with a property; state = (position, tight, started, extra); no two consecutive ones in binary; count numbers with unique digits; count special integers (distinct digits); digit sum / divisible by k (remainder in the state); count occurrences of a digit; range [L, R] as f(R) - f(L - 1); digits from an allowed set; rotated or confusing digits; memoise only when not tight and already started; stepping numbers; k-th number with a property (descend by counts); binary-representation DP; numbers with an order constraint on digits (monotone, alternating); lexicographic ranking of permutations.
13. **State machine DP.** Stocks: one transaction, unlimited, at most k (hold / sold states); cooldown; transaction fee; two transactions; alternating-sign subsequence sum; flip string to monotone (0s then 1s); paint with no equal neighbours (last-colour state); string avoiding a pattern (KMP automaton as DP states); DFA-driven counting; per-parity or per-remainder states (visit array positions with a penalty); phases of a shape (increasing then decreasing); last-chosen-value state; best of a few modes carried along the scan; operations with a toggle state (flip / not flipped); states that become a matrix (see matrix exponentiation).
14. **Probability and expected value.** Random walk probability after k steps (knight on a board); dice-sum probabilities with a sliding window (New 21 Game); expected number of steps by backward DP; soup-servings style problems that converge for large n (cap n); champagne-tower flow simulation; absorbing states and cyclic expectations (Gaussian elimination); probability of winning a game against a random opponent; linearity of expectation DP; coupon collector; probability with a bitmask of remaining items; Markov chain steps by matrix power; expected value modulo a prime (modular inverses); probability of reaching a target before another; DP over the probability that an event fails.
15. **Game and minimax DP.** Take from both ends (predict the winner); stone games I to VII; take 1 to 3 items; score difference dp (current player's lead); subset-state games (can I win); win / lose / draw states with retrograde analysis on a graph (cat and mouse); Nim and Sprague-Grundy numbers; parity shortcuts (stone game I); game with a growing limit M; suffix-sum formulation; split-the-row games; memoised minimax with alpha-beta pruning; who moves first state; cooperative versus adversarial turns; strategy as a threshold (binary search on the answer plus a game check).
16. **Counting DP.** Number of ways modulo 1e9 + 7; compositions and paths with steps; dice rolls to a target; domino and tromino tilings; arrangements with a constraint (rearrange sticks with k visible, k inverse pairs, music playlists); strings with adjacency rules (vowel permutation, knight dialer, attendance record); stay in place after k steps; counting subsequences; counting partitions into k non-empty groups; Catalan-numbered structures (non-crossing handshakes, parentheses); insertion DP on permutations (count permutations by inversions); inclusion-exclusion with DP; Stirling numbers; strings that avoid forbidden substrings (automaton states); counting with a prefix-sum speedup; counting distinct objects (avoid double counting by a canonical order); count sub-multisets with a bounded sum; counting paths with exactly k turns; combinatorics shortcut versus DP; handle negative values after modulo.
17. **Prefix-sum and monotonic-queue optimisation.** Prefix sums over dp for range-sum transitions (dice, corridor, jump game VII); sliding-window maximum in the transition (constrained subsequence sum, jump game VI); monotonic deque for partition counts with a max - min limit; prefix-max along a row (points with cost); left-to-right and right-to-left max passes; Fenwick / segment tree for dp[i] = best over a value range (LIS II); coordinate compression for the tree index; difference arrays for range-add transitions; last-occurrence map for distinct subsequence counts; sorted events plus binary search; best-so-far per key (per remainder, per value); monotonic stack contribution (subarray minimums, min-product); sqrt decomposition for transitions; two-pointer window for dp that depends on a range of length k.
18. **Divide and conquer, Knuth and convex hull trick.** Divide and conquer optimisation (monotone optimal split for k-partition DP); Knuth optimisation (interval DP in O(n squared)); Monge arrays and SMAWK; convex hull trick (monotone slopes) and Li Chao tree; the quadrangle inequality as the thing to check; Aliens trick / Lagrangian relaxation (WQS binary search on the penalty); slope trick (convex piecewise-linear dp); 1D/1D optimisation with a monotonic queue; CDQ divide and conquer for dp ordered by time; offline D&C with rollback; bitset optimisation as the practical alternative.
19. **Matrix exponentiation.** Linear recurrence as a transition matrix; fast Fibonacci and tribonacci; counting walks of length n in a graph; counting strings of length n by automaton state; knight dialer / vowel permutation for huge n; Kitamasa and characteristic polynomials; augmented matrix to carry a running sum; exponentiation by squaring modulo p; Berlekamp-Massey for an unknown recurrence; min-plus (tropical) matrix power for shortest paths with exactly k edges; fast doubling; tilings of a strip with large n; Gaussian elimination for expected values on cyclic chains.
20. **Space optimisation.** Rolling array: two rows / one row with the right iteration direction (downward for 0/1, upward for unbounded); O(1) variables for a k-step recurrence; previous-diagonal temp variable (edit distance, LCS); parity trick dp[i & 1]; bitset DP; Hirschberg when the answer must be reconstructed; keep only reachable states (hash map); a window of the last k rows; in-place DP on the input; transpose so the short dimension is the array; give up space when reconstruction needs the full table.
21. **Memoisation versus tabulation.** Memoisation: top-down with a memo (hash map / array with a sentinel) / bottom-up table; fill order (by length, by index, by topological order, by decreasing capacity); top-down wins on sparse state spaces; bottom-up wins on recursion depth; recursion limit and the iterative rewrite; memo key design (tuples, masks, packed integers; drop arguments that do not affect the answer); DFS + memo on implicit DAGs; cycles in the state graph (a visiting sentinel; DP is invalid on cycles); pull versus push DP; BFS over states as the alternative (coin change, perfect squares, fewest steps); from brute force to DP (write the recursion, find the overlapping calls, memoise, then tabulate).
22. **Reconstruction.** Choice / parent pointers; walking back through the table; rebuild the LCS or the edit script; rebuild a subset-sum solution; rebuild the LIS from predecessors; lexicographically smallest optimal answer (compare while filling, or fill from the end); enumerate all solutions with memoised results (word break II, unique BSTs II); count versus list; rebuild a tree structure; rebuild the path through a grid or a coin set; k-th solution by descending with counts; tie-breaking rules for a deterministic answer; reconstruction in linear space (Hirschberg).
23. **Constrained subsequences.** Gap constraint between chosen indices (jump, constrained subsequence sum); difference constraint between neighbours (longest subsequence with difference d); at most k changes between adjacent chosen elements (good subsequence); alphabet-indexed best (longest ideal subsequence); arithmetic subsequence with a map of differences; Fibonacci-like subsequences; subsequence selected by parity or remainder of adjacent sums (valid subsequence); choosing one of two arrays per position (non-decreasing from two arrays); matching a target as a subsequence (distinct subsequences, number of matching subsequences with next-occurrence tables); is-subsequence and next-pointer automaton; subsequence with a sum constraint (knapsack); at-most-k removals; binary subsequence below a bound (greedy + DP); products or sums over an alternating subsequence.
24. **Broken profile and tiling DP.** Domino tiling of a w x n board with a frontier mask; row-mask DP with precomputed compatibility (maximum students taking an exam, paint an n x 3 grid); counting tilings of 2 x n and 3 x n with dominoes and trominoes; broken profile (cell by cell, a mask of the last w cells); plug DP (connectivity states for Hamiltonian cycles on grids); Steiner tree (mask of terminals); profile DP plus matrix power for huge n; counting independent sets on grid strips; Gray-code ordering of masks; tiling with squares: backtracking versus DP.

## Coverage today

- **1-D Dynamic Programming.** 103 problems in the data (11 must-learn, 92 practice); 12 techniques: Bitmask DP (4); A recurrence over positions (17); Take or skip along a line (8); Expand around a center (2); Unbounded knapsack (5); Track both a max and a min (1); DP over prefixes with a dictionary (2); Longest increasing subsequence (10); 0/1 subset knapsack (7); Partitioning a sequence into groups (4); Counting paths over states (11); Minimax game DP (3).
- **2-D Dynamic Programming.** 74 problems in the data (6 must-learn, 68 practice); 6 techniques: Grid DP (14); Two-string DP table (10); DP over pairs of positions (2); State machine DP (3); DFS with memoization on a grid (1); Interval DP (3).
- **Tagged Dynamic Programming in other topics.** 102 more problems: Greedy 23; Backtracking 16; Arrays & Hashing 9; Sliding Window 8; Trees 8; Graphs 8; Intervals 6; Advanced Graphs 6; Stack 5; Two Pointers 4; Binary Search 3; Heap / Priority Queue 2; Math & Geometry 2; Bit Manipulation 1; Tries 1. The tag is a hint only; those problems are taught in their own topic's lesson.
- **Total.** 177 problems sit in the two DP topics and 279 carry the Dynamic Programming tag.
- **Covered well** (a technique and several problems): linear recurrence and take-skip (group 1), 0/1 and unbounded knapsack (2, 3), LIS (4), two-string tables (5), grid DP (8), state machines (13), counting tables (16), games (15), small bitmask problems (11).
- **Touched, with no lesson of their own:** palindromic DP (7, only the expand technique), tree DP (9, in Trees), DAG DP (10, in Graphs and Advanced Graphs), interval DP (6, three problems), and, at most, a pitfall line for reconstruction (22), space optimisation (20) and memo versus table (21).
- **Missing:** digit DP (12), probability and expected value (14, no lesson; only a few counting problems), prefix-sum and monotonic-queue optimisation (17), divide and conquer / Knuth / convex hull trick (18), matrix exponentiation (19), broken profile (24), and constrained subsequences as a named pattern (23).

## Example problems per pattern

Up to four problems per pattern, taken only from the data (`problems.json` and `practice.json`); each line is `LeetCode <number> <title> (<difficulty>; <lists>)`. A pattern with no fitting problem in the data says so: it needs one picked from LeetCode and checked there. Patterns are the headline lines of each group, not every item; other items in a group are taught inside the lesson of the nearest pattern here.

### 1. Linear and sequence DP

- **One-step and k-step recurrence**
    - LeetCode 70 Climbing Stairs (easy; blind75, neetcode150, neetcode250, all)
    - LeetCode 509 Fibonacci Number (easy; practice)
    - LeetCode 1137 N-th Tribonacci Number (easy; neetcode250, all)
    - LeetCode 746 Min Cost Climbing Stairs (easy; neetcode150, neetcode250, all)
- **Cost with fixed moves (min cost over tickets, stairs)**
    - LeetCode 983 Minimum Cost For Tickets (medium; all)
    - LeetCode 746 Min Cost Climbing Stairs (easy; neetcode150, neetcode250, all)
    - LeetCode 3154 Find Number of Ways to Reach the K-th Stair (hard; practice)
    - LeetCode 2466 Count Ways To Build Good Strings (medium; all)
- **Take or skip along a line**
    - LeetCode 198 House Robber (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 740 Delete and Earn (medium; all)
    - LeetCode 2320 Count Number of Ways to Place Houses (medium; practice)
    - LeetCode 2140 Solving Questions With Brainpower (medium; all)
- **Circular take or skip**
    - LeetCode 213 House Robber II (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 3840 House Robber V (medium; practice)
- **Maximum subarray, product and one deletion**
    - LeetCode 53 Maximum Subarray (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 152 Maximum Product Subarray (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 1186 Maximum Subarray Sum with One Deletion (medium; practice)
    - LeetCode 918 Maximum Sum Circular Subarray (medium; neetcode250, all)
- **Jump-reach DP**
    - LeetCode 55 Jump Game (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 45 Jump Game II (medium; neetcode150, neetcode250, all)
    - LeetCode 1871 Jump Game VII (medium; neetcode250, all)
    - LeetCode 2770 Maximum Number of Jumps to Reach the Last Index (medium; practice)
- **Counting decodings and splits of a string**
    - LeetCode 91 Decode Ways (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 2266 Count Number of Texts (medium; practice)
    - LeetCode 2369 Check if There is a Valid Partition For The Array (medium; all)
    - LeetCode 2147 Number of Ways to Divide a Long Corridor (hard; all)
- **Partition a sequence into groups with a cost**
    - LeetCode 1043 Partition Array for Maximum Sum (medium; all)
    - LeetCode 1105 Filling Bookcase Shelves (medium; all)
    - LeetCode 3144 Minimum Substring Partition of Equal Character Frequency (medium; practice)
    - LeetCode 2767 Partition String Into Minimum Beautiful Substrings (medium; practice)
- **Word break (dictionary prefix DP)**
    - LeetCode 139 Word Break (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 140 Word Break II (hard; neetcode250, all)
    - LeetCode 472 Concatenated Words (hard; all)
    - LeetCode 2707 Extra Characters in a String (medium; neetcode250, all)
- **Weighted interval scheduling**
    - LeetCode 1235 Maximum Profit in Job Scheduling (hard; all)
    - LeetCode 2008 Maximum Earnings From Taxi (medium; practice)
    - LeetCode 1751 Maximum Number of Events That Can Be Attended II (hard; practice)
    - LeetCode 689 Maximum Sum of 3 Non-Overlapping Subarrays (hard; all)
- **Number-splitting and generator recurrences**
    - LeetCode 343 Integer Break (medium; neetcode250, all)
    - LeetCode 264 Ugly Number II (medium; all)
    - LeetCode 313 Super Ugly Number (medium; practice)
    - LeetCode 651 4 Keys Keyboard (medium; all)
- **Pascal's triangle and table recurrences**
    - LeetCode 118 Pascal's Triangle (easy; all)
    - LeetCode 119 Pascal's Triangle II (easy; all)
    - LeetCode 650 2 Keys Keyboard (medium; all)

### 2. Knapsack family

- **0/1 knapsack and subset sum**
    - LeetCode 416 Partition Equal Subset Sum (medium; neetcode150, neetcode250, all)
    - LeetCode 1049 Last Stone Weight II (medium; neetcode250, all)
    - LeetCode 2915 Length of the Longest Subsequence That Sums to Target (medium; practice)
    - LeetCode 2742 Painting the Walls (hard; all)
- **Count subsets with a sum (target sum)**
    - LeetCode 494 Target Sum (medium; neetcode150, neetcode250, all)
    - LeetCode 2902 Count of Sub-Multisets With Bounded Sum (hard; practice)
    - LeetCode 879 Profitable Schemes (hard; all)
- **Two-budget and multi-dimension knapsack**
    - LeetCode 474 Ones and Zeroes (medium; all)
    - LeetCode 879 Profitable Schemes (hard; all)
    - LeetCode 2742 Painting the Walls (hard; all)
- **Group knapsack (one item per group)**
    - LeetCode 2218 Maximum Value of K Coins From Piles (hard; all)
    - LeetCode 1981 Minimize the Difference Between Target and Chosen Elements (medium; practice)
- **Unbounded knapsack and combination counting**
    - LeetCode 518 Coin Change II (medium; neetcode150, neetcode250, all)
    - LeetCode 377 Combination Sum IV (medium; neetcode250, all)
    - LeetCode 2787 Ways to Express an Integer as Sum of Powers (medium; practice)
    - LeetCode 322 Coin Change (medium; blind75, neetcode150, neetcode250, all)
- **Meet in the middle for subset sums**
    - LeetCode 805 Split Array With Same Average (hard; all)
    - LeetCode 2035 Partition Array Into Two Arrays to Minimize Sum Difference (hard; practice)

### 3. Coin change

- **Fewest coins for an amount**
    - LeetCode 322 Coin Change (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 279 Perfect Squares (medium; neetcode250, all)
    - LeetCode 3592 Inverse Coin Change (medium; practice)
- **Number of ways: combinations versus ordered sequences**
    - LeetCode 518 Coin Change II (medium; neetcode150, neetcode250, all)
    - LeetCode 377 Combination Sum IV (medium; neetcode250, all)
    - LeetCode 2787 Ways to Express an Integer as Sum of Powers (medium; practice)
    - LeetCode 2466 Count Ways To Build Good Strings (medium; all)
- **Coin change as BFS**
    - LeetCode 322 Coin Change (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 279 Perfect Squares (medium; neetcode250, all)
    - LeetCode 1553 Minimum Number of Days to Eat N Oranges (hard; all)

### 4. Longest increasing subsequence

- **O(n squared) DP and patience sorting**
    - LeetCode 300 Longest Increasing Subsequence (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 673 Number of Longest Increasing Subsequence (medium; all)
    - LeetCode 1626 Best Team With No Conflicts (medium; all)
    - LeetCode 368 Largest Divisible Subset (medium; all)
- **Count and reconstruct the LIS**
    - LeetCode 673 Number of Longest Increasing Subsequence (medium; all)
    - LeetCode 368 Largest Divisible Subset (medium; all)
    - LeetCode 300 Longest Increasing Subsequence (medium; blind75, neetcode150, neetcode250, all)
- **LIS with a Fenwick / segment tree**
    - LeetCode 2407 Longest Increasing Subsequence II (hard; practice)
    - LeetCode 1964 Find the Longest Valid Obstacle Course at Each Position (hard; all)
    - LeetCode 673 Number of Longest Increasing Subsequence (medium; all)
    - LeetCode 1395 Count Number of Teams (medium; all)
- **2-D LIS and chain problems**
    - LeetCode 354 Russian Doll Envelopes (hard; all)
    - LeetCode 646 Maximum Length of Pair Chain (medium; all)
    - LeetCode 1048 Longest String Chain (medium; all)
- **Bitonic / mountain (LIS from both ends)**
    - LeetCode 1671 Minimum Number of Removals to Make Mountain Array (hard; all)
    - LeetCode 845 Longest Mountain in Array (medium; practice)
- **Arithmetic and Fibonacci-like subsequences**
    - LeetCode 1218 Longest Arithmetic Subsequence of Given Difference (medium; practice)
    - LeetCode 873 Length of Longest Fibonacci Subsequence (medium; all)
    - LeetCode 446 Arithmetic Slices II - Subsequence (hard; all)
    - LeetCode 413 Arithmetic Slices (medium; practice)
- **Alphabet-indexed and parity-indexed LIS variants**
    - LeetCode 2370 Longest Ideal Subsequence (medium; all)
    - LeetCode 3201 Find the Maximum Length of Valid Subsequence I (medium; practice)
    - LeetCode 3202 Find the Maximum Length of Valid Subsequence II (medium; practice)
    - LeetCode 2771 Longest Non-decreasing Subarray From Two Arrays (medium; practice)
- **LIS over a circular array**
    - no problem in the data: needs one from LeetCode

### 5. LCS and edit distance

- **Longest common subsequence**
    - LeetCode 1143 Longest Common Subsequence (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 1035 Uncrossed Lines (medium; all)
    - LeetCode 583 Delete Operation for Two Strings (medium; practice)
    - LeetCode 712 Minimum ASCII Delete Sum for Two Strings (medium; practice)
- **Edit distance**
    - LeetCode 72 Edit Distance (medium; neetcode150, neetcode250, all)
    - LeetCode 583 Delete Operation for Two Strings (medium; practice)
    - LeetCode 712 Minimum ASCII Delete Sum for Two Strings (medium; practice)
    - LeetCode 1216 Valid Palindrome III (hard; all)
- **Shortest common supersequence and reconstruction**
    - LeetCode 1092 Shortest Common Supersequence (hard; all)
    - LeetCode 1143 Longest Common Subsequence (medium; blind75, neetcode150, neetcode250, all)
- **Counting subsequence matches (distinct subsequences)**
    - LeetCode 115 Distinct Subsequences (hard; neetcode150, neetcode250, all)
    - LeetCode 792 Number of Matching Subsequences (medium; practice)
    - LeetCode 730 Count Different Palindromic Subsequences (hard; practice)
- **Interleaving strings**
    - LeetCode 97 Interleaving String (medium; neetcode150, neetcode250, all)
- **Regular-expression and wildcard matching**
    - LeetCode 10 Regular Expression Matching (hard; neetcode150, neetcode250, all)
    - LeetCode 44 Wildcard Matching (hard; practice)
- **Longest common substring**
    - LeetCode 718 Maximum Length of Repeated Subarray (medium; practice)

### 6. Interval DP

- **Last-operation interval DP (burst balloons)**
    - LeetCode 312 Burst Balloons (hard; neetcode150, neetcode250, all)
    - LeetCode 1000 Minimum Cost to Merge Stones (hard; practice)
    - LeetCode 1547 Minimum Cost to Cut a Stick (hard; all)
- **Cut and merge costs**
    - LeetCode 1547 Minimum Cost to Cut a Stick (hard; all)
    - LeetCode 1000 Minimum Cost to Merge Stones (hard; practice)
    - LeetCode 471 Encode String with Shortest Length (hard; all)
    - LeetCode 664 Strange Printer (hard; practice)
- **Both-ends interval games**
    - LeetCode 486 Predict the Winner (medium; practice)
    - LeetCode 877 Stone Game (medium; neetcode250, all)
    - LeetCode 1690 Stone Game VII (medium; practice)
    - LeetCode 1563 Stone Game V (hard; practice)
- **Parenthesisation and splits**
    - LeetCode 241 Different Ways to Add Parentheses (medium; all)
    - LeetCode 96 Unique Binary Search Trees (medium; all)
    - LeetCode 95 Unique Binary Search Trees II (medium; all)
    - LeetCode 1259 Handshakes That Don't Cross (hard; all)
- **Matrix chain and polygon triangulation**
    - no problem in the data: needs one from LeetCode

### 7. Palindromic DP

- **Longest palindromic substring and counting substrings**
    - LeetCode 5 Longest Palindromic Substring (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 647 Palindromic Substrings (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 2472 Maximum Number of Non-overlapping Palindrome Substrings (hard; practice)
- **Longest palindromic subsequence**
    - LeetCode 516 Longest Palindromic Subsequence (medium; all)
    - LeetCode 1216 Valid Palindrome III (hard; all)
    - LeetCode 2002 Maximum Product of the Length of Two Palindromic Subsequences (medium; all)
- **Count palindromic subsequences**
    - LeetCode 730 Count Different Palindromic Subsequences (hard; practice)
    - LeetCode 2484 Count Palindromic Subsequences (hard; practice)
    - LeetCode 1930 Unique Length-3 Palindromic Subsequences (medium; all)
- **Palindrome partitioning**
    - LeetCode 131 Palindrome Partitioning (medium; neetcode150, neetcode250, all)
    - LeetCode 2472 Maximum Number of Non-overlapping Palindrome Substrings (hard; practice)

### 8. Grid and path DP

- **Unique paths and obstacles**
    - LeetCode 62 Unique Paths (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 63 Unique Paths II (medium; neetcode250, all)
    - LeetCode 576 Out of Boundary Paths (medium; all)
- **Minimum path sum, triangle and falling path**
    - LeetCode 64 Minimum Path Sum (medium; neetcode250, all)
    - LeetCode 120 Triangle (medium; all)
    - LeetCode 931 Minimum Falling Path Sum (medium; all)
    - LeetCode 1289 Minimum Falling Path Sum II (hard; all)
- **Backward DP from the goal (dungeon game)**
    - LeetCode 174 Dungeon Game (hard; practice)
- **Squares and rectangles in a matrix**
    - LeetCode 221 Maximal Square (medium; all)
    - LeetCode 1277 Count Square Submatrices with All Ones (medium; all)
    - LeetCode 85 Maximal Rectangle (hard; practice)
    - LeetCode 1504 Count Submatrices With All Ones (medium; practice)
- **Directional passes (largest plus sign)**
    - LeetCode 764 Largest Plus Sign (medium; practice)
- **Two walkers (cherry pickup)**
    - LeetCode 741 Cherry Pickup (hard; all)
    - LeetCode 1463 Cherry Pickup II (hard; all)
- **Memoised DFS on a grid DAG**
    - LeetCode 329 Longest Increasing Path in a Matrix (hard; neetcode150, neetcode250, all)
    - LeetCode 2328 Number of Increasing Paths in a Grid (hard; practice)
    - LeetCode 1594 Maximum Non Negative Product in a Matrix (medium; practice)
- **Row-to-row transition cost**
    - LeetCode 1937 Maximum Number of Points with Cost (medium; all)
    - LeetCode 2304 Minimum Path Cost in a Grid (medium; practice)
    - LeetCode 1981 Minimize the Difference Between Target and Chosen Elements (medium; practice)
- **Paint house with k colours**
    - LeetCode 256 Paint House (medium; all)
    - LeetCode 265 Paint House II (hard; all)
    - LeetCode 3429 Paint House IV (medium; practice)
- **Min / max product path**
    - LeetCode 1594 Maximum Non Negative Product in a Matrix (medium; practice)

### 9. Tree DP

- **Take or skip on a tree**
    - LeetCode 337 House Robber III (medium; neetcode250, all)
    - LeetCode 968 Binary Tree Cameras (hard; practice)
- **Path sums returned up the tree**
    - LeetCode 124 Binary Tree Maximum Path Sum (hard; blind75, neetcode150, neetcode250, all)
    - LeetCode 543 Diameter of Binary Tree (easy; neetcode150, neetcode250, all)
    - LeetCode 687 Longest Univalue Path (medium; practice)
    - LeetCode 549 Binary Tree Longest Consecutive Sequence II (medium; all)
- **Cameras and covering (multi-state)**
    - LeetCode 968 Binary Tree Cameras (hard; practice)
    - LeetCode 1443 Minimum Time to Collect All Apples in a Tree (medium; all)
- **Largest BST and validity DP**
    - LeetCode 333 Largest BST Subtree (medium; all)
    - LeetCode 1373 Maximum Sum BST in Binary Tree (hard; practice)
- **Counting tree shapes (Catalan)**
    - LeetCode 96 Unique Binary Search Trees (medium; all)
    - LeetCode 95 Unique Binary Search Trees II (medium; all)
    - LeetCode 894 All Possible Full Binary Trees (medium; all)
- **Rerooting**
    - LeetCode 2858 Minimum Edge Reversals So Every Node Is Reachable (hard; practice)
    - LeetCode 3068 Find the Maximum Sum of Node Values (hard; all)
- **Diameter and depth merges**
    - LeetCode 543 Diameter of Binary Tree (easy; neetcode150, neetcode250, all)
    - LeetCode 1522 Diameter of N-Ary Tree (medium; all)
    - LeetCode 1245 Tree Diameter (medium; all)
    - LeetCode 1530 Number of Good Leaf Nodes Pairs (medium; all)

### 10. DAG and graph DP

- **Longest path and DP in topological order**
    - LeetCode 1857 Largest Color Value in a Directed Graph (hard; all)
    - LeetCode 2050 Parallel Courses III (hard; all)
    - LeetCode 329 Longest Increasing Path in a Matrix (hard; neetcode150, neetcode250, all)
- **Counting paths in a DAG or shortest-path graph**
    - LeetCode 1976 Number of Ways to Arrive at Destination (medium; all)
    - LeetCode 2328 Number of Increasing Paths in a Grid (hard; practice)
    - LeetCode 329 Longest Increasing Path in a Matrix (hard; neetcode150, neetcode250, all)
- **Shortest path with an edge-count dimension**
    - LeetCode 787 Cheapest Flights Within K Stops (medium; neetcode150, neetcode250, all)
- **Floyd-Warshall as DP**
    - LeetCode 1334 Find the City With the Smallest Number of Neighbors at a Threshold Distance (medium; all)
    - LeetCode 3620 Network Recovery Pathways (hard; practice)
- **Functional-graph DP**
    - LeetCode 2127 Maximum Employees to Be Invited to a Meeting (hard; all)

### 11. Bitmask DP

- **Bucket assignment by used-mask**
    - LeetCode 698 Partition to K Equal Sum Subsets (medium; neetcode250, all)
    - LeetCode 473 Matchsticks to Square (medium; neetcode250, all)
    - LeetCode 2305 Fair Distribution of Cookies (medium; practice)
    - LeetCode 1723 Find Minimum Time to Finish All Jobs (hard; practice)
- **Permutation DP over a mask**
    - LeetCode 526 Beautiful Arrangement (medium; practice)
    - LeetCode 996 Number of Squareful Arrays (hard; practice)
    - LeetCode 2850 Minimum Moves to Spread Stones Over Grid (medium; practice)
    - LeetCode 1255 Maximum Score Words Formed by Letters (hard; all)
- **Subset games and minimum sufficient sets**
    - LeetCode 464 Can I Win (medium; practice)
    - LeetCode 691 Stickers to Spell Word (hard; all)
    - LeetCode 465 Optimal Account Balancing (hard; all)
    - LeetCode 638 Shopping Offers (medium; practice)
- **Pairing DP (maximise score after n operations)**
    - LeetCode 1799 Maximize Score After N Operations (hard; all)
    - LeetCode 2002 Maximum Product of the Length of Two Palindromic Subsequences (medium; all)
- **Sets of distinct values as state**
    - LeetCode 898 Bitwise ORs of Subarrays (medium; practice)
    - LeetCode 351 Android Unlock Patterns (medium; all)
- **TSP and shortest path visiting all nodes**
    - no problem in the data: needs one from LeetCode
- **Sum over subsets (SOS) DP**
    - no problem in the data: needs one from LeetCode

### 12. Digit DP

- **Count numbers with a digit property**
    - LeetCode 357 Count Numbers with Unique Digits (medium; practice)
    - LeetCode 2376 Count Special Integers (hard; practice)
    - LeetCode 600 Non-negative Integers without Consecutive Ones (hard; practice)
    - LeetCode 788 Rotated Digits (medium; practice)
- **Digit DP with a tight flag over a range [L, R]**
    - no problem in the data: needs one from LeetCode

### 13. State machine DP

- **Stock trading states**
    - LeetCode 309 Best Time to Buy and Sell Stock with Cooldown (medium; neetcode150, neetcode250, all)
    - LeetCode 123 Best Time to Buy and Sell Stock III (hard; practice)
    - LeetCode 714 Best Time to Buy and Sell Stock with Transaction Fee (medium; practice)
    - LeetCode 3573 Best Time to Buy and Sell Stock V (medium; practice)
- **Alternating-sign subsequence and flip DP**
    - LeetCode 1911 Maximum Alternating Subsequence Sum (medium; all)
    - LeetCode 926 Flip String to Monotone Increasing (medium; all)
    - LeetCode 1653 Minimum Deletions to Make String Balanced (medium; all)
    - LeetCode 2712 Minimum Cost to Make All Characters Equal (medium; practice)
- **Colour and parity states**
    - LeetCode 3429 Paint House IV (medium; practice)
    - LeetCode 2786 Visit Array Positions to Maximize Score (medium; practice)
    - LeetCode 3509 Maximum Product of Subsequences With an Alternating Sum Equal to K (hard; practice)

### 14. Probability and expected value

- **Random-walk probability**
    - LeetCode 688 Knight Probability in Chessboard (medium; practice)
    - LeetCode 576 Out of Boundary Paths (medium; all)
- **Dice and sliding-window probability**
    - LeetCode 837 New 21 Game (medium; all)
    - LeetCode 1155 Number of Dice Rolls With Target Sum (medium; all)
- **Flow-style probability simulation**
    - LeetCode 799 Champagne Tower (medium; all)
- **Expected steps with absorbing states**
    - no problem in the data: needs one from LeetCode

### 15. Game and minimax DP

- **Both-ends game**
    - LeetCode 486 Predict the Winner (medium; practice)
    - LeetCode 877 Stone Game (medium; neetcode250, all)
    - LeetCode 1690 Stone Game VII (medium; practice)
    - LeetCode 1563 Stone Game V (hard; practice)
- **Take-k-items games**
    - LeetCode 1406 Stone Game III (hard; neetcode250, all)
    - LeetCode 1140 Stone Game II (medium; neetcode250, all)
    - LeetCode 877 Stone Game (medium; neetcode250, all)
- **Subset-state game**
    - LeetCode 464 Can I Win (medium; practice)
- **Win / lose / draw retrograde analysis on a graph**
    - no problem in the data: needs one from LeetCode

### 16. Counting DP

- **Counting by last state (adjacency rules)**
    - LeetCode 935 Knight Dialer (medium; all)
    - LeetCode 1220 Count Vowels Permutation (hard; all)
    - LeetCode 552 Student Attendance Record II (hard; all)
    - LeetCode 276 Paint Fence (medium; all)
- **Counting permutations by property**
    - LeetCode 629 K Inverse Pairs Array (hard; all)
    - LeetCode 920 Number of Music Playlists (hard; all)
    - LeetCode 1866 Number of Ways to Rearrange Sticks With K Sticks Visible (hard; all)
    - LeetCode 3193 Count the Number of Inversions (hard; practice)
- **Counting with a step budget**
    - LeetCode 1269 Number of Ways to Stay in the Same Place After Some Steps (hard; all)
    - LeetCode 2400 Number of Ways to Reach a Position After Exactly k Steps (medium; practice)
    - LeetCode 576 Out of Boundary Paths (medium; all)
    - LeetCode 3154 Find Number of Ways to Reach the K-th Stair (hard; practice)
- **Counting tilings**
    - LeetCode 790 Domino and Tromino Tiling (medium; practice)
    - LeetCode 2320 Count Number of Ways to Place Houses (medium; practice)
- **Counting dice and string constructions**
    - LeetCode 1155 Number of Dice Rolls With Target Sum (medium; all)
    - LeetCode 1639 Number of Ways to Form a Target String Given a Dictionary (hard; all)
    - LeetCode 2930 Number of Strings Which Can Be Rearranged to Contain Substring (medium; practice)
    - LeetCode 2466 Count Ways To Build Good Strings (medium; all)
- **Catalan-numbered structures**
    - LeetCode 1259 Handshakes That Don't Cross (hard; all)
    - LeetCode 96 Unique Binary Search Trees (medium; all)
    - LeetCode 894 All Possible Full Binary Trees (medium; all)
    - LeetCode 22 Generate Parentheses (medium; neetcode150, neetcode250, all)

### 17. Prefix-sum and monotonic-queue optimisation

- **Prefix sums in the transition**
    - LeetCode 837 New 21 Game (medium; all)
    - LeetCode 1871 Jump Game VII (medium; neetcode250, all)
    - LeetCode 689 Maximum Sum of 3 Non-Overlapping Subarrays (hard; all)
    - LeetCode 2902 Count of Sub-Multisets With Bounded Sum (hard; practice)
- **Sliding-window max / min in the transition**
    - LeetCode 1425 Constrained Subsequence Sum (hard; all)
    - LeetCode 1696 Jump Game VI (medium; practice)
    - LeetCode 3578 Count Partitions With Max-Min Difference at Most K (medium; practice)
    - LeetCode 918 Maximum Sum Circular Subarray (medium; neetcode250, all)
- **Monotonic stack contribution**
    - LeetCode 1856 Maximum Subarray Min-Product (medium; all)
    - LeetCode 907 Sum of Subarray Minimums (medium; all)
- **Index structure over values**
    - LeetCode 2407 Longest Increasing Subsequence II (hard; practice)
    - LeetCode 673 Number of Longest Increasing Subsequence (medium; all)
    - LeetCode 1964 Find the Longest Valid Obstacle Course at Each Position (hard; all)

### 18. Divide and conquer, Knuth and convex hull trick

- **Divide-and-conquer optimisation for k-partition DP**
    - LeetCode 410 Split Array Largest Sum (hard; neetcode250, all)
    - LeetCode 1335 Minimum Difficulty of a Job Schedule (hard; all)
    - LeetCode 1531 String Compression II (hard; all)
- **Convex hull trick and Li Chao tree**
    - no problem in the data: needs one from LeetCode
- **Knuth optimisation for interval DP**
    - no problem in the data: needs one from LeetCode
- **Aliens trick / slope trick**
    - no problem in the data: needs one from LeetCode

### 19. Matrix exponentiation

- **Linear recurrences with large n**
    - LeetCode 509 Fibonacci Number (easy; practice)
    - LeetCode 1137 N-th Tribonacci Number (easy; neetcode250, all)
    - LeetCode 935 Knight Dialer (medium; all)
    - LeetCode 1220 Count Vowels Permutation (hard; all)
- **Counting walks and automaton strings of length n**
    - LeetCode 552 Student Attendance Record II (hard; all)
    - LeetCode 2400 Number of Ways to Reach a Position After Exactly k Steps (medium; practice)
    - LeetCode 3154 Find Number of Ways to Reach the K-th Stair (hard; practice)
- **Min-plus matrix power**
    - no problem in the data: needs one from LeetCode

### 20. Space optimisation

- **Rolling rows and one-row DP**
    - LeetCode 62 Unique Paths (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 64 Minimum Path Sum (medium; neetcode250, all)
    - LeetCode 1143 Longest Common Subsequence (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 72 Edit Distance (medium; neetcode150, neetcode250, all)
- **Capacity loop direction**
    - LeetCode 416 Partition Equal Subset Sum (medium; neetcode150, neetcode250, all)
    - LeetCode 322 Coin Change (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 518 Coin Change II (medium; neetcode150, neetcode250, all)
- **O(1) variables for a k-step recurrence**
    - LeetCode 70 Climbing Stairs (easy; blind75, neetcode150, neetcode250, all)
    - LeetCode 198 House Robber (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 1137 N-th Tribonacci Number (easy; neetcode250, all)

### 21. Memoisation versus tabulation

- **Top-down memo on a sparse state space**
    - LeetCode 329 Longest Increasing Path in a Matrix (hard; neetcode150, neetcode250, all)
    - LeetCode 1594 Maximum Non Negative Product in a Matrix (medium; practice)
    - LeetCode 3040 Maximum Number of Operations With the Same Score II (medium; practice)
    - LeetCode 2311 Longest Binary Subsequence Less Than or Equal to K (medium; practice)
- **Memoised recursion on integers**
    - LeetCode 397 Integer Replacement (medium; practice)
    - LeetCode 1387 Sort Integers by The Power Value (medium; practice)
    - LeetCode 1553 Minimum Number of Days to Eat N Oranges (hard; all)
    - LeetCode 1611 Minimum One Bit Operations to Make Integers Zero (hard; all)
- **BFS over states versus DP**
    - LeetCode 322 Coin Change (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 279 Perfect Squares (medium; neetcode250, all)
    - LeetCode 1553 Minimum Number of Days to Eat N Oranges (hard; all)
    - LeetCode 2998 Minimum Number of Operations to Make X and Y Equal (medium; practice)

### 22. Reconstruction

- **Reconstruct the sequence**
    - LeetCode 300 Longest Increasing Subsequence (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 368 Largest Divisible Subset (medium; all)
    - LeetCode 1092 Shortest Common Supersequence (hard; all)
- **Enumerate all solutions with memoised results**
    - LeetCode 140 Word Break II (hard; neetcode250, all)
    - LeetCode 95 Unique Binary Search Trees II (medium; all)
    - LeetCode 131 Palindrome Partitioning (medium; neetcode150, neetcode250, all)
- **Path / choice reconstruction**
    - LeetCode 656 Coin Path (hard; all)
    - LeetCode 72 Edit Distance (medium; neetcode150, neetcode250, all)

### 23. Constrained subsequences

- **Gap and difference constraints**
    - LeetCode 1425 Constrained Subsequence Sum (hard; all)
    - LeetCode 1696 Jump Game VI (medium; practice)
    - LeetCode 1218 Longest Arithmetic Subsequence of Given Difference (medium; practice)
- **At most k changes between neighbours**
    - LeetCode 3176 Find the Maximum Length of a Good Subsequence I (medium; practice)
    - LeetCode 2370 Longest Ideal Subsequence (medium; all)
- **Matching a target as a subsequence**
    - LeetCode 115 Distinct Subsequences (hard; neetcode150, neetcode250, all)
    - LeetCode 792 Number of Matching Subsequences (medium; practice)
    - LeetCode 392 Is Subsequence (easy; all)
    - LeetCode 2311 Longest Binary Subsequence Less Than or Equal to K (medium; practice)
- **Choose from two arrays per position**
    - LeetCode 2771 Longest Non-decreasing Subarray From Two Arrays (medium; practice)
    - LeetCode 1626 Best Team With No Conflicts (medium; all)

### 24. Broken profile and tiling DP

- **Tiling by frontier mask**
    - LeetCode 790 Domino and Tromino Tiling (medium; practice)
- **Row-mask compatibility DP**
    - no problem in the data: needs one from LeetCode
- **Plug DP and Steiner tree on grids**
    - no problem in the data: needs one from LeetCode

## Gaps

- 13 of 120 patterns above have no problem in the data and need one picked from LeetCode and checked there, never from memory: Row-mask compatibility DP (group 24); Plug DP and Steiner tree on grids (group 24); Convex hull trick and Li Chao tree (group 18); Knuth optimisation for interval DP (group 18); Aliens trick / slope trick (group 18); Digit DP with a tight flag over a range [L, R] (group 12); Expected steps with absorbing states (group 14); TSP and shortest path visiting all nodes (group 11); Sum over subsets (SOS) DP (group 11); Win / lose / draw retrograde analysis on a graph (group 15); Min-plus matrix power (group 19); LIS over a circular array (group 4); Matrix chain and polygon triangulation (group 6).
- Groups with no or very few problems in the data: digit DP (12), probability and expected value (14), divide and conquer / Knuth / convex hull trick (18), matrix exponentiation (19), broken profile (24).
- The two DP topics have 17 must-learn problems (5, 70, 139, 152, 198, 300, 322, 62, 1143, 416, 309, 312, 329, 1406, 935, 1105, 873). None belongs to: edit distance and regex matching (5), palindromic subsequences (7), tree DP and DAG DP (9, 10: those live in Trees and Graphs), bitmask DP (11), digit DP (12), probability (14), the optimisation techniques (17, 18), matrix exponentiation (19), reconstruction (22) or broken profile (24). They are lessons with LeetCode example problems only (decision 32).
- Several lines above are borrowed from other topics (stack, heap, sliding window, graphs, trees) because the idea is a DP idea there too; each is marked only by its lists, so check the topic before adding a card.
- A few lines show a problem whose DP use is optional (a greedy or binary-search answer exists, for example 55 Jump Game); the lesson should say so rather than force the DP.
- Open before building: where the extra patterns sit (more techniques inside the two topics, or new groups such as "Optimisations" and "Bitmask and profile"), how the tabs look (needs a mockup, rule 13), and which topic a cross-cutting pattern (knapsack, LCS, state machine) belongs to when it appears as both 1-D and 2-D.
