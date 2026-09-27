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
        ends_on_the_spare_for_even_n="""
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

# ---------------------------------------------------------------------------------------------------------------------
# Stage 2 · First backtracking (easy): push, recurse, pop on a `&mut Vec`.
# ---------------------------------------------------------------------------------------------------------------------

# Answers in any order: sort inside each group, then the groups.
NORM = """
fn norm<T: Ord>(mut groups: Vec<Vec<T>>) -> Vec<Vec<T>> {
    for g in &mut groups {
        g.sort();
    }
    groups.sort();
    groups
}
"""

# Answers in any order, keeping each group's own order.
SORTED = """
fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}
"""

P.append(dict(
    slug="subsets", title="Subsets", level="easy", stage="first-backtracking", tags=["backtracking", "Vec"],
    companies=["Meta", "Amazon", "Google", "Apple", "Microsoft", "Bloomberg", "Uber"],
    teaches=["Backtracking in its smallest form: for each value, leave it out, then take it.",
             "One `&mut Vec` path shared by every call: push, recurse, pop; clone it only when you record an answer."],
    statement="""
        `nums` holds distinct integers. Return every subset of `nums`: all `2^n` of them, including the empty one and
        `nums` itself.

        The subsets can come in any order, and so can the values inside each subset.
    """,
    examples=[("nums = [1, 2, 3]", "[[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]"), ("nums = [0]", "[[], [0]]")],
    constraints=["0 ≤ nums.len() ≤ 18", "the values are distinct"],
    starter="""
        pub fn subsets(nums: &[i32]) -> Vec<Vec<i32>> {
            todo!()
        }
    """,
    solution="""
        pub fn subsets(nums: &[i32]) -> Vec<Vec<i32>> {
            fn go(nums: &[i32], path: &mut Vec<i32>, out: &mut Vec<Vec<i32>>) {
                let Some((&first, rest)) = nums.split_first() else {
                    out.push(path.clone());
                    return;
                };
                go(rest, path, out); // leave `first` out
                path.push(first);
                go(rest, path, out); // take it
                path.pop();
            }
            let mut out = Vec::with_capacity(1 << nums.len());
            go(nums, &mut Vec::new(), &mut out);
            out
        }
    """,
    visible=[
        NORM,
        T("leetcode_three", "nums = [1, 2, 3]", "norm(subsets(&[1, 2, 3]))", "norm(vec![vec![], vec![1], vec![2], vec![1, 2], vec![3], vec![1, 3], vec![2, 3], vec![1, 2, 3]])"),
        T("leetcode_single", "nums = [0]", "norm(subsets(&[0]))", "vec![vec![], vec![0]]"),
        T("empty_has_one_subset", "nums = []", "subsets(&[])", "vec![Vec::<i32>::new()]"),
        T("negatives", "nums = [-1, 2]", "norm(subsets(&[-1, 2]))", "vec![vec![], vec![-1], vec![-1, 2], vec![2]]"),
        T("five_values_give_32", "nums = [1, 2, 3, 4, 5]", "subsets(&[1, 2, 3, 4, 5]).len()", "32"),
    ],
    hidden=[
        NORM,
        T("empty", "nums = []", "subsets(&[])", "vec![Vec::<i32>::new()]"),
        T("single_negative", "nums = [-7]", "norm(subsets(&[-7]))", "vec![vec![], vec![-7]]"),
        T("two", "nums = [5, 3]", "norm(subsets(&[5, 3]))", "vec![vec![], vec![3], vec![3, 5], vec![5]]"),
        T("not_contiguous_only", "nums = [1, 2, 3]: [1, 3] is a subset", "subsets(&[1, 2, 3]).into_iter().any(|mut s| { s.sort(); s == vec![1, 3] })", "true"),
        T("ten_values", "nums = 0..10", "subsets(&(0..10).collect::<Vec<i32>>()).len()", "1024"),
        T("extremes", "nums = [i32::MIN, i32::MAX]", "norm(subsets(&[i32::MIN, i32::MAX]))", "vec![vec![], vec![i32::MIN], vec![i32::MIN, i32::MAX], vec![i32::MAX]]"),
        T("no_duplicate_subsets", "nums = [4, 1, 3, 2]", "{ let mut s = norm(subsets(&[4, 1, 3, 2])); s.dedup(); s.len() }", "16"),
        T("unsorted_input", "nums = [3, 1, 2]", "norm(subsets(&[3, 1, 2]))", "norm(vec![vec![], vec![1], vec![2], vec![1, 2], vec![3], vec![1, 3], vec![2, 3], vec![1, 2, 3]])"),
        """
        #[test]
        fn random_vs_bitmasks() {
            let mut rng = anneal_prelude::Rng::new(1111);
            for _ in 0..200 {
                let n = rng.below(9);
                let mut nums: Vec<i32> = (-10..10).collect();
                rng.shuffle(&mut nums);
                nums.truncate(n);
                let want: Vec<Vec<i32>> = (0..1u32 << n).map(|mask| (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| nums[i]).collect()).collect();
                check!(format!("nums = {nums:?}"), norm(subsets(&nums)), norm(want));
            }
        }

        #[test]
        fn scale_18_values() {
            let nums: Vec<i32> = (0..18).collect();
            let mut all = norm(subsets(&nums));
            let total: usize = all.iter().map(Vec::len).sum();
            all.dedup();
            check!("nums = 0..18", (all.len(), total), (1 << 18, 18 << 17));
        }
        """,
    ],
    wrong=dict(
        misses_the_empty_subset="""
            pub fn subsets(nums: &[i32]) -> Vec<Vec<i32>> {
                fn go(nums: &[i32], start: usize, path: &mut Vec<i32>, out: &mut Vec<Vec<i32>>) {
                    for i in start..nums.len() {
                        path.push(nums[i]);
                        out.push(path.clone());
                        go(nums, i + 1, path, out);
                        path.pop();
                    }
                }
                let mut out = Vec::new();
                go(nums, 0, &mut Vec::new(), &mut out);
                out
            }
        """,
        contiguous_only="""
            pub fn subsets(nums: &[i32]) -> Vec<Vec<i32>> {
                let mut out = vec![Vec::new()];
                for i in 0..nums.len() {
                    for j in i + 1..=nums.len() {
                        out.push(nums[i..j].to_vec());
                    }
                }
                out
            }
        """,
    ),
    hints=[("approach", "Each value is either in or out. Recurse on the rest of the slice twice: once without it, once with it."),
           ("rust", "`nums.split_first()` gives `Some((&first, rest))` or `None` at the end; record `path.clone()` there."),
           ("edge case", "The empty set is a subset, so `subsets(&[])` returns `[[]]`, not `[]`.")],
    notes=("The recursion is a binary tree of depth n with 2ⁿ leaves, one per subset. The path is pushed and popped in place, "
           "so the only copies are the answers themselves.", "O(n · 2ⁿ)", "O(n) besides the output"),
    follow_up="Generate the subsets with a bitmask loop instead. When is the recursive version easier to adapt?",
    related=["D12"],
))

P.append(dict(
    slug="combinations", title="Combinations", level="easy", stage="first-backtracking", tags=["backtracking", "pruning"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "Bloomberg"],
    teaches=["Choose values in increasing order so every combination is built exactly once.",
             "First pruning: stop when too few values are left to fill the combination."],
    statement="""
        Return every way to choose `k` distinct numbers from `1..=n`. A combination is a set, so `[1, 2]` and `[2, 1]`
        are the same one and only one of them may appear.

        The combinations can come in any order, and so can the numbers inside each one.
    """,
    examples=[("n = 4, k = 2", "[[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]"), ("n = 1, k = 1", "[[1]]")],
    constraints=["1 ≤ n ≤ 30", "0 ≤ k ≤ n", "the answer has at most 2·10⁵ combinations"],
    starter="""
        pub fn combine(n: u32, k: u32) -> Vec<Vec<u32>> {
            todo!()
        }
    """,
    solution="""
        pub fn combine(n: u32, k: u32) -> Vec<Vec<u32>> {
            fn go(next: u32, n: u32, k: usize, path: &mut Vec<u32>, out: &mut Vec<Vec<u32>>) {
                if path.len() == k {
                    out.push(path.clone());
                    return;
                }
                // Leave room for the values still needed: the last start that can work is n - need + 1.
                let need = (k - path.len()) as u32;
                for x in next..=n + 1 - need {
                    path.push(x);
                    go(x + 1, n, k, path, out);
                    path.pop();
                }
            }
            let mut out = Vec::new();
            go(1, n, k as usize, &mut Vec::with_capacity(k as usize), &mut out);
            out
        }
    """,
    visible=[
        NORM,
        T("leetcode_four_choose_two", "n = 4, k = 2", "norm(combine(4, 2))", "vec![vec![1, 2], vec![1, 3], vec![1, 4], vec![2, 3], vec![2, 4], vec![3, 4]]"),
        T("leetcode_one_choose_one", "n = 1, k = 1", "combine(1, 1)", "vec![vec![1]]"),
        T("choose_zero", "n = 3, k = 0", "combine(3, 0)", "vec![Vec::<u32>::new()]"),
        T("choose_all", "n = 3, k = 3", "norm(combine(3, 3))", "vec![vec![1, 2, 3]]"),
        T("no_repeats_no_reorders", "n = 3, k = 2", "norm(combine(3, 2))", "vec![vec![1, 2], vec![1, 3], vec![2, 3]]"),
    ],
    hidden=[
        NORM,
        T("choose_one", "n = 4, k = 1", "norm(combine(4, 1))", "vec![vec![1], vec![2], vec![3], vec![4]]"),
        T("one_choose_zero", "n = 1, k = 0", "combine(1, 0)", "vec![Vec::<u32>::new()]"),
        T("five_choose_three", "n = 5, k = 3", "combine(5, 3).len()", "10"),
        T("ten_choose_five", "n = 10, k = 5", "combine(10, 5).len()", "252"),
        T("values_start_at_one", "n = 2, k = 2", "combine(2, 2)", "vec![vec![1, 2]]"),
        T("n_minus_one", "n = 5, k = 4", "norm(combine(5, 4))", "vec![vec![1, 2, 3, 4], vec![1, 2, 3, 5], vec![1, 2, 4, 5], vec![1, 3, 4, 5], vec![2, 3, 4, 5]]"),
        T("twenty_choose_ten", "n = 20, k = 10", "combine(20, 10).len()", "184_756"),
        T("thirty_choose_thirty", "n = 30, k = 30", "combine(30, 30)", "vec![(1..=30).collect::<Vec<u32>>()]"),
        """
        #[test]
        fn random_vs_bitmasks() {
            let mut rng = anneal_prelude::Rng::new(1112);
            for _ in 0..200 {
                let n = rng.int(1, 10) as u32;
                let k = rng.int(0, n as i64) as u32;
                let want: Vec<Vec<u32>> = (0..1u32 << n)
                    .filter(|m| m.count_ones() == k)
                    .map(|m| (0..n).filter(|&i| m >> i & 1 == 1).map(|i| i + 1).collect())
                    .collect();
                check!(format!("n = {n}, k = {k}"), norm(combine(n, k)), norm(want));
            }
        }

        #[test]
        fn scale_prune_when_too_few_remain() {
            let got = norm(combine(30, 28));
            check!("n = 30, k = 28", (got.len(), got[0].clone(), got[434].clone()), (435, (1..=28).collect::<Vec<u32>>(), (3..=30).collect::<Vec<u32>>()));
            check!("n = 29, k = 27", combine(29, 27).len(), 406);
        }
        """,
    ],
    wrong=dict(
        no_pruning="""
            pub fn combine(n: u32, k: u32) -> Vec<Vec<u32>> {
                fn go(next: u32, n: u32, k: usize, path: &mut Vec<u32>, out: &mut Vec<Vec<u32>>) {
                    if path.len() == k {
                        out.push(path.clone());
                        return;
                    }
                    for x in next..=n {
                        path.push(x);
                        go(x + 1, n, k, path, out);
                        path.pop();
                    }
                }
                let mut out = Vec::new();
                go(1, n, k as usize, &mut Vec::new(), &mut out);
                out
            }
        """,
        values_repeat="""
            pub fn combine(n: u32, k: u32) -> Vec<Vec<u32>> {
                fn go(next: u32, n: u32, k: usize, path: &mut Vec<u32>, out: &mut Vec<Vec<u32>>) {
                    if path.len() == k {
                        out.push(path.clone());
                        return;
                    }
                    for x in next..=n {
                        path.push(x);
                        go(x, n, k, path, out);
                        path.pop();
                    }
                }
                let mut out = Vec::new();
                go(1, n, k as usize, &mut Vec::new(), &mut out);
                out
            }
        """,
        zero_based="""
            pub fn combine(n: u32, k: u32) -> Vec<Vec<u32>> {
                fn go(next: u32, n: u32, k: usize, path: &mut Vec<u32>, out: &mut Vec<Vec<u32>>) {
                    if path.len() == k {
                        out.push(path.clone());
                        return;
                    }
                    let need = (k - path.len()) as u32;
                    for x in next..n + 1 - need {
                        path.push(x);
                        go(x + 1, n, k, path, out);
                        path.pop();
                    }
                }
                let mut out = Vec::new();
                go(0, n, k as usize, &mut Vec::new(), &mut out);
                out
            }
        """,
    ),
    hints=[("approach", "Pick the numbers in increasing order: after choosing x, the next pick starts at x + 1."),
           ("rust", "`fn go(next: u32, n: u32, k: usize, path: &mut Vec<u32>, out: &mut Vec<Vec<u32>>)`; record when `path.len() == k`."),
           ("edge case", "If only `need` more values are missing, starting past `n - need + 1` can never finish. Stop the loop there.")],
    notes=("Increasing order makes each combination appear once. The loop bound `n + 1 - need` cuts every branch that can't "
           "reach k values, so the work is proportional to the answer instead of to all 2ⁿ subsets.",
           "O(k · C(n, k))", "O(k) besides the output"),
    follow_up="Without the pruning, how many calls does `combine(30, 28)` make, and how many answers does it produce?",
    related=["D12"],
))

P.append(dict(
    slug="letter-combinations", title="Letter combinations of a phone number", level="easy", stage="first-backtracking",
    tags=["backtracking", "String", "Blind 75"],
    companies=["Meta", "Amazon", "Google", "Apple", "Microsoft", "Uber", "Bloomberg"],
    teaches=["One recursion level per digit, one branch per letter on that key.",
             "Build the answer in a single `String` with `push` and `pop`."],
    statement="""
        On a phone keypad, 2 is `abc`, 3 `def`, 4 `ghi`, 5 `jkl`, 6 `mno`, 7 `pqrs`, 8 `tuv` and 9 `wxyz`. Return every
        string you can spell by pressing the digits in `digits` in order, one letter per digit.

        An empty `digits` spells nothing: return an empty list. The strings can come in any order.
    """,
    examples=[("digits = \"23\"", "[\"ad\", \"ae\", \"af\", \"bd\", \"be\", \"bf\", \"cd\", \"ce\", \"cf\"]"), ("digits = \"\"", "[]")],
    constraints=["0 ≤ digits.len() ≤ 8", "digits holds only '2' to '9'"],
    starter="""
        pub fn letter_combinations(digits: &str) -> Vec<String> {
            todo!()
        }
    """,
    solution="""
        const KEYS: [&str; 10] = ["", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"];

        pub fn letter_combinations(digits: &str) -> Vec<String> {
            fn go(digits: &[u8], word: &mut String, out: &mut Vec<String>) {
                let Some((&d, rest)) = digits.split_first() else {
                    out.push(word.clone());
                    return;
                };
                for c in KEYS[(d - b'0') as usize].chars() {
                    word.push(c);
                    go(rest, word, out);
                    word.pop();
                }
            }
            let mut out = Vec::new();
            if !digits.is_empty() {
                go(digits.as_bytes(), &mut String::with_capacity(digits.len()), &mut out);
            }
            out
        }
    """,
    visible=[
        SORTED,
        T("leetcode_two_three", "digits = \"23\"", "sorted(letter_combinations(\"23\"))", "vec![\"ad\", \"ae\", \"af\", \"bd\", \"be\", \"bf\", \"cd\", \"ce\", \"cf\"]"),
        T("leetcode_empty", "digits = \"\"", "letter_combinations(\"\")", "Vec::<String>::new()"),
        T("leetcode_single", "digits = \"2\"", "sorted(letter_combinations(\"2\"))", "vec![\"a\", \"b\", \"c\"]"),
        T("seven_has_four_letters", "digits = \"7\"", "sorted(letter_combinations(\"7\"))", "vec![\"p\", \"q\", \"r\", \"s\"]"),
        T("repeated_digit", "digits = \"22\"", "sorted(letter_combinations(\"22\"))", "vec![\"aa\", \"ab\", \"ac\", \"ba\", \"bb\", \"bc\", \"ca\", \"cb\", \"cc\"]"),
    ],
    hidden=[
        SORTED,
        T("empty", "digits = \"\"", "letter_combinations(\"\")", "Vec::<String>::new()"),
        T("nine_has_four_letters", "digits = \"9\"", "sorted(letter_combinations(\"9\"))", "vec![\"w\", \"x\", \"y\", \"z\"]"),
        T("eight", "digits = \"8\"", "sorted(letter_combinations(\"8\"))", "vec![\"t\", \"u\", \"v\"]"),
        T("three_digits", "digits = \"234\"", "letter_combinations(\"234\").len()", "27"),
        T("seven_nine", "digits = \"79\"", "letter_combinations(\"79\").len()", "16"),
        T("order_of_digits_kept", "digits = \"32\"", "sorted(letter_combinations(\"32\"))", "vec![\"da\", \"db\", \"dc\", \"ea\", \"eb\", \"ec\", \"fa\", \"fb\", \"fc\"]"),
        T("four_four_letter_keys", "digits = \"7979\"", "letter_combinations(\"7979\").len()", "256"),
        T("every_key_once", "digits = \"23456789\"", "letter_combinations(\"23456789\").len()", "11_664"),
        T("five_six", "digits = \"56\"", "sorted(letter_combinations(\"56\"))", "vec![\"jm\", \"jn\", \"jo\", \"km\", \"kn\", \"ko\", \"lm\", \"ln\", \"lo\"]"),
        """
        #[test]
        fn random_vs_product() {
            let keys = ["", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"];
            let mut rng = anneal_prelude::Rng::new(1113);
            for _ in 0..200 {
                let len = rng.int(1, 5) as usize;
                let digits = rng.string(len, "23456789");
                let mut want = vec![String::new()];
                for d in digits.bytes() {
                    want = want.iter().flat_map(|w| keys[(d - b'0') as usize].chars().map(move |c| format!("{w}{c}"))).collect();
                }
                want.sort();
                check!(format!("digits = {digits:?}"), sorted(letter_combinations(&digits)), want);
            }
        }

        #[test]
        fn scale_eight_four_letter_keys() {
            let got = sorted(letter_combinations("79797979"));
            check!("digits = \\"79797979\\"", (got.len(), got[0].clone(), got[65_535].clone()), (65_536, "pwpwpwpw".to_string(), "szszszsz".to_string()));
        }
        """,
    ],
    wrong=dict(
        empty_gives_one_empty_string="""
            const KEYS: [&str; 10] = ["", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"];

            pub fn letter_combinations(digits: &str) -> Vec<String> {
                let mut out = vec![String::new()];
                for d in digits.bytes() {
                    out = out.iter().flat_map(|w| KEYS[(d - b'0') as usize].chars().map(move |c| format!("{w}{c}"))).collect();
                }
                out
            }
        """,
        three_letters_per_key="""
            pub fn letter_combinations(digits: &str) -> Vec<String> {
                fn go(digits: &[u8], word: &mut String, out: &mut Vec<String>) {
                    let Some((&d, rest)) = digits.split_first() else {
                        out.push(word.clone());
                        return;
                    };
                    let first = b'a' + 3 * (d - b'2');
                    for c in first..first + 3 {
                        word.push(c as char);
                        go(rest, word, out);
                        word.pop();
                    }
                }
                let mut out = Vec::new();
                if !digits.is_empty() {
                    go(digits.as_bytes(), &mut String::new(), &mut out);
                }
                out
            }
        """,
    ),
    hints=[("approach", "Recurse over the digits. At each digit try every letter on its key, then move to the next digit."),
           ("rust", "A `const KEYS: [&str; 10]` indexed by `(d - b'0') as usize`; keep one `String` and `push`/`pop` a char per level."),
           ("edge case", "7 and 9 have four letters. An empty input gives `[]`, not `[\"\"]`.")],
    notes=("The recursion has one level per digit and branches 3 or 4 ways, so it produces each string once and copies the "
           "buffer only at the leaves.", "O(4ⁿ · n)", "O(n) besides the output"),
    follow_up="Write it iteratively by extending a list of prefixes one digit at a time. Which uses less peak memory?",
    related=["S2"],
))

P.append(dict(
    slug="binary-watch", title="Binary watch", level="easy", stage="first-backtracking", tags=["backtracking", "bits", "format!"],
    companies=["Google", "Amazon"],
    teaches=["Choose which LEDs are on, pruning as soon as the hour or minute is out of range.",
             "`format!(\"{h}:{m:02}\")` pads the minutes to two digits."],
    statement="""
        A binary watch shows the hour (0–11) on 4 LEDs worth 8, 4, 2, 1 and the minute (0–59) on 6 LEDs worth
        32, 16, 8, 4, 2, 1. Given how many LEDs are on, return every time the watch could show.

        Write each time as `h:mm`: the hour without a leading zero, the minute always with two digits (`"1:05"`, not
        `"01:5"`). The times can come in any order.
    """,
    examples=[("turned_on = 1", "[\"0:01\", \"0:02\", \"0:04\", \"0:08\", \"0:16\", \"0:32\", \"1:00\", \"2:00\", \"4:00\", \"8:00\"]"), ("turned_on = 9", "[]")],
    constraints=["0 ≤ turned_on ≤ 10"],
    starter="""
        pub fn read_binary_watch(turned_on: u32) -> Vec<String> {
            todo!()
        }
    """,
    solution="""
        pub fn read_binary_watch(turned_on: u32) -> Vec<String> {
            // LEDs 0..4 are the hour bits 8, 4, 2, 1; LEDs 4..10 are the minute bits 32 … 1.
            fn go(led: u32, left: u32, hour: u32, minute: u32, out: &mut Vec<String>) {
                if hour > 11 || minute > 59 {
                    return;
                }
                if left == 0 {
                    out.push(format!("{hour}:{minute:02}"));
                    return;
                }
                if led == 10 {
                    return;
                }
                let (h, m) = if led < 4 { (8 >> led, 0) } else { (0, 32 >> (led - 4)) };
                go(led + 1, left - 1, hour + h, minute + m, out); // this LED on
                go(led + 1, left, hour, minute, out); // this LED off
            }
            let mut out = Vec::new();
            go(0, turned_on, 0, 0, &mut out);
            out
        }
    """,
    visible=[
        SORTED,
        T("leetcode_one_led", "turned_on = 1", "sorted(read_binary_watch(1))", "vec![\"0:01\", \"0:02\", \"0:04\", \"0:08\", \"0:16\", \"0:32\", \"1:00\", \"2:00\", \"4:00\", \"8:00\"]"),
        T("leetcode_nine_leds", "turned_on = 9", "read_binary_watch(9)", "Vec::<String>::new()"),
        T("zero_leds", "turned_on = 0", "read_binary_watch(0)", "vec![\"0:00\"]"),
        T("eight_leds", "turned_on = 8", "sorted(read_binary_watch(8))", "vec![\"11:31\", \"11:47\", \"11:55\", \"11:59\", \"7:31\", \"7:47\", \"7:55\", \"7:59\"]"),
        T("two_leds_count", "turned_on = 2", "read_binary_watch(2).len()", "44"),
    ],
    hidden=[
        SORTED,
        T("ten_leds", "turned_on = 10", "read_binary_watch(10)", "Vec::<String>::new()"),
        T("three_leds", "turned_on = 3", "read_binary_watch(3).len()", "112"),
        T("four_leds", "turned_on = 4", "read_binary_watch(4).len()", "181"),
        T("five_leds", "turned_on = 5", "read_binary_watch(5).len()", "190"),
        T("six_leds", "turned_on = 6", "read_binary_watch(6).len()", "126"),
        T("seven_leds", "turned_on = 7", "read_binary_watch(7).len()", "48"),
        T("minutes_padded", "turned_on = 1: \"0:01\" is there", "read_binary_watch(1).contains(&\"0:01\".to_string())", "true"),
        T("no_hour_twelve", "turned_on = 2: \"12:00\" is not a time", "read_binary_watch(2).contains(&\"12:00\".to_string())", "false"),
        T("no_minute_sixty", "turned_on = 4: \"0:60\" is not a time", "read_binary_watch(4).contains(&\"0:60\".to_string())", "false"),
        """
        #[test]
        fn every_count_vs_clock_scan() {
            for on in 0..=10u32 {
                let mut want = Vec::new();
                for h in 0..12u32 {
                    for m in 0..60u32 {
                        if h.count_ones() + m.count_ones() == on {
                            want.push(format!("{h}:{m:02}"));
                        }
                    }
                }
                want.sort();
                check!(format!("turned_on = {on}"), sorted(read_binary_watch(on)), want);
            }
        }
        """,
    ],
    wrong=dict(
        minutes_not_padded="""
            pub fn read_binary_watch(turned_on: u32) -> Vec<String> {
                let mut out = Vec::new();
                for h in 0..12u32 {
                    for m in 0..60u32 {
                        if h.count_ones() + m.count_ones() == turned_on {
                            out.push(format!("{h}:{m}"));
                        }
                    }
                }
                out
            }
        """,
        hour_twelve_allowed="""
            pub fn read_binary_watch(turned_on: u32) -> Vec<String> {
                let mut out = Vec::new();
                for h in 0..=12u32 {
                    for m in 0..60u32 {
                        if h.count_ones() + m.count_ones() == turned_on {
                            out.push(format!("{h}:{m:02}"));
                        }
                    }
                }
                out
            }
        """,
    ),
    hints=[("approach", "Walk the 10 LEDs; for each, try it on (if you still have LEDs to spend) and off. Stop a branch once the hour passes 11 or the minute passes 59."),
           ("rust", "`format!(\"{hour}:{minute:02}\")` gives `0:05`. A plain loop over all 720 times with `count_ones` is a good check."),
           ("edge case", "Hours stop at 11 and minutes at 59, so 9 or 10 LEDs give no time at all.")],
    notes=("There are only C(10, k) ways to light k LEDs, and the range checks cut the impossible ones early. "
           "Scanning all 720 times and counting bits is just as fast here; the backtracking version is the pattern that scales.",
           "O(C(10, k))", "O(1) besides the output"),
    follow_up="Which version would you pick in an interview, the 720-time scan or the backtracking, and why?",
    related=["S2"],
))

STAGES = [
    ("recursion", "Recursion", "easy"),
    ("first-backtracking", "First backtracking", "easy"),
]

if __name__ == "__main__":
    n = write_track("d11-recursion-backtracking", "D11", "Recursion & backtracking", "D", "core", 12,
                    "Recursion first (base cases, trusting the call, divide and conquer), then backtracking: choose, recurse, undo, and prune.",
                    STAGES, P)
    print("D11", n)
