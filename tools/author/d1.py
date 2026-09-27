from author import T, write_track

P = []

P.append(dict(
    slug="running-sum", title="Running sum", level="easy", stage="vec-and-slices", tags=["scan", "Vec"],
    teaches=["`iter().scan` carries state through an iterator chain.", "Borrow a slice in, return an owned `Vec` out."],
    statement="""
        Return the running sum of `nums`: element `i` of the result is `nums[0] + … + nums[i]`.
    """,
    examples=[("nums = [1, 2, 3, 4]", "[1, 3, 6, 10]")],
    constraints=["0 ≤ nums.len() ≤ 10⁴", "|nums[i]| ≤ 10⁴"],
    starter="""
        pub fn running_sum(nums: &[i32]) -> Vec<i32> {
            todo!()
        }
    """,
    solution="""
        pub fn running_sum(nums: &[i32]) -> Vec<i32> {
            nums.iter()
                .scan(0, |total, &x| {
                    *total += x;
                    Some(*total)
                })
                .collect()
        }
    """,
    visible=[
        T("four_numbers", "nums = [1, 2, 3, 4]", "running_sum(&[1, 2, 3, 4])", "vec![1, 3, 6, 10]"),
        T("empty", "nums = []", "running_sum(&[])", "Vec::<i32>::new()"),
        T("single", "nums = [5]", "running_sum(&[5])", "vec![5]"),
    ],
    hidden=[
        T("negatives", "nums = [3, -1, -2]", "running_sum(&[3, -1, -2])", "vec![3, 2, 0]"),
        T("ten_thousand_ones", "nums = [1; 10000]", "*running_sum(&[1; 10000]).last().unwrap()", "10000"),
    ],
    hints=[("approach", "Keep a total as you walk the slice and push it after each element."),
           ("rust", "`iter().scan(0, |total, &x| { *total += x; Some(*total) })` is that loop as an adapter.")],
    notes=("`scan` threads mutable state through the chain; `collect` builds the `Vec` with the right capacity because the length is known.", "O(n)", "O(n) for the output"),
    follow_up="How would you do this in place, and what would the signature need to change to?",
    related=["S6", "S3"],
))

P.append(dict(
    slug="concatenation-of-array", title="Concatenation of array", level="easy", stage="vec-and-slices", tags=["slices", "repeat"],
    teaches=["`slice::repeat` and `concat` build a new `Vec` from slices.", "`Vec::with_capacity` avoids regrowing when you know the size."],
    statement="Return `nums` followed by `nums` again, as one `Vec`.",
    examples=[("nums = [1, 2, 1]", "[1, 2, 1, 1, 2, 1]")],
    starter="""
        pub fn concat_twice(nums: &[i32]) -> Vec<i32> {
            todo!()
        }
    """,
    solution="""
        pub fn concat_twice(nums: &[i32]) -> Vec<i32> {
            nums.repeat(2)
        }
    """,
    visible=[
        T("three", "nums = [1, 2, 1]", "concat_twice(&[1, 2, 1])", "vec![1, 2, 1, 1, 2, 1]"),
        T("empty", "nums = []", "concat_twice(&[])", "Vec::<i32>::new()"),
    ],
    hidden=[
        T("one", "nums = [7]", "concat_twice(&[7])", "vec![7, 7]"),
        T("length", "nums = 0..1000", "concat_twice(&(0..1000).collect::<Vec<_>>()).len()", "2000"),
    ],
    hints=[("rust", "Slices have `repeat(n)`; `[a, b].concat()` and `extend_from_slice` work too.")],
    notes=("`nums.repeat(2)` allocates once with the final length.", "O(n)", "O(n)"),
    follow_up="What would change if the input were a `Vec<String>` instead of `&[i32]`?",
    related=["S3"],
))

P.append(dict(
    slug="two-sum", title="Two sum", level="easy", stage="vec-and-slices", tags=["HashMap", "Blind 75"],
    teaches=["One pass with a `HashMap` from value to index.", "`Option<(usize, usize)>` instead of a `[-1, -1]` sentinel."],
    statement="""
        Return the indices `(i, j)` with `i < j` of the two numbers in `nums` that add up to
        `target`, or `None` if no pair does. When a pair exists, exactly one does.
    """,
    examples=[("nums = [2, 7, 11, 15], target = 9", "Some((0, 1))")],
    constraints=["2 ≤ nums.len() ≤ 10⁴", "|nums[i]|, |target| ≤ 10⁹"],
    starter="""
        pub fn two_sum(nums: &[i32], target: i32) -> Option<(usize, usize)> {
            todo!()
        }
    """,
    solution="""
        use std::collections::HashMap;

        pub fn two_sum(nums: &[i32], target: i32) -> Option<(usize, usize)> {
            let mut seen: HashMap<i32, usize> = HashMap::with_capacity(nums.len());
            for (j, &x) in nums.iter().enumerate() {
                if let Some(&i) = seen.get(&(target - x)) {
                    return Some((i, j));
                }
                seen.insert(x, j);
            }
            None
        }
    """,
    visible=[
        T("first_two", "nums = [2, 7, 11, 15], target = 9", "two_sum(&[2, 7, 11, 15], 9)", "Some((0, 1))"),
        T("middle", "nums = [3, 2, 4], target = 6", "two_sum(&[3, 2, 4], 6)", "Some((1, 2))"),
        T("same_value_twice", "nums = [3, 3], target = 6", "two_sum(&[3, 3], 6)", "Some((0, 1))"),
        T("no_pair", "nums = [1, 2, 3], target = 7", "two_sum(&[1, 2, 3], 7)", "None"),
    ],
    hidden=[
        T("negatives", "nums = [-3, 4, 3, 90], target = 0", "two_sum(&[-3, 4, 3, 90], 0)", "Some((0, 2))"),
        T("large_input", "nums = 0..10000, target = 19997", "two_sum(&(0..10_000).collect::<Vec<i32>>(), 19_997)", "Some((9998, 9999))"),
    ],
    hints=[("approach", "For each number, the partner you need is `target - x`. Have you seen it already?"),
           ("rust", "Store value → index in a `HashMap<i32, usize>` and check before inserting, so an element never pairs with itself.")],
    notes=("Checking before inserting handles `[3, 3]` and never pairs an element with itself. Returning `Option` keeps the no-answer case in the type.", "O(n)", "O(n)"),
    follow_up="If the input were sorted, how would you do it in O(1) extra space?",
    related=["S4", "S1"],
))

P.append(dict(
    slug="contains-duplicate", title="Contains duplicate", level="easy", stage="vec-and-slices", tags=["HashSet", "Blind 75"],
    teaches=["`HashSet::insert` returns `false` when the value was already there.", "`any` stops at the first match."],
    statement="Return `true` if any value appears at least twice in `nums`.",
    examples=[("nums = [1, 2, 3, 1]", "true")],
    starter="""
        pub fn contains_duplicate(nums: &[i32]) -> bool {
            todo!()
        }
    """,
    solution="""
        use std::collections::HashSet;

        pub fn contains_duplicate(nums: &[i32]) -> bool {
            let mut seen = HashSet::with_capacity(nums.len());
            nums.iter().any(|x| !seen.insert(x))
        }
    """,
    visible=[
        T("has_duplicate", "nums = [1, 2, 3, 1]", "contains_duplicate(&[1, 2, 3, 1])", "true"),
        T("all_distinct", "nums = [1, 2, 3, 4]", "contains_duplicate(&[1, 2, 3, 4])", "false"),
        T("empty", "nums = []", "contains_duplicate(&[])", "false"),
    ],
    hidden=[
        T("many_repeats", "nums = [1, 1, 1, 3, 3, 4, 3, 2, 4, 2]", "contains_duplicate(&[1, 1, 1, 3, 3, 4, 3, 2, 4, 2])", "true"),
        T("large_distinct", "nums = 0..100000", "contains_duplicate(&(0..100_000).collect::<Vec<_>>())", "false"),
    ],
    hints=[("rust", "`HashSet::insert` tells you whether the value was new. Combine it with `any`.")],
    notes=("`any` short-circuits on the first repeat. Sorting a copy is O(n log n) with O(1) extra space if you may reorder the input.", "O(n)", "O(n)"),
    follow_up="How would you do it without extra memory if you're allowed to reorder `nums`?",
    related=["S4", "S6"],
))

P.append(dict(
    slug="valid-anagram", title="Valid anagram", level="easy", stage="vec-and-slices", tags=["[u8; 26]", "Blind 75"],
    teaches=["A fixed `[i32; 26]` beats a `HashMap` for a small alphabet.", "`bytes()` when input is ASCII."],
    statement="Return `true` if `t` is an anagram of `s`. Both contain only lowercase ASCII letters.",
    examples=[("s = \"anagram\", t = \"nagaram\"", "true")],
    starter="""
        pub fn is_anagram(s: &str, t: &str) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn is_anagram(s: &str, t: &str) -> bool {
            if s.len() != t.len() {
                return false;
            }
            let mut counts = [0i32; 26];
            for (a, b) in s.bytes().zip(t.bytes()) {
                counts[(a - b'a') as usize] += 1;
                counts[(b - b'a') as usize] -= 1;
            }
            counts.iter().all(|&c| c == 0)
        }
    """,
    visible=[
        T("anagram", "s = \"anagram\", t = \"nagaram\"", 'is_anagram("anagram", "nagaram")', "true"),
        T("not_anagram", "s = \"rat\", t = \"car\"", 'is_anagram("rat", "car")', "false"),
        T("different_lengths", "s = \"ab\", t = \"a\"", 'is_anagram("ab", "a")', "false"),
    ],
    hidden=[
        T("empty", "s = \"\", t = \"\"", 'is_anagram("", "")', "true"),
        T("same_letters_different_counts", "s = \"aab\", t = \"abb\"", 'is_anagram("aab", "abb")', "false"),
    ],
    hints=[("approach", "Count each letter up for `s` and down for `t`; every count ends at zero for an anagram."),
           ("rust", "Index a `[i32; 26]` with `(byte - b'a') as usize`.")],
    notes=("The length check makes the zip safe to use for both strings. A 26-slot array is cache-friendly and needs no hashing.", "O(n)", "O(1)"),
    follow_up="What changes if the input can contain any Unicode text?",
    related=["S2", "S4"],
))

P.append(dict(
    slug="fix-panicking-index", title="Fix: a panicking index", mode="fix", level="easy", stage="vec-and-slices", tags=["get()", "panic"],
    teaches=["`v[i]` panics out of bounds; `v.get(i)` returns an `Option`.", "`copied()` turns `Option<&i32>` into `Option<i32>`."],
    statement="""
        `nth_or_zero` should return the element at `i`, or 0 when `i` is past the end.
        It panics instead.
    """,
    starter="""
        /// The element at `i`, or 0 when `i` is past the end.
        pub fn nth_or_zero(v: &[i32], i: usize) -> i32 {
            v[i]
        }
    """,
    solution="""
        /// The element at `i`, or 0 when `i` is past the end.
        pub fn nth_or_zero(v: &[i32], i: usize) -> i32 {
            v.get(i).copied().unwrap_or(0)
        }
    """,
    rules=dict(lines=1),
    visible=[
        T("in_range", "v = [4, 5, 6], i = 1", "nth_or_zero(&[4, 5, 6], 1)", "5"),
        T("past_the_end", "v = [4, 5, 6], i = 3", "nth_or_zero(&[4, 5, 6], 3)", "0"),
    ],
    hidden=[
        T("empty", "v = [], i = 0", "nth_or_zero(&[], 0)", "0"),
        T("huge_index", "v = [1], i = usize::MAX", "nth_or_zero(&[1], usize::MAX)", "0"),
    ],
    hints=[("rust", "Slices have a non-panicking lookup that returns `Option<&T>`.")],
    notes=("`get` returns `None` past the end; `copied` and `unwrap_or` turn that into the default without a branch.", "O(1)", "O(1)"),
    follow_up="When is a panic on a bad index the right behaviour, and when isn't it?",
    related=["S1", "S3"],
))

P.append(dict(
    slug="majority-element", title="Majority element", level="easy", stage="counting", tags=["counting", "Boyer–Moore"],
    teaches=["Counting with a map, then the O(1)-space voting trick.", "Iterator `fold` for a two-field state."],
    statement="`nums` has a value that appears more than `nums.len() / 2` times. Return it.",
    examples=[("nums = [2, 2, 1, 1, 1, 2, 2]", "2")],
    starter="""
        pub fn majority(nums: &[i32]) -> i32 {
            todo!()
        }
    """,
    solution="""
        /// Boyer–Moore voting: the majority survives pairing off against everything else.
        pub fn majority(nums: &[i32]) -> i32 {
            nums.iter()
                .fold((0, 0), |(candidate, count), &x| match count {
                    0 => (x, 1),
                    _ if x == candidate => (candidate, count + 1),
                    _ => (candidate, count - 1),
                })
                .0
        }
    """,
    visible=[
        T("small", "nums = [3, 2, 3]", "majority(&[3, 2, 3])", "3"),
        T("longer", "nums = [2, 2, 1, 1, 1, 2, 2]", "majority(&[2, 2, 1, 1, 1, 2, 2])", "2"),
    ],
    hidden=[
        T("single", "nums = [9]", "majority(&[9])", "9"),
        T("negative_majority", "nums = [-1, 5, -1, -1, 6]", "majority(&[-1, 5, -1, -1, 6])", "-1"),
    ],
    hints=[("approach", "A `HashMap` of counts works. Can you do it with two variables?"),
           ("approach", "Pair each majority element off against a different one; the majority is left over.")],
    notes=("Boyer–Moore keeps one candidate and a count. Because the majority appears more than half the time, it can't be fully cancelled.", "O(n)", "O(1)"),
    follow_up="How would you find every value that appears more than n/3 times?",
    related=["S6", "S4"],
))

P.append(dict(
    slug="ransom-note", title="Ransom note", level="easy", stage="counting", tags=["counting", "[u8; 26]"],
    teaches=["Count what you have, then spend it.", "Early return from a loop once a count goes negative."],
    statement="Return `true` if `note` can be built from the letters of `magazine`, using each letter once. Both are lowercase ASCII.",
    examples=[("note = \"aa\", magazine = \"aab\"", "true")],
    starter="""
        pub fn can_construct(note: &str, magazine: &str) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn can_construct(note: &str, magazine: &str) -> bool {
            let mut have = [0u32; 26];
            for b in magazine.bytes() {
                have[(b - b'a') as usize] += 1;
            }
            for b in note.bytes() {
                let slot = &mut have[(b - b'a') as usize];
                if *slot == 0 {
                    return false;
                }
                *slot -= 1;
            }
            true
        }
    """,
    visible=[
        T("enough", "note = \"aa\", magazine = \"aab\"", 'can_construct("aa", "aab")', "true"),
        T("not_enough", "note = \"aa\", magazine = \"ab\"", 'can_construct("aa", "ab")', "false"),
    ],
    hidden=[
        T("empty_note", "note = \"\", magazine = \"\"", 'can_construct("", "")', "true"),
        T("missing_letter", "note = \"z\", magazine = \"abc\"", 'can_construct("z", "abc")', "false"),
    ],
    hints=[("approach", "Count the magazine's letters, then take one away for each letter of the note.")],
    notes=("Checking for zero before decrementing avoids unsigned underflow and exits early.", "O(n + m)", "O(1)"),
    follow_up="If this ran for many notes against one magazine, what would you precompute?",
    related=["S4"],
))

P.append(dict(
    slug="isomorphic-strings", title="Isomorphic strings", level="easy", stage="counting", tags=["HashMap", "bytes"],
    teaches=["A mapping must be one-to-one both ways, so check both directions.", "`[Option<u8>; 256]` as a byte-to-byte map."],
    statement="""
        Two strings are isomorphic if the characters of `s` can be replaced to get `t`, where
        each character maps to exactly one character and no two characters map to the same one.
        Both are ASCII and the same length.
    """,
    examples=[("s = \"egg\", t = \"add\"", "true"), ("s = \"foo\", t = \"bar\"", "false")],
    starter="""
        pub fn is_isomorphic(s: &str, t: &str) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn is_isomorphic(s: &str, t: &str) -> bool {
            let mut forward: [Option<u8>; 256] = [None; 256];
            let mut backward: [Option<u8>; 256] = [None; 256];
            for (a, b) in s.bytes().zip(t.bytes()) {
                match (forward[a as usize], backward[b as usize]) {
                    (None, None) => {
                        forward[a as usize] = Some(b);
                        backward[b as usize] = Some(a);
                    }
                    (Some(x), Some(y)) if x == b && y == a => {}
                    _ => return false,
                }
            }
            true
        }
    """,
    visible=[
        T("egg_add", "s = \"egg\", t = \"add\"", 'is_isomorphic("egg", "add")', "true"),
        T("foo_bar", "s = \"foo\", t = \"bar\"", 'is_isomorphic("foo", "bar")', "false"),
        T("paper_title", "s = \"paper\", t = \"title\"", 'is_isomorphic("paper", "title")', "true"),
    ],
    hidden=[
        T("two_to_one", "s = \"ab\", t = \"aa\"", 'is_isomorphic("ab", "aa")', "false"),
        T("badc_baba", "s = \"badc\", t = \"baba\"", 'is_isomorphic("badc", "baba")', "false"),
    ],
    hints=[("approach", "Record s→t and t→s. A clash in either direction means no."),
           ("rust", "Bytes index a `[Option<u8>; 256]` directly; no hashing needed.")],
    notes=("One map alone misses `ab` → `aa`, where two letters map to the same one. The reverse map catches it.", "O(n)", "O(1)"),
    follow_up="How would you group a list of words into isomorphism classes?",
    related=["S4", "S2"],
))

P.append(dict(
    slug="fix-double-lookup", title="Fix: count with the entry API", mode="fix", level="easy", stage="counting", tags=["HashMap::entry", "counting"],
    teaches=["`entry(k).or_insert(0)` finds or creates the slot in one lookup.", "Why `contains_key` then `get_mut` hashes the key twice."],
    statement="""
        `word_counts` works, but it hashes each word two or three times and unwraps.
        Rewrite the loop body so each word is looked up once.
    """,
    starter="""
        use std::collections::HashMap;

        /// How many times each word appears.
        pub fn word_counts(text: &str) -> HashMap<&str, usize> {
            let mut counts = HashMap::new();
            for word in text.split_whitespace() {
                if counts.contains_key(word) {
                    *counts.get_mut(word).unwrap() += 1;
                } else {
                    counts.insert(word, 1);
                }
            }
            counts
        }
    """,
    solution="""
        use std::collections::HashMap;

        /// How many times each word appears.
        pub fn word_counts(text: &str) -> HashMap<&str, usize> {
            let mut counts = HashMap::new();
            for word in text.split_whitespace() {
                *counts.entry(word).or_insert(0) += 1;
            }
            counts
        }
    """,
    rules=dict(methods=["contains_key", "get_mut", "unwrap"]),
    visible=[
        T("repeats", "text = \"a b a c a\"", 'word_counts("a b a c a")', 'std::collections::HashMap::from([("a", 3), ("b", 1), ("c", 1)])'),
        T("empty", "text = \"\"", 'word_counts("")', "std::collections::HashMap::new()"),
    ],
    hidden=[
        T("whitespace", "text = \"  x\\n x\\tx  \"", 'word_counts("  x\\n x\\tx  ")', 'std::collections::HashMap::from([("x", 3)])'),
    ],
    hints=[("rust", "`counts.entry(word)` gives you the slot whether or not it exists yet.")],
    notes=("`entry` hashes once and returns either the existing value or a vacant slot to fill; `or_insert(0)` then yields `&mut usize`.", "O(n)", "O(k) distinct words"),
    follow_up="When would you use `or_insert_with` or `and_modify` instead?",
    related=["S4", "L2"],
))

P.append(dict(
    slug="group-anagrams", title="Group anagrams", level="medium", stage="grouping-prefix-sums", tags=["HashMap", "sort", "Blind 75"],
    teaches=["A sorted `Vec<u8>` of letters is a hashable key for an anagram class.", "`entry(key).or_default().push(..)`."],
    statement="""
        Group the words that are anagrams of each other. Return the groups with each group's
        words sorted, and the groups sorted by their first word.
    """,
    examples=[("[\"eat\", \"tea\", \"tan\", \"ate\", \"nat\", \"bat\"]", "[[\"ate\", \"eat\", \"tea\"], [\"bat\"], [\"nat\", \"tan\"]]")],
    starter="""
        pub fn group_anagrams(words: &[&str]) -> Vec<Vec<String>> {
            todo!()
        }
    """,
    solution="""
        use std::collections::HashMap;

        pub fn group_anagrams(words: &[&str]) -> Vec<Vec<String>> {
            let mut groups: HashMap<Vec<u8>, Vec<String>> = HashMap::new();
            for &w in words {
                let mut key = w.as_bytes().to_vec();
                key.sort_unstable();
                groups.entry(key).or_default().push(w.to_string());
            }
            let mut out: Vec<Vec<String>> = groups.into_values().collect();
            for g in &mut out {
                g.sort();
            }
            out.sort();
            out
        }
    """,
    visible=[
        T("classic", "[\"eat\", \"tea\", \"tan\", \"ate\", \"nat\", \"bat\"]", 'group_anagrams(&["eat", "tea", "tan", "ate", "nat", "bat"])', 'vec![vec!["ate", "eat", "tea"], vec!["bat"], vec!["nat", "tan"]]'),
        T("empty_string", "[\"\"]", 'group_anagrams(&[""])', 'vec![vec![""]]'),
    ],
    hidden=[
        T("no_words", "[]", "group_anagrams(&[])", "Vec::<Vec<String>>::new()"),
        T("duplicates", "[\"ab\", \"ba\", \"ab\"]", 'group_anagrams(&["ab", "ba", "ab"])', 'vec![vec!["ab", "ab", "ba"]]'),
    ],
    hints=[("approach", "Anagrams have the same letters in sorted order. Use that as a map key."),
           ("rust", "`Vec<u8>` is `Hash + Eq`, so it can key a `HashMap` directly.")],
    notes=("Sorting each word costs O(k log k); a `[u8; 26]` count array is another valid key and avoids the sort.", "O(n · k log k)", "O(n · k)"),
    follow_up="How would you key the map without sorting each word?",
    related=["S4", "S3"],
))

P.append(dict(
    slug="top-k-frequent", title="Top K frequent elements", level="medium", stage="grouping-prefix-sums", tags=["HashMap", "sort_by", "Blind 75"],
    source="W32",
    teaches=["Count, then sort by a composite key with `then`.", "`Ordering::reverse` for descending order."],
    statement="""
        Return the `k` most frequent values in `nums`, most frequent first. Break ties by the
        smaller value first. `k` is at most the number of distinct values.
    """,
    examples=[("nums = [1, 1, 1, 2, 2, 3], k = 2", "[1, 2]")],
    starter="""
        pub fn top_k_frequent(nums: &[i32], k: usize) -> Vec<i32> {
            todo!()
        }
    """,
    solution="""
        use std::collections::HashMap;

        pub fn top_k_frequent(nums: &[i32], k: usize) -> Vec<i32> {
            let mut counts: HashMap<i32, usize> = HashMap::new();
            for &x in nums {
                *counts.entry(x).or_insert(0) += 1;
            }
            let mut by_count: Vec<(i32, usize)> = counts.into_iter().collect();
            by_count.sort_unstable_by(|a, b| b.1.cmp(&a.1).then(a.0.cmp(&b.0)));
            by_count.into_iter().take(k).map(|(x, _)| x).collect()
        }
    """,
    visible=[
        T("two_most", "nums = [1, 1, 1, 2, 2, 3], k = 2", "top_k_frequent(&[1, 1, 1, 2, 2, 3], 2)", "vec![1, 2]"),
        T("single", "nums = [1], k = 1", "top_k_frequent(&[1], 1)", "vec![1]"),
        T("ties_by_value", "nums = [4, 4, 1, 1, 7], k = 2", "top_k_frequent(&[4, 4, 1, 1, 7], 2)", "vec![1, 4]"),
    ],
    hidden=[
        T("all_distinct", "nums = [5, 3, 9], k = 3", "top_k_frequent(&[5, 3, 9], 3)", "vec![3, 5, 9]"),
        T("negatives", "nums = [-1, -1, 2, -1, 2, 3], k = 1", "top_k_frequent(&[-1, -1, 2, -1, 2, 3], 1)", "vec![-1]"),
    ],
    hints=[("approach", "Count first. Then you need the k largest counts."),
           ("rust", "Sort `(value, count)` pairs with `b.1.cmp(&a.1).then(a.0.cmp(&b.0))`."),
           ("edge case", "Ties need a rule, or the answer isn't deterministic; here the smaller value wins.")],
    notes=("Sorting all distinct values is O(d log d). A size-k `BinaryHeap<Reverse<_>>` or bucket sort by count gets closer to O(n).", "O(n + d log d)", "O(d)"),
    follow_up="How would you get O(n) with bucket sort, and when is a heap better?",
    related=["S4", "S5"],
))

P.append(dict(
    slug="product-except-self", title="Product of array except self", level="medium", stage="grouping-prefix-sums", tags=["prefix products", "Blind 75"],
    teaches=["Prefix and suffix passes over the same output buffer.", "`iter().rev()` with an index for the backward pass."],
    statement="Return `out` where `out[i]` is the product of every element except `nums[i]`, without using division.",
    examples=[("nums = [1, 2, 3, 4]", "[24, 12, 8, 6]")],
    constraints=["2 ≤ nums.len() ≤ 10⁵", "every product fits in i32"],
    starter="""
        pub fn product_except_self(nums: &[i32]) -> Vec<i32> {
            todo!()
        }
    """,
    solution="""
        pub fn product_except_self(nums: &[i32]) -> Vec<i32> {
            let n = nums.len();
            let mut out = vec![1; n];
            let mut prefix = 1;
            for i in 0..n {
                out[i] = prefix;
                prefix *= nums[i];
            }
            let mut suffix = 1;
            for i in (0..n).rev() {
                out[i] *= suffix;
                suffix *= nums[i];
            }
            out
        }
    """,
    visible=[
        T("four", "nums = [1, 2, 3, 4]", "product_except_self(&[1, 2, 3, 4])", "vec![24, 12, 8, 6]"),
        T("with_zero", "nums = [-1, 1, 0, -3, 3]", "product_except_self(&[-1, 1, 0, -3, 3])", "vec![0, 0, 9, 0, 0]"),
    ],
    hidden=[
        T("two_zeros", "nums = [0, 4, 0]", "product_except_self(&[0, 4, 0])", "vec![0, 0, 0]"),
        T("pair", "nums = [3, 5]", "product_except_self(&[3, 5])", "vec![5, 3]"),
    ],
    hints=[("approach", "out[i] = (product of everything left of i) × (product of everything right of i)."),
           ("approach", "Fill `out` with the left products in one pass, then multiply in the right products walking backwards.")],
    notes=("Two passes, one running product each. Division would fail on zeros anyway.", "O(n)", "O(1) beyond the output"),
    follow_up="What breaks if the products can overflow i32, and what would you return instead?",
    related=["S6"],
))

P.append(dict(
    slug="subarray-sum-equals-k", title="Subarray sum equals K", level="medium", stage="grouping-prefix-sums", tags=["prefix sums", "HashMap"],
    teaches=["A subarray sum is a difference of two prefix sums.", "Count prefix sums in a `HashMap<i64, usize>`, widening to avoid overflow."],
    statement="Return how many contiguous, non-empty subarrays of `nums` sum to `k`.",
    examples=[("nums = [1, 1, 1], k = 2", "2")],
    constraints=["1 ≤ nums.len() ≤ 2·10⁴", "|nums[i]| ≤ 1000"],
    starter="""
        pub fn subarray_sum(nums: &[i32], k: i32) -> usize {
            todo!()
        }
    """,
    solution="""
        use std::collections::HashMap;

        pub fn subarray_sum(nums: &[i32], k: i32) -> usize {
            let mut seen: HashMap<i64, usize> = HashMap::from([(0, 1)]);
            let (mut sum, mut count) = (0i64, 0usize);
            for &x in nums {
                sum += x as i64;
                count += seen.get(&(sum - k as i64)).copied().unwrap_or(0);
                *seen.entry(sum).or_insert(0) += 1;
            }
            count
        }
    """,
    visible=[
        T("ones", "nums = [1, 1, 1], k = 2", "subarray_sum(&[1, 1, 1], 2)", "2"),
        T("mixed", "nums = [1, 2, 3], k = 3", "subarray_sum(&[1, 2, 3], 3)", "2"),
        T("negatives", "nums = [1, -1, 0], k = 0", "subarray_sum(&[1, -1, 0], 0)", "3"),
    ],
    hidden=[
        T("none", "nums = [5, 5], k = 3", "subarray_sum(&[5, 5], 3)", "0"),
        T("all_zero", "nums = [0; 100], k = 0", "subarray_sum(&[0; 100], 0)", "5050"),
    ],
    hints=[("approach", "sum(i..j) = prefix[j] − prefix[i]. For each prefix, how many earlier prefixes equal prefix − k?"),
           ("rust", "Seed the map with `(0, 1)` so subarrays that start at index 0 count.")],
    notes=("The map counts how many earlier prefixes had each sum. Negative numbers rule out a sliding window, which is why this needs prefix sums.", "O(n)", "O(n)"),
    follow_up="Why doesn't a sliding window work here when it does for positive-only inputs?",
    related=["S4"],
))

P.append(dict(
    slug="encode-decode-strings", title="Encode and decode strings", level="medium", stage="grouping-prefix-sums", tags=["String", "framing", "Blind 75"],
    teaches=["Length-prefix framing survives any content, including the delimiter.", "Slicing a `&str` by byte offsets that fall on char boundaries."],
    statement="""
        Write `encode`, which turns a list of strings into one `String`, and `decode`, which turns
        it back into the same list. Any character may appear in the strings, including digits and `#`.
    """,
    starter="""
        pub fn encode(words: &[&str]) -> String {
            todo!()
        }

        pub fn decode(s: &str) -> Vec<String> {
            todo!()
        }
    """,
    solution="""
        /// Each word as `<byte length>#<word>`.
        pub fn encode(words: &[&str]) -> String {
            let mut out = String::new();
            for w in words {
                out.push_str(&w.len().to_string());
                out.push('#');
                out.push_str(w);
            }
            out
        }

        pub fn decode(s: &str) -> Vec<String> {
            let mut out = Vec::new();
            let mut rest = s;
            while let Some(hash) = rest.find('#') {
                let len: usize = rest[..hash].parse().expect("length prefix");
                let start = hash + 1;
                out.push(rest[start..start + len].to_string());
                rest = &rest[start + len..];
            }
            out
        }
    """,
    visible=[
        T("round_trip", "[\"lint\", \"code\", \"love\", \"you\"]", 'decode(&encode(&["lint", "code", "love", "you"]))', 'vec!["lint", "code", "love", "you"]'),
        T("delimiters_inside", "[\"a#b\", \"12#\", \"#\"]", 'decode(&encode(&["a#b", "12#", "#"]))', 'vec!["a#b", "12#", "#"]'),
        T("empty_strings", "[\"\", \"\"]", 'decode(&encode(&["", ""]))', 'vec!["", ""]'),
    ],
    hidden=[
        T("no_words", "[]", "decode(&encode(&[]))", "Vec::<String>::new()"),
        T("unicode", "[\"héllo\", \"🦀#rust\"]", 'decode(&encode(&["héllo", "🦀#rust"]))', 'vec!["héllo", "🦀#rust"]'),
    ],
    hints=[("approach", "A delimiter alone fails when words contain it. Prefix each word with its length."),
           ("rust", "Use byte lengths (`str::len`) and byte slicing; whole words always start and end on char boundaries.")],
    notes=("The length tells `decode` exactly how many bytes to take, so the content can contain anything.", "O(total length)", "O(total length)"),
    follow_up="How would you frame binary data on a TCP stream the same way?",
    related=["S2", "B4"],
))

P.append(dict(
    slug="fix-prefix-sum-overflow", title="Fix: overflow in prefix sums", mode="fix", level="medium", stage="grouping-prefix-sums", tags=["i64", "overflow"],
    source="B5",
    teaches=["Integer overflow panics in debug builds and wraps silently in release.", "Widen the accumulator, not each result."],
    statement="""
        `max_prefix_sum` returns the largest sum of a non-empty prefix of `nums`, or `None` for an
        empty slice. It panics on large inputs in tests, and would silently return wrong answers in a
        release build.
    """,
    starter="""
        /// The largest sum of `nums[..k]` over k ≥ 1.
        pub fn max_prefix_sum(nums: &[i32]) -> Option<i64> {
            let mut sum: i32 = 0;
            let mut best: Option<i64> = None;
            for &x in nums {
                sum += x;
                best = Some(best.map_or(sum as i64, |b| b.max(sum as i64)));
            }
            best
        }
    """,
    solution="""
        /// The largest sum of `nums[..k]` over k ≥ 1.
        pub fn max_prefix_sum(nums: &[i32]) -> Option<i64> {
            let mut sum: i64 = 0;
            let mut best: Option<i64> = None;
            for &x in nums {
                sum += i64::from(x);
                best = Some(best.map_or(sum, |b| b.max(sum)));
            }
            best
        }
    """,
    rules=dict(lines=3),
    visible=[
        T("small", "nums = [1, -2, 3]", "max_prefix_sum(&[1, -2, 3])", "Some(2)"),
        T("empty", "nums = []", "max_prefix_sum(&[])", "None"),
        T("past_i32_max", "nums = [i32::MAX, 1]", "max_prefix_sum(&[i32::MAX, 1])", "Some(2_147_483_648)"),
    ],
    hidden=[
        T("many_large", "nums = [2_000_000_000; 4]", "max_prefix_sum(&[2_000_000_000; 4])", "Some(8_000_000_000)"),
        T("all_negative", "nums = [-5, -1]", "max_prefix_sum(&[-5, -1])", "Some(-5)"),
    ],
    hints=[("rust", "The accumulator overflows, not the result. What type should `sum` be?"),
           ("rust", "`i64::from(x)` widens losslessly; `as` would also work here.")],
    notes=("Debug builds check arithmetic and panic; release builds wrap. Widening the accumulator fixes both.", "O(n)", "O(1)"),
    follow_up="When would you reach for `checked_add`, `wrapping_add` or `saturating_add` instead?",
    related=["S1", "Y1"],
))

P.append(dict(
    slug="sort-colors", title="Sort colors", level="medium", stage="sorting-order", tags=["Dutch flag", "swap"],
    teaches=["Three-way partitioning in one pass with `swap`.", "Why `mid` doesn't advance after swapping with `high`."],
    statement="Sort `nums`, which contains only 0, 1 and 2, in place and in one pass, without calling a sort function.",
    examples=[("nums = [2, 0, 2, 1, 1, 0]", "[0, 0, 1, 1, 2, 2]")],
    starter="""
        pub fn sort_colors(nums: &mut [u8]) {
            todo!()
        }
    """,
    solution="""
        /// Dutch national flag: [0, low) are 0s, [low, mid) are 1s, (high, end] are 2s.
        pub fn sort_colors(nums: &mut [u8]) {
            let (mut low, mut mid, mut high) = (0, 0, nums.len());
            while mid < high {
                match nums[mid] {
                    0 => {
                        nums.swap(low, mid);
                        low += 1;
                        mid += 1;
                    }
                    1 => mid += 1,
                    _ => {
                        high -= 1;
                        nums.swap(mid, high);
                    }
                }
            }
        }
    """,
    visible=[
        T("mixed", "nums = [2, 0, 2, 1, 1, 0]", "{ let mut v = vec![2, 0, 2, 1, 1, 0]; sort_colors(&mut v); v }", "vec![0, 0, 1, 1, 2, 2]"),
        T("three", "nums = [2, 0, 1]", "{ let mut v = vec![2, 0, 1]; sort_colors(&mut v); v }", "vec![0, 1, 2]"),
    ],
    hidden=[
        T("empty", "nums = []", "{ let mut v: Vec<u8> = vec![]; sort_colors(&mut v); v }", "Vec::<u8>::new()"),
        T("all_twos", "nums = [2, 2, 2]", "{ let mut v = vec![2, 2, 2]; sort_colors(&mut v); v }", "vec![2, 2, 2]"),
        T("long", "nums = [2, 1, 0] × 1000", "{ let mut v: Vec<u8> = [2, 1, 0].repeat(1000); sort_colors(&mut v); (v[999], v[1000], v[2000], v[2999]) }", "(0, 1, 2, 2)"),
    ],
    hints=[("approach", "Keep three regions: 0s at the front, 2s at the back, 1s in the middle."),
           ("edge case", "After swapping with the back, the value you swapped in hasn't been looked at yet.")],
    notes=("An exclusive `high` bound avoids underflow on empty input. Counting and rewriting is two passes; this is one.", "O(n)", "O(1)"),
    follow_up="How does this partition relate to quicksort with many equal keys?",
    related=["S3"],
))

P.append(dict(
    slug="largest-number", title="Largest number", level="medium", stage="sorting-order", tags=["sort_by", "String"],
    teaches=["A custom comparator: compare `a + b` with `b + a`.", "Edge case: all zeros."],
    statement="Arrange the numbers to form the largest possible number and return it as a string.",
    examples=[("nums = [3, 30, 34, 5, 9]", "\"9534330\"")],
    starter="""
        pub fn largest_number(nums: &[u32]) -> String {
            todo!()
        }
    """,
    solution="""
        pub fn largest_number(nums: &[u32]) -> String {
            let mut parts: Vec<String> = nums.iter().map(u32::to_string).collect();
            parts.sort_unstable_by(|a, b| (b.clone() + a).cmp(&(a.clone() + b)));
            if parts.first().is_some_and(|p| p == "0") {
                return "0".into();
            }
            parts.concat()
        }
    """,
    visible=[
        T("two", "nums = [10, 2]", "largest_number(&[10, 2])", '"210"'),
        T("five", "nums = [3, 30, 34, 5, 9]", "largest_number(&[3, 30, 34, 5, 9])", '"9534330"'),
    ],
    hidden=[
        T("zeros", "nums = [0, 0]", "largest_number(&[0, 0])", '"0"'),
        T("shared_prefix", "nums = [121, 12]", "largest_number(&[121, 12])", '"12121"'),
    ],
    hints=[("approach", "For two numbers a and b, put a first if the string ab is larger than ba."),
           ("edge case", "What does `[0, 0]` return?")],
    notes=("The comparator is transitive, so a sort works. Leading zeros only happen when every number is 0.", "O(n log n · d)", "O(n · d)"),
    follow_up="Why is the `a + b` versus `b + a` order transitive?",
    related=["S2", "S8"],
))

P.append(dict(
    slug="kth-largest", title="Kth largest element", level="medium", stage="sorting-order", tags=["select_nth_unstable", "quickselect"],
    teaches=["`select_nth_unstable` is quickselect in std: O(n) on average.", "Converting 'kth largest' to an ascending index."],
    statement="Return the `k`th largest value in `nums` (1-based). You may reorder `nums`.",
    examples=[("nums = [3, 2, 1, 5, 6, 4], k = 2", "5")],
    starter="""
        pub fn kth_largest(nums: &mut [i32], k: usize) -> i32 {
            todo!()
        }
    """,
    solution="""
        pub fn kth_largest(nums: &mut [i32], k: usize) -> i32 {
            let idx = nums.len() - k;
            *nums.select_nth_unstable(idx).1
        }
    """,
    visible=[
        T("second", "nums = [3, 2, 1, 5, 6, 4], k = 2", "kth_largest(&mut [3, 2, 1, 5, 6, 4], 2)", "5"),
        T("with_duplicates", "nums = [3, 2, 3, 1, 2, 4, 5, 5, 6], k = 4", "kth_largest(&mut [3, 2, 3, 1, 2, 4, 5, 5, 6], 4)", "4"),
    ],
    hidden=[
        T("largest", "nums = [7, -1], k = 1", "kth_largest(&mut [7, -1], 1)", "7"),
        T("smallest", "nums = 0..1000, k = 1000", "kth_largest(&mut (0..1000).collect::<Vec<_>>(), 1000)", "0"),
    ],
    hints=[("approach", "The kth largest is at ascending index n − k."),
           ("rust", "Slices have a partial sort that puts one element in its final position.")],
    notes=("`select_nth_unstable` partitions around the target index in O(n) average time. A size-k min-heap also works in O(n log k).", "O(n) average", "O(1)"),
    follow_up="When would you prefer a heap over quickselect?",
    related=["S3", "S5"],
))

P.append(dict(
    slug="longest-consecutive", title="Longest consecutive sequence", level="medium", stage="sorting-order", tags=["HashSet", "Blind 75"],
    teaches=["Only start counting from a number with no predecessor.", "A `HashSet` gives O(n) where sorting gives O(n log n)."],
    statement="Return the length of the longest run of consecutive integers in `nums`, in any order, in O(n) time.",
    examples=[("nums = [100, 4, 200, 1, 3, 2]", "4")],
    starter="""
        pub fn longest_consecutive(nums: &[i32]) -> usize {
            todo!()
        }
    """,
    solution="""
        use std::collections::HashSet;

        pub fn longest_consecutive(nums: &[i32]) -> usize {
            let set: HashSet<i32> = nums.iter().copied().collect();
            let mut best = 0;
            for &x in &set {
                if x != i32::MIN && set.contains(&(x - 1)) {
                    continue;
                }
                let mut len = 1;
                let mut y = x;
                while y != i32::MAX && set.contains(&(y + 1)) {
                    y += 1;
                    len += 1;
                }
                best = best.max(len);
            }
            best
        }
    """,
    visible=[
        T("four", "nums = [100, 4, 200, 1, 3, 2]", "longest_consecutive(&[100, 4, 200, 1, 3, 2])", "4"),
        T("nine", "nums = [0, 3, 7, 2, 5, 8, 4, 6, 0, 1]", "longest_consecutive(&[0, 3, 7, 2, 5, 8, 4, 6, 0, 1])", "9"),
        T("empty", "nums = []", "longest_consecutive(&[])", "0"),
    ],
    hidden=[
        T("extremes", "nums = [i32::MAX, i32::MIN, i32::MAX - 1]", "longest_consecutive(&[i32::MAX, i32::MIN, i32::MAX - 1])", "2"),
        T("large_run", "nums = (0..100000).rev()", "longest_consecutive(&(0..100_000).rev().collect::<Vec<_>>())", "100000"),
    ],
    hints=[("approach", "Put everything in a set. A run starts at x only if x − 1 isn't in the set."),
           ("edge case", "`x - 1` overflows at `i32::MIN` in a debug build.")],
    notes=("Each number is visited by at most one run, so the inner loop is O(n) in total. Guarding `i32::MIN`/`MAX` avoids overflow panics.", "O(n)", "O(n)"),
    follow_up="How would you solve it with union-find, and what would that buy you?",
    related=["S4", "D9"],
))

P.append(dict(
    slug="fix-sort-floats", title="Fix: sort a Vec<f64>", mode="fix", level="medium", stage="sorting-order", tags=["total_cmp", "Ord", "E0277"],
    teaches=["`f64` is `PartialOrd`, not `Ord`, because of NaN.", "`f64::total_cmp` gives a total order, NaN included."],
    statement="`sort_readings` should sort ascending, with NaN readings at the end. It doesn't compile.",
    starter="""
        /// Sorts readings ascending. NaN readings go last.
        pub fn sort_readings(readings: &mut Vec<f64>) {
            readings.sort();
        }
    """,
    solution="""
        /// Sorts readings ascending. NaN readings go last.
        pub fn sort_readings(readings: &mut Vec<f64>) {
            readings.sort_by(|a, b| a.total_cmp(b));
        }
    """,
    rules=dict(methods=["unwrap", "partial_cmp", "expect"], lines=1),
    visible=[
        T("plain", "[2.5, -1.0, 1.0]", '{ let mut v = vec![2.5, -1.0, 1.0]; sort_readings(&mut v); v.iter().map(|x| x.to_string()).collect::<Vec<_>>() }', 'vec!["-1", "1", "2.5"]'),
        T("nan_goes_last", "[3.0, NaN, 1.0]", '{ let mut v = vec![3.0, f64::NAN, 1.0]; sort_readings(&mut v); v.iter().map(|x| x.to_string()).collect::<Vec<_>>() }', 'vec!["1", "3", "NaN"]'),
    ],
    hidden=[
        T("infinities", "[inf, -inf, 0.0]", '{ let mut v = vec![f64::INFINITY, f64::NEG_INFINITY, 0.0]; sort_readings(&mut v); v.iter().map(|x| x.to_string()).collect::<Vec<_>>() }', 'vec!["-inf", "0", "inf"]'),
    ],
    hints=[("rust", "`sort` needs `Ord`. Why doesn't `f64` implement it?"),
           ("rust", "`partial_cmp(..).unwrap()` panics on NaN. `f64` has a method that orders every value.")],
    notes=("`total_cmp` follows IEEE 754 totalOrder: −NaN < −∞ < … < +∞ < +NaN, so NaN (positive by default) sorts last.", "O(n log n)", "O(n)"),
    follow_up="How would you use f64 as a key in a BinaryHeap or BTreeMap?",
    related=["S8", "S5"],
))

P.append(dict(
    slug="first-missing-positive", title="First missing positive", level="hard", stage="in-place", tags=["in place", "swap"],
    teaches=["Use the array itself as the hash: put value v at index v − 1.", "`swap` in a `while` until the slot is right."],
    statement="Return the smallest positive integer missing from `nums`, in O(n) time and O(1) extra space. You may reorder `nums`.",
    examples=[("nums = [3, 4, -1, 1]", "2")],
    starter="""
        pub fn first_missing_positive(nums: &mut [i32]) -> i32 {
            todo!()
        }
    """,
    solution="""
        pub fn first_missing_positive(nums: &mut [i32]) -> i32 {
            let n = nums.len();
            for i in 0..n {
                // Keep swapping nums[i] into its home slot until it's out of range or already home.
                while nums[i] > 0 && (nums[i] as usize) <= n && nums[nums[i] as usize - 1] != nums[i] {
                    let home = nums[i] as usize - 1;
                    nums.swap(i, home);
                }
            }
            (0..n).find(|&i| nums[i] != i as i32 + 1).map_or(n as i32 + 1, |i| i as i32 + 1)
        }
    """,
    visible=[
        T("gap_at_two", "nums = [3, 4, -1, 1]", "first_missing_positive(&mut [3, 4, -1, 1])", "2"),
        T("next_after_run", "nums = [1, 2, 0]", "first_missing_positive(&mut [1, 2, 0])", "3"),
        T("all_large", "nums = [7, 8, 9, 11, 12]", "first_missing_positive(&mut [7, 8, 9, 11, 12])", "1"),
    ],
    hidden=[
        T("duplicates", "nums = [1, 1]", "first_missing_positive(&mut [1, 1])", "2"),
        T("empty", "nums = []", "first_missing_positive(&mut [])", "1"),
        T("permutation", "nums = (1..=1000).rev()", "first_missing_positive(&mut (1..=1000).rev().collect::<Vec<_>>())", "1001"),
    ],
    hints=[("approach", "The answer is in 1..=n+1. Can each value v in that range live at index v − 1?"),
           ("edge case", "Duplicates would swap forever; stop when the target slot already holds the value.")],
    notes=("Each swap puts one value in its final slot, so there are at most n swaps in total.", "O(n)", "O(1)"),
    follow_up="Why is the answer always at most n + 1?",
    related=["S3"],
))

P.append(dict(
    slug="quicksort-in-place", title="Quicksort in place", level="hard", stage="in-place", tags=["split_at_mut", "recursion", "mem::take"],
    source="W33",
    teaches=["Hoare partitioning handles many equal keys.", "Recurse on the smaller half to bound stack depth.", "`mem::take` on a `&mut [T]` to reborrow in a loop."],
    statement="""
        Sort `v` in place with quicksort. It must handle sorted, reversed and all-equal inputs of
        20,000 elements without a stack overflow.
    """,
    starter="""
        pub fn quicksort(v: &mut [i32]) {
            todo!()
        }
    """,
    solution="""
        pub fn quicksort(mut v: &mut [i32]) {
            while v.len() > 1 {
                let p = partition(v);
                // `take` moves the slice out of `v` so its halves can be stored back into `v`.
                let (left, right) = std::mem::take(&mut v).split_at_mut(p + 1);
                // Recurse on the smaller half and loop on the larger: O(log n) stack.
                if left.len() < right.len() {
                    quicksort(left);
                    v = right;
                } else {
                    quicksort(right);
                    v = left;
                }
            }
        }

        /// Hoare partition. Returns j with v[..=j] ≤ pivot ≤ v[j+1..]; both sides are non-empty.
        fn partition(v: &mut [i32]) -> usize {
            let pivot = v[(v.len() - 1) / 2];
            let (mut i, mut j) = (0, v.len() - 1);
            loop {
                while v[i] < pivot {
                    i += 1;
                }
                while v[j] > pivot {
                    j -= 1;
                }
                if i >= j {
                    return j;
                }
                v.swap(i, j);
                i += 1;
                j -= 1;
            }
        }
    """,
    visible=[
        T("mixed", "[5, 2, 9, 1, 5, 6]", "{ let mut v = vec![5, 2, 9, 1, 5, 6]; quicksort(&mut v); v }", "vec![1, 2, 5, 5, 6, 9]"),
        T("empty", "[]", "{ let mut v: Vec<i32> = vec![]; quicksort(&mut v); v }", "Vec::<i32>::new()"),
        T("two", "[2, 1]", "{ let mut v = vec![2, 1]; quicksort(&mut v); v }", "vec![1, 2]"),
    ],
    hidden=[
        """
        fn sorted_copy(v: &[i32]) -> Vec<i32> {
            let mut s = v.to_vec();
            s.sort_unstable();
            s
        }

        #[test]
        fn already_sorted_20k() {
            let mut v: Vec<i32> = (0..20_000).collect();
            let want = sorted_copy(&v);
            quicksort(&mut v);
            check!("0..20000", v == want, true);
        }

        #[test]
        fn reversed_20k() {
            let mut v: Vec<i32> = (0..20_000).rev().collect();
            let want = sorted_copy(&v);
            quicksort(&mut v);
            check!("(0..20000).rev()", v == want, true);
        }

        #[test]
        fn all_equal_20k() {
            let mut v = vec![7; 20_000];
            quicksort(&mut v);
            check!("[7; 20000]", v == vec![7; 20_000], true);
        }

        #[test]
        fn pseudo_random_5k() {
            let mut x: u32 = 12345;
            let mut v: Vec<i32> = (0..5_000).map(|_| { x = x.wrapping_mul(1_103_515_245).wrapping_add(12_345); (x >> 16) as i32 % 1000 - 500 }).collect();
            let want = sorted_copy(&v);
            quicksort(&mut v);
            check!("5000 values in -500..500", v == want, true);
        }
        """,
    ],
    hints=[("approach", "Partition, then sort each side. Pick the middle element as the pivot to survive sorted input."),
           ("approach", "Lomuto partitioning degrades to O(n²) when every key is equal. Hoare's doesn't."),
           ("rust", "`split_at_mut` gives two disjoint `&mut` halves. To keep looping on one of them, `std::mem::take(&mut v)` first.")],
    notes=("Recursing into the smaller half bounds the stack at O(log n). `mem::take` swaps an empty slice into `v`, so the halves can be assigned back without fighting the borrow checker.", "O(n log n) average", "O(log n)"),
    follow_up="How does std's `sort_unstable` avoid quicksort's worst case?",
    related=["L2", "S3"],
))

P.append(dict(
    slug="max-points-on-a-line", title="Max points on a line", level="hard", stage="in-place", tags=["gcd", "HashMap"],
    teaches=["Normalise slopes with gcd instead of floats.", "Handle duplicate points separately."],
    statement="Return the largest number of points in `points` that lie on one straight line.",
    examples=[("points = [(1,1), (2,2), (3,3)]", "3")],
    starter="""
        pub fn max_points(points: &[(i32, i32)]) -> usize {
            todo!()
        }
    """,
    solution="""
        use std::collections::HashMap;

        fn gcd(a: i64, b: i64) -> i64 {
            if b == 0 { a.abs() } else { gcd(b, a % b) }
        }

        pub fn max_points(points: &[(i32, i32)]) -> usize {
            let mut best = points.len().min(2);
            for (i, &(x1, y1)) in points.iter().enumerate() {
                let mut slopes: HashMap<(i64, i64), usize> = HashMap::new();
                let mut same = 0;
                for &(x2, y2) in &points[i + 1..] {
                    let (mut dx, mut dy) = (x2 as i64 - x1 as i64, y2 as i64 - y1 as i64);
                    if dx == 0 && dy == 0 {
                        same += 1;
                        continue;
                    }
                    let g = gcd(dx, dy);
                    dx /= g;
                    dy /= g;
                    // One sign convention per direction.
                    if dx < 0 || (dx == 0 && dy < 0) {
                        dx = -dx;
                        dy = -dy;
                    }
                    *slopes.entry((dx, dy)).or_insert(0) += 1;
                }
                let on_line = slopes.values().copied().max().unwrap_or(0);
                best = best.max(1 + same + on_line);
            }
            best
        }
    """,
    visible=[
        T("diagonal", "points = [(1,1), (2,2), (3,3)]", "max_points(&[(1, 1), (2, 2), (3, 3)])", "3"),
        T("mixed", "points = [(1,1), (3,2), (5,3), (4,1), (2,3), (1,4)]", "max_points(&[(1, 1), (3, 2), (5, 3), (4, 1), (2, 3), (1, 4)])", "4"),
        T("single", "points = [(0,0)]", "max_points(&[(0, 0)])", "1"),
    ],
    hidden=[
        T("duplicates", "points = [(1,1), (1,1), (2,3)]", "max_points(&[(1, 1), (1, 1), (2, 3)])", "3"),
        T("vertical", "points = [(2,1), (2,5), (2,-3), (0,0)]", "max_points(&[(2, 1), (2, 5), (2, -3), (0, 0)])", "3"),
        T("empty", "points = []", "max_points(&[])", "0"),
    ],
    hints=[("approach", "Fix one point and group the others by the direction to it."),
           ("rust", "Floats lose precision; reduce (dx, dy) by their gcd and fix the sign instead."),
           ("edge case", "Duplicate points are on every line through that point.")],
    notes=("Each anchor point is compared with the points after it. Normalising by gcd and sign gives one exact key per direction.", "O(n²)", "O(n)"),
    follow_up="Why is using an f64 slope as a HashMap key a bad idea?",
    related=["S4", "D13"],
))

STAGES = [
    ("vec-and-slices", "Vec & slices", "easy"),
    ("counting", "Counting", "easy"),
    ("grouping-prefix-sums", "Grouping & prefix sums", "medium"),
    ("sorting-order", "Sorting & order", "medium"),
    ("in-place", "In place", "hard"),
]

if __name__ == "__main__":
    n = write_track("d1-arrays-hashing", "D1", "Arrays & hashing", "D", "core", 1,
                    "Vec, slices and hash maps: the first tools in every interview, and the first place Rust's ownership shows up.",
                    STAGES, P)
    print("D1", n)
