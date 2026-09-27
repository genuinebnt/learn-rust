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

# ---------------------------------------------------------------------------------------------------------------------
# Stage 3 · Choices & grids (medium): duplicates, reuse, partitions and grids, each with an inner `fn` taking `&mut`.
# ---------------------------------------------------------------------------------------------------------------------

P.append(dict(
    slug="subsets-ii", title="Subsets II", level="medium", stage="choices-grids", tags=["backtracking", "duplicates", "sort"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "Bloomberg"],
    teaches=["Sort first so equal values sit together.",
             "At one depth, only the first of a run of equal values may start a branch: that removes duplicates without a set."],
    statement="""
        `nums` may contain repeated values. Return every distinct subset of `nums`: two subsets that hold the same
        values the same number of times count once.

        The subsets can come in any order, and so can the values inside each subset.
    """,
    examples=[("nums = [1, 2, 2]", "[[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]"), ("nums = [0]", "[[], [0]]")],
    constraints=["0 ≤ nums.len() ≤ 26", "-10 ≤ nums[i] ≤ 10", "the answer has at most 10⁵ subsets"],
    starter="""
        pub fn subsets_with_dup(nums: &[i32]) -> Vec<Vec<i32>> {
            todo!()
        }
    """,
    solution="""
        pub fn subsets_with_dup(nums: &[i32]) -> Vec<Vec<i32>> {
            fn go(nums: &[i32], start: usize, path: &mut Vec<i32>, out: &mut Vec<Vec<i32>>) {
                out.push(path.clone());
                for i in start..nums.len() {
                    // Among equal values, only the first may be chosen at this depth.
                    if i > start && nums[i] == nums[i - 1] {
                        continue;
                    }
                    path.push(nums[i]);
                    go(nums, i + 1, path, out);
                    path.pop();
                }
            }
            let mut sorted = nums.to_vec();
            sorted.sort_unstable();
            let mut out = Vec::new();
            go(&sorted, 0, &mut Vec::new(), &mut out);
            out
        }
    """,
    visible=[
        NORM,
        T("leetcode_one_two_two", "nums = [1, 2, 2]", "norm(subsets_with_dup(&[1, 2, 2]))", "vec![vec![], vec![1], vec![1, 2], vec![1, 2, 2], vec![2], vec![2, 2]]"),
        T("leetcode_single", "nums = [0]", "norm(subsets_with_dup(&[0]))", "vec![vec![], vec![0]]"),
        T("empty", "nums = []", "subsets_with_dup(&[])", "vec![Vec::<i32>::new()]"),
        T("all_equal", "nums = [2, 2, 2]", "norm(subsets_with_dup(&[2, 2, 2]))", "vec![vec![], vec![2], vec![2, 2], vec![2, 2, 2]]"),
        T("duplicates_not_adjacent", "nums = [4, 4, 1, 4]", "norm(subsets_with_dup(&[4, 4, 1, 4]))", "vec![vec![], vec![1], vec![1, 4], vec![1, 4, 4], vec![1, 4, 4, 4], vec![4], vec![4, 4], vec![4, 4, 4]]"),
    ],
    hidden=[
        NORM,
        T("distinct_values", "nums = [1, 2, 3]", "subsets_with_dup(&[1, 2, 3]).len()", "8"),
        T("empty", "nums = []", "subsets_with_dup(&[])", "vec![Vec::<i32>::new()]"),
        T("negatives", "nums = [-1, 2, -1]", "norm(subsets_with_dup(&[-1, 2, -1]))", "vec![vec![], vec![-1], vec![-1, -1], vec![-1, -1, 2], vec![-1, 2], vec![2]]"),
        T("two_equal", "nums = [5, 5]", "norm(subsets_with_dup(&[5, 5]))", "vec![vec![], vec![5], vec![5, 5]]"),
        T("two_pairs", "nums = [3, 1, 3, 1]", "subsets_with_dup(&[3, 1, 3, 1]).len()", "9"),
        T("pair_kept_after_skipping", "nums = [2, 1, 2]: [2, 2] is there", "norm(subsets_with_dup(&[2, 1, 2])).contains(&vec![2, 2])", "true"),
        T("extremes", "nums = [10, -10, 10]", "norm(subsets_with_dup(&[10, -10, 10]))", "vec![vec![], vec![-10], vec![-10, 10], vec![-10, 10, 10], vec![10], vec![10, 10]]"),
        T("ten_distinct", "nums = 0..10", "subsets_with_dup(&(0..10).collect::<Vec<i32>>()).len()", "1024"),
        """
        #[test]
        fn random_vs_bitmasks_and_a_set() {
            let mut rng = anneal_prelude::Rng::new(1121);
            for _ in 0..300 {
                let n = rng.below(10);
                let nums: Vec<i32> = rng.vec(n, -2, 2);
                let mut all = std::collections::BTreeSet::new();
                for mask in 0..1u32 << n {
                    let mut s: Vec<i32> = (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| nums[i]).collect();
                    s.sort();
                    all.insert(s);
                }
                check!(format!("nums = {nums:?}"), norm(subsets_with_dup(&nums)), all.into_iter().collect::<Vec<_>>());
            }
        }

        #[test]
        fn scale_twenty_six_equal() {
            check!("nums = [5; 26]", norm(subsets_with_dup(&vec![5; 26])), (0..=26).map(|k| vec![5; k]).collect::<Vec<_>>());
        }

        #[test]
        fn scale_two_runs_of_thirteen() {
            let mut nums = vec![7; 13];
            nums.extend(vec![3; 13]);
            let got = norm(subsets_with_dup(&nums));
            check!("nums = [7; 13] + [3; 13]", (got.len(), got[195].clone()), (196, vec![7; 13]));
        }
        """,
    ],
    wrong=dict(
        all_subsets_then_a_set="""
            pub fn subsets_with_dup(nums: &[i32]) -> Vec<Vec<i32>> {
                let mut sorted = nums.to_vec();
                sorted.sort();
                let mut seen = std::collections::HashSet::new();
                for mask in 0..1u64 << sorted.len() {
                    let s: Vec<i32> = (0..sorted.len()).filter(|&i| mask >> i & 1 == 1).map(|i| sorted[i]).collect();
                    seen.insert(s);
                }
                seen.into_iter().collect()
            }
        """,
        no_sort_first="""
            pub fn subsets_with_dup(nums: &[i32]) -> Vec<Vec<i32>> {
                fn go(nums: &[i32], start: usize, path: &mut Vec<i32>, out: &mut Vec<Vec<i32>>) {
                    out.push(path.clone());
                    for i in start..nums.len() {
                        if i > start && nums[i] == nums[i - 1] {
                            continue;
                        }
                        path.push(nums[i]);
                        go(nums, i + 1, path, out);
                        path.pop();
                    }
                }
                let mut out = Vec::new();
                go(nums, 0, &mut Vec::new(), &mut out);
                out
            }
        """,
        skips_too_much="""
            pub fn subsets_with_dup(nums: &[i32]) -> Vec<Vec<i32>> {
                fn go(nums: &[i32], start: usize, path: &mut Vec<i32>, out: &mut Vec<Vec<i32>>) {
                    out.push(path.clone());
                    for i in start..nums.len() {
                        if i > 0 && nums[i] == nums[i - 1] {
                            continue;
                        }
                        path.push(nums[i]);
                        go(nums, i + 1, path, out);
                        path.pop();
                    }
                }
                let mut sorted = nums.to_vec();
                sorted.sort_unstable();
                let mut out = Vec::new();
                go(&sorted, 0, &mut Vec::new(), &mut out);
                out
            }
        """,
    ),
    hints=[("approach", "Sort, then build subsets by choosing the next index in increasing order. At each depth, skip a value equal to the one just before it in the loop."),
           ("rust", "The skip is `if i > start && nums[i] == nums[i - 1] { continue; }`: `i > start`, not `i > 0`."),
           ("edge case", "Generating all 2ⁿ subsets and deduplicating with a set is far too slow for `[5; 26]`, which has only 27 answers.")],
    notes=("After sorting, a run of equal values only matters by how many of them you take. Letting only the first of a run start "
           "a branch at each depth builds each count once, so the work is proportional to the answer.",
           "O(n · answer)", "O(n) besides the output"),
    follow_up="Count the distinct subsets without listing them. What does each run of equal values contribute?",
    related=["D12", "S4"],
))

P.append(dict(
    slug="permutations", title="Permutations", level="medium", stage="choices-grids", tags=["backtracking", "Blind 75"],
    companies=["Meta", "Amazon", "Google", "Apple", "Microsoft", "LinkedIn", "Bloomberg"],
    teaches=["A `used` flag per index says which values the current path already holds.",
             "Undo both the push and the flag on the way back up."],
    statement="""
        `nums` holds distinct integers. Return every ordering (permutation) of `nums`.

        The permutations can come in any order; inside each one the order is, of course, what matters.
    """,
    examples=[("nums = [1, 2, 3]", "[[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]"), ("nums = [0, 1]", "[[0, 1], [1, 0]]")],
    constraints=["0 ≤ nums.len() ≤ 8", "the values are distinct"],
    starter="""
        pub fn permute(nums: &[i32]) -> Vec<Vec<i32>> {
            todo!()
        }
    """,
    solution="""
        pub fn permute(nums: &[i32]) -> Vec<Vec<i32>> {
            fn go(nums: &[i32], used: &mut [bool], path: &mut Vec<i32>, out: &mut Vec<Vec<i32>>) {
                if path.len() == nums.len() {
                    out.push(path.clone());
                    return;
                }
                for i in 0..nums.len() {
                    if used[i] {
                        continue;
                    }
                    used[i] = true;
                    path.push(nums[i]);
                    go(nums, used, path, out);
                    path.pop();
                    used[i] = false;
                }
            }
            let mut out = Vec::new();
            go(nums, &mut vec![false; nums.len()], &mut Vec::with_capacity(nums.len()), &mut out);
            out
        }
    """,
    visible=[
        SORTED,
        T("leetcode_three", "nums = [1, 2, 3]", "sorted(permute(&[1, 2, 3]))", "vec![vec![1, 2, 3], vec![1, 3, 2], vec![2, 1, 3], vec![2, 3, 1], vec![3, 1, 2], vec![3, 2, 1]]"),
        T("leetcode_two", "nums = [0, 1]", "sorted(permute(&[0, 1]))", "vec![vec![0, 1], vec![1, 0]]"),
        T("leetcode_single", "nums = [1]", "permute(&[1])", "vec![vec![1]]"),
        T("empty_has_one_ordering", "nums = []", "permute(&[])", "vec![Vec::<i32>::new()]"),
        T("five_values_give_120", "nums = [1, 2, 3, 4, 5]", "permute(&[1, 2, 3, 4, 5]).len()", "120"),
    ],
    hidden=[
        SORTED,
        T("empty", "nums = []", "permute(&[])", "vec![Vec::<i32>::new()]"),
        T("negatives", "nums = [-1, -2]", "sorted(permute(&[-1, -2]))", "vec![vec![-2, -1], vec![-1, -2]]"),
        T("unsorted_input", "nums = [3, 1, 2]", "sorted(permute(&[3, 1, 2]))", "vec![vec![1, 2, 3], vec![1, 3, 2], vec![2, 1, 3], vec![2, 3, 1], vec![3, 1, 2], vec![3, 2, 1]]"),
        T("extremes", "nums = [i32::MAX, i32::MIN]", "sorted(permute(&[i32::MAX, i32::MIN]))", "vec![vec![i32::MIN, i32::MAX], vec![i32::MAX, i32::MIN]]"),
        T("four_distinct", "nums = [4, 3, 2, 1]", "{ let mut p = sorted(permute(&[4, 3, 2, 1])); p.dedup(); p.len() }", "24"),
        T("each_is_a_rearrangement", "nums = [5, 6, 7, 8]", "permute(&[5, 6, 7, 8]).into_iter().all(|mut p| { p.sort(); p == vec![5, 6, 7, 8] })", "true"),
        T("six_values", "nums = [1, 2, 3, 4, 5, 6]", "permute(&[1, 2, 3, 4, 5, 6]).len()", "720"),
        T("zero_and_negatives", "nums = [0, -1, 1]", "sorted(permute(&[0, -1, 1]))", "vec![vec![-1, 0, 1], vec![-1, 1, 0], vec![0, -1, 1], vec![0, 1, -1], vec![1, -1, 0], vec![1, 0, -1]]"),
        """
        /// Every ordering of `v` in lexicographic order, by repeated next-permutation steps.
        fn lexicographic(mut v: Vec<i32>) -> Vec<Vec<i32>> {
            v.sort();
            let mut out = vec![v.clone()];
            loop {
                let Some(i) = (1..v.len()).rev().find(|&i| v[i - 1] < v[i]) else { return out };
                let j = (i..v.len()).rev().find(|&j| v[j] > v[i - 1]).unwrap();
                v.swap(i - 1, j);
                v[i..].reverse();
                out.push(v.clone());
            }
        }

        #[test]
        fn random_vs_next_permutation() {
            let mut rng = anneal_prelude::Rng::new(1122);
            for _ in 0..200 {
                let n = rng.below(7);
                let mut nums: Vec<i32> = (-5..5).collect();
                rng.shuffle(&mut nums);
                nums.truncate(n);
                check!(format!("nums = {nums:?}"), sorted(permute(&nums)), lexicographic(nums.clone()));
            }
        }

        #[test]
        fn scale_eight_values() {
            let nums = vec![8, 1, 7, 2, 6, 3, 5, 4];
            check!("nums = [8, 1, 7, 2, 6, 3, 5, 4]", sorted(permute(&nums)) == lexicographic(nums.clone()), true);
        }
        """,
    ],
    wrong=dict(
        swaps_not_undone="""
            pub fn permute(nums: &[i32]) -> Vec<Vec<i32>> {
                fn go(v: &mut Vec<i32>, k: usize, out: &mut Vec<Vec<i32>>) {
                    if k == v.len() {
                        out.push(v.clone());
                        return;
                    }
                    for i in k..v.len() {
                        v.swap(k, i);
                        go(v, k + 1, out);
                    }
                }
                let mut out = Vec::new();
                go(&mut nums.to_vec(), 0, &mut out);
                out
            }
        """,
        no_used_check="""
            pub fn permute(nums: &[i32]) -> Vec<Vec<i32>> {
                fn go(nums: &[i32], path: &mut Vec<i32>, out: &mut Vec<Vec<i32>>) {
                    if path.len() == nums.len() {
                        out.push(path.clone());
                        return;
                    }
                    for &x in nums {
                        path.push(x);
                        go(nums, path, out);
                        path.pop();
                    }
                }
                let mut out = Vec::new();
                go(nums, &mut Vec::new(), &mut out);
                out
            }
        """,
    ),
    hints=[("approach", "Build the permutation one position at a time; any value not used yet can go next."),
           ("rust", "Pass `used: &mut [bool]` and `path: &mut Vec<i32>` to an inner `fn`; set and clear `used[i]` around the recursive call."),
           ("edge case", "If you swap values into place instead, swap them back after the call, or later branches see a scrambled slice.")],
    notes=("The tree has n choices at the first level, n − 1 at the next, and so on: n! leaves, each copied once into the answer.",
           "O(n · n!)", "O(n) besides the output"),
    follow_up="How does the in-place swap version work, and what does it save over the `used` array?",
    related=["D12"],
))

P.append(dict(
    slug="permutations-ii", title="Permutations II", level="medium", stage="choices-grids", tags=["backtracking", "duplicates"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "LinkedIn", "Bloomberg"],
    teaches=["Sort, then treat equal values as interchangeable: use them left to right only.",
             "Skip `nums[i]` when it equals `nums[i - 1]` and `nums[i - 1]` is not in the current path."],
    statement="""
        `nums` may contain repeated values. Return every distinct ordering of `nums`: orderings that read the same count
        once.

        The permutations can come in any order.
    """,
    examples=[("nums = [1, 1, 2]", "[[1, 1, 2], [1, 2, 1], [2, 1, 1]]"), ("nums = [1, 2, 3]", "all 6 orderings")],
    constraints=["0 ≤ nums.len() ≤ 11", "-10 ≤ nums[i] ≤ 10", "the answer has at most 10⁵ permutations"],
    starter="""
        pub fn permute_unique(nums: &[i32]) -> Vec<Vec<i32>> {
            todo!()
        }
    """,
    solution="""
        pub fn permute_unique(nums: &[i32]) -> Vec<Vec<i32>> {
            fn go(nums: &[i32], used: &mut [bool], path: &mut Vec<i32>, out: &mut Vec<Vec<i32>>) {
                if path.len() == nums.len() {
                    out.push(path.clone());
                    return;
                }
                for i in 0..nums.len() {
                    // Equal values are placed left to right: a copy can't go before the one to its left.
                    if used[i] || (i > 0 && nums[i] == nums[i - 1] && !used[i - 1]) {
                        continue;
                    }
                    used[i] = true;
                    path.push(nums[i]);
                    go(nums, used, path, out);
                    path.pop();
                    used[i] = false;
                }
            }
            let mut sorted = nums.to_vec();
            sorted.sort_unstable();
            let mut out = Vec::new();
            go(&sorted, &mut vec![false; sorted.len()], &mut Vec::with_capacity(sorted.len()), &mut out);
            out
        }
    """,
    visible=[
        SORTED,
        T("leetcode_one_one_two", "nums = [1, 1, 2]", "sorted(permute_unique(&[1, 1, 2]))", "vec![vec![1, 1, 2], vec![1, 2, 1], vec![2, 1, 1]]"),
        T("leetcode_distinct", "nums = [1, 2, 3]", "sorted(permute_unique(&[1, 2, 3]))", "vec![vec![1, 2, 3], vec![1, 3, 2], vec![2, 1, 3], vec![2, 3, 1], vec![3, 1, 2], vec![3, 2, 1]]"),
        T("empty", "nums = []", "permute_unique(&[])", "vec![Vec::<i32>::new()]"),
        T("all_equal", "nums = [2, 2, 2]", "permute_unique(&[2, 2, 2])", "vec![vec![2, 2, 2]]"),
        T("duplicates_not_adjacent", "nums = [3, 1, 3]", "sorted(permute_unique(&[3, 1, 3]))", "vec![vec![1, 3, 3], vec![3, 1, 3], vec![3, 3, 1]]"),
    ],
    hidden=[
        SORTED,
        T("single", "nums = [7]", "permute_unique(&[7])", "vec![vec![7]]"),
        T("two_pairs", "nums = [1, 1, 2, 2]", "sorted(permute_unique(&[1, 1, 2, 2]))", "vec![vec![1, 1, 2, 2], vec![1, 2, 1, 2], vec![1, 2, 2, 1], vec![2, 1, 1, 2], vec![2, 1, 2, 1], vec![2, 2, 1, 1]]"),
        T("two_equal", "nums = [-4, -4]", "permute_unique(&[-4, -4])", "vec![vec![-4, -4]]"),
        T("negatives", "nums = [0, -1, 0]", "sorted(permute_unique(&[0, -1, 0]))", "vec![vec![-1, 0, 0], vec![0, -1, 0], vec![0, 0, -1]]"),
        T("unsorted_pairs", "nums = [2, 1, 2, 1]", "permute_unique(&[2, 1, 2, 1]).len()", "6"),
        T("three_kinds", "nums = [1, 1, 2, 2, 3]", "permute_unique(&[1, 1, 2, 2, 3]).len()", "30"),
        T("six_distinct", "nums = [1, 2, 3, 4, 5, 6]", "permute_unique(&[1, 2, 3, 4, 5, 6]).len()", "720"),
        T("extremes", "nums = [10, -10, 10]", "sorted(permute_unique(&[10, -10, 10]))", "vec![vec![-10, 10, 10], vec![10, -10, 10], vec![10, 10, -10]]"),
        """
        /// Distinct orderings of `v` in lexicographic order; next-permutation skips repeats by itself.
        fn lexicographic(mut v: Vec<i32>) -> Vec<Vec<i32>> {
            v.sort();
            let mut out = vec![v.clone()];
            loop {
                let Some(i) = (1..v.len()).rev().find(|&i| v[i - 1] < v[i]) else { return out };
                let j = (i..v.len()).rev().find(|&j| v[j] > v[i - 1]).unwrap();
                v.swap(i - 1, j);
                v[i..].reverse();
                out.push(v.clone());
            }
        }

        #[test]
        fn random_vs_next_permutation() {
            let mut rng = anneal_prelude::Rng::new(1123);
            for _ in 0..300 {
                let n = rng.below(8);
                let nums: Vec<i32> = rng.vec(n, -2, 2);
                check!(format!("nums = {nums:?}"), sorted(permute_unique(&nums)), lexicographic(nums.clone()));
            }
        }

        #[test]
        fn scale_ten_equal_and_one_other() {
            let mut nums = vec![0; 10];
            nums.push(1);
            check!("nums = [0; 10] + [1]", permute_unique(&nums).len(), 11);
        }

        #[test]
        fn scale_two_runs_of_five() {
            let mut nums = vec![1, 1, 1, 1, 1, 3, 2, 2, 2, 2, 2];
            let got = sorted(permute_unique(&nums));
            nums.sort();
            check!("nums = [1, 1, 1, 1, 1, 3, 2, 2, 2, 2, 2]", (got.len(), got[0].clone()), (2772, nums));
        }
        """,
    ],
    wrong=dict(
        all_orderings_then_a_set="""
            pub fn permute_unique(nums: &[i32]) -> Vec<Vec<i32>> {
                fn go(v: &mut Vec<i32>, k: usize, seen: &mut std::collections::HashSet<Vec<i32>>) {
                    if k == v.len() {
                        seen.insert(v.clone());
                        return;
                    }
                    for i in k..v.len() {
                        v.swap(k, i);
                        go(v, k + 1, seen);
                        v.swap(k, i);
                    }
                }
                let mut seen = std::collections::HashSet::new();
                go(&mut nums.to_vec(), 0, &mut seen);
                seen.into_iter().collect()
            }
        """,
        no_sort_first="""
            pub fn permute_unique(nums: &[i32]) -> Vec<Vec<i32>> {
                fn go(nums: &[i32], used: &mut [bool], path: &mut Vec<i32>, out: &mut Vec<Vec<i32>>) {
                    if path.len() == nums.len() {
                        out.push(path.clone());
                        return;
                    }
                    for i in 0..nums.len() {
                        if used[i] || (i > 0 && nums[i] == nums[i - 1] && !used[i - 1]) {
                            continue;
                        }
                        used[i] = true;
                        path.push(nums[i]);
                        go(nums, used, path, out);
                        path.pop();
                        used[i] = false;
                    }
                }
                let mut out = Vec::new();
                go(nums, &mut vec![false; nums.len()], &mut Vec::new(), &mut out);
                out
            }
        """,
        skips_every_copy="""
            pub fn permute_unique(nums: &[i32]) -> Vec<Vec<i32>> {
                fn go(nums: &[i32], used: &mut [bool], path: &mut Vec<i32>, out: &mut Vec<Vec<i32>>) {
                    if path.len() == nums.len() {
                        out.push(path.clone());
                        return;
                    }
                    for i in 0..nums.len() {
                        if used[i] || (i > 0 && nums[i] == nums[i - 1]) {
                            continue;
                        }
                        used[i] = true;
                        path.push(nums[i]);
                        go(nums, used, path, out);
                        path.pop();
                        used[i] = false;
                    }
                }
                let mut sorted = nums.to_vec();
                sorted.sort_unstable();
                let mut out = Vec::new();
                go(&sorted, &mut vec![false; sorted.len()], &mut Vec::new(), &mut out);
                out
            }
        """,
    ),
    hints=[("approach", "Sort so equal values are neighbours. Then never use a copy while an equal copy to its left is still unused."),
           ("rust", "The skip is `used[i] || (i > 0 && nums[i] == nums[i - 1] && !used[i - 1])`."),
           ("edge case", "Collecting all n! orderings into a set is too slow: `[0; 10] + [1]` has 39,916,800 orderings but only 11 distinct ones.")],
    notes=("Forcing equal values to be used left to right means each distinct ordering is built by exactly one path, "
           "so no set is needed and dead branches are cut before they grow.", "O(n · answer)", "O(n) besides the output"),
    follow_up="How many distinct permutations does a multiset have? Check the formula against the scale tests.",
    related=["D12"],
))

P.append(dict(
    slug="combination-sum", title="Combination sum", level="medium", stage="choices-grids", tags=["backtracking", "pruning", "Blind 75"],
    companies=["Meta", "Amazon", "Google", "Apple", "Microsoft", "Airbnb", "Uber", "Bloomberg"],
    teaches=["Recurse with the same index to allow reuse; move on to allow the next value.",
             "Sort once, then `break` as soon as a candidate is bigger than what's left."],
    statement="""
        `candidates` holds distinct positive integers. Return every combination of them that adds up to `target`. A
        candidate may be used any number of times. Two combinations are the same if they use each candidate the same
        number of times, so `[2, 2, 3]` and `[3, 2, 2]` count once.

        The combinations can come in any order, and so can the values inside each one. If none exists, return `[]`.
    """,
    examples=[("candidates = [2, 3, 6, 7], target = 7", "[[2, 2, 3], [7]]"), ("candidates = [2], target = 1", "[]")],
    constraints=["1 ≤ candidates.len() ≤ 30", "1 ≤ candidates[i] ≤ 200, all distinct", "1 ≤ target ≤ 500", "the answer has at most 10⁴ combinations"],
    starter="""
        pub fn combination_sum(candidates: &[u32], target: u32) -> Vec<Vec<u32>> {
            todo!()
        }
    """,
    solution="""
        pub fn combination_sum(candidates: &[u32], target: u32) -> Vec<Vec<u32>> {
            fn go(c: &[u32], start: usize, left: u32, path: &mut Vec<u32>, out: &mut Vec<Vec<u32>>) {
                if left == 0 {
                    out.push(path.clone());
                    return;
                }
                for i in start..c.len() {
                    if c[i] > left {
                        break; // sorted: every later candidate is too big as well
                    }
                    path.push(c[i]);
                    go(c, i, left - c[i], path, out); // `i`, not `i + 1`: c[i] may be used again
                    path.pop();
                }
            }
            let mut c = candidates.to_vec();
            c.sort_unstable();
            let mut out = Vec::new();
            go(&c, 0, target, &mut Vec::new(), &mut out);
            out
        }
    """,
    visible=[
        NORM,
        T("leetcode_seven", "candidates = [2, 3, 6, 7], target = 7", "norm(combination_sum(&[2, 3, 6, 7], 7))", "vec![vec![2, 2, 3], vec![7]]"),
        T("leetcode_eight", "candidates = [2, 3, 5], target = 8", "norm(combination_sum(&[2, 3, 5], 8))", "vec![vec![2, 2, 2, 2], vec![2, 3, 3], vec![3, 5]]"),
        T("leetcode_none", "candidates = [2], target = 1", "combination_sum(&[2], 1)", "Vec::<Vec<u32>>::new()"),
        T("reuse_one_value", "candidates = [3], target = 9", "combination_sum(&[3], 9)", "vec![vec![3, 3, 3]]"),
        T("order_does_not_matter", "candidates = [1, 2], target = 4", "norm(combination_sum(&[1, 2], 4))", "vec![vec![1, 1, 1, 1], vec![1, 1, 2], vec![2, 2]]"),
    ],
    hidden=[
        NORM,
        T("unsorted_candidates", "candidates = [8, 2, 3], target = 7", "norm(combination_sum(&[8, 2, 3], 7))", "vec![vec![2, 2, 3]]"),
        T("all_too_big", "candidates = [5, 9], target = 4", "combination_sum(&[5, 9], 4)", "Vec::<Vec<u32>>::new()"),
        T("no_mix_reaches", "candidates = [3, 5], target = 4", "combination_sum(&[3, 5], 4)", "Vec::<Vec<u32>>::new()"),
        T("ones", "candidates = [1], target = 5", "combination_sum(&[1], 5)", "vec![vec![1, 1, 1, 1, 1]]"),
        T("exact_single", "candidates = [7], target = 7", "combination_sum(&[7], 7)", "vec![vec![7]]"),
        T("target_100", "candidates = [7, 11, 13], target = 100", "norm(combination_sum(&[7, 11, 13], 100))", "vec![vec![7, 7, 7, 7, 7, 7, 7, 7, 7, 11, 13, 13], vec![7, 7, 7, 7, 7, 7, 7, 7, 11, 11, 11, 11], vec![7, 7, 7, 7, 7, 13, 13, 13, 13, 13], vec![7, 7, 7, 7, 11, 11, 11, 13, 13, 13], vec![7, 7, 7, 11, 11, 11, 11, 11, 11, 13], vec![11, 11, 13, 13, 13, 13, 13, 13]]"),
        T("big_candidate", "candidates = [200, 100], target = 500", "norm(combination_sum(&[200, 100], 500))", "vec![vec![100, 100, 100, 100, 100], vec![100, 100, 100, 200], vec![100, 200, 200]]"),
        T("partitions_of_thirty", "candidates = 1..=30, target = 30", "combination_sum(&(1..=30).collect::<Vec<u32>>(), 30).len()", "5604"),
        """
        /// Every multiset of candidates summing to each total up to `target`, built bottom-up into sets.
        fn brute(c: &[u32], target: u32) -> Vec<Vec<u32>> {
            let mut ways: Vec<std::collections::BTreeSet<Vec<u32>>> = vec![Default::default(); target as usize + 1];
            ways[0].insert(Vec::new());
            for t in 1..=target as usize {
                for &x in c {
                    if x as usize <= t {
                        let before: Vec<Vec<u32>> = ways[t - x as usize].iter().cloned().collect();
                        for mut w in before {
                            w.push(x);
                            w.sort();
                            ways[t].insert(w);
                        }
                    }
                }
            }
            ways[target as usize].iter().cloned().collect()
        }

        #[test]
        fn random_vs_bottom_up_sets() {
            let mut rng = anneal_prelude::Rng::new(1124);
            for _ in 0..300 {
                let mut pool: Vec<u32> = (1..=12).collect();
                rng.shuffle(&mut pool);
                let n = rng.int(1, 5) as usize;
                pool.truncate(n);
                let target = rng.int(1, 20) as u32;
                check!(format!("candidates = {pool:?}, target = {target}"), norm(combination_sum(&pool, target)), brute(&pool, target));
            }
        }
        """,
    ],
    wrong=dict(
        orderings_counted_twice="""
            pub fn combination_sum(candidates: &[u32], target: u32) -> Vec<Vec<u32>> {
                fn go(c: &[u32], left: u32, path: &mut Vec<u32>, out: &mut Vec<Vec<u32>>) {
                    if left == 0 {
                        out.push(path.clone());
                        return;
                    }
                    for &x in c {
                        if x <= left {
                            path.push(x);
                            go(c, left - x, path, out);
                            path.pop();
                        }
                    }
                }
                let mut out = Vec::new();
                go(candidates, target, &mut Vec::new(), &mut out);
                out
            }
        """,
        each_used_once="""
            pub fn combination_sum(candidates: &[u32], target: u32) -> Vec<Vec<u32>> {
                fn go(c: &[u32], start: usize, left: u32, path: &mut Vec<u32>, out: &mut Vec<Vec<u32>>) {
                    if left == 0 {
                        out.push(path.clone());
                        return;
                    }
                    for i in start..c.len() {
                        if c[i] > left {
                            break;
                        }
                        path.push(c[i]);
                        go(c, i + 1, left - c[i], path, out);
                        path.pop();
                    }
                }
                let mut c = candidates.to_vec();
                c.sort_unstable();
                let mut out = Vec::new();
                go(&c, 0, target, &mut Vec::new(), &mut out);
                out
            }
        """,
        breaks_without_sorting="""
            pub fn combination_sum(candidates: &[u32], target: u32) -> Vec<Vec<u32>> {
                fn go(c: &[u32], start: usize, left: u32, path: &mut Vec<u32>, out: &mut Vec<Vec<u32>>) {
                    if left == 0 {
                        out.push(path.clone());
                        return;
                    }
                    for i in start..c.len() {
                        if c[i] > left {
                            break;
                        }
                        path.push(c[i]);
                        go(c, i, left - c[i], path, out);
                        path.pop();
                    }
                }
                let mut out = Vec::new();
                go(candidates, 0, target, &mut Vec::new(), &mut out);
                out
            }
        """,
    ),
    hints=[("approach", "Walk the candidates by index. Taking `c[i]` recurses with the same `i` (it may repeat); the loop moving on to `i + 1` is the choice to stop using it."),
           ("rust", "Pass `left: u32` down and record the path when it hits 0. Sort first so you can `break` once `c[i] > left` (that also avoids a `u32` underflow)."),
           ("edge case", "Starting every level from index 0 builds `[2, 2, 3]`, `[2, 3, 2]` and `[3, 2, 2]`: only move forward.")],
    notes=("Choosing candidates in non-decreasing index order makes each multiset appear once. Sorting lets one comparison cut "
           "the rest of a level.", "O(answer · target / min) in practice; exponential in the worst case", "O(target / min) recursion depth"),
    follow_up="If you only needed the number of combinations, what DP would replace the backtracking?",
    related=["D12"],
))

P.append(dict(
    slug="combination-sum-ii", title="Combination sum II", level="medium", stage="choices-grids", tags=["backtracking", "duplicates", "pruning"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "LinkedIn", "Bloomberg"],
    teaches=["Combination sum with each element used at most once: recurse with `i + 1`.",
             "The Subsets II skip removes duplicate combinations when `candidates` has repeats."],
    statement="""
        `candidates` may contain repeated values. Return every distinct combination that adds up to `target`, where
        each element of `candidates` is used at most once. Combinations with the same values the same number of times
        count once.

        The combinations can come in any order, and so can the values inside each one.
    """,
    examples=[("candidates = [10, 1, 2, 7, 6, 1, 5], target = 8", "[[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]"),
              ("candidates = [2, 5, 2, 1, 2], target = 5", "[[1, 2, 2], [5]]")],
    constraints=["1 ≤ candidates.len() ≤ 100", "1 ≤ candidates[i] ≤ 50", "1 ≤ target ≤ 30"],
    starter="""
        pub fn combination_sum2(candidates: &[u32], target: u32) -> Vec<Vec<u32>> {
            todo!()
        }
    """,
    solution="""
        pub fn combination_sum2(candidates: &[u32], target: u32) -> Vec<Vec<u32>> {
            fn go(c: &[u32], start: usize, left: u32, path: &mut Vec<u32>, out: &mut Vec<Vec<u32>>) {
                if left == 0 {
                    out.push(path.clone());
                    return;
                }
                for i in start..c.len() {
                    if c[i] > left {
                        break;
                    }
                    // Equal values at the same depth would build the same combinations again.
                    if i > start && c[i] == c[i - 1] {
                        continue;
                    }
                    path.push(c[i]);
                    go(c, i + 1, left - c[i], path, out);
                    path.pop();
                }
            }
            let mut c = candidates.to_vec();
            c.sort_unstable();
            let mut out = Vec::new();
            go(&c, 0, target, &mut Vec::new(), &mut out);
            out
        }
    """,
    visible=[
        NORM,
        T("leetcode_target_eight", "candidates = [10, 1, 2, 7, 6, 1, 5], target = 8", "norm(combination_sum2(&[10, 1, 2, 7, 6, 1, 5], 8))", "vec![vec![1, 1, 6], vec![1, 2, 5], vec![1, 7], vec![2, 6]]"),
        T("leetcode_target_five", "candidates = [2, 5, 2, 1, 2], target = 5", "norm(combination_sum2(&[2, 5, 2, 1, 2], 5))", "vec![vec![1, 2, 2], vec![5]]"),
        T("none", "candidates = [3], target = 2", "combination_sum2(&[3], 2)", "Vec::<Vec<u32>>::new()"),
        T("each_used_once", "candidates = [2], target = 4", "combination_sum2(&[2], 4)", "Vec::<Vec<u32>>::new()"),
        T("repeats_count_once", "candidates = [3, 3, 3, 3], target = 6", "combination_sum2(&[3, 3, 3, 3], 6)", "vec![vec![3, 3]]"),
    ],
    hidden=[
        NORM,
        T("single_exact", "candidates = [7], target = 7", "combination_sum2(&[7], 7)", "vec![vec![7]]"),
        T("uses_two_copies", "candidates = [4, 1, 1, 4, 4], target = 9", "norm(combination_sum2(&[4, 1, 1, 4, 4], 9))", "vec![vec![1, 4, 4]]"),
        T("pair_of_ones", "candidates = [1, 1], target = 2", "combination_sum2(&[1, 1], 2)", "vec![vec![1, 1]]"),
        T("all_too_big", "candidates = [40, 50], target = 30", "combination_sum2(&[40, 50], 30)", "Vec::<Vec<u32>>::new()"),
        T("whole_slice", "candidates = [1, 2, 3], target = 6", "norm(combination_sum2(&[1, 2, 3], 6))", "vec![vec![1, 2, 3]]"),
        T("two_ways", "candidates = [5, 1, 4, 2, 3], target = 5", "norm(combination_sum2(&[5, 1, 4, 2, 3], 5))", "vec![vec![1, 4], vec![2, 3], vec![5]]"),
        T("big_values", "candidates = [50, 30, 30], target = 30", "combination_sum2(&[50, 30, 30], 30)", "vec![vec![30]]"),
        T("thirty_from_one_to_thirty", "candidates = 1..=30, target = 30", "combination_sum2(&(1..=30).collect::<Vec<u32>>(), 30).len()", "296"),
        """
        #[test]
        fn random_vs_bitmasks_and_a_set() {
            let mut rng = anneal_prelude::Rng::new(1125);
            for _ in 0..300 {
                let n = rng.int(1, 12) as usize;
                let c: Vec<u32> = rng.vec(n, 1, 8);
                let target = rng.int(1, 20) as u32;
                let mut all = std::collections::BTreeSet::new();
                for mask in 0..1u32 << n {
                    let mut s: Vec<u32> = (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| c[i]).collect();
                    if s.iter().sum::<u32>() == target {
                        s.sort();
                        all.insert(s);
                    }
                }
                check!(format!("candidates = {c:?}, target = {target}"), norm(combination_sum2(&c, target)), all.into_iter().collect::<Vec<_>>());
            }
        }

        #[test]
        fn scale_a_hundred_ones() {
            check!("candidates = [1; 100], target = 30", combination_sum2(&vec![1; 100], 30), vec![vec![1; 30]]);
        }

        #[test]
        fn scale_a_hundred_mixed() {
            let c: Vec<u32> = (0..100).map(|i| i % 5 + 1).collect();
            check!("candidates = [1, 2, 3, 4, 5] × 20, target = 30", combination_sum2(&c, 30).len(), 651);
        }
        """,
    ],
    wrong=dict(
        no_duplicate_skip="""
            pub fn combination_sum2(candidates: &[u32], target: u32) -> Vec<Vec<u32>> {
                fn go(c: &[u32], start: usize, left: u32, path: &mut Vec<u32>, out: &mut Vec<Vec<u32>>) {
                    if left == 0 {
                        out.push(path.clone());
                        return;
                    }
                    for i in start..c.len() {
                        if c[i] > left {
                            break;
                        }
                        path.push(c[i]);
                        go(c, i + 1, left - c[i], path, out);
                        path.pop();
                    }
                }
                let mut c = candidates.to_vec();
                c.sort_unstable();
                let mut out = Vec::new();
                go(&c, 0, target, &mut Vec::new(), &mut out);
                out
            }
        """,
        dedupe_with_a_set="""
            pub fn combination_sum2(candidates: &[u32], target: u32) -> Vec<Vec<u32>> {
                fn go(c: &[u32], start: usize, left: u32, path: &mut Vec<u32>, out: &mut std::collections::BTreeSet<Vec<u32>>) {
                    if left == 0 {
                        out.insert(path.clone());
                        return;
                    }
                    for i in start..c.len() {
                        if c[i] > left {
                            break;
                        }
                        path.push(c[i]);
                        go(c, i + 1, left - c[i], path, out);
                        path.pop();
                    }
                }
                let mut c = candidates.to_vec();
                c.sort_unstable();
                let mut out = std::collections::BTreeSet::new();
                go(&c, 0, target, &mut Vec::new(), &mut out);
                out.into_iter().collect()
            }
        """,
        reuses_elements="""
            pub fn combination_sum2(candidates: &[u32], target: u32) -> Vec<Vec<u32>> {
                fn go(c: &[u32], start: usize, left: u32, path: &mut Vec<u32>, out: &mut Vec<Vec<u32>>) {
                    if left == 0 {
                        out.push(path.clone());
                        return;
                    }
                    for i in start..c.len() {
                        if c[i] > left {
                            break;
                        }
                        if i > start && c[i] == c[i - 1] {
                            continue;
                        }
                        path.push(c[i]);
                        go(c, i, left - c[i], path, out);
                        path.pop();
                    }
                }
                let mut c = candidates.to_vec();
                c.sort_unstable();
                let mut out = Vec::new();
                go(&c, 0, target, &mut Vec::new(), &mut out);
                out
            }
        """,
    ),
    hints=[("approach", "It's Combination sum with `i + 1` in the recursive call, plus the Subsets II trick for repeated values."),
           ("rust", "Sort, then inside the loop: `break` if `c[i] > left`, `continue` if `i > start && c[i] == c[i - 1]`."),
           ("edge case", "A set of results is not enough: `[1; 100]` with target 30 has C(100, 30) index choices but one answer.")],
    notes=("Sorting groups equal values, and letting only the first of a group start a branch at each depth builds each "
           "multiset once. The `break` cuts every branch that can no longer reach the target.",
           "O(2ⁿ) worst case; far less with the pruning", "O(n) recursion depth"),
    follow_up="How would you return only the number of distinct combinations, and could a DP do it?",
    related=["D12"],
))

P.append(dict(
    slug="combination-sum-iii", title="Combination sum III", level="medium", stage="choices-grids", tags=["backtracking", "pruning"],
    companies=["Meta", "Amazon", "Google", "Microsoft"],
    teaches=["Two limits at once: exactly k numbers and exactly the sum n.",
             "Prune on both: stop when the path is full or the next digit is already too big."],
    statement="""
        Return every set of exactly `k` distinct digits from 1 to 9 that adds up to `n`. Each digit is used at most once
        per set.

        The sets can come in any order, and so can the digits inside each one. If none exists, return `[]`.
    """,
    examples=[("k = 3, n = 7", "[[1, 2, 4]]"), ("k = 3, n = 9", "[[1, 2, 6], [1, 3, 5], [2, 3, 4]]"), ("k = 4, n = 1", "[]")],
    constraints=["1 ≤ k ≤ 9", "1 ≤ n ≤ 60"],
    starter="""
        pub fn combination_sum3(k: usize, n: u32) -> Vec<Vec<u32>> {
            todo!()
        }
    """,
    solution="""
        pub fn combination_sum3(k: usize, n: u32) -> Vec<Vec<u32>> {
            fn go(next: u32, k: usize, left: u32, path: &mut Vec<u32>, out: &mut Vec<Vec<u32>>) {
                if path.len() == k {
                    if left == 0 {
                        out.push(path.clone());
                    }
                    return;
                }
                for d in next..=9 {
                    if d > left {
                        break;
                    }
                    path.push(d);
                    go(d + 1, k, left - d, path, out);
                    path.pop();
                }
            }
            let mut out = Vec::new();
            go(1, k, n, &mut Vec::with_capacity(k), &mut out);
            out
        }
    """,
    visible=[
        NORM,
        T("leetcode_three_seven", "k = 3, n = 7", "norm(combination_sum3(3, 7))", "vec![vec![1, 2, 4]]"),
        T("leetcode_three_nine", "k = 3, n = 9", "norm(combination_sum3(3, 9))", "vec![vec![1, 2, 6], vec![1, 3, 5], vec![2, 3, 4]]"),
        T("leetcode_none", "k = 4, n = 1", "combination_sum3(4, 1)", "Vec::<Vec<u32>>::new()"),
        T("one_digit", "k = 1, n = 5", "combination_sum3(1, 5)", "vec![vec![5]]"),
        T("digits_stop_at_nine", "k = 1, n = 10", "combination_sum3(1, 10)", "Vec::<Vec<u32>>::new()"),
    ],
    hidden=[
        NORM,
        T("all_nine", "k = 9, n = 45", "combination_sum3(9, 45)", "vec![vec![1, 2, 3, 4, 5, 6, 7, 8, 9]]"),
        T("all_nine_wrong_sum", "k = 9, n = 44", "combination_sum3(9, 44)", "Vec::<Vec<u32>>::new()"),
        T("two_largest", "k = 2, n = 17", "combination_sum3(2, 17)", "vec![vec![8, 9]]"),
        T("too_big", "k = 2, n = 18", "combination_sum3(2, 18)", "Vec::<Vec<u32>>::new()"),
        T("no_repeats", "k = 2, n = 2", "combination_sum3(2, 2)", "Vec::<Vec<u32>>::new()"),
        T("four_twenty", "k = 4, n = 20", "combination_sum3(4, 20).len()", "12"),
        T("sixty", "k = 9, n = 60", "combination_sum3(9, 60)", "Vec::<Vec<u32>>::new()"),
        T("zero_not_a_digit", "k = 2, n = 9", "norm(combination_sum3(2, 9))", "vec![vec![1, 8], vec![2, 7], vec![3, 6], vec![4, 5]]"),
        """
        #[test]
        fn every_k_and_n_vs_bitmasks() {
            let mut rng = anneal_prelude::Rng::new(1126);
            let mut cases: Vec<(usize, u32)> = (1..=9).flat_map(|k| (1..=60).map(move |n| (k, n))).collect();
            rng.shuffle(&mut cases);
            for (k, n) in cases {
                let want: Vec<Vec<u32>> = (0..512u32)
                    .filter(|m| m.count_ones() as usize == k && (0..9).filter(|&i| m >> i & 1 == 1).map(|i| i + 1).sum::<u32>() == n)
                    .map(|m| (0..9).filter(|&i| m >> i & 1 == 1).map(|i| i + 1).collect())
                    .collect();
                check!(format!("k = {k}, n = {n}"), norm(combination_sum3(k, n)), norm(want));
            }
        }
        """,
    ],
    wrong=dict(
        zero_allowed="""
            pub fn combination_sum3(k: usize, n: u32) -> Vec<Vec<u32>> {
                fn go(next: u32, k: usize, left: u32, path: &mut Vec<u32>, out: &mut Vec<Vec<u32>>) {
                    if path.len() == k {
                        if left == 0 {
                            out.push(path.clone());
                        }
                        return;
                    }
                    for d in next..=9 {
                        if d > left {
                            break;
                        }
                        path.push(d);
                        go(d + 1, k, left - d, path, out);
                        path.pop();
                    }
                }
                let mut out = Vec::new();
                go(0, k, n, &mut Vec::new(), &mut out);
                out
            }
        """,
        any_count="""
            pub fn combination_sum3(k: usize, n: u32) -> Vec<Vec<u32>> {
                fn go(next: u32, k: usize, left: u32, path: &mut Vec<u32>, out: &mut Vec<Vec<u32>>) {
                    if left == 0 {
                        out.push(path.clone());
                        return;
                    }
                    if path.len() > k {
                        return;
                    }
                    for d in next..=9 {
                        if d > left {
                            break;
                        }
                        path.push(d);
                        go(d + 1, k, left - d, path, out);
                        path.pop();
                    }
                }
                let mut out = Vec::new();
                go(1, k, n, &mut Vec::new(), &mut out);
                out
            }
        """,
        digits_repeat="""
            pub fn combination_sum3(k: usize, n: u32) -> Vec<Vec<u32>> {
                fn go(next: u32, k: usize, left: u32, path: &mut Vec<u32>, out: &mut Vec<Vec<u32>>) {
                    if path.len() == k {
                        if left == 0 {
                            out.push(path.clone());
                        }
                        return;
                    }
                    for d in next..=9 {
                        if d > left {
                            break;
                        }
                        path.push(d);
                        go(d, k, left - d, path, out);
                        path.pop();
                    }
                }
                let mut out = Vec::new();
                go(1, k, n, &mut Vec::new(), &mut out);
                out
            }
        """,
    ),
    hints=[("approach", "Choose digits in increasing order from `next` to 9; stop when you have k of them and check the sum."),
           ("rust", "`fn go(next: u32, k: usize, left: u32, path: &mut Vec<u32>, out: &mut Vec<Vec<u32>>)`; `break` once `d > left`."),
           ("edge case", "A full path whose sum is not n is a dead end, and so is a sum reached with fewer than k digits.")],
    notes=("There are only 2⁹ subsets of the digits, so any correct search is fast; pruning on the remaining sum and the count "
           "keeps it to the useful branches.", "O(C(9, k) · k)", "O(k)"),
    follow_up="Could you answer this with one pass over the 512 bitmasks instead? What does that trade?",
    related=["D12"],
))

P.append(dict(
    slug="generate-parentheses", title="Generate parentheses", level="medium", stage="choices-grids", tags=["backtracking", "String", "pruning"],
    companies=["Meta", "Apple", "Amazon", "Google", "Microsoft", "Uber", "Bloomberg"],
    teaches=["Prune by an invariant while building: a `)` is only allowed while it has an open `(` to close.",
             "One `String` buffer: `push`, recurse, `pop`, and clone only at a leaf."],
    statement="""
        Return every string of `n` pairs of parentheses that is well formed: read left to right, no prefix closes more
        pairs than it opened, and the whole string closes all of them.

        The strings can come in any order. `n = 0` has one answer, the empty string.
    """,
    examples=[("n = 3", "[\"((()))\", \"(()())\", \"(())()\", \"()(())\", \"()()()\"]"), ("n = 1", "[\"()\"]")],
    constraints=["0 ≤ n ≤ 13"],
    starter="""
        pub fn generate_parenthesis(n: usize) -> Vec<String> {
            todo!()
        }
    """,
    solution="""
        pub fn generate_parenthesis(n: usize) -> Vec<String> {
            fn go(n: usize, open: usize, close: usize, path: &mut String, out: &mut Vec<String>) {
                if path.len() == 2 * n {
                    out.push(path.clone());
                    return;
                }
                if open < n {
                    path.push('(');
                    go(n, open + 1, close, path, out);
                    path.pop();
                }
                // A `)` needs an unmatched `(` before it.
                if close < open {
                    path.push(')');
                    go(n, open, close + 1, path, out);
                    path.pop();
                }
            }
            let mut out = Vec::new();
            go(n, 0, 0, &mut String::with_capacity(2 * n), &mut out);
            out
        }
    """,
    visible=[
        SORTED,
        T("leetcode_three", "n = 3", "sorted(generate_parenthesis(3))", 'vec!["((()))", "(()())", "(())()", "()(())", "()()()"]'),
        T("leetcode_one", "n = 1", "generate_parenthesis(1)", 'vec!["()"]'),
        T("zero_pairs", "n = 0 (one answer: the empty string)", "generate_parenthesis(0)", "vec![String::new()]"),
        T("two", "n = 2", "sorted(generate_parenthesis(2))", 'vec!["(())", "()()"]'),
        T("five_has_42", "n = 5", "generate_parenthesis(5).len()", "42"),
    ],
    hidden=[
        SORTED,
        """
        fn balanced(s: &str) -> bool {
            let mut depth = 0i32;
            for ch in s.chars() {
                depth += if ch == '(' { 1 } else if ch == ')' { -1 } else { return false };
                if depth < 0 {
                    return false;
                }
            }
            depth == 0
        }
        """,
        T("four", "n = 4", "sorted(generate_parenthesis(4))",
          'vec!["(((())))", "((()()))", "((())())", "((()))()", "(()(()))", "(()()())", "(()())()", "(())(())", "(())()()", "()((()))", "()(()())", "()(())()", "()()(())", "()()()()"]'),
        T("six", "n = 6", "generate_parenthesis(6).len()", "132"),
        T("seven_no_duplicates", "n = 7, duplicates removed", "{ let mut v = sorted(generate_parenthesis(7)); v.dedup(); v.len() }", "429"),
        T("eight", "n = 8", "generate_parenthesis(8).len()", "1430"),
        T("nine_all_balanced", "n = 9, every string well formed", "generate_parenthesis(9).iter().all(|s| balanced(s))", "true"),
        T("ten_all_length_twenty", "n = 10, every string has 20 characters", "generate_parenthesis(10).iter().all(|s| s.len() == 20)", "true"),
        T("eleven_first_and_last", "n = 11, smallest and largest", "{ let v = sorted(generate_parenthesis(11)); (v.len(), v[0].clone(), v[v.len() - 1].clone()) }",
          '(58786, "((((((((((()))))))))))".to_string(), "()()()()()()()()()()()".to_string())'),
        T("zero_again", "n = 0", "generate_parenthesis(0).len()", "1"),
        """
        #[test]
        fn random_strings_vs_balance_check() {
            let answers: Vec<std::collections::HashSet<String>> = (0..=8).map(|n| generate_parenthesis(n).into_iter().collect()).collect();
            for n in 0..=8usize {
                // Every string of n pairs, filtered by a direct balance check.
                let brute = (0u32..1 << (2 * n)).filter(|m| {
                    let s: String = (0..2 * n).map(|i| if m >> i & 1 == 1 { '(' } else { ')' }).collect();
                    balanced(&s)
                }).count();
                check!(format!("n = {n}: count vs brute force"), answers[n].len(), brute);
            }
            let mut rng = anneal_prelude::Rng::new(1127);
            for _ in 0..400 {
                let n = rng.int(0, 8) as usize;
                let len = 2 * n;
                let s = rng.string(len, "()");
                check!(format!("n = {n}: is {s:?} an answer?"), answers[n].contains(&s), balanced(&s));
            }
        }

        #[test]
        fn scale_thirteen_pairs() {
            let v = sorted(generate_parenthesis(13));
            let distinct = v.windows(2).all(|w| w[0] < w[1]);
            let valid = v.iter().all(|s| s.len() == 26 && balanced(s));
            check!("n = 13", (v.len(), distinct, valid, v[371_450].clone()), (742_900, true, true, "(()((()))((())))(())()()()".to_string()));
        }
        """,
    ],
    wrong=dict(
        every_string_then_filter="""
            pub fn generate_parenthesis(n: usize) -> Vec<String> {
                let mut out = Vec::new();
                for mask in 0u64..1 << (2 * n) {
                    let s: String = (0..2 * n).map(|i| if mask >> i & 1 == 1 { '(' } else { ')' }).collect();
                    let mut depth = 0i32;
                    let mut ok = true;
                    for ch in s.chars() {
                        depth += if ch == '(' { 1 } else { -1 };
                        if depth < 0 {
                            ok = false;
                            break;
                        }
                    }
                    if ok && depth == 0 {
                        out.push(s);
                    }
                }
                out
            }
        """,
        close_limited_by_n="""
            pub fn generate_parenthesis(n: usize) -> Vec<String> {
                fn go(n: usize, open: usize, close: usize, path: &mut String, out: &mut Vec<String>) {
                    if path.len() == 2 * n {
                        out.push(path.clone());
                        return;
                    }
                    if open < n {
                        path.push('(');
                        go(n, open + 1, close, path, out);
                        path.pop();
                    }
                    if close < n {
                        path.push(')');
                        go(n, open, close + 1, path, out);
                        path.pop();
                    }
                }
                let mut out = Vec::new();
                go(n, 0, 0, &mut String::new(), &mut out);
                out
            }
        """,
        nothing_for_zero="""
            pub fn generate_parenthesis(n: usize) -> Vec<String> {
                fn go(n: usize, open: usize, close: usize, path: &mut String, out: &mut Vec<String>) {
                    if path.len() == 2 * n {
                        out.push(path.clone());
                        return;
                    }
                    if open < n {
                        path.push('(');
                        go(n, open + 1, close, path, out);
                        path.pop();
                    }
                    if close < open {
                        path.push(')');
                        go(n, open, close + 1, path, out);
                        path.pop();
                    }
                }
                if n == 0 {
                    return Vec::new();
                }
                let mut out = Vec::new();
                go(n, 0, 0, &mut String::new(), &mut out);
                out
            }
        """,
    ),
    hints=[("approach", "Build the string left to right, counting `open` and `close`. You may add `(` while `open < n`, and `)` while `close < open`; every leaf is then an answer."),
           ("rust", "Keep one `String` and pass `&mut String` down: `push`, recurse, `pop`. Clone it only when it reaches length `2 * n`."),
           ("edge case", "Generating all 2²ⁿ strings and filtering is far too slow at n = 13, which has 742 900 answers out of 67 million strings.")],
    notes=("The two rules keep every prefix valid, so the search never enters a dead end: each leaf is an answer, and the work is "
           "the answer count (the n-th Catalan number, about 4ⁿ / n^1.5) times the length.", "O(4ⁿ / √n)", "O(n) besides the output"),
    follow_up="How would you return only the k-th answer in sorted order without generating the others?",
    related=["D3", "D12"],
))

P.append(dict(
    slug="different-ways-to-add-parentheses", title="Different ways to add parentheses", level="medium", stage="choices-grids",
    tags=["divide and conquer", "recursion", "parsing"],
    companies=["Amazon", "Google", "Microsoft", "Bloomberg"],
    teaches=["Divide and conquer: pick the operator applied last, solve both sides, combine every pair.",
             "Parse once into numbers and operators, then recurse on subslices of both."],
    statement="""
        `expression` holds non-negative integers joined by `+`, `-` and `*`, with no spaces or parentheses. Return the
        value of every way to fully parenthesise it (every order in which the operators can be applied).

        Two groupings that happen to give the same value both count, so the answer can hold duplicates. The values can
        come in any order.
    """,
    examples=[("expression = \"2-1-1\"", "[0, 2]"), ("expression = \"2*3-4*5\"", "[-34, -14, -10, -10, 10]")],
    constraints=["1 ≤ expression.len() ≤ 40", "numbers are 0 to 99, operators are `+`, `-`, `*`", "at most 11 operators",
                 "every intermediate value fits in an i64"],
    starter="""
        pub fn diff_ways_to_compute(expression: &str) -> Vec<i64> {
            todo!()
        }
    """,
    solution="""
        pub fn diff_ways_to_compute(expression: &str) -> Vec<i64> {
            // The expression is nums[0] ops[0] nums[1] ... ops[k-1] nums[k].
            fn ways(nums: &[i64], ops: &[u8]) -> Vec<i64> {
                if ops.is_empty() {
                    return vec![nums[0]];
                }
                let mut out = Vec::new();
                for i in 0..ops.len() {
                    // ops[i] is applied last: everything to its left, then everything to its right.
                    let left = ways(&nums[..=i], &ops[..i]);
                    let right = ways(&nums[i + 1..], &ops[i + 1..]);
                    for &a in &left {
                        for &b in &right {
                            out.push(match ops[i] {
                                b'+' => a + b,
                                b'-' => a - b,
                                _ => a * b,
                            });
                        }
                    }
                }
                out
            }
            let (mut nums, mut ops, mut cur) = (Vec::new(), Vec::new(), 0i64);
            for b in expression.bytes() {
                if b.is_ascii_digit() {
                    cur = cur * 10 + i64::from(b - b'0');
                } else {
                    nums.push(cur);
                    ops.push(b);
                    cur = 0;
                }
            }
            nums.push(cur);
            ways(&nums, &ops)
        }
    """,
    visible=[
        SORTED,
        T("leetcode_two_minus_one_minus_one", "expression = \"2-1-1\"", 'sorted(diff_ways_to_compute("2-1-1"))', "vec![0, 2]"),
        T("leetcode_mixed", "expression = \"2*3-4*5\"", 'sorted(diff_ways_to_compute("2*3-4*5"))', "vec![-34, -14, -10, -10, 10]"),
        T("single_number", "expression = \"7\"", 'diff_ways_to_compute("7")', "vec![7]"),
        T("duplicates_are_kept", "expression = \"1+1+1\" (two groupings, same value)", 'diff_ways_to_compute("1+1+1")', "vec![3, 3]"),
        T("two_digit_numbers", "expression = \"10-5*2\"", 'sorted(diff_ways_to_compute("10-5*2"))', "vec![0, 10]"),
    ],
    hidden=[
        SORTED,
        T("zero", "expression = \"0\"", 'diff_ways_to_compute("0")', "vec![0]"),
        T("ninety_nine", "expression = \"99\"", 'diff_ways_to_compute("99")', "vec![99]"),
        T("three_minuses", "expression = \"1-2-3-4\"", 'sorted(diff_ways_to_compute("1-2-3-4"))', "vec![-8, -2, -2, 0, 6]"),
        T("zero_times", "expression = \"0*5-3\"", 'sorted(diff_ways_to_compute("0*5-3"))', "vec![-3, 0]"),
        T("negative_results", "expression = \"1-99*99\"", 'sorted(diff_ways_to_compute("1-99*99"))', "vec![-9800, -9702]"),
        T("past_i32", "expression = \"99*99*99*99*99\" (99⁵ > i32::MAX)", 'diff_ways_to_compute("99*99*99*99*99")', "vec![9_509_900_499; 14]"),
        T("all_three_operators", "expression = \"2*3*4-5*6+7\"", 'sorted(diff_ways_to_compute("2*3*4-5*6+7"))',
          "vec![-366, -366, -198, -198, -149, -149, -142, -114, -114, -106, -78, -78, -78, -78, -78, -50, -41, -41, -29, -29, -29, -29, -29, -29, -22, -22, -22, -13, -13, 1, 1, 6, 6, 91, 91, 98, 121, 121, 182, 182, 247, 247]"),
        T("one_operator", "expression = \"12*34\"", 'diff_ways_to_compute("12*34")', "vec![408]"),
        """
        /// Every value of tokens i..=j, built bottom-up over interval lengths.
        fn brute(nums: &[i64], ops: &[char]) -> Vec<i64> {
            let n = nums.len();
            let mut table = vec![vec![Vec::<i64>::new(); n]; n];
            for i in 0..n {
                table[i][i] = vec![nums[i]];
            }
            for len in 2..=n {
                for i in 0..=n - len {
                    let j = i + len - 1;
                    let mut vals = Vec::new();
                    for k in i..j {
                        for &a in &table[i][k] {
                            for &b in &table[k + 1][j] {
                                vals.push(match ops[k] { '+' => a + b, '-' => a - b, _ => a * b });
                            }
                        }
                    }
                    table[i][j] = vals;
                }
            }
            let mut all = table[0][n - 1].clone();
            all.sort();
            all
        }

        #[test]
        fn random_vs_interval_table() {
            let mut rng = anneal_prelude::Rng::new(1128);
            for _ in 0..300 {
                let k = rng.below(6);
                let nums: Vec<i64> = rng.vec(k + 1, 0, 99);
                let ops: Vec<char> = (0..k).map(|_| *rng.pick(&['+', '-', '*'])).collect();
                let mut expr = nums[0].to_string();
                for i in 0..k {
                    expr.push(ops[i]);
                    expr += &nums[i + 1].to_string();
                }
                check!(format!("expression = {expr:?}"), sorted(diff_ways_to_compute(&expr)), brute(&nums, &ops));
            }
        }

        #[test]
        fn scale_eleven_operators() {
            let got = diff_ways_to_compute("1+2*3-4*5+6*7-8*9+1*2-3");
            let (min, max) = (*got.iter().min().unwrap(), *got.iter().max().unwrap());
            check!("expression = \\"1+2*3-4*5+6*7-8*9+1*2-3\\"", (got.len(), min, max, got.iter().sum::<i64>()), (58_786, -18_789, 20_601, -5_911_158));
        }
        """,
    ],
    wrong=dict(
        single_digit_numbers="""
            pub fn diff_ways_to_compute(expression: &str) -> Vec<i64> {
                let b = expression.as_bytes();
                if b.len() == 1 {
                    return vec![i64::from(b[0] - b'0')];
                }
                let mut out = Vec::new();
                for i in 0..b.len() {
                    if b[i].is_ascii_digit() {
                        continue;
                    }
                    for a in diff_ways_to_compute(&expression[..i]) {
                        for c in diff_ways_to_compute(&expression[i + 1..]) {
                            out.push(match b[i] { b'+' => a + c, b'-' => a - c, _ => a * c });
                        }
                    }
                }
                out
            }
        """,
        values_deduplicated="""
            pub fn diff_ways_to_compute(expression: &str) -> Vec<i64> {
                fn ways(nums: &[i64], ops: &[u8]) -> std::collections::BTreeSet<i64> {
                    if ops.is_empty() {
                        return [nums[0]].into();
                    }
                    let mut out = std::collections::BTreeSet::new();
                    for i in 0..ops.len() {
                        for &a in &ways(&nums[..=i], &ops[..i]) {
                            for &b in &ways(&nums[i + 1..], &ops[i + 1..]) {
                                out.insert(match ops[i] { b'+' => a + b, b'-' => a - b, _ => a * b });
                            }
                        }
                    }
                    out
                }
                let (mut nums, mut ops, mut cur) = (Vec::new(), Vec::new(), 0i64);
                for b in expression.bytes() {
                    if b.is_ascii_digit() {
                        cur = cur * 10 + i64::from(b - b'0');
                    } else {
                        nums.push(cur);
                        ops.push(b);
                        cur = 0;
                    }
                }
                nums.push(cur);
                ways(&nums, &ops).into_iter().collect()
            }
        """,
        i32_values="""
            pub fn diff_ways_to_compute(expression: &str) -> Vec<i64> {
                fn ways(nums: &[i32], ops: &[u8]) -> Vec<i32> {
                    if ops.is_empty() {
                        return vec![nums[0]];
                    }
                    let mut out = Vec::new();
                    for i in 0..ops.len() {
                        for &a in &ways(&nums[..=i], &ops[..i]) {
                            for &b in &ways(&nums[i + 1..], &ops[i + 1..]) {
                                out.push(match ops[i] { b'+' => a + b, b'-' => a - b, _ => a * b });
                            }
                        }
                    }
                    out
                }
                let (mut nums, mut ops, mut cur) = (Vec::new(), Vec::new(), 0i32);
                for b in expression.bytes() {
                    if b.is_ascii_digit() {
                        cur = cur * 10 + i32::from(b - b'0');
                    } else {
                        nums.push(cur);
                        ops.push(b);
                        cur = 0;
                    }
                }
                nums.push(cur);
                ways(&nums, &ops).into_iter().map(i64::from).collect()
            }
        """,
    ),
    hints=[("approach", "Choose which operator is applied last. Its left side and right side are smaller expressions of the same kind: get all their values recursively and combine every pair."),
           ("rust", "Parse once into `nums: Vec<i64>` and `ops: Vec<u8>`; operator `i` splits them into `(&nums[..=i], &ops[..i])` and `(&nums[i + 1..], &ops[i + 1..])`."),
           ("edge case", "Numbers can have two digits, and products like 99⁵ overflow an `i32`. Keep duplicate values: each grouping counts.")],
    notes=("Every full parenthesisation is a binary tree whose root is the operator applied last, so recursing on each root choice "
           "enumerates them all exactly once. With k operators there are Catalan(k) groupings. Memoising on the (start, end) of the "
           "subslice saves recomputing the same sub-expressions, though the answer itself is still Catalan-sized.",
           "O(Catalan(k) · k) roughly, the size of the answer", "O(Catalan(k))"),
    follow_up="Memoise on the subslice bounds. How much work does that save when the answer itself is Catalan(k) long?",
    related=["D12", "D3"],
))

P.append(dict(
    slug="word-search", title="Word search", level="medium", stage="choices-grids", tags=["backtracking", "grid", "pruning", "Blind 75"],
    companies=["Meta", "Apple", "Amazon", "Google", "Microsoft", "Uber", "Bloomberg"],
    teaches=["Grid backtracking: mark the cell as used, try the four neighbours, restore it on the way back.",
             "Prune before searching: if the board can't supply the word's letters, don't start."],
    statement="""
        `board` is a grid of ASCII letters, one `&str` per row. Return `true` if `word` can be traced on the board: start
        on any cell, and step up, down, left or right from each letter to the next. A cell can be used at most once in a
        word. Letters are case-sensitive.

        The tests include adversarial boards, such as a board full of `A` and a word of many `A`s ending in a letter the
        board doesn't have: plain backtracking takes far too long on those.
    """,
    examples=[("board = [\"ABCE\", \"SFCS\", \"ADEE\"], word = \"ABCCED\"", "true"), ("board = [\"ABCE\", \"SFCS\", \"ADEE\"], word = \"ABCB\"", "false")],
    constraints=["1 ≤ rows, cols ≤ 6, every row the same length", "1 ≤ word.len() ≤ 40", "board and word hold ASCII letters"],
    starter="""
        pub fn exist(board: &[&str], word: &str) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn exist(board: &[&str], word: &str) -> bool {
            fn found(grid: &mut [Vec<u8>], word: &[u8], r: usize, c: usize) -> bool {
                if grid[r][c] != word[0] {
                    return false;
                }
                if word.len() == 1 {
                    return true;
                }
                let letter = grid[r][c];
                grid[r][c] = 0; // on the current path: matches no letter
                let (h, w, rest) = (grid.len(), grid[0].len(), &word[1..]);
                let hit = (r > 0 && found(grid, rest, r - 1, c))
                    || (r + 1 < h && found(grid, rest, r + 1, c))
                    || (c > 0 && found(grid, rest, r, c - 1))
                    || (c + 1 < w && found(grid, rest, r, c + 1));
                grid[r][c] = letter;
                hit
            }
            let mut grid: Vec<Vec<u8>> = board.iter().map(|row| row.as_bytes().to_vec()).collect();
            let mut word = word.as_bytes().to_vec();
            // The board must hold every letter at least as often as the word uses it.
            let mut have = [0usize; 256];
            for &b in grid.iter().flatten() {
                have[b as usize] += 1;
            }
            let mut need = [0usize; 256];
            for &b in &word {
                need[b as usize] += 1;
                if need[b as usize] > have[b as usize] {
                    return false;
                }
            }
            // Start from the rarer end of the word: fewer starting cells, fewer dead branches.
            if let (Some(&first), Some(&last)) = (word.first(), word.last()) {
                if have[first as usize] > have[last as usize] {
                    word.reverse();
                }
            }
            for r in 0..grid.len() {
                for c in 0..grid[r].len() {
                    if found(&mut grid, &word, r, c) {
                        return true;
                    }
                }
            }
            false
        }
    """,
    visible=[
        T("leetcode_abcced", "board = [\"ABCE\", \"SFCS\", \"ADEE\"], word = \"ABCCED\"", 'exist(&["ABCE", "SFCS", "ADEE"], "ABCCED")', "true"),
        T("leetcode_see", "board = [\"ABCE\", \"SFCS\", \"ADEE\"], word = \"SEE\"", 'exist(&["ABCE", "SFCS", "ADEE"], "SEE")', "true"),
        T("leetcode_cell_used_twice", "board = [\"ABCE\", \"SFCS\", \"ADEE\"], word = \"ABCB\" (the B would be used twice)", 'exist(&["ABCE", "SFCS", "ADEE"], "ABCB")', "false"),
        T("single_cell", "board = [\"A\"], word = \"A\"", 'exist(&["A"], "A")', "true"),
        T("no_diagonal_steps", "board = [\"AB\", \"CD\"], word = \"AD\"", 'exist(&["AB", "CD"], "AD")', "false"),
    ],
    hidden=[
        T("back_and_forth", "board = [\"AB\"], word = \"ABA\"", 'exist(&["AB"], "ABA")', "false"),
        T("letter_missing", "board = [\"a\"], word = \"b\"", 'exist(&["a"], "b")', "false"),
        T("case_sensitive", "board = [\"aB\"], word = \"ab\"", 'exist(&["aB"], "ab")', "false"),
        T("snake_through_everything", "board = [\"ABC\", \"FED\", \"GHI\"], word = \"ABCDEFGHI\"", 'exist(&["ABC", "FED", "GHI"], "ABCDEFGHI")', "true"),
        T("right_to_left", "board = [\"AB\"], word = \"BA\"", 'exist(&["AB"], "BA")', "true"),
        T("longer_than_board", "board = [\"AAA\", \"AAA\"], word = \"AAAAAAA\"", 'exist(&["AAA", "AAA"], "AAAAAAA")', "false"),
        T("leetcode_restore_on_backtrack", "board = [\"ABCE\", \"SFES\", \"ADEE\"], word = \"ABCESEEEFS\"", 'exist(&["ABCE", "SFES", "ADEE"], "ABCESEEEFS")', "true"),
        T("leetcode_first_path_fails", "board = [\"CAA\", \"AAA\", \"BCD\"], word = \"AAB\"", 'exist(&["CAA", "AAA", "BCD"], "AAB")', "true"),
        T("whole_board_of_one_letter", "board = [\"AAAA\", \"AAAA\", \"AAAA\"], word = 12 × \"A\"", 'exist(&["AAAA", "AAAA", "AAAA"], "AAAAAAAAAAAA")', "true"),
        T("single_column", "board = [\"A\", \"B\", \"C\"], word = \"CBA\"", 'exist(&["A", "B", "C"], "CBA")', "true"),
        """
        /// Every path of distinct cells, with a bitmask of used cells instead of editing the board.
        fn brute(board: &[&str], word: &[u8]) -> bool {
            fn walk(g: &[&[u8]], word: &[u8], r: usize, c: usize, used: u64) -> bool {
                let w = g[0].len();
                if g[r][c] != word[0] || used >> (r * w + c) & 1 == 1 {
                    return false;
                }
                if word.len() == 1 {
                    return true;
                }
                let used = used | 1 << (r * w + c);
                let near = [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)];
                near.iter().any(|&(a, b)| a < g.len() && b < w && walk(g, &word[1..], a, b, used))
            }
            let g: Vec<&[u8]> = board.iter().map(|row| row.as_bytes()).collect();
            (0..g.len()).any(|r| (0..g[0].len()).any(|c| walk(&g, word, r, c, 0)))
        }

        #[test]
        fn random_vs_bitmask_paths() {
            let mut rng = anneal_prelude::Rng::new(1129);
            for _ in 0..400 {
                let (h, w) = (rng.int(1, 3) as usize, rng.int(1, 4) as usize);
                let rows: Vec<String> = (0..h).map(|_| rng.string(w, "ABC")).collect();
                let board: Vec<&str> = rows.iter().map(|s| s.as_str()).collect();
                let len = rng.int(1, 7) as usize;
                let word = rng.string(len, "ABC");
                check!(format!("board = {board:?}, word = {word:?}"), exist(&board, &word), brute(&board, word.as_bytes()));
            }
        }

        #[test]
        fn scale_letter_the_board_lacks() {
            // 6×6 of A, and 24 A's then a B: every path of A's is a dead end.
            let board = vec!["AAAAAA"; 6];
            let word = "A".repeat(24) + "B";
            check!("board = 6×6 of A, word = 24 × \\"A\\" + \\"B\\"", exist(&board, &word), false);
        }

        #[test]
        fn scale_one_letter_short() {
            // 35 A's and one C; the word needs 36 A's.
            let board = vec!["AAAAAA", "AAAAAA", "AAAAAA", "AAACAA", "AAAAAA", "AAAAAA"];
            let word = "A".repeat(36);
            check!("board = 6×6 of A with one C, word = 36 × \\"A\\"", exist(&board, &word), false);
        }

        #[test]
        fn scale_rare_last_letter() {
            let board = vec!["AAAAAA", "AAAAAA", "AAAAAA", "AAAAAA", "AAAAAA", "AAAAAB"];
            let word = "A".repeat(30) + "B";
            check!("board = 6×6 of A with a B in the corner, word = 30 × \\"A\\" + \\"B\\"", exist(&board, &word), true);
        }
        """,
    ],
    wrong=dict(
        plain_backtracking="""
            pub fn exist(board: &[&str], word: &str) -> bool {
                fn found(grid: &mut [Vec<u8>], word: &[u8], r: usize, c: usize) -> bool {
                    if grid[r][c] != word[0] {
                        return false;
                    }
                    if word.len() == 1 {
                        return true;
                    }
                    let letter = grid[r][c];
                    grid[r][c] = 0;
                    let (h, w, rest) = (grid.len(), grid[0].len(), &word[1..]);
                    let hit = (r > 0 && found(grid, rest, r - 1, c))
                        || (r + 1 < h && found(grid, rest, r + 1, c))
                        || (c > 0 && found(grid, rest, r, c - 1))
                        || (c + 1 < w && found(grid, rest, r, c + 1));
                    grid[r][c] = letter;
                    hit
                }
                let mut grid: Vec<Vec<u8>> = board.iter().map(|row| row.as_bytes().to_vec()).collect();
                if word.len() > grid.len() * grid[0].len() {
                    return false;
                }
                for r in 0..grid.len() {
                    for c in 0..grid[r].len() {
                        if found(&mut grid, word.as_bytes(), r, c) {
                            return true;
                        }
                    }
                }
                false
            }
        """,
        cells_reused="""
            pub fn exist(board: &[&str], word: &str) -> bool {
                fn found(grid: &[&[u8]], word: &[u8], r: usize, c: usize) -> bool {
                    if grid[r][c] != word[0] {
                        return false;
                    }
                    if word.len() == 1 {
                        return true;
                    }
                    let (h, w, rest) = (grid.len(), grid[0].len(), &word[1..]);
                    (r > 0 && found(grid, rest, r - 1, c))
                        || (r + 1 < h && found(grid, rest, r + 1, c))
                        || (c > 0 && found(grid, rest, r, c - 1))
                        || (c + 1 < w && found(grid, rest, r, c + 1))
                }
                let grid: Vec<&[u8]> = board.iter().map(|row| row.as_bytes()).collect();
                let mut have = [0usize; 256];
                for &b in grid.iter().copied().flatten() {
                    have[b as usize] += 1;
                }
                if word.bytes().any(|b| have[b as usize] == 0) {
                    return false;
                }
                (0..grid.len()).any(|r| (0..grid[r].len()).any(|c| found(&grid, word.as_bytes(), r, c)))
            }
        """,
        never_restored="""
            pub fn exist(board: &[&str], word: &str) -> bool {
                fn found(grid: &mut [Vec<u8>], word: &[u8], r: usize, c: usize) -> bool {
                    if grid[r][c] != word[0] {
                        return false;
                    }
                    if word.len() == 1 {
                        return true;
                    }
                    grid[r][c] = 0;
                    let (h, w, rest) = (grid.len(), grid[0].len(), &word[1..]);
                    (r > 0 && found(grid, rest, r - 1, c))
                        || (r + 1 < h && found(grid, rest, r + 1, c))
                        || (c > 0 && found(grid, rest, r, c - 1))
                        || (c + 1 < w && found(grid, rest, r, c + 1))
                }
                let mut grid: Vec<Vec<u8>> = board.iter().map(|row| row.as_bytes().to_vec()).collect();
                let mut have = [0usize; 256];
                for &b in grid.iter().flatten() {
                    have[b as usize] += 1;
                }
                let mut need = [0usize; 256];
                for b in word.bytes() {
                    need[b as usize] += 1;
                    if need[b as usize] > have[b as usize] {
                        return false;
                    }
                }
                for r in 0..grid.len() {
                    for c in 0..grid[r].len() {
                        if found(&mut grid, word.as_bytes(), r, c) {
                            return true;
                        }
                    }
                }
                false
            }
        """,
    ),
    hints=[("approach", "Try every starting cell. From a cell that matches `word[i]`, mark it used, try the four neighbours for `word[i + 1]`, and unmark it before returning."),
           ("rust", "Copy the board into `Vec<Vec<u8>>` and pass `&mut [Vec<u8>]` to an inner `fn`. Overwrite the cell with `0` while it's on the path and put the letter back afterwards."),
           ("edge case", "Before searching, count letters: if the word needs more of some letter than the board has, return `false` at once. Also start from whichever end of the word is rarer on the board.")],
    notes=("Each step has at most three unvisited neighbours, so a search from one cell costs up to 3^L for a word of length L; the "
           "letter count rejects the classic worst cases (a missing or too-rare letter) before any search, and starting from the rarer "
           "end shrinks the number of starting cells.", "O(rows · cols · 3^L) worst case", "O(L) recursion depth"),
    follow_up="How does the search change when you must find many words on the same board (Word search II, D10)?",
    related=["D9", "D10"],
))

P.append(dict(
    slug="palindrome-partitioning", title="Palindrome partitioning", level="medium", stage="choices-grids", tags=["backtracking", "lifetimes", "DP table"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "Bloomberg"],
    teaches=["Cut the string at every place where the next piece is a palindrome, and recurse on the rest.",
             "Return `&str` pieces that borrow from `s`: the inner `fn` needs an explicit lifetime `'a`."],
    statement="""
        Split `s` into pieces so that every piece is a palindrome (reads the same both ways). Return every such split,
        each as its list of pieces from left to right.

        The splits can come in any order; the pieces inside a split keep their order. An empty `s` has exactly one split,
        with no pieces.
    """,
    examples=[("s = \"aab\"", "[[\"a\", \"a\", \"b\"], [\"aa\", \"b\"]]"), ("s = \"a\"", "[[\"a\"]]")],
    constraints=["0 ≤ s.len() ≤ 16", "s holds lowercase ASCII letters"],
    starter="""
        pub fn partition(s: &str) -> Vec<Vec<&str>> {
            todo!()
        }
    """,
    solution="""
        pub fn partition(s: &str) -> Vec<Vec<&str>> {
            fn go<'a>(s: &'a str, start: usize, pal: &[Vec<bool>], path: &mut Vec<&'a str>, out: &mut Vec<Vec<&'a str>>) {
                if start == s.len() {
                    out.push(path.clone());
                    return;
                }
                for end in start + 1..=s.len() {
                    if pal[start][end - 1] {
                        path.push(&s[start..end]);
                        go(s, end, pal, path, out);
                        path.pop();
                    }
                }
            }
            let (b, n) = (s.as_bytes(), s.len());
            // pal[i][j]: s[i..=j] is a palindrome. Row i reads row i + 1, so fill from the bottom.
            let mut pal = vec![vec![false; n]; n];
            for i in (0..n).rev() {
                for j in i..n {
                    pal[i][j] = b[i] == b[j] && (j - i < 2 || pal[i + 1][j - 1]);
                }
            }
            let mut out = Vec::new();
            go(s, 0, &pal, &mut Vec::new(), &mut out);
            out
        }
    """,
    visible=[
        SORTED,
        T("leetcode_aab", "s = \"aab\"", 'sorted(partition("aab"))', 'vec![vec!["a", "a", "b"], vec!["aa", "b"]]'),
        T("leetcode_single", "s = \"a\"", 'partition("a")', 'vec![vec!["a"]]'),
        T("empty_has_one_split", "s = \"\" (one split with no pieces)", 'partition("")', "vec![Vec::<&str>::new()]"),
        T("no_long_palindromes", "s = \"abc\"", 'partition("abc")', 'vec![vec!["a", "b", "c"]]'),
        T("odd_palindrome", "s = \"aba\"", 'sorted(partition("aba"))', 'vec![vec!["a", "b", "a"], vec!["aba"]]'),
    ],
    hidden=[
        SORTED,
        T("four_equal", "s = \"aaaa\"", 'sorted(partition("aaaa"))',
          'vec![vec!["a", "a", "a", "a"], vec!["a", "a", "aa"], vec!["a", "aa", "a"], vec!["a", "aaa"], vec!["aa", "a", "a"], vec!["aa", "aa"], vec!["aaa", "a"], vec!["aaaa"]]'),
        T("even_palindrome", "s = \"abba\"", 'sorted(partition("abba"))', 'vec![vec!["a", "b", "b", "a"], vec!["a", "bb", "a"], vec!["abba"]]'),
        T("nested_palindromes", "s = \"racecar\"", 'sorted(partition("racecar"))',
          'vec![vec!["r", "a", "c", "e", "c", "a", "r"], vec!["r", "a", "cec", "a", "r"], vec!["r", "aceca", "r"], vec!["racecar"]]'),
        T("two_different", "s = \"ab\"", 'partition("ab")', 'vec![vec!["a", "b"]]'),
        T("ends_match_but_not_a_palindrome", "s = \"abca\"", 'partition("abca")', 'vec![vec!["a", "b", "c", "a"]]'),
        T("sixteen_distinct", "s = \"abcdefghijklmnop\"", 'partition("abcdefghijklmnop").len()', "1"),
        T("pieces_rebuild_s", "s = \"aabbaab\", every split joins back to s", 'partition("aabbaab").iter().all(|p| p.concat() == "aabbaab")', "true"),
        T("abcba", "s = \"abcba\"", 'sorted(partition("abcba"))', 'vec![vec!["a", "b", "c", "b", "a"], vec!["a", "bcb", "a"], vec!["abcba"]]'),
        """
        #[test]
        fn random_vs_every_cut_set() {
            let mut rng = anneal_prelude::Rng::new(1130);
            for _ in 0..300 {
                let n = rng.int(1, 10) as usize;
                let alphabet = *rng.pick(&["ab", "abc", "a"]);
                let s = rng.string(n, alphabet);
                // Each bit of `cuts` says whether s is cut after that position.
                let mut want: Vec<Vec<&str>> = Vec::new();
                for cuts in 0u32..1 << (n - 1) {
                    let (mut pieces, mut start) = (Vec::new(), 0);
                    for i in 0..n {
                        if i == n - 1 || cuts >> i & 1 == 1 {
                            pieces.push(&s[start..=i]);
                            start = i + 1;
                        }
                    }
                    if pieces.iter().all(|p| p.bytes().eq(p.bytes().rev())) {
                        want.push(pieces);
                    }
                }
                want.sort();
                check!(format!("s = {s:?}"), sorted(partition(&s)), want);
            }
        }

        #[test]
        fn scale_sixteen_equal() {
            let s = "a".repeat(16);
            let got = partition(&s);
            check!("s = 16 × \\"a\\"", (got.len(), got.iter().all(|p| p.concat() == s)), (32_768, true));
        }
        """,
    ],
    wrong=dict(
        only_the_ends_compared="""
            pub fn partition(s: &str) -> Vec<Vec<&str>> {
                fn go<'a>(s: &'a str, start: usize, path: &mut Vec<&'a str>, out: &mut Vec<Vec<&'a str>>) {
                    if start == s.len() {
                        out.push(path.clone());
                        return;
                    }
                    let b = s.as_bytes();
                    for end in start + 1..=s.len() {
                        if b[start] == b[end - 1] {
                            path.push(&s[start..end]);
                            go(s, end, path, out);
                            path.pop();
                        }
                    }
                }
                let mut out = Vec::new();
                go(s, 0, &mut Vec::new(), &mut out);
                out
            }
        """,
        nothing_for_empty="""
            pub fn partition(s: &str) -> Vec<Vec<&str>> {
                fn go<'a>(s: &'a str, start: usize, path: &mut Vec<&'a str>, out: &mut Vec<Vec<&'a str>>) {
                    if start == s.len() {
                        out.push(path.clone());
                        return;
                    }
                    for end in start + 1..=s.len() {
                        let piece = &s[start..end];
                        if piece.bytes().eq(piece.bytes().rev()) {
                            path.push(piece);
                            go(s, end, path, out);
                            path.pop();
                        }
                    }
                }
                if s.is_empty() {
                    return Vec::new();
                }
                let mut out = Vec::new();
                go(s, 0, &mut Vec::new(), &mut out);
                out
            }
        """,
    ),
    hints=[("approach", "From position `start`, try every end where `s[start..end]` is a palindrome, push that piece, recurse from `end`, pop. Reaching the end of `s` completes a split."),
           ("rust", "`fn go<'a>(s: &'a str, start: usize, path: &mut Vec<&'a str>, out: &mut Vec<Vec<&'a str>>)`: the lifetime says the pieces borrow from `s`, so no piece is copied."),
           ("edge case", "Precompute `pal[i][j]` bottom-up (s[i] == s[j] and the inside is a palindrome) so each check is O(1). The empty string has one split: `[[]]`.")],
    notes=("A string of n letters has 2ⁿ⁻¹ ways to cut it, and in the worst case (all letters equal) every one is an answer, so the "
           "output is exponential. The palindrome table makes each piece's check O(1); returning `&str` slices avoids copying pieces.",
           "O(n · 2ⁿ)", "O(n²) for the table, O(n) recursion"),
    follow_up="Find the minimum number of cuts instead of listing every split. Which DP does that need (D12)?",
    related=["D12", "L3"],
))

P.append(dict(
    slug="restore-ip-addresses", title="Restore IP addresses", level="medium", stage="choices-grids", tags=["backtracking", "String", "pruning"],
    companies=["Meta", "Apple", "Amazon", "Google", "Microsoft"],
    teaches=["A fixed depth (four parts) with a small choice at each level (1 to 3 digits).",
             "Prune on length: the digits left must fit in the parts left."],
    statement="""
        `s` holds only digits. Insert three dots into `s` to make a valid IPv4 address: four parts, each a number from 0 to
        255 written without leading zeros (`0` is fine, `00` and `01` are not). Every digit must be used, in order.

        Return every valid address you can make. They can come in any order; return `[]` if there are none.
    """,
    examples=[("s = \"25525511135\"", "[\"255.255.11.135\", \"255.255.111.35\"]"), ("s = \"0000\"", "[\"0.0.0.0\"]")],
    constraints=["1 ≤ s.len() ≤ 20", "s holds only ASCII digits"],
    starter="""
        pub fn restore_ip_addresses(s: &str) -> Vec<String> {
            todo!()
        }
    """,
    solution="""
        pub fn restore_ip_addresses(s: &str) -> Vec<String> {
            fn go<'a>(rest: &'a str, parts: &mut Vec<&'a str>, out: &mut Vec<String>) {
                let left = 4 - parts.len();
                if left == 0 {
                    if rest.is_empty() {
                        out.push(parts.join("."));
                    }
                    return;
                }
                // Each remaining part takes 1 to 3 digits.
                if rest.len() < left || rest.len() > 3 * left {
                    return;
                }
                for len in 1..=rest.len().min(3) {
                    let part = &rest[..len];
                    // A longer part would keep the leading zero or be larger still.
                    if (len > 1 && part.starts_with('0')) || part.parse::<u16>().is_ok_and(|v| v > 255) {
                        break;
                    }
                    parts.push(part);
                    go(&rest[len..], parts, out);
                    parts.pop();
                }
            }
            let mut out = Vec::new();
            go(s, &mut Vec::with_capacity(4), &mut out);
            out
        }
    """,
    visible=[
        SORTED,
        T("leetcode_two_answers", "s = \"25525511135\"", 'sorted(restore_ip_addresses("25525511135"))', 'vec!["255.255.11.135", "255.255.111.35"]'),
        T("leetcode_zeros", "s = \"0000\"", 'restore_ip_addresses("0000")', 'vec!["0.0.0.0"]'),
        T("leetcode_five_answers", "s = \"101023\"", 'sorted(restore_ip_addresses("101023"))', 'vec!["1.0.10.23", "1.0.102.3", "10.1.0.23", "10.10.2.3", "101.0.2.3"]'),
        T("too_short", "s = \"123\"", 'restore_ip_addresses("123")', "Vec::<String>::new()"),
        T("no_leading_zeros", "s = \"010010\"", 'sorted(restore_ip_addresses("010010"))', 'vec!["0.10.0.10", "0.100.1.0"]'),
    ],
    hidden=[
        SORTED,
        T("ones", "s = \"1111\"", 'restore_ip_addresses("1111")', 'vec!["1.1.1.1"]'),
        T("all_255", "s = \"255255255255\"", 'restore_ip_addresses("255255255255")', 'vec!["255.255.255.255"]'),
        T("part_256_is_too_big", "s = \"256256256256\"", 'restore_ip_addresses("256256256256")', "Vec::<String>::new()"),
        T("thirteen_digits", "s = \"1231231231234\"", 'restore_ip_addresses("1231231231234")', "Vec::<String>::new()"),
        T("twenty_digits", "s = 20 digits", 'restore_ip_addresses("12345678901234567890")', "Vec::<String>::new()"),
        T("zero_then_256", "s = \"000256\"", 'restore_ip_addresses("000256")', "Vec::<String>::new()"),
        T("home_router", "s = \"19216811\"", 'sorted(restore_ip_addresses("19216811"))',
          'vec!["1.92.168.11", "19.2.168.11", "19.21.68.11", "19.216.8.11", "19.216.81.1", "192.1.68.11", "192.16.8.11", "192.16.81.1", "192.168.1.1"]'),
        T("five_ones", "s = \"11111\"", 'sorted(restore_ip_addresses("11111"))', 'vec!["1.1.1.11", "1.1.11.1", "1.11.1.1", "11.1.1.1"]'),
        T("hundreds", "s = \"100100\"", 'sorted(restore_ip_addresses("100100"))', 'vec!["1.0.0.100", "10.0.10.0", "100.1.0.0"]'),
        T("single_digit", "s = \"5\"", 'restore_ip_addresses("5")', "Vec::<String>::new()"),
        """
        #[test]
        fn random_vs_three_cut_points() {
            let valid = |p: &str| !p.is_empty() && p.len() <= 3 && (p == "0" || !p.starts_with('0')) && p.parse::<u32>().unwrap() <= 255;
            let mut rng = anneal_prelude::Rng::new(1131);
            for _ in 0..400 {
                let n = rng.int(1, 13) as usize;
                let digits = *rng.pick(&["0125", "0123456789", "12", "0"]);
                let s = rng.string(n, digits);
                let mut want = Vec::new();
                for i in 1..n {
                    for j in i + 1..n {
                        for k in j + 1..n {
                            let parts = [&s[..i], &s[i..j], &s[j..k], &s[k..]];
                            if parts.iter().all(|p| valid(p)) {
                                want.push(parts.join("."));
                            }
                        }
                    }
                }
                want.sort();
                check!(format!("s = {s:?}"), sorted(restore_ip_addresses(&s)), want);
            }
        }
        """,
    ],
    wrong=dict(
        leading_zeros_allowed="""
            pub fn restore_ip_addresses(s: &str) -> Vec<String> {
                fn go(rest: &str, parts: &mut Vec<String>, out: &mut Vec<String>) {
                    if parts.len() == 4 {
                        if rest.is_empty() {
                            out.push(parts.join("."));
                        }
                        return;
                    }
                    for len in 1..=rest.len().min(3) {
                        let part = &rest[..len];
                        if part.parse::<u16>().unwrap() > 255 {
                            break;
                        }
                        parts.push(part.to_string());
                        go(&rest[len..], parts, out);
                        parts.pop();
                    }
                }
                let mut out = Vec::new();
                go(s, &mut Vec::new(), &mut out);
                out
            }
        """,
        any_three_digits="""
            pub fn restore_ip_addresses(s: &str) -> Vec<String> {
                fn go(rest: &str, parts: &mut Vec<String>, out: &mut Vec<String>) {
                    if parts.len() == 4 {
                        if rest.is_empty() {
                            out.push(parts.join("."));
                        }
                        return;
                    }
                    for len in 1..=rest.len().min(3) {
                        let part = &rest[..len];
                        if len > 1 && part.starts_with('0') {
                            break;
                        }
                        parts.push(part.to_string());
                        go(&rest[len..], parts, out);
                        parts.pop();
                    }
                }
                let mut out = Vec::new();
                go(s, &mut Vec::new(), &mut out);
                out
            }
        """,
    ),
    hints=[("approach", "Choose the parts one at a time: 1, 2 or 3 digits each. After four parts, keep the address only if every digit was used."),
           ("rust", "Recurse on the remaining `&str` and collect parts as `&str` slices in a `Vec`; `parts.join(\".\")` builds the answer."),
           ("edge case", "`0` is a valid part but `00` and `012` are not, and a three-digit part must be at most 255. If the digits left can't fill the parts left (1 to 3 each), stop early.")],
    notes=("There are at most 3⁴ = 81 ways to choose the part lengths, so the search is constant-sized; the length check stops long "
           "inputs (up to 20 digits) before any work.", "O(1): at most 81 leaves", "O(1) besides the output"),
    follow_up="How would you do the same for IPv6, with hex groups and the `::` shorthand?",
    related=["S2", "D2"],
))

P.append(dict(
    slug="fix-recursive-closure-grid", title="Fix: recursive closure can't borrow the grid mutably", mode="fix", level="medium", stage="choices-grids",
    tags=["closures", "inner fn", "E0425", "grid"],
    teaches=["A closure can't call itself: it has no name inside its own body.",
             "Even if it could, a closure that mutates `grid` holds `&mut grid` for as long as it lives, so nothing else may read `grid` meanwhile (E0502).",
             "An inner `fn` with the grid as an explicit `&mut` parameter borrows it only for each call."],
    statement="""
        `island_sizes` should return the size of every island (1s joined up, down, left or right) in the order each
        island's first cell appears reading row by row. The flood fill that sinks an island was written as a closure so it
        could see `grid` without taking it as a parameter. It doesn't compile.

        Rewrite `sink_island` as an inner `fn` that takes the grid as an explicit `&mut` parameter. Keep the recursion.
    """,
    examples=[("grid = [[1, 1, 0], [0, 1, 0], [0, 0, 1]]", "[3, 1]")],
    constraints=["0 ≤ rows, cols ≤ 50, every row the same length", "cells are 0 or 1"],
    starter="""
        /// The size of every island of 1s, in the order their first cells appear row by row.
        pub fn island_sizes(mut grid: Vec<Vec<u8>>) -> Vec<usize> {
            let (h, w) = (grid.len(), grid.first().map_or(0, Vec::len));
            // Sinks the island through (r, c) and returns how many cells it had.
            let mut sink_island = |r: usize, c: usize| -> usize {
                if r >= h || c >= w || grid[r][c] == 0 {
                    return 0;
                }
                grid[r][c] = 0;
                1 + sink_island(r + 1, c) + sink_island(r.wrapping_sub(1), c) + sink_island(r, c + 1) + sink_island(r, c.wrapping_sub(1))
            };
            let mut sizes = Vec::new();
            for r in 0..h {
                for c in 0..w {
                    if grid[r][c] == 1 {
                        sizes.push(sink_island(r, c));
                    }
                }
            }
            sizes
        }
    """,
    solution="""
        /// The size of every island of 1s, in the order their first cells appear row by row.
        pub fn island_sizes(mut grid: Vec<Vec<u8>>) -> Vec<usize> {
            let (h, w) = (grid.len(), grid.first().map_or(0, Vec::len));
            // Sinks the island through (r, c) and returns how many cells it had.
            fn sink_island(grid: &mut [Vec<u8>], r: usize, c: usize) -> usize {
                if r >= grid.len() || c >= grid[r].len() || grid[r][c] == 0 {
                    return 0;
                }
                grid[r][c] = 0;
                1 + sink_island(grid, r + 1, c) + sink_island(grid, r.wrapping_sub(1), c) + sink_island(grid, r, c + 1) + sink_island(grid, r, c.wrapping_sub(1))
            }
            let mut sizes = Vec::new();
            for r in 0..h {
                for c in 0..w {
                    if grid[r][c] == 1 {
                        sizes.push(sink_island(&mut grid, r, c));
                    }
                }
            }
            sizes
        }
    """,
    rules=dict(types=["RefCell", "Cell", "Rc", "Box"], lines=6),
    visible=[
        T("two_islands", "grid = [[1, 1, 0], [0, 1, 0], [0, 0, 1]]", "island_sizes(vec![vec![1, 1, 0], vec![0, 1, 0], vec![0, 0, 1]])", "vec![3, 1]"),
        T("no_land", "grid = [[0, 0], [0, 0]]", "island_sizes(vec![vec![0, 0], vec![0, 0]])", "Vec::<usize>::new()"),
        T("empty_grid", "grid = []", "island_sizes(Vec::new())", "Vec::<usize>::new()"),
        T("diagonals_do_not_join", "grid = [[1, 0], [0, 1]]", "island_sizes(vec![vec![1, 0], vec![0, 1]])", "vec![1, 1]"),
        T("order_of_first_cells", "grid = [[0, 0, 1], [1, 0, 0], [1, 0, 0]]", "island_sizes(vec![vec![0, 0, 1], vec![1, 0, 0], vec![1, 0, 0]])", "vec![1, 2]"),
    ],
    hidden=[
        T("single_cell", "grid = [[1]]", "island_sizes(vec![vec![1]])", "vec![1]"),
        T("u_shape", "grid = [[1, 0, 1], [1, 0, 1], [1, 1, 1]]", "island_sizes(vec![vec![1, 0, 1], vec![1, 0, 1], vec![1, 1, 1]])", "vec![7]"),
        T("ring_around_a_dot", "grid = 5×5 ring of 1s with a 1 in the middle",
          "island_sizes(vec![vec![1, 1, 1, 1, 1], vec![1, 0, 0, 0, 1], vec![1, 0, 1, 0, 1], vec![1, 0, 0, 0, 1], vec![1, 1, 1, 1, 1]])", "vec![16, 1]"),
        T("single_row", "grid = [[1, 1, 0, 1, 0, 1, 1, 1]]", "island_sizes(vec![vec![1, 1, 0, 1, 0, 1, 1, 1]])", "vec![2, 1, 3]"),
        T("single_column", "grid = [[1], [0], [1], [1]]", "island_sizes(vec![vec![1], vec![0], vec![1], vec![1]])", "vec![1, 2]"),
        T("rows_of_nothing", "grid = [[], []]", "island_sizes(vec![vec![], vec![]])", "Vec::<usize>::new()"),
        T("reaches_back_up", "grid = [[0, 1], [0, 1], [1, 1]]: the island's first cell is (0, 1)", "island_sizes(vec![vec![0, 1], vec![0, 1], vec![1, 1]])", "vec![4]"),
        T("full_50x50", "grid = 50×50 of 1", "island_sizes(vec![vec![1; 50]; 50])", "vec![2500]"),
        T("checkerboard_50x50", "grid = 50×50 checkerboard", "island_sizes((0..50).map(|r| (0..50).map(|c| ((r + c) % 2 == 0) as u8).collect()).collect())", "vec![1; 1250]"),
        """
        #[test]
        fn random_vs_breadth_first_labels() {
            let mut rng = anneal_prelude::Rng::new(1132);
            for _ in 0..300 {
                let (h, w) = (rng.int(1, 8) as usize, rng.int(1, 8) as usize);
                let grid: Vec<Vec<u8>> = (0..h).map(|_| rng.vec(w, 0, 1)).collect();
                let mut seen = vec![vec![false; w]; h];
                let mut want = Vec::new();
                for r in 0..h {
                    for c in 0..w {
                        if grid[r][c] == 1 && !seen[r][c] {
                            seen[r][c] = true;
                            let mut queue = std::collections::VecDeque::from([(r, c)]);
                            let mut size = 0;
                            while let Some((a, b)) = queue.pop_front() {
                                size += 1;
                                for (x, y) in [(a.wrapping_sub(1), b), (a + 1, b), (a, b.wrapping_sub(1)), (a, b + 1)] {
                                    if x < h && y < w && grid[x][y] == 1 && !seen[x][y] {
                                        seen[x][y] = true;
                                        queue.push_back((x, y));
                                    }
                                }
                            }
                            want.push(size);
                        }
                    }
                }
                check!(format!("grid = {grid:?}"), island_sizes(grid.clone()), want);
            }
        }

        #[test]
        fn scale_snake_50x50() {
            // Rows of land joined at alternating ends: one island of 1275 cells, 1275 calls deep.
            let grid: Vec<Vec<u8>> = (0..50)
                .map(|r| (0..50).map(|c| if r % 2 == 0 || (r % 4 == 1 && c == 49) || (r % 4 == 3 && c == 0) { 1 } else { 0 }).collect())
                .collect();
            check!("grid = 50×50 snake", island_sizes(grid), vec![1275]);
        }
        """,
    ],
    wrong=dict(
        eight_neighbours="""
            /// The size of every island of 1s, in the order their first cells appear row by row.
            pub fn island_sizes(mut grid: Vec<Vec<u8>>) -> Vec<usize> {
                let (h, w) = (grid.len(), grid.first().map_or(0, Vec::len));
                fn sink_island(grid: &mut [Vec<u8>], r: usize, c: usize) -> usize {
                    if r >= grid.len() || c >= grid[r].len() || grid[r][c] == 0 {
                        return 0;
                    }
                    grid[r][c] = 0;
                    let mut size = 1;
                    for (dr, dc) in [(-1i32, -1i32), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)] {
                        size += sink_island(grid, (r as i32 + dr) as usize, (c as i32 + dc) as usize);
                    }
                    size
                }
                let mut sizes = Vec::new();
                for r in 0..h {
                    for c in 0..w {
                        if grid[r][c] == 1 {
                            sizes.push(sink_island(&mut grid, r, c));
                        }
                    }
                }
                sizes
            }
        """,
        sorted_by_size="""
            /// The size of every island of 1s, in the order their first cells appear row by row.
            pub fn island_sizes(mut grid: Vec<Vec<u8>>) -> Vec<usize> {
                let (h, w) = (grid.len(), grid.first().map_or(0, Vec::len));
                fn sink_island(grid: &mut [Vec<u8>], r: usize, c: usize) -> usize {
                    if r >= grid.len() || c >= grid[r].len() || grid[r][c] == 0 {
                        return 0;
                    }
                    grid[r][c] = 0;
                    1 + sink_island(grid, r + 1, c) + sink_island(grid, r.wrapping_sub(1), c) + sink_island(grid, r, c + 1) + sink_island(grid, r, c.wrapping_sub(1))
                }
                let mut sizes = Vec::new();
                for r in 0..h {
                    for c in 0..w {
                        if grid[r][c] == 1 {
                            sizes.push(sink_island(&mut grid, r, c));
                        }
                    }
                }
                sizes.sort_unstable_by(|a, b| b.cmp(a));
                sizes
            }
        """,
    ),
    hints=[("rust", "Inside its own body a closure has no name, so `sink_island(..)` can't resolve (E0425). An inner `fn` can call itself, but it can't capture anything: `grid` must become a parameter."),
           ("approach", "`fn sink_island(grid: &mut [Vec<u8>], r: usize, c: usize) -> usize`, bounds-checked with `grid.len()` and `grid[r].len()`, called as `sink_island(&mut grid, r, c)`."),
           ("edge case", "Out-of-range steps use `wrapping_sub(1)`, which turns row 0 into `usize::MAX`: the bounds check rejects it.")],
    notes=("A closure's captured `&mut grid` lives as long as the closure, so even a non-recursive version would block the loop's "
           "`grid[r][c]` read (E0502). With `grid` as a parameter, each call reborrows it just for that call, and the loop is free to "
           "read it between calls. Each cell is sunk once.", "O(rows · cols)", "O(rows · cols) recursion depth in the worst case"),
    follow_up="When would you switch to an explicit `Vec` stack instead of recursion, and what does it cost?",
    related=["L6", "D9"],
))

STAGES = [
    ("recursion", "Recursion", "easy"),
    ("first-backtracking", "First backtracking", "easy"),
    ("choices-grids", "Choices & grids", "medium"),
]

if __name__ == "__main__":
    n = write_track("d11-recursion-backtracking", "D11", "Recursion & backtracking", "D", "core", 12,
                    "Recursion first (base cases, trusting the call, divide and conquer), then backtracking: choose, recurse, undo, and prune.",
                    STAGES, P)
    print("D11", n)
