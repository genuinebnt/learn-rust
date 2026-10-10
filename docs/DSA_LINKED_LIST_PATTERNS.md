# Linked List patterns: the exhaustive target list

The owner's rule (2026-10-09) applied to the Linked List topic: every linked-list pattern that can come up on LeetCode, as the target for the Linked List pattern lesson. The rule is in [DSA.md](DSA.md), decision 32: a topic's patterns section is exhaustive, patterns without a NeetCode problem get **example problems** from LeetCode, and variants of one pattern (iterative / recursive) are **tabs** of one lesson. The format follows [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md).

Status: documented only. Today `content/dsa/lessons/linked-list.toml` has 9 techniques (reverse, dummy-merge, fast-slow, splice, gap, clone-map, design-list, lru, kway-merge). Building the rest needs the tab mockup first (the same one as for Graphs), then lessons and picked example problems.

Items written *a / b* in a group are variants for tabs where one lesson covers both (for example "reverse: iterative / recursive"). Example problems are in the last sections and come only from the data in `content/dsa/problems.json` and `content/dsa/practice.json`.

1. **Reversal.** Whole list reversal (iterative with prev/cur/next) / recursive reversal; reverse a sub-range between positions (pull-to-front); reverse in k-groups (with and without a short tail); swap adjacent pairs; reverse only groups of a given parity or length; reverse a list you may not modify (stack or recursion); reverse a doubly linked list (swap prev and next); head insertion as reversal; reversing to read digits least-significant first.
2. **Fast and slow pointers.** Middle node (first / second middle for even length); cycle detection; cycle entrance; n-th node from the end (fixed gap); delete the middle node; k-th node from the end; split at the middle; palindrome check (middle + reverse half); why the restart-from-head works (meeting-point proof); the gap pointer as a variant of the two-speed idea.
3. **Merging and sorting.** Merge two sorted lists (iterative with dummy head / recursive); merge k sorted lists (min-heap / divide and conquer pairwise merge / sequential merge); merge sort on a list (top-down with a middle split / bottom-up in O(1) extra space); insertion sort on a list; stable merge (<= keeps order); merge by a key other than value (timestamps, frequency); merge with duplicate removal; selection and counting-based sorts on lists (three-value lists by counting).
4. **Partition and reorder.** Partition around a pivot value (two dummy lists, stitch) / stable partition; odd-even position regrouping; reorder list (L0, Ln, L1, Ln-1...: find middle, reverse second half, interleave); rotate by k (find length, make circular, cut); move all nodes with a value to the end; move a node to the front (most recently used); swap the k-th from the start and the k-th from the end; reverse alternate segments.
5. **Dummy head and in-place surgery.** Remove all nodes with a value; remove duplicates from a sorted list (keep one / remove all duplicated values); remove duplicates from an unsorted list (count then drop); delete nodes present in a set; delete a node given only that node (copy the next value); remove nodes with a greater node to the right (monotonic stack / reverse pass); remove zero-sum consecutive runs (prefix-sum map); insert into a sorted (circular) list; insert between nodes (for example gcd values); delete N nodes after M nodes; replace a range of nodes with another list; collapse runs between sentinel values; unlinking with a trailing pointer / a pointer-to-pointer.
6. **Arithmetic on lists.** Add two numbers stored least-significant first (carry loop with dummy head); add two numbers stored most-significant first (stacks / reverse both / recursion with padding); plus one (find the last non-9 node / reverse / recursion); double a number (carry from the next node); multiply or subtract numbers stored as lists (same carry or borrow loop); compare two numbers stored as lists (length first, then digit by digit); convert a binary list to an integer (shift and add); lists of different lengths.
7. **Intersection and comparison.** Intersection of two lists (switch heads at the end / length difference / hash set of nodes); compare two lists for equality; palindrome (compare front with reversed back); twin sums (pair node i with node n-1-i); check whether one list is a path in a tree or another structure; count components in a list given a subset of values; intersection of lists that may contain cycles; equality by value vs by identity (is vs ==).
8. **Copy with a random pointer.** Deep copy with an old-to-new hash map (two passes) / one pass with a lazily-created map; O(1)-space interleaving (insert each copy after its original, set random pointers, split the lists apart); recursive copy with memoization; clone a list with a child pointer (multilevel); clone a doubly linked list; clone a graph as a generalization of the same map idea.
9. **Flattening and linking structure.** Flatten a multilevel doubly linked list (stack / recursion with a tail return); flatten a binary tree to a list (pre-order, Morris-style rewiring); link nodes at each tree level with a next pointer (O(1)-space level walk using the already-built links); flatten a list of lists by merging; convert a binary search tree to a sorted circular doubly linked list (in-order with a prev pointer); thread a structure through its own next pointers.
10. **Design with linked lists.** Hash map plus doubly linked list: LRU cache; LFU cache (frequency buckets of lists); all-O(1) key counters (buckets in order); expiring tokens by recency; browser history; circular queue / deque with a list or an array; front-middle-back queue (two deques or a list); text editor with a cursor; list-based hash set / hash map (chaining); skip list; max stack with O(1) pop-max (doubly linked list + ordered map); design a plain singly / doubly linked list (get, addAtHead, addAtTail, addAtIndex, deleteAtIndex); sentinel head and tail nodes so no operation has a null case.
11. **List and structure conversion.** Sorted list to height-balanced BST (middle split / in-order simulation); BST to sorted doubly linked list; binary tree to list; list to array (random access for binary search or two pointers); array to list (building with a dummy head); list to number and number to list; list to a stack for next-greater queries; list in a matrix (spiral fill); a linked list as a path to match in a tree.
12. **Splitting.** Split into k parts of nearly equal size (length, then size and remainder); split into odd and even position lists; split a circular list into two halves; split at a value (partition without stitching); keep M, delete N repeatedly; segment between two sentinel values; cut a range out and splice another in; split in the middle for sorting or palindrome checks; break at the cycle entrance.
13. **Cycles in functional graphs.** A linked list is a functional graph (each node has one next), so the cycle ideas are the same as in other functional graphs: detect a cycle (Floyd / visited set); find the entrance; find the cycle length (count steps from the meeting point); find the tail length; array values as next pointers (find the duplicate; the array is the graph); repeated digit-square map (happy number); circular array loop detection; Brent's algorithm. Cross-reference: [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md) group 2 (functional graph cycle detection, Floyd's tortoise and hare).
14. **Random node.** Reservoir sampling of size 1 over a list of unknown length (keep the i-th node with probability 1/i); reservoir sampling of size k; random pick when the length is known (count first, then walk); random pick with weights; random pick from a stream.
15. **O(1)-space variants.** Reverse the second half in place instead of using a stack (palindrome, reorder, twin sum); fast-slow instead of a visited set (cycle, duplicate); two-pointer switch instead of a hash set (intersection); interleaved copy instead of a map (random pointer); bottom-up merge sort instead of recursion; Morris-style traversal for tree-to-list; iterative instead of recursive to avoid stack depth on long lists; undoing the temporary reversal so the input list is restored.
16. **Pitfalls and edge cases.** Empty list, single node, two nodes; head changes (dummy head); losing next before overwriting it; advancing after an unlink; fast.next null checks; comparing nodes by identity, not value; a stale next on the old tail (a cycle in the output); off-by-one on 1-based vs 0-based positions; k greater than the length (reduce modulo); odd vs even length (two middles); deleting a node you only have a reference to (no previous); mutating an input you were told to keep; scans that need three nodes at once; recursion depth on long lists; doubly linked lists need four pointer updates per insert or delete.

## Coverage today

The data holds 1550 distinct problems. 58 have the pattern Linked List and 74 carry the tag Linked List or the pattern (16 sit in other patterns: Trees, Stack, Arrays & Hashing, Math & Geometry, Heap / Priority Queue). Of the 58 with the pattern, 9 are the must-learn problems of the 9 techniques; the rest are examples or practice.

| Technique | Name | Must-learn | Problems in the data |
|---|---|---|---|
| `Linked List:splice` | Editing and splicing nodes in place | LeetCode 203 Remove Linked List Elements | 19 |
| `Linked List:reverse` | Reversing pointers in place | LeetCode 206 Reverse Linked List | 11 |
| `Linked List:dummy-merge` | Dummy head and merge | LeetCode 21 Merge Two Sorted Lists | 7 |
| `Linked List:fast-slow` | Fast and slow pointers | LeetCode 141 Linked List Cycle | 6 |
| `Linked List:lru` | Hash map plus doubly linked list | LeetCode 146 LRU Cache | 5 |
| `Linked List:design-list` | Designing list-backed structures | LeetCode 622 Design Circular Queue | 5 |
| `Linked List:gap` | Two pointers a fixed gap apart | LeetCode 19 Remove Nth Node From End of List | 3 |
| `Linked List:kway-merge` | K-way merge with a heap | LeetCode 23 Merge k Sorted Lists | 1 |
| `Linked List:clone-map` | Copy with an old-to-new map | LeetCode 138 Copy List with Random Pointer | 1 |

The nine techniques cover the NeetCode spine: reversal, dummy head and merge, fast/slow, in-place splicing, the fixed gap, the clone map, list-backed design, the LRU pair and the k-way merge. The target list above adds what has no lesson yet: arithmetic and partition/reorder as their own groups, intersection/comparison, flattening, conversion to and from other structures, splitting, the functional-graph view of cycles, random node, the O(1)-space variants and the pitfall catalogue.

## Example problems per pattern

Up to four per group, taken from the data only. Format: `LeetCode <number> <title> (<difficulty>; <lists>)`.

1. **Reversal.**
    - LeetCode 206 Reverse Linked List (easy; blind75, neetcode150, neetcode250, all)
    - LeetCode 92 Reverse Linked List II (medium; neetcode250, all)
    - LeetCode 25 Reverse Nodes in k-Group (hard; neetcode150, neetcode250, all)
    - LeetCode 24 Swap Nodes in Pairs (medium; all)
2. **Fast and slow pointers.**
    - LeetCode 876 Middle of the Linked List (easy; all)
    - LeetCode 141 Linked List Cycle (easy; blind75, neetcode150, neetcode250, all)
    - LeetCode 19 Remove Nth Node From End of List (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 2095 Delete the Middle Node of a Linked List (medium; practice)
3. **Merging and sorting.**
    - LeetCode 21 Merge Two Sorted Lists (easy; blind75, neetcode150, neetcode250, all)
    - LeetCode 23 Merge k Sorted Lists (hard; blind75, neetcode150, neetcode250, all)
    - LeetCode 148 Sort List (medium; all)
    - LeetCode 355 Design Twitter (medium; neetcode150, neetcode250, all)
4. **Partition and reorder.**
    - LeetCode 86 Partition List (medium; all)
    - LeetCode 328 Odd Even Linked List (medium; practice)
    - LeetCode 143 Reorder List (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 61 Rotate List (medium; all)
5. **Dummy head and in-place surgery.**
    - LeetCode 203 Remove Linked List Elements (easy; all)
    - LeetCode 82 Remove Duplicates from Sorted List II (medium; practice)
    - LeetCode 1836 Remove Duplicates From an Unsorted Linked List (medium; all)
    - LeetCode 3217 Delete Nodes From Linked List Present in Array (medium; all)
6. **Arithmetic on lists.**
    - LeetCode 2 Add Two Numbers (medium; neetcode150, neetcode250, all)
    - LeetCode 445 Add Two Numbers II (medium; all)
    - LeetCode 369 Plus One Linked List (medium; all)
    - LeetCode 2816 Double a Number Represented as a Linked List (medium; practice)
7. **Intersection and comparison.**
    - LeetCode 160 Intersection of Two Linked Lists (easy; all)
    - LeetCode 234 Palindrome Linked List (easy; all)
    - LeetCode 2130 Maximum Twin Sum of a Linked List (medium; all)
    - LeetCode 817 Linked List Components (medium; practice)
8. **Copy with a random pointer.**
    - LeetCode 138 Copy List with Random Pointer (medium; neetcode150, neetcode250, all)
9. **Flattening and linking structure.**
    - LeetCode 430 Flatten a Multilevel Doubly Linked List (medium; practice)
    - LeetCode 114 Flatten Binary Tree to Linked List (medium; practice)
    - LeetCode 426 Convert Binary Search Tree to Sorted Doubly Linked List (medium; all)
    - LeetCode 117 Populating Next Right Pointers in Each Node II (medium; practice)
10. **Design with linked lists.**
    - LeetCode 146 LRU Cache (medium; neetcode150, neetcode250, all)
    - LeetCode 460 LFU Cache (hard; neetcode250, all)
    - LeetCode 707 Design Linked List (medium; all)
    - LeetCode 1472 Design Browser History (medium; all)
11. **List and structure conversion.**
    - LeetCode 109 Convert Sorted List to Binary Search Tree (medium; practice)
    - LeetCode 1019 Next Greater Node In Linked List (medium; practice)
    - LeetCode 1290 Convert Binary Number in a Linked List to Integer (easy; practice)
    - LeetCode 2326 Spiral Matrix IV (medium; all)
12. **Splitting.**
    - LeetCode 725 Split Linked List in Parts (medium; all)
    - LeetCode 1474 Delete N Nodes After M Nodes of a Linked List (easy; all)
    - LeetCode 2181 Merge Nodes in Between Zeros (medium; all)
    - LeetCode 1669 Merge In Between Linked Lists (medium; all)
13. **Cycles in functional graphs.**
    - LeetCode 141 Linked List Cycle (easy; blind75, neetcode150, neetcode250, all)
    - LeetCode 142 Linked List Cycle II (medium; practice)
    - LeetCode 287 Find the Duplicate Number (medium; neetcode150, neetcode250, all)
    - LeetCode 202 Happy Number (easy; neetcode150, neetcode250, all)
14. **Random node.**
    - LeetCode 382 Linked List Random Node (medium; practice)
15. **O(1)-space variants.**
    - LeetCode 234 Palindrome Linked List (easy; all)
    - LeetCode 143 Reorder List (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 1265 Print Immutable Linked List in Reverse (medium; all)
    - LeetCode 2130 Maximum Twin Sum of a Linked List (medium; all)
16. **Pitfalls and edge cases.**
    - LeetCode 237 Delete Node in a Linked List (medium; practice)
    - LeetCode 708 Insert into a Sorted Circular Linked List (medium; all)
    - LeetCode 82 Remove Duplicates from Sorted List II (medium; practice)
    - LeetCode 2058 Find the Minimum and Maximum Number of Nodes Between Critical Points (medium; all)

## Gaps

Variants named above that have no problem in the data: no problem in the data: needs one from LeetCode (each example is to be picked and checked on LeetCode, never from memory).

- Reverse alternate k-groups (reverse k, skip k, repeat)
- Reverse a doubly linked list (swap prev and next)
- Counting-based sort of a three-value list, and selection sort on lists
- Split a circular list into two halves
- Cycle length and tail length measurement (count steps after the meeting point)
- Brent's cycle algorithm
- Circular array loop detection (a functional graph on an array with direction rules)
- Reservoir sampling of size k, and weighted random pick from a list
- Multiply or subtract numbers stored as lists
- Compare two numbers stored as lists
- Deep copy of a multilevel or doubly linked list
- Intersection of two lists that may contain cycles
- XOR linked list and unrolled linked list as designs
- Palindrome by recursion with a front pointer

Other open points:

- Groups with a single example in the data: Copy with a random pointer (LeetCode 138) and Random node (LeetCode 382). Both need a second example from LeetCode.
- 16 problems tagged Linked List live under other patterns; their lessons teach the other pattern, so the linked-list lesson should link to them rather than copy them.
- Cycles in functional graphs overlap Floyd's tortoise and hare in the Graphs target list; decide which lesson owns the template and which only cross-references it.
- Tabs (iterative / recursive, heap / divide and conquer for the k-way merge, map / interleaved for the copy) need the mockup before any lesson work.
