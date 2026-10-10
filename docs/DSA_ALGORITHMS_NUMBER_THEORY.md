# Number theory, combinatorics and discrete math: the exhaustive target list

The target list (2026-10-10) of every number-theory, combinatorics and discrete-math algorithm and technique that can come up on
LeetCode or in an interview, as the target for the Math & Geometry pattern lessons. The rule is in [DSA.md](DSA.md), decision 32: a
topic's patterns section is exhaustive, patterns without a NeetCode problem get **example problems** from LeetCode, and variants of one
pattern (recursive / iterative) are **tabs** of one lesson. The format follows [DSA_GRAPH_PATTERNS.md](DSA_GRAPH_PATTERNS.md).

Status: documented only. Today `content/dsa/lessons/math-geometry.toml` has 13 techniques (number-format, number-theory, formula,
matrix-sim, matrix-inplace, spiral, markers, number-cycle, digits, fast-pow, point-counts, median, lex-order); most of the list below has
no lesson yet. Building the rest needs a mockup of the tabs first, then lessons and picked example problems. Bit tricks live in the Bit
Manipulation topic and are not repeated here; probability sampling is cross-referenced from the Heap and Design topics.

Items written *a / b* in a group are variants for tabs where one lesson covers both (for example "Pascal / factorials / Lucas").

1. **Divisibility and gcd.** Divisibility rules and remainders; Euclid's algorithm (iterative / recursive); extended Euclid; Bezout's identity and linear Diophantine equations; binary gcd (Stein); lcm and the gcd-lcm product identity; gcd / lcm of an array (fold / prefix and suffix gcd); gcd of a range (sparse table / segment tree); gcd on strings and on fractions (reduce by gcd); coprime test and counting coprime pairs; number of common divisors via gcd; parity and divisibility invariants.
2. **Primes and factorisation.** Primality by trial division up to the square root (6k plus or minus 1 wheel); Sieve of Eratosthenes (plain / odd-only / bitset); linear (Euler) sieve; segmented sieve; smallest prime factor sieve and O(log n) factorisation; Miller-Rabin (deterministic bases for 64-bit / probabilistic); Fermat primality test and Carmichael numbers; trial-division factorisation; Pollard's rho (Floyd / Brent); Pollard's p-1; prime counting (sieve prefix / Lehmer / Meissel-Lehmer / Lucy_Hedgehog); nth prime; prime gaps and twin primes; prime factor multiplicities and exponent maps; number of divisors from factorisation; perfect squares and perfect powers; ugly and smooth numbers.
3. **Modular arithmetic.** Modular add / subtract / multiply with negatives; fast exponentiation (recursive / iterative, binary exponentiation); modular inverse by Fermat / extended Euclid; inverses of 1..n in linear time; batch inverses of arbitrary values; Chinese remainder theorem (coprime / non-coprime moduli, Garner); discrete logarithm by baby-step giant-step; multiplicative order and primitive roots; Euler's theorem and exponent reduction for huge powers; Lucas' theorem; Wilson's theorem; quadratic residues and Euler's criterion; modular square roots (Tonelli-Shanks / Cipolla); modular reduction of huge numbers given as strings or digit streams; Montgomery and Barrett reduction; modular division and "is the answer mod p" pitfalls.
4. **Arithmetic functions.** Euler's totient (single value / sieve); Mobius function and Mobius inversion; divisor count and divisor sum functions (sieve / from factorisation); multiplicative functions and the linear sieve; Dirichlet convolution and Dirichlet prefix sums; sum over divisors / multiples (harmonic-series loops); sum of floor division by blocks (n / i has O(sqrt n) values); counting coprime pairs by Mobius; gcd sums; sum of gcd over all pairs (phi-based); perfect, abundant and amicable numbers; sum of digits and digital root.
5. **Combinatorics.** nCr by Pascal's triangle / factorials with inverse factorials / Lucas / multiplicative formula; permutations and arrangements; multinomial coefficients and anagram counts; stars and bars (with lower bounds and upper bounds); Catalan numbers (balanced brackets, binary trees, non-crossing structures, lattice paths under a diagonal); Stirling numbers of the first / second kind; Bell numbers; derangements and rencontres numbers; integer partitions (DP / pentagonal number theorem); compositions; Fibonacci-like counting (Fibonacci / Zeckendorf); Narayana, Motzkin and Schroder numbers; inclusion-exclusion (subset enumeration / over divisors / on bitmasks); Burnside's lemma; Polya enumeration; Gray code (reflected / unranking); ranking and unranking of permutations (factorial number system); ranking and unranking of combinations (combinadic); next permutation / previous permutation; lexicographic enumeration of subsets, combinations and permutations; necklaces and bracelets; Latin squares and magic squares.
6. **Counting techniques.** Rule of sum and product; counting by complement; digit counting (digit DP / by position / numbers with distinct digits); counting up to N in a base; pigeonhole principle (duplicates / prefix-sum remainders); double counting (contribution of each element); counting pairs by hash map of a derived key; symmetry and bijection arguments; invariants and monovariants (parity, coloring); recurrence-relation counting; generating functions (ordinary / exponential, polynomial multiplication); linear recurrences with constant coefficients; characteristic polynomial and closed forms; Berlekamp-Massey; Kitamasa / Fiduccia (nth term in O(k^2 log n)); counting subsets with a property (meet in the middle / subset-sum DP); counting lattice paths with obstacles (DP / reflection principle); counting inversions and permutations by inversions (Mahonian numbers); expected counts by linearity.
7. **Big numbers.** Big integer representation (little-endian digit array, base 10^k); big add / subtract with carry and borrow; schoolbook multiplication; big multiplication by a small number; long division and division by a small number; Karatsuba; FFT / NTT multiplication; big integer comparison and normalisation; big integer powers and factorials; string arithmetic (add / multiply / subtract strings); adding numbers stored in linked lists (reverse / forward with a stack); array-form addition (add k to a digit array); big integer to string and base conversion; square root of a big integer (Newton / digit by digit); big modulo (Horner over digits).
8. **Number representations.** Positional bases and base conversion (any base / bijective base such as spreadsheet columns); two's complement and sign handling; hexadecimal and binary strings; balanced ternary and negabinary; Roman numerals; numbers to English words; fractions and rational arithmetic (normalise by gcd, keep the sign in the numerator); recurring decimals (remainder cycle detection); continued fractions and convergents; Farey sequence and Stern-Brocot tree; floating point pitfalls (non-associativity, epsilon comparison, catastrophic cancellation, integer-valued doubles); fixed point arithmetic; integer square root and cube root (binary search / Newton); rounding modes (floor / ceil / truncate toward zero, division of negatives); Zeckendorf and factorial number systems; Gray code as a representation.
9. **Matrix methods.** Matrix exponentiation for linear recurrences; matrix exponentiation for path counting in a graph (walks of length k); Fibonacci by fast doubling; Fibonacci mod m and the Pisano period; state-vector transitions (companion matrix); matrix power over other semirings (min-plus / max-plus / boolean); Gaussian elimination over the reals (partial pivoting); Gaussian elimination mod p; Gaussian elimination over GF(2) (bitset); determinants (elimination / cofactor / Bareiss); matrix rank; matrix inverse; solving linear systems and Gauss-Jordan; Kirchhoff's matrix-tree theorem; sparse matrix and sparse vector products; transpose, rotation and index algebra.
10. **Probability basics.** Sample space and equally likely outcomes; expected value; linearity of expectation (indicator variables); conditional probability and Bayes' rule; independence; expected value by DP over states (new 21 game / random walk); geometric distribution and expected waiting time (coupon collector); Monte Carlo estimation; Las Vegas vs Monte Carlo algorithms; rejection sampling; weighted random pick (prefix sums + binary search / alias method); uniform shuffle (Fisher-Yates); reservoir sampling (single item / k items; cross-reference Heap and Design); random pick with blacklist; birthday paradox; gambler's ruin and absorbing chains; probability as a modular fraction (p / q mod prime).
11. **Simple identities.** Sum of 1..n; sum of squares and cubes; arithmetic series (sum / nth term / missing term); geometric series (finite / infinite / mod p); telescoping sums; prefix sums and difference arrays as identities; sum of a range by closed form; triangular and pentagonal numbers; powers of two; Josephus problem (simulation / recurrence / closed form); sum of digits and digit patterns; XOR of 1..n; counting by symmetry and parity; completing the square and quadratic roots; AM-GM and Cauchy inequalities for greedy bounds; harmonic number approximations; Sum-of-two-squares and Lagrange's four-square theorem.
12. **Geometry-adjacent integer problems.** Lattice points on a segment (gcd + 1); lattice points inside a polygon (Pick's theorem); shoelace formula (twice the area in integers); gcd on grids (visible points, steps in a line); direction normalisation by gcd (slopes without floating point); collinearity by cross product; Manhattan and Chebyshev distance (rotation by 45 degrees); rectangle overlap and area union; squared distance comparisons (avoid sqrt); Pythagorean triples (Euclid's formula); integer circle points; counting rectangles / squares on a grid; angles between clock hands (rational angles); rotations and reflections of integer points; grid walking with lcm / gcd (laser, mirror, billiard unfolding).
13. **Core implementation patterns.** Integer overflow (check before multiply / widen / saturate); 32-bit and 64-bit limits and the INT_MIN trap (negation, abs, division by -1); 128-bit intermediates (u128 / mulmod by doubling / mulhi); modular arithmetic with negatives (rem_euclid vs %); modulus 10^9+7 and 998244353 constants and why; mulmod without overflow; precomputed factorial and inverse factorial tables; sieve array sizing and memory (bitset, odd-only, segmented); binary search on the answer with a monotone arithmetic predicate; digit-by-digit loops (divide by 10 / carry); epsilon comparisons for floats; integer ceil division and floor division with signs; checked / wrapping / saturating operations in Rust; early exit by square-root bound; cycle detection on number sequences (Floyd / hash set, happy number); iterating divisors in O(sqrt n) pairs.

## Problems in the data

Example problems per group, taken from `content/dsa/problems.json` and `content/dsa/practice.json` (matched by the tags Math, Number Theory,
Combinatorics, Counting, Probability and Statistics, Simulation and the related algorithm tags). The lists are the data's own: `blind75`,
`neetcode150`, `neetcode250`, `all` (the full NeetCode set) and `practice` (the practice tracks). A problem can serve more than one group.

1. **Divisibility and gcd.**
    - LeetCode 1071 Greatest Common Divisor of Strings (easy; neetcode250, all)
    - LeetCode 1979 Find Greatest Common Divisor of Array (easy; practice)
    - LeetCode 2807 Insert Greatest Common Divisors in Linked List (medium; neetcode250, all)
    - LeetCode 2427 Number of Common Factors (easy; practice)
2. **Primes and factorisation.**
    - LeetCode 204 Count Primes (medium; all)
    - LeetCode 2523 Closest Prime Numbers in Range (medium; all)
    - LeetCode 2709 Greatest Common Divisor Traversal (hard; neetcode250, all)
    - LeetCode 2818 Apply Operations to Maximize Score (hard; all)
    - No problem in the data for Miller-Rabin, Pollard's rho or prime counting.
3. **Modular arithmetic.**
    - LeetCode 50 Pow(x, n) (medium; neetcode150, neetcode250, all)
    - LeetCode 372 Super Pow (medium; practice)
    - LeetCode 1922 Count Good Numbers (medium; practice)
    - LeetCode 2514 Count Anagrams (hard; practice)
    - No problem in the data for the Chinese remainder theorem, discrete logarithm, primitive roots, Lucas, Wilson or Tonelli-Shanks.
4. **Arithmetic functions.**
    - LeetCode 2427 Number of Common Factors (easy; practice)
    - LeetCode 3233 Find the Count of Numbers Which Are Not Special (medium; practice)
    - LeetCode 2520 Count the Digits That Divide a Number (easy; practice)
    - No problem in the data for Euler's totient sieve, Mobius, Dirichlet convolution or floor-division blocks.
5. **Combinatorics.**
    - LeetCode 62 Unique Paths (medium; blind75, neetcode150, neetcode250, all)
    - LeetCode 96 Unique Binary Search Trees (medium; all)
    - LeetCode 60 Permutation Sequence (hard; practice)
    - LeetCode 2929 Distribute Candies Among Children II (medium; all)
    - No problem in the data for Bell numbers, derangements, Burnside, Polya or partitions.
6. **Counting techniques.**
    - LeetCode 357 Count Numbers with Unique Digits (medium; practice)
    - LeetCode 2376 Count Special Integers (hard; practice)
    - LeetCode 287 Find the Duplicate Number (medium; neetcode150, neetcode250, all)
    - LeetCode 523 Continuous Subarray Sum (medium; all)
7. **Big numbers.**
    - LeetCode 43 Multiply Strings (medium; neetcode150, neetcode250, all)
    - LeetCode 415 Add Strings (easy; practice)
    - LeetCode 2 Add Two Numbers (medium; neetcode150, neetcode250, all)
    - LeetCode 66 Plus One (easy; neetcode150, neetcode250, all)
    - No problem in the data for Karatsuba or big integer division.
8. **Number representations.**
    - LeetCode 166 Fraction to Recurring Decimal (medium; practice)
    - LeetCode 405 Convert a Number to Hexadecimal (easy; practice)
    - LeetCode 168 Excel Sheet Column Title (easy; neetcode250, all)
    - LeetCode 1780 Check if Number is a Sum of Powers of Three (medium; all)
9. **Matrix methods.**
    - LeetCode 509 Fibonacci Number (easy; practice)
    - LeetCode 1137 N-th Tribonacci Number (easy; neetcode250, all)
    - LeetCode 70 Climbing Stairs (easy; blind75, neetcode150, neetcode250, all)
    - LeetCode 311 Sparse Matrix Multiplication (medium; all)
    - No problem in the data for Gaussian elimination, determinants or matrix exponentiation by name (the listed ones are its simplest uses).
10. **Probability basics.**
    - LeetCode 837 New 21 Game (medium; all)
    - LeetCode 382 Linked List Random Node (medium; practice)
    - LeetCode 384 Shuffle an Array (medium; practice)
    - LeetCode 528 Random Pick with Weight (medium; all)
11. **Simple identities.**
    - LeetCode 1823 Find the Winner of the Circular Game (medium; all)
    - LeetCode 268 Missing Number (easy; blind75, neetcode150, neetcode250, all)
    - LeetCode 441 Arranging Coins (easy; all)
    - LeetCode 1685 Sum of Absolute Differences in a Sorted Array (medium; all)
12. **Geometry-adjacent integer problems.**
    - LeetCode 149 Max Points on a Line (hard; all)
    - LeetCode 2280 Minimum Lines to Represent a Line Chart (medium; practice)
    - LeetCode 223 Rectangle Area (medium; practice)
    - LeetCode 939 Minimum Area Rectangle (medium; practice)
    - No problem in the data for Pick's theorem or lattice-point counting.
13. **Core implementation patterns.**
    - LeetCode 7 Reverse Integer (medium; neetcode150, neetcode250, all)
    - LeetCode 29 Divide Two Integers (medium; practice)
    - LeetCode 69 Sqrt(x) (easy; neetcode250, all)
    - LeetCode 50 Pow(x, n) (medium; neetcode150, neetcode250, all)
