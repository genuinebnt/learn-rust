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

# ---------------------------------------------------------------------------------------------------------------------
# Stage 4 · Constraints & pruning (hard): bitmask constraints, most-constrained-first, sort-desc and symmetry cuts, memo
# on the used set, and dead-end tables that keep a search output-sensitive.
# ---------------------------------------------------------------------------------------------------------------------

# A board is n rows of n cells, one queen per row and column, no two on a diagonal.
QUEENS = """
fn valid(n: usize, board: &[String]) -> bool {
    if board.len() != n {
        return false;
    }
    let mut queens = Vec::new(); // (row, column)
    for (r, row) in board.iter().enumerate() {
        if row.len() != n || row.bytes().any(|b| b != b'.' && b != b'Q') || row.matches('Q').count() != 1 {
            return false;
        }
        queens.push((r, row.find('Q').unwrap()));
    }
    queens.iter().enumerate().all(|(i, &(r1, c1))| queens[i + 1..].iter().all(|&(r2, c2)| c1 != c2 && r2 - r1 != c1.abs_diff(c2)))
}
"""

# Every permutation of columns, kept when no two queens share a diagonal: the reference for n ≤ 8.
QUEENS_BRUTE = """
fn brute(n: usize) -> Vec<Vec<usize>> {
    fn go(n: usize, cols: &mut Vec<usize>, out: &mut Vec<Vec<usize>>) {
        if cols.len() == n {
            if (0..n).all(|i| (i + 1..n).all(|j| cols[i].abs_diff(cols[j]) != j - i)) {
                out.push(cols.clone());
            }
            return;
        }
        for c in 0..n {
            if !cols.contains(&c) {
                cols.push(c);
                go(n, cols, out);
                cols.pop();
            }
        }
    }
    let mut out = Vec::new();
    go(n, &mut Vec::new(), &mut out);
    out
}
"""

P.append(dict(
    slug="n-queens", title="N-Queens (bitmasks)", level="hard", stage="constraints-pruning", tags=["backtracking", "bitmask", "pruning"],
    companies=["Apple", "Amazon", "Google", "Microsoft", "Bloomberg"],
    teaches=["Prune as you place: a queen goes only on a square no earlier queen attacks, so dead boards are never built.",
             "Three `u16` masks (columns and both diagonals) make \"which squares are free?\" one expression; shifting the "
             "diagonal masks by one moves them down a row."],
    statement="""
        Place `n` queens on an `n × n` chessboard so that no two attack each other: no two share a row, a column or a
        diagonal. Return every such placement.

        Write each board as `n` strings, one per row from the top, with `Q` for the queen and `.` for an empty square.
        The boards can come in any order.

        `n` goes up to 12. Trying every arrangement and checking it at the end is far too slow there: check each queen
        as you place it.
    """,
    examples=[("n = 4", "[[\".Q..\", \"...Q\", \"Q...\", \"..Q.\"], [\"..Q.\", \"Q...\", \"...Q\", \".Q..\"]]"), ("n = 1", "[[\"Q\"]]")],
    constraints=["1 ≤ n ≤ 12"],
    starter="""
        pub fn solve_n_queens(n: usize) -> Vec<Vec<String>> {
            todo!()
        }
    """,
    solution="""
        pub fn solve_n_queens(n: usize) -> Vec<Vec<String>> {
            // Bit c of each mask is column c of the row being filled. `cols`: columns already taken. `diag` / `anti`:
            // squares attacked along the two diagonals by the queens above.
            fn place(full: u16, cols: u16, diag: u16, anti: u16, queens: &mut Vec<usize>, out: &mut Vec<Vec<String>>) {
                if cols == full {
                    let n = queens.len();
                    out.push(queens.iter().map(|&q| (0..n).map(|c| if c == q { 'Q' } else { '.' }).collect()).collect());
                    return;
                }
                let mut free = full & !(cols | diag | anti);
                while free != 0 {
                    let bit = free & free.wrapping_neg(); // the lowest free column
                    free ^= bit;
                    queens.push(bit.trailing_zeros() as usize);
                    // One row down, a diagonal attack moves one column right (<< 1), an anti-diagonal one left (>> 1).
                    place(full, cols | bit, (diag | bit) << 1, (anti | bit) >> 1, queens, out);
                    queens.pop();
                }
            }
            let full = ((1u32 << n) - 1) as u16;
            let mut out = Vec::new();
            place(full, 0, 0, 0, &mut Vec::with_capacity(n), &mut out);
            out
        }
    """,
    visible=[
        SORTED,
        QUEENS,
        T("leetcode_four", "n = 4", "sorted(solve_n_queens(4))", 'vec![vec!["..Q.", "Q...", "...Q", ".Q.."], vec![".Q..", "...Q", "Q...", "..Q."]]'),
        T("leetcode_one", "n = 1", "solve_n_queens(1)", 'vec![vec!["Q"]]'),
        T("two_has_none", "n = 2", "solve_n_queens(2)", "Vec::<Vec<String>>::new()"),
        T("three_has_none", "n = 3", "solve_n_queens(3)", "Vec::<Vec<String>>::new()"),
        T("five_has_ten", "n = 5: (boards, all valid)", "{ let all = solve_n_queens(5); (all.len(), all.iter().all(|b| valid(5, b))) }", "(10, true)"),
        T("six_exactly", "n = 6", "sorted(solve_n_queens(6))",
          'vec![vec!["....Q.", "..Q...", "Q.....", ".....Q", "...Q..", ".Q...."], vec!["...Q..", "Q.....", "....Q.", ".Q....", ".....Q", "..Q..."], '
          'vec!["..Q...", ".....Q", ".Q....", "....Q.", "Q.....", "...Q.."], vec![".Q....", "...Q..", ".....Q", "Q.....", "..Q...", "....Q."]]'),
    ],
    hidden=[
        SORTED,
        QUEENS,
        QUEENS_BRUTE,
        T("one", "n = 1", "solve_n_queens(1)", 'vec![vec!["Q"]]'),
        T("two", "n = 2", "solve_n_queens(2).len()", "0"),
        T("three", "n = 3", "solve_n_queens(3).len()", "0"),
        T("four_rows_are_n_long", "n = 4: every row has 4 cells", "solve_n_queens(4).iter().flatten().all(|row| row.len() == 4)", "true"),
        T("seven", "n = 7: (boards, all valid)", "{ let all = solve_n_queens(7); (all.len(), all.iter().all(|b| valid(7, b))) }", "(40, true)"),
        T("eight_distinct", "n = 8: (distinct boards, all valid)",
          "{ let mut all = solve_n_queens(8); let ok = all.iter().all(|b| valid(8, b)); all.sort(); all.dedup(); (all.len(), ok) }", "(92, true)"),
        T("nine", "n = 9", "solve_n_queens(9).len()", "352"),
        T("ten", "n = 10: (boards, all valid)", "{ let all = solve_n_queens(10); (all.len(), all.iter().all(|b| valid(10, b))) }", "(724, true)"),
        T("eleven", "n = 11", "solve_n_queens(11).len()", "2680"),
        """
        #[test]
        fn every_n_up_to_8_vs_permutations() {
            for n in 1..=8 {
                let want: Vec<Vec<String>> = brute(n)
                    .into_iter()
                    .map(|cols| cols.iter().map(|&q| (0..n).map(|c| if c == q { 'Q' } else { '.' }).collect()).collect())
                    .collect();
                check!(format!("n = {n}"), sorted(solve_n_queens(n)), sorted(want));
            }
        }

        #[test]
        fn scale_twelve() {
            let mut all = solve_n_queens(12);
            let ok = all.iter().all(|b| valid(12, b));
            all.sort();
            all.dedup();
            check!("n = 12: (distinct boards, all valid)", (all.len(), ok), (14200, true));
        }
        """,
    ],
    wrong=dict(
        checks_at_the_leaf="""
            pub fn solve_n_queens(n: usize) -> Vec<Vec<String>> {
                fn go(n: usize, queens: &mut Vec<usize>, taken: &mut Vec<bool>, out: &mut Vec<Vec<String>>) {
                    if queens.len() == n {
                        if (0..n).all(|i| (i + 1..n).all(|j| queens[i].abs_diff(queens[j]) != j - i)) {
                            out.push(queens.iter().map(|&q| (0..n).map(|c| if c == q { 'Q' } else { '.' }).collect()).collect());
                        }
                        return;
                    }
                    for c in 0..n {
                        if !taken[c] {
                            taken[c] = true;
                            queens.push(c);
                            go(n, queens, taken, out);
                            queens.pop();
                            taken[c] = false;
                        }
                    }
                }
                let mut out = Vec::new();
                go(n, &mut Vec::new(), &mut vec![false; n], &mut out);
                out
            }
        """,
        one_diagonal_only="""
            pub fn solve_n_queens(n: usize) -> Vec<Vec<String>> {
                fn place(full: u16, cols: u16, diag: u16, queens: &mut Vec<usize>, out: &mut Vec<Vec<String>>) {
                    if cols == full {
                        let n = queens.len();
                        out.push(queens.iter().map(|&q| (0..n).map(|c| if c == q { 'Q' } else { '.' }).collect()).collect());
                        return;
                    }
                    let mut free = full & !(cols | diag);
                    while free != 0 {
                        let bit = free & free.wrapping_neg();
                        free ^= bit;
                        queens.push(bit.trailing_zeros() as usize);
                        place(full, cols | bit, (diag | bit) << 1, queens, out);
                        queens.pop();
                    }
                }
                let full = ((1u32 << n) - 1) as u16;
                let mut out = Vec::new();
                place(full, 0, 0, &mut Vec::new(), &mut out);
                out
            }
        """,
    ),
    hints=[("approach", "Fill the board row by row, one queen per row. Keep which columns and which diagonals are already attacked, and "
                        "only try the free squares; a row with no free square is a dead end."),
           ("rust", "With `u16` masks, the free columns are `full & !(cols | diag | anti)`. Take the lowest with `free & free.wrapping_neg()`, "
                    "its column is `trailing_zeros()`, and the next row gets `(diag | bit) << 1` and `(anti | bit) >> 1`."),
           ("edge case", "n = 2 and n = 3 have no solution: return an empty `Vec`, not a board.")],
    notes=("One queen per row turns the search into choosing a column per row. The masks say, for the next row, which columns are "
           "attacked from above: straight down (`cols`), and along each diagonal, which drifts one column per row, hence the shifts. "
           "Every branch the search enters holds a valid partial board, so the work is proportional to the partial boards, not to "
           "all nⁿ arrangements. Syntax to remember: `x & x.wrapping_neg()` isolates the lowest set bit, `x ^= bit` clears it.",
           "O(n!) placements at most; far fewer in practice", "O(n) recursion depth besides the output"),
    follow_up="Why is `u16` enough here, and what changes to reach n = 32 or n = 64?",
    related=["D13"],
))

P.append(dict(
    slug="n-queens-ii", title="N-Queens II", level="hard", stage="constraints-pruning", tags=["backtracking", "bitmask", "symmetry"],
    companies=["Amazon", "Google", "Microsoft"],
    teaches=["When only the count matters, drop the boards: the search state is three masks passed by value.",
             "Mirror symmetry halves the work: a solution with the first queen in column c mirrors one with it in column n - 1 - c."],
    statement="""
        Return how many ways there are to place `n` queens on an `n × n` chessboard so that no two attack each other (no two
        in the same row, column or diagonal).

        `n` goes up to 14 (365 596 solutions). Checking a new queen against every earlier queen is too slow there: each
        check has to be O(1).
    """,
    examples=[("n = 4", "2"), ("n = 1", "1"), ("n = 8", "92")],
    constraints=["1 ≤ n ≤ 14"],
    starter="""
        pub fn total_n_queens(n: usize) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn total_n_queens(n: usize) -> usize {
            // `cols`, `diag`, `anti`: the columns of the next row attacked from above (see N-Queens).
            fn count(full: u16, cols: u16, diag: u16, anti: u16) -> usize {
                if cols == full {
                    return 1;
                }
                let mut free = full & !(cols | diag | anti);
                let mut total = 0;
                while free != 0 {
                    let bit = free & free.wrapping_neg();
                    free ^= bit;
                    total += count(full, cols | bit, (diag | bit) << 1, (anti | bit) >> 1);
                }
                total
            }
            let full = ((1u32 << n) - 1) as u16;
            let first_row = |c: usize| {
                let bit = 1u16 << c;
                count(full, bit, bit << 1, bit >> 1)
            };
            // The mirror image of a solution is a solution: count the left half of the first row twice,
            // and the middle column (odd n) once.
            let half: usize = (0..n / 2).map(first_row).sum();
            2 * half + if n % 2 == 1 { first_row(n / 2) } else { 0 }
        }
    """,
    visible=[
        T("leetcode_four", "n = 4", "total_n_queens(4)", "2"),
        T("leetcode_one", "n = 1", "total_n_queens(1)", "1"),
        T("two_has_none", "n = 2", "total_n_queens(2)", "0"),
        T("three_has_none", "n = 3", "total_n_queens(3)", "0"),
        T("five_is_odd", "n = 5 (odd: the middle column counts once)", "total_n_queens(5)", "10"),
        T("eight_queens", "n = 8", "total_n_queens(8)", "92"),
    ],
    hidden=[
        QUEENS_BRUTE,
        T("one", "n = 1", "total_n_queens(1)", "1"),
        T("six", "n = 6", "total_n_queens(6)", "4"),
        T("seven", "n = 7", "total_n_queens(7)", "40"),
        T("nine", "n = 9", "total_n_queens(9)", "352"),
        T("ten", "n = 10", "total_n_queens(10)", "724"),
        T("eleven", "n = 11", "total_n_queens(11)", "2680"),
        T("twelve", "n = 12", "total_n_queens(12)", "14200"),
        T("thirteen", "n = 13", "total_n_queens(13)", "73712"),
        """
        #[test]
        fn every_n_up_to_8_vs_permutations() {
            for n in 1..=8 {
                check!(format!("n = {n}"), total_n_queens(n), brute(n).len());
            }
        }

        #[test]
        fn scale_fourteen() {
            check!("n = 14", total_n_queens(14), 365_596);
        }
        """,
    ],
    wrong=dict(
        scans_earlier_queens="""
            pub fn total_n_queens(n: usize) -> usize {
                fn go(n: usize, queens: &mut Vec<usize>) -> usize {
                    let row = queens.len();
                    if row == n {
                        return 1;
                    }
                    let mut total = 0;
                    for c in 0..n {
                        if queens.iter().enumerate().all(|(r, &q)| q != c && q.abs_diff(c) != row - r) {
                            queens.push(c);
                            total += go(n, queens);
                            queens.pop();
                        }
                    }
                    total
                }
                go(n, &mut Vec::new())
            }
        """,
        doubles_the_middle_column="""
            pub fn total_n_queens(n: usize) -> usize {
                fn count(full: u16, cols: u16, diag: u16, anti: u16) -> usize {
                    if cols == full {
                        return 1;
                    }
                    let mut free = full & !(cols | diag | anti);
                    let mut total = 0;
                    while free != 0 {
                        let bit = free & free.wrapping_neg();
                        free ^= bit;
                        total += count(full, cols | bit, (diag | bit) << 1, (anti | bit) >> 1);
                    }
                    total
                }
                let full = ((1u32 << n) - 1) as u16;
                (0..(n + 1) / 2).map(|c| 2 * count(full, 1 << c, 1 << c << 1, 1 << c >> 1)).sum()
            }
        """,
    ),
    hints=[("approach", "The same search as N-Queens, returning a count: 1 when every row has a queen, otherwise the sum over the free "
                        "columns of the next row."),
           ("rust", "Pass the three `u16` masks by value, so there's nothing to undo. `free.count_ones()` tells you how many "
                    "columns are left to try."),
           ("edge case", "If you use the mirror trick, the middle column of an odd board is its own mirror: count it once, not twice.")],
    notes=("Masks make each placement O(1), so the cost is the number of partial boards the search visits; scanning the earlier "
           "queens instead multiplies every step by up to n. Reflecting a board left to right maps solutions to solutions and "
           "moves the first-row queen from column c to n - 1 - c, so counting the first half of the first row and doubling it "
           "halves the work.",
           "O(n!) at most; far fewer in practice", "O(n) recursion depth"),
    follow_up="The board also has rotational symmetry. How would you count only one board of each symmetry class?",
    related=["D13"],
))

def rows9(cells):
    """81 cells → nine rows separated by spaces, the form the Sudoku tests read and print."""
    assert len(cells) == 81, cells
    return " ".join(cells[i:i + 9] for i in range(0, 81, 9))


SUDOKU_LC = rows9("53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79")
SUDOKU_LC_SOLVED = rows9("534678912672195348198342567859761423426853791713924856961537284287419635345286179")
# Arto Inkala's "AI Escargot" and "Easter Monster": few forced moves, long chains of guesses.
SUDOKU_ESCARGOT = rows9("1....7.9..3..2...8..96..5....53..9...1..8...26....4...3......1..4......7..7...3..")
SUDOKU_ESCARGOT_SOLVED = rows9("162857493534129678789643521475312986913586742628794135356478219241935867897261354")
SUDOKU_EASTER = rows9("1.......2.9.4...5...6...7...5.9.3.......7.......85..4.7.....6...3...9.8...2.....1")
SUDOKU_EASTER_SOLVED = rows9("174385962293467158586192734451923876928674315367851249719548623635219487842736591")
# Built against reading-order backtracking: the first row's answer is 987654321, so it tries nearly every value first.
SUDOKU_ANTI = rows9("..............3.85..1.2.......5.7.....4...1...9.......5......73..2.1........4...9")
SUDOKU_ANTI_SOLVED = rows9("987654321246173985351928746128537694634892157795461832519286473472319568863745219")
# The same puzzle with one more given that doesn't clash with any other but leaves no solution.
SUDOKU_ANTI_DEAD_A = rows9("..............3.85..1.2.......5.7.....4...1...9.......5......73..2.1........4.5.9")
SUDOKU_ANTI_DEAD_B = rows9("..............3.85..1.2.......5.7.....4...1...9.......5......73..2.1...4....4...9")
SUDOKU_EMPTY = rows9("." * 81)

SUDOKU = """
/// Nine rows of nine cells separated by spaces; `.` is an empty cell.
fn grid(s: &str) -> [[u8; 9]; 9] {
    let cells: Vec<u8> = s.bytes().filter(|&b| b != b' ').map(|b| if b == b'.' { 0 } else { b - b'0' }).collect();
    assert_eq!(cells.len(), 81, "a board has 81 cells");
    let mut board = [[0; 9]; 9];
    for (i, d) in cells.into_iter().enumerate() {
        board[i / 9][i % 9] = d;
    }
    board
}

fn show(board: &[[u8; 9]; 9]) -> String {
    let rows: Vec<String> = board.iter().map(|row| row.iter().map(|&d| if d == 0 { '.' } else { (b'0' + d) as char }).collect()).collect();
    rows.join(" ")
}

/// Solves the puzzle: (the returned flag, the board afterwards).
fn run(puzzle: &str) -> (bool, String) {
    let mut board = grid(puzzle);
    let ok = solve_sudoku(&mut board);
    (ok, show(&board))
}

/// `board` is full, every row, column and box holds 1–9 once, and the givens of `puzzle` are still there.
fn completes(puzzle: &[[u8; 9]; 9], board: &[[u8; 9]; 9]) -> bool {
    let mut seen = [[0u16; 9]; 3];
    for r in 0..9 {
        for c in 0..9 {
            let d = board[r][c];
            if !(1..=9).contains(&d) || (puzzle[r][c] != 0 && puzzle[r][c] != d) {
                return false;
            }
            for (unit, i) in [(0, r), (1, c), (2, r / 3 * 3 + c / 3)] {
                if seen[unit][i] >> d & 1 == 1 {
                    return false;
                }
                seen[unit][i] |= 1 << d;
            }
        }
    }
    true
}
"""

SUDOKU_HIDDEN_TESTS = """
/// Reading-order backtracking that checks a digit by scanning its row, column and box.
fn brute(board: &mut [[u8; 9]; 9]) -> bool {
    fn fits(b: &[[u8; 9]; 9], r: usize, c: usize, d: u8) -> bool {
        (0..9).all(|i| b[r][i] != d && b[i][c] != d && b[r / 3 * 3 + i / 3][c / 3 * 3 + i % 3] != d)
    }
    fn go(b: &mut [[u8; 9]; 9], i: usize) -> bool {
        if i == 81 {
            return true;
        }
        let (r, c) = (i / 9, i % 9);
        if b[r][c] != 0 {
            return go(b, i + 1);
        }
        for d in 1..=9 {
            if fits(b, r, c, d) {
                b[r][c] = d;
                if go(b, i + 1) {
                    return true;
                }
            }
        }
        b[r][c] = 0;
        false
    }
    for r in 0..9 {
        for c in 0..9 {
            let d = board[r][c];
            if d != 0 {
                board[r][c] = 0;
                let alone = fits(board, r, c, d);
                board[r][c] = d;
                if !alone {
                    return false;
                }
            }
        }
    }
    go(board, 0)
}

/// A random full grid: the pattern (3·(r % 3) + r / 3 + c) % 9 with bands, rows, stacks, columns and digits shuffled.
fn random_grid(rng: &mut anneal_prelude::Rng) -> [[u8; 9]; 9] {
    fn order(rng: &mut anneal_prelude::Rng) -> Vec<usize> {
        let mut bands = vec![0, 1, 2];
        rng.shuffle(&mut bands);
        let mut out = Vec::new();
        for band in bands {
            let mut inner = vec![0, 1, 2];
            rng.shuffle(&mut inner);
            out.extend(inner.into_iter().map(|i| band * 3 + i));
        }
        out
    }
    let rows = order(rng);
    let cols = order(rng);
    let mut digits: Vec<u8> = (1..=9).collect();
    rng.shuffle(&mut digits);
    let mut board = [[0; 9]; 9];
    for r in 0..9 {
        for c in 0..9 {
            let (a, b) = (rows[r], cols[c]);
            board[r][c] = digits[(3 * (a % 3) + a / 3 + b) % 9];
        }
    }
    board
}

#[test]
fn random_vs_reading_order() {
    let mut rng = anneal_prelude::Rng::new(1133);
    for _ in 0..150 {
        let mut puzzle = random_grid(&mut rng);
        let blanks = rng.int(0, 50) as usize;
        let mut cells: Vec<usize> = (0..81).collect();
        rng.shuffle(&mut cells);
        for &i in &cells[..blanks] {
            puzzle[i / 9][i % 9] = 0;
        }
        if rng.below(3) == 0 {
            // Overwrite a given: usually a clash, sometimes a puzzle with no solution or a different one.
            let at = rng.int(blanks as i64, 80) as usize;
            let i = cells[at];
            puzzle[i / 9][i % 9] = rng.int(1, 9) as u8;
        }
        let mut reference = puzzle;
        let solvable = brute(&mut reference);
        let mut board = puzzle;
        let ok = solve_sudoku(&mut board);
        let kept = if ok { completes(&puzzle, &board) } else { board == puzzle };
        check!(format!("board = {}", show(&puzzle)), (ok, kept), (solvable, true));
    }
}

#[test]
fn scale_against_reading_order() {
    check!("board = @ANTI@", run("@ANTI@"), (true, "@ANTI_SOLVED@".to_string()));
    check!("board = @DEAD_A@", run("@DEAD_A@"), (false, "@DEAD_A@".to_string()));
    check!("board = @DEAD_B@", run("@DEAD_B@"), (false, "@DEAD_B@".to_string()));
}
""".replace("@ANTI_SOLVED@", SUDOKU_ANTI_SOLVED).replace("@ANTI@", SUDOKU_ANTI).replace("@DEAD_A@", SUDOKU_ANTI_DEAD_A).replace("@DEAD_B@", SUDOKU_ANTI_DEAD_B)


def sudoku_case(name, desc, puzzle, want_ok, after):
    return T(name, f"board = {puzzle}{desc}", f'run("{puzzle}")', f'({str(want_ok).lower()}, "{after}".to_string())')


def blank_one(solved, index):
    cells = solved.replace(" ", "")
    return rows9(cells[:index] + "." + cells[index + 1:])


def put(cells_rows, index, digit):
    cells = cells_rows.replace(" ", "")
    return rows9(cells[:index] + digit + cells[index + 1:])


SUDOKU_ROW_CLASH = put(put(SUDOKU_EMPTY, 0, "5"), 4, "5")
SUDOKU_NO_ROOM = rows9("12345678." + "........9" + "." * 63)
SUDOKU_BOX_CLASH = put(put(SUDOKU_EMPTY, 0, "5"), 10, "5")
SUDOKU_COL_CLASH = put(put(SUDOKU_EMPTY, 3, "7"), 48, "7")
# LeetCode's solution with a few cells cleared and one given changed to clash with its column.
SUDOKU_LATE_CLASH = put(blank_one(blank_one(SUDOKU_LC_SOLVED, 40), 70), 80, "8")

P.append(dict(
    slug="sudoku-solver", title="Sudoku solver", level="hard", stage="constraints-pruning", tags=["backtracking", "bitmask", "pruning"],
    companies=["Apple", "Amazon", "Google", "Microsoft", "Uber", "DoorDash"],
    teaches=["Constraint bookkeeping: a `u16` of used digits per row, column and box gives any cell's candidates in one expression.",
             "Most constrained cell first: always branch on the empty cell with the fewest candidates, so forced moves cost nothing and "
             "dead ends show up at once."],
    statement="""
        `board` is a 9 × 9 Sudoku: `1` to `9` are given digits and `0` is an empty cell. Fill every empty cell so that each
        row, each column and each of the nine 3 × 3 boxes holds the digits 1 to 9 once each, and return `true`.

        If that's impossible, including when two givens already clash, return `false` and leave `board` as it was. When a
        puzzle has more than one solution, any one of them is accepted.

        The tests include puzzles built to defeat backtracking that fills cells in reading order: pick the next cell with
        more care.
    """,
    examples=[("board = LeetCode's example: 53..7.... 6..195... .98....6. 8...6...3 4..8.3..1 7...2...6 .6....28. ...419..5 ....8..79 (. = 0)",
               "true; board = 534678912 672195348 198342567 859761423 426853791 713924856 961537284 287419635 345286179"),
              ("board = 5...5.... then eight empty rows", "false; board unchanged (two 5s in the first row)")],
    constraints=["`board` is 9 × 9, every cell 0 to 9", "the givens may clash, and the puzzle may have no solution or several"],
    starter="""
        pub fn solve_sudoku(board: &mut [[u8; 9]; 9]) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn solve_sudoku(board: &mut [[u8; 9]; 9]) -> bool {
            const DIGITS: u16 = 0b11_1111_1110; // bits 1 to 9

            fn box_of(r: usize, c: usize) -> usize {
                r / 3 * 3 + c / 3
            }

            // used[0][row], used[1][column], used[2][box]: bit d is set when digit d is already there.
            fn search(board: &mut [[u8; 9]; 9], used: &mut [[u16; 9]; 3]) -> bool {
                // The empty cell with the fewest candidates. One candidate is forced, none is a dead end: stop looking.
                let mut best: Option<(usize, usize, u16)> = None;
                'scan: for r in 0..9 {
                    for c in 0..9 {
                        if board[r][c] != 0 {
                            continue;
                        }
                        let free = DIGITS & !(used[0][r] | used[1][c] | used[2][box_of(r, c)]);
                        if best.is_none_or(|(_, _, f)| free.count_ones() < f.count_ones()) {
                            best = Some((r, c, free));
                            if free.count_ones() <= 1 {
                                break 'scan;
                            }
                        }
                    }
                }
                let Some((r, c, mut free)) = best else {
                    return true; // no empty cell left
                };
                let units = [(0, r), (1, c), (2, box_of(r, c))];
                while free != 0 {
                    let bit = free & free.wrapping_neg();
                    free ^= bit;
                    board[r][c] = bit.trailing_zeros() as u8;
                    for (u, i) in units {
                        used[u][i] ^= bit;
                    }
                    if search(board, used) {
                        return true;
                    }
                    for (u, i) in units {
                        used[u][i] ^= bit;
                    }
                }
                board[r][c] = 0; // leave the cell as it was found
                false
            }

            let mut used = [[0u16; 9]; 3];
            for (r, row) in board.iter().enumerate() {
                for (c, &d) in row.iter().enumerate() {
                    if d == 0 {
                        continue;
                    }
                    let bit = 1 << d;
                    let units = [(0, r), (1, c), (2, box_of(r, c))];
                    if units.iter().any(|&(u, i)| used[u][i] & bit != 0) {
                        return false; // two givens clash
                    }
                    for (u, i) in units {
                        used[u][i] |= bit;
                    }
                }
            }
            search(board, &mut used)
        }
    """,
    visible=[
        SUDOKU,
        sudoku_case("leetcode_example", "", SUDOKU_LC, True, SUDOKU_LC_SOLVED),
        sudoku_case("already_solved", " (nothing to fill)", SUDOKU_LC_SOLVED, True, SUDOKU_LC_SOLVED),
        sudoku_case("one_blank", " (one empty cell)", blank_one(SUDOKU_LC_SOLVED, 40), True, SUDOKU_LC_SOLVED),
        sudoku_case("givens_clash", " (two 5s in the first row)", SUDOKU_ROW_CLASH, False, SUDOKU_ROW_CLASH),
        sudoku_case("no_digit_fits", " (the first row's last cell needs a 9, and its column has one)", SUDOKU_NO_ROOM, False, SUDOKU_NO_ROOM),
        T("empty_board", "board = all 0: (returned flag, board is a valid fill)",
          "{ let mut board = [[0; 9]; 9]; let ok = solve_sudoku(&mut board); (ok, completes(&[[0; 9]; 9], &board)) }", "(true, true)"),
    ],
    hidden=[
        SUDOKU,
        sudoku_case("box_clash", " (two 5s in the top-left box, different rows and columns)", SUDOKU_BOX_CLASH, False, SUDOKU_BOX_CLASH),
        sudoku_case("column_clash", " (two 7s in the fourth column)", SUDOKU_COL_CLASH, False, SUDOKU_COL_CLASH),
        sudoku_case("clash_among_many_givens", " (the last given repeats a digit of its row and column)", SUDOKU_LATE_CLASH, False, SUDOKU_LATE_CLASH),
        sudoku_case("ai_escargot", "", SUDOKU_ESCARGOT, True, SUDOKU_ESCARGOT_SOLVED),
        sudoku_case("easter_monster", "", SUDOKU_EASTER, True, SUDOKU_EASTER_SOLVED),
        sudoku_case("last_cell_blank", " (only the bottom-right cell is empty)", blank_one(SUDOKU_LC_SOLVED, 80), True, SUDOKU_LC_SOLVED),
        sudoku_case("first_cell_blank", " (only the top-left cell is empty)", blank_one(SUDOKU_LC_SOLVED, 0), True, SUDOKU_LC_SOLVED),
        T("one_given_row", "board = 123456789 then eight empty rows: (returned flag, board is a valid fill)",
          '{ let puzzle = grid("123456789 ' + " ".join(["........."] * 8) + '"); let mut board = puzzle; let ok = solve_sudoku(&mut board); (ok, completes(&puzzle, &board)) }',
          "(true, true)"),
        T("empty_board", "board = all 0: (returned flag, board is a valid fill)",
          "{ let mut board = [[0; 9]; 9]; let ok = solve_sudoku(&mut board); (ok, completes(&[[0; 9]; 9], &board)) }", "(true, true)"),
        SUDOKU_HIDDEN_TESTS,
    ],
    wrong=dict(
        reading_order="""
            pub fn solve_sudoku(board: &mut [[u8; 9]; 9]) -> bool {
                fn box_of(r: usize, c: usize) -> usize {
                    r / 3 * 3 + c / 3
                }
                fn search(board: &mut [[u8; 9]; 9], i: usize, used: &mut [[u16; 9]; 3]) -> bool {
                    if i == 81 {
                        return true;
                    }
                    let (r, c) = (i / 9, i % 9);
                    if board[r][c] != 0 {
                        return search(board, i + 1, used);
                    }
                    for d in 1..=9u8 {
                        let bit = 1u16 << d;
                        if (used[0][r] | used[1][c] | used[2][box_of(r, c)]) & bit != 0 {
                            continue;
                        }
                        board[r][c] = d;
                        used[0][r] ^= bit;
                        used[1][c] ^= bit;
                        used[2][box_of(r, c)] ^= bit;
                        if search(board, i + 1, used) {
                            return true;
                        }
                        used[0][r] ^= bit;
                        used[1][c] ^= bit;
                        used[2][box_of(r, c)] ^= bit;
                    }
                    board[r][c] = 0;
                    false
                }
                let mut used = [[0u16; 9]; 3];
                for r in 0..9 {
                    for c in 0..9 {
                        let d = board[r][c];
                        if d == 0 {
                            continue;
                        }
                        let bit = 1 << d;
                        if (used[0][r] | used[1][c] | used[2][box_of(r, c)]) & bit != 0 {
                            return false;
                        }
                        used[0][r] |= bit;
                        used[1][c] |= bit;
                        used[2][box_of(r, c)] |= bit;
                    }
                }
                search(board, 0, &mut used)
            }
        """,
        trusts_the_givens="""
            pub fn solve_sudoku(board: &mut [[u8; 9]; 9]) -> bool {
                const DIGITS: u16 = 0b11_1111_1110;
                fn box_of(r: usize, c: usize) -> usize {
                    r / 3 * 3 + c / 3
                }
                fn search(board: &mut [[u8; 9]; 9], used: &mut [[u16; 9]; 3]) -> bool {
                    let mut best: Option<(usize, usize, u16)> = None;
                    for r in 0..9 {
                        for c in 0..9 {
                            if board[r][c] != 0 {
                                continue;
                            }
                            let free = DIGITS & !(used[0][r] | used[1][c] | used[2][box_of(r, c)]);
                            if best.is_none_or(|(_, _, f)| free.count_ones() < f.count_ones()) {
                                best = Some((r, c, free));
                            }
                        }
                    }
                    let Some((r, c, mut free)) = best else {
                        return true;
                    };
                    let units = [(0, r), (1, c), (2, box_of(r, c))];
                    while free != 0 {
                        let bit = free & free.wrapping_neg();
                        free ^= bit;
                        board[r][c] = bit.trailing_zeros() as u8;
                        for (u, i) in units {
                            used[u][i] ^= bit;
                        }
                        if search(board, used) {
                            return true;
                        }
                        for (u, i) in units {
                            used[u][i] ^= bit;
                        }
                    }
                    board[r][c] = 0;
                    false
                }
                let mut used = [[0u16; 9]; 3];
                for r in 0..9 {
                    for c in 0..9 {
                        let d = board[r][c];
                        if d != 0 {
                            for (u, i) in [(0, r), (1, c), (2, box_of(r, c))] {
                                used[u][i] |= 1 << d;
                            }
                        }
                    }
                }
                search(board, &mut used)
            }
        """,
        leaves_guesses_behind="""
            pub fn solve_sudoku(board: &mut [[u8; 9]; 9]) -> bool {
                const DIGITS: u16 = 0b11_1111_1110;
                fn box_of(r: usize, c: usize) -> usize {
                    r / 3 * 3 + c / 3
                }
                fn search(board: &mut [[u8; 9]; 9], used: &mut [[u16; 9]; 3]) -> bool {
                    let mut best: Option<(usize, usize, u16)> = None;
                    for r in 0..9 {
                        for c in 0..9 {
                            if board[r][c] != 0 {
                                continue;
                            }
                            let free = DIGITS & !(used[0][r] | used[1][c] | used[2][box_of(r, c)]);
                            if best.is_none_or(|(_, _, f)| free.count_ones() < f.count_ones()) {
                                best = Some((r, c, free));
                            }
                        }
                    }
                    let Some((r, c, mut free)) = best else {
                        return true;
                    };
                    let units = [(0, r), (1, c), (2, box_of(r, c))];
                    // Search a copy of the masks, so there's nothing to undo in them.
                    while free != 0 {
                        let bit = free & free.wrapping_neg();
                        free ^= bit;
                        board[r][c] = bit.trailing_zeros() as u8;
                        let mut next = *used;
                        for (u, i) in units {
                            next[u][i] |= bit;
                        }
                        if search(board, &mut next) {
                            return true;
                        }
                    }
                    false
                }
                let mut used = [[0u16; 9]; 3];
                for r in 0..9 {
                    for c in 0..9 {
                        let d = board[r][c];
                        if d == 0 {
                            continue;
                        }
                        let bit = 1 << d;
                        let units = [(0, r), (1, c), (2, box_of(r, c))];
                        if units.iter().any(|&(u, i)| used[u][i] & bit != 0) {
                            return false;
                        }
                        for (u, i) in units {
                            used[u][i] |= bit;
                        }
                    }
                }
                search(board, &mut used)
            }
        """,
    ),
    hints=[("approach", "Keep, for each row, column and box, which digits are used. Then repeatedly pick the empty cell with the fewest "
                        "candidates, try each, recurse, and undo. Check the givens against each other before you start."),
           ("rust", "`[[u16; 9]; 3]` holds the used digits (bit d = digit d). A cell's candidates are "
                    "`0b11_1111_1110 & !(rows[r] | cols[c] | boxes[b])`, and `count_ones()` ranks the cells."),
           ("edge case", "On `false` the board must be unchanged: set a guessed cell back to 0 when every candidate has failed.")],
    notes=("Branching on the most constrained cell (the minimum-remaining-values rule) makes forced cells free and finds a "
           "contradiction, a cell with no candidates, before any more guesses stack on top of it. Reading-order search has no such "
           "guard: on a puzzle built against it, it enumerates millions of first-row prefixes. The masks make each candidate "
           "test a few bit operations instead of 27 cell reads. Syntax to remember: a labelled `break 'scan` leaves both loops.",
           "exponential in the worst case; a few thousand nodes on hard puzzles", "O(81) recursion depth, O(1) masks"),
    follow_up="Add constraint propagation: when a digit fits in only one cell of a row, column or box, place it at once. How much "
              "does the search shrink?",
    related=["D13"],
))

P.append(dict(
    slug="matchsticks-to-square", title="Matchsticks to square", level="hard", stage="constraints-pruning", tags=["backtracking", "pruning", "sort"],
    companies=["Amazon", "Google", "Microsoft"],
    teaches=["Order the choices so failures come early: placing the longest sticks first cuts dead branches near the root.",
             "Symmetry pruning: sides with the same current length are interchangeable, so try only the first of them."],
    statement="""
        `matchsticks[i]` is the length of a matchstick. Use every matchstick exactly once, without breaking any, to make
        the four sides of a square. Sticks can be joined end to end within a side. Return `true` if it can be done.

        Lengths go up to 10⁹ and there can be 20 sticks, so the total doesn't fit in a `u32`. The tests include inputs
        where trying the sticks in the given order takes far too long.
    """,
    examples=[("matchsticks = [1, 1, 2, 2, 2]", "true (sides 2, 2, 1+1, 2)"), ("matchsticks = [3, 3, 3, 3, 4]", "false")],
    constraints=["1 ≤ matchsticks.len() ≤ 20", "1 ≤ matchsticks[i] ≤ 10⁹"],
    starter="""
        pub fn makesquare(matchsticks: &[u32]) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn makesquare(matchsticks: &[u32]) -> bool {
            fn place(sticks: &[u64], sides: &mut [u64; 4], side: u64) -> bool {
                let Some((&stick, rest)) = sticks.split_first() else {
                    return true; // every stick placed and no side over `side`: all four are exactly `side`
                };
                for i in 0..4 {
                    // A side as long as an earlier one would repeat that side's subtree.
                    if sides[i] + stick > side || sides[..i].contains(&sides[i]) {
                        continue;
                    }
                    sides[i] += stick;
                    if place(rest, sides, side) {
                        return true;
                    }
                    sides[i] -= stick;
                }
                false
            }
            let mut sticks: Vec<u64> = matchsticks.iter().map(|&m| u64::from(m)).collect();
            let total: u64 = sticks.iter().sum();
            if sticks.len() < 4 || !total.is_multiple_of(4) {
                return false;
            }
            // Longest first: they have the fewest places to go, so a dead end shows up near the root.
            sticks.sort_unstable_by(|a, b| b.cmp(a));
            let side = total / 4;
            sticks[0] <= side && place(&sticks, &mut [0; 4], side)
        }
    """,
    visible=[
        T("leetcode_square", "matchsticks = [1, 1, 2, 2, 2]", "makesquare(&[1, 1, 2, 2, 2])", "true"),
        T("leetcode_no_square", "matchsticks = [3, 3, 3, 3, 4]", "makesquare(&[3, 3, 3, 3, 4])", "false"),
        T("four_equal", "matchsticks = [7, 7, 7, 7]", "makesquare(&[7, 7, 7, 7])", "true"),
        T("too_few_sticks", "matchsticks = [4, 4, 4] (total 12, but only three sticks)", "makesquare(&[4, 4, 4])", "false"),
        T("stick_longer_than_a_side", "matchsticks = [1, 1, 1, 9] (side would be 3)", "makesquare(&[1, 1, 1, 9])", "false"),
        T("total_divides_but_no_split", "matchsticks = [3, 3, 3, 3, 2, 2] (side 4: each 3 needs a 1)", "makesquare(&[3, 3, 3, 3, 2, 2])", "false"),
    ],
    hidden=[
        T("single", "matchsticks = [1]", "makesquare(&[1])", "false"),
        T("four_ones", "matchsticks = [1, 1, 1, 1]", "makesquare(&[1, 1, 1, 1])", "true"),
        T("total_not_divisible", "matchsticks = [1, 1, 1, 1, 1]", "makesquare(&[1, 1, 1, 1, 1])", "false"),
        T("three_per_side", "matchsticks = [5, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3]", "makesquare(&[5, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3])", "true"),
        T("leetcode_fifteen", "matchsticks = [5, 5, 5, 5, 16, 4, 4, 4, 4, 4, 3, 3, 3, 3, 4]",
          "makesquare(&[5, 5, 5, 5, 16, 4, 4, 4, 4, 4, 3, 3, 3, 3, 4])", "false"),
        T("first_fit_fails", "matchsticks = [13, 13, 6, 4, 6, 2, 5, 3] (side 13: 6+4+3 and 6+5+2)", "makesquare(&[13, 13, 6, 4, 6, 2, 5, 3])", "true"),
        T("total_past_u32", "matchsticks = [10⁹; 16] (total 1.6·10¹⁰)", "makesquare(&[1_000_000_000; 16])", "true"),
        T("total_past_u32_no_square", "matchsticks = [10⁹; 16] + [4]", "makesquare(&[vec![1_000_000_000; 16], vec![4]].concat())", "false"),
        T("unsorted_input", "matchsticks = [2, 1, 2, 1, 2, 2, 1, 1]", "makesquare(&[2, 1, 2, 1, 2, 2, 1, 1])", "true"),
        """
        /// Every way to give each stick one of the four sides.
        fn brute(sticks: &[u32]) -> bool {
            (0..1usize << (2 * sticks.len())).any(|code| {
                let mut sides = [0u64; 4];
                for (i, &s) in sticks.iter().enumerate() {
                    sides[code >> (2 * i) & 3] += u64::from(s);
                }
                sides[0] > 0 && sides.iter().all(|&x| x == sides[0])
            })
        }

        #[test]
        fn random_vs_every_assignment() {
            let mut rng = anneal_prelude::Rng::new(1134);
            for _ in 0..300 {
                let mut sticks: Vec<u32> = Vec::new();
                if rng.bool() {
                    let n = rng.int(1, 7) as usize;
                    sticks = rng.vec(n, 1, 6);
                } else {
                    // Four equal sides, some cut in two, sometimes with one stick made longer.
                    let side = rng.int(2, 9) as u32;
                    for _ in 0..4 {
                        let cut = rng.int(0, side as i64 - 1) as u32;
                        if cut > 0 && sticks.len() < 5 {
                            sticks.push(cut);
                            sticks.push(side - cut);
                        } else {
                            sticks.push(side);
                        }
                    }
                    if rng.bool() {
                        let i = rng.below(sticks.len());
                        sticks[i] += 1;
                    }
                    rng.shuffle(&mut sticks);
                }
                check!(format!("matchsticks = {sticks:?}"), makesquare(&sticks), brute(&sticks));
            }
        }

        #[test]
        fn scale_twenty_sticks_no_square() {
            let sticks = [28, 318, 921, 8, 630, 3, 814, 403, 630, 379, 135, 834, 70, 36, 2, 47, 43, 918, 888, 913];
            check!(format!("matchsticks = {sticks:?}"), makesquare(&sticks), false);
        }

        #[test]
        fn scale_twenty_sticks_square() {
            let sticks = [856, 133, 296, 248, 751, 605, 757, 480, 14, 204, 644, 412, 860, 37, 138, 82, 10, 332, 771, 106];
            check!(format!("matchsticks = {sticks:?}"), makesquare(&sticks), true);
        }
        """,
    ],
    wrong=dict(
        given_order="""
            pub fn makesquare(matchsticks: &[u32]) -> bool {
                fn place(sticks: &[u64], sides: &mut [u64; 4], side: u64) -> bool {
                    let Some((&stick, rest)) = sticks.split_first() else {
                        return true;
                    };
                    for i in 0..4 {
                        if sides[i] + stick > side || sides[..i].contains(&sides[i]) {
                            continue;
                        }
                        sides[i] += stick;
                        if place(rest, sides, side) {
                            return true;
                        }
                        sides[i] -= stick;
                    }
                    false
                }
                let sticks: Vec<u64> = matchsticks.iter().map(|&m| u64::from(m)).collect();
                let total: u64 = sticks.iter().sum();
                if sticks.len() < 4 || total % 4 != 0 {
                    return false;
                }
                let side = total / 4;
                sticks.iter().all(|&s| s <= side) && place(&sticks, &mut [0; 4], side)
            }
        """,
        sums_in_u32="""
            pub fn makesquare(matchsticks: &[u32]) -> bool {
                fn place(sticks: &[u32], sides: &mut [u32; 4], side: u32) -> bool {
                    let Some((&stick, rest)) = sticks.split_first() else {
                        return true;
                    };
                    for i in 0..4 {
                        if sides[i] + stick > side || sides[..i].contains(&sides[i]) {
                            continue;
                        }
                        sides[i] += stick;
                        if place(rest, sides, side) {
                            return true;
                        }
                        sides[i] -= stick;
                    }
                    false
                }
                let mut sticks = matchsticks.to_vec();
                let total: u32 = sticks.iter().sum();
                if sticks.len() < 4 || total % 4 != 0 {
                    return false;
                }
                sticks.sort_unstable_by(|a, b| b.cmp(a));
                let side = total / 4;
                sticks[0] <= side && place(&sticks, &mut [0; 4], side)
            }
        """,
        first_fit_no_backtracking="""
            pub fn makesquare(matchsticks: &[u32]) -> bool {
                let mut sticks: Vec<u64> = matchsticks.iter().map(|&m| u64::from(m)).collect();
                let total: u64 = sticks.iter().sum();
                if sticks.len() < 4 || total % 4 != 0 {
                    return false;
                }
                sticks.sort_unstable_by(|a, b| b.cmp(a));
                let side = total / 4;
                let mut sides = [0u64; 4];
                for s in sticks {
                    match sides.iter_mut().find(|x| **x + s <= side) {
                        Some(x) => *x += s,
                        None => return false,
                    }
                }
                true
            }
        """,
    ),
    hints=[("approach", "Place the sticks one at a time into one of four sides, never letting a side exceed total / 4, and backtrack "
                        "on failure. Check first that there are at least four sticks and that the total divides by 4."),
           ("rust", "Sum in `u64` (`u64::from(m)`), sort with `sort_unstable_by(|a, b| b.cmp(a))`, and skip side `i` when "
                    "`sides[..i].contains(&sides[i])`."),
           ("edge case", "Greedy first-fit is not enough: for [13, 13, 6, 4, 6, 2, 5, 3] it puts 6 and 6 together and gets stuck, "
                         "though 6+4+3 and 6+5+2 both make 13.")],
    notes=("The search gives each stick one of four sides, so it's 4ⁿ in the worst case. Two cuts make it fast: sorting longest "
           "first, because a long stick fits in few places and a failure is found high in the tree instead of after every "
           "short stick is placed; and skipping a side whose length equals an earlier side's, which would only repeat that "
           "subtree (an empty side is the common case). Once every stick is placed with no side over total / 4, all four "
           "sides are exactly total / 4.",
           "O(4ⁿ) worst case; far less with the cuts", "O(n) recursion depth"),
    follow_up="Solve it with a DP over subsets of sticks in O(n · 2ⁿ). Which approach wins for n = 20?",
    related=["D12"],
))

P.append(dict(
    slug="partition-to-k-equal-subsets", title="Partition to K equal sum subsets", level="hard", stage="constraints-pruning",
    tags=["backtracking", "bitmask", "memoization"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "LinkedIn"],
    teaches=["Fill one bucket at a time: the set of used numbers then fixes everything else, so it can be memoised as a bitmask.",
             "Two cheaper cuts on top: an empty bucket always takes the largest unused number, and equal numbers are tried once per spot."],
    statement="""
        Return `true` if `nums` can be split into `k` non-empty groups with equal sums, every number in exactly one group.

        There can be 20 numbers and many repeats. The tests include inputs where plain backtracking, which retries equal
        numbers and never remembers a failed state, takes far too long.
    """,
    examples=[("nums = [4, 3, 2, 3, 5, 2, 1], k = 4", "true ([5], [1, 4], [2, 3], [2, 3])"), ("nums = [1, 2, 3, 4], k = 3", "false")],
    constraints=["1 ≤ k ≤ nums.len() ≤ 20", "1 ≤ nums[i] ≤ 10⁴"],
    starter="""
        pub fn can_partition_k_subsets(nums: &[u32], k: usize) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn can_partition_k_subsets(nums: &[u32], k: usize) -> bool {
            // `used`: which numbers are in a bucket. The open bucket holds (sum of used) % target, so `used` is the
            // whole state, and a state that failed once fails every time: `dead` remembers it.
            fn fill(nums: &[u32], target: u32, used: u32, open: u32, dead: &mut [bool]) -> bool {
                if used == (1 << nums.len()) - 1 {
                    return true;
                }
                if dead[used as usize] {
                    return false;
                }
                let mut tried = 0; // equal numbers lead to the same states: try the first one only
                for i in 0..nums.len() {
                    if used >> i & 1 == 1 || nums[i] == tried || open + nums[i] > target {
                        continue;
                    }
                    if fill(nums, target, used | 1 << i, (open + nums[i]) % target, dead) {
                        return true;
                    }
                    tried = nums[i];
                    if open == 0 {
                        break; // the largest unused number belongs to some bucket: this one is as good as any
                    }
                }
                dead[used as usize] = true;
                false
            }
            let total: u32 = nums.iter().sum();
            if !total.is_multiple_of(k as u32) {
                return false;
            }
            let target = total / k as u32;
            let mut nums = nums.to_vec();
            nums.sort_unstable_by(|a, b| b.cmp(a));
            nums[0] <= target && fill(&nums, target, 0, 0, &mut vec![false; 1 << nums.len()])
        }
    """,
    visible=[
        T("leetcode_four_groups", "nums = [4, 3, 2, 3, 5, 2, 1], k = 4", "can_partition_k_subsets(&[4, 3, 2, 3, 5, 2, 1], 4)", "true"),
        T("leetcode_no_split", "nums = [1, 2, 3, 4], k = 3", "can_partition_k_subsets(&[1, 2, 3, 4], 3)", "false"),
        T("one_group", "nums = [5, 1], k = 1", "can_partition_k_subsets(&[5, 1], 1)", "true"),
        T("each_its_own_group", "nums = [2, 2, 2, 2], k = 4", "can_partition_k_subsets(&[2, 2, 2, 2], 4)", "true"),
        T("number_bigger_than_a_group", "nums = [10, 1, 1], k = 2 (each group would sum to 6)", "can_partition_k_subsets(&[10, 1, 1], 2)", "false"),
        T("sum_divides_but_no_split", "nums = [1, 5, 5, 5], k = 2 (groups of 8)", "can_partition_k_subsets(&[1, 5, 5, 5], 2)", "false"),
    ],
    hidden=[
        T("single", "nums = [7], k = 1", "can_partition_k_subsets(&[7], 1)", "true"),
        T("leetcode_fives", "nums = [2, 2, 2, 2, 3, 4, 5], k = 4", "can_partition_k_subsets(&[2, 2, 2, 2, 3, 4, 5], 4)", "false"),
        T("leetcode_thirties", "nums = [10, 10, 10, 7, 7, 7, 7, 7, 7, 6, 6, 6], k = 3",
          "can_partition_k_subsets(&[10, 10, 10, 7, 7, 7, 7, 7, 7, 6, 6, 6], 3)", "true"),
        T("leetcode_mixed", "nums = [4, 15, 1, 1, 1, 1, 3, 11, 1, 10], k = 3", "can_partition_k_subsets(&[4, 15, 1, 1, 1, 1, 3, 11, 1, 10], 3)", "true"),
        T("leetcode_nine_groups", "nums = [3, 2, 1, 3, 6, 1, 4, 8, 10, 8, 9, 1, 7, 9, 8, 1], k = 9",
          "can_partition_k_subsets(&[3, 2, 1, 3, 6, 1, 4, 8, 10, 8, 9, 1, 7, 9, 8, 1], 9)", "false"),
        T("first_fit_fails", "nums = [6, 4, 6, 2, 5, 3], k = 2 (6+4+3 and 6+5+2)", "can_partition_k_subsets(&[6, 4, 6, 2, 5, 3], 2)", "true"),
        T("pairs", "nums = [1, 1, 1, 1, 2, 2, 2, 2], k = 4", "can_partition_k_subsets(&[1, 1, 1, 1, 2, 2, 2, 2], 4)", "true"),
        T("twenty_ones", "nums = [1; 20], k = 20", "can_partition_k_subsets(&[1; 20], 20)", "true"),
        T("big_values", "nums = [10⁴; 20], k = 5", "can_partition_k_subsets(&[10_000; 20], 5)", "true"),
        T("not_divisible", "nums = [1; 20], k = 3", "can_partition_k_subsets(&[1; 20], 3)", "false"),
        """
        /// Every way to give each number one of the k groups.
        fn brute(nums: &[u32], k: usize) -> bool {
            (0..k.pow(nums.len() as u32)).any(|mut code| {
                let mut sums = vec![0u32; k];
                for &x in nums {
                    sums[code % k] += x;
                    code /= k;
                }
                sums.iter().all(|&s| s == sums[0])
            })
        }

        #[test]
        fn random_vs_every_assignment() {
            let mut rng = anneal_prelude::Rng::new(1135);
            for _ in 0..300 {
                let n = rng.int(1, 8) as usize;
                let hi = if rng.bool() { 4 } else { 9 };
                let nums: Vec<u32> = rng.vec(n, 1, hi);
                let k = rng.int(1, n.min(4) as i64) as usize;
                check!(format!("nums = {nums:?}, k = {k}"), can_partition_k_subsets(&nums, k), brute(&nums, k));
            }
        }

        #[test]
        fn scale_repeats_and_parity() {
            // Groups of 9 each need one of the two 1s, and there are four groups.
            let nums = [vec![2; 17], vec![1, 1]].concat();
            check!("nums = [2; 17] + [1, 1], k = 4", can_partition_k_subsets(&nums, 4), false);
        }

        #[test]
        fn scale_twenty_distinct() {
            let nums: Vec<u32> = (1..=20).collect();
            check!("nums = 1..=20, k = 7", can_partition_k_subsets(&nums, 7), true);
        }
        """,
    ],
    wrong=dict(
        plain_backtracking="""
            pub fn can_partition_k_subsets(nums: &[u32], k: usize) -> bool {
                fn fill(nums: &[u32], target: u32, used: &mut [bool], k: usize, open: u32, start: usize) -> bool {
                    if k == 1 {
                        return true;
                    }
                    if open == target {
                        return fill(nums, target, used, k - 1, 0, 0);
                    }
                    for i in start..nums.len() {
                        if used[i] || open + nums[i] > target {
                            continue;
                        }
                        used[i] = true;
                        if fill(nums, target, used, k, open + nums[i], i + 1) {
                            return true;
                        }
                        used[i] = false;
                    }
                    false
                }
                let total: u32 = nums.iter().sum();
                if total % k as u32 != 0 {
                    return false;
                }
                let target = total / k as u32;
                let mut nums = nums.to_vec();
                nums.sort_unstable_by(|a, b| b.cmp(a));
                nums[0] <= target && fill(&nums, target, &mut vec![false; nums.len()], k, 0, 0)
            }
        """,
        first_fit_no_backtracking="""
            pub fn can_partition_k_subsets(nums: &[u32], k: usize) -> bool {
                let total: u32 = nums.iter().sum();
                if total % k as u32 != 0 {
                    return false;
                }
                let target = total / k as u32;
                let mut nums = nums.to_vec();
                nums.sort_unstable_by(|a, b| b.cmp(a));
                let mut groups = vec![0u32; k];
                for x in nums {
                    match groups.iter_mut().find(|g| **g + x <= target) {
                        Some(g) => *g += x,
                        None => return false,
                    }
                }
                true
            }
        """,
    ),
    hints=[("approach", "Fill the groups one at a time, each up to total / k, and move to the next group when one is full. The set of "
                        "numbers used so far determines the rest of the state, so remember the sets that failed."),
           ("rust", "Keep the used set in a `u32` bitmask and the failures in `vec![false; 1 << n]`. The open group's sum is "
                    "`(open + nums[i]) % target` after adding `nums[i]`."),
           ("edge case", "Sort descending, skip a number equal to one that just failed in the same spot, and when a group is empty "
                         "put the largest unused number in it rather than trying every number there.")],
    notes=("Filling groups in order makes the used-set bitmask a complete description of the search state: the full groups are "
           "interchangeable, and the open group's sum is the used sum modulo the target. So there are at most 2ⁿ states, each "
           "expanded once thanks to `dead`, which bounds the search at O(n · 2ⁿ). The duplicate skip and the empty-group rule "
           "cut the constant: without them, [2; 17] + [1, 1] with k = 4 rebuilds the same groups from different copies of 2 "
           "hundreds of millions of times.",
           "O(n · 2ⁿ)", "O(2ⁿ) for the memo"),
    follow_up="Matchsticks to square is the case k = 4. Would this memo help there, and what does it cost in memory for n = 20?",
    related=["D12"],
))

P.append(dict(
    slug="word-break-ii", title="Word break II", level="hard", stage="constraints-pruning", tags=["backtracking", "DP table", "pruning", "String"],
    companies=["Meta", "Apple", "Amazon", "Google", "Microsoft", "Uber", "Bloomberg"],
    teaches=["Prune with a table: first compute which suffixes can be split at all (Word break I, backwards), then search only "
             "through positions that can still finish. Every branch then ends in an answer.",
             "Hand out `&str` slices of `s` along the path and join them only when a sentence is complete."],
    statement="""
        Insert spaces into `s` so that every piece is a word from `word_dict`, and return every sentence you can make this
        way. A word can be used any number of times. The dictionary may list a word more than once; each sentence still
        appears once. The sentences can come in any order.

        `s` can be 100 letters long, and dictionary words 40. The tests include strings with a huge number of partial
        splits that never finish, where searching without first ruling out dead positions takes far too long.
    """,
    examples=[("s = \"catsanddog\", word_dict = [\"cat\", \"cats\", \"and\", \"sand\", \"dog\"]", "[\"cats and dog\", \"cat sand dog\"]"),
              ("s = \"pineapplepenapple\", word_dict = [\"apple\", \"pen\", \"applepen\", \"pine\", \"pineapple\"]",
               "[\"pine apple pen apple\", \"pineapple pen apple\", \"pine applepen apple\"]"),
              ("s = \"catsandog\", word_dict = [\"cats\", \"dog\", \"sand\", \"and\", \"cat\"]", "[]")],
    constraints=["1 ≤ s.len() ≤ 100", "1 ≤ word_dict.len() ≤ 1000", "1 ≤ word.len() ≤ 40",
                 "`s` and the words hold lowercase ASCII letters", "the answer holds at most 20 000 sentences"],
    starter="""
        pub fn word_break(s: &str, word_dict: &[&str]) -> Vec<String> {
            todo!()
        }
    """,
    solution="""
        use std::collections::HashSet;

        pub fn word_break(s: &str, word_dict: &[&str]) -> Vec<String> {
            let words: HashSet<&str> = word_dict.iter().copied().collect();
            let longest = words.iter().map(|w| w.len()).max().unwrap_or(0);
            let n = s.len();
            // finishes[i]: s[i..] splits into words. Built from the back, like Word break I.
            let mut finishes = vec![false; n + 1];
            finishes[n] = true;
            for i in (0..n).rev() {
                finishes[i] = (i + 1..=n.min(i + longest)).any(|j| finishes[j] && words.contains(&s[i..j]));
            }

            // Only steps to positions that can still finish, so every branch ends in a sentence.
            fn build<'a>(s: &'a str, i: usize, words: &HashSet<&str>, longest: usize, finishes: &[bool], path: &mut Vec<&'a str>, out: &mut Vec<String>) {
                if i == s.len() {
                    out.push(path.join(" "));
                    return;
                }
                for j in i + 1..=s.len().min(i + longest) {
                    if finishes[j] && words.contains(&s[i..j]) {
                        path.push(&s[i..j]);
                        build(s, j, words, longest, finishes, path, out);
                        path.pop();
                    }
                }
            }
            let mut out = Vec::new();
            if finishes[0] {
                build(s, 0, &words, longest, &finishes, &mut Vec::new(), &mut out);
            }
            out
        }
    """,
    visible=[
        SORTED,
        T("leetcode_cats_and_dog", "s = \"catsanddog\", word_dict = [\"cat\", \"cats\", \"and\", \"sand\", \"dog\"]",
          'sorted(word_break("catsanddog", &["cat", "cats", "and", "sand", "dog"]))', 'vec!["cat sand dog", "cats and dog"]'),
        T("leetcode_pineapple", "s = \"pineapplepenapple\", word_dict = [\"apple\", \"pen\", \"applepen\", \"pine\", \"pineapple\"]",
          'sorted(word_break("pineapplepenapple", &["apple", "pen", "applepen", "pine", "pineapple"]))',
          'vec!["pine apple pen apple", "pine applepen apple", "pineapple pen apple"]'),
        T("leetcode_no_sentence", "s = \"catsandog\", word_dict = [\"cats\", \"dog\", \"sand\", \"and\", \"cat\"]",
          'word_break("catsandog", &["cats", "dog", "sand", "and", "cat"])', "Vec::<String>::new()"),
        T("word_used_twice", "s = \"dogdog\", word_dict = [\"dog\"]", 'word_break("dogdog", &["dog"])', 'vec!["dog dog"]'),
        T("whole_string_is_a_word", "s = \"apple\", word_dict = [\"apple\", \"app\", \"le\"]", 'sorted(word_break("apple", &["apple", "app", "le"]))',
          'vec!["app le", "apple"]'),
        T("repeated_dictionary_word", "s = \"catcat\", word_dict = [\"cat\", \"cat\"]", 'word_break("catcat", &["cat", "cat"])', 'vec!["cat cat"]'),
    ],
    hidden=[
        SORTED,
        T("single_letter", "s = \"a\", word_dict = [\"a\"]", 'word_break("a", &["a"])', 'vec!["a"]'),
        T("no_word_fits", "s = \"b\", word_dict = [\"a\"]", 'word_break("b", &["a"])', "Vec::<String>::new()"),
        T("word_longer_than_s", "s = \"ab\", word_dict = [\"abc\"]", 'word_break("ab", &["abc"])', "Vec::<String>::new()"),
        T("four_as", "s = \"aaaa\", word_dict = [\"a\", \"aa\"]", 'sorted(word_break("aaaa", &["a", "aa"]))',
          'vec!["a a a a", "a a aa", "a aa a", "aa a a", "aa aa"]'),
        T("leetcode_seven_as", "s = \"aaaaaaa\", word_dict = [\"aaaa\", \"aa\", \"a\"]", 'word_break("aaaaaaa", &["aaaa", "aa", "a"]).len()', "31"),
        T("prefix_trap", "s = \"catsdog\", word_dict = [\"cat\", \"cats\", \"sdog\", \"dog\"]", 'sorted(word_break("catsdog", &["cat", "cats", "sdog", "dog"]))',
          'vec!["cat sdog", "cats dog"]'),
        T("last_letter_unmatched", "s = \"aaab\", word_dict = [\"a\", \"aa\", \"aaa\"]", 'word_break("aaab", &["a", "aa", "aaa"])', "Vec::<String>::new()"),
        T("hundred_letters", "s = \"catsanddog\" × 10, word_dict = [\"cat\", \"cats\", \"and\", \"sand\", \"dog\"]: 2¹⁰ sentences",
          '{ let s = "catsanddog".repeat(10); let all = word_break(&s, &["cat", "cats", "and", "sand", "dog"]); '
          '(all.len(), all.iter().all(|x| x.replace(' + "' '" + ', "") == s)) }',
          "(1024, true)"),
        """
        /// Every way to cut `s` into pieces, kept when every piece is a word.
        fn brute(s: &str, dict: &[&str]) -> Vec<String> {
            let n = s.len();
            let mut out = Vec::new();
            for cuts in 0..1u32 << (n - 1) {
                let mut pieces = Vec::new();
                let mut start = 0;
                for i in 1..=n {
                    if i == n || cuts >> (i - 1) & 1 == 1 {
                        pieces.push(&s[start..i]);
                        start = i;
                    }
                }
                if pieces.iter().all(|p| dict.contains(p)) {
                    out.push(pieces.join(" "));
                }
            }
            out
        }

        #[test]
        fn random_vs_every_cut() {
            let mut rng = anneal_prelude::Rng::new(1136);
            for _ in 0..300 {
                let len = rng.int(1, 10) as usize;
                let s = rng.string(len, "ab");
                let count = rng.int(1, 5) as usize;
                let mut words = Vec::new();
                for _ in 0..count {
                    let wlen = rng.int(1, 3) as usize;
                    words.push(rng.string(wlen, "ab"));
                }
                let dict: Vec<&str> = words.iter().map(String::as_str).collect();
                check!(format!("s = {s:?}, word_dict = {dict:?}"), sorted(word_break(&s, &dict)), sorted(brute(&s, &dict)));
            }
        }

        #[test]
        fn many_sentences() {
            // Fibonacci(21) ways to write 20 as a sum of 1s and 2s.
            let s = "a".repeat(20);
            let mut all = word_break(&s, &["a", "aa"]);
            all.sort();
            all.dedup();
            check!("s = 20 × \\"a\\", word_dict = [\\"a\\", \\"aa\\"]: distinct sentences", all.len(), 10946);
        }

        #[test]
        fn scale_no_sentence() {
            let s = "a".repeat(60) + "b";
            check!("s = 60 × \\"a\\" + \\"b\\", word_dict = [\\"a\\", \\"aa\\", \\"aaa\\", \\"aaaa\\", \\"aaaaa\\"]",
                word_break(&s, &["a", "aa", "aaa", "aaaa", "aaaaa"]), Vec::<String>::new());
        }

        #[test]
        fn scale_one_long_word() {
            // Only the 37-letter word covers the b; every split of the a's before it is a dead end.
            let s = "a".repeat(36) + "b";
            check!("s = 36 × \\"a\\" + \\"b\\", word_dict = [\\"a\\", \\"aa\\", \\"aaa\\", \\"aaaa\\", s]",
                word_break(&s, &["a", "aa", "aaa", "aaaa", s.as_str()]), vec![s.clone()]);
        }
        """,
    ],
    wrong=dict(
        plain_backtracking="""
            use std::collections::HashSet;

            pub fn word_break(s: &str, word_dict: &[&str]) -> Vec<String> {
                fn build<'a>(s: &'a str, i: usize, words: &HashSet<&str>, path: &mut Vec<&'a str>, out: &mut Vec<String>) {
                    if i == s.len() {
                        out.push(path.join(" "));
                        return;
                    }
                    for j in i + 1..=s.len() {
                        if words.contains(&s[i..j]) {
                            path.push(&s[i..j]);
                            build(s, j, words, path, out);
                            path.pop();
                        }
                    }
                }
                let words: HashSet<&str> = word_dict.iter().copied().collect();
                let mut out = Vec::new();
                build(s, 0, &words, &mut Vec::new(), &mut out);
                out
            }
        """,
        whole_string_check_only="""
            use std::collections::HashSet;

            pub fn word_break(s: &str, word_dict: &[&str]) -> Vec<String> {
                fn build<'a>(s: &'a str, i: usize, words: &HashSet<&str>, path: &mut Vec<&'a str>, out: &mut Vec<String>) {
                    if i == s.len() {
                        out.push(path.join(" "));
                        return;
                    }
                    for j in i + 1..=s.len() {
                        if words.contains(&s[i..j]) {
                            path.push(&s[i..j]);
                            build(s, j, words, path, out);
                            path.pop();
                        }
                    }
                }
                let words: HashSet<&str> = word_dict.iter().copied().collect();
                let n = s.len();
                // Word break I: can s be split at all?
                let mut splits = vec![false; n + 1];
                splits[0] = true;
                for j in 1..=n {
                    splits[j] = (0..j).any(|i| splits[i] && words.contains(&s[i..j]));
                }
                let mut out = Vec::new();
                if splits[n] {
                    build(s, 0, &words, &mut Vec::new(), &mut out);
                }
                out
            }
        """,
        dictionary_duplicates="""
            pub fn word_break(s: &str, word_dict: &[&str]) -> Vec<String> {
                let n = s.len();
                let mut finishes = vec![false; n + 1];
                finishes[n] = true;
                for i in (0..n).rev() {
                    finishes[i] = word_dict.iter().any(|w| s[i..].starts_with(w) && finishes[i + w.len()]);
                }
                fn build<'a>(s: &'a str, i: usize, dict: &[&'a str], finishes: &[bool], path: &mut Vec<&'a str>, out: &mut Vec<String>) {
                    if i == s.len() {
                        out.push(path.join(" "));
                        return;
                    }
                    for &w in dict {
                        if s[i..].starts_with(w) && finishes[i + w.len()] {
                            path.push(w);
                            build(s, i + w.len(), dict, finishes, path, out);
                            path.pop();
                        }
                    }
                }
                let mut out = Vec::new();
                if finishes[0] {
                    build(s, 0, word_dict, &finishes, &mut Vec::new(), &mut out);
                }
                out
            }
        """,
    ),
    hints=[("approach", "Plain backtracking explores every partial split, even ones that can never reach the end. First compute, from "
                        "the back, which positions `i` have a splittable suffix `s[i..]`; then backtrack only through those."),
           ("rust", "Put the words in a `HashSet<&str>` (this also drops repeated words), keep the path as `Vec<&str>` slices of "
                    "`s`, and `path.join(\" \")` at the end. Only try pieces up to the longest word's length."),
           ("edge case", "A string whose last letter no word covers has no sentence at all: the table says so before any search.")],
    notes=("The table is Word break I run backwards: `finishes[i]` is true when some word `s[i..j]` is followed by a position `j` "
           "that finishes. With it, the search never steps into a dead position, so every branch produces a sentence and the "
           "work is proportional to the output. Checking only whether the whole string splits is not enough: in 36 a's then a b, "
           "with the 37-letter word, the string splits, but every other split of the a's is a dead end. A memo of the sentences "
           "for each suffix works too, at the cost of storing them.",
           "O(n · L) for the table (L = longest word) plus O(output)", "O(n) besides the output"),
    follow_up="How would you return only the number of sentences, without building them?",
    related=["D12", "D10"],
))

EXPR_VALUE = """
/// The value of an expression of digits, `+`, `-` and `*`, or `None` if an operand has a leading zero.
fn value(expr: &str) -> Option<i64> {
    let bytes = expr.as_bytes();
    let (mut total, mut sign, mut start) = (0i64, 1i64, 0);
    for i in 0..=bytes.len() {
        if i == bytes.len() || bytes[i] == b'+' || bytes[i] == b'-' {
            let mut product = 1i64;
            for operand in expr[start..i].split('*') {
                if operand.len() > 1 && operand.starts_with('0') {
                    return None;
                }
                product *= operand.parse::<i64>().unwrap();
            }
            total += sign * product;
            if i < bytes.len() {
                sign = if bytes[i] == b'+' { 1 } else { -1 };
            }
            start = i + 1;
        }
    }
    Some(total)
}
"""

P.append(dict(
    slug="expression-add-operators", title="Expression add operators", level="hard", stage="constraints-pruning",
    tags=["backtracking", "String", "parsing"],
    companies=["Meta", "Amazon", "Google", "Microsoft"],
    teaches=["Evaluate while you build: carry the running value and the last product term, so `*` can undo that term and "
             "multiply it, with no parsing at the leaves.",
             "One `String` buffer for the expression: push the operator and digits, recurse, `truncate` back."],
    statement="""
        `num` is a string of digits. Put `+`, `-` or `*` (or nothing) between each pair of adjacent digits, and return every
        expression whose value is `target`. `*` binds tighter than `+` and `-`, as usual.

        An operand can't have a leading zero: `05` is not allowed, `0` on its own is. Operands can have up to 10 digits, so
        they don't all fit in an `i32`. The expressions can come in any order.
    """,
    examples=[("num = \"123\", target = 6", "[\"1*2*3\", \"1+2+3\"]"), ("num = \"232\", target = 8", "[\"2*3+2\", \"2+3*2\"]"),
              ("num = \"3456237490\", target = 9191", "[]")],
    constraints=["1 ≤ num.len() ≤ 10", "`num` holds only digits", "-2³¹ ≤ target ≤ 2³¹ - 1"],
    starter="""
        pub fn add_operators(num: &str, target: i64) -> Vec<String> {
            todo!()
        }
    """,
    solution="""
        pub fn add_operators(num: &str, target: i64) -> Vec<String> {
            // `value`: the expression so far. `last`: its final product term, which a `*` takes back out and multiplies.
            fn build(digits: &[u8], i: usize, target: i64, value: i64, last: i64, expr: &mut String, out: &mut Vec<String>) {
                if i == digits.len() {
                    if value == target {
                        out.push(expr.clone());
                    }
                    return;
                }
                let len = expr.len();
                let mut operand = 0i64;
                for j in i..digits.len() {
                    if j > i && digits[i] == b'0' {
                        break; // "05" is not an operand
                    }
                    operand = operand * 10 + i64::from(digits[j] - b'0');
                    let text = &digits[i..=j];
                    if i == 0 {
                        expr.extend(text.iter().map(|&d| d as char));
                        build(digits, j + 1, target, operand, operand, expr, out);
                        expr.truncate(len);
                        continue;
                    }
                    for (op, value, last) in [
                        ('+', value + operand, operand),
                        ('-', value - operand, -operand),
                        ('*', value - last + last * operand, last * operand),
                    ] {
                        expr.push(op);
                        expr.extend(text.iter().map(|&d| d as char));
                        build(digits, j + 1, target, value, last, expr, out);
                        expr.truncate(len);
                    }
                }
            }
            let mut out = Vec::new();
            build(num.as_bytes(), 0, target, 0, 0, &mut String::with_capacity(2 * num.len()), &mut out);
            out
        }
    """,
    visible=[
        SORTED,
        T("leetcode_six", "num = \"123\", target = 6", 'sorted(add_operators("123", 6))', 'vec!["1*2*3", "1+2+3"]'),
        T("leetcode_precedence", "num = \"232\", target = 8", 'sorted(add_operators("232", 8))', 'vec!["2*3+2", "2+3*2"]'),
        T("leetcode_none", "num = \"3456237490\", target = 9191", 'add_operators("3456237490", 9191)', "Vec::<String>::new()"),
        T("leetcode_no_leading_zero", "num = \"105\", target = 5 (\"1*05\" is not allowed)", 'sorted(add_operators("105", 5))', 'vec!["1*0+5", "10-5"]'),
        T("leetcode_zeros", "num = \"00\", target = 0", 'sorted(add_operators("00", 0))', 'vec!["0*0", "0+0", "0-0"]'),
        T("no_operator", "num = \"123\", target = 123", 'add_operators("123", 123)', 'vec!["123"]'),
    ],
    hidden=[
        SORTED,
        EXPR_VALUE,
        T("single_zero", "num = \"0\", target = 0", 'add_operators("0", 0)', 'vec!["0"]'),
        T("single_digit", "num = \"5\", target = 5", 'add_operators("5", 5)', 'vec!["5"]'),
        T("single_digit_miss", "num = \"5\", target = 3", 'add_operators("5", 3)', "Vec::<String>::new()"),
        T("times_before_plus", "num = \"123\", target = 7", 'add_operators("123", 7)', 'vec!["1+2*3"]'),
        T("negative_target", "num = \"123\", target = -4", 'add_operators("123", -4)', 'vec!["1-2-3"]'),
        T("three_zeros", "num = \"000\", target = 0", 'add_operators("000", 0).len()', "9"),
        T("leetcode_past_i32", "num = \"2147483648\", target = -2147483648", 'add_operators("2147483648", -2147483648)', "Vec::<String>::new()"),
        T("ten_nines", "num = \"9999999999\", target = 0: (expressions, all worth 0)",
          '{ let all = add_operators("9999999999", 0); (all.len(), all.iter().all(|e| value(e) == Some(0))) }', "(3930, true)"),
        T("big_products", "num = \"999999999\", target = 81", 'sorted(add_operators("999999999", 81))',
          'vec!["9+9+9+9+9+9+9+9+9", "999-9*99-9-9-9", "999-9-9*99-9-9", "999-9-9-9*99-9", "999-9-9-9-9*99", "999-9-9-9-99*9", '
          '"999-9-9-99*9-9", "999-9-99*9-9-9", "999-99*9-9-9-9"]'),
        """
        /// Every way to put nothing, `+`, `-` or `*` between the digits, kept when the value is `target`.
        fn brute(num: &str, target: i64) -> Vec<String> {
            let digits = num.as_bytes();
            let mut out = Vec::new();
            for mut code in 0..4usize.pow(digits.len() as u32 - 1) {
                let mut expr = String::from(digits[0] as char);
                for &d in &digits[1..] {
                    match code % 4 {
                        1 => expr.push('+'),
                        2 => expr.push('-'),
                        3 => expr.push('*'),
                        _ => {}
                    }
                    expr.push(d as char);
                    code /= 4;
                }
                if value(&expr) == Some(target) {
                    out.push(expr);
                }
            }
            out
        }

        #[test]
        fn random_vs_every_operator_choice() {
            let mut rng = anneal_prelude::Rng::new(1137);
            for _ in 0..300 {
                let len = rng.int(1, 6) as usize;
                let num = rng.string(len, "0012359");
                // Half the targets are the value of some expression, so there's an answer to find.
                let target = if rng.bool() {
                    rng.int(-30, 60)
                } else {
                    let ops = rng.string(len - 1, " +-*");
                    let mut expr = String::new();
                    for (i, d) in num.chars().enumerate() {
                        if i > 0 && &ops[i - 1..i] != " " {
                            expr.push_str(&ops[i - 1..i]);
                        }
                        expr.push(d);
                    }
                    value(&expr).unwrap_or(0)
                };
                check!(format!("num = {num:?}, target = {target}"), sorted(add_operators(&num, target)), sorted(brute(&num, target)));
            }
        }

        #[test]
        fn scale_ten_digits() {
            let all = add_operators("1234567890", 45);
            let ok = all.iter().all(|e| value(e) == Some(45));
            check!("num = \\"1234567890\\", target = 45: (expressions, all evaluate to 45)", (all.len(), ok), (473, true));
        }

        #[test]
        fn scale_many_zeros() {
            let all = add_operators("1000000009", 9);
            let ok = all.iter().all(|e| value(e) == Some(9));
            check!("num = \\"1000000009\\", target = 9: (expressions, all valid and worth 9)", (all.len(), ok), (3280, true));
        }
        """,
    ],
    wrong=dict(
        leading_zeros_allowed="""
            pub fn add_operators(num: &str, target: i64) -> Vec<String> {
                fn build(digits: &[u8], i: usize, target: i64, value: i64, last: i64, expr: &mut String, out: &mut Vec<String>) {
                    if i == digits.len() {
                        if value == target {
                            out.push(expr.clone());
                        }
                        return;
                    }
                    let len = expr.len();
                    let mut operand = 0i64;
                    for j in i..digits.len() {
                        operand = operand * 10 + i64::from(digits[j] - b'0');
                        let text = &digits[i..=j];
                        if i == 0 {
                            expr.extend(text.iter().map(|&d| d as char));
                            build(digits, j + 1, target, operand, operand, expr, out);
                            expr.truncate(len);
                            continue;
                        }
                        for (op, value, last) in [
                            ('+', value + operand, operand),
                            ('-', value - operand, -operand),
                            ('*', value - last + last * operand, last * operand),
                        ] {
                            expr.push(op);
                            expr.extend(text.iter().map(|&d| d as char));
                            build(digits, j + 1, target, value, last, expr, out);
                            expr.truncate(len);
                        }
                    }
                }
                let mut out = Vec::new();
                build(num.as_bytes(), 0, target, 0, 0, &mut String::new(), &mut out);
                out
            }
        """,
        left_to_right="""
            pub fn add_operators(num: &str, target: i64) -> Vec<String> {
                fn build(digits: &[u8], i: usize, target: i64, value: i64, expr: &mut String, out: &mut Vec<String>) {
                    if i == digits.len() {
                        if value == target {
                            out.push(expr.clone());
                        }
                        return;
                    }
                    let len = expr.len();
                    let mut operand = 0i64;
                    for j in i..digits.len() {
                        if j > i && digits[i] == b'0' {
                            break;
                        }
                        operand = operand * 10 + i64::from(digits[j] - b'0');
                        let text = &digits[i..=j];
                        if i == 0 {
                            expr.extend(text.iter().map(|&d| d as char));
                            build(digits, j + 1, target, operand, expr, out);
                            expr.truncate(len);
                            continue;
                        }
                        for (op, value) in [('+', value + operand), ('-', value - operand), ('*', value * operand)] {
                            expr.push(op);
                            expr.extend(text.iter().map(|&d| d as char));
                            build(digits, j + 1, target, value, expr, out);
                            expr.truncate(len);
                        }
                    }
                }
                let mut out = Vec::new();
                build(num.as_bytes(), 0, target, 0, &mut String::new(), &mut out);
                out
            }
        """,
        i32_operands="""
            pub fn add_operators(num: &str, target: i64) -> Vec<String> {
                fn build(digits: &[u8], i: usize, target: i32, value: i32, last: i32, expr: &mut String, out: &mut Vec<String>) {
                    if i == digits.len() {
                        if value == target {
                            out.push(expr.clone());
                        }
                        return;
                    }
                    let len = expr.len();
                    let mut operand = 0i32;
                    for j in i..digits.len() {
                        if j > i && digits[i] == b'0' {
                            break;
                        }
                        operand = operand * 10 + i32::from(digits[j] - b'0');
                        let text = &digits[i..=j];
                        if i == 0 {
                            expr.extend(text.iter().map(|&d| d as char));
                            build(digits, j + 1, target, operand, operand, expr, out);
                            expr.truncate(len);
                            continue;
                        }
                        for (op, value, last) in [
                            ('+', value + operand, operand),
                            ('-', value - operand, -operand),
                            ('*', value - last + last * operand, last * operand),
                        ] {
                            expr.push(op);
                            expr.extend(text.iter().map(|&d| d as char));
                            build(digits, j + 1, target, value, last, expr, out);
                            expr.truncate(len);
                        }
                    }
                }
                let mut out = Vec::new();
                build(num.as_bytes(), 0, target as i32, 0, 0, &mut String::new(), &mut out);
                out
            }
        """,
    ),
    hints=[("approach", "At each position, choose how many digits the next operand takes, then which operator goes before it. Track "
                        "the value so far and the last product term instead of evaluating the finished string."),
           ("rust", "For `*`: new value = `value - last + last * operand`, new last = `last * operand`. For `-`, last = `-operand`. "
                    "Build the expression in one `String` and `truncate(len)` after each recursive call."),
           ("edge case", "Stop extending an operand that starts with `0` after its first digit, and use `i64`: \"2147483648\" is "
                         "already past `i32::MAX`.")],
    notes=("There are 4ⁿ⁻¹ ways to fill the gaps, and the answer can hold thousands of them, so the search itself can't be cut much; "
           "the work that can go is re-evaluating each finished string. Carrying (value, last term) makes each step O(1): `+` and `-` "
           "start a new term, `*` replaces the last term with `last · operand`. The one real prune is the leading-zero rule, which "
           "stops a `0` operand from growing.",
           "O(n · 4ⁿ)", "O(n) recursion depth besides the output"),
    follow_up="How would you add parentheses, or a `/` that truncates towards zero?",
    related=["D3"],
))

STAGES = [
    ("recursion", "Recursion", "easy"),
    ("first-backtracking", "First backtracking", "easy"),
    ("choices-grids", "Choices & grids", "medium"),
    ("constraints-pruning", "Constraints & pruning", "hard"),
]

if __name__ == "__main__":
    n = write_track("d11-recursion-backtracking", "D11", "Recursion & backtracking", "D", "core", 12,
                    "Recursion first (base cases, trusting the call, divide and conquer), then backtracking: choose, recurse, undo, and prune.",
                    STAGES, P)
    print("D11", n)
