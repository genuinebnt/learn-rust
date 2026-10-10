# Bit manipulation patterns: the exhaustive target list

The target for the Bit Manipulation pattern lessons, in the same spirit as [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md). The rule is in [DSA.md](DSA.md), decision 32: a topic's patterns section is exhaustive, patterns without a NeetCode problem get **example problems** from LeetCode, and variants of one pattern are **tabs** of one lesson.

Status: documented only. Today `content/dsa/lessons/bit-manipulation.toml` has 6 techniques (xor, bit-count, shift, add-bits, digit-extract, prefix-xor), each with its must-learn problem. The list below has 18 groups and 109 patterns; building the rest needs lessons for the missing patterns and picked, checked example problems (never from memory), after the mockup of the tabs that decision 32 already asks for.

Items written *a / b* in a group are variants for tabs where one lesson covers both (for example "Count set bits: Kernighan / shift and test / lookup table / popcount"). Items separated by semicolons are separate patterns, each its own lesson.

1. **Single-number tricks.** Power of two / power of four; Lowest set bit (x & -x) / clear the lowest set bit (x & (x - 1)); Highest set bit and bit length / round up to a power of two; Count set bits: Kernighan / shift and test / lookup table / popcount; Parity of the set bits (fold with XOR); Reverse bits: loop / byte lookup table / swap halves; Swap two values without a temporary (XOR swap) / swap two bit positions.
2. **XOR tricks.** Single number: pairs cancel / one extra element / the root of a tree as the unpaired id; Single number II: every other value three times (per-bit count mod 3 / two-register state machine); Single number III: two singles, split by the lowest set bit of the total XOR; Missing number / duplicate / set mismatch: XOR the indices with the values; XOR of the range 0..n (period-4 formula) / XOR of a range of consecutive numbers; XOR prefix and range XOR queries; Subarray with a target XOR: prefix XOR with a hash map of counts; XOR contribution by count parity (all pairings, all subarrays); All counts even: toggle one flag per value; Decode with XOR: restore the array from prefix or neighbour XORs.
3. **Masks, shifts and fields.** Set / clear / toggle / test a bit, and the low-k-bits mask; Extract and pack fields with shift and mask: IP and CIDR, UTF-8 headers, hexadecimal digits; Rotate: circular shift within a fixed width; Pack several small values into one integer (in-place state encoding); Isolate or deposit bits under a mask (bit extract / bit deposit); Toggle ASCII letter case with XOR 32 / enumerate case flips by mask.
4. **Bitmask subsets and bitmask DP.** Enumerate all subsets (mask from 0 to 2^n - 1); Subsets with duplicates: sort and skip / dedupe the masks; Enumerate masks with exactly k set bits: popcount filter / Gosper's hack; Submask enumeration (sub = (sub - 1) & mask) / partition into k groups; Bitmask DP over subsets: assignment and ordering (dp[mask] = best for the items used); Bitmask DP with a game state or a cover; Visited-set state in path search (BFS / DFS with a keys or visited mask); Meet in the middle over two half-masks; Brute force over every mask with a validity check; Memoized search over a count vector packed into one integer. Cross-reference: DSA_GRAPH_PATTERNS.md groups 11 and 14 (graph DP, backtracking and enumeration), and the Backtracking and 1-D Dynamic Programming lessons, which own `Backtracking:include-exclude`, `Backtracking:partition-k` and `1-D Dynamic Programming:bitmask` today.
5. **Counting bits across numbers.** Per-bit column counting: for each bit, count the numbers that have it; DP on bits: bits[i] = bits[i >> 1] + (i & 1) / bits[i & (i - 1)] + 1; Bit contribution: each bit is set in 2^(n-1) of the subsets; Counting numbers up to n by bit pattern: digit DP on binary digits.
6. **Arithmetic with bits.** Add without +: XOR for the sum, AND shifted for the carry / add binary strings or digit arrays; Subtract and negate with two's complement (-x = ~x + 1); Multiply by shift-and-add / fast exponentiation (square and multiply on the exponent's bits); Divide by shift-and-subtract (doubling the divisor); Sign handling and overflow: 32-bit masks in Python, INT_MIN edge cases; Digit-wise arithmetic: reverse digits / change of base.
7. **Range AND / OR.** AND of a range: the common binary prefix of the endpoints; OR / XOR of a range of consecutive numbers, bit by bit; AND / OR over all subarrays: at most 32 distinct values per right end; AND over a connected component: union-find with an AND aggregate; Sliding window with per-bit counters (AND and OR cannot be undone); AND never grows, OR never shrinks: longest run of the maximum, largest group with AND above zero; Subsets with the maximum OR: count them / spend k doublings.
8. **Gray code.** Generate the Gray code sequence: i ^ (i >> 1) / reflect and prefix / backtrack one flip at a time; Gray code back to binary (prefix XOR of the bits) / minimum one-bit operations; Circular Gray permutation from a given start (rotate the sequence); Enumerate subsets changing one element per step.
9. **Bit-level greedy and tries.** Maximum XOR pair: decide bits from the top with a prefix set / binary trie; Maximum XOR under a limit: offline queries sorted, trie of inserted values; Best value against a fixed mask: flip toward all ones inside a bit width; Choose bits from the top: set the highest free bit first, keep or clear; Greedy on runs of ones: add or subtract a power of two. Cross-reference: the Tries lesson (`Tries:trie-dfs`), which holds Maximum XOR of Two Numbers today.
10. **Bit manipulation for sets.** Visited and used masks: a set of items as one integer; Letters as 26-bit masks: a word or substring as a set of letters; Parity state as a mask: prefix or path state, one bit per symbol; Set operations (|, &, & ~, subset test (a & b) == a) and masks as dictionary keys; Bitset data structure: flip all, count, find the k-th; Allowed-option sets as masks: one mask per key in a lookup table.
11. **Hamming distance and total Hamming.** Hamming distance: popcount of the XOR; Total Hamming distance over all pairs: ones times zeros per bit; Flips needed to reach a target: per-bit case analysis of a | b == c; Pairs by number of differing bits, or by XOR range.
12. **Bit tricks for strings.** Word product: disjoint letter masks (a & b == 0); Unique characters: test and set one bit per letter; Palindrome permutation: at most one odd count (mask & (mask - 1) == 0); Same letter set: equal masks as signatures; A window of k symbols as an integer: rolling shift, 2 bits per DNA letter; Binary substrings as numbers: value of a substring, XOR queries; Set of letters between two positions: one mask per letter; Groups of words by suffix, each group a mask of first letters.
13. **Sieve and bitset algorithms.** Sieve of Eratosthenes: bit-packed / odd only / segmented; Bitset DP with a big integer: dp |= dp << x; Bit-parallel reachability and transitive closure.
14. **Binary representation problems.** Number complement: XOR with an all-ones mask of the same length; Binary gap / adjacent and alternating bits (x & (x >> 1), x ^ (x >> 1)); Change of base: hexadecimal, base -2, negative bases; Read a binary sequence as a number (value = 2 * value + bit): list, tree path, string; Steps to reduce a number: halve when even, step when odd; Recursive structure of the index bits: k-th symbol, k-th bit of a built string; Concatenate binary numbers: shift by the bit length; Heap-style indexing: the bits of a node index spell its path from the root; Enumerate n-bit strings under an adjacent-bit constraint (mask & (mask >> 1) == 0).
15. **Flip operations on binary arrays.** Flip a window greedily: queue of expiring flips / difference array of flips; Flip rows and columns of a binary matrix; Flips with a global effect: XOR k on both ends of an edge, parity of the changed nodes.
16. **Algebraic properties and invariants.** Sum identities: a + b = (a ^ b) + 2 * (a & b), a | b = (a ^ b) + (a & b); Invariants of the operation: what AND / OR / XOR cannot change; Operations that keep the popcount: only equal-popcount values may swap; Set of reachable XOR values: a full range 0..2^k - 1; Bit 0 decides parity: even and odd numbers, partition by the lowest bit.
17. **Advanced bit techniques.** XOR linear basis: maximum subset XOR, reachable XORs; Sum over subsets (SOS DP): subset and superset zeta transform; Walsh-Hadamard transform: XOR convolution; Nim and Sprague-Grundy: XOR of pile values decides the game; Persistent binary trie: XOR queries over a range of versions; Bit-parallel DP: bit-vector LCS and edit distance, bitap matching; Lowbit-driven structures: Fenwick tree (i & -i), sparse table by bit length; Broken-profile DP: row masks for tilings and grid placements.
18. **Core implementation idioms.** Fixed-width integers in Python: mask with 0xFFFFFFFF, convert back when the sign bit is set; Built-ins: int.bit_count(), int.bit_length(), bin(), int(s, 2), format(x, '032b'); Iterating bits: range(32) and (x >> i) & 1 / while x: x >>= 1; Python traps: == binds tighter than &, ~x is -x - 1, >> floors negatives, no overflow.

## Coverage today

Source: `content/dsa/lessons/bit-manipulation.toml`, `content/dsa/problems.json` (943 problems) and `content/dsa/practice.json` (607 problems).

- **Problems by topic.** 31 problems of `problems.json` sit in the Bit Manipulation pattern (6 must learn, 25 practice). 60 problems of `problems.json` and 52 of `practice.json` carry LeetCode's Bit Manipulation tag; 33 of the tagged ones of `problems.json` are filed under other patterns (Backtracking, Arrays & Hashing, Greedy, 1-D Dynamic Programming and so on) because their main technique is not a bit trick. In all, 116 distinct problems are tagged Bit Manipulation or Bitmask or filed under the pattern.
- **Lessons.** The six techniques and what they cover:

| Technique | Must-learn problem | Problems in the data with this technique | Groups it touches |
|---|---|---|---|
| `Bit Manipulation:xor` | LeetCode 136 Single Number | 11 | 1 (single number), 2 (single number, missing number), 11 |
| `Bit Manipulation:bit-count` | LeetCode 191 Number of 1 Bits | 11 | 1 (Kernighan, power of two), 5 (DP on bits) |
| `Bit Manipulation:shift` | LeetCode 190 Reverse Bits | 12 | 1 (reverse bits), 3 (partly), 14 (partly) |
| `Bit Manipulation:add-bits` | LeetCode 371 Sum of Two Integers | 6 | 6 (add without +), 18 (32-bit masks) |
| `Bit Manipulation:digit-extract` | LeetCode 7 Reverse Integer | 5 | 6 (digit-wise arithmetic, overflow) |
| `Bit Manipulation:prefix-xor` | LeetCode 1310 XOR Queries of a Subarray | 8 | 2 (prefix XOR, subarray with a target XOR) |

- **Coverage by group.** Covered means a lesson with signals, template and pitfalls exists today; partly means the lesson touches some of the group's patterns; none means no lesson of this topic mentions it.

| # | Group | Status | Notes |
|---|---|---|---|
| 1 | Single-number tricks | partly | `bit-count` teaches Kernighan's loop and the power-of-two test; `shift` teaches reverse bits. Not covered: lowest set bit `x & -x`, highest set bit, parity, swap. |
| 2 | XOR tricks | partly | `xor` and `prefix-xor` cover single number, missing number, range XOR queries and the prefix-map count. Not covered: single number II and III, the 0..n formula, decoding, count parity. |
| 3 | Masks, shifts and fields | partly | `shift` builds a number bit by bit. Not covered: set / clear / toggle / test as a toolkit, field extraction, rotate. |
| 4 | Bitmask subsets and bitmask DP | none here | Lives in the Backtracking lessons (`include-exclude`, `partition-k`) and the 1-D Dynamic Programming `bitmask` lesson. Missing: submask enumeration, k-bit masks, meet in the middle as bit patterns. |
| 5 | Counting bits across numbers | partly | `bit-count` covers the DP on bits (Counting Bits). Not covered: per-bit column counting, bit contribution, digit DP. |
| 6 | Arithmetic with bits | partly | `add-bits` and `digit-extract` cover add without + and reverse digits. Not covered: multiply, divide, fast exponentiation, two's complement as a topic. |
| 7 | Range AND / OR | none | No lesson. Bitwise AND of Numbers Range sits under `shift`; the sliding-window problems sit in the Sliding Window lessons. |
| 8 | Gray code | none | No lesson. Gray Code is a Backtracking practice problem. |
| 9 | Bit-level greedy and tries | none here | Maximum XOR of Two Numbers is in the Tries lessons; the bit-by-bit greedy idea has no lesson of its own. |
| 10 | Bit manipulation for sets | none here | Masks as sets are used inside Arrays & Hashing, Backtracking and Graph lessons without a bit lesson. |
| 11 | Hamming distance and total Hamming | none | No lesson. Hamming Distance and Total Hamming Distance are practice problems under `xor` and `digit-extract`. |
| 12 | Bit tricks for strings | none here | Used in Arrays & Hashing (seen-set, counting) problems without a bit lesson. |
| 13 | Sieve and bitset algorithms | none | No lesson. Count Primes is in Math & Geometry. |
| 14 | Binary representation problems | none | No lesson. The problems are spread over `shift`, `add-bits`, `digit-extract` and `prefix-xor` by accident of their first idea. |
| 15 | Flip operations on binary arrays | none here | Flip windows are in the Greedy lessons (`flip-window`). |
| 16 | Algebraic properties and invariants | none | No lesson. |
| 17 | Advanced bit techniques | none | No lesson. |
| 18 | Core implementation idioms | partly | `add-bits` shows the 32-bit mask and the sign conversion; nothing yet on built-ins or precedence traps. |

## Example problems per pattern

Taken only from `content/dsa/problems.json` and `content/dsa/practice.json`, at most four per pattern, written `LeetCode <number> <title> (<difficulty>; <lists>)`. Where the data has no problem the pattern says so: the example has to be picked from LeetCode and checked there, never from memory. A problem can serve more than one pattern.

### 1. Single-number tricks

- **Power of two / power of four**
    - LeetCode 231 Power of Two (easy; all)
    - LeetCode 342 Power of Four (easy; all)
- **Lowest set bit (x & -x) / clear the lowest set bit (x & (x - 1))**
    - LeetCode 260 Single Number III (medium; all)
    - LeetCode 201 Bitwise AND of Numbers Range (medium; neetcode250, all)
    - LeetCode 191 Number of 1 Bits (easy; blind75, neetcode150, neetcode250, all)
- **Highest set bit and bit length / round up to a power of two**
    - LeetCode 1680 Concatenation of Consecutive Binary Numbers (medium; practice)
    - LeetCode 338 Counting Bits (easy; blind75, neetcode150, neetcode250, all)
- **Count set bits: Kernighan / shift and test / lookup table / popcount**
    - LeetCode 191 Number of 1 Bits (easy; blind75, neetcode150, neetcode250, all)
    - LeetCode 1356 Sort Integers by The Number of 1 Bits (easy; practice)
    - LeetCode 3011 Find if Array Can Be Sorted (medium; all)
- **Parity of the set bits (fold with XOR)**
    - LeetCode 3199 Count Triplets with Even XOR Set Bits I (easy; all)
- **Reverse bits: loop / byte lookup table / swap halves**
    - LeetCode 190 Reverse Bits (easy; blind75, neetcode150, neetcode250, all)
- **Swap two values without a temporary (XOR swap) / swap two bit positions**
    - no problem in the data: needs one from LeetCode

### 2. XOR tricks

- **Single number: pairs cancel / one extra element / the root of a tree as the unpaired id**
    - LeetCode 136 Single Number (easy; neetcode150, neetcode250, all)
    - LeetCode 389 Find the Difference (easy; all)
    - LeetCode 1506 Find Root of N-Ary Tree (medium; all)
    - LeetCode 3158 Find the XOR of Numbers Which Appear Twice (easy; practice)
- **Single number II: every other value three times (per-bit count mod 3 / two-register state machine)**
    - LeetCode 137 Single Number II (medium; practice)
- **Single number III: two singles, split by the lowest set bit of the total XOR**
    - LeetCode 260 Single Number III (medium; all)
- **Missing number / duplicate / set mismatch: XOR the indices with the values**
    - LeetCode 268 Missing Number (easy; blind75, neetcode150, neetcode250, all)
    - LeetCode 645 Set Mismatch (easy; all)
    - LeetCode 287 Find the Duplicate Number (medium; neetcode150, neetcode250, all)
- **XOR of the range 0..n (period-4 formula) / XOR of a range of consecutive numbers**
    - no problem in the data: needs one from LeetCode
- **XOR prefix and range XOR queries**
    - LeetCode 1310 XOR Queries of a Subarray (medium; all)
    - LeetCode 1829 Maximum XOR for Each Query (medium; all)
- **Subarray with a target XOR: prefix XOR with a hash map of counts**
    - LeetCode 1442 Count Triplets That Can Form Two Arrays of Equal XOR (medium; all)
    - LeetCode 2588 Count the Number of Beautiful Subarrays (medium; practice)
    - LeetCode 1371 Find the Longest Substring Containing Vowels in Even Counts (medium; all)
- **XOR contribution by count parity (all pairings, all subarrays)**
    - LeetCode 2425 Bitwise XOR of All Pairings (medium; all)
- **All counts even: toggle one flag per value**
    - LeetCode 2206 Divide Array Into Equal Pairs (easy; all)
    - LeetCode 266 Palindrome Permutation (easy; all)
- **Decode with XOR: restore the array from prefix or neighbour XORs**
    - LeetCode 2683 Neighboring Bitwise XOR (medium; all)
    - LeetCode 2433 Find The Original Array of Prefix Xor (medium; practice)

### 3. Masks, shifts and fields

- **Set / clear / toggle / test a bit, and the low-k-bits mask**
    - LeetCode 1318 Minimum Flips to Make a OR b Equal to c (medium; practice)
    - LeetCode 2429 Minimize XOR (medium; all)
- **Extract and pack fields with shift and mask: IP and CIDR, UTF-8 headers, hexadecimal digits**
    - LeetCode 751 IP to CIDR (medium; all)
    - LeetCode 393 UTF-8 Validation (medium; practice)
    - LeetCode 405 Convert a Number to Hexadecimal (easy; practice)
- **Rotate: circular shift within a fixed width**
    - no problem in the data: needs one from LeetCode
- **Pack several small values into one integer (in-place state encoding)**
    - LeetCode 1470 Shuffle the Array (easy; all)
    - LeetCode 289 Game of Life (medium; practice)
- **Isolate or deposit bits under a mask (bit extract / bit deposit)**
    - LeetCode 3133 Minimum Array End (medium; neetcode250, all)
- **Toggle ASCII letter case with XOR 32 / enumerate case flips by mask**
    - LeetCode 784 Letter Case Permutation (medium; practice)

### 4. Bitmask subsets and bitmask DP

- **Enumerate all subsets (mask from 0 to 2^n - 1)**
    - LeetCode 78 Subsets (medium; neetcode150, neetcode250, all)
    - LeetCode 1863 Sum of All Subset XOR Totals (easy; neetcode250, all)
    - LeetCode 2044 Count Number of Maximum Bitwise-OR Subsets (medium; all)
- **Subsets with duplicates: sort and skip / dedupe the masks**
    - LeetCode 90 Subsets II (medium; neetcode150, neetcode250, all)
    - LeetCode 491 Non-decreasing Subsequences (medium; practice)
- **Enumerate masks with exactly k set bits: popcount filter / Gosper's hack**
    - LeetCode 401 Binary Watch (easy; practice)
    - LeetCode 2397 Maximum Rows Covered by Columns (medium; practice)
- **Submask enumeration (sub = (sub - 1) & mask) / partition into k groups**
    - LeetCode 698 Partition to K Equal Sum Subsets (medium; neetcode250, all)
    - LeetCode 473 Matchsticks to Square (medium; neetcode250, all)
    - LeetCode 1723 Find Minimum Time to Finish All Jobs (hard; practice)
    - LeetCode 2305 Fair Distribution of Cookies (medium; practice)
- **Bitmask DP over subsets: assignment and ordering (dp[mask] = best for the items used)**
    - LeetCode 526 Beautiful Arrangement (medium; practice)
    - LeetCode 1799 Maximize Score After N Operations (hard; all)
    - LeetCode 996 Number of Squareful Arrays (hard; practice)
    - LeetCode 2850 Minimum Moves to Spread Stones Over Grid (medium; practice)
- **Bitmask DP with a game state or a cover**
    - LeetCode 464 Can I Win (medium; practice)
    - LeetCode 691 Stickers to Spell Word (hard; all)
    - LeetCode 465 Optimal Account Balancing (hard; all)
    - LeetCode 2397 Maximum Rows Covered by Columns (medium; practice)
- **Visited-set state in path search (BFS / DFS with a keys or visited mask)**
    - LeetCode 864 Shortest Path to Get All Keys (hard; practice)
    - LeetCode 980 Unique Paths III (hard; practice)
    - LeetCode 351 Android Unlock Patterns (medium; all)
- **Meet in the middle over two half-masks**
    - LeetCode 805 Split Array With Same Average (hard; all)
    - LeetCode 2035 Partition Array Into Two Arrays to Minimize Sum Difference (hard; practice)
- **Brute force over every mask with a validity check**
    - LeetCode 1239 Maximum Length of a Concatenated String with Unique Characters (medium; all)
    - LeetCode 1255 Maximum Score Words Formed by Letters (hard; all)
    - LeetCode 2151 Maximum Good People Based on Statements (hard; practice)
- **Memoized search over a count vector packed into one integer**
    - LeetCode 638 Shopping Offers (medium; practice)

### 5. Counting bits across numbers

- **Per-bit column counting: for each bit, count the numbers that have it**
    - LeetCode 2917 Find the K-or of an Array (easy; practice)
    - LeetCode 2275 Largest Combination With Bitwise AND Greater Than Zero (medium; all)
    - LeetCode 477 Total Hamming Distance (medium; practice)
    - LeetCode 137 Single Number II (medium; practice)
- **DP on bits: bits[i] = bits[i >> 1] + (i & 1) / bits[i & (i - 1)] + 1**
    - LeetCode 338 Counting Bits (easy; blind75, neetcode150, neetcode250, all)
- **Bit contribution: each bit is set in 2^(n-1) of the subsets**
    - LeetCode 1863 Sum of All Subset XOR Totals (easy; neetcode250, all)
    - LeetCode 2044 Count Number of Maximum Bitwise-OR Subsets (medium; all)
- **Counting numbers up to n by bit pattern: digit DP on binary digits**
    - LeetCode 600 Non-negative Integers without Consecutive Ones (hard; practice)
    - LeetCode 3154 Find Number of Ways to Reach the K-th Stair (hard; practice)

### 6. Arithmetic with bits

- **Add without +: XOR for the sum, AND shifted for the carry / add binary strings or digit arrays**
    - LeetCode 371 Sum of Two Integers (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 67 Add Binary (easy; neetcode250, all)
    - LeetCode 989 Add to Array-Form of Integer (easy; all)
- **Subtract and negate with two's complement (-x = ~x + 1)**
    - LeetCode 371 Sum of Two Integers (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 405 Convert a Number to Hexadecimal (easy; practice)
- **Multiply by shift-and-add / fast exponentiation (square and multiply on the exponent's bits)**
    - LeetCode 50 Pow(x, n) (medium; neetcode150, neetcode250, all)
- **Divide by shift-and-subtract (doubling the divisor)**
    - LeetCode 29 Divide Two Integers (medium; practice)
- **Sign handling and overflow: 32-bit masks in Python, INT_MIN edge cases**
    - LeetCode 29 Divide Two Integers (medium; practice)
    - LeetCode 7 Reverse Integer (medium; neetcode150, neetcode250, all)
    - LeetCode 371 Sum of Two Integers (medium; blind75, neetcode150, neetcode250, all)
- **Digit-wise arithmetic: reverse digits / change of base**
    - LeetCode 7 Reverse Integer (medium; neetcode150, neetcode250, all)
    - LeetCode 405 Convert a Number to Hexadecimal (easy; practice)

### 7. Range AND / OR

- **AND of a range: the common binary prefix of the endpoints**
    - LeetCode 201 Bitwise AND of Numbers Range (medium; neetcode250, all)
- **OR / XOR of a range of consecutive numbers, bit by bit**
    - no problem in the data: needs one from LeetCode
- **AND / OR over all subarrays: at most 32 distinct values per right end**
    - LeetCode 898 Bitwise ORs of Subarrays (medium; practice)
- **AND over a connected component: union-find with an AND aggregate**
    - LeetCode 3108 Minimum Cost Walk in Weighted Graph (hard; all)
- **Sliding window with per-bit counters (AND and OR cannot be undone)**
    - LeetCode 3097 Shortest Subarray With OR at Least K II (medium; all)
    - LeetCode 2401 Longest Nice Subarray (medium; all)
- **AND never grows, OR never shrinks: longest run of the maximum, largest group with AND above zero**
    - LeetCode 2419 Longest Subarray With Maximum Bitwise AND (medium; all)
    - LeetCode 2275 Largest Combination With Bitwise AND Greater Than Zero (medium; all)
- **Subsets with the maximum OR: count them / spend k doublings**
    - LeetCode 2044 Count Number of Maximum Bitwise-OR Subsets (medium; all)
    - LeetCode 2680 Maximum OR (medium; practice)

### 8. Gray code

- **Generate the Gray code sequence: i ^ (i >> 1) / reflect and prefix / backtrack one flip at a time**
    - LeetCode 89 Gray Code (medium; practice)
- **Gray code back to binary (prefix XOR of the bits) / minimum one-bit operations**
    - LeetCode 1611 Minimum One Bit Operations to Make Integers Zero (hard; all)
- **Circular Gray permutation from a given start (rotate the sequence)**
    - no problem in the data: needs one from LeetCode
- **Enumerate subsets changing one element per step**
    - no problem in the data: needs one from LeetCode

### 9. Bit-level greedy and tries

- **Maximum XOR pair: decide bits from the top with a prefix set / binary trie**
    - LeetCode 421 Maximum XOR of Two Numbers in an Array (medium; practice)
- **Maximum XOR under a limit: offline queries sorted, trie of inserted values**
    - LeetCode 1707 Maximum XOR With an Element From Array (hard; practice)
- **Best value against a fixed mask: flip toward all ones inside a bit width**
    - LeetCode 1829 Maximum XOR for Each Query (medium; all)
- **Choose bits from the top: set the highest free bit first, keep or clear**
    - LeetCode 2429 Minimize XOR (medium; all)
    - LeetCode 2939 Maximum Xor Product (medium; practice)
    - LeetCode 2680 Maximum OR (medium; practice)
    - LeetCode 3133 Minimum Array End (medium; neetcode250, all)
- **Greedy on runs of ones: add or subtract a power of two**
    - LeetCode 2571 Minimum Operations to Reduce an Integer to 0 (medium; practice)
    - LeetCode 397 Integer Replacement (medium; practice)
    - LeetCode 1404 Number of Steps to Reduce a Number in Binary Representation to One (medium; practice)

### 10. Bit manipulation for sets

- **Visited and used masks: a set of items as one integer**
    - LeetCode 526 Beautiful Arrangement (medium; practice)
    - LeetCode 864 Shortest Path to Get All Keys (hard; practice)
    - LeetCode 980 Unique Paths III (hard; practice)
    - LeetCode 351 Android Unlock Patterns (medium; all)
- **Letters as 26-bit masks: a word or substring as a set of letters**
    - LeetCode 1239 Maximum Length of a Concatenated String with Unique Characters (medium; all)
    - LeetCode 1684 Count the Number of Consistent Strings (easy; all)
    - LeetCode 2506 Count Pairs Of Similar Strings (easy; practice)
- **Parity state as a mask: prefix or path state, one bit per symbol**
    - LeetCode 1371 Find the Longest Substring Containing Vowels in Even Counts (medium; all)
    - LeetCode 1457 Pseudo-Palindromic Paths in a Binary Tree (medium; all)
    - LeetCode 2791 Count Paths That Can Form a Palindrome in a Tree (hard; practice)
- **Set operations (|, &, & ~, subset test (a & b) == a) and masks as dictionary keys**
    - LeetCode 2002 Maximum Product of the Length of Two Palindromic Subsequences (medium; all)
    - LeetCode 464 Can I Win (medium; practice)
    - LeetCode 691 Stickers to Spell Word (hard; all)
- **Bitset data structure: flip all, count, find the k-th**
    - LeetCode 2166 Design Bitset (medium; practice)
- **Allowed-option sets as masks: one mask per key in a lookup table**
    - LeetCode 756 Pyramid Transition Matrix (medium; practice)

### 11. Hamming distance and total Hamming

- **Hamming distance: popcount of the XOR**
    - LeetCode 461 Hamming Distance (easy; practice)
    - LeetCode 2220 Minimum Bit Flips to Convert Number (easy; all)
    - LeetCode 3199 Count Triplets with Even XOR Set Bits I (easy; all)
- **Total Hamming distance over all pairs: ones times zeros per bit**
    - LeetCode 477 Total Hamming Distance (medium; practice)
- **Flips needed to reach a target: per-bit case analysis of a | b == c**
    - LeetCode 1318 Minimum Flips to Make a OR b Equal to c (medium; practice)
    - LeetCode 2220 Minimum Bit Flips to Convert Number (easy; all)
- **Pairs by number of differing bits, or by XOR range**
    - no problem in the data: needs one from LeetCode

### 12. Bit tricks for strings

- **Word product: disjoint letter masks (a & b == 0)**
    - LeetCode 2002 Maximum Product of the Length of Two Palindromic Subsequences (medium; all)
    - LeetCode 1239 Maximum Length of a Concatenated String with Unique Characters (medium; all)
- **Unique characters: test and set one bit per letter**
    - LeetCode 1239 Maximum Length of a Concatenated String with Unique Characters (medium; all)
    - LeetCode 1684 Count the Number of Consistent Strings (easy; all)
- **Palindrome permutation: at most one odd count (mask & (mask - 1) == 0)**
    - LeetCode 266 Palindrome Permutation (easy; all)
    - LeetCode 1457 Pseudo-Palindromic Paths in a Binary Tree (medium; all)
- **Same letter set: equal masks as signatures**
    - LeetCode 2506 Count Pairs Of Similar Strings (easy; practice)
    - LeetCode 1684 Count the Number of Consistent Strings (easy; all)
- **A window of k symbols as an integer: rolling shift, 2 bits per DNA letter**
    - LeetCode 187 Repeated DNA Sequences (medium; all)
    - LeetCode 1461 Check If a String Contains All Binary Codes of Size K (medium; all)
- **Binary substrings as numbers: value of a substring, XOR queries**
    - LeetCode 2564 Substring XOR Queries (medium; practice)
- **Set of letters between two positions: one mask per letter**
    - LeetCode 1930 Unique Length-3 Palindromic Subsequences (medium; all)
- **Groups of words by suffix, each group a mask of first letters**
    - LeetCode 2306 Naming a Company (hard; all)

### 13. Sieve and bitset algorithms

- **Sieve of Eratosthenes: bit-packed / odd only / segmented**
    - LeetCode 204 Count Primes (medium; all)
    - LeetCode 2523 Closest Prime Numbers in Range (medium; all)
    - LeetCode 2601 Prime Subtraction Operation (medium; all)
- **Bitset DP with a big integer: dp |= dp << x**
    - LeetCode 416 Partition Equal Subset Sum (medium; neetcode150, neetcode250, all)
    - LeetCode 805 Split Array With Same Average (hard; all)
- **Bit-parallel reachability and transitive closure**
    - no problem in the data: needs one from LeetCode

### 14. Binary representation problems

- **Number complement: XOR with an all-ones mask of the same length**
    - LeetCode 1009 Complement of Base 10 Integer (easy; practice)
- **Binary gap / adjacent and alternating bits (x & (x >> 1), x ^ (x >> 1))**
    - LeetCode 868 Binary Gap (easy; practice)
    - LeetCode 693 Binary Number with Alternating Bits (easy; practice)
- **Change of base: hexadecimal, base -2, negative bases**
    - LeetCode 405 Convert a Number to Hexadecimal (easy; practice)
- **Read a binary sequence as a number (value = 2 * value + bit): list, tree path, string**
    - LeetCode 1290 Convert Binary Number in a Linked List to Integer (easy; practice)
    - LeetCode 1022 Sum of Root To Leaf Binary Numbers (easy; practice)
    - LeetCode 1404 Number of Steps to Reduce a Number in Binary Representation to One (medium; practice)
- **Steps to reduce a number: halve when even, step when odd**
    - LeetCode 1342 Number of Steps to Reduce a Number to Zero (easy; practice)
    - LeetCode 1404 Number of Steps to Reduce a Number in Binary Representation to One (medium; practice)
    - LeetCode 397 Integer Replacement (medium; practice)
- **Recursive structure of the index bits: k-th symbol, k-th bit of a built string**
    - LeetCode 779 K-th Symbol in Grammar (medium; all)
    - LeetCode 1545 Find Kth Bit in Nth Binary String (medium; all)
    - LeetCode 3304 Find the K-th Character in String Game I (easy; practice)
- **Concatenate binary numbers: shift by the bit length**
    - LeetCode 1680 Concatenation of Consecutive Binary Numbers (medium; practice)
- **Heap-style indexing: the bits of a node index spell its path from the root**
    - LeetCode 222 Count Complete Tree Nodes (medium; practice)
- **Enumerate n-bit strings under an adjacent-bit constraint (mask & (mask >> 1) == 0)**
    - LeetCode 3211 Generate Binary Strings Without Adjacent Zeros (medium; practice)
    - LeetCode 600 Non-negative Integers without Consecutive Ones (hard; practice)

### 15. Flip operations on binary arrays

- **Flip a window greedily: queue of expiring flips / difference array of flips**
    - LeetCode 995 Minimum Number of K Consecutive Bit Flips (hard; all)
    - LeetCode 3191 Minimum Operations to Make Binary Array Elements Equal to One I (medium; all)
- **Flip rows and columns of a binary matrix**
    - LeetCode 861 Score After Flipping Matrix (medium; all)
- **Flips with a global effect: XOR k on both ends of an edge, parity of the changed nodes**
    - LeetCode 3068 Find the Maximum Sum of Node Values (hard; all)

### 16. Algebraic properties and invariants

- **Sum identities: a + b = (a ^ b) + 2 * (a & b), a | b = (a ^ b) + (a & b)**
    - LeetCode 371 Sum of Two Integers (medium; blind75, neetcode150, neetcode250, all)
- **Invariants of the operation: what AND / OR / XOR cannot change**
    - LeetCode 2546 Apply Bitwise Operations to Make Strings Equal (medium; practice)
    - LeetCode 2683 Neighboring Bitwise XOR (medium; all)
    - LeetCode 3068 Find the Maximum Sum of Node Values (hard; all)
- **Operations that keep the popcount: only equal-popcount values may swap**
    - LeetCode 3011 Find if Array Can Be Sorted (medium; all)
- **Set of reachable XOR values: a full range 0..2^k - 1**
    - LeetCode 3513 Number of Unique XOR Triplets I (medium; practice)
- **Bit 0 decides parity: even and odd numbers, partition by the lowest bit**
    - LeetCode 3688 Bitwise OR of Even Numbers in an Array (easy; practice)
    - LeetCode 905 Sort Array By Parity (easy; all)

### 17. Advanced bit techniques

- **XOR linear basis: maximum subset XOR, reachable XORs**
    - no problem in the data: needs one from LeetCode
- **Sum over subsets (SOS DP): subset and superset zeta transform**
    - no problem in the data: needs one from LeetCode
- **Walsh-Hadamard transform: XOR convolution**
    - no problem in the data: needs one from LeetCode
- **Nim and Sprague-Grundy: XOR of pile values decides the game**
    - no problem in the data: needs one from LeetCode
- **Persistent binary trie: XOR queries over a range of versions**
    - no problem in the data: needs one from LeetCode
- **Bit-parallel DP: bit-vector LCS and edit distance, bitap matching**
    - no problem in the data: needs one from LeetCode
- **Lowbit-driven structures: Fenwick tree (i & -i), sparse table by bit length**
    - no problem in the data: needs one from LeetCode
- **Broken-profile DP: row masks for tilings and grid placements**
    - no problem in the data: needs one from LeetCode

### 18. Core implementation idioms

- **Fixed-width integers in Python: mask with 0xFFFFFFFF, convert back when the sign bit is set**
    - LeetCode 371 Sum of Two Integers (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 190 Reverse Bits (easy; blind75, neetcode150, neetcode250, all)
    - LeetCode 29 Divide Two Integers (medium; practice)
- **Built-ins: int.bit_count(), int.bit_length(), bin(), int(s, 2), format(x, '032b')**
    - LeetCode 191 Number of 1 Bits (easy; blind75, neetcode150, neetcode250, all)
    - LeetCode 1356 Sort Integers by The Number of 1 Bits (easy; practice)
    - LeetCode 1680 Concatenation of Consecutive Binary Numbers (medium; practice)
- **Iterating bits: range(32) and (x >> i) & 1 / while x: x >>= 1**
    - LeetCode 190 Reverse Bits (easy; blind75, neetcode150, neetcode250, all)
    - LeetCode 2917 Find the K-or of an Array (easy; practice)
- **Python traps: == binds tighter than &, ~x is -x - 1, >> floors negatives, no overflow**
    - no problem in the data: needs one from LeetCode

## Gaps

- **Patterns without a problem in the data: 17 of 109.** Each needs an example picked from LeetCode and checked before its lesson is written:
    - 1. Swap two values without a temporary (XOR swap) / swap two bit positions
    - 2. XOR of the range 0..n (period-4 formula) / XOR of a range of consecutive numbers
    - 3. Rotate: circular shift within a fixed width
    - 7. OR / XOR of a range of consecutive numbers, bit by bit
    - 8. Circular Gray permutation from a given start (rotate the sequence)
    - 8. Enumerate subsets changing one element per step
    - 11. Pairs by number of differing bits, or by XOR range
    - 13. Bit-parallel reachability and transitive closure
    - 17. XOR linear basis: maximum subset XOR, reachable XORs
    - 17. Sum over subsets (SOS DP): subset and superset zeta transform
    - 17. Walsh-Hadamard transform: XOR convolution
    - 17. Nim and Sprague-Grundy: XOR of pile values decides the game
    - 17. Persistent binary trie: XOR queries over a range of versions
    - 17. Bit-parallel DP: bit-vector LCS and edit distance, bitap matching
    - 17. Lowbit-driven structures: Fenwick tree (i & -i), sparse table by bit length
    - 17. Broken-profile DP: row masks for tilings and grid placements
    - 18. Python traps: == binds tighter than &, ~x is -x - 1, >> floors negatives, no overflow
- **Patterns with a problem but no lesson.** Everything outside the six existing techniques: the lessons today cover groups 1, 2, 5 and 6 only in part, group 3 and 18 in a few lines, and nothing of groups 7 to 17 (the exceptions are the bitmask pieces that live in the Backtracking, 1-D Dynamic Programming, Tries and Greedy lessons).
- **Pattern or technique labels that hide bit problems.** 33 problems tagged Bit Manipulation in `problems.json` are filed under other patterns, and in the Bit Manipulation pattern itself 989 Add to Array-Form of Integer has the technique `Math & Geometry:digits`, 2401 and 3097 are `Sliding Window` techniques and 2419 is a `Greedy` technique. The lessons for groups 4, 7, 9, 10 and 15 have to link to those other lessons rather than copy them.
- **Must-learn problems.** Every new lesson that is not an existing technique needs a first problem. Candidates already in the data, one per new lesson: Power of Two (group 1), Single Number III (2), Subsets (4), Bitwise AND of Numbers Range (7), Gray Code (8), Maximum XOR of Two Numbers in an Array (9), Hamming Distance (11), Palindrome Permutation (12), Count Primes (13), Complement of Base 10 Integer (14). The owner decides which are must learn (decision 7 defines it as the first problem that teaches a pattern).
- **Practice track alignment.** `practice.json` has 52 problems with the Bit Manipulation tag and all its entries use the list `practice`; the lessons should draw their practice problems from there first.
- **Recommended build order** (a proposal, not a decision): groups 1 to 3 and 5 to 6 first (they extend the existing six lessons with tabs and need no new data), then 11, 14 and 12 (small lessons with problems already in the data), then 7, 8 and 9, and last 10, 13, 15 and 16. Group 17 is optional depth for contests; group 18 becomes the shared pitfalls block of the whole topic.
