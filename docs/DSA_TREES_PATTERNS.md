# Tree patterns: the exhaustive target list

The owner's list (2026-10-10) of every tree pattern that can come up on LeetCode, as the target for the Trees pattern lessons. The rule is in [DSA.md](DSA.md), decision 32: a topic's patterns section is exhaustive, patterns without a NeetCode problem get **example problems** from LeetCode, and variants of one pattern (DFS recursive / iterative) are **tabs** of one lesson. This is the Trees companion of [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md).

Scope: binary trees, binary search trees and N-ary trees as data structures. Group 10 of the graph list (tree algorithms: diameter, center, LCA, binary lifting, Euler tour, heavy-light decomposition, rerooting DP, centroid decomposition, virtual trees, tree isomorphism, DSU on tree) is covered there. This list touches the same ground only where a tree problem on LeetCode uses it (LCA, diameter, tree DP, parent pointers) and cross-references the graph list for the heavy machinery. Segment trees, Fenwick trees, heaps and tries are other topics.

Status: documented only. Today `content/dsa/lessons/trees.toml` has 12 techniques (dfs, dfs-return, bst-walk, bst-edit, bfs-levels, tree-as-graph, dfs-carry, inorder, from-traversals, catalan, dfs-edit, serialize). Building the rest needs a mockup of the tabs first (the same mockup as for Graphs), then lessons and picked example problems.

Items written *a / b* in a group are variants for tabs where one lesson covers both (for example "DFS: recursive / iterative").

1. **Traversals.** DFS recursive: preorder / inorder / postorder; DFS iterative with an explicit stack; Iterative postorder: two stacks / last-visited pointer; Morris traversal (threaded, O(1) extra space); Inorder of a BST is sorted order; Reverse inorder (right, node, left); Preorder with null markers (root first, shape kept); Postorder (children before the parent); Boundary traversal; Vertical-column traversal; Diagonal traversal; Leaf sequence left to right.

2. **Level-order family.** Basic level-order / bottom-up level-order; Zigzag level-order; Per-level aggregates: sum, max, average; Side views by BFS: right / left (leftmost of the last row); Next-right pointers: queue / O(1) space using the pointers already built; Maximum width with position indices; Completeness check by BFS with null markers; Level-parity rules and per-level rewrites; Minimum depth by BFS (stop at the first leaf); Cousins (same depth, different parent); BFS spread from a start node (time to infect); Level order of an N-ary tree.

3. **Subtree aggregation.** Depth: maximum / minimum; Balanced check by returning height or a sentinel; Diameter (edges, or nodes); Maximum path sum (return a one-sided gain, record the bend); Subtree sum / count / average; Subtree property checks: univalue, perfect, same size; Longest consecutive or equal-value chain; Sum of tilts and similar per-node differences; Subtree height with one node removed (top-two heights); Leaf-pair distances (count pairs within distance k).

4. **Path problems.** Root-to-leaf path: exists / all paths; Root-to-leaf number or string built along the path; Any-to-any path with a prefix-sum map; Best path bending at a node; Longest path with a rule (equal, consecutive); Path property carried down: max so far, bitmask parity; Best difference between a node and its ancestors; Path between two nodes as a string of directions; Position and path in a perfect or labelled tree.

5. **Construction.** From preorder and inorder / inorder and postorder; From preorder and postorder (many answers); From a sorted array / sorted list (balanced BST); BST from its preorder: bounds / monotonic stack; From parent-child descriptions; From a depth-marked preorder string; Serialize and deserialize: preorder with nulls / BFS level format; Serialize an N-ary tree or encode it as a binary tree; String from a tree, and canonical subtree signatures; Rebuild or validate from constraints (pair sets, child arrays); Quad tree from a grid; Complete tree with an inserter or recovered values; Rebalance a BST via the sorted inorder list; Merge trees or BSTs into one.

6. **BST operations.** Search / insert iteratively; Delete (leaf, one child, two children via successor); Trim to a range; Validate with bounds / with an inorder walk; Kth smallest and order statistics; Successor and predecessor, with or without parent pointers; Range queries: sum in range; Closest value and nearest keys; Greater-sum tree; Recover a BST with two swapped nodes; Minimum difference between nodes, mode; Two-sum on BSTs (two iterators or a set); Largest BST inside a binary tree; BST to a sorted doubly linked list; Self-balancing trees (AVL rotations, red-black, treaps); Augmented BST with subtree sizes (rank, order-statistic tree).

7. **Lowest common ancestor.** LCA in a BST by splitting values; LCA in a binary tree: recursive return of found nodes; LCA with parent pointers (two-pointer swap / ancestor set); Distance between two nodes through the LCA; LCA of several nodes; LCA of the deepest leaves; Binary lifting for repeated queries; Euler tour + range-minimum, offline Tarjan.

8. **Tree comparison.** Same tree; Symmetric tree: recursive mirror / iterative queue; Subtree of another tree: compare at every node / serialize and match; Flip equivalence; Leaf-similar trees; Duplicate subtrees by canonical signature or hashing; Pattern match: a linked list in a tree; Merge two trees node by node.

9. **Transformations.** Invert / mirror; Flatten to a linked list: recursive / Morris-style in place; Upside-down tree (rotate the left spine); Prune subtrees that fail a rule; Delete nodes and return the forest; BST to greater tree / sorted doubly linked list; Reverse values on odd levels, replace values by sibling sums; Binary encoding of an N-ary tree; Trim or merge.

10. **Tree DP.** Two-state DP: take / skip a node (independent set); Three-state DP: camera placement (covered / has camera / needs cover); Balance and flow across edges (moves as the sum of excess); DP returning a tuple: validity, min, max, sum; Counting by removing a node (product of component sizes); Time or cost to collect along a tree; Prune or peel leaves then count components; Parity argument on a tree (flip pairs along paths); Knapsack on a tree (merge child tables by size); Rerooting DP (answers for every root).

11. **Parent pointers and tree-to-graph.** Parent map, then BFS outward from a node; Tree given as an edge list: build adjacency, pass the parent down; Manager / employee hierarchies; Find the root of an N-ary tree from children lists; Leaf peeling / center of a tree; Check that a graph or child arrays form a tree; Walk upward with parent pointers (LCA, successor); Tree game on subtree sizes; Dynamic tree structures: inheritance order, lock operations on a tree; Euler tour timestamps (entry / exit) and subtree ranges.

12. **Views.** Right-side view; Left view / bottom-left value; Vertical order; Boundary view; Top view / bottom view; Diagonal view.

13. **Count and enumerate trees.** Count BSTs with n keys (Catalan); Generate all BSTs with n keys; All full binary trees with n nodes (memoized); Count nodes of a complete tree faster than O(n); Count good nodes / paths with a property; Count tree shapes consistent with constraints; Count BST insertion orders giving the same tree.

14. **N-ary trees.** Preorder / postorder of an N-ary tree; Depth of an N-ary tree; Diameter of an N-ary tree; Clone an N-ary tree; Serialize an N-ary tree; Find the root without a parent pointer; Level order of an N-ary tree; Child-sibling (left-child right-sibling) representation.

15. **Iterator design.** BST iterator with an explicit stack (amortized O(1) next); Two iterators merged: two-sum on BSTs; Forward and backward iterators: closest values; Flatten a nested structure lazily; Design with a tree behind it: inserter, stream, locks; Peek / has-next with a precomputed list vs lazy stack.

Cross-references to [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md): group 10 (tree algorithms: heavy-light decomposition, centroid decomposition, rerooting DP, virtual tree, DSU on tree, tree isomorphism), group 7 (bridge tree, block-cut tree) and group 15 (offline LCA with Tarjan). Where an item above says "Euler tour", "binary lifting" or "rerooting", the lesson here teaches the tree-problem entry point and links to the graph lesson for the full method.

## Coverage today

- The data holds 141 problems in the Trees pattern (23 on the Blind 75 / NeetCode 150 / NeetCode 250 lists, the rest in `all` or `practice`), spread over 12 techniques. A further 15 problems tagged Tree, Binary Tree, Binary Search Tree or DP on Trees sit in other patterns (Graphs, Advanced Graphs, Stack, Heap / Priority Queue, Greedy).
- Tag counts across all 1550 problems in the data: Tree 155, Binary Tree 127, Binary Search Tree 34, DP on Trees 17.
- Problems per technique today:
  - `Trees:dfs` (plain recursion): 16 problems
  - `Trees:dfs-return` (return a value up, record a candidate): 20 problems
  - `Trees:bst-walk` (walk a BST, discard subtrees): 9 problems
  - `Trees:bst-edit` (insert, delete, trim): 7 problems
  - `Trees:bfs-levels` (queue by level): 19 problems
  - `Trees:tree-as-graph` (tree given as edges or via a parent map): 11 problems
  - `Trees:dfs-carry` (carry a value down): 10 problems
  - `Trees:inorder` (inorder and iterators): 15 problems
  - `Trees:from-traversals` (construction): 11 problems
  - `Trees:catalan` (count and build BSTs): 7 problems
  - `Trees:dfs-edit` (prune and delete): 7 problems
  - `Trees:serialize` (serialize and design): 9 problems
- Groups against the 12 techniques:
  - 1 Traversals: partly: `inorder` and `dfs` cover recursive and the explicit-stack inorder; no preorder / postorder iterative tabs, no Morris, no boundary or diagonal lesson
  - 2 Level-order family: mostly: `bfs-levels`; the zigzag, width, next-pointer and parity variants have problems but no tabs
  - 3 Subtree aggregation: yes: `dfs-return` (balanced, diameter, max path sum)
  - 4 Path problems: yes: `dfs-carry` and `dfs-return`; the prefix-sum path count (any-to-any) has no lesson of its own
  - 5 Construction: partly: `from-traversals` and `serialize`; no BST-from-preorder, depth-marked string or quad tree lesson
  - 6 BST operations: partly: `bst-walk`, `bst-edit`, `inorder`; no successor / predecessor, two-sum on BSTs, recover BST, largest BST subtree or self-balancing
  - 7 Lowest common ancestor: partly: BST LCA in `bst-walk`; the binary-tree LCA is filed under `dfs-return` without its own lesson; no parent-pointer tab, no binary lifting here
  - 8 Tree comparison: partly: the problems are filed under `dfs` (same, symmetric, subtree, flip); no lesson on canonical signatures or hashing
  - 9 Transformations: partly: `dfs` (invert) and `dfs-edit` (prune, delete); no flatten, upside-down or encode lesson
  - 10 Tree DP: partly: `dfs-return` holds house robber III and cameras; the multi-state and tuple-return DP has no lesson of its own; no knapsack or rerooting
  - 11 Parent pointers, tree to graph: yes: `tree-as-graph`; no Euler-tour timestamps
  - 12 Views: only the right-side view, inside `bfs-levels`
  - 13 Count and enumerate trees: yes: `catalan`
  - 14 N-ary trees: no lesson: the N-ary problems are spread over `dfs`, `inorder`, `serialize` and `tree-as-graph`
  - 15 Iterator design: partly: BST iterator in `inorder`; no two-iterator or forward / backward lesson

## Example problems per pattern

Up to four per pattern, all taken from `content/dsa/problems.json` and `content/dsa/practice.json` (the `problems` arrays), written as `LeetCode <number> <title> (<difficulty>; <lists>)`. A pattern with no problem in the data is marked, and needs one picked from LeetCode and checked there (never from memory). Problems repeat across patterns when one problem teaches several.

**1. Traversals**

- DFS recursive: preorder / inorder / postorder
  - LeetCode 94 Binary Tree Inorder Traversal (easy; neetcode250, all)
  - LeetCode 144 Binary Tree Preorder Traversal (easy; neetcode250, all)
  - LeetCode 145 Binary Tree Postorder Traversal (easy; neetcode250, all)
  - LeetCode 590 N-ary Tree Postorder Traversal (easy; all)
- DFS iterative with an explicit stack
  - LeetCode 94 Binary Tree Inorder Traversal (easy; neetcode250, all)
  - LeetCode 144 Binary Tree Preorder Traversal (easy; neetcode250, all)
  - LeetCode 145 Binary Tree Postorder Traversal (easy; neetcode250, all)
  - LeetCode 173 Binary Search Tree Iterator (medium; all)
- Iterative postorder: two stacks / last-visited pointer
  - LeetCode 145 Binary Tree Postorder Traversal (easy; neetcode250, all)
  - LeetCode 590 N-ary Tree Postorder Traversal (easy; all)
- Morris traversal (threaded, O(1) extra space)
  - LeetCode 94 Binary Tree Inorder Traversal (easy; neetcode250, all)
  - LeetCode 99 Recover Binary Search Tree (medium; all)
- Inorder of a BST is sorted order
  - LeetCode 230 Kth Smallest Element in a BST (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 783 Minimum Distance Between BST Nodes (easy; all)
  - LeetCode 530 Minimum Absolute Difference in BST (easy; practice)
  - LeetCode 653 Two Sum IV - Input is a BST (easy; practice)
- Reverse inorder (right, node, left)
  - LeetCode 538 Convert BST to Greater Tree (medium; all)
  - LeetCode 1038 Binary Search Tree to Greater Sum Tree (medium; practice)
- Preorder with null markers (root first, shape kept)
  - LeetCode 297 Serialize and Deserialize Binary Tree (hard; blind75, neetcode150, neetcode250, all)
  - LeetCode 606 Construct String from Binary Tree (medium; all)
- Postorder (children before the parent)
  - LeetCode 110 Balanced Binary Tree (easy; neetcode150, neetcode250, all)
  - LeetCode 366 Find Leaves of Binary Tree (medium; all)
  - LeetCode 1325 Delete Leaves With a Given Value (medium; neetcode250, all)
- Boundary traversal
  - LeetCode 545 Boundary of Binary Tree (medium; all)
- Vertical-column traversal
  - LeetCode 314 Binary Tree Vertical Order Traversal (medium; all)
  - LeetCode 987 Vertical Order Traversal of a Binary Tree (hard; practice)
- Diagonal traversal: no problem in the data: needs one from LeetCode
- Leaf sequence left to right
  - LeetCode 872 Leaf-Similar Trees (easy; all)

**2. Level-order family**

- Basic level-order / bottom-up level-order
  - LeetCode 102 Binary Tree Level Order Traversal (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 107 Binary Tree Level Order Traversal II (medium; practice)
- Zigzag level-order
  - LeetCode 103 Binary Tree Zigzag Level Order Traversal (medium; all)
- Per-level aggregates: sum, max, average
  - LeetCode 515 Find Largest Value in Each Tree Row (medium; all)
  - LeetCode 1161 Maximum Level Sum of a Binary Tree (medium; practice)
  - LeetCode 2583 Kth Largest Sum in a Binary Tree (medium; all)
  - LeetCode 2641 Cousins in Binary Tree II (medium; all)
- Side views by BFS: right / left (leftmost of the last row)
  - LeetCode 199 Binary Tree Right Side View (medium; neetcode150, neetcode250, all)
  - LeetCode 513 Find Bottom Left Tree Value (medium; all)
- Next-right pointers: queue / O(1) space using the pointers already built
  - LeetCode 116 Populating Next Right Pointers in Each Node (medium; all)
  - LeetCode 117 Populating Next Right Pointers in Each Node II (medium; practice)
- Maximum width with position indices
  - LeetCode 662 Maximum Width of Binary Tree (medium; all)
- Completeness check by BFS with null markers
  - LeetCode 958 Check Completeness of a Binary Tree (medium; all)
- Level-parity rules and per-level rewrites
  - LeetCode 1609 Even Odd Tree (medium; all)
  - LeetCode 2415 Reverse Odd Levels of Binary Tree (medium; all)
  - LeetCode 2471 Minimum Number of Operations to Sort a Binary Tree by Level (medium; all)
- Minimum depth by BFS (stop at the first leaf)
  - LeetCode 111 Minimum Depth of Binary Tree (easy; practice)
- Cousins (same depth, different parent)
  - LeetCode 993 Cousins in Binary Tree (easy; practice)
  - LeetCode 2641 Cousins in Binary Tree II (medium; all)
- BFS spread from a start node (time to infect)
  - LeetCode 2385 Amount of Time for Binary Tree to Be Infected (medium; practice)
- Level order of an N-ary tree: no problem in the data: needs one from LeetCode

**3. Subtree aggregation**

- Depth: maximum / minimum
  - LeetCode 104 Maximum Depth of Binary Tree (easy; blind75, neetcode150, neetcode250, all)
  - LeetCode 111 Minimum Depth of Binary Tree (easy; practice)
  - LeetCode 559 Maximum Depth of N-ary Tree (easy; practice)
- Balanced check by returning height or a sentinel
  - LeetCode 110 Balanced Binary Tree (easy; neetcode150, neetcode250, all)
- Diameter (edges, or nodes)
  - LeetCode 543 Diameter of Binary Tree (easy; neetcode150, neetcode250, all)
  - LeetCode 1522 Diameter of N-Ary Tree (medium; all)
  - LeetCode 1245 Tree Diameter (medium; all)
- Maximum path sum (return a one-sided gain, record the bend)
  - LeetCode 124 Binary Tree Maximum Path Sum (hard; blind75, neetcode150, neetcode250, all)
- Subtree sum / count / average
  - LeetCode 1120 Maximum Average Subtree (medium; all)
  - LeetCode 2265 Count Nodes Equal to Average of Subtree (medium; practice)
  - LeetCode 1339 Maximum Product of Splitted Binary Tree (medium; practice)
- Subtree property checks: univalue, perfect, same size
  - LeetCode 250 Count Univalue Subtrees (medium; all)
  - LeetCode 965 Univalued Binary Tree (easy; practice)
  - LeetCode 3319 K-th Largest Perfect Subtree Size in Binary Tree (medium; practice)
- Longest consecutive or equal-value chain
  - LeetCode 298 Binary Tree Longest Consecutive Sequence (medium; all)
  - LeetCode 549 Binary Tree Longest Consecutive Sequence II (medium; all)
  - LeetCode 687 Longest Univalue Path (medium; practice)
- Sum of tilts and similar per-node differences: no problem in the data: needs one from LeetCode
- Subtree height with one node removed (top-two heights)
  - LeetCode 2458 Height of Binary Tree After Subtree Removal Queries (hard; practice)
- Leaf-pair distances (count pairs within distance k)
  - LeetCode 1530 Number of Good Leaf Nodes Pairs (medium; all)

**4. Path problems**

- Root-to-leaf path: exists / all paths
  - LeetCode 112 Path Sum (easy; all)
  - LeetCode 113 Path Sum II (medium; practice)
  - LeetCode 257 Binary Tree Paths (easy; practice)
- Root-to-leaf number or string built along the path
  - LeetCode 129 Sum Root to Leaf Numbers (medium; all)
  - LeetCode 988 Smallest String Starting From Leaf (medium; all)
  - LeetCode 1022 Sum of Root To Leaf Binary Numbers (easy; practice)
- Any-to-any path with a prefix-sum map
  - LeetCode 437 Path Sum III (medium; practice)
- Best path bending at a node
  - LeetCode 124 Binary Tree Maximum Path Sum (hard; blind75, neetcode150, neetcode250, all)
  - LeetCode 543 Diameter of Binary Tree (easy; neetcode150, neetcode250, all)
- Longest path with a rule (equal, consecutive)
  - LeetCode 687 Longest Univalue Path (medium; practice)
  - LeetCode 298 Binary Tree Longest Consecutive Sequence (medium; all)
  - LeetCode 549 Binary Tree Longest Consecutive Sequence II (medium; all)
- Path property carried down: max so far, bitmask parity
  - LeetCode 1448 Count Good Nodes in Binary Tree (medium; neetcode150, neetcode250, all)
  - LeetCode 1457 Pseudo-Palindromic Paths in a Binary Tree (medium; all)
  - LeetCode 2791 Count Paths That Can Form a Palindrome in a Tree (hard; practice)
- Best difference between a node and its ancestors
  - LeetCode 1026 Maximum Difference Between Node and Ancestor (medium; practice)
- Path between two nodes as a string of directions
  - LeetCode 2096 Step-By-Step Directions From a Binary Tree Node to Another (medium; all)
- Position and path in a perfect or labelled tree
  - LeetCode 1104 Path In Zigzag Labelled Binary Tree (medium; practice)

**5. Construction**

- From preorder and inorder / inorder and postorder
  - LeetCode 105 Construct Binary Tree from Preorder and Inorder Traversal (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 106 Construct Binary Tree from Inorder and Postorder Traversal (medium; all)
- From preorder and postorder (many answers)
  - LeetCode 889 Construct Binary Tree from Preorder and Postorder Traversal (medium; all)
- From a sorted array / sorted list (balanced BST)
  - LeetCode 108 Convert Sorted Array to Binary Search Tree (easy; all)
  - LeetCode 109 Convert Sorted List to Binary Search Tree (medium; practice)
- BST from its preorder: bounds / monotonic stack
  - LeetCode 1008 Construct Binary Search Tree from Preorder Traversal (medium; practice)
  - LeetCode 255 Verify Preorder Sequence in Binary Search Tree (medium; all)
- From parent-child descriptions
  - LeetCode 2196 Create Binary Tree From Descriptions (medium; all)
- From a depth-marked preorder string
  - LeetCode 1028 Recover a Tree From Preorder Traversal (hard; all)
- Serialize and deserialize: preorder with nulls / BFS level format
  - LeetCode 297 Serialize and Deserialize Binary Tree (hard; blind75, neetcode150, neetcode250, all)
  - LeetCode 449 Serialize and Deserialize BST (medium; practice)
- Serialize an N-ary tree or encode it as a binary tree
  - LeetCode 428 Serialize and Deserialize N-ary Tree (hard; all)
  - LeetCode 431 Encode N-ary Tree to Binary Tree (hard; all)
- String from a tree, and canonical subtree signatures
  - LeetCode 606 Construct String from Binary Tree (medium; all)
  - LeetCode 652 Find Duplicate Subtrees (medium; all)
- Rebuild or validate from constraints (pair sets, child arrays)
  - LeetCode 1719 Number Of Ways To Reconstruct A Tree (hard; practice)
  - LeetCode 1361 Validate Binary Tree Nodes (medium; all)
- Quad tree from a grid
  - LeetCode 427 Construct Quad Tree (medium; neetcode250, all)
- Complete tree with an inserter or recovered values
  - LeetCode 919 Complete Binary Tree Inserter (medium; practice)
  - LeetCode 1261 Find Elements in a Contaminated Binary Tree (medium; practice)
- Rebalance a BST via the sorted inorder list
  - LeetCode 1382 Balance a Binary Search Tree (medium; practice)
- Merge trees or BSTs into one
  - LeetCode 617 Merge Two Binary Trees (easy; all)
  - LeetCode 1932 Merge BSTs to Create Single BST (hard; practice)

**6. BST operations**

- Search / insert iteratively
  - LeetCode 700 Search in a Binary Search Tree (easy; practice)
  - LeetCode 701 Insert into a Binary Search Tree (medium; neetcode250, all)
- Delete (leaf, one child, two children via successor)
  - LeetCode 450 Delete Node in a BST (medium; neetcode250, all)
- Trim to a range
  - LeetCode 669 Trim a Binary Search Tree (medium; all)
- Validate with bounds / with an inorder walk
  - LeetCode 98 Validate Binary Search Tree (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 230 Kth Smallest Element in a BST (medium; blind75, neetcode150, neetcode250, all)
- Kth smallest and order statistics
  - LeetCode 230 Kth Smallest Element in a BST (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 703 Kth Largest Element in a Stream (easy; neetcode150, neetcode250, all)
- Successor and predecessor, with or without parent pointers
  - LeetCode 510 Inorder Successor in BST II (medium; all)
- Range queries: sum in range
  - LeetCode 938 Range Sum of BST (easy; all)
- Closest value and nearest keys
  - LeetCode 270 Closest Binary Search Tree Value (easy; all)
  - LeetCode 272 Closest Binary Search Tree Value II (hard; all)
  - LeetCode 2476 Closest Nodes Queries in a Binary Search Tree (medium; practice)
- Greater-sum tree
  - LeetCode 538 Convert BST to Greater Tree (medium; all)
  - LeetCode 1038 Binary Search Tree to Greater Sum Tree (medium; practice)
- Recover a BST with two swapped nodes
  - LeetCode 99 Recover Binary Search Tree (medium; all)
- Minimum difference between nodes, mode
  - LeetCode 530 Minimum Absolute Difference in BST (easy; practice)
  - LeetCode 783 Minimum Distance Between BST Nodes (easy; all)
  - LeetCode 501 Find Mode in Binary Search Tree (easy; practice)
- Two-sum on BSTs (two iterators or a set)
  - LeetCode 653 Two Sum IV - Input is a BST (easy; practice)
  - LeetCode 1214 Two Sum BSTs (medium; all)
- Largest BST inside a binary tree
  - LeetCode 333 Largest BST Subtree (medium; all)
  - LeetCode 1373 Maximum Sum BST in Binary Tree (hard; practice)
- BST to a sorted doubly linked list
  - LeetCode 426 Convert Binary Search Tree to Sorted Doubly Linked List (medium; all)
- Self-balancing trees (AVL rotations, red-black, treaps): no problem in the data: needs one from LeetCode
- Augmented BST with subtree sizes (rank, order-statistic tree): no problem in the data: needs one from LeetCode

**7. Lowest common ancestor**

- LCA in a BST by splitting values
  - LeetCode 235 Lowest Common Ancestor of a Binary Search Tree (medium; blind75, neetcode150, neetcode250, all)
- LCA in a binary tree: recursive return of found nodes
  - LeetCode 236 Lowest Common Ancestor of a Binary Tree (medium; all)
- LCA with parent pointers (two-pointer swap / ancestor set)
  - LeetCode 1650 Lowest Common Ancestor of a Binary Tree III (medium; all)
- Distance between two nodes through the LCA
  - LeetCode 2096 Step-By-Step Directions From a Binary Tree Node to Another (medium; all)
- LCA of several nodes: no problem in the data: needs one from LeetCode
- LCA of the deepest leaves: no problem in the data: needs one from LeetCode
- Binary lifting for repeated queries
  - LeetCode 235 Lowest Common Ancestor of a Binary Search Tree (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 236 Lowest Common Ancestor of a Binary Tree (medium; all)
  - LeetCode 1650 Lowest Common Ancestor of a Binary Tree III (medium; all)
  - LeetCode 2096 Step-By-Step Directions From a Binary Tree Node to Another (medium; all)
- Euler tour + range-minimum, offline Tarjan: no problem in the data: needs one from LeetCode

**8. Tree comparison**

- Same tree
  - LeetCode 100 Same Tree (easy; blind75, neetcode150, neetcode250, all)
- Symmetric tree: recursive mirror / iterative queue
  - LeetCode 101 Symmetric Tree (easy; all)
- Subtree of another tree: compare at every node / serialize and match
  - LeetCode 572 Subtree of Another Tree (easy; blind75, neetcode150, neetcode250, all)
- Flip equivalence
  - LeetCode 951 Flip Equivalent Binary Trees (medium; all)
- Leaf-similar trees
  - LeetCode 872 Leaf-Similar Trees (easy; all)
- Duplicate subtrees by canonical signature or hashing
  - LeetCode 652 Find Duplicate Subtrees (medium; all)
- Pattern match: a linked list in a tree
  - LeetCode 1367 Linked List in Binary Tree (medium; all)
- Merge two trees node by node
  - LeetCode 617 Merge Two Binary Trees (easy; all)

**9. Transformations**

- Invert / mirror
  - LeetCode 226 Invert Binary Tree (easy; blind75, neetcode150, neetcode250, all)
- Flatten to a linked list: recursive / Morris-style in place
  - LeetCode 114 Flatten Binary Tree to Linked List (medium; practice)
- Upside-down tree (rotate the left spine)
  - LeetCode 156 Binary Tree Upside Down (medium; all)
- Prune subtrees that fail a rule
  - LeetCode 814 Binary Tree Pruning (medium; practice)
  - LeetCode 1325 Delete Leaves With a Given Value (medium; neetcode250, all)
- Delete nodes and return the forest
  - LeetCode 1110 Delete Nodes And Return Forest (medium; all)
- BST to greater tree / sorted doubly linked list
  - LeetCode 538 Convert BST to Greater Tree (medium; all)
  - LeetCode 426 Convert Binary Search Tree to Sorted Doubly Linked List (medium; all)
- Reverse values on odd levels, replace values by sibling sums
  - LeetCode 2415 Reverse Odd Levels of Binary Tree (medium; all)
  - LeetCode 2641 Cousins in Binary Tree II (medium; all)
- Binary encoding of an N-ary tree
  - LeetCode 431 Encode N-ary Tree to Binary Tree (hard; all)
- Trim or merge
  - LeetCode 669 Trim a Binary Search Tree (medium; all)
  - LeetCode 617 Merge Two Binary Trees (easy; all)

**10. Tree DP**

- Two-state DP: take / skip a node (independent set)
  - LeetCode 337 House Robber III (medium; neetcode250, all)
- Three-state DP: camera placement (covered / has camera / needs cover)
  - LeetCode 968 Binary Tree Cameras (hard; practice)
- Balance and flow across edges (moves as the sum of excess)
  - LeetCode 979 Distribute Coins in Binary Tree (medium; all)
- DP returning a tuple: validity, min, max, sum
  - LeetCode 1373 Maximum Sum BST in Binary Tree (hard; practice)
  - LeetCode 333 Largest BST Subtree (medium; all)
- Counting by removing a node (product of component sizes)
  - LeetCode 2049 Count Nodes With the Highest Score (medium; practice)
- Time or cost to collect along a tree
  - LeetCode 1443 Minimum Time to Collect All Apples in a Tree (medium; all)
  - LeetCode 2477 Minimum Fuel Cost to Report to the Capital (medium; all)
- Prune or peel leaves then count components
  - LeetCode 2603 Collect Coins in a Tree (hard; practice)
  - LeetCode 2872 Maximum Number of K-Divisible Components (hard; all)
- Parity argument on a tree (flip pairs along paths)
  - LeetCode 3068 Find the Maximum Sum of Node Values (hard; all)
- Knapsack on a tree (merge child tables by size): no problem in the data: needs one from LeetCode
- Rerooting DP (answers for every root): no problem in the data: needs one from LeetCode

**11. Parent pointers and tree-to-graph**

- Parent map, then BFS outward from a node
  - LeetCode 863 All Nodes Distance K in Binary Tree (medium; practice)
  - LeetCode 2385 Amount of Time for Binary Tree to Be Infected (medium; practice)
- Tree given as an edge list: build adjacency, pass the parent down
  - LeetCode 2467 Most Profitable Path in a Tree (medium; all)
  - LeetCode 2477 Minimum Fuel Cost to Report to the Capital (medium; all)
  - LeetCode 3067 Count Pairs of Connectable Servers in a Weighted Tree Network (medium; practice)
- Manager / employee hierarchies
  - LeetCode 1376 Time Needed to Inform All Employees (medium; all)
  - LeetCode 582 Kill Process (medium; all)
  - LeetCode 690 Employee Importance (medium; practice)
- Find the root of an N-ary tree from children lists
  - LeetCode 1506 Find Root of N-Ary Tree (medium; all)
- Leaf peeling / center of a tree
  - LeetCode 1245 Tree Diameter (medium; all)
  - LeetCode 3203 Find Minimum Diameter After Merging Two Trees (hard; all)
- Check that a graph or child arrays form a tree
  - LeetCode 1361 Validate Binary Tree Nodes (medium; all)
- Walk upward with parent pointers (LCA, successor)
  - LeetCode 1650 Lowest Common Ancestor of a Binary Tree III (medium; all)
  - LeetCode 510 Inorder Successor in BST II (medium; all)
- Tree game on subtree sizes
  - LeetCode 1145 Binary Tree Coloring Game (medium; practice)
- Dynamic tree structures: inheritance order, lock operations on a tree
  - LeetCode 1600 Throne Inheritance (medium; practice)
  - LeetCode 1993 Operations on Tree (medium; all)
- Euler tour timestamps (entry / exit) and subtree ranges: no problem in the data: needs one from LeetCode

**12. Views**

- Right-side view
  - LeetCode 199 Binary Tree Right Side View (medium; neetcode150, neetcode250, all)
- Left view / bottom-left value
  - LeetCode 513 Find Bottom Left Tree Value (medium; all)
- Vertical order
  - LeetCode 314 Binary Tree Vertical Order Traversal (medium; all)
  - LeetCode 987 Vertical Order Traversal of a Binary Tree (hard; practice)
- Boundary view
  - LeetCode 545 Boundary of Binary Tree (medium; all)
- Top view / bottom view: no problem in the data: needs one from LeetCode
- Diagonal view: no problem in the data: needs one from LeetCode

**13. Count and enumerate trees**

- Count BSTs with n keys (Catalan)
  - LeetCode 96 Unique Binary Search Trees (medium; all)
- Generate all BSTs with n keys
  - LeetCode 95 Unique Binary Search Trees II (medium; all)
- All full binary trees with n nodes (memoized)
  - LeetCode 894 All Possible Full Binary Trees (medium; all)
- Count nodes of a complete tree faster than O(n)
  - LeetCode 222 Count Complete Tree Nodes (medium; practice)
- Count good nodes / paths with a property
  - LeetCode 1448 Count Good Nodes in Binary Tree (medium; neetcode150, neetcode250, all)
  - LeetCode 437 Path Sum III (medium; practice)
  - LeetCode 2791 Count Paths That Can Form a Palindrome in a Tree (hard; practice)
- Count tree shapes consistent with constraints
  - LeetCode 1719 Number Of Ways To Reconstruct A Tree (hard; practice)
- Count BST insertion orders giving the same tree: no problem in the data: needs one from LeetCode

**14. N-ary trees**

- Preorder / postorder of an N-ary tree
  - LeetCode 589 N-ary Tree Preorder Traversal (easy; practice)
  - LeetCode 590 N-ary Tree Postorder Traversal (easy; all)
- Depth of an N-ary tree
  - LeetCode 559 Maximum Depth of N-ary Tree (easy; practice)
- Diameter of an N-ary tree
  - LeetCode 1522 Diameter of N-Ary Tree (medium; all)
- Clone an N-ary tree
  - LeetCode 1490 Clone N-ary Tree (medium; all)
- Serialize an N-ary tree
  - LeetCode 428 Serialize and Deserialize N-ary Tree (hard; all)
  - LeetCode 431 Encode N-ary Tree to Binary Tree (hard; all)
- Find the root without a parent pointer
  - LeetCode 1506 Find Root of N-Ary Tree (medium; all)
- Level order of an N-ary tree: no problem in the data: needs one from LeetCode
- Child-sibling (left-child right-sibling) representation
  - LeetCode 431 Encode N-ary Tree to Binary Tree (hard; all)

**15. Iterator design**

- BST iterator with an explicit stack (amortized O(1) next)
  - LeetCode 173 Binary Search Tree Iterator (medium; all)
- Two iterators merged: two-sum on BSTs
  - LeetCode 1214 Two Sum BSTs (medium; all)
  - LeetCode 653 Two Sum IV - Input is a BST (easy; practice)
- Forward and backward iterators: closest values
  - LeetCode 272 Closest Binary Search Tree Value II (hard; all)
- Flatten a nested structure lazily
  - LeetCode 341 Flatten Nested List Iterator (medium; all)
- Design with a tree behind it: inserter, stream, locks
  - LeetCode 919 Complete Binary Tree Inserter (medium; practice)
  - LeetCode 703 Kth Largest Element in a Stream (easy; neetcode150, neetcode250, all)
  - LeetCode 1993 Operations on Tree (medium; all)
- Peek / has-next with a precomputed list vs lazy stack
  - LeetCode 173 Binary Search Tree Iterator (medium; all)

## Gaps

- 145 patterns listed, 130 with at least one example from the data and 15 with none. 147 distinct problems are used as examples, out of 156 tree problems in the data (Trees pattern plus tree-tagged problems elsewhere).
- Patterns with no problem in the data (each needs one picked from LeetCode and checked there):
  - Group 1: Diagonal traversal
  - Group 2: Level order of an N-ary tree
  - Group 3: Sum of tilts and similar per-node differences
  - Group 6: Self-balancing trees (AVL rotations, red-black, treaps)
  - Group 6: Augmented BST with subtree sizes (rank, order-statistic tree)
  - Group 7: LCA of several nodes
  - Group 7: LCA of the deepest leaves
  - Group 7: Euler tour + range-minimum, offline Tarjan
  - Group 10: Knapsack on a tree (merge child tables by size)
  - Group 10: Rerooting DP (answers for every root)
  - Group 11: Euler tour timestamps (entry / exit) and subtree ranges
  - Group 12: Top view / bottom view
  - Group 12: Diagonal view
  - Group 13: Count BST insertion orders giving the same tree
  - Group 14: Level order of an N-ary tree
- 6 of the 141 Trees-pattern problems are not used as an example above; they stay in their technique as practice.
- Thin patterns (one or two problems in the data): Morris traversal (only as a follow-up on inorder and recover BST), delete in a BST, trim, binary-tree LCA, the tree-comparison variants, the three-state DP, rerooting.
- Left out on purpose and covered elsewhere: segment trees and Fenwick trees, tries (Tries), heaps (Heap / Priority Queue), heavy-light, centroid and virtual trees ([DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md) group 10).
- Open before building: where the extra patterns sit (more techniques inside Trees, or the tree-algorithm patterns shared with Graphs group 10), how the tabs look (needs a mockup, rule 13), whether items that reuse the same problem become one lesson with tabs, and the picked example problems for the empty patterns.
