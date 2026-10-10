# Data structures as algorithms: the exhaustive target list

The target list (2026-10-10) of every data structure and query technique that interviews and contests use, as the target for the
data-structure pattern lessons (Arrays & Hashing, Heap / Priority Queue, Linked List, Stack, Intervals, Tries and the Design problems).
The rule is in [DSA.md](DSA.md), decision 32: a topic's patterns section is exhaustive, patterns without a NeetCode problem get
**example problems** from LeetCode, and variants of one pattern (chaining / open addressing) are **tabs** of one lesson. The format
follows [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md); the number-theory sibling is
[DSA_ALGORITHMS_NUMBER_THEORY.md](DSA_ALGORITHMS_NUMBER_THEORY.md).

Status: documented only. Today the lesson files cover the NeetCode spine for these structures (for example `arrays-hashing.toml` has
15 techniques, `heap-priority-queue.toml` 7, `stack.toml` 9, `linked-list.toml` 9, `tries.toml` 3); most of the list below has no
lesson yet. Building the rest needs a mockup of the tabs first, then lessons and picked example problems. Graph-side structures
(union-find applications, shortest-path heaps) are cross-referenced, not repeated; string matching algorithms (KMP, Z, Manacher) and
bit tricks live in their own catalogues.

Items written *a / b* in a group are variants for tabs where one lesson covers both (for example "chaining / open addressing").

1. **Arrays and prefix techniques.** prefix sums (range sum, pivot index, split points); prefix XOR / prefix product / prefix count (any invertible operation); prefix sums plus a hash map (subarray sum equals k, remainder buckets, balance counters); prefix and suffix aggregates (product except self, trapping water, best split); 2-D prefix sums (rectangle sum, submatrices summing to a target); difference array (range add, then one prefix pass) / 2-D difference array; event-count difference array over sorted coordinates (car pooling, bookings, brightest point); sparse table (idempotent min / max / gcd, O(1) query) / sparse table for non-idempotent operations (O(log n) query); disjoint sparse table (O(1) query for any associative operation); sqrt decomposition (point update, block query) / block lazy tags for range update; Mo's algorithm / Mo's algorithm with updates / Mo's algorithm on trees; offline queries (sort queries by right end or by value, answer in one sweep); coordinate compression (sort + unique + binary search) / joint compression of intervals and points; rank transform and order-preserving relabeling; value bucketing (frequency of frequencies, count of values at most x); block prefix and suffix maxima (sliding-window maximum without a deque); segment summaries as a reusable node (prefix, suffix, best, total for maximum subarray).
2. **Range-query trees.** Fenwick tree (BIT): point update, prefix / range query; Fenwick tree: range update, point query; Fenwick tree: range update, range query (two trees); Fenwick tree descent (k-th element, lower bound on prefix sums); Fenwick tree for inversion counting and rank counting (with coordinate compression); 2-D Fenwick tree; Fenwick tree for prefix min / max (monotone updates only); segment tree: point update, range query / range update, point query; segment tree with lazy propagation (add / assign / add-and-assign tags, push-down and pull-up); iterative bottom-up segment tree / non-commutative combine in the iterative form; segment tree descent (first index satisfying a predicate, k-th one); segment tree with structured nodes (max subarray, min and count of min, gcd, matrix product, bracket balance); merge-sort tree (count of values in a range at most x); persistent segment tree (k-th smallest in a range, versions); dynamic / sparse segment tree (huge coordinate range, nodes created on demand); segment tree merging; segment tree beats (range chmin / chmax with sum); 2-D segment tree / segment tree of Fenwick trees; segment tree over time (offline dynamic connectivity, with rollback DSU); interval tree (stabbing and overlap queries); Li Chao tree (line container, convex hull trick); Cartesian tree (RMQ by LCA, shape by key and priority); sqrt tree.
3. **Balanced and ordered structures.** binary search tree (insert, delete, successor / predecessor, inorder iteration); AVL tree (height balance, four rotations); red-black tree / left-leaning red-black tree; treap (priorities; split / merge); splay tree (splay on access, amortised bound); scapegoat tree / weight-balanced tree; skip list (levels by coin flip; search, insert, erase); order statistic tree (rank / select by subtree size); implicit treap (sequence by position: insert, erase, reverse, cut and paste ranges); rope; B-tree (in-memory; split and merge); 2-3 tree / 2-3-4 tree; ordered map / set usage (floor, ceiling, lower, higher, range iteration); ordered multiset via a map of counts; sorted list with bisect (insort; sqrt-decomposed sorted list for fast insert); sliding-window ordered multiset (median, min and max of a window); interval map (assign a range, split and coalesce intervals) / interval set merging; k-th smallest and rank in a dynamic set (order statistic tree / BIT over compressed values); finger tree.
4. **Heaps and priority structures.** binary heap (sift up, sift down, heapify in O(n)); d-ary heap; pairing heap; Fibonacci heap; binomial heap; leftist heap / skew heap (mergeable heaps); indexed heap with decrease-key (position map); lazy deletion heap (stale entries skipped on pop); two heaps for the running median / two heaps for a sliding-window median (with lazy deletion); bounded heap for top-k (min-heap of size k for the k largest); k-way merge heap (lists, matrix rows, sorted streams); min-max heap / double-ended priority queue; heap with custom ordering (tuple keys, comparator, negation for a max-heap); event queue and timers (expiry-ordered heap); bucket queue / radix heap (monotone integer keys); tournament tree / loser tree; monotonic queue (sliding-window maximum / minimum, DP optimisation window); monotonic stack (next greater, span) as the one-sided cousin; deque (circular buffer; both ends O(1)); quickselect / nth_element (heap-free k-th selection).
5. **Hashing structures.** hash map / hash set interface (insert, find, erase, iterate); chaining / open addressing (linear probing, quadratic probing, double hashing) with tombstones; cuckoo hashing; robin hood hashing (cross-reference the BusTub course, module 26); hopscotch hashing; resizing: load factor, amortised rehash / incremental rehash; hash functions: division, multiplication, universal families, mixing finalisers; polynomial string hash / rolling hash (Rabin-Karp); hashing structured keys (tuples, canonical forms, sorted-key signatures, anagram keys); counting structures (frequency map, counter of counters, multiset); Bloom filter / counting Bloom filter / cuckoo filter; count-min sketch (cross-reference the BusTub course, module 27); HyperLogLog (cross-reference the BusTub course, module 27); MinHash / locality-sensitive hashing; consistent hashing / rendezvous hashing (virtual nodes); perfect hashing (FKS, two-level); extendible hashing / linear hashing (cross-reference the BusTub course, module 09); hash flooding and adversarial inputs (SipHash, randomised seeds).
6. **Caches and design.** LRU cache (hash map + doubly linked list / ordered dictionary); LFU cache (frequency lists, O(1) / heap with tie-break by recency); ARC / 2Q / CLOCK / FIFO / MRU (cross-reference the BusTub course, modules 03 to 05); TTL cache (lazy expiry on read / heap or queue based expiry); time-based key-value store (per-key timestamp list + binary search); snapshot array (per-index version list + binary search); rate limiter (fixed window / sliding window log / sliding window counter / token bucket / leaky bucket); hit counter and moving average over a window (queue / circular buckets); iterator designs (peeking / zigzag / flatten nested list / BST iterator with a stack / compressed string); randomised set and multiset with O(1) getRandom (array + hash map + swap-remove); min stack / max stack / maximum frequency stack; queue with two stacks / stack with queues (amortised O(1)); circular queue / circular deque / front-middle-back queue; all-O(1) structure (inc, dec, max key, min key); leaderboard and rank tracker (sorted structure + map); autocomplete and typeahead (trie with hot lists); text editor (two stacks around the cursor / gap buffer / doubly linked list); undo / redo and browser history; ID and resource allocators (smallest free id, seat reservation, memory allocator); calendar and booking structures (interval overlap, k-booking counts); in-memory file system and key path trees; spreadsheet with dependent cells (recompute order, cycle guard).
7. **Union-find variants.** basic union-find (find, union, connected); path compression (full / halving / splitting); union by rank / size; component count and component size; grid union-find (cell ids, online land addition); DSU with component metadata (size, min, max, sum, bitmask of values); weighted / potential DSU (ratios and offsets, evaluate division); parity DSU (bipartite check, enemy-of-enemy); rollback DSU (union by size, no path compression); offline reverse-time DSU (deletions as insertions); persistent DSU; DSU with a next-free-slot pointer (skip processed positions, interval painting); DSU over virtual nodes (rows and columns as nodes, value-sorted merging); DSU on tree / small-to-large merging; Kruskal's use of DSU (cross-reference DSA_GRAPH_PATTERNS.md, groups 4 and 6).
8. **String structures.** trie (array children / hash-map children; insert, search, prefix, delete); trie with counts and prefix aggregates (sum of prefix scores, top-k hot lists); trie with wildcard search (DFS over branches); compressed trie / radix tree / Patricia tree; ternary search tree; bitwise (XOR) trie (maximum XOR pair, maximum XOR under a limit); persistent trie (cross-reference the BusTub course, module 24); Aho-Corasick automaton (multi-pattern matching); suffix array (with LCP array, Kasai) / suffix tree; suffix automaton (cross-reference the future strings catalogue); palindromic tree (eertree); DAWG / minimal acyclic automaton for word sets; hashing for substring equality (cross-reference group 5).
9. **Geometry structures.** k-d tree (build by median split; nearest neighbour, k nearest, range query); quadtree / octree (point and region subdivision); R-tree / R*-tree (bounding rectangles, bulk loading); BSP tree; range tree / 2-D range counting (merge-sort tree, offline BIT; cross-reference group 2); grid / spatial hashing (cell buckets for neighbour search); sweep-line status structure (ordered set of active segments or intervals); ball tree / vantage-point tree; priority search tree; convex hull trick / Li Chao tree (cross-reference group 2).
10. **Persistent and functional structures.** persistent array (fat node / path copying / per-index version list); persistent stack (immutable cons list, shared tails); persistent queue (two lists, banker's queue); persistent segment tree (cross-reference group 2); persistent BST / persistent treap; persistent trie (cross-reference group 8); persistent union-find (cross-reference group 7); path copying / fat node method / node splitting; rollback (undo log, checkpoint stack, version stack); copy-on-write with structural sharing; versioned map / time-travel store; hash array mapped trie (HAMT); zipper.
11. **Bit-level structures.** bitset (fixed / dynamic; word-parallel and, or, xor, count, flip); bitmask set (membership, subset enumeration, submask iteration); bitset DP (subset-sum and reachability by shifted or); bitmap index / roaring bitmap; rank / select succinct structure (popcount blocks); van Emde Boas tree / x-fast trie / y-fast trie; XOR basis / linear basis over GF(2) (span, max xor, k-th xor); wavelet tree / wavelet matrix (k-th smallest, rank, range frequency); binary trie over bits (cross-reference group 8); bit-parallel string matching (Shift-Or, Myers).
12. **Disk-oriented structures.** B-tree / B+ tree (cross-reference the BusTub course, modules 10 and 11); buffer pool and page cache (cross-reference the BusTub course, modules 06 and 07); extendible hashing / linear hashing (cross-reference the BusTub course, module 09); LSM tree (memtable, SSTables, compaction; cross-reference ADVANCED_DB_COURSE.md); skip list as a memtable (cross-reference the BusTub course, module 25); write-ahead log and checkpoints (cross-reference the BusTub course, module 22); slotted page layout; B-epsilon tree / fractal tree; external merge sort; inverted index and posting lists; zone maps / columnar layout; MVCC version chains (cross-reference the BusTub course, modules 20 and 21).
13. **Probabilistic and streaming structures.** reservoir sampling (one item / k items / weighted); Fisher-Yates shuffle; weighted random pick (prefix sums + binary search / alias method); Boyer-Moore majority vote / Misra-Gries (k - 1 counters); top-k heavy hitters (Space-Saving / count-min sketch + heap); quantile sketches (t-digest, Greenwald-Khanna, KLL, q-digest); cardinality estimation (Flajolet-Martin / HyperLogLog; cross-reference group 5); Bloom filter membership (cross-reference group 5); sliding-window aggregation (two-stack queue, monotonic deque, DABA); exponentially decayed counters / moving averages; median of a stream (cross-reference group 4); random pick with blacklist (index remapping); sampling from a linked list or a tree.
14. **Concurrency structures (names only).** lock-free queue (Michael-Scott); lock-free stack (Treiber); concurrent hash map (striped locks / lock-free / split-ordered lists); concurrent skip list; single-producer single-consumer ring buffer / multi-producer multi-consumer queue; work-stealing deque; blocking queue / bounded buffer; read-copy-update / epoch-based reclamation / hazard pointers; sharded counters and striped structures; atomic snapshot.
15. **Core implementation patterns.** array-backed vs pointer-backed (and when an arena of indices replaces both); implicit tree indexing (heap 2i + 1 / 2i + 2, segment tree 2i / 2i + 1, 1-indexed Fenwick); sentinel and dummy nodes (list head and tail, tree nil); monoid interface: identity element + associative combine; half-open intervals [l, r) and inclusive-bound pitfalls; lazy tags: push-down before descent, pull-up after; swap-remove with an index map; tombstones and lazy deletion / generation counters; amortised resizing and rehashing; node pools and arena allocation (Vec of nodes with integer ids); ownership of linked structures in Rust (Option<Box>, Rc<RefCell>, Weak back-pointers, index links); comparator and key-function design (total order, ties, stability); iterative vs recursive traversal for deep trees; offline vs online: when sorting the queries removes the data structure; API invariants and O(1) / O(log n) guarantees stated per operation; a brute-force reference and randomised comparison as the test; small design structures (min stack, queue from stacks, circular queue, linked list design, iterators).

## Problems in the data

Example problems per group (at most four), taken from `content/dsa/problems.json` and `content/dsa/practice.json`, matched by tag or
by the design the title names. Format: `LeetCode <number> <title> (<difficulty>; <lists>)`; the lists are the ones the data gives, `all`
meaning only the full catalogue and `practice` the practice pool. Never add a problem that is not in the data.

1. **Arrays and prefix techniques.**
   - LeetCode 303 Range Sum Query - Immutable (easy; all)
   - LeetCode 304 Range Sum Query 2D - Immutable (medium; neetcode250, all)
   - LeetCode 2381 Shifting Letters II (medium; all)
   - LeetCode 1094 Car Pooling (medium; neetcode250, all)
2. **Range-query trees.**
   - LeetCode 307 Range Sum Query - Mutable (medium; practice)
   - LeetCode 308 Range Sum Query 2D - Mutable (medium; all)
   - LeetCode 493 Reverse Pairs (hard; practice)
   - LeetCode 2407 Longest Increasing Subsequence II (hard; practice)
3. **Balanced and ordered structures.**
   - LeetCode 1206 Design Skiplist (hard; practice)
   - LeetCode 220 Contains Duplicate III (hard; practice)
   - LeetCode 352 Data Stream as Disjoint Intervals (hard; all)
   - LeetCode 729 My Calendar I (medium; all)
4. **Heaps and priority structures.**
   - LeetCode 295 Find Median from Data Stream (hard; blind75, neetcode150, neetcode250, all)
   - LeetCode 703 Kth Largest Element in a Stream (easy; neetcode150, neetcode250, all)
   - LeetCode 480 Sliding Window Median (hard; practice)
   - LeetCode 239 Sliding Window Maximum (hard; neetcode150, neetcode250, all)
5. **Hashing structures.**
   - LeetCode 705 Design HashSet (easy; neetcode250, all)
   - LeetCode 706 Design HashMap (easy; neetcode250, all)
   - LeetCode 535 Encode and Decode TinyURL (medium; all)
   - LeetCode 2013 Detect Squares (medium; neetcode150, neetcode250, all)
6. **Caches and design.**
   - LeetCode 146 LRU Cache (medium; neetcode150, neetcode250, all)
   - LeetCode 460 LFU Cache (hard; neetcode250, all)
   - LeetCode 981 Time Based Key-Value Store (medium; neetcode150, neetcode250, all)
   - LeetCode 380 Insert Delete GetRandom O(1) (medium; all)
7. **Union-find variants.**
   - LeetCode 305 Number of Islands II (hard; all)
   - LeetCode 684 Redundant Connection (medium; neetcode150, neetcode250, all)
   - LeetCode 721 Accounts Merge (medium; neetcode250, all)
   - LeetCode 2421 Number of Good Paths (hard; all)
   - note: the graph-side variants are in [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md), group 4; this group is the data structure itself.
8. **String structures.**
   - LeetCode 208 Implement Trie (Prefix Tree) (medium; blind75, neetcode150, neetcode250, all)
   - LeetCode 211 Design Add and Search Words Data Structure (medium; blind75, neetcode150, neetcode250, all)
   - LeetCode 212 Word Search II (hard; blind75, neetcode150, neetcode250, all)
   - LeetCode 1268 Search Suggestions System (medium; all)
   - note: matching algorithms (KMP, Z, Manacher) belong to the strings catalogue; this group is the structures.
9. **Geometry structures.**
   - LeetCode 973 K Closest Points to Origin (medium; neetcode150, neetcode250, all)
   - LeetCode 218 The Skyline Problem (hard; practice)
   - note: 973 is the only k-d tree item in the data and 218 the nearest sweep-line one; no problem in the data for quadtree, R-tree or BSP.
10. **Persistent and functional structures.**
   - LeetCode 1146 Snapshot Array (medium; practice)
   - note: 1146 is the only problem tagged Persistent Data Structure; no problem in the data for rollback.
11. **Bit-level structures.**
   - LeetCode 2166 Design Bitset (medium; practice)
   - LeetCode 421 Maximum XOR of Two Numbers in an Array (medium; practice)
   - LeetCode 1707 Maximum XOR With an Element From Array (hard; practice)
   - note: no problem in the data for XOR basis, van Emde Boas or wavelet trees.
12. **Disk-oriented structures.**
   - no problem in the data
13. **Probabilistic and streaming structures.**
   - LeetCode 382 Linked List Random Node (medium; practice)
   - LeetCode 497 Random Point in Non-overlapping Rectangles (medium; practice)
   - LeetCode 229 Majority Element II (medium; neetcode250, all)
   - LeetCode 347 Top K Frequent Elements (medium; blind75, neetcode150, neetcode250, all)
14. **Concurrency structures (names only).**
   - no problem in the data
15. **Core implementation patterns.**
   - LeetCode 155 Min Stack (medium; neetcode150, neetcode250, all)
   - LeetCode 232 Implement Queue using Stacks (easy; neetcode250, all)
   - LeetCode 622 Design Circular Queue (medium; neetcode250, all)
   - LeetCode 173 Binary Search Tree Iterator (medium; all)
