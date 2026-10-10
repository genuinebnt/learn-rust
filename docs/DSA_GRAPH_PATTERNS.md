# Graph patterns: the exhaustive target list

The owner's list (2026-10-09) of every graph pattern that can come up on LeetCode, as the target for the Graphs and Advanced Graphs
pattern lessons. The rule is in [DSA.md](DSA.md), decision 32: a topic's patterns section is exhaustive, patterns without a NeetCode
problem get **example problems** from LeetCode, and variants of one pattern (DFS recursive / iterative) are **tabs** of one lesson.

Status: **partly built (2026-10-10)**: the page shows the groups, version tabs, example-only lessons and listed techniques; 5 of the "No lesson" patterns are written (DFS recursive/iterative, BFS by levels, bidirectional BFS, topological layers, 0-1 BFS) and the rest are listed by name. Until then it was documented only. Today `content/dsa/lessons/graphs.toml` has 12 techniques (simulation, degree, flood, clone, multi-bfs, border,
tree-walk, topo, dsu, bipartite, weighted, bfs-implicit) and `advanced-graphs.toml` has 7 (dijkstra, euler, mst, bellman, floyd, cycles,
articulation). Building the rest needs a mockup of the tabs first, then lessons and picked example problems.

Items written *a / b* in a group are variants for tabs where one lesson covers both (for example "DFS: recursive / iterative").

1. **Traversal.** DFS (recursive) / DFS (iterative, explicit stack) as tabs of one lesson; BFS (level-order); multi-source BFS; bidirectional BFS; flood fill; connected components; boundary-based traversal; reverse graph traversal; stateful traversal; path reconstruction; implicit graph traversal.
2. **Cycle detection and graph properties.** Undirected cycle: DFS / BFS / union-find; directed cycle: 3-color DFS / Kahn's algorithm; bipartite checking (BFS / DFS); odd-cycle detection; tree validation; functional graph cycle detection; Floyd's tortoise and hare; degree-based graph properties.
3. **Topological sort and dependencies.** DFS topological sort; Kahn's; dependency feasibility; dependency ordering; topological layers; unique topological ordering; ancestor propagation in DAGs; critical path in DAGs; DAG path counting; incremental dependency constraints.
4. **Union-find (DSU).** Basic; path compression; union by rank / size; component counting; redundant edge detection; grid union-find; DSU with component metadata; weighted / potential DSU; reverse-time connectivity; offline dynamic connectivity; rollback DSU; DSU on tree / small-to-large merging.
5. **Shortest paths.** Unweighted (BFS); multi-source; 0-1 BFS; Dijkstra (stale-entry skipping, path reconstruction); Bellman-Ford; negative-cycle detection; Floyd-Warshall; Johnson's; DAG shortest path; bidirectional; A*; with constraints / at most k stops; product-graph; shortest-path counting; k-shortest paths; minimax path; maximum-bottleneck path.
6. **Minimum spanning trees.** Kruskal; Prim; minimum spanning forest; maximum spanning tree; MST with preconnected vertices; bottleneck spanning tree; second-best MST; MST edge classification; Euclidean MST.
7. **Connectivity and graph decomposition.** SCC (Kosaraju / Tarjan); condensation DAG; bridges (low-link); articulation points; biconnected components; edge-biconnected components; bridge tree; block-cut tree; strong bridges; strong articulation points; vertex connectivity; edge connectivity; offline bridge queries; dominators.
8. **Matching and bipartite graphs.** Bipartite recognition; Kuhn's; Hopcroft-Karp; maximum bipartite matching; minimum vertex cover in bipartite graphs; Hall's theorem; Hungarian algorithm; blossom (general matching); minimum path cover in DAGs; maximum independent set in bipartite graphs.
9. **Network flow.** Ford-Fulkerson; Edmonds-Karp; Dinic; push-relabel; maximum flow; minimum cut; edge-disjoint paths; vertex-disjoint paths; bipartite matching via flow; circulation with demands; lower-bounded flow; min-cost max-flow; maximum closure; residual graph reasoning; super-source / super-sink.
10. **Tree algorithms.** Tree DFS / subtree aggregation; tree BFS; diameter; center; LCA; binary lifting; Euler tour / entry-exit timestamps; heavy-light decomposition; rerooting DP; centroid decomposition; tree DP; tree independent set / vertex cover; tree path queries; virtual tree; tree isomorphism / canonical encoding; rerooted subtree queries; tree matching / domination DP; DSU on tree.
11. **Graph dynamic programming.** DAG DP; longest path in DAG; path counting; shortest-path counting; bitmask DP over subsets; Hamiltonian path DP; TSP DP; DP over SCCs; graph coloring DP; independent-set DP; probability / expectation DP; resource-constrained state DP; meet-in-the-middle DP; treewidth / tree-decomposition DP.
12. **Graph modeling and state-space search.** Grid-to-graph; implicit graph; product / state-expanded graph; word transformation; constraint graph; dependency graph; keys-and-locks state graph; alternating-color / alternating-edge paths; parity-expanded graph; automaton x graph product; resource-constrained paths; time-expanded graph; reverse-time modeling; super-source / super-sink; virtual vertices; line graph / edge-state modeling; graph compression; terminal / boundary compression; dominance pruning.
13. **Eulerian and Hamiltonian.** Eulerian path / circuit; Hierholzer; directed Eulerian trail; itinerary reconstruction; De Bruijn sequence; Hamiltonian path / cycle; TSP; longest simple path.
14. **Backtracking and enumeration.** Simple path enumeration; all paths in a DAG; constrained path search; cycle enumeration; connected-subgraph enumeration; graph coloring by backtracking; clique search; maximum clique; maximum independent set; subgraph isomorphism; constraint propagation and branching; branch-and-bound; meet-in-the-middle enumeration.
15. **Advanced connectivity and offline algorithms.** Menger's theorem applications; SPQR trees; segment tree over time + rollback DSU; offline LCA (Tarjan); dynamic connectivity; dynamic bridge / connectivity maintenance; treewidth-based algorithms; planar graph algorithms; separator-based decomposition.
16. **Specialized graph algorithms.** Transitive closure / reduction; reachability bitsets; complement graph BFS; greedy graph coloring; minimum dominating set; graph centrality; PageRank / random walks; absorbing Markov chains; bipartite projection; graph sparsification; graph isomorphism; LCA in DAGs; minimum mean cycle (Karp); difference constraints; 2-SAT implication graph; min-cost circulation; algebraic path algorithms; bitset-optimized graph algorithms; external-memory graph algorithms; parallel graph traversal; approximation algorithms for hard graph problems.
17. **Core implementation patterns.** Adjacency list / matrix / edge list; reverse adjacency list; visitation states (white / gray / black); parent / predecessor arrays; discovery time + low-link arrays; indegree tracking; min-heap / priority queue; deque-based 0-1 BFS; residual edges; bitmask representation; coordinate-to-node mapping; state-to-node encoding; lazy neighbor generation; memoization over graph states; compact integer node ids; compressed sparse row (CSR); iterative traversal for deep graphs; stale priority-queue entry filtering; graph invariants and safe updates.

## Coverage today

How the 19 existing techniques (12 in Graphs, 7 in Advanced Graphs) map onto the 17 groups above, read from the lesson templates, signals and pitfalls in `content/dsa/lessons/graphs.toml` and `advanced-graphs.toml`. "Covered" means a template teaches the pattern (a missing tab for a second variant is noted); "partial" means a template touches it or teaches only one variant; "no lesson" means nothing in these two topics. Related lessons in other topics are named where they exist.

Techniques that map to no group: `Graphs:simulation` (checking a given order or procedure directly, no graph search). `Graphs:clone` maps to traversal (group 1) and to graph invariants (group 17).

### 1. Traversal

- **Existing lessons:** `Graphs:flood` (flood fill and component counting, an iterative DFS template), `Graphs:clone` (traversal with an old-to-new map as the visited set), `Graphs:multi-bfs` (multi-source BFS), `Graphs:border` (boundary-based traversal by reversing the question), `Graphs:bfs-implicit` (implicit graph traversal, BFS over generated states).
- **Covered (5):** multi-source BFS; flood fill; connected components; boundary-based traversal; implicit graph traversal
- **Partial (3):** DFS (recursive) / DFS (iterative, explicit stack) (iterative DFS only (flood, clone); no recursive tab); BFS (level-order) (BFS is inside multi-bfs and bfs-implicit, but there is no level-order lesson); reverse graph traversal (border walks uphill from the edge on a grid; no reverse adjacency list)
- **No lesson (3):** bidirectional BFS; stateful traversal; path reconstruction

### 2. Cycle detection and graph properties

- **Existing lessons:** `Graphs:dsu` (undirected cycle and tree validation through `union` returning False), `Graphs:topo` (directed cycle: fewer than n ordered), `Graphs:bipartite` (a colour clash is an odd cycle), `Advanced Graphs:cycles` (functional graphs), `Graphs:degree` (degree-based properties). Floyd's tortoise and hare is taught outside these topics, in `Linked List:fast-slow` (must-learn 141 Linked List Cycle).
- **Covered (4):** odd-cycle detection; tree validation; functional graph cycle detection; degree-based graph properties
- **Partial (3):** Undirected cycle: DFS / BFS / union-find (union-find (dsu) only; no DFS or BFS cycle tabs); directed cycle: 3-color DFS / Kahn's algorithm (Kahn's count in topo only; no 3-color DFS); bipartite checking (BFS / DFS) (BFS two-colouring only; no DFS tab)
- **No lesson (1):** Floyd's tortoise and hare

### 3. Topological sort and dependencies

- **Existing lessons:** `Graphs:topo` (Kahn's algorithm with an indegree array; feasibility by the ordered count; ordering).
- **Covered (3):** Kahn's; dependency feasibility; dependency ordering
- **Partial (0):** none
- **No lesson (7):** DFS topological sort; topological layers; unique topological ordering; ancestor propagation in DAGs; critical path in DAGs; DAG path counting; incremental dependency constraints

### 4. Union-find (DSU)

- **Existing lessons:** `Graphs:dsu` (find with path halving, union by size, group count, redundant edge from `union` returning False). `Advanced Graphs:mst` also carries a small DSU inside Kruskal.
- **Covered (5):** Basic; path compression; union by rank / size; component counting; redundant edge detection
- **Partial (1):** DSU with component metadata (the size array only; no merged min/max/xor payload)
- **No lesson (6):** grid union-find; weighted / potential DSU; reverse-time connectivity; offline dynamic connectivity; rollback DSU; DSU on tree / small-to-large merging

### 5. Shortest paths

- **Existing lessons:** `Graphs:bfs-implicit` and `Graphs:multi-bfs` (unweighted and multi-source BFS), `Advanced Graphs:dijkstra` (heap with stale-entry skipping), `Advanced Graphs:bellman` (Bellman-Ford rounds, at most k stops), `Advanced Graphs:floyd` (Floyd-Warshall), `Graphs:weighted` (a search whose weights multiply, not a shortest path).
- **Covered (5):** Unweighted (BFS); multi-source; Bellman-Ford; Floyd-Warshall; with constraints / at most k stops
- **Partial (2):** Dijkstra (stale-entry skipping, path reconstruction) (stale-entry skipping yes, path reconstruction no); minimax path (one pitfall line on a different combine step; no template)
- **No lesson (10):** 0-1 BFS; negative-cycle detection; Johnson's; DAG shortest path; bidirectional; A*; product-graph; shortest-path counting; k-shortest paths; maximum-bottleneck path

### 6. Minimum spanning trees

- **Existing lessons:** `Advanced Graphs:mst` (Kruskal with a DSU; its pitfalls mention Prim and the Euclidean case).
- **Covered (1):** Kruskal
- **Partial (3):** Prim (named in a pitfall, no template); minimum spanning forest (the template returns -1 when disconnected, but there is no forest variant); Euclidean MST (one pitfall line (Prim with an array is O(n squared)))
- **No lesson (5):** maximum spanning tree; MST with preconnected vertices; bottleneck spanning tree; second-best MST; MST edge classification

### 7. Connectivity and graph decomposition

- **Existing lessons:** `Advanced Graphs:articulation` (one lesson for bridges and articulation points with discovery time and low-link).
- **Covered (2):** bridges (low-link); articulation points
- **Partial (0):** none
- **No lesson (12):** SCC (Kosaraju / Tarjan); condensation DAG; biconnected components; edge-biconnected components; bridge tree; block-cut tree; strong bridges; strong articulation points; vertex connectivity; edge connectivity; offline bridge queries; dominators

### 8. Matching and bipartite graphs

- **Existing lessons:** `Graphs:bipartite` (recognition by two-colouring) is the only lesson here.
- **Covered (1):** Bipartite recognition
- **Partial (0):** none
- **No lesson (9):** Kuhn's; Hopcroft-Karp; maximum bipartite matching; minimum vertex cover in bipartite graphs; Hall's theorem; Hungarian algorithm; blossom (general matching); minimum path cover in DAGs; maximum independent set in bipartite graphs

### 9. Network flow

- **Existing lessons:** None.
- **Covered (0):** none
- **Partial (0):** none
- **No lesson (15):** Ford-Fulkerson; Edmonds-Karp; Dinic; push-relabel; maximum flow; minimum cut; edge-disjoint paths; vertex-disjoint paths; bipartite matching via flow; circulation with demands; lower-bounded flow; min-cost max-flow; maximum closure; residual graph reasoning; super-source / super-sink

### 10. Tree algorithms

- **Existing lessons:** `Graphs:tree-walk` (a tree given as an edge list, walked from a root with edge directions or costs). Outside these two topics: `Trees:dfs-return` (diameter, subtree values), `Trees:tree-as-graph`, `Trees:bfs-levels` and `Trees:dfs` cover binary-tree and n-ary-tree forms of tree DFS, tree BFS, diameter and tree DP.
- **Covered (0):** none
- **Partial (1):** Tree DFS / subtree aggregation (tree-walk walks an edge-list tree from a root; no subtree aggregation)
- **No lesson (17):** tree BFS; diameter; center; LCA; binary lifting; Euler tour / entry-exit timestamps; heavy-light decomposition; rerooting DP; centroid decomposition; tree DP; tree independent set / vertex cover; tree path queries; virtual tree; tree isomorphism / canonical encoding; rerooted subtree queries; tree matching / domination DP; DSU on tree

### 11. Graph dynamic programming

- **Existing lessons:** None in Graphs or Advanced Graphs. Related lessons elsewhere: `2-D Dynamic Programming:dfs-memo` (memoised DFS over a grid DAG), `1-D Dynamic Programming:count-states`, `1-D Dynamic Programming:bitmask`.
- **Covered (0):** none
- **Partial (0):** none
- **No lesson (14):** DAG DP; longest path in DAG; path counting; shortest-path counting; bitmask DP over subsets; Hamiltonian path DP; TSP DP; DP over SCCs; graph coloring DP; independent-set DP; probability / expectation DP; resource-constrained state DP; meet-in-the-middle DP; treewidth / tree-decomposition DP

### 12. Graph modeling and state-space search

- **Existing lessons:** `Graphs:flood` and `Graphs:multi-bfs` (grid to graph), `Graphs:bfs-implicit` (implicit graph, word transformation), `Graphs:topo` (dependency graph), `Graphs:weighted` (the ratio graph).
- **Covered (4):** Grid-to-graph; implicit graph; word transformation; dependency graph
- **Partial (2):** constraint graph (weighted covers the ratio graph only); super-source / super-sink (multi-bfs seeds one queue with all sources, which is a super-source without naming it)
- **No lesson (13):** product / state-expanded graph; keys-and-locks state graph; alternating-color / alternating-edge paths; parity-expanded graph; automaton x graph product; resource-constrained paths; time-expanded graph; reverse-time modeling; virtual vertices; line graph / edge-state modeling; graph compression; terminal / boundary compression; dominance pruning

### 13. Eulerian and Hamiltonian

- **Existing lessons:** `Advanced Graphs:euler` (Hierholzer's algorithm on a directed multigraph, itinerary reconstruction).
- **Covered (4):** Eulerian path / circuit; Hierholzer; directed Eulerian trail; itinerary reconstruction
- **Partial (0):** none
- **No lesson (4):** De Bruijn sequence; Hamiltonian path / cycle; TSP; longest simple path

### 14. Backtracking and enumeration

- **Existing lessons:** None in these topics. `Backtracking:grid` (must-learn 79 Word Search) covers constrained path search on a grid and is the nearest lesson.
- **Covered (0):** none
- **Partial (0):** none
- **No lesson (13):** Simple path enumeration; all paths in a DAG; constrained path search; cycle enumeration; connected-subgraph enumeration; graph coloring by backtracking; clique search; maximum clique; maximum independent set; subgraph isomorphism; constraint propagation and branching; branch-and-bound; meet-in-the-middle enumeration

### 15. Advanced connectivity and offline algorithms

- **Existing lessons:** None.
- **Covered (0):** none
- **Partial (0):** none
- **No lesson (9):** Menger's theorem applications; SPQR trees; segment tree over time + rollback DSU; offline LCA (Tarjan); dynamic connectivity; dynamic bridge / connectivity maintenance; treewidth-based algorithms; planar graph algorithms; separator-based decomposition

### 16. Specialized graph algorithms

- **Existing lessons:** None.
- **Covered (0):** none
- **Partial (0):** none
- **No lesson (21):** Transitive closure / reduction; reachability bitsets; complement graph BFS; greedy graph coloring; minimum dominating set; graph centrality; PageRank / random walks; absorbing Markov chains; bipartite projection; graph sparsification; graph isomorphism; LCA in DAGs; minimum mean cycle (Karp); difference constraints; 2-SAT implication graph; min-cost circulation; algebraic path algorithms; bitset-optimized graph algorithms; external-memory graph algorithms; parallel graph traversal; approximation algorithms for hard graph problems

### 17. Core implementation patterns

- **Existing lessons:** Taught implicitly by the templates rather than as lessons: adjacency lists (`Graphs:topo`, `Graphs:tree-walk`, `Advanced Graphs:dijkstra`), edge lists (`Advanced Graphs:mst`, `Advanced Graphs:bellman`), a matrix (`Advanced Graphs:floyd`), indegree (`Graphs:topo`), a heap (`Advanced Graphs:dijkstra`), discovery and low-link arrays (`Advanced Graphs:articulation`), lazy neighbour generation (`Graphs:bfs-implicit`), iterative traversal (`Graphs:flood`).
- **Covered (7):** Adjacency list / matrix / edge list; discovery time + low-link arrays; indegree tracking; min-heap / priority queue; lazy neighbor generation; iterative traversal for deep graphs; stale priority-queue entry filtering
- **Partial (4):** parent / predecessor arrays (only articulation passes a parent); coordinate-to-node mapping (grid cells are (r, c) tuples; no id mapping); state-to-node encoding (bfs-implicit keeps states as strings or tuples; no encoding lesson); compact integer node ids (one dsu pitfall line on mapping names to integer ids)
- **No lesson (8):** reverse adjacency list; visitation states (white / gray / black); deque-based 0-1 BFS; residual edges; bitmask representation; memoization over graph states; compressed sparse row (CSR); graph invariants and safe updates

Summary by group (patterns, covered, partial, no lesson):

| Group | Patterns | Covered | Partial | No lesson |
|---|---|---|---|---|
| 1. Traversal | 11 | 5 | 3 | 3 |
| 2. Cycle detection and graph properties | 8 | 4 | 3 | 1 |
| 3. Topological sort and dependencies | 10 | 3 | 0 | 7 |
| 4. Union-find (DSU) | 12 | 5 | 1 | 6 |
| 5. Shortest paths | 17 | 5 | 2 | 10 |
| 6. Minimum spanning trees | 9 | 1 | 3 | 5 |
| 7. Connectivity and graph decomposition | 14 | 2 | 0 | 12 |
| 8. Matching and bipartite graphs | 10 | 1 | 0 | 9 |
| 9. Network flow | 15 | 0 | 0 | 15 |
| 10. Tree algorithms | 18 | 0 | 1 | 17 |
| 11. Graph dynamic programming | 14 | 0 | 0 | 14 |
| 12. Graph modeling and state-space search | 19 | 4 | 2 | 13 |
| 13. Eulerian and Hamiltonian | 8 | 4 | 0 | 4 |
| 14. Backtracking and enumeration | 13 | 0 | 0 | 13 |
| 15. Advanced connectivity and offline algorithms | 9 | 0 | 0 | 9 |
| 16. Specialized graph algorithms | 21 | 0 | 0 | 21 |
| 17. Core implementation patterns | 19 | 7 | 4 | 8 |
| **Total** | **227** | **41** | **19** | **167** |

## Example problems per pattern

Every pattern of every group, one bullet each; variants written "a / b" in the list stay together as one pattern. Each problem is taken from `content/dsa/problems.json` or `content/dsa/practice.json` (the number, title, difficulty and lists are copied from the data by a generator script, and every line was checked against the data afterwards). Up to four per pattern. "No problem in the data" means no problem there fits; those patterns need an example from LeetCode, picked and checked against the site, never from memory (decision 32). A pattern marked *(nearest fits only)* has only problems that touch it without being a clean example (a similar technique, or a problem that can be solved that way); treat them as stand-ins until a better example is picked.

### 1. Traversal

- **DFS (recursive) / DFS (iterative, explicit stack)**
  - LeetCode 841 Keys and Rooms (medium; practice)
  - LeetCode 1971 Find if Path Exists in Graph (easy; practice)
  - LeetCode 133 Clone Graph (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 547 Number of Provinces (medium; all)
- **BFS (level-order)**
  - LeetCode 1311 Get Watched Videos by Your Friends (medium; practice)
  - LeetCode 1926 Nearest Exit from Entrance in Maze (medium; practice)
  - LeetCode 1091 Shortest Path in Binary Matrix (medium; all)
  - LeetCode 909 Snakes and Ladders (medium; all)
- **multi-source BFS**
  - LeetCode 994 Rotting Oranges (medium; neetcode150, neetcode250, all)
  - LeetCode 286 Walls and Gates (medium; neetcode150, neetcode250, all)
  - LeetCode 542 01 Matrix (medium; practice)
  - LeetCode 1162 As Far from Land as Possible (medium; all)
- **bidirectional BFS**
  - LeetCode 127 Word Ladder (hard; neetcode150, neetcode250, all)
  - LeetCode 752 Open the Lock (medium; neetcode250, all)
  - LeetCode 433 Minimum Genetic Mutation (medium; practice)
  - LeetCode 1197 Minimum Knight Moves (medium; all)
- **flood fill**
  - LeetCode 733 Flood Fill (easy; all)
  - LeetCode 200 Number of Islands (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 695 Max Area of Island (medium; neetcode150, neetcode250, all)
  - LeetCode 1992 Find All Groups of Farmland (medium; practice)
- **connected components**
  - LeetCode 323 Number of Connected Components in an Undirected Graph (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 547 Number of Provinces (medium; all)
  - LeetCode 2316 Count Unreachable Pairs of Nodes in an Undirected Graph (medium; practice)
  - LeetCode 2685 Count the Number of Complete Components (medium; all)
- **boundary-based traversal**
  - LeetCode 417 Pacific Atlantic Water Flow (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 130 Surrounded Regions (medium; neetcode150, neetcode250, all)
  - LeetCode 1020 Number of Enclaves (medium; all)
  - LeetCode 1254 Number of Closed Islands (medium; all)
- **reverse graph traversal**
  - LeetCode 417 Pacific Atlantic Water Flow (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 802 Find Eventual Safe States (medium; all)
  - LeetCode 1466 Reorder Routes to Make All Paths Lead to the City Zero (medium; all)
  - LeetCode 3650 Minimum Cost Path with Edge Reversals (medium; practice)
- **stateful traversal**
  - LeetCode 1129 Shortest Path with Alternating Colors (medium; all)
  - LeetCode 1293 Shortest Path in a Grid with Obstacles Elimination (hard; practice)
  - LeetCode 864 Shortest Path to Get All Keys (hard; practice)
  - LeetCode 1298 Maximum Candies You Can Get from Boxes (hard; practice)
- **path reconstruction**
  - LeetCode 126 Word Ladder II (hard; practice)
  - LeetCode 499 The Maze III (hard; all)
  - LeetCode 2096 Step-By-Step Directions From a Binary Tree Node to Another (medium; all)
  - LeetCode 332 Reconstruct Itinerary (hard; neetcode150, neetcode250, all)
- **implicit graph traversal**
  - LeetCode 752 Open the Lock (medium; neetcode250, all)
  - LeetCode 773 Sliding Puzzle (hard; all)
  - LeetCode 1553 Minimum Number of Days to Eat N Oranges (hard; all)
  - LeetCode 2998 Minimum Number of Operations to Make X and Y Equal (medium; practice)

### 2. Cycle detection and graph properties

- **Undirected cycle: DFS / BFS / union-find**
  - LeetCode 684 Redundant Connection (medium; neetcode150, neetcode250, all)
  - LeetCode 1559 Detect Cycles in 2D Grid (medium; practice)
  - LeetCode 261 Graph Valid Tree (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 2608 Shortest Cycle in a Graph (hard; practice)
- **directed cycle: 3-color DFS / Kahn's algorithm**
  - LeetCode 207 Course Schedule (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 210 Course Schedule II (medium; neetcode150, neetcode250, all)
  - LeetCode 802 Find Eventual Safe States (medium; all)
  - LeetCode 1059 All Paths from Source Lead to Destination (medium; all)
- **bipartite checking (BFS / DFS)**
  - LeetCode 785 Is Graph Bipartite? (medium; all)
  - LeetCode 886 Possible Bipartition (medium; practice)
  - LeetCode 2493 Divide Nodes Into the Maximum Number of Groups (hard; all)
- **odd-cycle detection**
  - LeetCode 785 Is Graph Bipartite? (medium; all)
  - LeetCode 886 Possible Bipartition (medium; practice)
  - LeetCode 2493 Divide Nodes Into the Maximum Number of Groups (hard; all)
- **tree validation**
  - LeetCode 261 Graph Valid Tree (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 1361 Validate Binary Tree Nodes (medium; all)
  - LeetCode 684 Redundant Connection (medium; neetcode150, neetcode250, all)
- **functional graph cycle detection**
  - LeetCode 2127 Maximum Employees to Be Invited to a Meeting (hard; all)
  - LeetCode 565 Array Nesting (medium; practice)
  - LeetCode 2359 Find Closest Node to Given Two Nodes (medium; all)
  - LeetCode 202 Happy Number (easy; neetcode150, neetcode250, all)
- **Floyd's tortoise and hare**
  - LeetCode 141 Linked List Cycle (easy; blind75, neetcode150, neetcode250, all)
  - LeetCode 142 Linked List Cycle II (medium; practice)
  - LeetCode 287 Find the Duplicate Number (medium; neetcode150, neetcode250, all)
  - LeetCode 202 Happy Number (easy; neetcode150, neetcode250, all)
- **degree-based graph properties**
  - LeetCode 997 Find the Town Judge (easy; neetcode250, all)
  - LeetCode 277 Find the Celebrity (medium; all)
  - LeetCode 1557 Minimum Number of Vertices to Reach All Nodes (medium; all)
  - LeetCode 2924 Find Champion II (medium; all)

### 3. Topological sort and dependencies

- **DFS topological sort**
  - LeetCode 210 Course Schedule II (medium; neetcode150, neetcode250, all)
  - LeetCode 269 Alien Dictionary (hard; blind75, neetcode150, neetcode250, all)
  - LeetCode 851 Loud and Rich (medium; practice)
  - LeetCode 329 Longest Increasing Path in a Matrix (hard; neetcode150, neetcode250, all)
- **Kahn's**
  - LeetCode 207 Course Schedule (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 210 Course Schedule II (medium; neetcode150, neetcode250, all)
  - LeetCode 1136 Parallel Courses (medium; all)
  - LeetCode 2115 Find All Possible Recipes from Given Supplies (medium; all)
- **dependency feasibility**
  - LeetCode 207 Course Schedule (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 2115 Find All Possible Recipes from Given Supplies (medium; all)
  - LeetCode 1059 All Paths from Source Lead to Destination (medium; all)
  - LeetCode 3481 Apply Substitutions (medium; all)
- **dependency ordering**
  - LeetCode 210 Course Schedule II (medium; neetcode150, neetcode250, all)
  - LeetCode 269 Alien Dictionary (hard; blind75, neetcode150, neetcode250, all)
  - LeetCode 2392 Build a Matrix With Conditions (hard; neetcode250, all)
- **topological layers**
  - LeetCode 1136 Parallel Courses (medium; all)
  - LeetCode 310 Minimum Height Trees (medium; neetcode250, all)
  - LeetCode 2603 Collect Coins in a Tree (hard; practice)
  - LeetCode 802 Find Eventual Safe States (medium; all)
- **unique topological ordering**
  - LeetCode 444 Sequence Reconstruction (medium; all)
- **ancestor propagation in DAGs**
  - LeetCode 2192 All Ancestors of a Node in a Directed Acyclic Graph (medium; practice)
  - LeetCode 1462 Course Schedule IV (medium; neetcode250, all)
  - LeetCode 851 Loud and Rich (medium; practice)
- **critical path in DAGs**
  - LeetCode 2050 Parallel Courses III (hard; all)
  - LeetCode 1857 Largest Color Value in a Directed Graph (hard; all)
  - LeetCode 329 Longest Increasing Path in a Matrix (hard; neetcode150, neetcode250, all)
- **DAG path counting**
  - LeetCode 1976 Number of Ways to Arrive at Destination (medium; all)
  - LeetCode 2328 Number of Increasing Paths in a Grid (hard; practice)
- **incremental dependency constraints** *(nearest fits only)*
  - LeetCode 631 Design Excel Sum Formula (hard; all)

### 4. Union-find (DSU)

- **Basic**
  - LeetCode 547 Number of Provinces (medium; all)
  - LeetCode 1971 Find if Path Exists in Graph (easy; practice)
  - LeetCode 323 Number of Connected Components in an Undirected Graph (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 721 Accounts Merge (medium; neetcode250, all)
- **path compression**
  - LeetCode 1101 The Earliest Moment When Everyone Become Friends (medium; all)
  - LeetCode 547 Number of Provinces (medium; all)
  - LeetCode 323 Number of Connected Components in an Undirected Graph (medium; blind75, neetcode150, neetcode250, all)
- **union by rank / size**
  - LeetCode 128 Longest Consecutive Sequence (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 305 Number of Islands II (hard; all)
  - LeetCode 1101 The Earliest Moment When Everyone Become Friends (medium; all)
  - LeetCode 2421 Number of Good Paths (hard; all)
- **component counting**
  - LeetCode 323 Number of Connected Components in an Undirected Graph (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 547 Number of Provinces (medium; all)
  - LeetCode 1319 Number of Operations to Make Network Connected (medium; practice)
  - LeetCode 2316 Count Unreachable Pairs of Nodes in an Undirected Graph (medium; practice)
- **redundant edge detection**
  - LeetCode 684 Redundant Connection (medium; neetcode150, neetcode250, all)
  - LeetCode 1319 Number of Operations to Make Network Connected (medium; practice)
  - LeetCode 1579 Remove Max Number of Edges to Keep Graph Fully Traversable (hard; all)
  - LeetCode 261 Graph Valid Tree (medium; blind75, neetcode150, neetcode250, all)
- **grid union-find**
  - LeetCode 305 Number of Islands II (hard; all)
  - LeetCode 959 Regions Cut By Slashes (medium; all)
  - LeetCode 130 Surrounded Regions (medium; neetcode150, neetcode250, all)
  - LeetCode 1905 Count Sub Islands (medium; all)
- **DSU with component metadata**
  - LeetCode 2492 Minimum Score of a Path Between Two Cities (medium; all)
  - LeetCode 3108 Minimum Cost Walk in Weighted Graph (hard; all)
  - LeetCode 2421 Number of Good Paths (hard; all)
  - LeetCode 1061 Lexicographically Smallest Equivalent String (medium; practice)
- **weighted / potential DSU**
  - LeetCode 399 Evaluate Division (medium; neetcode250, all)
- **reverse-time connectivity**
  - no problem in the data: needs one from LeetCode
- **offline dynamic connectivity** *(nearest fits only)*
  - LeetCode 2092 Find All People With Secret (hard; all)
  - LeetCode 2503 Maximum Number of Points From Grid Queries (hard; all)
- **rollback DSU** *(nearest fits only)*
  - LeetCode 2092 Find All People With Secret (hard; all)
- **DSU on tree / small-to-large merging**
  - no problem in the data: needs one from LeetCode

### 5. Shortest paths

- **Unweighted (BFS)**
  - LeetCode 1091 Shortest Path in Binary Matrix (medium; all)
  - LeetCode 909 Snakes and Ladders (medium; all)
  - LeetCode 752 Open the Lock (medium; neetcode250, all)
  - LeetCode 1926 Nearest Exit from Entrance in Maze (medium; practice)
- **multi-source**
  - LeetCode 994 Rotting Oranges (medium; neetcode150, neetcode250, all)
  - LeetCode 286 Walls and Gates (medium; neetcode150, neetcode250, all)
  - LeetCode 542 01 Matrix (medium; practice)
  - LeetCode 317 Shortest Distance from All Buildings (hard; all)
- **0-1 BFS**
  - LeetCode 1368 Minimum Cost to Make at Least One Valid Path in a Grid (hard; all)
  - LeetCode 2290 Minimum Obstacle Removal to Reach Corner (hard; all)
- **Dijkstra (stale-entry skipping, path reconstruction)**
  - LeetCode 743 Network Delay Time (medium; neetcode150, neetcode250, all)
  - LeetCode 1514 Path with Maximum Probability (medium; all)
  - LeetCode 1631 Path With Minimum Effort (medium; neetcode250, all)
  - LeetCode 505 The Maze II (medium; all)
- **Bellman-Ford**
  - LeetCode 787 Cheapest Flights Within K Stops (medium; neetcode150, neetcode250, all)
  - LeetCode 1334 Find the City With the Smallest Number of Neighbors at a Threshold Distance (medium; all)
- **negative-cycle detection**
  - no problem in the data: needs one from LeetCode
- **Floyd-Warshall**
  - LeetCode 1334 Find the City With the Smallest Number of Neighbors at a Threshold Distance (medium; all)
  - LeetCode 2976 Minimum Cost to Convert String I (medium; all)
  - LeetCode 399 Evaluate Division (medium; neetcode250, all)
  - LeetCode 2977 Minimum Cost to Convert String II (hard; practice)
- **Johnson's**
  - no problem in the data: needs one from LeetCode
- **DAG shortest path** *(nearest fits only)*
  - LeetCode 3620 Network Recovery Pathways (hard; practice)
- **bidirectional**
  - LeetCode 127 Word Ladder (hard; neetcode150, neetcode250, all)
  - LeetCode 752 Open the Lock (medium; neetcode250, all)
  - LeetCode 1197 Minimum Knight Moves (medium; all)
  - LeetCode 433 Minimum Genetic Mutation (medium; practice)
- **A***
  - LeetCode 499 The Maze III (hard; all)
  - LeetCode 505 The Maze II (medium; all)
  - LeetCode 773 Sliding Puzzle (hard; all)
  - LeetCode 1197 Minimum Knight Moves (medium; all)
- **with constraints / at most k stops**
  - LeetCode 787 Cheapest Flights Within K Stops (medium; neetcode150, neetcode250, all)
  - LeetCode 1293 Shortest Path in a Grid with Obstacles Elimination (hard; practice)
  - LeetCode 3970 Shortest Path With At Most K Consecutive Identical Characters (medium; practice)
- **product-graph**
  - LeetCode 1129 Shortest Path with Alternating Colors (medium; all)
  - LeetCode 1293 Shortest Path in a Grid with Obstacles Elimination (hard; practice)
  - LeetCode 864 Shortest Path to Get All Keys (hard; practice)
  - LeetCode 3970 Shortest Path With At Most K Consecutive Identical Characters (medium; practice)
- **shortest-path counting**
  - LeetCode 1976 Number of Ways to Arrive at Destination (medium; all)
- **k-shortest paths**
  - LeetCode 2045 Second Minimum Time to Reach Destination (hard; all)
- **minimax path**
  - LeetCode 778 Swim in Rising Water (hard; neetcode150, neetcode250, all)
  - LeetCode 1631 Path With Minimum Effort (medium; neetcode250, all)
  - LeetCode 3419 Minimize the Maximum Edge Weight of Graph (medium; practice)
- **maximum-bottleneck path**
  - LeetCode 1102 Path With Maximum Minimum Value (medium; all)
  - LeetCode 2812 Find the Safest Path in a Grid (medium; all)

### 6. Minimum spanning trees

- **Kruskal**
  - LeetCode 1584 Min Cost to Connect All Points (medium; neetcode150, neetcode250, all)
  - LeetCode 1489 Find Critical and Pseudo-Critical Edges in Minimum Spanning Tree (hard; neetcode250, all)
  - LeetCode 3600 Maximize Spanning Tree Stability with Upgrades (hard; practice)
- **Prim**
  - LeetCode 1584 Min Cost to Connect All Points (medium; neetcode150, neetcode250, all)
  - LeetCode 1489 Find Critical and Pseudo-Critical Edges in Minimum Spanning Tree (hard; neetcode250, all)
- **minimum spanning forest** *(nearest fits only)*
  - LeetCode 3613 Minimize Maximum Component Cost (medium; practice)
- **maximum spanning tree** *(nearest fits only)*
  - LeetCode 3600 Maximize Spanning Tree Stability with Upgrades (hard; practice)
- **MST with preconnected vertices** *(nearest fits only)*
  - LeetCode 3600 Maximize Spanning Tree Stability with Upgrades (hard; practice)
- **bottleneck spanning tree**
  - LeetCode 3419 Minimize the Maximum Edge Weight of Graph (medium; practice)
  - LeetCode 3613 Minimize Maximum Component Cost (medium; practice)
  - LeetCode 3600 Maximize Spanning Tree Stability with Upgrades (hard; practice)
  - LeetCode 778 Swim in Rising Water (hard; neetcode150, neetcode250, all)
- **second-best MST**
  - no problem in the data: needs one from LeetCode
- **MST edge classification**
  - LeetCode 1489 Find Critical and Pseudo-Critical Edges in Minimum Spanning Tree (hard; neetcode250, all)
- **Euclidean MST**
  - LeetCode 1584 Min Cost to Connect All Points (medium; neetcode150, neetcode250, all)

### 7. Connectivity and graph decomposition

- **SCC (Kosaraju / Tarjan)**
  - LeetCode 802 Find Eventual Safe States (medium; all)
  - LeetCode 1059 All Paths from Source Lead to Destination (medium; all)
  - LeetCode 2127 Maximum Employees to Be Invited to a Meeting (hard; all)
- **condensation DAG**
  - no problem in the data: needs one from LeetCode
- **bridges (low-link)**
  - no problem in the data: needs one from LeetCode
- **articulation points**
  - LeetCode 1568 Minimum Number of Days to Disconnect Island (hard; all)
- **biconnected components**
  - no problem in the data: needs one from LeetCode
- **edge-biconnected components**
  - no problem in the data: needs one from LeetCode
- **bridge tree**
  - no problem in the data: needs one from LeetCode
- **block-cut tree**
  - no problem in the data: needs one from LeetCode
- **strong bridges**
  - no problem in the data: needs one from LeetCode
- **strong articulation points**
  - no problem in the data: needs one from LeetCode
- **vertex connectivity**
  - no problem in the data: needs one from LeetCode
- **edge connectivity**
  - no problem in the data: needs one from LeetCode
- **offline bridge queries**
  - no problem in the data: needs one from LeetCode
- **dominators**
  - no problem in the data: needs one from LeetCode

### 8. Matching and bipartite graphs

- **Bipartite recognition**
  - LeetCode 785 Is Graph Bipartite? (medium; all)
  - LeetCode 886 Possible Bipartition (medium; practice)
  - LeetCode 2493 Divide Nodes Into the Maximum Number of Groups (hard; all)
- **Kuhn's**
  - no problem in the data: needs one from LeetCode
- **Hopcroft-Karp**
  - no problem in the data: needs one from LeetCode
- **maximum bipartite matching**
  - no problem in the data: needs one from LeetCode
- **minimum vertex cover in bipartite graphs**
  - no problem in the data: needs one from LeetCode
- **Hall's theorem**
  - no problem in the data: needs one from LeetCode
- **Hungarian algorithm** *(nearest fits only)*
  - LeetCode 1029 Two City Scheduling (medium; all)
- **blossom (general matching)**
  - no problem in the data: needs one from LeetCode
- **minimum path cover in DAGs**
  - no problem in the data: needs one from LeetCode
- **maximum independent set in bipartite graphs**
  - no problem in the data: needs one from LeetCode

### 9. Network flow

- **Ford-Fulkerson**
  - no problem in the data: needs one from LeetCode
- **Edmonds-Karp**
  - no problem in the data: needs one from LeetCode
- **Dinic**
  - no problem in the data: needs one from LeetCode
- **push-relabel**
  - no problem in the data: needs one from LeetCode
- **maximum flow** *(nearest fits only)*
  - LeetCode 1605 Find Valid Matrix Given Row and Column Sums (medium; all)
- **minimum cut**
  - no problem in the data: needs one from LeetCode
- **edge-disjoint paths**
  - no problem in the data: needs one from LeetCode
- **vertex-disjoint paths**
  - no problem in the data: needs one from LeetCode
- **bipartite matching via flow**
  - no problem in the data: needs one from LeetCode
- **circulation with demands**
  - no problem in the data: needs one from LeetCode
- **lower-bounded flow**
  - no problem in the data: needs one from LeetCode
- **min-cost max-flow**
  - no problem in the data: needs one from LeetCode
- **maximum closure**
  - no problem in the data: needs one from LeetCode
- **residual graph reasoning**
  - no problem in the data: needs one from LeetCode
- **super-source / super-sink**
  - no problem in the data: needs one from LeetCode

### 10. Tree algorithms

- **Tree DFS / subtree aggregation**
  - LeetCode 543 Diameter of Binary Tree (easy; neetcode150, neetcode250, all)
  - LeetCode 1120 Maximum Average Subtree (medium; all)
  - LeetCode 1443 Minimum Time to Collect All Apples in a Tree (medium; all)
  - LeetCode 2872 Maximum Number of K-Divisible Components (hard; all)
- **tree BFS**
  - LeetCode 102 Binary Tree Level Order Traversal (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 199 Binary Tree Right Side View (medium; neetcode150, neetcode250, all)
  - LeetCode 515 Find Largest Value in Each Tree Row (medium; all)
  - LeetCode 107 Binary Tree Level Order Traversal II (medium; practice)
- **diameter**
  - LeetCode 543 Diameter of Binary Tree (easy; neetcode150, neetcode250, all)
  - LeetCode 1245 Tree Diameter (medium; all)
  - LeetCode 1522 Diameter of N-Ary Tree (medium; all)
  - LeetCode 3203 Find Minimum Diameter After Merging Two Trees (hard; all)
- **center** *(nearest fits only)*
  - LeetCode 310 Minimum Height Trees (medium; neetcode250, all)
  - LeetCode 3203 Find Minimum Diameter After Merging Two Trees (hard; all)
- **LCA**
  - LeetCode 236 Lowest Common Ancestor of a Binary Tree (medium; all)
  - LeetCode 235 Lowest Common Ancestor of a Binary Search Tree (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 1650 Lowest Common Ancestor of a Binary Tree III (medium; all)
  - LeetCode 2096 Step-By-Step Directions From a Binary Tree Node to Another (medium; all)
- **binary lifting**
  - LeetCode 235 Lowest Common Ancestor of a Binary Search Tree (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 236 Lowest Common Ancestor of a Binary Tree (medium; all)
  - LeetCode 1650 Lowest Common Ancestor of a Binary Tree III (medium; all)
  - LeetCode 2096 Step-By-Step Directions From a Binary Tree Node to Another (medium; all)
- **Euler tour / entry-exit timestamps** *(nearest fits only)*
  - LeetCode 2458 Height of Binary Tree After Subtree Removal Queries (hard; practice)
- **heavy-light decomposition**
  - no problem in the data: needs one from LeetCode
- **rerooting DP**
  - LeetCode 2858 Minimum Edge Reversals So Every Node Is Reachable (hard; practice)
- **centroid decomposition**
  - no problem in the data: needs one from LeetCode
- **tree DP**
  - LeetCode 337 House Robber III (medium; neetcode250, all)
  - LeetCode 968 Binary Tree Cameras (hard; practice)
  - LeetCode 979 Distribute Coins in Binary Tree (medium; all)
  - LeetCode 124 Binary Tree Maximum Path Sum (hard; blind75, neetcode150, neetcode250, all)
- **tree independent set / vertex cover**
  - LeetCode 337 House Robber III (medium; neetcode250, all)
- **tree path queries**
  - LeetCode 2096 Step-By-Step Directions From a Binary Tree Node to Another (medium; all)
  - LeetCode 863 All Nodes Distance K in Binary Tree (medium; practice)
  - LeetCode 3067 Count Pairs of Connectable Servers in a Weighted Tree Network (medium; practice)
  - LeetCode 1530 Number of Good Leaf Nodes Pairs (medium; all)
- **virtual tree**
  - no problem in the data: needs one from LeetCode
- **tree isomorphism / canonical encoding**
  - LeetCode 652 Find Duplicate Subtrees (medium; all)
  - LeetCode 572 Subtree of Another Tree (easy; blind75, neetcode150, neetcode250, all)
  - LeetCode 951 Flip Equivalent Binary Trees (medium; all)
- **rerooted subtree queries** *(nearest fits only)*
  - LeetCode 2858 Minimum Edge Reversals So Every Node Is Reachable (hard; practice)
  - LeetCode 2458 Height of Binary Tree After Subtree Removal Queries (hard; practice)
- **tree matching / domination DP**
  - LeetCode 968 Binary Tree Cameras (hard; practice)
- **DSU on tree**
  - no problem in the data: needs one from LeetCode

### 11. Graph dynamic programming

- **DAG DP**
  - LeetCode 329 Longest Increasing Path in a Matrix (hard; neetcode150, neetcode250, all)
  - LeetCode 2328 Number of Increasing Paths in a Grid (hard; practice)
  - LeetCode 1857 Largest Color Value in a Directed Graph (hard; all)
  - LeetCode 2050 Parallel Courses III (hard; all)
- **longest path in DAG**
  - LeetCode 329 Longest Increasing Path in a Matrix (hard; neetcode150, neetcode250, all)
  - LeetCode 2050 Parallel Courses III (hard; all)
  - LeetCode 1857 Largest Color Value in a Directed Graph (hard; all)
- **path counting**
  - LeetCode 2328 Number of Increasing Paths in a Grid (hard; practice)
  - LeetCode 1976 Number of Ways to Arrive at Destination (medium; all)
- **shortest-path counting**
  - LeetCode 1976 Number of Ways to Arrive at Destination (medium; all)
- **bitmask DP over subsets** *(nearest fits only)*
  - LeetCode 698 Partition to K Equal Sum Subsets (medium; neetcode250, all)
  - LeetCode 526 Beautiful Arrangement (medium; practice)
  - LeetCode 1799 Maximize Score After N Operations (hard; all)
  - LeetCode 351 Android Unlock Patterns (medium; all)
- **Hamiltonian path DP**
  - LeetCode 980 Unique Paths III (hard; practice)
  - LeetCode 996 Number of Squareful Arrays (hard; practice)
  - LeetCode 351 Android Unlock Patterns (medium; all)
- **TSP DP** *(nearest fits only)*
  - LeetCode 864 Shortest Path to Get All Keys (hard; practice)
- **DP over SCCs** *(nearest fits only)*
  - LeetCode 2127 Maximum Employees to Be Invited to a Meeting (hard; all)
- **graph coloring DP**
  - no problem in the data: needs one from LeetCode
- **independent-set DP**
  - LeetCode 337 House Robber III (medium; neetcode250, all)
- **probability / expectation DP** *(nearest fits only)*
  - LeetCode 688 Knight Probability in Chessboard (medium; practice)
  - LeetCode 576 Out of Boundary Paths (medium; all)
- **resource-constrained state DP**
  - LeetCode 787 Cheapest Flights Within K Stops (medium; neetcode150, neetcode250, all)
  - LeetCode 1293 Shortest Path in a Grid with Obstacles Elimination (hard; practice)
  - LeetCode 3286 Find a Safe Walk Through a Grid (medium; practice)
  - LeetCode 3970 Shortest Path With At Most K Consecutive Identical Characters (medium; practice)
- **meet-in-the-middle DP** *(nearest fits only)*
  - LeetCode 2035 Partition Array Into Two Arrays to Minimize Sum Difference (hard; practice)
  - LeetCode 805 Split Array With Same Average (hard; all)
- **treewidth / tree-decomposition DP**
  - no problem in the data: needs one from LeetCode

### 12. Graph modeling and state-space search

- **Grid-to-graph**
  - LeetCode 200 Number of Islands (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 1091 Shortest Path in Binary Matrix (medium; all)
  - LeetCode 994 Rotting Oranges (medium; neetcode150, neetcode250, all)
  - LeetCode 1368 Minimum Cost to Make at Least One Valid Path in a Grid (hard; all)
- **implicit graph**
  - LeetCode 752 Open the Lock (medium; neetcode250, all)
  - LeetCode 773 Sliding Puzzle (hard; all)
  - LeetCode 909 Snakes and Ladders (medium; all)
  - LeetCode 1553 Minimum Number of Days to Eat N Oranges (hard; all)
- **product / state-expanded graph**
  - LeetCode 1129 Shortest Path with Alternating Colors (medium; all)
  - LeetCode 1293 Shortest Path in a Grid with Obstacles Elimination (hard; practice)
  - LeetCode 864 Shortest Path to Get All Keys (hard; practice)
  - LeetCode 3286 Find a Safe Walk Through a Grid (medium; practice)
- **word transformation**
  - LeetCode 127 Word Ladder (hard; neetcode150, neetcode250, all)
  - LeetCode 126 Word Ladder II (hard; practice)
  - LeetCode 433 Minimum Genetic Mutation (medium; practice)
- **constraint graph**
  - LeetCode 399 Evaluate Division (medium; neetcode250, all)
  - LeetCode 886 Possible Bipartition (medium; practice)
  - LeetCode 2101 Detonate the Maximum Bombs (medium; all)
  - LeetCode 737 Sentence Similarity II (medium; all)
- **dependency graph**
  - LeetCode 207 Course Schedule (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 2115 Find All Possible Recipes from Given Supplies (medium; all)
  - LeetCode 631 Design Excel Sum Formula (hard; all)
  - LeetCode 3481 Apply Substitutions (medium; all)
- **keys-and-locks state graph**
  - LeetCode 864 Shortest Path to Get All Keys (hard; practice)
  - LeetCode 1298 Maximum Candies You Can Get from Boxes (hard; practice)
  - LeetCode 841 Keys and Rooms (medium; practice)
- **alternating-color / alternating-edge paths**
  - LeetCode 1129 Shortest Path with Alternating Colors (medium; all)
- **parity-expanded graph**
  - LeetCode 2577 Minimum Time to Visit a Cell In a Grid (hard; all)
- **automaton x graph product** *(nearest fits only)*
  - LeetCode 3970 Shortest Path With At Most K Consecutive Identical Characters (medium; practice)
- **resource-constrained paths**
  - LeetCode 787 Cheapest Flights Within K Stops (medium; neetcode150, neetcode250, all)
  - LeetCode 1293 Shortest Path in a Grid with Obstacles Elimination (hard; practice)
  - LeetCode 3286 Find a Safe Walk Through a Grid (medium; practice)
  - LeetCode 3970 Shortest Path With At Most K Consecutive Identical Characters (medium; practice)
- **time-expanded graph**
  - LeetCode 2577 Minimum Time to Visit a Cell In a Grid (hard; all)
  - LeetCode 3341 Find Minimum Time to Reach Last Room I (medium; practice)
  - LeetCode 3342 Find Minimum Time to Reach Last Room II (medium; practice)
  - LeetCode 2045 Second Minimum Time to Reach Destination (hard; all)
- **reverse-time modeling**
  - no problem in the data: needs one from LeetCode
- **super-source / super-sink**
  - LeetCode 286 Walls and Gates (medium; neetcode150, neetcode250, all)
  - LeetCode 994 Rotting Oranges (medium; neetcode150, neetcode250, all)
  - LeetCode 1162 As Far from Land as Possible (medium; all)
  - LeetCode 542 01 Matrix (medium; practice)
- **virtual vertices**
  - LeetCode 815 Bus Routes (hard; all)
- **line graph / edge-state modeling** *(nearest fits only)*
  - LeetCode 1129 Shortest Path with Alternating Colors (medium; all)
- **graph compression**
  - LeetCode 947 Most Stones Removed with Same Row or Column (medium; practice)
  - LeetCode 2603 Collect Coins in a Tree (hard; practice)
- **terminal / boundary compression**
  - no problem in the data: needs one from LeetCode
- **dominance pruning** *(nearest fits only)*
  - LeetCode 1293 Shortest Path in a Grid with Obstacles Elimination (hard; practice)
  - LeetCode 3286 Find a Safe Walk Through a Grid (medium; practice)

### 13. Eulerian and Hamiltonian

- **Eulerian path / circuit**
  - LeetCode 332 Reconstruct Itinerary (hard; neetcode150, neetcode250, all)
- **Hierholzer**
  - LeetCode 332 Reconstruct Itinerary (hard; neetcode150, neetcode250, all)
- **directed Eulerian trail**
  - LeetCode 332 Reconstruct Itinerary (hard; neetcode150, neetcode250, all)
- **itinerary reconstruction**
  - LeetCode 332 Reconstruct Itinerary (hard; neetcode150, neetcode250, all)
- **De Bruijn sequence**
  - no problem in the data: needs one from LeetCode
- **Hamiltonian path / cycle**
  - LeetCode 980 Unique Paths III (hard; practice)
  - LeetCode 996 Number of Squareful Arrays (hard; practice)
- **TSP** *(nearest fits only)*
  - LeetCode 864 Shortest Path to Get All Keys (hard; practice)
- **longest simple path**
  - LeetCode 1219 Path with Maximum Gold (medium; all)
  - LeetCode 980 Unique Paths III (hard; practice)

### 14. Backtracking and enumeration

- **Simple path enumeration**
  - LeetCode 797 All Paths From Source to Target (medium; practice)
  - LeetCode 79 Word Search (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 1219 Path with Maximum Gold (medium; all)
  - LeetCode 257 Binary Tree Paths (easy; practice)
- **all paths in a DAG**
  - LeetCode 797 All Paths From Source to Target (medium; practice)
- **constrained path search**
  - LeetCode 79 Word Search (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 212 Word Search II (hard; blind75, neetcode150, neetcode250, all)
  - LeetCode 1219 Path with Maximum Gold (medium; all)
  - LeetCode 980 Unique Paths III (hard; practice)
- **cycle enumeration**
  - no problem in the data: needs one from LeetCode
- **connected-subgraph enumeration**
  - no problem in the data: needs one from LeetCode
- **graph coloring by backtracking** *(nearest fits only)*
  - LeetCode 1042 Flower Planting With No Adjacent (medium; practice)
- **clique search**
  - no problem in the data: needs one from LeetCode
- **maximum clique**
  - no problem in the data: needs one from LeetCode
- **maximum independent set**
  - no problem in the data: needs one from LeetCode
- **subgraph isomorphism**
  - no problem in the data: needs one from LeetCode
- **constraint propagation and branching**
  - LeetCode 37 Sudoku Solver (hard; practice)
- **branch-and-bound** *(nearest fits only)*
  - LeetCode 1723 Find Minimum Time to Finish All Jobs (hard; practice)
  - LeetCode 2305 Fair Distribution of Cookies (medium; practice)
- **meet-in-the-middle enumeration** *(nearest fits only)*
  - LeetCode 2035 Partition Array Into Two Arrays to Minimize Sum Difference (hard; practice)
  - LeetCode 805 Split Array With Same Average (hard; all)

### 15. Advanced connectivity and offline algorithms

- **Menger's theorem applications**
  - no problem in the data: needs one from LeetCode
- **SPQR trees**
  - no problem in the data: needs one from LeetCode
- **segment tree over time + rollback DSU**
  - no problem in the data: needs one from LeetCode
- **offline LCA (Tarjan)**
  - no problem in the data: needs one from LeetCode
- **dynamic connectivity** *(nearest fits only)*
  - LeetCode 305 Number of Islands II (hard; all)
  - LeetCode 3243 Shortest Distance After Road Addition Queries I (medium; all)
- **dynamic bridge / connectivity maintenance**
  - no problem in the data: needs one from LeetCode
- **treewidth-based algorithms**
  - no problem in the data: needs one from LeetCode
- **planar graph algorithms** *(nearest fits only)*
  - LeetCode 959 Regions Cut By Slashes (medium; all)
- **separator-based decomposition**
  - no problem in the data: needs one from LeetCode

### 16. Specialized graph algorithms

- **Transitive closure / reduction**
  - LeetCode 1462 Course Schedule IV (medium; neetcode250, all)
  - LeetCode 2192 All Ancestors of a Node in a Directed Acyclic Graph (medium; practice)
- **reachability bitsets** *(nearest fits only)*
  - LeetCode 1462 Course Schedule IV (medium; neetcode250, all)
  - LeetCode 2192 All Ancestors of a Node in a Directed Acyclic Graph (medium; practice)
- **complement graph BFS**
  - no problem in the data: needs one from LeetCode
- **greedy graph coloring**
  - LeetCode 1042 Flower Planting With No Adjacent (medium; practice)
- **minimum dominating set** *(nearest fits only)*
  - LeetCode 968 Binary Tree Cameras (hard; practice)
- **graph centrality**
  - no problem in the data: needs one from LeetCode
- **PageRank / random walks** *(nearest fits only)*
  - LeetCode 688 Knight Probability in Chessboard (medium; practice)
- **absorbing Markov chains**
  - no problem in the data: needs one from LeetCode
- **bipartite projection**
  - no problem in the data: needs one from LeetCode
- **graph sparsification**
  - no problem in the data: needs one from LeetCode
- **graph isomorphism** *(nearest fits only)*
  - LeetCode 694 Number of Distinct Islands (medium; all)
  - LeetCode 711 Number of Distinct Islands II (hard; all)
- **LCA in DAGs**
  - no problem in the data: needs one from LeetCode
- **minimum mean cycle (Karp)**
  - no problem in the data: needs one from LeetCode
- **difference constraints**
  - no problem in the data: needs one from LeetCode
- **2-SAT implication graph**
  - no problem in the data: needs one from LeetCode
- **min-cost circulation**
  - no problem in the data: needs one from LeetCode
- **algebraic path algorithms**
  - no problem in the data: needs one from LeetCode
- **bitset-optimized graph algorithms**
  - no problem in the data: needs one from LeetCode
- **external-memory graph algorithms**
  - no problem in the data: needs one from LeetCode
- **parallel graph traversal**
  - no problem in the data: needs one from LeetCode
- **approximation algorithms for hard graph problems**
  - no problem in the data: needs one from LeetCode

### 17. Core implementation patterns

- **Adjacency list / matrix / edge list**
  - LeetCode 547 Number of Provinces (medium; all)
  - LeetCode 997 Find the Town Judge (easy; neetcode250, all)
  - LeetCode 1971 Find if Path Exists in Graph (easy; practice)
  - LeetCode 133 Clone Graph (medium; blind75, neetcode150, neetcode250, all)
- **reverse adjacency list**
  - LeetCode 802 Find Eventual Safe States (medium; all)
  - LeetCode 851 Loud and Rich (medium; practice)
  - LeetCode 1466 Reorder Routes to Make All Paths Lead to the City Zero (medium; all)
- **visitation states (white / gray / black)**
  - LeetCode 207 Course Schedule (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 802 Find Eventual Safe States (medium; all)
  - LeetCode 210 Course Schedule II (medium; neetcode150, neetcode250, all)
  - LeetCode 1059 All Paths from Source Lead to Destination (medium; all)
- **parent / predecessor arrays**
  - LeetCode 126 Word Ladder II (hard; practice)
  - LeetCode 499 The Maze III (hard; all)
  - LeetCode 2096 Step-By-Step Directions From a Binary Tree Node to Another (medium; all)
  - LeetCode 1650 Lowest Common Ancestor of a Binary Tree III (medium; all)
- **discovery time + low-link arrays**
  - LeetCode 1568 Minimum Number of Days to Disconnect Island (hard; all)
- **indegree tracking**
  - LeetCode 207 Course Schedule (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 210 Course Schedule II (medium; neetcode150, neetcode250, all)
  - LeetCode 1136 Parallel Courses (medium; all)
  - LeetCode 997 Find the Town Judge (easy; neetcode250, all)
- **min-heap / priority queue**
  - LeetCode 743 Network Delay Time (medium; neetcode150, neetcode250, all)
  - LeetCode 1631 Path With Minimum Effort (medium; neetcode250, all)
  - LeetCode 778 Swim in Rising Water (hard; neetcode150, neetcode250, all)
  - LeetCode 1514 Path with Maximum Probability (medium; all)
- **deque-based 0-1 BFS**
  - LeetCode 1368 Minimum Cost to Make at Least One Valid Path in a Grid (hard; all)
  - LeetCode 2290 Minimum Obstacle Removal to Reach Corner (hard; all)
- **residual edges**
  - no problem in the data: needs one from LeetCode
- **bitmask representation**
  - LeetCode 864 Shortest Path to Get All Keys (hard; practice)
  - LeetCode 980 Unique Paths III (hard; practice)
  - LeetCode 698 Partition to K Equal Sum Subsets (medium; neetcode250, all)
  - LeetCode 526 Beautiful Arrangement (medium; practice)
- **coordinate-to-node mapping**
  - LeetCode 1091 Shortest Path in Binary Matrix (medium; all)
  - LeetCode 200 Number of Islands (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 959 Regions Cut By Slashes (medium; all)
  - LeetCode 947 Most Stones Removed with Same Row or Column (medium; practice)
- **state-to-node encoding**
  - LeetCode 773 Sliding Puzzle (hard; all)
  - LeetCode 864 Shortest Path to Get All Keys (hard; practice)
  - LeetCode 1293 Shortest Path in a Grid with Obstacles Elimination (hard; practice)
  - LeetCode 752 Open the Lock (medium; neetcode250, all)
- **lazy neighbor generation**
  - LeetCode 752 Open the Lock (medium; neetcode250, all)
  - LeetCode 773 Sliding Puzzle (hard; all)
  - LeetCode 127 Word Ladder (hard; neetcode150, neetcode250, all)
  - LeetCode 1197 Minimum Knight Moves (medium; all)
- **memoization over graph states**
  - LeetCode 329 Longest Increasing Path in a Matrix (hard; neetcode150, neetcode250, all)
  - LeetCode 2328 Number of Increasing Paths in a Grid (hard; practice)
  - LeetCode 1553 Minimum Number of Days to Eat N Oranges (hard; all)
  - LeetCode 1594 Maximum Non Negative Product in a Matrix (medium; practice)
- **compact integer node ids**
  - LeetCode 399 Evaluate Division (medium; neetcode250, all)
  - LeetCode 721 Accounts Merge (medium; neetcode250, all)
  - LeetCode 737 Sentence Similarity II (medium; all)
  - LeetCode 815 Bus Routes (hard; all)
- **compressed sparse row (CSR)**
  - no problem in the data: needs one from LeetCode
- **iterative traversal for deep graphs**
  - LeetCode 200 Number of Islands (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 695 Max Area of Island (medium; neetcode150, neetcode250, all)
  - LeetCode 94 Binary Tree Inorder Traversal (easy; neetcode250, all)
  - LeetCode 144 Binary Tree Preorder Traversal (easy; neetcode250, all)
- **stale priority-queue entry filtering**
  - LeetCode 743 Network Delay Time (medium; neetcode150, neetcode250, all)
  - LeetCode 1631 Path With Minimum Effort (medium; neetcode250, all)
  - LeetCode 778 Swim in Rising Water (hard; neetcode150, neetcode250, all)
  - LeetCode 1514 Path with Maximum Probability (medium; all)
- **graph invariants and safe updates** *(nearest fits only)*
  - LeetCode 133 Clone Graph (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 1490 Clone N-ary Tree (medium; all)

## Gaps

Counts: 227 patterns in 17 groups. 149 have at least one problem in the data (118 with a clean example, 31 with nearest fits only); 78 have none and need an example from LeetCode. 180 distinct problems are used.

**Patterns with no problem in the data**, by group:

- 1. Traversal (0 of 11): none
- 2. Cycle detection and graph properties (0 of 8): none
- 3. Topological sort and dependencies (0 of 10): none
- 4. Union-find (DSU) (2 of 12): reverse-time connectivity; DSU on tree / small-to-large merging
- 5. Shortest paths (2 of 17): negative-cycle detection; Johnson's
- 6. Minimum spanning trees (1 of 9): second-best MST
- 7. Connectivity and graph decomposition (12 of 14): condensation DAG; bridges (low-link); biconnected components; edge-biconnected components; bridge tree; block-cut tree; strong bridges; strong articulation points; vertex connectivity; edge connectivity; offline bridge queries; dominators
- 8. Matching and bipartite graphs (8 of 10): Kuhn's; Hopcroft-Karp; maximum bipartite matching; minimum vertex cover in bipartite graphs; Hall's theorem; blossom (general matching); minimum path cover in DAGs; maximum independent set in bipartite graphs
- 9. Network flow (14 of 15): Ford-Fulkerson; Edmonds-Karp; Dinic; push-relabel; minimum cut; edge-disjoint paths; vertex-disjoint paths; bipartite matching via flow; circulation with demands; lower-bounded flow; min-cost max-flow; maximum closure; residual graph reasoning; super-source / super-sink
- 10. Tree algorithms (4 of 18): heavy-light decomposition; centroid decomposition; virtual tree; DSU on tree
- 11. Graph dynamic programming (2 of 14): graph coloring DP; treewidth / tree-decomposition DP
- 12. Graph modeling and state-space search (2 of 19): reverse-time modeling; terminal / boundary compression
- 13. Eulerian and Hamiltonian (1 of 8): De Bruijn sequence
- 14. Backtracking and enumeration (6 of 13): cycle enumeration; connected-subgraph enumeration; clique search; maximum clique; maximum independent set; subgraph isomorphism
- 15. Advanced connectivity and offline algorithms (7 of 9): Menger's theorem applications; SPQR trees; segment tree over time + rollback DSU; offline LCA (Tarjan); dynamic bridge / connectivity maintenance; treewidth-based algorithms; separator-based decomposition
- 16. Specialized graph algorithms (15 of 21): complement graph BFS; graph centrality; absorbing Markov chains; bipartite projection; graph sparsification; LCA in DAGs; minimum mean cycle (Karp); difference constraints; 2-SAT implication graph; min-cost circulation; algebraic path algorithms; bitset-optimized graph algorithms; external-memory graph algorithms; parallel graph traversal; approximation algorithms for hard graph problems
- 17. Core implementation patterns (2 of 19): residual edges; compressed sparse row (CSR)

**Patterns with nearest fits only**, by group:

- 3. Topological sort and dependencies: incremental dependency constraints
- 4. Union-find (DSU): offline dynamic connectivity; rollback DSU
- 5. Shortest paths: DAG shortest path
- 6. Minimum spanning trees: minimum spanning forest; maximum spanning tree; MST with preconnected vertices
- 8. Matching and bipartite graphs: Hungarian algorithm
- 9. Network flow: maximum flow
- 10. Tree algorithms: center; Euler tour / entry-exit timestamps; rerooted subtree queries
- 11. Graph dynamic programming: bitmask DP over subsets; TSP DP; DP over SCCs; probability / expectation DP; meet-in-the-middle DP
- 12. Graph modeling and state-space search: automaton x graph product; line graph / edge-state modeling; dominance pruning
- 13. Eulerian and Hamiltonian: TSP
- 14. Backtracking and enumeration: graph coloring by backtracking; branch-and-bound; meet-in-the-middle enumeration
- 15. Advanced connectivity and offline algorithms: dynamic connectivity; planar graph algorithms
- 16. Specialized graph algorithms: reachability bitsets; minimum dominating set; PageRank / random walks; graph isomorphism
- 17. Core implementation patterns: graph invariants and safe updates

**What the gaps mean for building lessons**

- The data is strong on groups 1 to 5 (traversal, cycles, topological sort, union-find, shortest paths) and 12 (modeling), which come from the NeetCode lists and the practice set. Most of the work in these groups is lessons and tabs (DFS recursive / iterative, 3-color DFS, DFS topological sort, topological layers, grid and metadata DSU, 0-1 BFS, product graph, minimax and bottleneck paths), not problems.
- Groups 7 to 9 and 14 to 16 (SCC, biconnected components, matching, flow, backtracking enumeration, offline and specialised algorithms) are almost empty: the data has a few problems that only brush them (802, 1059 and 2127 for SCC, 1568 for articulation points, 1029 and 1605 for the Hungarian and flow tags). Almost every pattern there needs LeetCode examples, and the lesson and the example pick should happen together, checked against the site.
- Group 10 (trees) and group 11 (graph DP) are served by the Trees, Backtracking and DP topics. The decision for the owner is whether they stay there and the graph lessons link to them, or the graph topics get their own copies. Group 10 patterns with no problem here: heavy-light decomposition, centroid decomposition, virtual tree, DSU on tree.
- The nearest-fit examples in group 11 for bitmask DP (698, 526, 1799, 351) and meet-in-the-middle (2035, 805) are general bitmask problems, not graph-shaped. A graph-shaped example (a Hamiltonian path or TSP count over a small graph) still needs to be found for the graph lessons. 996 Number of Squareful Arrays is the closest in the data.
- Several patterns are best taught inside another pattern's lesson (path compression and union by size inside the basic DSU lesson; Hierholzer and the directed Eulerian trail inside the Eulerian lesson; most group 17 implementation patterns inside the templates). Counting each as a separate lesson would inflate the work; the example lines above repeat the same problems for these on purpose.
- Group 17 is implementation technique, not a family of problems. The example problems there show the technique in use; none of those patterns needs its own problem set.

**Data issues noticed while picking** (not fixed; outside this file)

- Some practice problems carry a technique that does not match them, which would put them under the wrong lesson: 3286, 3377, 3419 and 3928 are under `Advanced Graphs:euler` but are shortest-path or bottleneck problems; 542, 1559, 1926 and 1293 are under `Graphs:simulation` although they are BFS or cycle problems; 1306, 1743, 2039 and 1345 are under `Graphs:clone`; 1971, 1319, 3387 and 924 are under `Graphs:weighted`; 3112, 3604, 3970 and 2977 are under `Advanced Graphs:bellman`. Worth rechecking when the lessons are split into more techniques.
- Tags are LeetCode topic tags and are loose: 947 Most Stones Removed with Same Row or Column carries the Bipartite Graph tag but is a union-find problem, and 399 Evaluate Division carries Bellman-Ford and Floyd-Warshall although the standard solutions are a graph search or a weighted DSU. The picks above were judged by what each problem asks, not by tag alone.
- The data has no problem for several well-known graph problems (for example Critical Connections in a Network, Redundant Connection II, Cracking the Safe, Valid Arrangement of Pairs); these are the first candidates when examples are picked from LeetCode, to be checked on the site first.
