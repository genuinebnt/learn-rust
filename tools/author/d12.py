import textwrap

from author import T, write_track

P = []

# ---------------------------------------------------------------- 1-D basics (easy)

P.append(dict(
    slug="fibonacci", title="Fibonacci (memo vs table)", level="easy", stage="1d-basics", tags=["memoization", "tabulation"],
    companies=["Amazon", "Apple", "Google", "Microsoft", "Adobe"],
    teaches=["The same recurrence written top-down (recursion + a memo) and bottom-up (a loop over a table).",
             "Two rolling variables replace the whole table when a state only looks back two steps."],
    statement="""
        `F(0) = 0`, `F(1) = 1`, and `F(n) = F(n - 1) + F(n - 2)`.

        Write it twice:
        - `fib_memo`: recursion that remembers every `F(k)` it has already computed;
        - `fib_table`: a loop that builds the answers from `F(0)` upwards.

        `n` goes up to 93, the largest `F(n)` that fits in a `u64`. Plain recursion without a memo
        takes far too long there.
    """,
    examples=[("n = 10", "55"), ("n = 0", "0")],
    constraints=["0 ≤ n ≤ 93"],
    starter="""
        /// F(n), top-down: recursion plus a memo.
        pub fn fib_memo(n: u32) -> u64 {
            todo!()
        }

        /// F(n), bottom-up: a loop from F(0) upwards.
        pub fn fib_table(n: u32) -> u64 {
            todo!()
        }
    """,
    solution="""
        /// F(n), top-down: recursion plus a memo.
        pub fn fib_memo(n: u32) -> u64 {
            fn go(k: usize, memo: &mut [Option<u64>]) -> u64 {
                if k < 2 {
                    return k as u64;
                }
                if let Some(v) = memo[k] {
                    return v;
                }
                let v = go(k - 1, memo) + go(k - 2, memo);
                memo[k] = Some(v);
                v
            }
            let n = n as usize;
            go(n, &mut vec![None; n + 1])
        }

        /// F(n), bottom-up: a loop from F(0) upwards.
        pub fn fib_table(n: u32) -> u64 {
            if n == 0 {
                return 0;
            }
            // After k rounds, cur = F(k + 1); stopping at F(n) keeps F(93) from computing F(94).
            let (mut prev, mut cur) = (0u64, 1u64);
            for _ in 1..n {
                (prev, cur) = (cur, prev + cur);
            }
            cur
        }
    """,
    visible=[
        T("ten", "n = 10", "(fib_memo(10), fib_table(10))", "(55, 55)"),
        T("zero", "n = 0", "(fib_memo(0), fib_table(0))", "(0, 0)"),
        T("one", "n = 1", "(fib_memo(1), fib_table(1))", "(1, 1)"),
        T("leetcode_two", "n = 2", "(fib_memo(2), fib_table(2))", "(1, 1)"),
        T("leetcode_three", "n = 3", "(fib_memo(3), fib_table(3))", "(2, 2)"),
        T("leetcode_four", "n = 4", "(fib_memo(4), fib_table(4))", "(3, 3)"),
        T("fifty", "n = 50", "(fib_memo(50), fib_table(50))", "(12_586_269_025, 12_586_269_025)"),
    ],
    hidden=[
        T("zero", "n = 0", "(fib_memo(0), fib_table(0))", "(0, 0)"),
        T("one", "n = 1", "(fib_memo(1), fib_table(1))", "(1, 1)"),
        T("five", "n = 5", "(fib_memo(5), fib_table(5))", "(5, 5)"),
        T("thirty", "n = 30", "(fib_memo(30), fib_table(30))", "(832_040, 832_040)"),
        T("past_i32", "n = 47", "(fib_memo(47), fib_table(47))", "(2_971_215_073, 2_971_215_073)"),
        T("ninety", "n = 90", "(fib_memo(90), fib_table(90))", "(2_880_067_194_370_816_120, 2_880_067_194_370_816_120)"),
        T("largest_that_fits", "n = 93", "(fib_memo(93), fib_table(93))", "(12_200_160_415_121_876_738, 12_200_160_415_121_876_738)"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1201);
            for _ in 0..300 {
                let n = rng.below(94) as u32;
                let (mut a, mut b) = (0u128, 1u128);
                for _ in 0..n {
                    (a, b) = (b, a + b);
                }
                let want = a as u64;
                check!(format!("n = {n}"), (fib_memo(n), fib_table(n)), (want, want));
            }
        }

        #[test]
        fn every_n_satisfies_the_recurrence() {
            for n in 2..=93u32 {
                check!(format!("n = {n}"), fib_memo(n), fib_memo(n - 1) + fib_memo(n - 2));
                check!(format!("n = {n}"), fib_table(n), fib_table(n - 1) + fib_table(n - 2));
            }
        }

        #[test]
        fn scale_memo_at_93() {
            // Without the memo this is about 10¹⁹ calls.
            check!("n = 93, called 1000 times", (0..1000).map(|_| fib_memo(93)).max(), Some(12_200_160_415_121_876_738));
        }
        """,
    ],
    wrong=dict(
        memo_never_written="""
            /// F(n), top-down: recursion plus a memo.
            pub fn fib_memo(n: u32) -> u64 {
                fn go(k: usize, memo: &mut [Option<u64>]) -> u64 {
                    if k < 2 {
                        return k as u64;
                    }
                    if let Some(v) = memo[k] {
                        return v;
                    }
                    go(k - 1, memo) + go(k - 2, memo)
                }
                let n = n as usize;
                go(n, &mut vec![None; n + 1])
            }

            /// F(n), bottom-up: a loop from F(0) upwards.
            pub fn fib_table(n: u32) -> u64 {
                let (mut a, mut b) = (0u64, 1u64);
                for _ in 0..n {
                    let next = a.wrapping_add(b);
                    a = b;
                    b = next;
                }
                a
            }
        """,
        one_step_too_far="""
            /// F(n), top-down: recursion plus a memo.
            pub fn fib_memo(n: u32) -> u64 {
                fib_table(n)
            }

            /// F(n), bottom-up: a loop from F(0) upwards.
            pub fn fib_table(n: u32) -> u64 {
                let (mut a, mut b) = (0u64, 1u64);
                for _ in 0..n {
                    (a, b) = (b, a + b);
                }
                a
            }
        """,
        starts_at_one="""
            /// F(n), top-down: recursion plus a memo.
            pub fn fib_memo(n: u32) -> u64 {
                fib_table(n)
            }

            /// F(n), bottom-up: a loop from F(0) upwards.
            pub fn fib_table(n: u32) -> u64 {
                let (mut prev, mut cur) = (1u64, 1u64);
                for _ in 1..n.min(92) {
                    (prev, cur) = (cur, prev + cur);
                }
                cur
            }
        """,
    ),
    hints=[("approach", "Top-down: before recursing, look `k` up in a `Vec<Option<u64>>`; store the result after. Bottom-up: start from F(0) and F(1) and add forwards."),
           ("rust", "A nested `fn go(k: usize, memo: &mut [Option<u64>]) -> u64` keeps the memo out of the public signature. `(prev, cur) = (cur, prev + cur)` is a destructuring assignment."),
           ("edge case", "F(94) overflows a `u64`. A loop that always computes one value ahead panics at n = 93 in a debug build.")],
    notes=("Both versions compute each F(k) once. The memo version stores the answers on the way back up the recursion; the table version fills them from the bottom, and since each value needs only the two before it, two variables are enough.",
           "O(n)", "O(n) for the memo (and its recursion), O(1) for the rolling loop"),
    follow_up="How would you compute F(n) mod m for n = 10¹⁸? (Matrix exponentiation or fast doubling, O(log n).)",
    related=["D11", "L6"],
))

P.append(dict(
    slug="climbing-stairs", title="Climbing stairs", level="easy", stage="1d-basics", tags=["1-D DP", "Blind 75"],
    companies=["Amazon", "Apple", "Google", "Microsoft", "Adobe", "Bloomberg", "Uber"],
    teaches=["Turning \"how many ways\" into a recurrence over the last step taken.", "Rolling two variables instead of a table."],
    statement="""
        You climb a staircase of `n` steps, taking 1 or 2 steps at a time. Return how many different
        sequences of moves reach the top.
    """,
    examples=[("n = 3", "3 (1+1+1, 1+2, 2+1)")],
    constraints=["1 ≤ n ≤ 90"],
    starter="""
        pub fn climb_stairs(n: u32) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn climb_stairs(n: u32) -> u64 {
            // ways(i) = ways(i - 1) + ways(i - 2): the last move was a 1 or a 2.
            let (mut two_back, mut one_back) = (1u64, 1u64); // ways(0), ways(1)
            for _ in 1..n {
                (two_back, one_back) = (one_back, two_back + one_back);
            }
            one_back
        }
    """,
    visible=[
        T("leetcode_two", "n = 2", "climb_stairs(2)", "2"),
        T("leetcode_three", "n = 3", "climb_stairs(3)", "3"),
        T("one_step", "n = 1", "climb_stairs(1)", "1"),
        T("four", "n = 4", "climb_stairs(4)", "5"),
        T("order_matters", "n = 5 (1+2 and 2+1 count separately)", "climb_stairs(5)", "8"),
    ],
    hidden=[
        T("one_step", "n = 1", "climb_stairs(1)", "1"),
        T("ten", "n = 10", "climb_stairs(10)", "89"),
        T("twenty", "n = 20", "climb_stairs(20)", "10_946"),
        T("leetcode_max", "n = 45", "climb_stairs(45)", "1_836_311_903"),
        T("past_u32", "n = 50", "climb_stairs(50)", "20_365_011_074"),
        T("eighty", "n = 80", "climb_stairs(80)", "37_889_062_373_143_906"),
        T("largest", "n = 90", "climb_stairs(90)", "4_660_046_610_375_530_309"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn ways(n: u32) -> u64 {
                if n <= 1 { 1 } else { ways(n - 1) + ways(n - 2) }
            }
            let mut rng = anneal_prelude::Rng::new(1202);
            for _ in 0..300 {
                let n = rng.int(1, 22) as u32;
                check!(format!("n = {n}"), climb_stairs(n), ways(n));
            }
        }

        #[test]
        fn scale_90_many_times() {
            // Plain recursion is about 10¹⁹ calls here.
            check!("n = 90, called 1000 times", (0..1000).map(|_| climb_stairs(90)).min(), Some(4_660_046_610_375_530_309));
        }
        """,
    ],
    wrong=dict(
        plain_recursion="""
            pub fn climb_stairs(n: u32) -> u64 {
                if n <= 1 { 1 } else { climb_stairs(n - 1) + climb_stairs(n - 2) }
            }
        """,
        fibonacci_off_by_one="""
            pub fn climb_stairs(n: u32) -> u64 {
                let (mut a, mut b) = (0u64, 1u64);
                for _ in 0..n {
                    (a, b) = (b, a + b);
                }
                a
            }
        """,
    ),
    hints=[("approach", "The last move onto step `n` came from step `n - 1` or step `n - 2`, so ways(n) = ways(n - 1) + ways(n - 2)."),
           ("rust", "Only the previous two values matter: keep them in two `u64`s and update with `(a, b) = (b, a + b)`."),
           ("edge case", "ways(0) = 1 (do nothing) and ways(1) = 1 are the seeds; n = 90 needs a `u64`.")],
    notes=("The answer is the Fibonacci sequence shifted by one: ways(n) = F(n + 1). Rolling two values gives O(1) space.", "O(n)", "O(1)"),
    follow_up="What changes if you may take 1, 2 or 3 steps, or any step size from a given set?",
    related=["D11"],
))

P.append(dict(
    slug="min-cost-climbing-stairs", title="Min cost climbing stairs", level="easy", stage="1d-basics", tags=["1-D DP"],
    companies=["Amazon", "Google", "Microsoft", "Adobe"],
    teaches=["The DP state is \"cheapest cost to stand here\"; the answer is a state past the last index.",
             "Widening to `u64` once, at the accumulator."],
    statement="""
        `cost[i]` is what you pay to leave step `i`; from there you climb 1 or 2 steps. You may start
        on step 0 or step 1 for free. The top is just past the last step (index `cost.len()`).
        Return the cheapest total to reach the top.
    """,
    examples=[("cost = [10, 15, 20]", "15 (start on step 1, pay 15, climb 2)")],
    constraints=["0 ≤ cost.len() ≤ 2·10⁵", "0 ≤ cost[i] ≤ 10⁴"],
    starter="""
        pub fn min_cost_climbing_stairs(cost: &[u32]) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn min_cost_climbing_stairs(cost: &[u32]) -> u64 {
            // reach[i] = cheapest way to stand on step i; reach[0] = reach[1] = 0.
            let (mut two_back, mut one_back) = (0u64, 0u64);
            for i in 2..=cost.len() {
                let here = (one_back + cost[i - 1] as u64).min(two_back + cost[i - 2] as u64);
                (two_back, one_back) = (one_back, here);
            }
            one_back
        }
    """,
    visible=[
        T("leetcode_three", "cost = [10, 15, 20]", "min_cost_climbing_stairs(&[10, 15, 20])", "15"),
        T("leetcode_ten", "cost = [1, 100, 1, 1, 1, 100, 1, 1, 100, 1]", "min_cost_climbing_stairs(&[1, 100, 1, 1, 1, 100, 1, 1, 100, 1])", "6"),
        T("empty", "cost = []", "min_cost_climbing_stairs(&[])", "0"),
        T("one_step_is_free", "cost = [5] (start on step 1, which is the top)", "min_cost_climbing_stairs(&[5])", "0"),
        T("two_steps", "cost = [1, 2]", "min_cost_climbing_stairs(&[1, 2])", "1"),
        T("top_is_past_the_end", "cost = [3, 1, 1, 3]", "min_cost_climbing_stairs(&[3, 1, 1, 3])", "2"),
    ],
    hidden=[
        T("empty", "cost = []", "min_cost_climbing_stairs(&[])", "0"),
        T("single", "cost = [9]", "min_cost_climbing_stairs(&[9])", "0"),
        T("zeros", "cost = [0, 0, 0, 0]", "min_cost_climbing_stairs(&[0, 0, 0, 0])", "0"),
        T("start_on_one", "cost = [100, 1, 100]", "min_cost_climbing_stairs(&[100, 1, 100])", "1"),
        T("start_on_zero", "cost = [1, 100, 1, 100]", "min_cost_climbing_stairs(&[1, 100, 1, 100])", "2"),
        T("skip_the_last", "cost = [1, 1, 9]", "min_cost_climbing_stairs(&[1, 1, 9])", "1"),
        T("all_max", "cost = [10000; 6]", "min_cost_climbing_stairs(&[10_000; 6])", "30_000"),
        T("past_u32", "cost = [10000; 1000000]", "min_cost_climbing_stairs(&vec![10_000; 1_000_000])", "5_000_000_000"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn best(cost: &[u32], at: usize) -> u64 {
                if at >= cost.len() { return 0; }
                cost[at] as u64 + best(cost, at + 1).min(best(cost, at + 2))
            }
            let mut rng = anneal_prelude::Rng::new(1203);
            for _ in 0..300 {
                let n = rng.below(16);
                let cost: Vec<u32> = rng.vec(n, 0, 20);
                let want = best(&cost, 0).min(best(&cost, 1));
                check!(format!("cost = {cost:?}"), min_cost_climbing_stairs(&cost), want);
            }
        }

        #[test]
        fn scale_200k() {
            let cost: Vec<u32> = (0..200_000u32).map(|i| (i * 7919) % 10_000).collect();
            check!("cost[i] = (7919·i) % 10000, 200000 steps", min_cost_climbing_stairs(&cost), 427_375_280);
        }
        """,
    ],
    wrong=dict(
        plain_recursion="""
            fn best(cost: &[u32], at: usize) -> u64 {
                if at >= cost.len() { return 0; }
                cost[at] as u64 + best(cost, at + 1).min(best(cost, at + 2))
            }

            pub fn min_cost_climbing_stairs(cost: &[u32]) -> u64 {
                best(cost, 0).min(best(cost, 1))
            }
        """,
        must_start_on_zero="""
            pub fn min_cost_climbing_stairs(cost: &[u32]) -> u64 {
                let (mut two_back, mut one_back) = (0u64, cost.first().map_or(0, |&c| c as u64));
                for i in 2..=cost.len() {
                    let here = (one_back + cost[i - 1] as u64).min(two_back + cost[i - 2] as u64);
                    (two_back, one_back) = (one_back, here);
                }
                if cost.len() < 2 { 0 } else { one_back }
            }
        """,
        top_is_last_step="""
            pub fn min_cost_climbing_stairs(cost: &[u32]) -> u64 {
                let n = cost.len();
                if n < 2 { return 0; }
                let mut pay = vec![0u64; n];
                pay[0] = cost[0] as u64;
                pay[1] = cost[1] as u64;
                for i in 2..n {
                    pay[i] = cost[i] as u64 + pay[i - 1].min(pay[i - 2]);
                }
                pay[n - 1]
            }
        """,
    ),
    hints=[("approach", "Let reach(i) be the cheapest way to stand on step i. reach(0) = reach(1) = 0, and reach(i) = min(reach(i-1) + cost[i-1], reach(i-2) + cost[i-2]). The answer is reach(n)."),
           ("rust", "Keep two `u64`s and convert each cost with `as u64` as you add it."),
           ("edge case", "With 0 or 1 steps you are already at the top: the answer is 0.")],
    notes=("The state is where you stand, and the cost is paid when you leave a step. The top is index n, one past the end, so the loop runs up to n inclusive.", "O(n)", "O(1)"),
    follow_up="How would you also return which steps you stepped on?",
    related=["D11"],
))

P.append(dict(
    slug="pascals-triangle", title="Pascal's triangle", level="easy", stage="1d-basics", tags=["Vec<Vec<_>>", "binomials"],
    companies=["Amazon", "Apple", "Google", "Microsoft", "Adobe", "Bloomberg"],
    teaches=["Each row is built from the previous one: the smallest table DP.", "`windows(2)` sums neighbouring pairs without index arithmetic."],
    statement="""
        Return the first `num_rows` rows of Pascal's triangle. Row 0 is `[1]`; every later row starts
        and ends with 1, and each inner value is the sum of the two values above it.
    """,
    examples=[("num_rows = 4", "[[1], [1, 1], [1, 2, 1], [1, 3, 3, 1]]")],
    constraints=["0 ≤ num_rows ≤ 60"],
    starter="""
        pub fn generate(num_rows: usize) -> Vec<Vec<u64>> {
            todo!()
        }
    """,
    solution="""
        pub fn generate(num_rows: usize) -> Vec<Vec<u64>> {
            let mut rows: Vec<Vec<u64>> = Vec::with_capacity(num_rows);
            for r in 0..num_rows {
                let mut row = Vec::with_capacity(r + 1);
                row.push(1);
                if let Some(above) = rows.last() {
                    row.extend(above.windows(2).map(|w| w[0] + w[1]));
                    row.push(1);
                }
                rows.push(row);
            }
            rows
        }
    """,
    visible=[
        T("leetcode_five", "num_rows = 5", "generate(5)", "vec![vec![1], vec![1, 1], vec![1, 2, 1], vec![1, 3, 3, 1], vec![1, 4, 6, 4, 1]]"),
        T("leetcode_one", "num_rows = 1", "generate(1)", "vec![vec![1u64]]"),
        T("zero_rows", "num_rows = 0", "generate(0)", "Vec::<Vec<u64>>::new()"),
        T("two_rows", "num_rows = 2", "generate(2)", "vec![vec![1], vec![1, 1]]"),
        T("row_six", "num_rows = 7, last row", "generate(7).pop()", "Some(vec![1, 6, 15, 20, 15, 6, 1])"),
    ],
    hidden=[
        T("zero_rows", "num_rows = 0", "generate(0)", "Vec::<Vec<u64>>::new()"),
        T("one_row", "num_rows = 1", "generate(1)", "vec![vec![1u64]]"),
        T("three_rows", "num_rows = 3", "generate(3)", "vec![vec![1], vec![1, 1], vec![1, 2, 1]]"),
        T("row_lengths", "num_rows = 10, row lengths", "generate(10).iter().map(|r| r.len()).collect::<Vec<_>>()", "(1..=10).collect::<Vec<usize>>()"),
        T("leetcode_max_middle", "num_rows = 30, middle of the last row", "generate(30)[29][14]", "77_558_760"),
        T("past_factorials", "num_rows = 22, middle of the last row", "generate(22)[21][10]", "352_716"),
        T("past_u32", "num_rows = 60, middle of the last row", "generate(60)[59][29]", "59_132_290_782_430_712"),
        T("last_row_sum", "num_rows = 60, sum of the last row", "generate(60)[59].iter().sum::<u64>()", "1u64 << 59"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn choose(n: u64, k: u64) -> u64 {
                let mut c: u128 = 1;
                for i in 0..k {
                    c = c * (n - i) as u128 / (i + 1) as u128;
                }
                c as u64
            }
            let mut rng = anneal_prelude::Rng::new(1204);
            for _ in 0..200 {
                let n = rng.below(61);
                let want: Vec<Vec<u64>> = (0..n as u64).map(|r| (0..=r).map(|k| choose(r, k)).collect()).collect();
                check!(format!("num_rows = {n}"), generate(n), want);
            }
        }
        """,
    ],
    wrong=dict(
        factorials="""
            pub fn generate(num_rows: usize) -> Vec<Vec<u64>> {
                let fact = |n: u64| (1..=n).product::<u64>();
                (0..num_rows as u64).map(|r| (0..=r).map(|k| fact(r) / (fact(k) * fact(r - k))).collect()).collect()
            }
        """,
        one_row_short="""
            pub fn generate(num_rows: usize) -> Vec<Vec<u64>> {
                let mut rows: Vec<Vec<u64>> = vec![vec![1]];
                for r in 1..num_rows.saturating_sub(1).max(1) {
                    let above = &rows[r - 1];
                    let mut row = vec![1];
                    row.extend(above.windows(2).map(|w| w[0] + w[1]));
                    row.push(1);
                    rows.push(row);
                }
                rows
            }
        """,
    ),
    hints=[("approach", "Build row r from row r - 1: a 1, then the sums of each neighbouring pair above, then a 1."),
           ("rust", "`above.windows(2).map(|w| w[0] + w[1])` yields the inner values; `rows.last()` is `None` for the first row."),
           ("edge case", "Computing C(n, k) with factorials overflows a `u64` from 21! on; adding neighbours never does for these sizes.")],
    notes=("Each row depends only on the row above, so the triangle is its own DP table. Adding neighbours keeps every intermediate value no bigger than the answer.", "O(n²)", "O(n²) for the output"),
    follow_up="How would you return only row n in O(n) space?",
    related=["D13", "S3"],
))

P.append(dict(
    slug="counting-bits", title="Counting bits", level="easy", stage="1d-basics", tags=["bits", "1-D DP"],
    companies=["Amazon", "Apple", "Microsoft", "Adobe"],
    teaches=["Reusing an earlier answer: `bits(i) = bits(i >> 1) + (i & 1)`.", "Building a `Vec` whose entries read earlier entries."],
    statement="""
        Return a `Vec` of length `n + 1` whose element `i` is the number of 1 bits in the binary form
        of `i`. Do it without counting the bits of each number from scratch.
    """,
    examples=[("n = 5", "[0, 1, 1, 2, 1, 2]")],
    constraints=["0 ≤ n ≤ 10⁶"],
    starter="""
        pub fn count_bits(n: usize) -> Vec<u32> {
            todo!()
        }
    """,
    solution="""
        pub fn count_bits(n: usize) -> Vec<u32> {
            let mut bits = vec![0u32; n + 1];
            for i in 1..=n {
                // i >> 1 drops the lowest bit; add it back.
                bits[i] = bits[i >> 1] + (i & 1) as u32;
            }
            bits
        }
    """,
    visible=[
        T("leetcode_two", "n = 2", "count_bits(2)", "vec![0, 1, 1]"),
        T("leetcode_five", "n = 5", "count_bits(5)", "vec![0, 1, 1, 2, 1, 2]"),
        T("zero", "n = 0", "count_bits(0)", "vec![0]"),
        T("one", "n = 1", "count_bits(1)", "vec![0, 1]"),
        T("up_to_eight", "n = 8", "count_bits(8)", "vec![0, 1, 1, 2, 1, 2, 2, 3, 1]"),
    ],
    hidden=[
        T("zero", "n = 0", "count_bits(0)", "vec![0]"),
        T("one", "n = 1", "count_bits(1)", "vec![0, 1]"),
        T("seven", "n = 7", "count_bits(7)", "vec![0, 1, 1, 2, 1, 2, 2, 3]"),
        T("power_of_two", "n = 16, last value", "count_bits(16)[16]", "1"),
        T("all_ones", "n = 1023, last value", "count_bits(1023)[1023]", "10"),
        T("length", "n = 100, length", "count_bits(100).len()", "101"),
        T("largest", "n = 1000000, last value", "count_bits(1_000_000)[1_000_000]", "7"),
        T("largest_all_ones_below", "n = 1000000, value at 2^19 - 1", "count_bits(1_000_000)[(1 << 19) - 1]", "19"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1205);
            for _ in 0..200 {
                let n = rng.below(300);
                let want: Vec<u32> = (0..=n).map(|i| i.count_ones()).collect();
                check!(format!("n = {n}"), count_bits(n), want);
            }
        }

        #[test]
        fn scale_million() {
            let bits = count_bits(1_000_000);
            let total: u64 = bits.iter().map(|&b| b as u64).sum();
            check!("n = 1000000, total of all counts", (bits.len(), total), (1_000_001, 9_884_999));
        }
        """,
    ],
    wrong=dict(
        previous_plus_one="""
            pub fn count_bits(n: usize) -> Vec<u32> {
                let mut bits = vec![0u32; n + 1];
                for i in 1..=n {
                    bits[i] = if i.is_power_of_two() { 1 } else { bits[i - 1] + 1 };
                }
                bits
            }
        """,
        forgets_low_bit="""
            pub fn count_bits(n: usize) -> Vec<u32> {
                let mut bits = vec![0u32; n + 1];
                for i in 1..=n {
                    bits[i] = bits[i >> 1] + if i == 1 { 1 } else { 0 };
                }
                bits
            }
        """,
        stops_before_n="""
            pub fn count_bits(n: usize) -> Vec<u32> {
                (0..n.max(1)).map(|i| i.count_ones()).collect()
            }
        """,
    ),
    hints=[("approach", "Shifting `i` right by one drops its lowest bit, and `i >> 1 < i`, so its count is already known."),
           ("rust", "`bits[i] = bits[i >> 1] + (i & 1) as u32` fills the `Vec` left to right. `i & (i - 1)` (clear the lowest set bit) works too.")],
    notes=("Every number is a smaller number with one bit appended, so each entry is one lookup and one add.", "O(n)", "O(n) for the output"),
    follow_up="Which other recurrences work here? (`i & (i - 1)` removes the lowest set bit; the highest power of two gives another.)",
    related=["D13"],
))

P.append(dict(
    slug="house-robber", title="House robber", level="medium", stage="1d-basics", tags=["1-D DP", "Blind 75"],
    companies=["Amazon", "Google", "Meta", "Apple", "Microsoft", "Adobe", "Bloomberg", "Uber"],
    teaches=["Take-or-skip: the best up to house i is the better of skipping it or taking it plus the best up to i - 2.",
             "Two rolling totals are the whole table."],
    statement="""
        `nums[i]` is the money in house `i` along a street. You can't rob two neighbouring houses.
        Return the most you can rob.
    """,
    examples=[("nums = [2, 7, 9, 3, 1]", "12 (houses 0, 2 and 4)")],
    constraints=["0 ≤ nums.len() ≤ 10⁶", "0 ≤ nums[i] ≤ 10⁴"],
    starter="""
        pub fn rob(nums: &[u32]) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn rob(nums: &[u32]) -> u64 {
            // best_before: best up to house i - 2; best: best up to house i - 1.
            let (mut best_before, mut best) = (0u64, 0u64);
            for &x in nums {
                (best_before, best) = (best, best.max(best_before + x as u64));
            }
            best
        }
    """,
    visible=[
        T("leetcode_four", "nums = [1, 2, 3, 1]", "rob(&[1, 2, 3, 1])", "4"),
        T("leetcode_five", "nums = [2, 7, 9, 3, 1]", "rob(&[2, 7, 9, 3, 1])", "12"),
        T("empty", "nums = []", "rob(&[])", "0"),
        T("single", "nums = [5]", "rob(&[5])", "5"),
        T("not_every_other_house", "nums = [2, 1, 1, 2]", "rob(&[2, 1, 1, 2])", "4"),
    ],
    hidden=[
        T("empty", "nums = []", "rob(&[])", "0"),
        T("single", "nums = [7]", "rob(&[7])", "7"),
        T("two_pick_larger", "nums = [2, 1]", "rob(&[2, 1])", "2"),
        T("gap_of_two", "nums = [5, 1, 1, 5]", "rob(&[5, 1, 1, 5])", "10"),
        T("zeros", "nums = [0, 0, 0]", "rob(&[0, 0, 0])", "0"),
        T("middle_wins", "nums = [1, 3, 1]", "rob(&[1, 3, 1])", "3"),
        T("mixed", "nums = [4, 1, 2, 7, 5, 3, 1]", "rob(&[4, 1, 2, 7, 5, 3, 1])", "14"),
        T("past_u32", "nums = [10000; 1000000]", "rob(&vec![10_000; 1_000_000])", "5_000_000_000"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1206);
            for _ in 0..300 {
                let n = rng.below(13);
                let nums: Vec<u32> = rng.vec(n, 0, 30);
                let mut want = 0u64;
                for mask in 0u32..(1 << n) {
                    if mask & (mask >> 1) == 0 {
                        want = want.max((0..n).filter(|&i| mask >> i & 1 == 1).map(|i| nums[i] as u64).sum());
                    }
                }
                check!(format!("nums = {nums:?}"), rob(&nums), want);
            }
        }

        #[test]
        fn scale_200k() {
            let nums: Vec<u32> = (0..200_000u32).map(|i| (i * 37) % 1000).collect();
            check!("nums[i] = (37·i) % 1000, 200000 houses", rob(&nums), 51_666_800);
        }
        """,
    ],
    wrong=dict(
        plain_recursion="""
            fn best(nums: &[u32]) -> u64 {
                match nums {
                    [] => 0,
                    [x, rest @ ..] => best(rest).max(*x as u64 + best(rest.get(1..).unwrap_or(&[]))),
                }
            }

            pub fn rob(nums: &[u32]) -> u64 {
                best(nums)
            }
        """,
        evens_or_odds="""
            pub fn rob(nums: &[u32]) -> u64 {
                let even: u64 = nums.iter().step_by(2).map(|&x| x as u64).sum();
                let odd: u64 = nums.iter().skip(1).step_by(2).map(|&x| x as u64).sum();
                even.max(odd)
            }
        """,
    ),
    hints=[("approach", "At house i you either skip it (keep the best up to i - 1) or rob it (its money plus the best up to i - 2)."),
           ("rust", "Two `u64`s, `best_before` and `best`, updated with a destructuring assignment in one `for &x in nums` loop."),
           ("edge case", "The best plan can skip two houses in a row, so \"all even or all odd houses\" is not enough: [2, 1, 1, 2] → 4.")],
    notes=("best(i) = max(best(i - 1), best(i - 2) + nums[i]). Only the last two values are live, so the table collapses to two variables.", "O(n)", "O(1)"),
    follow_up="How would you return which houses to rob, not just the total?",
    related=["D11"],
))

P.append(dict(
    slug="house-robber-ii", title="House robber II", level="medium", stage="1d-basics", tags=["1-D DP", "Blind 75"],
    companies=["Amazon", "Google", "Meta", "Microsoft", "Adobe", "Bloomberg"],
    teaches=["Breaking a cycle by solving two straight lines: without the first house and without the last.",
             "Reusing a helper over subslices (`&nums[1..]`, `&nums[..n - 1]`)."],
    statement="""
        Same as House robber, but the houses stand in a circle: the first and last houses are
        neighbours. Return the most you can rob without taking two neighbours.
    """,
    examples=[("nums = [2, 3, 2]", "3 (houses 0 and 2 are neighbours)")],
    constraints=["0 ≤ nums.len() ≤ 10⁶", "0 ≤ nums[i] ≤ 10⁴"],
    starter="""
        pub fn rob(nums: &[u32]) -> u64 {
            todo!()
        }
    """,
    solution="""
        fn rob_line(nums: &[u32]) -> u64 {
            let (mut best_before, mut best) = (0u64, 0u64);
            for &x in nums {
                (best_before, best) = (best, best.max(best_before + x as u64));
            }
            best
        }

        pub fn rob(nums: &[u32]) -> u64 {
            match nums {
                [] => 0,
                [only] => *only as u64,
                // The first and last house can't both be robbed: drop one or the other.
                _ => rob_line(&nums[1..]).max(rob_line(&nums[..nums.len() - 1])),
            }
        }
    """,
    visible=[
        T("leetcode_three", "nums = [2, 3, 2]", "rob(&[2, 3, 2])", "3"),
        T("leetcode_four", "nums = [1, 2, 3, 1]", "rob(&[1, 2, 3, 1])", "4"),
        T("leetcode_one_two_three", "nums = [1, 2, 3]", "rob(&[1, 2, 3])", "3"),
        T("empty", "nums = []", "rob(&[])", "0"),
        T("single", "nums = [5]", "rob(&[5])", "5"),
        T("ends_are_neighbours", "nums = [5, 1, 1, 5]", "rob(&[5, 1, 1, 5])", "6"),
    ],
    hidden=[
        T("empty", "nums = []", "rob(&[])", "0"),
        T("single", "nums = [7]", "rob(&[7])", "7"),
        T("two", "nums = [2, 1]", "rob(&[2, 1])", "2"),
        T("zeros", "nums = [0, 0, 0]", "rob(&[0, 0, 0])", "0"),
        T("five_equal", "nums = [10000; 5]", "rob(&[10_000; 5])", "20_000"),
        T("line_answer_uses_both_ends", "nums = [2, 7, 9, 3, 1]", "rob(&[2, 7, 9, 3, 1])", "11"),
        T("skip_two", "nums = [2, 1, 1, 2]", "rob(&[2, 1, 1, 2])", "3"),
        T("mixed", "nums = [4, 1, 2, 7, 5, 3, 1]", "rob(&[4, 1, 2, 7, 5, 3, 1])", "14"),
        T("past_u32", "nums = [10000; 1000000]", "rob(&vec![10_000; 1_000_000])", "5_000_000_000"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1207);
            for _ in 0..300 {
                let n = rng.below(13);
                let nums: Vec<u32> = rng.vec(n, 0, 30);
                let mut want = 0u64;
                for mask in 0u32..(1 << n) {
                    let wraps = n > 1 && mask & 1 == 1 && mask >> (n - 1) & 1 == 1;
                    if mask & (mask >> 1) == 0 && !wraps {
                        want = want.max((0..n).filter(|&i| mask >> i & 1 == 1).map(|i| nums[i] as u64).sum());
                    }
                }
                check!(format!("nums = {nums:?}"), rob(&nums), want);
            }
        }

        #[test]
        fn scale_200k() {
            let mut nums: Vec<u32> = (0..200_000u32).map(|i| (i * 37) % 1000).collect();
            nums[0] = 10_000;
            nums[199_999] = 10_000;
            check!("nums[i] = (37·i) % 1000 with 10000 at both ends, 200000 houses", rob(&nums), 51_676_282);
        }
        """,
    ],
    wrong=dict(
        ignores_the_circle="""
            pub fn rob(nums: &[u32]) -> u64 {
                let (mut best_before, mut best) = (0u64, 0u64);
                for &x in nums {
                    (best_before, best) = (best, best.max(best_before + x as u64));
                }
                best
            }
        """,
        forgets_single_house="""
            fn rob_line(nums: &[u32]) -> u64 {
                let (mut best_before, mut best) = (0u64, 0u64);
                for &x in nums {
                    (best_before, best) = (best, best.max(best_before + x as u64));
                }
                best
            }

            pub fn rob(nums: &[u32]) -> u64 {
                if nums.is_empty() {
                    return 0;
                }
                rob_line(&nums[1..]).max(rob_line(&nums[..nums.len() - 1]))
            }
        """,
        drops_both_ends="""
            fn rob_line(nums: &[u32]) -> u64 {
                let (mut best_before, mut best) = (0u64, 0u64);
                for &x in nums {
                    (best_before, best) = (best, best.max(best_before + x as u64));
                }
                best
            }

            pub fn rob(nums: &[u32]) -> u64 {
                match nums {
                    [] => 0,
                    [only] => *only as u64,
                    [_, mid @ .., _] => rob_line(mid).max(nums[0] as u64),
                }
            }
        """,
    ),
    hints=[("approach", "Any valid plan skips the first house or skips the last one. Solve the straight street twice and take the better."),
           ("rust", "Write `rob_line(&[u32]) -> u64` and call it on `&nums[1..]` and `&nums[..n - 1]`; a slice pattern handles the short cases."),
           ("edge case", "One house: `nums[1..]` and `nums[..0]` are both empty, but the single house can still be robbed.")],
    notes=("The circle only forbids taking both house 0 and house n - 1, so the answer is the better of the line without house 0 and the line without house n - 1.", "O(n)", "O(1)"),
    follow_up="How would you solve it if the street were a tree instead of a circle? (That is House robber III, at the end of this track.)",
    related=["D11"],
))

# ---------------------------------------------------------------- 1-D choices (medium)

P.append(dict(
    slug="decode-ways", title="Decode ways", level="medium", stage="1d-choices", tags=["1-D DP", "as_bytes", "Blind 75"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "Uber", "Bloomberg", "Salesforce"],
    teaches=["A choice of one or two characters per step: the climbing-stairs recurrence with conditions.",
             "Working on `as_bytes()` and comparing against byte literals like `b'0'`."],
    statement="""
        A message of letters was encoded as digits with `A → 1`, `B → 2`, …, `Z → 26`, and the
        separators were lost. Return how many ways the digit string `s` can be decoded.

        A code never starts with `0`: `"06"` is not a valid code for `F`, and `"0"` on its own decodes
        to nothing.
    """,
    examples=[("s = \"226\"", "3 (\"2 2 6\", \"22 6\", \"2 26\")"), ("s = \"06\"", "0")],
    constraints=["1 ≤ s.len() ≤ 100", "s holds only the digits 0–9", "the answer fits in a u64"],
    starter="""
        pub fn num_decodings(s: &str) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn num_decodings(s: &str) -> u64 {
            let d = s.as_bytes();
            // ways(i) = decodings of the first i digits; keep ways(i - 2) and ways(i - 1).
            let (mut two_back, mut one_back) = (0u64, 1u64);
            for i in 0..d.len() {
                let mut here = 0;
                if d[i] != b'0' {
                    here += one_back; // d[i] alone is a letter
                }
                if i > 0 && (d[i - 1] == b'1' || (d[i - 1] == b'2' && d[i] <= b'6')) {
                    here += two_back; // d[i - 1..=i] is 10..=26
                }
                (two_back, one_back) = (one_back, here);
            }
            one_back
        }
    """,
    visible=[
        T("leetcode_twelve", "s = \"12\"", "num_decodings(\"12\")", "2"),
        T("leetcode_two_two_six", "s = \"226\"", "num_decodings(\"226\")", "3"),
        T("leetcode_leading_zero", "s = \"06\"", "num_decodings(\"06\")", "0"),
        T("single_zero", "s = \"0\"", "num_decodings(\"0\")", "0"),
        T("single_digit", "s = \"1\"", "num_decodings(\"1\")", "1"),
        T("ten_only_as_a_pair", "s = \"10\"", "num_decodings(\"10\")", "1"),
        T("above_twenty_six", "s = \"27\"", "num_decodings(\"27\")", "1"),
    ],
    hidden=[
        T("single_zero", "s = \"0\"", "num_decodings(\"0\")", "0"),
        T("double_zero", "s = \"100\"", "num_decodings(\"100\")", "0"),
        T("zero_in_the_middle", "s = \"101\"", "num_decodings(\"101\")", "1"),
        T("thirty", "s = \"230\"", "num_decodings(\"230\")", "0"),
        T("thirty_first", "s = \"301\"", "num_decodings(\"301\")", "0"),
        T("leetcode_11106", "s = \"11106\"", "num_decodings(\"11106\")", "2"),
        T("ten_ones", "s = \"1111111111\"", "num_decodings(\"1111111111\")", "89"),
        T("mixed", "s = \"2611055971756562\"", "num_decodings(\"2611055971756562\")", "4"),
        T("tens_only", "s = \"1010…10\" (100 digits)", "num_decodings(&\"10\".repeat(50))", "1"),
        T("twenty_sevens", "s = \"2727…27\" (100 digits)", "num_decodings(&\"27\".repeat(50))", "1"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn count(d: &[u8]) -> u64 {
                if d.is_empty() {
                    return 1;
                }
                let mut n = 0;
                if d[0] != b'0' {
                    n += count(&d[1..]);
                    if d.len() >= 2 && (d[0] - b'0') * 10 + (d[1] - b'0') <= 26 {
                        n += count(&d[2..]);
                    }
                }
                n
            }
            let mut rng = anneal_prelude::Rng::new(1208);
            for _ in 0..400 {
                let len = rng.int(1, 14) as usize;
                let s = rng.string(len, "0011122223456789");
                check!(format!("s = {s:?}"), num_decodings(&s), count(s.as_bytes()));
            }
        }

        #[test]
        fn scale_ninety_ones() {
            // Plain recursion branches twice per digit here: about 10¹⁹ calls.
            let s = "1".repeat(90);
            check!("s = \\"111…1\\" (90 ones)", num_decodings(&s), 4_660_046_610_375_530_309);
        }
        """,
    ],
    wrong=dict(
        plain_recursion="""
            fn count(d: &[u8]) -> u64 {
                if d.is_empty() {
                    return 1;
                }
                let mut n = 0;
                if d[0] != b'0' {
                    n += count(&d[1..]);
                    if d.len() >= 2 && (d[0] - b'0') * 10 + (d[1] - b'0') <= 26 {
                        n += count(&d[2..]);
                    }
                }
                n
            }

            pub fn num_decodings(s: &str) -> u64 {
                count(s.as_bytes())
            }
        """,
        zero_is_a_letter="""
            pub fn num_decodings(s: &str) -> u64 {
                let d = s.as_bytes();
                let (mut two_back, mut one_back) = (0u64, 1u64);
                for i in 0..d.len() {
                    let mut here = one_back;
                    if i > 0 && (d[i - 1] == b'1' || (d[i - 1] == b'2' && d[i] <= b'6')) {
                        here += two_back;
                    }
                    (two_back, one_back) = (one_back, here);
                }
                one_back
            }
        """,
        pair_with_leading_zero="""
            pub fn num_decodings(s: &str) -> u64 {
                let d = s.as_bytes();
                let (mut two_back, mut one_back) = (0u64, 1u64);
                for i in 0..d.len() {
                    let mut here = 0;
                    if d[i] != b'0' {
                        here += one_back;
                    }
                    if i > 0 && (1..=26).contains(&((d[i - 1] - b'0') * 10 + (d[i] - b'0'))) {
                        here += two_back;
                    }
                    (two_back, one_back) = (one_back, here);
                }
                one_back
            }
        """,
    ),
    hints=[("approach", "Let ways(i) count decodings of the first i digits. Digit i on its own adds ways(i - 1) if it isn't '0'; digits i - 1 and i together add ways(i - 2) if they form 10..=26."),
           ("rust", "Walk `s.as_bytes()` and compare with byte literals (`b'0'`, `b'2'`, `b'6'`). Two rolling `u64`s are enough."),
           ("edge case", "\"06\" is not a code, \"10\" and \"20\" only decode as pairs, and \"30\" makes the whole string undecodable.")],
    notes=("It is climbing stairs where each step of 1 or 2 digits is allowed only if those digits form a letter. ways(0) = 1 seeds the empty prefix.", "O(n)", "O(1)"),
    follow_up="How does the recurrence change if `*` may stand for any digit 1–9 (LeetCode 639)?",
    related=["D11", "S2"],
))

P.append(dict(
    slug="delete-and-earn", title="Delete and earn", level="medium", stage="1d-choices", tags=["1-D DP", "counting"],
    companies=["Amazon", "Google", "Microsoft", "Goldman Sachs"],
    teaches=["Reducing a problem to one you know: total points per value, then House robber over the values.",
             "A counting `Vec` indexed by value instead of sorting."],
    statement="""
        Each move, pick a number `x` from `nums`, earn `x` points, and delete every `x - 1` and
        `x + 1` from `nums`. Picking `x` again later earns `x` again. Return the most points you
        can earn.
    """,
    examples=[("nums = [2, 2, 3, 3, 3, 4]", "9 (take the three 3s; every 2 and 4 is deleted)")],
    constraints=["0 ≤ nums.len() ≤ 2·10⁵", "1 ≤ nums[i] ≤ 10⁵"],
    starter="""
        pub fn delete_and_earn(nums: &[u32]) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn delete_and_earn(nums: &[u32]) -> u64 {
            let Some(&max) = nums.iter().max() else {
                return 0;
            };
            // points[v] = what taking every copy of v earns.
            let mut points = vec![0u64; max as usize + 1];
            for &x in nums {
                points[x as usize] += x as u64;
            }
            // House robber over the values: v and v + 1 are neighbours.
            let (mut before, mut best) = (0u64, 0u64);
            for &p in &points {
                (before, best) = (best, best.max(before + p));
            }
            best
        }
    """,
    visible=[
        T("leetcode_three_values", "nums = [3, 4, 2]", "delete_and_earn(&[3, 4, 2])", "6"),
        T("leetcode_repeats", "nums = [2, 2, 3, 3, 3, 4]", "delete_and_earn(&[2, 2, 3, 3, 3, 4])", "9"),
        T("empty", "nums = []", "delete_and_earn(&[])", "0"),
        T("single", "nums = [5]", "delete_and_earn(&[5])", "5"),
        T("copies_all_count", "nums = [1, 1, 1]", "delete_and_earn(&[1, 1, 1])", "3"),
        T("gaps_are_free", "nums = [1, 3]", "delete_and_earn(&[1, 3])", "4"),
    ],
    hidden=[
        T("empty", "nums = []", "delete_and_earn(&[])", "0"),
        T("single", "nums = [5]", "delete_and_earn(&[5])", "5"),
        T("run", "nums = [1, 2, 3]", "delete_and_earn(&[1, 2, 3])", "4"),
        T("largest_values", "nums = [100000, 99999]", "delete_and_earn(&[100_000, 99_999])", "100_000"),
        T("unsorted_repeats", "nums = [3, 3, 3, 4, 2]", "delete_and_earn(&[3, 3, 3, 4, 2])", "9"),
        T("mixed_ten", "nums = [8, 10, 4, 9, 1, 3, 5, 9, 4, 10]", "delete_and_earn(&[8, 10, 4, 9, 1, 3, 5, 9, 4, 10])", "37"),
        T("mixed_ten_again", "nums = [1, 6, 3, 3, 8, 4, 8, 10, 1, 3]", "delete_and_earn(&[1, 6, 3, 3, 8, 4, 8, 10, 1, 3])", "43"),
        T("past_u32", "nums = [100000; 200000]", "delete_and_earn(&vec![100_000; 200_000])", "20_000_000_000"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1209);
            for _ in 0..300 {
                let n = rng.below(12);
                let nums: Vec<u32> = rng.vec(n, 1, 9);
                let mut want = 0u64;
                // Choose a set of values with no two consecutive; take every copy of each.
                for mask in 0u32..(1 << 10) {
                    if mask & (mask >> 1) == 0 {
                        let earned = nums.iter().filter(|&&x| mask >> x & 1 == 1).map(|&x| x as u64).sum();
                        want = want.max(earned);
                    }
                }
                check!(format!("nums = {nums:?}"), delete_and_earn(&nums), want);
            }
        }

        #[test]
        fn scale_200k() {
            let nums: Vec<u32> = (0..200_000u64).map(|i| (i * 7919 % 100_000 + 1) as u32).collect();
            check!("nums[i] = (7919·i) % 100000 + 1, 200000 values", delete_and_earn(&nums), 5_000_100_000);
        }
        """,
    ],
    wrong=dict(
        rescans_per_value="""
            pub fn delete_and_earn(nums: &[u32]) -> u64 {
                let max = nums.iter().copied().max().unwrap_or(0);
                let (mut before, mut best) = (0u64, 0u64);
                for v in 0..=max {
                    let p = nums.iter().filter(|&&x| x == v).count() as u64 * v as u64;
                    (before, best) = (best, best.max(before + p));
                }
                best
            }
        """,
        each_value_once="""
            pub fn delete_and_earn(nums: &[u32]) -> u64 {
                let Some(&max) = nums.iter().max() else {
                    return 0;
                };
                let mut points = vec![0u64; max as usize + 1];
                for &x in nums {
                    points[x as usize] = x as u64;
                }
                let (mut before, mut best) = (0u64, 0u64);
                for &p in &points {
                    (before, best) = (best, best.max(before + p));
                }
                best
            }
        """,
        robs_sorted_positions="""
            pub fn delete_and_earn(nums: &[u32]) -> u64 {
                let mut sorted = nums.to_vec();
                sorted.sort_unstable();
                let (mut before, mut best) = (0u64, 0u64);
                for &x in &sorted {
                    (before, best) = (best, best.max(before + x as u64));
                }
                best
            }
        """,
    ),
    hints=[("approach", "Taking one copy of x deletes every x - 1 and x + 1, so you may as well take every copy of x. Sum the points per value; then values v and v + 1 are neighbouring houses."),
           ("rust", "`let Some(&max) = nums.iter().max() else { return 0 };` then a `vec![0u64; max + 1]` of totals, then the House robber loop over it."),
           ("edge case", "Values that differ by 2 or more don't interfere: [1, 3] → 4.")],
    notes=("Group by value, then it is House robber on the value line. Building the totals is O(n) and the robber pass is O(max value).", "O(n + max)", "O(max)"),
    follow_up="If values went up to 10⁹, how would you avoid a `Vec` that long? (Sort the distinct values; neighbours are only values that differ by 1.)",
    related=["D1", "S4"],
))

P.append(dict(
    slug="coin-change", title="Coin change", level="medium", stage="1d-choices", tags=["unbounded knapsack", "Option", "Blind 75"],
    companies=["Amazon", "Google", "Meta", "Apple", "Microsoft", "Bloomberg", "Uber", "Goldman Sachs"],
    teaches=["\"Fewest\" DP over amounts: each amount tries every coin as its last coin.",
             "`Option<u32>` for \"can't be made\" instead of a -1 or `u32::MAX` sentinel."],
    statement="""
        Return the fewest coins that add up to `amount`, using any number of each coin in `coins`,
        or `None` if no combination makes it. Making 0 needs no coins.
    """,
    examples=[("coins = [1, 2, 5], amount = 11", "Some(3) (5 + 5 + 1)"), ("coins = [2], amount = 3", "None")],
    constraints=["0 ≤ coins.len() ≤ 12, all distinct", "1 ≤ coins[i] ≤ 2³¹ - 1", "0 ≤ amount ≤ 10⁵"],
    starter="""
        pub fn coin_change(coins: &[u32], amount: u32) -> Option<u32> {
            todo!()
        }
    """,
    solution="""
        pub fn coin_change(coins: &[u32], amount: u32) -> Option<u32> {
            let amount = amount as usize;
            // fewest[a] = the fewest coins that make a, or None if a can't be made.
            let mut fewest: Vec<Option<u32>> = vec![None; amount + 1];
            fewest[0] = Some(0);
            for a in 1..=amount {
                fewest[a] = coins
                    .iter()
                    .filter(|&&c| c as usize <= a)
                    .filter_map(|&c| fewest[a - c as usize])
                    .min()
                    .map(|n| n + 1);
            }
            fewest[amount]
        }
    """,
    visible=[
        T("leetcode_eleven", "coins = [1, 2, 5], amount = 11", "coin_change(&[1, 2, 5], 11)", "Some(3)"),
        T("leetcode_impossible", "coins = [2], amount = 3", "coin_change(&[2], 3)", "None"),
        T("leetcode_zero", "coins = [1], amount = 0", "coin_change(&[1], 0)", "Some(0)"),
        T("greedy_fails", "coins = [1, 3, 4], amount = 6", "coin_change(&[1, 3, 4], 6)", "Some(2)"),
        T("one_coin", "coins = [5], amount = 5", "coin_change(&[5], 5)", "Some(1)"),
        T("no_coins", "coins = [], amount = 3", "coin_change(&[], 3)", "None"),
    ],
    hidden=[
        T("zero_amount", "coins = [7], amount = 0", "coin_change(&[7], 0)", "Some(0)"),
        T("no_coins_zero", "coins = [], amount = 0", "coin_change(&[], 0)", "Some(0)"),
        T("greedy_dead_end", "coins = [4, 5], amount = 8", "coin_change(&[4, 5], 8)", "Some(2)"),
        T("leetcode_big", "coins = [186, 419, 83, 408], amount = 6249", "coin_change(&[186, 419, 83, 408], 6249)", "Some(20)"),
        T("unsorted_coins", "coins = [2, 5, 10, 1], amount = 27", "coin_change(&[2, 5, 10, 1], 27)", "Some(4)"),
        T("unreachable", "coins = [3, 7], amount = 11", "coin_change(&[3, 7], 11)", "None"),
        T("also_unreachable", "coins = [3, 5], amount = 7", "coin_change(&[3, 5], 7)", "None"),
        T("huge_coin", "coins = [2147483647], amount = 2", "coin_change(&[2_147_483_647], 2)", "None"),
        T("many_ones", "coins = [1], amount = 10000", "coin_change(&[1], 10_000)", "Some(10_000)"),
        """
        #[test]
        fn random_vs_brute_force() {
            // Try every count of the first coin, then recurse on the rest.
            fn fewest(coins: &[u32], amount: u32) -> Option<u32> {
                match coins {
                    [] => (amount == 0).then_some(0),
                    [c, rest @ ..] => (0..=amount / c).filter_map(|k| fewest(rest, amount - k * c).map(|n| n + k)).min(),
                }
            }
            let mut rng = anneal_prelude::Rng::new(1210);
            for _ in 0..300 {
                let k = rng.int(0, 3) as usize;
                let mut coins: Vec<u32> = rng.vec(k, 1, 12);
                coins.sort_unstable();
                coins.dedup();
                let amount = rng.int(0, 40) as u32;
                check!(format!("coins = {coins:?}, amount = {amount}"), coin_change(&coins, amount), fewest(&coins, amount));
            }
        }

        #[test]
        fn scale_amount_100k() {
            let coins = [7, 23, 51, 97, 211, 479, 983, 1999, 4001, 7919, 9973, 10007];
            check!("coins = [7, 23, 51, 97, 211, 479, 983, 1999, 4001, 7919, 9973, 10007], amount = 100000", coin_change(&coins, 100_000), Some(14));
        }
        """,
    ],
    wrong=dict(
        greedy_largest_first="""
            pub fn coin_change(coins: &[u32], amount: u32) -> Option<u32> {
                let mut sorted = coins.to_vec();
                sorted.sort_unstable_by(|a, b| b.cmp(a));
                let (mut left, mut used) = (amount, 0);
                for c in sorted {
                    used += left / c;
                    left %= c;
                }
                (left == 0).then_some(used)
            }
        """,
        plain_recursion="""
            pub fn coin_change(coins: &[u32], amount: u32) -> Option<u32> {
                if amount == 0 {
                    return Some(0);
                }
                coins.iter().filter(|&&c| c <= amount).filter_map(|&c| coin_change(coins, amount - c)).min().map(|n| n + 1)
            }
        """,
        max_sentinel="""
            pub fn coin_change(coins: &[u32], amount: u32) -> Option<u32> {
                let amount = amount as usize;
                let mut fewest = vec![u32::MAX; amount + 1];
                fewest[0] = 0;
                for a in 1..=amount {
                    for &c in coins {
                        if c as usize <= a {
                            fewest[a] = fewest[a].min(fewest[a - c as usize] + 1);
                        }
                    }
                }
                (fewest[amount] != u32::MAX).then_some(fewest[amount])
            }
        """,
    ),
    hints=[("approach", "fewest(a) = 1 + min over coins c ≤ a of fewest(a - c). Fill it for a = 0, 1, …, amount."),
           ("rust", "A `Vec<Option<u32>>` table keeps \"unreachable\" in the type: `filter_map` skips the `None`s and `.min().map(|n| n + 1)` stays `None` when nothing works."),
           ("edge case", "Taking the largest coin first fails: [1, 3, 4] for 6 is 3 + 3, not 4 + 1 + 1. A `u32::MAX` sentinel overflows when you add 1 to it.")],
    notes=("Every amount is built from a smaller amount plus one coin, so a table over amounts 0..=amount answers it bottom-up. `Option` makes the unreachable case impossible to add to by accident.", "O(amount × coins)", "O(amount)"),
    follow_up="How would you also return which coins to use? And how would BFS over amounts compare?",
    related=["D9", "S1"],
))

P.append(dict(
    slug="perfect-squares", title="Perfect squares", level="medium", stage="1d-choices", tags=["unbounded knapsack", "1-D DP"],
    companies=["Google", "Amazon", "Meta", "Apple", "Microsoft", "Adobe", "Uber"],
    teaches=["Coin change where the coins are the squares up to n.", "Looping `j` while `j * j <= i` instead of a floating-point square root."],
    statement="Return the fewest perfect squares (1, 4, 9, 16, …) that add up to `n`.",
    examples=[("n = 12", "3 (4 + 4 + 4)"), ("n = 13", "2 (4 + 9)")],
    constraints=["1 ≤ n ≤ 10⁵"],
    starter="""
        pub fn num_squares(n: u32) -> u32 {
            todo!()
        }
    """,
    solution="""
        pub fn num_squares(n: u32) -> u32 {
            let n = n as usize;
            // fewest[i] = the fewest squares that sum to i; 1 is a square, so every i is reachable.
            let mut fewest = vec![u32::MAX; n + 1];
            fewest[0] = 0;
            for i in 1..=n {
                let mut j = 1;
                while j * j <= i {
                    fewest[i] = fewest[i].min(fewest[i - j * j] + 1);
                    j += 1;
                }
            }
            fewest[n]
        }
    """,
    visible=[
        T("leetcode_twelve", "n = 12", "num_squares(12)", "3"),
        T("leetcode_thirteen", "n = 13", "num_squares(13)", "2"),
        T("one", "n = 1", "num_squares(1)", "1"),
        T("already_square", "n = 16", "num_squares(16)", "1"),
        T("needs_four", "n = 7", "num_squares(7)", "4"),
    ],
    hidden=[
        T("one", "n = 1", "num_squares(1)", "1"),
        T("two", "n = 2", "num_squares(2)", "2"),
        T("three", "n = 3", "num_squares(3)", "3"),
        T("four", "n = 4", "num_squares(4)", "1"),
        T("greedy_trap", "n = 43", "num_squares(43)", "3"),
        T("form_4k_times_7", "n = 28", "num_squares(28)", "4"),
        T("leetcode_max", "n = 10000", "num_squares(10_000)", "1"),
        T("just_below", "n = 9999", "num_squares(9_999)", "4"),
        """
        #[test]
        fn random_vs_brute_force() {
            // Lagrange and Legendre: 1 if square, 2 if a sum of two squares, 4 if n = 4^a(8b + 7), else 3.
            fn want(n: u32) -> u32 {
                let is_square = |x: u32| (0..=x).take_while(|r| r * r <= x).any(|r| r * r == x);
                if is_square(n) {
                    return 1;
                }
                if (1..).take_while(|a| a * a <= n).any(|a| is_square(n - a * a)) {
                    return 2;
                }
                let mut m = n;
                while m % 4 == 0 {
                    m /= 4;
                }
                if m % 8 == 7 { 4 } else { 3 }
            }
            let mut rng = anneal_prelude::Rng::new(1211);
            for _ in 0..300 {
                let n = rng.int(1, 2000) as u32;
                check!(format!("n = {n}"), num_squares(n), want(n));
            }
        }

        #[test]
        fn scale_100k() {
            check!("n = 99999, then n = 100000", (num_squares(99_999), num_squares(100_000)), (4, 2));
        }
        """,
    ],
    wrong=dict(
        greedy_largest_square="""
            pub fn num_squares(n: u32) -> u32 {
                let (mut left, mut used) = (n, 0);
                while left > 0 {
                    let mut r = 1;
                    while (r + 1) * (r + 1) <= left {
                        r += 1;
                    }
                    left -= r * r;
                    used += 1;
                }
                used
            }
        """,
        plain_recursion="""
            pub fn num_squares(n: u32) -> u32 {
                if n == 0 {
                    return 0;
                }
                (1..).take_while(|j| j * j <= n).map(|j| num_squares(n - j * j) + 1).min().unwrap()
            }
        """,
    ),
    hints=[("approach", "This is Coin change with the squares 1, 4, 9, … ≤ n as the coins: fewest(i) = 1 + min over j of fewest(i - j²)."),
           ("rust", "Loop `while j * j <= i` on integers; `(n as f64).sqrt()` can be off by one for large values."),
           ("edge case", "Taking the largest square first fails: 12 = 9 + 1 + 1 + 1 greedily, but 4 + 4 + 4 is three.")],
    notes=("Each i tries every square below it as the last one. There are about √i of those, so the table costs O(n√n). The answer is never more than 4 (Lagrange's four-square theorem).", "O(n√n)", "O(n)"),
    follow_up="How would BFS from n find the answer, and when would it beat the table?",
    related=["D13", "D9"],
))

P.append(dict(
    slug="coin-change-ii", title="Coin change II", level="medium", stage="1d-choices", tags=["unbounded knapsack", "counting"],
    companies=["Amazon", "Google", "Meta", "Microsoft", "Bloomberg"],
    teaches=["Counting combinations, not orderings: put the coin loop outside the amount loop.",
             "`u64` counts for answers that grow fast."],
    statement="""
        Return how many different combinations of coins make `amount`, using any number of each
        coin. Order doesn't matter: `1 + 2` and `2 + 1` are the same combination. Making 0 has
        exactly one combination (no coins).
    """,
    examples=[("amount = 5, coins = [1, 2, 5]", "4 (5, 2+2+1, 2+1+1+1, 1+1+1+1+1)")],
    constraints=["0 ≤ amount ≤ 5000", "0 ≤ coins.len() ≤ 300, all distinct, 1 ≤ coins[i] ≤ 5000", "the answer fits in a u64"],
    starter="""
        pub fn change(amount: u32, coins: &[u32]) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn change(amount: u32, coins: &[u32]) -> u64 {
            let amount = amount as usize;
            // ways[a] = combinations of the coins seen so far that make a.
            let mut ways = vec![0u64; amount + 1];
            ways[0] = 1;
            // Coins outside: each combination is built in coin order, so it is counted once.
            for &c in coins {
                for a in c as usize..=amount {
                    ways[a] += ways[a - c as usize];
                }
            }
            ways[amount]
        }
    """,
    visible=[
        T("leetcode_five", "amount = 5, coins = [1, 2, 5]", "change(5, &[1, 2, 5])", "4"),
        T("leetcode_impossible", "amount = 3, coins = [2]", "change(3, &[2])", "0"),
        T("leetcode_exact", "amount = 10, coins = [10]", "change(10, &[10])", "1"),
        T("zero_amount", "amount = 0, coins = [7]", "change(0, &[7])", "1"),
        T("order_does_not_matter", "amount = 4, coins = [1, 2] (1+1+2 and 2+1+1 are one combination)", "change(4, &[1, 2])", "3"),
    ],
    hidden=[
        T("zero_amount", "amount = 0, coins = [7]", "change(0, &[7])", "1"),
        T("no_coins_zero", "amount = 0, coins = []", "change(0, &[])", "1"),
        T("no_coins", "amount = 5, coins = []", "change(5, &[])", "0"),
        T("coin_too_big", "amount = 1, coins = [2]", "change(1, &[2])", "0"),
        T("even_coins_odd_amount", "amount = 7, coins = [2, 4]", "change(7, &[2, 4])", "0"),
        T("one_two_three", "amount = 12, coins = [1, 2, 3]", "change(12, &[1, 2, 3])", "19"),
        T("us_cents", "amount = 100, coins = [1, 5, 10, 25, 50]", "change(100, &[1, 5, 10, 25, 50])", "292"),
        T("leetcode_large", "amount = 500, coins = [3, 5, 7, 8, 9, 10, 11]", "change(500, &[3, 5, 7, 8, 9, 10, 11])", "35_502_874"),
        """
        #[test]
        fn random_vs_brute_force() {
            // Try every count of the first coin, then recurse on the rest.
            fn count(coins: &[u32], amount: u32) -> u64 {
                match coins {
                    [] => (amount == 0) as u64,
                    [c, rest @ ..] => (0..=amount / c).map(|k| count(rest, amount - k * c)).sum(),
                }
            }
            let mut rng = anneal_prelude::Rng::new(1212);
            for _ in 0..300 {
                let k = rng.int(0, 4) as usize;
                let mut coins: Vec<u32> = rng.vec(k, 1, 10);
                coins.sort_unstable();
                coins.dedup();
                rng.shuffle(&mut coins);
                let amount = rng.int(0, 30) as u32;
                check!(format!("amount = {amount}, coins = {coins:?}"), change(amount, &coins), count(&coins, amount));
            }
        }

        #[test]
        fn scale_amount_5000() {
            let coins = [1, 2, 5, 10, 20, 50, 100, 200, 500];
            check!("amount = 5000, coins = [1, 2, 5, 10, 20, 50, 100, 200, 500]", change(5000, &coins), 18_682_149_631_801);
        }
        """,
    ],
    wrong=dict(
        counts_orderings="""
            pub fn change(amount: u32, coins: &[u32]) -> u64 {
                let amount = amount as usize;
                let mut ways = vec![0u64; amount + 1];
                ways[0] = 1;
                for a in 1..=amount {
                    for &c in coins {
                        if c as usize <= a {
                            ways[a] = ways[a].wrapping_add(ways[a - c as usize]);
                        }
                    }
                }
                ways[amount]
            }
        """,
        plain_recursion="""
            fn count(coins: &[u32], amount: u32) -> u64 {
                match coins {
                    [] => (amount == 0) as u64,
                    [c, rest @ ..] => {
                        let skip = count(rest, amount);
                        if *c <= amount { skip + count(coins, amount - c) } else { skip }
                    }
                }
            }

            pub fn change(amount: u32, coins: &[u32]) -> u64 {
                count(coins, amount)
            }
        """,
        zero_amount_is_zero="""
            pub fn change(amount: u32, coins: &[u32]) -> u64 {
                if amount == 0 {
                    return 0;
                }
                let amount = amount as usize;
                let mut ways = vec![0u64; amount + 1];
                ways[0] = 1;
                for &c in coins {
                    for a in c as usize..=amount {
                        ways[a] += ways[a - c as usize];
                    }
                }
                ways[amount]
            }
        """,
    ),
    hints=[("approach", "Process one coin at a time. After coin c, ways[a] counts combinations that use only the coins so far, so each combination is built in one fixed order."),
           ("rust", "`for &c in coins { for a in c as usize..=amount { ways[a] += ways[a - c as usize]; } }` — the range is empty when c > amount."),
           ("edge case", "Swapping the loops counts orderings (1+2 and 2+1 twice). amount = 0 has one combination, even with no coins.")],
    notes=("With coins in the outer loop, each combination is counted once, when its coins are added in order. Going forwards over amounts lets a coin be reused (unbounded).", "O(amount × coins)", "O(amount)"),
    follow_up="Which loop order counts orderings instead, and which problem is that (Combination sum IV)?",
    related=["D11"],
))

P.append(dict(
    slug="word-break", title="Word break", level="medium", stage="1d-choices", tags=["1-D DP", "HashSet", "Blind 75"],
    companies=["Meta", "Amazon", "Google", "Apple", "Microsoft", "Bloomberg", "Uber", "Adobe"],
    teaches=["A boolean table over prefixes: `ok[end]` is true if some word ends at `end` after an `ok` prefix.",
             "Slicing bytes (`&s.as_bytes()[a..b]`) so non-ASCII text never splits a character."],
    statement="""
        Return whether `s` can be split into a sequence of one or more words from `words`. Words
        may be reused. Strings may contain any Unicode text. The empty string needs no words, so it
        can always be split.
    """,
    examples=[("s = \"applepenapple\", words = [\"apple\", \"pen\"]", "true (apple pen apple)"),
              ("s = \"catsandog\", words = [\"cats\", \"dog\", \"sand\", \"and\", \"cat\"]", "false")],
    constraints=["0 ≤ s.len() ≤ 300 bytes", "0 ≤ words.len() ≤ 1000", "1 ≤ words[i].len() ≤ 20 bytes"],
    starter="""
        pub fn word_break(s: &str, words: &[&str]) -> bool {
            todo!()
        }
    """,
    solution="""
        use std::collections::HashSet;

        pub fn word_break(s: &str, words: &[&str]) -> bool {
            let dict: HashSet<&[u8]> = words.iter().map(|w| w.as_bytes()).collect();
            let longest = words.iter().map(|w| w.len()).max().unwrap_or(0);
            let s = s.as_bytes();
            // ok[end]: the first `end` bytes split into words.
            let mut ok = vec![false; s.len() + 1];
            ok[0] = true;
            for end in 1..=s.len() {
                let first = end.saturating_sub(longest);
                ok[end] = (first..end).any(|start| ok[start] && dict.contains(&s[start..end]));
            }
            ok[s.len()]
        }
    """,
    visible=[
        T("leetcode_leetcode", "s = \"leetcode\", words = [\"leet\", \"code\"]", "word_break(\"leetcode\", &[\"leet\", \"code\"])", "true"),
        T("leetcode_reuse", "s = \"applepenapple\", words = [\"apple\", \"pen\"]", "word_break(\"applepenapple\", &[\"apple\", \"pen\"])", "true"),
        T("leetcode_catsandog", "s = \"catsandog\", words = [\"cats\", \"dog\", \"sand\", \"and\", \"cat\"]", "word_break(\"catsandog\", &[\"cats\", \"dog\", \"sand\", \"and\", \"cat\"])", "false"),
        T("empty_string", "s = \"\", words = [\"a\"]", "word_break(\"\", &[\"a\"])", "true"),
        T("no_words", "s = \"a\", words = []", "word_break(\"a\", &[])", "false"),
        T("longest_first_fails", "s = \"cars\", words = [\"car\", \"ca\", \"rs\"]", "word_break(\"cars\", &[\"car\", \"ca\", \"rs\"])", "true"),
    ],
    hidden=[
        T("empty_everything", "s = \"\", words = []", "word_break(\"\", &[])", "true"),
        T("single_word", "s = \"a\", words = [\"a\"]", "word_break(\"a\", &[\"a\"])", "true"),
        T("word_longer_than_s", "s = \"ab\", words = [\"abc\"]", "word_break(\"ab\", &[\"abc\"])", "false"),
        T("overlapping_choices", "s = \"aaaaaaa\", words = [\"aaaa\", \"aaa\"]", "word_break(\"aaaaaaa\", &[\"aaaa\", \"aaa\"])", "true"),
        T("only_long_words_fit", "s = \"bb\", words = [\"a\", \"b\", \"bbb\", \"bbbb\"]", "word_break(\"bb\", &[\"a\", \"b\", \"bbb\", \"bbbb\"])", "true"),
        T("leftover_char", "s = \"catsanddogs\", words = [\"cats\", \"dog\", \"sand\", \"and\", \"cat\"]", "word_break(\"catsanddogs\", &[\"cats\", \"dog\", \"sand\", \"and\", \"cat\"])", "false"),
        T("unicode", "s = \"日本語\", words = [\"日本\", \"語\"]", "word_break(\"日本語\", &[\"日本\", \"語\"])", "true"),
        T("unicode_missing_piece", "s = \"日本語\", words = [\"日\", \"語\"]", "word_break(\"日本語\", &[\"日\", \"語\"])", "false"),
        T("accented", "s = \"héllo\", words = [\"hé\", \"llo\"]", "word_break(\"héllo\", &[\"hé\", \"llo\"])", "true"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn can(s: &str, words: &[String]) -> bool {
                s.is_empty() || words.iter().any(|w| s.starts_with(w.as_str()) && can(&s[w.len()..], words))
            }
            let mut rng = anneal_prelude::Rng::new(1213);
            for _ in 0..400 {
                let len = rng.below(13);
                let s = rng.string(len, "ab");
                let k = rng.int(0, 4) as usize;
                let mut words: Vec<String> = Vec::new();
                for _ in 0..k {
                    let wl = rng.int(1, 4) as usize;
                    words.push(rng.string(wl, "ab"));
                }
                let refs: Vec<&str> = words.iter().map(|w| w.as_str()).collect();
                check!(format!("s = {s:?}, words = {words:?}"), word_break(&s, &refs), can(&s, &words));
            }
        }

        #[test]
        fn scale_many_ways_to_fail() {
            // Every prefix of a's splits many ways, but the final b never fits.
            let s = format!("{}b", "a".repeat(299));
            let words: Vec<String> = (1..=20).map(|k| "a".repeat(k)).collect();
            let refs: Vec<&str> = words.iter().map(|w| w.as_str()).collect();
            check!("s = \\"aaa…ab\\" (300 bytes), words = [\\"a\\", \\"aa\\", …, 20 a's]", word_break(&s, &refs), false);
        }
        """,
    ],
    wrong=dict(
        plain_recursion="""
            pub fn word_break(s: &str, words: &[&str]) -> bool {
                s.is_empty() || words.iter().any(|w| s.starts_with(w) && word_break(&s[w.len()..], words))
            }
        """,
        longest_word_first="""
            pub fn word_break(s: &str, words: &[&str]) -> bool {
                let mut rest = s;
                while !rest.is_empty() {
                    match words.iter().filter(|w| rest.starts_with(**w)).max_by_key(|w| w.len()) {
                        Some(w) => rest = &rest[w.len()..],
                        None => return false,
                    }
                }
                true
            }
        """,
        slices_str_at_every_byte="""
            use std::collections::HashSet;

            pub fn word_break(s: &str, words: &[&str]) -> bool {
                let dict: HashSet<&str> = words.iter().copied().collect();
                let mut ok = vec![false; s.len() + 1];
                ok[0] = true;
                for end in 1..=s.len() {
                    ok[end] = (end.saturating_sub(20)..end).any(|start| ok[start] && dict.contains(&s[start..end]));
                }
                ok[s.len()]
            }
        """,
    ),
    hints=[("approach", "ok[end] is true when some start < end has ok[start] and s[start..end] is a word. ok[0] is true: the empty prefix needs no words."),
           ("rust", "Put the words in a `HashSet<&[u8]>` and slice `s.as_bytes()`. Only look back as far as the longest word."),
           ("edge case", "`&s[a..b]` on a `&str` panics when a or b falls inside a multi-byte character, like the middle of \"日\". Byte slices never panic.")],
    notes=("Each end position checks at most `longest` start positions, and each check hashes a slice of at most `longest` bytes. Taking the longest matching word first fails on \"cars\" with [\"car\", \"ca\", \"rs\"].", "O(n × L²) for L = longest word", "O(n + total word length)"),
    follow_up="How would you return every valid sentence (Word break II), and how big can that output get?",
    related=["D10", "S2", "S4"],
))

P.append(dict(
    slug="maximum-product-subarray", title="Maximum product subarray", level="medium", stage="1d-choices", tags=["Kadane", "Blind 75"],
    companies=["Amazon", "Google", "Meta", "Apple", "Microsoft", "LinkedIn", "Bloomberg"],
    teaches=["Carrying the largest and the smallest product ending here: a negative number swaps them.",
             "`Option<i64>` for the empty slice, `i64` for the products."],
    statement="""
        Return the largest product of a non-empty contiguous subarray of `nums`, or `None` if
        `nums` is empty.
    """,
    examples=[("nums = [2, 3, -2, 4]", "Some(6) ([2, 3])"), ("nums = [-2, 3, -4]", "Some(24) (the whole slice)")],
    constraints=["0 ≤ nums.len() ≤ 2·10⁵", "-10 ≤ nums[i] ≤ 10", "the product of every subarray fits in an i64"],
    starter="""
        pub fn max_product(nums: &[i32]) -> Option<i64> {
            todo!()
        }
    """,
    solution="""
        pub fn max_product(nums: &[i32]) -> Option<i64> {
            let (&first, rest) = nums.split_first()?;
            let first = first as i64;
            // hi / lo: the largest / smallest product of a subarray ending at the current element.
            let (mut hi, mut lo, mut best) = (first, first, first);
            for &x in rest {
                let x = x as i64;
                let options = [x, hi * x, lo * x];
                hi = *options.iter().max().unwrap();
                lo = *options.iter().min().unwrap();
                best = best.max(hi);
            }
            Some(best)
        }
    """,
    visible=[
        T("leetcode_positive_run", "nums = [2, 3, -2, 4]", "max_product(&[2, 3, -2, 4])", "Some(6)"),
        T("leetcode_zero", "nums = [-2, 0, -1]", "max_product(&[-2, 0, -1])", "Some(0)"),
        T("empty", "nums = []", "max_product(&[])", "None"),
        T("single_negative", "nums = [-2]", "max_product(&[-2])", "Some(-2)"),
        T("two_negatives_cancel", "nums = [-2, 3, -4]", "max_product(&[-2, 3, -4])", "Some(24)"),
    ],
    hidden=[
        T("empty", "nums = []", "max_product(&[])", "None"),
        T("single_zero", "nums = [0]", "max_product(&[0])", "Some(0)"),
        T("single_negative", "nums = [-3]", "max_product(&[-3])", "Some(-3)"),
        T("negative_pair", "nums = [-2, -3]", "max_product(&[-2, -3])", "Some(6)"),
        T("odd_negatives", "nums = [-1, -1, -1]", "max_product(&[-1, -1, -1])", "Some(1)"),
        T("skip_the_negative", "nums = [3, -1, 4]", "max_product(&[3, -1, 4])", "Some(4)"),
        T("zero_splits", "nums = [-2, 0]", "max_product(&[-2, 0])", "Some(0)"),
        T("even_negatives_inside", "nums = [2, -5, -2, -4, 3]", "max_product(&[2, -5, -2, -4, 3])", "Some(24)"),
        T("before_a_zero", "nums = [-1, -2, -3, 0]", "max_product(&[-1, -2, -3, 0])", "Some(6)"),
        T("past_i32", "nums = [-10; 18]", "max_product(&[-10; 18])", "Some(1_000_000_000_000_000_000)"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1214);
            for _ in 0..400 {
                let n = rng.below(11);
                let nums: Vec<i32> = rng.vec(n, -4, 4);
                let mut want: Option<i64> = None;
                for i in 0..n {
                    let mut p = 1i64;
                    for j in i..n {
                        p *= nums[j] as i64;
                        want = Some(want.map_or(p, |w| w.max(p)));
                    }
                }
                check!(format!("nums = {nums:?}"), max_product(&nums), want);
            }
        }

        #[test]
        fn scale_200k() {
            let mut nums = vec![1i32; 200_000];
            for i in (0..200_000).step_by(5_000) {
                nums[i] = -2;
            }
            nums[100_000] = 0;
            check!("nums = 200000 ones, -2 at every multiple of 5000, 0 at 100000", max_product(&nums), Some(1_048_576));
        }
        """,
    ],
    wrong=dict(
        only_the_max="""
            pub fn max_product(nums: &[i32]) -> Option<i64> {
                let (&first, rest) = nums.split_first()?;
                let (mut hi, mut best) = (first as i64, first as i64);
                for &x in rest {
                    let x = x as i64;
                    hi = x.max(hi * x);
                    best = best.max(hi);
                }
                Some(best)
            }
        """,
        quadratic="""
            pub fn max_product(nums: &[i32]) -> Option<i64> {
                let mut best: Option<i64> = None;
                for i in 0..nums.len() {
                    let mut p = 1i64;
                    for &x in &nums[i..] {
                        p *= x as i64;
                        best = Some(best.map_or(p, |b| b.max(p)));
                    }
                }
                best
            }
        """,
        best_starts_at_zero="""
            pub fn max_product(nums: &[i32]) -> Option<i64> {
                if nums.is_empty() {
                    return None;
                }
                let (mut hi, mut lo, mut best) = (1i64, 1i64, 0i64);
                for &x in nums {
                    let x = x as i64;
                    let options = [x, hi * x, lo * x];
                    hi = *options.iter().max().unwrap();
                    lo = *options.iter().min().unwrap();
                    best = best.max(hi);
                }
                Some(best)
            }
        """,
    ),
    hints=[("approach", "Keep the largest and the smallest product of a subarray ending here. Multiplying by a negative turns the smallest into the largest."),
           ("rust", "`let (&first, rest) = nums.split_first()?;` handles the empty slice and seeds the three running values."),
           ("edge case", "A single negative element is its own best answer, so don't start `best` at 0.")],
    notes=("It is Kadane's algorithm with two running values: at each element the new extremes are among x, hi·x and lo·x. Zeros reset both naturally.", "O(n)", "O(1)"),
    follow_up="How would you return the subarray's bounds, not just the product?",
    related=["D2", "D1"],
))

P.append(dict(
    slug="longest-increasing-subsequence", title="Longest increasing subsequence", level="medium", stage="1d-choices", tags=["1-D DP", "O(n²)", "Blind 75"],
    companies=["Amazon", "Google", "Meta", "Microsoft", "Apple", "Bloomberg", "Uber"],
    teaches=["The \"ends at i\" state: the best subsequence that finishes on element i.", "An O(n²) table first; the next problem makes it O(n log n)."],
    statement="""
        Return the length of the longest strictly increasing subsequence of `nums`. A subsequence
        keeps the original order but may skip elements.
    """,
    examples=[("nums = [10, 9, 2, 5, 3, 7, 101, 18]", "4 ([2, 3, 7, 18])")],
    constraints=["0 ≤ nums.len() ≤ 2500", "nums[i] fits in an i32"],
    starter="""
        pub fn length_of_lis(nums: &[i32]) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn length_of_lis(nums: &[i32]) -> usize {
            // ends_at[i] = the longest increasing subsequence that ends on nums[i].
            let mut ends_at = vec![1usize; nums.len()];
            for i in 0..nums.len() {
                for j in 0..i {
                    if nums[j] < nums[i] {
                        ends_at[i] = ends_at[i].max(ends_at[j] + 1);
                    }
                }
            }
            ends_at.into_iter().max().unwrap_or(0)
        }
    """,
    visible=[
        T("leetcode_eight", "nums = [10, 9, 2, 5, 3, 7, 101, 18]", "length_of_lis(&[10, 9, 2, 5, 3, 7, 101, 18])", "4"),
        T("leetcode_six", "nums = [0, 1, 0, 3, 2, 3]", "length_of_lis(&[0, 1, 0, 3, 2, 3])", "4"),
        T("leetcode_all_equal", "nums = [7, 7, 7, 7, 7, 7, 7]", "length_of_lis(&[7, 7, 7, 7, 7, 7, 7])", "1"),
        T("empty", "nums = []", "length_of_lis(&[])", "0"),
        T("single", "nums = [5]", "length_of_lis(&[5])", "1"),
        T("may_skip", "nums = [1, 5, 2, 3] (skips the 5)", "length_of_lis(&[1, 5, 2, 3])", "3"),
    ],
    hidden=[
        T("empty", "nums = []", "length_of_lis(&[])", "0"),
        T("single", "nums = [-4]", "length_of_lis(&[-4])", "1"),
        T("increasing", "nums = [1, 2, 3]", "length_of_lis(&[1, 2, 3])", "3"),
        T("decreasing", "nums = [3, 2, 1]", "length_of_lis(&[3, 2, 1])", "1"),
        T("equal_not_increasing", "nums = [2, 2, 3, 3]", "length_of_lis(&[2, 2, 3, 3])", "2"),
        T("not_contiguous", "nums = [1, 3, 6, 7, 9, 4, 10, 5, 6]", "length_of_lis(&[1, 3, 6, 7, 9, 4, 10, 5, 6])", "6"),
        T("restart_trap", "nums = [4, 10, 4, 3, 8, 9]", "length_of_lis(&[4, 10, 4, 3, 8, 9])", "3"),
        T("extremes", "nums = [i32::MIN, i32::MAX]", "length_of_lis(&[i32::MIN, i32::MAX])", "2"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1215);
            for _ in 0..300 {
                let n = rng.below(12);
                let nums: Vec<i32> = rng.vec(n, -5, 5);
                let mut want = 0;
                for mask in 0u32..(1 << n) {
                    let picked: Vec<i32> = (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| nums[i]).collect();
                    if picked.windows(2).all(|w| w[0] < w[1]) {
                        want = want.max(picked.len());
                    }
                }
                check!(format!("nums = {nums:?}"), length_of_lis(&nums), want);
            }
        }

        #[test]
        fn scale_2500() {
            let nums: Vec<i32> = (0..2500i64).map(|i| (i * 7919 % 10_007 - 5_000) as i32).collect();
            check!("nums[i] = (7919·i) % 10007 - 5000, 2500 values", length_of_lis(&nums), 44);
        }
        """,
    ],
    wrong=dict(
        take_or_skip_recursion="""
            fn best(nums: &[i32], prev: Option<i32>) -> usize {
                match nums {
                    [] => 0,
                    [x, rest @ ..] => {
                        let skip = best(rest, prev);
                        if prev.map_or(true, |p| p < *x) { skip.max(1 + best(rest, Some(*x))) } else { skip }
                    }
                }
            }

            pub fn length_of_lis(nums: &[i32]) -> usize {
                best(nums, None)
            }
        """,
        allows_equal="""
            pub fn length_of_lis(nums: &[i32]) -> usize {
                let mut ends_at = vec![1usize; nums.len()];
                for i in 0..nums.len() {
                    for j in 0..i {
                        if nums[j] <= nums[i] {
                            ends_at[i] = ends_at[i].max(ends_at[j] + 1);
                        }
                    }
                }
                ends_at.into_iter().max().unwrap_or(0)
            }
        """,
        longest_run="""
            pub fn length_of_lis(nums: &[i32]) -> usize {
                let (mut run, mut best) = (0, 0);
                for i in 0..nums.len() {
                    run = if i > 0 && nums[i - 1] < nums[i] { run + 1 } else { 1 };
                    best = best.max(run);
                }
                best
            }
        """,
    ),
    hints=[("approach", "Let ends_at[i] be the longest increasing subsequence that ends on nums[i]: 1 plus the best ends_at[j] over j < i with nums[j] < nums[i]."),
           ("rust", "`vec![1usize; n]` seeds every element as a subsequence of its own; `into_iter().max().unwrap_or(0)` covers the empty slice."),
           ("edge case", "Strictly increasing: equal values don't extend each other, so [7, 7, 7] → 1.")],
    notes=("The answer is the best ends_at over all positions, since the subsequence can end anywhere. Each i scans every j before it.", "O(n²)", "O(n)"),
    follow_up="How would you reconstruct one longest subsequence, not just its length?",
    related=["D4"],
))

P.append(dict(
    slug="lis-n-log-n", title="Longest increasing subsequence in O(n log n)", level="medium", stage="1d-choices", tags=["binary search", "partition_point"],
    companies=["Google", "Amazon", "Meta", "Microsoft"],
    teaches=["Patience sorting: keep the smallest possible tail for every length, and binary-search where each value goes.",
             "`slice::partition_point` as a lower bound."],
    statement="""
        The same question as before (the length of the longest strictly increasing subsequence),
        but `nums` can now hold 2·10⁵ values, so O(n²) is too slow.
    """,
    examples=[("nums = [0, 1, 0, 3, 2, 3]", "4")],
    constraints=["0 ≤ nums.len() ≤ 2·10⁵", "nums[i] fits in an i32"],
    starter="""
        pub fn length_of_lis(nums: &[i32]) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn length_of_lis(nums: &[i32]) -> usize {
            // tails[k] = the smallest last value of any increasing subsequence of length k + 1.
            // It is strictly increasing, so it can be binary-searched.
            let mut tails: Vec<i32> = Vec::new();
            for &x in nums {
                let k = tails.partition_point(|&t| t < x);
                if k == tails.len() {
                    tails.push(x);
                } else {
                    tails[k] = x;
                }
            }
            tails.len()
        }
    """,
    visible=[
        T("leetcode_eight", "nums = [10, 9, 2, 5, 3, 7, 101, 18]", "length_of_lis(&[10, 9, 2, 5, 3, 7, 101, 18])", "4"),
        T("leetcode_six", "nums = [0, 1, 0, 3, 2, 3]", "length_of_lis(&[0, 1, 0, 3, 2, 3])", "4"),
        T("leetcode_all_equal", "nums = [7, 7, 7, 7, 7, 7, 7]", "length_of_lis(&[7, 7, 7, 7, 7, 7, 7])", "1"),
        T("empty", "nums = []", "length_of_lis(&[])", "0"),
        T("single", "nums = [5]", "length_of_lis(&[5])", "1"),
        T("smaller_tail_wins_later", "nums = [4, 10, 4, 3, 8, 9]", "length_of_lis(&[4, 10, 4, 3, 8, 9])", "3"),
    ],
    hidden=[
        T("empty", "nums = []", "length_of_lis(&[])", "0"),
        T("decreasing", "nums = [3, 2, 1]", "length_of_lis(&[3, 2, 1])", "1"),
        T("equal_not_increasing", "nums = [2, 2, 3, 3]", "length_of_lis(&[2, 2, 3, 3])", "2"),
        T("not_contiguous", "nums = [1, 3, 6, 7, 9, 4, 10, 5, 6]", "length_of_lis(&[1, 3, 6, 7, 9, 4, 10, 5, 6])", "6"),
        T("replace_middle", "nums = [1, 5, 2, 3]", "length_of_lis(&[1, 5, 2, 3])", "3"),
        T("extremes", "nums = [i32::MIN, i32::MAX]", "length_of_lis(&[i32::MIN, i32::MAX])", "2"),
        T("negatives", "nums = [-3, -5, -1, -2, 0]", "length_of_lis(&[-3, -5, -1, -2, 0])", "3"),
        T("increasing_200k", "nums = 0..200000", "length_of_lis(&(0..200_000).collect::<Vec<i32>>())", "200_000"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1216);
            for _ in 0..400 {
                let n = rng.below(40);
                let nums: Vec<i32> = rng.vec(n, -8, 8);
                let mut ends_at = vec![1usize; n];
                for i in 0..n {
                    for j in 0..i {
                        if nums[j] < nums[i] {
                            ends_at[i] = ends_at[i].max(ends_at[j] + 1);
                        }
                    }
                }
                let want = ends_at.into_iter().max().unwrap_or(0);
                check!(format!("nums = {nums:?}"), length_of_lis(&nums), want);
            }
        }

        #[test]
        fn scale_200k() {
            let nums: Vec<i32> = (0..200_000i64).map(|i| (i * 7919 % 100_003 - 50_000) as i32).collect();
            check!("nums[i] = (7919·i) % 100003 - 50000, 200000 values", length_of_lis(&nums), 511);
        }

        #[test]
        fn scale_pairs_200k() {
            let nums: Vec<i32> = (0..200_000).map(|i| i / 2).collect();
            check!("nums = [0, 0, 1, 1, 2, 2, …] (200000 values)", length_of_lis(&nums), 100_000);
        }
        """,
    ],
    wrong=dict(
        quadratic="""
            pub fn length_of_lis(nums: &[i32]) -> usize {
                let mut ends_at = vec![1usize; nums.len()];
                for i in 0..nums.len() {
                    for j in 0..i {
                        if nums[j] < nums[i] {
                            ends_at[i] = ends_at[i].max(ends_at[j] + 1);
                        }
                    }
                }
                ends_at.into_iter().max().unwrap_or(0)
            }
        """,
        upper_bound="""
            pub fn length_of_lis(nums: &[i32]) -> usize {
                let mut tails: Vec<i32> = Vec::new();
                for &x in nums {
                    let k = tails.partition_point(|&t| t <= x);
                    if k == tails.len() {
                        tails.push(x);
                    } else {
                        tails[k] = x;
                    }
                }
                tails.len()
            }
        """,
        replaces_only_the_last="""
            pub fn length_of_lis(nums: &[i32]) -> usize {
                let mut tails: Vec<i32> = Vec::new();
                for &x in nums {
                    match tails.last() {
                        Some(&t) if t >= x => *tails.last_mut().unwrap() = x,
                        _ => tails.push(x),
                    }
                }
                tails.len()
            }
        """,
    ),
    hints=[("approach", "Keep tails[k], the smallest value that can end an increasing subsequence of length k + 1. Each new x either extends the longest one or lowers the first tail that is ≥ x."),
           ("rust", "`tails.partition_point(|&t| t < x)` is the index of the first tail ≥ x (a lower bound), in O(log n)."),
           ("edge case", "Using `t <= x` (an upper bound) lets equal values extend each other: [0, 0, 1, 1] would count 4.")],
    notes=("`tails` stays sorted, and replacing a tail with a smaller value never shortens anything, it only makes later extensions easier. Its length is the answer; its contents are not necessarily a real subsequence.", "O(n log n)", "O(n)"),
    follow_up="How would you recover an actual longest subsequence with this method? (Store, for each element, the index of its predecessor.)",
    related=["D4"],
))

P.append(dict(
    slug="russian-doll-envelopes", title="Russian doll envelopes", level="hard", stage="1d-choices", tags=["LIS", "sorting"],
    companies=["Google", "Amazon", "Microsoft", "Meta"],
    teaches=["Reducing two dimensions to one: sort by width, then LIS on heights.",
             "Sorting equal widths by height descending so they can't nest in each other."],
    statement="""
        Envelope `(w, h)` fits inside another only if both its width and height are strictly
        smaller. Rotating is not allowed. Return how many envelopes you can nest one inside another
        at most.
    """,
    examples=[("envelopes = [(5, 4), (6, 4), (6, 7), (2, 3)]", "3 ((2, 3) → (5, 4) → (6, 7))")],
    constraints=["0 ≤ envelopes.len() ≤ 10⁵", "1 ≤ w, h ≤ 10⁵"],
    starter="""
        pub fn max_envelopes(envelopes: &[(u32, u32)]) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn max_envelopes(envelopes: &[(u32, u32)]) -> usize {
            let mut env = envelopes.to_vec();
            // Width ascending; equal widths by height descending, so two of the same width
            // can never both appear in the increasing run of heights.
            env.sort_unstable_by(|a, b| a.0.cmp(&b.0).then(b.1.cmp(&a.1)));
            let mut tails: Vec<u32> = Vec::new();
            for &(_, h) in &env {
                let k = tails.partition_point(|&t| t < h);
                if k == tails.len() {
                    tails.push(h);
                } else {
                    tails[k] = h;
                }
            }
            tails.len()
        }
    """,
    visible=[
        T("leetcode_four", "envelopes = [(5, 4), (6, 4), (6, 7), (2, 3)]", "max_envelopes(&[(5, 4), (6, 4), (6, 7), (2, 3)])", "3"),
        T("leetcode_all_same", "envelopes = [(1, 1), (1, 1), (1, 1)]", "max_envelopes(&[(1, 1), (1, 1), (1, 1)])", "1"),
        T("empty", "envelopes = []", "max_envelopes(&[])", "0"),
        T("single", "envelopes = [(1, 1)]", "max_envelopes(&[(1, 1)])", "1"),
        T("same_width_never_nests", "envelopes = [(2, 3), (2, 4)]", "max_envelopes(&[(2, 3), (2, 4)])", "1"),
        T("no_rotation", "envelopes = [(3, 1), (2, 2), (1, 3)]", "max_envelopes(&[(3, 1), (2, 2), (1, 3)])", "1"),
    ],
    hidden=[
        T("empty", "envelopes = []", "max_envelopes(&[])", "0"),
        T("chain", "envelopes = [(1, 2), (2, 3), (3, 4)]", "max_envelopes(&[(1, 2), (2, 3), (3, 4)])", "3"),
        T("shuffled_chain", "envelopes = [(3, 4), (1, 2), (2, 3)]", "max_envelopes(&[(3, 4), (1, 2), (2, 3)])", "3"),
        T("tie_on_width", "envelopes = [(4, 5), (4, 6), (6, 7), (2, 3), (1, 1)]", "max_envelopes(&[(4, 5), (4, 6), (6, 7), (2, 3), (1, 1)])", "4"),
        T("mixed", "envelopes = [(1, 3), (3, 5), (6, 7), (6, 8), (8, 4), (9, 5)]", "max_envelopes(&[(1, 3), (3, 5), (6, 7), (6, 8), (8, 4), (9, 5)])", "3"),
        T("many_ties", "envelopes = [(2, 100), (3, 200), (4, 300), (5, 500), (5, 400), (5, 250), (6, 370), (6, 360), (7, 380)]",
          "max_envelopes(&[(2, 100), (3, 200), (4, 300), (5, 500), (5, 400), (5, 250), (6, 370), (6, 360), (7, 380)])", "5"),
        T("equal_heights", "envelopes = [(1, 5), (2, 5), (3, 5)]", "max_envelopes(&[(1, 5), (2, 5), (3, 5)])", "1"),
        T("largest_values", "envelopes = [(100000, 100000), (1, 1)]", "max_envelopes(&[(100_000, 100_000), (1, 1)])", "2"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1217);
            for _ in 0..300 {
                let n = rng.below(10);
                let mut env: Vec<(u32, u32)> = Vec::new();
                for _ in 0..n {
                    let w = rng.int(1, 5) as u32;
                    let h = rng.int(1, 5) as u32;
                    env.push((w, h));
                }
                // Chain DP after a plain sort: fits[j] < fits[i] needs both sides smaller.
                let mut sorted = env.clone();
                sorted.sort_unstable();
                let mut best = vec![1usize; n];
                for i in 0..n {
                    for j in 0..i {
                        if sorted[j].0 < sorted[i].0 && sorted[j].1 < sorted[i].1 {
                            best[i] = best[i].max(best[j] + 1);
                        }
                    }
                }
                let want = best.into_iter().max().unwrap_or(0);
                check!(format!("envelopes = {env:?}"), max_envelopes(&env), want);
            }
        }

        #[test]
        fn scale_100k() {
            let env: Vec<(u32, u32)> = (0..100_000u64).map(|i| ((i * 7919 % 100_003 + 1) as u32, (i * 104_729 % 99_991 + 1) as u32)).collect();
            check!("envelopes[i] = ((7919·i) % 100003 + 1, (104729·i) % 99991 + 1), 100000 envelopes", max_envelopes(&env), 544);
        }

        #[test]
        fn scale_width_pairs() {
            let env: Vec<(u32, u32)> = (0..100_000u32).map(|i| (1 + i / 2, 1 + i / 2)).collect();
            check!("envelopes = [(1, 1), (1, 1), (2, 2), (2, 2), …] (100000 envelopes)", max_envelopes(&env), 50_000);
        }
        """,
    ],
    wrong=dict(
        ties_by_height_ascending="""
            pub fn max_envelopes(envelopes: &[(u32, u32)]) -> usize {
                let mut env = envelopes.to_vec();
                env.sort_unstable();
                let mut tails: Vec<u32> = Vec::new();
                for &(_, h) in &env {
                    let k = tails.partition_point(|&t| t < h);
                    if k == tails.len() {
                        tails.push(h);
                    } else {
                        tails[k] = h;
                    }
                }
                tails.len()
            }
        """,
        quadratic="""
            pub fn max_envelopes(envelopes: &[(u32, u32)]) -> usize {
                let mut env = envelopes.to_vec();
                env.sort_unstable();
                let mut best = vec![1usize; env.len()];
                for i in 0..env.len() {
                    for j in 0..i {
                        if env[j].0 < env[i].0 && env[j].1 < env[i].1 {
                            best[i] = best[i].max(best[j] + 1);
                        }
                    }
                }
                best.into_iter().max().unwrap_or(0)
            }
        """,
        equal_heights_nest="""
            pub fn max_envelopes(envelopes: &[(u32, u32)]) -> usize {
                let mut env = envelopes.to_vec();
                env.sort_unstable_by(|a, b| a.0.cmp(&b.0).then(b.1.cmp(&a.1)));
                let mut tails: Vec<u32> = Vec::new();
                for &(_, h) in &env {
                    let k = tails.partition_point(|&t| t <= h);
                    if k == tails.len() {
                        tails.push(h);
                    } else {
                        tails[k] = h;
                    }
                }
                tails.len()
            }
        """,
    ),
    hints=[("approach", "Sort by width; then a nesting chain is an increasing subsequence of heights. Solve that with the O(n log n) LIS."),
           ("rust", "`sort_unstable_by(|a, b| a.0.cmp(&b.0).then(b.1.cmp(&a.1)))` sorts width ascending and height descending on ties."),
           ("edge case", "Envelopes with the same width can't nest. Sorting their heights descending stops the LIS from using two of them.")],
    notes=("After the sort, an increasing run of heights automatically has increasing widths, and the descending tie-break rules out equal widths. The LIS pass is the tails-and-binary-search method.", "O(n log n)", "O(n)"),
    follow_up="What if envelopes could be rotated, or if you had boxes in three dimensions?",
    related=["D4", "D8"],
))

# ---------------------------------------------------------------- 2-D grids (medium)

P.append(dict(
    slug="unique-paths", title="Unique paths", level="medium", stage="2d-grids", tags=["2-D DP", "rolling row", "Blind 75"],
    companies=["Amazon", "Google", "Meta", "Apple", "Microsoft", "Bloomberg", "Goldman Sachs"],
    teaches=["A grid DP where each cell adds the cell above and the cell to the left.",
             "One rolling row: updating `row[j] += row[j - 1]` in place reads \"above\" and \"left\" at once."],
    statement="""
        A robot starts in the top-left cell of an `m × n` grid and may only move right or down.
        Return how many different paths reach the bottom-right cell.
    """,
    examples=[("m = 3, n = 7", "28"), ("m = 3, n = 2", "3")],
    constraints=["1 ≤ m, n ≤ 100", "the answer fits in a u64"],
    starter="""
        pub fn unique_paths(m: usize, n: usize) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn unique_paths(m: usize, n: usize) -> u64 {
            // row[j] = paths to (i, j). The first row is all 1s (only moves right).
            let mut row = vec![1u64; n];
            for _ in 1..m {
                for j in 1..n {
                    row[j] += row[j - 1]; // above (old row[j]) + left (new row[j - 1])
                }
            }
            row[n - 1]
        }
    """,
    visible=[
        T("leetcode_three_by_seven", "m = 3, n = 7", "unique_paths(3, 7)", "28"),
        T("leetcode_three_by_two", "m = 3, n = 2", "unique_paths(3, 2)", "3"),
        T("one_cell", "m = 1, n = 1", "unique_paths(1, 1)", "1"),
        T("one_row", "m = 1, n = 100", "unique_paths(1, 100)", "1"),
        T("two_by_two", "m = 2, n = 2", "unique_paths(2, 2)", "2"),
    ],
    hidden=[
        T("one_cell", "m = 1, n = 1", "unique_paths(1, 1)", "1"),
        T("one_column", "m = 100, n = 1", "unique_paths(100, 1)", "1"),
        T("two_rows", "m = 2, n = 100", "unique_paths(2, 100)", "100"),
        T("ten_by_ten", "m = 10, n = 10", "unique_paths(10, 10)", "48_620"),
        T("symmetric", "m = 7, n = 3", "unique_paths(7, 3)", "28"),
        T("leetcode_large", "m = 23, n = 12", "unique_paths(23, 12)", "193_536_720"),
        T("thirty_three", "m = 33, n = 33", "unique_paths(33, 33)", "1_832_624_140_942_590_534"),
        T("largest_square", "m = 34, n = 34", "unique_paths(34, 34)", "7_219_428_434_016_265_740"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn count(i: usize, j: usize) -> u64 {
                if i == 0 || j == 0 { 1 } else { count(i - 1, j) + count(i, j - 1) }
            }
            let mut rng = anneal_prelude::Rng::new(1218);
            for _ in 0..300 {
                let m = rng.int(1, 10) as usize;
                let n = rng.int(1, 10) as usize;
                check!(format!("m = {m}, n = {n}"), unique_paths(m, n), count(m - 1, n - 1));
            }
        }

        #[test]
        fn scale_many_grids() {
            // Plain recursion visits every path: about 10¹⁸ of them for 33 × 33.
            let total: u64 = (1..=30).map(|k| unique_paths(k, 30) % 1_000_007).sum();
            check!("sum over m = 1..=30 of unique_paths(m, 30) % 1000007", (total, unique_paths(33, 33)), (12_292_783, 1_832_624_140_942_590_534));
        }
        """,
    ],
    wrong=dict(
        plain_recursion="""
            pub fn unique_paths(m: usize, n: usize) -> u64 {
                if m == 1 || n == 1 { 1 } else { unique_paths(m - 1, n) + unique_paths(m, n - 1) }
            }
        """,
        factorials="""
            pub fn unique_paths(m: usize, n: usize) -> u64 {
                let fact = |k: usize| (1..=k as u64).product::<u64>();
                fact(m + n - 2) / (fact(m - 1) * fact(n - 1))
            }
        """,
        one_row_too_many="""
            pub fn unique_paths(m: usize, n: usize) -> u64 {
                let mut row = vec![1u64; n];
                for _ in 0..m {
                    for j in 1..n {
                        row[j] += row[j - 1];
                    }
                }
                row[n - 1]
            }
        """,
    ),
    hints=[("approach", "paths(i, j) = paths(i - 1, j) + paths(i, j - 1), and every cell in the first row or column has one path."),
           ("rust", "Keep one `Vec<u64>` row. `row[j] += row[j - 1]` adds the new left value to the old above value in place."),
           ("edge case", "The closed form C(m + n - 2, m - 1) is right, but computing it with factorials overflows a `u64` from 21! on.")],
    notes=("Each cell is reached from above or from the left, so its count is the sum of those two. A single row is enough because the update reads the old value (above) and the freshly updated one (left).", "O(m × n)", "O(n)"),
    follow_up="How would you compute C(m + n - 2, m - 1) directly without overflowing?",
    related=["D13"],
))

P.append(dict(
    slug="unique-paths-ii", title="Unique paths II", level="medium", stage="2d-grids", tags=["2-D DP", "rolling row"],
    companies=["Amazon", "Google", "Meta", "Microsoft", "Bloomberg"],
    teaches=["An obstacle cell has 0 paths, and that zero flows on to the cells after it.",
             "Iterating a grid of rows (`&[Vec<u8>]`) with one rolling row."],
    statement="""
        Same robot, but `grid[i][j] == 1` marks an obstacle the robot can't enter (0 is free).
        Return how many paths reach the bottom-right cell. If the start or the end is an obstacle,
        there are none.
    """,
    examples=[("grid = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]", "2")],
    constraints=["1 ≤ m, n ≤ 100", "grid[i][j] is 0 or 1", "the path count to every cell fits in a u64"],
    starter="""
        pub fn unique_paths_with_obstacles(grid: &[Vec<u8>]) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn unique_paths_with_obstacles(grid: &[Vec<u8>]) -> u64 {
            let n = grid.first().map_or(0, |r| r.len());
            // row[j] = paths to (i, j). Seed one path "arriving" at the start.
            let mut row = vec![0u64; n];
            if n > 0 {
                row[0] = 1;
            }
            for cells in grid {
                for j in 0..n {
                    if cells[j] == 1 {
                        row[j] = 0;
                    } else if j > 0 {
                        row[j] += row[j - 1];
                    }
                }
            }
            row.last().copied().unwrap_or(0)
        }
    """,
    visible=[
        T("leetcode_center_rock", "grid = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]", "unique_paths_with_obstacles(&[vec![0, 0, 0], vec![0, 1, 0], vec![0, 0, 0]])", "2"),
        T("leetcode_two_by_two", "grid = [[0, 1], [0, 0]]", "unique_paths_with_obstacles(&[vec![0, 1], vec![0, 0]])", "1"),
        T("one_free_cell", "grid = [[0]]", "unique_paths_with_obstacles(&[vec![0]])", "1"),
        T("one_blocked_cell", "grid = [[1]]", "unique_paths_with_obstacles(&[vec![1]])", "0"),
        T("start_blocked", "grid = [[1, 0], [0, 0]]", "unique_paths_with_obstacles(&[vec![1, 0], vec![0, 0]])", "0"),
        T("end_blocked", "grid = [[0, 0], [0, 1]]", "unique_paths_with_obstacles(&[vec![0, 0], vec![0, 1]])", "0"),
    ],
    hidden=[
        T("one_blocked_cell", "grid = [[1]]", "unique_paths_with_obstacles(&[vec![1]])", "0"),
        T("start_blocked", "grid = [[1, 0], [0, 0]]", "unique_paths_with_obstacles(&[vec![1, 0], vec![0, 0]])", "0"),
        T("first_row_cut_off", "grid = [[0, 1, 0], [0, 0, 0]]", "unique_paths_with_obstacles(&[vec![0, 1, 0], vec![0, 0, 0]])", "1"),
        T("wall", "grid = [[0, 0], [1, 1], [0, 0]]", "unique_paths_with_obstacles(&[vec![0, 0], vec![1, 1], vec![0, 0]])", "0"),
        T("single_row_blocked", "grid = [[0, 0, 1, 0]]", "unique_paths_with_obstacles(&[vec![0, 0, 1, 0]])", "0"),
        T("single_column", "grid = [[0], [0], [0]]", "unique_paths_with_obstacles(&[vec![0], vec![0], vec![0]])", "1"),
        T("single_column_blocked", "grid = [[0], [1], [0]]", "unique_paths_with_obstacles(&[vec![0], vec![1], vec![0]])", "0"),
        T("scattered", "grid = [[0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [1, 0, 0, 0]]",
          "unique_paths_with_obstacles(&[vec![0, 0, 0, 0], vec![0, 1, 0, 0], vec![0, 0, 0, 1], vec![1, 0, 0, 0]])", "3"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn count(g: &[Vec<u8>], i: usize, j: usize) -> u64 {
                if g[i][j] == 1 {
                    return 0;
                }
                if i == 0 && j == 0 {
                    return 1;
                }
                (if i > 0 { count(g, i - 1, j) } else { 0 }) + (if j > 0 { count(g, i, j - 1) } else { 0 })
            }
            let mut rng = anneal_prelude::Rng::new(1219);
            for _ in 0..300 {
                let m = rng.int(1, 7) as usize;
                let n = rng.int(1, 7) as usize;
                let grid: Vec<Vec<u8>> = (0..m).map(|_| (0..n).map(|_| (rng.below(4) == 0) as u8).collect()).collect();
                check!(format!("grid = {grid:?}"), unique_paths_with_obstacles(&grid), count(&grid, m - 1, n - 1));
            }
        }

        #[test]
        fn scale_free_33() {
            let grid = vec![vec![0u8; 33]; 33];
            check!("grid = 33 × 33, no obstacles", unique_paths_with_obstacles(&grid), 1_832_624_140_942_590_534);
        }

        #[test]
        fn scale_rocks_33() {
            let grid: Vec<Vec<u8>> = (0..33usize)
                .map(|i| (0..33usize).map(|j| ((i * 7 + j * 3) % 11 == 5 && (i, j) != (0, 0) && (i, j) != (32, 32)) as u8).collect())
                .collect();
            check!("grid = 33 × 33, rock where (7i + 3j) % 11 == 5", unique_paths_with_obstacles(&grid), 105_440_613_552_200);
        }
        """,
    ],
    wrong=dict(
        edges_always_one="""
            pub fn unique_paths_with_obstacles(grid: &[Vec<u8>]) -> u64 {
                let (m, n) = (grid.len(), grid[0].len());
                let mut paths = vec![vec![0u64; n]; m];
                for i in 0..m {
                    for j in 0..n {
                        paths[i][j] = if grid[i][j] == 1 {
                            0
                        } else if i == 0 || j == 0 {
                            1
                        } else {
                            paths[i - 1][j] + paths[i][j - 1]
                        };
                    }
                }
                paths[m - 1][n - 1]
            }
        """,
        plain_recursion="""
            fn count(g: &[Vec<u8>], i: usize, j: usize) -> u64 {
                if g[i][j] == 1 {
                    return 0;
                }
                if i == 0 && j == 0 {
                    return 1;
                }
                (if i > 0 { count(g, i - 1, j) } else { 0 }) + (if j > 0 { count(g, i, j - 1) } else { 0 })
            }

            pub fn unique_paths_with_obstacles(grid: &[Vec<u8>]) -> u64 {
                count(grid, grid.len() - 1, grid[0].len() - 1)
            }
        """,
    ),
    hints=[("approach", "Same recurrence as Unique paths, except an obstacle cell is 0. Seed the start with 1 (or 0 if it's a rock)."),
           ("rust", "One `Vec<u64>` row: for each cell, set `row[j] = 0` on a rock, else `row[j] += row[j - 1]` for j > 0."),
           ("edge case", "A rock in the first row blocks every cell to its right in that row; don't initialise the first row and column to 1 blindly.")],
    notes=("Rocks contribute 0, and that zero propagates: cells past a rock in the first row or column are unreachable. Seeding row[0] = 1 before the first row handles a rock at the start too.", "O(m × n)", "O(n)"),
    follow_up="What if the robot could also move diagonally, or if some cells cost more to cross?",
    related=["D9"],
))

P.append(dict(
    slug="minimum-path-sum", title="Minimum path sum", level="medium", stage="2d-grids", tags=["2-D DP", "rolling row"],
    companies=["Amazon", "Google", "Meta", "Apple", "Microsoft", "Goldman Sachs"],
    teaches=["The min-cost version of the grid walk: each cell adds its value to the cheaper of above and left.",
             "Seeding a rolling row with `u64::MAX` so the first row only takes from the left."],
    statement="""
        Every cell of a non-empty grid holds a cost. Moving only right or down from the top-left to
        the bottom-right, return the smallest total cost of the cells on the path (both ends
        included).
    """,
    examples=[("grid = [[1, 3, 1], [1, 5, 1], [4, 2, 1]]", "7 (1 → 3 → 1 → 1 → 1)")],
    constraints=["1 ≤ m, n ≤ 1000", "0 ≤ grid[i][j] ≤ 10⁴"],
    starter="""
        pub fn min_path_sum(grid: &[Vec<u32>]) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn min_path_sum(grid: &[Vec<u32>]) -> u64 {
            let n = grid[0].len();
            // best[j] = cheapest path to (i, j). Before the first row only the start is reachable.
            let mut best = vec![u64::MAX; n];
            best[0] = 0;
            for row in grid {
                for j in 0..n {
                    let from = if j > 0 { best[j].min(best[j - 1]) } else { best[0] };
                    best[j] = from + row[j] as u64;
                }
            }
            best[n - 1]
        }
    """,
    visible=[
        T("leetcode_three_by_three", "grid = [[1, 3, 1], [1, 5, 1], [4, 2, 1]]", "min_path_sum(&[vec![1, 3, 1], vec![1, 5, 1], vec![4, 2, 1]])", "7"),
        T("leetcode_two_by_three", "grid = [[1, 2, 3], [4, 5, 6]]", "min_path_sum(&[vec![1, 2, 3], vec![4, 5, 6]])", "12"),
        T("one_cell", "grid = [[5]]", "min_path_sum(&[vec![5]])", "5"),
        T("one_row", "grid = [[1, 2, 3]]", "min_path_sum(&[vec![1, 2, 3]])", "6"),
        T("one_column", "grid = [[1], [2], [3]]", "min_path_sum(&[vec![1], vec![2], vec![3]])", "6"),
    ],
    hidden=[
        T("one_cell", "grid = [[0]]", "min_path_sum(&[vec![0]])", "0"),
        T("zeros", "grid = [[0, 0], [0, 0]]", "min_path_sum(&[vec![0, 0], vec![0, 0]])", "0"),
        T("tie", "grid = [[1, 2], [1, 1]]", "min_path_sum(&[vec![1, 2], vec![1, 1]])", "3"),
        T("winding", "grid = [[1, 1, 9, 9], [5, 1, 9, 9], [5, 9, 9, 9], [1, 1, 1, 1]]",
          "min_path_sum(&[vec![1, 1, 9, 9], vec![5, 1, 9, 9], vec![5, 9, 9, 9], vec![1, 1, 1, 1]])", "15"),
        T("greedy_trap", "grid = 7 × 8 (LeetCode)",
          "min_path_sum(&[vec![1, 4, 8, 6, 2, 2, 1, 7], vec![4, 7, 3, 1, 4, 5, 5, 1], vec![8, 8, 2, 1, 1, 8, 0, 1], vec![8, 9, 2, 9, 8, 0, 8, 9], vec![5, 7, 5, 7, 1, 8, 5, 5], vec![7, 0, 9, 4, 5, 6, 5, 6], vec![4, 9, 9, 7, 9, 1, 9, 0]])", "47"),
        T("long_row", "grid = [[10000; 1000]]", "min_path_sum(&[vec![10_000; 1000]])", "10_000_000"),
        T("past_u32", "grid = 1000 × 1000 of 10000", "min_path_sum(&vec![vec![10_000; 1000]; 1000])", "19_990_000"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn cheapest(g: &[Vec<u32>], i: usize, j: usize) -> u64 {
                let here = g[i][j] as u64;
                match (i, j) {
                    (0, 0) => here,
                    (0, _) => here + cheapest(g, 0, j - 1),
                    (_, 0) => here + cheapest(g, i - 1, 0),
                    _ => here + cheapest(g, i - 1, j).min(cheapest(g, i, j - 1)),
                }
            }
            let mut rng = anneal_prelude::Rng::new(1220);
            for _ in 0..300 {
                let m = rng.int(1, 6) as usize;
                let n = rng.int(1, 6) as usize;
                let grid: Vec<Vec<u32>> = (0..m).map(|_| rng.vec(n, 0, 9)).collect();
                check!(format!("grid = {grid:?}"), min_path_sum(&grid), cheapest(&grid, m - 1, n - 1));
            }
        }

        #[test]
        fn scale_1000() {
            let grid: Vec<Vec<u32>> = (0..1000u32).map(|i| (0..1000u32).map(|j| (i * 31 + j * 17) % 100).collect()).collect();
            check!("grid[i][j] = (31i + 17j) % 100, 1000 × 1000", min_path_sum(&grid), 72_771);
        }
        """,
    ],
    wrong=dict(
        greedy_cheaper_neighbour="""
            pub fn min_path_sum(grid: &[Vec<u32>]) -> u64 {
                let (m, n) = (grid.len(), grid[0].len());
                let (mut i, mut j) = (0, 0);
                let mut total = grid[0][0] as u64;
                while (i, j) != (m - 1, n - 1) {
                    if i == m - 1 {
                        j += 1;
                    } else if j == n - 1 || grid[i + 1][j] <= grid[i][j + 1] {
                        i += 1;
                    } else {
                        j += 1;
                    }
                    total += grid[i][j] as u64;
                }
                total
            }
        """,
        plain_recursion="""
            fn cheapest(g: &[Vec<u32>], i: usize, j: usize) -> u64 {
                let here = g[i][j] as u64;
                match (i, j) {
                    (0, 0) => here,
                    (0, _) => here + cheapest(g, 0, j - 1),
                    (_, 0) => here + cheapest(g, i - 1, 0),
                    _ => here + cheapest(g, i - 1, j).min(cheapest(g, i, j - 1)),
                }
            }

            pub fn min_path_sum(grid: &[Vec<u32>]) -> u64 {
                cheapest(grid, grid.len() - 1, grid[0].len() - 1)
            }
        """,
        first_row_not_summed="""
            pub fn min_path_sum(grid: &[Vec<u32>]) -> u64 {
                let (m, n) = (grid.len(), grid[0].len());
                let mut best = vec![vec![0u64; n]; m];
                for i in 0..m {
                    for j in 0..n {
                        let here = grid[i][j] as u64;
                        best[i][j] = match (i, j) {
                            (0, _) => here,
                            (_, 0) => here + best[i - 1][0],
                            _ => here + best[i - 1][j].min(best[i][j - 1]),
                        };
                    }
                }
                best[m - 1][n - 1]
            }
        """,
    ),
    hints=[("approach", "best(i, j) = grid[i][j] + min(best(i - 1, j), best(i, j - 1)); the first row and column have only one way in."),
           ("rust", "A rolling `Vec<u64>` seeded with `u64::MAX` except `best[0] = 0` makes the first row take only from the left without special cases."),
           ("edge case", "Stepping to the cheaper neighbour each time is not optimal: a cheap step can lead into an expensive region.")],
    notes=("Each cell is entered from above or from the left, so its best cost is its own value plus the cheaper of those two. Sweeping rows top to bottom and cells left to right means both are ready.", "O(m × n)", "O(n)"),
    follow_up="How would you print the path itself, and how would the approach change if moves in all four directions were allowed? (Then it's Dijkstra.)",
    related=["D9"],
))

P.append(dict(
    slug="triangle", title="Triangle", level="medium", stage="2d-grids", tags=["2-D DP", "bottom-up"],
    companies=["Amazon", "Google", "Apple", "Microsoft", "Bloomberg"],
    teaches=["Solving bottom-up so every cell has exactly two choices below it and the answer lands at the top.",
             "Reusing one `Vec` that shrinks by one live cell per row."],
    statement="""
        Walk from the top of a triangle of numbers to the bottom row. From position `c` in one row
        you may step to position `c` or `c + 1` in the next. Return the smallest possible sum of
        the numbers on the walk.
    """,
    examples=[("triangle = [[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]", "11 (2 + 3 + 5 + 1)")],
    constraints=["1 ≤ triangle.len() ≤ 2000", "triangle[r].len() == r + 1", "-10⁴ ≤ triangle[r][c] ≤ 10⁴"],
    starter="""
        pub fn minimum_total(triangle: &[Vec<i32>]) -> i64 {
            todo!()
        }
    """,
    solution="""
        pub fn minimum_total(triangle: &[Vec<i32>]) -> i64 {
            // below[c] = the cheapest walk from (r, c) down to the bottom, filled from the last row up.
            let mut below: Vec<i64> = triangle[triangle.len() - 1].iter().map(|&x| x as i64).collect();
            for row in triangle.iter().rev().skip(1) {
                for (c, &x) in row.iter().enumerate() {
                    below[c] = x as i64 + below[c].min(below[c + 1]);
                }
            }
            below[0]
        }
    """,
    visible=[
        T("leetcode_four_rows", "triangle = [[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]", "minimum_total(&[vec![2], vec![3, 4], vec![6, 5, 7], vec![4, 1, 8, 3]])", "11"),
        T("leetcode_one_row", "triangle = [[-10]]", "minimum_total(&[vec![-10]])", "-10"),
        T("two_rows", "triangle = [[1], [2, 3]]", "minimum_total(&[vec![1], vec![2, 3]])", "3"),
        T("cheap_first_step_is_a_trap", "triangle = [[1], [2, 3], [100, 100, 1]]", "minimum_total(&[vec![1], vec![2, 3], vec![100, 100, 1]])", "5"),
        T("steps_must_be_adjacent", "triangle = [[-1], [2, 3], [1, -1, -3]]", "minimum_total(&[vec![-1], vec![2, 3], vec![1, -1, -3]])", "-1"),
    ],
    hidden=[
        T("one_row", "triangle = [[7]]", "minimum_total(&[vec![7]])", "7"),
        T("zeros", "triangle = [[0], [0, 0]]", "minimum_total(&[vec![0], vec![0, 0]])", "0"),
        T("greedy_trap", "triangle = [[1], [2, 3], [100, 100, 1]]", "minimum_total(&[vec![1], vec![2, 3], vec![100, 100, 1]])", "5"),
        T("not_row_minimums", "triangle = [[-1], [2, 3], [1, -1, -3]]", "minimum_total(&[vec![-1], vec![2, 3], vec![1, -1, -3]])", "-1"),
        T("all_max", "triangle = [[10000], [10000, 10000]]", "minimum_total(&[vec![10_000], vec![10_000, 10_000]])", "20_000"),
        T("all_min", "triangle = [[-10000], [-10000, -10000], [-10000, -10000, -10000]]",
          "minimum_total(&[vec![-10_000], vec![-10_000, -10_000], vec![-10_000, -10_000, -10_000]])", "-30_000"),
        T("deep_negative", "triangle = 1000 rows of -10000", "minimum_total(&(1..=1000).map(|r| vec![-10_000; r]).collect::<Vec<_>>())", "-10_000_000"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn walk(t: &[Vec<i32>], r: usize, c: usize) -> i64 {
                let here = t[r][c] as i64;
                if r + 1 == t.len() { here } else { here + walk(t, r + 1, c).min(walk(t, r + 1, c + 1)) }
            }
            let mut rng = anneal_prelude::Rng::new(1221);
            for _ in 0..300 {
                let rows = rng.int(1, 10) as usize;
                let tri: Vec<Vec<i32>> = (1..=rows).map(|len| rng.vec(len, -9, 9)).collect();
                check!(format!("triangle = {tri:?}"), minimum_total(&tri), walk(&tri, 0, 0));
            }
        }

        #[test]
        fn scale_2000_rows() {
            let tri: Vec<Vec<i32>> = (0..2000i32).map(|r| (0..=r).map(|c| (r * 7 + c * 13) % 201 - 100).collect()).collect();
            check!("triangle[r][c] = (7r + 13c) % 201 - 100, 2000 rows", minimum_total(&tri), -58_605);
        }
        """,
    ],
    wrong=dict(
        greedy_smaller_child="""
            pub fn minimum_total(triangle: &[Vec<i32>]) -> i64 {
                let mut c = 0;
                let mut total = triangle[0][0] as i64;
                for row in &triangle[1..] {
                    if row[c + 1] < row[c] {
                        c += 1;
                    }
                    total += row[c] as i64;
                }
                total
            }
        """,
        row_minimums="""
            pub fn minimum_total(triangle: &[Vec<i32>]) -> i64 {
                triangle.iter().map(|row| *row.iter().min().unwrap() as i64).sum()
            }
        """,
        plain_recursion="""
            fn walk(t: &[Vec<i32>], r: usize, c: usize) -> i64 {
                let here = t[r][c] as i64;
                if r + 1 == t.len() { here } else { here + walk(t, r + 1, c).min(walk(t, r + 1, c + 1)) }
            }

            pub fn minimum_total(triangle: &[Vec<i32>]) -> i64 {
                walk(triangle, 0, 0)
            }
        """,
    ),
    hints=[("approach", "Go bottom-up: the best walk from (r, c) is triangle[r][c] plus the better of the best walks from (r + 1, c) and (r + 1, c + 1)."),
           ("rust", "Start `below` as the last row (as `i64`), then for each row above update `below[c]` left to right; `below[c + 1]` hasn't been overwritten yet."),
           ("edge case", "Stepping to the smaller child greedily fails when a small number leads to a big one below.")],
    notes=("Bottom-up, every cell has exactly two children and the answer ends up at below[0]; top-down you would need to take a min over the whole last row. Each row reuses the same `Vec`.", "O(n²) for n rows (every cell once)", "O(n)"),
    follow_up="Can you do it in O(1) extra space by overwriting the input, and when would that be acceptable?",
    related=["D11"],
))

P.append(dict(
    slug="maximal-square", title="Maximal square", level="medium", stage="2d-grids", tags=["2-D DP", "rolling row"],
    companies=["Google", "Amazon", "Meta", "Apple", "Microsoft", "Bloomberg"],
    teaches=["A square ending at (i, j) is limited by the smallest square above, to the left and diagonally up-left.",
             "Keeping the up-left value in a variable while updating one row in place."],
    statement="""
        `matrix` is a grid of `'0'` and `'1'` characters, one string per row. Return the area of
        the largest square made only of `'1'`s.
    """,
    examples=[("matrix = [\"10100\", \"10111\", \"11111\", \"10010\"]", "4 (a 2 × 2 square)")],
    constraints=["0 ≤ rows, columns ≤ 1000", "every row has the same length and holds only '0' and '1'"],
    starter="""
        pub fn maximal_square(matrix: &[&str]) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn maximal_square(matrix: &[&str]) -> usize {
            let cols = matrix.first().map_or(0, |r| r.len());
            // side[j + 1] = the largest all-'1' square whose bottom-right corner is (i, j).
            let mut side = vec![0usize; cols + 1];
            let mut best = 0;
            for row in matrix {
                let mut up_left = 0;
                for (j, &b) in row.as_bytes().iter().enumerate() {
                    let up = side[j + 1];
                    side[j + 1] = if b == b'1' { 1 + up_left.min(up).min(side[j]) } else { 0 };
                    up_left = up;
                    best = best.max(side[j + 1]);
                }
            }
            best * best
        }
    """,
    visible=[
        T("leetcode_four_rows", "matrix = [\"10100\", \"10111\", \"11111\", \"10010\"]", "maximal_square(&[\"10100\", \"10111\", \"11111\", \"10010\"])", "4"),
        T("leetcode_diagonal", "matrix = [\"01\", \"10\"]", "maximal_square(&[\"01\", \"10\"])", "1"),
        T("leetcode_zero", "matrix = [\"0\"]", "maximal_square(&[\"0\"])", "0"),
        T("empty", "matrix = []", "maximal_square(&[])", "0"),
        T("area_not_side", "matrix = [\"111\", \"111\", \"111\"]", "maximal_square(&[\"111\", \"111\", \"111\"])", "9"),
    ],
    hidden=[
        T("empty", "matrix = []", "maximal_square(&[])", "0"),
        T("single_one", "matrix = [\"1\"]", "maximal_square(&[\"1\"])", "1"),
        T("row_of_zeros", "matrix = [\"0000\"]", "maximal_square(&[\"0000\"])", "0"),
        T("rectangle", "matrix = [\"1111\", \"1111\"]", "maximal_square(&[\"1111\", \"1111\"])", "4"),
        T("hole_in_the_middle", "matrix = [\"111\", \"101\", \"111\"]", "maximal_square(&[\"111\", \"101\", \"111\"])", "1"),
        T("rounded_corners", "matrix = [\"0110\", \"1111\", \"1111\", \"0110\"]", "maximal_square(&[\"0110\", \"1111\", \"1111\", \"0110\"])", "4"),
        T("square_at_the_edge", "matrix = [\"1110\", \"1110\", \"1101\"]", "maximal_square(&[\"1110\", \"1110\", \"1101\"])", "4"),
        T("bottom_right", "matrix = [\"11110\", \"11110\", \"11011\", \"11111\"]", "maximal_square(&[\"11110\", \"11110\", \"11011\", \"11111\"])", "4"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1222);
            for _ in 0..300 {
                let m = rng.int(0, 6) as usize;
                let n = rng.int(1, 6) as usize;
                let rows: Vec<String> = (0..m).map(|_| rng.string(n, "1110")).collect();
                let refs: Vec<&str> = rows.iter().map(|r| r.as_str()).collect();
                let g: Vec<&[u8]> = rows.iter().map(|r| r.as_bytes()).collect();
                let mut want = 0;
                for i in 0..m {
                    for j in 0..n {
                        for k in 1..=(m - i).min(n - j) {
                            if (i..i + k).all(|r| (j..j + k).all(|c| g[r][c] == b'1')) {
                                want = want.max(k * k);
                            }
                        }
                    }
                }
                check!(format!("matrix = {rows:?}"), maximal_square(&refs), want);
            }
        }

        #[test]
        fn scale_all_ones() {
            let rows = vec!["1".repeat(1000); 1000];
            let refs: Vec<&str> = rows.iter().map(|r| r.as_str()).collect();
            check!("matrix = 1000 × 1000 of '1'", maximal_square(&refs), 1_000_000);
        }

        #[test]
        fn scale_scattered_zeros() {
            let rows: Vec<String> = (0..1000usize).map(|i| (0..1000usize).map(|j| if (i * i + j * 7) % 97 == 0 { '0' } else { '1' }).collect()).collect();
            let refs: Vec<&str> = rows.iter().map(|r| r.as_str()).collect();
            check!("matrix = 1000 × 1000, '0' where (i² + 7j) % 97 == 0", maximal_square(&refs), 576);
        }
        """,
    ],
    wrong=dict(
        returns_the_side="""
            pub fn maximal_square(matrix: &[&str]) -> usize {
                let cols = matrix.first().map_or(0, |r| r.len());
                let mut side = vec![0usize; cols + 1];
                let mut best = 0;
                for row in matrix {
                    let mut up_left = 0;
                    for (j, &b) in row.as_bytes().iter().enumerate() {
                        let up = side[j + 1];
                        side[j + 1] = if b == b'1' { 1 + up_left.min(up).min(side[j]) } else { 0 };
                        up_left = up;
                        best = best.max(side[j + 1]);
                    }
                }
                best
            }
        """,
        forgets_the_diagonal="""
            pub fn maximal_square(matrix: &[&str]) -> usize {
                let cols = matrix.first().map_or(0, |r| r.len());
                let mut side = vec![0usize; cols + 1];
                let mut best = 0;
                for row in matrix {
                    for (j, &b) in row.as_bytes().iter().enumerate() {
                        side[j + 1] = if b == b'1' { 1 + side[j + 1].min(side[j]) } else { 0 };
                        best = best.max(side[j + 1]);
                    }
                }
                best * best
            }
        """,
        grow_every_square="""
            pub fn maximal_square(matrix: &[&str]) -> usize {
                let g: Vec<&[u8]> = matrix.iter().map(|r| r.as_bytes()).collect();
                let (m, n) = (g.len(), g.first().map_or(0, |r| r.len()));
                let mut best = 0;
                for i in 0..m {
                    for j in 0..n {
                        let mut k = 1;
                        while i + k <= m && j + k <= n && (i..i + k).all(|r| (j..j + k).all(|c| g[r][c] == b'1')) {
                            best = best.max(k);
                            k += 1;
                        }
                    }
                }
                best * best
            }
        """,
    ),
    hints=[("approach", "side(i, j) = 1 + min(side(i - 1, j), side(i, j - 1), side(i - 1, j - 1)) when the cell is '1', else 0. The answer is the largest side, squared."),
           ("rust", "Compare `row.as_bytes()[j]` with `b'1'`. In one rolling row, save the old `side[j + 1]` before overwriting it: it is the next cell's up-left."),
           ("edge case", "The question asks for the area, not the side. A missing diagonal cell must shrink the square: [\"111\", \"101\", \"111\"] → 1.")],
    notes=("A square with corner (i, j) of side k needs squares of side k - 1 ending above, to the left and up-left, so the smallest of the three limits it. The row is updated in place with one saved value for the diagonal.", "O(m × n)", "O(n)"),
    follow_up="How would you find the largest rectangle of 1s instead? (Histogram + monotonic stack per row.)",
    related=["D3"],
))

P.append(dict(
    slug="dungeon-game", title="Dungeon game", level="hard", stage="2d-grids", tags=["2-D DP", "backwards DP"],
    companies=["Google", "Amazon", "Microsoft", "Meta"],
    teaches=["Solving from the goal backwards when the constraint (health never below 1) depends on the future, not the past.",
             "Clamping with `.max(1)` at every step."],
    statement="""
        A knight starts in the top-left room of a dungeon and must reach the princess in the
        bottom-right room, moving only right or down. Each room changes his health by
        `dungeon[i][j]` (negative hurts, positive heals), including the first and last rooms. If
        his health ever drops to 0 or below, he dies. Return the least starting health that gets
        him through.
    """,
    examples=[("dungeon = [[-2, -3, 3], [-5, -10, 1], [10, 30, -5]]", "7 (right, right, down, down)")],
    constraints=["1 ≤ m, n ≤ 500", "-1000 ≤ dungeon[i][j] ≤ 1000"],
    starter="""
        pub fn calculate_minimum_hp(dungeon: &[Vec<i32>]) -> i64 {
            todo!()
        }
    """,
    solution="""
        pub fn calculate_minimum_hp(dungeon: &[Vec<i32>]) -> i64 {
            let n = dungeon[0].len();
            // need[j] = the least health to enter room (i, j) and survive to the end.
            // Extra slot n and the "row below" start at MAX, except the princess's exit.
            let mut need = vec![i64::MAX; n + 1];
            need[n - 1] = 1;
            for row in dungeon.iter().rev() {
                for j in (0..n).rev() {
                    let next = need[j].min(need[j + 1]); // down or right
                    need[j] = (next - row[j] as i64).max(1);
                }
            }
            need[0]
        }
    """,
    visible=[
        T("leetcode_three_by_three", "dungeon = [[-2, -3, 3], [-5, -10, 1], [10, 30, -5]]", "calculate_minimum_hp(&[vec![-2, -3, 3], vec![-5, -10, 1], vec![10, 30, -5]])", "7"),
        T("leetcode_one_room", "dungeon = [[0]]", "calculate_minimum_hp(&[vec![0]])", "1"),
        T("healing_room", "dungeon = [[100]] (health must start at least 1)", "calculate_minimum_hp(&[vec![100]])", "1"),
        T("hurting_room", "dungeon = [[-5]]", "calculate_minimum_hp(&[vec![-5]])", "6"),
        T("biggest_sum_is_not_safest", "dungeon = [[3, -20, 30], [-3, 4, 0]]", "calculate_minimum_hp(&[vec![3, -20, 30], vec![-3, 4, 0]])", "1"),
    ],
    hidden=[
        T("one_room", "dungeon = [[0]]", "calculate_minimum_hp(&[vec![0]])", "1"),
        T("known_trap", "dungeon = [[1, -3, 3], [0, -2, 0], [-3, -3, -3]]", "calculate_minimum_hp(&[vec![1, -3, 3], vec![0, -2, 0], vec![-3, -3, -3]])", "3"),
        T("avoid_the_pit", "dungeon = [[0, 5], [-1000, 0]]", "calculate_minimum_hp(&[vec![0, 5], vec![-1000, 0]])", "1"),
        T("heal_comes_too_late", "dungeon = [[1, -2, 3], [2, -2, -2]]", "calculate_minimum_hp(&[vec![1, -2, 3], vec![2, -2, -2]])", "2"),
        T("one_row", "dungeon = [[-1000, -1000, -1000]]", "calculate_minimum_hp(&[vec![-1000, -1000, -1000]])", "3001"),
        T("one_column", "dungeon = [[2], [1]]", "calculate_minimum_hp(&[vec![2], vec![1]])", "1"),
        T("last_room_hurts", "dungeon = [[0, 0, 0], [1, 1, -1]]", "calculate_minimum_hp(&[vec![0, 0, 0], vec![1, 1, -1]])", "1"),
        T("worst_case", "dungeon = 500 × 500 of -1000", "calculate_minimum_hp(&vec![vec![-1000; 500]; 500])", "999_001"),
        """
        #[test]
        fn random_vs_brute_force() {
            // Try every path; each needs 1 - (its lowest running total), at least 1.
            fn walk(d: &[Vec<i32>], i: usize, j: usize, sum: i64, low: i64, best: &mut i64) {
                let sum = sum + d[i][j] as i64;
                let low = low.min(sum);
                if i + 1 == d.len() && j + 1 == d[0].len() {
                    *best = (*best).min((1 - low).max(1));
                    return;
                }
                if i + 1 < d.len() {
                    walk(d, i + 1, j, sum, low, best);
                }
                if j + 1 < d[0].len() {
                    walk(d, i, j + 1, sum, low, best);
                }
            }
            let mut rng = anneal_prelude::Rng::new(1223);
            for _ in 0..300 {
                let m = rng.int(1, 5) as usize;
                let n = rng.int(1, 5) as usize;
                let d: Vec<Vec<i32>> = (0..m).map(|_| rng.vec(n, -10, 10)).collect();
                let mut want = i64::MAX;
                walk(&d, 0, 0, 0, i64::MAX, &mut want);
                check!(format!("dungeon = {d:?}"), calculate_minimum_hp(&d), want);
            }
        }

        #[test]
        fn scale_500() {
            let d: Vec<Vec<i32>> = (0..500i32).map(|i| (0..500i32).map(|j| (i * 37 + j * 91) % 2001 - 1000).collect()).collect();
            check!("dungeon[i][j] = (37i + 91j) % 2001 - 1000, 500 × 500", calculate_minimum_hp(&d), 5996);
        }
        """,
    ],
    wrong=dict(
        forward_largest_sum="""
            pub fn calculate_minimum_hp(dungeon: &[Vec<i32>]) -> i64 {
                let (m, n) = (dungeon.len(), dungeon[0].len());
                // (running sum, lowest running sum) along the path with the larger sum.
                let mut best = vec![vec![(0i64, 0i64); n]; m];
                for i in 0..m {
                    for j in 0..n {
                        let prev = match (i, j) {
                            (0, 0) => (0, 0),
                            (0, _) => best[0][j - 1],
                            (_, 0) => best[i - 1][0],
                            _ => if best[i - 1][j].0 >= best[i][j - 1].0 { best[i - 1][j] } else { best[i][j - 1] },
                        };
                        let sum = prev.0 + dungeon[i][j] as i64;
                        best[i][j] = (sum, prev.1.min(sum));
                    }
                }
                1 - best[m - 1][n - 1].1
            }
        """,
        no_clamp="""
            pub fn calculate_minimum_hp(dungeon: &[Vec<i32>]) -> i64 {
                let n = dungeon[0].len();
                let mut need = vec![i64::MAX; n + 1];
                need[n - 1] = 1;
                for row in dungeon.iter().rev() {
                    for j in (0..n).rev() {
                        let next = need[j].min(need[j + 1]);
                        need[j] = next - row[j] as i64;
                    }
                }
                need[0].max(1)
            }
        """,
        plain_recursion="""
            fn need(d: &[Vec<i32>], i: usize, j: usize) -> i64 {
                let (m, n) = (d.len(), d[0].len());
                let next = if i + 1 == m && j + 1 == n {
                    1
                } else {
                    let down = if i + 1 < m { need(d, i + 1, j) } else { i64::MAX };
                    let right = if j + 1 < n { need(d, i, j + 1) } else { i64::MAX };
                    down.min(right)
                };
                (next - d[i][j] as i64).max(1)
            }

            pub fn calculate_minimum_hp(dungeon: &[Vec<i32>]) -> i64 {
                need(dungeon, 0, 0)
            }
        """,
    ),
    hints=[("approach", "Work backwards: need(i, j) = max(1, min(need(i + 1, j), need(i, j + 1)) - dungeon[i][j]). The princess's room needs 1 after its effect."),
           ("rust", "A rolling `Vec<i64>` of width n + 1 filled with `i64::MAX`, with the slot below the princess set to 1, avoids edge cases; walk rows and columns in reverse."),
           ("edge case", "Going forwards and keeping the path with the biggest total fails: a path can end rich but dip too low on the way. Health must also never be required below 1.")],
    notes=("Forwards, a cell would need two numbers (current health and the lowest point) and neither dominates. Backwards, one number suffices: the least health on entry. The `.max(1)` says that a big heal later can't pay for dying now.", "O(m × n)", "O(n)"),
    follow_up="Why doesn't a forward DP work here? Give a small grid where it fails.",
    related=["D4"],
))

# ---------------------------------------------------------------- Strings (medium)

P.append(dict(
    slug="longest-common-subsequence", title="Longest common subsequence", level="medium", stage="strings", tags=["2-D DP", "as_bytes", "Blind 75"],
    companies=["Amazon", "Google", "Meta", "Microsoft", "Apple", "Bloomberg"],
    teaches=["The classic two-string table: `dp[i][j]` answers the question for `a[..i]` and `b[..j]`.",
             "Two rows and `std::mem::swap` instead of the full table."],
    statement="""
        Return the length of the longest sequence of characters that appears, in order but not
        necessarily next to each other, in both `a` and `b`.
    """,
    examples=[("a = \"abcde\", b = \"ace\"", "3 (\"ace\")")],
    constraints=["0 ≤ a.len(), b.len() ≤ 2000", "a and b are ASCII lowercase letters"],
    starter="""
        pub fn longest_common_subsequence(a: &str, b: &str) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn longest_common_subsequence(a: &str, b: &str) -> usize {
            let (a, b) = (a.as_bytes(), b.as_bytes());
            // prev[j] = LCS of a[..i] and b[..j]; cur becomes row i + 1.
            let mut prev = vec![0usize; b.len() + 1];
            let mut cur = vec![0usize; b.len() + 1];
            for &x in a {
                for (j, &y) in b.iter().enumerate() {
                    cur[j + 1] = if x == y { prev[j] + 1 } else { prev[j + 1].max(cur[j]) };
                }
                std::mem::swap(&mut prev, &mut cur);
            }
            prev[b.len()]
        }
    """,
    visible=[
        T("leetcode_ace", "a = \"abcde\", b = \"ace\"", "longest_common_subsequence(\"abcde\", \"ace\")", "3"),
        T("leetcode_same", "a = \"abc\", b = \"abc\"", "longest_common_subsequence(\"abc\", \"abc\")", "3"),
        T("leetcode_nothing_shared", "a = \"abc\", b = \"def\"", "longest_common_subsequence(\"abc\", \"def\")", "0"),
        T("empty", "a = \"\", b = \"abc\"", "longest_common_subsequence(\"\", \"abc\")", "0"),
        T("order_matters", "a = \"abc\", b = \"cba\"", "longest_common_subsequence(\"abc\", \"cba\")", "1"),
        T("gaps_allowed", "a = \"abcxdef\", b = \"abcydef\"", "longest_common_subsequence(\"abcxdef\", \"abcydef\")", "6"),
    ],
    hidden=[
        T("both_empty", "a = \"\", b = \"\"", "longest_common_subsequence(\"\", \"\")", "0"),
        T("second_empty", "a = \"abc\", b = \"\"", "longest_common_subsequence(\"abc\", \"\")", "0"),
        T("single_match", "a = \"a\", b = \"a\"", "longest_common_subsequence(\"a\", \"a\")", "1"),
        T("repeats", "a = \"aaaa\", b = \"aa\"", "longest_common_subsequence(\"aaaa\", \"aa\")", "2"),
        T("first_match_is_wrong", "a = \"xab\", b = \"abx\"", "longest_common_subsequence(\"xab\", \"abx\")", "2"),
        T("short_second", "a = \"bl\", b = \"yby\"", "longest_common_subsequence(\"bl\", \"yby\")", "1"),
        T("leetcode_mixed", "a = \"ezupkr\", b = \"ubmrapg\"", "longest_common_subsequence(\"ezupkr\", \"ubmrapg\")", "2"),
        T("leetcode_mixed_longer", "a = \"oxcpqrsvwf\", b = \"shmtulqrypy\"", "longest_common_subsequence(\"oxcpqrsvwf\", \"shmtulqrypy\")", "2"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn is_subsequence(small: &[u8], big: &[u8]) -> bool {
                let mut it = big.iter();
                small.iter().all(|c| it.any(|d| d == c))
            }
            let mut rng = anneal_prelude::Rng::new(1224);
            for _ in 0..300 {
                let (la, lb) = (rng.below(9), rng.below(9));
                let a = rng.string(la, "abc");
                let b = rng.string(lb, "abc");
                let ab = a.as_bytes();
                let mut want = 0;
                for mask in 0u32..(1 << la) {
                    let picked: Vec<u8> = (0..la).filter(|&i| mask >> i & 1 == 1).map(|i| ab[i]).collect();
                    if is_subsequence(&picked, b.as_bytes()) {
                        want = want.max(picked.len());
                    }
                }
                check!(format!("a = {a:?}, b = {b:?}"), longest_common_subsequence(&a, &b), want);
            }
        }

        #[test]
        fn scale_2000() {
            let a: String = (0..2000u64).map(|i| (b'a' + (i * 7919 % 26) as u8) as char).collect();
            let b: String = (0..2000u64).map(|i| (b'a' + ((i * 104_729 + 13) % 26) as u8) as char).collect();
            check!("a[i] = 'a' + (7919·i) % 26, b[i] = 'a' + (104729·i + 13) % 26, 2000 each", longest_common_subsequence(&a, &b), 615);
        }
        """,
    ],
    wrong=dict(
        common_substring="""
            pub fn longest_common_subsequence(a: &str, b: &str) -> usize {
                let (a, b) = (a.as_bytes(), b.as_bytes());
                let mut prev = vec![0usize; b.len() + 1];
                let mut best = 0;
                for &x in a {
                    let mut cur = vec![0usize; b.len() + 1];
                    for (j, &y) in b.iter().enumerate() {
                        if x == y {
                            cur[j + 1] = prev[j] + 1;
                            best = best.max(cur[j + 1]);
                        }
                    }
                    prev = cur;
                }
                best
            }
        """,
        greedy_first_match="""
            pub fn longest_common_subsequence(a: &str, b: &str) -> usize {
                let b = b.as_bytes();
                let (mut j, mut count) = (0, 0);
                for &x in a.as_bytes() {
                    if let Some(k) = b[j..].iter().position(|&y| y == x) {
                        j += k + 1;
                        count += 1;
                    }
                }
                count
            }
        """,
        plain_recursion="""
            fn lcs(a: &[u8], b: &[u8]) -> usize {
                match (a, b) {
                    ([], _) | (_, []) => 0,
                    ([x, ra @ ..], [y, rb @ ..]) if x == y => 1 + lcs(ra, rb),
                    ([_, ra @ ..], [_, rb @ ..]) => lcs(ra, b).max(lcs(a, rb)),
                }
            }

            pub fn longest_common_subsequence(a: &str, b: &str) -> usize {
                lcs(a.as_bytes(), b.as_bytes())
            }
        """,
    ),
    hints=[("approach", "dp[i][j] = dp[i - 1][j - 1] + 1 if a[i - 1] == b[j - 1], else max(dp[i - 1][j], dp[i][j - 1])."),
           ("rust", "Index `a.as_bytes()` and `b.as_bytes()`. Keep two rows of length b.len() + 1 and `std::mem::swap` them after each character of `a`."),
           ("edge case", "Matching each character of `a` to its first occurrence in `b` is greedy and misses better pairings: \"xab\" and \"abx\" share \"ab\".")],
    notes=("If the last characters match they end the LCS together; otherwise one of them isn't in it, so drop either and take the better. Only the previous row is needed.", "O(n × m)", "O(m)"),
    follow_up="How would you recover the subsequence itself, and how much of the table do you need for that?",
    related=["S2", "D2"],
))

P.append(dict(
    slug="delete-operation-for-two-strings", title="Delete operation for two strings", level="medium", stage="strings", tags=["2-D DP", "LCS"],
    companies=["Google", "Amazon", "Microsoft"],
    teaches=["Reusing LCS: what survives the deletions is a common subsequence.", "Recognising when a new problem is an old table read differently."],
    statement="""
        In one step you delete one character from either string. Return the fewest steps that
        make `a` and `b` equal.
    """,
    examples=[("a = \"sea\", b = \"eat\"", "2 (delete 's' from a and 't' from b)")],
    constraints=["0 ≤ a.len(), b.len() ≤ 2000", "a and b are ASCII lowercase letters"],
    starter="""
        pub fn min_distance(a: &str, b: &str) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn min_distance(a: &str, b: &str) -> usize {
            let (x, y) = (a.as_bytes(), b.as_bytes());
            let mut prev = vec![0usize; y.len() + 1];
            let mut cur = vec![0usize; y.len() + 1];
            for &p in x {
                for (j, &q) in y.iter().enumerate() {
                    cur[j + 1] = if p == q { prev[j] + 1 } else { prev[j + 1].max(cur[j]) };
                }
                std::mem::swap(&mut prev, &mut cur);
            }
            // Keep the longest common subsequence; delete everything else.
            let lcs = prev[y.len()];
            x.len() + y.len() - 2 * lcs
        }
    """,
    visible=[
        T("leetcode_sea_eat", "a = \"sea\", b = \"eat\"", "min_distance(\"sea\", \"eat\")", "2"),
        T("leetcode_leetcode", "a = \"leetcode\", b = \"etco\"", "min_distance(\"leetcode\", \"etco\")", "4"),
        T("empty", "a = \"\", b = \"abc\"", "min_distance(\"\", \"abc\")", "3"),
        T("already_equal", "a = \"abc\", b = \"abc\"", "min_distance(\"abc\", \"abc\")", "0"),
        T("no_replacing", "a = \"a\", b = \"b\" (delete both)", "min_distance(\"a\", \"b\")", "2"),
    ],
    hidden=[
        T("both_empty", "a = \"\", b = \"\"", "min_distance(\"\", \"\")", "0"),
        T("second_empty", "a = \"abc\", b = \"\"", "min_distance(\"abc\", \"\")", "3"),
        T("nothing_shared", "a = \"abc\", b = \"def\"", "min_distance(\"abc\", \"def\")", "6"),
        T("reversed", "a = \"abc\", b = \"cba\"", "min_distance(\"abc\", \"cba\")", "4"),
        T("swap", "a = \"ab\", b = \"ba\"", "min_distance(\"ab\", \"ba\")", "2"),
        T("repeats", "a = \"aaaa\", b = \"aa\"", "min_distance(\"aaaa\", \"aa\")", "2"),
        T("mixed", "a = \"ezupkr\", b = \"ubmrapg\"", "min_distance(\"ezupkr\", \"ubmrapg\")", "9"),
        T("one_letter_differs", "a = \"abcxdef\", b = \"abcydef\"", "min_distance(\"abcxdef\", \"abcydef\")", "2"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn dist(a: &[u8], b: &[u8]) -> usize {
                match (a, b) {
                    ([], _) => b.len(),
                    (_, []) => a.len(),
                    ([x, ra @ ..], [y, rb @ ..]) if x == y => dist(ra, rb),
                    ([_, ra @ ..], [_, rb @ ..]) => 1 + dist(ra, b).min(dist(a, rb)),
                }
            }
            let mut rng = anneal_prelude::Rng::new(1225);
            for _ in 0..300 {
                let (la, lb) = (rng.below(8), rng.below(8));
                let a = rng.string(la, "abc");
                let b = rng.string(lb, "abc");
                check!(format!("a = {a:?}, b = {b:?}"), min_distance(&a, &b), dist(a.as_bytes(), b.as_bytes()));
            }
        }

        #[test]
        fn scale_2000() {
            let a: String = (0..2000u64).map(|i| (b'a' + (i * 7919 % 26) as u8) as char).collect();
            let b: String = (0..2000u64).map(|i| (b'a' + ((i * 104_729 + 13) % 26) as u8) as char).collect();
            check!("a[i] = 'a' + (7919·i) % 26, b[i] = 'a' + (104729·i + 13) % 26, 2000 each", min_distance(&a, &b), 2770);
        }
        """,
    ],
    wrong=dict(
        allows_replacing="""
            pub fn min_distance(a: &str, b: &str) -> usize {
                let (x, y) = (a.as_bytes(), b.as_bytes());
                let mut prev: Vec<usize> = (0..=y.len()).collect();
                let mut cur = vec![0usize; y.len() + 1];
                for (i, &p) in x.iter().enumerate() {
                    cur[0] = i + 1;
                    for (j, &q) in y.iter().enumerate() {
                        cur[j + 1] = if p == q { prev[j] } else { 1 + prev[j].min(prev[j + 1]).min(cur[j]) };
                    }
                    std::mem::swap(&mut prev, &mut cur);
                }
                prev[y.len()]
            }
        """,
        deletes_from_one_side="""
            pub fn min_distance(a: &str, b: &str) -> usize {
                let (x, y) = (a.as_bytes(), b.as_bytes());
                let mut prev = vec![0usize; y.len() + 1];
                let mut cur = vec![0usize; y.len() + 1];
                for &p in x {
                    for (j, &q) in y.iter().enumerate() {
                        cur[j + 1] = if p == q { prev[j] + 1 } else { prev[j + 1].max(cur[j]) };
                    }
                    std::mem::swap(&mut prev, &mut cur);
                }
                x.len().max(y.len()) - prev[y.len()]
            }
        """,
        plain_recursion="""
            fn dist(a: &[u8], b: &[u8]) -> usize {
                match (a, b) {
                    ([], _) => b.len(),
                    (_, []) => a.len(),
                    ([x, ra @ ..], [y, rb @ ..]) if x == y => dist(ra, rb),
                    ([_, ra @ ..], [_, rb @ ..]) => 1 + dist(ra, b).min(dist(a, rb)),
                }
            }

            pub fn min_distance(a: &str, b: &str) -> usize {
                dist(a.as_bytes(), b.as_bytes())
            }
        """,
    ),
    hints=[("approach", "The characters that survive form a common subsequence, so keep the longest one: the answer is len(a) + len(b) - 2·LCS."),
           ("rust", "Reuse the two-row LCS loop over `as_bytes()`, then do the subtraction in `usize` (it can't go negative)."),
           ("edge case", "Only deletions count: \"a\" and \"b\" need 2 steps, not 1 replacement.")],
    notes=("Deleting down to a common string is the same as choosing a common subsequence to keep; the longest one needs the fewest deletions. A direct DP (1 + min of deleting from either side) works too.", "O(n × m)", "O(m)"),
    follow_up="What if deleting each character had its own cost (LeetCode 712, minimum ASCII delete sum)?",
    related=["S2"],
))

P.append(dict(
    slug="longest-palindromic-subsequence", title="Longest palindromic subsequence", level="medium", stage="strings", tags=["interval DP", "as_bytes"],
    companies=["Amazon", "Google", "Meta", "Microsoft", "LinkedIn", "Uber"],
    teaches=["Interval DP: the answer for `s[i..=j]` from the answers for shorter intervals inside it.",
             "Iterating `i` downwards so every inner interval is ready."],
    statement="""
        Return the length of the longest subsequence of `s` that reads the same forwards and
        backwards. A subsequence keeps the order but may skip characters.
    """,
    examples=[("s = \"bbbab\"", "4 (\"bbbb\")")],
    constraints=["0 ≤ s.len() ≤ 2000", "s is ASCII lowercase letters"],
    starter="""
        pub fn longest_palindrome_subseq(s: &str) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn longest_palindrome_subseq(s: &str) -> usize {
            let s = s.as_bytes();
            let n = s.len();
            // For the current i, best[j] = LPS of s[i..=j]. Before updating it holds s[i + 1..=j].
            let mut best = vec![0usize; n];
            for i in (0..n).rev() {
                best[i] = 1;
                let mut inner = 0; // LPS of s[i + 1..=j - 1]
                for j in i + 1..n {
                    let without_i = best[j];
                    best[j] = if s[i] == s[j] { inner + 2 } else { without_i.max(best[j - 1]) };
                    inner = without_i;
                }
            }
            best.last().copied().unwrap_or(0)
        }
    """,
    visible=[
        T("leetcode_bbbab", "s = \"bbbab\"", "longest_palindrome_subseq(\"bbbab\")", "4"),
        T("leetcode_cbbd", "s = \"cbbd\"", "longest_palindrome_subseq(\"cbbd\")", "2"),
        T("empty", "s = \"\"", "longest_palindrome_subseq(\"\")", "0"),
        T("single", "s = \"a\"", "longest_palindrome_subseq(\"a\")", "1"),
        T("all_different", "s = \"abcde\"", "longest_palindrome_subseq(\"abcde\")", "1"),
        T("gaps_allowed", "s = \"aebcbda\" (\"abcba\")", "longest_palindrome_subseq(\"aebcbda\")", "5"),
    ],
    hidden=[
        T("empty", "s = \"\"", "longest_palindrome_subseq(\"\")", "0"),
        T("pair", "s = \"aa\"", "longest_palindrome_subseq(\"aa\")", "2"),
        T("different_pair", "s = \"ab\"", "longest_palindrome_subseq(\"ab\")", "1"),
        T("all_same", "s = \"aaaa\"", "longest_palindrome_subseq(\"aaaa\")", "4"),
        T("not_rearranged", "s = \"abab\"", "longest_palindrome_subseq(\"abab\")", "3"),
        T("inner_skip", "s = \"agbdba\"", "longest_palindrome_subseq(\"agbdba\")", "5"),
        T("word", "s = \"character\"", "longest_palindrome_subseq(\"character\")", "5"),
        T("long_run", "s = \"aaa…a\" (2000)", "longest_palindrome_subseq(&\"a\".repeat(2000))", "2000"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1226);
            for _ in 0..300 {
                let n = rng.below(12);
                let s = rng.string(n, "abc");
                let b = s.as_bytes();
                let mut want = 0;
                for mask in 0u32..(1 << n) {
                    let picked: Vec<u8> = (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| b[i]).collect();
                    if picked.iter().eq(picked.iter().rev()) {
                        want = want.max(picked.len());
                    }
                }
                check!(format!("s = {s:?}"), longest_palindrome_subseq(&s), want);
            }
        }

        #[test]
        fn scale_2000() {
            let s: String = (0..2000u64).map(|i| (b'a' + (i * 7919 % 26) as u8) as char).collect();
            check!("s[i] = 'a' + (7919·i) % 26, 2000 characters", longest_palindrome_subseq(&s), 153);
        }
        """,
    ],
    wrong=dict(
        longest_palindromic_substring="""
            pub fn longest_palindrome_subseq(s: &str) -> usize {
                let s = s.as_bytes();
                let n = s.len();
                let mut best = n.min(1);
                for center in 0..2 * n {
                    let (mut lo, mut hi) = (center / 2, center / 2 + center % 2);
                    while hi < n && s[lo] == s[hi] {
                        best = best.max(hi - lo + 1);
                        if lo == 0 {
                            break;
                        }
                        lo -= 1;
                        hi += 1;
                    }
                }
                best
            }
        """,
        pairs_of_letters="""
            pub fn longest_palindrome_subseq(s: &str) -> usize {
                let mut counts = [0usize; 26];
                for b in s.bytes() {
                    counts[(b - b'a') as usize] += 1;
                }
                let pairs: usize = counts.iter().map(|c| c / 2 * 2).sum();
                pairs + counts.iter().any(|c| c % 2 == 1) as usize
            }
        """,
        plain_recursion="""
            fn lps(s: &[u8]) -> usize {
                match s {
                    [] => 0,
                    [_] => 1,
                    [a, mid @ .., b] if a == b => 2 + lps(mid),
                    [_, rest @ ..] => lps(rest).max(lps(&s[..s.len() - 1])),
                }
            }

            pub fn longest_palindrome_subseq(s: &str) -> usize {
                lps(s.as_bytes())
            }
        """,
    ),
    hints=[("approach", "For s[i..=j]: if the ends match they wrap the best palindrome inside (2 + LPS(i + 1, j - 1)); otherwise drop one end: max(LPS(i + 1, j), LPS(i, j - 1))."),
           ("rust", "Loop `i` from n - 1 down to 0 and `j` upwards; one `Vec` works if you save the old `best[j]` before overwriting it (it is the next j's inner interval)."),
           ("edge case", "The characters must stay in order: \"abab\" gives 3 (\"aba\"), not 4. A subsequence, not a substring: \"aebcbda\" gives 5.")],
    notes=("Every interval depends only on intervals strictly inside it, so filling by decreasing i and increasing j works. It also equals LCS(s, reverse(s)).", "O(n²)", "O(n)"),
    follow_up="How would you find the fewest insertions that make s a palindrome? (n - LPS.)",
    related=["D2", "S2"],
))

P.append(dict(
    slug="edit-distance", title="Edit distance", level="medium", stage="strings", tags=["2-D DP", "chars", "Unicode"],
    companies=["Google", "Amazon", "Meta", "Microsoft", "Apple", "Bloomberg", "LinkedIn"],
    teaches=["Three moves (insert, delete, replace) as three neighbours in the table.",
             "`chars().collect::<Vec<char>>()` when an edit means a character, not a byte."],
    statement="""
        In one edit you insert a character, delete a character, or replace one character with
        another. Return the fewest edits that turn `a` into `b`.

        The strings can hold any Unicode text; an edit changes one `char`, so `"café"` → `"cafe"`
        is one edit.
    """,
    examples=[("a = \"horse\", b = \"ros\"", "3 (horse → rorse → rose → ros)")],
    constraints=["0 ≤ a and b ≤ 2000 chars each"],
    starter="""
        pub fn edit_distance(a: &str, b: &str) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn edit_distance(a: &str, b: &str) -> usize {
            let a: Vec<char> = a.chars().collect();
            let b: Vec<char> = b.chars().collect();
            // prev[j] = edits between a[..i] and b[..j]; row 0 is j inserts.
            let mut prev: Vec<usize> = (0..=b.len()).collect();
            let mut cur = vec![0usize; b.len() + 1];
            for (i, &x) in a.iter().enumerate() {
                cur[0] = i + 1; // delete all of a[..=i]
                for (j, &y) in b.iter().enumerate() {
                    cur[j + 1] = if x == y {
                        prev[j]
                    } else {
                        1 + prev[j].min(prev[j + 1]).min(cur[j]) // replace, delete, insert
                    };
                }
                std::mem::swap(&mut prev, &mut cur);
            }
            prev[b.len()]
        }
    """,
    visible=[
        T("leetcode_horse", "a = \"horse\", b = \"ros\"", "edit_distance(\"horse\", \"ros\")", "3"),
        T("leetcode_intention", "a = \"intention\", b = \"execution\"", "edit_distance(\"intention\", \"execution\")", "5"),
        T("empty_to_word", "a = \"\", b = \"abc\"", "edit_distance(\"\", \"abc\")", "3"),
        T("word_to_empty", "a = \"abc\", b = \"\"", "edit_distance(\"abc\", \"\")", "3"),
        T("same", "a = \"same\", b = \"same\"", "edit_distance(\"same\", \"same\")", "0"),
        T("unicode_is_one_edit", "a = \"café\", b = \"cafe\"", "edit_distance(\"café\", \"cafe\")", "1"),
    ],
    hidden=[
        T("both_empty", "a = \"\", b = \"\"", "edit_distance(\"\", \"\")", "0"),
        T("one_replace", "a = \"a\", b = \"b\"", "edit_distance(\"a\", \"b\")", "1"),
        T("swap", "a = \"ab\", b = \"ba\"", "edit_distance(\"ab\", \"ba\")", "2"),
        T("kitten", "a = \"kitten\", b = \"sitting\"", "edit_distance(\"kitten\", \"sitting\")", "3"),
        T("insert_and_replace", "a = \"abc\", b = \"yabd\"", "edit_distance(\"abc\", \"yabd\")", "2"),
        T("plasma", "a = \"plasma\", b = \"altruism\"", "edit_distance(\"plasma\", \"altruism\")", "6"),
        T("cjk_insert", "a = \"日本\", b = \"日本語\"", "edit_distance(\"日本\", \"日本語\")", "1"),
        T("tilde", "a = \"ñ\", b = \"n\"", "edit_distance(\"ñ\", \"n\")", "1"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn dist(a: &[char], b: &[char]) -> usize {
                match (a, b) {
                    ([], _) => b.len(),
                    (_, []) => a.len(),
                    ([x, ra @ ..], [y, rb @ ..]) if x == y => dist(ra, rb),
                    ([_, ra @ ..], [_, rb @ ..]) => 1 + dist(ra, rb).min(dist(ra, b)).min(dist(a, rb)),
                }
            }
            let mut rng = anneal_prelude::Rng::new(1227);
            for _ in 0..300 {
                let (la, lb) = (rng.below(7), rng.below(7));
                let a = rng.string(la, "abé");
                let b = rng.string(lb, "abé");
                let (ca, cb): (Vec<char>, Vec<char>) = (a.chars().collect(), b.chars().collect());
                check!(format!("a = {a:?}, b = {b:?}"), edit_distance(&a, &b), dist(&ca, &cb));
            }
        }

        #[test]
        fn scale_2000() {
            let a: String = (0..2000u64).map(|i| (b'a' + (i * 7919 % 26) as u8) as char).collect();
            let b: String = (0..2000u64).map(|i| (b'a' + ((i * 104_729 + 13) % 26) as u8) as char).collect();
            check!("a[i] = 'a' + (7919·i) % 26, b[i] = 'a' + (104729·i + 13) % 26, 2000 each", edit_distance(&a, &b), 1847);
        }
        """,
    ],
    wrong=dict(
        compares_bytes="""
            pub fn edit_distance(a: &str, b: &str) -> usize {
                let (a, b) = (a.as_bytes(), b.as_bytes());
                let mut prev: Vec<usize> = (0..=b.len()).collect();
                let mut cur = vec![0usize; b.len() + 1];
                for (i, &x) in a.iter().enumerate() {
                    cur[0] = i + 1;
                    for (j, &y) in b.iter().enumerate() {
                        cur[j + 1] = if x == y { prev[j] } else { 1 + prev[j].min(prev[j + 1]).min(cur[j]) };
                    }
                    std::mem::swap(&mut prev, &mut cur);
                }
                prev[b.len()]
            }
        """,
        no_replace="""
            pub fn edit_distance(a: &str, b: &str) -> usize {
                let a: Vec<char> = a.chars().collect();
                let b: Vec<char> = b.chars().collect();
                let mut prev: Vec<usize> = (0..=b.len()).collect();
                let mut cur = vec![0usize; b.len() + 1];
                for (i, &x) in a.iter().enumerate() {
                    cur[0] = i + 1;
                    for (j, &y) in b.iter().enumerate() {
                        cur[j + 1] = if x == y { prev[j] } else { 1 + prev[j + 1].min(cur[j]) };
                    }
                    std::mem::swap(&mut prev, &mut cur);
                }
                prev[b.len()]
            }
        """,
        plain_recursion="""
            fn dist(a: &[char], b: &[char]) -> usize {
                match (a, b) {
                    ([], _) => b.len(),
                    (_, []) => a.len(),
                    ([x, ra @ ..], [y, rb @ ..]) if x == y => dist(ra, rb),
                    ([_, ra @ ..], [_, rb @ ..]) => 1 + dist(ra, rb).min(dist(ra, b)).min(dist(a, rb)),
                }
            }

            pub fn edit_distance(a: &str, b: &str) -> usize {
                let a: Vec<char> = a.chars().collect();
                let b: Vec<char> = b.chars().collect();
                dist(&a, &b)
            }
        """,
    ),
    hints=[("approach", "dp[i][j] = dp[i - 1][j - 1] if the characters match, else 1 + min(replace dp[i - 1][j - 1], delete dp[i - 1][j], insert dp[i][j - 1]). Row 0 is j, column 0 is i."),
           ("rust", "Collect both strings into `Vec<char>` first; `as_bytes()` would count \"é\" as two edits. Two rows plus `std::mem::swap` keep it O(m) space."),
           ("edge case", "Turning a string into \"\" (or back) costs its length, so the first row and column are 0, 1, 2, …")],
    notes=("The last characters either match (free), or the last edit was a replace, a delete or an insert, each leaving a smaller pair of prefixes. Collecting into chars makes each edit one Unicode scalar value.", "O(n × m)", "O(m)"),
    follow_up="Graphemes like \"é\" written as e + a combining accent are two chars. How would you make that one edit? (Grapheme clusters, e.g. the unicode-segmentation crate.)",
    related=["S2"],
))

P.append(dict(
    slug="interleaving-string", title="Interleaving string", level="medium", stage="strings", tags=["2-D DP", "as_bytes"],
    companies=["Google", "Amazon", "Microsoft", "Meta", "Apple"],
    teaches=["A boolean table over two prefixes: position `i + j` of `s3` comes from `s1[i - 1]` or `s2[j - 1]`.",
             "Checking the lengths first so the table indices always line up."],
    statement="""
        Return whether `s3` can be formed by interleaving `s1` and `s2`: taking all their
        characters, keeping each string's own order, and merging them in some way.
    """,
    examples=[("s1 = \"aabcc\", s2 = \"dbbca\", s3 = \"aadbbcbcac\"", "true"),
              ("s1 = \"aabcc\", s2 = \"dbbca\", s3 = \"aadbbbaccc\"", "false")],
    constraints=["0 ≤ s1.len(), s2.len() ≤ 1000", "0 ≤ s3.len() ≤ 2000", "ASCII lowercase letters"],
    starter="""
        pub fn is_interleave(s1: &str, s2: &str, s3: &str) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn is_interleave(s1: &str, s2: &str, s3: &str) -> bool {
            let (a, b, c) = (s1.as_bytes(), s2.as_bytes(), s3.as_bytes());
            if a.len() + b.len() != c.len() {
                return false;
            }
            // ok[j] for the current i: a[..i] and b[..j] interleave into c[..i + j].
            let mut ok = vec![false; b.len() + 1];
            for i in 0..=a.len() {
                for j in 0..=b.len() {
                    ok[j] = if i == 0 && j == 0 {
                        true
                    } else {
                        (i > 0 && ok[j] && a[i - 1] == c[i + j - 1]) || (j > 0 && ok[j - 1] && b[j - 1] == c[i + j - 1])
                    };
                }
            }
            ok[b.len()]
        }
    """,
    visible=[
        T("leetcode_true", "s1 = \"aabcc\", s2 = \"dbbca\", s3 = \"aadbbcbcac\"", "is_interleave(\"aabcc\", \"dbbca\", \"aadbbcbcac\")", "true"),
        T("leetcode_false", "s1 = \"aabcc\", s2 = \"dbbca\", s3 = \"aadbbbaccc\"", "is_interleave(\"aabcc\", \"dbbca\", \"aadbbbaccc\")", "false"),
        T("leetcode_all_empty", "s1 = \"\", s2 = \"\", s3 = \"\"", "is_interleave(\"\", \"\", \"\")", "true"),
        T("one_side_empty", "s1 = \"a\", s2 = \"\", s3 = \"a\"", "is_interleave(\"a\", \"\", \"a\")", "true"),
        T("length_mismatch", "s1 = \"a\", s2 = \"b\", s3 = \"abc\"", "is_interleave(\"a\", \"b\", \"abc\")", "false"),
        T("either_string_first", "s1 = \"a\", s2 = \"b\", s3 = \"ba\"", "is_interleave(\"a\", \"b\", \"ba\")", "true"),
    ],
    hidden=[
        T("too_short", "s1 = \"abc\", s2 = \"\", s3 = \"ab\"", "is_interleave(\"abc\", \"\", \"ab\")", "false"),
        T("empty_s3", "s1 = \"a\", s2 = \"\", s3 = \"\"", "is_interleave(\"a\", \"\", \"\")", "false"),
        T("order_kept", "s1 = \"ab\", s2 = \"\", s3 = \"ba\"", "is_interleave(\"ab\", \"\", \"ba\")", "false"),
        T("symmetric", "s1 = \"ab\", s2 = \"ba\", s3 = \"abba\"", "is_interleave(\"ab\", \"ba\", \"abba\")", "true"),
        T("greedy_trap", "s1 = \"aa\", s2 = \"ab\", s3 = \"abaa\"", "is_interleave(\"aa\", \"ab\", \"abaa\")", "true"),
        T("greedy_trap_longer", "s1 = \"abc\", s2 = \"abd\", s3 = \"abdabc\"", "is_interleave(\"abc\", \"abd\", \"abdabc\")", "true"),
        T("shared_letters", "s1 = \"db\", s2 = \"b\", s3 = \"dbb\"", "is_interleave(\"db\", \"b\", \"dbb\")", "true"),
        T("same_letters_wrong_count", "s1 = \"aa\", s2 = \"a\", s3 = \"aab\"", "is_interleave(\"aa\", \"a\", \"aab\")", "false"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn can(a: &[u8], b: &[u8], c: &[u8]) -> bool {
                match c {
                    [] => a.is_empty() && b.is_empty(),
                    [x, rest @ ..] => (a.first() == Some(x) && can(&a[1..], b, rest)) || (b.first() == Some(x) && can(a, &b[1..], rest)),
                }
            }
            let mut rng = anneal_prelude::Rng::new(1228);
            for _ in 0..400 {
                let (l1, l2) = (rng.below(5), rng.below(5));
                let s1 = rng.string(l1, "ab");
                let s2 = rng.string(l2, "ab");
                let l3 = if rng.below(8) == 0 { rng.below(9) } else { l1 + l2 };
                let s3 = rng.string(l3, "ab");
                check!(format!("s1 = {s1:?}, s2 = {s2:?}, s3 = {s3:?}"), is_interleave(&s1, &s2, &s3), can(s1.as_bytes(), s2.as_bytes(), s3.as_bytes()));
            }
        }

        #[test]
        fn scale_all_a_then_b() {
            // Every split of the a's matches until the final b: plain recursion tries them all.
            let s1 = "a".repeat(1000);
            let s2 = "a".repeat(1000);
            let s3 = format!("{}b", "a".repeat(1999));
            check!("s1 = s2 = 1000 a's, s3 = 1999 a's then b", is_interleave(&s1, &s2, &s3), false);
        }

        #[test]
        fn scale_real_interleave() {
            let s1: Vec<u8> = (0..1000usize).map(|i| b'a' + (i * 7 % 3) as u8).collect();
            let s2: Vec<u8> = (0..1000usize).map(|i| b'a' + ((i * 5 + 1) % 3) as u8).collect();
            let mut s3 = Vec::new();
            let (mut i, mut j, mut k) = (0, 0, 0usize);
            while i < 1000 || j < 1000 {
                if j >= 1000 || (i < 1000 && k * 7919 % 3 != 0) {
                    s3.push(s1[i]);
                    i += 1;
                } else {
                    s3.push(s2[j]);
                    j += 1;
                }
                k += 1;
            }
            let (s1, s2, s3) = (String::from_utf8(s1).unwrap(), String::from_utf8(s2).unwrap(), String::from_utf8(s3).unwrap());
            check!("s1, s2 = 1000 letters of a/b/c, s3 = one interleaving of them", is_interleave(&s1, &s2, &s3), true);
        }
        """,
    ],
    wrong=dict(
        greedy_prefers_s1="""
            pub fn is_interleave(s1: &str, s2: &str, s3: &str) -> bool {
                let (a, b) = (s1.as_bytes(), s2.as_bytes());
                let (mut i, mut j) = (0, 0);
                for &ch in s3.as_bytes() {
                    if i < a.len() && a[i] == ch {
                        i += 1;
                    } else if j < b.len() && b[j] == ch {
                        j += 1;
                    } else {
                        return false;
                    }
                }
                i == a.len() && j == b.len()
            }
        """,
        plain_recursion="""
            fn can(a: &[u8], b: &[u8], c: &[u8]) -> bool {
                match c {
                    [] => a.is_empty() && b.is_empty(),
                    [x, rest @ ..] => (a.first() == Some(x) && can(&a[1..], b, rest)) || (b.first() == Some(x) && can(a, &b[1..], rest)),
                }
            }

            pub fn is_interleave(s1: &str, s2: &str, s3: &str) -> bool {
                can(s1.as_bytes(), s2.as_bytes(), s3.as_bytes())
            }
        """,
        no_length_check="""
            pub fn is_interleave(s1: &str, s2: &str, s3: &str) -> bool {
                let (a, b, c) = (s1.as_bytes(), s2.as_bytes(), s3.as_bytes());
                let mut ok = vec![false; b.len() + 1];
                for i in 0..=a.len() {
                    for j in 0..=b.len() {
                        ok[j] = if i == 0 && j == 0 {
                            true
                        } else {
                            (i > 0 && ok[j] && c.get(i + j - 1) == Some(&a[i - 1])) || (j > 0 && ok[j - 1] && c.get(i + j - 1) == Some(&b[j - 1]))
                        };
                    }
                }
                ok[b.len()]
            }
        """,
    ),
    hints=[("approach", "ok(i, j) is true if s3[..i + j] interleaves s1[..i] and s2[..j]: either s1[i - 1] == s3[i + j - 1] and ok(i - 1, j), or s2[j - 1] == s3[i + j - 1] and ok(i, j - 1)."),
           ("rust", "Return `false` early unless `s1.len() + s2.len() == s3.len()`; then one `Vec<bool>` of width s2.len() + 1 is the whole table."),
           ("edge case", "Taking from s1 whenever it matches is greedy and fails when both strings offer the same letter: s1 = \"aa\", s2 = \"ab\", s3 = \"abaa\".")],
    notes=("The table has one cell per pair of prefix lengths; s3's position is always i + j, so it isn't a third dimension. Row i only needs row i - 1, hence one rolling row.", "O(n × m)", "O(m)"),
    follow_up="How would you return which string each character of s3 came from?",
    related=["D2"],
))

P.append(dict(
    slug="distinct-subsequences", title="Distinct subsequences", level="hard", stage="strings", tags=["2-D DP", "u64", "wrapping"],
    companies=["Google", "Amazon", "Microsoft", "Bloomberg"],
    teaches=["Counting DP over two strings, updated backwards so each character of `s` is used once per subsequence.",
             "Counts that never reach the answer can still overflow; `wrapping_add` is exact modulo 2⁶⁴."],
    statement="""
        Return how many different ways you can choose characters of `s`, in order, that spell
        `t`. Two ways differ if they pick a different set of positions in `s`.

        The answer fits in a `u64`, but counts for prefixes of `t` along the way may not.
    """,
    examples=[("s = \"rabbbit\", t = \"rabbit\"", "3 (drop any one of the three b's)")],
    constraints=["0 ≤ s.len() ≤ 10⁴", "0 ≤ t.len() ≤ 1000", "ASCII lowercase letters", "the answer fits in a u64"],
    starter="""
        pub fn num_distinct(s: &str, t: &str) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn num_distinct(s: &str, t: &str) -> u64 {
            let t = t.as_bytes();
            // ways[j] = ways to spell t[..j] with the part of s seen so far.
            let mut ways = vec![0u64; t.len() + 1];
            ways[0] = 1;
            for &c in s.as_bytes() {
                // Backwards, so this c extends only spellings that didn't use it already.
                for j in (1..=t.len()).rev() {
                    if t[j - 1] == c {
                        // Partial counts may wrap; the final answer is exact because it fits.
                        ways[j] = ways[j].wrapping_add(ways[j - 1]);
                    }
                }
            }
            ways[t.len()]
        }
    """,
    visible=[
        T("leetcode_rabbit", "s = \"rabbbit\", t = \"rabbit\"", "num_distinct(\"rabbbit\", \"rabbit\")", "3"),
        T("leetcode_bag", "s = \"babgbag\", t = \"bag\"", "num_distinct(\"babgbag\", \"bag\")", "5"),
        T("empty_t", "s = \"abc\", t = \"\"", "num_distinct(\"abc\", \"\")", "1"),
        T("empty_s", "s = \"\", t = \"a\"", "num_distinct(\"\", \"a\")", "0"),
        T("positions_not_letters", "s = \"aaa\", t = \"aa\"", "num_distinct(\"aaa\", \"aa\")", "3"),
    ],
    hidden=[
        T("both_empty", "s = \"\", t = \"\"", "num_distinct(\"\", \"\")", "1"),
        T("single", "s = \"a\", t = \"a\"", "num_distinct(\"a\", \"a\")", "1"),
        T("t_longer", "s = \"ab\", t = \"abc\"", "num_distinct(\"ab\", \"abc\")", "0"),
        T("one_letter_three_times", "s = \"aaa\", t = \"a\"", "num_distinct(\"aaa\", \"a\")", "3"),
        T("overlapping", "s = \"abab\", t = \"ab\"", "num_distinct(\"abab\", \"ab\")", "3"),
        T("order_matters", "s = \"ba\", t = \"ab\"", "num_distinct(\"ba\", \"ab\")", "0"),
        T("near_u64_max", "s = 64 a's, t = 32 a's", "num_distinct(&\"a\".repeat(64), &\"a\".repeat(32))", "1_832_624_140_942_590_534"),
        T("dead_counts_overflow", "s = 200 a's, t = 100 a's then c", "num_distinct(&\"a\".repeat(200), &format!(\"{}c\", \"a\".repeat(100)))", "0"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1229);
            for _ in 0..300 {
                let (ls, lt) = (rng.below(12), rng.below(4));
                let s = rng.string(ls, "ab");
                let t = rng.string(lt, "ab");
                let sb = s.as_bytes();
                let mut want = 0u64;
                for mask in 0u32..(1 << ls) {
                    let picked: Vec<u8> = (0..ls).filter(|&i| mask >> i & 1 == 1).map(|i| sb[i]).collect();
                    want += (picked == t.as_bytes()) as u64;
                }
                check!(format!("s = {s:?}, t = {t:?}"), num_distinct(&s, &t), want);
            }
        }

        #[test]
        fn scale_10k() {
            let s: String = (0..10_000u64).map(|i| (b'a' + (i * 7919 % 26) as u8) as char).collect();
            let t: String = (0..9u64).map(|i| (b'a' + ((i * 104_729 + 5) % 26) as u8) as char).collect();
            check!(format!("s[i] = 'a' + (7919·i) % 26 (10000 letters), t = {t:?}"), num_distinct(&s, &t), 536_473_971_710_831_440);
        }
        """,
    ],
    wrong=dict(
        plain_add="""
            pub fn num_distinct(s: &str, t: &str) -> u64 {
                let t = t.as_bytes();
                let mut ways = vec![0u64; t.len() + 1];
                ways[0] = 1;
                for &c in s.as_bytes() {
                    for j in (1..=t.len()).rev() {
                        if t[j - 1] == c {
                            ways[j] += ways[j - 1];
                        }
                    }
                }
                ways[t.len()]
            }
        """,
        forwards_reuses_a_char="""
            pub fn num_distinct(s: &str, t: &str) -> u64 {
                let t = t.as_bytes();
                let mut ways = vec![0u64; t.len() + 1];
                ways[0] = 1;
                for &c in s.as_bytes() {
                    for j in 1..=t.len() {
                        if t[j - 1] == c {
                            ways[j] = ways[j].wrapping_add(ways[j - 1]);
                        }
                    }
                }
                ways[t.len()]
            }
        """,
        plain_recursion="""
            fn count(s: &[u8], t: &[u8]) -> u64 {
                match (s, t) {
                    (_, []) => 1,
                    ([], _) => 0,
                    ([x, rs @ ..], [y, rt @ ..]) => count(rs, t) + if x == y { count(rs, rt) } else { 0 },
                }
            }

            pub fn num_distinct(s: &str, t: &str) -> u64 {
                count(s.as_bytes(), t.as_bytes())
            }
        """,
    ),
    hints=[("approach", "ways(i, j) = ways(i - 1, j) + (s[i - 1] == t[j - 1] ? ways(i - 1, j - 1) : 0): skip this character of s, or use it for t's j-th letter. ways(i, 0) = 1."),
           ("rust", "One `Vec<u64>` over t, updated for each byte of s with j running backwards, so `ways[j - 1]` is still the value from before this byte."),
           ("edge case", "Counts for prefixes of t that never finish can pass 2⁶⁴ (200 a's against 100 a's then 'c'); a plain `+` panics in debug. `wrapping_add` is exact modulo 2⁶⁴, and the real answer fits.")],
    notes=("Each position of s either extends spellings of t[..j - 1] into t[..j] or is skipped. Updating j backwards is the 0/1-knapsack trick: each character is used at most once per spelling. All arithmetic is modulo 2⁶⁴, which is exact for the final count.", "O(|s| × |t|)", "O(|t|)"),
    follow_up="If the answer were only needed modulo 10⁹ + 7, what changes? And why is wrapping safe here but not for a minimum or maximum?",
    related=["D11"],
))

# ---------------------------------------------------------------- Knapsack (medium)

P.append(dict(
    slug="zero-one-knapsack", title="0/1 knapsack", level="medium", stage="knapsack", tags=["0/1 knapsack", "1-D DP"],
    companies=["Amazon", "Google", "Microsoft", "Goldman Sachs"],
    teaches=["The 0/1 knapsack table over capacities, and why each item's pass runs downwards.",
             "Going from `dp[i][c]` to one `Vec` indexed by capacity."],
    statement="""
        Each item is a `(weight, value)` pair and can be taken at most once. Return the largest
        total value whose total weight is at most `capacity`.
    """,
    examples=[("items = [(1, 1), (3, 4), (4, 5), (5, 7)], capacity = 7", "9 (weights 3 + 4)")],
    constraints=["0 ≤ items.len() ≤ 100", "0 ≤ weight ≤ 10⁵, 0 ≤ value ≤ 10⁹", "0 ≤ capacity ≤ 10⁵"],
    starter="""
        pub fn knapsack(items: &[(usize, u64)], capacity: usize) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn knapsack(items: &[(usize, u64)], capacity: usize) -> u64 {
            // best[c] = the most value with total weight ≤ c, using the items seen so far.
            let mut best = vec![0u64; capacity + 1];
            for &(weight, value) in items {
                // Downwards, so best[c - weight] doesn't include this item yet: each item once.
                for c in (weight..=capacity).rev() {
                    best[c] = best[c].max(best[c - weight] + value);
                }
            }
            best[capacity]
        }
    """,
    visible=[
        T("four_items", "items = [(1, 1), (3, 4), (4, 5), (5, 7)], capacity = 7", "knapsack(&[(1, 1), (3, 4), (4, 5), (5, 7)], 7)", "9"),
        T("no_items", "items = [], capacity = 10", "knapsack(&[], 10)", "0"),
        T("no_capacity", "items = [(1, 1)], capacity = 0", "knapsack(&[(1, 1)], 0)", "0"),
        T("each_item_once", "items = [(1, 10)], capacity = 5", "knapsack(&[(1, 10)], 5)", "10"),
        T("best_ratio_is_a_trap", "items = [(10, 60), (20, 100), (30, 120)], capacity = 50", "knapsack(&[(10, 60), (20, 100), (30, 120)], 50)", "220"),
    ],
    hidden=[
        T("no_items", "items = [], capacity = 0", "knapsack(&[], 0)", "0"),
        T("too_heavy", "items = [(5, 10)], capacity = 4", "knapsack(&[(5, 10)], 4)", "0"),
        T("weightless_item", "items = [(0, 5), (2, 3)], capacity = 1", "knapsack(&[(0, 5), (2, 3)], 1)", "5"),
        T("exact_fit", "items = [(2, 3), (3, 4), (4, 5), (5, 6)], capacity = 5", "knapsack(&[(2, 3), (3, 4), (4, 5), (5, 6)], 5)", "7"),
        T("duplicates", "items = [(3, 5); 4], capacity = 9", "knapsack(&[(3, 5); 4], 9)", "15"),
        T("big_values", "items = [(1, 10⁹); 100], capacity = 100", "knapsack(&[(1, 1_000_000_000); 100], 100)", "100_000_000_000"),
        T("everything_fits", "items = [(1, 2), (2, 3)], capacity = 100000", "knapsack(&[(1, 2), (2, 3)], 100_000)", "5"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1230);
            for _ in 0..300 {
                let n = rng.below(11);
                let mut items: Vec<(usize, u64)> = Vec::new();
                for _ in 0..n {
                    let w = rng.int(0, 8) as usize;
                    let v = rng.int(0, 20) as u64;
                    items.push((w, v));
                }
                let cap = rng.int(0, 20) as usize;
                let mut want = 0;
                for mask in 0u32..(1 << n) {
                    let (w, v) = (0..n).filter(|&i| mask >> i & 1 == 1).fold((0, 0), |(w, v), i| (w + items[i].0, v + items[i].1));
                    if w <= cap {
                        want = want.max(v);
                    }
                }
                check!(format!("items = {items:?}, capacity = {cap}"), knapsack(&items, cap), want);
            }
        }

        #[test]
        fn scale_100_items() {
            let items: Vec<(usize, u64)> = (0..100u64).map(|i| ((i * 7919 % 3000 + 500) as usize, i * 104_729 % 1000 + 1)).collect();
            check!("items[i] = ((7919·i) % 3000 + 500, (104729·i) % 1000 + 1), 100 items, capacity = 50000", knapsack(&items, 50_000), 25_744);
        }
        """,
    ],
    wrong=dict(
        capacity_upwards="""
            pub fn knapsack(items: &[(usize, u64)], capacity: usize) -> u64 {
                let mut best = vec![0u64; capacity + 1];
                for &(weight, value) in items {
                    for c in weight.max(1)..=capacity {
                        best[c] = best[c].max(best[c - weight] + value);
                    }
                }
                best[capacity]
            }
        """,
        best_ratio_first="""
            pub fn knapsack(items: &[(usize, u64)], capacity: usize) -> u64 {
                let mut sorted = items.to_vec();
                sorted.sort_by(|a, b| (b.1 * a.0.max(1) as u64).cmp(&(a.1 * b.0.max(1) as u64)));
                let (mut left, mut total) = (capacity, 0);
                for (w, v) in sorted {
                    if w <= left {
                        left -= w;
                        total += v;
                    }
                }
                total
            }
        """,
        plain_recursion="""
            fn best(items: &[(usize, u64)], cap: usize) -> u64 {
                match items {
                    [] => 0,
                    [(w, v), rest @ ..] => {
                        let skip = best(rest, cap);
                        if *w <= cap { skip.max(v + best(rest, cap - w)) } else { skip }
                    }
                }
            }

            pub fn knapsack(items: &[(usize, u64)], capacity: usize) -> u64 {
                best(items, capacity)
            }
        """,
    ),
    hints=[("approach", "Take items one at a time: best(c) with this item is max(best(c) without it, value + best(c - weight) without it)."),
           ("rust", "One `Vec<u64>` of length capacity + 1. For each item, loop `for c in (weight..=capacity).rev()` so `best[c - weight]` is still the value before this item."),
           ("edge case", "Looping capacities upwards lets an item be added again and again (that is the unbounded knapsack). Sorting by value per weight is not optimal either.")],
    notes=("The 2-D table best[i][c] only reads row i - 1, and only at capacities ≤ c. Sweeping c downwards in one row reads those old values before they are overwritten.", "O(n × capacity)", "O(capacity)"),
    follow_up="How would you list which items were taken? And what if capacity were 10⁹ but values small? (DP over value instead of weight.)",
    related=["D8"],
))

P.append(dict(
    slug="partition-equal-subset-sum", title="Partition equal subset sum", level="medium", stage="knapsack", tags=["0/1 knapsack", "subset sum"],
    companies=["Amazon", "Meta", "Google", "Apple", "Microsoft", "Bloomberg"],
    teaches=["Subset sum as a boolean knapsack aiming at half the total.", "Rejecting an odd total before building any table."],
    statement="""
        Return whether `nums` can be split into two groups (every number in exactly one group)
        with equal sums. An empty slice splits into two empty groups.
    """,
    examples=[("nums = [1, 5, 11, 5]", "true ([1, 5, 5] and [11])"), ("nums = [1, 2, 3, 5]", "false")],
    constraints=["0 ≤ nums.len() ≤ 200", "1 ≤ nums[i] ≤ 100"],
    starter="""
        pub fn can_partition(nums: &[u32]) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn can_partition(nums: &[u32]) -> bool {
            let total: u32 = nums.iter().sum();
            if total % 2 == 1 {
                return false;
            }
            let half = (total / 2) as usize;
            // reach[s] = some subset of the numbers so far sums to s.
            let mut reach = vec![false; half + 1];
            reach[0] = true;
            for &x in nums {
                let x = x as usize;
                for s in (x..=half).rev() {
                    reach[s] = reach[s] || reach[s - x];
                }
            }
            reach[half]
        }
    """,
    visible=[
        T("leetcode_true", "nums = [1, 5, 11, 5]", "can_partition(&[1, 5, 11, 5])", "true"),
        T("leetcode_false", "nums = [1, 2, 3, 5]", "can_partition(&[1, 2, 3, 5])", "false"),
        T("empty", "nums = []", "can_partition(&[])", "true"),
        T("single", "nums = [1]", "can_partition(&[1])", "false"),
        T("pair", "nums = [1, 1]", "can_partition(&[1, 1])", "true"),
        T("even_total_is_not_enough", "nums = [1, 2, 5]", "can_partition(&[1, 2, 5])", "false"),
    ],
    hidden=[
        T("empty", "nums = []", "can_partition(&[])", "true"),
        T("odd_total", "nums = [1, 2, 4]", "can_partition(&[1, 2, 4])", "false"),
        T("each_number_once", "nums = [2, 2, 3, 5]", "can_partition(&[2, 2, 3, 5])", "false"),
        T("max_pair", "nums = [100, 100]", "can_partition(&[100, 100])", "true"),
        T("five_numbers", "nums = [3, 3, 3, 4, 5]", "can_partition(&[3, 3, 3, 4, 5])", "true"),
        T("one_to_seven", "nums = [1, 2, 3, 4, 5, 6, 7]", "can_partition(&[1, 2, 3, 4, 5, 6, 7])", "true"),
        T("one_big", "nums = [1, 1, 1, 100]", "can_partition(&[1, 1, 1, 100])", "false"),
        T("two_hundred", "nums[i] = (7919·i) % 100 + 1, 200 numbers", "can_partition(&(0..200u32).map(|i| i * 7919 % 100 + 1).collect::<Vec<_>>())", "true"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1231);
            for _ in 0..300 {
                let n = rng.below(13);
                let nums: Vec<u32> = rng.vec(n, 1, 12);
                let total: u32 = nums.iter().sum();
                let want = (0u32..(1 << n)).any(|mask| 2 * (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| nums[i]).sum::<u32>() == total);
                check!(format!("nums = {nums:?}"), can_partition(&nums), want);
            }
        }

        #[test]
        fn scale_all_twos() {
            // Half of 202 is 101, which no set of 2s can hit; plain recursion tries every subset.
            check!("nums = [2; 101]", can_partition(&vec![2; 101]), false);
        }
        """,
    ],
    wrong=dict(
        sums_upwards="""
            pub fn can_partition(nums: &[u32]) -> bool {
                let total: u32 = nums.iter().sum();
                if total % 2 == 1 {
                    return false;
                }
                let half = (total / 2) as usize;
                let mut reach = vec![false; half + 1];
                reach[0] = true;
                for &x in nums {
                    let x = x as usize;
                    for s in x..=half {
                        reach[s] = reach[s] || reach[s - x];
                    }
                }
                reach[half]
            }
        """,
        parity_only="""
            pub fn can_partition(nums: &[u32]) -> bool {
                nums.iter().sum::<u32>() % 2 == 0
            }
        """,
        plain_recursion="""
            fn hits(nums: &[u32], left: u32) -> bool {
                left == 0 || matches!(nums, [x, rest @ ..] if (*x <= left && hits(rest, left - x)) || hits(rest, left))
            }

            pub fn can_partition(nums: &[u32]) -> bool {
                let total: u32 = nums.iter().sum();
                total % 2 == 0 && hits(nums, total / 2)
            }
        """,
    ),
    hints=[("approach", "Two equal groups each sum to total / 2, so the question is whether some subset sums to exactly half. An odd total is impossible."),
           ("rust", "A `Vec<bool>` of length half + 1 with `reach[0] = true`; for each number, sweep `s` downwards and set `reach[s] |= reach[s - x]`."),
           ("edge case", "Sweeping upwards lets one number count twice: [1, 2, 5] would \"reach\" 4 as 2 + 2.")],
    notes=("It is 0/1 knapsack with booleans. The table has one entry per reachable sum up to half the total (at most 10⁴ here).", "O(n × total)", "O(total)"),
    follow_up="How would a `u128` or a bitset (`reach |= reach << x`) speed this up?",
    related=["D11", "D13"],
))

P.append(dict(
    slug="target-sum", title="Target sum", level="medium", stage="knapsack", tags=["0/1 knapsack", "counting"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "Bloomberg"],
    teaches=["Algebra first: choosing signs is choosing the subset that gets a `+`, with a fixed required sum.",
             "Guarding the transform (parity, range) before indexing."],
    statement="""
        Put a `+` or a `-` in front of every number in `nums` and add them up. Return how many sign
        choices give exactly `target`. With no numbers the only expression is 0.
    """,
    examples=[("nums = [1, 1, 1, 1, 1], target = 3", "5 (the - can go on any one of the five)")],
    constraints=["0 ≤ nums.len() ≤ 60", "0 ≤ nums[i], and sum(nums) ≤ 1000", "|target| ≤ 1000"],
    starter="""
        pub fn find_target_sum_ways(nums: &[u32], target: i32) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn find_target_sum_ways(nums: &[u32], target: i32) -> u64 {
            let total: i64 = nums.iter().map(|&x| x as i64).sum();
            // The + numbers sum to P and the - numbers to total - P, so P = (total + target) / 2.
            let doubled = total + target as i64;
            if doubled < 0 || doubled > 2 * total || doubled % 2 == 1 {
                return 0;
            }
            let plus = (doubled / 2) as usize;
            // ways[s] = subsets of the numbers so far that sum to s.
            let mut ways = vec![0u64; plus + 1];
            ways[0] = 1;
            for &x in nums {
                let x = x as usize;
                for s in (x..=plus).rev() {
                    ways[s] += ways[s - x]; // a 0 doubles every count: +0 and -0
                }
            }
            ways[plus]
        }
    """,
    visible=[
        T("leetcode_five_ones", "nums = [1, 1, 1, 1, 1], target = 3", "find_target_sum_ways(&[1, 1, 1, 1, 1], 3)", "5"),
        T("leetcode_single", "nums = [1], target = 1", "find_target_sum_ways(&[1], 1)", "1"),
        T("empty_makes_zero", "nums = [], target = 0", "find_target_sum_ways(&[], 0)", "1"),
        T("empty_cannot_make_one", "nums = [], target = 1", "find_target_sum_ways(&[], 1)", "0"),
        T("zeros_take_both_signs", "nums = [0, 0], target = 0", "find_target_sum_ways(&[0, 0], 0)", "4"),
        T("negative_target", "nums = [1], target = -1", "find_target_sum_ways(&[1], -1)", "1"),
    ],
    hidden=[
        T("out_of_reach", "nums = [1, 2], target = 4", "find_target_sum_ways(&[1, 2], 4)", "0"),
        T("out_of_reach_below", "nums = [1], target = -2", "find_target_sum_ways(&[1], -2)", "0"),
        T("wrong_parity", "nums = [1, 1], target = 1", "find_target_sum_ways(&[1, 1], 1)", "0"),
        T("one_zero", "nums = [1, 0], target = 1", "find_target_sum_ways(&[1, 0], 1)", "2"),
        T("balanced", "nums = [2, 3, 5], target = 0", "find_target_sum_ways(&[2, 3, 5], 0)", "2"),
        T("small_mixed", "nums = [1, 2, 1], target = 0", "find_target_sum_ways(&[1, 2, 1], 0)", "2"),
        T("forty_ones", "nums = [1; 40], target = 0", "find_target_sum_ways(&[1; 40], 0)", "137_846_528_820"),
        T("sixty_zeros", "nums = [0; 60], target = 0", "find_target_sum_ways(&[0; 60], 0)", "1 << 60"),
        T("far_target", "nums = [1000], target = -1000", "find_target_sum_ways(&[1000], -1000)", "1"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1232);
            for _ in 0..300 {
                let n = rng.below(12);
                let nums: Vec<u32> = rng.vec(n, 0, 5);
                let target = rng.int(-12, 12) as i32;
                let want = (0u32..(1 << n))
                    .filter(|mask| (0..n).map(|i| if mask >> i & 1 == 1 { nums[i] as i32 } else { -(nums[i] as i32) }).sum::<i32>() == target)
                    .count() as u64;
                check!(format!("nums = {nums:?}, target = {target}"), find_target_sum_ways(&nums, target), want);
            }
        }

        #[test]
        fn scale_sixty() {
            // 2⁶⁰ sign choices for plain recursion.
            let nums: Vec<u32> = (0..60u32).map(|i| i * 7919 % 16 + 1).collect();
            check!("nums[i] = (7919·i) % 16 + 1, 60 numbers, target = 10", find_target_sum_ways(&nums, 10), 11_765_817_607_280_003);
        }
        """,
    ],
    wrong=dict(
        plain_recursion="""
            fn count(nums: &[u32], target: i64) -> u64 {
                match nums {
                    [] => (target == 0) as u64,
                    [x, rest @ ..] => count(rest, target - *x as i64) + count(rest, target + *x as i64),
                }
            }

            pub fn find_target_sum_ways(nums: &[u32], target: i32) -> u64 {
                count(nums, target as i64)
            }
        """,
        no_parity_check="""
            pub fn find_target_sum_ways(nums: &[u32], target: i32) -> u64 {
                let total: i64 = nums.iter().map(|&x| x as i64).sum();
                let doubled = total + target as i64;
                if doubled < 0 || doubled > 2 * total {
                    return 0;
                }
                let plus = (doubled / 2) as usize;
                let mut ways = vec![0u64; plus + 1];
                ways[0] = 1;
                for &x in nums {
                    let x = x as usize;
                    for s in (x..=plus).rev() {
                        ways[s] += ways[s - x];
                    }
                }
                ways[plus]
            }
        """,
        skips_zeros="""
            pub fn find_target_sum_ways(nums: &[u32], target: i32) -> u64 {
                let total: i64 = nums.iter().map(|&x| x as i64).sum();
                let doubled = total + target as i64;
                if doubled < 0 || doubled > 2 * total || doubled % 2 == 1 {
                    return 0;
                }
                let plus = (doubled / 2) as usize;
                let mut ways = vec![0u64; plus + 1];
                ways[0] = 1;
                for &x in nums.iter().filter(|&&x| x > 0) {
                    let x = x as usize;
                    for s in (x..=plus).rev() {
                        ways[s] += ways[s - x];
                    }
                }
                ways[plus]
            }
        """,
    ),
    hints=[("approach", "If the + numbers sum to P, the - numbers sum to total - P, so P - (total - P) = target and P = (total + target) / 2. Count subsets that sum to P."),
           ("rust", "Do the algebra in `i64`, return 0 unless 0 ≤ total + target ≤ 2·total and it is even, then run the counting knapsack over a `Vec<u64>` with the sum running downwards."),
           ("edge case", "A 0 can take either sign, doubling the count; with the downward sweep, `ways[s] += ways[s - 0]` does exactly that.")],
    notes=("The sign choice splits the numbers into a + group and a - group, which is a subset. The transform turns an exponential search into a counting knapsack of size (total + target) / 2.", "O(n × total)", "O(total)"),
    follow_up="Without the algebra, how would you write the DP over running sums from -total to total, and how does its size compare?",
    related=["D11"],
))

P.append(dict(
    slug="last-stone-weight-ii", title="Last stone weight II", level="medium", stage="knapsack", tags=["0/1 knapsack", "subset sum"],
    companies=["Google", "Amazon", "Microsoft"],
    teaches=["Seeing through the story: any sequence of smashes is a split into two piles.",
             "Finding the reachable subset sum closest to half with a backwards scan."],
    statement="""
        Smashing two stones of weights `x ≤ y` destroys the lighter one and leaves a stone of
        weight `y - x` (nothing if they are equal). Smash stones in any order until at most one is
        left. Return the smallest weight that can be left (0 if none).
    """,
    examples=[("stones = [2, 7, 4, 1, 8, 1]", "1"), ("stones = [31, 26, 33, 21, 40]", "5")],
    constraints=["0 ≤ stones.len() ≤ 100", "1 ≤ stones[i] ≤ 100"],
    starter="""
        pub fn last_stone_weight_ii(stones: &[u32]) -> u32 {
            todo!()
        }
    """,
    solution="""
        pub fn last_stone_weight_ii(stones: &[u32]) -> u32 {
            // Any smashing order ends as |A - B| for some split of the stones into A and B.
            let total: u32 = stones.iter().sum();
            let half = (total / 2) as usize;
            let mut reach = vec![false; half + 1];
            reach[0] = true;
            for &x in stones {
                let x = x as usize;
                for s in (x..=half).rev() {
                    reach[s] = reach[s] || reach[s - x];
                }
            }
            // The lighter pile should be as close to half as possible.
            let best = (0..=half).rev().find(|&s| reach[s]).unwrap_or(0) as u32;
            total - 2 * best
        }
    """,
    visible=[
        T("leetcode_six", "stones = [2, 7, 4, 1, 8, 1]", "last_stone_weight_ii(&[2, 7, 4, 1, 8, 1])", "1"),
        T("leetcode_heaviest_first_fails", "stones = [31, 26, 33, 21, 40]", "last_stone_weight_ii(&[31, 26, 33, 21, 40])", "5"),
        T("no_stones", "stones = []", "last_stone_weight_ii(&[])", "0"),
        T("one_stone", "stones = [1]", "last_stone_weight_ii(&[1])", "1"),
        T("equal_pair", "stones = [5, 5]", "last_stone_weight_ii(&[5, 5])", "0"),
    ],
    hidden=[
        T("no_stones", "stones = []", "last_stone_weight_ii(&[])", "0"),
        T("one_heavy", "stones = [100]", "last_stone_weight_ii(&[100])", "100"),
        T("pair", "stones = [1, 2]", "last_stone_weight_ii(&[1, 2])", "1"),
        T("three_equal", "stones = [3, 3, 3]", "last_stone_weight_ii(&[3, 3, 3])", "3"),
        T("splits_evenly", "stones = [1, 1, 4, 2, 2]", "last_stone_weight_ii(&[1, 1, 4, 2, 2])", "0"),
        T("hundred_max", "stones = [100; 100]", "last_stone_weight_ii(&[100; 100])", "0"),
        T("odd_count_max", "stones = [100; 99]", "last_stone_weight_ii(&[100; 99])", "100"),
        T("one_big_rest_small", "stones = [100, 1, 1, 1]", "last_stone_weight_ii(&[100, 1, 1, 1])", "97"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1233);
            for _ in 0..300 {
                let n = rng.below(12);
                let stones: Vec<u32> = rng.vec(n, 1, 30);
                let total: i64 = stones.iter().map(|&x| x as i64).sum();
                let want = (0u32..(1 << n))
                    .map(|mask| {
                        let a: i64 = (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| stones[i] as i64).sum();
                        (total - 2 * a).unsigned_abs() as u32
                    })
                    .min()
                    .unwrap();
                check!(format!("stones = {stones:?}"), last_stone_weight_ii(&stones), want);
            }
        }

        #[test]
        fn scale_hundred() {
            let mut stones: Vec<u32> = (0..99u32).map(|i| i * 7919 % 50 * 2 + 2).collect();
            stones.push(1);
            check!("stones = 99 even weights ((7919·i) % 50 · 2 + 2) and a 1", last_stone_weight_ii(&stones), 1);
        }
        """,
    ],
    wrong=dict(
        heaviest_two_first="""
            use std::collections::BinaryHeap;

            pub fn last_stone_weight_ii(stones: &[u32]) -> u32 {
                let mut heap: BinaryHeap<u32> = stones.iter().copied().collect();
                while heap.len() > 1 {
                    let y = heap.pop().unwrap();
                    let x = heap.pop().unwrap();
                    if y > x {
                        heap.push(y - x);
                    }
                }
                heap.pop().unwrap_or(0)
            }
        """,
        plain_recursion="""
            fn best(stones: &[u32], diff: i64) -> u32 {
                match stones {
                    [] => diff.unsigned_abs() as u32,
                    [x, rest @ ..] => best(rest, diff + *x as i64).min(best(rest, diff - *x as i64)),
                }
            }

            pub fn last_stone_weight_ii(stones: &[u32]) -> u32 {
                best(stones, 0)
            }
        """,
        parity_only="""
            pub fn last_stone_weight_ii(stones: &[u32]) -> u32 {
                stones.iter().sum::<u32>() % 2
            }
        """,
    ),
    hints=[("approach", "Every smash subtracts one stone from another, so whatever is left is (sum of one group) - (sum of the other). Make the two groups as even as possible."),
           ("rust", "Build a `Vec<bool>` of reachable sums up to total / 2 (0/1 knapsack, sweeping down), then `(0..=half).rev().find(|&s| reach[s])`."),
           ("edge case", "Always smashing the two heaviest stones (Last stone weight I) is not optimal here: [31, 26, 33, 21, 40] leaves 9 that way, but 5 is possible.")],
    notes=("Signs again: each stone ends up added or subtracted, and any split can be realised by some smash order. The best split puts the lighter group as close to total / 2 as possible.", "O(n × total)", "O(total)"),
    follow_up="Prove that every split into two groups can be realised by some order of smashes.",
    related=["D7"],
))

P.append(dict(
    slug="ones-and-zeroes", title="Ones and zeroes", level="medium", stage="knapsack", tags=["0/1 knapsack", "2-D capacity"],
    companies=["Google", "Amazon", "Microsoft"],
    teaches=["A knapsack with two capacities: the table is indexed by zeros used and ones used.",
             "Counting bytes with `bytes().filter(..).count()`."],
    statement="""
        Each string in `strs` is made of `'0'` and `'1'`. Return the largest number of strings you
        can pick (each at most once) so that together they contain at most `m` zeros and at most
        `n` ones.
    """,
    examples=[("strs = [\"10\", \"0001\", \"111001\", \"1\", \"0\"], m = 5, n = 3", "4 (\"10\", \"0001\", \"1\", \"0\")")],
    constraints=["0 ≤ strs.len() ≤ 600", "1 ≤ strs[i].len() ≤ 100", "0 ≤ m, n ≤ 100"],
    starter="""
        pub fn find_max_form(strs: &[&str], m: usize, n: usize) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn find_max_form(strs: &[&str], m: usize, n: usize) -> usize {
            // best[z][o] = the most strings using at most z zeros and o ones.
            let mut best = vec![vec![0usize; n + 1]; m + 1];
            for s in strs {
                let zeros = s.bytes().filter(|&b| b == b'0').count();
                let ones = s.len() - zeros;
                // Both capacities downwards: each string is picked at most once.
                for z in (zeros..=m).rev() {
                    for o in (ones..=n).rev() {
                        best[z][o] = best[z][o].max(best[z - zeros][o - ones] + 1);
                    }
                }
            }
            best[m][n]
        }
    """,
    visible=[
        T("leetcode_five", "strs = [\"10\", \"0001\", \"111001\", \"1\", \"0\"], m = 5, n = 3", "find_max_form(&[\"10\", \"0001\", \"111001\", \"1\", \"0\"], 5, 3)", "4"),
        T("leetcode_three", "strs = [\"10\", \"0\", \"1\"], m = 1, n = 1", "find_max_form(&[\"10\", \"0\", \"1\"], 1, 1)", "2"),
        T("no_strings", "strs = [], m = 5, n = 5", "find_max_form(&[], 5, 5)", "0"),
        T("no_budget", "strs = [\"0\"], m = 0, n = 0", "find_max_form(&[\"0\"], 0, 0)", "0"),
        T("each_string_once", "strs = [\"0\"], m = 5, n = 5", "find_max_form(&[\"0\"], 5, 5)", "1"),
    ],
    hidden=[
        T("not_enough_zeros", "strs = [\"00\"], m = 1, n = 5", "find_max_form(&[\"00\"], 1, 5)", "0"),
        T("all_fit", "strs = [\"0\", \"0\", \"1\", \"1\"], m = 2, n = 2", "find_max_form(&[\"0\", \"0\", \"1\", \"1\"], 2, 2)", "4"),
        T("ones_budget_zero", "strs = [\"11\", \"0\", \"0\"], m = 2, n = 0", "find_max_form(&[\"11\", \"0\", \"0\"], 2, 0)", "2"),
        T("shortest_first_fails", "strs = [\"111\", \"001\", \"110\", \"0001\"], m = 4, n = 3", "find_max_form(&[\"111\", \"001\", \"110\", \"0001\"], 4, 3)", "2"),
        T("shortest_first_fails_again", "strs = [\"001\", \"110\", \"0000\", \"0000\"], m = 9, n = 2", "find_max_form(&[\"001\", \"110\", \"0000\", \"0000\"], 9, 2)", "3"),
        T("duplicates", "strs = [\"01\"; 10], m = 4, n = 100", "find_max_form(&[\"01\"; 10], 4, 100)", "4"),
        T("big_budget", "strs = [\"01\"; 600], m = 100, n = 100", "find_max_form(&[\"01\"; 600], 100, 100)", "100"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1234);
            for _ in 0..300 {
                let k = rng.below(10);
                let mut strs: Vec<String> = Vec::new();
                for _ in 0..k {
                    let len = rng.int(1, 4) as usize;
                    strs.push(rng.string(len, "01"));
                }
                let refs: Vec<&str> = strs.iter().map(|s| s.as_str()).collect();
                let (m, n) = (rng.int(0, 6) as usize, rng.int(0, 6) as usize);
                let mut want = 0;
                for mask in 0u32..(1 << k) {
                    let picked: Vec<&String> = (0..k).filter(|&i| mask >> i & 1 == 1).map(|i| &strs[i]).collect();
                    let zeros: usize = picked.iter().map(|s| s.bytes().filter(|&b| b == b'0').count()).sum();
                    let total: usize = picked.iter().map(|s| s.len()).sum();
                    if zeros <= m && total - zeros <= n {
                        want = want.max(picked.len());
                    }
                }
                check!(format!("strs = {strs:?}, m = {m}, n = {n}"), find_max_form(&refs, m, n), want);
            }
        }

        #[test]
        fn scale_600() {
            let strs: Vec<String> = (0..600usize)
                .map(|i| (0..(i * 13) % 9 + 1).map(|k| if (i * 7 + k * 3) % 5 < 2 { '0' } else { '1' }).collect())
                .collect();
            let refs: Vec<&str> = strs.iter().map(|s| s.as_str()).collect();
            check!("600 strings of length 1–9, m = 100, n = 100", find_max_form(&refs, 100, 100), 127);
        }
        """,
    ],
    wrong=dict(
        capacities_upwards="""
            pub fn find_max_form(strs: &[&str], m: usize, n: usize) -> usize {
                let mut best = vec![vec![0usize; n + 1]; m + 1];
                for s in strs {
                    let zeros = s.bytes().filter(|&b| b == b'0').count();
                    let ones = s.len() - zeros;
                    for z in zeros..=m {
                        for o in ones..=n {
                            best[z][o] = best[z][o].max(best[z - zeros][o - ones] + 1);
                        }
                    }
                }
                best[m][n]
            }
        """,
        shortest_first="""
            pub fn find_max_form(strs: &[&str], m: usize, n: usize) -> usize {
                let mut sorted = strs.to_vec();
                sorted.sort_by_key(|s| s.len());
                let (mut zeros_left, mut ones_left, mut count) = (m, n, 0);
                for s in sorted {
                    let zeros = s.bytes().filter(|&b| b == b'0').count();
                    let ones = s.len() - zeros;
                    if zeros <= zeros_left && ones <= ones_left {
                        zeros_left -= zeros;
                        ones_left -= ones;
                        count += 1;
                    }
                }
                count
            }
        """,
        plain_recursion="""
            fn best(strs: &[&str], m: usize, n: usize) -> usize {
                match strs {
                    [] => 0,
                    [s, rest @ ..] => {
                        let zeros = s.bytes().filter(|&b| b == b'0').count();
                        let ones = s.len() - zeros;
                        let skip = best(rest, m, n);
                        if zeros <= m && ones <= n { skip.max(1 + best(rest, m - zeros, n - ones)) } else { skip }
                    }
                }
            }

            pub fn find_max_form(strs: &[&str], m: usize, n: usize) -> usize {
                best(strs, m, n)
            }
        """,
    ),
    hints=[("approach", "It is 0/1 knapsack where every item has two weights (its zeros and its ones) and value 1. The table is indexed by both budgets."),
           ("rust", "`vec![vec![0usize; n + 1]; m + 1]`; for each string count zeros with `s.bytes().filter(|&b| b == b'0').count()`, then sweep both indices downwards."),
           ("edge case", "Picking the shortest strings first is not optimal: it can spend the scarce digit on a string that blocks two others.")],
    notes=("Adding a second capacity adds a second index; the downward sweep in both keeps each string to one use.", "O(k × m × n) for k strings", "O(m × n)"),
    follow_up="How would the table change if you could pick each string any number of times?",
    related=["D2"],
))

# ---------------------------------------------------------------- State machines (medium)

P.append(dict(
    slug="paint-house", title="Paint house", level="medium", stage="state-machines", tags=["state DP", "[u64; 3]"],
    companies=["Amazon", "Google", "LinkedIn", "Microsoft"],
    teaches=["The state is \"the colour of the last house\": three numbers carried from house to house.",
             "A fixed-size array `[u64; 3]` rebuilt each step instead of a table."],
    statement="""
        `costs[i][c]` is the cost of painting house `i` with colour `c` (red, green or blue). No
        two neighbouring houses may have the same colour. Return the cheapest way to paint every
        house.
    """,
    examples=[("costs = [[17, 2, 17], [16, 16, 5], [14, 3, 19]]", "10 (green, blue, green)")],
    constraints=["0 ≤ costs.len() ≤ 2·10⁵", "0 ≤ costs[i][c] ≤ 10⁴"],
    starter="""
        pub fn min_cost(costs: &[[u32; 3]]) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn min_cost(costs: &[[u32; 3]]) -> u64 {
            // best[c] = the cheapest way to paint the houses so far, the last one in colour c.
            let mut best = [0u64; 3];
            for house in costs {
                best = [
                    house[0] as u64 + best[1].min(best[2]),
                    house[1] as u64 + best[0].min(best[2]),
                    house[2] as u64 + best[0].min(best[1]),
                ];
            }
            best.into_iter().min().unwrap()
        }
    """,
    visible=[
        T("leetcode_three", "costs = [[17, 2, 17], [16, 16, 5], [14, 3, 19]]", "min_cost(&[[17, 2, 17], [16, 16, 5], [14, 3, 19]])", "10"),
        T("leetcode_one", "costs = [[7, 6, 2]]", "min_cost(&[[7, 6, 2]])", "2"),
        T("no_houses", "costs = []", "min_cost(&[])", "0"),
        T("neighbours_differ", "costs = [[1, 2, 3], [1, 2, 3]]", "min_cost(&[[1, 2, 3], [1, 2, 3]])", "3"),
        T("cheapest_first_is_a_trap", "costs = [[1, 100, 100], [1, 100, 100], [100, 1, 100]]", "min_cost(&[[1, 100, 100], [1, 100, 100], [100, 1, 100]])", "102"),
    ],
    hidden=[
        T("no_houses", "costs = []", "min_cost(&[])", "0"),
        T("one_house_zero", "costs = [[0, 5, 5]]", "min_cost(&[[0, 5, 5]])", "0"),
        T("two_houses", "costs = [[1, 5, 3], [2, 9, 4]]", "min_cost(&[[1, 5, 3], [2, 9, 4]])", "5"),
        T("five_houses", "costs = [[5, 8, 6], [19, 14, 13], [7, 5, 12], [14, 15, 17], [3, 20, 10]]", "min_cost(&[[5, 8, 6], [19, 14, 13], [7, 5, 12], [14, 15, 17], [3, 20, 10]])", "43"),
        T("ties", "costs = [[3, 5, 3], [6, 17, 6], [7, 13, 18], [9, 10, 18]]", "min_cost(&[[3, 5, 3], [6, 17, 6], [7, 13, 18], [9, 10, 18]])", "26"),
        T("all_max", "costs = [[10000; 3]; 3]", "min_cost(&[[10_000; 3]; 3])", "30_000"),
        T("past_u32", "costs = [[10000, 10000, 10000]; 1000000]", "min_cost(&vec![[10_000; 3]; 1_000_000])", "10_000_000_000"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn cheapest(costs: &[[u32; 3]], last: usize) -> u64 {
                match costs {
                    [] => 0,
                    [house, rest @ ..] => (0..3).filter(|&c| c != last).map(|c| house[c] as u64 + cheapest(rest, c)).min().unwrap(),
                }
            }
            let mut rng = anneal_prelude::Rng::new(1235);
            for _ in 0..300 {
                let n = rng.below(8);
                let mut costs: Vec<[u32; 3]> = Vec::new();
                for _ in 0..n {
                    let r = rng.int(0, 9) as u32;
                    let g = rng.int(0, 9) as u32;
                    let b = rng.int(0, 9) as u32;
                    costs.push([r, g, b]);
                }
                check!(format!("costs = {costs:?}"), min_cost(&costs), cheapest(&costs, 3));
            }
        }

        #[test]
        fn scale_200k() {
            let costs: Vec<[u32; 3]> = (0..200_000u64).map(|i| [(i * 7919 % 10_000) as u32, (i * 104_729 % 10_000) as u32, (i * 15_485_863 % 10_000) as u32]).collect();
            check!("costs[i] = [(7919·i), (104729·i), (15485863·i)] % 10000, 200000 houses", min_cost(&costs), 549_408_720);
        }
        """,
    ],
    wrong=dict(
        cheapest_different_colour="""
            pub fn min_cost(costs: &[[u32; 3]]) -> u64 {
                let mut last = 3;
                let mut total = 0u64;
                for house in costs {
                    let c = (0..3).filter(|&c| c != last).min_by_key(|&c| house[c]).unwrap();
                    total += house[c] as u64;
                    last = c;
                }
                total
            }
        """,
        ignores_neighbours="""
            pub fn min_cost(costs: &[[u32; 3]]) -> u64 {
                costs.iter().map(|h| *h.iter().min().unwrap() as u64).sum()
            }
        """,
        plain_recursion="""
            fn cheapest(costs: &[[u32; 3]], last: usize) -> u64 {
                match costs {
                    [] => 0,
                    [house, rest @ ..] => (0..3).filter(|&c| c != last).map(|c| house[c] as u64 + cheapest(rest, c)).min().unwrap(),
                }
            }

            pub fn min_cost(costs: &[[u32; 3]]) -> u64 {
                cheapest(costs, 3)
            }
        """,
    ),
    hints=[("approach", "Carry three numbers: the cheapest total so far if the last house is red, green or blue. Each new colour adds its cost to the cheaper of the other two."),
           ("rust", "Rebuild a `[u64; 3]` per house with an array literal; `best.into_iter().min().unwrap()` at the end (an empty street leaves `[0, 0, 0]`)."),
           ("edge case", "Picking the cheapest allowed colour house by house is greedy and can force an expensive house later.")],
    notes=("The only thing a house needs to know about the past is the previous colour, so three running totals are the whole state. Each step is constant work.", "O(n)", "O(1)"),
    follow_up="With k colours instead of 3, how do you avoid O(n·k²)? (Keep the smallest and second-smallest of the previous row.)",
    related=["D8"],
))

P.append(dict(
    slug="best-time-to-buy-and-sell-stock-with-cooldown", title="Best time to buy and sell stock with cooldown", level="medium", stage="state-machines",
    tags=["state machine", "stocks"],
    companies=["Amazon", "Google", "Meta", "Apple", "Microsoft", "Bloomberg"],
    teaches=["Modelling a day as a state machine: holding, just sold (cooling down), or free to buy.",
             "Updating all states from yesterday's values at once with a tuple assignment."],
    statement="""
        `prices[i]` is a stock's price on day `i`. You may buy and sell as many times as you like,
        holding at most one share at a time, but after you sell you must wait one day before
        buying again. Return the largest total profit.
    """,
    examples=[("prices = [1, 2, 3, 0, 2]", "3 (buy, sell, cooldown, buy, sell)")],
    constraints=["0 ≤ prices.len() ≤ 2·10⁵", "0 ≤ prices[i] ≤ 10⁴"],
    starter="""
        pub fn max_profit(prices: &[u32]) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn max_profit(prices: &[u32]) -> u64 {
            // The best profit so far if, at the end of today, you are…
            let impossible = i64::MIN / 2; // below any real profit, and safe to add to
            let mut holding = impossible; // …holding a share
            let mut cooling = impossible; // …not holding, having sold today
            let mut free = 0i64; // …not holding, free to buy tomorrow
            for &p in prices {
                let p = p as i64;
                (holding, cooling, free) = (holding.max(free - p), holding + p, free.max(cooling));
            }
            free.max(cooling) as u64
        }
    """,
    visible=[
        T("leetcode_five", "prices = [1, 2, 3, 0, 2]", "max_profit(&[1, 2, 3, 0, 2])", "3"),
        T("leetcode_one", "prices = [1]", "max_profit(&[1])", "0"),
        T("empty", "prices = []", "max_profit(&[])", "0"),
        T("falling", "prices = [5, 4, 3]", "max_profit(&[5, 4, 3])", "0"),
        T("cooldown_costs_a_trade", "prices = [1, 2, 1, 2]", "max_profit(&[1, 2, 1, 2])", "1"),
    ],
    hidden=[
        T("empty", "prices = []", "max_profit(&[])", "0"),
        T("rising", "prices = [1, 2, 4]", "max_profit(&[1, 2, 4])", "3"),
        T("dip_first", "prices = [2, 1, 4]", "max_profit(&[2, 1, 4])", "3"),
        T("skip_a_small_trade", "prices = [6, 1, 6, 4, 3, 0, 2]", "max_profit(&[6, 1, 6, 4, 3, 0, 2])", "7"),
        T("one_trade_beats_two", "prices = [1, 4, 2]", "max_profit(&[1, 4, 2])", "3"),
        T("flat", "prices = [3, 3, 3]", "max_profit(&[3, 3, 3])", "0"),
        T("mixed", "prices = [3, 3, 5, 0, 0, 3, 1, 4]", "max_profit(&[3, 3, 5, 0, 0, 3, 1, 4])", "6"),
        T("big_swings", "prices = [0, 10000] × 1000", "max_profit(&[0u32, 10_000].repeat(1000))", "5_000_000"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn best(p: &[u32], holding: bool) -> i64 {
                match p {
                    [] => 0,
                    [x, rest @ ..] => {
                        let x = *x as i64;
                        let wait = best(rest, holding);
                        if holding {
                            wait.max(x + best(rest.get(1..).unwrap_or(&[]), false))
                        } else {
                            wait.max(-x + best(rest, true))
                        }
                    }
                }
            }
            let mut rng = anneal_prelude::Rng::new(1236);
            for _ in 0..300 {
                let n = rng.below(11);
                let prices: Vec<u32> = rng.vec(n, 0, 9);
                check!(format!("prices = {prices:?}"), max_profit(&prices), best(&prices, false) as u64);
            }
        }

        #[test]
        fn scale_200k() {
            let prices: Vec<u32> = (0..200_000u32).map(|i| i * 7919 % 10_000).collect();
            check!("prices[i] = (7919·i) % 10000, 200000 days", max_profit(&prices), 329_588_780);
        }
        """,
    ],
    wrong=dict(
        no_cooldown="""
            pub fn max_profit(prices: &[u32]) -> u64 {
                prices.windows(2).map(|w| w[1].saturating_sub(w[0]) as u64).sum()
            }
        """,
        cooldown_after_buying="""
            pub fn max_profit(prices: &[u32]) -> u64 {
                let (mut holding, mut just_bought, mut free) = (i64::MIN / 2, i64::MIN / 2, 0i64);
                for &p in prices {
                    let p = p as i64;
                    (holding, just_bought, free) = (holding.max(just_bought), free - p, free.max(holding + p));
                }
                free as u64
            }
        """,
        plain_recursion="""
            fn best(p: &[u32], holding: bool) -> i64 {
                match p {
                    [] => 0,
                    [x, rest @ ..] => {
                        let x = *x as i64;
                        let wait = best(rest, holding);
                        if holding {
                            wait.max(x + best(rest.get(1..).unwrap_or(&[]), false))
                        } else {
                            wait.max(-x + best(rest, true))
                        }
                    }
                }
            }

            pub fn max_profit(prices: &[u32]) -> u64 {
                best(prices, false) as u64
            }
        """,
    ),
    hints=[("approach", "Three states at the end of each day: holding, just sold (so tomorrow is a cooldown), and free. Holding comes from holding or buying from free; just sold comes from holding; free comes from free or cooling."),
           ("rust", "Three `i64`s updated together: `(holding, cooling, free) = (holding.max(free - p), holding + p, free.max(cooling));` reads only yesterday's values."),
           ("edge case", "Start `holding` and `cooling` at a very negative value (not `i64::MIN`, which overflows when you add a price).")],
    notes=("Each day's best profit per state depends only on yesterday's three numbers. The cooldown is the rule that the buy transition leaves from free, not from cooling.", "O(n)", "O(1)"),
    follow_up="Draw the state machine. How does it change for a two-day cooldown?",
    related=["L7", "D8"],
))

P.append(dict(
    slug="best-time-to-buy-and-sell-stock-with-transaction-fee", title="Best time to buy and sell stock with transaction fee", level="medium", stage="state-machines",
    tags=["state machine", "stocks"],
    companies=["Amazon", "Google", "Meta", "Microsoft", "Bloomberg"],
    teaches=["The two-state machine (holding / free), with the fee paid on the sell transition.",
             "Why taking every price rise stops working once each trade costs something."],
    statement="""
        `prices[i]` is the price on day `i`. You may trade as often as you like, holding at most
        one share at a time, but each completed trade (a buy and its sell) costs `fee`. Return the
        largest total profit.
    """,
    examples=[("prices = [1, 3, 2, 8, 4, 9], fee = 2", "8 (buy 1 sell 8, buy 4 sell 9)")],
    constraints=["0 ≤ prices.len() ≤ 2·10⁵", "0 ≤ prices[i], fee ≤ 5·10⁴"],
    starter="""
        pub fn max_profit(prices: &[u32], fee: u32) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn max_profit(prices: &[u32], fee: u32) -> u64 {
            let fee = fee as i64;
            // The best profit so far if, at the end of today, you are holding a share / not.
            let (mut holding, mut free) = (i64::MIN / 2, 0i64);
            for &p in prices {
                let p = p as i64;
                (holding, free) = (holding.max(free - p), free.max(holding + p - fee));
            }
            free as u64
        }
    """,
    visible=[
        T("leetcode_fee_two", "prices = [1, 3, 2, 8, 4, 9], fee = 2", "max_profit(&[1, 3, 2, 8, 4, 9], 2)", "8"),
        T("leetcode_fee_three", "prices = [1, 3, 7, 5, 10, 3], fee = 3", "max_profit(&[1, 3, 7, 5, 10, 3], 3)", "6"),
        T("empty", "prices = [], fee = 1", "max_profit(&[], 1)", "0"),
        T("one_day", "prices = [5], fee = 1", "max_profit(&[5], 1)", "0"),
        T("fee_eats_the_gain", "prices = [1, 3], fee = 5", "max_profit(&[1, 3], 5)", "0"),
        T("no_fee", "prices = [1, 3, 2, 4], fee = 0", "max_profit(&[1, 3, 2, 4], 0)", "4"),
    ],
    hidden=[
        T("empty", "prices = [], fee = 0", "max_profit(&[], 0)", "0"),
        T("break_even", "prices = [1, 5], fee = 4", "max_profit(&[1, 5], 4)", "0"),
        T("just_worth_it", "prices = [1, 5], fee = 3", "max_profit(&[1, 5], 3)", "1"),
        T("falling", "prices = [9, 8, 7, 1, 2], fee = 3", "max_profit(&[9, 8, 7, 1, 2], 3)", "0"),
        T("hold_through_dips", "prices = [4, 5, 2, 4, 3, 3, 1, 2, 5, 4], fee = 1", "max_profit(&[4, 5, 2, 4, 3, 3, 1, 2, 5, 4], 1)", "4"),
        T("big_values", "prices = [0, 50000] × 1000, fee = 1", "max_profit(&[0u32, 50_000].repeat(1000), 1)", "49_999_000"),
        T("huge_fee", "prices = [0, 50000], fee = 50000", "max_profit(&[0, 50_000], 50_000)", "0"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn best(p: &[u32], fee: i64, holding: bool) -> i64 {
                match p {
                    [] => 0,
                    [x, rest @ ..] => {
                        let x = *x as i64;
                        let wait = best(rest, fee, holding);
                        if holding { wait.max(x - fee + best(rest, fee, false)) } else { wait.max(-x + best(rest, fee, true)) }
                    }
                }
            }
            let mut rng = anneal_prelude::Rng::new(1237);
            for _ in 0..300 {
                let n = rng.below(11);
                let prices: Vec<u32> = rng.vec(n, 0, 9);
                let fee = rng.int(0, 4) as u32;
                check!(format!("prices = {prices:?}, fee = {fee}"), max_profit(&prices, fee), best(&prices, fee as i64, false) as u64);
            }
        }

        #[test]
        fn scale_200k() {
            let prices: Vec<u32> = (0..200_000u32).map(|i| i * 7919 % 10_000).collect();
            check!("prices[i] = (7919·i) % 10000, 200000 days, fee = 50", max_profit(&prices, 50), 327_507_780);
        }
        """,
    ],
    wrong=dict(
        ignores_the_fee="""
            pub fn max_profit(prices: &[u32], _fee: u32) -> u64 {
                prices.windows(2).map(|w| w[1].saturating_sub(w[0]) as u64).sum()
            }
        """,
        fee_on_every_rise="""
            pub fn max_profit(prices: &[u32], fee: u32) -> u64 {
                prices.windows(2).map(|w| w[1].saturating_sub(w[0]).saturating_sub(fee) as u64).sum()
            }
        """,
        plain_recursion="""
            fn best(p: &[u32], fee: i64, holding: bool) -> i64 {
                match p {
                    [] => 0,
                    [x, rest @ ..] => {
                        let x = *x as i64;
                        let wait = best(rest, fee, holding);
                        if holding { wait.max(x - fee + best(rest, fee, false)) } else { wait.max(-x + best(rest, fee, true)) }
                    }
                }
            }

            pub fn max_profit(prices: &[u32], fee: u32) -> u64 {
                best(prices, fee as i64, false) as u64
            }
        """,
    ),
    hints=[("approach", "Two states: holding a share or not. Holding = max(keep holding, buy today from not-holding); not holding = max(stay out, sell today from holding and pay the fee)."),
           ("rust", "`(holding, free) = (holding.max(free - p), free.max(holding + p - fee));` with `i64` values and `holding` starting very negative."),
           ("edge case", "Taking every up-day as its own trade pays the fee many times; one long trade through small dips can be better: [1, 3, 2, 8, 4, 9] with fee 2.")],
    notes=("The fee is charged once per sell, so the machine decides by itself when holding through a small dip beats selling and re-buying.", "O(n)", "O(1)"),
    follow_up="Why is it equivalent to charge the fee when buying instead of when selling?",
    related=["L7"],
))

P.append(dict(
    slug="best-time-to-buy-and-sell-stock-iii", title="Best time to buy and sell stock III", level="hard", stage="state-machines", tags=["state machine", "stocks"],
    companies=["Amazon", "Google", "Meta", "Microsoft", "Apple", "Bloomberg", "Goldman Sachs"],
    teaches=["Four states in a line: after the first buy, first sell, second buy, second sell.",
             "Updating the states in order within a day, which is safe because a same-day buy and sell earns nothing."],
    statement="""
        `prices[i]` is the price on day `i`. Make at most two trades (buy then sell), never
        holding more than one share. Return the largest total profit.
    """,
    examples=[("prices = [3, 3, 5, 0, 0, 3, 1, 4]", "6 (buy 0 sell 3, buy 1 sell 4)")],
    constraints=["0 ≤ prices.len() ≤ 2·10⁵", "0 ≤ prices[i] ≤ 10⁵"],
    starter="""
        pub fn max_profit(prices: &[u32]) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn max_profit(prices: &[u32]) -> u64 {
            // The best profit so far after the first buy, first sell, second buy, second sell.
            let impossible = i64::MIN / 2;
            let (mut buy1, mut sell1, mut buy2, mut sell2) = (impossible, 0i64, impossible, 0i64);
            for &p in prices {
                let p = p as i64;
                buy1 = buy1.max(-p);
                sell1 = sell1.max(buy1 + p);
                buy2 = buy2.max(sell1 - p);
                sell2 = sell2.max(buy2 + p);
            }
            sell2 as u64
        }
    """,
    visible=[
        T("leetcode_eight", "prices = [3, 3, 5, 0, 0, 3, 1, 4]", "max_profit(&[3, 3, 5, 0, 0, 3, 1, 4])", "6"),
        T("leetcode_rising", "prices = [1, 2, 3, 4, 5]", "max_profit(&[1, 2, 3, 4, 5])", "4"),
        T("leetcode_falling", "prices = [7, 6, 4, 3, 1]", "max_profit(&[7, 6, 4, 3, 1])", "0"),
        T("empty", "prices = []", "max_profit(&[])", "0"),
        T("one_day", "prices = [1]", "max_profit(&[1])", "0"),
        T("at_most_two", "prices = [1, 5, 2, 6, 3, 7] (three rises, only two trades)", "max_profit(&[1, 5, 2, 6, 3, 7])", "9"),
    ],
    hidden=[
        T("empty", "prices = []", "max_profit(&[])", "0"),
        T("leetcode_ten", "prices = [1, 2, 4, 2, 5, 7, 2, 4, 9, 0]", "max_profit(&[1, 2, 4, 2, 5, 7, 2, 4, 9, 0])", "13"),
        T("two_small", "prices = [2, 1, 2, 0, 1]", "max_profit(&[2, 1, 2, 0, 1])", "2"),
        T("two_trades", "prices = [3, 2, 6, 5, 0, 3]", "max_profit(&[3, 2, 6, 5, 0, 3])", "7"),
        T("flat", "prices = [4, 4, 4, 4]", "max_profit(&[4, 4, 4, 4])", "0"),
        T("one_big_rise", "prices = [0, 100000]", "max_profit(&[0, 100_000])", "100_000"),
        T("many_swings", "prices = [0, 100000] × 1000", "max_profit(&[0u32, 100_000].repeat(1000))", "200_000"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn best(p: &[u32], holding: bool, left: usize) -> i64 {
                match p {
                    [] => 0,
                    [x, rest @ ..] => {
                        let x = *x as i64;
                        let wait = best(rest, holding, left);
                        if holding {
                            wait.max(x + best(rest, false, left))
                        } else if left > 0 {
                            wait.max(-x + best(rest, true, left - 1))
                        } else {
                            wait
                        }
                    }
                }
            }
            let mut rng = anneal_prelude::Rng::new(1238);
            for _ in 0..300 {
                let n = rng.below(11);
                let prices: Vec<u32> = rng.vec(n, 0, 9);
                check!(format!("prices = {prices:?}"), max_profit(&prices), best(&prices, false, 2) as u64);
            }
        }

        #[test]
        fn scale_200k() {
            let prices: Vec<u32> = (0..200_000u32).map(|i| i * 7919 % 10_000).collect();
            check!("prices[i] = (7919·i) % 10000, 200000 days", max_profit(&prices), 19_998);
        }
        """,
    ],
    wrong=dict(
        two_biggest_rises="""
            pub fn max_profit(prices: &[u32]) -> u64 {
                let mut runs: Vec<u64> = Vec::new();
                let mut start = 0;
                for i in 1..=prices.len() {
                    if i == prices.len() || prices[i] <= prices[i - 1] {
                        if i - 1 > start {
                            runs.push((prices[i - 1] - prices[start]) as u64);
                        }
                        start = i;
                    }
                }
                runs.sort_unstable_by(|a, b| b.cmp(a));
                runs.iter().take(2).sum()
            }
        """,
        one_trade="""
            pub fn max_profit(prices: &[u32]) -> u64 {
                let (mut low, mut best) = (u32::MAX, 0u32);
                for &p in prices {
                    low = low.min(p);
                    best = best.max(p - low);
                }
                best as u64
            }
        """,
        every_split_point="""
            fn one_trade(prices: &[u32]) -> u64 {
                let (mut low, mut best) = (u32::MAX, 0u32);
                for &p in prices {
                    low = low.min(p);
                    best = best.max(p - low);
                }
                best as u64
            }

            pub fn max_profit(prices: &[u32]) -> u64 {
                (0..=prices.len()).map(|k| one_trade(&prices[..k]) + one_trade(&prices[k..])).max().unwrap_or(0)
            }
        """,
    ),
    hints=[("approach", "Track four running bests: after buying once, after selling once, after buying a second time, after selling a second time. Each one feeds the next."),
           ("rust", "Four `i64`s. Updating them in order within the same day is fine: buying and selling on one day adds 0."),
           ("edge case", "The two best separate rises aren't always the answer: merging two rises into one trade can free a trade for a bigger one.")],
    notes=("buy1 = max(buy1, -p), sell1 = max(sell1, buy1 + p), buy2 = max(buy2, sell1 - p), sell2 = max(sell2, buy2 + p). The chain enforces the order of trades; unused trades just stay at 0 profit.", "O(n)", "O(1)"),
    follow_up="Another way: best single trade in prices[..k] plus best in prices[k..], for every k, with two passes. Write it and compare.",
    related=["D2"],
))

P.append(dict(
    slug="best-time-to-buy-and-sell-stock-iv", title="Best time to buy and sell stock IV", level="hard", stage="state-machines", tags=["state machine", "stocks", "Vec<i64>"],
    companies=["Amazon", "Google", "Meta", "Microsoft", "Apple", "Bloomberg"],
    teaches=["The same chain with `k` links: `buy[j]` and `sell[j]` for j = 1..=k.",
             "Spotting when `k` stops mattering (k ≥ n / 2) and switching to the greedy answer."],
    statement="""
        `prices[i]` is the price on day `i`. Make at most `k` trades (buy then sell), never holding
        more than one share. Return the largest total profit.
    """,
    examples=[("k = 2, prices = [3, 2, 6, 5, 0, 3]", "7 (buy 2 sell 6, buy 0 sell 3)")],
    constraints=["0 ≤ k ≤ 10⁵", "0 ≤ prices.len() ≤ 2·10⁵", "0 ≤ prices[i] ≤ 10⁴"],
    starter="""
        pub fn max_profit(k: usize, prices: &[u32]) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn max_profit(k: usize, prices: &[u32]) -> u64 {
            // With k ≥ n / 2 you can take every rise, so k no longer limits anything.
            if k >= prices.len() / 2 {
                return prices.windows(2).map(|w| w[1].saturating_sub(w[0]) as u64).sum();
            }
            // buy[j] / sell[j] = the best profit after the j-th buy / j-th sell.
            let mut buy = vec![i64::MIN / 2; k + 1];
            let mut sell = vec![0i64; k + 1];
            for &p in prices {
                let p = p as i64;
                for j in 1..=k {
                    buy[j] = buy[j].max(sell[j - 1] - p);
                    sell[j] = sell[j].max(buy[j] + p);
                }
            }
            sell[k] as u64
        }
    """,
    visible=[
        T("leetcode_three_days", "k = 2, prices = [2, 4, 1]", "max_profit(2, &[2, 4, 1])", "2"),
        T("leetcode_six_days", "k = 2, prices = [3, 2, 6, 5, 0, 3]", "max_profit(2, &[3, 2, 6, 5, 0, 3])", "7"),
        T("no_trades_allowed", "k = 0, prices = [1, 5]", "max_profit(0, &[1, 5])", "0"),
        T("empty", "k = 1, prices = []", "max_profit(1, &[])", "0"),
        T("one_trade", "k = 1, prices = [1, 5, 2, 6, 3, 7]", "max_profit(1, &[1, 5, 2, 6, 3, 7])", "6"),
        T("k_larger_than_needed", "k = 100, prices = [1, 2, 1, 2, 1, 2]", "max_profit(100, &[1, 2, 1, 2, 1, 2])", "3"),
    ],
    hidden=[
        T("empty_no_trades", "k = 0, prices = []", "max_profit(0, &[])", "0"),
        T("two_of_three", "k = 2, prices = [1, 5, 2, 6, 3, 7]", "max_profit(2, &[1, 5, 2, 6, 3, 7])", "9"),
        T("three_of_three", "k = 3, prices = [1, 5, 2, 6, 3, 7]", "max_profit(3, &[1, 5, 2, 6, 3, 7])", "12"),
        T("four_of_three", "k = 4, prices = [1, 5, 2, 6, 3, 7]", "max_profit(4, &[1, 5, 2, 6, 3, 7])", "12"),
        T("falling", "k = 3, prices = [7, 6, 4, 3, 1]", "max_profit(3, &[7, 6, 4, 3, 1])", "0"),
        T("one_day", "k = 5, prices = [4]", "max_profit(5, &[4])", "0"),
        T("merge_to_save_a_trade", "k = 2, prices = [1, 2, 4, 2, 5, 7, 2, 4, 9, 0]", "max_profit(2, &[1, 2, 4, 2, 5, 7, 2, 4, 9, 0])", "13"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn best(p: &[u32], holding: bool, left: usize) -> i64 {
                match p {
                    [] => 0,
                    [x, rest @ ..] => {
                        let x = *x as i64;
                        let wait = best(rest, holding, left);
                        if holding {
                            wait.max(x + best(rest, false, left))
                        } else if left > 0 {
                            wait.max(-x + best(rest, true, left - 1))
                        } else {
                            wait
                        }
                    }
                }
            }
            let mut rng = anneal_prelude::Rng::new(1239);
            for _ in 0..300 {
                let n = rng.below(11);
                let prices: Vec<u32> = rng.vec(n, 0, 9);
                let k = rng.int(0, 4) as usize;
                check!(format!("k = {k}, prices = {prices:?}"), max_profit(k, &prices), best(&prices, false, k) as u64);
            }
        }

        #[test]
        fn scale_k_100() {
            let prices: Vec<u32> = (0..20_000u32).map(|i| i * 7919 % 1000).collect();
            check!("k = 100, prices[i] = (7919·i) % 1000, 20000 days", max_profit(100, &prices), 98_700);
        }

        #[test]
        fn scale_huge_k() {
            let prices: Vec<u32> = (0..200_000u32).map(|i| i * 7919 % 10_000).collect();
            check!("k = 100000, prices[i] = (7919·i) % 10000, 200000 days", max_profit(100_000, &prices), 329_588_780);
        }
        """,
    ],
    wrong=dict(
        no_shortcut_for_big_k="""
            pub fn max_profit(k: usize, prices: &[u32]) -> u64 {
                let mut buy = vec![i64::MIN / 2; k + 1];
                let mut sell = vec![0i64; k + 1];
                for &p in prices {
                    let p = p as i64;
                    for j in 1..=k {
                        buy[j] = buy[j].max(sell[j - 1] - p);
                        sell[j] = sell[j].max(buy[j] + p);
                    }
                }
                sell[k] as u64
            }
        """,
        one_trade_too_many="""
            pub fn max_profit(k: usize, prices: &[u32]) -> u64 {
                let k = k + 1;
                if k >= prices.len() / 2 {
                    return prices.windows(2).map(|w| w[1].saturating_sub(w[0]) as u64).sum();
                }
                let mut buy = vec![i64::MIN / 2; k + 1];
                let mut sell = vec![0i64; k + 1];
                for &p in prices {
                    let p = p as i64;
                    for j in 1..=k {
                        buy[j] = buy[j].max(sell[j - 1] - p);
                        sell[j] = sell[j].max(buy[j] + p);
                    }
                }
                sell[k] as u64
            }
        """,
        buy_and_sell_count_separately="""
            pub fn max_profit(k: usize, prices: &[u32]) -> u64 {
                let k = k / 2;
                if k >= prices.len() / 2 {
                    return prices.windows(2).map(|w| w[1].saturating_sub(w[0]) as u64).sum();
                }
                let mut buy = vec![i64::MIN / 2; k + 1];
                let mut sell = vec![0i64; k + 1];
                for &p in prices {
                    let p = p as i64;
                    for j in 1..=k {
                        buy[j] = buy[j].max(sell[j - 1] - p);
                        sell[j] = sell[j].max(buy[j] + p);
                    }
                }
                sell[k] as u64
            }
        """,
    ),
    hints=[("approach", "Generalise Stock III: buy[j] = max(buy[j], sell[j - 1] - p) and sell[j] = max(sell[j], buy[j] + p) for every j from 1 to k."),
           ("rust", "Two `Vec<i64>` of length k + 1, with `buy` starting very negative. The inner loop over j runs once per day."),
           ("edge case", "Each trade needs two days, so k ≥ n / 2 means \"unlimited\": return the sum of all rises, or an O(n·k) loop with k = 10⁵ is far too slow.")],
    notes=("The states form a chain of 2k steps; each day advances every link at most once. Capping k at n / 2 keeps the work at O(n · min(k, n)).", "O(n · min(k, n))", "O(min(k, n))"),
    follow_up="There is an O(n log n) method for any k using a heap of rise/fall pairs. Can you sketch why merging trades works?",
    related=["D7"],
))

# ---------------------------------------------------------------- Intervals & games (hard)

P.append(dict(
    slug="unique-binary-search-trees", title="Unique binary search trees", level="medium", stage="intervals-games", tags=["Catalan", "1-D DP"],
    companies=["Amazon", "Google", "Meta", "Microsoft", "Apple", "Bloomberg"],
    teaches=["Splitting on the root: the left and right subtrees are independent smaller problems.",
             "A sum of products over every split, the pattern behind the interval DPs in this stage."],
    statement="""
        Return how many structurally different binary search trees hold exactly the keys
        `1..=n`. The empty tree (n = 0) counts as one.
    """,
    examples=[("n = 3", "5")],
    constraints=["0 ≤ n ≤ 36"],
    starter="""
        pub fn num_trees(n: u32) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn num_trees(n: u32) -> u64 {
            let n = n as usize;
            // trees[k] = shapes of a BST with k keys. With root r, the left side has r - 1
            // keys and the right side k - r, and any left shape pairs with any right shape.
            let mut trees = vec![0u64; n + 1];
            trees[0] = 1;
            for k in 1..=n {
                trees[k] = (0..k).map(|left| trees[left] * trees[k - 1 - left]).sum();
            }
            trees[n]
        }
    """,
    visible=[
        T("leetcode_three", "n = 3", "num_trees(3)", "5"),
        T("leetcode_one", "n = 1", "num_trees(1)", "1"),
        T("empty_tree", "n = 0", "num_trees(0)", "1"),
        T("two", "n = 2", "num_trees(2)", "2"),
        T("four", "n = 4", "num_trees(4)", "14"),
    ],
    hidden=[
        T("empty_tree", "n = 0", "num_trees(0)", "1"),
        T("five", "n = 5", "num_trees(5)", "42"),
        T("ten", "n = 10", "num_trees(10)", "16_796"),
        T("leetcode_max", "n = 19", "num_trees(19)", "1_767_263_190"),
        T("past_u32", "n = 20", "num_trees(20)", "6_564_120_420"),
        T("thirty_five", "n = 35", "num_trees(35)", "3_116_285_494_907_301_262"),
        T("largest", "n = 36", "num_trees(36)", "11_959_798_385_860_453_492"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn count(k: usize) -> u64 {
                if k == 0 { 1 } else { (0..k).map(|l| count(l) * count(k - 1 - l)).sum() }
            }
            let mut rng = anneal_prelude::Rng::new(1240);
            for _ in 0..200 {
                let n = rng.below(13);
                check!(format!("n = {n}"), num_trees(n as u32), count(n));
            }
        }

        #[test]
        fn every_n_up_to_36() {
            // Catalan numbers also satisfy C(k + 1) = C(k) · 2(2k + 1) / (k + 2).
            let mut c: u128 = 1;
            for k in 0..=36u32 {
                check!(format!("n = {k}"), num_trees(k) as u128, c);
                c = c * 2 * (2 * k as u128 + 1) / (k as u128 + 2);
            }
        }

        #[test]
        fn scale_36_repeated() {
            // Without the table, splitting on every root is about 3^36 calls.
            check!("n = 36, called 1000 times", (0..1000).map(|_| num_trees(36)).min(), Some(11_959_798_385_860_453_492));
        }
        """,
    ],
    wrong=dict(
        plain_recursion="""
            pub fn num_trees(n: u32) -> u64 {
                if n == 0 { 1 } else { (0..n).map(|l| num_trees(l) * num_trees(n - 1 - l)).sum() }
            }
        """,
        factorial_formula="""
            pub fn num_trees(n: u32) -> u64 {
                let fact = |k: u64| (1..=k).product::<u64>();
                let n = n as u64;
                fact(2 * n) / (fact(n + 1) * fact(n))
            }
        """,
        empty_tree_is_zero="""
            pub fn num_trees(n: u32) -> u64 {
                let n = n as usize;
                let mut trees = vec![0u64; n + 1];
                trees[0] = 1;
                for k in 1..=n {
                    trees[k] = (0..k).map(|left| trees[left] * trees[k - 1 - left]).sum();
                }
                if n == 0 { 0 } else { trees[n] }
            }
        """,
    ),
    hints=[("approach", "Choose the root r. The keys below it form the left subtree (r - 1 keys) and the keys above form the right (n - r keys); multiply their counts and add over every r."),
           ("rust", "Fill a `Vec<u64>` from 0 up with `(0..k).map(|l| trees[l] * trees[k - 1 - l]).sum()`."),
           ("edge case", "trees[0] = 1: an empty side is one shape, not zero, or every tree with a leaf root disappears.")],
    notes=("Only the number of keys on each side matters, not which keys, so the state is one integer. These are the Catalan numbers.", "O(n²)", "O(n)"),
    follow_up="How would you build every such tree (Unique binary search trees II), and how many are there for n = 8?",
    related=["D6", "D13"],
))

P.append(dict(
    slug="predict-the-winner", title="Predict the winner", level="medium", stage="intervals-games", tags=["interval DP", "minimax"],
    companies=["Google", "Amazon", "Microsoft", "Meta"],
    teaches=["Game DP as a score difference: the mover's best lead on `nums[i..=j]` is what they take minus the opponent's best lead after.",
             "Filling `dp[i][j]` by interval length, in one rolling row."],
    statement="""
        Two players take turns removing a number from either end of `nums` and adding it to
        their score. Player 1 moves first, and both play as well as possible. Return whether
        player 1 ends with at least as many points as player 2 (a tie counts as a win).
    """,
    examples=[("nums = [1, 5, 2]", "false"), ("nums = [1, 5, 233, 7]", "true (take 1, then 233)")],
    constraints=["0 ≤ nums.len() ≤ 1000", "0 ≤ nums[i] ≤ 10⁷"],
    starter="""
        pub fn predict_the_winner(nums: &[u32]) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn predict_the_winner(nums: &[u32]) -> bool {
            let n = nums.len();
            // For the current i, lead[j] = the mover's best (own score - other's score) on nums[i..=j].
            // Before updating it still holds nums[i + 1..=j].
            let mut lead = vec![0i64; n];
            for i in (0..n).rev() {
                lead[i] = nums[i] as i64;
                for j in i + 1..n {
                    lead[j] = (nums[i] as i64 - lead[j]).max(nums[j] as i64 - lead[j - 1]);
                }
            }
            lead.last().map_or(true, |&d| d >= 0)
        }
    """,
    visible=[
        T("leetcode_three", "nums = [1, 5, 2]", "predict_the_winner(&[1, 5, 2])", "false"),
        T("leetcode_four", "nums = [1, 5, 233, 7]", "predict_the_winner(&[1, 5, 233, 7])", "true"),
        T("empty", "nums = []", "predict_the_winner(&[])", "true"),
        T("single", "nums = [5]", "predict_the_winner(&[5])", "true"),
        T("tie_counts_as_a_win", "nums = [1, 1]", "predict_the_winner(&[1, 1])", "true"),
    ],
    hidden=[
        T("single_zero", "nums = [0]", "predict_the_winner(&[0])", "true"),
        T("middle_is_big", "nums = [1, 3, 1]", "predict_the_winner(&[1, 3, 1])", "false"),
        T("five", "nums = [2, 4, 55, 6, 8]", "predict_the_winner(&[2, 4, 55, 6, 8])", "false"),
        T("take_the_small_end", "nums = [1, 2, 99]", "predict_the_winner(&[1, 2, 99])", "true"),
        T("four_greedy_loses", "nums = [3, 9, 1, 2]", "predict_the_winner(&[3, 9, 1, 2])", "true"),
        T("seven", "nums = [0, 0, 7, 6, 5, 6, 1]", "predict_the_winner(&[0, 0, 7, 6, 5, 6, 1])", "false"),
        T("twenty", "nums = [10, 17, 11, 16, 17, 9, 14, 17, 18, 13, 11, 4, 17, 18, 15, 3, 13, 9, 11, 7]",
          "predict_the_winner(&[10, 17, 11, 16, 17, 9, 14, 17, 18, 13, 11, 4, 17, 18, 15, 3, 13, 9, 11, 7])", "true"),
        T("big_values", "nums = [10⁷; 999]", "predict_the_winner(&[10_000_000; 999])", "true"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn lead(nums: &[u32]) -> i64 {
                match nums {
                    [] => 0,
                    [x] => *x as i64,
                    [first, .., last] => (*first as i64 - lead(&nums[1..])).max(*last as i64 - lead(&nums[..nums.len() - 1])),
                }
            }
            let mut rng = anneal_prelude::Rng::new(1241);
            for _ in 0..300 {
                let n = rng.below(12);
                let nums: Vec<u32> = rng.vec(n, 0, 20);
                check!(format!("nums = {nums:?}"), predict_the_winner(&nums), lead(&nums) >= 0);
            }
        }

        #[test]
        fn scale_1000() {
            let nums: Vec<u32> = (0..1000u32).map(|i| i * 7919 % 1000).collect();
            check!("nums[i] = (7919·i) % 1000, 1000 numbers", predict_the_winner(&nums), true);
        }

        #[test]
        fn scale_999_loses() {
            let nums: Vec<u32> = (0..999u64).map(|i| (i * 104_729 % 997) as u32).collect();
            check!("nums[i] = (104729·i) % 997, 999 numbers", predict_the_winner(&nums), false);
        }
        """,
    ],
    wrong=dict(
        take_the_bigger_end="""
            pub fn predict_the_winner(nums: &[u32]) -> bool {
                let (mut lo, mut hi) = (0, nums.len());
                let mut scores = [0u64; 2];
                let mut turn = 0;
                while lo < hi {
                    if nums[lo] >= nums[hi - 1] {
                        scores[turn] += nums[lo] as u64;
                        lo += 1;
                    } else {
                        scores[turn] += nums[hi - 1] as u64;
                        hi -= 1;
                    }
                    turn ^= 1;
                }
                scores[0] >= scores[1]
            }
        """,
        tie_is_a_loss="""
            pub fn predict_the_winner(nums: &[u32]) -> bool {
                let n = nums.len();
                let mut lead = vec![0i64; n];
                for i in (0..n).rev() {
                    lead[i] = nums[i] as i64;
                    for j in i + 1..n {
                        lead[j] = (nums[i] as i64 - lead[j]).max(nums[j] as i64 - lead[j - 1]);
                    }
                }
                lead.last().map_or(false, |&d| d > 0)
            }
        """,
        plain_recursion="""
            fn lead(nums: &[u32]) -> i64 {
                match nums {
                    [] => 0,
                    [x] => *x as i64,
                    [first, .., last] => (*first as i64 - lead(&nums[1..])).max(*last as i64 - lead(&nums[..nums.len() - 1])),
                }
            }

            pub fn predict_the_winner(nums: &[u32]) -> bool {
                lead(nums) >= 0
            }
        """,
    ),
    hints=[("approach", "Let lead(i, j) be the best score difference for whoever moves on nums[i..=j]. Taking an end gives that number minus the opponent's best lead on what's left."),
           ("rust", "Fill by increasing length, or with one `Vec<i64>`: loop i downwards and j upwards; `lead[j]` still holds (i + 1, j) and `lead[j - 1]` already holds (i, j - 1)."),
           ("edge case", "Taking the bigger end each turn is not optimal: [1, 5, 233, 7] needs player 1 to take the 1.")],
    notes=("Scoring the game as a difference makes it zero-sum, so one number per interval suffices: my lead = what I take - your lead afterwards. Every interval depends on the two intervals one shorter.", "O(n²)", "O(n)"),
    follow_up="When the length is even, player 1 can always at least tie without any DP. Why? (Take all even or all odd positions.)",
    related=["D11"],
))

P.append(dict(
    slug="stone-game", title="Stone game", level="medium", stage="intervals-games", tags=["interval DP", "minimax"],
    companies=["Google", "Amazon", "Microsoft", "Meta"],
    teaches=["Recovering both players' totals from the total and the difference.",
             "Reusing an interval DP when the question asks for more than yes or no."],
    statement="""
        Alice and Bob take turns taking the whole pile at either end of the row `piles`; Alice
        goes first. Each wants to finish with as many stones as possible and plays perfectly.
        Return `(alice, bob)`: the stones each one ends with.
    """,
    examples=[("piles = [3, 7, 2, 3]", "(10, 5)"), ("piles = [5, 3, 4, 5]", "(9, 8)")],
    constraints=["0 ≤ piles.len() ≤ 1000", "0 ≤ piles[i] ≤ 10⁶"],
    starter="""
        pub fn stone_game(piles: &[u32]) -> (u64, u64) {
            todo!()
        }
    """,
    solution="""
        pub fn stone_game(piles: &[u32]) -> (u64, u64) {
            let n = piles.len();
            // Maximising your own total is maximising (yours - theirs), because the total is fixed.
            // lead[j] for the current i = the mover's best difference on piles[i..=j].
            let mut lead = vec![0i64; n];
            for i in (0..n).rev() {
                lead[i] = piles[i] as i64;
                for j in i + 1..n {
                    lead[j] = (piles[i] as i64 - lead[j]).max(piles[j] as i64 - lead[j - 1]);
                }
            }
            let total: i64 = piles.iter().map(|&p| p as i64).sum();
            let diff = lead.last().copied().unwrap_or(0);
            // alice + bob = total and alice - bob = diff.
            (((total + diff) / 2) as u64, ((total - diff) / 2) as u64)
        }
    """,
    visible=[
        T("four_piles", "piles = [3, 7, 2, 3]", "stone_game(&[3, 7, 2, 3])", "(10, 5)"),
        T("leetcode_four", "piles = [5, 3, 4, 5]", "stone_game(&[5, 3, 4, 5])", "(9, 8)"),
        T("empty", "piles = []", "stone_game(&[])", "(0, 0)"),
        T("one_pile", "piles = [4]", "stone_game(&[4])", "(4, 0)"),
        T("two_piles", "piles = [1, 2]", "stone_game(&[1, 2])", "(2, 1)"),
        T("bob_can_win", "piles = [1, 100, 1]", "stone_game(&[1, 100, 1])", "(2, 100)"),
    ],
    hidden=[
        T("empty", "piles = []", "stone_game(&[])", "(0, 0)"),
        T("three", "piles = [2, 1, 1]", "stone_game(&[2, 1, 1])", "(3, 1)"),
        T("greedy_trap", "piles = [3, 9, 1, 2]", "stone_game(&[3, 9, 1, 2])", "(11, 4)"),
        T("ties", "piles = [5, 5, 5, 5]", "stone_game(&[5, 5, 5, 5])", "(10, 10)"),
        T("close", "piles = [7, 8, 8, 10]", "stone_game(&[7, 8, 8, 10])", "(18, 15)"),
        T("zeros", "piles = [0, 0, 0]", "stone_game(&[0, 0, 0])", "(0, 0)"),
        T("big", "piles = [10⁶; 1000]", "stone_game(&[1_000_000; 1000])", "(500_000_000, 500_000_000)"),
        """
        #[test]
        fn random_vs_brute_force() {
            // Returns (mover's total, other's total).
            fn play(p: &[u32]) -> (u64, u64) {
                match p {
                    [] => (0, 0),
                    [first, .., last] => {
                        let (other_l, me_l) = play(&p[1..]);
                        let (other_r, me_r) = play(&p[..p.len() - 1]);
                        let left = (*first as u64 + me_l, other_l);
                        let right = (*last as u64 + me_r, other_r);
                        if left.0 >= right.0 { left } else { right }
                    }
                    [x] => (*x as u64, 0),
                }
            }
            let mut rng = anneal_prelude::Rng::new(1242);
            for _ in 0..300 {
                let n = rng.below(12);
                let piles: Vec<u32> = rng.vec(n, 0, 20);
                check!(format!("piles = {piles:?}"), stone_game(&piles), play(&piles));
            }
        }

        #[test]
        fn scale_1000() {
            let piles: Vec<u32> = (0..1000u32).map(|i| i * 7919 % 1000).collect();
            check!("piles[i] = (7919·i) % 1000, 1000 piles", stone_game(&piles), (250_000, 249_500));
        }
        """,
    ],
    wrong=dict(
        take_the_bigger_end="""
            pub fn stone_game(piles: &[u32]) -> (u64, u64) {
                let (mut lo, mut hi) = (0, piles.len());
                let mut scores = [0u64; 2];
                let mut turn = 0;
                while lo < hi {
                    if piles[lo] >= piles[hi - 1] {
                        scores[turn] += piles[lo] as u64;
                        lo += 1;
                    } else {
                        scores[turn] += piles[hi - 1] as u64;
                        hi -= 1;
                    }
                    turn ^= 1;
                }
                (scores[0], scores[1])
            }
        """,
        bob_first="""
            pub fn stone_game(piles: &[u32]) -> (u64, u64) {
                let n = piles.len();
                let mut lead = vec![0i64; n];
                for i in (0..n).rev() {
                    lead[i] = piles[i] as i64;
                    for j in i + 1..n {
                        lead[j] = (piles[i] as i64 - lead[j]).max(piles[j] as i64 - lead[j - 1]);
                    }
                }
                let total: i64 = piles.iter().map(|&p| p as i64).sum();
                let diff = lead.last().copied().unwrap_or(0);
                (((total - diff) / 2) as u64, ((total + diff) / 2) as u64)
            }
        """,
        plain_recursion="""
            fn lead(p: &[u32]) -> i64 {
                match p {
                    [] => 0,
                    [x] => *x as i64,
                    [first, .., last] => (*first as i64 - lead(&p[1..])).max(*last as i64 - lead(&p[..p.len() - 1])),
                }
            }

            pub fn stone_game(piles: &[u32]) -> (u64, u64) {
                let total: i64 = piles.iter().map(|&p| p as i64).sum();
                let diff = lead(piles);
                (((total + diff) / 2) as u64, ((total - diff) / 2) as u64)
            }
        """,
    ),
    hints=[("approach", "Since the stones add up to a fixed total, each player maximising their own total is the same as maximising their lead. Compute Alice's best lead as in Predict the winner."),
           ("rust", "Then solve alice + bob = total, alice - bob = lead: `((total + lead) / 2, (total - lead) / 2)` in `i64`, cast at the end."),
           ("edge case", "Bob can come out ahead when the length is odd: [1, 100, 1] gives (2, 100).")],
    notes=("One interval DP gives the lead; the totals follow from two linear equations. In LeetCode's version (even count, odd total) Alice always wins, but the totals still need the DP.", "O(n²)", "O(n)"),
    follow_up="Why can Alice always win when the number of piles is even and the total is odd?",
    related=["D11"],
))

P.append(dict(
    slug="palindrome-partitioning-ii", title="Palindrome partitioning II", level="hard", stage="intervals-games", tags=["1-D DP", "palindromes"],
    companies=["Amazon", "Google", "Microsoft", "Meta", "Bloomberg"],
    teaches=["Combining two DPs: which substrings are palindromes, and the fewest pieces for each prefix.",
             "Expanding around each centre to visit every palindrome once, in O(n²) total."],
    statement="""
        Cut `s` into pieces that are all palindromes. Return the fewest cuts needed (a string
        that is already a palindrome, or is empty, needs none).
    """,
    examples=[("s = \"aab\"", "1 (\"aa\" | \"b\")")],
    constraints=["0 ≤ s.len() ≤ 2000", "s is ASCII lowercase letters"],
    starter="""
        pub fn min_cut(s: &str) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn min_cut(s: &str) -> usize {
            let s = s.as_bytes();
            let n = s.len();
            // pieces[k] = the fewest palindromes that s[..k] splits into.
            let mut pieces: Vec<usize> = (0..=n).collect();
            for center in 0..n {
                // Odd palindromes around s[center], then even ones around s[center], s[center + 1].
                for (mut lo, mut hi) in [(center, center), (center, center + 1)] {
                    while hi < n && s[lo] == s[hi] {
                        // s[lo..=hi] is a palindrome: s[..lo] then this piece.
                        pieces[hi + 1] = pieces[hi + 1].min(pieces[lo] + 1);
                        if lo == 0 {
                            break;
                        }
                        lo -= 1;
                        hi += 1;
                    }
                }
            }
            pieces[n].saturating_sub(1)
        }
    """,
    visible=[
        T("leetcode_aab", "s = \"aab\"", "min_cut(\"aab\")", "1"),
        T("leetcode_a", "s = \"a\"", "min_cut(\"a\")", "0"),
        T("leetcode_ab", "s = \"ab\"", "min_cut(\"ab\")", "1"),
        T("empty", "s = \"\"", "min_cut(\"\")", "0"),
        T("already_a_palindrome", "s = \"aba\"", "min_cut(\"aba\")", "0"),
        T("longest_first_is_a_trap", "s = \"bbab\" (\"b\" | \"bab\")", "min_cut(\"bbab\")", "1"),
    ],
    hidden=[
        T("empty", "s = \"\"", "min_cut(\"\")", "0"),
        T("all_different", "s = \"abcde\"", "min_cut(\"abcde\")", "4"),
        T("all_same", "s = \"aaaa\"", "min_cut(\"aaaa\")", "0"),
        T("two_pieces", "s = \"cdd\"", "min_cut(\"cdd\")", "1"),
        T("even_palindromes", "s = \"abccbc\"", "min_cut(\"abccbc\")", "2"),
        T("greedy_trap", "s = \"ababbbabbababa\"", "min_cut(\"ababbbabbababa\")", "3"),
        T("long_mixed", "s = \"eegiicgaeadbcfacfhifdbiehbgejcaeggcgbahfcajfhjjdgj\"", "min_cut(\"eegiicgaeadbcfacfhifdbiehbgejcaeggcgbahfcajfhjjdgj\")", "42"),
        T("longest_all_same", "s = \"aaa…a\" (2000)", "min_cut(&\"a\".repeat(2000))", "0"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn fewest_pieces(s: &[u8]) -> usize {
                if s.is_empty() {
                    return 0;
                }
                (1..=s.len()).filter(|&k| s[..k].iter().eq(s[..k].iter().rev())).map(|k| 1 + fewest_pieces(&s[k..])).min().unwrap()
            }
            let mut rng = anneal_prelude::Rng::new(1243);
            for _ in 0..300 {
                let n = rng.below(11);
                let s = rng.string(n, "ab");
                check!(format!("s = {s:?}"), min_cut(&s), fewest_pieces(s.as_bytes()).saturating_sub(1));
            }
        }

        #[test]
        fn scale_2000() {
            let s: String = (0..2000u64).map(|i| (b'a' + (i * i / 7 % 3) as u8) as char).collect();
            check!("s[i] = 'a' + (i² / 7) % 3, 2000 characters", min_cut(&s), 3);
        }

        #[test]
        fn scale_all_a_then_b() {
            // Every substring of the a's is a palindrome: checking each one from scratch is O(n³).
            let s = format!("{}b", "a".repeat(1999));
            check!("s = 1999 a's then b", min_cut(&s), 1);
        }
        """,
    ],
    wrong=dict(
        longest_palindrome_prefix="""
            pub fn min_cut(s: &str) -> usize {
                let s = s.as_bytes();
                let (mut start, mut pieces) = (0, 0usize);
                while start < s.len() {
                    let end = (start + 1..=s.len()).rev().find(|&e| s[start..e].iter().eq(s[start..e].iter().rev())).unwrap();
                    start = end;
                    pieces += 1;
                }
                pieces.saturating_sub(1)
            }
        """,
        checks_every_substring="""
            pub fn min_cut(s: &str) -> usize {
                let s = s.as_bytes();
                let n = s.len();
                let mut pieces: Vec<usize> = (0..=n).collect();
                for end in 1..=n {
                    for start in 0..end {
                        if s[start..end].iter().eq(s[start..end].iter().rev()) {
                            pieces[end] = pieces[end].min(pieces[start] + 1);
                        }
                    }
                }
                pieces[n].saturating_sub(1)
            }
        """,
        plain_recursion="""
            fn fewest_pieces(s: &[u8]) -> usize {
                if s.is_empty() {
                    return 0;
                }
                (1..=s.len()).filter(|&k| s[..k].iter().eq(s[..k].iter().rev())).map(|k| 1 + fewest_pieces(&s[k..])).min().unwrap()
            }

            pub fn min_cut(s: &str) -> usize {
                fewest_pieces(s.as_bytes()).saturating_sub(1)
            }
        """,
    ),
    hints=[("approach", "pieces(k) = the fewest palindromes for s[..k] = 1 + min over palindromes s[j..k] of pieces(j). The answer is pieces(n) - 1."),
           ("rust", "Instead of testing every (j, k), expand around each centre (odd and even); every palindrome s[lo..=hi] you reach updates `pieces[hi + 1]` from `pieces[lo]`."),
           ("edge case", "Cutting off the longest palindrome first is greedy and can cost more: \"bbab\" → \"bb\" | \"a\" | \"b\" (2 cuts) instead of \"b\" | \"bab\" (1).")],
    notes=("Centre expansion visits each palindrome once in O(1) and stops at the first mismatch, so the whole thing is O(n²) with O(n) memory. Palindromes ending at lo - 1 have centres before the current one, so pieces[lo] is final when it's read.", "O(n²)", "O(n)"),
    follow_up="How would you list one optimal partition? And all partitions (Palindrome partitioning I, a backtracking problem)?",
    related=["D11", "D10"],
))

P.append(dict(
    slug="minimum-cost-to-cut-a-stick", title="Minimum cost to cut a stick", level="hard", stage="intervals-games", tags=["interval DP", "dp[i][j] by length"],
    companies=["Google", "Amazon", "Microsoft", "Meta"],
    teaches=["Interval DP over the cut points: pick which cut happens first inside an interval.",
             "Sorting the points and adding both ends of the stick as sentinels."],
    statement="""
        A stick runs from 0 to `n`. `cuts` lists the positions where it must be cut, in no
        particular order. Cutting a piece costs its current length, and you may do the cuts in any
        order. Return the cheapest total.
    """,
    examples=[("n = 7, cuts = [1, 3, 4, 5]", "16 (cut at 3, then 5, then 1, then 4: 7 + 4 + 3 + 2)")],
    constraints=["2 ≤ n ≤ 10⁶", "0 ≤ cuts.len() ≤ 200", "cuts are distinct and 0 < cuts[i] < n"],
    starter="""
        pub fn min_cost(n: u32, cuts: &[u32]) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn min_cost(n: u32, cuts: &[u32]) -> u64 {
            let mut pts: Vec<u64> = Vec::with_capacity(cuts.len() + 2);
            pts.push(0);
            pts.extend(cuts.iter().map(|&c| c as u64));
            pts.push(n as u64);
            pts.sort_unstable();
            let m = pts.len();
            // cost[i][j] = the cheapest way to make every cut strictly between pts[i] and pts[j].
            let mut cost = vec![vec![0u64; m]; m];
            for len in 2..m {
                for i in 0..m - len {
                    let j = i + len;
                    // Whichever cut k goes first costs the whole piece, then splits it in two.
                    let best = (i + 1..j).map(|k| cost[i][k] + cost[k][j]).min().unwrap();
                    cost[i][j] = pts[j] - pts[i] + best;
                }
            }
            cost[0][m - 1]
        }
    """,
    visible=[
        T("leetcode_seven", "n = 7, cuts = [1, 3, 4, 5]", "min_cost(7, &[1, 3, 4, 5])", "16"),
        T("leetcode_nine", "n = 9, cuts = [5, 6, 1, 4, 2]", "min_cost(9, &[5, 6, 1, 4, 2])", "22"),
        T("no_cuts", "n = 5, cuts = []", "min_cost(5, &[])", "0"),
        T("one_cut", "n = 2, cuts = [1]", "min_cost(2, &[1])", "2"),
        T("order_matters", "n = 10, cuts = [2, 5] (cutting 5 first is cheaper)", "min_cost(10, &[2, 5])", "15"),
    ],
    hidden=[
        T("no_cuts", "n = 5, cuts = []", "min_cost(5, &[])", "0"),
        T("middle", "n = 100, cuts = [50]", "min_cost(100, &[50])", "100"),
        T("reversed_input", "n = 10, cuts = [5, 2]", "min_cost(10, &[5, 2])", "15"),
        T("near_the_ends", "n = 1000000, cuts = [1, 999999]", "min_cost(1_000_000, &[1, 999_999])", "1_999_999"),
        T("every_point", "n = 5, cuts = [1, 2, 3, 4]", "min_cost(5, &[1, 2, 3, 4])", "12"),
        T("nineteen_cuts", "n = 30, cuts = [13, 25, 16, 20, 26, 5, 27, 8, 23, 14, 6, 15, 21, 24, 29, 1, 19, 9, 3]",
          "min_cost(30, &[13, 25, 16, 20, 26, 5, 27, 8, 23, 14, 6, 15, 21, 24, 29, 1, 19, 9, 3])", "127"),
        T("unsorted_six", "n = 20, cuts = [17, 3, 11, 8, 14, 5]", "min_cost(20, &[17, 3, 11, 8, 14, 5])", "57"),
        """
        #[test]
        fn random_vs_brute_force() {
            // Try every cut first on the piece [lo, hi], then recurse on both halves.
            fn cheapest(lo: u32, hi: u32, cuts: &[u32]) -> u64 {
                let inside: Vec<u32> = cuts.iter().copied().filter(|&c| lo < c && c < hi).collect();
                inside.iter().map(|&c| (hi - lo) as u64 + cheapest(lo, c, &inside) + cheapest(c, hi, &inside)).min().unwrap_or(0)
            }
            let mut rng = anneal_prelude::Rng::new(1244);
            for _ in 0..300 {
                let n = rng.int(2, 15) as u32;
                let mut cuts: Vec<u32> = (1..n).filter(|_| rng.below(3) == 0).collect();
                cuts.truncate(6);
                rng.shuffle(&mut cuts);
                check!(format!("n = {n}, cuts = {cuts:?}"), min_cost(n, &cuts), cheapest(0, n, &cuts));
            }
        }

        #[test]
        fn scale_200_cuts() {
            let cuts: Vec<u32> = (0..200u32).map(|i| i * 7919 % 999_999 + 1).collect();
            check!("n = 1000000, cuts[i] = (7919·i) % 999999 + 1, 200 cuts", min_cost(1_000_000, &cuts), 7_575_883);
        }
        """,
    ],
    wrong=dict(
        cuts_in_given_order="""
            pub fn min_cost(n: u32, cuts: &[u32]) -> u64 {
                let mut pieces: Vec<(u32, u32)> = vec![(0, n)];
                let mut total = 0u64;
                for &c in cuts {
                    let k = pieces.iter().position(|&(a, b)| a < c && c < b).unwrap();
                    let (a, b) = pieces.swap_remove(k);
                    total += (b - a) as u64;
                    pieces.push((a, c));
                    pieces.push((c, b));
                }
                total
            }
        """,
        middle_cut_first="""
            fn split(lo: u32, hi: u32, cuts: &[u32]) -> u64 {
                let inside: Vec<u32> = cuts.iter().copied().filter(|&c| lo < c && c < hi).collect();
                let mid = (lo + hi) / 2;
                match inside.iter().copied().min_by_key(|&c| c.abs_diff(mid)) {
                    None => 0,
                    Some(c) => (hi - lo) as u64 + split(lo, c, &inside) + split(c, hi, &inside),
                }
            }

            pub fn min_cost(n: u32, cuts: &[u32]) -> u64 {
                split(0, n, cuts)
            }
        """,
        plain_recursion="""
            fn cheapest(pts: &[u64]) -> u64 {
                if pts.len() <= 2 {
                    return 0;
                }
                let len = pts[pts.len() - 1] - pts[0];
                (1..pts.len() - 1).map(|k| len + cheapest(&pts[..=k]) + cheapest(&pts[k..])).min().unwrap()
            }

            pub fn min_cost(n: u32, cuts: &[u32]) -> u64 {
                let mut pts: Vec<u64> = cuts.iter().map(|&c| c as u64).collect();
                pts.push(0);
                pts.push(n as u64);
                pts.sort_unstable();
                cheapest(&pts)
            }
        """,
    ),
    hints=[("approach", "Sort the cuts and add 0 and n. For the piece between points i and j, the first cut k costs pts[j] - pts[i] and leaves the pieces (i, k) and (k, j)."),
           ("rust", "`cost[i][j]` in a `Vec<Vec<u64>>`, filled by increasing `len = j - i` so both halves are ready; `(i + 1..j).map(..).min().unwrap()` picks the best first cut."),
           ("edge case", "The input order is not the cutting order, and it isn't sorted. Cutting nearest the middle first isn't always optimal either.")],
    notes=("Once a cut is made, the two sides never interact, so each piece between two chosen points is an independent subproblem. There are O(c²) pieces and each tries O(c) first cuts.", "O(c³) for c cuts", "O(c²)"),
    follow_up="This is the same shape as optimal BST and matrix-chain multiplication. Can you name the choice and the cost in each?",
    related=["D8"],
))

P.append(dict(
    slug="burst-balloons", title="Burst balloons", level="hard", stage="intervals-games", tags=["interval DP", "dp[i][j] by length"],
    companies=["Google", "Amazon", "Meta", "Microsoft", "Apple"],
    teaches=["Choosing the LAST action in an interval so its neighbours are fixed: the key trick of interval DP.",
             "Padding with sentinel 1s so edge balloons need no special case."],
    statement="""
        Balloon `i` shows the number `nums[i]`. Bursting it earns `left × nums[i] × right`, where
        `left` and `right` are the numbers on the balloons currently next to it (1 if there is none
        on that side). Burst them all, in any order. Return the most coins you can earn.
    """,
    examples=[("nums = [3, 1, 5, 8]", "167 (burst 1, 5, 3, 8: 15 + 120 + 24 + 8)")],
    constraints=["0 ≤ nums.len() ≤ 300", "0 ≤ nums[i] ≤ 100"],
    starter="""
        pub fn max_coins(nums: &[u32]) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn max_coins(nums: &[u32]) -> u64 {
            // Sentinel 1s at both ends: a balloon at the edge multiplies by 1.
            let mut a: Vec<u64> = Vec::with_capacity(nums.len() + 2);
            a.push(1);
            a.extend(nums.iter().map(|&x| x as u64));
            a.push(1);
            let m = a.len();
            // best[i][j] = the most coins from bursting every balloon strictly between i and j.
            // If k is the LAST one burst there, its neighbours at that moment are i and j.
            let mut best = vec![vec![0u64; m]; m];
            for len in 2..m {
                for i in 0..m - len {
                    let j = i + len;
                    best[i][j] = (i + 1..j).map(|k| best[i][k] + best[k][j] + a[i] * a[k] * a[j]).max().unwrap();
                }
            }
            best[0][m - 1]
        }
    """,
    visible=[
        T("leetcode_four", "nums = [3, 1, 5, 8]", "max_coins(&[3, 1, 5, 8])", "167"),
        T("leetcode_two", "nums = [1, 5]", "max_coins(&[1, 5])", "10"),
        T("empty", "nums = []", "max_coins(&[])", "0"),
        T("one", "nums = [7]", "max_coins(&[7])", "7"),
        T("three", "nums = [2, 3, 4]", "max_coins(&[2, 3, 4])", "36"),
    ],
    hidden=[
        T("empty", "nums = []", "max_coins(&[])", "0"),
        T("zero_and_one", "nums = [0, 1]", "max_coins(&[0, 1])", "1"),
        T("four_big", "nums = [9, 76, 64, 21]", "max_coins(&[9, 76, 64, 21])", "116_718"),
        T("max_values", "nums = [100, 100, 100]", "max_coins(&[100, 100, 100])", "1_010_100"),
        T("with_zeros", "nums = [8, 2, 6, 8, 9, 8, 1, 4, 1, 5, 3, 0, 7, 7, 0, 4, 2, 2, 5]",
          "max_coins(&[8, 2, 6, 8, 9, 8, 1, 4, 1, 5, 3, 0, 7, 7, 0, 4, 2, 2, 5])", "3630"),
        T("single_zero", "nums = [0]", "max_coins(&[0])", "0"),
        T("all_zero", "nums = [0, 0, 0]", "max_coins(&[0, 0, 0])", "0"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn best(v: &mut Vec<u64>) -> u64 {
                let mut top = 0;
                for k in 0..v.len() {
                    let left = if k > 0 { v[k - 1] } else { 1 };
                    let right = if k + 1 < v.len() { v[k + 1] } else { 1 };
                    let x = v.remove(k);
                    top = top.max(left * x * right + best(v));
                    v.insert(k, x);
                }
                top
            }
            let mut rng = anneal_prelude::Rng::new(1245);
            for _ in 0..200 {
                let n = rng.below(7);
                let nums: Vec<u32> = rng.vec(n, 0, 9);
                let mut v: Vec<u64> = nums.iter().map(|&x| x as u64).collect();
                check!(format!("nums = {nums:?}"), max_coins(&nums), best(&mut v));
            }
        }

        #[test]
        fn scale_300() {
            let nums: Vec<u32> = (0..300u32).map(|i| i * 7919 % 100 + 1).collect();
            check!("nums[i] = (7919·i) % 100 + 1, 300 balloons", max_coins(&nums), 112_945_464);
        }
        """,
    ],
    wrong=dict(
        smallest_first="""
            pub fn max_coins(nums: &[u32]) -> u64 {
                let mut v: Vec<u64> = nums.iter().map(|&x| x as u64).collect();
                let mut total = 0;
                while !v.is_empty() {
                    let k = (0..v.len()).min_by_key(|&i| v[i]).unwrap();
                    let left = if k > 0 { v[k - 1] } else { 1 };
                    let right = if k + 1 < v.len() { v[k + 1] } else { 1 };
                    total += left * v[k] * right;
                    v.remove(k);
                }
                total
            }
        """,
        k_bursts_first="""
            pub fn max_coins(nums: &[u32]) -> u64 {
                let mut a: Vec<u64> = vec![1];
                a.extend(nums.iter().map(|&x| x as u64));
                a.push(1);
                let m = a.len();
                let mut best = vec![vec![0u64; m]; m];
                for len in 2..m {
                    for i in 0..m - len {
                        let j = i + len;
                        best[i][j] = (i + 1..j).map(|k| best[i][k] + best[k][j] + a[k - 1] * a[k] * a[k + 1]).max().unwrap();
                    }
                }
                best[0][m - 1]
            }
        """,
        plain_recursion="""
            fn best(v: &mut Vec<u64>) -> u64 {
                let mut top = 0;
                for k in 0..v.len() {
                    let left = if k > 0 { v[k - 1] } else { 1 };
                    let right = if k + 1 < v.len() { v[k + 1] } else { 1 };
                    let x = v.remove(k);
                    top = top.max(left * x * right + best(v));
                    v.insert(k, x);
                }
                top
            }

            pub fn max_coins(nums: &[u32]) -> u64 {
                let mut v: Vec<u64> = nums.iter().map(|&x| x as u64).collect();
                best(&mut v)
            }
        """,
    ),
    hints=[("approach", "Think about the last balloon k burst between two fixed balloons i and j: when it goes, its neighbours are exactly i and j, and the two sides were solved independently before."),
           ("rust", "Pad the numbers with a 1 at each end, then fill `best[i][j]` by increasing j - i: max over k of best[i][k] + best[k][j] + a[i]·a[k]·a[j]."),
           ("edge case", "Choosing the FIRST balloon to burst doesn't split the problem, because its neighbours' neighbours change afterwards. Bursting the smallest first is not optimal either.")],
    notes=("Fixing the last balloon in an interval freezes its neighbours at the interval's ends, which makes the left and right parts independent. There are O(n²) intervals and each tries O(n) last balloons.", "O(n³)", "O(n²)"),
    follow_up="Why does \"first to burst\" fail to give independent subproblems, while \"last to burst\" works?",
    related=["D11"],
))

# ---------------------------------------------------------------- Bitmasks & digits (hard)


P.append(dict(
    slug="count-numbers-with-unique-digits", title="Count numbers with unique digits", level="medium", stage="bitmasks-digits",
    tags=["counting", "digits"],
    companies=["Google", "Amazon", "Microsoft"],
    teaches=["Counting by position: how many choices the first digit has, then the second, and so on.",
             "Noticing when a count stops growing (no number has 11 distinct digits)."],
    statement="""
        Return how many integers `x` with `0 ≤ x < 10ⁿ` have no repeated digit. For example 102
        counts but 110 doesn't.
    """,
    examples=[("n = 2", "91 (every number below 100 except 11, 22, …, 99)"), ("n = 0", "1 (just 0)")],
    constraints=["0 ≤ n ≤ 20"],
    starter="""
        pub fn count_numbers_with_unique_digits(n: u32) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn count_numbers_with_unique_digits(n: u32) -> u64 {
            // 0 on its own, then the numbers of each length k = 1..=n. A k-digit number has 9 choices
            // for its first digit (1-9) and 9, 8, 7, ... for the rest, since each must be new.
            let mut total = 1;
            let mut of_length = 9u64;
            // Past 10 digits some digit must repeat, so longer lengths add nothing.
            for k in 1..=n.min(10) as u64 {
                if k > 1 {
                    of_length *= 11 - k;
                }
                total += of_length;
            }
            total
        }
    """,
    visible=[
        T("leetcode_two", "n = 2", "count_numbers_with_unique_digits(2)", "91"),
        T("leetcode_zero", "n = 0", "count_numbers_with_unique_digits(0)", "1"),
        T("one_digit", "n = 1", "count_numbers_with_unique_digits(1)", "10"),
        T("three_digits", "n = 3", "count_numbers_with_unique_digits(3)", "739"),
        T("stops_growing_after_ten", "n = 11", "count_numbers_with_unique_digits(11)", "8_877_691"),
    ],
    hidden=[
        T("zero", "n = 0", "count_numbers_with_unique_digits(0)", "1"),
        T("four", "n = 4", "count_numbers_with_unique_digits(4)", "5275"),
        T("eight", "n = 8", "count_numbers_with_unique_digits(8)", "2_345_851"),
        T("nine", "n = 9", "count_numbers_with_unique_digits(9)", "5_611_771"),
        T("ten", "n = 10", "count_numbers_with_unique_digits(10)", "8_877_691"),
        T("twelve", "n = 12", "count_numbers_with_unique_digits(12)", "8_877_691"),
        T("largest", "n = 20", "count_numbers_with_unique_digits(20)", "8_877_691"),
        """
        #[test]
        fn every_n_up_to_6_vs_brute_force() {
            let unique = |mut x: u32| {
                let mut seen = [false; 10];
                loop {
                    let d = (x % 10) as usize;
                    if seen[d] {
                        return false;
                    }
                    seen[d] = true;
                    x /= 10;
                    if x == 0 {
                        return true;
                    }
                }
            };
            // want[k] = how many x < 10^k have unique digits, counted one number at a time.
            let mut want: Vec<u64> = Vec::new();
            let mut count = 0u64;
            let mut next_power = 1u32;
            for x in 0..=1_000_000u32 {
                if x == next_power {
                    want.push(count);
                    next_power *= 10;
                }
                count += unique(x) as u64;
            }
            for (n, &w) in want.iter().enumerate() {
                check!(format!("n = {n}"), count_numbers_with_unique_digits(n as u32), w);
            }
        }

        #[test]
        fn every_n_up_to_20() {
            let mut want = 1u64;
            let mut of_length = 9u64;
            for n in 0..=20u32 {
                if n >= 1 {
                    want += of_length;
                    of_length *= 10u64.saturating_sub(n as u64);
                }
                check!(format!("n = {n}"), count_numbers_with_unique_digits(n), want);
            }
        }
        """,
    ],
    wrong=dict(
        count_one_by_one="""
            pub fn count_numbers_with_unique_digits(n: u32) -> u64 {
                let unique = |mut x: u64| {
                    let mut seen = [false; 10];
                    loop {
                        let d = (x % 10) as usize;
                        if seen[d] {
                            return false;
                        }
                        seen[d] = true;
                        x /= 10;
                        if x == 0 {
                            return true;
                        }
                    }
                };
                (0..10u64.pow(n.min(10))).filter(|&x| unique(x)).count() as u64
            }
        """,
        leading_zero_allowed="""
            pub fn count_numbers_with_unique_digits(n: u32) -> u64 {
                let mut total = 1;
                let mut of_length = 1u64;
                for k in 1..=n.min(10) as u64 {
                    of_length *= 11 - k;
                    total += of_length;
                }
                total
            }
        """,
        zero_not_counted="""
            pub fn count_numbers_with_unique_digits(n: u32) -> u64 {
                let mut total = 0;
                let mut of_length = 9u64;
                for k in 1..=n.min(10) as u64 {
                    if k > 1 {
                        of_length *= 11 - k;
                    }
                    total += of_length;
                }
                total.max(1)
            }
        """,
    ),
    hints=[("approach", "Count by length. One-digit numbers: 10 (including 0). A k-digit number: 9 choices for the first digit (not 0), then 9, then 8, … for the others."),
           ("rust", "Keep a running product in a `u64` and add it for each length from 1 to n."),
           ("edge case", "An 11-digit number must repeat a digit (there are only 10), so the answer stops growing at n = 10. n = 0 means just the number 0.")],
    notes=("This is the counting rule of digit DP without the upper bound: each position multiplies the choices left. The next problem adds the bound, which is where digit DP proper starts.", "O(min(n, 10))", "O(1)"),
    follow_up="How would you count the numbers with unique digits in [1, N] for an arbitrary N (Count special integers)?",
    related=["D13"],
))

P.append(dict(
    slug="numbers-at-most-n-given-digit-set", title="Numbers at most N given digit set", level="hard", stage="bitmasks-digits",
    tags=["digit DP", "counting"],
    companies=["Amazon", "Google"],
    teaches=["Digit DP: count everything shorter than N, then walk N's digits and count what first drops below it at each position.",
             "`to_string().bytes()` to get an integer's digits, `u64::pow` for the free positions."],
    statement="""
        `digits` holds distinct digits from 1 to 9, sorted. You can write positive integers using
        only those digits, each as often as you like. Return how many such integers are at most `n`.
    """,
    examples=[("digits = [1, 3, 5, 7], n = 100", "20 (1, 3, 5, 7, 11, 13, …, 77)"), ("digits = [7], n = 8", "1")],
    constraints=["0 ≤ digits.len() ≤ 9", "digits are distinct, sorted, and each in 1..=9", "1 ≤ n ≤ u64::MAX"],
    starter="""
        pub fn at_most_n_given_digit_set(digits: &[u8], n: u64) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn at_most_n_given_digit_set(digits: &[u8], n: u64) -> u64 {
            let s: Vec<u8> = n.to_string().bytes().map(|b| b - b'0').collect();
            let d = digits.len() as u64;
            let len = s.len();
            // Every number shorter than n: d choices in each of its k positions.
            let mut total: u64 = (1..len as u32).map(|k| d.pow(k)).sum();
            // Same length as n: match n's prefix, then put a smaller digit at position i;
            // the positions after it are free.
            for (i, &c) in s.iter().enumerate() {
                let smaller = digits.iter().filter(|&&x| x < c).count() as u64;
                total += smaller * d.pow((len - i - 1) as u32);
                if !digits.contains(&c) {
                    // The prefix can't continue matching n.
                    return total;
                }
            }
            // Every digit of n is available, so n itself counts too.
            total + 1
        }
    """,
    visible=[
        T("leetcode_hundred", "digits = [1, 3, 5, 7], n = 100", "at_most_n_given_digit_set(&[1, 3, 5, 7], 100)", "20"),
        T("leetcode_billion", "digits = [1, 4, 9], n = 1000000000", "at_most_n_given_digit_set(&[1, 4, 9], 1_000_000_000)", "29523"),
        T("leetcode_seven", "digits = [7], n = 8", "at_most_n_given_digit_set(&[7], 8)", "1"),
        T("n_itself_counts", "digits = [1], n = 11", "at_most_n_given_digit_set(&[1], 11)", "2"),
        T("no_digits", "digits = [], n = 100", "at_most_n_given_digit_set(&[], 100)", "0"),
    ],
    hidden=[
        T("no_digits_big_n", "digits = [], n = 10^18", "at_most_n_given_digit_set(&[], 1_000_000_000_000_000_000)", "0"),
        T("n_equals_the_digit", "digits = [5], n = 5", "at_most_n_given_digit_set(&[5], 5)", "1"),
        T("n_below_every_digit", "digits = [5], n = 4", "at_most_n_given_digit_set(&[5], 4)", "0"),
        T("one_digit_n", "digits = [3, 4, 8], n = 4", "at_most_n_given_digit_set(&[3, 4, 8], 4)", "2"),
        T("ones_up_to_10_18", "digits = [1], n = 10^18", "at_most_n_given_digit_set(&[1], 1_000_000_000_000_000_000)", "18"),
        T("prefix_matches_then_misses", "digits = [1, 7, 9], n = 555555555555555555",
          "at_most_n_given_digit_set(&[1, 7, 9], 555_555_555_555_555_555)", "322_850_406"),
        T("all_nines", "digits = [2, 9], n = 999999999999999999", "at_most_n_given_digit_set(&[2, 9], 999_999_999_999_999_999)", "524_286"),
        T("n_made_of_digits", "digits = [6], n = 6666666666", "at_most_n_given_digit_set(&[6], 6_666_666_666)", "10"),
        T("alternating", "digits = [1, 2], n = 12121212121212121", "at_most_n_given_digit_set(&[1, 2], 12_121_212_121_212_121)", "174_761"),
        T("every_digit_10_18", "digits = [1..=9], n = 10^18", "at_most_n_given_digit_set(&[1, 2, 3, 4, 5, 6, 7, 8, 9], 1_000_000_000_000_000_000)",
          "168_856_464_709_124_010"),
        T("every_digit_u64_max", "digits = [1..=9], n = u64::MAX", "at_most_n_given_digit_set(&[1, 2, 3, 4, 5, 6, 7, 8, 9], u64::MAX)", "2_627_136_424_427_962_617"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(1247);
            for _ in 0..300 {
                let digits: Vec<u8> = (1..=9u8).filter(|_| rng.below(3) == 0).collect();
                let n = rng.int(1, 3000) as u64;
                let want = (1..=n).filter(|&x| x.to_string().bytes().all(|b| digits.contains(&(b - b'0')))).count() as u64;
                check!(format!("digits = {digits:?}, n = {n}"), at_most_n_given_digit_set(&digits, n), want);
            }
        }
        """,
    ],
    wrong=dict(
        build_every_number="""
            pub fn at_most_n_given_digit_set(digits: &[u8], n: u64) -> u64 {
                // Grow numbers one digit at a time, keeping the ones still at most n.
                let mut count = 0;
                let mut layer: Vec<u64> = vec![0];
                while !layer.is_empty() {
                    let mut next = Vec::new();
                    for &x in &layer {
                        for &d in digits {
                            if let Some(y) = x.checked_mul(10).and_then(|y| y.checked_add(d as u64)) {
                                if y <= n {
                                    count += 1;
                                    next.push(y);
                                }
                            }
                        }
                    }
                    layer = next;
                }
                count
            }
        """,
        forgets_n_itself="""
            pub fn at_most_n_given_digit_set(digits: &[u8], n: u64) -> u64 {
                let s: Vec<u8> = n.to_string().bytes().map(|b| b - b'0').collect();
                let d = digits.len() as u64;
                let len = s.len();
                let mut total: u64 = (1..len as u32).map(|k| d.pow(k)).sum();
                for (i, &c) in s.iter().enumerate() {
                    let smaller = digits.iter().filter(|&&x| x < c).count() as u64;
                    total += smaller * d.pow((len - i - 1) as u32);
                    if !digits.contains(&c) {
                        return total;
                    }
                }
                total
            }
        """,
        keeps_going_after_a_miss="""
            pub fn at_most_n_given_digit_set(digits: &[u8], n: u64) -> u64 {
                let s: Vec<u8> = n.to_string().bytes().map(|b| b - b'0').collect();
                let d = digits.len() as u64;
                let len = s.len();
                let mut total: u64 = (1..len as u32).map(|k| d.pow(k)).sum();
                for (i, &c) in s.iter().enumerate() {
                    let smaller = digits.iter().filter(|&&x| x < c).count() as u64;
                    total += smaller * d.pow((len - i - 1) as u32);
                }
                if s.iter().all(|c| digits.contains(c)) { total + 1 } else { total }
            }
        """,
    ),
    hints=[("approach", "Numbers with fewer digits than n are all fine: d¹ + d² + … + d^(len - 1). For numbers as long as n, go through n's digits left to right: at position i, any smaller digit from the set makes the rest free (d^(remaining) ways)."),
           ("rust", "`n.to_string().bytes().map(|b| b - b'0')` gives the digits; `d.pow(k)` counts the free positions."),
           ("edge case", "Stop as soon as n's digit isn't in the set, since no number can keep matching n past it. If you get through every digit, n itself counts: add 1.")],
    notes=("Every number below n of the same length agrees with n up to some position, then has a smaller digit there. Grouping by that position gives one term per digit of n, so the work is proportional to the number of digits.", "O(log n · |digits|)", "O(log n)"),
    follow_up="How would the count change if 0 were allowed in `digits` (numbers can't start with 0)?",
    related=["D13"],
))

P.append(dict(
    slug="can-i-win", title="Can I win", level="hard", stage="bitmasks-digits", tags=["bitmask memo", "minimax"],
    companies=["Google", "LinkedIn", "Amazon"],
    teaches=["A set of used numbers as a `u32`-style bitmask indexing a `Vec` memo.",
             "Game DP: a position is winning if some move leads to a losing position for the opponent."],
    statement="""
        Two players take turns picking a number from 1 to `max_choosable`; a number can't be picked
        twice. Each pick is added to a running total, and whoever makes the total reach at least
        `desired_total` wins. Both play perfectly. Return whether the first player can force a win.
        If the numbers add up to less than `desired_total`, nobody can win: return `false`. A
        `desired_total` of 0 is already reached: return `true`.
    """,
    examples=[("max_choosable = 10, desired_total = 11", "false (whatever player 1 picks, player 2 reaches 11)"),
              ("max_choosable = 10, desired_total = 1", "true")],
    constraints=["1 ≤ max_choosable ≤ 20", "0 ≤ desired_total ≤ 300"],
    starter="""
        pub fn can_i_win(max_choosable: u32, desired_total: u32) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn can_i_win(max_choosable: u32, desired_total: u32) -> bool {
            let m = max_choosable as usize;
            if desired_total == 0 {
                return true;
            }
            if m * (m + 1) / 2 < desired_total as usize {
                return false;
            }
            // The set of used numbers fixes the running total too, so it is the whole state.
            // memo[used]: 0 = not solved yet, 1 = the player to move wins, 2 = they lose.
            fn wins(used: usize, left: u32, m: usize, memo: &mut [u8]) -> bool {
                if memo[used] != 0 {
                    return memo[used] == 1;
                }
                let win = (0..m).any(|i| {
                    let pick = i as u32 + 1;
                    used & (1 << i) == 0 && (pick >= left || !wins(used | 1 << i, left - pick, m, memo))
                });
                memo[used] = if win { 1 } else { 2 };
                win
            }
            let mut memo = vec![0u8; 1 << m];
            wins(0, desired_total, m, &mut memo)
        }
    """,
    visible=[
        T("leetcode_eleven", "max_choosable = 10, desired_total = 11", "can_i_win(10, 11)", "false"),
        T("leetcode_zero", "max_choosable = 10, desired_total = 0", "can_i_win(10, 0)", "true"),
        T("leetcode_one", "max_choosable = 10, desired_total = 1", "can_i_win(10, 1)", "true"),
        T("nobody_reaches_it", "max_choosable = 5, desired_total = 50", "can_i_win(5, 50)", "false"),
        T("must_think_ahead", "max_choosable = 4, desired_total = 6", "can_i_win(4, 6)", "true"),
    ],
    hidden=[
        T("zero", "max_choosable = 1, desired_total = 0", "can_i_win(1, 0)", "true"),
        T("one_number_enough", "max_choosable = 1, desired_total = 1", "can_i_win(1, 1)", "true"),
        T("one_number_short", "max_choosable = 1, desired_total = 2", "can_i_win(1, 2)", "false"),
        T("three_to_five", "max_choosable = 3, desired_total = 5", "can_i_win(3, 5)", "true"),
        T("exact_sum_even_count", "max_choosable = 20, desired_total = 210", "can_i_win(20, 210)", "false"),
        T("exact_sum_odd_count", "max_choosable = 19, desired_total = 190", "can_i_win(19, 190)", "true"),
        T("too_big", "max_choosable = 20, desired_total = 300", "can_i_win(20, 300)", "false"),
        T("ten_forty", "max_choosable = 10, desired_total = 40", "can_i_win(10, 40)", "false"),
        T("twelve_forty_nine", "max_choosable = 12, desired_total = 49", "can_i_win(12, 49)", "true"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn wins(used: &mut Vec<bool>, left: i32) -> bool {
                for i in 0..used.len() {
                    if !used[i] {
                        if i as i32 + 1 >= left {
                            return true;
                        }
                        used[i] = true;
                        let other = wins(used, left - i as i32 - 1);
                        used[i] = false;
                        if !other {
                            return true;
                        }
                    }
                }
                false
            }
            let mut rng = anneal_prelude::Rng::new(1248);
            for _ in 0..300 {
                let m = rng.int(1, 8) as u32;
                let d = rng.int(0, 40) as u32;
                let want = d == 0 || (m * (m + 1) / 2 >= d && wins(&mut vec![false; m as usize], d as i32));
                check!(format!("max_choosable = {m}, desired_total = {d}"), can_i_win(m, d), want);
            }
        }

        #[test]
        fn scale_twenty() {
            check!("max_choosable = 20, desired_total = 152", can_i_win(20, 152), false);
            check!("max_choosable = 20, desired_total = 200", can_i_win(20, 200), false);
            check!("max_choosable = 20, desired_total = 160", can_i_win(20, 160), true);
            check!("max_choosable = 18, desired_total = 79", can_i_win(18, 79), true);
        }
        """,
    ],
    wrong=dict(
        no_memo="""
            fn wins(used: &mut Vec<bool>, left: u32) -> bool {
                for i in 0..used.len() {
                    if !used[i] {
                        let pick = i as u32 + 1;
                        if pick >= left {
                            return true;
                        }
                        used[i] = true;
                        let other = wins(used, left - pick);
                        used[i] = false;
                        if !other {
                            return true;
                        }
                    }
                }
                false
            }

            pub fn can_i_win(max_choosable: u32, desired_total: u32) -> bool {
                if desired_total == 0 {
                    return true;
                }
                if max_choosable * (max_choosable + 1) / 2 < desired_total {
                    return false;
                }
                wins(&mut vec![false; max_choosable as usize], desired_total)
            }
        """,
        no_sum_check="""
            pub fn can_i_win(max_choosable: u32, desired_total: u32) -> bool {
                let m = max_choosable as usize;
                if desired_total == 0 {
                    return true;
                }
                fn wins(used: usize, left: u32, m: usize, memo: &mut [u8]) -> bool {
                    if memo[used] != 0 {
                        return memo[used] == 1;
                    }
                    let win = (0..m).any(|i| {
                        let pick = i as u32 + 1;
                        used & (1 << i) == 0 && (pick >= left || !wins(used | 1 << i, left - pick, m, memo))
                    });
                    memo[used] = if win { 1 } else { 2 };
                    win
                }
                let mut memo = vec![0u8; 1 << m];
                wins(0, desired_total, m, &mut memo)
            }
        """,
        memo_by_total="""
            pub fn can_i_win(max_choosable: u32, desired_total: u32) -> bool {
                let m = max_choosable as usize;
                if desired_total == 0 {
                    return true;
                }
                if m * (m + 1) / 2 < desired_total as usize {
                    return false;
                }
                // Remembers the answer per remaining total, forgetting which numbers are used.
                fn wins(used: usize, left: u32, m: usize, memo: &mut [u8]) -> bool {
                    if memo[left as usize] != 0 {
                        return memo[left as usize] == 1;
                    }
                    let win = (0..m).any(|i| {
                        let pick = i as u32 + 1;
                        used & (1 << i) == 0 && (pick >= left || !wins(used | 1 << i, left - pick, m, memo))
                    });
                    memo[left as usize] = if win { 1 } else { 2 };
                    win
                }
                let mut memo = vec![0u8; desired_total as usize + 1];
                wins(0, desired_total, m, &mut memo)
            }
        """,
    ),
    hints=[("approach", "Try every unused number: if it reaches the total, or leaves a position where the opponent can't win, the mover wins. The used numbers determine the running total, so memoise on them alone."),
           ("rust", "Numbers 1..=20 fit in the bits of a `usize`: `used & (1 << i)` tests, `used | 1 << i` adds. A `Vec<u8>` of length `1 << m` is the memo (0 unknown, 1 win, 2 loss)."),
           ("edge case", "Check the two early answers first: a total of 0 is already won, and if 1 + 2 + … + m < desired_total nobody wins, so player 1 can't.")],
    notes=("Without a memo the game tree has up to 20! lines of play. The used-set bitmask has 2²⁰ values and each tries up to 20 moves.", "O(2^m · m)", "O(2^m)"),
    follow_up="Why is the remaining total alone not enough as a memo key?",
    related=["D11", "D13"],
))

P.append(dict(
    slug="shortest-path-visiting-all-nodes", title="Shortest path visiting all nodes", level="hard", stage="bitmasks-digits",
    tags=["BFS on states", "bitmask"],
    companies=["Google", "Amazon", "Meta"],
    teaches=["BFS over (node, visited set) states, with the set as a bitmask.",
             "Multi-source BFS: start from every node at distance 0."],
    statement="""
        `graph` is a connected undirected graph: `graph[u]` lists the neighbours of node `u`.
        Return the length (number of edges) of the shortest walk that visits every node. The walk
        may start and end anywhere, revisit nodes and reuse edges.
    """,
    examples=[("graph = [[1, 2, 3], [0], [0], [0]]", "4 (1 → 0 → 2 → 0 → 3)"),
              ("graph = [[1], [0, 2, 4], [1, 3, 4], [2], [1, 2]]", "4 (0 → 1 → 4 → 2 → 3)")],
    constraints=["0 ≤ graph.len() ≤ 12", "the graph is connected, with no self-loops or repeated edges", "v is in graph[u] exactly when u is in graph[v]"],
    starter="""
        pub fn shortest_path_length(graph: &[Vec<usize>]) -> usize {
            todo!()
        }
    """,
    solution="""
        use std::collections::VecDeque;

        pub fn shortest_path_length(graph: &[Vec<usize>]) -> usize {
            let n = graph.len();
            if n <= 1 {
                return 0;
            }
            let all = (1usize << n) - 1;
            // A state is (where we are, which nodes we've visited). BFS from every start at once.
            let mut seen = vec![vec![false; 1 << n]; n];
            let mut queue = VecDeque::new();
            for u in 0..n {
                seen[u][1 << u] = true;
                queue.push_back((u, 1usize << u, 0));
            }
            while let Some((u, visited, dist)) = queue.pop_front() {
                for &v in &graph[u] {
                    let next = visited | 1 << v;
                    if next == all {
                        return dist + 1;
                    }
                    if !seen[v][next] {
                        seen[v][next] = true;
                        queue.push_back((v, next, dist + 1));
                    }
                }
            }
            unreachable!("the graph is connected")
        }
    """,
    visible=[
        T("leetcode_star", "graph = [[1, 2, 3], [0], [0], [0]]", "shortest_path_length(&[vec![1, 2, 3], vec![0], vec![0], vec![0]])", "4"),
        T("leetcode_five", "graph = [[1], [0, 2, 4], [1, 3, 4], [2], [1, 2]]",
          "shortest_path_length(&[vec![1], vec![0, 2, 4], vec![1, 3, 4], vec![2], vec![1, 2]])", "4"),
        T("single_node", "graph = [[]]", "shortest_path_length(&[vec![]])", "0"),
        T("two_nodes", "graph = [[1], [0]]", "shortest_path_length(&[vec![1], vec![0]])", "1"),
        T("triangle", "graph = [[1, 2], [0, 2], [0, 1]]", "shortest_path_length(&[vec![1, 2], vec![0, 2], vec![0, 1]])", "2"),
    ],
    hidden=[
        T("empty", "graph = []", "shortest_path_length(&[])", "0"),
        T("single_node", "graph = [[]]", "shortest_path_length(&[vec![]])", "0"),
        T("lollipop", "a triangle 0-1-2 with a tail 2-3-4-5", "shortest_path_length(&g)", "5",
          setup="let g = vec![vec![1, 2], vec![0, 2], vec![1, 0, 3], vec![2, 4], vec![3, 5], vec![4]];"),
        T("spider", "node 0 with three legs of three nodes each", "shortest_path_length(&g)", "12",
          setup="let g = vec![vec![1, 4, 7], vec![0, 2], vec![1, 3], vec![2], vec![0, 5], vec![4, 6], vec![5], vec![0, 8], vec![7, 9], vec![8]];"),
        T("path_12", "a path 0-1-…-11", "shortest_path_length(&g)", "11",
          setup="let g: Vec<Vec<usize>> = (0..12usize).map(|i| [i.checked_sub(1), (i + 1 < 12).then_some(i + 1)].into_iter().flatten().collect()).collect();"),
        T("star_12", "node 0 joined to nodes 1..=11", "shortest_path_length(&g)", "20",
          setup="let g: Vec<Vec<usize>> = (0..12).map(|i| if i == 0 { (1..12).collect() } else { vec![0] }).collect();"),
        T("complete_12", "every pair of 12 nodes joined", "shortest_path_length(&g)", "11",
          setup="let g: Vec<Vec<usize>> = (0..12).map(|i| (0..12).filter(|&j| j != i).collect()).collect();"),
        T("binary_tree_12", "node i > 0 joined to (i - 1) / 2, 12 nodes", "shortest_path_length(&g)", "16",
          setup="let mut g = vec![vec![]; 12];\nfor i in 1..12usize {\n    g[i].push((i - 1) / 2);\n    g[(i - 1) / 2].push(i);\n}"),
        """
        #[test]
        fn random_vs_brute_force() {
            // Shortest distances between all pairs, then the best order to visit the nodes in.
            fn best(dist: &[Vec<usize>], order: &mut Vec<usize>, used: &mut Vec<bool>) -> usize {
                let n = dist.len();
                if order.len() == n {
                    return order.windows(2).map(|w| dist[w[0]][w[1]]).sum();
                }
                let mut top = usize::MAX;
                for v in 0..n {
                    if !used[v] {
                        used[v] = true;
                        order.push(v);
                        top = top.min(best(dist, order, used));
                        order.pop();
                        used[v] = false;
                    }
                }
                top
            }
            let mut rng = anneal_prelude::Rng::new(1249);
            for _ in 0..300 {
                let n = rng.int(1, 7) as usize;
                let mut g = vec![vec![]; n];
                // A random tree keeps it connected, then a few extra edges.
                for v in 1..n {
                    let u = rng.below(v);
                    g[u].push(v);
                    g[v].push(u);
                }
                let extra = rng.below(n + 1);
                for _ in 0..extra {
                    let (a, b) = (rng.below(n), rng.below(n));
                    if a != b && !g[a].contains(&b) {
                        g[a].push(b);
                        g[b].push(a);
                    }
                }
                let mut dist = vec![vec![usize::MAX / 4; n]; n];
                for u in 0..n {
                    dist[u][u] = 0;
                    for &v in &g[u] {
                        dist[u][v] = 1;
                    }
                }
                for k in 0..n {
                    for i in 0..n {
                        for j in 0..n {
                            dist[i][j] = dist[i][j].min(dist[i][k] + dist[k][j]);
                        }
                    }
                }
                let want = best(&dist, &mut vec![], &mut vec![false; n]);
                check!(format!("graph = {g:?}"), shortest_path_length(&g), want);
            }
        }

        #[test]
        fn scale_twelve_nodes() {
            // A cycle of 12 with a few chords; brute force over visiting orders is 12! ≈ 4.8·10⁸.
            let mut g: Vec<Vec<usize>> = (0..12).map(|i| vec![(i + 11) % 12, (i + 1) % 12]).collect();
            for (a, b) in [(0, 6), (3, 9), (1, 7)] {
                g[a].push(b);
                g[b].push(a);
            }
            check!("cycle of 12 plus chords 0-6, 3-9, 1-7", shortest_path_length(&g), 11);
            let star: Vec<Vec<usize>> = (0..12).map(|i| if i == 0 { (1..12).collect() } else { vec![0] }).collect();
            check!("star of 12", shortest_path_length(&star), 20);
        }
        """,
    ],
    wrong=dict(
        try_every_order="""
            fn best(dist: &[Vec<usize>], last: usize, used: &mut Vec<bool>, left: usize) -> usize {
                if left == 0 {
                    return 0;
                }
                let mut top = usize::MAX;
                for v in 0..dist.len() {
                    if !used[v] {
                        used[v] = true;
                        top = top.min(dist[last][v] + best(dist, v, used, left - 1));
                        used[v] = false;
                    }
                }
                top
            }

            pub fn shortest_path_length(graph: &[Vec<usize>]) -> usize {
                let n = graph.len();
                let mut dist = vec![vec![usize::MAX / 4; n]; n];
                for u in 0..n {
                    dist[u][u] = 0;
                    for &v in &graph[u] {
                        dist[u][v] = 1;
                    }
                }
                for k in 0..n {
                    for i in 0..n {
                        for j in 0..n {
                            dist[i][j] = dist[i][j].min(dist[i][k] + dist[k][j]);
                        }
                    }
                }
                let mut top = 0;
                for s in 0..n {
                    let mut used = vec![false; n];
                    used[s] = true;
                    let b = best(&dist, s, &mut used, n - 1);
                    top = if s == 0 { b } else { top.min(b) };
                }
                top
            }
        """,
        start_at_zero="""
            use std::collections::VecDeque;

            pub fn shortest_path_length(graph: &[Vec<usize>]) -> usize {
                let n = graph.len();
                if n <= 1 {
                    return 0;
                }
                let all = (1usize << n) - 1;
                let mut seen = vec![vec![false; 1 << n]; n];
                let mut queue = VecDeque::new();
                seen[0][1] = true;
                queue.push_back((0, 1usize, 0));
                while let Some((u, visited, dist)) = queue.pop_front() {
                    for &v in &graph[u] {
                        let next = visited | 1 << v;
                        if next == all {
                            return dist + 1;
                        }
                        if !seen[v][next] {
                            seen[v][next] = true;
                            queue.push_back((v, next, dist + 1));
                        }
                    }
                }
                unreachable!()
            }
        """,
        seen_by_node_only="""
            use std::collections::VecDeque;

            pub fn shortest_path_length(graph: &[Vec<usize>]) -> usize {
                let n = graph.len();
                if n <= 1 {
                    return 0;
                }
                let all = (1usize << n) - 1;
                let mut seen = vec![false; n];
                let mut queue = VecDeque::new();
                for u in 0..n {
                    queue.push_back((u, 1usize << u, 0));
                }
                while let Some((u, visited, dist)) = queue.pop_front() {
                    for &v in &graph[u] {
                        let next = visited | 1 << v;
                        if next == all {
                            return dist + 1;
                        }
                        if !seen[v] {
                            seen[v] = true;
                            queue.push_back((v, next, dist + 1));
                        }
                    }
                }
                usize::MAX
            }
        """,
    ),
    hints=[("approach", "Where you are isn't enough to describe progress; where you are plus which nodes you've visited is. BFS over those (node, mask) states from every node at once; the first state with every bit set gives the answer."),
           ("rust", "`1usize << n` masks; `seen: Vec<Vec<bool>>` indexed `[node][mask]`; a `VecDeque<(usize, usize, usize)>` of (node, mask, distance)."),
           ("edge case", "The walk may revisit nodes (a star needs to), and it may start anywhere, so seed the queue with every node. One node (or none) needs 0 edges.")],
    notes=("There are n · 2ⁿ states and each has at most n - 1 neighbours, so BFS over them is exact and fast for n ≤ 12, while trying visiting orders is n!.", "O(2ⁿ · n²)", "O(2ⁿ · n)"),
    follow_up="How would you solve it with weighted edges? (Held–Karp: all-pairs distances, then a DP over (mask, last).)",
    related=["D9"],
))

P.append(dict(
    slug="number-of-ways-to-wear-different-hats", title="Number of ways to wear different hats", level="hard", stage="bitmasks-digits",
    tags=["bitmask DP", "modulo"],
    companies=["Google", "Amazon"],
    teaches=["Putting the bitmask on the small side: 10 people fit a mask, 40 hats don't.",
             "Walking masks downwards so each hat is used at most once, as in 0/1 knapsack."],
    statement="""
        `hats[i]` lists the hats (numbered 1 to 40) that person `i` is willing to wear. Every
        person must wear exactly one hat they like, and no two people may wear the same hat. Return
        the number of ways to do that, modulo 1 000 000 007. With nobody to dress there is one way.
    """,
    examples=[("hats = [[3, 4], [4, 5], [5]]", "1 (hat 3, then 4, then 5)"), ("hats = [[3, 5, 1], [3, 5]]", "4")],
    constraints=["0 ≤ hats.len() ≤ 10", "1 ≤ hats[i][j] ≤ 40", "each hats[i] has distinct values"],
    starter="""
        pub fn number_ways(hats: &[Vec<u8>]) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn number_ways(hats: &[Vec<u8>]) -> u64 {
            const MOD: u64 = 1_000_000_007;
            let n = hats.len();
            // likes[h] = the people who would wear hat h, as a bitmask.
            let mut likes = [0usize; 41];
            for (person, list) in hats.iter().enumerate() {
                for &h in list {
                    likes[h as usize] |= 1 << person;
                }
            }
            // ways[mask] = ways to dress exactly the people in mask using the hats handled so far.
            let mut ways = vec![0u64; 1 << n];
            ways[0] = 1;
            for h in 1..=40 {
                // Downwards, so ways[mask ^ p] still excludes hat h: it goes to one person at most.
                for mask in (1..1usize << n).rev() {
                    let mut wearers = likes[h] & mask;
                    while wearers != 0 {
                        let p = wearers & wearers.wrapping_neg();
                        ways[mask] = (ways[mask] + ways[mask ^ p]) % MOD;
                        wearers ^= p;
                    }
                }
            }
            ways[(1 << n) - 1]
        }
    """,
    visible=[
        T("leetcode_one_way", "hats = [[3, 4], [4, 5], [5]]", "number_ways(&[vec![3, 4], vec![4, 5], vec![5]])", "1"),
        T("leetcode_four_ways", "hats = [[3, 5, 1], [3, 5]]", "number_ways(&[vec![3, 5, 1], vec![3, 5]])", "4"),
        T("leetcode_all_alike", "hats = [[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]]",
          "number_ways(&[vec![1, 2, 3, 4], vec![1, 2, 3, 4], vec![1, 2, 3, 4], vec![1, 2, 3, 4]])", "24"),
        T("nobody", "hats = []", "number_ways(&[])", "1"),
        T("same_single_hat", "hats = [[5], [5]]", "number_ways(&[vec![5], vec![5]])", "0"),
    ],
    hidden=[
        T("nobody", "hats = []", "number_ways(&[])", "1"),
        T("one_person_one_hat", "hats = [[7]]", "number_ways(&[vec![7]])", "1"),
        T("someone_likes_nothing", "hats = [[1, 2], []]", "number_ways(&[vec![1, 2], vec![]])", "0"),
        T("one_person_every_hat", "hats = [[1..=40]]", "number_ways(&[(1..=40).collect()])", "40"),
        T("ends_of_the_range", "hats = [[1, 40], [1, 40]]", "number_ways(&[vec![1, 40], vec![1, 40]])", "2"),
        T("chain", "hats = [[1, 2], [2, 3], [3, 4], [4, 5]]", "number_ways(&[vec![1, 2], vec![2, 3], vec![3, 4], vec![4, 5]])", "5"),
        T("ten_people_every_hat", "10 people, each likes hats 1..=40", "number_ways(&h)", "502_474_470",
          setup="let h: Vec<Vec<u8>> = vec![(1..=40).collect(); 10];"),
        T("ten_people_mixed", "person p likes hat x when x·(p + 3) % 7 < 4", "number_ways(&h)", "664_239_731",
          setup="let h: Vec<Vec<u8>> = (0..10u32).map(|p| (1..=40u8).filter(|&x| x as u32 * (p + 3) % 7 < 4).collect()).collect();"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn count(hats: &[Vec<u8>], used: &mut [bool; 41]) -> u64 {
                let Some((first, rest)) = hats.split_first() else { return 1 };
                let mut total = 0;
                for &h in first {
                    if !used[h as usize] {
                        used[h as usize] = true;
                        total += count(rest, used);
                        used[h as usize] = false;
                    }
                }
                total
            }
            let mut rng = anneal_prelude::Rng::new(1250);
            for _ in 0..300 {
                let n = rng.below(6);
                let hats: Vec<Vec<u8>> = (0..n).map(|_| (1..=8u8).filter(|_| rng.bool()).collect()).collect();
                check!(format!("hats = {hats:?}"), number_ways(&hats), count(&hats, &mut [false; 41]));
            }
        }
        """,
    ],
    wrong=dict(
        person_by_person="""
            fn count(hats: &[Vec<u8>], used: &mut [bool; 41]) -> u64 {
                let Some((first, rest)) = hats.split_first() else { return 1 };
                let mut total = 0;
                for &h in first {
                    if !used[h as usize] {
                        used[h as usize] = true;
                        total = (total + count(rest, used)) % 1_000_000_007;
                        used[h as usize] = false;
                    }
                }
                total
            }

            pub fn number_ways(hats: &[Vec<u8>]) -> u64 {
                count(hats, &mut [false; 41])
            }
        """,
        masks_upwards="""
            pub fn number_ways(hats: &[Vec<u8>]) -> u64 {
                const MOD: u64 = 1_000_000_007;
                let n = hats.len();
                let mut likes = [0usize; 41];
                for (person, list) in hats.iter().enumerate() {
                    for &h in list {
                        likes[h as usize] |= 1 << person;
                    }
                }
                let mut ways = vec![0u64; 1 << n];
                ways[0] = 1;
                for h in 1..=40 {
                    for mask in 1..1usize << n {
                        let mut wearers = likes[h] & mask;
                        while wearers != 0 {
                            let p = wearers & wearers.wrapping_neg();
                            ways[mask] = (ways[mask] + ways[mask ^ p]) % MOD;
                            wearers ^= p;
                        }
                    }
                }
                ways[(1 << n) - 1]
            }
        """,
        no_modulo="""
            pub fn number_ways(hats: &[Vec<u8>]) -> u64 {
                let n = hats.len();
                let mut likes = [0usize; 41];
                for (person, list) in hats.iter().enumerate() {
                    for &h in list {
                        likes[h as usize] |= 1 << person;
                    }
                }
                let mut ways = vec![0u64; 1 << n];
                ways[0] = 1;
                for h in 1..=40 {
                    for mask in (1..1usize << n).rev() {
                        let mut wearers = likes[h] & mask;
                        while wearers != 0 {
                            let p = wearers & wearers.wrapping_neg();
                            ways[mask] += ways[mask ^ p];
                            wearers ^= p;
                        }
                    }
                }
                ways[(1 << n) - 1]
            }
        """,
    ),
    hints=[("approach", "There are at most 10 people but 40 hats, so keep a mask of which people are dressed and hand the hats out one at a time: each hat goes to nobody or to one person who likes it and isn't dressed yet."),
           ("rust", "`likes[h]` as a people-mask; `ways: Vec<u64>` of length `1 << n`; `mask & mask.wrapping_neg()` isolates the lowest set bit."),
           ("edge case", "Go through the masks from high to low for each hat, or the same hat gets handed to two people. Reduce modulo 1 000 000 007 as you add.")],
    notes=("A mask over hats would have 2⁴⁰ states; a mask over people has 2¹⁰. Each of the 40 hats updates every mask once per person who likes it.", "O(40 · 2ⁿ · n)", "O(2ⁿ)"),
    follow_up="If there were 40 people and 10 hats, which side would the mask go on, and what would the answer be?",
    related=["D11", "D13"],
))

STAGES = [
    ("1d-basics", "1-D basics", "easy"),
    ("1d-choices", "1-D choices", "medium"),
    ("2d-grids", "2-D grids", "medium"),
    ("strings", "Strings", "medium"),
    ("knapsack", "Knapsack", "medium"),
    ("state-machines", "State machines", "medium"),
    ("intervals-games", "Intervals & games", "hard"),
    ("bitmasks-digits", "Bitmasks & digits", "hard"),
    ("hard-strings", "Hard strings", "hard"),
    ("dp-the-rust-way", "DP the Rust way", "hard"),
]

if __name__ == "__main__":
    n = write_track("d12-dynamic-programming", "D12", "Dynamic programming", "D", "core", 10,
                    "From memoised recursion to tables to rolling variables: one-dimensional choices, grids, strings, knapsacks, state machines, intervals and bitmasks, in owned, overflow-safe Rust.",
                    STAGES, P)
    print("D12", n)
