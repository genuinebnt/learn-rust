# Backtracking patterns: the exhaustive target list

Every backtracking pattern that can come up on LeetCode, as the target for the Backtracking pattern lessons, in the format of [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md). The rule is in [DSA.md](DSA.md), decision 32: a topic's patterns section is exhaustive, patterns without a NeetCode problem get **example problems** from LeetCode, and variants of one pattern (used array / swap in place) are **tabs** of one lesson.

Status: documented only. Today `content/dsa/lessons/backtracking.toml` has 9 techniques (include-exclude, reuse, skip-dups, permute, construct, grid, partition-k, n-queens, split-memo). Building the rest needs a mockup of the tabs first, then lessons and picked example problems. Several groups below (bitmask, game-tree, path enumeration in trees and graphs, the DP boundary) overlap lessons that already live in other topics; whether those lessons are linked or duplicated is an open question (see Gaps).

Items written *a / b* in a group are variants for tabs where one lesson covers both (for example "Permutations: used array / swap in place"). Each item is one lesson; the numbering (1.1, 1.2, ...) is used again in the example list below.

1. **Subsets, combinations and permutations.** Subsets: include-or-skip recursion / start-index loop; Subsets and subsequences with duplicates: sort and skip / per-level seen set; Combinations of k items: fixed size with a "enough items left" bound; Combination sum: reuse allowed / each item once with duplicates / exactly k numbers; Permutations: used array / swap in place; Permutations with duplicates: sort and skip / count map; Arrangements of a multiset of any length / partial permutations of k items; Best-subset search: take / skip with a running feasibility state.
2. **Constraint satisfaction.** N-Queens: column and diagonal sets / bitmasks, enumerate or count; Sudoku: row, column and box sets, most-constrained cell first; Position-value assignment: divisibility and adjacency rules; Truth and consistency assignment: each item in or out, checked against claims; Board placement and tiling; Layered construction from a local rule table: build level by level (pyramids, row tilings); Colouring and group assignment under conflicts; Constraint propagation: forward checking / most-constrained variable / arc consistency; Exact cover: Algorithm X / dancing links; Verbal arithmetic and digit puzzles.
3. **Partitioning.** Palindrome partitioning: all cuts / precomputed palindrome table; Split a string into numbers under a rule: additive / Fibonacci / descending, no leading zeros; Split into distinct pieces, maximise the count; Equal-sum groups: item to bucket / bucket takes items (bitmask); Dictionary splits: every sentence, with memo; Split at an operator: every parenthesisation, split-and-combine with memo; Split into parts whose sum matches a target; Split into two halves with a balance goal; Fewest pieces: backtracking with memo, then DP.
4. **String generation.** Balanced parentheses: open / close counters; Remove invalid parentheses: minimum removals, level BFS / DFS with dedupe; One choice per position: phone letters / letter case / brace expansion; Segmented numeric strings: IP addresses / coordinates; Expression building: insert operators with the carried operand / combine pairs; Digit-by-digit numbers: digit constraints / strobogrammatic / consecutive differences; The k-th string in order: count branches and skip / stop at the k-th; Sequences under structural rules: DI patterns / no adjacent zeros / nested placement; Mappings and substitutions: bijective pattern / synonym expansion; Covering sequences: De Bruijn / cracking the safe.
5. **Grid and word search with visited state.** Word search: in-place mark / visited set; Many words: trie-guided search that prunes exhausted branches; Best path from any start: maximum gold / longest self-avoiding path; Cover every cell: Hamiltonian grid paths; Exploring an unknown map with physical undo: robot, interactive; Visited state: per-path with undo / global (flood) / bitmask / memoised DFS; Knight tours, self-avoiding walks, maze path counting.
6. **Path enumeration in graphs and trees.** Root-to-leaf paths: path list with pop / string passed by value; All paths in a DAG: no visited set needed; All simple paths in a general graph: per-path visited, length and target limits; All shortest paths: BFS layers, then DFS reconstruction; Eulerian trail by backtracking / Hierholzer; Generating all trees: all BSTs / all full binary trees; Path counting with carried sums: prefix-sum map with undo; Cycle, clique and connected-subgraph enumeration.
7. **Pruning techniques.** Sort and skip an equal value at the same depth; Sorted break: stop the loop at the first candidate that is too big; Feasibility bounds: not enough items left, suffix sums, remaining target; Symmetry breaking: interchangeable buckets, mirrored halves; Fail-first ordering: largest first / most-constrained variable; Memoised backtracking: state key (index, remaining) / (mask); Search goal: first solution / count only / enumerate all / best so far; Pre-checks before searching: divisibility, largest item, parity.
8. **Bitmask state.** Used set as an integer mask, memo over the mask; Enumerate every mask and test it; Column and diagonal masks: N-Queens bit tricks; Assignment by mask and position; Game state as a mask; Submask enumeration: groups drawn from a subset of a subset; Multiset counts as the state key.
9. **Meet in the middle.** Two halves: enumerate each half, sort, two pointers (balanced split); Closest to a target / count subsets with a given sum; k-sum by pairs: hash the pair sums; Bidirectional search on a state space.
10. **Iterative generation.** Next permutation / previous permutation; k-th permutation: factorial number system; Gray code: reflection / i xor (i >> 1); Next combination / subsets by counting masks (Gosper's hack); Lexicographic order walks: iterative number-trie DFS with branch counting; Minimal-change permutations: Heap's algorithm / Steinhaus-Johnson-Trotter; Lazy generation: iterators and generators over combinations.
11. **Branch and bound and search order.** Branch and bound: cut on best-so-far with an optimistic bound; Iterative deepening / depth-limited search; A* / IDA* with an admissible heuristic; Value ordering and incumbent seeding: greedy first, then improve; Relaxation bounds for TSP-style problems: MST / assignment bound.
12. **Game-tree search.** Minimax with memo: (mask, remaining) / (left, right); Alpha-beta pruning and move ordering; When the search collapses: parity and counting arguments.
13. **Backtracking versus DP boundary.** Count / exists / optimise with a repeating state: memoise, then tabulate; Enumerate every answer: output-bound, so backtracking stays; Same recursion, enumerate versus count; Search over values instead of choices: bitset subset sum / knapsack; Closed form instead of search: combinatorics and digit counting.
14. **Core implementation patterns.** choose / explore / un-choose, with every change paired with its undo; record a copy of the path (a shared list keeps changing); state passed by value (a string, a tuple) versus mutated state with an undo; used array / set / mask: which one, and when each is cheap; in-place mark and restore for grid cells; start index: what turns permutations into combinations; a per-level seen set (not a global one) for duplicates; early exit: returning a bool and propagating it up the call chain; a global counter or best-so-far (nonlocal) for count-only and optimisation search; sort once at the start, and keep the order stable for the skip rules; generators (yield) for lazy enumeration; an explicit stack for iterative backtracking, and the recursion-depth limit; output-size reasoning: the answer count is the lower bound on the work.

## Coverage today

Technique lessons in `content/dsa/lessons/backtracking.toml`, with the problems the data files file under each (problems.json and practice.json together):

- `Backtracking:include-exclude` (Include or exclude choices): 17 problems filed; must-learn: LeetCode 78 Subsets.
- `Backtracking:reuse` (Choices that can repeat, with a start index): 6 problems filed; must-learn: LeetCode 39 Combination Sum.
- `Backtracking:skip-dups` (Skipping duplicates at the same level): 7 problems filed; must-learn: LeetCode 40 Combination Sum II.
- `Backtracking:permute` (Permutations with a used set): 6 problems filed; must-learn: LeetCode 46 Permutations.
- `Backtracking:construct` (Building a valid sequence under a rule): 10 problems filed; must-learn: LeetCode 22 Generate Parentheses.
- `Backtracking:grid` (Backtracking on a grid): 3 problems filed; must-learn: LeetCode 79 Word Search.
- `Backtracking:partition-k` (Partitioning into K equal groups): 6 problems filed; must-learn: LeetCode 473 Matchsticks to Square.
- `Backtracking:n-queens` (Constraint sets for placement): 3 problems filed; must-learn: LeetCode 51 N-Queens.
- `Backtracking:split-memo` (Splitting with a memoized DFS): 6 problems filed; must-learn: LeetCode 140 Word Break II.

Problems filed under the Backtracking pattern: 63 (36 in problems.json, 27 in practice.json). Problems tagged Backtracking that are filed under another topic: 18.

Against the 91 patterns in groups 1 to 13:

- **covered** (12): a technique above is the lesson, possibly without every variant tab.
- **partial** (16): a technique's template touches the pattern but not its signals, variants or pitfalls.
- **elsewhere** (23): the problems are filed under a lesson of another topic (Trees, Graphs, 1-D Dynamic Programming, ...); the Backtracking lesson would link or restate it.
- **none** (40): no lesson anywhere.

Per pattern (status, then the technique ids that hold it):

- 1.1 Subsets: partial (`Backtracking:include-exclude`)
- 1.2 Subsets and subsequences with duplicates: partial (`Backtracking:skip-dups`)
- 1.3 Combinations of k items: partial (`Backtracking:include-exclude`)
- 1.4 Combination sum: covered (`Backtracking:reuse`, `Backtracking:skip-dups`)
- 1.5 Permutations: covered (`Backtracking:permute`)
- 1.6 Permutations with duplicates: partial (`Backtracking:skip-dups`)
- 1.7 Arrangements of a multiset of any length / partial permutations of k items: none
- 1.8 Best-subset search: partial (`Backtracking:include-exclude`)
- 2.1 N-Queens: covered (`Backtracking:n-queens`)
- 2.2 Sudoku: none
- 2.3 Position-value assignment: none
- 2.4 Truth and consistency assignment: none
- 2.5 Board placement and tiling: none
- 2.6 Layered construction from a local rule table: none
- 2.7 Colouring and group assignment under conflicts: none
- 2.8 Constraint propagation: none
- 2.9 Exact cover: none
- 2.10 Verbal arithmetic and digit puzzles: none
- 3.1 Palindrome partitioning: partial (`Backtracking:include-exclude`)
- 3.2 Split a string into numbers under a rule: none
- 3.3 Split into distinct pieces, maximise the count: none
- 3.4 Equal-sum groups: covered (`Backtracking:partition-k`)
- 3.5 Dictionary splits: covered (`Backtracking:split-memo`)
- 3.6 Split at an operator: partial (`Backtracking:split-memo`)
- 3.7 Split into parts whose sum matches a target: none
- 3.8 Split into two halves with a balance goal: none
- 3.9 Fewest pieces: none
- 4.1 Balanced parentheses: covered (`Backtracking:construct`)
- 4.2 Remove invalid parentheses: none
- 4.3 One choice per position: partial (`Backtracking:construct`)
- 4.4 Segmented numeric strings: none
- 4.5 Expression building: none
- 4.6 Digit-by-digit numbers: partial (`Backtracking:construct`)
- 4.7 The k-th string in order: none
- 4.8 Sequences under structural rules: partial (`Backtracking:construct`)
- 4.9 Mappings and substitutions: none
- 4.10 Covering sequences: none
- 5.1 Word search: covered (`Backtracking:grid`)
- 5.2 Many words: elsewhere (`Tries:trie-grid`)
- 5.3 Best path from any start: elsewhere (`Graphs:flood`)
- 5.4 Cover every cell: none
- 5.5 Exploring an unknown map with physical undo: none
- 5.6 Visited state: partial (`Backtracking:grid`)
- 5.7 Knight tours, self-avoiding walks, maze path counting: none
- 6.1 Root-to-leaf paths: elsewhere (`Trees:dfs-carry`)
- 6.2 All paths in a DAG: elsewhere (`Graphs:topo`)
- 6.3 All simple paths in a general graph: none
- 6.4 All shortest paths: elsewhere (`Graphs:bfs-implicit`)
- 6.5 Eulerian trail by backtracking / Hierholzer: elsewhere (`Advanced Graphs:euler`)
- 6.6 Generating all trees: elsewhere (`Trees:catalan`)
- 6.7 Path counting with carried sums: elsewhere (`Trees:dfs-carry`)
- 6.8 Cycle, clique and connected-subgraph enumeration: none
- 7.1 Sort and skip an equal value at the same depth: covered (`Backtracking:skip-dups`)
- 7.2 Sorted break: covered (`Backtracking:reuse`)
- 7.3 Feasibility bounds: partial (`Backtracking:partition-k`)
- 7.4 Symmetry breaking: covered (`Backtracking:partition-k`)
- 7.5 Fail-first ordering: covered (`Backtracking:partition-k`)
- 7.6 Memoised backtracking: covered (`Backtracking:split-memo`)
- 7.7 Search goal: partial (`Backtracking:grid`)
- 7.8 Pre-checks before searching: partial (`Backtracking:partition-k`)
- 8.1 Used set as an integer mask, memo over the mask: elsewhere (`1-D Dynamic Programming:bitmask`)
- 8.2 Enumerate every mask and test it: none
- 8.3 Column and diagonal masks: none
- 8.4 Assignment by mask and position: elsewhere (`1-D Dynamic Programming:bitmask`)
- 8.5 Game state as a mask: elsewhere (`1-D Dynamic Programming:bitmask`)
- 8.6 Submask enumeration: none
- 8.7 Multiset counts as the state key: none
- 9.1 Two halves: none
- 9.2 Closest to a target / count subsets with a given sum: none
- 9.3 k-sum by pairs: elsewhere (`Two Pointers:ksum`)
- 9.4 Bidirectional search on a state space: elsewhere (`Graphs:bfs-implicit`)
- 10.1 Next permutation / previous permutation: elsewhere (`Greedy:swap-greedy`)
- 10.2 k-th permutation: elsewhere (`Math & Geometry:fast-pow`)
- 10.3 Gray code: partial (`Backtracking:include-exclude`)
- 10.4 Next combination / subsets by counting masks (Gosper's hack): none
- 10.5 Lexicographic order walks: elsewhere (`Math & Geometry:lex-order`)
- 10.6 Minimal-change permutations: none
- 10.7 Lazy generation: none
- 11.1 Branch and bound: none
- 11.2 Iterative deepening / depth-limited search: none
- 11.3 A* / IDA* with an admissible heuristic: elsewhere (`Graphs:bfs-implicit`)
- 11.4 Value ordering and incumbent seeding: none
- 11.5 Relaxation bounds for TSP-style problems: none
- 12.1 Minimax with memo: elsewhere (`1-D Dynamic Programming:game`)
- 12.2 Alpha-beta pruning and move ordering: none
- 12.3 When the search collapses: elsewhere (`Greedy:count-greedy`)
- 13.1 Count / exists / optimise with a repeating state: elsewhere (`1-D Dynamic Programming:subset`)
- 13.2 Enumerate every answer: partial (`Backtracking:split-memo`)
- 13.3 Same recursion, enumerate versus count: elsewhere (`1-D Dynamic Programming:recurrence`)
- 13.4 Search over values instead of choices: elsewhere (`1-D Dynamic Programming:subset`)
- 13.5 Closed form instead of search: elsewhere (`2-D Dynamic Programming:grid-dp`)

## Example problems per pattern

Taken only from `content/dsa/problems.json` and `content/dsa/practice.json`, at most four per pattern, as `LeetCode <number> <title> (<difficulty>; <lists>)`. A pattern with nothing in the data says so: a problem for it has to be picked from LeetCode and checked there, never from memory. A problem marked premium is a LeetCode premium problem (the `premium` field of the data); prefer a free one when a lesson picks its final examples. The "practice" list is the extra problems of practice.json; "all" is every problem of problems.json. A problem can serve more than one pattern.

### 1. Subsets, combinations and permutations

**1.1 Subsets: include-or-skip recursion / start-index loop**

- LeetCode 78 Subsets (medium; neetcode150, neetcode250, all)
- LeetCode 1863 Sum of All Subset XOR Totals (easy; neetcode250, all)
- LeetCode 2044 Count Number of Maximum Bitwise-OR Subsets (medium; all)

**1.2 Subsets and subsequences with duplicates: sort and skip / per-level seen set**

- LeetCode 90 Subsets II (medium; neetcode150, neetcode250, all)
- LeetCode 491 Non-decreasing Subsequences (medium; practice)

**1.3 Combinations of k items: fixed size with a "enough items left" bound**

- LeetCode 77 Combinations (medium; neetcode250, all)
- LeetCode 401 Binary Watch (easy; practice)

**1.4 Combination sum: reuse allowed / each item once with duplicates / exactly k numbers**

- LeetCode 39 Combination Sum (medium; blind75, neetcode150, neetcode250, all)
- LeetCode 40 Combination Sum II (medium; neetcode150, neetcode250, all)
- LeetCode 216 Combination Sum III (medium; practice)
- LeetCode 254 Factor Combinations (medium; all; premium)

**1.5 Permutations: used array / swap in place**

- LeetCode 46 Permutations (medium; neetcode150, neetcode250, all)
- LeetCode 2850 Minimum Moves to Spread Stones Over Grid (medium; practice)

**1.6 Permutations with duplicates: sort and skip / count map**

- LeetCode 47 Permutations II (medium; neetcode250, all)
- LeetCode 996 Number of Squareful Arrays (hard; practice)

**1.7 Arrangements of a multiset of any length / partial permutations of k items**

- LeetCode 1079 Letter Tile Possibilities (medium; all)
- LeetCode 2048 Next Greater Numerically Balanced Number (medium; practice)

**1.8 Best-subset search: take / skip with a running feasibility state**

- LeetCode 1239 Maximum Length of a Concatenated String with Unique Characters (medium; all)
- LeetCode 1255 Maximum Score Words Formed by Letters (hard; all)
- LeetCode 2597 The Number of Beautiful Subsets (medium; all)

### 2. Constraint satisfaction

**2.1 N-Queens: column and diagonal sets / bitmasks, enumerate or count**

- LeetCode 51 N-Queens (hard; neetcode150, neetcode250, all)
- LeetCode 52 N-Queens II (hard; neetcode250, all)

**2.2 Sudoku: row, column and box sets, most-constrained cell first**

- LeetCode 37 Sudoku Solver (hard; practice)
- LeetCode 36 Valid Sudoku (medium; neetcode150, neetcode250, all)

**2.3 Position-value assignment: divisibility and adjacency rules**

- LeetCode 526 Beautiful Arrangement (medium; practice)
- LeetCode 1718 Construct the Lexicographically Largest Valid Sequence (medium; all)

**2.4 Truth and consistency assignment: each item in or out, checked against claims**

- LeetCode 2151 Maximum Good People Based on Statements (hard; practice)
- LeetCode 2397 Maximum Rows Covered by Columns (medium; practice)

**2.5 Board placement and tiling**

- LeetCode 1240 Tiling a Rectangle with the Fewest Squares (hard; practice)

**2.6 Layered construction from a local rule table: build level by level (pyramids, row tilings)**

- LeetCode 756 Pyramid Transition Matrix (medium; practice)

**2.7 Colouring and group assignment under conflicts**

- LeetCode 886 Possible Bipartition (medium; practice)
- LeetCode 785 Is Graph Bipartite? (medium; all)

**2.8 Constraint propagation: forward checking / most-constrained variable / arc consistency**

- LeetCode 37 Sudoku Solver (hard; practice)

**2.9 Exact cover: Algorithm X / dancing links**

- LeetCode 37 Sudoku Solver (hard; practice)
- LeetCode 51 N-Queens (hard; neetcode150, neetcode250, all)
- LeetCode 52 N-Queens II (hard; neetcode250, all)

**2.10 Verbal arithmetic and digit puzzles**

- no problem in the data: needs one from LeetCode

### 3. Partitioning

**3.1 Palindrome partitioning: all cuts / precomputed palindrome table**

- LeetCode 131 Palindrome Partitioning (medium; neetcode150, neetcode250, all)

**3.2 Split a string into numbers under a rule: additive / Fibonacci / descending, no leading zeros**

- LeetCode 306 Additive Number (medium; practice)
- LeetCode 842 Split Array into Fibonacci Sequence (medium; practice)
- LeetCode 1849 Splitting a String Into Descending Consecutive Values (medium; all)

**3.3 Split into distinct pieces, maximise the count**

- LeetCode 1593 Split a String Into the Max Number of Unique Substrings (medium; all)

**3.4 Equal-sum groups: item to bucket / bucket takes items (bitmask)**

- LeetCode 698 Partition to K Equal Sum Subsets (medium; neetcode250, all)
- LeetCode 473 Matchsticks to Square (medium; neetcode250, all)
- LeetCode 2305 Fair Distribution of Cookies (medium; practice)
- LeetCode 1723 Find Minimum Time to Finish All Jobs (hard; practice)

**3.5 Dictionary splits: every sentence, with memo**

- LeetCode 140 Word Break II (hard; neetcode250, all)

**3.6 Split at an operator: every parenthesisation, split-and-combine with memo**

- LeetCode 241 Different Ways to Add Parentheses (medium; all)

**3.7 Split into parts whose sum matches a target**

- LeetCode 2698 Find the Punishment Number of an Integer (medium; all)

**3.8 Split into two halves with a balance goal**

- LeetCode 2035 Partition Array Into Two Arrays to Minimize Sum Difference (hard; practice)
- LeetCode 805 Split Array With Same Average (hard; all)
- LeetCode 2002 Maximum Product of the Length of Two Palindromic Subsequences (medium; all)

**3.9 Fewest pieces: backtracking with memo, then DP**

- LeetCode 2767 Partition String Into Minimum Beautiful Substrings (medium; practice)

### 4. String generation

**4.1 Balanced parentheses: open / close counters**

- LeetCode 22 Generate Parentheses (medium; neetcode150, neetcode250, all)

**4.2 Remove invalid parentheses: minimum removals, level BFS / DFS with dedupe**

- LeetCode 301 Remove Invalid Parentheses (hard; practice)

**4.3 One choice per position: phone letters / letter case / brace expansion**

- LeetCode 17 Letter Combinations of a Phone Number (medium; neetcode150, neetcode250, all)
- LeetCode 784 Letter Case Permutation (medium; practice)
- LeetCode 1087 Brace Expansion (medium; all; premium)
- LeetCode 1096 Brace Expansion II (hard; practice)

**4.4 Segmented numeric strings: IP addresses / coordinates**

- LeetCode 93 Restore IP Addresses (medium; all)
- LeetCode 816 Ambiguous Coordinates (medium; practice)

**4.5 Expression building: insert operators with the carried operand / combine pairs**

- LeetCode 282 Expression Add Operators (hard; practice)
- LeetCode 679 24 Game (hard; practice)

**4.6 Digit-by-digit numbers: digit constraints / strobogrammatic / consecutive differences**

- LeetCode 247 Strobogrammatic Number II (medium; all; premium)
- LeetCode 967 Numbers With Same Consecutive Differences (medium; practice)
- LeetCode 1291 Sequential Digits (medium; all)
- LeetCode 357 Count Numbers with Unique Digits (medium; practice)

**4.7 The k-th string in order: count branches and skip / stop at the k-th**

- LeetCode 1415 The k-th Lexicographical String of All Happy Strings of Length n (medium; all)
- LeetCode 1980 Find Unique Binary String (medium; all)

**4.8 Sequences under structural rules: DI patterns / no adjacent zeros / nested placement**

- LeetCode 2375 Construct Smallest Number From DI String (medium; all)
- LeetCode 3211 Generate Binary Strings Without Adjacent Zeros (medium; practice)
- LeetCode 1718 Construct the Lexicographically Largest Valid Sequence (medium; all)

**4.9 Mappings and substitutions: bijective pattern / synonym expansion**

- LeetCode 291 Word Pattern II (medium; all; premium)
- LeetCode 1258 Synonymous Sentences (medium; all; premium)

**4.10 Covering sequences: De Bruijn / cracking the safe**

- no problem in the data: needs one from LeetCode

### 5. Grid and word search with visited state

**5.1 Word search: in-place mark / visited set**

- LeetCode 79 Word Search (medium; blind75, neetcode150, neetcode250, all)

**5.2 Many words: trie-guided search that prunes exhausted branches**

- LeetCode 212 Word Search II (hard; blind75, neetcode150, neetcode250, all)

**5.3 Best path from any start: maximum gold / longest self-avoiding path**

- LeetCode 1219 Path with Maximum Gold (medium; all)

**5.4 Cover every cell: Hamiltonian grid paths**

- LeetCode 980 Unique Paths III (hard; practice)

**5.5 Exploring an unknown map with physical undo: robot, interactive**

- LeetCode 489 Robot Room Cleaner (hard; all; premium)

**5.6 Visited state: per-path with undo / global (flood) / bitmask / memoised DFS**

- LeetCode 79 Word Search (medium; blind75, neetcode150, neetcode250, all)
- LeetCode 200 Number of Islands (medium; blind75, neetcode150, neetcode250, all)
- LeetCode 695 Max Area of Island (medium; neetcode150, neetcode250, all)
- LeetCode 329 Longest Increasing Path in a Matrix (hard; neetcode150, neetcode250, all)

**5.7 Knight tours, self-avoiding walks, maze path counting**

- no problem in the data: needs one from LeetCode

### 6. Path enumeration in graphs and trees

**6.1 Root-to-leaf paths: path list with pop / string passed by value**

- LeetCode 257 Binary Tree Paths (easy; practice)
- LeetCode 113 Path Sum II (medium; practice)
- LeetCode 988 Smallest String Starting From Leaf (medium; all)
- LeetCode 1457 Pseudo-Palindromic Paths in a Binary Tree (medium; all)

**6.2 All paths in a DAG: no visited set needed**

- LeetCode 797 All Paths From Source to Target (medium; practice)

**6.3 All simple paths in a general graph: per-path visited, length and target limits**

- no problem in the data: needs one from LeetCode

**6.4 All shortest paths: BFS layers, then DFS reconstruction**

- LeetCode 126 Word Ladder II (hard; practice)

**6.5 Eulerian trail by backtracking / Hierholzer**

- LeetCode 332 Reconstruct Itinerary (hard; neetcode150, neetcode250, all)

**6.6 Generating all trees: all BSTs / all full binary trees**

- LeetCode 95 Unique Binary Search Trees II (medium; all)
- LeetCode 894 All Possible Full Binary Trees (medium; all)

**6.7 Path counting with carried sums: prefix-sum map with undo**

- LeetCode 437 Path Sum III (medium; practice)
- LeetCode 112 Path Sum (easy; all)

**6.8 Cycle, clique and connected-subgraph enumeration**

- no problem in the data: needs one from LeetCode

### 7. Pruning techniques

**7.1 Sort and skip an equal value at the same depth**

- LeetCode 40 Combination Sum II (medium; neetcode150, neetcode250, all)
- LeetCode 47 Permutations II (medium; neetcode250, all)
- LeetCode 90 Subsets II (medium; neetcode150, neetcode250, all)
- LeetCode 996 Number of Squareful Arrays (hard; practice)

**7.2 Sorted break: stop the loop at the first candidate that is too big**

- LeetCode 39 Combination Sum (medium; blind75, neetcode150, neetcode250, all)
- LeetCode 40 Combination Sum II (medium; neetcode150, neetcode250, all)
- LeetCode 216 Combination Sum III (medium; practice)

**7.3 Feasibility bounds: not enough items left, suffix sums, remaining target**

- LeetCode 77 Combinations (medium; neetcode250, all)
- LeetCode 698 Partition to K Equal Sum Subsets (medium; neetcode250, all)
- LeetCode 2305 Fair Distribution of Cookies (medium; practice)

**7.4 Symmetry breaking: interchangeable buckets, mirrored halves**

- LeetCode 698 Partition to K Equal Sum Subsets (medium; neetcode250, all)
- LeetCode 473 Matchsticks to Square (medium; neetcode250, all)
- LeetCode 1723 Find Minimum Time to Finish All Jobs (hard; practice)
- LeetCode 51 N-Queens (hard; neetcode150, neetcode250, all)

**7.5 Fail-first ordering: largest first / most-constrained variable**

- LeetCode 473 Matchsticks to Square (medium; neetcode250, all)
- LeetCode 698 Partition to K Equal Sum Subsets (medium; neetcode250, all)
- LeetCode 1723 Find Minimum Time to Finish All Jobs (hard; practice)
- LeetCode 37 Sudoku Solver (hard; practice)

**7.6 Memoised backtracking: state key (index, remaining) / (mask)**

- LeetCode 140 Word Break II (hard; neetcode250, all)
- LeetCode 698 Partition to K Equal Sum Subsets (medium; neetcode250, all)
- LeetCode 691 Stickers to Spell Word (hard; all)
- LeetCode 241 Different Ways to Add Parentheses (medium; all)

**7.7 Search goal: first solution / count only / enumerate all / best so far**

- LeetCode 79 Word Search (medium; blind75, neetcode150, neetcode250, all)
- LeetCode 52 N-Queens II (hard; neetcode250, all)
- LeetCode 51 N-Queens (hard; neetcode150, neetcode250, all)
- LeetCode 1255 Maximum Score Words Formed by Letters (hard; all)

**7.8 Pre-checks before searching: divisibility, largest item, parity**

- LeetCode 698 Partition to K Equal Sum Subsets (medium; neetcode250, all)
- LeetCode 473 Matchsticks to Square (medium; neetcode250, all)
- LeetCode 805 Split Array With Same Average (hard; all)

### 8. Bitmask state

**8.1 Used set as an integer mask, memo over the mask**

- LeetCode 691 Stickers to Spell Word (hard; all)
- LeetCode 1799 Maximize Score After N Operations (hard; all)
- LeetCode 2002 Maximum Product of the Length of Two Palindromic Subsequences (medium; all)

**8.2 Enumerate every mask and test it**

- LeetCode 2397 Maximum Rows Covered by Columns (medium; practice)
- LeetCode 2151 Maximum Good People Based on Statements (hard; practice)
- LeetCode 2002 Maximum Product of the Length of Two Palindromic Subsequences (medium; all)
- LeetCode 1255 Maximum Score Words Formed by Letters (hard; all)

**8.3 Column and diagonal masks: N-Queens bit tricks**

- LeetCode 51 N-Queens (hard; neetcode150, neetcode250, all)
- LeetCode 52 N-Queens II (hard; neetcode250, all)

**8.4 Assignment by mask and position**

- LeetCode 526 Beautiful Arrangement (medium; practice)
- LeetCode 2850 Minimum Moves to Spread Stones Over Grid (medium; practice)
- LeetCode 1799 Maximize Score After N Operations (hard; all)
- LeetCode 351 Android Unlock Patterns (medium; all; premium)

**8.5 Game state as a mask**

- LeetCode 464 Can I Win (medium; practice)

**8.6 Submask enumeration: groups drawn from a subset of a subset**

- LeetCode 698 Partition to K Equal Sum Subsets (medium; neetcode250, all)
- LeetCode 2305 Fair Distribution of Cookies (medium; practice)

**8.7 Multiset counts as the state key**

- LeetCode 691 Stickers to Spell Word (hard; all)

### 9. Meet in the middle

**9.1 Two halves: enumerate each half, sort, two pointers (balanced split)**

- LeetCode 2035 Partition Array Into Two Arrays to Minimize Sum Difference (hard; practice)
- LeetCode 805 Split Array With Same Average (hard; all)

**9.2 Closest to a target / count subsets with a given sum**

- no problem in the data: needs one from LeetCode

**9.3 k-sum by pairs: hash the pair sums**

- LeetCode 18 4Sum (medium; neetcode250, all)

**9.4 Bidirectional search on a state space**

- LeetCode 127 Word Ladder (hard; neetcode150, neetcode250, all)
- LeetCode 752 Open the Lock (medium; neetcode250, all)
- LeetCode 433 Minimum Genetic Mutation (medium; practice)

### 10. Iterative generation

**10.1 Next permutation / previous permutation**

- LeetCode 31 Next Permutation (medium; all)
- LeetCode 1850 Minimum Adjacent Swaps to Reach the Kth Smallest Number (medium; practice)

**10.2 k-th permutation: factorial number system**

- LeetCode 60 Permutation Sequence (hard; practice)

**10.3 Gray code: reflection / i xor (i >> 1)**

- LeetCode 89 Gray Code (medium; practice)

**10.4 Next combination / subsets by counting masks (Gosper's hack)**

- LeetCode 78 Subsets (medium; neetcode150, neetcode250, all)
- LeetCode 2397 Maximum Rows Covered by Columns (medium; practice)
- LeetCode 401 Binary Watch (easy; practice)

**10.5 Lexicographic order walks: iterative number-trie DFS with branch counting**

- LeetCode 386 Lexicographical Numbers (medium; all)
- LeetCode 440 K-th Smallest in Lexicographical Order (hard; all)

**10.6 Minimal-change permutations: Heap's algorithm / Steinhaus-Johnson-Trotter**

- no problem in the data: needs one from LeetCode

**10.7 Lazy generation: iterators and generators over combinations**

- no problem in the data: needs one from LeetCode

### 11. Branch and bound and search order

**11.1 Branch and bound: cut on best-so-far with an optimistic bound**

- LeetCode 1723 Find Minimum Time to Finish All Jobs (hard; practice)
- LeetCode 2305 Fair Distribution of Cookies (medium; practice)
- LeetCode 638 Shopping Offers (medium; practice)
- LeetCode 465 Optimal Account Balancing (hard; all; premium)

**11.2 Iterative deepening / depth-limited search**

- LeetCode 773 Sliding Puzzle (hard; all)

**11.3 A* / IDA* with an admissible heuristic**

- LeetCode 773 Sliding Puzzle (hard; all)
- LeetCode 505 The Maze II (medium; all; premium)
- LeetCode 499 The Maze III (hard; all; premium)

**11.4 Value ordering and incumbent seeding: greedy first, then improve**

- LeetCode 473 Matchsticks to Square (medium; neetcode250, all)
- LeetCode 1723 Find Minimum Time to Finish All Jobs (hard; practice)

**11.5 Relaxation bounds for TSP-style problems: MST / assignment bound**

- no problem in the data: needs one from LeetCode

### 12. Game-tree search

**12.1 Minimax with memo: (mask, remaining) / (left, right)**

- LeetCode 464 Can I Win (medium; practice)
- LeetCode 486 Predict the Winner (medium; practice)
- LeetCode 877 Stone Game (medium; neetcode250, all)
- LeetCode 1140 Stone Game II (medium; neetcode250, all)

**12.2 Alpha-beta pruning and move ordering**

- no problem in the data: needs one from LeetCode

**12.3 When the search collapses: parity and counting arguments**

- LeetCode 2038 Remove Colored Pieces if Both Neighbors are the Same Color (medium; all)
- LeetCode 877 Stone Game (medium; neetcode250, all)

### 13. Backtracking versus DP boundary

**13.1 Count / exists / optimise with a repeating state: memoise, then tabulate**

- LeetCode 494 Target Sum (medium; neetcode150, neetcode250, all)
- LeetCode 416 Partition Equal Subset Sum (medium; neetcode150, neetcode250, all)
- LeetCode 377 Combination Sum IV (medium; neetcode250, all)
- LeetCode 139 Word Break (medium; blind75, neetcode150, neetcode250, all)

**13.2 Enumerate every answer: output-bound, so backtracking stays**

- LeetCode 140 Word Break II (hard; neetcode250, all)
- LeetCode 131 Palindrome Partitioning (medium; neetcode150, neetcode250, all)
- LeetCode 22 Generate Parentheses (medium; neetcode150, neetcode250, all)
- LeetCode 78 Subsets (medium; neetcode150, neetcode250, all)

**13.3 Same recursion, enumerate versus count**

- LeetCode 91 Decode Ways (medium; blind75, neetcode150, neetcode250, all)
- LeetCode 139 Word Break (medium; blind75, neetcode150, neetcode250, all)
- LeetCode 140 Word Break II (hard; neetcode250, all)

**13.4 Search over values instead of choices: bitset subset sum / knapsack**

- LeetCode 1981 Minimize the Difference Between Target and Chosen Elements (medium; practice)
- LeetCode 416 Partition Equal Subset Sum (medium; neetcode150, neetcode250, all)
- LeetCode 494 Target Sum (medium; neetcode150, neetcode250, all)

**13.5 Closed form instead of search: combinatorics and digit counting**

- LeetCode 357 Count Numbers with Unique Digits (medium; practice)
- LeetCode 62 Unique Paths (medium; blind75, neetcode150, neetcode250, all)
- LeetCode 1359 Count All Valid Pickup and Delivery Options (hard; all)
- LeetCode 920 Number of Music Playlists (hard; all)

### 14. Core implementation patterns

Taught inside the lessons above (each template shows them), so this group has no example problems of its own.

## Gaps

1. **No lesson yet: 40 of 91 patterns.** 1.7, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 3.2, 3.3, 3.7, 3.8, 3.9, 4.2, 4.4, 4.5, 4.7, 4.9, 4.10, 5.4, 5.5, 5.7, 6.3, 6.8, 8.2, 8.3, 8.6, 8.7, 9.1, 9.2, 10.4, 10.6, 10.7, 11.1, 11.2, 11.4, 11.5, 12.2.
2. **No example problem in the data: 10 patterns.** 2.10, 4.10, 5.7, 6.3, 6.8, 9.2, 10.6, 10.7, 11.5, 12.2. Each needs a problem picked from LeetCode and checked there.
3. **Variant tabs missing.** The nine techniques have one template each. Tabs still to write: subsets (start-index loop), duplicates (per-level seen set), permutations (swap in place; count map), combinations (exactly k), N-Queens (bitmask), word search (visited set), partition (bucket versus item, bitmask), parentheses (counters versus BFS-by-removal).
4. **Technique filing is loose.** With only nine techniques, many problems sit under a technique that is not their shape: LeetCode 301 Remove Invalid Parentheses under `Backtracking:n-queens`; LeetCode 357 Count Numbers with Unique Digits under `Backtracking:split-memo`; LeetCode 282 Expression Add Operators under `Backtracking:split-memo`; LeetCode 93 Restore IP Addresses under `Backtracking:include-exclude`; LeetCode 17 Letter Combinations of a Phone Number under `Backtracking:include-exclude`; LeetCode 89 Gray Code under `Backtracking:include-exclude`; LeetCode 526 Beautiful Arrangement under `Backtracking:partition-k`; LeetCode 2397 Maximum Rows Covered by Columns under `Backtracking:partition-k`; LeetCode 679 24 Game under `Backtracking:permute`; LeetCode 816 Ambiguous Coordinates under `Backtracking:permute`; LeetCode 2850 Minimum Moves to Spread Stones Over Grid under `Backtracking:permute`; LeetCode 3211 Generate Binary Strings Without Adjacent Zeros under `Backtracking:skip-dups`; LeetCode 1240 Tiling a Rectangle with the Fewest Squares under `Backtracking:reuse`; LeetCode 967 Numbers With Same Consecutive Differences under `Backtracking:reuse`; LeetCode 638 Shopping Offers under `Backtracking:reuse`. A new lesson per pattern lets the filing be redone, and the problems keep their ids.
5. **Backtracking problems filed in other topics (18).** 37 Sudoku Solver (Arrays & Hashing:seen-set); 95 Unique Binary Search Trees II (Trees:catalan); 113 Path Sum II (Trees:dfs-carry); 126 Word Ladder II (Graphs:bfs-implicit); 212 Word Search II (Tries:trie-grid); 257 Binary Tree Paths (Trees:dfs-carry); 465 Optimal Account Balancing (1-D Dynamic Programming:bitmask); 494 Target Sum (1-D Dynamic Programming:subset); 691 Stickers to Spell Word (1-D Dynamic Programming:bitmask); 773 Sliding Puzzle (Graphs:bfs-implicit); 797 All Paths From Source to Target (Graphs:topo); 988 Smallest String Starting From Leaf (Trees:dfs-carry); 1219 Path with Maximum Gold (Graphs:flood); 1258 Synonymous Sentences (Graphs:dsu); 1799 Maximize Score After N Operations (1-D Dynamic Programming:bitmask); 2002 Maximum Product of the Length of Two Palindromic Subsequences (1-D Dynamic Programming:bitmask); 2698 Find the Punishment Number of an Integer (Backtracking:include-exclude); 2767 Partition String Into Minimum Beautiful Substrings (1-D Dynamic Programming:partition-dp). They stay with their topic's lesson; the Backtracking lesson links to them.
6. **Open decisions.** (a) Where the cross-topic groups sit: bitmask (8), game-tree (12), the DP boundary (13) and path enumeration (6) could be Backtracking lessons that link to the Trees, Graphs and 1-D Dynamic Programming lessons, or new techniques inside Backtracking with their own examples. (b) The tab layout needs a mockup first (rule 13). (c) The 1-D and 2-D DP topics own bitmask DP and the game problems today, so a duplicate lesson would drift from them.
7. **Premium examples (10).** 247, 254, 291, 351, 465, 489, 499, 505, 1087, 1258 are premium on LeetCode, so a learner without a subscription cannot open them. Where a pattern lists only premium problems (4.9, 5.5), a free problem should be picked from LeetCode.
