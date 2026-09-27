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
