from author import T, prob, write_track, tag_companies

P = []

# ---------------------------------------------------------------- on an index (easy)

P.append(prob(
    "binary-search", "Binary search", "easy", "on-an-index", ["half-open range"],
    """
    Return the index of `target` in the sorted slice `nums` (values distinct), or `None`. Write the loop
    yourself: no `binary_search` or `partition_point`.
    """,
    """
    pub fn search(nums: &[i32], target: i32) -> Option<usize> {
        todo!()
    }
    """,
    """
    pub fn search(nums: &[i32], target: i32) -> Option<usize> {
        // Half-open [lo, hi): empty when lo == hi, and `hi - lo` never underflows.
        let (mut lo, mut hi) = (0, nums.len());
        while lo < hi {
            let mid = lo + (hi - lo) / 2;
            match nums[mid].cmp(&target) {
                std::cmp::Ordering::Less => lo = mid + 1,
                std::cmp::Ordering::Greater => hi = mid,
                std::cmp::Ordering::Equal => return Some(mid),
            }
        }
        None
    }
    """,
    [T("found", "[-1,0,3,5,9,12], 9", "search(&[-1, 0, 3, 5, 9, 12], 9)", "Some(4)"),
     T("missing", "[-1,0,3,5,9,12], 2", "search(&[-1, 0, 3, 5, 9, 12], 2)", "None"),
     T("empty_slice", "[], 0", "search(&[], 0)", "None"),
     T("single_found", "[5], 5", "search(&[5], 5)", "Some(0)"),
     T("outside_both_ends", "[1,3], 0 and 4", "(search(&[1, 3], 0), search(&[1, 3], 4))", "(None, None)")],
    [T("empty", "[], 1", "search(&[], 1)", "None"),
     T("ends", "[1,2,3], 1 and 3", "(search(&[1, 2, 3], 1), search(&[1, 2, 3], 3))", "(Some(0), Some(2))"),
     T("below_all", "[5], 1", "search(&[5], 1)", "None"),
     T("million", "0..10⁶ evens, 777_778", "search(&v, 777_778)", "Some(388_889)", setup="let v: Vec<i32> = (0..1_000_000).map(|i| i * 2).collect();"),
     T("extremes", "[i32::MIN, 0, i32::MAX], each value", "(search(&v, i32::MIN), search(&v, 0), search(&v, i32::MAX))", "(Some(0), Some(1), Some(2))",
       setup="let v = [i32::MIN, 0, i32::MAX];"),
     T("two_elements", "[4,8], 4, 8 and 6", "(search(&[4, 8], 4), search(&[4, 8], 8), search(&[4, 8], 6))", "(Some(0), Some(1), None)"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(401);
         for _ in 0..400 {
             let n = rng.below(12);
             let mut nums: Vec<i32> = rng.vec(n, -30, 30);
             nums.sort_unstable();
             nums.dedup();
             let target = rng.int(-32, 32) as i32;
             let want = nums.iter().position(|&x| x == target);
             check!(format!("nums = {nums:?}, target = {target}"), search(&nums, target), want);
         }
     }

     #[test]
     fn scale_100k_queries() {
         let v: Vec<i32> = (0..100_000).map(|i| i * 3).collect();
         let hits = (0..300_000).filter(|&t| search(&v, t).is_some_and(|i| v[i] == t)).count();
         check!("nums = 0, 3, …, 299997; every target in 0..300000", hits, 100_000);
     }
     """],
    [("rust", "Use a half-open range `[lo, hi)` of `usize`s. With a closed range, `hi = mid - 1` underflows when `mid` is 0."),
     ("rust", "`match nums[mid].cmp(&target)` covers the three cases with no chance of mixing up `<` and `<=`.")],
    ("Half-open bounds make the loop condition `lo < hi` and the updates `lo = mid + 1` / `hi = mid`, with no `- 1` on an unsigned index.", "O(log n)", "O(1)"),
    "What does `slice::binary_search` return when the value is missing, and why is that useful?",
    ["Half-open ranges with `usize`.", "`Ordering` from `cmp` in a `match`."],
    examples=[("nums = [-1,0,3,5,9,12], target = 9", "Some(4)")],
    wrong=dict(
        linear_scan="""
            pub fn search(nums: &[i32], target: i32) -> Option<usize> {
                nums.iter().position(|&x| x == target)
            }
        """,
        closed_range="""
            pub fn search(nums: &[i32], target: i32) -> Option<usize> {
                let (mut lo, mut hi) = (0, nums.len() - 1);
                while lo <= hi {
                    let mid = lo + (hi - lo) / 2;
                    match nums[mid].cmp(&target) {
                        std::cmp::Ordering::Less => lo = mid + 1,
                        std::cmp::Ordering::Greater => hi = mid - 1,
                        std::cmp::Ordering::Equal => return Some(mid),
                    }
                }
                None
            }
        """,
        lo_never_moves_past_mid="""
            pub fn search(nums: &[i32], target: i32) -> Option<usize> {
                let (mut lo, mut hi) = (0, nums.len());
                while lo < hi {
                    let mid = lo + (hi - lo) / 2;
                    match nums[mid].cmp(&target) {
                        std::cmp::Ordering::Less => lo = mid,
                        std::cmp::Ordering::Greater => hi = mid,
                        std::cmp::Ordering::Equal => return Some(mid),
                    }
                }
                None
            }
        """,
    ),
))

P.append(prob(
    "search-insert-position", "Search insert position", "easy", "on-an-index", ["partition_point"],
    """
    `nums` is sorted with distinct values. Return the index of `target`, or where it would be inserted to keep
    the slice sorted. Use `partition_point`.
    """,
    """
    pub fn insert_position(nums: &[i32], target: i32) -> usize {
        todo!()
    }
    """,
    """
    pub fn insert_position(nums: &[i32], target: i32) -> usize {
        nums.partition_point(|&x| x < target)
    }
    """,
    [T("present", "[1,3,5,6], 5", "insert_position(&[1, 3, 5, 6], 5)", "2"),
     T("between", "[1,3,5,6], 2", "insert_position(&[1, 3, 5, 6], 2)", "1"),
     T("past_the_end", "[1,3,5,6], 7", "insert_position(&[1, 3, 5, 6], 7)", "4"),
     T("before_the_start", "[2,4], 1", "insert_position(&[2, 4], 1)", "0"),
     T("empty_slice", "[], 5", "insert_position(&[], 5)", "0")],
    [T("after_all", "[1,3,5,6], 7", "insert_position(&[1, 3, 5, 6], 7)", "4"),
     T("before_all", "[1,3,5,6], 0", "insert_position(&[1, 3, 5, 6], 0)", "0"),
     T("empty", "[], 3", "insert_position(&[], 3)", "0"),
     T("single", "[1], 0, 1 and 2", "(insert_position(&[1], 0), insert_position(&[1], 1), insert_position(&[1], 2))", "(0, 0, 1)"),
     T("negatives", "[-9,-4,-1], -4 and -5", "(insert_position(&[-9, -4, -1], -4), insert_position(&[-9, -4, -1], -5))", "(1, 1)"),
     T("extremes", "[i32::MIN, i32::MAX], i32::MIN, 0 and i32::MAX", "(insert_position(&v, i32::MIN), insert_position(&v, 0), insert_position(&v, i32::MAX))", "(0, 1, 1)",
       setup="let v = [i32::MIN, i32::MAX];"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(402);
         for _ in 0..400 {
             let n = rng.below(12);
             let mut nums: Vec<i32> = rng.vec(n, -30, 30);
             nums.sort_unstable();
             nums.dedup();
             let target = rng.int(-32, 32) as i32;
             let want = nums.iter().filter(|&&x| x < target).count();
             check!(format!("nums = {nums:?}, target = {target}"), insert_position(&nums, target), want);
         }
     }

     #[test]
     fn scale_100k_queries() {
         let v: Vec<i32> = (0..100_000).map(|i| i * 2).collect();
         let total: usize = (0..200_000).map(|t| insert_position(&v, t)).sum();
         check!("nums = 0, 2, …, 199998; sum of answers for every target in 0..200000", total, 10_000_000_000usize);
     }
     """],
    [("rust", "`partition_point(pred)` returns the first index where `pred` is false, given `pred` is true for a prefix and false after.")],
    ("Phrasing the search as 'how many elements are smaller than target' makes the predicate obviously monotone, and std does the loop.", "O(log n)", "O(1)"),
    "How does `binary_search`'s `Err(i)` relate to this answer?",
    ["`partition_point` with a monotone predicate."],
    examples=[("nums = [1,3,5,6], target = 2", "1")],
    wrong=dict(
        less_or_equal="""
            pub fn insert_position(nums: &[i32], target: i32) -> usize {
                nums.partition_point(|&x| x <= target)
            }
        """,
        linear_scan="""
            pub fn insert_position(nums: &[i32], target: i32) -> usize {
                nums.iter().position(|&x| x >= target).unwrap_or(nums.len())
            }
        """,
    ),
))

P.append(prob(
    "first-bad-version", "First bad version", "easy", "on-an-index", ["u32", "overflow-safe mid"],
    """
    Versions `1..=n` are good up to some point and bad after it. Using as few calls to `is_bad` as possible
    (at most 33), return the first bad version, or `None` if none is bad. `n` can be `u32::MAX`.
    """,
    """
    pub fn first_bad(n: u32, is_bad: impl Fn(u32) -> bool) -> Option<u32> {
        todo!()
    }
    """,
    """
    pub fn first_bad(n: u32, is_bad: impl Fn(u32) -> bool) -> Option<u32> {
        if n == 0 || !is_bad(n) {
            return None;
        }
        // The answer is in [lo, hi]; hi is known to be bad.
        let (mut lo, mut hi) = (1, n);
        while lo < hi {
            let mid = lo + (hi - lo) / 2;
            if is_bad(mid) {
                hi = mid;
            } else {
                lo = mid + 1;
            }
        }
        Some(lo)
    }
    """,
    [T("middle", "n = 5, first bad 4", "first_bad(5, |v| v >= 4)", "Some(4)"),
     T("all_bad", "n = 1, first bad 1", "first_bad(1, |v| v >= 1)", "Some(1)"),
     T("nothing_bad", "n = 3, none bad", "first_bad(3, |_| false)", "None"),
     T("no_versions", "n = 0", "first_bad(0, |_| true)", "None"),
     T("only_the_last_is_bad", "n = 10, first bad 10", "first_bad(10, |v| v >= 10)", "Some(10)")],
    [T("none_bad", "n = 10, none bad", "first_bad(10, |_| false)", "None"),
     T("first_is_bad_at_max_n", "n = u32::MAX, every version bad", "(found, calls.get() <= 33)", "(Some(1), true)",
       setup="let calls = std::cell::Cell::new(0);\nlet found = first_bad(u32::MAX, |v| {\n    calls.set(calls.get() + 1);\n    v >= 1\n});"),
     T("only_max_is_bad", "n = u32::MAX, first bad u32::MAX", "first_bad(u32::MAX, |v| v == u32::MAX)", "Some(u32::MAX)"),
     T("two_versions", "n = 2, first bad 2, and first bad 1", "(first_bad(2, |v| v >= 2), first_bad(2, |v| v >= 1))", "(Some(2), Some(1))"),
     T("never_asks_about_version_zero", "n = 7, first bad 3; is_bad panics on 0 or > n", "first_bad(7, |v| { assert!((1..=7).contains(&v)); v >= 3 })", "Some(3)"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(403);
         for _ in 0..400 {
             let n = rng.int(0, 2000) as u32;
             let bad_from = rng.int(1, i64::from(n) + 1) as u32;
             let calls = std::cell::Cell::new(0u32);
             let got = first_bad(n, |v| {
                 calls.set(calls.get() + 1);
                 v >= bad_from
             });
             let want = (1..=n).find(|&v| v >= bad_from);
             check!(format!("n = {n}, first bad = {bad_from} (at most 13 calls)"), (got, calls.get() <= 13), (want, true));
         }
     }
     """,
     T("max_n", "n = u32::MAX, first bad u32::MAX - 1", "first_bad(u32::MAX, |v| v >= u32::MAX - 1)", "Some(u32::MAX - 1)"),
     T("few_calls", "n = u32::MAX, count calls", "(found, calls.get() <= 33)", "(Some(123_456_789), true)",
       setup="let calls = std::cell::Cell::new(0);\nlet found = first_bad(u32::MAX, |v| {\n    calls.set(calls.get() + 1);\n    v >= 123_456_789\n});")],
    [("rust", "`(lo + hi) / 2` overflows `u32` near `u32::MAX`. `lo + (hi - lo) / 2` can't."),
     ("approach", "Keep `hi` pointing at a known-bad version and shrink `[lo, hi]` until it's one element.")],
    ("Checking `n` first handles 'nothing bad' and guarantees the loop's invariant. 32 halvings of a `u32` range plus that check is 33 calls.", "O(log n)", "O(1)"),
    "Why is `impl Fn(u32) -> bool` a better parameter here than `&dyn Fn` or a generic `F`?",
    ["Overflow-safe midpoints.", "Binary search on a predicate you can only call."],
    wrong=dict(
        sum_midpoint="""
            pub fn first_bad(n: u32, is_bad: impl Fn(u32) -> bool) -> Option<u32> {
                if n == 0 || !is_bad(n) {
                    return None;
                }
                let (mut lo, mut hi) = (1, n);
                while lo < hi {
                    let mid = (lo + hi) / 2;
                    if is_bad(mid) {
                        hi = mid;
                    } else {
                        lo = mid + 1;
                    }
                }
                Some(lo)
            }
        """,
        linear_scan="""
            pub fn first_bad(n: u32, is_bad: impl Fn(u32) -> bool) -> Option<u32> {
                (1..=n).find(|&v| is_bad(v))
            }
        """,
        checks_both_sides="""
            pub fn first_bad(n: u32, is_bad: impl Fn(u32) -> bool) -> Option<u32> {
                let (mut lo, mut hi) = (1u32, n);
                while lo <= hi && hi > 0 {
                    let mid = lo + (hi - lo) / 2;
                    if is_bad(mid) && (mid == 1 || !is_bad(mid - 1)) {
                        return Some(mid);
                    }
                    if is_bad(mid) {
                        hi = mid - 1;
                    } else {
                        lo = mid + 1;
                    }
                }
                None
            }
        """,
    ),
))

P.append(prob(
    "integer-square-root", "Integer square root", "easy", "on-an-index", ["checked_mul", "search on the answer"],
    """
    Return the largest `r` with `r * r <= x`. Don't use floating point or `u64::isqrt`.
    """,
    """
    pub fn isqrt(x: u64) -> u64 {
        todo!()
    }
    """,
    """
    pub fn isqrt(x: u64) -> u64 {
        // Invariant: lo * lo <= x < hi * hi. The root of a u64 is below 2^32.
        let (mut lo, mut hi) = (0u64, x.min(u64::from(u32::MAX)) + 1);
        while hi - lo > 1 {
            let mid = lo + (hi - lo) / 2;
            if mid.checked_mul(mid).is_some_and(|sq| sq <= x) {
                lo = mid;
            } else {
                hi = mid;
            }
        }
        lo
    }
    """,
    [T("eight", "8", "isqrt(8)", "2"),
     T("perfect", "16", "isqrt(16)", "4"),
     T("four", "4", "isqrt(4)", "2"),
     T("zero", "0", "isqrt(0)", "0"),
     T("just_below_a_square", "15", "isqrt(15)", "3")],
    [T("zero_one", "0 and 1", "(isqrt(0), isqrt(1))", "(0, 1)"),
     T("two_and_three", "2 and 3", "(isqrt(2), isqrt(3))", "(1, 1)"),
     T("u32_max", "u32::MAX and 2³²", "(isqrt(u64::from(u32::MAX)), isqrt(1 << 32))", "(65_535, 65_536)"),
     T("big_square_and_neighbours", "10¹⁸ − 1, 10¹⁸, 10¹⁸ + 1", "(isqrt(999_999_999_999_999_999), isqrt(1_000_000_000_000_000_000), isqrt(1_000_000_000_000_000_001))",
       "(999_999_999, 1_000_000_000, 1_000_000_000)"),
     """
     #[test]
     fn scale_squares_sweep() {
         // r² and r² − 1 for r in 1..=100000.
         let bad = (1..=100_000u64).filter(|&r| isqrt(r * r) != r || isqrt(r * r - 1) != r - 1).count();
         check!("isqrt(r²) and isqrt(r² − 1) for r in 1..=100000: how many are wrong", bad, 0);
     }

     #[test]
     fn random_vs_brute_force() {
         // r is right exactly when r² ≤ x < (r + 1)², checked in u128.
         let mut rng = anneal_prelude::Rng::new(404);
         for i in 0..3000 {
             let x = match i % 3 {
                 0 => rng.int(0, 10_000) as u64,
                 1 => rng.next_u64(),
                 _ => { let r = rng.next_u64() >> 32; (r * r).wrapping_add(rng.int(-1, 1) as u64) }
             };
             let r = u128::from(isqrt(x));
             check!(format!("x = {x}"), r * r <= u128::from(x) && u128::from(x) < (r + 1) * (r + 1), true);
         }
     }
     """,
     T("max", "u64::MAX", "isqrt(u64::MAX)", "4_294_967_295"),
     T("near_square", "(2³² − 1)² and one less", "(isqrt(18_446_744_065_119_617_025), isqrt(18_446_744_065_119_617_024))", "(4_294_967_295, 4_294_967_294)")],
    [("approach", "Binary search for the answer: the predicate `r * r <= x` is true up to the root and false after."),
     ("rust", "`mid * mid` overflows for large `mid`. `mid.checked_mul(mid)` returns `None` instead, which means 'too big'.")],
    ("Searching on the answer turns a math problem into a monotone predicate. `checked_mul` makes overflow part of the comparison instead of a panic.", "O(log x)", "O(1)"),
    "Why does `(x as f64).sqrt() as u64` give wrong answers near `u64::MAX`?",
    ["Binary search on the answer.", "`checked_mul` for overflow-aware comparisons."],
    wrong=dict(
        float_sqrt="""
            pub fn isqrt(x: u64) -> u64 {
                (x as f64).sqrt() as u64
            }
        """,
        unchecked_square="""
            pub fn isqrt(x: u64) -> u64 {
                let (mut lo, mut hi) = (0u64, x / 2 + 2);
                while hi - lo > 1 {
                    let mid = lo + (hi - lo) / 2;
                    if mid * mid <= x {
                        lo = mid;
                    } else {
                        hi = mid;
                    }
                }
                lo
            }
        """,
        count_up="""
            pub fn isqrt(x: u64) -> u64 {
                let mut r: u64 = 0;
                while (r + 1).checked_mul(r + 1).is_some_and(|sq| sq <= x) {
                    r += 1;
                }
                r
            }
        """,
    ),
))

# ---------------------------------------------------------------- on structure & answer (medium)

P.append(prob(
    "first-and-last-position", "First and last position", "medium", "on-structure-and-answer", ["partition_point"],
    """
    `nums` is sorted and may repeat values. Return the first and last index of `target` as a pair, or `None`.
    O(log n).
    """,
    """
    pub fn search_range(nums: &[i32], target: i32) -> Option<(usize, usize)> {
        todo!()
    }
    """,
    """
    pub fn search_range(nums: &[i32], target: i32) -> Option<(usize, usize)> {
        let start = nums.partition_point(|&x| x < target);
        let end = nums.partition_point(|&x| x <= target);
        (start < end).then(|| (start, end - 1))
    }
    """,
    [T("run", "[5,7,7,8,8,10], 8", "search_range(&[5, 7, 7, 8, 8, 10], 8)", "Some((3, 4))"),
     T("missing", "[5,7,7,8,8,10], 6", "search_range(&[5, 7, 7, 8, 8, 10], 6)", "None"),
     T("empty_slice", "[], 0", "search_range(&[], 0)", "None"),
     T("single_match", "[1], 1", "search_range(&[1], 1)", "Some((0, 0))"),
     T("run_at_the_end", "[1,2,2], 2", "search_range(&[1, 2, 2], 2)", "Some((1, 2))")],
    [T("empty", "[], 0", "search_range(&[], 0)", "None"),
     T("outside_both_ends", "[2,3,3], 1 and 4", "(search_range(&[2, 3, 3], 1), search_range(&[2, 3, 3], 4))", "(None, None)"),
     T("negatives", "[-5,-5,-3,0], -5", "search_range(&[-5, -5, -3, 0], -5)", "Some((0, 1))"),
     T("extremes", "[i32::MIN, i32::MIN, i32::MAX], i32::MIN and i32::MAX", "(search_range(&v, i32::MIN), search_range(&v, i32::MAX))", "(Some((0, 1)), Some((2, 2)))",
       setup="let v = [i32::MIN, i32::MIN, i32::MAX];"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(405);
         for _ in 0..400 {
             let n = rng.below(14);
             let mut nums: Vec<i32> = rng.vec(n, -5, 5);
             nums.sort_unstable();
             let target = rng.int(-6, 6) as i32;
             let first = nums.iter().position(|&x| x == target);
             let last = nums.iter().rposition(|&x| x == target);
             let want = first.zip(last);
             check!(format!("nums = {nums:?}, target = {target}"), search_range(&nums, target), want);
         }
     }

     #[test]
     fn scale_long_runs() {
         // Four runs of 500000; 200000 lookups. Walking outward from a hit costs a whole run each time.
         let v: Vec<i32> = (0..2_000_000).map(|i| i / 500_000).collect();
         let total: usize = (0..200_000).map(|q| search_range(&v, q % 4).map_or(0, |(a, b)| b - a + 1)).sum();
         check!("nums = 500000 × 0, 1, 2, 3; 200000 lookups", total, 100_000_000_000usize);
     }
     """,
     T("all_same", "[2,2,2], 2", "search_range(&[2, 2, 2], 2)", "Some((0, 2))"),
     T("big_run", "10⁶ copies of 1 between 0s and 2s", "search_range(&v, 1)", "Some((10, 1_000_009))",
       setup="let mut v = vec![0; 10];\nv.extend(std::iter::repeat(1).take(1_000_000));\nv.extend([2, 2]);")],
    [("approach", "The first index is 'how many are smaller'; one past the last is 'how many are smaller or equal'."),
     ("rust", "Two `partition_point` calls with `<` and `<=`, then `(start < end).then(...)`.")],
    ("Both bounds come from the same monotone-predicate idea, so there are no hand-written loops to get off by one.", "O(log n)", "O(1)"),
    "Count occurrences of every value in a sorted slice with this. What's the total cost?",
    ["Lower and upper bounds with `partition_point`."],
    examples=[("nums = [5,7,7,8,8,10], target = 8", "Some((3, 4))")],
    wrong=dict(
        walk_out_from_a_hit="""
            pub fn search_range(nums: &[i32], target: i32) -> Option<(usize, usize)> {
                let hit = nums.binary_search(&target).ok()?;
                let (mut start, mut end) = (hit, hit);
                while start > 0 && nums[start - 1] == target {
                    start -= 1;
                }
                while end + 1 < nums.len() && nums[end + 1] == target {
                    end += 1;
                }
                Some((start, end))
            }
        """,
        end_is_one_past="""
            pub fn search_range(nums: &[i32], target: i32) -> Option<(usize, usize)> {
                let start = nums.partition_point(|&x| x < target);
                let end = nums.partition_point(|&x| x <= target);
                (start < end).then_some((start, end))
            }
        """,
    ),
))

P.append(prob(
    "min-in-rotated-sorted-array", "Minimum in rotated sorted array", "medium", "on-structure-and-answer", ["partition_point", "Blind 75"],
    """
    A sorted slice of distinct values was rotated, e.g. `[3,4,5,1,2]`. Return its minimum, or `None` if empty. O(log n).
    """,
    """
    pub fn find_min(nums: &[i32]) -> Option<i32> {
        todo!()
    }
    """,
    """
    pub fn find_min(nums: &[i32]) -> Option<i32> {
        let last = *nums.last()?;
        // Everything before the minimum is greater than the last element; everything from it on isn't.
        Some(nums[nums.partition_point(|&x| x > last)])
    }
    """,
    [T("rotated", "[3,4,5,1,2]", "find_min(&[3, 4, 5, 1, 2])", "Some(1)"),
     T("longer", "[4,5,6,7,0,1,2]", "find_min(&[4, 5, 6, 7, 0, 1, 2])", "Some(0)"),
     T("not_rotated_at_all", "[11,13,15,17]", "find_min(&[11, 13, 15, 17])", "Some(11)"),
     T("empty_slice", "[]", "find_min(&[])", "None"),
     T("minimum_last", "[2,3,4,5,1]", "find_min(&[2, 3, 4, 5, 1])", "Some(1)")],
    [T("not_rotated", "[11,13,15,17]", "find_min(&[11, 13, 15, 17])", "Some(11)"),
     T("single", "[1]", "find_min(&[1])", "Some(1)"),
     T("empty", "[]", "find_min(&[])", "None"),
     T("two", "[2,1]", "find_min(&[2, 1])", "Some(1)"),
     T("extremes", "[i32::MAX, i32::MIN, 0]", "find_min(&[i32::MAX, i32::MIN, 0])", "Some(i32::MIN)"),
     T("negatives", "[-1,-10,-7,-4]", "find_min(&[-1, -10, -7, -4])", "Some(-10)"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(406);
         for _ in 0..400 {
             let n = rng.below(12);
             let mut nums: Vec<i32> = rng.vec(n, -50, 50);
             nums.sort_unstable();
             nums.dedup();
             let k = if nums.is_empty() { 0 } else { rng.below(nums.len()) };
             nums.rotate_left(k);
             check!(format!("nums = {nums:?}"), find_min(&nums), nums.iter().copied().min());
         }
     }

     #[test]
     fn scale_every_rotation() {
         // Every rotation of 0..100000, as a window into the doubled slice.
         let n = 100_000;
         let doubled: Vec<i32> = (0..2 * n).map(|i| (i % n) as i32).collect();
         let bad = (0..n).filter(|&k| find_min(&doubled[k..k + n]) != Some(0)).count();
         check!("all 100000 rotations of 0..100000: how many give a minimum other than 0", bad, 0);
     }
     """],
    [("approach", "Compare each element with the last one. The rotated-away prefix is all greater; the rest is not. That's a monotone predicate."),
     ("rust", "`nums.partition_point(|&x| x > last)` is the index of the minimum.")],
    ("Comparing against the last element gives a predicate that's true then false, so the whole problem is one `partition_point`.", "O(log n)", "O(1)"),
    "What breaks if values can repeat, and what's the worst-case complexity then?",
    ["Finding a monotone predicate in a non-sorted array."],
    examples=[("nums = [3,4,5,1,2]", "Some(1)")],
    wrong=dict(
        linear_min="""
            pub fn find_min(nums: &[i32]) -> Option<i32> {
                nums.iter().copied().min()
            }
        """,
        compare_mid_with_left="""
            pub fn find_min(nums: &[i32]) -> Option<i32> {
                if nums.is_empty() {
                    return None;
                }
                let (mut lo, mut hi) = (0, nums.len() - 1);
                while lo < hi {
                    let mid = lo + (hi - lo) / 2;
                    if nums[mid] > nums[lo] {
                        lo = mid + 1;
                    } else {
                        hi = mid;
                    }
                }
                Some(nums[lo])
            }
        """,
    ),
))

P.append(prob(
    "search-in-rotated-sorted-array", "Search in rotated sorted array", "medium", "on-structure-and-answer", ["split_at", "Blind 75"],
    """
    Find `target` in a rotated sorted slice of distinct values. Return its index or `None`. O(log n).
    """,
    """
    pub fn search_rotated(nums: &[i32], target: i32) -> Option<usize> {
        todo!()
    }
    """,
    """
    pub fn search_rotated(nums: &[i32], target: i32) -> Option<usize> {
        let last = *nums.last()?;
        let pivot = nums.partition_point(|&x| x > last);
        let (high, low) = nums.split_at(pivot);
        if target > last {
            high.binary_search(&target).ok()
        } else {
            low.binary_search(&target).ok().map(|i| i + pivot)
        }
    }
    """,
    [T("found", "[4,5,6,7,0,1,2], 0", "search_rotated(&[4, 5, 6, 7, 0, 1, 2], 0)", "Some(4)"),
     T("missing", "[4,5,6,7,0,1,2], 3", "search_rotated(&[4, 5, 6, 7, 0, 1, 2], 3)", "None"),
     T("single_missing", "[1], 0", "search_rotated(&[1], 0)", "None"),
     T("in_the_first_run", "[4,5,6,7,0,1,2], 6", "search_rotated(&[4, 5, 6, 7, 0, 1, 2], 6)", "Some(2)"),
     T("empty_slice", "[], 5", "search_rotated(&[], 5)", "None")],
    [T("left_part", "[4,5,6,7,0,1,2], 5", "search_rotated(&[4, 5, 6, 7, 0, 1, 2], 5)", "Some(1)"),
     T("single_miss", "[1], 0", "search_rotated(&[1], 0)", "None"),
     T("empty", "[], 1", "search_rotated(&[], 1)", "None"),
     T("not_rotated", "[1,3,5], 5", "search_rotated(&[1, 3, 5], 5)", "Some(2)"),
     T("target_equals_last", "[4,5,6,7,0,1,2], 2", "search_rotated(&[4, 5, 6, 7, 0, 1, 2], 2)", "Some(6)"),
     T("target_equals_first", "[4,5,6,7,0,1,2], 4", "search_rotated(&[4, 5, 6, 7, 0, 1, 2], 4)", "Some(0)"),
     T("extremes", "[i32::MAX, i32::MIN, 0], each value", "(search_rotated(&v, i32::MAX), search_rotated(&v, i32::MIN), search_rotated(&v, 0))", "(Some(0), Some(1), Some(2))",
       setup="let v = [i32::MAX, i32::MIN, 0];"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(407);
         for _ in 0..400 {
             let n = rng.below(12);
             let mut nums: Vec<i32> = rng.vec(n, -30, 30);
             nums.sort_unstable();
             nums.dedup();
             let k = if nums.is_empty() { 0 } else { rng.below(nums.len()) };
             nums.rotate_left(k);
             let target = rng.int(-32, 32) as i32;
             check!(format!("nums = {nums:?}, target = {target}"), search_rotated(&nums, target), nums.iter().position(|&x| x == target));
         }
     }

     #[test]
     fn scale_every_rotation() {
         let n = 100_000;
         let doubled: Vec<i32> = (0..2 * n).map(|i| (i % n) as i32).collect();
         // In rotation k, value v sits at (v - k) mod n.
         let bad = (0..n).filter(|&k| { let t = ((k * 7 + 3) % n) as i32; search_rotated(&doubled[k..k + n], t) != Some((t as usize + n - k) % n) }).count();
         check!("all 100000 rotations of 0..100000, one lookup each: how many are wrong", bad, 0);
     }
     """],
    [("approach", "Find the rotation point first (previous problem), then do an ordinary search in the half that could contain the target."),
     ("rust", "`split_at(pivot)` gives two sorted slices; `binary_search(..).ok()` turns the result into an `Option`.")],
    ("Splitting the problem into 'find the pivot' and 'search a sorted half' avoids the error-prone single-loop version with four cases.", "O(log n)", "O(1)"),
    "Solve it in a single loop without finding the pivot first. Which version would you rather debug?",
    ["Reusing `partition_point` + `split_at` + `binary_search`."],
    related=["S3"],
    wrong=dict(
        linear_scan="""
            pub fn search_rotated(nums: &[i32], target: i32) -> Option<usize> {
                nums.iter().position(|&x| x == target)
            }
        """,
        last_goes_to_the_first_run="""
            pub fn search_rotated(nums: &[i32], target: i32) -> Option<usize> {
                let last = *nums.last()?;
                let pivot = nums.partition_point(|&x| x > last);
                let (high, low) = nums.split_at(pivot);
                if target >= last {
                    high.binary_search(&target).ok()
                } else {
                    low.binary_search(&target).ok().map(|i| i + pivot)
                }
            }
        """,
    ),
))

P.append(prob(
    "search-a-2d-matrix", "Search a 2-D matrix", "medium", "on-structure-and-answer", ["partition_point", "2-D"],
    """
    Each row of `matrix` is sorted, and each row starts after the previous row ends. Return whether `target`
    is in it. O(log(rows · cols)).
    """,
    """
    pub fn search_matrix(matrix: &[Vec<i32>], target: i32) -> bool {
        todo!()
    }
    """,
    """
    pub fn search_matrix(matrix: &[Vec<i32>], target: i32) -> bool {
        // The last row whose first element is <= target is the only row that can hold it.
        let rows = matrix.partition_point(|row| row.first().is_some_and(|&x| x <= target));
        rows > 0 && matrix[rows - 1].binary_search(&target).is_ok()
    }
    """,
    [T("found", "[[1,3,5,7],[10,11,16,20],[23,30,34,60]], 3", "search_matrix(&[vec![1, 3, 5, 7], vec![10, 11, 16, 20], vec![23, 30, 34, 60]], 3)", "true"),
     T("missing", "same, 13", "search_matrix(&[vec![1, 3, 5, 7], vec![10, 11, 16, 20], vec![23, 30, 34, 60]], 13)", "false"),
     T("first_of_a_row", "same, 10", "search_matrix(&[vec![1, 3, 5, 7], vec![10, 11, 16, 20], vec![23, 30, 34, 60]], 10)", "true"),
     T("past_the_last_cell", "same, 61", "search_matrix(&[vec![1, 3, 5, 7], vec![10, 11, 16, 20], vec![23, 30, 34, 60]], 61)", "false"),
     T("one_cell", "[[5]], 5", "search_matrix(&[vec![5]], 5)", "true")],
    [T("before_all", "[[5]], 1", "search_matrix(&[vec![5]], 1)", "false"),
     T("last_cell", "[[1,2],[3,4]], 4", "search_matrix(&[vec![1, 2], vec![3, 4]], 4)", "true"),
     T("empty", "[]", "search_matrix(&[], 1)", "false"),
     T("between_rows", "[[1,3],[7,9]], 5", "search_matrix(&[vec![1, 3], vec![7, 9]], 5)", "false"),
     T("single_column", "[[1],[4],[9]], 4 and 5", "(search_matrix(&m, 4), search_matrix(&m, 5))", "(true, false)", setup="let m = [vec![1], vec![4], vec![9]];"),
     T("extremes", "[[i32::MIN, 0],[5, i32::MAX]], i32::MIN and i32::MAX", "(search_matrix(&m, i32::MIN), search_matrix(&m, i32::MAX))", "(true, true)",
       setup="let m = [vec![i32::MIN, 0], vec![5, i32::MAX]];"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(408);
         for _ in 0..400 {
             let (r, c) = (1 + rng.below(4), 1 + rng.below(4));
             let mut vals: Vec<i32> = rng.vec(r * c, -40, 40);
             vals.sort_unstable();
             let m: Vec<Vec<i32>> = vals.chunks(c).map(|ch| ch.to_vec()).collect();
             let target = rng.int(-42, 42) as i32;
             check!(format!("matrix = {m:?}, target = {target}"), search_matrix(&m, target), vals.contains(&target));
         }
     }

     #[test]
     fn scale_tall_matrix() {
         // 100000 rows of two values each; 200000 lookups.
         let m: Vec<Vec<i32>> = (0..100_000).map(|i| vec![4 * i, 4 * i + 2]).collect();
         let found = (0..200_000).filter(|&t| search_matrix(&m, 2 * t)).count();
         check!("rows [4i, 4i + 2] for i < 100000; look up every even number below 400000", found, 200_000);
     }
     """],
    [("approach", "First pick the row: the last one whose first element is ≤ target. Then search inside it."),
     ("rust", "`partition_point` works on a slice of rows too; the predicate just looks at `row[0]`.")],
    ("Two binary searches, one over rows and one within a row, cost O(log r + log c) = O(log rc) without any index arithmetic.", "O(log(r·c))", "O(1)"),
    "What if only rows and columns were sorted separately (each row and each column ascending)?",
    ["`partition_point` over a slice of `Vec`s."],
    wrong=dict(
        scan_every_cell="""
            pub fn search_matrix(matrix: &[Vec<i32>], target: i32) -> bool {
                matrix.iter().flatten().any(|&x| x == target)
            }
        """,
        scan_rows_then_search="""
            pub fn search_matrix(matrix: &[Vec<i32>], target: i32) -> bool {
                matrix.iter().any(|row| row.first().is_some_and(|&x| x <= target) && row.last().is_some_and(|&x| x >= target) && row.binary_search(&target).is_ok())
            }
        """,
        row_by_strictly_less="""
            pub fn search_matrix(matrix: &[Vec<i32>], target: i32) -> bool {
                let rows = matrix.partition_point(|row| row.first().is_some_and(|&x| x < target));
                rows > 0 && matrix[rows - 1].binary_search(&target).is_ok()
            }
        """,
    ),
))

P.append(prob(
    "koko-eating-bananas", "Koko eating bananas", "medium", "on-structure-and-answer", ["search on the answer", "div_ceil"],
    """
    Koko eats at `k` bananas per hour, one pile at a time; a pile with fewer than `k` left still takes the whole
    hour. Return the smallest `k` that finishes all piles within `hours`, or `None` if it's impossible
    (fewer hours than piles).
    """,
    """
    pub fn min_eating_speed(piles: &[u32], hours: u64) -> Option<u32> {
        todo!()
    }
    """,
    """
    pub fn min_eating_speed(piles: &[u32], hours: u64) -> Option<u32> {
        if piles.is_empty() || (piles.len() as u64) > hours {
            return None;
        }
        let needed = |k: u32| piles.iter().map(|&p| u64::from(p.div_ceil(k))).sum::<u64>();
        let (mut lo, mut hi) = (1, *piles.iter().max()?);
        while lo < hi {
            let mid = lo + (hi - lo) / 2;
            if needed(mid) <= hours {
                hi = mid;
            } else {
                lo = mid + 1;
            }
        }
        Some(lo)
    }
    """,
    [T("four", "[3,6,7,11], 8 hours", "min_eating_speed(&[3, 6, 7, 11], 8)", "Some(4)"),
     T("tight", "[30,11,23,4,20], 5 hours", "min_eating_speed(&[30, 11, 23, 4, 20], 5)", "Some(30)"),
     T("six_hours", "[30,11,23,4,20], 6 hours", "min_eating_speed(&[30, 11, 23, 4, 20], 6)", "Some(23)"),
     T("fewer_hours_than_piles", "[1,1,1], 2 hours", "min_eating_speed(&[1, 1, 1], 2)", "None"),
     T("leftover_still_costs_an_hour", "[10], 3 hours", "min_eating_speed(&[10], 3)", "Some(4)")],
    [T("one_spare_hour", "[30,11,23,4,20], 6 hours", "min_eating_speed(&[30, 11, 23, 4, 20], 6)", "Some(23)"),
     T("impossible", "[1,1,1], 2 hours", "min_eating_speed(&[1, 1, 1], 2)", "None"),
     T("huge_pile", "[10⁹], 2 hours", "min_eating_speed(&[1_000_000_000], 2)", "Some(500_000_000)"),
     T("many_piles", "10⁵ piles of 10⁹, 10¹⁴ hours", "min_eating_speed(&v, 100_000_000_000_000)", "Some(1)", setup="let v = vec![1_000_000_000u32; 100_000];"),
     T("no_piles", "[], 5 hours", "min_eating_speed(&[], 5)", "None"),
     T("one_hour_per_pile", "[3,9,4], 3 hours", "min_eating_speed(&[3, 9, 4], 3)", "Some(9)"),
     T("max_pile_values", "[u32::MAX; 2], 4 hours", "min_eating_speed(&[u32::MAX, u32::MAX], 4)", "Some(2_147_483_648)"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(409);
         for _ in 0..400 {
             let n = rng.below(6);
             let piles: Vec<u32> = rng.vec(n, 1, 30);
             let hours = rng.int(0, 40) as u64;
             let top = piles.iter().copied().max().unwrap_or(0);
             let want = (1..=top).find(|&k| piles.iter().map(|&p| u64::from(p.div_ceil(k))).sum::<u64>() <= hours);
             check!(format!("piles = {piles:?}, hours = {hours}"), min_eating_speed(&piles, hours), want);
         }
     }

     #[test]
     fn scale_big_answer() {
         // 10⁵ piles of 10⁹ with two hours each: the answer is 5·10⁸, far from 1.
         let v = vec![1_000_000_000u32; 100_000];
         check!("10⁵ piles of 10⁹, 2·10⁵ hours", min_eating_speed(&v, 200_000), Some(500_000_000));
     }
     """],
    [("approach", "Faster eating never takes more hours, so 'finishes in time' is monotone in `k`. Binary search `k` between 1 and the largest pile."),
     ("rust", "`p.div_ceil(k)` is the hours for one pile. Sum in `u64`: 10⁵ piles × 10⁹ hours overflows `u32`.")],
    ("Searching on the answer: each probe costs O(n), and there are O(log max) probes.", "O(n log max)", "O(1)"),
    "How would you pick a tighter lower bound than 1?",
    ["Binary search on the answer with a monotone feasibility check.", "`div_ceil` instead of `(p + k - 1) / k`."],
    wrong=dict(
        try_every_speed="""
            pub fn min_eating_speed(piles: &[u32], hours: u64) -> Option<u32> {
                let top = *piles.iter().max()?;
                (1..=top).find(|&k| piles.iter().map(|&p| u64::from(p.div_ceil(k))).sum::<u64>() <= hours)
            }
        """,
        floor_division="""
            pub fn min_eating_speed(piles: &[u32], hours: u64) -> Option<u32> {
                if piles.is_empty() || (piles.len() as u64) > hours {
                    return None;
                }
                let needed = |k: u32| piles.iter().map(|&p| u64::from(p / k)).sum::<u64>();
                let (mut lo, mut hi) = (1, *piles.iter().max()?);
                while lo < hi {
                    let mid = lo + (hi - lo) / 2;
                    if needed(mid) <= hours {
                        hi = mid;
                    } else {
                        lo = mid + 1;
                    }
                }
                Some(lo)
            }
        """,
        hours_summed_in_u32="""
            pub fn min_eating_speed(piles: &[u32], hours: u64) -> Option<u32> {
                if piles.is_empty() || (piles.len() as u64) > hours {
                    return None;
                }
                let needed = |k: u32| piles.iter().map(|&p| p.div_ceil(k)).sum::<u32>();
                let (mut lo, mut hi) = (1, *piles.iter().max()?);
                while lo < hi {
                    let mid = lo + (hi - lo) / 2;
                    if u64::from(needed(mid)) <= hours {
                        hi = mid;
                    } else {
                        lo = mid + 1;
                    }
                }
                Some(lo)
            }
        """,
    ),
))

P.append(prob(
    "time-based-kv-store", "Time-based key-value store", "medium", "on-structure-and-answer", ["BTreeMap::range", "HashMap"],
    """
    `set(key, value, t)` stores `value` for `key` at time `t`. `get(key, t)` returns the value set at the latest
    time `≤ t`, or `None`. Times can arrive in any order.
    """,
    """
    use std::collections::{BTreeMap, HashMap};

    #[derive(Default)]
    pub struct TimeMap {
        entries: HashMap<String, BTreeMap<u64, String>>,
    }

    impl TimeMap {
        pub fn new() -> Self {
            Self::default()
        }

        pub fn set(&mut self, key: &str, value: &str, t: u64) {
            todo!()
        }

        pub fn get(&self, key: &str, t: u64) -> Option<&str> {
            todo!()
        }
    }
    """,
    """
    use std::collections::{BTreeMap, HashMap};

    #[derive(Default)]
    pub struct TimeMap {
        entries: HashMap<String, BTreeMap<u64, String>>,
    }

    impl TimeMap {
        pub fn new() -> Self {
            Self::default()
        }

        pub fn set(&mut self, key: &str, value: &str, t: u64) {
            self.entries.entry(key.to_string()).or_default().insert(t, value.to_string());
        }

        pub fn get(&self, key: &str, t: u64) -> Option<&str> {
            self.entries.get(key)?.range(..=t).next_back().map(|(_, v)| v.as_str())
        }
    }
    """,
    [T("latest_before", "set foo=bar@1, foo=bar2@4; get @1, @3, @4, @5", '(m.get("foo", 1), m.get("foo", 3), m.get("foo", 4), m.get("foo", 5))',
       '(Some("bar"), Some("bar"), Some("bar2"), Some("bar2"))', setup='let mut m = TimeMap::new();\nm.set("foo", "bar", 1);\nm.set("foo", "bar2", 4);'),
     T("too_early", "set a=x@10; get @9", 'm.get("a", 9)', "None", setup='let mut m = TimeMap::new();\nm.set("a", "x", 10);'),
     T("key_never_set", "set a=x@1; get b@5", 'm.get("b", 5)', "None", setup='let mut m = TimeMap::new();\nm.set("a", "x", 1);'),
     T("keys_are_separate", "set a=1@1, b=2@2; get a@5 and b@5", '(m.get("a", 5), m.get("b", 5))', '(Some("1"), Some("2"))',
       setup='let mut m = TimeMap::new();\nm.set("a", "1", 1);\nm.set("b", "2", 2);'),
     T("sets_out_of_time_order", "set k=late@9, then k=early@3; get @5 and @10", '(m.get("k", 5), m.get("k", 10))', '(Some("early"), Some("late"))',
       setup='let mut m = TimeMap::new();\nm.set("k", "late", 9);\nm.set("k", "early", 3);')],
    [T("out_of_order", "set @5 then @2; get @3", 'm.get("k", 3)', 'Some("two")', setup='let mut m = TimeMap::new();\nm.set("k", "five", 5);\nm.set("k", "two", 2);'),
     T("unknown_key", "get a key never set", 'TimeMap::new().get("nope", 1).is_none()', "true"),
     T("overwrite", "set @1 twice", 'm.get("k", 1)', 'Some("new")', setup='let mut m = TimeMap::new();\nm.set("k", "old", 1);\nm.set("k", "new", 1);'),
     T("time_bounds", "set k=zero@0 and k=max@u64::MAX; get @0, @u64::MAX - 1, @u64::MAX", '(m.get("k", 0), m.get("k", u64::MAX - 1), m.get("k", u64::MAX))',
       '(Some("zero"), Some("zero"), Some("max"))', setup='let mut m = TimeMap::new();\nm.set("k", "zero", 0);\nm.set("k", "max", u64::MAX);'),
     T("unicode", "set 键=värde@2; get @3", 'm.get("键", 3)', 'Some("värde")', setup='let mut m = TimeMap::new();\nm.set("键", "värde", 2);'),
     T("empty_key_and_value", "set \"\"=\"\"@1; get @1", 'm.get("", 1)', 'Some("")', setup='let mut m = TimeMap::new();\nm.set("", "", 1);'),
     """
     #[test]
     fn random_vs_brute_force() {
         let keys = ["a", "b", "c"];
         let vals = ["x", "y", "z", "w"];
         let mut rng = anneal_prelude::Rng::new(410);
         for _ in 0..100 {
             let mut m = TimeMap::new();
             let mut log: Vec<(&str, &str, u64)> = Vec::new();
             for _ in 0..20 {
                 if rng.bool() {
                     let (k, v, t) = (*rng.pick(&keys), *rng.pick(&vals), rng.int(0, 10) as u64);
                     m.set(k, v, t);
                     log.push((k, v, t));
                 } else {
                     let (k, t) = (*rng.pick(&keys), rng.int(0, 11) as u64);
                     // Brute force: the last write to k with the largest time <= t.
                     let best = log.iter().filter(|e| e.0 == k && e.2 <= t).map(|e| e.2).max();
                     let want = best.and_then(|b| log.iter().rev().find(|e| e.0 == k && e.2 == b).map(|e| e.1));
                     check!(format!("after set calls {log:?}: get({k:?}, {t})"), m.get(k, t), want);
                 }
             }
         }
     }

     #[test]
     fn scale_100k_sets_and_gets() {
         let mut m = TimeMap::new();
         for t in 0..100_000u64 {
             m.set("k", if t % 2 == 0 { "even" } else { "odd" }, 2 * t);
         }
         let odd = (0..200_000u64).filter(|&t| m.get("k", t) == Some("odd")).count();
         check!("100000 sets at times 0, 2, 4, …; 200000 gets", odd, 100_000);
     }
     """],
    [("rust", "`BTreeMap::range(..=t).next_back()` is the entry with the largest key ≤ t."),
     ("approach", "One sorted map of time → value per key. The sorted map does the binary search for you.")],
    ("The ordered map keeps each key's history sorted even when times arrive out of order, which a `Vec` plus binary search wouldn't.", "O(log n) per call", "O(n)"),
    "If `set` always arrives in increasing time, what simpler structure would you use?",
    ["`BTreeMap::range` for floor lookups.", "`entry(..).or_default()`."],
    related=["S4"],
    wrong=dict(
        scan_the_history="""
            use std::collections::HashMap;

            #[derive(Default)]
            pub struct TimeMap {
                history: HashMap<String, Vec<(u64, String)>>,
            }

            impl TimeMap {
                pub fn new() -> Self {
                    Self::default()
                }

                pub fn set(&mut self, key: &str, value: &str, t: u64) {
                    let list = self.history.entry(key.to_string()).or_default();
                    list.retain(|(time, _)| *time != t);
                    list.push((t, value.to_string()));
                }

                pub fn get(&self, key: &str, t: u64) -> Option<&str> {
                    self.history.get(key)?.iter().filter(|(time, _)| *time <= t).max_by_key(|(time, _)| *time).map(|(_, v)| v.as_str())
                }
            }
        """,
        earliest_at_or_after="""
            use std::collections::{BTreeMap, HashMap};

            #[derive(Default)]
            pub struct TimeMap {
                entries: HashMap<String, BTreeMap<u64, String>>,
            }

            impl TimeMap {
                pub fn new() -> Self {
                    Self::default()
                }

                pub fn set(&mut self, key: &str, value: &str, t: u64) {
                    self.entries.entry(key.to_string()).or_default().insert(t, value.to_string());
                }

                pub fn get(&self, key: &str, t: u64) -> Option<&str> {
                    self.entries.get(key)?.range(t..).next().map(|(_, v)| v.as_str())
                }
            }
        """,
        exact_time_only="""
            use std::collections::{BTreeMap, HashMap};

            #[derive(Default)]
            pub struct TimeMap {
                entries: HashMap<String, BTreeMap<u64, String>>,
            }

            impl TimeMap {
                pub fn new() -> Self {
                    Self::default()
                }

                pub fn set(&mut self, key: &str, value: &str, t: u64) {
                    self.entries.entry(key.to_string()).or_default().insert(t, value.to_string());
                }

                pub fn get(&self, key: &str, t: u64) -> Option<&str> {
                    self.entries.get(key)?.get(&t).map(|v| v.as_str())
                }
            }
        """,
    ),
))

# ---------------------------------------------------------------- hard searches

P.append(prob(
    "median-of-two-sorted-arrays", "Median of two sorted arrays", "hard", "hard-searches", ["partition search"],
    """
    Return the median of the combined values of two sorted slices, or `None` if both are empty. Run in
    O(log(min(m, n))): don't merge them.
    """,
    """
    pub fn median(a: &[i32], b: &[i32]) -> Option<f64> {
        todo!()
    }
    """,
    """
    pub fn median(a: &[i32], b: &[i32]) -> Option<f64> {
        let (a, b) = if a.len() <= b.len() { (a, b) } else { (b, a) };
        let (m, n) = (a.len(), b.len());
        if m + n == 0 {
            return None;
        }
        let half = (m + n + 1) / 2;
        // Take i elements from a and half - i from b for the left half; search for the right i.
        let (mut lo, mut hi) = (0, m);
        loop {
            let i = lo + (hi - lo) / 2;
            let j = half - i;
            // Widen to i64 so the out-of-range sentinels can't collide with real values.
            let a_left = if i == 0 { i64::MIN } else { i64::from(a[i - 1]) };
            let a_right = if i == m { i64::MAX } else { i64::from(a[i]) };
            let b_left = if j == 0 { i64::MIN } else { i64::from(b[j - 1]) };
            let b_right = if j == n { i64::MAX } else { i64::from(b[j]) };
            if a_left > b_right {
                hi = i - 1;
            } else if b_left > a_right {
                lo = i + 1;
            } else {
                let left = a_left.max(b_left);
                return Some(if (m + n) % 2 == 1 {
                    left as f64
                } else {
                    (left + a_right.min(b_right)) as f64 / 2.0
                });
            }
        }
    }
    """,
    [T("odd", "[1,3], [2]", "median(&[1, 3], &[2])", "Some(2.0)"),
     T("even", "[1,2], [3,4]", "median(&[1, 2], &[3, 4])", "Some(2.5)"),
     T("second_empty", "[1,2,3], []", "median(&[1, 2, 3], &[])", "Some(2.0)"),
     T("nothing_at_all", "[], []", "median(&[], &[])", "None"),
     T("same_values_in_both", "[1,2], [1,2]", "median(&[1, 2], &[1, 2])", "Some(1.5)")],
    [T("one_empty", "[], [5]", "median(&[], &[5])", "Some(5.0)"),
     T("both_empty", "[], []", "median(&[], &[])", "None"),
     T("extremes", "[i32::MIN], [i32::MAX]", "median(&[i32::MIN], &[i32::MAX])", "Some(-0.5)"),
     T("interleaved", "odds and evens up to 10⁵", "median(&odd, &even)", "Some(49_999.5)",
       setup="let odd: Vec<i32> = (0..100_000).filter(|x| x % 2 == 1).collect();\nlet even: Vec<i32> = (0..100_000).filter(|x| x % 2 == 0).collect();"),
     T("disjoint", "[1,2,3], [10,11,12,13]", "median(&[1, 2, 3], &[10, 11, 12, 13])", "Some(10.0)"),
     T("both_max", "[i32::MAX], [i32::MAX]", "median(&[i32::MAX], &[i32::MAX])", "Some(2_147_483_647.0)"),
     T("negatives", "[-5,-3], [-4]", "median(&[-5, -3], &[-4])", "Some(-4.0)"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(411);
         for _ in 0..400 {
             let (m, n) = (rng.below(7), rng.below(7));
             let mut a: Vec<i32> = rng.vec(m, -20, 20);
             let mut b: Vec<i32> = rng.vec(n, -20, 20);
             a.sort_unstable();
             b.sort_unstable();
             let mut all: Vec<i64> = a.iter().chain(&b).map(|&x| i64::from(x)).collect();
             all.sort_unstable();
             let k = all.len();
             let want = (k > 0).then(|| if k % 2 == 1 { all[k / 2] as f64 } else { (all[k / 2 - 1] + all[k / 2]) as f64 / 2.0 });
             check!(format!("a = {a:?}, b = {b:?}"), median(&a, &b), want);
         }
     }

     #[test]
     fn scale_100k_queries() {
         // a = evens, b = odds, each 200000 long; 100000 medians of prefixes a[..i], b[..j] with i, j ≥ 100000.
         let a: Vec<i32> = (0..200_000).map(|x| 2 * x).collect();
         let b: Vec<i32> = (0..200_000).map(|x| 2 * x + 1).collect();
         let bad = (0..100_000usize).filter(|&q| {
             let (i, j) = (100_000 + q * 7919 % 100_000, 100_000 + q * 104_729 % 100_000);
             // The k-th smallest of the union, from 0: 0, 1, 2, … up to 2·min(i, j), then every other value of the longer prefix.
             let m = i.min(j);
             let kth = |k: usize| (if k < 2 * m { k } else { 2 * m + 2 * (k - 2 * m) + usize::from(j > i) }) as f64;
             let t = i + j;
             let want = if t % 2 == 1 { kth(t / 2) } else { (kth(t / 2 - 1) + kth(t / 2)) / 2.0 };
             median(&a[..i], &b[..j]) != Some(want)
         }).count();
         check!("100000 medians of long prefixes of the evens and the odds: how many are wrong", bad, 0);
     }
     """],
    [("approach", "Split both arrays so the left parts together hold half the elements. The split is right when every left value ≤ every right value."),
     ("approach", "Binary search the split point in the shorter array; the other array's split follows from it."),
     ("edge case", "At the ends, use −∞/+∞ sentinels. Widen to `i64` first, or `i32::MIN` in the data collides with the sentinel.")],
    ("Searching the shorter array bounds the work by O(log min). Widening to `i64` also keeps `left + right` from overflowing for extreme values.", "O(log min(m, n))", "O(1)"),
    "Generalise this to the k-th smallest element of the union.",
    ["Binary search over a partition, not a value.", "Sentinels that can't collide: widen the type."],
    wrong=dict(
        merge_then_pick="""
            pub fn median(a: &[i32], b: &[i32]) -> Option<f64> {
                let mut all: Vec<i64> = a.iter().chain(b).map(|&x| i64::from(x)).collect();
                all.sort_unstable();
                let k = all.len();
                (k > 0).then(|| if k % 2 == 1 { all[k / 2] as f64 } else { (all[k / 2 - 1] + all[k / 2]) as f64 / 2.0 })
            }
        """,
        integer_average="""
            pub fn median(a: &[i32], b: &[i32]) -> Option<f64> {
                let (a, b) = if a.len() <= b.len() { (a, b) } else { (b, a) };
                let (m, n) = (a.len(), b.len());
                if m + n == 0 {
                    return None;
                }
                let half = (m + n + 1) / 2;
                let (mut lo, mut hi) = (0, m);
                loop {
                    let i = lo + (hi - lo) / 2;
                    let j = half - i;
                    let a_left = if i == 0 { i64::MIN } else { i64::from(a[i - 1]) };
                    let a_right = if i == m { i64::MAX } else { i64::from(a[i]) };
                    let b_left = if j == 0 { i64::MIN } else { i64::from(b[j - 1]) };
                    let b_right = if j == n { i64::MAX } else { i64::from(b[j]) };
                    if a_left > b_right {
                        hi = i - 1;
                    } else if b_left > a_right {
                        lo = i + 1;
                    } else {
                        let left = a_left.max(b_left);
                        return Some(if (m + n) % 2 == 1 { left as f64 } else { ((left + a_right.min(b_right)) / 2) as f64 });
                    }
                }
            }
        """,
    ),
))

P.append(prob(
    "split-array-largest-sum", "Split array largest sum", "hard", "hard-searches", ["search on the answer", "greedy check"],
    """
    Split `nums` into `k` non-empty contiguous parts, minimising the largest part's sum. Return that minimum.
    `1 ≤ k ≤ nums.len()`.
    """,
    """
    pub fn split_array(nums: &[u32], k: usize) -> u64 {
        todo!()
    }
    """,
    """
    pub fn split_array(nums: &[u32], k: usize) -> u64 {
        // How many parts are needed if no part may exceed `cap`?
        let parts = |cap: u64| {
            let (mut parts, mut sum) = (1, 0u64);
            for &x in nums {
                let x = u64::from(x);
                if sum + x > cap {
                    parts += 1;
                    sum = 0;
                }
                sum += x;
            }
            parts
        };
        let mut lo = nums.iter().copied().map(u64::from).max().unwrap_or(0);
        let mut hi: u64 = nums.iter().copied().map(u64::from).sum();
        while lo < hi {
            let mid = lo + (hi - lo) / 2;
            if parts(mid) <= k {
                hi = mid;
            } else {
                lo = mid + 1;
            }
        }
        lo
    }
    """,
    [T("two_parts", "[7,2,5,10,8], k = 2", "split_array(&[7, 2, 5, 10, 8], 2)", "18"),
     T("even", "[1,2,3,4,5], k = 2", "split_array(&[1, 2, 3, 4, 5], 2)", "9"),
     T("every_value_alone", "[1,4,4], k = 3", "split_array(&[1, 4, 4], 3)", "4"),
     T("one_part_is_the_total", "[1,2,3], k = 1", "split_array(&[1, 2, 3], 1)", "6"),
     T("zeros_count_as_parts", "[0,0,5], k = 2", "split_array(&[0, 0, 5], 2)", "5")],
    [T("each_alone", "[1,4,4], k = 3", "split_array(&[1, 4, 4], 3)", "4"),
     T("one_part", "[1,2,3], k = 1", "split_array(&[1, 2, 3], 1)", "6"),
     T("big_values", "[4·10⁹; 4], k = 2", "split_array(&[4_000_000_000, 4_000_000_000, 4_000_000_000, 4_000_000_000], 2)", "8_000_000_000"),
     T("long", "10⁵ ones, k = 7", "split_array(&v, 7)", "14_286", setup="let v = vec![1u32; 100_000];"),
     T("single", "[7], k = 1", "split_array(&[7], 1)", "7"),
     T("all_zero", "[0,0,0], k = 2", "split_array(&[0, 0, 0], 2)", "0"),
     T("u32_max_values", "[u32::MAX; 3], k = 1 and k = 3", "(split_array(&v, 1), split_array(&v, 3))", "(12_884_901_885, 4_294_967_295)", setup="let v = [u32::MAX; 3];"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(412);
         for _ in 0..400 {
             let n = 1 + rng.below(8);
             let nums: Vec<u32> = rng.vec(n, 0, 20);
             let k = 1 + rng.below(n);
             // Brute force: DP over (prefix length, parts used).
             let mut best = vec![vec![u64::MAX; k + 1]; n + 1];
             best[0][0] = 0;
             for i in 1..=n {
                 for p in 1..=k.min(i) {
                     for j in p - 1..i {
                         if best[j][p - 1] != u64::MAX {
                             let part: u64 = nums[j..i].iter().map(|&x| u64::from(x)).sum();
                             best[i][p] = best[i][p].min(best[j][p - 1].max(part));
                         }
                     }
                 }
             }
             check!(format!("nums = {nums:?}, k = {k}"), split_array(&nums, k), best[n][k]);
         }
     }

     #[test]
     fn scale_100k_values() {
         let mut x: u64 = 5;
         let v: Vec<u32> = (0..100_000).map(|_| { x = x.wrapping_mul(6_364_136_223_846_793_005).wrapping_add(1_442_695_040_888_963_407); ((x >> 33) % 1_000_000_000) as u32 }).collect();
         check!("10⁵ pseudo-random values below 10⁹ (LCG seed 5), k = 50", split_array(&v, 50), 943_751_813_026);
     }
     """],
    [("approach", "Guess the answer `cap`. Greedily cut whenever the running sum would exceed it; if that needs ≤ k parts, `cap` is feasible."),
     ("approach", "Feasibility is monotone in `cap`, so binary search it between the largest element and the total."),
     ("rust", "Sums of `u32`s overflow `u32`; do the arithmetic in `u64`.")],
    ("The greedy check is optimal for a fixed cap (cutting later never helps), so binary search plus an O(n) check solves it without DP.", "O(n log Σ)", "O(1)"),
    "Solve it with DP. When would you prefer the DP?",
    ["Binary search on the answer with a greedy feasibility check."],
    related=["D12"],
    wrong=dict(
        raise_the_cap_one_at_a_time="""
            pub fn split_array(nums: &[u32], k: usize) -> u64 {
                let parts = |cap: u64| {
                    let (mut parts, mut sum) = (1, 0u64);
                    for &x in nums {
                        let x = u64::from(x);
                        if sum + x > cap {
                            parts += 1;
                            sum = 0;
                        }
                        sum += x;
                    }
                    parts
                };
                let mut cap = nums.iter().copied().map(u64::from).max().unwrap_or(0);
                while parts(cap) > k {
                    cap += 1;
                }
                cap
            }
        """,
        sums_in_u32="""
            pub fn split_array(nums: &[u32], k: usize) -> u64 {
                let parts = |cap: u32| {
                    let (mut parts, mut sum) = (1, 0u32);
                    for &x in nums {
                        if sum + x > cap {
                            parts += 1;
                            sum = 0;
                        }
                        sum += x;
                    }
                    parts
                };
                let mut lo = nums.iter().copied().max().unwrap_or(0);
                let mut hi: u32 = nums.iter().sum();
                while lo < hi {
                    let mid = lo + (hi - lo) / 2;
                    if parts(mid) <= k {
                        hi = mid;
                    } else {
                        lo = mid + 1;
                    }
                }
                u64::from(lo)
            }
        """,
        quadratic_dp="""
            pub fn split_array(nums: &[u32], k: usize) -> u64 {
                let n = nums.len();
                let mut prefix = vec![0u64; n + 1];
                for i in 0..n {
                    prefix[i + 1] = prefix[i] + u64::from(nums[i]);
                }
                let mut best = vec![u64::MAX; n + 1];
                best[0] = 0;
                for _ in 0..k {
                    let mut next = vec![u64::MAX; n + 1];
                    for i in 1..=n {
                        for j in 0..i {
                            if best[j] != u64::MAX {
                                next[i] = next[i].min(best[j].max(prefix[i] - prefix[j]));
                            }
                        }
                    }
                    best = next;
                }
                best[n]
            }
        """,
    ),
))

P.append(prob(
    "kth-smallest-pair-distance", "K-th smallest pair distance", "hard", "hard-searches", ["search on the answer", "two pointers"],
    """
    The distance of a pair is `|a - b|`. Return the `k`-th smallest distance among all pairs `i < j`
    (`k` counts from 1).
    """,
    """
    pub fn smallest_distance_pair(nums: &[i32], k: usize) -> u32 {
        todo!()
    }
    """,
    """
    pub fn smallest_distance_pair(nums: &[i32], k: usize) -> u32 {
        let mut v = nums.to_vec();
        v.sort_unstable();
        // Pairs with distance <= d, counted with a sliding window over the sorted values.
        let count = |d: u32| {
            let (mut total, mut left) = (0usize, 0);
            for right in 0..v.len() {
                while v[right].abs_diff(v[left]) > d {
                    left += 1;
                }
                total += right - left;
            }
            total
        };
        let (mut lo, mut hi) = (0, v[v.len() - 1].abs_diff(v[0]));
        while lo < hi {
            let mid = lo + (hi - lo) / 2;
            if count(mid) >= k {
                hi = mid;
            } else {
                lo = mid + 1;
            }
        }
        lo
    }
    """,
    [T("zero", "[1,3,1], k = 1", "smallest_distance_pair(&[1, 3, 1], 1)", "0"),
     T("largest", "[1,6,1], k = 3", "smallest_distance_pair(&[1, 6, 1], 3)", "5"),
     T("equal_values", "[1,1,1], k = 2", "smallest_distance_pair(&[1, 1, 1], 2)", "0"),
     T("one_pair", "[5,1], k = 1", "smallest_distance_pair(&[5, 1], 1)", "4"),
     T("repeated_distances_count_separately", "[1,1,2], k = 3", "smallest_distance_pair(&[1, 1, 2], 3)", "1")],
    [T("all_equal", "[1,1,1], k = 2", "smallest_distance_pair(&[1, 1, 1], 2)", "0"),
     T("extremes", "[i32::MIN, i32::MAX], k = 1", "smallest_distance_pair(&[i32::MIN, i32::MAX], 1)", "u32::MAX"),
     T("many", "0..10⁴, k = 10⁶", "smallest_distance_pair(&v, 1_000_000)", "101", setup="let v: Vec<i32> = (0..10_000).collect();"),
     T("negatives", "[-3,-1,4], k = 2", "smallest_distance_pair(&[-3, -1, 4], 2)", "5"),
     T("k_is_the_last_pair", "[1,5,9,20], k = 6", "smallest_distance_pair(&[1, 5, 9, 20], 6)", "19"),
     T("unsorted_input", "[9,1,5], k = 1 and k = 2", "(smallest_distance_pair(&[9, 1, 5], 1), smallest_distance_pair(&[9, 1, 5], 2))", "(4, 4)"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(413);
         for _ in 0..400 {
             let n = 2 + rng.below(8);
             let nums: Vec<i32> = rng.vec(n, -20, 20);
             let mut all: Vec<u32> = (0..n).flat_map(|i| (i + 1..n).map(move |j| (i, j))).map(|(i, j)| nums[i].abs_diff(nums[j])).collect();
             all.sort_unstable();
             let k = 1 + rng.below(all.len());
             check!(format!("nums = {nums:?}, k = {k}"), smallest_distance_pair(&nums, k), all[k - 1]);
         }
     }

     #[test]
     fn scale_100k() {
         // 0..100000 shuffled; pairs with distance ≤ d number d·n − d(d+1)/2.
         let mut v: Vec<i32> = (0..100_000).collect();
         anneal_prelude::Rng::new(414).shuffle(&mut v);
         check!("a shuffle of 0..100000, k = 2.5·10⁹", smallest_distance_pair(&v, 2_500_000_000), 29_290);
     }
     """],
    [("approach", "Binary search the distance `d`: count the pairs with distance ≤ d; the answer is the smallest d with count ≥ k."),
     ("approach", "After sorting, pairs within distance d of each right end form a window; slide it in O(n)."),
     ("rust", "`a.abs_diff(b)` returns `u32` and can't overflow, even for `i32::MIN` and `i32::MAX`.")],
    ("There are O(n²) pairs, but counting those within d takes O(n) on sorted data, so the whole search is O(n log n + n log W).", "O(n log n + n log W)", "O(n)"),
    "How would a heap-based approach compare for small k?",
    ["Counting instead of listing.", "`abs_diff` on signed integers."],
    constraints=["2 ≤ nums.len() ≤ 10⁵", "1 ≤ k ≤ n·(n − 1)/2"],
    wrong=dict(
        count_every_pair="""
            pub fn smallest_distance_pair(nums: &[i32], k: usize) -> u32 {
                let count = |d: u32| (0..nums.len()).map(|i| (i + 1..nums.len()).filter(|&j| nums[i].abs_diff(nums[j]) <= d).count()).sum::<usize>();
                let (mut lo, mut hi) = (0, u32::MAX);
                while lo < hi {
                    let mid = lo + (hi - lo) / 2;
                    if count(mid) >= k {
                        hi = mid;
                    } else {
                        lo = mid + 1;
                    }
                }
                lo
            }
        """,
        counts_strictly_closer="""
            pub fn smallest_distance_pair(nums: &[i32], k: usize) -> u32 {
                let mut v = nums.to_vec();
                v.sort_unstable();
                let count = |d: u32| {
                    let (mut total, mut left) = (0usize, 0);
                    for right in 0..v.len() {
                        while v[right].abs_diff(v[left]) >= d && left < right {
                            left += 1;
                        }
                        total += right - left;
                    }
                    total
                };
                let (mut lo, mut hi) = (0, v[v.len() - 1].abs_diff(v[0]));
                while lo < hi {
                    let mid = lo + (hi - lo) / 2;
                    if count(mid) >= k {
                        hi = mid;
                    } else {
                        lo = mid + 1;
                    }
                }
                lo
            }
        """,
    ),
))

P.append(prob(
    "fix-mid-overflow-and-infinite-loop", "Fix: mid overflow and an infinite loop", "hard", "hard-searches", ["overflow", "rounding"],
    """
    `last_true` finds the largest `x` in `lo..=hi` for which `pred(x)` is true (pred is true up to some
    point, then false). It has two bugs: one panics near `u32::MAX`, and one loops forever on a range of
    two values. Fix both by changing one line.
    """,
    """
    /// The largest x in lo..=hi with pred(x) true, or None if pred(lo) is false.
    /// pred must be true up to some point and false after it.
    pub fn last_true(lo: u32, hi: u32, pred: impl Fn(u32) -> bool) -> Option<u32> {
        if !pred(lo) {
            return None;
        }
        let (mut lo, mut hi) = (lo, hi);
        while lo < hi {
            let mid = (lo + hi) / 2;
            if pred(mid) {
                lo = mid;
            } else {
                hi = mid - 1;
            }
        }
        Some(lo)
    }
    """,
    """
    /// The largest x in lo..=hi with pred(x) true, or None if pred(lo) is false.
    /// pred must be true up to some point and false after it.
    pub fn last_true(lo: u32, hi: u32, pred: impl Fn(u32) -> bool) -> Option<u32> {
        if !pred(lo) {
            return None;
        }
        let (mut lo, mut hi) = (lo, hi);
        while lo < hi {
            let mid = lo + (hi - lo).div_ceil(2);
            if pred(mid) {
                lo = mid;
            } else {
                hi = mid - 1;
            }
        }
        Some(lo)
    }
    """,
    [T("big_range", "0..=u32::MAX, x ≤ 3·10⁹", "last_true(0, u32::MAX, |x| x <= 3_000_000_000)", "Some(3_000_000_000)"),
     T("squares", "0..=100, x² ≤ 50", "last_true(0, 100, |x| x * x <= 50)", "Some(7)"),
     T("single_value", "7..=7, always true", "last_true(7, 7, |_| true)", "Some(7)"),
     T("pair_both_true", "3..=4, x ≤ 4", "last_true(3, 4, |x| x <= 4)", "Some(4)"),
     T("false_from_the_start", "10..=20, never true", "last_true(10, 20, |_| false)", "None")],
    [T("two_values", "0..=1, always true", "last_true(0, 1, |_| true)", "Some(1)"),
     T("none", "5..=9, never true", "last_true(5, 9, |_| false)", "None"),
     T("top_of_range", "u32::MAX - 1..=u32::MAX, always true", "last_true(u32::MAX - 1, u32::MAX, |_| true)", "Some(u32::MAX)"),
     T("whole_range_true", "0..=u32::MAX, always true", "last_true(0, u32::MAX, |_| true)", "Some(u32::MAX)"),
     T("boundary_at_2_31", "0..=u32::MAX, x < 2³¹", "last_true(0, u32::MAX, |x| x < 2_147_483_648)", "Some(2_147_483_647)"),
     T("only_lo_true", "0..=u32::MAX, x == 0", "last_true(0, u32::MAX, |x| x == 0)", "Some(0)"),
     T("few_calls", "0..=u32::MAX, x ≤ 2³¹; count pred calls", "(found, calls.get() <= 34)", "(Some(2_147_483_648), true)",
       setup="let calls = std::cell::Cell::new(0);\nlet found = last_true(0, u32::MAX, |x| {\n    calls.set(calls.get() + 1);\n    x <= 2_147_483_648\n});"),
     """
     #[test]
     fn random_vs_brute_force() {
         let mut rng = anneal_prelude::Rng::new(415);
         for i in 0..400 {
             let lo = if i % 2 == 0 { rng.int(0, 50) as u32 } else { u32::MAX - rng.int(0, 50) as u32 };
             let hi = lo.saturating_add(rng.int(0, 20) as u32);
             let edge = lo.saturating_add(rng.int(0, 25) as u32).saturating_sub(2);
             let pred = |x: u32| x <= edge;
             let want = (lo..=hi).filter(|&x| pred(x)).last();
             check!(format!("lo = {lo}, hi = {hi}, pred = x <= {edge}"), last_true(lo, hi, pred), want);
         }
     }
     """],
    [("rust", "`lo + hi` overflows `u32` once both are past 2³¹. `lo + (hi - lo) / 2` can't."),
     ("approach", "With `lo = mid`, `mid` must round up, or `lo..=lo+1` never shrinks when `pred(lo+1)` is true."),
     ("rust", "`(hi - lo).div_ceil(2)` rounds up without the `+ 1` that would overflow when the range is `0..=u32::MAX`.")],
    ("The midpoint must round toward the side that moves: here `lo = mid`, so round up. `div_ceil` gives that without another overflow.", "O(log range)", "O(1)"),
    "Rewrite it with a half-open range. Which rounding bugs disappear?",
    ["Overflow-free midpoints.", "Rounding toward the side that moves."],
    mode="fix", rules=dict(lines=1, methods=["checked_add", "wrapping_add", "saturating_add"], types=["u64", "u128", "i64"]),
    wrong=dict(
        rounds_down="""
            /// The largest x in lo..=hi with pred(x) true, or None if pred(lo) is false.
            /// pred must be true up to some point and false after it.
            pub fn last_true(lo: u32, hi: u32, pred: impl Fn(u32) -> bool) -> Option<u32> {
                if !pred(lo) {
                    return None;
                }
                let (mut lo, mut hi) = (lo, hi);
                while lo < hi {
                    let mid = lo + (hi - lo) / 2;
                    if pred(mid) {
                        lo = mid;
                    } else {
                        hi = mid - 1;
                    }
                }
                Some(lo)
            }
        """,
        rounds_up_but_overflows="""
            /// The largest x in lo..=hi with pred(x) true, or None if pred(lo) is false.
            /// pred must be true up to some point and false after it.
            pub fn last_true(lo: u32, hi: u32, pred: impl Fn(u32) -> bool) -> Option<u32> {
                if !pred(lo) {
                    return None;
                }
                let (mut lo, mut hi) = (lo, hi);
                while lo < hi {
                    let mid = (lo + hi + 1) / 2;
                    if pred(mid) {
                        lo = mid;
                    } else {
                        hi = mid - 1;
                    }
                }
                Some(lo)
            }
        """,
    ),
))

COMPANIES = {
    "binary-search": ["Amazon", "Google", "Apple", "Microsoft", "Adobe"],
    "search-insert-position": ["Amazon", "Google", "Apple", "Microsoft", "Adobe", "Bloomberg"],
    "first-bad-version": ["Meta", "Amazon", "Google", "Microsoft"],
    "integer-square-root": ["Meta", "Apple", "Amazon", "Google", "Microsoft", "Bloomberg"],
    "first-and-last-position": ["Meta", "Amazon", "Google", "Microsoft", "Bloomberg", "LinkedIn", "Uber"],
    "min-in-rotated-sorted-array": ["Meta", "Amazon", "Google", "Microsoft", "Bloomberg"],
    "search-in-rotated-sorted-array": ["Meta", "Apple", "Amazon", "Google", "Microsoft", "Bloomberg", "LinkedIn", "Uber"],
    "search-a-2d-matrix": ["Meta", "Apple", "Amazon", "Google", "Microsoft", "Bloomberg"],
    "koko-eating-bananas": ["Meta", "Amazon", "Google", "Microsoft", "DoorDash", "Uber"],
    "time-based-kv-store": ["Apple", "Amazon", "Google", "Microsoft", "Uber"],
    "median-of-two-sorted-arrays": ["Meta", "Apple", "Amazon", "Google", "Microsoft", "Adobe", "Bloomberg", "Goldman Sachs"],
    "split-array-largest-sum": ["Meta", "Amazon", "Google"],
    "kth-smallest-pair-distance": ["Amazon", "Google"],
}
tag_companies(P, COMPANIES)

STAGES = [
    ("on-an-index", "On an index", "easy"),
    ("on-structure-and-answer", "On structure & answer", "medium"),
    ("hard-searches", "Hard searches", "hard"),
]

if __name__ == "__main__":
    n = write_track("d4-binary-search", "D4", "Binary search", "D", "core", 4,
                    "Half-open ranges, overflow-safe midpoints, and `partition_point` for any monotone predicate: on indices, on structure, and on the answer itself.",
                    STAGES, P)
    print("D4", n)
