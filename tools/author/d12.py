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
