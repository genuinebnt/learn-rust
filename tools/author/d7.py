from author import T, write_track

P = []

# ---------------------------------------------------------------- heap basics (easy)

P.append(dict(
    slug="kth-largest-in-a-stream", title="Kth largest in a stream", level="easy", stage="heap-basics",
    tags=["BinaryHeap", "Reverse", "min-heap"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "Adobe"],
    teaches=["`BinaryHeap` is a max-heap; `BinaryHeap<Reverse<i32>>` turns it into a min-heap.",
             "Keep only the `k` largest values: the smallest of them, on top, is the answer.",
             "`Option<i32>` instead of a sentinel while fewer than `k` values have arrived."],
    statement="""
        Build a `KthLargest` that watches a stream of numbers:

        - `new(k, nums)` starts the stream with the values in `nums`;
        - `add(val)` adds `val` and returns the `k`-th largest value seen so far, counting duplicates
          (for `k = 1` that is the maximum).

        While fewer than `k` values have arrived there is no `k`-th largest, so `add` returns `None`.
    """,
    examples=[("k = 3, nums = [4, 5, 8, 2]; add 3, 5, 10, 9, 4", "Some(4), Some(5), Some(5), Some(8), Some(8)"),
              ("k = 3, nums = []; add 1, 2, 3", "None, None, Some(1)")],
    constraints=["1 ≤ k ≤ 10⁵", "0 ≤ nums.len() ≤ 10⁵", "up to 10⁵ calls to add", "values are any i32"],
    starter="""
        pub struct KthLargest {
            // your fields
        }

        impl KthLargest {
            pub fn new(k: usize, nums: &[i32]) -> Self {
                todo!()
            }

            pub fn add(&mut self, val: i32) -> Option<i32> {
                todo!()
            }
        }
    """,
    solution="""
        use std::cmp::Reverse;
        use std::collections::BinaryHeap;

        pub struct KthLargest {
            k: usize,
            /// The k largest values so far; the smallest of them is on top.
            heap: BinaryHeap<Reverse<i32>>,
        }

        impl KthLargest {
            pub fn new(k: usize, nums: &[i32]) -> Self {
                let mut s = KthLargest { k, heap: BinaryHeap::with_capacity(k + 1) };
                for &x in nums {
                    s.add(x);
                }
                s
            }

            pub fn add(&mut self, val: i32) -> Option<i32> {
                self.heap.push(Reverse(val));
                if self.heap.len() > self.k {
                    self.heap.pop();
                }
                if self.heap.len() < self.k {
                    return None;
                }
                self.heap.peek().map(|&Reverse(x)| x)
            }
        }
    """,
    visible=[
        T("leetcode_example", "k = 3, nums = [4, 5, 8, 2]; add 3, 5, 10, 9, 4", "[3, 5, 10, 9, 4].map(|v| s.add(v))",
          "[Some(4), Some(5), Some(5), Some(8), Some(8)]", setup="let mut s = KthLargest::new(3, &[4, 5, 8, 2]);"),
        T("leetcode_duplicates_count", "k = 4, nums = [7, 7, 7, 7, 8, 3]; add 2, 10, 9, 9", "[2, 10, 9, 9].map(|v| s.add(v))",
          "[Some(7), Some(7), Some(7), Some(8)]", setup="let mut s = KthLargest::new(4, &[7, 7, 7, 7, 8, 3]);"),
        T("none_until_k_values", "k = 3, nums = []; add 1, 2, 3, 4", "[1, 2, 3, 4].map(|v| s.add(v))", "[None, None, Some(1), Some(2)]",
          setup="let mut s = KthLargest::new(3, &[]);"),
        T("k_one_is_the_maximum", "k = 1, nums = [5]; add 3, 9, 2", "[3, 9, 2].map(|v| s.add(v))", "[Some(5), Some(9), Some(9)]",
          setup="let mut s = KthLargest::new(1, &[5]);"),
        T("negatives", "k = 2, nums = [-5, -1]; add -3, -10, 0", "[-3, -10, 0].map(|v| s.add(v))", "[Some(-3), Some(-3), Some(-1)]",
          setup="let mut s = KthLargest::new(2, &[-5, -1]);"),
    ],
    hidden=[
        T("empty_start_k_one", "k = 1, nums = []; add -4, -9", "[-4, -9].map(|v| s.add(v))", "[Some(-4), Some(-4)]",
          setup="let mut s = KthLargest::new(1, &[]);"),
        T("small_value_changes_nothing", "k = 2, nums = [10, 20, 30]; add 1, 1, 1", "[1, 1, 1].map(|v| s.add(v))", "[Some(20), Some(20), Some(20)]",
          setup="let mut s = KthLargest::new(2, &[10, 20, 30]);"),
        T("one_short_of_k", "k = 3, nums = [1]; add 2, 3", "[2, 3].map(|v| s.add(v))", "[None, Some(1)]",
          setup="let mut s = KthLargest::new(3, &[1]);"),
        T("extremes", "k = 2, nums = [i32::MAX, i32::MIN]; add i32::MIN, i32::MAX", "[i32::MIN, i32::MAX].map(|v| s.add(v))",
          "[Some(i32::MIN), Some(i32::MAX)]", setup="let mut s = KthLargest::new(2, &[i32::MAX, i32::MIN]);"),
        T("all_equal", "k = 3, nums = [4, 4, 4, 4]; add 4, 5", "[4, 5].map(|v| s.add(v))", "[Some(4), Some(4)]",
          setup="let mut s = KthLargest::new(3, &[4, 4, 4, 4]);"),
        T("each_new_maximum", "k = 2, nums = [1, 2]; add 3, 4, 5", "[3, 4, 5].map(|v| s.add(v))", "[Some(2), Some(3), Some(4)]",
          setup="let mut s = KthLargest::new(2, &[1, 2]);"),
        T("k_larger_than_everything", "k = 5, nums = [9, 8]; add 7, 6, 5, 4", "[7, 6, 5, 4].map(|v| s.add(v))", "[None, None, Some(5), Some(5)]",
          setup="let mut s = KthLargest::new(5, &[9, 8]);"),
        T("two_streams_are_independent", "a: k = 1, nums = [1]; b: k = 1, nums = [100]; a.add(2), b.add(3)", "(a.add(2), b.add(3))", "(Some(2), Some(100))",
          setup="let mut a = KthLargest::new(1, &[1]);\nlet mut b = KthLargest::new(1, &[100]);"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(701);
            for _ in 0..300 {
                let k = 1 + rng.below(5);
                let n = rng.below(8);
                let nums: Vec<i32> = rng.vec(n, -10, 10);
                let adds_len = rng.below(10);
                let adds: Vec<i32> = rng.vec(adds_len, -10, 10);
                let mut s = KthLargest::new(k, &nums);
                let mut seen = nums.clone();
                let mut got = Vec::new();
                let mut want = Vec::new();
                for &v in &adds {
                    got.push(s.add(v));
                    seen.push(v);
                    let mut sorted = seen.clone();
                    sorted.sort_unstable_by(|a, b| b.cmp(a));
                    want.push(sorted.get(k - 1).copied());
                }
                check!(format!("k = {k}, nums = {nums:?}; add {adds:?}"), got, want);
            }
        }

        #[test]
        fn scale_100k_adds() {
            let mut rng = anneal_prelude::Rng::new(702);
            let mut nums: Vec<i32> = (0..100_000).collect();
            rng.shuffle(&mut nums);
            let mut s = KthLargest::new(50_000, &nums);
            // Even steps add a new maximum, odd steps a value far below the k-th largest.
            let mut first_wrong = None;
            for i in 0..100_000 {
                let v = if i % 2 == 0 { 100_000 + i / 2 } else { -1 - i };
                if s.add(v) != Some(50_001 + i / 2) && first_wrong.is_none() {
                    first_wrong = Some(i);
                }
            }
            check!("k = 50000, nums = 0..100000 shuffled; add 100000, -2, 100001, -4, … (100000 adds); first add with a wrong answer", first_wrong, None);
        }
        """,
    ],
    wrong=dict(
        select_each_add="""
            pub struct KthLargest {
                k: usize,
                all: Vec<i32>,
            }

            impl KthLargest {
                pub fn new(k: usize, nums: &[i32]) -> Self {
                    KthLargest { k, all: nums.to_vec() }
                }

                pub fn add(&mut self, val: i32) -> Option<i32> {
                    self.all.push(val);
                    if self.all.len() < self.k {
                        return None;
                    }
                    let k = self.k;
                    Some(*self.all.select_nth_unstable_by(k - 1, |a, b| b.cmp(a)).1)
                }
            }
        """,
        max_heap_top="""
            use std::collections::BinaryHeap;

            pub struct KthLargest {
                k: usize,
                heap: BinaryHeap<i32>,
            }

            impl KthLargest {
                pub fn new(k: usize, nums: &[i32]) -> Self {
                    KthLargest { k, heap: nums.iter().copied().collect() }
                }

                pub fn add(&mut self, val: i32) -> Option<i32> {
                    self.heap.push(val);
                    // Pops the largest values: keeps the smallest ones instead.
                    while self.heap.len() > self.k {
                        self.heap.pop();
                    }
                    if self.heap.len() < self.k {
                        return None;
                    }
                    self.heap.peek().copied()
                }
            }
        """,
        answers_before_k="""
            use std::cmp::Reverse;
            use std::collections::BinaryHeap;

            pub struct KthLargest {
                k: usize,
                heap: BinaryHeap<Reverse<i32>>,
            }

            impl KthLargest {
                pub fn new(k: usize, nums: &[i32]) -> Self {
                    let mut s = KthLargest { k, heap: BinaryHeap::new() };
                    for &x in nums {
                        s.add(x);
                    }
                    s
                }

                pub fn add(&mut self, val: i32) -> Option<i32> {
                    self.heap.push(Reverse(val));
                    if self.heap.len() > self.k {
                        self.heap.pop();
                    }
                    self.heap.peek().map(|&Reverse(x)| x)
                }
            }
        """,
    ),
    hints=[("approach", "You never need values below the k-th largest again. Keep just the k largest, and look at the smallest of those."),
           ("rust", "`BinaryHeap` pops the maximum. Wrap values in `std::cmp::Reverse` to get a min-heap; `peek()` gives the top without removing it."),
           ("edge case", "Until k values have arrived, the heap is short and the answer is `None`.")],
    notes=("A min-heap capped at k holds the k largest values seen; its top is the k-th largest. Each `add` pushes, pops once if the heap grew past k, and peeks. "
           "`Reverse<T>` flips `Ord`, so `BinaryHeap<Reverse<i32>>` is the min-heap std doesn't ship separately.", "O(log k) per add, O(n log k) for new", "O(k)"),
    follow_up="If `k` could change between calls, what would you keep instead of a single capped heap?",
    related=["S5", "D1"],
))

P.append(dict(
    slug="last-stone-weight", title="Last stone weight", level="easy", stage="heap-basics", tags=["BinaryHeap", "simulation"],
    companies=["Amazon", "Google", "Microsoft"],
    teaches=["`BinaryHeap::from(vec)` heapifies in O(n), faster than n pushes.",
             "`let … else` to stop when the second pop comes back empty.",
             '`Option<u32>` for "no stone left" instead of 0.'],
    statement="""
        Each turn, take the two heaviest stones, `y ≥ x`, and smash them together: if `x == y` both are destroyed,
        otherwise a stone of weight `y − x` goes back. Play until at most one stone is left.

        Return the weight of the last stone, or `None` if every stone was destroyed.
    """,
    examples=[("stones = [2, 7, 4, 1, 8, 1]", "Some(1)"), ("stones = [3, 3]", "None")],
    constraints=["0 ≤ stones.len() ≤ 2·10⁵", "1 ≤ stones[i] ≤ 10⁹"],
    starter="""
        pub fn last_stone_weight(stones: &[u32]) -> Option<u32> {
            todo!()
        }
    """,
    solution="""
        use std::collections::BinaryHeap;

        pub fn last_stone_weight(stones: &[u32]) -> Option<u32> {
            let mut heap = BinaryHeap::from(stones.to_vec());
            while let Some(y) = heap.pop() {
                let Some(x) = heap.pop() else {
                    return Some(y);
                };
                if y > x {
                    heap.push(y - x);
                }
            }
            None
        }
    """,
    visible=[
        T("leetcode_example", "stones = [2, 7, 4, 1, 8, 1]", "last_stone_weight(&[2, 7, 4, 1, 8, 1])", "Some(1)"),
        T("leetcode_single", "stones = [1]", "last_stone_weight(&[1])", "Some(1)"),
        T("equal_pair_destroys_both", "stones = [3, 3]", "last_stone_weight(&[3, 3])", "None"),
        T("empty", "stones = []", "last_stone_weight(&[])", "None"),
        T("heaviest_two_first", "stones = [10, 4, 2, 10] (10 and 10 go first)", "last_stone_weight(&[10, 4, 2, 10])", "Some(2)"),
        T("no_zero_stone", "stones = [5, 5, 5, 5]", "last_stone_weight(&[5, 5, 5, 5])", "None"),
    ],
    hidden=[
        T("two_different", "stones = [7, 3]", "last_stone_weight(&[7, 3])", "Some(4)"),
        T("three_equal", "stones = [1, 1, 1]", "last_stone_weight(&[1, 1, 1])", "Some(1)"),
        T("large_weights", "stones = [1000000000, 1]", "last_stone_weight(&[1_000_000_000, 1])", "Some(999_999_999)"),
        T("max_weights_cancel", "stones = [1000000000, 1000000000]", "last_stone_weight(&[1_000_000_000, 1_000_000_000])", "None"),
        T("remainder_is_heaviest", "stones = [9, 1, 1] (8 goes back and beats 1)", "last_stone_weight(&[9, 1, 1])", "Some(7)"),
        T("ends_in_destruction", "stones = [2, 2, 1, 1]", "last_stone_weight(&[2, 2, 1, 1])", "None"),
        T("sorted_input", "stones = [1, 2, 3, 4, 5]", "last_stone_weight(&[1, 2, 3, 4, 5])", "Some(1)"),
        T("many_ones", "stones = [1; 1001]", "last_stone_weight(&vec![1; 1001])", "Some(1)"),
        T("powers_of_two", "stones = [1, 2, 4, 8, 16]", "last_stone_weight(&[1, 2, 4, 8, 16])", "Some(1)"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(703);
            for _ in 0..300 {
                let n = rng.below(10);
                let stones: Vec<u32> = rng.vec(n, 1, 12);
                let mut left = stones.clone();
                while left.len() > 1 {
                    left.sort_unstable();
                    let y = left.pop().unwrap();
                    let x = left.pop().unwrap();
                    if y > x {
                        left.push(y - x);
                    }
                }
                check!(format!("stones = {stones:?}"), last_stone_weight(&stones), left.first().copied());
            }
        }

        #[test]
        fn scale_200k() {
            let mut rng = anneal_prelude::Rng::new(704);
            let stones: Vec<u32> = rng.vec(200_000, 1, 1_000_000_000);
            // Reference: the same game on a BTreeMap multiset (weight → count).
            let mut bag = std::collections::BTreeMap::new();
            for &s in &stones {
                *bag.entry(s).or_insert(0u32) += 1;
            }
            let take = |bag: &mut std::collections::BTreeMap<u32, u32>| {
                let mut e = bag.last_entry()?;
                let w = *e.key();
                *e.get_mut() -= 1;
                if *e.get() == 0 {
                    e.remove();
                }
                Some(w)
            };
            let want = loop {
                let Some(y) = take(&mut bag) else { break None };
                let Some(x) = take(&mut bag) else { break Some(y) };
                if y > x {
                    *bag.entry(y - x).or_insert(0) += 1;
                }
            };
            check!("stones = 200000 random weights in 1..=10⁹", last_stone_weight(&stones), want);
        }
        """,
    ],
    wrong=dict(
        pushes_zero="""
            use std::collections::BinaryHeap;

            pub fn last_stone_weight(stones: &[u32]) -> Option<u32> {
                let mut heap = BinaryHeap::from(stones.to_vec());
                while heap.len() > 1 {
                    let y = heap.pop().unwrap();
                    let x = heap.pop().unwrap();
                    heap.push(y - x);
                }
                heap.pop()
            }
        """,
        sort_each_turn="""
            pub fn last_stone_weight(stones: &[u32]) -> Option<u32> {
                let mut left = stones.to_vec();
                while left.len() > 1 {
                    left.sort_unstable();
                    let y = left.pop().unwrap();
                    let x = left.pop().unwrap();
                    if y > x {
                        left.push(y - x);
                    }
                }
                left.pop()
            }
        """,
        lightest_two="""
            use std::cmp::Reverse;
            use std::collections::BinaryHeap;

            pub fn last_stone_weight(stones: &[u32]) -> Option<u32> {
                let mut heap: BinaryHeap<Reverse<u32>> = stones.iter().map(|&s| Reverse(s)).collect();
                while let Some(Reverse(x)) = heap.pop() {
                    let Some(Reverse(y)) = heap.pop() else {
                        return Some(x);
                    };
                    if y > x {
                        heap.push(Reverse(y - x));
                    }
                }
                None
            }
        """,
    ),
    hints=[("approach", "You need the two largest stones over and over while new stones arrive: a max-heap."),
           ("rust", "`BinaryHeap::from(stones.to_vec())` builds the heap in O(n). Pop `y`, then `let Some(x) = heap.pop() else { return Some(y) };`."),
           ("edge case", "Equal stones leave nothing. Pushing a 0 back would turn `None` into `Some(0)`.")],
    notes=("Every turn removes at least one stone, so there are at most n turns of O(log n) each. `BinaryHeap::from` reuses the vector's buffer and "
           'heapifies bottom-up in O(n). Returning `Option` keeps "nothing left" out of the weight range.', "O(n log n)", "O(n)"),
    follow_up="Last stone weight II lets you pick any two stones each turn and asks for the smallest possible result. Why does a heap no longer help?",
    related=["S5", "D12"],
))

READING_START = """
    use std::cmp::Reverse;
    use std::collections::BinaryHeap;

    /// A sensor reading. It must work as a key in heaps, B-tree sets and hash sets.
    #[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Hash)]
    pub struct Reading(pub f64);
"""

TOP_K = """
    /// The `k` highest readings, highest first. NaN readings are sensor faults and are skipped.
    /// The heap never holds more than `k + 1` readings.
    pub fn top_k(readings: &[f64], k: usize) -> Vec<Reading> {
        let mut heap: BinaryHeap<Reverse<Reading>> = BinaryHeap::with_capacity(k + 1);
        for &r in readings {
            if r.is_nan() {
                continue;
            }
            heap.push(Reverse(Reading(r)));
            if heap.len() > k {
                heap.pop();
            }
        }
        // Ascending by Reverse<Reading> is descending by Reading.
        heap.into_sorted_vec().into_iter().map(|Reverse(r)| r).collect()
    }
"""

READING_FIXED = """
    use std::cmp::{Ordering, Reverse};
    use std::collections::BinaryHeap;
    use std::hash::{Hash, Hasher};

    /// A sensor reading. It must work as a key in heaps, B-tree sets and hash sets.
    #[derive(Debug, Clone, Copy)]
    pub struct Reading(pub f64);

    impl Ord for Reading {
        fn cmp(&self, other: &Self) -> Ordering {
            self.0.total_cmp(&other.0)
        }
    }

    impl PartialOrd for Reading {
        fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
            Some(self.cmp(other))
        }
    }

    impl PartialEq for Reading {
        fn eq(&self, other: &Self) -> bool {
            self.cmp(other) == Ordering::Equal
        }
    }

    impl Eq for Reading {}

    impl Hash for Reading {
        // total_cmp says Equal exactly when the bits match, so hashing the bits agrees with Eq.
        fn hash<H: Hasher>(&self, state: &mut H) {
            self.0.to_bits().hash(state);
        }
    }
"""


def reading(head: str) -> str:
    return head.strip("\n") + "\n" + TOP_K


# Shows readings the way the tests compare them: -0 and 0 differ, NaN is "NaN".
SHOW = """
fn show(rs: &[Reading]) -> Vec<String> {
    rs.iter().map(|r| r.0.to_string()).collect()
}
"""

P.append(dict(
    slug="fix-binary-heap-f64", title="Fix: BinaryHeap<f64> won't compile", mode="fix", level="medium", stage="heap-basics",
    tags=["Ord", "total_cmp", "Hash", "E0277"],
    teaches=["`f64` is only `PartialOrd`/`PartialEq`: NaN breaks totality and reflexivity, so it can't be `Ord`, `Eq` or `Hash`.",
             "An `Ord` newtype over `total_cmp` must bring `PartialOrd`, `PartialEq` and `Hash` along with it; deriving those next to a hand-written `Ord` makes them disagree.",
             "`total_cmp` says `Equal` exactly when the bits match, so `to_bits()` is the hash that agrees with it."],
    statement="""
        `top_k` keeps the highest readings in a `BinaryHeap<Reverse<Reading>>`, and other code keeps `Reading`s
        in `BTreeSet`s and `HashSet`s. None of it compiles.

        Make `Reading` a lawful key, ordered by the IEEE 754 total order (`f64::total_cmp`):

        - `-0.0` ranks below `0.0`, and the two are **not** equal;
        - a NaN equals itself (`Eq` is reflexive). A positive NaN ranks above `+∞`, a negative one below `-∞`;
        - `==`, `<`, `cmp`, `partial_cmp` and hashing all agree with each other.

        Fix `Reading`; leave `top_k` as it is.
    """,
    starter=reading(READING_START),
    solution=reading(READING_FIXED),
    rules=dict(methods=["partial_cmp", "unwrap", "expect", "unwrap_or", "sort", "sort_by", "sort_unstable", "sort_unstable_by", "sort_by_key"], lines=30),
    use="use solution::*;\n\n" + SHOW.strip("\n"),
    visible=[
        T("top_two", "readings = [3.5, -1.0, 9.25, 2.0], k = 2", "show(&top_k(&[3.5, -1.0, 9.25, 2.0], 2))", 'vec!["9.25", "3.5"]'),
        T("nan_is_skipped", "readings = [NaN, 1.0, NaN, -4.0], k = 3", "show(&top_k(&[f64::NAN, 1.0, f64::NAN, -4.0], 3))", 'vec!["1", "-4"]'),
        T("positive_zero_ranks_higher", "readings = [-0.0, 0.0], k = 1", "show(&top_k(&[-0.0, 0.0], 1))", 'vec!["0"]'),
        T("nan_equals_itself", "Reading(NaN) == Reading(NaN)", "Reading(f64::NAN) == Reading(f64::NAN)", "true"),
        T("zeros_differ", "Reading(0.0) == Reading(-0.0), Reading(-0.0) < Reading(0.0)", "(Reading(0.0) == Reading(-0.0), Reading(-0.0) < Reading(0.0))", "(false, true)"),
        T("k_zero", "readings = [1.0, 2.0], k = 0", "show(&top_k(&[1.0, 2.0], 0))", "Vec::<String>::new()"),
    ],
    hidden=[
        T("fewer_than_k", "readings = [2.0, 7.5], k = 5", "show(&top_k(&[2.0, 7.5], 5))", 'vec!["7.5", "2"]'),
        T("negatives", "readings = [-1.0, -2.0, 0.5], k = 2", "show(&top_k(&[-1.0, -2.0, 0.5], 2))", 'vec!["0.5", "-1"]'),
        T("only_negatives", "readings = [-3.0, -1.5, -2.0, -10.0], k = 3", "show(&top_k(&[-3.0, -1.5, -2.0, -10.0], 3))", 'vec!["-1.5", "-2", "-3"]'),
        T("infinities", "readings = [-inf, 5.0, inf, -0.0], k = 4", "show(&top_k(&[f64::NEG_INFINITY, 5.0, f64::INFINITY, -0.0], 4))", 'vec!["inf", "5", "-0", "-inf"]'),
        T("duplicates", "readings = [2.0, 1.0, 2.0], k = 2", "show(&top_k(&[2.0, 1.0, 2.0], 2))", 'vec!["2", "2"]'),
        T("only_nan", "readings = [NaN, NaN], k = 2", "show(&top_k(&[f64::NAN, f64::NAN], 2))", "Vec::<String>::new()"),
        T("empty", "readings = [], k = 3", "show(&top_k(&[], 3))", "Vec::<String>::new()"),
        T("nan_signs", "Reading(-NaN) < Reading(-inf), Reading(inf) < Reading(NaN), Reading(NaN) == Reading(-NaN)",
          "(Reading(-f64::NAN) < Reading(f64::NEG_INFINITY), Reading(f64::INFINITY) < Reading(f64::NAN), Reading(f64::NAN) == Reading(-f64::NAN))",
          "(true, true, false)"),
        T("btree_set", "BTreeSet of NaN, NaN, 0.0, -0.0, 1.0, -inf", "show(&set.into_iter().collect::<Vec<_>>())", 'vec!["-inf", "-0", "0", "1", "NaN"]',
          setup="let set: std::collections::BTreeSet<Reading> = [f64::NAN, f64::NAN, 0.0, -0.0, 1.0, f64::NEG_INFINITY].into_iter().map(Reading).collect();"),
        T("hash_set", "HashSet of NaN, NaN, 0.0, -0.0, 0.0, 2.5", "set.len()", "4",
          setup="let set: std::collections::HashSet<Reading> = [f64::NAN, f64::NAN, 0.0, -0.0, 0.0, 2.5].into_iter().map(Reading).collect();"),
        T("partial_cmp_is_total", "Reading(NaN).partial_cmp(&Reading(1.0)), Reading(0.0).partial_cmp(&Reading(-0.0))",
          "(Reading(f64::NAN).partial_cmp(&Reading(1.0)), Reading(0.0).partial_cmp(&Reading(-0.0)))",
          "(Some(std::cmp::Ordering::Greater), Some(std::cmp::Ordering::Greater))"),
        """
        #[test]
        fn laws_hold_for_every_pair() {
            use std::cmp::Ordering;
            use std::hash::{DefaultHasher, Hash, Hasher};
            let hash = |r: &Reading| {
                let mut h = DefaultHasher::new();
                r.hash(&mut h);
                h.finish()
            };
            let pool = [f64::NAN, -f64::NAN, f64::NEG_INFINITY, -2.5, -0.0, 0.0, 1.0, 3.25, f64::INFINITY, f64::MIN_POSITIVE, f64::MAX];
            for &x in &pool {
                for &y in &pool {
                    let (a, b) = (Reading(x), Reading(y));
                    let order = x.total_cmp(&y);
                    let got = (a.cmp(&b), a.partial_cmp(&b), a == b, a < b, a >= b);
                    let want = (order, Some(order), order == Ordering::Equal, order == Ordering::Less, order != Ordering::Less);
                    check!(format!("Reading({x:?}) vs Reading({y:?}): (cmp, partial_cmp, ==, <, >=)"), got, want);
                    if a == b {
                        check!(format!("hash(Reading({x:?})) == hash(Reading({y:?})) since they are equal"), hash(&a) == hash(&b), true);
                    }
                }
            }
        }

        #[test]
        fn random_vs_reference() {
            let mut rng = anneal_prelude::Rng::new(705);
            let pool = [f64::NAN, -f64::NAN, -2.5, -0.0, 0.0, 1.0, 3.25, 3.25, f64::INFINITY, f64::NEG_INFINITY];
            for _ in 0..300 {
                let n = rng.below(10);
                let readings: Vec<f64> = (0..n).map(|_| *rng.pick(&pool)).collect();
                let k = rng.below(6);
                let mut want: Vec<f64> = readings.iter().copied().filter(|x| !x.is_nan()).collect();
                want.sort_by(|a, b| b.total_cmp(a));
                want.truncate(k);
                let want: Vec<String> = want.iter().map(|x| x.to_string()).collect();
                check!(format!("readings = {readings:?}, k = {k}"), show(&top_k(&readings, k)), want);
            }
        }

        #[test]
        fn scale_200k_readings() {
            let mut rng = anneal_prelude::Rng::new(706);
            let readings: Vec<f64> = (0..200_000).map(|i| if i % 1000 == 0 { f64::NAN } else { rng.int(-1_000_000, 1_000_000) as f64 / 4.0 }).collect();
            let mut want: Vec<f64> = readings.iter().copied().filter(|x| !x.is_nan()).collect();
            want.sort_by(|a, b| b.total_cmp(a));
            want.truncate(1000);
            let got: Vec<f64> = top_k(&readings, 1000).iter().map(|r| r.0).collect();
            check!("200000 random readings (every 1000th NaN), k = 1000", got == want, true);
        }
        """,
    ],
    wrong=dict(
        derived_partial_traits="""
            use std::cmp::{Ordering, Reverse};
            use std::collections::BinaryHeap;
            use std::hash::{Hash, Hasher};

            /// A sensor reading. It must work as a key in heaps, B-tree sets and hash sets.
            #[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
            pub struct Reading(pub f64);

            impl Eq for Reading {}

            impl Ord for Reading {
                fn cmp(&self, other: &Self) -> Ordering {
                    self.0.total_cmp(&other.0)
                }
            }

            impl Hash for Reading {
                fn hash<H: Hasher>(&self, state: &mut H) {
                    self.0.to_bits().hash(state);
                }
            }
        """ + TOP_K,
        order_by_bits="""
            use std::cmp::{Ordering, Reverse};
            use std::collections::BinaryHeap;
            use std::hash::{Hash, Hasher};

            /// A sensor reading. It must work as a key in heaps, B-tree sets and hash sets.
            #[derive(Debug, Clone, Copy)]
            pub struct Reading(pub f64);

            impl Ord for Reading {
                fn cmp(&self, other: &Self) -> Ordering {
                    self.0.to_bits().cmp(&other.0.to_bits())
                }
            }

            impl PartialOrd for Reading {
                fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
                    Some(self.cmp(other))
                }
            }

            impl PartialEq for Reading {
                fn eq(&self, other: &Self) -> bool {
                    self.0.to_bits() == other.0.to_bits()
                }
            }

            impl Eq for Reading {}

            impl Hash for Reading {
                fn hash<H: Hasher>(&self, state: &mut H) {
                    self.0.to_bits().hash(state);
                }
            }
        """ + TOP_K,
        numeric_equality="""
            use std::cmp::{Ordering, Reverse};
            use std::collections::BinaryHeap;
            use std::hash::{Hash, Hasher};

            /// A sensor reading. It must work as a key in heaps, B-tree sets and hash sets.
            #[derive(Debug, Clone, Copy)]
            pub struct Reading(pub f64);

            impl Ord for Reading {
                fn cmp(&self, other: &Self) -> Ordering {
                    self.0.total_cmp(&other.0)
                }
            }

            impl PartialOrd for Reading {
                fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
                    Some(self.cmp(other))
                }
            }

            impl PartialEq for Reading {
                // NaN made reflexive, but 0.0 == -0.0 still holds while cmp says Greater.
                fn eq(&self, other: &Self) -> bool {
                    self.0 == other.0 || (self.0.is_nan() && other.0.is_nan())
                }
            }

            impl Eq for Reading {}

            impl Hash for Reading {
                fn hash<H: Hasher>(&self, state: &mut H) {
                    self.0.to_bits().hash(state);
                }
            }
        """ + TOP_K,
    ),
    hints=[("rust", "`#[derive(PartialOrd, PartialEq, Hash)]` on an `f64` field gives you f64's rules: NaN ≠ NaN, 0.0 == -0.0, and no `Hash` at all. None of that can become `Eq`/`Ord`."),
           ("rust", "Write `Ord` with `total_cmp`, then define `partial_cmp` as `Some(self.cmp(other))` and `eq` as `self.cmp(other) == Ordering::Equal`, so there's one source of truth."),
           ("edge case", "Equal values must hash equally. Under `total_cmp`, equal means identical bits, so hash `to_bits()`.")],
    notes=("`BinaryHeap`, `BTreeSet` and `sort` trust `Ord` to be a total order, and `HashSet` trusts `a == b ⇒ hash(a) == hash(b)`. "
           "`f64` can't promise either, which is why it stops at `PartialOrd`. The newtype picks `total_cmp` (IEEE 754 totalOrder: "
           "−NaN < −∞ < … < −0 < +0 < … < +∞ < +NaN) and routes every other trait through it. Mixing derived `PartialEq`/`PartialOrd` "
           "with a hand-written `Ord` compiles, but then `==` and `cmp` disagree on NaN and ±0, and heaps and sets misbehave silently "
           "(Clippy: `derive_ord_xor_partial_ord`). Syntax to remember: `impl Hash for T { fn hash<H: Hasher>(&self, state: &mut H) { … } }`.",
           "O(n log k)", "O(k)"),
    follow_up="When would you rather reject NaN at construction (a `NotNan` type with a fallible `new`) than give it a place in the order?",
    related=["S8", "L4", "D1"],
))

# ---------------------------------------------------------------- heaps at work (medium)

P.append(dict(
    slug="k-closest-points", title="K closest points to origin", level="medium", stage="heaps-at-work",
    tags=["BinaryHeap", "tuple ordering", "overflow"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "LinkedIn", "Uber"],
    teaches=["A max-heap capped at k keeps the k smallest: the worst of them sits on top, ready to be evicted.",
             "Tuples compare field by field, so `(dist, x, y)` is the tie rule written as a heap key.",
             "`i32::unsigned_abs` into `u64`: a squared distance from the i32 corner doesn't fit in i64."],
    statement="""
        Return the `k` points of `points` closest to the origin `(0, 0)` by Euclidean distance, nearest first.
        Points at the same distance come in `(x, y)` order (smaller `x` first, then smaller `y`).
        A point listed twice counts twice. If `k` is at least `points.len()`, return every point.

        Coordinates can be any `i32`.
    """,
    examples=[("points = [(1, 3), (-2, 2)], k = 1", "[(-2, 2)]"), ("points = [(3, 3), (5, -1), (-2, 4)], k = 2", "[(3, 3), (-2, 4)]")],
    constraints=["0 ≤ points.len() ≤ 2·10⁵", "0 ≤ k", "coordinates are any i32"],
    starter="""
        pub fn k_closest(points: &[(i32, i32)], k: usize) -> Vec<(i32, i32)> {
            todo!()
        }
    """,
    solution="""
        use std::collections::BinaryHeap;

        /// Squared distance. |i32::MIN|² · 2 = 2⁶³, one past i64::MAX, so this is u64.
        fn dist2(x: i32, y: i32) -> u64 {
            let (x, y) = (x.unsigned_abs() as u64, y.unsigned_abs() as u64);
            x * x + y * y
        }

        pub fn k_closest(points: &[(i32, i32)], k: usize) -> Vec<(i32, i32)> {
            if k == 0 {
                return Vec::new();
            }
            // The k best so far; the worst of them (farthest, then largest (x, y)) is on top.
            let mut heap: BinaryHeap<(u64, i32, i32)> = BinaryHeap::with_capacity(k + 1);
            for &(x, y) in points {
                let key = (dist2(x, y), x, y);
                if heap.len() < k {
                    heap.push(key);
                } else if heap.peek().is_some_and(|&top| key < top) {
                    heap.pop();
                    heap.push(key);
                }
            }
            heap.into_sorted_vec().into_iter().map(|(_, x, y)| (x, y)).collect()
        }
    """,
    visible=[
        T("leetcode_one", "points = [(1, 3), (-2, 2)], k = 1", "k_closest(&[(1, 3), (-2, 2)], 1)", "vec![(-2, 2)]"),
        T("leetcode_two", "points = [(3, 3), (5, -1), (-2, 4)], k = 2", "k_closest(&[(3, 3), (5, -1), (-2, 4)], 2)", "vec![(3, 3), (-2, 4)]"),
        T("ties_in_x_then_y_order", "points = [(1, 0), (0, 1), (-1, 0), (0, -1)], k = 3", "k_closest(&[(1, 0), (0, 1), (-1, 0), (0, -1)], 3)", "vec![(-1, 0), (0, -1), (0, 1)]"),
        T("k_zero", "points = [(1, 1)], k = 0", "k_closest(&[(1, 1)], 0)", "Vec::<(i32, i32)>::new()"),
        T("k_past_the_end", "points = [(2, 2), (1, 1)], k = 5", "k_closest(&[(2, 2), (1, 1)], 5)", "vec![(1, 1), (2, 2)]"),
        T("repeated_point_counts_twice", "points = [(2, 0), (1, 1), (1, 1)], k = 2", "k_closest(&[(2, 0), (1, 1), (1, 1)], 2)", "vec![(1, 1), (1, 1)]"),
    ],
    hidden=[
        T("empty", "points = [], k = 3", "k_closest(&[], 3)", "Vec::<(i32, i32)>::new()"),
        T("origin", "points = [(0, 0), (0, 1)], k = 1", "k_closest(&[(0, 0), (0, 1)], 1)", "vec![(0, 0)]"),
        T("past_i32_squares", "points = [(50000, 0), (0, 46341)], k = 1", "k_closest(&[(50_000, 0), (0, 46_341)], 1)", "vec![(0, 46_341)]"),
        T("the_i32_corners", "points = [(i32::MIN, i32::MIN), (i32::MAX, i32::MAX), (0, 0)], k = 3",
          "k_closest(&[(i32::MIN, i32::MIN), (i32::MAX, i32::MAX), (0, 0)], 3)", "vec![(0, 0), (i32::MAX, i32::MAX), (i32::MIN, i32::MIN)]"),
        T("min_corner_alone", "points = [(i32::MIN, i32::MIN)], k = 1", "k_closest(&[(i32::MIN, i32::MIN)], 1)", "vec![(i32::MIN, i32::MIN)]"),
        T("circle_of_25", "points = [(3, -4), (5, 0), (-3, 4), (0, 5), (4, 3), (-5, 0)], k = 4",
          "k_closest(&[(3, -4), (5, 0), (-3, 4), (0, 5), (4, 3), (-5, 0)], 4)", "vec![(-5, 0), (-3, 4), (0, 5), (3, -4)]"),
        T("negative_x_is_not_nearer", "points = [(-3, 0), (2, 2)], k = 1 (9 > 8)", "k_closest(&[(-3, 0), (2, 2)], 1)", "vec![(2, 2)]"),
        T("k_equals_len", "points = [(5, 5), (-1, -1), (2, -2)], k = 3", "k_closest(&[(5, 5), (-1, -1), (2, -2)], 3)", "vec![(-1, -1), (2, -2), (5, 5)]"),
        T("all_same_point", "points = [(7, 7); 4], k = 2", "k_closest(&[(7, 7); 4], 2)", "vec![(7, 7), (7, 7)]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(707);
            for _ in 0..300 {
                let n = rng.below(10);
                let points: Vec<(i32, i32)> = (0..n).map(|_| (rng.int(-3, 3) as i32, rng.int(-3, 3) as i32)).collect();
                let k = rng.below(12);
                let mut want = points.clone();
                want.sort_by_key(|&(x, y)| (x * x + y * y, x, y));
                want.truncate(k);
                check!(format!("points = {points:?}, k = {k}"), k_closest(&points, k), want);
            }
        }

        #[test]
        fn scale_200k_points() {
            let mut rng = anneal_prelude::Rng::new(708);
            let points: Vec<(i32, i32)> = (0..200_000).map(|_| (rng.int(-1000, 1000) as i32, rng.int(-1000, 1000) as i32)).collect();
            let mut want = points.clone();
            want.sort_unstable_by_key(|&(x, y)| (x as i64 * x as i64 + y as i64 * y as i64, x, y));
            want.truncate(100_000);
            let got = k_closest(&points, 100_000);
            check!("200000 random points in [-1000, 1000]², k = 100000; first wrong index", got.iter().zip(&want).position(|(a, b)| a != b).or((got.len() != want.len()).then_some(got.len())), None);
        }
        """,
    ],
    wrong=dict(
        pick_min_k_times="""
            pub fn k_closest(points: &[(i32, i32)], k: usize) -> Vec<(i32, i32)> {
                let key = |&(x, y): &(i32, i32)| {
                    let (a, b) = (x.unsigned_abs() as u64, y.unsigned_abs() as u64);
                    (a * a + b * b, x, y)
                };
                let mut left = points.to_vec();
                let mut out = Vec::new();
                while out.len() < k && !left.is_empty() {
                    let best = (0..left.len()).min_by_key(|&i| key(&left[i])).unwrap();
                    out.push(left.swap_remove(best));
                }
                out
            }
        """,
        ties_in_input_order="""
            use std::cmp::Reverse;
            use std::collections::BinaryHeap;

            pub fn k_closest(points: &[(i32, i32)], k: usize) -> Vec<(i32, i32)> {
                let mut heap: BinaryHeap<Reverse<(u64, usize)>> = points
                    .iter()
                    .enumerate()
                    .map(|(i, &(x, y))| {
                        let (a, b) = (x.unsigned_abs() as u64, y.unsigned_abs() as u64);
                        Reverse((a * a + b * b, i))
                    })
                    .collect();
                let mut out = Vec::new();
                while out.len() < k {
                    let Some(Reverse((_, i))) = heap.pop() else { break };
                    out.push(points[i]);
                }
                out
            }
        """,
        i64_distance="""
            use std::collections::BinaryHeap;

            pub fn k_closest(points: &[(i32, i32)], k: usize) -> Vec<(i32, i32)> {
                if k == 0 {
                    return Vec::new();
                }
                let mut heap: BinaryHeap<(i64, i32, i32)> = BinaryHeap::new();
                for &(x, y) in points {
                    let (a, b) = (x as i64, y as i64);
                    heap.push((a * a + b * b, x, y));
                    if heap.len() > k {
                        heap.pop();
                    }
                }
                heap.into_sorted_vec().into_iter().map(|(_, x, y)| (x, y)).collect()
            }
        """,
    ),
    hints=[("approach", "Keep the k nearest points seen so far in a max-heap. A new point only matters if it beats the farthest of them, which is on top."),
           ("rust", "Push `(dist, x, y)` tuples: tuples compare field by field, so the tie rule is the key. `into_sorted_vec()` returns them ascending, nearest first."),
           ("edge case", "`(i32::MIN)² + (i32::MIN)² = 2⁶³` overflows `i64`. Square `x.unsigned_abs() as u64`.")],
    notes=("A max-heap of size k holds the k best candidates; each point costs one comparison with the top and at most one pop and push. "
           "Because the key is the whole `(distance², x, y)` tuple, the answer is unique and the heap's order is the output order. "
           "Squared distances avoid floats entirely; `u64` holds 2⁶³. Quickselect (`select_nth_unstable_by_key`) gets O(n) on average if the order of the k points didn't matter.",
           "O(n log k)", "O(k)"),
    follow_up="If the points arrived as an endless stream and you had to answer \"k closest so far\" at any moment, what would you keep?",
    related=["D1", "S5"],
))

# Checks a task schedule for the tests: the right tasks, the cooldown kept, no idle slot at the end.
SCHED_CHECK = """
use std::collections::HashMap;

/// Every way `sched` breaks the rules for `tasks` with cooldown `n` (empty when it is valid).
fn problems(tasks: &[char], n: usize, sched: &[Option<char>]) -> Vec<String> {
    let mut out = Vec::new();
    let mut want: HashMap<char, usize> = HashMap::new();
    for &c in tasks {
        *want.entry(c).or_default() += 1;
    }
    let mut got: HashMap<char, usize> = HashMap::new();
    for &c in sched.iter().flatten() {
        *got.entry(c).or_default() += 1;
    }
    if want != got {
        out.push("doesn't run each task exactly as often as it appears".to_string());
    }
    if sched.last() == Some(&None) {
        out.push("ends with an idle slot".to_string());
    }
    let mut last: HashMap<char, usize> = HashMap::new();
    for (t, slot) in sched.iter().enumerate() {
        if let Some(c) = *slot {
            if let Some(&p) = last.get(&c) {
                if t - p <= n {
                    out.push(format!("{c:?} runs at {p} and again at {t}"));
                }
            }
            last.insert(c, t);
        }
    }
    out
}
"""

SCHED_BRUTE = """
/// Breadth-first search over (tasks left, cooldown left) states: the true minimum for tiny inputs.
fn brute_least(tasks: &[char], n: usize) -> usize {
    let mut ids = tasks.to_vec();
    ids.sort_unstable();
    ids.dedup();
    let left: Vec<usize> = ids.iter().map(|c| tasks.iter().filter(|&t| t == c).count()).collect();
    let start = (left, vec![0usize; ids.len()]);
    let mut seen = std::collections::HashSet::new();
    seen.insert(start.clone());
    let mut queue = std::collections::VecDeque::from([(start, 0)]);
    while let Some(((left, wait), steps)) = queue.pop_front() {
        if left.iter().all(|&x| x == 0) {
            return steps;
        }
        // Run task `pick`, or stay idle when pick == ids.len().
        for pick in 0..=ids.len() {
            if pick < ids.len() && (left[pick] == 0 || wait[pick] > 0) {
                continue;
            }
            let mut l = left.clone();
            let mut w: Vec<usize> = wait.iter().map(|&x| x.saturating_sub(1)).collect();
            if pick < ids.len() {
                l[pick] -= 1;
                w[pick] = n;
            }
            if seen.insert((l.clone(), w.clone())) {
                queue.push_back(((l, w), steps + 1));
            }
        }
    }
    unreachable!()
}
"""


def chars(s):
    return f'"{s}".chars().collect::<Vec<char>>()'


def sched_case(name, s, n, want_len, desc=None):
    return T(name, desc or f'tasks = "{s}", n = {n}; schedule(tasks, n): (length, rule breaks)', f"(s.len(), problems(&tasks, {n}, &s))",
             f"({want_len}, Vec::<String>::new())", setup=f"let tasks = {chars(s)};\nlet s = schedule(&tasks, {n});")


P.append(dict(
    slug="task-scheduler", title="Task scheduler", level="medium", stage="heaps-at-work", source="W46",
    tags=["BinaryHeap", "VecDeque", "greedy", "HashMap"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "Uber"],
    teaches=["Counting shows the answer: `max(len, (most − 1)(n + 1) + tied)`.",
             "Building the schedule: a max-heap of ready tasks by remaining count plus a `VecDeque` of tasks cooling down.",
             "Task ids are any `char`, so count with a `HashMap`, not a `[usize; 26]`."],
    statement="""
        Each task takes one time slot. Two runs of the same task need at least `n` other slots between them
        (other tasks or idle slots). Slots run one after another, starting at 0.

        - `least_interval(tasks, n)` returns the fewest slots that run every task, idle slots included.
        - `schedule(tasks, n)` returns one such shortest schedule: `Some(task)` for a slot that runs a task, `None`
          for an idle slot. Any shortest valid schedule is accepted; it never ends with an idle slot.

        Task ids can be any `char`, not only `A`–`Z`, and there can be thousands of different ones.
    """,
    examples=[("tasks = \"AAABBB\", n = 2", "8, e.g. A B _ A B _ A B"), ("tasks = \"AAABBB\", n = 0", "6"),
              ("tasks = \"AAAAAABCDEFG\", n = 2", "16")],
    constraints=["0 ≤ tasks.len() ≤ 10⁵", "0 ≤ n ≤ 100"],
    starter="""
        pub fn least_interval(tasks: &[char], n: usize) -> usize {
            todo!()
        }

        pub fn schedule(tasks: &[char], n: usize) -> Vec<Option<char>> {
            todo!()
        }
    """,
    solution="""
        use std::collections::{BinaryHeap, HashMap, VecDeque};

        fn counts(tasks: &[char]) -> HashMap<char, usize> {
            let mut counts = HashMap::new();
            for &c in tasks {
                *counts.entry(c).or_insert(0) += 1;
            }
            counts
        }

        pub fn least_interval(tasks: &[char], n: usize) -> usize {
            let counts = counts(tasks);
            let Some(&most) = counts.values().max() else {
                return 0;
            };
            let tied = counts.values().filter(|&&c| c == most).count();
            // `most - 1` full frames of n + 1 slots, then one slot per task tied for most.
            tasks.len().max((most - 1) * (n + 1) + tied)
        }

        pub fn schedule(tasks: &[char], n: usize) -> Vec<Option<char>> {
            // Ready tasks, most runs left first.
            let mut ready: BinaryHeap<(usize, char)> = counts(tasks).into_iter().map(|(c, left)| (left, c)).collect();
            // Tasks cooling down: (first slot they may run in, runs left, id). One task starts per slot,
            // so the queue is already in time order.
            let mut cooling: VecDeque<(usize, usize, char)> = VecDeque::new();
            let mut out = Vec::with_capacity(tasks.len());
            while !ready.is_empty() || !cooling.is_empty() {
                let t = out.len();
                while let Some(&(at, left, c)) = cooling.front() {
                    if at > t {
                        break;
                    }
                    cooling.pop_front();
                    ready.push((left, c));
                }
                match ready.pop() {
                    Some((left, c)) => {
                        out.push(Some(c));
                        if left > 1 {
                            cooling.push_back((t + n + 1, left - 1, c));
                        }
                    }
                    None => out.push(None),
                }
            }
            out
        }
    """,
    use="use solution::*;\n" + SCHED_CHECK.rstrip("\n"),
    visible=[
        T("leetcode_two_tied", 'tasks = "AAABBB", n = 2', f'least_interval(&{chars("AAABBB")}, 2)', "8"),
        T("leetcode_no_cooldown", 'tasks = "AAABBB", n = 0', f'least_interval(&{chars("AAABBB")}, 0)', "6"),
        T("leetcode_one_dominant", 'tasks = "AAAAAABCDEFG", n = 2', f'least_interval(&{chars("AAAAAABCDEFG")}, 2)', "16"),
        T("leetcode_no_idle_needed", 'tasks = "ACABDB", n = 1', f'least_interval(&{chars("ACABDB")}, 1)', "6"),
        T("only_one_kind", 'tasks = "AAAA", n = 2 (A _ _ A _ _ A _ _ A)', f'least_interval(&{chars("AAAA")}, 2)', "10"),
        sched_case("schedule_aaabbb", "AAABBB", 2, 8),
        T("empty", "tasks = [], n = 3", "(least_interval(&[], 3), schedule(&[], 3))", "(0, Vec::<Option<char>>::new())"),
    ],
    hidden=[
        T("enough_kinds_to_fill_gaps", 'tasks = "AAABBBCCCDDE", n = 2', f'least_interval(&{chars("AAABBBCCCDDE")}, 2)', "12"),
        T("unicode_ids", 'tasks = "ééé🦀🦀", n = 1', f'least_interval(&{chars("ééé🦀🦀")}, 1)', "5"),
        T("lowercase_and_uppercase_differ", 'tasks = "aaZ", n = 3', f'least_interval(&{chars("aaZ")}, 3)', "5"),
        T("single_task_long_cooldown", 'tasks = "A", n = 100', f'least_interval(&{chars("A")}, 100)', "1"),
        T("twice_long_cooldown", 'tasks = "AA", n = 100', f'least_interval(&{chars("AA")}, 100)', "102"),
        sched_case("schedule_unicode", "ééé🦀🦀", 1, 5),
        sched_case("schedule_one_dominant", "AAAAAABCDEFG", 2, 16),
        sched_case("schedule_no_cooldown", "ABBA", 0, 4),
        sched_case("schedule_single_kind", "ZZZ", 3, 9),
        sched_case("schedule_many_tied", "AAABBBCCCDDE", 2, 12),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(709);
            for _ in 0..300 {
                let len = rng.below(8);
                let tasks: Vec<char> = rng.string(len, "abc").chars().collect();
                let n = rng.below(4);
                let want = brute_least(&tasks, n);
                let s = schedule(&tasks, n);
                check!(format!("tasks = {tasks:?}, n = {n}"), (least_interval(&tasks, n), s.len(), problems(&tasks, n, &s)), (want, want, Vec::<String>::new()));
            }
        }

        #[test]
        fn scale_50k_kinds() {
            // 50000 different ids (from U+10000 up), each twice.
            let ids: Vec<char> = (0..50_000).map(|i| char::from_u32(0x1_0000 + i).unwrap()).collect();
            let tasks: Vec<char> = ids.iter().chain(ids.iter()).copied().collect();
            let s = schedule(&tasks, 3);
            check!("tasks = 50000 different ids, each twice, n = 3", (least_interval(&tasks, 3), s.len(), problems(&tasks, 3, &s)), (100_000, 100_000, Vec::<String>::new()));
        }

        #[test]
        fn scale_one_kind_many_times() {
            let tasks = vec!['x'; 1000];
            let s = schedule(&tasks, 100);
            check!("tasks = 'x' × 1000, n = 100", (least_interval(&tasks, 100), s.len(), problems(&tasks, 100, &s)), (100_900, 100_900, Vec::<String>::new()));
        }
        """ + SCHED_BRUTE,
    ],
    wrong=dict(
        fixed_alphabet="""
            fn counts(tasks: &[char]) -> [usize; 26] {
                let mut counts = [0; 26];
                for &c in tasks {
                    counts[(c as u8 - b'A') as usize] += 1;
                }
                counts
            }

            pub fn least_interval(tasks: &[char], n: usize) -> usize {
                let counts = counts(tasks);
                let most = *counts.iter().max().unwrap();
                if most == 0 {
                    return 0;
                }
                let tied = counts.iter().filter(|&&c| c == most).count();
                tasks.len().max((most - 1) * (n + 1) + tied)
            }

            pub fn schedule(tasks: &[char], n: usize) -> Vec<Option<char>> {
                let mut left = counts(tasks);
                let mut next_ok = [0usize; 26];
                let mut out = Vec::new();
                let mut remaining = tasks.len();
                while remaining > 0 {
                    let t = out.len();
                    let pick = (0..26).filter(|&i| left[i] > 0 && next_ok[i] <= t).max_by_key(|&i| left[i]);
                    match pick {
                        Some(i) => {
                            left[i] -= 1;
                            remaining -= 1;
                            next_ok[i] = t + n + 1;
                            out.push(Some((b'A' + i as u8) as char));
                        }
                        None => out.push(None),
                    }
                }
                out
            }
        """,
        formula_without_len="""
            use std::collections::{BinaryHeap, HashMap, VecDeque};

            fn counts(tasks: &[char]) -> HashMap<char, usize> {
                let mut counts = HashMap::new();
                for &c in tasks {
                    *counts.entry(c).or_insert(0) += 1;
                }
                counts
            }

            pub fn least_interval(tasks: &[char], n: usize) -> usize {
                let counts = counts(tasks);
                let Some(&most) = counts.values().max() else {
                    return 0;
                };
                let tied = counts.values().filter(|&&c| c == most).count();
                (most - 1) * (n + 1) + tied
            }

            pub fn schedule(tasks: &[char], n: usize) -> Vec<Option<char>> {
                let mut ready: BinaryHeap<(usize, char)> = counts(tasks).into_iter().map(|(c, left)| (left, c)).collect();
                let mut cooling: VecDeque<(usize, usize, char)> = VecDeque::new();
                let mut out = Vec::new();
                while !ready.is_empty() || !cooling.is_empty() {
                    let t = out.len();
                    while let Some(&(at, left, c)) = cooling.front() {
                        if at > t {
                            break;
                        }
                        cooling.pop_front();
                        ready.push((left, c));
                    }
                    match ready.pop() {
                        Some((left, c)) => {
                            out.push(Some(c));
                            if left > 1 {
                                cooling.push_back((t + n + 1, left - 1, c));
                            }
                        }
                        None => out.push(None),
                    }
                }
                out
            }
        """,
        scan_every_slot="""
            use std::collections::HashMap;

            pub fn least_interval(tasks: &[char], n: usize) -> usize {
                schedule(tasks, n).len()
            }

            pub fn schedule(tasks: &[char], n: usize) -> Vec<Option<char>> {
                let mut counts: HashMap<char, usize> = HashMap::new();
                for &c in tasks {
                    *counts.entry(c).or_insert(0) += 1;
                }
                // (runs left, first slot it may run in, id)
                let mut state: Vec<(usize, usize, char)> = counts.into_iter().map(|(c, k)| (k, 0, c)).collect();
                let mut remaining = tasks.len();
                let mut out = Vec::new();
                while remaining > 0 {
                    let t = out.len();
                    let pick = (0..state.len()).filter(|&i| state[i].0 > 0 && state[i].1 <= t).max_by_key(|&i| state[i].0);
                    match pick {
                        Some(i) => {
                            state[i].0 -= 1;
                            state[i].1 = t + n + 1;
                            remaining -= 1;
                            out.push(Some(state[i].2));
                        }
                        None => out.push(None),
                    }
                }
                out
            }
        """,
    ),
    hints=[("approach", "The most frequent task sets the frame: `most − 1` gaps of `n + 1` slots, plus one slot per task tied for most. With enough different tasks there are no idles at all."),
           ("rust", "For the schedule: a `BinaryHeap<(usize, char)>` of ready tasks by runs left, and a `VecDeque` of `(ready_at, left, id)` for tasks cooling down. Each slot, move ready ones back, then pop."),
           ("edge case", "Ids aren't limited to `A`–`Z`; `c as u8 - b'A'` panics on `'é'`. And never finish on an idle slot.")],
    notes=("Counting: the most frequent task needs `most − 1` gaps of `n + 1` slots, and the tasks tied with it fill the last frame; other tasks fit in "
           "the gaps, and if they overflow them no idle is needed at all, so the answer is `max(len, (most − 1)(n + 1) + tied)`. The schedule comes "
           "from the greedy \"run the ready task with the most runs left\": the heap holds ready tasks, the queue holds cooling ones in the order they "
           "wake up. Each slot costs O(log k) for k different tasks.", "O(len) to count, O(T log k) to schedule T slots", "O(k)"),
    follow_up="If tasks had to run in their given order (only idles may be inserted), how would the answer change?",
    related=["D8", "S5", "S4"],
))

REORG_CHECK = """
/// "ok" if `got` is a rearrangement of `s` with no two equal neighbours, otherwise what's wrong.
fn verdict(s: &str, got: Option<String>) -> String {
    let Some(t) = got else {
        return "None".to_string();
    };
    let (mut a, mut b): (Vec<char>, Vec<char>) = (s.chars().collect(), t.chars().collect());
    if let Some(i) = b.windows(2).position(|w| w[0] == w[1]) {
        return format!("{t:?} has {:?} twice in a row at char {i}", b[i]);
    }
    a.sort_unstable();
    b.sort_unstable();
    if a != b {
        return format!("{t:?} is not a rearrangement of the input");
    }
    "ok".to_string()
}
"""


def reorg_case(name, s, desc=None):
    return T(name, desc or f's = "{s}" (any valid answer)', f'verdict("{s}", reorganize("{s}"))', '"ok"')


P.append(dict(
    slug="reorganize-string", title="Reorganize string", level="medium", stage="heaps-at-work", tags=["BinaryHeap", "greedy", "chars"],
    companies=["Amazon", "Google", "Meta", "Microsoft", "Uber"],
    teaches=["Greedy with a heap of `(count, char)`: place the most frequent character that isn't the one just placed.",
             "Hold the last character out of the heap for one step instead of popping twice.",
             "Work in `char`s: a byte-level shuffle can split a UTF-8 sequence."],
    statement="""
        Rearrange the characters of `s` so that no two neighbours are equal, and return the result.
        Return `None` if no such arrangement exists. When several exist, any of them is accepted.

        `s` can hold any Unicode characters; rearrange whole characters, not bytes.
    """,
    examples=[("s = \"aab\"", "Some(\"aba\")"), ("s = \"aaab\"", "None")],
    constraints=["0 ≤ s.chars().count() ≤ 2·10⁵"],
    starter="""
        pub fn reorganize(s: &str) -> Option<String> {
            todo!()
        }
    """,
    solution="""
        use std::collections::{BinaryHeap, HashMap};

        pub fn reorganize(s: &str) -> Option<String> {
            let mut counts: HashMap<char, usize> = HashMap::new();
            for c in s.chars() {
                *counts.entry(c).or_insert(0) += 1;
            }
            let mut heap: BinaryHeap<(usize, char)> = counts.into_iter().map(|(c, k)| (k, c)).collect();
            let mut out = String::with_capacity(s.len());
            // The character just placed sits out one step so it can't come next.
            let mut held: Option<(usize, char)> = None;
            while let Some((k, c)) = heap.pop() {
                out.push(c);
                if let Some(h) = held.take() {
                    heap.push(h);
                }
                if k > 1 {
                    held = Some((k - 1, c));
                }
            }
            // Copies still held at the end had nothing to separate them.
            held.is_none().then_some(out)
        }
    """,
    use="use solution::*;\n" + REORG_CHECK.rstrip("\n"),
    visible=[
        T("leetcode_aab", 's = "aab"', 'reorganize("aab")', 'Some("aba".to_string())'),
        T("leetcode_impossible", 's = "aaab"', 'reorganize("aaab")', "None"),
        T("empty", 's = ""', 'reorganize("")', 'Some(String::new())'),
        T("single", 's = "a"', 'reorganize("a")', 'Some("a".to_string())'),
        reorg_case("any_valid_answer", "aabb"),
        T("just_possible", 's = "aaabb" (3 a in 5 chars still fits)', 'reorganize("aaabb")', 'Some("ababa".to_string())'),
        T("unicode_chars", 's = "ééa"', 'reorganize("ééa")', 'Some("éaé".to_string())'),
    ],
    hidden=[
        T("pair_of_same", 's = "aa"', 'reorganize("aa")', "None"),
        reorg_case("pair_of_different", "ab"),
        reorg_case("three_kinds", "aaabbbccc"),
        reorg_case("crabs_and_spaces", "🦀🦀 🦀 x"),
        reorg_case("case_matters", "aAaA"),
        T("half_plus_one", 's = "aaaabbb" (4 of 7)', 'reorganize("aaaabbb")', 'Some("abababa".to_string())'),
        T("too_many_by_one", 's = "aaaabb" (4 of 6)', 'reorganize("aaaabb")', "None"),
        T("unicode_impossible", 's = "日日日本"', 'reorganize("日日日本")', "None"),
        reorg_case("mostly_one", "vvvvvabcd"),
        """
        #[test]
        fn random_vs_brute_force() {
            // Is there any arrangement? Backtracking over counts is the brute force.
            fn possible(counts: &mut [usize], last: Option<usize>, left: usize) -> bool {
                if left == 0 {
                    return true;
                }
                for i in 0..counts.len() {
                    if counts[i] > 0 && Some(i) != last {
                        counts[i] -= 1;
                        let ok = possible(counts, Some(i), left - 1);
                        counts[i] += 1;
                        if ok {
                            return true;
                        }
                    }
                }
                false
            }
            let mut rng = anneal_prelude::Rng::new(710);
            for _ in 0..300 {
                let len = rng.below(9);
                let s = rng.string(len, "abé");
                let mut counts: Vec<usize> = ['a', 'b', 'é'].iter().map(|&c| s.chars().filter(|&x| x == c).count()).collect();
                let got = reorganize(&s);
                let want = if possible(&mut counts, None, len) { "ok" } else { "None" };
                check!(format!("s = {s:?}"), verdict(&s, got), want);
            }
        }

        #[test]
        fn scale_50k_kinds() {
            // 20000 kinds five times each, 30000 more kinds once or twice, and 30000 copies of 'x'.
            let mut s: String = (0..100_000).map(|i| char::from_u32(0x4E00 + i % 20_000).unwrap()).collect();
            s.extend((0..50_000).map(|i| char::from_u32(0x1_0000 + i % 30_000).unwrap()));
            s.push_str(&"x".repeat(30_000));
            check!("s = 180000 chars of 50001 kinds, 30000 of them 'x'", verdict(&s, reorganize(&s)), "ok");
        }

        #[test]
        fn scale_two_kinds_exactly_half() {
            let s = "ab".repeat(50_000) + "a";
            let want = "ab".repeat(50_000) + "a";
            check!("s = \\"ab\\" × 50000 + \\"a\\" (only one answer)", reorganize(&s) == Some(want), true);
        }
        """,
    ],
    wrong=dict(
        bytes_not_chars="""
            pub fn reorganize(s: &str) -> Option<String> {
                let mut counts = [0usize; 256];
                for b in s.bytes() {
                    counts[b as usize] += 1;
                }
                let mut out: Vec<u8> = Vec::with_capacity(s.len());
                let mut last: Option<u8> = None;
                for _ in 0..s.len() {
                    let pick = (0..256).filter(|&b| counts[b] > 0 && Some(b as u8) != last).max_by_key(|&b| counts[b])?;
                    counts[pick] -= 1;
                    out.push(pick as u8);
                    last = Some(pick as u8);
                }
                Some(String::from_utf8_lossy(&out).into_owned())
            }
        """,
        half_bound_off_by_one="""
            use std::collections::{BinaryHeap, HashMap};

            pub fn reorganize(s: &str) -> Option<String> {
                let mut counts: HashMap<char, usize> = HashMap::new();
                for c in s.chars() {
                    *counts.entry(c).or_insert(0) += 1;
                }
                let len = s.chars().count();
                if counts.values().any(|&k| k > len / 2) && len > 1 {
                    return None;
                }
                let mut heap: BinaryHeap<(usize, char)> = counts.into_iter().map(|(c, k)| (k, c)).collect();
                let mut out = String::new();
                let mut held: Option<(usize, char)> = None;
                while let Some((k, c)) = heap.pop() {
                    out.push(c);
                    if let Some(h) = held.take() {
                        heap.push(h);
                    }
                    if k > 1 {
                        held = Some((k - 1, c));
                    }
                }
                Some(out)
            }
        """,
        scan_for_most="""
            use std::collections::HashMap;

            pub fn reorganize(s: &str) -> Option<String> {
                let mut counts: HashMap<char, usize> = HashMap::new();
                for c in s.chars() {
                    *counts.entry(c).or_insert(0) += 1;
                }
                let mut left: Vec<(char, usize)> = counts.into_iter().collect();
                let mut out = String::new();
                let mut last = None;
                for _ in 0..s.chars().count() {
                    let i = (0..left.len()).filter(|&i| left[i].1 > 0 && Some(left[i].0) != last).max_by_key(|&i| left[i].1)?;
                    left[i].1 -= 1;
                    out.push(left[i].0);
                    last = Some(left[i].0);
                }
                Some(out)
            }
        """,
    ),
    hints=[("approach", "Always place the most frequent remaining character, unless it's the one you just placed; then place the runner-up."),
           ("rust", "A `BinaryHeap<(usize, char)>` orders by count first. Pop one, push back the previously held one, and hold the popped one (count − 1) for a step."),
           ("edge case", "It's impossible exactly when some character appears more than `(len + 1) / 2` times, where `len` counts chars, not bytes.")],
    notes=("Placing the most frequent available character keeps the worst offender from piling up at the end. Holding the last placed character "
           "out of the heap for one step enforces the neighbour rule without a second pop. If a character is still held when the heap runs dry, "
           "no arrangement exists, which happens exactly when its count exceeds `(len + 1) / 2`. An O(len) alternative fills even positions with the "
           "most frequent character first, then the odd ones.", "O(len log k) for k different characters", "O(k)"),
    follow_up="Rearrange so equal characters are at least `d` apart. What changes in the heap loop?",
    related=["S2", "D8"],
))

P.append(dict(
    slug="merge-k-sorted-arrays", title="Merge k sorted arrays", level="medium", stage="heaps-at-work", tags=["BinaryHeap", "Reverse", "k-way merge"],
    companies=["Amazon", "Google", "Microsoft", "Meta"],
    teaches=["A k-way merge keeps one candidate per array in a min-heap of `Reverse((value, array, index))`.",
             "Tuple fields after the value say where the next candidate comes from.",
             "Merging arrays one by one into an accumulator is O(N·k); the heap is O(N log k)."],
    statement="""
        Every array in `arrays` is sorted ascending. Return all their values in one ascending `Vec`, duplicates included.
        Arrays may be empty, and there may be no arrays at all.
    """,
    examples=[("arrays = [[1, 4, 5], [1, 3, 4], [2, 6]]", "[1, 1, 2, 3, 4, 4, 5, 6]"), ("arrays = []", "[]")],
    constraints=["0 ≤ arrays.len() ≤ 2·10⁴", "total length N ≤ 2·10⁵", "values are any i32"],
    starter="""
        pub fn merge_k_sorted(arrays: &[Vec<i32>]) -> Vec<i32> {
            todo!()
        }
    """,
    solution="""
        use std::cmp::Reverse;
        use std::collections::BinaryHeap;

        pub fn merge_k_sorted(arrays: &[Vec<i32>]) -> Vec<i32> {
            let total = arrays.iter().map(Vec::len).sum();
            let mut out = Vec::with_capacity(total);
            // One candidate per array: (value, which array, index in it).
            let mut heap: BinaryHeap<Reverse<(i32, usize, usize)>> =
                arrays.iter().enumerate().filter_map(|(a, v)| v.first().map(|&x| Reverse((x, a, 0)))).collect();
            while let Some(Reverse((x, a, i))) = heap.pop() {
                out.push(x);
                if let Some(&next) = arrays[a].get(i + 1) {
                    heap.push(Reverse((next, a, i + 1)));
                }
            }
            out
        }
    """,
    visible=[
        T("leetcode_example", "arrays = [[1, 4, 5], [1, 3, 4], [2, 6]]", "merge_k_sorted(&[vec![1, 4, 5], vec![1, 3, 4], vec![2, 6]])", "vec![1, 1, 2, 3, 4, 4, 5, 6]"),
        T("no_arrays", "arrays = []", "merge_k_sorted(&[])", "Vec::<i32>::new()"),
        T("one_empty_array", "arrays = [[]]", "merge_k_sorted(&[vec![]])", "Vec::<i32>::new()"),
        T("empty_arrays_skipped", "arrays = [[], [3], [], [1, 2]]", "merge_k_sorted(&[vec![], vec![3], vec![], vec![1, 2]])", "vec![1, 2, 3]"),
        T("duplicates_kept", "arrays = [[2, 2], [2]]", "merge_k_sorted(&[vec![2, 2], vec![2]])", "vec![2, 2, 2]"),
        T("negatives", "arrays = [[-5, 0], [-7, -1, 8]]", "merge_k_sorted(&[vec![-5, 0], vec![-7, -1, 8]])", "vec![-7, -5, -1, 0, 8]"),
    ],
    hidden=[
        T("single_array", "arrays = [[1, 2, 3]]", "merge_k_sorted(&[vec![1, 2, 3]])", "vec![1, 2, 3]"),
        T("extremes", "arrays = [[i32::MIN, i32::MAX], [0], [i32::MIN]]", "merge_k_sorted(&[vec![i32::MIN, i32::MAX], vec![0], vec![i32::MIN]])", "vec![i32::MIN, i32::MIN, 0, i32::MAX]"),
        T("disjoint_ranges", "arrays = [[7, 8, 9], [1, 2, 3], [4, 5, 6]]", "merge_k_sorted(&[vec![7, 8, 9], vec![1, 2, 3], vec![4, 5, 6]])", "vec![1, 2, 3, 4, 5, 6, 7, 8, 9]"),
        T("interleaved", "arrays = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]", "merge_k_sorted(&[vec![1, 4, 7], vec![2, 5, 8], vec![3, 6, 9]])", "vec![1, 2, 3, 4, 5, 6, 7, 8, 9]"),
        T("very_different_lengths", "arrays = [[5], 0..10, [-1]]", "merge_k_sorted(&[vec![5], (0..10).collect(), vec![-1]])", "vec![-1, 0, 1, 2, 3, 4, 5, 5, 6, 7, 8, 9]"),
        T("all_equal", "arrays = [[0, 0], [0], [0, 0, 0]]", "merge_k_sorted(&[vec![0, 0], vec![0], vec![0, 0, 0]])", "vec![0; 6]"),
        T("many_empty", "arrays = 1000 empty arrays", "merge_k_sorted(&vec![Vec::new(); 1000])", "Vec::<i32>::new()"),
        T("last_array_holds_the_minimum", "arrays = [[2], [3], [1]]", "merge_k_sorted(&[vec![2], vec![3], vec![1]])", "vec![1, 2, 3]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(711);
            for _ in 0..300 {
                let k = rng.below(6);
                let mut arrays: Vec<Vec<i32>> = Vec::new();
                for _ in 0..k {
                    let len = rng.below(6);
                    let mut v: Vec<i32> = rng.vec(len, -10, 10);
                    v.sort_unstable();
                    arrays.push(v);
                }
                let mut want: Vec<i32> = arrays.concat();
                want.sort_unstable();
                check!(format!("arrays = {arrays:?}"), merge_k_sorted(&arrays), want);
            }
        }

        #[test]
        fn scale_20k_arrays() {
            let mut rng = anneal_prelude::Rng::new(712);
            let arrays: Vec<Vec<i32>> = (0..20_000)
                .map(|_| {
                    let mut v: Vec<i32> = rng.vec(10, -1_000_000, 1_000_000);
                    v.sort_unstable();
                    v
                })
                .collect();
            let mut want = arrays.concat();
            want.sort_unstable();
            check!("20000 sorted arrays of 10 random values", merge_k_sorted(&arrays) == want, true);
        }
        """,
    ],
    wrong=dict(
        merge_one_at_a_time="""
            pub fn merge_k_sorted(arrays: &[Vec<i32>]) -> Vec<i32> {
                let mut acc: Vec<i32> = Vec::new();
                for v in arrays {
                    let mut merged = Vec::with_capacity(acc.len() + v.len());
                    let (mut i, mut j) = (0, 0);
                    while i < acc.len() || j < v.len() {
                        if j == v.len() || (i < acc.len() && acc[i] <= v[j]) {
                            merged.push(acc[i]);
                            i += 1;
                        } else {
                            merged.push(v[j]);
                            j += 1;
                        }
                    }
                    acc = merged;
                }
                acc
            }
        """,
        scan_all_heads="""
            pub fn merge_k_sorted(arrays: &[Vec<i32>]) -> Vec<i32> {
                let mut pos = vec![0; arrays.len()];
                let mut out = Vec::new();
                loop {
                    let best = (0..arrays.len()).filter(|&a| pos[a] < arrays[a].len()).min_by_key(|&a| arrays[a][pos[a]]);
                    let Some(a) = best else { break };
                    out.push(arrays[a][pos[a]]);
                    pos[a] += 1;
                }
                out
            }
        """,
        forgot_reverse="""
            use std::collections::BinaryHeap;

            pub fn merge_k_sorted(arrays: &[Vec<i32>]) -> Vec<i32> {
                let mut out = Vec::new();
                let mut heap: BinaryHeap<(i32, usize, usize)> =
                    arrays.iter().enumerate().filter_map(|(a, v)| v.first().map(|&x| (x, a, 0))).collect();
                while let Some((x, a, i)) = heap.pop() {
                    out.push(x);
                    if let Some(&next) = arrays[a].get(i + 1) {
                        heap.push((next, a, i + 1));
                    }
                }
                out
            }
        """,
    ),
    hints=[("approach", "The next output is the smallest of the k array heads. Keep the heads in a min-heap; after popping one, push its array's next value."),
           ("rust", "`BinaryHeap<Reverse<(i32, usize, usize)>>`: value first so it decides the order, then the array and the index to continue from."),
           ("edge case", "Seed the heap only from non-empty arrays: `v.first().map(...)` inside `filter_map`.")],
    notes=("The heap never holds more than one value per array, so each of the N outputs costs O(log k). Merging arrays into an accumulator one "
           "after another re-copies the accumulator k times: O(N·k). Concatenating and sorting is O(N log N) and fine in memory; the heap "
           "version is the one that also works when the arrays are streams (see External merge sort).", "O(N log k)", "O(k) besides the output"),
    follow_up="How would you merge pairwise, like merge sort's merge tree, and what does that cost?",
    related=["D5", "S5"],
))

P.append(dict(
    slug="top-k-frequent-words", title="Top K frequent words", level="medium", stage="heaps-at-work",
    tags=["BinaryHeap", "Reverse", "custom order", "&str"],
    companies=["Amazon", "Meta", "Google", "Microsoft", "Bloomberg", "Uber"],
    teaches=["`(Reverse(count), word)` puts \"worse\" on top of a max-heap: lower count, then later word.",
             "A size-k heap is O(n log k) instead of sorting every distinct word.",
             "Return `&'a str` slices of the input instead of new `String`s."],
    statement="""
        Return the `k` most frequent words, most frequent first. Words with the same count come in lexicographic
        order (`str`'s own `Ord`, which compares bytes: `"B" < "a" < "é"`). If there are fewer than `k` different
        words, return them all.
    """,
    examples=[("words = [\"i\", \"love\", \"leetcode\", \"i\", \"love\", \"coding\"], k = 2", "[\"i\", \"love\"]"),
              ("words = [\"the\", \"day\", \"is\", \"sunny\", \"the\", \"the\", \"the\", \"sunny\", \"is\", \"is\"], k = 4", "[\"the\", \"is\", \"sunny\", \"day\"]")],
    constraints=["0 ≤ words.len() ≤ 5·10⁵", "0 ≤ k"],
    starter="""
        pub fn top_k_frequent<'a>(words: &[&'a str], k: usize) -> Vec<&'a str> {
            todo!()
        }
    """,
    solution="""
        use std::cmp::Reverse;
        use std::collections::{BinaryHeap, HashMap};

        pub fn top_k_frequent<'a>(words: &[&'a str], k: usize) -> Vec<&'a str> {
            let mut counts: HashMap<&'a str, usize> = HashMap::new();
            for &w in words {
                *counts.entry(w).or_insert(0) += 1;
            }
            // Max-heap on (Reverse(count), word): the top is the worst kept word,
            // i.e. the lowest count, and among equal counts the latest word.
            let mut heap: BinaryHeap<(Reverse<usize>, &'a str)> = BinaryHeap::with_capacity(k + 1);
            for (w, c) in counts {
                heap.push((Reverse(c), w));
                if heap.len() > k {
                    heap.pop();
                }
            }
            // Ascending order of (Reverse(count), word) is the answer's order.
            heap.into_sorted_vec().into_iter().map(|(_, w)| w).collect()
        }
    """,
    visible=[
        T("leetcode_two", 'words = ["i", "love", "leetcode", "i", "love", "coding"], k = 2',
          'top_k_frequent(&["i", "love", "leetcode", "i", "love", "coding"], 2)', 'vec!["i", "love"]'),
        T("leetcode_four", 'words = ["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"], k = 4',
          'top_k_frequent(&["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"], 4)', 'vec!["the", "is", "sunny", "day"]'),
        T("ties_alphabetical", 'words = ["b", "c", "a"], k = 2', 'top_k_frequent(&["b", "c", "a"], 2)', 'vec!["a", "b"]'),
        T("empty", "words = [], k = 3", "top_k_frequent(&[], 3)", "Vec::<&str>::new()"),
        T("k_zero", 'words = ["a"], k = 0', 'top_k_frequent(&["a"], 0)', "Vec::<&str>::new()"),
        T("fewer_words_than_k", 'words = ["x", "y", "x"], k = 5', 'top_k_frequent(&["x", "y", "x"], 5)', 'vec!["x", "y"]'),
    ],
    hidden=[
        T("uppercase_sorts_first", 'words = ["b", "B", "a"], k = 3', 'top_k_frequent(&["b", "B", "a"], 3)', 'vec!["B", "a", "b"]'),
        T("accent_after_z", 'words = ["é", "z"], k = 2', 'top_k_frequent(&["é", "z"], 2)', 'vec!["z", "é"]'),
        T("prefixes_first", 'words = ["abc", "a", "ab"], k = 3', 'top_k_frequent(&["abc", "a", "ab"], 3)', 'vec!["a", "ab", "abc"]'),
        T("count_beats_alphabet", 'words = ["z", "a", "z"], k = 1', 'top_k_frequent(&["z", "a", "z"], 1)', 'vec!["z"]'),
        T("tie_at_the_cut", 'words = ["d", "c", "b", "a", "e", "e"], k = 3', 'top_k_frequent(&["d", "c", "b", "a", "e", "e"], 3)', 'vec!["e", "a", "b"]'),
        T("empty_word", 'words = ["", "a", ""], k = 2', 'top_k_frequent(&["", "a", ""], 2)', 'vec!["", "a"]'),
        T("one_word_many_times", 'words = ["same"; 1000], k = 1', 'top_k_frequent(&vec!["same"; 1000], 1)', 'vec!["same"]'),
        T("returns_slices_of_the_input", 'words = [s, s] where s is a String, k = 1', "top_k_frequent(&[s.as_str(), s.as_str()], 1)[0].as_ptr() == s.as_ptr()", "true",
          setup='let s = String::from("borrowed");'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(713);
            let pool = ["a", "b", "ab", "B", "é", "ba", ""];
            for _ in 0..300 {
                let n = rng.below(12);
                let words: Vec<&str> = (0..n).map(|_| *rng.pick(&pool)).collect();
                let k = rng.below(8);
                let mut distinct = words.clone();
                distinct.sort_unstable();
                distinct.dedup();
                let count = |w: &str| words.iter().filter(|&&x| x == w).count();
                distinct.sort_by(|a, b| count(b).cmp(&count(a)).then(a.cmp(b)));
                distinct.truncate(k);
                check!(format!("words = {words:?}, k = {k}"), top_k_frequent(&words, k), distinct);
            }
        }

        #[test]
        fn scale_100k_distinct_words() {
            let names: Vec<String> = (0..100_000).map(|i| format!("w{:05}", (i * 7919) % 100_000)).collect();
            let mut words: Vec<&str> = Vec::new();
            for (i, w) in names.iter().enumerate() {
                for _ in 0..(i % 4) + 1 {
                    words.push(w);
                }
            }
            let mut want: Vec<(usize, &str)> = names.iter().enumerate().map(|(i, w)| ((i % 4) + 1, w.as_str())).collect();
            want.sort_unstable_by(|a, b| b.0.cmp(&a.0).then(a.1.cmp(b.1)));
            let want: Vec<&str> = want.into_iter().take(50_000).map(|(_, w)| w).collect();
            check!("100000 different words appearing 1–4 times (250000 words), k = 50000", top_k_frequent(&words, 50_000) == want, true);
        }
        """,
    ],
    wrong=dict(
        ties_evict_the_wrong_word="""
            use std::cmp::Reverse;
            use std::collections::{BinaryHeap, HashMap};

            pub fn top_k_frequent<'a>(words: &[&'a str], k: usize) -> Vec<&'a str> {
                let mut counts: HashMap<&'a str, usize> = HashMap::new();
                for &w in words {
                    *counts.entry(w).or_insert(0) += 1;
                }
                // Min-heap on (count, word): pops the lowest count, but on ties the *earliest* word.
                let mut heap: BinaryHeap<Reverse<(usize, &'a str)>> = BinaryHeap::new();
                for (w, c) in counts {
                    heap.push(Reverse((c, w)));
                    if heap.len() > k {
                        heap.pop();
                    }
                }
                let mut out: Vec<(usize, &str)> = heap.into_iter().map(|Reverse(x)| x).collect();
                out.sort_by(|a, b| b.0.cmp(&a.0).then(a.1.cmp(b.1)));
                out.into_iter().map(|(_, w)| w).collect()
            }
        """,
        sort_by_count_only="""
            use std::collections::HashMap;

            pub fn top_k_frequent<'a>(words: &[&'a str], k: usize) -> Vec<&'a str> {
                let mut counts: HashMap<&'a str, usize> = HashMap::new();
                for &w in words {
                    *counts.entry(w).or_insert(0) += 1;
                }
                let mut all: Vec<(&'a str, usize)> = counts.into_iter().collect();
                all.sort_by(|a, b| b.1.cmp(&a.1));
                all.into_iter().take(k).map(|(w, _)| w).collect()
            }
        """,
        pick_best_k_times="""
            use std::collections::HashMap;

            pub fn top_k_frequent<'a>(words: &[&'a str], k: usize) -> Vec<&'a str> {
                let mut counts: HashMap<&'a str, usize> = HashMap::new();
                for &w in words {
                    *counts.entry(w).or_insert(0) += 1;
                }
                let mut left: Vec<(&'a str, usize)> = counts.into_iter().collect();
                let mut out = Vec::new();
                while out.len() < k && !left.is_empty() {
                    let mut best = 0;
                    for i in 1..left.len() {
                        if left[i].1 > left[best].1 || (left[i].1 == left[best].1 && left[i].0 < left[best].0) {
                            best = i;
                        }
                    }
                    out.push(left.swap_remove(best).0);
                }
                out
            }
        """,
    ),
    hints=[("approach", "Count with a `HashMap`, then keep only the k best words in a heap whose top is the worst of them."),
           ("rust", "\"Worse\" means lower count, or the same count and a later word. `(Reverse(count), word)` in a max-heap orders exactly that way, and `into_sorted_vec()` then lists best first."),
           ("edge case", "Equal counts at the cut-off: the word that stays is the lexicographically smaller one.")],
    notes=("The heap holds at most k entries and its top is the one to evict. Wrapping only the count in `Reverse` makes the tuple compare "
           "counts descending but words ascending, so one derived tuple order encodes the whole rule; no custom `Ord` impl needed. The map's keys "
           "are the input's `&'a str`, so nothing is copied.", "O(n + d log k) for d different words", "O(d)"),
    follow_up="How would you answer this for a stream of words that never ends, with k fixed?",
    related=["D1", "S4", "L3"],
))

# ---------------------------------------------------------------- two heaps & merges (hard)

MEDIAN_SOLUTION = """
    use std::cmp::Reverse;
    use std::collections::{BinaryHeap, HashMap};

    #[derive(Default)]
    pub struct MedianFinder {
        /// The smaller half, largest on top.
        low: BinaryHeap<i32>,
        /// The larger half, smallest on top.
        high: BinaryHeap<Reverse<i32>>,
        /// Live sizes of the halves (the heaps may also hold removed copies).
        low_len: usize,
        high_len: usize,
        /// Copies of each value still in the stream.
        live: HashMap<i32, usize>,
        /// Removed copies still sitting inside a heap, dropped when they reach a top.
        doomed: HashMap<i32, usize>,
    }

    impl MedianFinder {
        pub fn new() -> Self {
            Self::default()
        }

        pub fn add_num(&mut self, num: i32) {
            *self.live.entry(num).or_insert(0) += 1;
            if self.low.peek().is_none_or(|&top| num <= top) {
                self.low.push(num);
                self.low_len += 1;
            } else {
                self.high.push(Reverse(num));
                self.high_len += 1;
            }
            self.rebalance();
        }

        pub fn remove_num(&mut self, num: i32) -> bool {
            match self.live.get_mut(&num) {
                Some(c) => {
                    *c -= 1;
                    if *c == 0 {
                        self.live.remove(&num);
                    }
                }
                None => return false,
            }
            *self.doomed.entry(num).or_insert(0) += 1;
            // Tops are always live, so this says which half the copy belongs to.
            if self.low.peek().is_some_and(|&top| num <= top) {
                self.low_len -= 1;
            } else {
                self.high_len -= 1;
            }
            self.prune();
            self.rebalance();
            true
        }

        /// `&self` works because every mutation leaves both tops live.
        pub fn find_median(&self) -> Option<f64> {
            let &lo = self.low.peek()?;
            if self.low_len > self.high_len {
                return Some(lo as f64);
            }
            let &Reverse(hi) = self.high.peek()?;
            // In f64, not i32: i32::MAX + i32::MAX overflows.
            Some((lo as f64 + hi as f64) / 2.0)
        }

        fn take_doomed(&mut self, v: i32) -> bool {
            match self.doomed.get_mut(&v) {
                Some(c) => {
                    *c -= 1;
                    if *c == 0 {
                        self.doomed.remove(&v);
                    }
                    true
                }
                None => false,
            }
        }

        /// Pops removed copies off both tops.
        fn prune(&mut self) {
            while let Some(&top) = self.low.peek() {
                if !self.take_doomed(top) {
                    break;
                }
                self.low.pop();
            }
            while let Some(&Reverse(top)) = self.high.peek() {
                if !self.take_doomed(top) {
                    break;
                }
                self.high.pop();
            }
        }

        /// Keeps low_len == high_len or low_len == high_len + 1.
        fn rebalance(&mut self) {
            if self.low_len > self.high_len + 1 {
                if let Some(x) = self.low.pop() {
                    self.high.push(Reverse(x));
                    self.low_len -= 1;
                    self.high_len += 1;
                }
                self.prune();
            } else if self.high_len > self.low_len {
                if let Some(Reverse(x)) = self.high.pop() {
                    self.low.push(x);
                    self.high_len -= 1;
                    self.low_len += 1;
                }
                self.prune();
            }
        }
    }
"""


def ops(setup_ops):
    """Rust statements for a sequence like "add 1; add 2; remove 1" on `m`."""
    lines = ["let mut m = MedianFinder::new();"]
    for op in setup_ops.split("; "):
        verb, arg = op.split(" ", 1)
        lines.append(f"m.{'add_num' if verb == 'add' else 'remove_num'}({arg});")
    return "\n".join(lines)


P.append(dict(
    slug="find-median-from-data-stream", title="Find median from data stream", level="hard", stage="two-heaps-merges",
    tags=["two heaps", "lazy deletion", "Reverse", "Blind 75"],
    companies=["Amazon", "Meta", "Google", "Microsoft", "Apple", "Uber", "Goldman Sachs"],
    teaches=["Two heaps: a max-heap for the smaller half and a `Reverse` min-heap for the larger half, sizes within one.",
             "Lazy deletion: `BinaryHeap` can't remove from the middle, so record the removal and drop the copy when it reaches a top.",
             "Keep both tops live after every mutation so `find_median` can take `&self`."],
    statement="""
        Build a `MedianFinder` over a multiset of numbers:

        - `add_num(num)` adds one copy of `num`;
        - `remove_num(num)` removes one copy of `num` and returns `true`, or returns `false` if there is none;
        - `find_median()` returns the median of the numbers currently held, or `None` when there are none.
          With an even count it's the mean of the two middle values (so it can end in `.5`).

        Every operation must be O(log n) amortized.
    """,
    examples=[("add 1, add 2, find_median, add 3, find_median", "Some(1.5), Some(2.0)"),
              ("add 1, add 2, add 3, remove 2, find_median", "Some(2.0)")],
    constraints=["up to 3·10⁵ operations", "values are any i32"],
    starter="""
        pub struct MedianFinder {
            // your fields
        }

        impl MedianFinder {
            pub fn new() -> Self {
                todo!()
            }

            pub fn add_num(&mut self, num: i32) {
                todo!()
            }

            pub fn remove_num(&mut self, num: i32) -> bool {
                todo!()
            }

            pub fn find_median(&self) -> Option<f64> {
                todo!()
            }
        }
    """,
    solution=MEDIAN_SOLUTION,
    visible=[
        T("leetcode_example", "add 1, add 2, find_median, add 3, find_median", "(a, m.find_median())", "(Some(1.5), Some(2.0))",
          setup="let mut m = MedianFinder::new();\nm.add_num(1);\nm.add_num(2);\nlet a = m.find_median();\nm.add_num(3);"),
        T("empty", "new, find_median", "MedianFinder::new().find_median()", "None"),
        T("remove_the_middle", "add 1, add 2, add 3, remove 2 → [1, 3]", "(removed, m.find_median())", "(true, Some(2.0))",
          setup=ops("add 1; add 2; add 3") + "\nlet removed = m.remove_num(2);"),
        T("remove_missing_value", "add 5, remove 7", "(m.remove_num(7), m.find_median())", "(false, Some(5.0))", setup=ops("add 5")),
        T("duplicates_are_copies", "add 4, add 4, add 9, remove 4 → [4, 9]", "(m.remove_num(4), m.find_median())", "(true, Some(6.5))",
          setup=ops("add 4; add 4; add 9")),
        T("large_values_average", "add i32::MAX, add i32::MAX - 2", "m.find_median()", "Some(2147483646.0)",
          setup="let mut m = MedianFinder::new();\nm.add_num(i32::MAX);\nm.add_num(i32::MAX - 2);"),
    ],
    hidden=[
        T("extremes_average", "add i32::MIN, add i32::MAX", "m.find_median()", "Some(-0.5)", setup=ops("add i32::MIN; add i32::MAX")),
        T("remove_everything", "add 3, add 1, remove 1, remove 3", "(m.find_median(), m.remove_num(3))", "(None, false)",
          setup=ops("add 3; add 1; remove 1; remove 3")),
        T("refill_after_empty", "add 2, remove 2, add 8, add 6", "m.find_median()", "Some(7.0)", setup=ops("add 2; remove 2; add 8; add 6")),
        T("same_value_on_both_sides", "add 5, add 5, remove 5, find, remove 5, find, remove 5",
          "(a, b, m.remove_num(5))", "(Some(5.0), None, false)",
          setup="let mut m = MedianFinder::new();\nm.add_num(5);\nm.add_num(5);\nm.remove_num(5);\nlet a = m.find_median();\nm.remove_num(5);\nlet b = m.find_median();"),
        T("remove_from_the_bottom", "add 1..=7, remove 1, remove 2 → [3..=7]", "m.find_median()", "Some(5.0)",
          setup=ops("add 1; add 2; add 3; add 4; add 5; add 6; add 7; remove 1; remove 2")),
        T("remove_from_the_top", "add 1..=7, remove 7, remove 6, remove 5 → [1..=4]", "m.find_median()", "Some(2.5)",
          setup=ops("add 1; add 2; add 3; add 4; add 5; add 6; add 7; remove 7; remove 6; remove 5")),
        T("negatives", "add -5, add -1, add -3, add -2", "m.find_median()", "Some(-2.5)", setup=ops("add -5; add -1; add -3; add -2")),
        T("descending_adds", "add 9, 8, 7, 6, 5", "m.find_median()", "Some(7.0)", setup=ops("add 9; add 8; add 7; add 6; add 5")),
        T("remove_twice_one_copy", "add 3, add 3, remove 3, remove 3, remove 3", "(a, b, c)", "(true, true, false)",
          setup="let mut m = MedianFinder::new();\nm.add_num(3);\nm.add_num(3);\nlet (a, b, c) = (m.remove_num(3), m.remove_num(3), m.remove_num(3));"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(714);
            for _ in 0..300 {
                let mut m = MedianFinder::new();
                let mut bag: Vec<i32> = Vec::new();
                let mut log = Vec::new();
                let steps = rng.below(30);
                for _ in 0..steps {
                    let v = rng.int(-3, 3) as i32;
                    match rng.below(5) {
                        0 | 1 => {
                            m.add_num(v);
                            bag.push(v);
                            log.push(format!("add {v}"));
                        }
                        2 => {
                            let want = bag.iter().position(|&x| x == v).map(|i| bag.swap_remove(i)).is_some();
                            log.push(format!("remove {v}"));
                            check!(log.join(", "), m.remove_num(v), want);
                        }
                        _ => {
                            let mut s = bag.clone();
                            s.sort_unstable();
                            let n = s.len();
                            let want = match n {
                                0 => None,
                                _ if n % 2 == 1 => Some(s[n / 2] as f64),
                                _ => Some((s[n / 2 - 1] as f64 + s[n / 2] as f64) / 2.0),
                            };
                            log.push("find_median".to_string());
                            check!(log.join(", "), m.find_median(), want);
                        }
                    }
                }
            }
        }

        #[test]
        fn scale_sliding_window() {
            // Reference: a Fenwick tree of counts over the values 0..2^18; k-th smallest by binary lifting.
            const N: usize = 1 << 18;
            fn bump(tree: &mut [i64], v: usize, d: i64) {
                let mut i = v + 1;
                while i <= N {
                    tree[i] += d;
                    i += i & i.wrapping_neg();
                }
            }
            fn kth(tree: &[i64], mut k: i64) -> f64 {
                let (mut pos, mut step) = (0, N);
                while step > 0 {
                    if pos + step <= N && tree[pos + step] < k {
                        pos += step;
                        k -= tree[pos];
                    }
                    step >>= 1;
                }
                pos as f64
            }
            let mut tree = vec![0i64; N + 1];
            let mut rng = anneal_prelude::Rng::new(715);
            let vals: Vec<i32> = rng.vec(150_000, 0, N as i64 - 1);
            let mut m = MedianFinder::new();
            let mut first_wrong = None;
            for (i, &v) in vals.iter().enumerate() {
                m.add_num(v);
                bump(&mut tree, v as usize, 1);
                // A window of the last 50000 values: remove the one that falls out.
                if i >= 50_000 {
                    let old = vals[i - 50_000];
                    m.remove_num(old);
                    bump(&mut tree, old as usize, -1);
                }
                let n = (i + 1).min(50_000) as i64;
                let want = if n % 2 == 1 { kth(&tree, (n + 1) / 2) } else { (kth(&tree, n / 2) + kth(&tree, n / 2 + 1)) / 2.0 };
                if m.find_median() != Some(want) && first_wrong.is_none() {
                    first_wrong = Some(i);
                }
            }
            check!("150000 random values, a window of the last 50000 (add one, remove the oldest, find_median); first step with a wrong median", first_wrong, None);
        }
        """,
    ],
    wrong=dict(
        sort_on_every_find="""
            #[derive(Default)]
            pub struct MedianFinder {
                values: Vec<i32>,
            }

            impl MedianFinder {
                pub fn new() -> Self {
                    Self::default()
                }

                pub fn add_num(&mut self, num: i32) {
                    self.values.push(num);
                }

                pub fn remove_num(&mut self, num: i32) -> bool {
                    match self.values.iter().position(|&x| x == num) {
                        Some(i) => {
                            self.values.swap_remove(i);
                            true
                        }
                        None => false,
                    }
                }

                pub fn find_median(&self) -> Option<f64> {
                    let mut s = self.values.clone();
                    s.sort_unstable();
                    let n = s.len();
                    match n {
                        0 => None,
                        _ if n % 2 == 1 => Some(s[n / 2] as f64),
                        _ => Some((s[n / 2 - 1] as f64 + s[n / 2] as f64) / 2.0),
                    }
                }
            }
        """,
        sum_in_i32=MEDIAN_SOLUTION.replace("Some((lo as f64 + hi as f64) / 2.0)", "Some((lo + hi) as f64 / 2.0)"),
        strict_side_test=MEDIAN_SOLUTION.replace("if self.low.peek().is_some_and(|&top| num <= top) {", "if self.low.peek().is_some_and(|&top| num < top) {"),
    ),
    hints=[("approach", "Split the numbers into a lower half (max-heap) and an upper half (min-heap) whose sizes differ by at most one; the median is on the tops."),
           ("rust", "`BinaryHeap` has no `remove`. Count removed copies in a `HashMap<i32, usize>` and pop them only when they surface; balance the halves by *live* sizes, not `len()`."),
           ("edge case", "Average the two middles in `f64`: `i32::MAX + i32::MAX` overflows. And a removed value equal to the lower top belongs to the lower half.")],
    notes=("The lower half's top and the upper half's top straddle the median. Adding goes to the side the value belongs to, then one top may move "
           "across to restore the sizes. Removal is lazy: the copy is marked in `doomed` and the live size of its half drops; any doomed copy that "
           "reaches a top is popped then. Each copy is pushed and popped at most a constant number of times, so everything is O(log n) amortized. "
           "Since every mutation prunes the tops, `find_median` only peeks. A sorted `Vec` with binary search is simpler but O(n) per update.",
           "O(log n) amortized per operation", "O(n), including removed copies not yet popped"),
    follow_up="Sliding window median gives you the window as a slice and a width k. Which parts of this design would you keep?",
    related=["S5", "S4", "D14"],
))

P.append(dict(
    slug="ipo", title="IPO", level="hard", stage="two-heaps-merges", tags=["two heaps", "greedy", "Reverse"],
    companies=["Amazon", "Google", "Microsoft"],
    teaches=["Two heaps with different keys: a min-heap by capital holds locked projects, a max-heap by profit holds the affordable ones.",
             "Capital only grows, so each project moves from locked to affordable once.",
             "`u64` for capital: `w` plus many profits outgrows `u32`."],
    statement="""
        You start with capital `w` and may finish at most `k` projects, one after another. Project `i` needs
        at least `capital[i]` to start, and finishing it adds `profits[i]` to your capital (starting it costs nothing).
        Each project can be done once. Return the largest capital you can end with.
    """,
    examples=[("k = 2, w = 0, profits = [1, 2, 3], capital = [0, 1, 1]", "4"), ("k = 3, w = 0, profits = [1, 2, 3], capital = [0, 1, 2]", "6")],
    constraints=["0 ≤ k ≤ 10⁵", "0 ≤ n ≤ 10⁵, profits.len() == capital.len()", "0 ≤ w, capital[i] ≤ 10¹²", "0 ≤ profits[i] ≤ 10⁹"],
    starter="""
        pub fn find_maximized_capital(k: usize, w: u64, profits: &[u64], capital: &[u64]) -> u64 {
            todo!()
        }
    """,
    solution="""
        use std::cmp::Reverse;
        use std::collections::BinaryHeap;

        pub fn find_maximized_capital(k: usize, mut w: u64, profits: &[u64], capital: &[u64]) -> u64 {
            // Projects we can't afford yet, cheapest first.
            let mut locked: BinaryHeap<Reverse<(u64, u64)>> = capital.iter().zip(profits).map(|(&c, &p)| Reverse((c, p))).collect();
            // Projects we can afford, most profitable first.
            let mut affordable: BinaryHeap<u64> = BinaryHeap::new();
            for _ in 0..k {
                while let Some(&Reverse((c, p))) = locked.peek() {
                    if c > w {
                        break;
                    }
                    locked.pop();
                    affordable.push(p);
                }
                let Some(p) = affordable.pop() else {
                    break;
                };
                w += p;
            }
            w
        }
    """,
    visible=[
        T("leetcode_one", "k = 2, w = 0, profits = [1, 2, 3], capital = [0, 1, 1]", "find_maximized_capital(2, 0, &[1, 2, 3], &[0, 1, 1])", "4"),
        T("leetcode_two", "k = 3, w = 0, profits = [1, 2, 3], capital = [0, 1, 2]", "find_maximized_capital(3, 0, &[1, 2, 3], &[0, 1, 2])", "6"),
        T("nothing_affordable", "k = 3, w = 1, profits = [5, 9], capital = [2, 3]", "find_maximized_capital(3, 1, &[5, 9], &[2, 3])", "1"),
        T("k_zero", "k = 0, w = 7, profits = [100], capital = [0]", "find_maximized_capital(0, 7, &[100], &[0])", "7"),
        T("each_project_once", "k = 5, w = 0, profits = [4], capital = [0]", "find_maximized_capital(5, 0, &[4], &[0])", "4"),
        T("unlock_the_big_one_first", "k = 2, w = 0, profits = [1, 1, 10], capital = [0, 0, 1]", "find_maximized_capital(2, 0, &[1, 1, 10], &[0, 0, 1])", "11"),
    ],
    hidden=[
        T("no_projects", "k = 4, w = 3, profits = [], capital = []", "find_maximized_capital(4, 3, &[], &[])", "3"),
        T("capital_exactly_w", "k = 1, w = 5, profits = [2], capital = [5]", "find_maximized_capital(1, 5, &[2], &[5])", "7"),
        T("zero_profit_projects", "k = 3, w = 0, profits = [0, 0, 0], capital = [0, 0, 1]", "find_maximized_capital(3, 0, &[0, 0, 0], &[0, 0, 1])", "0"),
        T("several_unlock_at_once", "k = 2, w = 0, profits = [1, 3, 5, 2], capital = [0, 1, 1, 1]", "find_maximized_capital(2, 0, &[1, 3, 5, 2], &[0, 1, 1, 1])", "6"),
        T("past_u32", "k = 3, w = 4000000000, profits = [10⁹; 3], capital = [0; 3]",
          "find_maximized_capital(3, 4_000_000_000, &[1_000_000_000; 3], &[0; 3])", "7_000_000_000"),
        T("chain", "k = 4, w = 1, profits = [1, 2, 4, 8], capital = [1, 2, 4, 8]", "find_maximized_capital(4, 1, &[1, 2, 4, 8], &[1, 2, 4, 8])", "16"),
        T("best_affordable_not_best_overall", "k = 1, w = 2, profits = [3, 100], capital = [2, 3]", "find_maximized_capital(1, 2, &[3, 100], &[2, 3])", "5"),
        T("k_larger_than_n", "k = 100, w = 0, profits = [1, 2], capital = [0, 0]", "find_maximized_capital(100, 0, &[1, 2], &[0, 0])", "3"),
        """
        #[test]
        fn random_vs_brute_force() {
            // Try every order of every affordable project, up to k of them.
            fn best(k: usize, w: u64, profits: &[u64], capital: &[u64], used: &mut [bool]) -> u64 {
                let mut out = w;
                if k == 0 {
                    return out;
                }
                for i in 0..profits.len() {
                    if !used[i] && capital[i] <= w {
                        used[i] = true;
                        out = out.max(best(k - 1, w + profits[i], profits, capital, used));
                        used[i] = false;
                    }
                }
                out
            }
            let mut rng = anneal_prelude::Rng::new(716);
            for _ in 0..300 {
                let n = rng.below(7);
                let profits: Vec<u64> = rng.vec(n, 0, 6);
                let capital: Vec<u64> = rng.vec(n, 0, 8);
                let k = rng.below(5);
                let w = rng.int(0, 3) as u64;
                let want = best(k, w, &profits, &capital, &mut vec![false; n]);
                check!(format!("k = {k}, w = {w}, profits = {profits:?}, capital = {capital:?}"), find_maximized_capital(k, w, &profits, &capital), want);
            }
        }

        #[test]
        fn scale_100k_projects() {
            let mut rng = anneal_prelude::Rng::new(717);
            let n = 100_000;
            let profits: Vec<u64> = rng.vec(n, 1, 1000);
            // Every 1000th project is free, so there is always somewhere to start.
            let capital: Vec<u64> = (0..n).map(|i| if i % 1000 == 0 { 0 } else { rng.int(0, 40_000_000) as u64 }).collect();
            let k = 50_000;
            // Reference: the same greedy with a sorted Vec and a BTreeMap multiset of affordable profits.
            let mut order: Vec<usize> = (0..n).collect();
            order.sort_unstable_by_key(|&i| capital[i]);
            let mut bag = std::collections::BTreeMap::new();
            let (mut w, mut next) = (0u64, 0);
            for _ in 0..k {
                while next < n && capital[order[next]] <= w {
                    *bag.entry(profits[order[next]]).or_insert(0u32) += 1;
                    next += 1;
                }
                let Some(mut e) = bag.last_entry() else { break };
                w += *e.key();
                *e.get_mut() -= 1;
                if *e.get() == 0 {
                    e.remove();
                }
            }
            check!("n = 100000 random projects (profit 1..=1000, capital 0..=4·10⁷, every 1000th free), k = 50000, w = 0", find_maximized_capital(k, 0, &profits, &capital), w);
        }
        """,
    ],
    wrong=dict(
        rescan_every_round="""
            pub fn find_maximized_capital(k: usize, mut w: u64, profits: &[u64], capital: &[u64]) -> u64 {
                let mut done = vec![false; profits.len()];
                for _ in 0..k {
                    let best = (0..profits.len()).filter(|&i| !done[i] && capital[i] <= w).max_by_key(|&i| profits[i]);
                    let Some(i) = best else { break };
                    done[i] = true;
                    w += profits[i];
                }
                w
            }
        """,
        unlock_one_per_round="""
            use std::cmp::Reverse;
            use std::collections::BinaryHeap;

            pub fn find_maximized_capital(k: usize, mut w: u64, profits: &[u64], capital: &[u64]) -> u64 {
                let mut locked: BinaryHeap<Reverse<(u64, u64)>> = capital.iter().zip(profits).map(|(&c, &p)| Reverse((c, p))).collect();
                let mut affordable: BinaryHeap<u64> = BinaryHeap::new();
                for _ in 0..k {
                    if let Some(&Reverse((c, p))) = locked.peek() {
                        if c <= w {
                            locked.pop();
                            affordable.push(p);
                        }
                    }
                    let Some(p) = affordable.pop() else {
                        break;
                    };
                    w += p;
                }
                w
            }
        """,
        cheapest_first="""
            pub fn find_maximized_capital(k: usize, mut w: u64, profits: &[u64], capital: &[u64]) -> u64 {
                let mut order: Vec<usize> = (0..profits.len()).collect();
                order.sort_by_key(|&i| (capital[i], std::cmp::Reverse(profits[i])));
                for &i in order.iter().take(k) {
                    if capital[i] > w {
                        break;
                    }
                    w += profits[i];
                }
                w
            }
        """,
    ),
    hints=[("approach", "At each step, do the most profitable project you can afford. Finishing it only raises capital, so nothing affordable ever becomes unaffordable."),
           ("rust", "Keep locked projects in `BinaryHeap<Reverse<(capital, profit)>>`; before each pick, move every one with `capital <= w` into a `BinaryHeap<u64>` of profits."),
           ("edge case", "Stop early when nothing is affordable, and move *all* newly affordable projects, not just one per round.")],
    notes=("Exchange argument: any plan that skips the most profitable affordable project can swap it in without ending lower, because capital "
           "only grows. Each project moves from the capital heap to the profit heap once and leaves it at most once, so the total is "
           "O((n + k) log n). Sorting by capital with an index pointer replaces the first heap equally well.", "O((n + k) log n)", "O(n)"),
    follow_up="What changes if starting a project also costs its capital (you pay `capital[i]` and get back `capital[i] + profits[i]`)?",
    related=["D8", "S5"],
))

P.append(dict(
    slug="smallest-range-covering-k-lists", title="Smallest range covering elements from K lists", level="hard", stage="two-heaps-merges",
    tags=["BinaryHeap", "k-way merge", "i64"],
    companies=["Google", "Amazon", "Microsoft", "Uber"],
    teaches=["Merge the lists with a heap of their current heads while tracking the largest head: the heads always form a candidate range.",
             "Advancing the list with the smallest head is the only move that can shrink the range.",
             "Range widths in `i64`: `i32::MAX - i32::MIN` overflows `i32`."],
    statement="""
        Every list in `lists` is sorted ascending. Return the smallest range `(lo, hi)` (inclusive) that contains at least
        one number from every list. Range `(a, b)` is smaller than `(c, d)` if `b − a < d − c`, or if the widths are
        equal and `a < c`. Return `None` if there are no lists or some list is empty.

        Values can be any `i32`.
    """,
    examples=[("lists = [[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]]", "Some((20, 24))"), ("lists = [[1, 2, 3], [1, 2, 3], [1, 2, 3]]", "Some((1, 1))")],
    constraints=["0 ≤ lists.len() ≤ 2·10⁴", "total length N ≤ 2·10⁵", "values are any i32"],
    starter="""
        pub fn smallest_range(lists: &[Vec<i32>]) -> Option<(i32, i32)> {
            todo!()
        }
    """,
    solution="""
        use std::cmp::Reverse;
        use std::collections::BinaryHeap;

        pub fn smallest_range(lists: &[Vec<i32>]) -> Option<(i32, i32)> {
            // One head per list: (value, list, index). The heads always cover every list.
            let mut heap = BinaryHeap::with_capacity(lists.len());
            let mut hi = i32::MIN;
            for (l, list) in lists.iter().enumerate() {
                let &first = list.first()?;
                hi = hi.max(first);
                heap.push(Reverse((first, l, 0)));
            }
            let mut best: Option<(i32, i32)> = None;
            while let Some(Reverse((lo, l, i))) = heap.pop() {
                let width = |(a, b): (i32, i32)| b as i64 - a as i64;
                // lo never decreases, so on equal widths the first range found has the smaller start.
                if best.is_none_or(|b| width((lo, hi)) < width(b)) {
                    best = Some((lo, hi));
                }
                // Once a list runs out, no range without its last head can cover it.
                let Some(&next) = lists[l].get(i + 1) else {
                    break;
                };
                hi = hi.max(next);
                heap.push(Reverse((next, l, i + 1)));
            }
            best
        }
    """,
    visible=[
        T("leetcode_one", "lists = [[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]]",
          "smallest_range(&[vec![4, 10, 15, 24, 26], vec![0, 9, 12, 20], vec![5, 18, 22, 30]])", "Some((20, 24))"),
        T("leetcode_same_lists", "lists = [[1, 2, 3], [1, 2, 3], [1, 2, 3]]", "smallest_range(&[vec![1, 2, 3], vec![1, 2, 3], vec![1, 2, 3]])", "Some((1, 1))"),
        T("single_list", "lists = [[5, 8]]", "smallest_range(&[vec![5, 8]])", "Some((5, 5))"),
        T("equal_widths_take_smaller_start", "lists = [[1, 10], [4, 13]] ((1, 4) and (10, 13) both have width 3)",
          "smallest_range(&[vec![1, 10], vec![4, 13]])", "Some((1, 4))"),
        T("no_lists", "lists = []", "smallest_range(&[])", "None"),
        T("an_empty_list", "lists = [[1, 2], []]", "smallest_range(&[vec![1, 2], vec![]])", "None"),
    ],
    hidden=[
        T("full_i32_width", "lists = [[i32::MIN], [i32::MAX]]", "smallest_range(&[vec![i32::MIN], vec![i32::MAX]])", "Some((i32::MIN, i32::MAX))"),
        T("wide_then_narrow", "lists = [[i32::MIN, 0], [1, i32::MAX]]", "smallest_range(&[vec![i32::MIN, 0], vec![1, i32::MAX]])", "Some((0, 1))"),
        T("negatives", "lists = [[-10, -5], [-7, 3], [-6]]", "smallest_range(&[vec![-10, -5], vec![-7, 3], vec![-6]])", "Some((-7, -5))"),
        T("duplicates_inside_a_list", "lists = [[1, 1, 1, 9], [9, 9]]", "smallest_range(&[vec![1, 1, 1, 9], vec![9, 9]])", "Some((9, 9))"),
        T("one_long_list", "lists = [0..1000, [500]]", "smallest_range(&[(0..1000).collect(), vec![500]])", "Some((500, 500))"),
        T("disjoint_blocks", "lists = [[1, 2, 3], [10, 11], [20]]", "smallest_range(&[vec![1, 2, 3], vec![10, 11], vec![20]])", "Some((3, 20))"),
        T("answer_at_the_end", "lists = [[1, 100], [50, 101], [80, 102]]", "smallest_range(&[vec![1, 100], vec![50, 101], vec![80, 102]])", "Some((100, 102))"),
        T("empty_list_last", "lists = [[1], [2], []]", "smallest_range(&[vec![1], vec![2], vec![]])", "None"),
        T("many_equal_widths", "lists = [[0, 5, 10], [2, 7, 12]]", "smallest_range(&[vec![0, 5, 10], vec![2, 7, 12]])", "Some((0, 2))"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(718);
            for _ in 0..300 {
                let k = rng.below(4);
                let mut lists: Vec<Vec<i32>> = Vec::new();
                for _ in 0..k {
                    let len = rng.below(5);
                    let mut v: Vec<i32> = rng.vec(len, -8, 8);
                    v.sort_unstable();
                    lists.push(v);
                }
                let values: Vec<i32> = lists.concat();
                let mut want: Option<(i32, i32)> = None;
                if k > 0 && lists.iter().all(|l| !l.is_empty()) {
                    for &a in &values {
                        for &b in &values {
                            let covers = a <= b && lists.iter().all(|l| l.iter().any(|&x| a <= x && x <= b));
                            if covers && want.is_none_or(|(c, d)| (b - a, a) < (d - c, c)) {
                                want = Some((a, b));
                            }
                        }
                    }
                }
                check!(format!("lists = {lists:?}"), smallest_range(&lists), want);
            }
        }

        #[test]
        fn scale_10k_lists() {
            let mut rng = anneal_prelude::Rng::new(719);
            let lists: Vec<Vec<i32>> = (0..10_000)
                .map(|_| {
                    let mut v: Vec<i32> = rng.vec(20, -1_000_000_000, 1_000_000_000);
                    v.sort_unstable();
                    v
                })
                .collect();
            // Reference: a sliding window over all values sorted, counting how many lists it covers.
            let mut all: Vec<(i32, usize)> = lists.iter().enumerate().flat_map(|(l, v)| v.iter().map(move |&x| (x, l))).collect();
            all.sort_unstable();
            let (mut count, mut covered, mut left) = (vec![0usize; lists.len()], 0, 0);
            let mut want: Option<(i32, i32)> = None;
            for right in 0..all.len() {
                if count[all[right].1] == 0 {
                    covered += 1;
                }
                count[all[right].1] += 1;
                while covered == lists.len() {
                    let (a, b) = (all[left].0, all[right].0);
                    if want.is_none_or(|(c, d)| (b as i64 - a as i64) < (d as i64 - c as i64)) {
                        want = Some((a, b));
                    }
                    count[all[left].1] -= 1;
                    if count[all[left].1] == 0 {
                        covered -= 1;
                    }
                    left += 1;
                }
            }
            check!("10000 sorted lists of 20 random values in ±10⁹", smallest_range(&lists), want);
        }
        """,
    ],
    wrong=dict(
        scan_all_heads="""
            pub fn smallest_range(lists: &[Vec<i32>]) -> Option<(i32, i32)> {
                if lists.is_empty() || lists.iter().any(|l| l.is_empty()) {
                    return None;
                }
                let mut pos = vec![0; lists.len()];
                let mut best: Option<(i32, i32)> = None;
                loop {
                    let lo_list = (0..lists.len()).min_by_key(|&l| lists[l][pos[l]]).unwrap();
                    let lo = lists[lo_list][pos[lo_list]];
                    let hi = (0..lists.len()).map(|l| lists[l][pos[l]]).max().unwrap();
                    if best.is_none_or(|(a, b)| (hi as i64 - lo as i64) < (b as i64 - a as i64)) {
                        best = Some((lo, hi));
                    }
                    pos[lo_list] += 1;
                    if pos[lo_list] == lists[lo_list].len() {
                        return best;
                    }
                }
            }
        """,
        width_in_i32="""
            use std::cmp::Reverse;
            use std::collections::BinaryHeap;

            pub fn smallest_range(lists: &[Vec<i32>]) -> Option<(i32, i32)> {
                let mut heap = BinaryHeap::new();
                let mut hi = i32::MIN;
                for (l, list) in lists.iter().enumerate() {
                    let &first = list.first()?;
                    hi = hi.max(first);
                    heap.push(Reverse((first, l, 0)));
                }
                let mut best: Option<(i32, i32)> = None;
                while let Some(Reverse((lo, l, i))) = heap.pop() {
                    if best.is_none_or(|(a, b)| hi - lo < b - a) {
                        best = Some((lo, hi));
                    }
                    let Some(&next) = lists[l].get(i + 1) else {
                        break;
                    };
                    hi = hi.max(next);
                    heap.push(Reverse((next, l, i + 1)));
                }
                best
            }
        """,
        later_tie_wins="""
            use std::cmp::Reverse;
            use std::collections::BinaryHeap;

            pub fn smallest_range(lists: &[Vec<i32>]) -> Option<(i32, i32)> {
                let mut heap = BinaryHeap::new();
                let mut hi = i32::MIN;
                for (l, list) in lists.iter().enumerate() {
                    let &first = list.first()?;
                    hi = hi.max(first);
                    heap.push(Reverse((first, l, 0)));
                }
                let mut best: Option<(i32, i32)> = None;
                while let Some(Reverse((lo, l, i))) = heap.pop() {
                    if best.is_none_or(|(a, b)| hi as i64 - lo as i64 <= b as i64 - a as i64) {
                        best = Some((lo, hi));
                    }
                    let Some(&next) = lists[l].get(i + 1) else {
                        break;
                    };
                    hi = hi.max(next);
                    heap.push(Reverse((next, l, i + 1)));
                }
                best
            }
        """,
    ),
    hints=[("approach", "Take one element from each list: the range from their minimum to their maximum covers every list. To shrink it, you can only advance the list holding the minimum."),
           ("rust", "A min-heap of `Reverse((value, list, index))` gives the minimum head; keep the maximum head in a plain variable, since it only grows."),
           ("edge case", "Stop as soon as the list with the minimum head runs out. Compare widths as `i64`, and keep the first range on ties.")],
    notes=("The current heads always cover all k lists, so `[min head, max head]` is a candidate. Any better range must drop the current minimum, "
           "so pop it and push the next element from the same list; the maximum can only grow, so one variable tracks it. When a list is "
           "exhausted no later candidate can cover it. Each of the N elements enters the heap once.", "O(N log k)", "O(k)"),
    follow_up="How would you solve it with a sliding window over all values sorted together, and when would you prefer that?",
    related=["D2", "D5", "S5"],
))

# Test helper for the k-way merge: a run that counts its reads.
MERGE_HELPERS = """
use std::cell::Cell;
use std::rc::Rc;

/// A run that counts how many items have been read from it.
struct Counted<I> {
    inner: I,
    reads: Rc<Cell<usize>>,
}

impl<I: Iterator> Iterator for Counted<I> {
    type Item = I::Item;

    fn next(&mut self) -> Option<I::Item> {
        let x = self.inner.next();
        if x.is_some() {
            self.reads.set(self.reads.get() + 1);
        }
        x
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        self.inner.size_hint()
    }
}
"""

# Hidden tests only: an item type with no traits at all.
REC = """
/// No Clone, Copy, Debug, PartialEq or Ord: the merge must only move items.
struct Rec {
    key: u32,
    tag: &'static str,
}
"""

KMERGE_HEAD = """
    use std::cmp::Ordering;
    use std::collections::BinaryHeap;

    /// A run's current item with its key. Ordered so that `BinaryHeap` (a max-heap) pops the smallest
    /// key first, and on equal keys the lowest run. The item itself is never compared.
    struct Head<K, T> {
        key: K,
        run: usize,
        item: T,
    }

    impl<K: Ord, T> Ord for Head<K, T> {
        fn cmp(&self, other: &Self) -> Ordering {
            other.key.cmp(&self.key).then_with(|| other.run.cmp(&self.run))
        }
    }

    impl<K: Ord, T> PartialOrd for Head<K, T> {
        fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
            Some(self.cmp(other))
        }
    }

    impl<K: Ord, T> PartialEq for Head<K, T> {
        fn eq(&self, other: &Self) -> bool {
            self.cmp(other) == Ordering::Equal
        }
    }

    impl<K: Ord, T> Eq for Head<K, T> {}
"""

KMERGE_REST = """
    /// Merges runs that are each sorted by `key` into one sorted stream.
    pub struct KMerge<I: Iterator, K, F> {
        runs: Vec<I>,
        key: F,
        /// At most one item per run: the next one it has to offer.
        heap: BinaryHeap<Head<K, I::Item>>,
    }

    pub fn kmerge_by_key<I, K, F>(mut runs: Vec<I>, mut key: F) -> KMerge<I, K, F>
    where
        I: Iterator,
        K: Ord,
        F: FnMut(&I::Item) -> K,
    {
        let mut heap = BinaryHeap::with_capacity(runs.len());
        for (run, it) in runs.iter_mut().enumerate() {
            if let Some(item) = it.next() {
                heap.push(Head { key: key(&item), run, item });
            }
        }
        KMerge { runs, key, heap }
    }

    impl<I, K, F> Iterator for KMerge<I, K, F>
    where
        I: Iterator,
        K: Ord,
        F: FnMut(&I::Item) -> K,
    {
        type Item = I::Item;

        fn next(&mut self) -> Option<I::Item> {
            let Head { run, item, .. } = self.heap.pop()?;
            // Refill from the same run only; an exhausted run is never polled again.
            if let Some(next) = self.runs[run].next() {
                let key = (self.key)(&next);
                self.heap.push(Head { key, run, item: next });
            }
            Some(item)
        }

        fn size_hint(&self) -> (usize, Option<usize>) {
            let held = self.heap.len();
            self.runs.iter().fold((held, Some(held)), |(lo, hi), run| {
                let (a, b) = run.size_hint();
                (lo.saturating_add(a), hi.zip(b).and_then(|(h, b)| h.checked_add(b)))
            })
        }
    }
"""

P.append(dict(
    slug="external-merge-sort", title="External merge sort", level="hard", stage="two-heaps-merges", source="W64",
    tags=["k-way merge", "custom Ord", "Iterator", "generics"],
    teaches=["The merge phase of external sort as a lazy `Iterator`: one buffered item per run, O(log k) per item.",
             "A heap entry with a hand-written `Ord` over `(key, run)` that never compares the payload, so items need no traits.",
             "Stability from the run index, and a key computed once per item because `Ord` can't call the key closure.",
             "Syntax to remember: `impl<I, K, F> Iterator for KMerge<I, K, F> where I: Iterator, K: Ord, F: FnMut(&I::Item) -> K`."],
    statement="""
        External sorting handles data too big for memory: sort chunks into *runs* on disk, then merge the runs in
        one streaming pass. Write that merge. `kmerge_by_key(runs, key)` takes iterators that each yield items in
        ascending `key` order and returns an iterator over all their items in ascending `key` order.

        - **Lazy:** hold at most one unreturned item per run. The tests watch how far each run has been read.
        - **Stable:** equal keys come out in run order (run 0 first), and a run's own items keep their order.
        - **One key per item:** call `key` exactly once for each item; keys may be expensive (think parsing a record).
        - **Any item type:** items need no `Clone`, `Ord` or `Debug`; only keys are compared.
        - **`size_hint`:** items held plus the runs' own hints, exact when every run's hint is exact.
    """,
    examples=[("runs = [[1, 4, 9], [2, 3], []], key = |x| *x", "1, 2, 3, 4, 9"),
              ("runs = [[(1, \"a\")], [(1, \"b\"), (2, \"c\")]], key = |r| r.0", "(1, \"a\"), (1, \"b\"), (2, \"c\")")],
    constraints=["0 ≤ runs ≤ 2·10⁴", "total items N ≤ 2·10⁵ in the tests"],
    starter="""
        /// Merges runs that are each sorted by `key` into one sorted stream.
        pub struct KMerge<I: Iterator, K, F> {
            runs: Vec<I>,
            key: F,
            // Add what you need, and drop this marker once K and I::Item are used elsewhere.
            _marker: std::marker::PhantomData<(K, I::Item)>,
        }

        pub fn kmerge_by_key<I, K, F>(runs: Vec<I>, key: F) -> KMerge<I, K, F>
        where
            I: Iterator,
            K: Ord,
            F: FnMut(&I::Item) -> K,
        {
            todo!()
        }

        impl<I, K, F> Iterator for KMerge<I, K, F>
        where
            I: Iterator,
            K: Ord,
            F: FnMut(&I::Item) -> K,
        {
            type Item = I::Item;

            fn next(&mut self) -> Option<I::Item> {
                todo!()
            }

            fn size_hint(&self) -> (usize, Option<usize>) {
                todo!()
            }
        }
    """,
    solution=KMERGE_HEAD.rstrip("\n") + "\n" + KMERGE_REST,
    use="use solution::*;\n" + MERGE_HELPERS.rstrip("\n"),
    visible=[
        T("three_runs", "runs = [[1, 4, 9], [2, 3], []], key = |x| *x",
          "kmerge_by_key(vec![vec![1, 4, 9].into_iter(), vec![2, 3].into_iter(), vec![].into_iter()], |x: &i32| *x).collect::<Vec<_>>()", "vec![1, 2, 3, 4, 9]"),
        T("no_runs", "runs = []", "kmerge_by_key(Vec::<std::vec::IntoIter<i32>>::new(), |x: &i32| *x).count()", "0"),
        T("equal_keys_in_run_order", 'runs = [[(1, "a0"), (2, "a1")], [(1, "b0"), (1, "b1")]], key = |r| r.0',
          'kmerge_by_key(vec![vec![(1, "a0"), (2, "a1")].into_iter(), vec![(1, "b0"), (1, "b1")].into_iter()], |r: &(u32, &str)| r.0).collect::<Vec<_>>()',
          'vec![(1, "a0"), (1, "b0"), (1, "b1"), (2, "a1")]'),
        T("key_called_once_per_item", "runs = [[5, 7], [1, 6, 8]], counting key calls", "(out, calls.get())", "(vec![1, 5, 6, 7, 8], 5)",
          setup="let calls = Cell::new(0);\nlet out: Vec<u32> = kmerge_by_key(vec![vec![5, 7].into_iter(), vec![1, 6, 8].into_iter()], |x: &u32| {\n    calls.set(calls.get() + 1);\n    *x\n})\n.collect();"),
        T("reads_lazily", "runs = [[0, 10, 20], [1, 11, 21], [2, 12, 22]], take 4: no run read more than one item past what it returned",
          "ahead.iter().all(|&a| a <= 1)", "true",
          setup="let reads: Vec<Rc<Cell<usize>>> = (0..3).map(|_| Rc::new(Cell::new(0))).collect();\n"
                "let runs: Vec<Counted<std::vec::IntoIter<u32>>> = (0..3u32).map(|r| Counted { inner: vec![r, r + 10, r + 20].into_iter(), reads: reads[r as usize].clone() }).collect();\n"
                "let taken: Vec<u32> = kmerge_by_key(runs, |x: &u32| *x).take(4).collect();\n"
                "let ahead: Vec<usize> = (0..3u32).map(|r| reads[r as usize].get() - taken.iter().filter(|&&x| x % 10 == r).count()).collect();"),
        T("exact_size_hint", "runs = [[1, 3], [2]]: size_hint before and after one next()", "(before, after)", "((3, Some(3)), (2, Some(2)))",
          setup="let mut m = kmerge_by_key(vec![vec![1, 3].into_iter(), vec![2].into_iter()], |x: &i32| *x);\nlet before = m.size_hint();\nm.next();\nlet after = m.size_hint();"),
        T("descending_with_reverse_key", "runs = [[9, 4, 1], [8, 2]] (each descending), key = |x| Reverse(*x)",
          "kmerge_by_key(vec![vec![9, 4, 1].into_iter(), vec![8, 2].into_iter()], |x: &i32| std::cmp::Reverse(*x)).collect::<Vec<_>>()", "vec![9, 8, 4, 2, 1]"),
    ],
    hidden=[
        REC,
        T("empty_runs_between", "runs = [[], [1], [], [0, 2], []]",
          "kmerge_by_key(vec![vec![], vec![1], vec![], vec![0, 2], vec![]].into_iter().map(Vec::into_iter).collect(), |x: &i32| *x).collect::<Vec<_>>()", "vec![0, 1, 2]"),
        T("items_without_traits", 'runs of Rec { key, tag } with no derives: [[(2, "x"), (3, "y")], [(2, "z")]]', "out", 'vec![(2, "x"), (2, "z"), (3, "y")]',
          setup='let runs = vec![vec![Rec { key: 2, tag: "x" }, Rec { key: 3, tag: "y" }].into_iter(), vec![Rec { key: 2, tag: "z" }].into_iter()];\n'
                'let out: Vec<(u32, &str)> = kmerge_by_key(runs, |r: &Rec| r.key).map(|r| (r.key, r.tag)).collect();'),
        T("owned_strings_by_length", 'runs = [["a", "ccc"], ["bb", "dd", "eeee"]] as Strings, key = len',
          "kmerge_by_key(runs, |s: &String| s.len()).collect::<Vec<_>>()", 'vec!["a", "bb", "dd", "ccc", "eeee"]',
          setup='let runs: Vec<std::vec::IntoIter<String>> = vec![vec!["a".to_string(), "ccc".to_string()].into_iter(), vec!["bb".to_string(), "dd".to_string(), "eeee".to_string()].into_iter()];'),
        T("stops_before_the_tripwire", "run 0 = [1, 2, 10, then panics if read]; run 1 = [3, 4, 5]; take 3",
          "m.take(3).collect::<Vec<_>>()", "vec![1, 2, 3]",
          setup='let trip: Box<dyn Iterator<Item = u32>> = Box::new([1, 2, 10].into_iter().chain(std::iter::from_fn(|| -> Option<u32> { panic!("read further than needed") })));\n'
                "let other: Box<dyn Iterator<Item = u32>> = Box::new([3, 4, 5].into_iter());\n"
                "let m = kmerge_by_key(vec![trip, other], |x: &u32| *x);"),
        T("unknown_length_run", "runs = [[1, 2], a from_fn run with no upper bound]: size_hint().1",
          "m.size_hint().1", "None",
          setup="let mut n = 0;\nlet open: Box<dyn Iterator<Item = u32>> = Box::new(std::iter::from_fn(move || { n += 1; (n <= 3).then_some(n) }));\n"
                "let closed: Box<dyn Iterator<Item = u32>> = Box::new(vec![1, 2].into_iter());\n"
                "let m = kmerge_by_key(vec![closed, open], |x: &u32| *x);"),
        T("stable_many_runs_same_key", "10 runs, each [(7, run)]", "kmerge_by_key(runs, |r: &(u32, usize)| r.0).map(|r| r.1).collect::<Vec<_>>()", "(0..10).collect::<Vec<usize>>()",
          setup="let runs: Vec<std::vec::IntoIter<(u32, usize)>> = (0..10).map(|r| vec![(7, r)].into_iter()).collect();"),
        T("one_run", "runs = [[3, 3, 5]]", "kmerge_by_key(vec![vec![3, 3, 5].into_iter()], |x: &i32| *x).collect::<Vec<_>>()", "vec![3, 3, 5]"),
        T("extreme_keys", "runs = [[i64::MIN, i64::MAX], [0]]", "kmerge_by_key(vec![vec![i64::MIN, i64::MAX].into_iter(), vec![0].into_iter()], |x: &i64| *x).collect::<Vec<_>>()",
          "vec![i64::MIN, 0, i64::MAX]"),
        """
        #[test]
        fn random_vs_stable_sort() {
            let mut rng = anneal_prelude::Rng::new(720);
            for _ in 0..300 {
                let k = rng.below(6);
                let mut runs: Vec<Vec<(u32, usize, usize)>> = Vec::new();
                for r in 0..k {
                    let len = rng.below(6);
                    let mut keys: Vec<u32> = rng.vec(len, 0, 4);
                    keys.sort_unstable();
                    runs.push(keys.into_iter().enumerate().map(|(i, key)| (key, r, i)).collect());
                }
                let reads: Vec<Rc<Cell<usize>>> = (0..k).map(|_| Rc::new(Cell::new(0))).collect();
                let calls = Cell::new(0);
                let mut m = kmerge_by_key(
                    runs.iter().zip(&reads).map(|(v, c)| Counted { inner: v.clone().into_iter(), reads: c.clone() }).collect(),
                    |x: &(u32, usize, usize)| {
                        calls.set(calls.get() + 1);
                        x.0
                    },
                );
                // Never more than one unreturned item per run.
                let mut returned = vec![0; k];
                let mut got = Vec::new();
                let mut lazy = true;
                while let Some(x) = m.next() {
                    returned[x.1] += 1;
                    lazy &= (0..k).all(|r| reads[r].get() <= returned[r] + 1);
                    got.push(x);
                }
                let mut want: Vec<(u32, usize, usize)> = runs.concat();
                want.sort();
                let n = want.len();
                check!(format!("runs (key, run, index) = {runs:?}; (merged, lazy, key calls)"), (got, lazy, calls.get()), (want, true, n));
            }
        }

        #[test]
        fn size_hint_brackets_what_is_left() {
            // Filtered runs report (0, Some(n)): the hint must still bracket the true remainder at every step.
            let runs: Vec<std::iter::Filter<std::vec::IntoIter<u32>, fn(&u32) -> bool>> =
                (0..4).map(|r| (0..10).map(|i| i * 4 + r).collect::<Vec<u32>>().into_iter().filter((|x: &u32| x % 3 != 0) as fn(&u32) -> bool)).collect();
            let total = (0..40u32).filter(|x| x % 3 != 0).count();
            let mut m = kmerge_by_key(runs, |x: &u32| *x);
            let mut left = total;
            let mut ok = true;
            loop {
                let (lo, hi) = m.size_hint();
                ok &= lo <= left && hi.is_some_and(|h| left <= h);
                if m.next().is_none() {
                    break;
                }
                left -= 1;
            }
            check!("4 filtered runs over 0..40 without multiples of 3: lo <= remaining <= hi at every step", (ok, left), (true, 0));
        }

        #[test]
        fn scale_10k_runs() {
            let mut rng = anneal_prelude::Rng::new(721);
            let runs: Vec<Vec<u32>> = (0..10_000)
                .map(|_| {
                    let mut v: Vec<u32> = rng.vec(20, 0, 1_000_000_000);
                    v.sort_unstable();
                    v
                })
                .collect();
            let mut want = runs.concat();
            want.sort_unstable();
            let got: Vec<u32> = kmerge_by_key(runs.into_iter().map(Vec::into_iter).collect(), |x: &u32| *x).collect();
            check!("10000 runs of 20 random values", got == want, true);
        }
        """,
    ],
    wrong=dict(
        collect_and_sort="""
            use std::marker::PhantomData;

            /// Merges runs that are each sorted by `key` into one sorted stream.
            pub struct KMerge<I: Iterator, K, F> {
                items: std::vec::IntoIter<(K, usize, I::Item)>,
                _key: PhantomData<F>,
            }

            pub fn kmerge_by_key<I, K, F>(runs: Vec<I>, mut key: F) -> KMerge<I, K, F>
            where
                I: Iterator,
                K: Ord,
                F: FnMut(&I::Item) -> K,
            {
                let mut all = Vec::new();
                for (run, it) in runs.into_iter().enumerate() {
                    for item in it {
                        all.push((key(&item), run, item));
                    }
                }
                // Stable, so equal keys keep run order.
                all.sort_by(|a, b| a.0.cmp(&b.0).then(a.1.cmp(&b.1)));
                KMerge { items: all.into_iter(), _key: PhantomData }
            }

            impl<I, K, F> Iterator for KMerge<I, K, F>
            where
                I: Iterator,
                K: Ord,
                F: FnMut(&I::Item) -> K,
            {
                type Item = I::Item;

                fn next(&mut self) -> Option<I::Item> {
                    self.items.next().map(|(_, _, item)| item)
                }

                fn size_hint(&self) -> (usize, Option<usize>) {
                    self.items.size_hint()
                }
            }
        """,
        ties_ignore_the_run=KMERGE_HEAD.replace("other.key.cmp(&self.key).then_with(|| other.run.cmp(&self.run))", "other.key.cmp(&self.key)").rstrip("\n") + "\n" + KMERGE_REST,
        scan_every_head="""
            /// Merges runs that are each sorted by `key` into one sorted stream.
            pub struct KMerge<I: Iterator, K, F> {
                runs: Vec<I>,
                key: F,
                heads: Vec<Option<(K, I::Item)>>,
            }

            pub fn kmerge_by_key<I, K, F>(mut runs: Vec<I>, mut key: F) -> KMerge<I, K, F>
            where
                I: Iterator,
                K: Ord,
                F: FnMut(&I::Item) -> K,
            {
                let heads = runs.iter_mut().map(|it| it.next().map(|x| (key(&x), x))).collect();
                KMerge { runs, key, heads }
            }

            impl<I, K, F> Iterator for KMerge<I, K, F>
            where
                I: Iterator,
                K: Ord,
                F: FnMut(&I::Item) -> K,
            {
                type Item = I::Item;

                fn next(&mut self) -> Option<I::Item> {
                    let mut best: Option<usize> = None;
                    for r in 0..self.heads.len() {
                        if let Some((k, _)) = &self.heads[r] {
                            if best.is_none_or(|b| k < &self.heads[b].as_ref().unwrap().0) {
                                best = Some(r);
                            }
                        }
                    }
                    let r = best?;
                    let refill = self.runs[r].next().map(|x| ((self.key)(&x), x));
                    let (_, item) = std::mem::replace(&mut self.heads[r], refill)?;
                    Some(item)
                }

                fn size_hint(&self) -> (usize, Option<usize>) {
                    let held = self.heads.iter().filter(|h| h.is_some()).count();
                    self.runs.iter().fold((held, Some(held)), |(lo, hi), run| {
                        let (a, b) = run.size_hint();
                        (lo.saturating_add(a), hi.zip(b).and_then(|(h, b)| h.checked_add(b)))
                    })
                }
            }
        """,
    ),
    hints=[("approach", "Keep one pending item per run in a min-heap keyed by `(key, run)`. Pop the smallest, then read the next item from that same run."),
           ("rust", "`Ord` can't see your key closure, so compute the key when an item enters the heap and store it next to the item in a `Head { key, run, item }`. Implement `Ord` by hand on `(key, run)`, reversed for a min-heap, and never touch `item`; derives would demand `Ord` on the item."),
           ("edge case", "Stability comes from the run index in the ordering. `size_hint` must count the items sitting in the heap, and add upper bounds with `checked_add`.")],
    notes=("This is the merge phase of external sort (and of LSM-tree compaction): each run is a sorted file read sequentially, and memory holds "
           "one item per run. The heap entry carries its precomputed key, so the closure runs once per item and `Ord` stays a pure function of "
           "stored data. Comparing `(key, run)` makes the merge stable, which is what lets a multi-pass external sort stay stable. Because only "
           "keys are compared, `Head<K, T>` implements `PartialEq`/`Eq`/`PartialOrd`/`Ord` for any `T`. Collecting everything and sorting "
           "would need all N items in memory at once, which is the one thing external sort exists to avoid.",
           "O(N log k)", "O(k)"),
    follow_up="With k = 10 000 runs, a heap costs log k comparisons per item. How does a tournament (loser) tree cut that, and why do databases use one?",
    related=["D5", "S6", "L5"],
))

P.append(dict(
    slug="single-threaded-cpu", title="Single-threaded CPU", level="hard", stage="two-heaps-merges", tags=["BinaryHeap", "simulation", "u64"],
    companies=["Amazon", "Google", "Microsoft"],
    teaches=["Sort by arrival once, then feed a min-heap of `Reverse((processing, index))` as the clock passes arrivals.",
             "When nothing is waiting, jump the clock to the next arrival instead of ticking.",
             "The clock is `u64`: 10⁵ tasks of up to ~4·10⁹ each overflow `u32`."],
    statement="""
        `tasks[i] = (enqueue_time, processing_time)`. A single CPU runs tasks one at a time, to completion:

        - when it's free and tasks are waiting, it starts the one with the shortest processing time, breaking ties by
          smaller index;
        - when it's free and nothing is waiting, it idles until the next task arrives;
        - a task whose enqueue time equals the moment the CPU becomes free is already waiting.

        Return the indices in the order the CPU runs them.
    """,
    examples=[("tasks = [(1, 2), (2, 4), (3, 2), (4, 1)]", "[0, 2, 3, 1]"), ("tasks = [(7, 10), (7, 12), (7, 5), (7, 4), (7, 2)]", "[4, 3, 2, 0, 1]")],
    constraints=["0 ≤ tasks.len() ≤ 10⁵", "enqueue and processing times are any u32"],
    starter="""
        pub fn get_order(tasks: &[(u32, u32)]) -> Vec<usize> {
            todo!()
        }
    """,
    solution="""
        use std::cmp::Reverse;
        use std::collections::BinaryHeap;

        pub fn get_order(tasks: &[(u32, u32)]) -> Vec<usize> {
            let mut arrivals: Vec<usize> = (0..tasks.len()).collect();
            arrivals.sort_unstable_by_key(|&i| (tasks[i].0, i));
            // Waiting tasks: shortest processing time first, then smallest index.
            let mut waiting: BinaryHeap<Reverse<(u32, usize)>> = BinaryHeap::new();
            let mut out = Vec::with_capacity(tasks.len());
            let mut clock: u64 = 0;
            let mut next = 0;
            while out.len() < tasks.len() {
                if waiting.is_empty() {
                    // Idle: jump straight to the next arrival.
                    clock = clock.max(tasks[arrivals[next]].0 as u64);
                }
                while next < arrivals.len() && tasks[arrivals[next]].0 as u64 <= clock {
                    let i = arrivals[next];
                    waiting.push(Reverse((tasks[i].1, i)));
                    next += 1;
                }
                if let Some(Reverse((time, i))) = waiting.pop() {
                    clock += time as u64;
                    out.push(i);
                }
            }
            out
        }
    """,
    visible=[
        T("leetcode_one", "tasks = [(1, 2), (2, 4), (3, 2), (4, 1)]", "get_order(&[(1, 2), (2, 4), (3, 2), (4, 1)])", "vec![0, 2, 3, 1]"),
        T("leetcode_same_arrival", "tasks = [(7, 10), (7, 12), (7, 5), (7, 4), (7, 2)]", "get_order(&[(7, 10), (7, 12), (7, 5), (7, 4), (7, 2)])", "vec![4, 3, 2, 0, 1]"),
        T("empty", "tasks = []", "get_order(&[])", "Vec::<usize>::new()"),
        T("idle_until_the_next_arrival", "tasks = [(10, 1), (0, 1)]", "get_order(&[(10, 1), (0, 1)])", "vec![1, 0]"),
        T("ties_by_index", "tasks = [(0, 5), (0, 5), (0, 5)]", "get_order(&[(0, 5), (0, 5), (0, 5)])", "vec![0, 1, 2]"),
        T("arrival_at_finish_counts", "tasks = [(0, 2), (2, 1), (1, 3)] (at time 2 both 1 and 2 wait)", "get_order(&[(0, 2), (2, 1), (1, 3)])", "vec![0, 1, 2]"),
    ],
    hidden=[
        T("single", "tasks = [(5, 5)]", "get_order(&[(5, 5)])", "vec![0]"),
        T("clock_past_u32", "tasks = [(0, 4000000000), (1, 4000000000), (2, 1)]", "get_order(&[(0, 4_000_000_000), (1, 4_000_000_000), (2, 1)])", "vec![0, 2, 1]"),
        T("long_idle_gap", "tasks = [(4000000000, 1), (5, 1)]", "get_order(&[(4_000_000_000, 1), (5, 1)])", "vec![1, 0]"),
        T("max_times", "tasks = [(u32::MAX, u32::MAX), (u32::MAX, 0)]", "get_order(&[(u32::MAX, u32::MAX), (u32::MAX, 0)])", "vec![1, 0]"),
        T("late_short_task_waits", "tasks = [(0, 10), (1, 1), (2, 5)]", "get_order(&[(0, 10), (1, 1), (2, 5)])", "vec![0, 1, 2]"),
        T("zero_processing", "tasks = [(3, 0), (3, 0), (0, 3)]", "get_order(&[(3, 0), (3, 0), (0, 3)])", "vec![2, 0, 1]"),
        T("shorter_wins_over_earlier", "tasks = [(0, 1), (1, 9), (1, 2)]", "get_order(&[(0, 1), (1, 9), (1, 2)])", "vec![0, 2, 1]"),
        T("unsorted_arrivals", "tasks = [(9, 1), (3, 1), (6, 1), (0, 1)]", "get_order(&[(9, 1), (3, 1), (6, 1), (0, 1)])", "vec![3, 1, 2, 0]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(722);
            for _ in 0..300 {
                let n = rng.below(9);
                let tasks: Vec<(u32, u32)> = (0..n).map(|_| (rng.int(0, 10) as u32, rng.int(0, 4) as u32)).collect();
                let mut done = vec![false; n];
                let mut clock = 0u64;
                let mut want = Vec::new();
                while want.len() < n {
                    let pick = (0..n).filter(|&i| !done[i] && tasks[i].0 as u64 <= clock).min_by_key(|&i| (tasks[i].1, i));
                    match pick {
                        Some(i) => {
                            done[i] = true;
                            clock += tasks[i].1 as u64;
                            want.push(i);
                        }
                        None => clock = (0..n).filter(|&i| !done[i]).map(|i| tasks[i].0 as u64).min().unwrap(),
                    }
                }
                check!(format!("tasks = {tasks:?}"), get_order(&tasks), want);
            }
        }

        #[test]
        fn scale_100k_all_at_once() {
            let mut rng = anneal_prelude::Rng::new(723);
            let tasks: Vec<(u32, u32)> = (0..100_000).map(|_| (0, rng.int(1, 1_000_000) as u32)).collect();
            let mut want: Vec<usize> = (0..tasks.len()).collect();
            want.sort_unstable_by_key(|&i| (tasks[i].1, i));
            check!("100000 tasks all enqueued at 0, random processing times", get_order(&tasks) == want, true);
        }

        #[test]
        fn scale_100k_spread_out() {
            // Task i arrives at 10·i and takes 9 or 10: each one ends before the next arrives, often with an idle gap.
            let tasks: Vec<(u32, u32)> = (0..100_000u32).map(|i| (10 * i, 9 + i % 2)).collect();
            check!("100000 tasks arriving every 10, taking 9 or 10", get_order(&tasks) == (0..100_000).collect::<Vec<usize>>(), true);
        }
        """,
    ],
    wrong=dict(
        scan_waiting_tasks="""
            pub fn get_order(tasks: &[(u32, u32)]) -> Vec<usize> {
                let n = tasks.len();
                let mut done = vec![false; n];
                let mut clock = 0u64;
                let mut out = Vec::new();
                while out.len() < n {
                    let pick = (0..n).filter(|&i| !done[i] && tasks[i].0 as u64 <= clock).min_by_key(|&i| (tasks[i].1, i));
                    match pick {
                        Some(i) => {
                            done[i] = true;
                            clock += tasks[i].1 as u64;
                            out.push(i);
                        }
                        None => clock = (0..n).filter(|&i| !done[i]).map(|i| tasks[i].0 as u64).min().unwrap(),
                    }
                }
                out
            }
        """,
        u32_clock="""
            use std::cmp::Reverse;
            use std::collections::BinaryHeap;

            pub fn get_order(tasks: &[(u32, u32)]) -> Vec<usize> {
                let mut arrivals: Vec<usize> = (0..tasks.len()).collect();
                arrivals.sort_unstable_by_key(|&i| (tasks[i].0, i));
                let mut waiting: BinaryHeap<Reverse<(u32, usize)>> = BinaryHeap::new();
                let mut out = Vec::new();
                let mut clock: u32 = 0;
                let mut next = 0;
                while out.len() < tasks.len() {
                    if waiting.is_empty() {
                        clock = clock.max(tasks[arrivals[next]].0);
                    }
                    while next < arrivals.len() && tasks[arrivals[next]].0 <= clock {
                        let i = arrivals[next];
                        waiting.push(Reverse((tasks[i].1, i)));
                        next += 1;
                    }
                    if let Some(Reverse((time, i))) = waiting.pop() {
                        clock += time;
                        out.push(i);
                    }
                }
                out
            }
        """,
        tick_while_idle="""
            use std::cmp::Reverse;
            use std::collections::BinaryHeap;

            pub fn get_order(tasks: &[(u32, u32)]) -> Vec<usize> {
                let mut arrivals: Vec<usize> = (0..tasks.len()).collect();
                arrivals.sort_unstable_by_key(|&i| (tasks[i].0, i));
                let mut waiting: BinaryHeap<Reverse<(u32, usize)>> = BinaryHeap::new();
                let mut out = Vec::new();
                let mut clock: u64 = 0;
                let mut next = 0;
                while out.len() < tasks.len() {
                    while next < arrivals.len() && tasks[arrivals[next]].0 as u64 <= clock {
                        let i = arrivals[next];
                        waiting.push(Reverse((tasks[i].1, i)));
                        next += 1;
                    }
                    match waiting.pop() {
                        Some(Reverse((time, i))) => {
                            clock += time as u64;
                            out.push(i);
                        }
                        // Nothing waiting: let one unit of time pass.
                        None => clock += 1,
                    }
                }
                out
            }
        """,
    ),
    hints=[("approach", "Process arrivals in time order. Keep the tasks that have arrived in a min-heap by (processing time, index); each time the CPU is free, pop one and advance the clock by its processing time."),
           ("rust", "Sort indices by `(enqueue, index)` once and walk them with a pointer. `BinaryHeap<Reverse<(u32, usize)>>` gives shortest-first with index tie-breaks for free."),
           ("edge case", "If nothing is waiting, set the clock to the next arrival rather than ticking. Keep the clock in `u64`.")],
    notes=("Two structures play different roles: the sorted arrival list says *when* tasks become available, the heap says *which* available task "
           "runs next. The tuple `(processing, index)` inside `Reverse` encodes the whole selection rule. Jumping the clock over idle stretches "
           "makes the run time independent of the time values.", "O(n log n)", "O(n)"),
    follow_up="With m identical CPUs instead of one, what second heap would you add?",
    related=["D8", "S5"],
))

STAGES = [
    ("heap-basics", "Heap basics", "easy"),
    ("heaps-at-work", "Heaps at work", "medium"),
    ("two-heaps-merges", "Two heaps & merges", "hard"),
]

if __name__ == "__main__":
    n = write_track("d7-heaps", "D7", "Heaps & priority queues", "D", "core", 8,
                    "BinaryHeap the Rust way: Reverse for min-heaps, Ord newtypes and tuple keys, two heaps, k-way merges and lazy deletion.",
                    STAGES, P)
    print("D7", n)
