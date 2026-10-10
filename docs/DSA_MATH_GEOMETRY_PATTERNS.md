# Math & Geometry patterns: the exhaustive target list

The owner's list (2026-10-10) of every pattern that can come up on LeetCode or in an interview under the topic Math & Geometry, as the target for the Math & Geometry pattern lessons. It is written by problem shape: what the statement looks like, not which theorem solves it. The rule is in [DSA.md](DSA.md), decision 32: a topic's patterns section is exhaustive, patterns without a NeetCode problem get **example problems** from LeetCode, and variants of one pattern are **tabs** of one lesson. The algorithm side of the same topic (sieves, modular arithmetic, arithmetic functions, big numbers, matrix methods) is the list in [DSA_ALGORITHMS_NUMBER_THEORY.md](DSA_ALGORITHMS_NUMBER_THEORY.md); this file cross-references it instead of copying it. The geometry algorithms behind group 8 (convex hull, polygon area and containment, rotating calipers, closest pair, sweep line, circles) are catalogued in [DSA_ALGORITHMS_GEOMETRY.md](DSA_ALGORITHMS_GEOMETRY.md); group 8 below lists the problem shapes. The format follows [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md).

Status: documented only. Today `content/dsa/lessons/math-geometry.toml` has 13 techniques (number-format, number-theory, formula, matrix-sim, matrix-inplace, spiral, markers, number-cycle, digits, fast-pow, point-counts, median, lex-order), each with its must-learn problem. The list below has 15 groups and 202 patterns; building the rest needs a mockup of the tabs first (decision 32), then lessons and picked example problems checked against LeetCode, never from memory.

Items written *a / b* in a pattern are variants for tabs where one lesson covers both (for example "Fast power: recursive halving / iterative squaring"). Items separated by semicolons are separate patterns, each its own lesson or tab set. A name with a prefix before a colon ("Points on a line: ...", "Rectangles: ...") belongs to one family inside the group. Bit tricks (group 13) are only cross-referenced: they are owned by the Bit Manipulation topic.

1. **Digit manipulation.** Extract digits with % 10 and // 10 (right to left) / convert to a string and index; Digit sum and digital root (loop / the formula 1 + (n - 1) % 9); Reverse an integer, checking for overflow before each digit; Palindrome number (reverse half / compare as a string); Digit powers and per-digit functions (Armstrong numbers, digit squares); Happy number: the digit-square map falls into a cycle (hash set / Floyd / the known cycle at 4); Carry propagation on a digit array (plus one, add to array-form); Schoolbook addition of two digit strings / arrays / binary strings; Schoolbook multiplication of digit strings (result array of size m + n, digit pair i + j); Digit-by-digit construction of a target number (next greater permutation of digits / closest palindrome / round up to the next beautiful number); Rearrange or delete digits for the largest or smallest value (maximum swap / remove k digits / largest odd number); Enumerate numbers by digit shape (sequential digits / symmetric halves / palindromes of a fixed length); Count numbers with distinct digits or a digit property (position counting / digit DP); Place value and the nth digit of a concatenated sequence; Digit groups of three (numbers to words, thousands separators). Number theory: [DSA_ALGORITHMS_NUMBER_THEORY.md](DSA_ALGORITHMS_NUMBER_THEORY.md) groups 6 (digit counting), 7 (big numbers, string arithmetic) and 8 (representations).
2. **Counting and number properties.** Parity: even / odd counts, parity of a sum or product; Perfect square and perfect cube tests (integer square root, then square it back); Power of two / three / four (loop / largest power divides / logarithm with an epsilon / bit test); Ugly numbers: divide out 2, 3, 5 / generate with three pointers or a heap; Count divisors by looping to the square root (pairs d and n / d); Primality test and prime counting (trial division / sieve of Eratosthenes); Trailing zeros of a factorial (count the factor 5, Legendre's formula); Count multiples with floor division (in a range / of a or b by inclusion-exclusion); Nth number divisible by a or b (binary search on a counting function with lcm); Digit-divisibility properties (self-dividing numbers, digits that divide the number); Figurate and triangular numbers (staircase rows, closed-form cell counts); Counting by runs (a run of length k contributes k(k + 1) / 2 substrings); Count pairs and tuples by a hash map of a derived key (product / ratio / difference of positions and values); Pigeonhole principle and remainders (a repeat is forced); Which values can exist after repeated operations (a closed-form set, not a simulation); Perfect, abundant and amicable numbers (sum of proper divisors). Number theory: [DSA_ALGORITHMS_NUMBER_THEORY.md](DSA_ALGORITHMS_NUMBER_THEORY.md) groups 1 to 4 and 6 hold the full list; only the shapes that show up as everyday math problems are named here.
3. **Exponentiation and roots.** Fast power: recursive halving / iterative squaring on the bits of the exponent; Negative exponents, x = 0, 1 or -1, and the exponent INT_MIN; Power with a modulus (reduce after every multiplication); Huge exponent given as a digit array (pow of the base to each digit, or Euler's theorem); Closed forms with 2^n (all assignments, minus the ones that do not count); Integer square root: binary search / Newton's method / bit by bit; Sum of two squares (two pointers up to the square root / Fermat's two-square theorem); Nth root and cube root by binary search or Newton's method; Logarithms to test or compare powers (log vs repeated division, and why floats lie); Fibonacci and linear recurrences by fast doubling or matrix power; Geometric series in closed form (finite / mod p); Exponent tower and exponent reduction by Euler's theorem. Number theory: [DSA_ALGORITHMS_NUMBER_THEORY.md](DSA_ALGORITHMS_NUMBER_THEORY.md) groups 3 (modular exponentiation) and 9 (matrix methods). Real-number square roots are in [DSA_ALGORITHMS_SORTING_SEARCHING.md](DSA_ALGORITHMS_SORTING_SEARCHING.md) group 18.
4. **GCD, LCM and divisibility.** Euclid's algorithm (iterative / recursive) and the gcd of an array; gcd of strings (concatenation check / gcd of the lengths); gcd of adjacent elements (insert gcd between list nodes / array fold); lcm from gcd, dividing before multiplying; Reduced fractions as keys (ratios, slopes, directions); Count common divisors through the gcd; Connectivity by shared prime factors (union-find over primes); Divisibility by digits and remainders; Smallest prime factor and factorisation by repeated division; Bezout's identity and extended Euclid (jugs, reachable amounts, linear Diophantine equations); Periodic events and lcm (when do cycles line up); Divisibility invariants (what stays a multiple of g under the allowed operations). Number theory: [DSA_ALGORITHMS_NUMBER_THEORY.md](DSA_ALGORITHMS_NUMBER_THEORY.md) groups 1 (divisibility and gcd) and 2 (primes and factorisation).
5. **Base conversion and representation.** Convert to and from base k (repeated divmod, then reverse the digits); Bijective numeration with no zero digit (Excel columns, spreadsheet cells); Roman numerals both ways (greedy table / subtractive pairs); Number to English words (chunks of three digits); Hexadecimal and two's complement of negative numbers (mask to a fixed width); Binary strings: add, convert, step counting by the lowest bit; Fractions as decimals: the remainder map finds the repeating part; Negative bases and balanced ternary; Palindromes by generating the first half and mirroring it; Lexicographic order of numbers as strings (preorder over a digit tree); Sum of digits in another base. Number theory: [DSA_ALGORITHMS_NUMBER_THEORY.md](DSA_ALGORITHMS_NUMBER_THEORY.md) group 8 (number representations).
6. **Simulation and sequences.** Direct simulation with a formula shortcut (loop until done / closed form); Josephus problem: queue / recurrence f(n, k) = (f(n - 1, k) + k) % n; Generate a sequence from a rule (look-and-say / Pascal rows / Fibonacci-like); Rule-based labelling (Fizz Buzz and its variants); Clock and angle arithmetic; Calendar arithmetic (days between dates, leap years, day of the year); Times of day on a circle (sort the minutes, add the wrap-around gap); Arithmetic progressions (missing term / check / nth term); Cycle in a generated sequence (seen set / Floyd / a known period); A robot on a plane (direction index, turn by +1 / -1 mod 4, obstacles in a set); Simulate a few periods, then stop (a bounded state must repeat); Halving and subtracting steps to reach zero (count by the bits); Row-bounce index patterns (zigzag conversion). Number theory: [DSA_ALGORITHMS_NUMBER_THEORY.md](DSA_ALGORITHMS_NUMBER_THEORY.md) group 11 (simple identities, Josephus).
7. **Matrix on grids.** Rotate a matrix 90 degrees in place (transpose + reverse the rows / a four-cell cycle) and rotation checks; Transpose and reshape (flat index r * cols + c); Spiral traversal / spiral fill / spiral from a start cell / spiral into a linked list; Diagonal traversal and diagonal keys (r - c for diagonals, r + c for anti-diagonals); In-place markers: the first row and column as notes (set matrix zeroes); In-place state encoding: store old and new state in one cell (Game of Life); Neighbour kernels with direction arrays (8-neighbour smoothing, local maxima); Shift a grid by k (flatten, then rotate the index modulo the size); Row and column scans for extremes (lucky numbers, row with most ones, X-matrix); Row / column / box uniqueness and magic-square checks; Gravity and compaction inside a row (rotate the box); Bounding box of the marked cells; Position map plus row and column counters (first completely painted row or column); Sorting columns of heights per row (rearranged submatrix); Layer-by-layer ring processing (ring index, four sides). Cross-reference: prefix sums on a matrix and searching a sorted matrix belong to the Arrays and Binary Search lessons; grid search to [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md) group 1.
8. **Geometry.** Points on a line: slope as a reduced fraction (gcd, sign normalised, vertical line) / collinearity by the cross product; Points on a line: count the lines needed to cover a chart or a set of points; Points on a line: reflection across a vertical line (min x + max x, set of mirrored points); Points on a line: equal distances from a pivot (squared distances in a hash map); Points on a line: Manhattan distance and the median (best meeting point); Points on a line: widest gap after sorting by one coordinate; Distances: compare squared distances, never take the square root; Circles: containment and reachability between circles (centre distance against radius); Rectangles: overlap and union area of two rectangles (clamp min / max); Rectangles: minimum area rectangle from axis-parallel points (hash set + diagonal pairs); Rectangles: bounding box of a set of points or cells; Rectangles: equal ratios by reduced fraction (interchangeable rectangles); Rectangles: perfect rectangle cover (corner parity) / containment / union area by sweep; Squares: detect squares by the diagonal corner and a point count map; Squares: is a set of four points a square (six pairwise distances, four equal and two equal); Squares: largest square from a point set or from fences; Convex hull: monotone chain (Andrew) / Graham scan / gift wrapping (Jarvis); Orientation test: sign of the cross product (left turn / right turn / collinear); Polygon: area by the shoelace formula, convexity check, point in polygon (ray casting / winding number); Triangles: validity from sides, largest area from points, largest perimeter; Rotating calipers: diameter and minimum bounding box of a convex hull; Angle sort around a point (visible points / widest angular gap); Closest pair of points (divide and conquer / grid hashing); Segment intersection and sweep line over segments; Minimum enclosing circle (names only). Cross-reference: lattice points, Pick's theorem, shoelace in integers and cross-product collinearity are group 12 of [DSA_ALGORITHMS_NUMBER_THEORY.md](DSA_ALGORITHMS_NUMBER_THEORY.md); k-d trees, quadtrees and range trees are group 9 of [DSA_ALGORITHMS_DATA_STRUCTURES.md](DSA_ALGORITHMS_DATA_STRUCTURES.md); the sweep over rectangles and the skyline are groups 12 and 14 of [DSA_INTERVALS_PATTERNS.md](DSA_INTERVALS_PATTERNS.md). There is no catalogue for computational geometry proper (hull, polygon, calipers, closest pair, segments): this group is its only list.
9. **Probability and random.** Shuffle: Fisher-Yates, and why the naive swap-with-any-index shuffle is biased; Weighted random pick: prefix sums + binary search; Reservoir sampling (one item / k items from a stream); Random with O(1) delete: array + hash map, swap with the last; Random pick that skips a blacklist (remap into the tail); Random point in rectangles or in a circle (area-weighted choice / rejection sampling / square-root radius); Rejection sampling: build rand(n) from rand(m); Probability by DP: expected value or reach probability over states; Linearity of expectation with indicator variables; Coupon collector and geometric waiting times; Fair coin from a biased coin, and Monte Carlo estimation; Probability as favourable over total by counting (cards, dice, draws). Number theory: [DSA_ALGORITHMS_NUMBER_THEORY.md](DSA_ALGORITHMS_NUMBER_THEORY.md) group 10 (probability basics); the random-pick design problems are also taught in the Binary Search, Linked List and Arrays and Hashing lessons.
10. **Combinatorics.** nCr by Pascal's triangle (whole rows / one row); nCr by factorials and inverse factorials mod p / by the multiplicative formula without overflow; Lattice paths as a binomial coefficient (with and without obstacles); k-th permutation by the factorial number system; Next permutation (suffix scan + swap + reverse); Generate all permutations (backtracking, with duplicates); Multiset permutations and anagram counts (n! over the product of counts!); Stars and bars with upper limits (inclusion-exclusion over the capped variables); Catalan numbers (balanced brackets, binary search trees); Stirling numbers and arrangements by visible count; Product rule over independent positions (good numbers, choices per slot); Counting orders with constraints (pickup before delivery); Number of ways to reach a point in exactly k steps (binomial of the right moves); Every element appears in 2^(n - 1) subsets (sum over all subsets in closed form); Derangements and Burnside's lemma. Number theory: [DSA_ALGORITHMS_NUMBER_THEORY.md](DSA_ALGORITHMS_NUMBER_THEORY.md) groups 5 (combinatorics) and 6 (counting techniques) hold the full list.
11. **Math plus greedy.** The median minimises the sum of absolute differences (equalise values, meeting point, uni-value grid); The mean minimises the sum of squares; Extremes after sorting (maximum product of three, product of two digits); Greedy construction of the largest or smallest number from digits or divisors; Case analysis with caps (distribute money / candies / children); Cell equivalence classes (positions that repeat with the window period); Constraint propagation from both sides (height limits left to right and right to left); Exchange loops (empty bottles for full ones) in closed form; Greedy on the digits of a base (powers of three, powers of two); Spread a remaining sum as evenly as possible (missing observations); Winner decided by counting moves of each kind (coloured pieces); Canonical coin systems: when greedy change is optimal. Cross-reference: the Greedy lessons own exchange arguments and interval-style greedy.
12. **Number ranges.** Count in [L, R] as f(R) - f(L - 1); Primes in a range (segmented sieve / sieve up to R); Enumerate numbers in [low, high] by construction (sequential digits / palindromes / squares of primes); Lexicographic order of 1..n: next-number walk / k-th by subtree sizes; Numbers up to N with a digit property (digit DP / position counting); Nth digit of the infinite sequence 123456789101112...; Binary search for the answer over a numeric range; Missing term or missing range inside a sorted progression; Enumerate up to n with a check that partitions the digits (punishment number); Closed-form sums over a range; Inclusive / exclusive endpoints and the 32-bit range. Cross-reference: missing ranges and summary ranges are [DSA_INTERVALS_PATTERNS.md](DSA_INTERVALS_PATTERNS.md) groups 10 and 18.
13. **Bit tricks (cross-reference).** Power of two / power of four tests with n & (n - 1) and a mask; Divide and multiply with shifts (no division operator); Add without plus (XOR and carry); Parity and odd / even by n & 1; Minimum flips to make a OR b equal c; Binary gap (distance between set bits); XOR of all pairings (parity of lengths); Recursive bit operations to reach zero (Gray code inverse). These live in [DSA_BIT_MANIPULATION_PATTERNS.md](DSA_BIT_MANIPULATION_PATTERNS.md) (the Bit Manipulation topic). They are listed here only because the owner's Math & Geometry data contains problems of this shape; do not write the lessons twice.
14. **Overflow and precision pitfalls.** Check before you multiply or add (reverse integer, 32-bit bounds); INT_MIN: negation, abs and division by -1 overflow; Products modulo m need a wider type (u64 / u128) before the reduction; lcm overflow: divide before you multiply; Floating-point slopes and ratios lose precision: use reduced fractions or cross products; Cross products and areas of large coordinates overflow i32 (use i64); Square roots and logarithms on floats near exact powers (correct with an integer check); Floor and ceiling division of negative numbers differ between languages; Doubles hold integers exactly only up to 2^53; Huge values as strings: do not parse them; Midpoint without overflow: lo + (hi - lo) / 2; Angles and decimals: compare with an epsilon or stay in integers; Exact decimals through remainders instead of floating division; Rust: checked_ / wrapping_ / saturating_ / overflowing_ arithmetic, `as` casts truncate, debug builds panic on overflow. Number theory: [DSA_ALGORITHMS_NUMBER_THEORY.md](DSA_ALGORITHMS_NUMBER_THEORY.md) group 13 (core implementation patterns).
15. **Observation problems.** Closed form from small cases (compute n = 1..6 by hand, guess, test with a brute force); Count everything and subtract the exceptions (2^n - 2); Invariants and parity (what never changes under the operation); Digital root and mod 9; The first player wins by a symmetry or parity argument; Periodicity: simulate a few rounds and stop; The answer is decided by an extreme (largest, smallest, first, last); A sum constraint pins the missing part; Interactive and query-limited problems (what does one answer reveal); Bulb-switcher style toggles (count divisors, so only squares end on); Brainteasers: reduce to a smaller instance of the same problem.

## Coverage today

Source: `content/dsa/lessons/math-geometry.toml`, `content/dsa/problems.json` (943 problems) and `content/dsa/practice.json` (607 problems).

- **Problems by topic.** 63 problems of `problems.json` sit in the Math & Geometry pattern (13 must learn, 50 practice). 53 of them carry a Math & Geometry technique; 10 are filed under another topic's technique (342 Power of Four: Bit Manipulation:bit-count; 539 Minimum Time Difference: Greedy:sort-pick; 633 Sum of Square Numbers: Two Pointers:opposite; 1183 Maximum Number of Ones: Greedy:sort-pick; 1538 Guess the Majority in a Hidden Array: Arrays & Hashing:counting; 1611 Minimum One Bit Operations to Make Integers Zero: Bit Manipulation:shift; 1637 Widest Vertical Area Between Two Points Containing No Points: Greedy:sort-pick; 1726 Tuple with Same Product: Arrays & Hashing:counting; 1727 Largest Submatrix With Rearrangements: Greedy:sort-pick; 2698 Find the Punishment Number of an Integer: Backtracking:include-exclude). `practice.json` holds 52 more problems of the pattern, all with the list `practice`, four per technique.
- **Lessons.** The 13 techniques and what they cover:

| Technique | Must-learn problem | Problems in the data with this technique | Groups it touches |
|---|---|---|---|
| `Math & Geometry:number-format` | LeetCode 168 Excel Sheet Column Title | 7 | 5 (bijective numeration, Roman numerals, words), 1 (palindrome number) |
| `Math & Geometry:number-theory` | LeetCode 1071 Greatest Common Divisor of Strings | 7 | 4 (gcd, lcm), 2 (primes, sieve, ugly numbers) |
| `Math & Geometry:formula` | LeetCode 1523 Count Odd Numbers in an Interval Range | 10 | 2 (closed-form counts), 6 (Josephus, exchange loops), 11 (case analysis), 12 (range counts), 15 |
| `Math & Geometry:matrix-sim` | LeetCode 867 Transpose Matrix | 12 | 7 (transpose, reshape, kernels, robot, zigzag), 6 (robot) |
| `Math & Geometry:matrix-inplace` | LeetCode 48 Rotate Image | 1 | 7 (rotate image) |
| `Math & Geometry:spiral` | LeetCode 54 Spiral Matrix | 4 | 7 (spiral order, fill, diagonals) |
| `Math & Geometry:markers` | LeetCode 73 Set Matrix Zeroes | 1 | 7 (set zeroes, state encoding) |
| `Math & Geometry:number-cycle` | LeetCode 202 Happy Number | 1 | 1 (happy number, digit sums), 6 (cycles in sequences) |
| `Math & Geometry:digits` | LeetCode 66 Plus One | 3 | 1 (plus one, add strings, multiply strings), 6 (dates and clocks) |
| `Math & Geometry:fast-pow` | LeetCode 50 Pow(x, n) | 1 | 3 (fast power, modulus), 10 (the pow-shaped counts) |
| `Math & Geometry:point-counts` | LeetCode 2013 Detect Squares | 3 | 8 (detect squares, points in a hash map) |
| `Math & Geometry:median` | LeetCode 2033 Minimum Operations to Make a Uni-Value Grid | 2 | 11 (median minimises distance), 8 (meeting point) |
| `Math & Geometry:lex-order` | LeetCode 386 Lexicographical Numbers | 2 | 12 (lexicographic numbers), 5 |

- **Coverage by group.** Covered means a lesson with signals, template and pitfalls exists today; partly means the lessons touch some of the group's patterns; none means no lesson of this topic mentions it.

| # | Group | Status | Notes |
|---|---|---|---|
| 1 | Digit manipulation | partly | `digits` teaches carry propagation; `number-cycle` the digit-square loop. Not covered: reverse integer (lives in Bit Manipulation `digit-extract`), digit-by-digit construction, multiply strings as a template, digit DP. |
| 2 | Counting and number properties | partly | `formula` and `number-theory` cover range counts, the sieve and primality. Not covered: perfect squares, ugly numbers, pigeonhole, trailing zeros. |
| 3 | Exponentiation and roots | partly | `fast-pow` covers the loop and the modulus. Not covered: integer square root (a Binary Search `on-answer` problem), sum of two squares, huge exponents, Fibonacci by fast doubling. |
| 4 | GCD, LCM and divisibility | partly | `number-theory` covers gcd, lcm and gcd of strings. Not covered: extended Euclid, factorisation, periodic events. |
| 5 | Base conversion and representation | partly | `number-format` covers bijective numeration and Roman numerals. Not covered: hexadecimal and two's complement, negative bases, recurring decimals, words. |
| 6 | Simulation and sequences | partly | `formula` has Josephus and bottle exchanges; `matrix-sim` has the robot; `number-cycle` has cycles. Not covered: calendar and clock arithmetic, sequence generation, step counting. |
| 7 | Matrix on grids | covered | `matrix-sim`, `matrix-inplace`, `spiral` and `markers`. Not covered as their own tab: neighbour kernels, diagonal keys, row gravity, ring layers. |
| 8 | Geometry | partly | `point-counts` teaches the hash-map count of points (detect squares). Nothing on slopes by gcd, cross products, rectangle overlap, circles, convex hull, polygons or calipers. |
| 9 | Probability and random | none here | The random-pick design problems sit in Binary Search `weighted`, Linked List and Arrays & Hashing `design-hash`; 384 Shuffle an Array is filed under `lex-order`. No lesson on sampling or expectation. |
| 10 | Combinatorics | none here | Problems sit in 1-D / 2-D Dynamic Programming and Backtracking; only 2929 is a `formula` problem. No lesson on nCr, Catalan or stars and bars. |
| 11 | Math plus greedy | partly | `median` teaches the median target; `formula` has case analysis (distribute money). Not covered: exchange-argument arithmetic, constraint propagation, greedy on base digits. |
| 12 | Number ranges | partly | `formula` teaches f(R) - f(L - 1); `lex-order` teaches the lexicographic walk. Not covered: segmented sieve, nth digit, digit DP over a range. |
| 13 | Bit tricks (cross-reference) | none here | Owned by [DSA_BIT_MANIPULATION_PATTERNS.md](DSA_BIT_MANIPULATION_PATTERNS.md). Bit Manipulation has 6 techniques; this topic only cross-references. |
| 14 | Overflow and precision pitfalls | partly | Pitfall lines exist inside `number-theory`, `digits`, `fast-pow` and `formula`; no lesson treats overflow and precision as a topic of its own. |
| 15 | Observation problems | partly | `formula` teaches working small cases to find the formula. Not covered: invariants, parity and game-theory observations as patterns. |

## Example problems per pattern

Taken only from `content/dsa/problems.json` and `content/dsa/practice.json`, at most four per pattern, written `LeetCode <number> <title> (<difficulty>; <lists>)`. Where the data has no problem the pattern says so and needs one picked from LeetCode and checked before its lesson is written. A problem can serve more than one pattern. Problems filed under other topics (probability, combinatorics, geometry and ranges live partly in Binary Search, Dynamic Programming, Heap, Graphs and Greedy) are included when they show the shape.

### 1. Digit manipulation

- **Extract digits with % 10 and // 10 (right to left) / convert to a string and index**
    - LeetCode 2520 Count the Digits That Divide a Number (easy; practice)
    - LeetCode 1134 Armstrong Number (easy; all)
    - LeetCode 2843 Count Symmetric Integers (easy; practice)
    - LeetCode 1945 Sum of Digits of String After Convert (easy; practice)
- **Digit sum and digital root (loop / the formula 1 + (n - 1) % 9)**
    - LeetCode 258 Add Digits (easy; practice)
    - LeetCode 1945 Sum of Digits of String After Convert (easy; practice)
    - LeetCode 202 Happy Number (easy; neetcode150, neetcode250, all)
- **Reverse an integer, checking for overflow before each digit**
    - LeetCode 7 Reverse Integer (medium; neetcode150, neetcode250, all)
- **Palindrome number (reverse half / compare as a string)**
    - LeetCode 9 Palindrome Number (easy; all)
- **Digit powers and per-digit functions (Armstrong numbers, digit squares)**
    - LeetCode 1134 Armstrong Number (easy; all)
    - LeetCode 202 Happy Number (easy; neetcode150, neetcode250, all)
    - LeetCode 2520 Count the Digits That Divide a Number (easy; practice)
- **Happy number: the digit-square map falls into a cycle (hash set / Floyd / the known cycle at 4)**
    - LeetCode 202 Happy Number (easy; neetcode150, neetcode250, all)
- **Carry propagation on a digit array (plus one, add to array-form)**
    - LeetCode 66 Plus One (easy; neetcode150, neetcode250, all)
    - LeetCode 989 Add to Array-Form of Integer (easy; all)
- **Schoolbook addition of two digit strings / arrays / binary strings**
    - LeetCode 415 Add Strings (easy; practice)
    - LeetCode 67 Add Binary (easy; neetcode250, all)
    - LeetCode 989 Add to Array-Form of Integer (easy; all)
- **Schoolbook multiplication of digit strings (result array of size m + n, digit pair i + j)**
    - LeetCode 43 Multiply Strings (medium; neetcode150, neetcode250, all)
- **Digit-by-digit construction of a target number (next greater permutation of digits / closest palindrome / round up to the next beautiful number)**
    - LeetCode 556 Next Greater Element III (medium; practice)
    - LeetCode 564 Find the Closest Palindrome (hard; practice)
    - LeetCode 2457 Minimum Addition to Make Integer Beautiful (medium; practice)
- **Rearrange or delete digits for the largest or smallest value (maximum swap / remove k digits / largest odd number)**
    - LeetCode 670 Maximum Swap (medium; all)
    - LeetCode 402 Remove K Digits (medium; all)
    - LeetCode 1903 Largest Odd Number in String (easy; all)
- **Enumerate numbers by digit shape (sequential digits / symmetric halves / palindromes of a fixed length)**
    - LeetCode 1291 Sequential Digits (medium; all)
    - LeetCode 2843 Count Symmetric Integers (easy; practice)
    - LeetCode 2217 Find Palindrome With Fixed Length (medium; practice)
- **Count numbers with distinct digits or a digit property (position counting / digit DP)**
    - LeetCode 357 Count Numbers with Unique Digits (medium; practice)
    - LeetCode 2376 Count Special Integers (hard; practice)
- **Place value and the nth digit of a concatenated sequence**
    - LeetCode 400 Nth Digit (medium; practice)
- **Digit groups of three (numbers to words, thousands separators)**
    - LeetCode 273 Integer to English Words (hard; all)

### 2. Counting and number properties

- **Parity: even / odd counts, parity of a sum or product**
    - LeetCode 1523 Count Odd Numbers in an Interval Range (easy; all)
    - LeetCode 2413 Smallest Even Multiple (easy; practice)
- **Perfect square and perfect cube tests (integer square root, then square it back)**
    - LeetCode 367 Valid Perfect Square (easy; all)
    - LeetCode 633 Sum of Square Numbers (medium; all)
- **Power of two / three / four (loop / largest power divides / logarithm with an epsilon / bit test)**
    - LeetCode 231 Power of Two (easy; all)
    - LeetCode 326 Power of Three (easy; practice)
    - LeetCode 342 Power of Four (easy; all)
    - LeetCode 1780 Check if Number is a Sum of Powers of Three (medium; all)
- **Ugly numbers: divide out 2, 3, 5 / generate with three pointers or a heap**
    - LeetCode 263 Ugly Number (easy; all)
    - LeetCode 264 Ugly Number II (medium; all)
    - LeetCode 313 Super Ugly Number (medium; practice)
- **Count divisors by looping to the square root (pairs d and n / d)**
    - LeetCode 2427 Number of Common Factors (easy; practice)
- **Primality test and prime counting (trial division / sieve of Eratosthenes)**
    - LeetCode 204 Count Primes (medium; all)
    - LeetCode 2523 Closest Prime Numbers in Range (medium; all)
    - LeetCode 3233 Find the Count of Numbers Which Are Not Special (medium; practice)
    - LeetCode 2601 Prime Subtraction Operation (medium; all)
- **Trailing zeros of a factorial (count the factor 5, Legendre's formula)**
    - no problem in the data: needs one from LeetCode
- **Count multiples with floor division (in a range / of a or b by inclusion-exclusion)**
    - LeetCode 1523 Count Odd Numbers in an Interval Range (easy; all)
- **Nth number divisible by a or b (binary search on a counting function with lcm)**
    - no problem in the data: needs one from LeetCode
- **Digit-divisibility properties (self-dividing numbers, digits that divide the number)**
    - LeetCode 2520 Count the Digits That Divide a Number (easy; practice)
- **Figurate and triangular numbers (staircase rows, closed-form cell counts)**
    - LeetCode 2579 Count Total Number of Colored Cells (medium; all)
    - LeetCode 1716 Calculate Money in Leetcode Bank (easy; all)
    - LeetCode 1688 Count of Matches in Tournament (easy; all)
- **Counting by runs (a run of length k contributes k(k + 1) / 2 substrings)**
    - LeetCode 1180 Count Substrings with Only One Distinct Letter (easy; all)
- **Count pairs and tuples by a hash map of a derived key (product / ratio / difference of positions and values)**
    - LeetCode 1726 Tuple with Same Product (medium; all)
    - LeetCode 2001 Number of Pairs of Interchangeable Rectangles (medium; all)
    - LeetCode 2364 Count Number of Bad Pairs (medium; all)
    - LeetCode 1512 Number of Good Pairs (easy; all)
- **Pigeonhole principle and remainders (a repeat is forced)**
    - LeetCode 523 Continuous Subarray Sum (medium; all)
    - LeetCode 287 Find the Duplicate Number (medium; neetcode150, neetcode250, all)
- **Which values can exist after repeated operations (a closed-form set, not a simulation)**
    - LeetCode 2549 Count Distinct Numbers on Board (easy; practice)
- **Perfect, abundant and amicable numbers (sum of proper divisors)**
    - no problem in the data: needs one from LeetCode

### 3. Exponentiation and roots

- **Fast power: recursive halving / iterative squaring on the bits of the exponent**
    - LeetCode 50 Pow(x, n) (medium; neetcode150, neetcode250, all)
    - LeetCode 1922 Count Good Numbers (medium; practice)
- **Negative exponents, x = 0, 1 or -1, and the exponent INT_MIN**
    - LeetCode 50 Pow(x, n) (medium; neetcode150, neetcode250, all)
- **Power with a modulus (reduce after every multiplication)**
    - LeetCode 1922 Count Good Numbers (medium; practice)
    - LeetCode 372 Super Pow (medium; practice)
- **Huge exponent given as a digit array (pow of the base to each digit, or Euler's theorem)**
    - LeetCode 372 Super Pow (medium; practice)
- **Closed forms with 2^n (all assignments, minus the ones that do not count)**
    - LeetCode 2550 Count Collisions of Monkeys on a Polygon (medium; practice)
- **Integer square root: binary search / Newton's method / bit by bit**
    - LeetCode 69 Sqrt(x) (easy; neetcode250, all)
    - LeetCode 367 Valid Perfect Square (easy; all)
- **Sum of two squares (two pointers up to the square root / Fermat's two-square theorem)**
    - LeetCode 633 Sum of Square Numbers (medium; all)
- **Nth root and cube root by binary search or Newton's method**
    - no problem in the data: needs one from LeetCode
- **Logarithms to test or compare powers (log vs repeated division, and why floats lie)**
    - LeetCode 326 Power of Three (easy; practice)
    - LeetCode 342 Power of Four (easy; all)
- **Fibonacci and linear recurrences by fast doubling or matrix power**
    - LeetCode 509 Fibonacci Number (easy; practice)
    - LeetCode 1137 N-th Tribonacci Number (easy; neetcode250, all)
- **Geometric series in closed form (finite / mod p)**
    - no problem in the data: needs one from LeetCode
- **Exponent tower and exponent reduction by Euler's theorem**
    - LeetCode 372 Super Pow (medium; practice)

### 4. GCD, LCM and divisibility

- **Euclid's algorithm (iterative / recursive) and the gcd of an array**
    - LeetCode 1979 Find Greatest Common Divisor of Array (easy; practice)
    - LeetCode 2427 Number of Common Factors (easy; practice)
    - LeetCode 1071 Greatest Common Divisor of Strings (easy; neetcode250, all)
- **gcd of strings (concatenation check / gcd of the lengths)**
    - LeetCode 1071 Greatest Common Divisor of Strings (easy; neetcode250, all)
- **gcd of adjacent elements (insert gcd between list nodes / array fold)**
    - LeetCode 2807 Insert Greatest Common Divisors in Linked List (medium; neetcode250, all)
- **lcm from gcd, dividing before multiplying**
    - LeetCode 2413 Smallest Even Multiple (easy; practice)
- **Reduced fractions as keys (ratios, slopes, directions)**
    - LeetCode 2001 Number of Pairs of Interchangeable Rectangles (medium; all)
    - LeetCode 149 Max Points on a Line (hard; all)
- **Count common divisors through the gcd**
    - LeetCode 2427 Number of Common Factors (easy; practice)
- **Connectivity by shared prime factors (union-find over primes)**
    - LeetCode 2709 Greatest Common Divisor Traversal (hard; neetcode250, all)
- **Divisibility by digits and remainders**
    - LeetCode 2520 Count the Digits That Divide a Number (easy; practice)
- **Smallest prime factor and factorisation by repeated division**
    - LeetCode 625 Minimum Factorization (medium; all)
- **Bezout's identity and extended Euclid (jugs, reachable amounts, linear Diophantine equations)**
    - no problem in the data: needs one from LeetCode
- **Periodic events and lcm (when do cycles line up)**
    - no problem in the data: needs one from LeetCode
- **Divisibility invariants (what stays a multiple of g under the allowed operations)**
    - no problem in the data: needs one from LeetCode

### 5. Base conversion and representation

- **Convert to and from base k (repeated divmod, then reverse the digits)**
    - LeetCode 1780 Check if Number is a Sum of Powers of Three (medium; all)
    - LeetCode 405 Convert a Number to Hexadecimal (easy; practice)
- **Bijective numeration with no zero digit (Excel columns, spreadsheet cells)**
    - LeetCode 168 Excel Sheet Column Title (easy; neetcode250, all)
    - LeetCode 171 Excel Sheet Column Number (easy; practice)
    - LeetCode 3484 Design Spreadsheet (medium; practice)
- **Roman numerals both ways (greedy table / subtractive pairs)**
    - LeetCode 12 Integer to Roman (medium; all)
    - LeetCode 13 Roman to Integer (easy; neetcode250, all)
- **Number to English words (chunks of three digits)**
    - LeetCode 273 Integer to English Words (hard; all)
- **Hexadecimal and two's complement of negative numbers (mask to a fixed width)**
    - LeetCode 405 Convert a Number to Hexadecimal (easy; practice)
- **Binary strings: add, convert, step counting by the lowest bit**
    - LeetCode 67 Add Binary (easy; neetcode250, all)
    - LeetCode 1342 Number of Steps to Reduce a Number to Zero (easy; practice)
- **Fractions as decimals: the remainder map finds the repeating part**
    - LeetCode 166 Fraction to Recurring Decimal (medium; practice)
- **Negative bases and balanced ternary**
    - no problem in the data: needs one from LeetCode
- **Palindromes by generating the first half and mirroring it**
    - LeetCode 2217 Find Palindrome With Fixed Length (medium; practice)
    - LeetCode 564 Find the Closest Palindrome (hard; practice)
- **Lexicographic order of numbers as strings (preorder over a digit tree)**
    - LeetCode 386 Lexicographical Numbers (medium; all)
    - LeetCode 440 K-th Smallest in Lexicographical Order (hard; all)
- **Sum of digits in another base**
    - no problem in the data: needs one from LeetCode

### 6. Simulation and sequences

- **Direct simulation with a formula shortcut (loop until done / closed form)**
    - LeetCode 1518 Water Bottles (easy; all)
    - LeetCode 3100 Water Bottles II (medium; practice)
    - LeetCode 1688 Count of Matches in Tournament (easy; all)
    - LeetCode 1716 Calculate Money in Leetcode Bank (easy; all)
- **Josephus problem: queue / recurrence f(n, k) = (f(n - 1, k) + k) % n**
    - LeetCode 1823 Find the Winner of the Circular Game (medium; all)
- **Generate a sequence from a rule (look-and-say / Pascal rows / Fibonacci-like)**
    - LeetCode 38 Count and Say (medium; practice)
    - LeetCode 118 Pascal's Triangle (easy; all)
    - LeetCode 119 Pascal's Triangle II (easy; all)
- **Rule-based labelling (Fizz Buzz and its variants)**
    - LeetCode 412 Fizz Buzz (easy; practice)
- **Clock and angle arithmetic**
    - LeetCode 1344 Angle Between Hands of a Clock (medium; practice)
- **Calendar arithmetic (days between dates, leap years, day of the year)**
    - LeetCode 1360 Number of Days Between Two Dates (easy; practice)
- **Times of day on a circle (sort the minutes, add the wrap-around gap)**
    - LeetCode 539 Minimum Time Difference (medium; all)
- **Arithmetic progressions (missing term / check / nth term)**
    - LeetCode 1228 Missing Number In Arithmetic Progression (easy; all)
- **Cycle in a generated sequence (seen set / Floyd / a known period)**
    - LeetCode 202 Happy Number (easy; neetcode150, neetcode250, all)
    - LeetCode 258 Add Digits (easy; practice)
- **A robot on a plane (direction index, turn by +1 / -1 mod 4, obstacles in a set)**
    - LeetCode 1041 Robot Bounded In Circle (medium; all)
    - LeetCode 874 Walking Robot Simulation (medium; all)
- **Simulate a few periods, then stop (a bounded state must repeat)**
    - LeetCode 1041 Robot Bounded In Circle (medium; all)
- **Halving and subtracting steps to reach zero (count by the bits)**
    - LeetCode 1342 Number of Steps to Reduce a Number to Zero (easy; practice)
    - LeetCode 2571 Minimum Operations to Reduce an Integer to 0 (medium; practice)
- **Row-bounce index patterns (zigzag conversion)**
    - LeetCode 6 Zigzag Conversion (medium; all)

### 7. Matrix on grids

- **Rotate a matrix 90 degrees in place (transpose + reverse the rows / a four-cell cycle) and rotation checks**
    - LeetCode 48 Rotate Image (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 1886 Determine Whether Matrix Can Be Obtained By Rotation (easy; practice)
- **Transpose and reshape (flat index r * cols + c)**
    - LeetCode 867 Transpose Matrix (easy; neetcode250, all)
    - LeetCode 566 Reshape the Matrix (easy; practice)
    - LeetCode 2022 Convert 1D Array Into 2D Array (easy; all)
- **Spiral traversal / spiral fill / spiral from a start cell / spiral into a linked list**
    - LeetCode 54 Spiral Matrix (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 59 Spiral Matrix II (medium; all)
    - LeetCode 885 Spiral Matrix III (medium; all)
    - LeetCode 2326 Spiral Matrix IV (medium; all)
- **Diagonal traversal and diagonal keys (r - c for diagonals, r + c for anti-diagonals)**
    - LeetCode 498 Diagonal Traverse (medium; practice)
    - LeetCode 766 Toeplitz Matrix (easy; practice)
    - LeetCode 1572 Matrix Diagonal Sum (easy; all)
- **In-place markers: the first row and column as notes (set matrix zeroes)**
    - LeetCode 73 Set Matrix Zeroes (medium; blind75, neetcode150, neetcode250, all)
- **In-place state encoding: store old and new state in one cell (Game of Life)**
    - LeetCode 289 Game of Life (medium; practice)
- **Neighbour kernels with direction arrays (8-neighbour smoothing, local maxima)**
    - LeetCode 661 Image Smoother (easy; all)
    - LeetCode 2373 Largest Local Values in a Matrix (easy; all)
    - LeetCode 289 Game of Life (medium; practice)
- **Shift a grid by k (flatten, then rotate the index modulo the size)**
    - LeetCode 1260 Shift 2D Grid (easy; all)
- **Row and column scans for extremes (lucky numbers, row with most ones, X-matrix)**
    - LeetCode 1380 Lucky Numbers in a Matrix (easy; all)
    - LeetCode 2643 Row With Maximum Ones (easy; practice)
    - LeetCode 2319 Check if Matrix Is X-Matrix (easy; practice)
- **Row / column / box uniqueness and magic-square checks**
    - LeetCode 2133 Check if Every Row and Column Contains All Numbers (easy; practice)
    - LeetCode 840 Magic Squares In Grid (medium; all)
    - LeetCode 1895 Largest Magic Square (medium; practice)
- **Gravity and compaction inside a row (rotate the box)**
    - LeetCode 1861 Rotating the Box (medium; all)
- **Bounding box of the marked cells**
    - LeetCode 3195 Find the Minimum Area to Cover All Ones I (medium; practice)
- **Position map plus row and column counters (first completely painted row or column)**
    - LeetCode 2661 First Completely Painted Row or Column (medium; practice)
- **Sorting columns of heights per row (rearranged submatrix)**
    - LeetCode 1727 Largest Submatrix With Rearrangements (medium; all)
- **Layer-by-layer ring processing (ring index, four sides)**
    - LeetCode 54 Spiral Matrix (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 48 Rotate Image (medium; blind75, neetcode150, neetcode250, all)

### 8. Geometry

- **Points on a line: slope as a reduced fraction (gcd, sign normalised, vertical line) / collinearity by the cross product**
    - LeetCode 149 Max Points on a Line (hard; all)
    - LeetCode 2280 Minimum Lines to Represent a Line Chart (medium; practice)
- **Points on a line: count the lines needed to cover a chart or a set of points**
    - LeetCode 2280 Minimum Lines to Represent a Line Chart (medium; practice)
- **Points on a line: reflection across a vertical line (min x + max x, set of mirrored points)**
    - LeetCode 356 Line Reflection (medium; all)
- **Points on a line: equal distances from a pivot (squared distances in a hash map)**
    - LeetCode 447 Number of Boomerangs (medium; practice)
- **Points on a line: Manhattan distance and the median (best meeting point)**
    - LeetCode 296 Best Meeting Point (hard; all)
- **Points on a line: widest gap after sorting by one coordinate**
    - LeetCode 1637 Widest Vertical Area Between Two Points Containing No Points (easy; all)
- **Distances: compare squared distances, never take the square root**
    - LeetCode 973 K Closest Points to Origin (medium; neetcode150, neetcode250, all)
    - LeetCode 2101 Detonate the Maximum Bombs (medium; all)
    - LeetCode 447 Number of Boomerangs (medium; practice)
- **Circles: containment and reachability between circles (centre distance against radius)**
    - LeetCode 2101 Detonate the Maximum Bombs (medium; all)
- **Rectangles: overlap and union area of two rectangles (clamp min / max)**
    - LeetCode 223 Rectangle Area (medium; practice)
- **Rectangles: minimum area rectangle from axis-parallel points (hash set + diagonal pairs)**
    - LeetCode 939 Minimum Area Rectangle (medium; practice)
- **Rectangles: bounding box of a set of points or cells**
    - LeetCode 3195 Find the Minimum Area to Cover All Ones I (medium; practice)
- **Rectangles: equal ratios by reduced fraction (interchangeable rectangles)**
    - LeetCode 2001 Number of Pairs of Interchangeable Rectangles (medium; all)
- **Rectangles: perfect rectangle cover (corner parity) / containment / union area by sweep**
    - no problem in the data: needs one from LeetCode
- **Squares: detect squares by the diagonal corner and a point count map**
    - LeetCode 2013 Detect Squares (medium; neetcode150, neetcode250, all)
- **Squares: is a set of four points a square (six pairwise distances, four equal and two equal)**
    - no problem in the data: needs one from LeetCode
- **Squares: largest square from a point set or from fences**
    - no problem in the data: needs one from LeetCode
- **Convex hull: monotone chain (Andrew) / Graham scan / gift wrapping (Jarvis)**
    - no problem in the data: needs one from LeetCode
- **Orientation test: sign of the cross product (left turn / right turn / collinear)**
    - no problem in the data: needs one from LeetCode
- **Polygon: area by the shoelace formula, convexity check, point in polygon (ray casting / winding number)**
    - no problem in the data: needs one from LeetCode
- **Triangles: validity from sides, largest area from points, largest perimeter**
    - no problem in the data: needs one from LeetCode
- **Rotating calipers: diameter and minimum bounding box of a convex hull**
    - no problem in the data: needs one from LeetCode
- **Angle sort around a point (visible points / widest angular gap)**
    - no problem in the data: needs one from LeetCode
- **Closest pair of points (divide and conquer / grid hashing)**
    - no problem in the data: needs one from LeetCode
- **Segment intersection and sweep line over segments**
    - no problem in the data: needs one from LeetCode
- **Minimum enclosing circle (names only)**
    - no problem in the data: needs one from LeetCode

### 9. Probability and random

- **Shuffle: Fisher-Yates, and why the naive swap-with-any-index shuffle is biased**
    - LeetCode 384 Shuffle an Array (medium; practice)
- **Weighted random pick: prefix sums + binary search**
    - LeetCode 528 Random Pick with Weight (medium; all)
- **Reservoir sampling (one item / k items from a stream)**
    - LeetCode 382 Linked List Random Node (medium; practice)
    - LeetCode 497 Random Point in Non-overlapping Rectangles (medium; practice)
- **Random with O(1) delete: array + hash map, swap with the last**
    - LeetCode 380 Insert Delete GetRandom O(1) (medium; all)
- **Random pick that skips a blacklist (remap into the tail)**
    - LeetCode 710 Random Pick with Blacklist (hard; practice)
- **Random point in rectangles or in a circle (area-weighted choice / rejection sampling / square-root radius)**
    - LeetCode 497 Random Point in Non-overlapping Rectangles (medium; practice)
- **Rejection sampling: build rand(n) from rand(m)**
    - no problem in the data: needs one from LeetCode
- **Probability by DP: expected value or reach probability over states**
    - LeetCode 837 New 21 Game (medium; all)
    - LeetCode 688 Knight Probability in Chessboard (medium; practice)
- **Linearity of expectation with indicator variables**
    - no problem in the data: needs one from LeetCode
- **Coupon collector and geometric waiting times**
    - no problem in the data: needs one from LeetCode
- **Fair coin from a biased coin, and Monte Carlo estimation**
    - no problem in the data: needs one from LeetCode
- **Probability as favourable over total by counting (cards, dice, draws)**
    - no problem in the data: needs one from LeetCode

### 10. Combinatorics

- **nCr by Pascal's triangle (whole rows / one row)**
    - LeetCode 118 Pascal's Triangle (easy; all)
    - LeetCode 119 Pascal's Triangle II (easy; all)
    - LeetCode 62 Unique Paths (medium; blind75, neetcode150, neetcode250, all)
- **nCr by factorials and inverse factorials mod p / by the multiplicative formula without overflow**
    - LeetCode 62 Unique Paths (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 1359 Count All Valid Pickup and Delivery Options (hard; all)
    - LeetCode 2514 Count Anagrams (hard; practice)
- **Lattice paths as a binomial coefficient (with and without obstacles)**
    - LeetCode 62 Unique Paths (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 63 Unique Paths II (medium; neetcode250, all)
- **k-th permutation by the factorial number system**
    - LeetCode 60 Permutation Sequence (hard; practice)
- **Next permutation (suffix scan + swap + reverse)**
    - LeetCode 31 Next Permutation (medium; all)
- **Generate all permutations (backtracking, with duplicates)**
    - LeetCode 46 Permutations (medium; neetcode150, neetcode250, all)
    - LeetCode 47 Permutations II (medium; neetcode250, all)
- **Multiset permutations and anagram counts (n! over the product of counts!)**
    - LeetCode 2514 Count Anagrams (hard; practice)
- **Stars and bars with upper limits (inclusion-exclusion over the capped variables)**
    - LeetCode 2929 Distribute Candies Among Children II (medium; all)
- **Catalan numbers (balanced brackets, binary search trees)**
    - LeetCode 96 Unique Binary Search Trees (medium; all)
    - LeetCode 22 Generate Parentheses (medium; neetcode150, neetcode250, all)
- **Stirling numbers and arrangements by visible count**
    - LeetCode 1866 Number of Ways to Rearrange Sticks With K Sticks Visible (hard; all)
    - LeetCode 920 Number of Music Playlists (hard; all)
- **Product rule over independent positions (good numbers, choices per slot)**
    - LeetCode 1922 Count Good Numbers (medium; practice)
- **Counting orders with constraints (pickup before delivery)**
    - LeetCode 1359 Count All Valid Pickup and Delivery Options (hard; all)
- **Number of ways to reach a point in exactly k steps (binomial of the right moves)**
    - LeetCode 2400 Number of Ways to Reach a Position After Exactly k Steps (medium; practice)
    - LeetCode 3154 Find Number of Ways to Reach the K-th Stair (hard; practice)
- **Every element appears in 2^(n - 1) subsets (sum over all subsets in closed form)**
    - LeetCode 1863 Sum of All Subset XOR Totals (easy; neetcode250, all)
- **Derangements and Burnside's lemma**
    - no problem in the data: needs one from LeetCode

### 11. Math plus greedy

- **The median minimises the sum of absolute differences (equalise values, meeting point, uni-value grid)**
    - LeetCode 462 Minimum Moves to Equal Array Elements II (medium; practice)
    - LeetCode 2033 Minimum Operations to Make a Uni-Value Grid (medium; all)
    - LeetCode 296 Best Meeting Point (hard; all)
- **The mean minimises the sum of squares**
    - no problem in the data: needs one from LeetCode
- **Extremes after sorting (maximum product of three, product of two digits)**
    - LeetCode 628 Maximum Product of Three Numbers (easy; practice)
    - LeetCode 3536 Maximum Product of Two Digits (easy; practice)
- **Greedy construction of the largest or smallest number from digits or divisors**
    - LeetCode 625 Minimum Factorization (medium; all)
    - LeetCode 2457 Minimum Addition to Make Integer Beautiful (medium; practice)
    - LeetCode 564 Find the Closest Palindrome (hard; practice)
- **Case analysis with caps (distribute money / candies / children)**
    - LeetCode 2591 Distribute Money to Maximum Children (easy; practice)
    - LeetCode 2929 Distribute Candies Among Children II (medium; all)
- **Cell equivalence classes (positions that repeat with the window period)**
    - LeetCode 1183 Maximum Number of Ones (hard; all)
- **Constraint propagation from both sides (height limits left to right and right to left)**
    - LeetCode 1840 Maximum Building Height (hard; practice)
- **Exchange loops (empty bottles for full ones) in closed form**
    - LeetCode 1518 Water Bottles (easy; all)
    - LeetCode 3100 Water Bottles II (medium; practice)
- **Greedy on the digits of a base (powers of three, powers of two)**
    - LeetCode 1780 Check if Number is a Sum of Powers of Three (medium; all)
    - LeetCode 2571 Minimum Operations to Reduce an Integer to 0 (medium; practice)
- **Spread a remaining sum as evenly as possible (missing observations)**
    - LeetCode 2028 Find Missing Observations (medium; all)
- **Winner decided by counting moves of each kind (coloured pieces)**
    - LeetCode 2038 Remove Colored Pieces if Both Neighbors are the Same Color (medium; all)
- **Canonical coin systems: when greedy change is optimal**
    - no problem in the data: needs one from LeetCode

### 12. Number ranges

- **Count in [L, R] as f(R) - f(L - 1)**
    - LeetCode 1523 Count Odd Numbers in an Interval Range (easy; all)
    - LeetCode 3233 Find the Count of Numbers Which Are Not Special (medium; practice)
- **Primes in a range (segmented sieve / sieve up to R)**
    - LeetCode 2523 Closest Prime Numbers in Range (medium; all)
    - LeetCode 204 Count Primes (medium; all)
- **Enumerate numbers in [low, high] by construction (sequential digits / palindromes / squares of primes)**
    - LeetCode 1291 Sequential Digits (medium; all)
    - LeetCode 3233 Find the Count of Numbers Which Are Not Special (medium; practice)
- **Lexicographic order of 1..n: next-number walk / k-th by subtree sizes**
    - LeetCode 386 Lexicographical Numbers (medium; all)
    - LeetCode 440 K-th Smallest in Lexicographical Order (hard; all)
- **Numbers up to N with a digit property (digit DP / position counting)**
    - LeetCode 2376 Count Special Integers (hard; practice)
    - LeetCode 357 Count Numbers with Unique Digits (medium; practice)
    - LeetCode 2843 Count Symmetric Integers (easy; practice)
- **Nth digit of the infinite sequence 123456789101112...**
    - LeetCode 400 Nth Digit (medium; practice)
- **Binary search for the answer over a numeric range**
    - LeetCode 69 Sqrt(x) (easy; neetcode250, all)
- **Missing term or missing range inside a sorted progression**
    - LeetCode 1228 Missing Number In Arithmetic Progression (easy; all)
- **Enumerate up to n with a check that partitions the digits (punishment number)**
    - LeetCode 2698 Find the Punishment Number of an Integer (medium; all)
- **Closed-form sums over a range**
    - LeetCode 1716 Calculate Money in Leetcode Bank (easy; all)
- **Inclusive / exclusive endpoints and the 32-bit range**
    - no problem in the data: needs one from LeetCode

### 13. Bit tricks (cross-reference)

- **Power of two / power of four tests with n & (n - 1) and a mask**
    - LeetCode 231 Power of Two (easy; all)
    - LeetCode 342 Power of Four (easy; all)
- **Divide and multiply with shifts (no division operator)**
    - LeetCode 29 Divide Two Integers (medium; practice)
- **Add without plus (XOR and carry)**
    - LeetCode 371 Sum of Two Integers (medium; blind75, neetcode150, neetcode250, all)
- **Parity and odd / even by n & 1**
    - LeetCode 1342 Number of Steps to Reduce a Number to Zero (easy; practice)
- **Minimum flips to make a OR b equal c**
    - LeetCode 1318 Minimum Flips to Make a OR b Equal to c (medium; practice)
- **Binary gap (distance between set bits)**
    - LeetCode 868 Binary Gap (easy; practice)
- **XOR of all pairings (parity of lengths)**
    - LeetCode 2425 Bitwise XOR of All Pairings (medium; all)
- **Recursive bit operations to reach zero (Gray code inverse)**
    - LeetCode 1611 Minimum One Bit Operations to Make Integers Zero (hard; all)

### 14. Overflow and precision pitfalls

- **Check before you multiply or add (reverse integer, 32-bit bounds)**
    - LeetCode 7 Reverse Integer (medium; neetcode150, neetcode250, all)
- **INT_MIN: negation, abs and division by -1 overflow**
    - LeetCode 29 Divide Two Integers (medium; practice)
    - LeetCode 50 Pow(x, n) (medium; neetcode150, neetcode250, all)
- **Products modulo m need a wider type (u64 / u128) before the reduction**
    - LeetCode 1922 Count Good Numbers (medium; practice)
    - LeetCode 372 Super Pow (medium; practice)
- **lcm overflow: divide before you multiply**
    - LeetCode 2413 Smallest Even Multiple (easy; practice)
- **Floating-point slopes and ratios lose precision: use reduced fractions or cross products**
    - LeetCode 149 Max Points on a Line (hard; all)
    - LeetCode 2001 Number of Pairs of Interchangeable Rectangles (medium; all)
- **Cross products and areas of large coordinates overflow i32 (use i64)**
    - LeetCode 149 Max Points on a Line (hard; all)
    - LeetCode 2280 Minimum Lines to Represent a Line Chart (medium; practice)
- **Square roots and logarithms on floats near exact powers (correct with an integer check)**
    - LeetCode 69 Sqrt(x) (easy; neetcode250, all)
    - LeetCode 326 Power of Three (easy; practice)
- **Floor and ceiling division of negative numbers differ between languages**
    - no problem in the data: needs one from LeetCode
- **Doubles hold integers exactly only up to 2^53**
    - no problem in the data: needs one from LeetCode
- **Huge values as strings: do not parse them**
    - LeetCode 43 Multiply Strings (medium; neetcode150, neetcode250, all)
    - LeetCode 415 Add Strings (easy; practice)
- **Midpoint without overflow: lo + (hi - lo) / 2**
    - LeetCode 69 Sqrt(x) (easy; neetcode250, all)
- **Angles and decimals: compare with an epsilon or stay in integers**
    - LeetCode 1344 Angle Between Hands of a Clock (medium; practice)
- **Exact decimals through remainders instead of floating division**
    - LeetCode 166 Fraction to Recurring Decimal (medium; practice)
- **Rust: checked_ / wrapping_ / saturating_ / overflowing_ arithmetic, `as` casts truncate, debug builds panic on overflow**
    - no problem in the data: needs one from LeetCode

### 15. Observation problems

- **Closed form from small cases (compute n = 1..6 by hand, guess, test with a brute force)**
    - LeetCode 2579 Count Total Number of Colored Cells (medium; all)
    - LeetCode 1716 Calculate Money in Leetcode Bank (easy; all)
    - LeetCode 1688 Count of Matches in Tournament (easy; all)
    - LeetCode 1518 Water Bottles (easy; all)
- **Count everything and subtract the exceptions (2^n - 2)**
    - LeetCode 2550 Count Collisions of Monkeys on a Polygon (medium; practice)
- **Invariants and parity (what never changes under the operation)**
    - LeetCode 2549 Count Distinct Numbers on Board (easy; practice)
    - LeetCode 1823 Find the Winner of the Circular Game (medium; all)
- **Digital root and mod 9**
    - LeetCode 258 Add Digits (easy; practice)
- **The first player wins by a symmetry or parity argument**
    - LeetCode 877 Stone Game (medium; neetcode250, all)
    - LeetCode 464 Can I Win (medium; practice)
- **Periodicity: simulate a few rounds and stop**
    - LeetCode 1041 Robot Bounded In Circle (medium; all)
- **The answer is decided by an extreme (largest, smallest, first, last)**
    - LeetCode 628 Maximum Product of Three Numbers (easy; practice)
    - LeetCode 2038 Remove Colored Pieces if Both Neighbors are the Same Color (medium; all)
- **A sum constraint pins the missing part**
    - LeetCode 2028 Find Missing Observations (medium; all)
- **Interactive and query-limited problems (what does one answer reveal)**
    - LeetCode 1538 Guess the Majority in a Hidden Array (medium; all)
- **Bulb-switcher style toggles (count divisors, so only squares end on)**
    - no problem in the data: needs one from LeetCode
- **Brainteasers: reduce to a smaller instance of the same problem**
    - no problem in the data: needs one from LeetCode

## Gaps

- **Patterns without a problem in the data: 36 of 202.** Each needs an example picked from LeetCode and checked before its lesson is written:
    - 2. Trailing zeros of a factorial (count the factor 5, Legendre's formula)
    - 2. Nth number divisible by a or b (binary search on a counting function with lcm)
    - 2. Perfect, abundant and amicable numbers (sum of proper divisors)
    - 3. Nth root and cube root by binary search or Newton's method
    - 3. Geometric series in closed form (finite / mod p)
    - 4. Bezout's identity and extended Euclid (jugs, reachable amounts, linear Diophantine equations)
    - 4. Periodic events and lcm (when do cycles line up)
    - 4. Divisibility invariants (what stays a multiple of g under the allowed operations)
    - 5. Negative bases and balanced ternary
    - 5. Sum of digits in another base
    - 8. Rectangles: perfect rectangle cover (corner parity) / containment / union area by sweep
    - 8. Squares: is a set of four points a square (six pairwise distances, four equal and two equal)
    - 8. Squares: largest square from a point set or from fences
    - 8. Convex hull: monotone chain (Andrew) / Graham scan / gift wrapping (Jarvis)
    - 8. Orientation test: sign of the cross product (left turn / right turn / collinear)
    - 8. Polygon: area by the shoelace formula, convexity check, point in polygon (ray casting / winding number)
    - 8. Triangles: validity from sides, largest area from points, largest perimeter
    - 8. Rotating calipers: diameter and minimum bounding box of a convex hull
    - 8. Angle sort around a point (visible points / widest angular gap)
    - 8. Closest pair of points (divide and conquer / grid hashing)
    - 8. Segment intersection and sweep line over segments
    - 8. Minimum enclosing circle (names only)
    - 9. Rejection sampling: build rand(n) from rand(m)
    - 9. Linearity of expectation with indicator variables
    - 9. Coupon collector and geometric waiting times
    - 9. Fair coin from a biased coin, and Monte Carlo estimation
    - 9. Probability as favourable over total by counting (cards, dice, draws)
    - 10. Derangements and Burnside's lemma
    - 11. The mean minimises the sum of squares
    - 11. Canonical coin systems: when greedy change is optimal
    - 12. Inclusive / exclusive endpoints and the 32-bit range
    - 14. Floor and ceiling division of negative numbers differ between languages
    - 14. Doubles hold integers exactly only up to 2^53
    - 14. Rust: checked_ / wrapping_ / saturating_ / overflowing_ arithmetic, `as` casts truncate, debug builds panic on overflow
    - 15. Bulb-switcher style toggles (count divisors, so only squares end on)
    - 15. Brainteasers: reduce to a smaller instance of the same problem
- **Geometry is the thinnest group.** 12 of its 25 patterns have no problem in the data: the data teaches counting points in a hash map and little else (convex hull, polygons, calipers, closest pair, segments and angle sorts have none). Of all problems in the data, only 6 carry LeetCode's Geometry tag (149, 223, 939, 973, 2101, 2280). Decide whether Math & Geometry should teach computational geometry at all or only the interview staples (slopes by gcd, cross product, rectangle overlap, squares from points, hull as a recognised name).
- **Patterns with a problem but no lesson.** Everything outside the 13 techniques: groups 9 (probability and random), 10 (combinatorics) and 13 (bit tricks) have no lesson in this topic, and groups 2, 3, 5, 6, 8, 12, 14 and 15 are covered only in a few lines of a technique.
- **Technique labels that hide topic problems.** Ten problems of the pattern in `problems.json` are filed under another topic's technique (see Coverage today). In `practice.json` the four practice problems of each technique look assigned by position, so several fit another group better: 166 Fraction to Recurring Decimal, 564 Find the Closest Palindrome and 2235 Add Two Integers sit under `matrix-inplace`; 384 Shuffle an Array, 939 Minimum Area Rectangle, 1352 Product of the Last K Numbers and 2376 Count Special Integers sit under `lex-order`; 1672 Richest Customer Wealth and 2303 Calculate Amount Paid in Taxes sit under `spiral`. Re-file before the new lessons pick their practice problems.
- **Must-learn problems.** Every new lesson that is not an existing technique needs a first problem. Candidates already in the data, one per new lesson (a proposal): group 8 geometry 149 Max Points on a Line (slopes by gcd) and 223 Rectangle Area; group 9 384 Shuffle an Array and 528 Random Pick with Weight; group 10 62 Unique Paths (binomial) or 60 Permutation Sequence; group 3 69 Sqrt(x); group 6 1344 Angle Between Hands of a Clock or 1360 Number of Days Between Two Dates; group 14 7 Reverse Integer.
- **Cross-referenced lists to keep in sync.** Groups 1 to 5 and 10 overlap groups 1 to 12 of [DSA_ALGORITHMS_NUMBER_THEORY.md](DSA_ALGORITHMS_NUMBER_THEORY.md); a pattern is written once, in the list that owns it, and the other list only points at it. Group 13 is owned by [DSA_BIT_MANIPULATION_PATTERNS.md](DSA_BIT_MANIPULATION_PATTERNS.md). No document yet owns computational geometry (group 8); the nearest lists are the integer-geometry group of the number theory file, the geometry structures group of the data structures file and the intervals file.
- **Practice track alignment.** `practice.json` has 52 problems with this pattern, all on the list `practice`, four per technique; the new lessons should draw their practice problems from there first.
- **Recommended build order** (a proposal, not a decision): groups 7, 1, 4 and 5 first (they extend existing techniques and need no new data), then 2, 3, 6, 11, 12 and 15 (small lessons with problems already in the data), then 14 (a checklist lesson across the others), then 9 and 10 (need a decision on whether they stay in this topic or move to Heap, Design and Dynamic Programming), and last 8 (needs the scope decision above and new problems).
