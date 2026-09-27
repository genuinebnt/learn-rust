from author import T, write_track

MINIVEC = """
use std::alloc::{self, Layout};
use std::marker::PhantomData;
use std::ptr::{self, NonNull};

/// A growable array on a raw allocation. Zero-sized `T` isn't supported.
pub struct MiniVec<T> {
    ptr: NonNull<T>,
    cap: usize,
    len: usize,
    _owns: PhantomData<T>,
}

impl<T> MiniVec<T> {
    pub fn new() -> Self {
        assert!(std::mem::size_of::<T>() != 0, "zero-sized types aren't supported");
        MiniVec { ptr: NonNull::dangling(), cap: 0, len: 0, _owns: PhantomData }
    }

    pub fn len(&self) -> usize {
        self.len
    }

    pub fn is_empty(&self) -> bool {
        self.len == 0
    }

    pub fn capacity(&self) -> usize {
        self.cap
    }

    pub fn push(&mut self, value: T) {
        if self.len == self.cap {
            self.grow();
        }
        // SAFETY: len < cap, so the slot is inside the allocation and not yet initialised.
        unsafe { ptr::write(self.ptr.as_ptr().add(self.len), value) };
        self.len += 1;
    }

    pub fn pop(&mut self) -> Option<T> {
        if self.len == 0 {
            return None;
        }
        self.len -= 1;
        // SAFETY: the slot was initialised and is now past len, so it's read exactly once.
        Some(unsafe { ptr::read(self.ptr.as_ptr().add(self.len)) })
    }

    pub fn get(&self, i: usize) -> Option<&T> {
        // SAFETY: i < len, so the slot is initialised and inside the allocation.
        (i < self.len).then(|| unsafe { &*self.ptr.as_ptr().add(i) })
    }

    fn grow(&mut self) {
        let new_cap = if self.cap == 0 { 4 } else { self.cap * 2 };
        let new_layout = Layout::array::<T>(new_cap).expect("capacity overflow");
        let raw = if self.cap == 0 {
            // SAFETY: new_layout has a non-zero size because T isn't zero-sized.
            unsafe { alloc::alloc(new_layout) }
        } else {
            let old_layout = Layout::array::<T>(self.cap).expect("existing layout");
            // SAFETY: ptr was allocated with old_layout by this allocator.
            unsafe { alloc::realloc(self.ptr.as_ptr().cast(), old_layout, new_layout.size()) }
        };
        self.ptr = NonNull::new(raw.cast()).unwrap_or_else(|| alloc::handle_alloc_error(new_layout));
        self.cap = new_cap;
    }
}

impl<T> Default for MiniVec<T> {
    fn default() -> Self {
        Self::new()
    }
}

impl<T> Drop for MiniVec<T> {
    fn drop(&mut self) {
        while self.pop().is_some() {}
        if self.cap != 0 {
            // SAFETY: ptr was allocated with this layout and every element has been dropped.
            unsafe { alloc::dealloc(self.ptr.as_ptr().cast(), Layout::array::<T>(self.cap).expect("layout")) };
        }
    }
}
"""

P = []

P.append(dict(
    slug="vec-ops", title="Push, pop, insert, remove", level="easy", stage="use-it", tags=["Vec", "match"],
    teaches=["The core `Vec` operations and which ones panic.", "Guard clauses in a `match` for out-of-range indices."],
    statement="""
        Apply `ops` to an empty `Vec<i32>` and return it. `Pop` on an empty vec does nothing.
        `Insert(i, x)` with `i > len` and `Remove(i)` with `i >= len` do nothing instead of panicking.
    """,
    starter="""
        #[derive(Debug, Clone, Copy)]
        pub enum Op {
            Push(i32),
            Pop,
            Insert(usize, i32),
            Remove(usize),
        }

        pub fn apply(ops: &[Op]) -> Vec<i32> {
            todo!()
        }
    """,
    solution="""
        #[derive(Debug, Clone, Copy)]
        pub enum Op {
            Push(i32),
            Pop,
            Insert(usize, i32),
            Remove(usize),
        }

        pub fn apply(ops: &[Op]) -> Vec<i32> {
            let mut v = Vec::new();
            for &op in ops {
                match op {
                    Op::Push(x) => v.push(x),
                    Op::Pop => {
                        v.pop();
                    }
                    Op::Insert(i, x) if i <= v.len() => v.insert(i, x),
                    Op::Remove(i) if i < v.len() => {
                        v.remove(i);
                    }
                    Op::Insert(..) | Op::Remove(_) => {}
                }
            }
            v
        }
    """,
    visible=[
        T("push_pop", "Push 1, Push 2, Pop, Push 3", "apply(&[Op::Push(1), Op::Push(2), Op::Pop, Op::Push(3)])", "vec![1, 3]"),
        T("insert_front", "Push 2, Insert(0, 1)", "apply(&[Op::Push(2), Op::Insert(0, 1)])", "vec![1, 2]"),
        T("pop_empty", "Pop", "apply(&[Op::Pop])", "Vec::<i32>::new()"),
    ],
    hidden=[
        T("out_of_range", "Push 5, Insert(3, 9), Remove(1)", "apply(&[Op::Push(5), Op::Insert(3, 9), Op::Remove(1)])", "vec![5]"),
        T("insert_at_end", "Push 1, Insert(1, 2), Remove(0)", "apply(&[Op::Push(1), Op::Insert(1, 2), Op::Remove(0)])", "vec![2]"),
    ],
    hints=[("rust", "`insert(i, x)` allows `i == len`; `remove(i)` needs `i < len`. Both panic otherwise.")],
    notes=("Match guards keep each operation's bounds check next to the operation.", "O(n) per insert or remove", "O(n)"),
    follow_up="Which of these operations are O(1), and which shift elements?",
    related=["S3"],
))

P.append(dict(
    slug="retain-and-dedup", title="retain and dedup", level="easy", stage="use-it", tags=["retain", "dedup"],
    teaches=["`retain` filters in place without a second Vec.", "`dedup` removes only consecutive repeats."],
    statement="Remove the negative numbers from `v`, then collapse runs of equal neighbours into one.",
    examples=[("v = [1, 1, -2, 1, 3, 3, -3, 3]", "[1, 3]")],
    starter="""
        pub fn clean(v: &mut Vec<i32>) {
            todo!()
        }
    """,
    solution="""
        pub fn clean(v: &mut Vec<i32>) {
            v.retain(|&x| x >= 0);
            v.dedup();
        }
    """,
    visible=[
        T("mixed", "v = [1, 1, -2, 1, 3, 3, -3, 3]", "{ let mut v = vec![1, 1, -2, 1, 3, 3, -3, 3]; clean(&mut v); v }", "vec![1, 3]"),
        T("no_change", "v = [1, 2]", "{ let mut v = vec![1, 2]; clean(&mut v); v }", "vec![1, 2]"),
    ],
    hidden=[
        T("non_adjacent", "v = [2, 1, 2]", "{ let mut v = vec![2, 1, 2]; clean(&mut v); v }", "vec![2, 1, 2]"),
        T("all_negative", "v = [-1, -1]", "{ let mut v = vec![-1, -1]; clean(&mut v); v }", "Vec::<i32>::new()"),
    ],
    hints=[("rust", "Order matters: removing negatives can make equal values adjacent.")],
    notes=("Filtering first lets `dedup` see the neighbours that removal created.", "O(n)", "O(1)"),
    follow_up="How would you remove every duplicate, not just adjacent ones, and keep first-seen order?",
    related=["D1"],
))

P.append(dict(
    slug="sort-by-key", title="sort_by with a tie-breaker", level="easy", stage="use-it", tags=["sort_by", "Ordering::then_with"],
    teaches=["`Ordering::then_with` for multi-key sorts.", "Why `sort_by_key` with a `String` key clones every comparison."],
    statement="Sort `words` by length, shortest first, and alphabetically among words of equal length.",
    examples=[("[\"pear\", \"fig\", \"apple\", \"kiwi\"]", "[\"fig\", \"kiwi\", \"pear\", \"apple\"]")],
    starter="""
        pub fn by_len_then_alpha(words: &mut [String]) {
            todo!()
        }
    """,
    solution="""
        pub fn by_len_then_alpha(words: &mut [String]) {
            words.sort_by(|a, b| a.len().cmp(&b.len()).then_with(|| a.cmp(b)));
        }
    """,
    visible=[
        T("fruit", "[\"pear\", \"fig\", \"apple\", \"kiwi\"]", '{ let mut w: Vec<String> = ["pear", "fig", "apple", "kiwi"].map(String::from).to_vec(); by_len_then_alpha(&mut w); w }', 'vec!["fig", "kiwi", "pear", "apple"]'),
        T("empty", "[]", "{ let mut w: Vec<String> = vec![]; by_len_then_alpha(&mut w); w }", "Vec::<String>::new()"),
    ],
    hidden=[
        T("same_length", "[\"b\", \"a\", \"c\"]", '{ let mut w: Vec<String> = ["b", "a", "c"].map(String::from).to_vec(); by_len_then_alpha(&mut w); w }', 'vec!["a", "b", "c"]'),
    ],
    hints=[("rust", "Compare lengths, and only if they're equal, compare the strings: `then_with`.")],
    notes=("`then_with` only evaluates the second comparison on a tie. `sort_by_key(|w| (w.len(), w.clone()))` also works but allocates per comparison; `sort_by_cached_key` would allocate once per element.", "O(n log n)", "O(n)"),
    follow_up="When is `sort_by_cached_key` the right choice?",
    related=["S8"],
))

P.append(dict(
    slug="slices-as-views", title="Slices as views", level="easy", stage="use-it", tags=["&[T]", "ranges", "position"],
    teaches=["Returning a sub-slice borrows from the input; nothing is copied.", "`get(range)` instead of indexing when the range might be invalid."],
    statement="""
        Write `middle`, which drops the first and last elements (empty if there are fewer than two),
        and `trim_zeros`, which drops leading and trailing zeros. Both return views into the input.
    """,
    starter="""
        pub fn middle(v: &[i32]) -> &[i32] {
            todo!()
        }

        pub fn trim_zeros(v: &[i32]) -> &[i32] {
            todo!()
        }
    """,
    solution="""
        pub fn middle(v: &[i32]) -> &[i32] {
            v.get(1..v.len().saturating_sub(1)).unwrap_or(&[])
        }

        pub fn trim_zeros(v: &[i32]) -> &[i32] {
            let start = v.iter().position(|&x| x != 0).unwrap_or(v.len());
            let end = v.iter().rposition(|&x| x != 0).map_or(start, |i| i + 1);
            &v[start..end]
        }
    """,
    visible=[
        T("middle_of_four", "v = [1, 2, 3, 4]", "middle(&[1, 2, 3, 4])", "&[2, 3][..]"),
        T("middle_of_one", "v = [1]", "middle(&[1])", "&[][..]"),
        T("trim", "v = [0, 0, 5, 0, 7, 0]", "trim_zeros(&[0, 0, 5, 0, 7, 0])", "&[5, 0, 7][..]"),
    ],
    hidden=[
        T("middle_of_empty", "v = []", "middle(&[])", "&[][..]"),
        T("trim_all_zero", "v = [0, 0]", "trim_zeros(&[0, 0])", "&[][..]"),
        T("middle_of_two", "v = [1, 2]", "middle(&[1, 2])", "&[][..]"),
    ],
    hints=[("rust", "`v.get(a..b)` returns `None` when the range is invalid, including a > b."),
           ("rust", "`position` and `rposition` find the first and last non-zero.")],
    notes=("The returned slices borrow `v`, so their lifetime is tied to the input by elision.", "O(n)", "O(1)"),
    follow_up="Why can these functions omit lifetime annotations?",
    related=["L3"],
))

P.append(dict(
    slug="fix-neighbour-loop", title="Fix: off-by-one in a neighbour loop", mode="fix", level="easy", stage="use-it", tags=["windows", "index out of bounds"],
    teaches=["`windows(2)` yields each pair of neighbours without index arithmetic."],
    statement="`pair_sums` should return the sum of each pair of neighbours. It panics.",
    examples=[("v = [1, 2, 3]", "[3, 5]")],
    starter="""
        /// Sums of neighbouring pairs: [a, b, c] → [a + b, b + c].
        pub fn pair_sums(v: &[i32]) -> Vec<i32> {
            let mut out = Vec::new();
            for i in 0..v.len() {
                out.push(v[i] + v[i + 1]);
            }
            out
        }
    """,
    solution="""
        /// Sums of neighbouring pairs: [a, b, c] → [a + b, b + c].
        pub fn pair_sums(v: &[i32]) -> Vec<i32> {
            v.windows(2).map(|w| w[0] + w[1]).collect()
        }
    """,
    visible=[
        T("three", "v = [1, 2, 3]", "pair_sums(&[1, 2, 3])", "vec![3, 5]"),
        T("one", "v = [9]", "pair_sums(&[9])", "Vec::<i32>::new()"),
    ],
    hidden=[
        T("empty", "v = []", "pair_sums(&[])", "Vec::<i32>::new()"),
        T("negatives", "v = [-1, 1, -1]", "pair_sums(&[-1, 1, -1])", "vec![0, 0]"),
    ],
    hints=[("approach", "The last index has no right neighbour."), ("rust", "Slices can hand you overlapping pairs directly.")],
    notes=("`windows(2)` yields nothing for fewer than two elements, so the empty and single cases need no special handling.", "O(n)", "O(n)"),
    follow_up="How is `windows` different from `chunks`?",
    related=["S6"],
))

P.append(dict(
    slug="rotate-in-place", title="Rotate a slice in place", level="easy", stage="use-it", tags=["reverse", "rotate"],
    teaches=["Three reversals rotate a slice in O(1) space.", "Reduce `k` modulo the length first."],
    statement="Rotate `v` right by `k` positions in place.",
    examples=[("v = [1, 2, 3, 4, 5], k = 2", "[4, 5, 1, 2, 3]")],
    starter="""
        pub fn rotate_right(v: &mut [i32], k: usize) {
            todo!()
        }
    """,
    solution="""
        pub fn rotate_right(v: &mut [i32], k: usize) {
            if v.is_empty() {
                return;
            }
            let k = k % v.len();
            v.reverse();
            v[..k].reverse();
            v[k..].reverse();
        }
    """,
    visible=[
        T("two", "v = [1, 2, 3, 4, 5], k = 2", "{ let mut v = [1, 2, 3, 4, 5]; rotate_right(&mut v, 2); v }", "[4, 5, 1, 2, 3]"),
        T("full_turn", "v = [1, 2], k = 2", "{ let mut v = [1, 2]; rotate_right(&mut v, 2); v }", "[1, 2]"),
    ],
    hidden=[
        T("empty", "v = [], k = 3", "{ let mut v: [i32; 0] = []; rotate_right(&mut v, 3); v }", "[]"),
        T("large_k", "v = [1, 2, 3], k = 7", "{ let mut v = [1, 2, 3]; rotate_right(&mut v, 7); v }", "[3, 1, 2]"),
    ],
    hints=[("approach", "Reverse the whole slice, then reverse the first k and the rest separately."), ("edge case", "k can be larger than the length, and the length can be 0.")],
    notes=("std has `slice::rotate_right`, which does the same in O(n) time and O(1) space; the three-reversal trick is what interviews ask for.", "O(n)", "O(1)"),
    follow_up="Prove that the three reversals produce the rotation.",
    related=["D2"],
))

P.append(dict(
    slug="remove-duplicates-sorted", title="Remove duplicates from a sorted slice", level="easy", stage="use-it", tags=["two pointers", "in place"],
    teaches=["A write index for in-place compaction.", "Returning a length instead of shrinking the slice."],
    statement="`v` is sorted. Move its distinct values to the front, in order, and return how many there are.",
    examples=[("v = [0, 0, 1, 1, 1, 2]", "3, with v starting [0, 1, 2]")],
    starter="""
        pub fn dedup_sorted(v: &mut [i32]) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn dedup_sorted(v: &mut [i32]) -> usize {
            if v.is_empty() {
                return 0;
            }
            let mut write = 1;
            for read in 1..v.len() {
                if v[read] != v[write - 1] {
                    v[write] = v[read];
                    write += 1;
                }
            }
            write
        }
    """,
    visible=[
        T("classic", "v = [0, 0, 1, 1, 1, 2]", "{ let mut v = [0, 0, 1, 1, 1, 2]; let k = dedup_sorted(&mut v); v[..k].to_vec() }", "vec![0, 1, 2]"),
        T("count", "v = [1, 1, 2]", "dedup_sorted(&mut [1, 1, 2])", "2"),
    ],
    hidden=[
        T("empty", "v = []", "dedup_sorted(&mut [])", "0"),
        T("all_distinct", "v = [-3, 0, 7]", "{ let mut v = [-3, 0, 7]; let k = dedup_sorted(&mut v); v[..k].to_vec() }", "vec![-3, 0, 7]"),
    ],
    hints=[("approach", "Keep a write position; copy a value there only if it differs from the last value written.")],
    notes=("A slice can't shrink, so the length is the result. `Vec::dedup` does this and then truncates.", "O(n)", "O(1)"),
    follow_up="How would you allow each value at most twice?",
    related=["D2"],
))

P.append(dict(
    slug="exact-capacity", title="Capacity and reallocation", level="medium", stage="understand-it", tags=["with_capacity", "String"],
    source="W41",
    teaches=["Pre-sizing a `String` or `Vec` avoids reallocating as it grows.", "Computing the exact final length up front."],
    statement="""
        Join `parts` with `sep` between them. The result must be allocated exactly once:
        its capacity must equal its length.
    """,
    examples=[("parts = [\"a\", \"bb\", \"ccc\"], sep = \", \"", "\"a, bb, ccc\"")],
    starter="""
        pub fn join_with(parts: &[&str], sep: &str) -> String {
            todo!()
        }
    """,
    solution="""
        pub fn join_with(parts: &[&str], sep: &str) -> String {
            let total = parts.iter().map(|p| p.len()).sum::<usize>() + sep.len() * parts.len().saturating_sub(1);
            let mut out = String::with_capacity(total);
            for (i, p) in parts.iter().enumerate() {
                if i > 0 {
                    out.push_str(sep);
                }
                out.push_str(p);
            }
            out
        }
    """,
    visible=[
        T("three", "parts = [\"a\", \"bb\", \"ccc\"], sep = \", \"", '{ let s = join_with(&["a", "bb", "ccc"], ", "); (s.clone(), s.capacity() == s.len()) }', '("a, bb, ccc".to_string(), true)'),
        T("one", "parts = [\"solo\"], sep = \"-\"", '{ let s = join_with(&["solo"], "-"); (s.clone(), s.capacity() == s.len()) }', '("solo".to_string(), true)'),
    ],
    hidden=[
        T("none", "parts = [], sep = \",\"", 'join_with(&[], ",")', '""'),
        T("many", "100 parts of \"xyz\", sep = \"/\"", '{ let parts = vec!["xyz"; 100]; let s = join_with(&parts, "/"); (s.len(), s.capacity() == s.len()) }', "(399, true)"),
    ],
    hints=[("approach", "Add up the parts' lengths and the separators before building anything."), ("rust", "`String::with_capacity(n)`, then `push_str`.")],
    notes=("One allocation of the exact size. std's `[&str]::join` computes the same total internally.", "O(total length)", "O(total length)"),
    follow_up="How much memory does pushing into an empty `String` waste on average?",
    related=["Y4", "S2"],
))

P.append(dict(
    slug="predict-reallocations", title="Predict the allocation count", level="medium", stage="understand-it", tags=["capacity", "growth"],
    teaches=["`Vec` grows geometrically: amortised O(1) push.", "Its first allocation holds 4 small elements, not 1."],
    statement="""
        Don't run anything yet. Pushing the numbers `0..100` one at a time into `Vec::<u32>::new()`:
        how many times does the capacity change, and what is it at the end? Fill in the constants.
    """,
    starter="""
        /// How many times the capacity changes while pushing 0..100 into Vec::<u32>::new().
        pub const REALLOCATIONS: usize = 0;

        /// The capacity after those 100 pushes.
        pub const FINAL_CAPACITY: usize = 0;
    """,
    solution="""
        /// How many times the capacity changes while pushing 0..100 into Vec::<u32>::new().
        /// 0 → 4 → 8 → 16 → 32 → 64 → 128.
        pub const REALLOCATIONS: usize = 6;

        /// The capacity after those 100 pushes.
        pub const FINAL_CAPACITY: usize = 128;
    """,
    visible=[
        """
        #[test]
        fn reallocation_count() {
            let mut v: Vec<u32> = Vec::new();
            let (mut changes, mut cap) = (0, v.capacity());
            for i in 0..100 {
                v.push(i);
                if v.capacity() != cap {
                    changes += 1;
                    cap = v.capacity();
                }
            }
            check!("push 0..100 into Vec::<u32>::new()", REALLOCATIONS, changes);
        }
        """,
        """
        #[test]
        fn final_capacity() {
            let mut v: Vec<u32> = Vec::new();
            v.extend(0..100u32);
            let mut w: Vec<u32> = Vec::new();
            for i in 0..100 {
                w.push(i);
            }
            check!("capacity after 100 pushes", FINAL_CAPACITY, w.capacity());
        }
        """,
    ],
    hidden=[
        """
        #[test]
        fn with_capacity_never_reallocates() {
            let mut v: Vec<u32> = Vec::with_capacity(100);
            let cap = v.capacity();
            v.extend(0..100u32);
            check!("Vec::with_capacity(100) then 100 pushes", (REALLOCATIONS > 0, v.capacity() == cap), (true, true));
        }
        """,
    ],
    hints=[("rust", "Capacity doubles when full. What's the first non-zero capacity for a small element type?")],
    notes=("std's minimum non-zero capacity is 4 for elements up to 1 KiB, then it doubles, so 100 pushes cost 6 allocations and copy fewer than 128 elements in total.", "O(1) amortised per push", "O(n)"),
    follow_up="Why does doubling give amortised O(1) push, while growing by a constant doesn't?",
    related=["Y1", "Y4"],
))

P.append(dict(
    slug="drain-splice-split-off", title="drain, splice and split_off", level="medium", stage="understand-it", tags=["split_off", "splice"],
    teaches=["`split_off` moves the tail into a new Vec.", "`splice` replaces a range and returns what it removed."],
    statement="""
        Write `take_tail`, which removes everything from index `at` on and returns it (empty if `at`
        is past the end), and `replace_range`, which replaces `v[start..end]` with `with` and returns
        the removed values.
    """,
    starter="""
        pub fn take_tail(v: &mut Vec<i32>, at: usize) -> Vec<i32> {
            todo!()
        }

        pub fn replace_range(v: &mut Vec<i32>, start: usize, end: usize, with: &[i32]) -> Vec<i32> {
            todo!()
        }
    """,
    solution="""
        pub fn take_tail(v: &mut Vec<i32>, at: usize) -> Vec<i32> {
            let at = at.min(v.len());
            v.split_off(at)
        }

        pub fn replace_range(v: &mut Vec<i32>, start: usize, end: usize, with: &[i32]) -> Vec<i32> {
            v.splice(start..end, with.iter().copied()).collect()
        }
    """,
    visible=[
        T("tail", "v = [1, 2, 3, 4], at = 2", "{ let mut v = vec![1, 2, 3, 4]; let t = take_tail(&mut v, 2); (v, t) }", "(vec![1, 2], vec![3, 4])"),
        T("splice", "v = [1, 2, 3, 4], replace 1..3 with [9]", "{ let mut v = vec![1, 2, 3, 4]; let r = replace_range(&mut v, 1, 3, &[9]); (v, r) }", "(vec![1, 9, 4], vec![2, 3])"),
    ],
    hidden=[
        T("tail_past_end", "v = [1], at = 5", "{ let mut v = vec![1]; let t = take_tail(&mut v, 5); (v, t) }", "(vec![1], vec![])"),
        T("splice_insert", "v = [1, 4], replace 1..1 with [2, 3]", "{ let mut v = vec![1, 4]; let r = replace_range(&mut v, 1, 1, &[2, 3]); (v, r) }", "(vec![1, 2, 3, 4], vec![])"),
    ],
    hints=[("rust", "`split_off` panics when `at > len`; clamp it."), ("rust", "`splice` returns an iterator of the removed items.")],
    notes=("`splice` shifts the tail once, however long the replacement is. The removed items are yielded as the iterator is consumed, which is why it's collected immediately.", "O(n)", "O(n)"),
    follow_up="What happens to the Vec if you drop the `Splice` iterator without consuming it?",
    related=["S6"],
))

P.append(dict(
    slug="chunks-and-windows", title="chunks and windows", level="medium", stage="understand-it", tags=["chunks", "windows"],
    teaches=["`chunks` for non-overlapping groups, `windows` for overlapping ones.", "`max()` on an iterator returns an `Option`."],
    statement="""
        Write `chunk_sums`, the sum of each consecutive group of `size` (the last may be shorter), and
        `max_window_sum`, the largest sum of `k` consecutive values or `None` if `v` is shorter than `k`.
        `size` and `k` are at least 1.
    """,
    starter="""
        pub fn chunk_sums(v: &[i32], size: usize) -> Vec<i32> {
            todo!()
        }

        pub fn max_window_sum(v: &[i32], k: usize) -> Option<i32> {
            todo!()
        }
    """,
    solution="""
        pub fn chunk_sums(v: &[i32], size: usize) -> Vec<i32> {
            v.chunks(size).map(|c| c.iter().sum()).collect()
        }

        pub fn max_window_sum(v: &[i32], k: usize) -> Option<i32> {
            v.windows(k).map(|w| w.iter().sum()).max()
        }
    """,
    visible=[
        T("chunks", "v = [1, 2, 3, 4, 5], size = 2", "chunk_sums(&[1, 2, 3, 4, 5], 2)", "vec![3, 7, 5]"),
        T("windows", "v = [1, -2, 3, 4, -1], k = 2", "max_window_sum(&[1, -2, 3, 4, -1], 2)", "Some(7)"),
    ],
    hidden=[
        T("window_too_big", "v = [1, 2], k = 3", "max_window_sum(&[1, 2], 3)", "None"),
        T("chunks_empty", "v = [], size = 3", "chunk_sums(&[], 3)", "Vec::<i32>::new()"),
    ],
    hints=[("rust", "Both are slice methods that return iterators of sub-slices.")],
    notes=("This `max_window_sum` is O(n·k); a running sum that adds the new element and subtracts the old one is O(n).", "O(n·k)", "O(1)"),
    follow_up="Rewrite `max_window_sum` in O(n).",
    related=["D2"],
))

P.append(dict(
    slug="split-at-mut", title="split_at_mut for two halves", level="medium", stage="understand-it", tags=["split_at_mut", "E0499"],
    teaches=["`split_at_mut` gives two non-overlapping `&mut` into one slice.", "Why `&mut v[..m]` and `&mut v[m..]` at once doesn't compile."],
    statement="Add each value in the first half of `v` to the matching value in the second half: `v[mid + i] += v[i]` for `i < len / 2`.",
    examples=[("v = [1, 2, 10, 20]", "[1, 2, 11, 22]")],
    starter="""
        pub fn add_halves(v: &mut [i32]) {
            todo!()
        }
    """,
    solution="""
        pub fn add_halves(v: &mut [i32]) {
            let mid = v.len() / 2;
            let (first, second) = v.split_at_mut(mid);
            for (a, b) in first.iter().zip(second.iter_mut()) {
                *b += *a;
            }
        }
    """,
    visible=[
        T("even", "v = [1, 2, 10, 20]", "{ let mut v = [1, 2, 10, 20]; add_halves(&mut v); v }", "[1, 2, 11, 22]"),
        T("odd", "v = [1, 5, 5]", "{ let mut v = [1, 5, 5]; add_halves(&mut v); v }", "[1, 6, 5]"),
    ],
    hidden=[
        T("empty", "v = []", "{ let mut v: [i32; 0] = []; add_halves(&mut v); v }", "[]"),
        T("one", "v = [4]", "{ let mut v = [4]; add_halves(&mut v); v }", "[4]"),
    ],
    hints=[("rust", "Two `&mut` borrows of `v` at once won't compile, even to different ranges. Which slice method splits one borrow into two?")],
    notes=("`split_at_mut` is safe because the halves provably don't overlap; it's implemented with `unsafe` inside std.", "O(n)", "O(1)"),
    follow_up="How would you get `&mut` to two arbitrary indices i and j?",
    related=["L2"],
))

P.append(dict(
    slug="fix-push-while-reading", title="Fix: push to a Vec while reading it", mode="fix", level="medium", stage="understand-it", tags=["E0502", "extend_from_within"],
    teaches=["You can't push to a Vec while iterating it: a push may reallocate under the iterator.", "`extend_from_within` copies a range of the Vec onto its end in one call."],
    statement="`double_up` should append a copy of every element, so `[1, 2]` becomes `[1, 2, 1, 2]`. It doesn't compile.",
    starter="""
        /// Appends a copy of every element: [1, 2] → [1, 2, 1, 2].
        pub fn double_up(v: &mut Vec<i32>) {
            for x in v.iter() {
                v.push(*x);
            }
        }
    """,
    solution="""
        /// Appends a copy of every element: [1, 2] → [1, 2, 1, 2].
        pub fn double_up(v: &mut Vec<i32>) {
            v.extend_from_within(..);
        }
    """,
    rules=dict(methods=["clone", "to_vec", "to_owned", "collect"]),
    visible=[
        T("two", "v = [1, 2]", "{ let mut v = vec![1, 2]; double_up(&mut v); v }", "vec![1, 2, 1, 2]"),
        T("empty", "v = []", "{ let mut v: Vec<i32> = vec![]; double_up(&mut v); v }", "Vec::<i32>::new()"),
    ],
    hidden=[
        T("big", "v = 0..1000", "{ let mut v: Vec<i32> = (0..1000).collect(); double_up(&mut v); (v.len(), v[1000], v[1999]) }", "(2000, 0, 999)"),
    ],
    hints=[("rust", "The loop holds a shared borrow of `v` while `push` needs a mutable one (E0502)."),
           ("rust", "`Vec` has a method that appends a copy of a range of itself, with no temporary Vec.")],
    notes=("If the loop compiled, `push` could reallocate and leave the iterator pointing at freed memory; that's exactly what the borrow checker prevents.", "O(n)", "O(n)"),
    follow_up="What would go wrong in C++ with the same loop?",
    related=["L2"],
))

P.append(dict(
    slug="flat-grid", title="A 2-D grid in one Vec", level="medium", stage="understand-it", tags=["strides", "Vec<u8>"],
    teaches=["Row-major indexing: `y * width + x`.", "Returning `&[u8]` rows straight from the backing Vec."],
    statement="""
        Store a `w × h` grid of bytes in one `Vec<u8>`. `get` and `set` return `None` / `false` out of
        bounds; `row(y)` returns that row as a slice.
    """,
    starter="""
        pub struct Grid {
            w: usize,
            h: usize,
            cells: Vec<u8>,
        }

        impl Grid {
            pub fn new(w: usize, h: usize) -> Self {
                todo!()
            }

            pub fn get(&self, x: usize, y: usize) -> Option<u8> {
                todo!()
            }

            pub fn set(&mut self, x: usize, y: usize, value: u8) -> bool {
                todo!()
            }

            pub fn row(&self, y: usize) -> Option<&[u8]> {
                todo!()
            }
        }
    """,
    solution="""
        pub struct Grid {
            w: usize,
            h: usize,
            cells: Vec<u8>,
        }

        impl Grid {
            pub fn new(w: usize, h: usize) -> Self {
                Grid { w, h, cells: vec![0; w * h] }
            }

            fn index(&self, x: usize, y: usize) -> Option<usize> {
                (x < self.w && y < self.h).then(|| y * self.w + x)
            }

            pub fn get(&self, x: usize, y: usize) -> Option<u8> {
                self.index(x, y).map(|i| self.cells[i])
            }

            pub fn set(&mut self, x: usize, y: usize, value: u8) -> bool {
                match self.index(x, y) {
                    Some(i) => {
                        self.cells[i] = value;
                        true
                    }
                    None => false,
                }
            }

            pub fn row(&self, y: usize) -> Option<&[u8]> {
                (y < self.h).then(|| &self.cells[y * self.w..(y + 1) * self.w])
            }
        }
    """,
    visible=[
        T("set_and_get", "3×2 grid, set (2, 1) = 7", "{ let mut g = Grid::new(3, 2); g.set(2, 1, 7); (g.get(2, 1), g.get(0, 0)) }", "(Some(7), Some(0))"),
        T("row", "3×2 grid, set (1, 1) = 5", "g.row(1)", "Some(&[0, 5, 0][..])", setup="let mut g = Grid::new(3, 2);\ng.set(1, 1, 5);"),
        T("out_of_bounds", "3×2 grid", "{ let mut g = Grid::new(3, 2); (g.get(3, 0), g.set(0, 2, 1), g.row(2).is_none()) }", "(None, false, true)"),
    ],
    hidden=[
        T("empty_grid", "0×0 grid", "{ let g = Grid::new(0, 0); (g.get(0, 0), g.row(0).is_none()) }", "(None, true)"),
        T("x_not_wrapping", "2×2 grid, get (2, 0)", "{ let mut g = Grid::new(2, 2); g.set(0, 1, 9); g.get(2, 0) }", "None"),
    ],
    hints=[("approach", "Cell (x, y) lives at index y · width + x."), ("edge case", "Check x against the width, or (width, 0) silently reads the next row.")],
    notes=("One allocation and contiguous rows make this cache-friendly compared with `Vec<Vec<u8>>`.", "O(1) per access", "O(w · h)"),
    follow_up="When is `Vec<Vec<T>>` still the better choice?",
    related=["Y1", "D9"],
))

P.append(dict(
    slug="keep-sorted", title="Keep a Vec sorted with partition_point", level="medium", stage="understand-it", tags=["partition_point", "binary search"],
    teaches=["`partition_point` finds the insertion index in O(log n).", "Counting a range with two partition points."],
    statement="`v` is sorted. Write `insert_sorted`, which inserts `x` keeping `v` sorted, and `count_in_range`, how many values lie in `lo..=hi`.",
    starter="""
        pub fn insert_sorted(v: &mut Vec<i32>, x: i32) {
            todo!()
        }

        pub fn count_in_range(v: &[i32], lo: i32, hi: i32) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn insert_sorted(v: &mut Vec<i32>, x: i32) {
            let i = v.partition_point(|&y| y < x);
            v.insert(i, x);
        }

        pub fn count_in_range(v: &[i32], lo: i32, hi: i32) -> usize {
            let start = v.partition_point(|&y| y < lo);
            let end = v.partition_point(|&y| y <= hi);
            end.saturating_sub(start)
        }
    """,
    visible=[
        T("insert", "v = [1, 3, 5], x = 4", "{ let mut v = vec![1, 3, 5]; insert_sorted(&mut v, 4); v }", "vec![1, 3, 4, 5]"),
        T("count", "v = [1, 2, 2, 3, 7], lo = 2, hi = 3", "count_in_range(&[1, 2, 2, 3, 7], 2, 3)", "3"),
    ],
    hidden=[
        T("insert_front_and_back", "v = [5], x = 1 then 9", "{ let mut v = vec![5]; insert_sorted(&mut v, 1); insert_sorted(&mut v, 9); v }", "vec![1, 5, 9]"),
        T("empty_range", "v = [1, 2, 3], lo = 5, hi = 1", "count_in_range(&[1, 2, 3], 5, 1)", "0"),
    ],
    hints=[("rust", "`partition_point(|&y| y < x)` returns the first index where the predicate is false.")],
    notes=("The search is O(log n), but `insert` still shifts the tail in O(n). For many insertions, a `BTreeSet` is better.", "O(n) insert, O(log n) count", "O(1)"),
    follow_up="When would you switch from a sorted Vec to a BTreeSet?",
    related=["D4", "S4"],
))

P.append(dict(
    slug="minivec-core", title="MiniVec: push, pop and Drop", level="hard", stage="build-it", tags=["std::alloc", "unsafe", "NonNull"],
    teaches=["What `Vec` is: a pointer, a capacity and a length.", "Growing with `alloc`/`realloc` and freeing in `Drop`.", "Writing a `// SAFETY:` comment for every `unsafe` block."],
    statement="""
        Build `MiniVec<T>` on a raw allocation from `std::alloc`, without using `Vec`. Implement `new`,
        `push`, `pop`, `get`, `len`, `capacity` and `Drop`. Grow from 0 to 4, then double. `Drop` must drop
        every remaining element and free the buffer. You don't need to support zero-sized `T`.
    """,
    starter="""
        use std::alloc::{self, Layout};
        use std::marker::PhantomData;
        use std::ptr::{self, NonNull};

        /// A growable array on a raw allocation. Zero-sized `T` isn't supported.
        pub struct MiniVec<T> {
            ptr: NonNull<T>,
            cap: usize,
            len: usize,
            _owns: PhantomData<T>,
        }

        impl<T> MiniVec<T> {
            pub fn new() -> Self {
                todo!()
            }

            pub fn len(&self) -> usize {
                todo!()
            }

            pub fn capacity(&self) -> usize {
                todo!()
            }

            pub fn push(&mut self, value: T) {
                todo!()
            }

            pub fn pop(&mut self) -> Option<T> {
                todo!()
            }

            pub fn get(&self, i: usize) -> Option<&T> {
                todo!()
            }
        }

        impl<T> Drop for MiniVec<T> {
            fn drop(&mut self) {
                // TODO: drop the remaining elements, then free the buffer.
                // (Left empty rather than todo!(): a panic in drop during a failing test aborts every test.)
            }
        }
    """,
    solution=MINIVEC,
    visible=[
        T("push_pop", "push 1, 2, 3 then pop twice", "{ let mut v = MiniVec::new(); v.push(1); v.push(2); v.push(3); (v.pop(), v.pop(), v.len()) }", "(Some(3), Some(2), 1)"),
        T("growth", "capacity after 0, 1 and 5 pushes", "{ let mut v = MiniVec::new(); let a = v.capacity(); v.push(1u64); let b = v.capacity(); for i in 0..4 { v.push(i); } (a, b, v.capacity()) }", "(0, 4, 8)"),
        T("get", "push \"a\", \"b\"", '{ let mut v = MiniVec::new(); v.push(String::from("a")); v.push(String::from("b")); (v.get(1).cloned(), v.get(2).cloned()) }', '(Some("b".to_string()), None)'),
    ],
    hidden=[
        """
        use std::rc::Rc;

        #[test]
        fn drop_releases_every_element() {
            let counter = Rc::new(());
            {
                let mut v = MiniVec::new();
                for _ in 0..10 {
                    v.push(Rc::clone(&counter));
                }
                v.pop();
            }
            check!("10 Rc clones pushed, one popped, then the MiniVec dropped", Rc::strong_count(&counter), 1);
        }

        #[test]
        fn many_strings_survive_reallocation() {
            let mut v = MiniVec::new();
            for i in 0..1000 {
                v.push(i.to_string());
            }
            check!("push 0..1000 as Strings", (v.len(), v.get(999).cloned()), (1000, Some("999".to_string())));
        }
        """,
        T("pop_empty", "new MiniVec", "MiniVec::<u8>::new().pop()", "None"),
    ],
    hints=[("approach", "`new` uses `NonNull::dangling()` and capacity 0; allocate on the first push."),
           ("rust", "`Layout::array::<T>(cap)` describes the buffer; `alloc`, `realloc` and `dealloc` must all get the same layout for the same block."),
           ("rust", "`ptr::write` into uninitialised memory and `ptr::read` out of it; plain assignment would drop garbage.")],
    notes=("`PhantomData<T>` tells the compiler the MiniVec owns `T`s, which matters for drop checking. `Drop` pops everything first so each element's destructor runs exactly once, then frees the buffer.", "O(1) amortised push", "O(n)"),
    follow_up="What would you need to change to support zero-sized types?",
    related=["Y2", "S7", "Y1"],
))

P.append(dict(
    slug="minivec-deref", title="MiniVec: slices and Deref", level="hard", stage="build-it", tags=["Deref", "slice::from_raw_parts"],
    teaches=["Implementing `Deref<Target = [T]>` gives a collection every slice method.", "`slice::from_raw_parts` and its safety contract."],
    statement="""
        `MiniVec` works. Add `as_slice` and `as_mut_slice`, then `Deref` and `DerefMut` to `[T]`,
        so `v.iter()`, `v.sort()` and `&v[1..]` all work on a `MiniVec`.
    """,
    starter=MINIVEC + """
impl<T> MiniVec<T> {
    pub fn as_slice(&self) -> &[T] {
        todo!()
    }

    pub fn as_mut_slice(&mut self) -> &mut [T] {
        todo!()
    }
}

impl<T> std::ops::Deref for MiniVec<T> {
    type Target = [T];
    fn deref(&self) -> &[T] {
        self.as_slice()
    }
}

impl<T> std::ops::DerefMut for MiniVec<T> {
    fn deref_mut(&mut self) -> &mut [T] {
        self.as_mut_slice()
    }
}
""",
    solution=MINIVEC + """
impl<T> MiniVec<T> {
    pub fn as_slice(&self) -> &[T] {
        // SAFETY: ptr is non-null and aligned (dangling is fine when len is 0), and the first len
        // elements are initialised. The slice borrows self, so it can't outlive the buffer.
        unsafe { std::slice::from_raw_parts(self.ptr.as_ptr(), self.len) }
    }

    pub fn as_mut_slice(&mut self) -> &mut [T] {
        // SAFETY: as above, and &mut self guarantees no other reference to the elements exists.
        unsafe { std::slice::from_raw_parts_mut(self.ptr.as_ptr(), self.len) }
    }
}

impl<T> std::ops::Deref for MiniVec<T> {
    type Target = [T];
    fn deref(&self) -> &[T] {
        self.as_slice()
    }
}

impl<T> std::ops::DerefMut for MiniVec<T> {
    fn deref_mut(&mut self) -> &mut [T] {
        self.as_mut_slice()
    }
}
""",
    visible=[
        T("iter_sum", "push 1..=4", "{ let mut v = MiniVec::new(); for i in 1..=4 { v.push(i); } v.iter().sum::<i32>() }", "10"),
        T("sort", "push 3, 1, 2", "{ let mut v = MiniVec::new(); v.push(3); v.push(1); v.push(2); v.sort(); v.as_slice().to_vec() }", "vec![1, 2, 3]"),
    ],
    hidden=[
        T("empty_slice", "new MiniVec", "MiniVec::<String>::new().as_slice().len()", "0"),
        T("range_index", "push 10, 20, 30", "{ let mut v = MiniVec::new(); v.push(10); v.push(20); v.push(30); v[1..].to_vec() }", "vec![20, 30]"),
        T("mutate_through_slice", "push 1, 2", "{ let mut v = MiniVec::new(); v.push(1); v.push(2); for x in v.iter_mut() { *x *= 5; } v.as_slice().to_vec() }", "vec![5, 10]"),
    ],
    hints=[("rust", "`std::slice::from_raw_parts(ptr, len)` builds a slice from a pointer and a length."),
           ("edge case", "Is a dangling pointer OK when len is 0? Read the function's safety section.")],
    notes=("Once `Deref` to `[T]` exists, every slice method works through auto-deref, which is how `Vec` gets `sort`, `iter` and indexing.", "O(1)", "O(1)"),
    follow_up="Why shouldn't you implement Deref for types that aren't smart pointers or containers?",
    related=["S8", "Y2"],
))

P.append(dict(
    slug="small-vec", title="An inline small-vector", level="hard", stage="build-it", tags=["enum", "spill to heap"],
    teaches=["Store up to N items inline and spill to a `Vec` after that.", "Replacing `*self` with a new variant after moving data out."],
    statement="""
        `SmallVec4<T>` keeps up to four items inline, with no heap allocation, and moves them into a
        `Vec` when a fifth arrives. Implement `new`, `push`, `len`, `get` and `is_inline` without `unsafe`.
    """,
    starter="""
        pub enum SmallVec4<T> {
            Inline { items: [Option<T>; 4], len: usize },
            Heap(Vec<T>),
        }

        impl<T> SmallVec4<T> {
            pub fn new() -> Self {
                todo!()
            }

            pub fn push(&mut self, value: T) {
                todo!()
            }

            pub fn len(&self) -> usize {
                todo!()
            }

            pub fn get(&self, i: usize) -> Option<&T> {
                todo!()
            }

            pub fn is_inline(&self) -> bool {
                todo!()
            }
        }
    """,
    solution="""
        pub enum SmallVec4<T> {
            Inline { items: [Option<T>; 4], len: usize },
            Heap(Vec<T>),
        }

        impl<T> SmallVec4<T> {
            pub fn new() -> Self {
                SmallVec4::Inline { items: [None, None, None, None], len: 0 }
            }

            pub fn push(&mut self, value: T) {
                match self {
                    SmallVec4::Inline { items, len } if *len < 4 => {
                        items[*len] = Some(value);
                        *len += 1;
                    }
                    SmallVec4::Inline { items, .. } => {
                        let mut heap: Vec<T> = Vec::with_capacity(8);
                        heap.extend(items.iter_mut().filter_map(Option::take));
                        heap.push(value);
                        *self = SmallVec4::Heap(heap);
                    }
                    SmallVec4::Heap(heap) => heap.push(value),
                }
            }

            pub fn len(&self) -> usize {
                match self {
                    SmallVec4::Inline { len, .. } => *len,
                    SmallVec4::Heap(heap) => heap.len(),
                }
            }

            pub fn get(&self, i: usize) -> Option<&T> {
                match self {
                    SmallVec4::Inline { items, len } if i < *len => items[i].as_ref(),
                    SmallVec4::Inline { .. } => None,
                    SmallVec4::Heap(heap) => heap.get(i),
                }
            }

            pub fn is_inline(&self) -> bool {
                matches!(self, SmallVec4::Inline { .. })
            }
        }

        impl<T> Default for SmallVec4<T> {
            fn default() -> Self {
                Self::new()
            }
        }
    """,
    visible=[
        T("stays_inline", "push 4 items", "{ let mut v = SmallVec4::new(); for i in 0..4 { v.push(i); } (v.len(), v.is_inline(), v.get(3).copied()) }", "(4, true, Some(3))"),
        T("spills", "push 5 items", "{ let mut v = SmallVec4::new(); for i in 0..5 { v.push(i * 10); } (v.len(), v.is_inline(), v.get(0).copied(), v.get(4).copied()) }", "(5, false, Some(0), Some(40))"),
    ],
    hidden=[
        T("get_past_len", "push 1 item", "{ let mut v = SmallVec4::new(); v.push('a'); (v.get(1).copied(), v.get(0).copied()) }", "(None, Some('a'))"),
        T("strings", "push 6 Strings", '{ let mut v = SmallVec4::new(); for w in ["a", "b", "c", "d", "e", "f"] { v.push(w.to_string()); } v.get(5).cloned() }', 'Some("f".to_string())'),
    ],
    hints=[("approach", "When the inline array is full, move its items into a new Vec, push the new one, and switch variants."),
           ("rust", "`Option::take` moves each item out of the array and leaves `None`, so nothing is cloned.")],
    notes=("`[Option<T>; 4]` keeps this safe; real small-vectors use `MaybeUninit` to avoid the `Option` tags. Assigning `*self` after the items are moved out is fine because the borrow of `items` has ended.", "O(1) amortised push", "O(n)"),
    follow_up="How does `MaybeUninit<[T; N]>` let you drop the Option tags, and what does it cost in unsafe code?",
    related=["Y1", "S11"],
))

P.append(dict(
    slug="ring-buffer", title="Ring buffer on a boxed slice", level="hard", stage="build-it", tags=["Box<[T]>", "modular index"],
    teaches=["`Box<[T]>` for a fixed-size buffer: no capacity field, no growth.", "Head plus length with wrap-around indexing."],
    statement="""
        `Ring<T>` holds up to `capacity` items. `push` adds to the newest end and, when full, evicts
        and returns the oldest. `iter` yields oldest to newest.
    """,
    starter="""
        pub struct Ring<T> {
            buf: Box<[Option<T>]>,
            head: usize,
            len: usize,
        }

        impl<T> Ring<T> {
            /// Panics if `capacity` is 0.
            pub fn with_capacity(capacity: usize) -> Self {
                todo!()
            }

            /// Adds `value`, returning the evicted oldest value if the ring was full.
            pub fn push(&mut self, value: T) -> Option<T> {
                todo!()
            }

            pub fn len(&self) -> usize {
                todo!()
            }

            pub fn iter(&self) -> impl Iterator<Item = &T> + '_ {
                std::iter::empty() // TODO
            }
        }
    """,
    solution="""
        pub struct Ring<T> {
            buf: Box<[Option<T>]>,
            head: usize,
            len: usize,
        }

        impl<T> Ring<T> {
            /// Panics if `capacity` is 0.
            pub fn with_capacity(capacity: usize) -> Self {
                assert!(capacity > 0, "capacity must be at least 1");
                Ring { buf: (0..capacity).map(|_| None).collect(), head: 0, len: 0 }
            }

            /// Adds `value`, returning the evicted oldest value if the ring was full.
            pub fn push(&mut self, value: T) -> Option<T> {
                let cap = self.buf.len();
                if self.len == cap {
                    let old = self.buf[self.head].replace(value);
                    self.head = (self.head + 1) % cap;
                    old
                } else {
                    self.buf[(self.head + self.len) % cap] = Some(value);
                    self.len += 1;
                    None
                }
            }

            pub fn len(&self) -> usize {
                self.len
            }

            pub fn is_empty(&self) -> bool {
                self.len == 0
            }

            pub fn iter(&self) -> impl Iterator<Item = &T> + '_ {
                let cap = self.buf.len();
                (0..self.len).map(move |i| self.buf[(self.head + i) % cap].as_ref().expect("live slot"))
            }
        }
    """,
    visible=[
        T("not_full", "capacity 3, push 1, 2", "{ let mut r = Ring::with_capacity(3); r.push(1); r.push(2); r.iter().copied().collect::<Vec<_>>() }", "vec![1, 2]"),
        T("evicts_oldest", "capacity 2, push 1, 2, 3", "{ let mut r = Ring::with_capacity(2); r.push(1); r.push(2); let e = r.push(3); (e, r.iter().copied().collect::<Vec<_>>()) }", "(Some(1), vec![2, 3])"),
    ],
    hidden=[
        T("wraps_many_times", "capacity 3, push 0..10", "{ let mut r = Ring::with_capacity(3); for i in 0..10 { r.push(i); } (r.len(), r.iter().copied().collect::<Vec<_>>()) }", "(3, vec![7, 8, 9])"),
        T("capacity_one", "capacity 1, push \"a\", \"b\"", '{ let mut r = Ring::with_capacity(1); r.push("a"); (r.push("b"), r.iter().copied().collect::<Vec<_>>()) }', '(Some("a"), vec!["b"])'),
    ],
    hints=[("approach", "The newest slot is `(head + len) % capacity`. When full, overwrite `head` and advance it."),
           ("rust", "`Option::replace` puts the new value in and hands back the old one.")],
    notes=("`Box<[T]>` is a pointer and a length: the right type for a buffer that never grows. `iter` borrows `self`, hence the `+ '_`.", "O(1) push", "O(capacity)"),
    follow_up="How would you make this lock-free for one producer and one consumer?",
    related=["S5", "C3"],
))

P.append(dict(
    slug="pairs-iterator", title="A zero-cost iterator over pairs", level="hard", stage="build-it", tags=["Iterator", "lifetimes", "slice patterns"],
    teaches=["An iterator that holds a sub-slice and advances it.", "Item references tied to the slice, not the iterator: `(&'a T, &'a T)`.", "`ExactSizeIterator` via an exact `size_hint`."],
    statement="""
        Write `pairs(v)`, which yields non-overlapping pairs `(&v[0], &v[1])`, `(&v[2], &v[3])`, … and drops
        a trailing odd element. The items must outlive the iterator, and `len()` must work.
    """,
    starter="""
        pub struct Pairs<'a, T> {
            rest: &'a [T],
        }

        pub fn pairs<T>(v: &[T]) -> Pairs<'_, T> {
            Pairs { rest: v }
        }

        impl<'a, T> Iterator for Pairs<'a, T> {
            type Item = (&'a T, &'a T);

            fn next(&mut self) -> Option<Self::Item> {
                todo!()
            }

            // TODO: an exact size_hint, so that len() below works.
        }

        impl<T> ExactSizeIterator for Pairs<'_, T> {}
    """,
    solution="""
        pub struct Pairs<'a, T> {
            rest: &'a [T],
        }

        pub fn pairs<T>(v: &[T]) -> Pairs<'_, T> {
            Pairs { rest: v }
        }

        impl<'a, T> Iterator for Pairs<'a, T> {
            type Item = (&'a T, &'a T);

            fn next(&mut self) -> Option<Self::Item> {
                match self.rest {
                    [a, b, rest @ ..] => {
                        self.rest = rest;
                        Some((a, b))
                    }
                    _ => None,
                }
            }

            fn size_hint(&self) -> (usize, Option<usize>) {
                let n = self.rest.len() / 2;
                (n, Some(n))
            }
        }

        impl<T> ExactSizeIterator for Pairs<'_, T> {}
    """,
    visible=[
        T("odd_length", "v = [1, 2, 3, 4, 5]", "pairs(&[1, 2, 3, 4, 5]).map(|(a, b)| (*a, *b)).collect::<Vec<_>>()", "vec![(1, 2), (3, 4)]"),
        T("items_outlive_iterator", "v = [\"a\", \"b\"]", "first", '(&"a", &"b")', setup='let v = ["a", "b"];\nlet first = { let mut it = pairs(&v); it.next().unwrap() };'),
    ],
    hidden=[
        T("len", "v = [0; 7]", "pairs(&[0; 7]).len()", "3"),
        T("empty", "v = []", "pairs::<u8>(&[]).next()", "None"),
    ],
    hints=[("rust", "A slice pattern `[a, b, rest @ ..]` takes two elements and the remainder in one match."),
           ("rust", "Items borrow from `'a`, the slice's lifetime, so they can outlive the `Pairs` value.")],
    notes=("`Pairs` is one fat pointer; the loop compiles to index arithmetic. std's `chunks_exact(2)` is the library version.", "O(1) per item", "O(1)"),
    follow_up="Why can't a `pairs_mut` returning `(&'a mut T, &'a mut T)` be written the same way without care?",
    related=["S6", "L3"],
))

STAGES = [("use-it", "Use it", "easy"), ("understand-it", "Understand it", "medium"), ("build-it", "Build it", "hard")]

if __name__ == "__main__":
    n = write_track("s3-vec-slices", "S3", "Vec & slices", "S", "core", 3,
                    "Rust's workhorse collection: the API, its cost model, and building one yourself on a raw allocation.",
                    STAGES, P)
    print("S3", n)
