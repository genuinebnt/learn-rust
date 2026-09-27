from author import T, write_track, tag_companies

P = []

P.append(dict(
    slug="valid-palindrome", title="Valid palindrome", level="easy", stage="two-ends", tags=["two pointers", "bytes", "Blind 75"],
    teaches=["Two indices walking inward over `as_bytes()`.", "`is_ascii_alphanumeric` and `eq_ignore_ascii_case` instead of allocating a cleaned copy."],
    statement="Return `true` if `s` reads the same forwards and backwards after ignoring case and every character that isn't an ASCII letter or digit.",
    examples=[("s = \"A man, a plan, a canal: Panama\"", "true")],
    constraints=["0 ≤ s.len() ≤ 2·10⁵"],
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
        T("single_space", "s = \" \"", 'is_palindrome(" ")', "true"),
        T("empty", "s = \"\"", 'is_palindrome("")', "true"),
        T("case_ignored", "s = \"No lemon, no melon\"", 'is_palindrome("No lemon, no melon")', "true"),
    ],
    hidden=[
        T("digits_matter", "s = \"0P\"", 'is_palindrome("0P")', "false"),
        T("empty", "s = \"\"", 'is_palindrome("")', "true"),
        T("single", "s = \"a\"", 'is_palindrome("a")', "true"),
        T("mixed_case", "s = \"Aa\"", 'is_palindrome("Aa")', "true"),
        T("two_different", "s = \"ab\"", 'is_palindrome("ab")', "false"),
        T("digits", "s = \"12321\"", 'is_palindrome("12321")', "true"),
        T("digit_mismatch", "s = \"1a2\"", 'is_palindrome("1a2")', "false"),
        T("non_ascii_skipped", "s = \"éa\"", 'is_palindrome("éa")', "true"),
        T("non_ascii_between", "s = \"ab😀 ÜBA\"", 'is_palindrome("ab😀 ÜBA")', "true"),
        T("punctuation_both_ends", "s = \".,a,.b\"", 'is_palindrome(".,a,.b")', "false"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(201);
            for _ in 0..400 {
                let n = rng.below(10);
                let s = rng.string(n, "aAbB01 ,.é");
                let kept: Vec<char> = s.chars().filter(|c| c.is_ascii_alphanumeric()).map(|c| c.to_ascii_lowercase()).collect();
                let want = kept.iter().eq(kept.iter().rev());
                check!(format!("s = {s:?}"), is_palindrome(&s), want);
            }
        }

        #[test]
        fn scale_200k() {
            let half: String = (0..100_000).map(|i| if i % 3 == 1 { ',' } else { (b'a' + (i % 26) as u8) as char }).collect();
            let s: String = half.chars().chain(half.chars().rev().map(|c| c.to_ascii_uppercase())).collect();
            let mut t = s.clone();
            t.pop();
            t.push('!');
            check!("s = a 200000-byte palindrome with punctuation, and the same with its last letter changed", (is_palindrome(&s), is_palindrome(&t)), (true, false));
        }
        """,
    ],
    wrong=dict(
        unicode_letters="""
            pub fn is_palindrome(s: &str) -> bool {
                let kept: Vec<char> = s.chars().filter(|c| c.is_alphanumeric()).flat_map(|c| c.to_lowercase()).collect();
                kept.iter().eq(kept.iter().rev())
            }
        """,
        letters_only="""
            pub fn is_palindrome(s: &str) -> bool {
                let b = s.as_bytes();
                let (mut l, mut r) = (0, b.len());
                while l < r {
                    if !b[l].is_ascii_alphabetic() {
                        l += 1;
                    } else if !b[r - 1].is_ascii_alphabetic() {
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
        quadratic_remove_front="""
            pub fn is_palindrome(s: &str) -> bool {
                let mut kept: Vec<u8> = s.bytes().filter(|b| b.is_ascii_alphanumeric()).map(|b| b.to_ascii_lowercase()).collect();
                while kept.len() > 1 {
                    let first = kept[0];
                    for i in 1..kept.len() {
                        kept[i - 1] = kept[i];
                    }
                    kept.pop();
                    if kept.pop() != Some(first) {
                        return false;
                    }
                }
                true
            }
        """,
    ),
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
    constraints=["0 ≤ s.len() ≤ 2·10⁵"],
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
        T("even_four", "s = b\"abcd\"", '{ let mut s = b"abcd".to_vec(); reverse_in_place(&mut s); s }', 'b"dcba".to_vec()'),
        T("hannah", "s = b\"Hannah\"", '{ let mut s = b"Hannah".to_vec(); reverse_in_place(&mut s); s }', 'b"hannaH".to_vec()'),
        T("empty", "s = b\"\"", '{ let mut s: Vec<u8> = vec![]; reverse_in_place(&mut s); s }', "Vec::<u8>::new()"),
        T("single", "s = b\"x\"", '{ let mut s = b"x".to_vec(); reverse_in_place(&mut s); s }', 'b"x".to_vec()'),
    ],
    hidden=[
        T("empty", "s = b\"\"", '{ let mut s: Vec<u8> = vec![]; reverse_in_place(&mut s); s }', "Vec::<u8>::new()"),
        T("single", "s = b\"x\"", '{ let mut s = b"x".to_vec(); reverse_in_place(&mut s); s }', 'b"x".to_vec()'),
        T("odd_three", "s = b\"abc\"", '{ let mut s = b"abc".to_vec(); reverse_in_place(&mut s); s }', 'b"cba".to_vec()'),
        T("palindrome", "s = b\"racecar\"", '{ let mut s = b"racecar".to_vec(); reverse_in_place(&mut s); s }', 'b"racecar".to_vec()'),
        T("all_same", "s = b\"zzzz\"", '{ let mut s = b"zzzz".to_vec(); reverse_in_place(&mut s); s }', 'b"zzzz".to_vec()'),
        T("utf8_bytes", "s = \"é!\".as_bytes() = [0xC3, 0xA9, 0x21]", '{ let mut s = "é!".as_bytes().to_vec(); reverse_in_place(&mut s); s }', "vec![0x21, 0xA9, 0xC3]"),
        T("extreme_bytes", "s = [0, 255, 128]", "{ let mut s = vec![0u8, 255, 128]; reverse_in_place(&mut s); s }", "vec![128u8, 255, 0]"),
        T("five", "s = b\"hello\"", '{ let mut s = b"hello".to_vec(); reverse_in_place(&mut s); s }', 'b"olleh".to_vec()'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(202);
            for _ in 0..300 {
                let n = rng.below(16);
                let s: Vec<u8> = rng.vec(n, 0, 255);
                let want: Vec<u8> = s.iter().rev().copied().collect();
                let mut got = s.clone();
                reverse_in_place(&mut got);
                check!(format!("s = {s:?}"), got, want);
            }
        }

        #[test]
        fn scale_200k() {
            let s: Vec<u8> = (0..200_000u32).map(|i| (i % 251) as u8).collect();
            let want: Vec<u8> = s.iter().rev().copied().collect();
            let mut got = s.clone();
            reverse_in_place(&mut got);
            check!("s = [i % 251 for i in 0..200000]", got == want, true);
        }
        """,
    ],
    wrong=dict(
        swaps_twice="""
            pub fn reverse_in_place(s: &mut [u8]) {
                let n = s.len();
                for i in 0..n {
                    s.swap(i, n - 1 - i);
                }
            }
        """,
        stops_one_early="""
            pub fn reverse_in_place(s: &mut [u8]) {
                let n = s.len();
                if n == 0 {
                    return;
                }
                for i in 0..(n - 1) / 2 {
                    s.swap(i, n - 1 - i);
                }
            }
        """,
        bubble_to_the_end="""
            pub fn reverse_in_place(s: &mut [u8]) {
                // Carry the first byte to the end, then the new first byte to one before it, and so on.
                let n = s.len();
                for done in 0..n {
                    for j in 0..n - 1 - done {
                        s.swap(j, j + 1);
                    }
                }
            }
        """,
    ),
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
    constraints=["0 ≤ m, nums2.len() ≤ 10⁵", "nums1.len() = m + nums2.len()"],
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
        T("nums2_smaller", "nums1 = [4, 5, 0, 0], m = 2, nums2 = [1, 2]", "{ let mut a = [4, 5, 0, 0]; merge(&mut a, 2, &[1, 2]); a }", "[1, 2, 4, 5]"),
        T("nums1_has_no_values", "nums1 = [0], m = 0, nums2 = [1]", "{ let mut a = [0]; merge(&mut a, 0, &[1]); a }", "[1]"),
        T("equal_values", "nums1 = [1, 3, 0, 0], m = 2, nums2 = [1, 3]", "{ let mut a = [1, 3, 0, 0]; merge(&mut a, 2, &[1, 3]); a }", "[1, 1, 3, 3]"),
    ],
    hidden=[
        T("nums1_empty", "nums1 = [0], m = 0, nums2 = [1]", "{ let mut a = [0]; merge(&mut a, 0, &[1]); a }", "[1]"),
        T("all_smaller", "nums1 = [4, 5, 0, 0], m = 2, nums2 = [1, 2]", "{ let mut a = [4, 5, 0, 0]; merge(&mut a, 2, &[1, 2]); a }", "[1, 2, 4, 5]"),
        T("both_empty", "nums1 = [], m = 0, nums2 = []", "{ let mut a: [i32; 0] = []; merge(&mut a, 0, &[]); a }", "[0i32; 0]"),
        T("all_larger", "nums1 = [1, 2, 0, 0], m = 2, nums2 = [3, 4]", "{ let mut a = [1, 2, 0, 0]; merge(&mut a, 2, &[3, 4]); a }", "[1, 2, 3, 4]"),
        T("interleaved", "nums1 = [1, 3, 5, 0, 0, 0], m = 3, nums2 = [2, 4, 6]", "{ let mut a = [1, 3, 5, 0, 0, 0]; merge(&mut a, 3, &[2, 4, 6]); a }", "[1, 2, 3, 4, 5, 6]"),
        T("duplicates", "nums1 = [2, 2, 0, 0], m = 2, nums2 = [2, 2]", "{ let mut a = [2, 2, 0, 0]; merge(&mut a, 2, &[2, 2]); a }", "[2, 2, 2, 2]"),
        T("negatives_and_zeros", "nums1 = [-3, 0, 0, 0], m = 2, nums2 = [-5, 0]", "{ let mut a = [-3, 0, 0, 0]; merge(&mut a, 2, &[-5, 0]); a }", "[-5, -3, 0, 0]"),
        T("extremes", "nums1 = [i32::MIN, i32::MAX, 0, 0], m = 2, nums2 = [i32::MIN, i32::MAX]", "{ let mut a = [i32::MIN, i32::MAX, 0, 0]; merge(&mut a, 2, &[i32::MIN, i32::MAX]); a }", "[i32::MIN, i32::MIN, i32::MAX, i32::MAX]"),
        T("nums1_empty_several", "nums1 = [0, 0, 0], m = 0, nums2 = [-1, 0, 7]", "{ let mut a = [0, 0, 0]; merge(&mut a, 0, &[-1, 0, 7]); a }", "[-1, 0, 7]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(203);
            for _ in 0..300 {
                let m = rng.below(8);
                let n = rng.below(8);
                let mut a: Vec<i32> = rng.vec(m, -9, 9);
                let mut b: Vec<i32> = rng.vec(n, -9, 9);
                a.sort();
                b.sort();
                let mut want = [a.clone(), b.clone()].concat();
                want.sort();
                let mut got = a.clone();
                got.resize(m + n, 0);
                merge(&mut got, m, &b);
                check!(format!("nums1 = {a:?} + {n} zeros, m = {m}, nums2 = {b:?}"), got, want);
            }
        }

        #[test]
        fn scale_100k_each() {
            let n = 100_000;
            let mut a: Vec<i32> = (0..n as i32).map(|i| 1_000_000 + i).collect();
            a.resize(2 * n, 0);
            let b: Vec<i32> = (0..n as i32).collect();
            merge(&mut a, n, &b);
            let want: Vec<i32> = (0..n as i32).chain((0..n as i32).map(|i| 1_000_000 + i)).collect();
            check!("nums1 = 1000000..1100000 + 100000 zeros, m = 100000, nums2 = 0..100000", a == want, true);
        }
        """,
    ],
    wrong=dict(
        forgets_leftover_nums2="""
            pub fn merge(nums1: &mut [i32], m: usize, nums2: &[i32]) {
                let (mut i, mut j, mut w) = (m, nums2.len(), m + nums2.len());
                while i > 0 && j > 0 {
                    w -= 1;
                    if nums1[i - 1] > nums2[j - 1] {
                        nums1[w] = nums1[i - 1];
                        i -= 1;
                    } else {
                        nums1[w] = nums2[j - 1];
                        j -= 1;
                    }
                }
            }
        """,
        merges_from_the_front="""
            pub fn merge(nums1: &mut [i32], m: usize, nums2: &[i32]) {
                let (mut i, mut j) = (0, 0);
                for w in 0..m + nums2.len() {
                    if j >= nums2.len() || (i < m && nums1[i] <= nums2[j]) {
                        nums1[w] = nums1[i];
                        i += 1;
                    } else {
                        nums1[w] = nums2[j];
                        j += 1;
                    }
                }
            }
        """,
        insert_and_shift="""
            pub fn merge(nums1: &mut [i32], m: usize, nums2: &[i32]) {
                let mut len = m;
                for &x in nums2 {
                    let mut pos = 0;
                    while pos < len && nums1[pos] <= x {
                        pos += 1;
                    }
                    let mut k = len;
                    while k > pos {
                        nums1[k] = nums1[k - 1];
                        k -= 1;
                    }
                    nums1[pos] = x;
                    len += 1;
                }
            }
        """,
    ),
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
    constraints=["0 ≤ nums.len() ≤ 2·10⁵"],
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
        T("zero_first", "nums = [0, 1]", "{ let mut v = [0, 1]; move_zeroes(&mut v); v }", "[1, 0]"),
        T("no_zeroes", "nums = [1, 2, 3]", "{ let mut v = [1, 2, 3]; move_zeroes(&mut v); v }", "[1, 2, 3]"),
        T("empty", "nums = []", "{ let mut v: [i32; 0] = []; move_zeroes(&mut v); v }", "[0i32; 0]"),
    ],
    hidden=[
        T("no_zeroes", "nums = [1, 2, 3]", "{ let mut v = [1, 2, 3]; move_zeroes(&mut v); v }", "[1, 2, 3]"),
        T("negatives", "nums = [-1, 0, 0, -2]", "{ let mut v = [-1, 0, 0, -2]; move_zeroes(&mut v); v }", "[-1, -2, 0, 0]"),
        T("empty", "nums = []", "{ let mut v: [i32; 0] = []; move_zeroes(&mut v); v }", "[0i32; 0]"),
        T("all_zeroes", "nums = [0, 0, 0]", "{ let mut v = [0, 0, 0]; move_zeroes(&mut v); v }", "[0, 0, 0]"),
        T("already_at_end", "nums = [4, 5, 0, 0]", "{ let mut v = [4, 5, 0, 0]; move_zeroes(&mut v); v }", "[4, 5, 0, 0]"),
        T("single_value", "nums = [7]", "{ let mut v = [7]; move_zeroes(&mut v); v }", "[7]"),
        T("order_kept", "nums = [0, 3, 0, 1, 0, 2]", "{ let mut v = [0, 3, 0, 1, 0, 2]; move_zeroes(&mut v); v }", "[3, 1, 2, 0, 0, 0]"),
        T("duplicates", "nums = [2, 0, 2, 0, 2]", "{ let mut v = [2, 0, 2, 0, 2]; move_zeroes(&mut v); v }", "[2, 2, 2, 0, 0]"),
        T("extremes", "nums = [0, i32::MIN, 0, i32::MAX]", "{ let mut v = [0, i32::MIN, 0, i32::MAX]; move_zeroes(&mut v); v }", "[i32::MIN, i32::MAX, 0, 0]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(204);
            for _ in 0..300 {
                let n = rng.below(12);
                let nums: Vec<i32> = rng.vec(n, -3, 3);
                let mut want: Vec<i32> = nums.iter().copied().filter(|&x| x != 0).collect();
                want.resize(n, 0);
                let mut got = nums.clone();
                move_zeroes(&mut got);
                check!(format!("nums = {nums:?}"), got, want);
            }
        }

        #[test]
        fn scale_200k() {
            let n = 200_000;
            let mut nums = vec![0; n];
            for i in n / 2..n {
                nums[i] = (i - n / 2 + 1) as i32;
            }
            move_zeroes(&mut nums);
            let mut want: Vec<i32> = (1..=(n / 2) as i32).collect();
            want.resize(n, 0);
            check!("nums = [0; 100000] followed by 1..=100000", nums == want, true);
        }
        """,
    ],
    wrong=dict(
        swap_from_the_back="""
            pub fn move_zeroes(nums: &mut [i32]) {
                let (mut l, mut r) = (0, nums.len());
                while l < r {
                    if nums[l] == 0 {
                        r -= 1;
                        nums.swap(l, r);
                    } else {
                        l += 1;
                    }
                }
            }
        """,
        no_zero_fill="""
            pub fn move_zeroes(nums: &mut [i32]) {
                let mut write = 0;
                for read in 0..nums.len() {
                    if nums[read] != 0 {
                        nums[write] = nums[read];
                        write += 1;
                    }
                }
            }
        """,
        bubble_each_zero="""
            pub fn move_zeroes(nums: &mut [i32]) {
                let n = nums.len();
                let mut end = n;
                let mut i = 0;
                while i < end {
                    if nums[i] == 0 {
                        for j in i..n - 1 {
                            nums.swap(j, j + 1);
                        }
                        end -= 1;
                    } else {
                        i += 1;
                    }
                }
            }
        """,
    ),
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
        T("single", "v = [5]", "is_mirror(&[5])", "true"),
        T("even", "v = [3, 4, 4, 3]", "is_mirror(&[3, 4, 4, 3])", "true"),
    ],
    hidden=[
        T("single", "v = [5]", "is_mirror(&[5])", "true"),
        T("even", "v = [3, 4, 4, 3]", "is_mirror(&[3, 4, 4, 3])", "true"),
        T("two_equal", "v = [7, 7]", "is_mirror(&[7, 7])", "true"),
        T("middle_differs", "v = [1, 2, 3, 1]", "is_mirror(&[1, 2, 3, 1])", "false"),
        T("ends_differ", "v = [1, 5, 5, 2]", "is_mirror(&[1, 5, 5, 2])", "false"),
        T("negatives", "v = [-1, 0, -1]", "is_mirror(&[-1, 0, -1])", "true"),
        T("extremes", "v = [i32::MIN, i32::MAX, i32::MIN]", "is_mirror(&[i32::MIN, i32::MAX, i32::MIN])", "true"),
        T("extremes_swapped", "v = [i32::MIN, i32::MAX]", "is_mirror(&[i32::MIN, i32::MAX])", "false"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(205);
            for _ in 0..300 {
                let n = rng.below(8);
                let mut v: Vec<i32> = rng.vec(n, -2, 2);
                if rng.bool() {
                    for i in 0..n / 2 {
                        v[n - 1 - i] = v[i];
                    }
                }
                let want = v.iter().eq(v.iter().rev());
                check!(format!("v = {v:?}"), is_mirror(&v), want);
            }
        }

        #[test]
        fn scale_200k() {
            let v: Vec<i32> = (0..200_000).map(|i: i32| (i.min(199_999 - i)) % 1000).collect();
            let mut w = v.clone();
            w[100_000] = -1;
            check!("v = a 200000-value mirror, and the same with one middle value changed", (is_mirror(&v), is_mirror(&w)), (true, false));
        }
        """,
    ],
    wrong=dict(
        empty_returns_false="""
            /// True if `v` reads the same forwards and backwards.
            pub fn is_mirror(v: &[i32]) -> bool {
                let Some(last) = v.len().checked_sub(1) else { return false };
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
        saturating_inclusive_loop="""
            /// True if `v` reads the same forwards and backwards.
            pub fn is_mirror(v: &[i32]) -> bool {
                let (mut l, mut r) = (0, v.len().saturating_sub(1));
                while l <= r {
                    if v[l] != v[r] {
                        return false;
                    }
                    l += 1;
                    r -= 1;
                }
                true
            }
        """,
    ),
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
    constraints=["0 ≤ nums.len() ≤ 2·10⁵", "at most one pair sums to target"],
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
        T("negative", "nums = [-1, 0], target = -1", "two_sum_sorted(&[-1, 0], -1)", "Some((0, 1))"),
        T("empty", "nums = [], target = 0", "two_sum_sorted(&[], 0)", "None"),
    ],
    hidden=[
        T("empty", "nums = [], target = 0", "two_sum_sorted(&[], 0)", "None"),
        T("extremes", "nums = [i32::MIN, 0, i32::MAX], target = -1", "two_sum_sorted(&[i32::MIN, 0, i32::MAX], -1)", "Some((0, 2))"),
        T("single", "nums = [5], target = 10", "two_sum_sorted(&[5], 10)", "None"),
        T("no_self_pair", "nums = [3, 4], target = 6", "two_sum_sorted(&[3, 4], 6)", "None"),
        T("equal_values", "nums = [1, 3, 3, 8], target = 6", "two_sum_sorted(&[1, 3, 3, 8], 6)", "Some((1, 2))"),
        T("negatives", "nums = [-8, -5, -3, 1, 7], target = -8", "two_sum_sorted(&[-8, -5, -3, 1, 7], -8)", "Some((1, 2))"),
        T("last_two", "nums = [1, 2, 3, 4, 5], target = 9", "two_sum_sorted(&[1, 2, 3, 4, 5], 9)", "Some((3, 4))"),
        T("sum_past_i32_max", "nums = [1, i32::MAX], target = i32::MIN", "two_sum_sorted(&[1, i32::MAX], i32::MIN)", "None"),
        T("sum_below_i32_min", "nums = [i32::MIN, -1, 5], target = 4", "two_sum_sorted(&[i32::MIN, -1, 5], 4)", "Some((1, 2))"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(206);
            let mut tried = 0;
            while tried < 300 {
                let n = rng.below(10);
                let mut nums: Vec<i32> = rng.vec(n, -20, 20);
                nums.sort();
                let target = rng.int(-40, 40) as i32;
                let pairs: Vec<(usize, usize)> = (0..n).flat_map(|i| (i + 1..n).map(move |j| (i, j))).filter(|&(i, j)| nums[i] + nums[j] == target).collect();
                // Keep inputs with at most one answer, so any correct method agrees.
                if pairs.len() > 1 {
                    continue;
                }
                tried += 1;
                check!(format!("nums = {nums:?}, target = {target}"), two_sum_sorted(&nums, target), pairs.first().copied());
            }
        }

        #[test]
        fn scale_200k() {
            let nums: Vec<i32> = (0..200_000).collect();
            check!("nums = 0..200000, target = 399997 / -1", (two_sum_sorted(&nums, 399_997), two_sum_sorted(&nums, -1)), (Some((199_998, 199_999)), None));
        }
        """,
    ],
    wrong=dict(
        quadratic="""
            pub fn two_sum_sorted(nums: &[i32], target: i32) -> Option<(usize, usize)> {
                for i in 0..nums.len() {
                    for j in i + 1..nums.len() {
                        if nums[i] as i64 + nums[j] as i64 == target as i64 {
                            return Some((i, j));
                        }
                    }
                }
                None
            }
        """,
        i32_sum="""
            use std::cmp::Ordering;

            pub fn two_sum_sorted(nums: &[i32], target: i32) -> Option<(usize, usize)> {
                let (mut l, mut r) = (0, nums.len().checked_sub(1)?);
                while l < r {
                    match (nums[l] + nums[r]).cmp(&target) {
                        Ordering::Equal => return Some((l, r)),
                        Ordering::Less => l += 1,
                        Ordering::Greater => r -= 1,
                    }
                }
                None
            }
        """,
        pointers_may_meet="""
            use std::cmp::Ordering;

            pub fn two_sum_sorted(nums: &[i32], target: i32) -> Option<(usize, usize)> {
                let (mut l, mut r) = (0, nums.len().checked_sub(1)?);
                while l <= r {
                    match (nums[l] as i64 + nums[r] as i64).cmp(&(target as i64)) {
                        Ordering::Equal => return Some((l, r)),
                        Ordering::Less => l += 1,
                        Ordering::Greater if r == 0 => return None,
                        Ordering::Greater => r -= 1,
                    }
                }
                None
            }
        """,
    ),
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
    constraints=["0 ≤ nums.len() ≤ 5000"],
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
        T("three_zeros", "nums = [0, 0, 0]", "three_sum(&[0, 0, 0])", "vec![[0, 0, 0]]"),
        T("empty", "nums = []", "three_sum(&[])", "Vec::<[i32; 3]>::new()"),
        T("sorted_output", "nums = [2, -2, 0, 1, -1]", "three_sum(&[2, -2, 0, 1, -1])", "vec![[-2, 0, 2], [-1, 0, 1]]"),
    ],
    hidden=[
        T("many_dups", "nums = [-2, 0, 0, 2, 2, -2]", "three_sum(&[-2, 0, 0, 2, 2, -2])", "vec![[-2, 0, 2]]"),
        T("wide", "nums = [-4, -1, -1, 0, 1, 2, 3]", "three_sum(&[-4, -1, -1, 0, 1, 2, 3])", "vec![[-4, 1, 3], [-1, -1, 2], [-1, 0, 1]]"),
        T("empty", "nums = []", "three_sum(&[])", "Vec::<[i32; 3]>::new()"),
        T("two_values", "nums = [0, 0]", "three_sum(&[0, 0])", "Vec::<[i32; 3]>::new()"),
        T("exactly_three", "nums = [3, -1, -2]", "three_sum(&[3, -1, -2])", "vec![[-2, -1, 3]]"),
        T("all_positive", "nums = [1, 2, 3, 4]", "three_sum(&[1, 2, 3, 4])", "Vec::<[i32; 3]>::new()"),
        T("many_zeros", "nums = [0; 1000]", "three_sum(&vec![0; 1000])", "vec![[0, 0, 0]]"),
        T("extremes_no_overflow", "nums = [i32::MIN, -1, 1, i32::MAX]", "three_sum(&[i32::MIN, -1, 1, i32::MAX])", "vec![[i32::MIN, 1, i32::MAX]]"),
        T("repeated_last", "nums = [-2, 1, 1, 1, 1]", "three_sum(&[-2, 1, 1, 1, 1])", "vec![[-2, 1, 1]]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(207);
            for _ in 0..300 {
                let n = rng.below(10);
                let nums: Vec<i32> = rng.vec(n, -6, 6);
                let mut want = std::collections::BTreeSet::new();
                for i in 0..n {
                    for j in i + 1..n {
                        for k in j + 1..n {
                            if nums[i] + nums[j] + nums[k] == 0 {
                                let mut t = [nums[i], nums[j], nums[k]];
                                t.sort();
                                want.insert(t);
                            }
                        }
                    }
                }
                check!(format!("nums = {nums:?}"), three_sum(&nums), want.into_iter().collect::<Vec<_>>());
            }
        }

        #[test]
        fn scale_5000() {
            // Three odd numbers never sum to 0, so only the three far-away values at the end form a triplet.
            let mut rng = anneal_prelude::Rng::new(208);
            let mut nums: Vec<i32> = (0..5000).map(|i| 2 * i - 4999).collect();
            rng.shuffle(&mut nums);
            nums.extend_from_slice(&[-500_000, 1_000_000, -500_000]);
            check!("nums = the odd values -4999..=4999 shuffled, then -500000, 1000000, -500000", three_sum(&nums), vec![[-500_000, -500_000, 1_000_000]]);
        }
        """,
    ],
    wrong=dict(
        cubic="""
            pub fn three_sum(nums: &[i32]) -> Vec<[i32; 3]> {
                let mut out = std::collections::BTreeSet::new();
                let n = nums.len();
                for i in 0..n {
                    for j in i + 1..n {
                        for k in j + 1..n {
                            if nums[i] as i64 + nums[j] as i64 + nums[k] as i64 == 0 {
                                let mut t = [nums[i], nums[j], nums[k]];
                                t.sort();
                                out.insert(t);
                            }
                        }
                    }
                }
                out.into_iter().collect()
            }
        """,
        i32_sum="""
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
                        let sum = v[i] + v[l] + v[r - 1];
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
        no_left_dedup="""
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
                            r -= 1;
                        }
                    }
                }
                out
            }
        """,
    ),
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
    constraints=["0 ≤ heights.len() ≤ 2·10⁵"],
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
        T("tall_middle", "heights = [1, 100, 100, 1]", "max_area(&[1, 100, 100, 1])", "100"),
        T("one_line", "heights = [5]", "max_area(&[5])", "0"),
        T("empty", "heights = []", "max_area(&[])", "0"),
    ],
    hidden=[
        T("one_line", "heights = [5]", "max_area(&[5])", "0"),
        T("large", "heights = [u32::MAX, u32::MAX]", "max_area(&[u32::MAX, u32::MAX])", "u32::MAX as u64"),
        T("empty", "heights = []", "max_area(&[])", "0"),
        T("uneven_pair", "heights = [1, 5]", "max_area(&[1, 5])", "1"),
        T("zeros", "heights = [0, 0, 0]", "max_area(&[0, 0, 0])", "0"),
        T("descending", "heights = [5, 4, 3, 2, 1]", "max_area(&[5, 4, 3, 2, 1])", "6"),
        T("equal_walls", "heights = [2, 3, 4, 5, 18, 17, 6]", "max_area(&[2, 3, 4, 5, 18, 17, 6])", "17"),
        T("area_past_u32", "heights = [u32::MAX, 0, u32::MAX]", "max_area(&[u32::MAX, 0, u32::MAX])", "2 * u32::MAX as u64"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(209);
            for _ in 0..300 {
                let n = rng.below(12);
                let heights: Vec<u32> = rng.vec(n, 0, 20);
                let mut want = 0u64;
                for i in 0..n {
                    for j in i + 1..n {
                        want = want.max(heights[i].min(heights[j]) as u64 * (j - i) as u64);
                    }
                }
                check!(format!("heights = {heights:?}"), max_area(&heights), want);
            }
        }

        #[test]
        fn scale_200k() {
            let heights: Vec<u32> = (0..200_000u64).map(|i| (i * 7919 % 100_003) as u32).collect();
            check!("heights[i] = i * 7919 % 100003 for i in 0..200000", max_area(&heights), 19_906_008_474);
        }
        """,
    ],
    wrong=dict(
        quadratic="""
            pub fn max_area(heights: &[u32]) -> u64 {
                let mut best = 0u64;
                for i in 0..heights.len() {
                    for j in i + 1..heights.len() {
                        best = best.max(heights[i].min(heights[j]) as u64 * (j - i) as u64);
                    }
                }
                best
            }
        """,
        moves_taller_wall="""
            pub fn max_area(heights: &[u32]) -> u64 {
                let (mut l, mut r) = (0, heights.len());
                let mut best = 0u64;
                while l + 1 < r {
                    let (a, b) = (heights[l], heights[r - 1]);
                    best = best.max(a.min(b) as u64 * (r - 1 - l) as u64);
                    if a > b {
                        l += 1;
                    } else {
                        r -= 1;
                    }
                }
                best
            }
        """,
        u32_product="""
            pub fn max_area(heights: &[u32]) -> u64 {
                let (mut l, mut r) = (0, heights.len());
                let mut best = 0u64;
                while l + 1 < r {
                    let (a, b) = (heights[l], heights[r - 1]);
                    best = best.max((a.min(b) * (r - 1 - l) as u32) as u64);
                    if a < b {
                        l += 1;
                    } else {
                        r -= 1;
                    }
                }
                best
            }
        """,
    ),
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
    constraints=["3 ≤ nums.len() ≤ 5000", "|nums[i]| ≤ 10⁴", "|target| ≤ 10⁵"],
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
        T("below_zero_is_closer", "nums = [1, 1, 1], target = 0", "three_sum_closest(&[1, 1, 1], 0)", "3"),
        T("exactly_three", "nums = [1, 2, 3], target = 100", "three_sum_closest(&[1, 2, 3], 100)", "6"),
        T("negative_target", "nums = [-5, -4, -3, -2], target = -100", "three_sum_closest(&[-5, -4, -3, -2], -100)", "-12"),
    ],
    hidden=[
        T("hit", "nums = [1, 1, 1, 0], target = 3", "three_sum_closest(&[1, 1, 1, 0], 3)", "3"),
        T("negative_target", "nums = [4, 0, 5, -5, 3, 3, 0, -4, -5], target = -2", "three_sum_closest(&[4, 0, 5, -5, 3, 3, 0, -4, -5], -2)", "-2"),
        T("exactly_three", "nums = [1, 2, 3], target = 100", "three_sum_closest(&[1, 2, 3], 100)", "6"),
        T("all_negative", "nums = [-5, -4, -3, -2], target = -100", "three_sum_closest(&[-5, -4, -3, -2], -100)", "-12"),
        T("far_value_unused", "nums = [-1, 0, 1, 1, 55], target = 3", "three_sum_closest(&[-1, 0, 1, 1, 55], 3)", "2"),
        T("needs_the_big_value", "nums = [1, 6, 9, 14, 16, 70], target = 81", "three_sum_closest(&[1, 6, 9, 14, 16, 70], 81)", "80"),
        T("duplicates", "nums = [-1000, -5, -5, -5, -5, -5, -5, -1, -1, -1], target = -14", "three_sum_closest(&[-1000, -5, -5, -5, -5, -5, -5, -1, -1, -1], -14)", "-15"),
        T("bounds", "nums = [10000, 10000, 10000, -10000], target = 100000", "three_sum_closest(&[10_000, 10_000, 10_000, -10_000], 100_000)", "30000"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(210);
            let mut tried = 0;
            while tried < 300 {
                let n = 3 + rng.below(8);
                let nums: Vec<i32> = rng.vec(n, -20, 20);
                let target = rng.int(-70, 70) as i32;
                let mut sums = Vec::new();
                for i in 0..n {
                    for j in i + 1..n {
                        for k in j + 1..n {
                            sums.push(nums[i] + nums[j] + nums[k]);
                        }
                    }
                }
                let d = sums.iter().map(|s| s.abs_diff(target)).min().unwrap();
                let mut closest: Vec<i32> = sums.into_iter().filter(|s| s.abs_diff(target) == d).collect();
                closest.dedup();
                closest.sort();
                closest.dedup();
                // The problem promises exactly one closest sum.
                if closest.len() > 1 {
                    continue;
                }
                tried += 1;
                check!(format!("nums = {nums:?}, target = {target}"), three_sum_closest(&nums, target), closest[0]);
            }
        }

        #[test]
        fn scale_5000() {
            let nums: Vec<i32> = (0..5000).map(|i| (i * 7919 % 20_001) - 10_000).collect();
            let mut top = nums.clone();
            top.sort();
            let want: i32 = top[4997..].iter().sum();
            check!("nums[i] = i * 7919 % 20001 - 10000 for i in 0..5000, target = 100000", three_sum_closest(&nums, 100_000), want);
        }
        """,
    ],
    wrong=dict(
        cubic="""
            pub fn three_sum_closest(nums: &[i32], target: i32) -> i32 {
                let n = nums.len();
                let mut best = nums[0] + nums[1] + nums[2];
                for i in 0..n {
                    for j in i + 1..n {
                        for k in j + 1..n {
                            let sum = nums[i] + nums[j] + nums[k];
                            if sum.abs_diff(target) < best.abs_diff(target) {
                                best = sum;
                            }
                        }
                    }
                }
                best
            }
        """,
        best_starts_at_zero="""
            pub fn three_sum_closest(nums: &[i32], target: i32) -> i32 {
                let mut v = nums.to_vec();
                v.sort_unstable();
                let mut best: i32 = 0;
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
        unsorted_two_pointers="""
            pub fn three_sum_closest(nums: &[i32], target: i32) -> i32 {
                let v = nums;
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
    ),
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
    constraints=["0 ≤ prices.len() ≤ 2·10⁵"],
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
        T("empty", "prices = []", "max_profit(&[])", "0"),
        T("single", "prices = [5]", "max_profit(&[5])", "0"),
        T("buy_before_sell", "prices = [2, 4, 1]", "max_profit(&[2, 4, 1])", "2"),
    ],
    hidden=[
        T("empty", "prices = []", "max_profit(&[])", "0"),
        T("late_low", "prices = [2, 4, 1]", "max_profit(&[2, 4, 1])", "2"),
        T("single", "prices = [5]", "max_profit(&[5])", "0"),
        T("flat", "prices = [3, 3, 3]", "max_profit(&[3, 3, 3])", "0"),
        T("rising", "prices = [1, 2, 3, 4, 5]", "max_profit(&[1, 2, 3, 4, 5])", "4"),
        T("low_after_high", "prices = [3, 8, 1, 5]", "max_profit(&[3, 8, 1, 5])", "5"),
        T("extremes", "prices = [0, u32::MAX]", "max_profit(&[0, u32::MAX])", "u32::MAX"),
        T("extremes_falling", "prices = [u32::MAX, 0]", "max_profit(&[u32::MAX, 0])", "0"),
        T("new_low_then_bigger_gain", "prices = [5, 7, 1, 9]", "max_profit(&[5, 7, 1, 9])", "8"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(211);
            for _ in 0..300 {
                let n = rng.below(12);
                let prices: Vec<u32> = rng.vec(n, 0, 30);
                let mut want = 0;
                for i in 0..n {
                    for j in i + 1..n {
                        want = want.max(prices[j].saturating_sub(prices[i]));
                    }
                }
                check!(format!("prices = {prices:?}"), max_profit(&prices), want);
            }
        }

        #[test]
        fn scale_200k() {
            let mut prices: Vec<u32> = (0..200_000).map(|i| 1_000_000 - i).collect();
            prices.push(1_000_000);
            check!("prices = 1000000 down to 800001, then 1000000", max_profit(&prices), 199_999);
        }
        """,
    ],
    wrong=dict(
        quadratic="""
            pub fn max_profit(prices: &[u32]) -> u32 {
                let mut best = 0;
                for i in 0..prices.len() {
                    for j in i + 1..prices.len() {
                        best = best.max(prices[j].saturating_sub(prices[i]));
                    }
                }
                best
            }
        """,
        max_minus_min="""
            pub fn max_profit(prices: &[u32]) -> u32 {
                let hi = prices.iter().copied().max().unwrap_or(0);
                let lo = prices.iter().copied().min().unwrap_or(0);
                hi - lo
            }
        """,
        buys_at_first_day="""
            pub fn max_profit(prices: &[u32]) -> u32 {
                let Some(&first) = prices.first() else { return 0 };
                prices.iter().map(|&p| p.saturating_sub(first)).max().unwrap_or(0)
            }
        """,
    ),
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
    constraints=["0 ≤ s.len() ≤ 2·10⁵"],
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
        T("empty", "s = \"\"", 'length_of_longest_substring("")', "0"),
        T("single", "s = \"x\"", 'length_of_longest_substring("x")', "1"),
    ],
    hidden=[
        T("empty", "s = \"\"", 'length_of_longest_substring("")', "0"),
        T("stale_repeat", "s = \"abba\"", 'length_of_longest_substring("abba")', "2"),
        T("spaces", "s = \" a b\"", 'length_of_longest_substring(" a b")', "3"),
        T("single", "s = \"x\"", 'length_of_longest_substring("x")', "1"),
        T("dvdf", "s = \"dvdf\"", 'length_of_longest_substring("dvdf")', "3"),
        T("all_distinct", "s = \"abcdefghijklmnopqrstuvwxyz\"", 'length_of_longest_substring("abcdefghijklmnopqrstuvwxyz")', "26"),
        T("case_sensitive", "s = \"aAbB\"", 'length_of_longest_substring("aAbB")', "4"),
        T("digits_and_symbols", "s = \"12!1@#\"", 'length_of_longest_substring("12!1@#")', "5"),
        T("every_ascii_byte", "s = every ASCII byte 0..128, twice", "{ let s: String = (0u8..128).chain(0u8..128).map(char::from).collect(); length_of_longest_substring(&s) }", "128"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(212);
            for _ in 0..300 {
                let n = rng.below(14);
                let s = rng.string(n, "abcd ");
                let b = s.as_bytes();
                let mut want = 0;
                for i in 0..n {
                    for j in i..n {
                        let w = &b[i..=j];
                        if (0..w.len()).all(|x| !w[x + 1..].contains(&w[x])) {
                            want = want.max(w.len());
                        }
                    }
                }
                check!(format!("s = {s:?}"), length_of_longest_substring(&s), want);
            }
        }

        #[test]
        fn scale_200k() {
            let printable: String = (0x20u8..0x7f).map(char::from).collect();
            let s = "a".repeat(200_000 - printable.len()) + &printable;
            check!("s = \\"a\\" × 199905 followed by the 95 printable ASCII characters", length_of_longest_substring(&s), 95);
        }
        """,
    ],
    wrong=dict(
        jumps_back_on_stale_repeat="""
            pub fn length_of_longest_substring(s: &str) -> usize {
                let mut last: [Option<usize>; 256] = [None; 256];
                let (mut start, mut best) = (0, 0);
                for (i, b) in s.bytes().enumerate() {
                    if let Some(prev) = last[b as usize] {
                        start = prev + 1;
                    }
                    last[b as usize] = Some(i);
                    best = best.max(i + 1 - start);
                }
                best
            }
        """,
        restarts_at_the_repeat="""
            pub fn length_of_longest_substring(s: &str) -> usize {
                let mut seen = [false; 256];
                let (mut len, mut best) = (0, 0);
                for b in s.bytes() {
                    if seen[b as usize] {
                        seen = [false; 256];
                        len = 0;
                    }
                    seen[b as usize] = true;
                    len += 1;
                    best = best.max(len);
                }
                best
            }
        """,
        lowercase_table="""
            pub fn length_of_longest_substring(s: &str) -> usize {
                let mut last: [Option<usize>; 26] = [None; 26];
                let (mut start, mut best) = (0, 0);
                for (i, b) in s.bytes().enumerate() {
                    let c = (b.to_ascii_lowercase() % 26) as usize;
                    if let Some(prev) = last[c].filter(|&p| p >= start) {
                        start = prev + 1;
                    }
                    last[c] = Some(i);
                    best = best.max(i + 1 - start);
                }
                best
            }
        """,
    ),
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
    constraints=["0 ≤ s.len() ≤ 2·10⁵"],
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
        T("empty", "s = \"\", k = 3", 'character_replacement("", 3)', "0"),
        T("zero_k", "s = \"ABBB\", k = 0", 'character_replacement("ABBB", 0)', "3"),
        T("k_past_length", "s = \"AB\", k = 5", 'character_replacement("AB", 5)', "2"),
    ],
    hidden=[
        T("zero_k", "s = \"ABBB\", k = 0", 'character_replacement("ABBB", 0)', "3"),
        T("empty", "s = \"\", k = 3", 'character_replacement("", 3)', "0"),
        T("single", "s = \"Q\", k = 0", 'character_replacement("Q", 0)', "1"),
        T("k_past_length", "s = \"AB\", k = 5", 'character_replacement("AB", 5)', "2"),
        T("all_same", "s = \"ZZZZ\", k = 0", 'character_replacement("ZZZZ", 0)', "4"),
        T("zero_k_alternating", "s = \"ABABAB\", k = 0", 'character_replacement("ABABAB", 0)', "1"),
        T("best_run_late", "s = \"ABCDEEEEF\", k = 1", 'character_replacement("ABCDEEEEF", 1)', "5"),
        T("fill_a_gap", "s = \"AAABAAACAA\", k = 2", 'character_replacement("AAABAAACAA", 2)', "10"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(213);
            for _ in 0..300 {
                let n = rng.below(14);
                let s = rng.string(n, "ABC");
                let k = rng.below(4);
                let b = s.as_bytes();
                let mut want = 0;
                for i in 0..n {
                    for j in i..n {
                        let w = &b[i..=j];
                        let most = (b'A'..=b'C').map(|c| w.iter().filter(|&&x| x == c).count()).max().unwrap();
                        if w.len() - most <= k {
                            want = want.max(w.len());
                        }
                    }
                }
                check!(format!("s = {s:?}, k = {k}"), character_replacement(&s, k), want);
            }
        }

        #[test]
        fn scale_200k() {
            let s = "AB".repeat(100_000);
            check!("s = \\"AB\\" × 100000, k = 100000 / 99999", (character_replacement(&s, 100_000), character_replacement(&s, 99_999)), (200_000, 199_999));
        }
        """,
    ],
    wrong=dict(
        quadratic="""
            pub fn character_replacement(s: &str, k: usize) -> usize {
                let b = s.as_bytes();
                let mut best = 0;
                for start in 0..b.len() {
                    let mut counts = [0usize; 26];
                    let mut most = 0;
                    for end in start..b.len() {
                        let c = (b[end] - b'A') as usize;
                        counts[c] += 1;
                        most = most.max(counts[c]);
                        if end + 1 - start - most > k {
                            break;
                        }
                        best = best.max(end + 1 - start);
                    }
                }
                best
            }
        """,
        window_length_off_by_one="""
            pub fn character_replacement(s: &str, k: usize) -> usize {
                let b = s.as_bytes();
                let mut counts = [0usize; 26];
                let (mut start, mut most, mut best) = (0, 0, 0);
                for end in 0..b.len() {
                    let c = (b[end] - b'A') as usize;
                    counts[c] += 1;
                    most = most.max(counts[c]);
                    while end - start > most + k {
                        counts[(b[start] - b'A') as usize] -= 1;
                        start += 1;
                    }
                    best = best.max(end + 1 - start);
                }
                best
            }
        """,
        longest_run_plus_k="""
            pub fn character_replacement(s: &str, k: usize) -> usize {
                let b = s.as_bytes();
                let (mut run, mut best) = (0, 0);
                for i in 0..b.len() {
                    run = if i > 0 && b[i] == b[i - 1] { run + 1 } else { 1 };
                    best = best.max(run);
                }
                (best + k).min(b.len())
            }
        """,
    ),
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
    constraints=["1 ≤ pattern.len(), s.len() ≤ 2·10⁵"],
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
            let (mut want, mut have) = ([0u32; 26], [0u32; 26]);
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
        T("single_match", "pattern = \"a\", s = \"a\"", 'check_inclusion("a", "a")', "true"),
        T("longer_pattern", "pattern = \"abc\", s = \"ab\"", 'check_inclusion("abc", "ab")', "false"),
        T("counts_matter", "pattern = \"aab\", s = \"abbab\"", 'check_inclusion("aab", "abbab")', "false"),
    ],
    hidden=[
        T("longer_pattern", "pattern = \"abc\", s = \"ab\"", 'check_inclusion("abc", "ab")', "false"),
        T("whole_string", "pattern = \"adc\", s = \"dcda\"", 'check_inclusion("adc", "dcda")', "true"),
        T("single_match", "pattern = \"a\", s = \"a\"", 'check_inclusion("a", "a")', "true"),
        T("single_miss", "pattern = \"a\", s = \"b\"", 'check_inclusion("a", "b")', "false"),
        T("counts_matter", "pattern = \"aab\", s = \"abbab\"", 'check_inclusion("aab", "abbab")', "false"),
        T("repeated_letters", "pattern = \"aab\", s = \"xabab\"", 'check_inclusion("aab", "xabab")', "true"),
        T("at_the_end", "pattern = \"xyz\", s = \"aaaaazyx\"", 'check_inclusion("xyz", "aaaaazyx")', "true"),
        T("same_length_not_perm", "pattern = \"abc\", s = \"abd\"", 'check_inclusion("abc", "abd")', "false"),
        T("split_across_gap", "pattern = \"ab\", s = \"acb\"", 'check_inclusion("ab", "acb")', "false"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(214);
            for _ in 0..400 {
                let pn = 1 + rng.below(4);
                let n = 1 + rng.below(10);
                let pattern = rng.string(pn, "abc");
                let s = rng.string(n, "abc");
                let mut want_sorted: Vec<u8> = pattern.bytes().collect();
                want_sorted.sort();
                let want = s.as_bytes().windows(pn).any(|w| {
                    let mut w = w.to_vec();
                    w.sort();
                    w == want_sorted
                });
                check!(format!("pattern = {pattern:?}, s = {s:?}"), check_inclusion(&pattern, &s), want);
            }
        }

        #[test]
        fn scale_200k() {
            let pattern = "a".repeat(99_999) + "b";
            let s = "a".repeat(199_999) + "b";
            let t = "a".repeat(200_000);
            check!("pattern = \\"a\\" × 99999 + \\"b\\", s = \\"a\\" × 199999 + \\"b\\" / \\"a\\" × 200000", (check_inclusion(&pattern, &s), check_inclusion(&pattern, &t)), (true, false));
        }
        """,
    ],
    wrong=dict(
        recount_each_window="""
            pub fn check_inclusion(pattern: &str, s: &str) -> bool {
                let (p, s) = (pattern.as_bytes(), s.as_bytes());
                if p.len() > s.len() {
                    return false;
                }
                let mut want = [0u32; 26];
                for &b in p {
                    want[(b - b'a') as usize] += 1;
                }
                (0..=s.len() - p.len()).any(|i| {
                    let mut have = [0u32; 26];
                    for &b in &s[i..i + p.len()] {
                        have[(b - b'a') as usize] += 1;
                    }
                    have == want
                })
            }
        """,
        letter_set_not_counts="""
            pub fn check_inclusion(pattern: &str, s: &str) -> bool {
                let (p, s) = (pattern.as_bytes(), s.as_bytes());
                if p.len() > s.len() {
                    return false;
                }
                let mut want = [false; 26];
                for &b in p {
                    want[(b - b'a') as usize] = true;
                }
                s.windows(p.len()).any(|w| {
                    let mut have = [false; 26];
                    for &b in w {
                        have[(b - b'a') as usize] = true;
                    }
                    have == want
                })
            }
        """,
        skips_last_window="""
            pub fn check_inclusion(pattern: &str, s: &str) -> bool {
                let (p, s) = (pattern.as_bytes(), s.as_bytes());
                if p.len() > s.len() {
                    return false;
                }
                let idx = |b: u8| (b - b'a') as usize;
                let (mut want, mut have) = ([0u32; 26], [0u32; 26]);
                for &b in p {
                    want[idx(b)] += 1;
                }
                for i in 0..s.len() - 1 {
                    have[idx(s[i])] += 1;
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
    ),
    hints=[("approach", "Slide a window the size of the pattern and compare letter counts."), ("rust", "Arrays implement `==` element-wise.")],
    notes=("Comparing two `[u32; 26]` arrays is 26 comparisons, so each step is O(1).", "O(n)", "O(1)"),
    follow_up="How would you avoid comparing all 26 counts on every step?",
    related=["D1"],
))

P.append(dict(
    slug="find-all-anagrams", title="Find all anagrams in a string", level="medium", stage="windows", tags=["fixed window"],
    teaches=["The same window as permutation-in-string, collecting every start index."],
    statement="Return every start index in `s` where an anagram of `p` begins, ascending. Both are lowercase ASCII.",
    examples=[("s = \"cbaebabacd\", p = \"abc\"", "[0, 6]")],
    constraints=["0 ≤ s.len(), p.len() ≤ 2·10⁵"],
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
            let (mut want, mut have) = ([0u32; 26], [0u32; 26]);
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
        T("none", "s = \"aaaa\", p = \"b\"", 'find_anagrams("aaaa", "b")', "Vec::<usize>::new()"),
        T("longer_pattern", "s = \"a\", p = \"ab\"", 'find_anagrams("a", "ab")', "Vec::<usize>::new()"),
        T("empty_pattern", "s = \"abc\", p = \"\"", 'find_anagrams("abc", "")', "Vec::<usize>::new()"),
    ],
    hidden=[
        T("none", "s = \"aaaa\", p = \"b\"", 'find_anagrams("aaaa", "b")', "Vec::<usize>::new()"),
        T("longer_pattern", "s = \"a\", p = \"ab\"", 'find_anagrams("a", "ab")', "Vec::<usize>::new()"),
        T("empty_pattern", "s = \"abc\", p = \"\"", 'find_anagrams("abc", "")', "Vec::<usize>::new()"),
        T("empty_s", "s = \"\", p = \"a\"", 'find_anagrams("", "a")', "Vec::<usize>::new()"),
        T("whole_string", "s = \"bca\", p = \"abc\"", 'find_anagrams("bca", "abc")', "vec![0]"),
        T("single_letters", "s = \"aaa\", p = \"a\"", 'find_anagrams("aaa", "a")', "vec![0, 1, 2]"),
        T("counts_matter", "s = \"abbab\", p = \"aab\"", 'find_anagrams("abbab", "aab")', "Vec::<usize>::new()"),
        T("last_window", "s = \"xxxba\", p = \"ab\"", 'find_anagrams("xxxba", "ab")', "vec![3]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(215);
            for _ in 0..400 {
                let pn = 1 + rng.below(4);
                let n = rng.below(11);
                let p = rng.string(pn, "abc");
                let s = rng.string(n, "abc");
                let mut key: Vec<u8> = p.bytes().collect();
                key.sort();
                let want: Vec<usize> = (0..(n + 1).saturating_sub(pn))
                    .filter(|&i| {
                        let mut w = s.as_bytes()[i..i + pn].to_vec();
                        w.sort();
                        w == key
                    })
                    .collect();
                check!(format!("s = {s:?}, p = {p:?}"), find_anagrams(&s, &p), want);
            }
        }

        #[test]
        fn scale_200k() {
            let s = "a".repeat(199_999) + "b";
            let p = "a".repeat(99_999) + "b";
            check!("s = \\"a\\" × 199999 + \\"b\\", p = \\"a\\" × 99999 + \\"b\\"", find_anagrams(&s, &p), vec![100_000]);
        }
        """,
    ],
    wrong=dict(
        recount_each_window="""
            pub fn find_anagrams(s: &str, p: &str) -> Vec<usize> {
                let (s, p) = (s.as_bytes(), p.as_bytes());
                if p.is_empty() || p.len() > s.len() {
                    return Vec::new();
                }
                let mut want = [0u32; 26];
                for &b in p {
                    want[(b - b'a') as usize] += 1;
                }
                (0..=s.len() - p.len())
                    .filter(|&i| {
                        let mut have = [0u32; 26];
                        for &b in &s[i..i + p.len()] {
                            have[(b - b'a') as usize] += 1;
                        }
                        have == want
                    })
                    .collect()
            }
        """,
        misses_last_window="""
            pub fn find_anagrams(s: &str, p: &str) -> Vec<usize> {
                let (s, p) = (s.as_bytes(), p.as_bytes());
                let mut out = Vec::new();
                if p.is_empty() || p.len() > s.len() {
                    return out;
                }
                let idx = |b: u8| (b - b'a') as usize;
                let (mut want, mut have) = ([0u32; 26], [0u32; 26]);
                for &b in p {
                    want[idx(b)] += 1;
                }
                for &b in &s[..p.len()] {
                    have[idx(b)] += 1;
                }
                for i in p.len()..s.len() {
                    if have == want {
                        out.push(i - p.len());
                    }
                    have[idx(s[i])] += 1;
                    have[idx(s[i - p.len()])] -= 1;
                }
                out
            }
        """,
        end_indices="""
            pub fn find_anagrams(s: &str, p: &str) -> Vec<usize> {
                let (s, p) = (s.as_bytes(), p.as_bytes());
                let mut out = Vec::new();
                if p.is_empty() || p.len() > s.len() {
                    return out;
                }
                let idx = |b: u8| (b - b'a') as usize;
                let (mut want, mut have) = ([0u32; 26], [0u32; 26]);
                for &b in p {
                    want[idx(b)] += 1;
                }
                for (i, &b) in s.iter().enumerate() {
                    have[idx(b)] += 1;
                    if i >= p.len() {
                        have[idx(s[i - p.len()])] -= 1;
                    }
                    if i + 1 >= p.len() && have == want {
                        out.push(i);
                    }
                }
                out
            }
        """,
    ),
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
    constraints=["0 ≤ s.len() ≤ 2·10⁵", "1 ≤ t.len() ≤ 2·10⁵"],
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
        T("leftmost_tie", "s = \"abcab\", t = \"ab\"", 'min_window("abcab", "ab")', '"ab"'),
        T("duplicates_counted", "s = \"abaa\", t = \"aa\"", 'min_window("abaa", "aa")', '"aa"'),
    ],
    hidden=[
        T("duplicates_needed", "s = \"aaflslflsldkalskaaa\", t = \"aaa\"", 'min_window("aaflslflsldkalskaaa", "aaa")', '"aaa"'),
        T("leftmost_tie", "s = \"abcab\", t = \"ab\"", 'min_window("abcab", "ab")', '"ab"'),
        T("empty_s", "s = \"\", t = \"a\"", 'min_window("", "a")', '""'),
        T("t_longer", "s = \"ab\", t = \"abc\"", 'min_window("ab", "abc")', '""'),
        T("case_sensitive", "s = \"aA\", t = \"A\"", 'min_window("aA", "A")', '"A"'),
        T("whole_string", "s = \"cab\", t = \"bac\"", 'min_window("cab", "bac")', '"cab"'),
        T("window_at_end", "s = \"xxxxab\", t = \"ba\"", 'min_window("xxxxab", "ba")', '"ab"'),
        T("shrinks_past_surplus", "s = \"aab\", t = \"ab\"", 'min_window("aab", "ab")', '"ab"'),
        T("symbols_and_spaces", "s = \"x !y! z\", t = \"! \"", 'min_window("x !y! z", "! ")', '" !"'),
        """
        #[test]
        fn returns_a_slice_of_s() {
            let s = String::from("ADOBECODEBANC");
            let got = min_window(&s, "ABC");
            check!("s = \\"ADOBECODEBANC\\", t = \\"ABC\\" (the result points into s)", (got, got.as_ptr() as usize - s.as_ptr() as usize), ("BANC", 9));
        }

        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(216);
            for _ in 0..300 {
                let n = rng.below(12);
                let tn = 1 + rng.below(4);
                let s = rng.string(n, "abc");
                let t = rng.string(tn, "abc");
                let count = |w: &str, c: char| w.chars().filter(|&x| x == c).count();
                let covers = |w: &str| t.chars().all(|c| count(w, c) >= count(&t, c));
                let mut want = "";
                'outer: for len in 1..=n {
                    for i in 0..=n - len {
                        if covers(&s[i..i + len]) {
                            want = &s[i..i + len];
                            break 'outer;
                        }
                    }
                }
                check!(format!("s = {s:?}, t = {t:?}"), min_window(&s, &t).to_string(), want.to_string());
            }
        }

        #[test]
        fn scale_200k() {
            let s = "a".to_string() + &"x".repeat(199_998) + "b";
            let got = min_window(&s, "ab");
            check!("s = \\"a\\" + \\"x\\" × 199998 + \\"b\\", t = \\"ab\\"", got.len(), 200_000);
        }
        """,
    ],
    wrong=dict(
        quadratic="""
            pub fn min_window<'a>(s: &'a str, t: &str) -> &'a str {
                let b = s.as_bytes();
                let mut need = [0i32; 128];
                for c in t.bytes() {
                    need[c as usize] += 1;
                }
                let mut best: Option<(usize, usize)> = None;
                for start in 0..b.len() {
                    let mut left = need;
                    let mut missing = t.len();
                    for end in start..b.len() {
                        let c = b[end] as usize;
                        if left[c] > 0 {
                            missing -= 1;
                        }
                        left[c] -= 1;
                        if missing == 0 {
                            if best.is_none_or(|(l, r)| end + 1 - start < r - l) {
                                best = Some((start, end + 1));
                            }
                            break;
                        }
                    }
                }
                best.map_or("", |(l, r)| &s[l..r])
            }
        """,
        rightmost_tie="""
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
                        if best.is_none_or(|(l, r)| end + 1 - start <= r - l) {
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
        ignores_duplicates_in_t="""
            pub fn min_window<'a>(s: &'a str, t: &str) -> &'a str {
                let b = s.as_bytes();
                let mut need = [0i32; 128];
                for c in t.bytes() {
                    need[c as usize] = 1;
                }
                let mut missing = need.iter().filter(|&&x| x > 0).count();
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
    ),
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
    constraints=["0 ≤ heights.len() ≤ 2·10⁵"],
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
        T("empty", "heights = []", "trap(&[])", "0"),
        T("monotonic", "heights = [1, 2, 3, 4]", "trap(&[1, 2, 3, 4])", "0"),
        T("lower_wall_decides", "heights = [3, 0, 1]", "trap(&[3, 0, 1])", "1"),
    ],
    hidden=[
        T("empty", "heights = []", "trap(&[])", "0"),
        T("monotonic", "heights = [1, 2, 3, 4]", "trap(&[1, 2, 3, 4])", "0"),
        T("tall_walls", "heights = [u32::MAX, 0, u32::MAX]", "trap(&[u32::MAX, 0, u32::MAX])", "u32::MAX as u64"),
        T("single", "heights = [7]", "trap(&[7])", "0"),
        T("two", "heights = [3, 0]", "trap(&[3, 0])", "0"),
        T("descending", "heights = [4, 3, 2, 1]", "trap(&[4, 3, 2, 1])", "0"),
        T("uneven_walls", "heights = [3, 0, 1]", "trap(&[3, 0, 1])", "1"),
        T("plateau", "heights = [2, 0, 0, 2]", "trap(&[2, 0, 0, 2])", "4"),
        T("total_past_u32", "heights = [u32::MAX, 0, 0, u32::MAX]", "trap(&[u32::MAX, 0, 0, u32::MAX])", "2 * u32::MAX as u64"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(217);
            for _ in 0..300 {
                let n = rng.below(14);
                let heights: Vec<u32> = rng.vec(n, 0, 6);
                let want: u64 = (0..n)
                    .map(|i| {
                        let left = *heights[..=i].iter().max().unwrap();
                        let right = *heights[i..].iter().max().unwrap();
                        (left.min(right) - heights[i]) as u64
                    })
                    .sum();
                check!(format!("heights = {heights:?}"), trap(&heights), want);
            }
        }

        #[test]
        fn scale_200k() {
            let heights: Vec<u32> = (0..200_000u64).map(|i| (i * 7919 % 100_003) as u32).collect();
            check!("heights[i] = i * 7919 % 100003 for i in 0..200000", trap(&heights), 9_997_919_672);
        }
        """,
    ],
    wrong=dict(
        quadratic="""
            pub fn trap(heights: &[u32]) -> u64 {
                (0..heights.len())
                    .map(|i| {
                        let left = *heights[..=i].iter().max().unwrap();
                        let right = *heights[i..].iter().max().unwrap();
                        (left.min(right) - heights[i]) as u64
                    })
                    .sum()
            }
        """,
        u32_total="""
            pub fn trap(heights: &[u32]) -> u64 {
                let (mut l, mut r) = (0, heights.len());
                let (mut left_max, mut right_max) = (0u32, 0u32);
                let mut water = 0u32;
                while l < r {
                    if heights[l] < heights[r - 1] {
                        left_max = left_max.max(heights[l]);
                        water += left_max - heights[l];
                        l += 1;
                    } else {
                        right_max = right_max.max(heights[r - 1]);
                        water += right_max - heights[r - 1];
                        r -= 1;
                    }
                }
                water as u64
            }
        """,
        left_wall_only="""
            pub fn trap(heights: &[u32]) -> u64 {
                let mut left_max = 0u32;
                let mut water = 0u64;
                for &h in heights {
                    left_max = left_max.max(h);
                    water += (left_max - h) as u64;
                }
                water
            }
        """,
    ),
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
    constraints=["1 ≤ k ≤ nums.len() ≤ 2·10⁵"],
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
        T("single", "nums = [1], k = 1", "max_sliding_window(&[1], 1)", "vec![1]"),
        T("whole", "nums = [9, 10, 9, -7], k = 4", "max_sliding_window(&[9, 10, 9, -7], 4)", "vec![10]"),
        T("max_leaves_window", "nums = [9, 1, 1, 1], k = 2", "max_sliding_window(&[9, 1, 1, 1], 2)", "vec![9, 1, 1]"),
    ],
    hidden=[
        T("whole", "nums = [9, 10, 9, -7], k = 4", "max_sliding_window(&[9, 10, 9, -7], 4)", "vec![10]"),
        T("descending", "nums = [5, 4, 3, 2, 1], k = 2", "max_sliding_window(&[5, 4, 3, 2, 1], 2)", "vec![5, 4, 3, 2]"),
        T("large", "nums = 0..100000, k = 1000", "max_sliding_window(&(0..100_000).collect::<Vec<_>>(), 1000).len()", "99001"),
        T("single", "nums = [1], k = 1", "max_sliding_window(&[1], 1)", "vec![1]"),
        T("ascending", "nums = [1, 2, 3, 4, 5], k = 2", "max_sliding_window(&[1, 2, 3, 4, 5], 2)", "vec![2, 3, 4, 5]"),
        T("all_equal", "nums = [7, 7, 7, 7], k = 3", "max_sliding_window(&[7, 7, 7, 7], 3)", "vec![7, 7]"),
        T("max_leaves_window", "nums = [9, 1, 1, 1], k = 2", "max_sliding_window(&[9, 1, 1, 1], 2)", "vec![9, 1, 1]"),
        T("extremes", "nums = [i32::MIN, i32::MAX, i32::MIN, i32::MIN], k = 2", "max_sliding_window(&[i32::MIN, i32::MAX, i32::MIN, i32::MIN], 2)", "vec![i32::MAX, i32::MAX, i32::MIN]"),
        T("negatives", "nums = [-7, -8, 7, 5, 7, 1, 6, 0], k = 4", "max_sliding_window(&[-7, -8, 7, 5, 7, 1, 6, 0], 4)", "vec![7, 7, 7, 7, 7]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(218);
            for _ in 0..300 {
                let n = 1 + rng.below(14);
                let k = 1 + rng.below(n);
                let nums: Vec<i32> = rng.vec(n, -5, 5);
                let want: Vec<i32> = nums.windows(k).map(|w| *w.iter().max().unwrap()).collect();
                check!(format!("nums = {nums:?}, k = {k}"), max_sliding_window(&nums, k), want);
            }
        }

        #[test]
        fn scale_200k() {
            let nums: Vec<i32> = (0..200_000).rev().collect();
            let want: Vec<i32> = (100_000 - 1..200_000).rev().collect();
            check!("nums = 199999 down to 0, k = 100000", max_sliding_window(&nums, 100_000) == want, true);
        }
        """,
    ],
    wrong=dict(
        rescan_each_window="""
            pub fn max_sliding_window(nums: &[i32], k: usize) -> Vec<i32> {
                nums.windows(k).map(|w| *w.iter().max().unwrap()).collect()
            }
        """,
        window_one_too_wide="""
            use std::collections::VecDeque;

            pub fn max_sliding_window(nums: &[i32], k: usize) -> Vec<i32> {
                let mut dq: VecDeque<usize> = VecDeque::new();
                let mut out = Vec::with_capacity(nums.len() + 1 - k);
                for i in 0..nums.len() {
                    if dq.front().is_some_and(|&f| f + k < i) {
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
        max_so_far="""
            pub fn max_sliding_window(nums: &[i32], k: usize) -> Vec<i32> {
                let mut best = i32::MIN;
                let mut out = Vec::new();
                for (i, &x) in nums.iter().enumerate() {
                    best = best.max(x);
                    if i + 1 >= k {
                        out.push(best);
                    }
                }
                out
            }
        """,
    ),
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
    constraints=["0 ≤ nums.len() ≤ 600"],
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
        T("too_short", "nums = [1, 2, 3], target = 6", "four_sum(&[1, 2, 3], 6)", "Vec::<[i32; 4]>::new()"),
        T("empty", "nums = [], target = 0", "four_sum(&[], 0)", "Vec::<[i32; 4]>::new()"),
        T("sorted_output", "nums = [4, -1, 3, 0], target = 6", "four_sum(&[4, -1, 3, 0], 6)", "vec![[-1, 0, 3, 4]]"),
    ],
    hidden=[
        T("overflow", "nums = [1e9 × 4], target = 4e9", "four_sum(&[1_000_000_000; 4], 4_000_000_000)", "vec![[1_000_000_000; 4]]"),
        T("too_short", "nums = [1, 2, 3], target = 6", "four_sum(&[1, 2, 3], 6)", "Vec::<[i32; 4]>::new()"),
        T("empty", "nums = [], target = 0", "four_sum(&[], 0)", "Vec::<[i32; 4]>::new()"),
        T("exactly_four", "nums = [4, -1, 3, 0], target = 6", "four_sum(&[4, -1, 3, 0], 6)", "vec![[-1, 0, 3, 4]]"),
        T("negative_target", "nums = [-3, -2, -1, 0, 0, 1, 2, 3], target = -6", "four_sum(&[-3, -2, -1, 0, 0, 1, 2, 3], -6)", "vec![[-3, -2, -1, 0]]"),
        T("many_zeros", "nums = [0; 500], target = 0", "four_sum(&vec![0; 500], 0)", "vec![[0, 0, 0, 0]]"),
        T("below_i32_min", "nums = [-1e9 × 4, 1e9], target = -4e9", "four_sum(&[-1_000_000_000, -1_000_000_000, -1_000_000_000, -1_000_000_000, 1_000_000_000], -4_000_000_000)", "vec![[-1_000_000_000; 4]]"),
        T("target_out_of_i32", "nums = [1e9 × 4], target = -294967296", "four_sum(&[1_000_000_000; 4], -294_967_296)", "Vec::<[i32; 4]>::new()"),
        T("dedup_second_value", "nums = [-1, 0, 0, 0, 1, 1], target = 1", "four_sum(&[-1, 0, 0, 0, 1, 1], 1)", "vec![[-1, 0, 1, 1], [0, 0, 0, 1]]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(219);
            for _ in 0..300 {
                let n = rng.below(9);
                let nums: Vec<i32> = rng.vec(n, -4, 4);
                let target = rng.int(-6, 6);
                let mut want = std::collections::BTreeSet::new();
                for a in 0..n {
                    for b in a + 1..n {
                        for c in b + 1..n {
                            for d in c + 1..n {
                                if (nums[a] + nums[b] + nums[c] + nums[d]) as i64 == target {
                                    let mut q = [nums[a], nums[b], nums[c], nums[d]];
                                    q.sort();
                                    want.insert(q);
                                }
                            }
                        }
                    }
                }
                check!(format!("nums = {nums:?}, target = {target}"), four_sum(&nums, target), want.into_iter().collect::<Vec<_>>());
            }
        }

        #[test]
        fn scale_600() {
            // Every value is 1 more than a multiple of 4, so four of them sum to a multiple of 4 and never to 2.
            let mut rng = anneal_prelude::Rng::new(220);
            let mut nums: Vec<i32> = (0..600).map(|i| 4 * i - 1199).collect();
            rng.shuffle(&mut nums);
            check!("nums = 4i - 1199 for i in 0..600, shuffled, target = 2", four_sum(&nums, 2), Vec::<[i32; 4]>::new());
        }
        """,
    ],
    wrong=dict(
        quartic="""
            pub fn four_sum(nums: &[i32], target: i64) -> Vec<[i32; 4]> {
                let n = nums.len();
                let mut out = std::collections::BTreeSet::new();
                for a in 0..n {
                    for b in a + 1..n {
                        for c in b + 1..n {
                            for d in c + 1..n {
                                if nums[a] as i64 + nums[b] as i64 + nums[c] as i64 + nums[d] as i64 == target {
                                    let mut q = [nums[a], nums[b], nums[c], nums[d]];
                                    q.sort();
                                    out.insert(q);
                                }
                            }
                        }
                    }
                }
                out.into_iter().collect()
            }
        """,
        target_cast_to_i32="""
            pub fn four_sum(nums: &[i32], target: i64) -> Vec<[i32; 4]> {
                let mut v = nums.to_vec();
                v.sort_unstable();
                let n = v.len();
                let target = target as i32 as i64;
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
        no_second_level_dedup="""
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
    ),
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

# Companies known to ask each problem (names from COMPANIES in crates/content/src/model.rs).
COMPANIES = {
    "valid-palindrome": ["Meta", "Microsoft", "Amazon", "Apple", "Google", "Bloomberg"],
    "reverse-string": ["Amazon", "Apple", "Microsoft", "Adobe"],
    "merge-sorted-array": ["Meta", "Amazon", "Microsoft", "Apple", "Google", "Bloomberg"],
    "move-zeroes": ["Meta", "Amazon", "Apple", "Microsoft", "Google", "Bloomberg"],
    "two-sum-sorted": ["Amazon", "Google", "Microsoft", "Apple", "Adobe"],
    "three-sum": ["Meta", "Amazon", "Apple", "Google", "Microsoft", "Bloomberg", "Adobe"],
    "container-with-most-water": ["Amazon", "Google", "Meta", "Microsoft", "Apple", "Bloomberg", "Goldman Sachs"],
    "three-sum-closest": ["Meta", "Amazon", "Google", "Apple", "Bloomberg"],
    "best-time-to-buy-and-sell-stock": ["Amazon", "Meta", "Microsoft", "Google", "Apple", "Bloomberg", "Goldman Sachs", "Uber"],
    "longest-substring-without-repeating": ["Amazon", "Google", "Meta", "Microsoft", "Apple", "Bloomberg", "Adobe", "Uber"],
    "longest-repeating-character-replacement": ["Google", "Amazon", "Meta", "Microsoft", "Uber"],
    "permutation-in-string": ["Microsoft", "Amazon", "Google", "Meta", "Oracle"],
    "find-all-anagrams": ["Amazon", "Meta", "Microsoft", "Google", "Uber"],
    "minimum-window-substring": ["Meta", "Amazon", "Google", "LinkedIn", "Microsoft", "Apple", "Uber", "Airbnb"],
    "trapping-rain-water": ["Amazon", "Google", "Meta", "Microsoft", "Apple", "Bloomberg", "Goldman Sachs", "Uber"],
    "sliding-window-maximum": ["Amazon", "Google", "Microsoft", "Meta", "Apple", "Uber"],
    "four-sum": ["Amazon", "Apple", "Google", "Microsoft", "Bloomberg"],
}
tag_companies(P, COMPANIES)

if __name__ == "__main__":
    n = write_track("d2-two-pointers-windows", "D2", "Two pointers & sliding window", "D", "core", 2,
                    "Two indices over a slice, and windows that grow and shrink: O(n) answers to problems that look O(n²).",
                    STAGES, P)
    print("D2", n)
