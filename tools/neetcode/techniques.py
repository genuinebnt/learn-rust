"""The technique taxonomy behind must learn vs practice (docs/DSA.md, decision 7).

A technique is one idea a pattern lesson teaches. The first problem of a technique in NeetCode's order is its
*must learn*; every other problem using it is *practice* for that one. The NeetCode 150 is assigned by hand below;
`RULES` places the other problems from LeetCode tags and title words, and `build.py` reports what it couldn't place.

TECHNIQUES[pattern] = [(key, name), ...]   ASSIGN_150[slug] = key, or "Pattern:key" when the technique first appears in an earlier pattern   RULES[pattern] = [(key, tags, title words), ...]
"""

TECHNIQUES = {
    "Arrays & Hashing": [
        ("seen-set", "Hash set for membership"), ("counting", "Counting with a hash map or array"),
        ("complement", "Complement lookup in a hash map"), ("signature", "Group by a canonical key"),
        ("top-k", "Top K by frequency (bucket sort)"), ("prefix", "Prefix and suffix products or sums"),
        ("encoding", "Length-prefix encoding"), ("consecutive", "Start of a sequence in a set"),
        ("simulation", "Direct simulation"),
        ("design-hash", "Designing with hash maps and queues"),
        ("index-marks", "Using the array's indices as markers"),
        ("majority-vote", "Boyer-Moore majority vote"),
        ("sorting", "Sorting with a custom order"),
        ("string-match", "String matching and rolling hash"),
        ("prefix-map", "Prefix sums with a hash map"),
    ],
    "Two Pointers": [
        ("opposite", "Pointers from both ends"), ("ksum", "Sort, fix one, two pointers"),
        ("running-max", "Two pointers with a running maximum"),
        ("in-place", "In-place read and write pointers"),
        ("merge-sorted", "Merging two sorted arrays"),
        ("pair-count", "Counting pairs in a sorted array"),
        ("greedy-pair", "Greedy pairing from both ends"),
        ("simulate", "Two-pointer simulation"),
    ],
    "Sliding Window": [
        ("running-best", "One pass tracking the best so far"), ("window-max", "Variable window: longest valid"),
        ("window-min", "Variable window: shortest valid"), ("fixed-window", "Fixed-size window with counts"),
        ("mono-deque", "Monotonic deque for the window maximum"),
        ("at-most-k", "Window with at most K of something"),
        ("count-windows", "Counting windows (at most K minus at most K-1)"),
        ("fixed-sum", "Fixed window with a running sum"),
        ("window-sort", "Window over a sorted array"),
    ],
    "Stack": [
        ("matching", "Matching pairs with a stack"), ("aux-stack", "Stack that tracks running state"),
        ("expression", "Evaluating expressions with a stack"), ("mono-stack", "Monotonic stack"),
        ("simulate-stack", "Stack simulation (undo, collide, cancel)"),
        ("nested", "Nested structures with a stack"),
        ("design-queue-stack", "Queue and stack from each other"),
        ("mono-contrib", "Monotonic stack for contribution counting"),
        ("calculator", "Calculator with operator precedence"),
    ],
    "Binary Search": [
        ("classic", "Classic binary search"), ("on-answer", "Binary search on the answer"),
        ("rotated", "Binary search on a rotated array"), ("partition", "Binary search on a partition"),
        ("insert-pos", "Insertion point and boundaries"),
        ("peak", "Binary search on a changing slope"),
        ("by-count", "Binary search on a count function"),
        ("weighted", "Prefix sums with binary search"),
    ],
    "Linked List": [
        ("reverse", "Reversing pointers in place"), ("dummy-merge", "Dummy head and merge"),
        ("fast-slow", "Fast and slow pointers"), ("gap", "Two pointers a fixed gap apart"),
        ("clone-map", "Copy with an old-to-new map"), ("lru", "Hash map plus doubly linked list"),
        ("kway-merge", "K-way merge with a heap"),
        ("splice", "Editing and splicing nodes in place"),
        ("design-list", "Designing list-backed structures"),
    ],
    "Trees": [
        ("dfs", "Recursive DFS on a tree"), ("dfs-return", "DFS that returns a value and updates an answer"),
        ("bst-walk", "Navigating a BST by its order"), ("bfs-levels", "BFS level by level"),
        ("dfs-carry", "DFS carrying state down"), ("inorder", "Inorder traversal of a BST"),
        ("from-traversals", "Building a tree from traversals"), ("serialize", "Serializing a tree"),
        ("bst-edit", "Insert, delete and trim in a BST"),
        ("tree-as-graph", "Treating a tree as a graph"),
        ("catalan", "Counting and building trees by root choice"),
        ("dfs-edit", "Postorder editing of a tree"),
    ],
    "Heap / Priority Queue": [
        ("size-k", "Min-heap of size K"), ("pool", "Heap as a priority pool"), ("quickselect", "Quickselect"),
        ("cooldown", "Greedy with a heap and a cooldown queue"), ("two-heaps", "Two heaps for the median"),
        ("greedy-heap", "Greedy with a heap of the best choices"),
        ("schedule-sim", "Event simulation with heaps"),
    ],
    "Backtracking": [
        ("include-exclude", "Include or exclude choices"), ("reuse", "Choices that can repeat, with a start index"),
        ("skip-dups", "Skipping duplicates at the same level"), ("permute", "Permutations with a used set"),
        ("construct", "Building a valid sequence under a rule"), ("grid", "Backtracking on a grid"),
        ("n-queens", "Constraint sets for placement"),
        ("partition-k", "Partitioning into K equal groups"),
        ("split-memo", "Splitting with a memoized DFS"),
    ],
    "Tries": [
        ("trie", "Trie insert and search"), ("trie-dfs", "Trie with a wildcard DFS"),
        ("trie-grid", "Trie to prune a grid search"),
    ],
    "Graphs": [
        ("flood", "Flood fill on grids"), ("clone", "Graph traversal with a copy map"),
        ("multi-bfs", "Multi-source BFS"), ("border", "Search inward from the border"),
        ("topo", "Cycle detection and topological sort"), ("dsu", "Union-Find"),
        ("bfs-implicit", "BFS on an implicit graph"),
        ("bipartite", "Bipartite check (two-coloring)"),
        ("degree", "Counting in-degrees and out-degrees"),
        ("tree-walk", "Walking a tree as a graph from a root"),
        ("weighted", "Weighted queries on a graph"),
        ("simulation", "Direct simulation on a graph"),
    ],
    "Advanced Graphs": [
        ("dijkstra", "Dijkstra"), ("euler", "Eulerian path"), ("mst", "Minimum spanning tree"),
        ("bellman", "Bellman-Ford"),
        ("floyd", "All-pairs shortest paths (Floyd-Warshall)"),
        ("cycles", "Cycles in a functional graph"),
        ("articulation", "Articulation points and bridges"),
    ],
    "1-D Dynamic Programming": [
        ("recurrence", "A recurrence over positions"), ("take-skip", "Take or skip along a line"),
        ("expand", "Expand around a center"), ("unbounded", "Unbounded knapsack"),
        ("min-max-run", "Track both a max and a min"), ("prefix-dp", "DP over prefixes with a dictionary"),
        ("lis", "Longest increasing subsequence"), ("subset", "0/1 subset knapsack"),
        ("partition-dp", "Partitioning a sequence into groups"),
        ("bitmask", "Bitmask DP"),
        ("count-states", "Counting paths over states"),
        ("game", "Minimax game DP"),
    ],
    "2-D Dynamic Programming": [
        ("grid-dp", "Grid DP"), ("two-string", "Two-string DP table"), ("state-machine", "State machine DP"),
        ("dfs-memo", "DFS with memoization on a grid"), ("interval", "Interval DP"),
        ("pair-dp", "DP over pairs of positions"),
    ],
    "Greedy": [
        ("kadane", "Kadane's algorithm"), ("reach", "Furthest reachable"), ("surplus", "Running surplus and reset"),
        ("group-smallest", "Group the smallest first"), ("filter", "Filter by constraints"),
        ("last-seen", "Greedy with last occurrence"), ("paren-range", "Range of open counts"),
        ("sort-pick", "Sort, then take greedily"),
        ("count-greedy", "Greedy from counts"),
        ("scan-balance", "One pass with a running balance"),
        ("swap-greedy", "Greedy swaps and digit rearrangement"),
        ("simulate-greedy", "Greedy simulation of a game"),
        ("flip-window", "Greedy flips with a difference array"),
    ],
    "Intervals": [
        ("merge", "Sort by start and merge"), ("by-end", "Greedy by earliest end"),
        ("sweep", "Sweep line or heap of ends"),
        ("calendar", "Booking with a sorted structure"),
    ],
    "Math & Geometry": [
        ("matrix-inplace", "In-place matrix transforms"), ("spiral", "Shrinking boundaries"),
        ("markers", "In-place markers"), ("number-cycle", "Cycle detection on number sequences"),
        ("digits", "Digit arithmetic with a carry"), ("fast-pow", "Fast exponentiation"),
        ("point-counts", "Counting points in a hash map"),
        ("number-theory", "GCD, primes and divisibility"),
        ("matrix-sim", "Matrix and grid simulation"),
        ("number-format", "Number and string conversion"),
        ("formula", "Closed-form counting"),
        ("median", "The median minimizes distance"),
        ("lex-order", "Walking numbers in lexicographic order"),
    ],
    "Bit Manipulation": [
        ("xor", "XOR cancellation"), ("bit-count", "Counting bits"), ("shift", "Shifting bit by bit"),
        ("add-bits", "Adding with XOR and carry"), ("digit-extract", "Digit extraction with overflow"),
        ("prefix-xor", "Prefix XOR"),
    ],
}

ASSIGN_150 = {
    # Arrays & Hashing
    "contains-duplicate": "seen-set", "valid-anagram": "counting", "two-sum": "complement",
    "group-anagrams": "signature", "top-k-frequent-elements": "top-k", "encode-and-decode-strings": "encoding",
    "product-of-array-except-self": "prefix", "valid-sudoku": "seen-set", "longest-consecutive-sequence": "consecutive",
    # Two Pointers
    "valid-palindrome": "opposite", "two-sum-ii-input-array-is-sorted": "opposite", "3sum": "ksum",
    "container-with-most-water": "opposite", "trapping-rain-water": "running-max",
    # Sliding Window
    "best-time-to-buy-and-sell-stock": "running-best", "longest-substring-without-repeating-characters": "window-max",
    "longest-repeating-character-replacement": "window-max", "permutation-in-string": "fixed-window",
    "minimum-window-substring": "window-min", "sliding-window-maximum": "mono-deque",
    # Stack
    "valid-parentheses": "matching", "min-stack": "aux-stack", "evaluate-reverse-polish-notation": "expression",
    "daily-temperatures": "mono-stack", "car-fleet": "mono-stack", "largest-rectangle-in-histogram": "mono-stack",
    # Binary Search
    "binary-search": "classic", "search-a-2d-matrix": "classic", "koko-eating-bananas": "on-answer",
    "find-minimum-in-rotated-sorted-array": "rotated", "search-in-rotated-sorted-array": "rotated",
    "time-based-key-value-store": "classic", "median-of-two-sorted-arrays": "partition",
    # Linked List
    "reverse-linked-list": "reverse", "merge-two-sorted-lists": "dummy-merge", "linked-list-cycle": "fast-slow",
    "reorder-list": "reverse", "remove-nth-node-from-end-of-list": "gap", "copy-list-with-random-pointer": "clone-map",
    "add-two-numbers": "dummy-merge", "find-the-duplicate-number": "fast-slow", "lru-cache": "lru",
    "merge-k-sorted-lists": "kway-merge", "reverse-nodes-in-k-group": "reverse",
    # Trees
    "invert-binary-tree": "dfs", "maximum-depth-of-binary-tree": "dfs", "diameter-of-binary-tree": "dfs-return",
    "balanced-binary-tree": "dfs-return", "same-tree": "dfs", "subtree-of-another-tree": "dfs",
    "lowest-common-ancestor-of-a-binary-search-tree": "bst-walk", "binary-tree-level-order-traversal": "bfs-levels",
    "binary-tree-right-side-view": "bfs-levels", "count-good-nodes-in-binary-tree": "dfs-carry",
    "validate-binary-search-tree": "dfs-carry", "kth-smallest-element-in-a-bst": "inorder",
    "construct-binary-tree-from-preorder-and-inorder-traversal": "from-traversals",
    "binary-tree-maximum-path-sum": "dfs-return", "serialize-and-deserialize-binary-tree": "serialize",
    # Heap / Priority Queue
    "kth-largest-element-in-a-stream": "size-k", "last-stone-weight": "pool", "k-closest-points-to-origin": "size-k",
    "kth-largest-element-in-an-array": "quickselect", "task-scheduler": "cooldown", "design-twitter": "Linked List:kway-merge",
    "find-median-from-data-stream": "two-heaps",
    # Backtracking
    "subsets": "include-exclude", "combination-sum": "reuse", "combination-sum-ii": "skip-dups", "permutations": "permute",
    "subsets-ii": "skip-dups", "generate-parentheses": "construct", "word-search": "grid",
    "palindrome-partitioning": "include-exclude", "letter-combinations-of-a-phone-number": "include-exclude",
    "n-queens": "n-queens",
    # Tries
    "implement-trie-prefix-tree": "trie", "design-add-and-search-words-data-structure": "trie-dfs", "word-search-ii": "trie-grid",
    # Graphs
    "number-of-islands": "flood", "max-area-of-island": "flood", "clone-graph": "clone", "walls-and-gates": "multi-bfs",
    "rotting-oranges": "multi-bfs", "pacific-atlantic-water-flow": "border", "surrounded-regions": "border",
    "course-schedule": "topo", "course-schedule-ii": "topo", "graph-valid-tree": "dsu",
    "number-of-connected-components-in-an-undirected-graph": "dsu", "redundant-connection": "dsu", "word-ladder": "bfs-implicit",
    # Advanced Graphs
    "network-delay-time": "dijkstra", "reconstruct-itinerary": "euler", "min-cost-to-connect-all-points": "mst",
    "swim-in-rising-water": "dijkstra", "alien-dictionary": "Graphs:topo", "cheapest-flights-within-k-stops": "bellman",
    # 1-D DP
    "climbing-stairs": "recurrence", "min-cost-climbing-stairs": "recurrence", "house-robber": "take-skip",
    "house-robber-ii": "take-skip", "longest-palindromic-substring": "expand", "palindromic-substrings": "expand",
    "decode-ways": "recurrence", "coin-change": "unbounded", "maximum-product-subarray": "min-max-run",
    "word-break": "prefix-dp", "longest-increasing-subsequence": "lis", "partition-equal-subset-sum": "subset",
    # 2-D DP
    "unique-paths": "grid-dp", "longest-common-subsequence": "two-string", "best-time-to-buy-and-sell-stock-with-cooldown": "state-machine",
    "coin-change-ii": "1-D Dynamic Programming:unbounded", "target-sum": "1-D Dynamic Programming:subset", "interleaving-string": "two-string",
    "longest-increasing-path-in-a-matrix": "dfs-memo", "distinct-subsequences": "two-string", "edit-distance": "two-string",
    "burst-balloons": "interval", "regular-expression-matching": "two-string",
    # Greedy
    "maximum-subarray": "kadane", "jump-game": "reach", "jump-game-ii": "reach", "gas-station": "surplus",
    "hand-of-straights": "group-smallest", "merge-triplets-to-form-target-triplet": "filter", "partition-labels": "last-seen",
    "valid-parenthesis-string": "paren-range",
    # Intervals
    "insert-interval": "merge", "merge-intervals": "merge", "non-overlapping-intervals": "by-end", "meeting-rooms": "merge",
    "meeting-rooms-ii": "sweep", "minimum-interval-to-include-each-query": "sweep",
    # Math & Geometry
    "rotate-image": "matrix-inplace", "spiral-matrix": "spiral", "set-matrix-zeroes": "markers", "happy-number": "number-cycle",
    "plus-one": "digits", "powx-n": "fast-pow", "multiply-strings": "digits", "detect-squares": "point-counts",
    # Bit Manipulation
    "single-number": "xor", "number-of-1-bits": "bit-count", "counting-bits": "bit-count", "reverse-bits": "shift",
    "missing-number": "xor", "sum-of-two-integers": "add-bits", "reverse-integer": "digit-extract",
}
