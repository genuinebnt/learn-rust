from author import T, write_track

P = []

# ---------------------------------------------------------------------------------------------------------------------
# Stage 1 · Recursion (easy): base case, trust the recursive call, divide and conquer.
# ---------------------------------------------------------------------------------------------------------------------

# Float answers: `approx` returns `want` when `got` is within 1e-9 (relative), so a failure still shows the real value.
APPROX = """
fn approx(got: f64, want: f64) -> f64 {
    if got == want || (got - want).abs() <= 1e-9 * want.abs().max(1.0) {
        want
    } else {
        got
    }
}
"""

P.append(dict(
    slug="pow-x-n", title="Pow(x, n)", level="easy", stage="recursion", tags=["recursion", "fast power"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "LinkedIn", "Bloomberg"],
    teaches=["Halve the problem: x⁽ⁿ⁾ = (x⁽ⁿᐟ²⁾)², so the recursion is only log n deep.",
             "`i32::unsigned_abs` avoids the overflow of `-i32::MIN`."],
    statement="""
        Return `x` raised to the power `n`. `n` can be negative (then the answer is `1 / x^|n|`) and can be as large as
        `i32::MAX` or as small as `i32::MIN`, so multiplying `x` in a loop `n` times is too slow.

        `x⁰` is 1 for every `x`, including 0. Answers are compared with a relative tolerance of 10⁻⁹.
    """,
    examples=[("x = 2.0, n = 10", "1024.0"), ("x = 2.1, n = 3", "9.261"), ("x = 2.0, n = -2", "0.25")],
    constraints=["-100 < x < 100", "i32::MIN ≤ n ≤ i32::MAX", "x ≠ 0 when n < 0, except where the answer is ∞"],
    starter="""
        pub fn my_pow(x: f64, n: i32) -> f64 {
            todo!()
        }
    """,
    solution="""
        pub fn my_pow(x: f64, n: i32) -> f64 {
            // x^n for n ≥ 0: square the answer for n / 2, times x once more when n is odd.
            fn power(x: f64, n: u32) -> f64 {
                if n == 0 {
                    return 1.0;
                }
                let half = power(x, n / 2);
                if n % 2 == 0 { half * half } else { half * half * x }
            }
            // `unsigned_abs` is exact for i32::MIN, where `-n` would overflow.
            let p = power(x, n.unsigned_abs());
            if n < 0 { 1.0 / p } else { p }
        }
    """,
    visible=[
        APPROX,
        T("leetcode_two_to_the_ten", "x = 2.0, n = 10", "approx(my_pow(2.0, 10), 1024.0)", "1024.0"),
        T("leetcode_fractional_base", "x = 2.1, n = 3", "approx(my_pow(2.1, 3), 9.261)", "9.261"),
        T("leetcode_negative_exponent", "x = 2.0, n = -2", "approx(my_pow(2.0, -2), 0.25)", "0.25"),
        T("zero_exponent_is_one", "x = 5.0, n = 0", "approx(my_pow(5.0, 0), 1.0)", "1.0"),
        T("exponent_one", "x = 0.5, n = 1", "approx(my_pow(0.5, 1), 0.5)", "0.5"),
        T("negative_base_odd_exponent", "x = -2.0, n = 3", "approx(my_pow(-2.0, 3), -8.0)", "-8.0"),
    ],
    hidden=[
        APPROX,
        T("zero_base", "x = 0.0, n = 5", "approx(my_pow(0.0, 5), 0.0)", "0.0"),
        T("zero_to_the_zero", "x = 0.0, n = 0", "approx(my_pow(0.0, 0), 1.0)", "1.0"),
        T("negative_base_even_exponent", "x = -2.0, n = 4", "approx(my_pow(-2.0, 4), 16.0)", "16.0"),
        T("half_to_minus_three", "x = 0.5, n = -3", "approx(my_pow(0.5, -3), 8.0)", "8.0"),
        T("one_to_min_exponent", "x = 1.0, n = i32::MIN", "approx(my_pow(1.0, i32::MIN), 1.0)", "1.0"),
        T("two_to_min_exponent", "x = 2.0, n = i32::MIN", "approx(my_pow(2.0, i32::MIN), 0.0)", "0.0"),
        T("minus_one_to_min_exponent", "x = -1.0, n = i32::MIN", "approx(my_pow(-1.0, i32::MIN), 1.0)", "1.0"),
        T("minus_one_to_max_exponent", "x = -1.0, n = i32::MAX", "approx(my_pow(-1.0, i32::MAX), -1.0)", "-1.0"),
        T("half_to_max_exponent", "x = 0.5, n = i32::MAX", "approx(my_pow(0.5, i32::MAX), 0.0)", "0.0"),
        T("small_answer", "x = 0.1, n = 5", "approx(my_pow(0.1, 5), 1e-5)", "1e-5"),
        """
        #[test]
        fn random_vs_powi() {
            let mut rng = anneal_prelude::Rng::new(1101);
            for _ in 0..400 {
                let x = rng.int(-200, 200) as f64 / 100.0;
                let n = rng.int(-20, 20) as i32;
                let want = x.powi(n);
                check!(format!("x = {x}, n = {n}"), approx(my_pow(x, n), want), want);
            }
        }

        #[test]
        fn scale_huge_exponents() {
            let got = (my_pow(1.0, i32::MAX), my_pow(-1.0, i32::MAX - 2), my_pow(1.0, i32::MIN + 1), my_pow(0.5, i32::MAX - 1), my_pow(-1.0, i32::MIN + 3));
            check!("x = ±1.0 or 0.5, n near i32::MAX / i32::MIN", got, (1.0, -1.0, 1.0, 0.0, -1.0));
        }
        """,
    ],
    wrong=dict(
        linear="""
            pub fn my_pow(x: f64, n: i32) -> f64 {
                let mut p = 1.0;
                for _ in 0..n.unsigned_abs() {
                    p *= x;
                }
                if n < 0 { 1.0 / p } else { p }
            }
        """,
        negate_overflows="""
            pub fn my_pow(x: f64, n: i32) -> f64 {
                if n < 0 {
                    return 1.0 / my_pow(x, -n);
                }
                if n == 0 {
                    return 1.0;
                }
                let half = my_pow(x, n / 2);
                if n % 2 == 0 { half * half } else { half * half * x }
            }
        """,
        ignores_the_sign="""
            pub fn my_pow(x: f64, n: i32) -> f64 {
                fn power(x: f64, n: u32) -> f64 {
                    if n == 0 {
                        return 1.0;
                    }
                    let half = power(x, n / 2);
                    if n % 2 == 0 { half * half } else { half * half * x }
                }
                power(x, n.unsigned_abs())
            }
        """,
    ),
    hints=[("approach", "x^n = (x^(n/2))² when n is even, and one more factor of x when n is odd. Compute the half once."),
           ("rust", "Work on `n.unsigned_abs()` (a `u32`) in an inner `fn`, then take `1.0 / p` for a negative `n`."),
           ("edge case", "`-i32::MIN` overflows and panics in a debug build.")],
    notes=("Each call halves the exponent and reuses one recursive result, so there are about log₂|n| calls. "
           "Working on the unsigned magnitude sidesteps the one negative `i32` with no positive twin.", "O(log n)", "O(log n) recursion depth"),
    follow_up="Write it iteratively by walking the bits of n. Where does modular exponentiation use the same idea?",
    related=["D13", "S1"],
))

P.append(dict(
    slug="k-th-symbol-in-grammar", title="K-th symbol in grammar", level="easy", stage="recursion", tags=["recursion", "bits"],
    companies=["Amazon", "Google", "Microsoft"],
    teaches=["Describe row n in terms of row n − 1 and recurse on the half that holds k.",
             "Never build a row that has 2⁶³ symbols: follow one path down instead."],
    statement="""
        Row 1 is `0`. Each next row replaces every `0` in the previous row with `01` and every `1` with `10`, so the
        rows start `0`, `01`, `0110`, `01101001`. Row `n` has `2^(n-1)` symbols.

        Return the `k`-th symbol of row `n`, counting from **1**.
    """,
    examples=[("n = 2, k = 2", "1"), ("n = 4, k = 5", "1")],
    constraints=["1 ≤ n ≤ 64", "1 ≤ k ≤ 2^(n-1)"],
    starter="""
        pub fn kth_grammar(n: u32, k: u64) -> u8 {
            todo!()
        }
    """,
    solution="""
        pub fn kth_grammar(n: u32, k: u64) -> u8 {
            if n == 1 {
                return 0;
            }
            // Row n is row n - 1 followed by row n - 1 with every symbol flipped.
            let half = 1u64 << (n - 2);
            if k <= half { kth_grammar(n - 1, k) } else { 1 - kth_grammar(n - 1, k - half) }
        }
    """,
    visible=[
        T("first_row", "n = 1, k = 1", "kth_grammar(1, 1)", "0"),
        T("leetcode_row_two_first", "n = 2, k = 1", "kth_grammar(2, 1)", "0"),
        T("leetcode_row_two_second", "n = 2, k = 2", "kth_grammar(2, 2)", "1"),
        T("k_counts_from_one", "n = 3, k = 4 (row 0110)", "kth_grammar(3, 4)", "0"),
        T("row_four", "n = 4, k = 1..=8 (row 01101001)", "(1..=8).map(|k| kth_grammar(4, k)).collect::<Vec<u8>>()", "vec![0, 1, 1, 0, 1, 0, 0, 1]"),
    ],
    hidden=[
        T("row_three_middle", "n = 3, k = 3", "kth_grammar(3, 3)", "1"),
        T("last_of_row_four", "n = 4, k = 8", "kth_grammar(4, 8)", "1"),
        T("last_of_row_five", "n = 5, k = 16", "kth_grammar(5, 16)", "0"),
        T("row_ten", "n = 10, k = 500", "kth_grammar(10, 500)", "1"),
        T("row_thirty_first", "n = 30, k = 1", "kth_grammar(30, 1)", "0"),
        T("row_thirty_last", "n = 30, k = 2^29", "kth_grammar(30, 1 << 29)", "1"),
        T("row_64_first", "n = 64, k = 1", "kth_grammar(64, 1)", "0"),
        T("row_64_last", "n = 64, k = 2^63", "kth_grammar(64, 1 << 63)", "1"),
        T("row_64_middle", "n = 64, k = 2^62", "kth_grammar(64, 1 << 62)", "0"),
        T("row_64_just_past_middle", "n = 64, k = 2^62 + 1", "kth_grammar(64, (1 << 62) + 1)", "1"),
        T("row_64_large_k", "n = 64, k = 12345678901234567", "kth_grammar(64, 12_345_678_901_234_567)", "1"),
        """
        #[test]
        fn random_vs_built_rows() {
            let mut rows: Vec<Vec<u8>> = vec![vec![0]];
            for _ in 1..12 {
                let next = rows.last().unwrap().iter().flat_map(|&s| if s == 0 { [0, 1] } else { [1, 0] }).collect();
                rows.push(next);
            }
            let mut rng = anneal_prelude::Rng::new(1102);
            for _ in 0..400 {
                let n = rng.int(1, 12) as u32;
                let k = rng.int(1, 1 << (n - 1)) as u64;
                check!(format!("n = {n}, k = {k}"), kth_grammar(n, k), rows[n as usize - 1][k as usize - 1]);
            }
        }

        #[test]
        fn scale_100k_queries_on_row_64() {
            let mut rng = anneal_prelude::Rng::new(1103);
            for _ in 0..100_000 {
                let k = rng.next_u64() % (1 << 63) + 1;
                let want = ((k - 1).count_ones() % 2) as u8;
                let got = kth_grammar(64, k);
                if got != want {
                    check!(format!("n = 64, k = {k}"), got, want);
                }
            }
        }
        """,
    ],
    wrong=dict(
        zero_based_k="""
            pub fn kth_grammar(n: u32, k: u64) -> u8 {
                let _ = n;
                (k.count_ones() % 2) as u8
            }
        """,
        second_half_not_flipped="""
            pub fn kth_grammar(n: u32, k: u64) -> u8 {
                if n == 1 {
                    return 0;
                }
                let half = 1u64 << (n - 2);
                if k <= half { kth_grammar(n - 1, k) } else { kth_grammar(n - 1, k - half) }
            }
        """,
    ),
    hints=[("approach", "The first half of row n is row n − 1; the second half is row n − 1 with every symbol flipped."),
           ("rust", "The half length is `1u64 << (n - 2)`. Recurse into row n − 1 with `k` or `k - half`."),
           ("edge case", "k counts from 1, so k = 2^(n-2) is still in the first half.")],
    notes=("Each call moves up one row and keeps only the half that holds k, flipping the answer when k is in the second half. "
           "The same walk shows the answer is the parity of the set bits of k − 1.", "O(n)", "O(n) recursion depth"),
    follow_up="Why is the answer the parity of `(k - 1).count_ones()`? Write that one-liner and explain it.",
    related=["D13"],
))

HANOI_CHECK = """
/// Plays `moves` on n disks that start on peg 0; the number of moves if they are legal and end on peg 2.
fn replay(n: u32, moves: &[(u8, u8)]) -> Result<usize, String> {
    let mut pegs: Vec<Vec<u32>> = vec![(1..=n).rev().collect(), Vec::new(), Vec::new()];
    for (i, &(from, to)) in moves.iter().enumerate() {
        if from > 2 || to > 2 || from == to {
            return Err(format!("move {i} ({from}, {to}) is not a move between two pegs"));
        }
        let Some(&disk) = pegs[from as usize].last() else {
            return Err(format!("move {i} takes from empty peg {from}"));
        };
        if pegs[to as usize].last().is_some_and(|&top| top < disk) {
            return Err(format!("move {i} puts disk {disk} on a smaller disk"));
        }
        pegs[from as usize].pop();
        pegs[to as usize].push(disk);
    }
    if pegs[2].len() != n as usize {
        return Err("not every disk ended on peg 2".into());
    }
    Ok(moves.len())
}
"""

P.append(dict(
    slug="tower-of-hanoi", title="Tower of Hanoi", level="easy", stage="recursion", tags=["recursion", "Vec"],
    teaches=["Trust the recursive call: move n − 1 disks out of the way, move the big one, move them back on top.",
             "An inner `fn` that pushes into a `&mut Vec` shared by every call."],
    statement="""
        `n` disks of different sizes sit on peg 0, largest at the bottom. Move them all to peg 2, one disk at a time,
        never putting a disk on a smaller one. Peg 1 is the spare.

        Return the moves as `(from, to)` pairs, in order, using the fewest moves possible (there is only one shortest
        sequence).
    """,
    examples=[("n = 2", "[(0, 1), (0, 2), (1, 2)]")],
    constraints=["0 ≤ n ≤ 20"],
    starter="""
        pub fn hanoi(n: u32) -> Vec<(u8, u8)> {
            todo!()
        }
    """,
    solution="""
        pub fn hanoi(n: u32) -> Vec<(u8, u8)> {
            fn solve(n: u32, from: u8, spare: u8, to: u8, moves: &mut Vec<(u8, u8)>) {
                if n == 0 {
                    return;
                }
                solve(n - 1, from, to, spare, moves);
                moves.push((from, to));
                solve(n - 1, spare, from, to, moves);
            }
            let mut moves = Vec::with_capacity((1usize << n) - 1);
            solve(n, 0, 1, 2, &mut moves);
            moves
        }
    """,
    visible=[
        T("one_disk", "n = 1", "hanoi(1)", "vec![(0, 2)]"),
        T("no_disks", "n = 0", "hanoi(0)", "Vec::<(u8, u8)>::new()"),
        T("two_disks", "n = 2", "hanoi(2)", "vec![(0, 1), (0, 2), (1, 2)]"),
        T("three_disks", "n = 3", "hanoi(3)", "vec![(0, 2), (0, 1), (2, 1), (0, 2), (1, 0), (1, 2), (0, 2)]"),
        T("ten_disks_take_1023_moves", "n = 10", "hanoi(10).len()", "1023"),
    ],
    hidden=[
        HANOI_CHECK,
        T("four_disks", "n = 4", "hanoi(4)", "vec![(0, 1), (0, 2), (1, 2), (0, 1), (2, 0), (2, 1), (0, 1), (0, 2), (1, 2), (1, 0), (2, 0), (1, 2), (0, 1), (0, 2), (1, 2)]"),
        T("no_disks", "n = 0", "hanoi(0)", "Vec::<(u8, u8)>::new()"),
        T("one_disk", "n = 1", "hanoi(1)", "vec![(0, 2)]"),
        T("five_disks_legal", "n = 5", "replay(5, &hanoi(5))", "Ok(31)"),
        T("six_disks_legal", "n = 6", "replay(6, &hanoi(6))", "Ok(63)"),
        T("seven_disks_first_and_last", "n = 7", "{ let m = hanoi(7); (m[0], m[63], m[126]) }", "((0, 2), (0, 2), (0, 2))"),
        T("eight_disks_first_move", "n = 8 (even: the smallest disk goes to the spare first)", "hanoi(8)[0]", "(0, 1)"),
        T("twelve_disks_legal", "n = 12", "replay(12, &hanoi(12))", "Ok(4095)"),
        """
        /// The classic iterative solution: move the smallest disk around a fixed cycle, then make the only other legal move.
        fn iterative(n: u32) -> Vec<(u8, u8)> {
            let mut pegs: Vec<Vec<u32>> = vec![(1..=n).rev().collect(), Vec::new(), Vec::new()];
            let cycle: [u8; 3] = if n % 2 == 0 { [0, 1, 2] } else { [0, 2, 1] };
            let mut small = 0;
            let mut moves = Vec::new();
            for i in 0..(1usize << n) - 1 {
                if i % 2 == 0 {
                    let (a, b) = (cycle[small], cycle[(small + 1) % 3]);
                    let d = pegs[a as usize].pop().unwrap();
                    pegs[b as usize].push(d);
                    moves.push((a, b));
                    small = (small + 1) % 3;
                } else {
                    let others: Vec<u8> = (0..3).filter(|&p| p != cycle[small]).collect();
                    let (x, y) = (others[0], others[1]);
                    let (tx, ty) = (pegs[x as usize].last().copied(), pegs[y as usize].last().copied());
                    let (a, b) = match (tx, ty) {
                        (Some(p), Some(q)) if p < q => (x, y),
                        (Some(_), Some(_)) => (y, x),
                        (Some(_), None) => (x, y),
                        _ => (y, x),
                    };
                    let d = pegs[a as usize].pop().unwrap();
                    pegs[b as usize].push(d);
                    moves.push((a, b));
                }
            }
            moves
        }

        #[test]
        fn random_vs_iterative() {
            let mut rng = anneal_prelude::Rng::new(1104);
            for _ in 0..40 {
                let n = rng.int(0, 11) as u32;
                check!(format!("n = {n}"), hanoi(n), iterative(n));
            }
        }

        #[test]
        fn scale_20_disks() {
            check!("n = 20", replay(20, &hanoi(20)), Ok((1 << 20) - 1));
        }
        """,
    ],
    wrong=dict(
        spare_and_target_swapped="""
            pub fn hanoi(n: u32) -> Vec<(u8, u8)> {
                fn solve(n: u32, from: u8, spare: u8, to: u8, moves: &mut Vec<(u8, u8)>) {
                    if n == 0 {
                        return;
                    }
                    solve(n - 1, from, spare, to, moves);
                    moves.push((from, to));
                    solve(n - 1, spare, from, to, moves);
                }
                let mut moves = Vec::new();
                solve(n, 0, 1, 2, &mut moves);
                moves
            }
        """,
        smallest_always_clockwise="""
            pub fn hanoi(n: u32) -> Vec<(u8, u8)> {
                fn solve(n: u32, from: u8, spare: u8, to: u8, moves: &mut Vec<(u8, u8)>) {
                    if n == 0 {
                        return;
                    }
                    solve(n - 1, from, to, spare, moves);
                    moves.push((from, to));
                    solve(n - 1, spare, from, to, moves);
                }
                let mut moves = Vec::new();
                // Ignores parity: for even n this ends on peg 1.
                if n % 2 == 0 { solve(n, 0, 2, 1, &mut moves) } else { solve(n, 0, 1, 2, &mut moves) }
                moves
            }
        """,
    ),
    hints=[("approach", "To move n disks from A to C: move n − 1 from A to B, move the largest from A to C, move n − 1 from B to C."),
           ("rust", "Write `fn solve(n, from, spare, to, moves: &mut Vec<(u8, u8)>)` inside `hanoi` and call it once."),
           ("edge case", "n = 0 needs no moves; make that the base case and n = 1 falls out of it.")],
    notes=("The largest disk moves once, and only when the n − 1 smaller disks are all on the spare, so every shortest solution "
           "has this shape: T(n) = 2·T(n − 1) + 1 = 2ⁿ − 1 moves.", "O(2ⁿ)", "O(n) recursion depth plus the 2ⁿ − 1 moves"),
    follow_up="How many moves does the disk of size k make? Can you print move number m without generating the others?",
    related=["D12"],
))

P.append(dict(
    slug="merge-sort", title="Merge sort", level="easy", stage="recursion", tags=["divide and conquer", "split_at"],
    companies=["Meta", "Amazon", "Google", "Microsoft"],
    teaches=["Divide and conquer: sort each half, then merge two sorted runs in one pass.",
             "`split_at` gives two borrowed halves without copying."],
    statement="""
        Return the values of `nums` in ascending order, using merge sort: split the slice in half, sort each half
        recursively, and merge the two sorted halves. Don't call a library sort.
    """,
    examples=[("nums = [5, 2, 3, 1]", "[1, 2, 3, 5]"), ("nums = [5, 1, 1, 2, 0, 0]", "[0, 0, 1, 1, 2, 5]")],
    constraints=["0 ≤ nums.len() ≤ 2·10⁵", "i32::MIN ≤ nums[i] ≤ i32::MAX"],
    starter="""
        pub fn merge_sort(nums: &[i32]) -> Vec<i32> {
            todo!()
        }
    """,
    solution="""
        pub fn merge_sort(nums: &[i32]) -> Vec<i32> {
            if nums.len() <= 1 {
                return nums.to_vec();
            }
            let (left, right) = nums.split_at(nums.len() / 2);
            let (left, right) = (merge_sort(left), merge_sort(right));
            let mut out = Vec::with_capacity(nums.len());
            let (mut i, mut j) = (0, 0);
            while i < left.len() && j < right.len() {
                if left[i] <= right[j] {
                    out.push(left[i]);
                    i += 1;
                } else {
                    out.push(right[j]);
                    j += 1;
                }
            }
            // One side is used up; the rest of the other is already sorted.
            out.extend_from_slice(&left[i..]);
            out.extend_from_slice(&right[j..]);
            out
        }
    """,
    visible=[
        T("leetcode_four", "nums = [5, 2, 3, 1]", "merge_sort(&[5, 2, 3, 1])", "vec![1, 2, 3, 5]"),
        T("leetcode_duplicates", "nums = [5, 1, 1, 2, 0, 0]", "merge_sort(&[5, 1, 1, 2, 0, 0])", "vec![0, 0, 1, 1, 2, 5]"),
        T("empty", "nums = []", "merge_sort(&[])", "Vec::<i32>::new()"),
        T("single", "nums = [7]", "merge_sort(&[7])", "vec![7]"),
        T("negatives", "nums = [3, -1, 3, -8]", "merge_sort(&[3, -1, 3, -8])", "vec![-8, -1, 3, 3]"),
        T("already_sorted", "nums = [1, 2, 3]", "merge_sort(&[1, 2, 3])", "vec![1, 2, 3]"),
    ],
    hidden=[
        T("two_swapped", "nums = [2, 1]", "merge_sort(&[2, 1])", "vec![1, 2]"),
        T("reversed", "nums = [9, 8, …, 0]", "merge_sort(&(0..10).rev().collect::<Vec<i32>>())", "(0..10).collect::<Vec<i32>>()"),
        T("all_equal", "nums = [4, 4, 4, 4, 4]", "merge_sort(&[4, 4, 4, 4, 4])", "vec![4, 4, 4, 4, 4]"),
        T("extremes", "nums = [i32::MAX, 0, i32::MIN, -1]", "merge_sort(&[i32::MAX, 0, i32::MIN, -1])", "vec![i32::MIN, -1, 0, i32::MAX]"),
        T("odd_length", "nums = [3, 1, 2]", "merge_sort(&[3, 1, 2])", "vec![1, 2, 3]"),
        T("tail_left_over", "nums = [1, 2, 3, 10, 11, 12, 4]", "merge_sort(&[1, 2, 3, 10, 11, 12, 4])", "vec![1, 2, 3, 4, 10, 11, 12]"),
        T("negatives_only", "nums = [-3, -1, -2]", "merge_sort(&[-3, -1, -2])", "vec![-3, -2, -1]"),
        T("single_negative", "nums = [-5]", "merge_sort(&[-5])", "vec![-5]"),
        """
        #[test]
        fn random_vs_std_sort() {
            let mut rng = anneal_prelude::Rng::new(1105);
            for _ in 0..300 {
                let n = rng.below(30);
                let nums: Vec<i32> = rng.vec(n, -20, 20);
                let mut want = nums.clone();
                want.sort();
                check!(format!("nums = {nums:?}"), merge_sort(&nums), want);
            }
        }

        #[test]
        fn scale_200k_reversed() {
            let nums: Vec<i32> = (0..200_000).rev().collect();
            let out = merge_sort(&nums);
            check!("nums = [199999, 199998, …, 0]", out == (0..200_000).collect::<Vec<i32>>(), true);
        }

        #[test]
        fn scale_200k_random() {
            let mut rng = anneal_prelude::Rng::new(1106);
            let nums: Vec<i32> = rng.vec(200_000, i32::MIN as i64, i32::MAX as i64);
            let mut want = nums.clone();
            want.sort();
            check!("nums = 200000 random values", merge_sort(&nums) == want, true);
        }
        """,
    ],
    wrong=dict(
        insertion_sort="""
            pub fn merge_sort(nums: &[i32]) -> Vec<i32> {
                let mut out = nums.to_vec();
                for i in 1..out.len() {
                    let mut j = i;
                    while j > 0 && out[j - 1] > out[j] {
                        out.swap(j - 1, j);
                        j -= 1;
                    }
                }
                out
            }
        """,
        drops_the_right_tail="""
            pub fn merge_sort(nums: &[i32]) -> Vec<i32> {
                if nums.len() <= 1 {
                    return nums.to_vec();
                }
                let (left, right) = nums.split_at(nums.len() / 2);
                let (left, right) = (merge_sort(left), merge_sort(right));
                let mut out = Vec::with_capacity(nums.len());
                let (mut i, mut j) = (0, 0);
                while i < left.len() && j < right.len() {
                    if left[i] <= right[j] {
                        out.push(left[i]);
                        i += 1;
                    } else {
                        out.push(right[j]);
                        j += 1;
                    }
                }
                out.extend_from_slice(&left[i..]);
                out
            }
        """,
    ),
    hints=[("approach", "A slice of 0 or 1 values is sorted. Otherwise sort both halves and merge them with two indices."),
           ("rust", "`let (left, right) = nums.split_at(nums.len() / 2);` then `extend_from_slice` whatever is left of each side."),
           ("edge case", "When one half runs out, the rest of the other half still has to be copied.")],
    notes=("The recursion is log₂ n levels deep and each level merges n values in total. `<=` in the merge keeps equal values in "
           "their original order, which makes merge sort stable.", "O(n log n)", "O(n) for the merged vectors"),
    follow_up="How would you sort in place with a single scratch buffer instead of allocating at every level?",
    related=["S3", "D4"],
))

P.append(dict(
    slug="fix-unbounded-recursion", title="Fix: unbounded recursion", mode="fix", level="easy", stage="recursion",
    tags=["base case", "split_at", "stack overflow"],
    teaches=["Every recursive call must get strictly closer to a base case.",
             "`split_at(len / 2)` on a one-element slice gives back the same element: that call never shrinks."],
    statement="""
        `split_sum` should add up `nums` by splitting the slice in half and summing each half. It works for an empty
        slice, but anything else overflows the stack. Fix the base case; keep the recursion.
    """,
    examples=[("nums = [1, 2, 3, 4]", "10")],
    constraints=["0 ≤ nums.len() ≤ 2·10⁵", "the sum fits in an i64"],
    starter="""
        /// The sum of `nums`, computed by summing each half.
        pub fn split_sum(nums: &[i64]) -> i64 {
            if nums.is_empty() {
                return 0;
            }
            let (left, right) = nums.split_at(nums.len() / 2);
            split_sum(left) + split_sum(right)
        }
    """,
    solution="""
        /// The sum of `nums`, computed by summing each half.
        pub fn split_sum(nums: &[i64]) -> i64 {
            if nums.is_empty() {
                return 0;
            }
            if nums.len() == 1 {
                return nums[0];
            }
            let (left, right) = nums.split_at(nums.len() / 2);
            split_sum(left) + split_sum(right)
        }
    """,
    rules=dict(methods=["iter", "into_iter"], lines=3),
    visible=[
        T("four_values", "nums = [1, 2, 3, 4]", "split_sum(&[1, 2, 3, 4])", "10"),
        T("empty", "nums = []", "split_sum(&[])", "0"),
        T("single", "nums = [5]", "split_sum(&[5])", "5"),
        T("odd_length", "nums = [1, 2, 3]", "split_sum(&[1, 2, 3])", "6"),
        T("negatives", "nums = [-3, 3, 7]", "split_sum(&[-3, 3, 7])", "7"),
    ],
    hidden=[
        T("single_negative", "nums = [-9]", "split_sum(&[-9])", "-9"),
        T("single_zero", "nums = [0]", "split_sum(&[0])", "0"),
        T("two", "nums = [4, 6]", "split_sum(&[4, 6])", "10"),
        T("cancels_out", "nums = [5, -5, 5, -5, 1]", "split_sum(&[5, -5, 5, -5, 1])", "1"),
        T("near_max", "nums = [i64::MAX - 1, 1]", "split_sum(&[i64::MAX - 1, 1])", "i64::MAX"),
        T("near_min", "nums = [i64::MIN + 5, -5]", "split_sum(&[i64::MIN + 5, -5])", "i64::MIN"),
        T("large_values", "nums = [10¹⁵; 1000]", "split_sum(&vec![1_000_000_000_000_000; 1000])", "1_000_000_000_000_000_000"),
        T("empty_again", "nums = []", "split_sum(&[])", "0"),
        """
        #[test]
        fn random_vs_loop() {
            let mut rng = anneal_prelude::Rng::new(1107);
            for _ in 0..300 {
                let n = rng.below(40);
                let nums: Vec<i64> = rng.vec(n, -1_000_000_000, 1_000_000_000);
                let mut want = 0;
                for &x in &nums {
                    want += x;
                }
                check!(format!("nums = {nums:?}"), split_sum(&nums), want);
            }
        }

        #[test]
        fn scale_200k() {
            let nums: Vec<i64> = (1..=200_000).collect();
            check!("nums = 1..=200000", split_sum(&nums), 20_000_100_000);
        }
        """,
    ],
    wrong=dict(
        single_counts_as_zero="""
            /// The sum of `nums`, computed by summing each half.
            pub fn split_sum(nums: &[i64]) -> i64 {
                if nums.len() <= 1 {
                    return 0;
                }
                let (left, right) = nums.split_at(nums.len() / 2);
                split_sum(left) + split_sum(right)
            }
        """,
        lost_the_empty_case="""
            /// The sum of `nums`, computed by summing each half.
            pub fn split_sum(nums: &[i64]) -> i64 {
                if nums.len() == 1 {
                    return nums[0];
                }
                let (left, right) = nums.split_at(nums.len() / 2);
                split_sum(left) + split_sum(right)
            }
        """,
    ),
    hints=[("approach", "Trace `split_sum(&[5])`: what are `left` and `right`, and which call is the same as the one you started with?"),
           ("rust", "A one-element slice needs its own base case: `if nums.len() == 1 { return nums[0]; }`."),
           ("edge case", "Keep the empty-slice case too, or `split_sum(&[])` recurses forever.")],
    notes=("`split_at(len / 2)` of a one-element slice is `([], [x])`, so the right-hand call gets the same slice back and never "
           "reaches a base case. With both base cases every call gets a strictly shorter slice, and the depth is log₂ n.",
           "O(n)", "O(log n) recursion depth"),
    follow_up="Rust doesn't guarantee tail-call elimination. When would you turn a recursion like this into a loop?",
    related=["S3", "D12"],
))

STAGES = [
    ("recursion", "Recursion", "easy"),
]

if __name__ == "__main__":
    n = write_track("d11-recursion-backtracking", "D11", "Recursion & backtracking", "D", "core", 12,
                    "Recursion first (base cases, trusting the call, divide and conquer), then backtracking: choose, recurse, undo, and prune.",
                    STAGES, P)
    print("D11", n)
