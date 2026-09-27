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
