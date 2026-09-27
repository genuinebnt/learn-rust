from author import T, write_track

P = []

P.append(dict(
    slug="valid-palindrome", title="Valid palindrome", level="easy", stage="two-ends", tags=["two pointers", "bytes", "Blind 75"],
    teaches=["Two indices walking inward over `as_bytes()`.", "`is_ascii_alphanumeric` and `eq_ignore_ascii_case` instead of allocating a cleaned copy."],
    statement="Return `true` if `s` reads the same forwards and backwards after ignoring case and every character that isn't an ASCII letter or digit.",
    examples=[("s = \"A man, a plan, a canal: Panama\"", "true")],
    starter="""
        pub fn is_palindrome(s: &str) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn is_palindrome(s: &str) -> bool {
            let b = s.as_bytes();
            let (mut l, mut r) = (0, b.len());
            while l < r {
                if !b[l].is_ascii_alphanumeric() {
                    l += 1;
                } else if !b[r - 1].is_ascii_alphanumeric() {
                    r -= 1;
                } else if !b[l].eq_ignore_ascii_case(&b[r - 1]) {
                    return false;
                } else {
                    l += 1;
                    r -= 1;
                }
            }
            true
        }
    """,
    visible=[
        T("panama", "s = \"A man, a plan, a canal: Panama\"", 'is_palindrome("A man, a plan, a canal: Panama")', "true"),
        T("race_a_car", "s = \"race a car\"", 'is_palindrome("race a car")', "false"),
        T("only_punctuation", "s = \" .,\"", 'is_palindrome(" .,")', "true"),
    ],
    hidden=[
        T("digits_matter", "s = \"0P\"", 'is_palindrome("0P")', "false"),
        T("empty", "s = \"\"", 'is_palindrome("")', "true"),
    ],
    hints=[("approach", "Walk one index from each end, skipping characters that don't count."),
           ("rust", "Keep `r` exclusive (compare `b[r - 1]`) so an empty string never underflows.")],
    notes=("No allocation: the comparison happens on the original bytes. An exclusive right index keeps every subtraction safe.", "O(n)", "O(1)"),
    follow_up="What changes if the input is arbitrary Unicode and 'letter' means a Unicode letter?",
    related=["S2"],
))

P.append(dict(
    slug="reverse-string", title="Reverse a string in place", level="easy", stage="two-ends", tags=["swap", "two pointers"],
    teaches=["`slice::swap` with two indices.", "Why a `String` can't be reversed byte by byte, but a `&mut [u8]` can."],
    statement="Reverse the bytes of `s` in place without calling `reverse`.",
    examples=[("s = b\"hello\"", "b\"olleh\"")],
    starter="""
        pub fn reverse_in_place(s: &mut [u8]) {
            todo!()
        }
    """,
    solution="""
        pub fn reverse_in_place(s: &mut [u8]) {
            let (mut l, mut r) = (0, s.len());
            while l + 1 < r {
                r -= 1;
                s.swap(l, r);
                l += 1;
            }
        }
    """,
    visible=[
        T("hello", "s = b\"hello\"", '{ let mut s = b"hello".to_vec(); reverse_in_place(&mut s); s }', 'b"olleh".to_vec()'),
        T("even", "s = b\"ab\"", '{ let mut s = b"ab".to_vec(); reverse_in_place(&mut s); s }', 'b"ba".to_vec()'),
    ],
    hidden=[
        T("empty", "s = b\"\"", '{ let mut s: Vec<u8> = vec![]; reverse_in_place(&mut s); s }', "Vec::<u8>::new()"),
        T("single", "s = b\"x\"", '{ let mut s = b"x".to_vec(); reverse_in_place(&mut s); s }', 'b"x".to_vec()'),
    ],
    hints=[("rust", "`s.swap(i, j)` exchanges two elements of a mutable slice.")],
    notes=("Bytes are safe to reverse. Reversing a UTF-8 `String` byte by byte would break multi-byte characters, which is why `str` has no in-place reverse.", "O(n)", "O(1)"),
    follow_up="How would you reverse the characters of a UTF-8 string, and what about grapheme clusters?",
    related=["S2", "S3"],
))

P.append(dict(
    slug="merge-sorted-array", title="Merge sorted array", level="easy", stage="two-ends", tags=["two pointers", "from the back"],
    teaches=["Fill from the back so nothing is overwritten before it's read."],
    statement="""
        `nums1` holds `m` sorted values followed by `nums2.len()` zeros. Merge the sorted `nums2` into
        `nums1` so that all of `nums1` is sorted, in place.
    """,
    examples=[("nums1 = [1, 2, 3, 0, 0, 0], m = 3, nums2 = [2, 5, 6]", "[1, 2, 2, 3, 5, 6]")],
    starter="""
        pub fn merge(nums1: &mut [i32], m: usize, nums2: &[i32]) {
            todo!()
        }
    """,
    solution="""
        pub fn merge(nums1: &mut [i32], m: usize, nums2: &[i32]) {
            let (mut i, mut j, mut w) = (m, nums2.len(), m + nums2.len());
            while j > 0 {
                w -= 1;
                if i > 0 && nums1[i - 1] > nums2[j - 1] {
                    nums1[w] = nums1[i - 1];
                    i -= 1;
                } else {
                    nums1[w] = nums2[j - 1];
                    j -= 1;
                }
            }
        }
    """,
    visible=[
        T("classic", "nums1 = [1, 2, 3, 0, 0, 0], m = 3, nums2 = [2, 5, 6]", "{ let mut a = [1, 2, 3, 0, 0, 0]; merge(&mut a, 3, &[2, 5, 6]); a }", "[1, 2, 2, 3, 5, 6]"),
        T("nums2_empty", "nums1 = [1], m = 1, nums2 = []", "{ let mut a = [1]; merge(&mut a, 1, &[]); a }", "[1]"),
    ],
    hidden=[
        T("nums1_empty", "nums1 = [0], m = 0, nums2 = [1]", "{ let mut a = [0]; merge(&mut a, 0, &[1]); a }", "[1]"),
        T("all_smaller", "nums1 = [4, 5, 0, 0], m = 2, nums2 = [1, 2]", "{ let mut a = [4, 5, 0, 0]; merge(&mut a, 2, &[1, 2]); a }", "[1, 2, 4, 5]"),
    ],
    hints=[("approach", "The empty space is at the end of nums1. Which end should you write from?")],
    notes=("Writing from the back means every slot written is either free or already consumed. Once nums2 is empty, the rest of nums1 is already in place.", "O(m + n)", "O(1)"),
    follow_up="How would you merge k sorted arrays?",
    related=["D7"],
))

P.append(dict(
    slug="move-zeroes", title="Move zeroes", level="easy", stage="two-ends", tags=["two pointers", "stable"],
    teaches=["A write index that trails a read index.", "Stable in-place compaction."],
    statement="Move every 0 in `nums` to the end, keeping the order of the other values, in place.",
    examples=[("nums = [0, 1, 0, 3, 12]", "[1, 3, 12, 0, 0]")],
    starter="""
        pub fn move_zeroes(nums: &mut [i32]) {
            todo!()
        }
    """,
    solution="""
        pub fn move_zeroes(nums: &mut [i32]) {
            let mut write = 0;
            for read in 0..nums.len() {
                if nums[read] != 0 {
                    nums.swap(write, read);
                    write += 1;
                }
            }
        }
    """,
    visible=[
        T("mixed", "nums = [0, 1, 0, 3, 12]", "{ let mut v = [0, 1, 0, 3, 12]; move_zeroes(&mut v); v }", "[1, 3, 12, 0, 0]"),
        T("single_zero", "nums = [0]", "{ let mut v = [0]; move_zeroes(&mut v); v }", "[0]"),
    ],
    hidden=[
        T("no_zeroes", "nums = [1, 2, 3]", "{ let mut v = [1, 2, 3]; move_zeroes(&mut v); v }", "[1, 2, 3]"),
        T("negatives", "nums = [-1, 0, 0, -2]", "{ let mut v = [-1, 0, 0, -2]; move_zeroes(&mut v); v }", "[-1, -2, 0, 0]"),
    ],
    hints=[("approach", "Keep a write position for the next non-zero value.")],
    notes=("Swapping instead of overwriting leaves the zeros at the end without a second pass.", "O(n)", "O(1)"),
    follow_up="How does this relate to `Vec::retain`?",
    related=["S3"],
))

P.append(dict(
    slug="fix-usize-underflow", title="Fix: usize underflow on an empty slice", mode="fix", level="easy", stage="two-ends", tags=["usize", "checked_sub"],
    teaches=["`len() - 1` underflows on an empty slice: a panic in debug, a huge index in release.", "`checked_sub` or an exclusive bound avoids it."],
    statement="`is_mirror` should return `true` for an empty slice. It panics instead.",
    starter="""
        /// True if `v` reads the same forwards and backwards.
        pub fn is_mirror(v: &[i32]) -> bool {
            let (mut l, mut r) = (0, v.len() - 1);
            while l < r {
                if v[l] != v[r] {
                    return false;
                }
                l += 1;
                r -= 1;
            }
            true
        }
    """,
    solution="""
        /// True if `v` reads the same forwards and backwards.
        pub fn is_mirror(v: &[i32]) -> bool {
            let Some(last) = v.len().checked_sub(1) else { return true };
            let (mut l, mut r) = (0, last);
            while l < r {
                if v[l] != v[r] {
                    return false;
                }
                l += 1;
                r -= 1;
            }
            true
        }
    """,
    rules=dict(lines=2),
    visible=[
        T("odd", "v = [1, 2, 1]", "is_mirror(&[1, 2, 1])", "true"),
        T("not_mirror", "v = [1, 2]", "is_mirror(&[1, 2])", "false"),
        T("empty", "v = []", "is_mirror(&[])", "true"),
    ],
    hidden=[
        T("single", "v = [5]", "is_mirror(&[5])", "true"),
        T("even", "v = [3, 4, 4, 3]", "is_mirror(&[3, 4, 4, 3])", "true"),
    ],
    hints=[("rust", "What is `0usize - 1`?"), ("rust", "`checked_sub(1)` returns `None` instead of underflowing.")],
    notes=("`let … else` handles the empty case before the loop. An exclusive right bound (`v[r - 1]`) is the other common fix.", "O(n)", "O(1)"),
    follow_up="Why does Rust panic on overflow in debug but wrap in release?",
    related=["S1", "Y1"],
))

P.append(dict(
    slug="two-sum-sorted", title="Two sum II (sorted input)", level="medium", stage="pointers", tags=["two pointers"],
    teaches=["On sorted input, move the pointer that brings the sum toward the target.", "O(1) space versus the hash-map version."],
    statement="`nums` is sorted ascending. Return indices `(i, j)`, `i < j`, of two values summing to `target`, or `None`.",
    examples=[("nums = [2, 7, 11, 15], target = 9", "Some((0, 1))")],
    starter="""
        pub fn two_sum_sorted(nums: &[i32], target: i32) -> Option<(usize, usize)> {
            todo!()
        }
    """,
    solution="""
        use std::cmp::Ordering;

        pub fn two_sum_sorted(nums: &[i32], target: i32) -> Option<(usize, usize)> {
            let (mut l, mut r) = (0, nums.len().checked_sub(1)?);
            while l < r {
                match (nums[l] as i64 + nums[r] as i64).cmp(&(target as i64)) {
                    Ordering::Equal => return Some((l, r)),
                    Ordering::Less => l += 1,
                    Ordering::Greater => r -= 1,
                }
            }
            None
        }
    """,
    visible=[
        T("first_two", "nums = [2, 7, 11, 15], target = 9", "two_sum_sorted(&[2, 7, 11, 15], 9)", "Some((0, 1))"),
        T("outer", "nums = [2, 3, 4], target = 6", "two_sum_sorted(&[2, 3, 4], 6)", "Some((0, 2))"),
        T("none", "nums = [1, 2], target = 5", "two_sum_sorted(&[1, 2], 5)", "None"),
    ],
    hidden=[
        T("empty", "nums = [], target = 0", "two_sum_sorted(&[], 0)", "None"),
        T("extremes", "nums = [i32::MIN, 0, i32::MAX], target = -1", "two_sum_sorted(&[i32::MIN, 0, i32::MAX], -1)", "Some((0, 2))"),
    ],
    hints=[("approach", "Start at both ends. If the sum is too small, which pointer should move?"),
           ("edge case", "Two i32s can overflow when added; widen first.")],
    notes=("Each step discards one candidate that can't be part of the answer. `match` on `Ordering` reads better than nested ifs.", "O(n)", "O(1)"),
    follow_up="Prove that moving the smaller side never skips the answer.",
    related=["D1"],
))

P.append(dict(
    slug="three-sum", title="3Sum", level="medium", stage="pointers", tags=["two pointers", "dedup", "Blind 75"],
    teaches=["Sort, fix one value, two-pointer the rest.", "Skip equal neighbours to avoid duplicate triplets."],
    statement="""
        Return every unique triplet of values from `nums` that sums to 0. Each triplet is sorted
        ascending and the list is in lexicographic order.
    """,
    examples=[("nums = [-1, 0, 1, 2, -1, -4]", "[[-1, -1, 2], [-1, 0, 1]]")],
    starter="""
        pub fn three_sum(nums: &[i32]) -> Vec<[i32; 3]> {
            todo!()
        }
    """,
    solution="""
        pub fn three_sum(nums: &[i32]) -> Vec<[i32; 3]> {
            let mut v = nums.to_vec();
            v.sort_unstable();
            let mut out = Vec::new();
            for i in 0..v.len() {
                if i > 0 && v[i] == v[i - 1] {
                    continue;
                }
                let (mut l, mut r) = (i + 1, v.len());
                while l + 1 < r {
                    let sum = v[i] as i64 + v[l] as i64 + v[r - 1] as i64;
                    if sum < 0 {
                        l += 1;
                    } else if sum > 0 {
                        r -= 1;
                    } else {
                        out.push([v[i], v[l], v[r - 1]]);
                        l += 1;
                        while l + 1 < r && v[l] == v[l - 1] {
                            l += 1;
                        }
                        r -= 1;
                    }
                }
            }
            out
        }
    """,
    visible=[
        T("classic", "nums = [-1, 0, 1, 2, -1, -4]", "three_sum(&[-1, 0, 1, 2, -1, -4])", "vec![[-1, -1, 2], [-1, 0, 1]]"),
        T("none", "nums = [0, 1, 1]", "three_sum(&[0, 1, 1])", "Vec::<[i32; 3]>::new()"),
        T("zeros", "nums = [0, 0, 0, 0]", "three_sum(&[0, 0, 0, 0])", "vec![[0, 0, 0]]"),
    ],
    hidden=[
        T("many_dups", "nums = [-2, 0, 0, 2, 2, -2]", "three_sum(&[-2, 0, 0, 2, 2, -2])", "vec![[-2, 0, 2]]"),
        T("wide", "nums = [-4, -1, -1, 0, 1, 2, 3]", "three_sum(&[-4, -1, -1, 0, 1, 2, 3])", "vec![[-4, 1, 3], [-1, -1, 2], [-1, 0, 1]]"),
    ],
    hints=[("approach", "Sort. For each first value, find pairs in the rest with two pointers."),
           ("edge case", "Skip a first value equal to the previous one, and skip repeated left values after a match.")],
    notes=("Sorting makes duplicates adjacent, so skipping neighbours is enough to dedupe. `[i32; 3]` is `Copy` and compares element-wise.", "O(n²)", "O(n) for the sorted copy"),
    follow_up="How does this generalise to k-sum?",
    related=["D1"],
))

P.append(dict(
    slug="container-with-most-water", title="Container with most water", level="medium", stage="pointers", tags=["two pointers", "Blind 75"],
    teaches=["Move the shorter wall; the taller one can't do better with less width."],
    statement="Pick two lines from `heights` that, with the x-axis, hold the most water. Return that area.",
    examples=[("heights = [1, 8, 6, 2, 5, 4, 8, 3, 7]", "49")],
    starter="""
        pub fn max_area(heights: &[u32]) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn max_area(heights: &[u32]) -> u64 {
            let (mut l, mut r) = (0, heights.len());
            let mut best = 0u64;
            while l + 1 < r {
                let (a, b) = (heights[l], heights[r - 1]);
                best = best.max(a.min(b) as u64 * (r - 1 - l) as u64);
                if a < b {
                    l += 1;
                } else {
                    r -= 1;
                }
            }
            best
        }
    """,
    visible=[
        T("classic", "heights = [1, 8, 6, 2, 5, 4, 8, 3, 7]", "max_area(&[1, 8, 6, 2, 5, 4, 8, 3, 7])", "49"),
        T("two", "heights = [1, 1]", "max_area(&[1, 1])", "1"),
    ],
    hidden=[
        T("one_line", "heights = [5]", "max_area(&[5])", "0"),
        T("large", "heights = [u32::MAX, u32::MAX]", "max_area(&[u32::MAX, u32::MAX])", "u32::MAX as u64"),
    ],
    hints=[("approach", "Start with the widest container. Which wall is limiting the height?")],
    notes=("Moving the taller wall can only shrink width without raising the minimum height, so it never helps.", "O(n)", "O(1)"),
    follow_up="Why is it safe to discard the shorter wall for good?",
    related=["D1"],
))

P.append(dict(
    slug="three-sum-closest", title="3Sum closest", level="medium", stage="pointers", tags=["two pointers"],
    teaches=["Same shape as 3Sum, tracking the best distance instead of exact matches.", "`abs_diff` for distances without overflow."],
    statement="Return the sum of the three values in `nums` whose sum is closest to `target`. `nums` has at least 3 values and exactly one closest sum.",
    examples=[("nums = [-1, 2, 1, -4], target = 1", "2")],
    starter="""
        pub fn three_sum_closest(nums: &[i32], target: i32) -> i32 {
            todo!()
        }
    """,
    solution="""
        pub fn three_sum_closest(nums: &[i32], target: i32) -> i32 {
            let mut v = nums.to_vec();
            v.sort_unstable();
            let mut best = v[0] + v[1] + v[2];
            for i in 0..v.len() - 2 {
                let (mut l, mut r) = (i + 1, v.len() - 1);
                while l < r {
                    let sum = v[i] + v[l] + v[r];
                    if sum.abs_diff(target) < best.abs_diff(target) {
                        best = sum;
                    }
                    if sum < target {
                        l += 1;
                    } else if sum > target {
                        r -= 1;
                    } else {
                        return sum;
                    }
                }
            }
            best
        }
    """,
    visible=[
        T("classic", "nums = [-1, 2, 1, -4], target = 1", "three_sum_closest(&[-1, 2, 1, -4], 1)", "2"),
        T("exact", "nums = [0, 0, 0], target = 1", "three_sum_closest(&[0, 0, 0], 1)", "0"),
    ],
    hidden=[
        T("hit", "nums = [1, 1, 1, 0], target = 3", "three_sum_closest(&[1, 1, 1, 0], 3)", "3"),
        T("negative_target", "nums = [4, 0, 5, -5, 3, 3, 0, -4, -5], target = -2", "three_sum_closest(&[4, 0, 5, -5, 3, 3, 0, -4, -5], -2)", "-2"),
    ],
    hints=[("approach", "Sort, fix one value, move two pointers toward the target."), ("rust", "`i32::abs_diff` returns a `u32` distance.")],
    notes=("An exact hit can return early. `abs_diff` avoids the overflow `(a - b).abs()` can hit.", "O(n²)", "O(n)"),
    follow_up="How would you return the triplet itself, not just its sum?",
    related=["D1"],
))

P.append(dict(
    slug="best-time-to-buy-and-sell-stock", title="Best time to buy and sell stock", level="medium", stage="windows", tags=["running min", "Blind 75"],
    teaches=["Track the lowest price so far; each day is a potential sell."],
    statement="Return the most profit from buying on one day and selling on a later day, or 0 if no trade makes money.",
    examples=[("prices = [7, 1, 5, 3, 6, 4]", "5")],
    starter="""
        pub fn max_profit(prices: &[u32]) -> u32 {
            todo!()
        }
    """,
    solution="""
        pub fn max_profit(prices: &[u32]) -> u32 {
            let mut lowest = u32::MAX;
            let mut best = 0;
            for &p in prices {
                lowest = lowest.min(p);
                best = best.max(p - lowest);
            }
            best
        }
    """,
    visible=[
        T("classic", "prices = [7, 1, 5, 3, 6, 4]", "max_profit(&[7, 1, 5, 3, 6, 4])", "5"),
        T("falling", "prices = [7, 6, 4, 3, 1]", "max_profit(&[7, 6, 4, 3, 1])", "0"),
    ],
    hidden=[
        T("empty", "prices = []", "max_profit(&[])", "0"),
        T("late_low", "prices = [2, 4, 1]", "max_profit(&[2, 4, 1])", "2"),
    ],
    hints=[("approach", "For each day, the best sale ends today and buys at the cheapest earlier day.")],
    notes=("`lowest` is updated before the subtraction, so `p - lowest` is never negative.", "O(n)", "O(1)"),
    follow_up="What if you may buy and sell many times, or with a cooldown?",
    related=["D12"],
))

P.append(dict(
    slug="longest-substring-without-repeating", title="Longest substring without repeating characters", level="medium", stage="windows", tags=["sliding window", "Blind 75"],
    teaches=["A window that jumps its left edge past the last repeat.", "`[Option<usize>; 256]` as a last-seen table for bytes."],
    statement="Return the length of the longest substring of `s` with no repeated byte. `s` is ASCII.",
    examples=[("s = \"abcabcbb\"", "3")],
    starter="""
        pub fn length_of_longest_substring(s: &str) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn length_of_longest_substring(s: &str) -> usize {
            let mut last: [Option<usize>; 256] = [None; 256];
            let (mut start, mut best) = (0, 0);
            for (i, b) in s.bytes().enumerate() {
                // Only a repeat inside the current window moves the start.
                if let Some(prev) = last[b as usize].filter(|&p| p >= start) {
                    start = prev + 1;
                }
                last[b as usize] = Some(i);
                best = best.max(i + 1 - start);
            }
            best
        }
    """,
    visible=[
        T("abc", "s = \"abcabcbb\"", 'length_of_longest_substring("abcabcbb")', "3"),
        T("all_same", "s = \"bbbbb\"", 'length_of_longest_substring("bbbbb")', "1"),
        T("pwwkew", "s = \"pwwkew\"", 'length_of_longest_substring("pwwkew")', "3"),
    ],
    hidden=[
        T("empty", "s = \"\"", 'length_of_longest_substring("")', "0"),
        T("stale_repeat", "s = \"abba\"", 'length_of_longest_substring("abba")', "2"),
        T("spaces", "s = \" a b\"", 'length_of_longest_substring(" a b")', "3"),
    ],
    hints=[("approach", "Keep a window with no repeats. When a byte repeats inside it, move the start past the earlier copy."),
           ("edge case", "In \"abba\", the second a's earlier copy is already outside the window.")],
    notes=("Only jumping `start` forward (the `prev >= start` check) keeps the window valid for inputs like \"abba\".", "O(n)", "O(1)"),
    follow_up="How would you return the substring itself as a `&str`?",
    related=["S2"],
))

P.append(dict(
    slug="longest-repeating-character-replacement", title="Longest repeating character replacement", level="medium", stage="windows", tags=["sliding window", "Blind 75"],
    teaches=["A window is valid when `len − most_common ≤ k`.", "The max count never needs to decrease."],
    statement="`s` is uppercase ASCII. You may replace up to `k` characters. Return the length of the longest substring of one repeated letter you can make.",
    examples=[("s = \"AABABBA\", k = 1", "4")],
    starter="""
        pub fn character_replacement(s: &str, k: usize) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn character_replacement(s: &str, k: usize) -> usize {
            let b = s.as_bytes();
            let mut counts = [0usize; 26];
            let (mut start, mut most, mut best) = (0, 0, 0);
            for end in 0..b.len() {
                let c = (b[end] - b'A') as usize;
                counts[c] += 1;
                most = most.max(counts[c]);
                while end + 1 - start - most > k {
                    counts[(b[start] - b'A') as usize] -= 1;
                    start += 1;
                }
                best = best.max(end + 1 - start);
            }
            best
        }
    """,
    visible=[
        T("abab", "s = \"ABAB\", k = 2", 'character_replacement("ABAB", 2)', "4"),
        T("aababba", "s = \"AABABBA\", k = 1", 'character_replacement("AABABBA", 1)', "4"),
    ],
    hidden=[
        T("zero_k", "s = \"ABBB\", k = 0", 'character_replacement("ABBB", 0)', "3"),
        T("empty", "s = \"\", k = 3", 'character_replacement("", 3)', "0"),
    ],
    hints=[("approach", "A window can be made uniform if its length minus its most frequent letter's count is at most k."),
           ("approach", "You don't need to shrink `most` when the window shrinks; a stale max never gives a wrong larger answer.")],
    notes=("The answer only grows when `most` grows, so keeping the historical max is enough.", "O(n)", "O(1)"),
    follow_up="Why is it safe not to recompute `most` when the window shrinks?",
    related=["S2"],
))

P.append(dict(
    slug="permutation-in-string", title="Permutation in string", level="medium", stage="windows", tags=["fixed window", "[u8; 26]"],
    teaches=["A fixed-size window with two count arrays, compared in O(26)."],
    statement="Return `true` if some permutation of `pattern` appears as a substring of `s`. Both are lowercase ASCII.",
    examples=[("pattern = \"ab\", s = \"eidbaooo\"", "true")],
    starter="""
        pub fn check_inclusion(pattern: &str, s: &str) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn check_inclusion(pattern: &str, s: &str) -> bool {
            let (p, s) = (pattern.as_bytes(), s.as_bytes());
            if p.len() > s.len() {
                return false;
            }
            let idx = |b: u8| (b - b'a') as usize;
            let (mut want, mut have) = ([0u16; 26], [0u16; 26]);
            for &b in p {
                want[idx(b)] += 1;
            }
            for (i, &b) in s.iter().enumerate() {
                have[idx(b)] += 1;
                if i >= p.len() {
                    have[idx(s[i - p.len()])] -= 1;
                }
                if have == want {
                    return true;
                }
            }
            false
        }
    """,
    visible=[
        T("found", "pattern = \"ab\", s = \"eidbaooo\"", 'check_inclusion("ab", "eidbaooo")', "true"),
        T("not_found", "pattern = \"ab\", s = \"eidboaoo\"", 'check_inclusion("ab", "eidboaoo")', "false"),
    ],
    hidden=[
        T("longer_pattern", "pattern = \"abc\", s = \"ab\"", 'check_inclusion("abc", "ab")', "false"),
        T("whole_string", "pattern = \"adc\", s = \"dcda\"", 'check_inclusion("adc", "dcda")', "true"),
    ],
    hints=[("approach", "Slide a window the size of the pattern and compare letter counts."), ("rust", "Arrays implement `==` element-wise.")],
    notes=("Comparing two `[u16; 26]` arrays is 26 comparisons, so each step is O(1).", "O(n)", "O(1)"),
    follow_up="How would you avoid comparing all 26 counts on every step?",
    related=["D1"],
))

P.append(dict(
    slug="find-all-anagrams", title="Find all anagrams in a string", level="medium", stage="windows", tags=["fixed window"],
    teaches=["The same window as permutation-in-string, collecting every start index."],
    statement="Return every start index in `s` where an anagram of `p` begins, ascending. Both are lowercase ASCII.",
    examples=[("s = \"cbaebabacd\", p = \"abc\"", "[0, 6]")],
    starter="""
        pub fn find_anagrams(s: &str, p: &str) -> Vec<usize> {
            todo!()
        }
    """,
    solution="""
        pub fn find_anagrams(s: &str, p: &str) -> Vec<usize> {
            let (s, p) = (s.as_bytes(), p.as_bytes());
            let mut out = Vec::new();
            if p.is_empty() || p.len() > s.len() {
                return out;
            }
            let idx = |b: u8| (b - b'a') as usize;
            let (mut want, mut have) = ([0u16; 26], [0u16; 26]);
            for &b in p {
                want[idx(b)] += 1;
            }
            for (i, &b) in s.iter().enumerate() {
                have[idx(b)] += 1;
                if i >= p.len() {
                    have[idx(s[i - p.len()])] -= 1;
                }
                if i + 1 >= p.len() && have == want {
                    out.push(i + 1 - p.len());
                }
            }
            out
        }
    """,
    visible=[
        T("two", "s = \"cbaebabacd\", p = \"abc\"", 'find_anagrams("cbaebabacd", "abc")', "vec![0, 6]"),
        T("overlapping", "s = \"abab\", p = \"ab\"", 'find_anagrams("abab", "ab")', "vec![0, 1, 2]"),
    ],
    hidden=[
        T("none", "s = \"aaaa\", p = \"b\"", 'find_anagrams("aaaa", "b")', "Vec::<usize>::new()"),
        T("longer_pattern", "s = \"a\", p = \"ab\"", 'find_anagrams("a", "ab")', "Vec::<usize>::new()"),
    ],
    hints=[("approach", "Keep counts for a window of `p.len()` letters as it slides.")],
    notes=("Identical to the permutation check, except it records each match instead of returning.", "O(n)", "O(1) beyond the output"),
    follow_up="Could you return an iterator of indices instead of a Vec?",
    related=["S6"],
))

P.append(dict(
    slug="minimum-window-substring", title="Minimum window substring", level="hard", stage="hard-windows", tags=["sliding window", "lifetimes", "Blind 75"],
    teaches=["Grow the window until it covers `t`, then shrink it while it still does.", "Return a `&'a str` borrowed from the input instead of allocating."],
    statement="""
        Return the shortest substring of `s` that contains every character of `t`, counting
        duplicates, or `""` if there isn't one. Both are ASCII. If several are shortest, return the
        leftmost.
    """,
    examples=[("s = \"ADOBECODEBANC\", t = \"ABC\"", "\"BANC\"")],
    starter="""
        pub fn min_window<'a>(s: &'a str, t: &str) -> &'a str {
            todo!()
        }
    """,
    solution="""
        pub fn min_window<'a>(s: &'a str, t: &str) -> &'a str {
            let b = s.as_bytes();
            let mut need = [0i32; 128];
            for c in t.bytes() {
                need[c as usize] += 1;
            }
            let mut missing = t.len();
            let mut best: Option<(usize, usize)> = None;
            let mut start = 0;
            for end in 0..b.len() {
                let c = b[end] as usize;
                if need[c] > 0 {
                    missing -= 1;
                }
                need[c] -= 1;
                while missing == 0 {
                    if best.is_none_or(|(l, r)| end + 1 - start < r - l) {
                        best = Some((start, end + 1));
                    }
                    let d = b[start] as usize;
                    need[d] += 1;
                    if need[d] > 0 {
                        missing += 1;
                    }
                    start += 1;
                }
            }
            best.map_or("", |(l, r)| &s[l..r])
        }
    """,
    visible=[
        T("classic", "s = \"ADOBECODEBANC\", t = \"ABC\"", 'min_window("ADOBECODEBANC", "ABC")', '"BANC"'),
        T("single", "s = \"a\", t = \"a\"", 'min_window("a", "a")', '"a"'),
        T("impossible", "s = \"a\", t = \"aa\"", 'min_window("a", "aa")', '""'),
    ],
    hidden=[
        T("duplicates_needed", "s = \"aaflslflsldkalskaaa\", t = \"aaa\"", 'min_window("aaflslflsldkalskaaa", "aaa")', '"aaa"'),
        T("leftmost_tie", "s = \"abcab\", t = \"ab\"", 'min_window("abcab", "ab")', '"ab"'),
    ],
    hints=[("approach", "Expand the right edge until everything in t is covered, then shrink the left edge while it stays covered."),
           ("approach", "Track how many required characters are still missing instead of comparing whole count arrays."),
           ("rust", "Return `&s[l..r]`: the lifetime `'a` ties the result to `s`, not to `t`.")],
    notes=("`need` goes negative for surplus characters, so `missing` only changes when a required character enters or leaves. Returning a slice of `s` costs no allocation.", "O(|s| + |t|)", "O(1)"),
    follow_up="Why does the signature need `'a` on `s` but not on `t`?",
    related=["L3", "S2"],
))

P.append(dict(
    slug="trapping-rain-water", title="Trapping rain water", level="hard", stage="hard-windows", tags=["two pointers"],
    teaches=["Water at a position is bounded by the lower of the tallest walls on each side.", "Two pointers carry both running maxima."],
    statement="`heights` is an elevation map with bars of width 1. Return how much water it traps after rain.",
    examples=[("heights = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]", "6")],
    starter="""
        pub fn trap(heights: &[u32]) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn trap(heights: &[u32]) -> u64 {
            let (mut l, mut r) = (0, heights.len());
            let (mut left_max, mut right_max) = (0u32, 0u32);
            let mut water = 0u64;
            while l < r {
                if heights[l] < heights[r - 1] {
                    left_max = left_max.max(heights[l]);
                    water += (left_max - heights[l]) as u64;
                    l += 1;
                } else {
                    right_max = right_max.max(heights[r - 1]);
                    water += (right_max - heights[r - 1]) as u64;
                    r -= 1;
                }
            }
            water
        }
    """,
    visible=[
        T("classic", "heights = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]", "trap(&[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])", "6"),
        T("bowl", "heights = [4, 2, 0, 3, 2, 5]", "trap(&[4, 2, 0, 3, 2, 5])", "9"),
    ],
    hidden=[
        T("empty", "heights = []", "trap(&[])", "0"),
        T("monotonic", "heights = [1, 2, 3, 4]", "trap(&[1, 2, 3, 4])", "0"),
        T("tall_walls", "heights = [u32::MAX, 0, u32::MAX]", "trap(&[u32::MAX, 0, u32::MAX])", "u32::MAX as u64"),
    ],
    hints=[("approach", "Water above bar i = min(tallest to the left, tallest to the right) − height[i]."),
           ("approach", "Process whichever side has the lower wall: its bound is already known.")],
    notes=("When the left bar is lower, the right side is guaranteed to have a wall at least that tall, so `left_max` alone bounds the water.", "O(n)", "O(1)"),
    follow_up="How would you solve it with a monotonic stack, and what does that version compute differently?",
    related=["D3"],
))

P.append(dict(
    slug="sliding-window-maximum", title="Sliding window maximum", level="hard", stage="hard-windows", tags=["VecDeque", "monotonic queue"],
    teaches=["A monotonic deque of indices: the front is always the window's max.", "`VecDeque::pop_back` while the new value dominates."],
    statement="Return the maximum of each window of `k` consecutive values in `nums`, left to right. `1 ≤ k ≤ nums.len()`.",
    examples=[("nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 3", "[3, 3, 5, 5, 6, 7]")],
    starter="""
        pub fn max_sliding_window(nums: &[i32], k: usize) -> Vec<i32> {
            todo!()
        }
    """,
    solution="""
        use std::collections::VecDeque;

        pub fn max_sliding_window(nums: &[i32], k: usize) -> Vec<i32> {
            let mut dq: VecDeque<usize> = VecDeque::new();
            let mut out = Vec::with_capacity(nums.len() + 1 - k);
            for i in 0..nums.len() {
                if dq.front().is_some_and(|&f| f + k <= i) {
                    dq.pop_front();
                }
                while dq.back().is_some_and(|&b| nums[b] <= nums[i]) {
                    dq.pop_back();
                }
                dq.push_back(i);
                if i + 1 >= k {
                    out.push(nums[dq[0]]);
                }
            }
            out
        }
    """,
    visible=[
        T("classic", "nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 3", "max_sliding_window(&[1, 3, -1, -3, 5, 3, 6, 7], 3)", "vec![3, 3, 5, 5, 6, 7]"),
        T("k_one", "nums = [4, 2], k = 1", "max_sliding_window(&[4, 2], 1)", "vec![4, 2]"),
    ],
    hidden=[
        T("whole", "nums = [9, 10, 9, -7], k = 4", "max_sliding_window(&[9, 10, 9, -7], 4)", "vec![10]"),
        T("descending", "nums = [5, 4, 3, 2, 1], k = 2", "max_sliding_window(&[5, 4, 3, 2, 1], 2)", "vec![5, 4, 3, 2]"),
        T("large", "nums = 0..100000, k = 1000", "max_sliding_window(&(0..100_000).collect::<Vec<_>>(), 1000).len()", "99001"),
    ],
    hints=[("approach", "A value that's smaller than a later value in the window can never be the max again."),
           ("rust", "Keep indices in a `VecDeque` in decreasing value order; drop the front when it leaves the window.")],
    notes=("Each index is pushed and popped at most once, so the whole pass is linear.", "O(n)", "O(k)"),
    follow_up="How would you support a stream where k changes over time?",
    related=["S5", "D3"],
))

P.append(dict(
    slug="four-sum", title="4Sum", level="hard", stage="hard-windows", tags=["two pointers", "i64"],
    teaches=["Two fixed loops plus two pointers.", "Widen to i64: four i32s can overflow."],
    statement="""
        Return every unique quadruplet of values from `nums` summing to `target`. Each quadruplet is
        sorted ascending and the list is in lexicographic order.
    """,
    examples=[("nums = [1, 0, -1, 0, -2, 2], target = 0", "[[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]")],
    starter="""
        pub fn four_sum(nums: &[i32], target: i64) -> Vec<[i32; 4]> {
            todo!()
        }
    """,
    solution="""
        pub fn four_sum(nums: &[i32], target: i64) -> Vec<[i32; 4]> {
            let mut v = nums.to_vec();
            v.sort_unstable();
            let n = v.len();
            let mut out = Vec::new();
            for a in 0..n {
                if a > 0 && v[a] == v[a - 1] {
                    continue;
                }
                for b in a + 1..n {
                    if b > a + 1 && v[b] == v[b - 1] {
                        continue;
                    }
                    let (mut l, mut r) = (b + 1, n);
                    while l + 1 < r {
                        let sum = v[a] as i64 + v[b] as i64 + v[l] as i64 + v[r - 1] as i64;
                        if sum < target {
                            l += 1;
                        } else if sum > target {
                            r -= 1;
                        } else {
                            out.push([v[a], v[b], v[l], v[r - 1]]);
                            l += 1;
                            while l + 1 < r && v[l] == v[l - 1] {
                                l += 1;
                            }
                            r -= 1;
                        }
                    }
                }
            }
            out
        }
    """,
    visible=[
        T("classic", "nums = [1, 0, -1, 0, -2, 2], target = 0", "four_sum(&[1, 0, -1, 0, -2, 2], 0)", "vec![[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]"),
        T("all_twos", "nums = [2, 2, 2, 2, 2], target = 8", "four_sum(&[2, 2, 2, 2, 2], 8)", "vec![[2, 2, 2, 2]]"),
    ],
    hidden=[
        T("overflow", "nums = [1e9 × 4], target = 4e9", "four_sum(&[1_000_000_000; 4], 4_000_000_000)", "vec![[1_000_000_000; 4]]"),
        T("too_short", "nums = [1, 2, 3], target = 6", "four_sum(&[1, 2, 3], 6)", "Vec::<[i32; 4]>::new()"),
    ],
    hints=[("approach", "Fix two values with loops, then two-pointer the remaining pair."),
           ("edge case", "Four values near 10⁹ overflow i32; sum in i64.")],
    notes=("The dedup rule is the same as 3Sum at each level.", "O(n³)", "O(n)"),
    follow_up="Write k-sum recursively. What's the complexity?",
    related=["D1"],
))

STAGES = [
    ("two-ends", "Two ends", "easy"),
    ("pointers", "Pointers", "medium"),
    ("windows", "Windows", "medium"),
    ("hard-windows", "Hard windows", "hard"),
]

if __name__ == "__main__":
    n = write_track("d2-two-pointers-windows", "D2", "Two pointers & sliding window", "D", "core", 2,
                    "Two indices over a slice, and windows that grow and shrink: O(n) answers to problems that look O(n²).",
                    STAGES, P)
    print("D2", n)
