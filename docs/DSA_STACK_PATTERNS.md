# Stack patterns: the exhaustive target list

The target for the Stack pattern lessons, in the style of [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md). The rule is in
[DSA.md](DSA.md), decision 32: a topic's patterns section is exhaustive, patterns without a NeetCode problem get **example problems**
from LeetCode, and variants of one pattern are **tabs** of one lesson. The monotonic queue and queue groups are included because
the data tags those problems together with Stack problems; their lessons live under Sliding Window and Linked List today.

Status: documented only. Today `content/dsa/lessons/stack.toml` has 9 techniques (simulate-stack, matching, design-queue-stack,
aux-stack, expression, mono-stack, nested, calculator, mono-contrib). Building the rest needs a mockup of the tabs first, then
lessons and picked example problems. The example problems below come only from `content/dsa/problems.json` and
`content/dsa/practice.json`; a pattern with none says so and needs a problem picked from LeetCode and checked there, never from memory.

Items written *a / b* in a group are variants for tabs where one lesson covers both (for example "one kind / several kinds" or
"to the right / to the left").

1. **Matching and nesting.** Balanced brackets, one kind / several kinds; Minimum insertions to balance (counter or stack); Minimum removals to make valid (stack of indices to delete); Longest valid parentheses (stack of indices / two-pass counters / DP); Wildcard parentheses (range of open counts / two index stacks); Nesting depth and depth assignment; Score by depth (stack of partial scores); Strip the outer layer; Reverse inside each pair of brackets; Tag and markup validation; Per-key stack (nearest earlier unmatched partner); Enumerate or repair invalid strings (backtracking, BFS; cross-reference).
2. **Monotonic stack.** Next greater / next smaller element (value, to the right / to the left); Circular array (scan 2n, index mod n); Distance to the next greater (days, span, visible people); Largest rectangle in a histogram (left and right boundary of each bar); Maximal rectangle / submatrices of ones (histogram per row); Contribution counting (sum of subarray minimums / maximums / ranges); Remove k digits (pop while the new digit is smaller); 132 pattern (right to left, stack of candidates for the middle); Line of sight (buildings with a view); Car fleet (sort, then stack of arrival times); Trapping rain water (stack of bars, versus two pointers); Max chunks to make sorted (stack of chunk maximums); Linked-list monotonic stack (remove nodes, next greater node); Decreasing stack plus backward scan (maximum width ramp); Two stacks (second greater element); Offline queries with a monotonic stack (meeting buildings); Preorder validity with a lower-bound stack (BST from preorder); Binary searchable elements (prefix maximum / suffix minimum).
3. **Expression evaluation.** Postfix (reverse Polish); Infix with + - * / (stack of terms); Infix with parentheses and unary minus (sign stack); Infix with every operator and parentheses; Prefix evaluation (scan right to left); Shunting-yard (infix to postfix with an operator stack); Operators that cycle (clumsy factorial); Right-associative operators (ternary expressions); Boolean expressions with nested calls; Expressions with scopes and variables (Lisp); Symbolic algebra (polynomial arithmetic); Splitting at each operator (divide and conquer; cross-reference); Inserting operators between digits (backtracking with the last operand; cross-reference).
4. **Stack and queue design.** Min stack / max stack (stack of pairs); Max stack with pop-max (linked list plus ordered map); Frequency stack (count to stack of values); Queue from two stacks / stack from queues; Stack with lazy increments; Undo / redo (two stacks, or a list and a cursor); Iterators over a stack (BST, nested list, peeking); Circular queue / circular deque; Front, middle and back operations (two deques); Online monotonic design (stock span); Queue over a data stream (moving average, hit counter, first unique); Set of stacks with capacity (plates).
5. **Simulation with a stack.** Replay operations, with undo (baseball, stars, backspace, clear digits); Cancel adjacent equal items (pairs, runs of k); Remove a pattern repeatedly (substring at the top of the stack); Collisions (asteroids, robots, cars); Path normalisation (cd, .., .); Call-stack timing (exclusive time of functions); Push/pop sequence validity (can this output come from a stack?).
6. **Iterative DFS and tree traversal.** Inorder (go left, pop, go right); Preorder (push right, then left); Postorder (two stacks / last-visited pointer / reversed modified preorder); Lazy iterator (BST iterator, successor); Flatten in place using a stack; Stack of iterators (flatten a nested list); Graph and grid DFS with an explicit stack (cross-reference); Enter / exit markers on the stack (postorder work without recursion); Build a tree from a traversal with a stack.
7. **Sorting with stacks.** Stack-sortable and stack-realisable sequences; Sort a stack with one extra stack or with recursion; Stack as a holding buffer for the lexicographically smallest output; Chunks that sort independently (monotonic stack of maximums); Minimal unsorted window (stack or two scans); Avoiding the 132 pattern (stack-sortable permutations); Permutation from an increase/decrease string (reverse runs with a stack); Stack-based iterative quick sort / merge sort (cross-reference).
8. **Monotonic queue (cross-reference: Sliding Window).** Window maximum / minimum; Two deques: max and min inside the window; Shortest subarray with sum at least k (deque over prefix sums); DP optimisation (best of the last k states); Circular subarray with a window of fixed span; Binary search on the answer with a deque check; Sliding window median (heaps or sorted multiset; contrast).
9. **Stack and greedy.** Lexicographically smallest after deleting k (pop while worse); Smallest subsequence of distinct letters (last occurrence plus in-stack set); Merge two best subsequences into the maximum number; Greedy removal order (higher-scoring pair first); Minimum operations by popping larger values (zero out an array); Removing stars with the smallest letter first; Ranges from a monotonic stack, then pick greedily (prime score); Counters instead of a stack (balance, open count).
10. **Stack and DP.** Longest valid parentheses (dp[i] from the matching opener); Histogram per row (maximal rectangle); DP over the nearest smaller (dp[i] built from dp[prev smaller]); Prefix sums with a monotonic stack (min-product); Minimum deletions to balance (stack versus DP); Minimum additions to complete a pattern (state per letter); Monotonic queue DP (cross-reference); Interval DP that removes elements (stack of segments).
11. **Parsing.** Nested repeat encoding (stack of (text, count)); Formula with counts (stack of maps); Nested data structures (lists inside lists); Expression grammars (ternary, boolean, Lisp, full calculator); Brace expansion (union and product on a stack); Paths and file systems with depth; Tag validators; Indexing into an encoded string without expanding it (work backwards); Recursive descent versus an explicit stack; Tokeniser (numbers, signs, identifiers).
12. **Recursion to iteration.** Tree traversals with an explicit stack; Process a list from the end (print in reverse, digits from the least significant); Palindrome checks with a stack of values; Parser: recursive to stack of contexts; Deep recursion that overflows the call stack (DFS on large inputs); Divide and conquer as a stack of subproblems; Backtracking with an explicit stack of choices; Tail recursion to a loop; Memoised recursion to bottom-up (cross-reference: DP).
13. **Queues next to stacks (round simulation and streams).** Round-by-round simulation with a queue; Circular elimination (Josephus); Two queues competing (scheduling, doors); Interleaving iterators; Stack from queues, queue from stacks; Level-order BFS (cross-reference: Trees, Graphs).
14. **Core implementation patterns.** List used as a stack (append / pop, top is index -1); Store indices or store values; Entries that carry an aggregate (value, running minimum); Sentinel to flush the stack at the end; Strict versus non-strict comparison and tie-breaking; Two passes for circular input; Run-length entries (value, count); Lazy propagation and lazy deletion; Amortised analysis (each item is pushed and popped once); Stack of contexts (saved state per nesting level); Deque used as a stack at one end and a queue at the other.

## Coverage today

The 9 techniques of `stack.toml` and where each target group stands:

| Group | Existing technique | Status |
| --- | --- | --- |
| 1 Matching and nesting | Stack:matching, Stack:nested | Basic matching covered; repair, depth, score and markup variants missing. |
| 2 Monotonic stack | Stack:mono-stack, Stack:mono-contrib | Next greater, distance and contribution counting covered; histogram, remove-k, 132, car fleet and two-stack variants missing. |
| 3 Expression evaluation | Stack:expression, Stack:calculator | Postfix and precedence calculator covered; parentheses with unary minus, prefix and shunting-yard missing. |
| 4 Stack and queue design | Stack:aux-stack, Stack:design-queue-stack | Min stack and queue-from-stacks covered; frequency stack, undo/redo, lazy increment and iterators missing. |
| 5 Simulation | Stack:simulate-stack | One template (asteroids); path, call-stack timing and pattern removal missing. |
| 6 Iterative DFS | none (Trees:inorder holds the problems) | Not a Stack lesson today. |
| 7 Sorting with stacks | none | Not covered. |
| 8 Monotonic queue | Sliding Window:mono-deque | Covered under Sliding Window; cross-reference only. |
| 9 Stack and greedy | Stack:mono-contrib (partly) | Only inside the monotonic lessons. |
| 10 Stack and DP | none | Not covered. |
| 11 Parsing | Stack:nested | Decode string covered; formula, grammar and brace expansion missing. |
| 12 Recursion to iteration | none | Not covered. |
| 13 Queues next to stacks | Arrays & Hashing:simulation, Linked List:design-list | Covered elsewhere; cross-reference only. |
| 14 Core implementation patterns | pitfalls inside each technique | Not a lesson of its own. |

Data today: 75 problems have the pattern Stack (9 of them must-learn, the rest practice or all-list extras); 81 problems have a `Stack:` technique; 154 problems in total have the Stack pattern or a Stack, Monotonic Stack, Queue or Monotonic Queue tag. Technique sizes: mono-stack 18, simulate-stack 16, nested 10, matching 7, aux-stack 7, design-queue-stack 6, mono-contrib 6, calculator 6, expression 5.

## Example problems per pattern

Up to four per pattern, from the data only, as `LeetCode <number> <title> (<difficulty>; <lists>)`.

### 1. Matching and nesting

- **Balanced brackets, one kind / several kinds**
  - LeetCode 20 Valid Parentheses (easy; blind75, neetcode150, neetcode250, all)
  - LeetCode 1003 Check If Word Is Valid After Substitutions (medium; practice)
- **Minimum insertions to balance (counter or stack)**
  - LeetCode 921 Minimum Add to Make Parentheses Valid (medium; all)
  - LeetCode 1541 Minimum Insertions to Balance a Parentheses String (medium; practice)
  - LeetCode 1963 Minimum Number of Swaps to Make the String Balanced (medium; all)
- **Minimum removals to make valid (stack of indices to delete)**
  - LeetCode 1249 Minimum Remove to Make Valid Parentheses (medium; all)
- **Longest valid parentheses (stack of indices / two-pass counters / DP)**
  - LeetCode 32 Longest Valid Parentheses (hard; practice)
- **Wildcard parentheses (range of open counts / two index stacks)**
  - LeetCode 678 Valid Parenthesis String (medium; neetcode150, neetcode250, all)
  - LeetCode 2116 Check if a Parentheses String Can Be Valid (medium; all)
- **Nesting depth and depth assignment**
  - LeetCode 1614 Maximum Nesting Depth of the Parentheses (easy; all)
  - LeetCode 1111 Maximum Nesting Depth of Two Valid Parentheses Strings (medium; practice)
- **Score by depth (stack of partial scores)**
  - LeetCode 856 Score of Parentheses (medium; practice)
- **Strip the outer layer**
  - LeetCode 1021 Remove Outermost Parentheses (easy; practice)
- **Reverse inside each pair of brackets**
  - LeetCode 1190 Reverse Substrings Between Each Pair of Parentheses (medium; all)
- **Tag and markup validation**
  - LeetCode 591 Tag Validator (hard; practice)
- **Per-key stack (nearest earlier unmatched partner)**
  - LeetCode 3412 Find Mirror Score of a String (medium; practice)
- **Enumerate or repair invalid strings (backtracking, BFS; cross-reference)**
  - LeetCode 301 Remove Invalid Parentheses (hard; practice)
  - LeetCode 22 Generate Parentheses (medium; neetcode150, neetcode250, all)

### 2. Monotonic stack

- **Next greater / next smaller element (value, to the right / to the left)**
  - LeetCode 496 Next Greater Element I (easy; all)
  - LeetCode 1475 Final Prices With a Special Discount in a Shop (easy; all)
  - LeetCode 1019 Next Greater Node In Linked List (medium; practice)
- **Circular array (scan 2n, index mod n)**
  - LeetCode 503 Next Greater Element II (medium; practice)
- **Distance to the next greater (days, span, visible people)**
  - LeetCode 739 Daily Temperatures (medium; neetcode150, neetcode250, all)
  - LeetCode 901 Online Stock Span (medium; neetcode250, all)
  - LeetCode 1944 Number of Visible People in a Queue (hard; all)
  - LeetCode 962 Maximum Width Ramp (medium; all)
- **Largest rectangle in a histogram (left and right boundary of each bar)**
  - LeetCode 84 Largest Rectangle in Histogram (hard; neetcode150, neetcode250, all)
  - LeetCode 1793 Maximum Score of a Good Subarray (hard; all)
  - LeetCode 1856 Maximum Subarray Min-Product (medium; all)
- **Maximal rectangle / submatrices of ones (histogram per row)**
  - LeetCode 85 Maximal Rectangle (hard; practice)
  - LeetCode 1504 Count Submatrices With All Ones (medium; practice)
- **Contribution counting (sum of subarray minimums / maximums / ranges)**
  - LeetCode 907 Sum of Subarray Minimums (medium; all)
  - LeetCode 2104 Sum of Subarray Ranges (medium; practice)
  - LeetCode 2281 Sum of Total Strength of Wizards (hard; practice)
  - LeetCode 2818 Apply Operations to Maximize Score (hard; all)
- **Remove k digits (pop while the new digit is smaller)**
  - LeetCode 402 Remove K Digits (medium; all)
- **132 pattern (right to left, stack of candidates for the middle)**
  - LeetCode 456 132 Pattern (medium; all)
- **Line of sight (buildings with a view)**
  - LeetCode 1762 Buildings With an Ocean View (medium; all)
- **Car fleet (sort, then stack of arrival times)**
  - LeetCode 853 Car Fleet (medium; neetcode150, neetcode250, all)
- **Trapping rain water (stack of bars, versus two pointers)**
  - LeetCode 42 Trapping Rain Water (hard; neetcode150, neetcode250, all)
- **Max chunks to make sorted (stack of chunk maximums)**
  - LeetCode 769 Max Chunks To Make Sorted (medium; all)
  - LeetCode 768 Max Chunks To Make Sorted II (hard; practice)
- **Linked-list monotonic stack (remove nodes, next greater node)**
  - LeetCode 2487 Remove Nodes From Linked List (medium; all)
  - LeetCode 1019 Next Greater Node In Linked List (medium; practice)
- **Decreasing stack plus backward scan (maximum width ramp)**
  - LeetCode 962 Maximum Width Ramp (medium; all)
- **Two stacks (second greater element)**
  - LeetCode 2454 Next Greater Element IV (hard; practice)
- **Offline queries with a monotonic stack (meeting buildings)**
  - LeetCode 2940 Find Building Where Alice and Bob Can Meet (hard; all)
- **Preorder validity with a lower-bound stack (BST from preorder)**
  - LeetCode 255 Verify Preorder Sequence in Binary Search Tree (medium; all)
  - LeetCode 1008 Construct Binary Search Tree from Preorder Traversal (medium; practice)
- **Binary searchable elements (prefix maximum / suffix minimum)**
  - LeetCode 1966 Binary Searchable Numbers in an Unsorted Array (medium; all)

### 3. Expression evaluation

- **Postfix (reverse Polish)**
  - LeetCode 150 Evaluate Reverse Polish Notation (medium; neetcode150, neetcode250, all)
- **Infix with + - * / (stack of terms)**
  - LeetCode 227 Basic Calculator II (medium; all)
- **Infix with parentheses and unary minus (sign stack)**
  - LeetCode 224 Basic Calculator (hard; practice)
- **Infix with every operator and parentheses**
  - LeetCode 772 Basic Calculator III (hard; all)
- **Prefix evaluation (scan right to left)**
  - no problem in the data: needs one from LeetCode
- **Shunting-yard (infix to postfix with an operator stack)**
  - no problem in the data: needs one from LeetCode
- **Operators that cycle (clumsy factorial)**
  - LeetCode 1006 Clumsy Factorial (medium; practice)
- **Right-associative operators (ternary expressions)**
  - LeetCode 439 Ternary Expression Parser (medium; all)
- **Boolean expressions with nested calls**
  - LeetCode 1106 Parsing A Boolean Expression (hard; all)
- **Expressions with scopes and variables (Lisp)**
  - LeetCode 736 Parse Lisp Expression (hard; practice)
- **Symbolic algebra (polynomial arithmetic)**
  - no problem in the data: needs one from LeetCode
- **Splitting at each operator (divide and conquer; cross-reference)**
  - LeetCode 241 Different Ways to Add Parentheses (medium; all)
- **Inserting operators between digits (backtracking with the last operand; cross-reference)**
  - LeetCode 282 Expression Add Operators (hard; practice)

### 4. Stack and queue design

- **Min stack / max stack (stack of pairs)**
  - LeetCode 155 Min Stack (medium; neetcode150, neetcode250, all)
- **Max stack with pop-max (linked list plus ordered map)**
  - LeetCode 716 Max Stack (hard; all)
- **Frequency stack (count to stack of values)**
  - LeetCode 895 Maximum Frequency Stack (hard; neetcode250, all)
- **Queue from two stacks / stack from queues**
  - LeetCode 232 Implement Queue using Stacks (easy; neetcode250, all)
  - LeetCode 225 Implement Stack using Queues (easy; neetcode250, all)
- **Stack with lazy increments**
  - LeetCode 1381 Design a Stack With Increment Operation (medium; practice)
- **Undo / redo (two stacks, or a list and a cursor)**
  - LeetCode 1472 Design Browser History (medium; all)
  - LeetCode 2296 Design a Text Editor (hard; practice)
- **Iterators over a stack (BST, nested list, peeking)**
  - LeetCode 173 Binary Search Tree Iterator (medium; all)
  - LeetCode 341 Flatten Nested List Iterator (medium; all)
  - LeetCode 284 Peeking Iterator (medium; practice)
- **Circular queue / circular deque**
  - LeetCode 622 Design Circular Queue (medium; neetcode250, all)
  - LeetCode 641 Design Circular Deque (medium; practice)
- **Front, middle and back operations (two deques)**
  - LeetCode 1670 Design Front Middle Back Queue (medium; practice)
- **Online monotonic design (stock span)**
  - LeetCode 901 Online Stock Span (medium; neetcode250, all)
- **Queue over a data stream (moving average, hit counter, first unique)**
  - LeetCode 346 Moving Average from Data Stream (easy; all)
  - LeetCode 362 Design Hit Counter (medium; all)
  - LeetCode 1429 First Unique Number (medium; all)
  - LeetCode 387 First Unique Character in a String (easy; all)
- **Set of stacks with capacity (plates)**
  - no problem in the data: needs one from LeetCode

### 5. Simulation with a stack

- **Replay operations, with undo (baseball, stars, backspace, clear digits)**
  - LeetCode 682 Baseball Game (easy; neetcode250, all)
  - LeetCode 2390 Removing Stars From a String (medium; all)
  - LeetCode 844 Backspace String Compare (easy; all)
  - LeetCode 3174 Clear Digits (easy; all)
- **Cancel adjacent equal items (pairs, runs of k)**
  - LeetCode 1047 Remove All Adjacent Duplicates In String (easy; practice)
  - LeetCode 1209 Remove All Adjacent Duplicates in String II (medium; all)
  - LeetCode 1544 Make The String Great (easy; all)
- **Remove a pattern repeatedly (substring at the top of the stack)**
  - LeetCode 1910 Remove All Occurrences of a Substring (medium; practice)
  - LeetCode 2696 Minimum String Length After Removing Substrings (easy; all)
  - LeetCode 1717 Maximum Score From Removing Substrings (medium; all)
- **Collisions (asteroids, robots, cars)**
  - LeetCode 735 Asteroid Collision (medium; neetcode250, all)
  - LeetCode 2751 Robot Collisions (hard; all)
  - LeetCode 2211 Count Collisions on a Road (medium; practice)
- **Path normalisation (cd, .., .)**
  - LeetCode 71 Simplify Path (medium; neetcode250, all)
  - LeetCode 1598 Crawler Log Folder (easy; all)
  - LeetCode 388 Longest Absolute File Path (medium; practice)
- **Call-stack timing (exclusive time of functions)**
  - LeetCode 636 Exclusive Time of Functions (medium; practice)
- **Push/pop sequence validity (can this output come from a stack?)**
  - LeetCode 946 Validate Stack Sequences (medium; all)
  - LeetCode 1441 Build an Array With Stack Operations (medium; practice)

### 6. Iterative DFS and tree traversal

- **Inorder (go left, pop, go right)**
  - LeetCode 94 Binary Tree Inorder Traversal (easy; neetcode250, all)
  - LeetCode 230 Kth Smallest Element in a BST (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 98 Validate Binary Search Tree (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 538 Convert BST to Greater Tree (medium; all)
- **Preorder (push right, then left)**
  - LeetCode 144 Binary Tree Preorder Traversal (easy; neetcode250, all)
  - LeetCode 589 N-ary Tree Preorder Traversal (easy; practice)
- **Postorder (two stacks / last-visited pointer / reversed modified preorder)**
  - LeetCode 145 Binary Tree Postorder Traversal (easy; neetcode250, all)
  - LeetCode 590 N-ary Tree Postorder Traversal (easy; all)
- **Lazy iterator (BST iterator, successor)**
  - LeetCode 173 Binary Search Tree Iterator (medium; all)
  - LeetCode 510 Inorder Successor in BST II (medium; all)
- **Flatten in place using a stack**
  - LeetCode 114 Flatten Binary Tree to Linked List (medium; practice)
  - LeetCode 430 Flatten a Multilevel Doubly Linked List (medium; practice)
  - LeetCode 426 Convert Binary Search Tree to Sorted Doubly Linked List (medium; all)
- **Stack of iterators (flatten a nested list)**
  - LeetCode 341 Flatten Nested List Iterator (medium; all)
- **Graph and grid DFS with an explicit stack (cross-reference)**
  - LeetCode 200 Number of Islands (medium; blind75, neetcode150, neetcode250, all)
- **Enter / exit markers on the stack (postorder work without recursion)**
  - LeetCode 145 Binary Tree Postorder Traversal (easy; neetcode250, all)
  - LeetCode 1028 Recover a Tree From Preorder Traversal (hard; all)
- **Build a tree from a traversal with a stack**
  - LeetCode 1008 Construct Binary Search Tree from Preorder Traversal (medium; practice)
  - LeetCode 1028 Recover a Tree From Preorder Traversal (hard; all)
  - LeetCode 889 Construct Binary Tree from Preorder and Postorder Traversal (medium; all)

### 7. Sorting with stacks

- **Stack-sortable and stack-realisable sequences**
  - LeetCode 946 Validate Stack Sequences (medium; all)
- **Sort a stack with one extra stack or with recursion**
  - no problem in the data: needs one from LeetCode
- **Stack as a holding buffer for the lexicographically smallest output**
  - LeetCode 2434 Using a Robot to Print the Lexicographically Smallest String (medium; practice)
- **Chunks that sort independently (monotonic stack of maximums)**
  - LeetCode 769 Max Chunks To Make Sorted (medium; all)
  - LeetCode 768 Max Chunks To Make Sorted II (hard; practice)
- **Minimal unsorted window (stack or two scans)**
  - LeetCode 581 Shortest Unsorted Continuous Subarray (medium; practice)
- **Avoiding the 132 pattern (stack-sortable permutations)**
  - LeetCode 456 132 Pattern (medium; all)
- **Permutation from an increase/decrease string (reverse runs with a stack)**
  - LeetCode 484 Find Permutation (medium; all)
  - LeetCode 2375 Construct Smallest Number From DI String (medium; all)
- **Stack-based iterative quick sort / merge sort (cross-reference)**
  - LeetCode 912 Sort an Array (medium; neetcode250, all)

### 8. Monotonic queue (cross-reference: Sliding Window)

- **Window maximum / minimum**
  - LeetCode 239 Sliding Window Maximum (hard; neetcode150, neetcode250, all)
- **Two deques: max and min inside the window**
  - LeetCode 1438 Longest Continuous Subarray With Absolute Diff Less Than or Equal to Limit (medium; all)
  - LeetCode 2762 Continuous Subarrays (medium; practice)
  - LeetCode 3578 Count Partitions With Max-Min Difference at Most K (medium; practice)
  - LeetCode 2444 Count Subarrays With Fixed Bounds (hard; practice)
- **Shortest subarray with sum at least k (deque over prefix sums)**
  - LeetCode 862 Shortest Subarray with Sum at Least K (hard; all)
- **DP optimisation (best of the last k states)**
  - LeetCode 1425 Constrained Subsequence Sum (hard; all)
  - LeetCode 1696 Jump Game VI (medium; practice)
- **Circular subarray with a window of fixed span**
  - LeetCode 918 Maximum Sum Circular Subarray (medium; neetcode250, all)
- **Binary search on the answer with a deque check**
  - LeetCode 2398 Maximum Number of Robots Within Budget (hard; practice)
  - LeetCode 2528 Maximize the Minimum Powered City (hard; practice)
- **Sliding window median (heaps or sorted multiset; contrast)**
  - no problem in the data: needs one from LeetCode

### 9. Stack and greedy

- **Lexicographically smallest after deleting k (pop while worse)**
  - LeetCode 402 Remove K Digits (medium; all)
- **Smallest subsequence of distinct letters (last occurrence plus in-stack set)**
  - LeetCode 316 Remove Duplicate Letters (medium; practice)
  - LeetCode 1081 Smallest Subsequence of Distinct Characters (medium; practice)
- **Merge two best subsequences into the maximum number**
  - LeetCode 321 Create Maximum Number (hard; practice)
- **Greedy removal order (higher-scoring pair first)**
  - LeetCode 1717 Maximum Score From Removing Substrings (medium; all)
- **Minimum operations by popping larger values (zero out an array)**
  - LeetCode 3542 Minimum Operations to Convert All Elements to Zero (medium; practice)
  - LeetCode 1526 Minimum Number of Increments on Subarrays to Form a Target Array (hard; all)
- **Removing stars with the smallest letter first**
  - LeetCode 3170 Lexicographically Minimum String After Removing Stars (medium; practice)
- **Ranges from a monotonic stack, then pick greedily (prime score)**
  - LeetCode 2818 Apply Operations to Maximize Score (hard; all)
- **Counters instead of a stack (balance, open count)**
  - LeetCode 1963 Minimum Number of Swaps to Make the String Balanced (medium; all)
  - LeetCode 1541 Minimum Insertions to Balance a Parentheses String (medium; practice)
  - LeetCode 921 Minimum Add to Make Parentheses Valid (medium; all)

### 10. Stack and DP

- **Longest valid parentheses (dp[i] from the matching opener)**
  - LeetCode 32 Longest Valid Parentheses (hard; practice)
- **Histogram per row (maximal rectangle)**
  - LeetCode 85 Maximal Rectangle (hard; practice)
  - LeetCode 1504 Count Submatrices With All Ones (medium; practice)
- **DP over the nearest smaller (dp[i] built from dp[prev smaller])**
  - LeetCode 907 Sum of Subarray Minimums (medium; all)
  - LeetCode 2866 Beautiful Towers II (medium; practice)
- **Prefix sums with a monotonic stack (min-product)**
  - LeetCode 1856 Maximum Subarray Min-Product (medium; all)
- **Minimum deletions to balance (stack versus DP)**
  - LeetCode 1653 Minimum Deletions to Make String Balanced (medium; all)
- **Minimum additions to complete a pattern (state per letter)**
  - LeetCode 2645 Minimum Additions to Make Valid String (medium; practice)
- **Monotonic queue DP (cross-reference)**
  - LeetCode 1425 Constrained Subsequence Sum (hard; all)
  - LeetCode 1696 Jump Game VI (medium; practice)
- **Interval DP that removes elements (stack of segments)**
  - no problem in the data: needs one from LeetCode

### 11. Parsing

- **Nested repeat encoding (stack of (text, count))**
  - LeetCode 394 Decode String (medium; neetcode250, all)
- **Formula with counts (stack of maps)**
  - LeetCode 726 Number of Atoms (hard; all)
- **Nested data structures (lists inside lists)**
  - LeetCode 385 Mini Parser (medium; practice)
  - LeetCode 341 Flatten Nested List Iterator (medium; all)
- **Expression grammars (ternary, boolean, Lisp, full calculator)**
  - LeetCode 439 Ternary Expression Parser (medium; all)
  - LeetCode 1106 Parsing A Boolean Expression (hard; all)
  - LeetCode 736 Parse Lisp Expression (hard; practice)
  - LeetCode 772 Basic Calculator III (hard; all)
- **Brace expansion (union and product on a stack)**
  - LeetCode 1096 Brace Expansion II (hard; practice)
  - LeetCode 1087 Brace Expansion (medium; all)
- **Paths and file systems with depth**
  - LeetCode 388 Longest Absolute File Path (medium; practice)
  - LeetCode 71 Simplify Path (medium; neetcode250, all)
- **Tag validators**
  - LeetCode 591 Tag Validator (hard; practice)
- **Indexing into an encoded string without expanding it (work backwards)**
  - LeetCode 880 Decoded String at Index (medium; practice)
- **Recursive descent versus an explicit stack**
  - LeetCode 394 Decode String (medium; neetcode250, all)
  - LeetCode 224 Basic Calculator (hard; practice)
- **Tokeniser (numbers, signs, identifiers)**
  - LeetCode 227 Basic Calculator II (medium; all)
  - LeetCode 726 Number of Atoms (hard; all)
  - LeetCode 224 Basic Calculator (hard; practice)

### 12. Recursion to iteration

- **Tree traversals with an explicit stack**
  - LeetCode 94 Binary Tree Inorder Traversal (easy; neetcode250, all)
  - LeetCode 144 Binary Tree Preorder Traversal (easy; neetcode250, all)
  - LeetCode 145 Binary Tree Postorder Traversal (easy; neetcode250, all)
- **Process a list from the end (print in reverse, digits from the least significant)**
  - LeetCode 1265 Print Immutable Linked List in Reverse (medium; all)
  - LeetCode 445 Add Two Numbers II (medium; all)
- **Palindrome checks with a stack of values**
  - LeetCode 234 Palindrome Linked List (easy; all)
  - LeetCode 2130 Maximum Twin Sum of a Linked List (medium; all)
- **Parser: recursive to stack of contexts**
  - LeetCode 394 Decode String (medium; neetcode250, all)
  - LeetCode 224 Basic Calculator (hard; practice)
- **Deep recursion that overflows the call stack (DFS on large inputs)**
  - LeetCode 200 Number of Islands (medium; blind75, neetcode150, neetcode250, all)
  - LeetCode 590 N-ary Tree Postorder Traversal (easy; all)
- **Divide and conquer as a stack of subproblems**
  - LeetCode 912 Sort an Array (medium; neetcode250, all)
  - LeetCode 241 Different Ways to Add Parentheses (medium; all)
- **Backtracking with an explicit stack of choices**
  - no problem in the data: needs one from LeetCode
- **Tail recursion to a loop**
  - no problem in the data: needs one from LeetCode
- **Memoised recursion to bottom-up (cross-reference: DP)**
  - no problem in the data: needs one from LeetCode

### 13. Queues next to stacks (round simulation and streams)

- **Round-by-round simulation with a queue**
  - LeetCode 1700 Number of Students Unable to Eat Lunch (easy; all)
  - LeetCode 2073 Time Needed to Buy Tickets (easy; all)
  - LeetCode 649 Dota2 Senate (medium; neetcode250, all)
  - LeetCode 950 Reveal Cards In Increasing Order (medium; all)
- **Circular elimination (Josephus)**
  - LeetCode 1823 Find the Winner of the Circular Game (medium; all)
- **Two queues competing (scheduling, doors)**
  - LeetCode 2534 Time Taken to Cross the Door (hard; all)
  - LeetCode 649 Dota2 Senate (medium; neetcode250, all)
- **Interleaving iterators**
  - LeetCode 281 Zigzag Iterator (medium; all)
- **Stack from queues, queue from stacks**
  - LeetCode 225 Implement Stack using Queues (easy; neetcode250, all)
  - LeetCode 232 Implement Queue using Stacks (easy; neetcode250, all)
- **Level-order BFS (cross-reference: Trees, Graphs)**
  - no problem in the data: needs one from LeetCode

### 14. Core implementation patterns

- **List used as a stack (append / pop, top is index -1)**
  - LeetCode 682 Baseball Game (easy; neetcode250, all)
- **Store indices or store values**
  - LeetCode 739 Daily Temperatures (medium; neetcode150, neetcode250, all)
  - LeetCode 496 Next Greater Element I (easy; all)
- **Entries that carry an aggregate (value, running minimum)**
  - LeetCode 155 Min Stack (medium; neetcode150, neetcode250, all)
- **Sentinel to flush the stack at the end**
  - LeetCode 227 Basic Calculator II (medium; all)
  - LeetCode 84 Largest Rectangle in Histogram (hard; neetcode150, neetcode250, all)
- **Strict versus non-strict comparison and tie-breaking**
  - LeetCode 907 Sum of Subarray Minimums (medium; all)
- **Two passes for circular input**
  - LeetCode 503 Next Greater Element II (medium; practice)
- **Run-length entries (value, count)**
  - LeetCode 901 Online Stock Span (medium; neetcode250, all)
- **Lazy propagation and lazy deletion**
  - LeetCode 1381 Design a Stack With Increment Operation (medium; practice)
- **Amortised analysis (each item is pushed and popped once)**
  - LeetCode 232 Implement Queue using Stacks (easy; neetcode250, all)
- **Stack of contexts (saved state per nesting level)**
  - LeetCode 726 Number of Atoms (hard; all)
  - LeetCode 394 Decode String (medium; neetcode250, all)
- **Deque used as a stack at one end and a queue at the other**
  - LeetCode 239 Sliding Window Maximum (hard; neetcode150, neetcode250, all)

## Gaps

Patterns with no problem in the data (each needs one from LeetCode, checked there):

- Group 3: Prefix evaluation (scan right to left)
- Group 3: Shunting-yard (infix to postfix with an operator stack)
- Group 3: Symbolic algebra (polynomial arithmetic)
- Group 4: Set of stacks with capacity (plates)
- Group 7: Sort a stack with one extra stack or with recursion
- Group 8: Sliding window median (heaps or sorted multiset; contrast)
- Group 10: Interval DP that removes elements (stack of segments)
- Group 12: Backtracking with an explicit stack of choices
- Group 12: Tail recursion to a loop
- Group 12: Memoised recursion to bottom-up (cross-reference: DP)
- Group 13: Level-order BFS (cross-reference: Trees, Graphs)

67 patterns have exactly one example. For a named problem (car fleet, 132 pattern) that is enough; a second problem is only worth picking where the pattern has real variants (the infix calculator, brace and tag parsing, the contribution-counting family).


Other gaps:

- Iterative DFS, sorting with stacks, stack and DP and recursion to iteration have no lesson today; their problems sit in Trees, Greedy, Linked List and Sliding Window.
- Many monotonic-stack problems are filed under other patterns (Greedy, Two Pointers, Trees, Linked List, Heap). The lesson should link them by tag rather than move them.
- Group 14 is a teaching checklist, not a set of problems: its examples are borrowed from the other groups.
