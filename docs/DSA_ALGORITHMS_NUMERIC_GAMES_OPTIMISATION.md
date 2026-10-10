# Numeric, game, scheduling, optimisation and system-style algorithms: the exhaustive target list

The target list for every numeric / transform algorithm, game-theory technique, scheduling and resource-allocation rule, optimisation
technique, probability and simulation pattern, and system-style algorithm (compression, hashing, caches, concurrency, rate limiting,
distributed protocols) that can come up in an interview or on LeetCode. The rule is in [DSA.md](DSA.md), decision 32 (pattern lessons are
exhaustive per topic; variants of one pattern are tabs of one lesson), and the format follows [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md).

Status: documented only. Nothing here is built. Today the nearest lessons are the techniques of Math & Geometry (13), Greedy (13),
Binary Search (8), Heap / Priority Queue (7), Bit Manipulation (6) and Intervals (4) in `content/dsa/lessons/`, plus the design problems
spread over Arrays & Hashing, Linked List and Stack. Building the rest needs a mockup of the tabs first (rule 13), then lessons and picked
example problems checked against LeetCode, never from memory.

Items written *a / b* in a group are variants for tabs where one lesson covers both (for example "Misere Nim / normal Nim"). Items marked
"(names)" are for recognition only: one paragraph in a lesson, no template, no exercise. "Cross-ref" means the algorithm lives in another
topic's list and is only named here for the connection. Every item is a candidate lesson or tab; the lesson order is the owner's decision.

1. **Transforms and convolution.** Schoolbook polynomial multiplication; Karatsuba; Toom-Cook (names); discrete Fourier transform (the O(n^2) definition); FFT recursive (Cooley-Tukey) / FFT iterative (bit-reversal permutation, butterflies); inverse FFT; FFT precision, rounding and splitting large coefficients; NTT (number-theoretic transform: NTT-friendly primes such as 998244353, primitive roots); arbitrary-modulus convolution (three-prime NTT with CRT / split-FFT); polynomial multiplication; big-number multiplication via FFT (digits as coefficients, then a carry pass); pattern matching with wildcards via convolution; counting pair sums or differences with convolution; Bluestein / chirp-z (names); Walsh-Hadamard transform (XOR convolution) / AND and OR convolution; subset-sum convolution (ranked zeta transform); fast zeta transform (sum over subsets) / Moebius transform (inverse); SOS DP (sum over subsets / sum over supersets); inclusion-exclusion by Moebius over subsets; polynomial inverse, division and modulo via Newton iteration (names); multipoint evaluation and Lagrange interpolation; online (relaxed) convolution (names); Dirichlet convolution and Dirichlet prefix sums (cross-ref number theory); matrix exponentiation as the alternative for linear recurrences (cross-ref linear algebra).

2. **Linear algebra.** Gaussian elimination (partial pivoting, floating-point stability) / Gauss-Jordan elimination; row echelon and reduced row echelon form; back substitution; LU decomposition (with pivoting); Cholesky and QR decomposition (names); matrix inverse by augmented Gauss-Jordan; determinant by elimination / Bareiss fraction-free determinant; determinant mod p; rank; solving linear systems mod p (modular inverse of the pivot); solving systems over GF(2) with bitsets / Gauss-Jordan on XOR systems (lights-out, switch puzzles); counting solutions (2^(n - rank)); linear basis over GF(2) (XOR basis: insert, maximum XOR, k-th smallest, membership); prefix linear basis with timestamps (offline range queries); matrix multiplication naive / blocked and Strassen (names); matrix exponentiation (linear recurrences, path counts); sparse matrix multiplication and sparse-vector dot product; Kirchhoff's matrix-tree theorem (spanning-tree count by determinant); Berlekamp-Massey and Kitamasa (names); Gram-Schmidt and least squares (names); power iteration and eigenvalues (names); matrix chain order (cross-ref 2-D DP); absorbing-chain systems by elimination (cross-ref probability); transpose, rotation and in-place matrix transforms (cross-ref Math & Geometry); cross and dot product as determinants (cross-ref geometry).

3. **Numeric methods.** Newton's method for roots / Newton's method for sqrt and reciprocal; integer square root by binary search / by Newton / digit by digit (sqrt without a library); cube root and n-th root; bisection; binary search on reals (fixed iteration count vs epsilon); secant method and regula falsi (names); fixed-point iteration; numerical integration: trapezoid / Simpson's rule / adaptive Simpson; numerical differentiation (names); gradient descent basics (learning rate, convergence, stopping rule); fast exponentiation for float and negative exponents; Horner's method; Taylor-series evaluation of exp / log / sin (names); floating-point summation: naive / Kahan compensated / Neumaier and pairwise summation; catastrophic cancellation and stable formulas (quadratic roots, log-sum-exp); floating-point comparison (absolute vs relative epsilon, ULPs); integer overflow and checked arithmetic; fixed-point arithmetic; rational arithmetic with gcd (fractions); big-integer arithmetic (add, subtract, multiply, divide by strings, base conversion); Lagrange and linear interpolation; Monte Carlo integration (cross-ref probability); golden-section search (cross-ref optimisation).

4. **Impartial games and Sprague-Grundy theory.** Winning / losing (N- / P-) position labelling; take-away game with a subtraction set (periodicity of win states); take 1..k (losing when n mod (k + 1) = 0, Bash game); Nim (XOR of pile sizes); misere Nim / normal-play Nim; mex (minimum excludant); Sprague-Grundy theorem; Grundy values by memoised DP; sum of independent games (XOR of Grundy values); Nim variants: Moore's Nim_k, staircase Nim, Poker Nim; pile-splitting games (Grundy's game, Kayles / Dawson's Kayles); Wythoff's game (golden ratio, Beatty sequences); Fibonacci Nim (Zeckendorf); Euclid's game; Chomp and strategy stealing; mirror / symmetry strategy; pairing strategy; parity strategies (count the moves, who moves last); coin-turning games (Turning Turtles; names); Green Hackenbush on trees; games on a DAG by retrograde analysis (win / lose / draw); games on graphs with cycles (draw states); games on trees; partizan games, surreal numbers and cold games (names).

5. **Adversarial search and game DP.** Minimax; negamax; alpha-beta pruning (move ordering, fail-soft); depth-limited search with an evaluation function; iterative deepening; transposition table (memoise the state; Zobrist keys, cross-ref hashing); game DP on an interval (l, r) / game DP as a win flag over a count; score-difference DP (current player's best margin: stone games, coins in a line, predict the winner); game DP over a bitmask of used choices (can-I-win); game DP with a prefix-sum cost (stone games II, III, V, VII); coins in a line (I, II, III); stone game parity proofs (first player wins on even length); take-away game DP (dp[i] is win or lose); games with draws (three-valued memo); territory games (binary-tree coloring game); greedy proofs for removal games (count of moves by colour); Tic-tac-toe win detection with counters; expectimax (chance nodes; names); Monte Carlo tree search and UCT (names); zero-sum matrix games, the minimax theorem and mixed strategies by LP (names); Nash equilibrium, prisoner's dilemma and auctions (names).

6. **Single-machine and multi-machine scheduling.** FIFO; shortest job first / shortest remaining time first; Smith's rule (weighted completion time); earliest deadline first (EDF); earliest due date / Jackson's rule (minimise maximum lateness); Moore-Hodgson (minimum number of late jobs, heap of durations); job sequencing with deadlines and profits (sort by profit, DSU for free slots); weighted job scheduling (sort by end, DP with binary search); interval scheduling (earliest finish time) / activity selection; interval partitioning / minimum meeting rooms (heap of end times / sweep line over events); minimum number of platforms (sweep); room assignment with ties (meeting rooms III: two heaps); non-overlapping intervals and minimum removals; maximum events attended (sort by start, heap of ends); course schedule III (sort by deadline, max-heap of durations); task scheduler with cooldown (counting formula / heap with cooldown queue); rearrange with distance k (cooldown on characters); single-threaded CPU (sort by arrival, heap by duration); priority scheduling and aging; round robin (time quantum, queue simulation); multilevel feedback queue; lottery and stride scheduling (names); CFS (names); rate-monotonic and deadline-monotonic scheduling (utilisation bound; names); list scheduling and LPT on parallel machines; makespan minimisation by binary search + greedy check; Johnson's rule (two-machine flow shop); critical path method and PERT (cross-ref DAG longest path); precedence-constrained scheduling (cross-ref topological order); preemptive vs non-preemptive variants.

7. **Resource allocation, load balancing and packing.** Round robin / weighted round robin; least connections and least loaded (heap); power of two choices; join-the-shortest-queue; consistent hashing for balancing (cross-ref hashing); work stealing (cross-ref concurrency); server assignment with two heaps (free servers by weight, busy servers by finish time); bin packing heuristics: next-fit / first-fit / best-fit / worst-fit; first-fit decreasing / best-fit decreasing (11/9 bound; names); online vs offline packing; cutting stock and strip packing (names); knapsack variants (cross-ref DP): 0/1 / unbounded / bounded, fractional knapsack (greedy by ratio), multi-dimensional knapsack, subset-sum by bitset, meet in the middle for huge weights; assignment problem by bitmask DP; Hungarian algorithm (cross-ref matching); min-cost flow formulation of assignment (cross-ref flow); two-city scheduling (greedy by cost difference); stable matching (Gale-Shapley; names for stable roommates); fair division and cake cutting (names); max-min fairness and water-filling; capacity over time with a difference array (car pooling, booking); circular feasibility and reset (gas station); Banker's algorithm and deadlock avoidance (names); deadlock detection on a resource-allocation graph (cross-ref cycle detection); budgeted selection with a heap (hire K workers, furthest building).

8. **Search on the answer and monotone constraints.** Two pointers on a monotone constraint (window grows while valid, shrinks when not) / sliding window as a monotone predicate; binary search on the answer, minimise-the-maximum / maximise-the-minimum; feasibility check by greedy / by counting (k-th smallest pair distance, k-th element of a multiplication table or sorted matrix); binary search on reals (iteration count, precision); parametric search; ternary search for unimodal functions on integers / on reals; plateaus that break ternary search; golden-section search; binary search on a changing slope (peak, mountain array); fractional programming by binary search on the ratio / Dinkelbach's method; exponential (galloping) search; binary search over an interactive predicate; nested binary searches; binary search with a union-find or DP check; parallel binary search (offline; names); binary lifting search on a monotone function.

9. **DP optimisation techniques.** Convex hull trick (monotone slopes with a deque / binary search on the hull); Li Chao tree (arbitrary lines, segments); dynamic convex hull (set-based); Lagrangian relaxation / "aliens trick" (WQS binary search on the penalty); slope trick (convex function kept in heaps); divide and conquer optimisation (monotone opt, quadrangle inequality); Knuth optimisation (interval DP, O(n^2)); SMAWK and totally monotone matrices; Monge arrays; monotone-queue optimisation (sliding-window minimum DP); bitset optimisation (knapsack, LCS); DP accelerated by a segment tree or BIT (LIS and counting variants); Garsia-Wachs and Hu-Tucker (names); SOS DP and subset DP speed-ups (cross-ref transforms); matrix exponentiation for linear-recurrence DP (cross-ref linear algebra); CDQ divide and conquer for DP (names); checking the preconditions (convexity, monotone opt, Monge) before applying any of these.

10. **Exact search and exponential-time techniques.** Meet in the middle (split, enumerate both halves, sort + two pointers or hash); branch and bound (bounding function, best-first order; knapsack, TSP); backtracking with pruning and ordering; iterative-deepening DFS and IDA* (cross-ref A*); subset and submask enumeration (2^n, 3^n); Gray-code enumeration; bitmask DP over subsets (cross-ref graph DP); inclusion-exclusion over subsets; exact cover by Algorithm X and dancing links (cross-ref backtracking); SAT and DPLL (names); constraint propagation and symmetry breaking; dominance pruning; randomised restarts (names).

11. **Mathematical programming and heuristic optimisation (names).** Linear programming: standard form, feasible region and vertices; simplex (tableau, pivot rules, Bland's rule); LP duality (weak, strong; complementary slackness); interior-point and ellipsoid methods; integer linear programming: branch and bound / cutting planes and branch and cut; LP relaxation and rounding; total unimodularity; transportation and assignment problems as LPs; network simplex and min-cost flow (cross-ref flow); difference constraints (cross-ref graph); Lagrange multipliers and convex optimisation; gradient descent and SGD (cross-ref numeric methods); hill climbing; simulated annealing; tabu search; genetic algorithms; approximation algorithms (vertex-cover 2-approximation, greedy set cover, Christofides); matroid greedy and exchange arguments; greedy for submodular maximisation.

12. **Probability and expectation.** Expected value DP (dp[state] = sum of probability times dp[next]); probability DP (dice sums, random walk on a grid, knight probability); probability DP with a sliding window (New 21 Game); linearity of expectation and indicator variables; geometric waiting time and the coupon collector; Markov chains: transition matrix and its powers / stationary distribution; absorbing Markov chains (fundamental matrix, elimination); random walks on graphs (cross-ref PageRank); gambler's ruin; maximum-probability path (Dijkstra on products or on -log p); Bayes updates (prior, likelihood, posterior) / naive Bayes counting; conditional probability and the law of total probability; birthday paradox and collision bounds (hash tables, Bloom filters); Monte Carlo estimation (a sampled estimate of pi or of an expectation); Monte Carlo integration; secretary problem (1/e stopping rule; names); expected running time of randomised algorithms (quickselect); inclusion-exclusion probabilities; variance and concentration bounds (Chernoff, names).

13. **Randomised algorithms and sampling.** Reservoir sampling (k = 1 / k > 1); weighted reservoir sampling (A-Res; names); Fisher-Yates (Knuth) shuffle; random permutation and the biased-shuffle pitfall; random pick with weight (prefix sums + binary search) / alias method (Vose); rejection sampling (rand7 to rand10; uniform point in a circle); inverse-transform sampling; random pick with a blacklist (remap into the tail); insert / delete / get-random in O(1) (array + hash map swap-delete); random point in non-overlapping rectangles (weighted by area); random node of a linked list (reservoir); sampling without replacement (Floyd's algorithm); Monte Carlo vs Las Vegas algorithms; randomised quicksort and quickselect pivots; Karger's minimum cut (names); randomised primality test (cross-ref number theory); universal hashing (cross-ref hashing); probabilistic data structures: Bloom filter / count-min sketch / HyperLogLog / MinHash (names); pseudo-random generators: LCG / xorshift / Mersenne Twister (names); randomised rounding (names).

14. **Simulation.** Direct step-by-step simulation; event-driven simulation (priority queue by time, event types, tie-breaking) / fixed time-step simulation; queue simulation (single server / many servers, waiting time); bank and teller simulation; elevator simulation (state machine; SCAN / LOOK ordering); parking and reservation systems; order-book and backlog matching (two heaps); cellular automata (1-D rules; names) / Game of Life (in-place with encoded states, double buffer); grid simulation (spiral, rotation, gravity, candy crush); robot walking (direction vector, obstacle set, cycle after four rounds); collisions (stack for asteroids and robots); circular elimination / Josephus (queue simulation, recurrence J(n, k) = (J(n - 1, k) + k) mod n, closed form for k = 2); snake game (deque + set); Tic-tac-toe and board-game state; card and deck processes (reveal cards: simulate in reverse); text-editor cursor (two stacks); time compression (jump to the next event); cycle detection to skip steps (state repeats after N days); simulating in reverse; invariants and step bounds; Monte Carlo simulation (cross-ref probability).

15. **Compression and coding.** Run-length encoding (encode / decode; in-place string compression; operations on run-length arrays; compressed-string iterator); Huffman coding (heap merges; canonical codes; optimal merge pattern as the same greedy); arithmetic coding and range coding; ANS (names); LZ77 / LZ78 / LZW; DEFLATE and gzip (LZ77 plus Huffman; names); Burrows-Wheeler transform and move-to-front; dictionary coding (names); delta encoding / varint (LEB128) / zigzag encoding; Elias gamma-delta and Golomb-Rice codes (names); prefix codes and the Kraft inequality; entropy and the lower bound; bit packing; base-62 and base64 encodings; length-prefixed and delimiter-escaped serialisation (encode and decode strings); error-detecting and error-correcting codes: parity / Hamming / Reed-Solomon (names); Gray code; shortest-encoding string by interval DP.

16. **Checksums and hash functions.** Parity and additive checksums; Fletcher and Adler-32; CRC (polynomial division over GF(2), table-driven CRC-32); FNV-1a; djb2; MurmurHash3 and xxHash (names); CityHash and SipHash (hash-flooding resistance; names); polynomial rolling hash (cross-ref Rabin-Karp); multiplicative / Fibonacci hashing; universal hashing; Zobrist hashing; tabulation hashing (names); perfect hashing (names); cryptographic hashes MD5 / SHA-1 / SHA-2 / SHA-3 / BLAKE (names; Merkle-Damgard vs sponge); HMAC (names); Merkle trees; hash table design: separate chaining / open addressing (linear probing, double hashing, Robin Hood, cuckoo); load factor and rehashing; hash set and hash map design; consistent hashing (ring with virtual nodes) / rendezvous (HRW) hashing; jump hash and Maglev (names); locality-sensitive hashing and SimHash (names); canonical-form hashing of structures (shapes of islands, trees); password hashing: bcrypt / scrypt / Argon2 (names); fingerprinting and deduplication.

17. **Cache and memory algorithms.** LRU (hash map + doubly linked list); LFU (frequency buckets, O(1)); MRU; FIFO; CLOCK / second chance; NRU; LRU-K and 2Q (names); ARC and LIRS (names); TinyLFU (names); random replacement; Belady's optimal (MIN, offline, furthest in the future); page replacement comparison and Belady's anomaly; working set model; write policies: write-through / write-back / write-around; TTL expiry (lazy vs active; timer wheel); cache-aside and cache stampede (names); memory allocators: first-fit / best-fit / worst-fit free lists; buddy system; slab allocator (names); arena / bump and pool allocators; coalescing and fragmentation; TLSF, jemalloc, tcmalloc (names); garbage collection: reference counting / mark-sweep / copying / generational (names); memory-allocator design problems (allocate and free by id); virtual memory, paging and TLB (names); locality, blocking and loop tiling; ring buffers; snapshot and persistent arrays (versioned reads).

18. **Concurrency algorithms (names).** Mutual exclusion in software: Peterson's / Dekker's / Lamport's bakery; test-and-set and ticket spinlocks; MCS and CLH queue locks; semaphores; monitors and condition variables; producer / consumer (bounded buffer); readers-writers (reader-preference, writer-preference, fair); dining philosophers (resource hierarchy, waiter, Chandy-Misra); sleeping barber; barriers; deadlock conditions, lock ordering and detection; livelock and starvation; lock-free CAS loops / ABA problem; Treiber stack and Michael-Scott queue; hazard pointers and epoch-based reclamation; RCU and seqlocks; memory ordering and fences; fetch-and-add and atomic counters; wait-free vs lock-free vs obstruction-free; double-checked locking; work-stealing deque and thread pools; striped and concurrent hash maps; ordering threads by signals (print in order, alternating); actor model and CSP channels.

19. **Rate limiting and admission control.** Token bucket; leaky bucket as a meter / leaky bucket as a queue; fixed-window counter; sliding-window log; sliding-window counter; GCRA (names); hit counter and moving window with a queue; per-key limiter with timestamps (logger rate limiter); time-bucketed counters in a ring buffer; per-key state eviction; concurrency limiter; distributed rate limiting (central counter, token pre-allocation; names); exponential backoff with jitter; circuit breaker; load shedding and backpressure; weighted fair queuing (names); retry budgets and quotas (names).

20. **Distributed algorithms (names only).** Consistent hashing and rendezvous hashing (cross-ref hashing); gossip / epidemic protocols and SWIM; failure detectors (heartbeat, phi accrual); leader election (bully, ring); consensus: Paxos (single-decree, multi-Paxos) / Raft / Viewstamped Replication / Zab; Byzantine fault tolerance (PBFT); logical clocks: Lamport / vector clocks / version vectors / hybrid logical clocks; CRDTs (G-counter, PN-counter, OR-set, LWW-register, sequence CRDTs) and operational transformation; two-phase commit / three-phase commit / saga; quorum reads and writes (R + W > N); Chandy-Lamport snapshots; anti-entropy and Merkle trees; replication: primary-backup / chain replication; sharding and partitioning; distributed id generation (Snowflake, UUID, ULID); distributed locks (leases, fencing tokens); clock synchronisation (NTP, TrueTime); MapReduce shuffle; CAP / PACELC, linearizability vs serialisability; idempotency and exactly-once delivery.

21. **Core implementation patterns.** Sort by key then sweep; event list of (time, kind) with a defined tie-break; min-heap / max-heap and tuple ordering; lazy deletion in a heap; two heaps (median, free / busy); difference array; monotone deque; ring buffer and circular index (mod n); hash map + array with swap-delete; hash map + doubly linked list; counting arrays; bitsets and bitmasks; double buffer vs in-place state encoding; memo keys (mask + position, state tuples); fixed iteration count for real-valued search; epsilon comparison; modular arithmetic (inverse by Fermat, wide intermediates); overflow-safe midpoint; carry loops for big numbers; an injectable clock for time-based designs; seeded RNG for reproducible tests; Rust: `Reverse` for a min-heap, `f64::total_cmp` or an ordered wrapper for float keys, `VecDeque`, `BTreeMap` for ordered state, `checked_*` / `wrapping_*` arithmetic.

## Problems in the data

Example problems per group, taken from `content/dsa/problems.json` and `content/dsa/practice.json` only. Each line is
`LeetCode <number> <title> (<difficulty>; <lists>)`. Where nothing in the data fits the group, the line says so, and any closest
neighbour is named as such. The data has no Concurrency, Rate Limiting or Rejection Sampling tag and no Nim, Divisor Game, Rand10,
Print in Order or Soup Servings problem.

**1. Transforms and convolution.** No problem in the data needs a transform. The closest is the schoolbook form of big-number multiplication that Karatsuba and FFT replace, and a subset-enumeration problem for the zeta / SOS family:
- LeetCode 43 Multiply Strings (medium; neetcode150, neetcode250, all)
- LeetCode 2044 Count Number of Maximum Bitwise-OR Subsets (medium; all)

**2. Linear algebra.**
- LeetCode 311 Sparse Matrix Multiplication (medium; all)
- LeetCode 1570 Dot Product of Two Sparse Vectors (medium; all)
- LeetCode 421 Maximum XOR of Two Numbers in an Array (medium; practice)

No elimination, determinant or matrix-inverse problem is in the data; 421 is solved with a trie and is the closest neighbour of the XOR linear basis.

**3. Numeric methods.**
- LeetCode 69 Sqrt(x) (easy; neetcode250, all)
- LeetCode 367 Valid Perfect Square (easy; all)
- LeetCode 50 Pow(x, n) (medium; neetcode150, neetcode250, all)
- LeetCode 774 Minimize Max Distance to Gas Station (hard; all)

**4. Impartial games and Sprague-Grundy theory.** No Nim, Sprague-Grundy, mex, misere or take-away problem is in the data. Closest, both tagged Game Theory or about a counting / territory strategy:
- LeetCode 2038 Remove Colored Pieces if Both Neighbors are the Same Color (medium; all)
- LeetCode 1145 Binary Tree Coloring Game (medium; practice)

**5. Adversarial search and game DP.**
- LeetCode 877 Stone Game (medium; neetcode250, all)
- LeetCode 1406 Stone Game III (hard; neetcode250, all)
- LeetCode 486 Predict the Winner (medium; practice)
- LeetCode 464 Can I Win (medium; practice)

**6. Single-machine and multi-machine scheduling.**
- LeetCode 621 Task Scheduler (medium; neetcode150, neetcode250, all)
- LeetCode 253 Meeting Rooms II (medium; blind75, neetcode150, neetcode250, all)
- LeetCode 1235 Maximum Profit in Job Scheduling (hard; all)
- LeetCode 630 Course Schedule III (hard; practice)

**7. Resource allocation, load balancing and packing.**
- LeetCode 1029 Two City Scheduling (medium; all)
- LeetCode 1882 Process Tasks Using Servers (medium; all)
- LeetCode 1094 Car Pooling (medium; neetcode250, all)
- LeetCode 416 Partition Equal Subset Sum (medium; neetcode150, neetcode250, all)

**8. Search on the answer and monotone constraints.**
- LeetCode 875 Koko Eating Bananas (medium; neetcode150, neetcode250, all)
- LeetCode 410 Split Array Largest Sum (hard; neetcode250, all)
- LeetCode 719 Find K-th Smallest Pair Distance (hard; all)
- LeetCode 852 Peak Index in a Mountain Array (medium; practice)

**9. DP optimisation techniques.** No problem in the data needs the convex hull trick, a Li Chao tree, the aliens trick, the slope trick or SMAWK. Interval and partition DPs where Knuth or divide-and-conquer optimisation is an optional speed-up:
- LeetCode 1547 Minimum Cost to Cut a Stick (hard; all)
- LeetCode 1000 Minimum Cost to Merge Stones (hard; practice)
- LeetCode 410 Split Array Largest Sum (hard; neetcode250, all)

**10. Exact search and exponential-time techniques.**
- LeetCode 805 Split Array With Same Average (hard; all)
- LeetCode 2035 Partition Array Into Two Arrays to Minimize Sum Difference (hard; practice)
- LeetCode 1723 Find Minimum Time to Finish All Jobs (hard; practice)
- LeetCode 679 24 Game (hard; practice)

**11. Mathematical programming and heuristic optimisation (names).** No problem in the data. LeetCode 1029 Two City Scheduling (listed in group 7) is tagged Hungarian Algorithm and Successive Shortest Path Algorithm and is the only min-cost-flow-flavoured neighbour.

**12. Probability and expectation.**
- LeetCode 837 New 21 Game (medium; all)
- LeetCode 688 Knight Probability in Chessboard (medium; practice)
- LeetCode 1514 Path with Maximum Probability (medium; all)

**13. Randomised algorithms and sampling.**
- LeetCode 528 Random Pick with Weight (medium; all)
- LeetCode 382 Linked List Random Node (medium; practice)
- LeetCode 384 Shuffle an Array (medium; practice)
- LeetCode 710 Random Pick with Blacklist (hard; practice)

**14. Simulation.**
- LeetCode 289 Game of Life (medium; practice)
- LeetCode 1823 Find the Winner of the Circular Game (medium; all)
- LeetCode 874 Walking Robot Simulation (medium; all)
- LeetCode 1834 Single-Threaded CPU (medium; neetcode250, all)

**15. Compression and coding.**
- LeetCode 443 String Compression (medium; all)
- LeetCode 1868 Product of Two Run-Length Encoded Arrays (medium; all)
- LeetCode 604 Design Compressed String Iterator (easy; all)
- LeetCode 1167 Minimum Cost to Connect Sticks (medium; all)

**16. Checksums and hash functions.**
- LeetCode 705 Design HashSet (easy; neetcode250, all)
- LeetCode 706 Design HashMap (easy; neetcode250, all)
- LeetCode 535 Encode and Decode TinyURL (medium; all)
- LeetCode 187 Repeated DNA Sequences (medium; all)

**17. Cache and memory algorithms.**
- LeetCode 146 LRU Cache (medium; neetcode150, neetcode250, all)
- LeetCode 460 LFU Cache (hard; neetcode250, all)
- LeetCode 2502 Design Memory Allocator (medium; practice)
- LeetCode 1146 Snapshot Array (medium; practice)

**18. Concurrency algorithms (names).** No problem in the data.

**19. Rate limiting and admission control.**
- LeetCode 359 Logger Rate Limiter (easy; all)
- LeetCode 362 Design Hit Counter (medium; all)
- LeetCode 1348 Tweet Counts Per Frequency (medium; practice)
- LeetCode 346 Moving Average from Data Stream (easy; all)

**20. Distributed algorithms (names only).** No problem in the data.

**21. Core implementation patterns.**
- LeetCode 380 Insert Delete GetRandom O(1) (medium; all)
- LeetCode 295 Find Median from Data Stream (hard; blind75, neetcode150, neetcode250, all)
- LeetCode 622 Design Circular Queue (medium; neetcode250, all)
- LeetCode 1094 Car Pooling (medium; neetcode250, all)
