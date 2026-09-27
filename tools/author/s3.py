import textwrap

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

GRID = """
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
    """

SMALLVEC = """
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
    """

RING = """
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
    """

DEREF_IMPLS = """
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
"""

def sub(code, *edits):
    """`code`, dedented, with each (old, new) replacement made; every `old` must be there.
    An `old` copied from the indented spec source (8 spaces deeper than the dedented code) is re-indented to match."""
    code = textwrap.dedent(code)
    for old, new in edits:
        if old not in code:
            old, new = old.replace("\n        ", "\n"), new.replace("\n        ", "\n")
        assert old in code, old
        code = code.replace(old, new)
    return code


P = []

RM_SOL = """
        /// Removes the elements at `indices` (any order, repeats allowed, out-of-range ones ignored), keeping the
        /// rest in order. O(n + k log k).
        pub fn remove_indices<T>(v: &mut Vec<T>, indices: &[usize]) {
            let mut idx = indices.to_vec();
            idx.sort_unstable();
            idx.dedup();
            let mut next = idx.iter().peekable();
            let mut i = 0;
            v.retain(|_| {
                let drop = next.next_if_eq(&&i).is_some();
                i += 1;
                !drop
            });
        }

        /// Removes the elements at `indices` with `swap_remove`, highest index first, and returns them in that
        /// order. The order of what's left is whatever that produces. O(k log k): nothing is shifted.
        pub fn remove_indices_unordered<T>(v: &mut Vec<T>, indices: &[usize]) -> Vec<T> {
            let mut idx: Vec<usize> = indices.iter().copied().filter(|&i| i < v.len()).collect();
            idx.sort_unstable_by(|a, b| b.cmp(a));
            idx.dedup();
            idx.into_iter().map(|i| v.swap_remove(i)).collect()
        }
"""

RM_STARTER = """
        /// Removes the elements at `indices` (any order, repeats allowed, out-of-range ones ignored), keeping the
        /// rest in order. O(n + k log k).
        pub fn remove_indices<T>(v: &mut Vec<T>, indices: &[usize]) {
            todo!()
        }

        /// Removes the elements at `indices` with `swap_remove`, highest index first, and returns them in that
        /// order. The order of what's left is whatever that produces. O(k log k): nothing is shifted.
        pub fn remove_indices_unordered<T>(v: &mut Vec<T>, indices: &[usize]) -> Vec<T> {
            todo!()
        }
"""


def ri(name, v, idx, want):
    return T(name, f"v = {v}, indices = {idx}", "v", f"vec!{want}" if want else "Vec::<i32>::new()",
             setup=f"let mut v = vec!{v};\nremove_indices(&mut v, &{idx});" if v else f"let mut v: Vec<i32> = vec![];\nremove_indices(&mut v, &{idx});")


def py_unordered(v, idx):
    v = list(v)
    ids = sorted({i for i in idx if i < len(v)}, reverse=True)
    out = []
    for i in ids:
        out.append(v[i])
        v[i] = v[-1]
        v.pop()
    return v, out


def ru(name, v, idx):
    left, removed = py_unordered(v, idx)
    lit = lambda xs: f"vec!{xs}" if xs else "Vec::<i32>::new()"
    return T(name, f"v = {v}, indices = {idx}", "(removed, v)", f"({lit(removed)}, {lit(left)})",
             setup=f"let mut v: Vec<i32> = vec!{v};\nlet removed = remove_indices_unordered(&mut v, &{idx});")


RM_SOL = """
        /// Removes the elements at `indices` (any order, repeats allowed, out-of-range ones ignored), keeping the
        /// rest in order. O(n + k log k).
        pub fn remove_indices<T>(v: &mut Vec<T>, indices: &[usize]) {
            let mut idx = indices.to_vec();
            idx.sort_unstable();
            idx.dedup();
            let mut next = idx.iter().peekable();
            let mut i = 0;
            v.retain(|_| {
                let drop = next.next_if_eq(&&i).is_some();
                i += 1;
                !drop
            });
        }

        /// Removes the elements at `indices` with `swap_remove`, highest index first, and returns them in that
        /// order. The order of what's left is whatever that produces. O(k log k): nothing is shifted.
        pub fn remove_indices_unordered<T>(v: &mut Vec<T>, indices: &[usize]) -> Vec<T> {
            let mut idx: Vec<usize> = indices.iter().copied().filter(|&i| i < v.len()).collect();
            idx.sort_unstable_by(|a, b| b.cmp(a));
            idx.dedup();
            idx.into_iter().map(|i| v.swap_remove(i)).collect()
        }
"""

RM_STARTER = """
        /// Removes the elements at `indices` (any order, repeats allowed, out-of-range ones ignored), keeping the
        /// rest in order. O(n + k log k).
        pub fn remove_indices<T>(v: &mut Vec<T>, indices: &[usize]) {
            todo!()
        }

        /// Removes the elements at `indices` with `swap_remove`, highest index first, and returns them in that
        /// order. The order of what's left is whatever that produces. O(k log k): nothing is shifted.
        pub fn remove_indices_unordered<T>(v: &mut Vec<T>, indices: &[usize]) -> Vec<T> {
            todo!()
        }
"""


def ri(name, v, idx, want):
    return T(name, f"v = {v}, indices = {idx}", "v", f"vec!{want}" if want else "Vec::<i32>::new()",
             setup=f"let mut v = vec!{v};\nremove_indices(&mut v, &{idx});" if v else f"let mut v: Vec<i32> = vec![];\nremove_indices(&mut v, &{idx});")


def py_unordered(v, idx):
    v = list(v)
    ids = sorted({i for i in idx if i < len(v)}, reverse=True)
    out = []
    for i in ids:
        out.append(v[i])
        v[i] = v[-1]
        v.pop()
    return v, out


def ru(name, v, idx):
    left, removed = py_unordered(v, idx)
    lit = lambda xs: f"vec!{xs}" if xs else "Vec::<i32>::new()"
    return T(name, f"v = {v}, indices = {idx}", "(removed, v)", f"({lit(removed)}, {lit(left)})",
             setup=f"let mut v: Vec<i32> = vec!{v};\nlet removed = remove_indices_unordered(&mut v, &{idx});")


RM_SOL = """
        /// Removes the elements at `indices` (any order, repeats allowed, out-of-range ones ignored), keeping the
        /// rest in order. O(n + k log k).
        pub fn remove_indices<T>(v: &mut Vec<T>, indices: &[usize]) {
            let mut idx = indices.to_vec();
            idx.sort_unstable();
            idx.dedup();
            let mut next = idx.iter().peekable();
            let mut i = 0;
            v.retain(|_| {
                let drop = next.next_if_eq(&&i).is_some();
                i += 1;
                !drop
            });
        }

        /// Removes the elements at `indices` with `swap_remove`, highest index first, and returns them in that
        /// order. The order of what's left is whatever that produces. O(k log k): nothing is shifted.
        pub fn remove_indices_unordered<T>(v: &mut Vec<T>, indices: &[usize]) -> Vec<T> {
            let mut idx: Vec<usize> = indices.iter().copied().filter(|&i| i < v.len()).collect();
            idx.sort_unstable_by(|a, b| b.cmp(a));
            idx.dedup();
            idx.into_iter().map(|i| v.swap_remove(i)).collect()
        }
"""

RM_STARTER = """
        /// Removes the elements at `indices` (any order, repeats allowed, out-of-range ones ignored), keeping the
        /// rest in order. O(n + k log k).
        pub fn remove_indices<T>(v: &mut Vec<T>, indices: &[usize]) {
            todo!()
        }

        /// Removes the elements at `indices` with `swap_remove`, highest index first, and returns them in that
        /// order. The order of what's left is whatever that produces. O(k log k): nothing is shifted.
        pub fn remove_indices_unordered<T>(v: &mut Vec<T>, indices: &[usize]) -> Vec<T> {
            todo!()
        }
"""


def ri(name, v, idx, want):
    return T(name, f"v = {v}, indices = {idx}", "v", f"vec!{want}" if want else "Vec::<i32>::new()",
             setup=f"let mut v = vec!{v};\nremove_indices(&mut v, &{idx});" if v else f"let mut v: Vec<i32> = vec![];\nremove_indices(&mut v, &{idx});")


def py_unordered(v, idx):
    v = list(v)
    ids = sorted({i for i in idx if i < len(v)}, reverse=True)
    out = []
    for i in ids:
        out.append(v[i])
        v[i] = v[-1]
        v.pop()
    return v, out


def ru(name, v, idx):
    left, removed = py_unordered(v, idx)
    lit = lambda xs: f"vec!{xs}" if xs else "Vec::<i32>::new()"
    return T(name, f"v = {v}, indices = {idx}", "(removed, v)", f"({lit(removed)}, {lit(left)})",
             setup=f"let mut v: Vec<i32> = vec!{v};\nlet removed = remove_indices_unordered(&mut v, &{idx});")


RM_SOL = """
        /// Removes the elements at `indices` (any order, repeats allowed, out-of-range ones ignored), keeping the
        /// rest in order. O(n + k log k).
        pub fn remove_indices<T>(v: &mut Vec<T>, indices: &[usize]) {
            let mut idx = indices.to_vec();
            idx.sort_unstable();
            idx.dedup();
            let mut next = idx.iter().peekable();
            let mut i = 0;
            v.retain(|_| {
                let drop = next.next_if_eq(&&i).is_some();
                i += 1;
                !drop
            });
        }

        /// Removes the elements at `indices` with `swap_remove`, highest index first, and returns them in that
        /// order. The order of what's left is whatever that produces. O(k log k): nothing is shifted.
        pub fn remove_indices_unordered<T>(v: &mut Vec<T>, indices: &[usize]) -> Vec<T> {
            let mut idx: Vec<usize> = indices.iter().copied().filter(|&i| i < v.len()).collect();
            idx.sort_unstable_by(|a, b| b.cmp(a));
            idx.dedup();
            idx.into_iter().map(|i| v.swap_remove(i)).collect()
        }
"""

RM_STARTER = """
        /// Removes the elements at `indices` (any order, repeats allowed, out-of-range ones ignored), keeping the
        /// rest in order. O(n + k log k).
        pub fn remove_indices<T>(v: &mut Vec<T>, indices: &[usize]) {
            todo!()
        }

        /// Removes the elements at `indices` with `swap_remove`, highest index first, and returns them in that
        /// order. The order of what's left is whatever that produces. O(k log k): nothing is shifted.
        pub fn remove_indices_unordered<T>(v: &mut Vec<T>, indices: &[usize]) -> Vec<T> {
            todo!()
        }
"""


def ri(name, v, idx, want):
    return T(name, f"v = {v}, indices = {idx}", "v", f"vec!{want}" if want else "Vec::<i32>::new()",
             setup=f"let mut v = vec!{v};\nremove_indices(&mut v, &{idx});" if v else f"let mut v: Vec<i32> = vec![];\nremove_indices(&mut v, &{idx});")


def py_unordered(v, idx):
    v = list(v)
    ids = sorted({i for i in idx if i < len(v)}, reverse=True)
    out = []
    for i in ids:
        out.append(v[i])
        v[i] = v[-1]
        v.pop()
    return v, out


def ru(name, v, idx):
    left, removed = py_unordered(v, idx)
    lit = lambda xs: f"vec!{xs}" if xs else "Vec::<i32>::new()"
    return T(name, f"v = {v}, indices = {idx}", "(removed, v)", f"({lit(removed)}, {lit(left)})",
             setup=f"let mut v: Vec<i32> = vec!{v};\nlet removed = remove_indices_unordered(&mut v, &{idx});")


P.append(dict(
    slug="vec-ops", title="Remove many indices at once", level="easy", stage="use-it", tags=["retain", "swap_remove", "sort_unstable", "dedup", "Peekable"],
    teaches=[
        "Removing by index in a loop shifts everything after it: ascending order hits the wrong elements, and even the right order is O(n) per removal.",
        "`retain` visits elements once, in order, with an `FnMut` closure, so it can track the index and drop a sorted set of positions in one O(n) pass.",
        "`swap_remove` is O(1) because it moves the last element into the hole; processing indices from the highest down keeps the rest valid.",
    ],
    statement="""
        Two ways to delete a batch of positions from a `Vec`. In both, `indices` may be in any order, may repeat,
        and may contain positions past the end, which are ignored.

        - `remove_indices(v, indices)`: keep the remaining elements in their original order. It must be
          O(n + k log k) for `n` elements and `k` indices; a loop of `v.remove(i)` is O(n·k).
        - `remove_indices_unordered(v, indices)`: when order doesn't matter, remove each position with
          `swap_remove`, highest index first, and return the removed elements in that order. Whatever order is
          left after that is the expected answer.
    """,
    examples=[("remove_indices on [10, 11, 12, 13, 14], indices [3, 0, 3, 9]", "[11, 12, 14]"),
              ("remove_indices_unordered on [10, 11, 12, 13, 14], indices [0, 3]", "returns [13, 10], leaves [14, 11, 12]")],
    starter=RM_STARTER,
    solution=RM_SOL,
    visible=[
        ri("keeps_order", [10, 11, 12, 13, 14], [3, 0, 3, 9], [11, 12, 14]),
        ri("adjacent_indices", [1, 2, 3, 4], [1, 2], [1, 4]),
        ri("nothing_to_remove", [1, 2], [], [1, 2]),
        ru("unordered_two", [10, 11, 12, 13, 14], [0, 3]),
        ru("unordered_includes_last", [1, 2, 3], [2, 0]),
    ],
    hidden=[
        ri("remove_everything", [5, 6, 7], [2, 1, 0], []),
        ri("all_out_of_range", [5, 6], [2, 7, 100], [5, 6]),
        ri("empty_vec", [], [0, 1], []),
        ri("first_and_last", [1, 2, 3, 4, 5], [4, 0], [2, 3, 4]),
        ri("many_repeats", [1, 2, 3], [1, 1, 1, 1], [1, 3]),
        ri("huge_index", [1, 2], [18446744073709551615], [1, 2]),
        ru("unordered_everything", [1, 2, 3, 4], [0, 1, 2, 3]),
        ru("unordered_repeats_and_out_of_range", [1, 2, 3, 4, 5], [1, 1, 9, 4]),
        ru("unordered_last_two", [1, 2, 3, 4], [3, 2]),
        ru("unordered_nothing", [1, 2], [5]),
        T("strings", 'v = ["a", "b", "c", "d"], remove [0, 2] (both ways)', "(a, b, removed)", '(["b", "d"].map(String::from).to_vec(), ["d", "b"].map(String::from).to_vec(), ["c", "a"].map(String::from).to_vec())',
          setup='let words = vec!["a".to_string(), "b".to_string(), "c".to_string(), "d".to_string()];\nlet (mut a, mut b) = (words.clone(), words);\nremove_indices(&mut a, &[0, 2]);\nlet removed = remove_indices_unordered(&mut b, &[0, 2]);'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(7301);
            for _ in 0..400 {
                let n = rng.below(10);
                let v: Vec<i32> = (0..n as i32).collect();
                let k = rng.below(6);
                let idx: Vec<usize> = (0..k).map(|_| rng.below(n + 2)).collect();
                let want: Vec<i32> = v.iter().copied().filter(|&x| !idx.contains(&(x as usize))).collect();
                let mut sorted: Vec<usize> = idx.iter().copied().filter(|&i| i < n).collect();
                sorted.sort();
                sorted.dedup();
                let mut left = v.clone();
                let mut removed = Vec::new();
                for &i in sorted.iter().rev() {
                    let last = left.len() - 1;
                    left.swap(i, last);
                    removed.push(left.pop().unwrap());
                }
                let (mut a, mut b) = (v.clone(), v.clone());
                remove_indices(&mut a, &idx);
                let got_removed = remove_indices_unordered(&mut b, &idx);
                check!(format!("v = {v:?}, indices = {idx:?}"), (a, got_removed, b), (want, removed, left));
            }
        }

        #[test]
        fn scale_remove_100k_of_300k() {
            let mut v: Vec<u64> = (0..300_000).collect();
            let idx: Vec<usize> = (1..200_000).step_by(2).rev().collect();
            remove_indices(&mut v, &idx);
            check!("v = 0..300000, remove the odd indices below 200000 (listed high to low)", (v.len(), v[0], v[99_999], v[100_000]), (200_000, 0, 199_998, 200_000));
            let mut w: Vec<u64> = (0..300_000).collect();
            let removed = remove_indices_unordered(&mut w, &idx);
            check!("the same, unordered", (w.len(), removed.len(), removed[0]), (200_000, 100_000, 199_999));
        }
        """,
    ],
    wrong=dict(
        removes_in_ascending_order=sub(RM_SOL, ("""let mut next = idx.iter().peekable();
            let mut i = 0;
            v.retain(|_| {
                let drop = next.next_if_eq(&&i).is_some();
                i += 1;
                !drop
            });""", """for i in idx {
                if i < v.len() {
                    v.remove(i);
                }
            }""")),
        removes_highest_first_one_by_one=sub(RM_SOL, ("""let mut next = idx.iter().peekable();
            let mut i = 0;
            v.retain(|_| {
                let drop = next.next_if_eq(&&i).is_some();
                i += 1;
                !drop
            });""", """for &i in idx.iter().rev() {
                if i < v.len() {
                    v.remove(i);
                }
            }""")),
        swap_remove_lowest_first=sub(RM_SOL, ("idx.sort_unstable_by(|a, b| b.cmp(a));", "idx.sort_unstable();\n    let _ = |a: usize, b: usize| b.cmp(&a);")),
        repeats_removed_twice=sub(RM_SOL, ("""idx.sort_unstable_by(|a, b| b.cmp(a));
    idx.dedup();
    idx.into_iter().map(|i| v.swap_remove(i)).collect()""", """idx.sort_unstable_by(|a, b| b.cmp(a));
    idx.into_iter().filter_map(|i| (i < v.len()).then(|| v.swap_remove(i))).collect()""")),
    ),
    hints=[("approach", "Sort and dedup a copy of the indices. Then one `retain` pass: keep a counter of the current position and drop it when it's the next index in the sorted list."),
           ("rust", "`retain`'s closure is `FnMut` and is called once per element, in order. `iter.peekable()` + `next_if_eq(&&i)` consumes the next index only when it matches."),
           ("edge case", "`swap_remove(i)` moves the last element into `i`. Go from the highest index down, so that element is never one you still have to remove.")],
    notes=("""`Vec::remove(i)` shifts every later element left, so k removals cost O(n·k), and doing them in ascending order also removes the wrong elements after the first. `retain` compacts in one pass instead (the same thing `dedup` and `drain_filter`-style code does internally), and it's documented to visit elements exactly once in order, which is what makes a position counter in the closure legitimate. When order doesn't matter, `swap_remove` is O(1) per removal. Syntax to remember: `v.retain(|x| keep)`, `v.retain_mut(|x| …)`, `v.swap_remove(i)`, `v.remove(i)`, `v.insert(i, x)`, `v.truncate(n)`, `idx.sort_unstable_by(|a, b| b.cmp(a))`, `it.peekable().next_if_eq(&x)`.""", "O(n + k log k) and O(k log k)", "O(k)"),
    follow_up="`retain` must leave the Vec valid even if the closure panics halfway. How does std manage that without moving every element twice?",
    related=["D1"],
))

RD_SOL = """
        #[derive(Debug, Clone, PartialEq)]
        pub struct Job {
            pub id: u32,
            pub retries_left: u32,
        }

        /// One scheduler tick: every job uses up one retry, and jobs left with none are removed. One pass.
        pub fn tick(jobs: &mut Vec<Job>) {
            jobs.retain_mut(|job| {
                job.retries_left = job.retries_left.saturating_sub(1);
                job.retries_left > 0
            });
        }

        #[derive(Debug, Clone, PartialEq)]
        pub struct Run {
            pub key: char,
            pub count: u32,
        }

        /// Merges each stretch of neighbouring runs with the same key into its first run, adding up the counts.
        pub fn merge_runs(runs: &mut Vec<Run>) {
            runs.dedup_by(|next, kept| {
                if next.key == kept.key {
                    kept.count += next.count;
                    true
                } else {
                    false
                }
            });
        }

        /// Keeps only the first event of each stretch of consecutive events in the same minute (seconds / 60).
        pub fn first_per_minute(events: &mut Vec<(u64, String)>) {
            events.dedup_by_key(|e| e.0 / 60);
        }
"""

RD_STARTER = """
        #[derive(Debug, Clone, PartialEq)]
        pub struct Job {
            pub id: u32,
            pub retries_left: u32,
        }

        /// One scheduler tick: every job uses up one retry, and jobs left with none are removed. One pass.
        pub fn tick(jobs: &mut Vec<Job>) {
            todo!()
        }

        #[derive(Debug, Clone, PartialEq)]
        pub struct Run {
            pub key: char,
            pub count: u32,
        }

        /// Merges each stretch of neighbouring runs with the same key into its first run, adding up the counts.
        pub fn merge_runs(runs: &mut Vec<Run>) {
            todo!()
        }

        /// Keeps only the first event of each stretch of consecutive events in the same minute (seconds / 60).
        pub fn first_per_minute(events: &mut Vec<(u64, String)>) {
            todo!()
        }
"""


def jobs(pairs):
    return "vec![" + ", ".join(f"Job {{ id: {a}, retries_left: {b} }}" for a, b in pairs) + "]" if pairs else "Vec::<Job>::new()"


def runs(pairs):
    return "vec![" + ", ".join(f"Run {{ key: '{a}', count: {b} }}" for a, b in pairs) + "]" if pairs else "Vec::<Run>::new()"


def py_merge(pairs):
    out = []
    for k, c in pairs:
        if out and out[-1][0] == k:
            out[-1] = (k, out[-1][1] + c)
        else:
            out.append((k, c))
    return out


def tk(name, pairs):
    want = [(a, b - 1) for a, b in pairs if b > 1]
    return T(name, f"jobs (id, retries_left) = {pairs}", "j", jobs(want), setup=f"let mut j = {jobs(pairs)};\ntick(&mut j);")


def mr(name, pairs):
    return T(name, f"runs = {pairs}".replace("'", ""), "r", runs(py_merge(pairs)), setup=f"let mut r = {runs(pairs)};\nmerge_runs(&mut r);")


def ev(xs):
    return "vec![" + ", ".join(f'({t}, "{s}".to_string())' for t, s in xs) + "]" if xs else "Vec::<(u64, String)>::new()"


def fm(name, xs):
    out = []
    for t, s in xs:
        if not out or out[-1][0] // 60 != t // 60:
            out.append((t, s))
    return T(name, f"events = {xs}".replace("'", '"'), "e", ev(out), setup=f"let mut e = {ev(xs)};\nfirst_per_minute(&mut e);")


P.append(dict(
    slug="retain-and-dedup", title="retain_mut, dedup_by and dedup_by_key", level="easy", stage="use-it", tags=["retain_mut", "dedup_by", "dedup_by_key"],
    teaches=[
        "`retain_mut` updates and filters in one pass; `retain`'s closure only gets `&T`.",
        "`dedup_by(|a, b| …)` gets the element that may be removed as `a` and the one that stays as `b`: merge into `b`.",
        "`dedup_by_key` and every `dedup` only look at neighbours; equal values further apart are kept.",
    ],
    statement="""
        - `tick(jobs)`: one scheduler tick. Every job uses up one retry (`retries_left` goes down by one, not below
          zero), and every job left with no retries is removed. Do it in one pass over the `Vec`.
        - `merge_runs(runs)`: merge each stretch of neighbouring runs with the same `key` into the first run of the
          stretch, whose `count` becomes the stretch's total.
        - `first_per_minute(events)`: events are `(seconds, name)`. In each stretch of consecutive events that fall
          in the same minute (`seconds / 60`), keep only the first.
    """,
    examples=[("tick on [Job { id: 1, retries_left: 2 }, Job { id: 2, retries_left: 1 }]", "[Job { id: 1, retries_left: 1 }]"),
              ("merge_runs on a×2, a×3, b×1, a×1", "a×5, b×1, a×1"), ('first_per_minute on [(0, "a"), (59, "b"), (60, "c")]', '[(0, "a"), (60, "c")]')],
    starter=RD_STARTER,
    solution=RD_SOL,
    visible=[
        tk("tick_decrements_and_drops", [(1, 2), (2, 1), (3, 5)]),
        mr("merge_neighbours", [("a", 2), ("a", 3), ("b", 1), ("a", 1)]),
        fm("first_of_each_minute", [(0, "a"), (59, "b"), (60, "c"), (61, "d")]),
        tk("tick_empty", []),
        mr("merge_nothing_to_merge", [("a", 1), ("b", 2)]),
    ],
    hidden=[
        tk("tick_zero_is_removed", [(1, 0), (2, 3)]),
        tk("tick_all_expire", [(1, 1), (2, 1)]),
        tk("tick_keeps_order", [(5, 9), (3, 1), (4, 2), (1, 7)]),
        T("tick_twice", "jobs (id, retries_left) = [(1, 2), (2, 3)], two ticks", "j", jobs([(2, 1)]),
          setup=f"let mut j = {jobs([(1, 2), (2, 3)])};\ntick(&mut j);\ntick(&mut j);"),
        mr("merge_one_long_run", [("x", 1)] * 5),
        mr("merge_separated_runs_stay_apart", [("a", 1), ("b", 1), ("a", 1), ("b", 1)]),
        mr("merge_empty", []),
        mr("merge_zero_counts", [("a", 0), ("a", 0), ("b", 4), ("b", 0)]),
        fm("same_minute_not_adjacent", [(0, "a"), (70, "b"), (10, "c")]),
        fm("minute_boundary", [(119, "a"), (120, "b"), (179, "c"), (180, "d")]),
        fm("all_one_minute", [(3, "a"), (3, "b"), (30, "c")]),
        fm("no_events", []),
        fm("large_timestamps", [(18446744073709551615, "a"), (18446744073709551600, "b")]),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(7302);
            for _ in 0..400 {
                let n = rng.below(8);
                let js: Vec<Job> = (0..n).map(|i| Job { id: i as u32, retries_left: rng.below(4) as u32 }).collect();
                let want_jobs: Vec<Job> = js.iter().filter(|j| j.retries_left > 1).map(|j| Job { id: j.id, retries_left: j.retries_left - 1 }).collect();
                let rs: Vec<Run> = (0..n).map(|_| Run { key: *rng.pick(&['a', 'b']), count: rng.below(5) as u32 }).collect();
                let mut want_runs: Vec<Run> = Vec::new();
                for r in &rs {
                    match want_runs.last_mut() {
                        Some(last) if last.key == r.key => last.count += r.count,
                        _ => want_runs.push(r.clone()),
                    }
                }
                let es: Vec<(u64, String)> = (0..n).map(|i| (rng.below(200) as u64, i.to_string())).collect();
                let mut want_events: Vec<(u64, String)> = Vec::new();
                for e in &es {
                    if want_events.last().map_or(true, |l| l.0 / 60 != e.0 / 60) {
                        want_events.push(e.clone());
                    }
                }
                let (mut a, mut b, mut c) = (js.clone(), rs.clone(), es.clone());
                tick(&mut a);
                merge_runs(&mut b);
                first_per_minute(&mut c);
                check!(format!("jobs = {js:?}, runs = {rs:?}, events = {es:?}"), (a, b, c), (want_jobs, want_runs, want_events));
            }
        }

        #[test]
        fn scale_200k() {
            let mut j: Vec<Job> = (0..200_000).map(|i| Job { id: i, retries_left: i % 3 }).collect();
            tick(&mut j);
            let mut r: Vec<Run> = (0..200_000).map(|i| Run { key: if i < 100_000 { 'a' } else { 'b' }, count: 1 }).collect();
            merge_runs(&mut r);
            check!("200000 jobs and 200000 runs", (j.len(), j[0].id, r), (66_666, 2, vec![Run { key: 'a', count: 100_000 }, Run { key: 'b', count: 100_000 }]));
        }
        """,
    ],
    wrong=dict(
        filters_before_decrementing=sub(RD_SOL, ("""job.retries_left = job.retries_left.saturating_sub(1);
                job.retries_left > 0""", """let keep = job.retries_left > 0;
                job.retries_left = job.retries_left.saturating_sub(1);
                keep""")),
        merges_into_the_removed_one=sub(RD_SOL, ("kept.count += next.count;", "next.count += kept.count;")),
        keyed_by_second=sub(RD_SOL, ("events.dedup_by_key(|e| e.0 / 60);", "events.dedup_by_key(|e| e.0);")),
        dedups_the_whole_vec=sub(RD_SOL, ("events.dedup_by_key(|e| e.0 / 60);", "let mut seen = std::collections::HashSet::new();\n    events.retain(|e| seen.insert(e.0 / 60));")),
    ),
    hints=[("rust", "`jobs.retain_mut(|job| { job.retries_left = …; job.retries_left > 0 })` changes each job and decides whether to keep it in the same call."),
           ("rust", "In `v.dedup_by(|a, b| …)`, `b` is the earlier element that stays and `a` the later one that's removed if you return `true`. Add `a`'s count into `b`."),
           ("edge case", "Events in the same minute that aren't next to each other are all kept: `dedup` only compares neighbours.")],
    notes=("""All three are single in-place passes that shift the survivors down, with no second `Vec`. `retain` gives the closure `&T` (historically so it could be used on shared data); `retain_mut` gives `&mut T`, so updating and filtering is one pass instead of `iter_mut` plus `retain`. The `dedup_by` argument order is the classic trap: the closure sees `(current, previous_kept)`, so merging into the first argument silently loses the counts when it's dropped. Syntax to remember: `v.retain(|x| …)`, `v.retain_mut(|x| …)`, `v.dedup()`, `v.dedup_by_key(|x| key(x))`, `v.dedup_by(|a, b| same(a, b))` (a = later, b = kept), `n.saturating_sub(1)`.""", "O(n)", "O(1)"),
    follow_up="`dedup_by_key(|e| e.name.to_lowercase())` allocates twice per comparison. How would you write it with `dedup_by` and no allocation?",
    related=["D1"],
))

SORT_SOL = """
        use std::cmp::Reverse;

        #[derive(Debug, Clone, PartialEq)]
        pub struct File {
            pub name: String,
            pub size: u64,
        }

        /// The text after the last '.', if any.
        fn extension(name: &str) -> Option<&str> {
            name.rsplit_once('.').map(|(_, ext)| ext)
        }

        /// By extension, ignoring ASCII case (files without one first), then largest first. Ties keep their order.
        pub fn sort_files(files: &mut [File]) {
            files.sort_by_cached_key(|f| (extension(&f.name).map(str::to_ascii_lowercase), Reverse(f.size)));
        }

        /// Most wins first, then fewest losses, then by name. Names are unique.
        pub fn leaderboard(players: &mut [(String, u32, u32)]) {
            players.sort_unstable_by(|a, b| b.1.cmp(&a.1).then(a.2.cmp(&b.2)).then_with(|| a.0.cmp(&b.0)));
        }

        /// Ascending in IEEE 754 total order: -NaN < -inf < … < -0.0 < 0.0 < … < inf < NaN.
        pub fn sort_readings(v: &mut [f64]) {
            v.sort_unstable_by(f64::total_cmp);
        }
"""

SORT_STARTER = """
        use std::cmp::Reverse;

        #[derive(Debug, Clone, PartialEq)]
        pub struct File {
            pub name: String,
            pub size: u64,
        }

        /// By extension, ignoring ASCII case (files without one first), then largest first. Ties keep their order.
        pub fn sort_files(files: &mut [File]) {
            todo!()
        }

        /// Most wins first, then fewest losses, then by name. Names are unique.
        pub fn leaderboard(players: &mut [(String, u32, u32)]) {
            todo!()
        }

        /// Ascending in IEEE 754 total order: -NaN < -inf < … < -0.0 < 0.0 < … < inf < NaN.
        pub fn sort_readings(v: &mut [f64]) {
            todo!()
        }
"""

SORT_TESTS = """
        fn files(spec: &[(&str, u64)]) -> Vec<File> {
            spec.iter().map(|&(name, size)| File { name: name.to_string(), size }).collect()
        }

        fn names(fs: &[File]) -> Vec<&str> {
            fs.iter().map(|f| f.name.as_str()).collect()
        }

        fn players(spec: &[(&str, u32, u32)]) -> Vec<(String, u32, u32)> {
            spec.iter().map(|&(n, w, l)| (n.to_string(), w, l)).collect()
        }
"""


def sf(name, spec, want):
    return T(name, "files = " + str(spec).replace("'", '"'), "names(&f)", "vec![" + ", ".join(f'"{w}"' for w in want) + "]",
             setup=f"let mut f = files(&{str(spec).replace(chr(39), chr(34))});\nsort_files(&mut f);")


def py_sort_files(spec):
    def key(f):
        n, s = f
        ext = n.rsplit(".", 1)[1].lower() if "." in n else None
        return (ext is not None, ext or "", -s)
    return [n for n, _ in sorted(spec, key=key)]


def sfc(name, spec):
    return sf(name, spec, py_sort_files(spec))


def lb(name, spec):
    want = sorted(spec, key=lambda p: (-p[1], p[2], p[0]))
    return T(name, "players (name, wins, losses) = " + str(spec).replace("'", '"'), "p.iter().map(|p| p.0.as_str()).collect::<Vec<_>>()",
             "vec![" + ", ".join(f'"{w[0]}"' for w in want) + "]", setup=f"let mut p = players(&{str(spec).replace(chr(39), chr(34))});\nleaderboard(&mut p);")


P.append(dict(
    slug="sort-by-key", title="Sorting: keys, stability and floats", level="easy", stage="use-it",
    tags=["sort_by_cached_key", "sort_unstable_by", "Reverse", "then_with", "f64::total_cmp"], use="use solution::*;",
    teaches=[
        "`sort_by_key` calls the key function on every comparison; when the key allocates, `sort_by_cached_key` computes it once per element.",
        "Stable sorts (`sort`, `sort_by*`, `sort_by_cached_key`) keep ties in input order; `sort_unstable*` is faster and doesn't, so use it only when the key is total.",
        "`f64` isn't `Ord`: `partial_cmp().unwrap()` panics on NaN, `total_cmp` orders every value, including `-0.0 < 0.0`.",
    ],
    statement="""
        - `sort_files(files)`: order by extension (the text after the last `.`), ignoring ASCII case, with files
          that have no extension first; within an extension, largest first. Files that tie on both keep their input
          order. This runs on directories of thousands of files: don't allocate on every comparison.
        - `leaderboard(players)`: `(name, wins, losses)`. Most wins first, then fewest losses, then by name. Names
          are unique, so there are no ties.
        - `sort_readings(v)`: ascending in IEEE 754 total order, which places `-0.0` before `0.0`, infinities at the
          ends and NaN after `+inf`. Readings may contain NaN.
    """,
    examples=[('sort_files on [("b.TXT", 1), ("a.rs", 5), ("c.txt", 9), ("Makefile", 2)]', '["Makefile", "a.rs", "c.txt", "b.TXT"]'),
              ("sort_readings on [1.0, NaN, -0.0, 0.0, -inf]", "[-inf, -0.0, 0.0, 1.0, NaN]")],
    starter=SORT_STARTER,
    solution=SORT_SOL,
    visible=[
        SORT_TESTS,
        sfc("files_by_extension_then_size", [("b.TXT", 1), ("a.rs", 5), ("c.txt", 9), ("Makefile", 2)]),
        sf("ties_keep_input_order", [("z.md", 3), ("a.md", 3), ("m.MD", 3)], ["z.md", "a.md", "m.MD"]),
        lb("wins_then_losses_then_name", [("cy", 3, 2), ("al", 5, 0), ("bo", 3, 1), ("di", 3, 1)]),
        T("readings_with_nan_and_zeros", "[1.0, NaN, -0.0, 0.0, -inf]", "v.iter().map(|x| x.to_bits()).collect::<Vec<_>>() == [f64::NEG_INFINITY, -0.0, 0.0, 1.0, f64::NAN].iter().map(|x| x.to_bits()).collect::<Vec<_>>()", "true",
          setup="let mut v = [1.0, f64::NAN, -0.0, 0.0, f64::NEG_INFINITY];\nsort_readings(&mut v);"),
        T("readings_plain", "[3.5, -1.0, 2.0]", "v", "[-1.0, 2.0, 3.5]", setup="let mut v = [3.5, -1.0, 2.0];\nsort_readings(&mut v);"),
    ],
    hidden=[
        SORT_TESTS,
        sfc("no_extension_first", [("x.a", 1), ("README", 1), ("LICENSE", 9)]),
        sfc("last_dot_counts", [("a.tar.gz", 1), ("b.gz", 2), ("c.tar", 3)]),
        sfc("case_insensitive_extension", [("a.Rs", 1), ("b.rS", 2), ("c.RS", 3)]),
        sfc("trailing_dot_is_empty_extension", [("a.", 1), ("b", 1), ("c.a", 1)]),
        T("empty_files", "[]", "{ let mut f: Vec<File> = vec![]; sort_files(&mut f); f.len() }", "0"),
        lb("leaderboard_single", [("solo", 0, 0)]),
        lb("leaderboard_all_tied_but_name", [("c", 1, 1), ("a", 1, 1), ("b", 1, 1)]),
        lb("leaderboard_max_values", [("x", 4294967295, 4294967295), ("y", 4294967295, 0), ("z", 0, 0)]),
        T("readings_negative_nan_first", "[0.0, -NaN, NaN, -1.0]", "(v[0].is_nan() && v[0].is_sign_negative(), v[1], v[2], v[3].is_nan() && v[3].is_sign_positive())", "(true, -1.0, 0.0, true)",
          setup="let mut v = [0.0, -f64::NAN, f64::NAN, -1.0];\nsort_readings(&mut v);"),
        T("readings_infinities", "[inf, -inf, 0.0]", "v", "[f64::NEG_INFINITY, 0.0, f64::INFINITY]", setup="let mut v = [f64::INFINITY, f64::NEG_INFINITY, 0.0];\nsort_readings(&mut v);"),
        T("readings_empty", "[]", "{ let mut v: [f64; 0] = []; sort_readings(&mut v); v.len() }", "0"),
        T("readings_many_nans_do_not_panic", "1000 values, every third NaN", "(v[..667].iter().all(|x| !x.is_nan()), v[667..].iter().all(|x| x.is_nan()), v[..667].windows(2).all(|w| w[0] <= w[1]))", "(true, true, true)",
          setup="let mut v: Vec<f64> = (0..1000).map(|i| if i % 3 == 2 { f64::NAN } else { (i * 7919 % 1000) as f64 - 500.0 }).collect();\nsort_readings(&mut v);"),
        """
        #[test]
        fn random_stability_vs_stable_sort() {
            let mut rng = anneal_prelude::Rng::new(7303);
            let exts = ["", ".a", ".A", ".b", ".B"];
            for round in 0..200 {
                let n = rng.below(60);
                let fs: Vec<File> = (0..n).map(|i| File { name: format!("f{i}{}", rng.pick(&exts)), size: rng.below(3) as u64 }).collect();
                let mut want = fs.clone();
                want.sort_by(|a, b| {
                    let ka = a.name.rsplit_once('.').map(|(_, e)| e.to_ascii_lowercase());
                    let kb = b.name.rsplit_once('.').map(|(_, e)| e.to_ascii_lowercase());
                    ka.cmp(&kb).then(b.size.cmp(&a.size))
                });
                let mut got = fs.clone();
                sort_files(&mut got);
                check!(format!("round {round}: files = {:?}", names(&fs)), names(&got), names(&want));
            }
        }

        #[test]
        fn cached_key_allocations() {
            let mut fs: Vec<File> = (0..2000u64).map(|i| File { name: format!("f{i}.EXT{}", i % 7), size: i * 7919 % 1000 }).collect();
            let ((), n) = anneal_prelude::allocs(|| sort_files(&mut fs));
            check!("2000 files: allocations while sorting (at most 3 per file)", n.count <= 6000, true);
        }
        """,
    ],
    wrong=dict(
        unstable_sort=sub(SORT_SOL, ("files.sort_by_cached_key(", "files.sort_unstable_by_key(")),
        key_on_every_comparison=sub(SORT_SOL, ("files.sort_by_cached_key(", "files.sort_by_key(")),
        smallest_first=sub(SORT_SOL, ("Reverse(f.size)", "f.size")),
        wins_ascending=sub(SORT_SOL, ("b.1.cmp(&a.1)", "a.1.cmp(&b.1)")),
        partial_cmp_unwrap=sub(SORT_SOL, ("v.sort_unstable_by(f64::total_cmp);", "v.sort_by(|a, b| a.partial_cmp(b).unwrap());")),
    ),
    hints=[("rust", "`files.sort_by_cached_key(|f| (ext_lowercase(f), Reverse(f.size)))`: the key is a tuple, `Option<String>` puts `None` first, and `Reverse` flips one field."),
           ("rust", "`a.cmp(&b).then(…)` for a cheap second key, `.then_with(|| …)` when it's worth computing only on a tie. `v.sort_unstable_by(f64::total_cmp)` sorts floats."),
           ("edge case", "Ties must keep input order: that rules out every `sort_unstable*` for `sort_files`.")],
    notes=("""Pick the sort by two questions: is the key total (then unstable is fine and faster, and needs no extra memory), and is the key expensive (then `sort_by_cached_key`, which builds a `Vec<(key, index)>` once and is stable). `sort_by_key(|f| f.name.to_lowercase())` allocates O(n log n) Strings; the cached version allocates n. For floats, `total_cmp` is the IEEE `totalOrder` predicate: it never panics and distinguishes `-0.0` from `0.0` and positive from negative NaN, which also makes it usable for `dedup` and binary search. Syntax to remember: `v.sort()`, `v.sort_unstable()`, `v.sort_by(|a, b| …)`, `v.sort_by_key(|x| k)`, `v.sort_by_cached_key(|x| k)`, `v.sort_unstable_by_key(|x| Reverse(k))`, `ord.then(o2)`, `ord.then_with(|| …)`, `ord.reverse()`, `f64::total_cmp`, `v.is_sorted()`.""", "O(n log n)", "O(n) for the cached keys"),
    follow_up="Why can a comparator that isn't a total order make `sort_by` panic in Rust 1.81+, and what did it do before?",
    related=["S8", "S2"],
    perf=dict(allocs=True),
))

TLV_SOL = """
        /// Parses `tag, len, value` records (`len` is one byte; the value is `len` bytes). A leading "TLV" magic is
        /// skipped. `None` if a record is cut short. Values borrow from `data`.
        pub fn parse_tlv(data: &[u8]) -> Option<Vec<(u8, &[u8])>> {
            let mut rest = data.strip_prefix(b"TLV").unwrap_or(data);
            let mut out = Vec::new();
            while let Some((&tag, after)) = rest.split_first() {
                let (&len, after) = after.split_first()?;
                let (value, after) = after.split_at_checked(usize::from(len))?;
                out.push((tag, value));
                rest = after;
            }
            Some(out)
        }

        /// The records encoded as `tag, len, value`, in one allocation of exactly the right size. `None` if a
        /// value is longer than 255 bytes.
        pub fn encode_tlv(records: &[(u8, &[u8])]) -> Option<Vec<u8>> {
            let mut out = Vec::with_capacity(records.iter().map(|(_, value)| 2 + value.len()).sum());
            for &(tag, value) in records {
                let len = u8::try_from(value.len()).ok()?;
                out.push(tag);
                out.push(len);
                out.extend_from_slice(value);
            }
            Some(out)
        }

        /// The records' values, joined with `sep` between them.
        pub fn join_values(records: &[(u8, &[u8])], sep: u8) -> Vec<u8> {
            records.iter().map(|&(_, value)| value).collect::<Vec<_>>().join(&sep)
        }
"""

TLV_STARTER = """
        /// Parses `tag, len, value` records (`len` is one byte; the value is `len` bytes). A leading "TLV" magic is
        /// skipped. `None` if a record is cut short. Values borrow from `data`.
        pub fn parse_tlv(data: &[u8]) -> Option<Vec<(u8, &[u8])>> {
            todo!()
        }

        /// The records encoded as `tag, len, value`, in one allocation of exactly the right size. `None` if a
        /// value is longer than 255 bytes.
        pub fn encode_tlv(records: &[(u8, &[u8])]) -> Option<Vec<u8>> {
            todo!()
        }

        /// The records' values, joined with `sep` between them.
        pub fn join_values(records: &[(u8, &[u8])], sep: u8) -> Vec<u8> {
            todo!()
        }
"""

P.append(dict(
    slug="slices-as-views", title="Slices as views: a TLV parser", level="easy", stage="use-it",
    tags=["split_first", "split_at_checked", "strip_prefix", "extend_from_slice", "join"],
    teaches=[
        "Parse by peeling: `split_first` and `split_at_checked` return `Option`s, so a truncated input is `None` instead of a panic.",
        "Returning `&[u8]` pieces of the input costs nothing; the lifetime ties them to `data`.",
        "`[&[T]]::join(&sep)` and `concat()` flatten slices of slices; `u8::try_from(len)` refuses what `as u8` would silently truncate.",
    ],
    statement="""
        A tag-length-value format: each record is a tag byte, a length byte `len`, then `len` bytes of value.

        - `parse_tlv(data)`: the records in order, as `(tag, value)` with each value borrowed from `data`. If the
          data starts with the magic bytes `b"TLV"`, skip them first. Return `None` if the last record is cut
          short (a tag with no length, or fewer than `len` value bytes).
        - `encode_tlv(records)`: the bytes for these records, in one allocation of exactly the final size (no
          allocation at all for no records). `None` if any value is longer than 255 bytes.
        - `join_values(records, sep)`: all the values, with the byte `sep` between each pair.
    """,
    examples=[('parse_tlv(b"TLV\\x01\\x02hi\\x07\\x00")', 'Some([(1, b"hi"), (7, b"")])'), ('parse_tlv(b"\\x01\\x05abc")', "None"),
              ('join_values([(1, b"ab"), (2, b"c")], b\'/\')', 'b"ab/c"')],
    starter=TLV_STARTER,
    solution=TLV_SOL,
    visible=[
        T("parse_with_magic", 'b"TLV\\x01\\x02hi\\x07\\x00"', 'parse_tlv(b"TLV\\x01\\x02hi\\x07\\x00")', 'Some(vec![(1, &b"hi"[..]), (7, &b""[..])])'),
        T("parse_truncated_value", 'b"\\x01\\x05abc"', 'parse_tlv(b"\\x01\\x05abc")', "None"),
        T("parse_empty", 'b"" and b"TLV"', '(parse_tlv(b""), parse_tlv(b"TLV"))', "(Some(vec![]), Some(vec![]))"),
        T("encode_round_trip", '[(1, b"hi"), (2, b"")]', 'encode_tlv(&[(1, b"hi"), (2, b"")])', 'Some(b"\\x01\\x02hi\\x02\\x00".to_vec())'),
        T("join_with_separator", '[(1, b"ab"), (2, b""), (3, b"c")], sep = b\'/\'', "join_values(&[(1, b\"ab\"), (2, b\"\"), (3, b\"c\")], b'/')", 'b"ab//c".to_vec()'),
    ],
    hidden=[
        T("parse_tag_without_length", 'b"\\x01\\x01a\\x09"', 'parse_tlv(b"\\x01\\x01a\\x09")', "None"),
        T("parse_magic_only_at_start", 'b"\\x01\\x03TLV"', 'parse_tlv(b"\\x01\\x03TLV")', 'Some(vec![(1, &b"TLV"[..])])'),
        T("parse_partial_magic_is_data", 'b"T\\x00"', 'parse_tlv(b"T\\x00")', 'Some(vec![(b\'T\', &b""[..])])'),
        T("parse_max_length", "a record with len 255", "parse_tlv(&data).map(|r| (r.len(), r[0].0, r[0].1.len()))", "Some((1, 9, 255))",
          setup="let mut data = vec![9u8, 255];\ndata.extend(std::iter::repeat(7u8).take(255));"),
        T("parse_len_one_short", "a record with len 255 and 254 bytes", "parse_tlv(&data)", "None",
          setup="let mut data = vec![9u8, 255];\ndata.extend(std::iter::repeat(7u8).take(254));"),
        T("values_borrow_input", "values point into data", "r[0].1.as_ptr() == data[2..].as_ptr() && r[1].1.as_ptr() == data[6..].as_ptr()", "true",
          setup='let data = b"\\x01\\x02ab\\x02\\x01c".to_vec();\nlet r = parse_tlv(&data).unwrap();'),
        T("encode_too_long", "a 256-byte value", "encode_tlv(&[(1, &big)])", "None", setup="let big = vec![0u8; 256];"),
        T("encode_255_is_fine", "a 255-byte value", "encode_tlv(&[(1, &big)]).map(|e| (e.len(), e[1]))", "Some((257, 255))", setup="let big = vec![0u8; 255];"),
        T("encode_one_exact_allocation", "three records", "(out.as_ref().map(|v| v.len() == v.capacity()), n.count)", "(Some(true), 1)",
          setup='let (out, n) = anneal_prelude::allocs(|| encode_tlv(&[(1, b"abc"), (2, b""), (3, b"z")]));'),
        T("encode_nothing_allocates_nothing", "no records", "(out, n.count)", "(Some(vec![]), 0)", setup="let (out, n) = anneal_prelude::allocs(|| encode_tlv(&[]));"),
        T("join_edges", "no records, one record", "(join_values(&[], b','), join_values(&[(1, b\"x\")], b','))", "(vec![], b\"x\".to_vec())"),
        T("join_all_empty", "three empty values", "join_values(&[(1, b\"\"), (2, b\"\"), (3, b\"\")], b',')", 'b",,".to_vec()'),
        """
        #[test]
        fn random_round_trip() {
            let mut rng = anneal_prelude::Rng::new(7304);
            for _ in 0..300 {
                let n = rng.below(5);
                let values: Vec<Vec<u8>> = (0..n).map(|_| {
                    let len = rng.below(5);
                    rng.vec(len, 0, 255)
                }).collect();
                let recs: Vec<(u8, &[u8])> = values.iter().enumerate().map(|(i, v)| (i as u8, v.as_slice())).collect();
                let mut want_bytes = Vec::new();
                for (t, v) in &recs {
                    want_bytes.push(*t);
                    want_bytes.push(v.len() as u8);
                    want_bytes.extend(v.iter());
                }
                let enc = encode_tlv(&recs);
                let cut = rng.below(want_bytes.len() + 1);
                let prefix = &want_bytes[..cut];
                let mut boundaries = vec![0];
                for (_, v) in &recs {
                    boundaries.push(boundaries.last().unwrap() + 2 + v.len());
                }
                let want_prefix = boundaries.iter().position(|&b| b == cut).map(|k| recs[..k].to_vec());
                let mut sep_join = Vec::new();
                for (i, v) in values.iter().enumerate() {
                    if i > 0 {
                        sep_join.push(b'|');
                    }
                    sep_join.extend(v.iter());
                }
                check!(format!("records = {recs:?}, cut at {cut}"),
                       (enc.clone(), parse_tlv(&want_bytes), parse_tlv(prefix), join_values(&recs, b'|')),
                       (Some(want_bytes.clone()), Some(recs.clone()), want_prefix, sep_join));
            }
        }

        #[test]
        fn scale_100k_records() {
            let data: Vec<u8> = (0..100_000u32).flat_map(|i| [(i % 256) as u8, 3, 1, 2, 3]).collect();
            let recs = parse_tlv(&data).unwrap();
            let enc = encode_tlv(&recs).unwrap();
            check!("100000 records of 3 bytes", (recs.len(), enc == data, join_values(&recs, 0).len()), (100_000, true, 399_999));
        }
        """,
    ],
    wrong=dict(
        slices_with_brackets=sub(TLV_SOL, ("let (value, after) = after.split_at_checked(usize::from(len))?;", "let (value, after) = after.split_at(usize::from(len).min(after.len()));")),
        length_truncated=sub(TLV_SOL, ("let len = u8::try_from(value.len()).ok()?;", "let len = value.len() as u8;")),
        grows_while_encoding=sub(TLV_SOL, ("let mut out = Vec::with_capacity(records.iter().map(|(_, value)| 2 + value.len()).sum());", "let mut out = Vec::new();")),
        magic_not_skipped=sub(TLV_SOL, ('let mut rest = data.strip_prefix(b"TLV").unwrap_or(data);', "let mut rest = data;")),
        concat_drops_separators=sub(TLV_SOL, ("records.iter().map(|&(_, value)| value).collect::<Vec<_>>().join(&sep)", "let _ = sep;\n    records.iter().map(|&(_, value)| value).collect::<Vec<_>>().concat()")),
    ),
    hints=[("rust", "`let Some((&tag, after)) = rest.split_first()` peels one byte; `after.split_at_checked(n)?` peels `n` more or returns `None`. `data.strip_prefix(b\"TLV\")` is `Option<&[u8]>`."),
           ("rust", "Sum `2 + value.len()` for `Vec::with_capacity`, then `push` and `extend_from_slice`. `u8::try_from(len).ok()?` rejects 256 and up."),
           ("rust", "A `Vec<&[u8]>` has `.join(&sep)` (with a separator) and `.concat()` (without).")],
    notes=("""Nothing here copies value bytes while parsing: each value is a `&[u8]` into `data`, so the whole parse is one `Vec` of pairs. The `Option`-returning splitters (`split_first`, `split_last`, `split_at_checked`, `get(a..b)`, `strip_prefix`) turn every bounds check into a `?`, which is how you write parsers for untrusted input that can't panic. `as u8` on a length silently wraps 256 to 0, producing a corrupt but well-formed-looking frame; `try_from` makes it an error. Syntax to remember: `s.split_first()` / `split_last()` → `Option<(&T, &[T])>`, `s.split_at_checked(n)` (1.80+), `s.strip_prefix(b"…")`, `s.get(a..b)`, `v.extend_from_slice(s)`, `slices.concat()`, `slices.join(&sep)`, `u8::try_from(n)`.""", "O(n)", "O(records)"),
    follow_up="How would you make `parse_tlv` a lazy iterator of `Result<(u8, &[u8]), Truncated>` instead of building a Vec?",
    related=["L3", "S2"],
    perf=dict(allocs=True),
))

NB_STARTER = """
        /// Differences between neighbours: [a, b, c] → [b - a, c - b].
        pub fn deltas(v: &[i64]) -> Vec<i64> {
            let mut out = Vec::new();
            for i in 0..v.len() - 1 {
                out.push(v[i + 1] - v[i]);
            }
            out
        }

        /// Indices of strict local peaks: v[i - 1] < v[i] > v[i + 1]. The two ends are never peaks.
        pub fn peaks(v: &[i32]) -> Vec<usize> {
            let mut out = Vec::new();
            for i in 1..v.len() {
                if v[i - 1] < v[i] && v[i] > v[i + 1] {
                    out.push(i);
                }
            }
            out
        }

        /// The wrapping sum of the big-endian 16-bit words in `bytes`; an odd last byte is padded with a zero byte.
        pub fn sum16(bytes: &[u8]) -> u16 {
            let mut sum = 0u16;
            for i in (0..bytes.len()).step_by(2) {
                sum = sum.wrapping_add(u16::from_be_bytes([bytes[i], bytes[i + 1]]));
            }
            sum
        }

        /// Groups of three digits from the right, joined by commas: "1234567" → "1,234,567". `digits` is ASCII.
        pub fn with_commas(digits: &str) -> String {
            digits.as_bytes().chunks(3).map(|c| std::str::from_utf8(c).unwrap()).collect::<Vec<_>>().join(",")
        }
"""

NB_SOL = """
        /// Differences between neighbours: [a, b, c] → [b - a, c - b].
        pub fn deltas(v: &[i64]) -> Vec<i64> {
            v.windows(2).map(|w| w[1] - w[0]).collect()
        }

        /// Indices of strict local peaks: v[i - 1] < v[i] > v[i + 1]. The two ends are never peaks.
        pub fn peaks(v: &[i32]) -> Vec<usize> {
            v.windows(3).enumerate().filter(|(_, w)| w[0] < w[1] && w[1] > w[2]).map(|(i, _)| i + 1).collect()
        }

        /// The wrapping sum of the big-endian 16-bit words in `bytes`; an odd last byte is padded with a zero byte.
        pub fn sum16(bytes: &[u8]) -> u16 {
            let words = bytes.chunks_exact(2);
            let tail = match words.remainder() {
                [last] => u16::from_be_bytes([*last, 0]),
                _ => 0,
            };
            words.fold(tail, |sum, w| sum.wrapping_add(u16::from_be_bytes([w[0], w[1]])))
        }

        /// Groups of three digits from the right, joined by commas: "1234567" → "1,234,567". `digits` is ASCII.
        pub fn with_commas(digits: &str) -> String {
            digits.as_bytes().rchunks(3).rev().map(|c| std::str::from_utf8(c).unwrap()).collect::<Vec<_>>().join(",")
        }
"""


def py_sum16(bs):
    s = 0
    for i in range(0, len(bs), 2):
        hi = bs[i]
        lo = bs[i + 1] if i + 1 < len(bs) else 0
        s = (s + (hi << 8 | lo)) & 0xFFFF
    return s


def commas(d):
    out = []
    while d:
        out.append(d[-3:])
        d = d[:-3]
    return ",".join(reversed(out))


def s16(name, bs):
    lit = "&[" + ", ".join(f"0x{b:02X}" for b in bs) + "]"
    return T(name, f"bytes = {lit[1:]}", f"sum16({lit})", f"0x{py_sum16(bs):04X}")


def wc(name, d):
    return T(name, f'"{d}"', f'with_commas("{d}")', f'"{commas(d)}".to_string()')


P.append(dict(
    slug="fix-neighbour-loop", title="Fix: off-by-one in neighbour loops", mode="fix", level="easy", stage="use-it",
    tags=["windows", "chunks_exact", "remainder", "rchunks", "usize underflow"],
    teaches=[
        "`0..v.len() - 1` underflows on an empty slice; `windows(n)` yields nothing when there aren't `n` elements.",
        "`chunks_exact(2)` plus `remainder()` separates the full words from an odd tail; `step_by(2)` with `v[i + 1]` panics on it.",
        "`rchunks(3)` groups from the right, which is what digit grouping needs; `.rev()` puts the groups back in reading order.",
    ],
    statement="""
        Four helpers that loop over neighbours or fixed-size groups. They were written with index arithmetic and
        tested on "nice" lengths only: each one panics or gives the wrong answer on some input. Fix them to match
        their doc comments.
    """,
    examples=[("deltas(&[])", "[] (not a panic)"), ("sum16(&[0x12, 0x34, 0x56])", "0x6834"), ('with_commas("1234567")', '"1,234,567"')],
    starter=NB_STARTER,
    solution=NB_SOL,
    visible=[
        T("deltas_basic", "v = [1, 4, 9]", "deltas(&[1, 4, 9])", "vec![3, 5]"),
        T("deltas_empty", "v = []", "deltas(&[])", "Vec::<i64>::new()"),
        T("peaks_basic", "v = [1, 3, 2, 5, 4]", "peaks(&[1, 3, 2, 5, 4])", "vec![1, 3]"),
        s16("sum16_odd_length", [0x12, 0x34, 0x56]),
        wc("commas_seven_digits", "1234567"),
    ],
    hidden=[
        T("deltas_single", "v = [5]", "deltas(&[5])", "Vec::<i64>::new()"),
        T("deltas_negative", "v = [3, -2, -2]", "deltas(&[3, -2, -2])", "vec![-5, 0]"),
        T("peaks_short", "v = [], [1], [1, 2]", "(peaks(&[]), peaks(&[1]), peaks(&[1, 2]))", "(vec![], vec![], vec![])"),
        T("peaks_ends_never_count", "v = [9, 1, 9]", "peaks(&[9, 1, 9])", "Vec::<usize>::new()"),
        T("peaks_plateau_is_not_strict", "v = [1, 3, 3, 1]", "peaks(&[1, 3, 3, 1])", "Vec::<usize>::new()"),
        T("peaks_last_interior", "v = [0, 1, 0]", "peaks(&[0, 1, 0])", "vec![1]"),
        s16("sum16_empty", []),
        s16("sum16_one_byte", [0xAB]),
        s16("sum16_even", [0x12, 0x34, 0x56, 0x78]),
        s16("sum16_wraps", [0xFF, 0xFF, 0x00, 0x02]),
        wc("commas_short", "12"),
        wc("commas_exact_three", "123"),
        wc("commas_four", "1000"),
        wc("commas_six", "123456"),
        T("commas_empty", '""', 'with_commas("")', "String::new()"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(7305);
            for _ in 0..400 {
                let n = rng.below(9);
                let v: Vec<i64> = rng.vec(n, -5, 5);
                let w: Vec<i32> = v.iter().map(|&x| x as i32).collect();
                let want_d: Vec<i64> = (1..n).map(|i| v[i] - v[i - 1]).collect();
                let want_p: Vec<usize> = (1..n.saturating_sub(1)).filter(|&i| w[i - 1] < w[i] && w[i] > w[i + 1]).collect();
                let bytes: Vec<u8> = rng.vec(n, 0, 255);
                let mut want_s = 0u16;
                let mut i = 0;
                while i < n {
                    let lo = if i + 1 < n { bytes[i + 1] } else { 0 };
                    want_s = want_s.wrapping_add((bytes[i] as u16) << 8 | lo as u16);
                    i += 2;
                }
                let digits: String = (0..n).map(|k| char::from(b'0' + (k % 10) as u8)).collect();
                let mut want_c = String::new();
                for (k, c) in digits.chars().enumerate() {
                    if k > 0 && (n - k) % 3 == 0 {
                        want_c.push(',');
                    }
                    want_c.push(c);
                }
                check!(format!("v = {v:?}, bytes = {bytes:?}, digits = {digits:?}"),
                       (deltas(&v), peaks(&w), sum16(&bytes), with_commas(&digits)), (want_d, want_p, want_s, want_c));
            }
        }

        #[test]
        fn scale_200k() {
            let v: Vec<i64> = (0..200_000).map(|i| i * i % 1000).collect();
            let w: Vec<i32> = (0..200_001).map(|i| if i % 2 == 1 { 1 } else { 0 }).collect();
            let bytes = vec![0xFFu8; 200_001];
            check!("200000 values", (deltas(&v).len(), peaks(&w).len(), sum16(&bytes), with_commas(&"9".repeat(200_000)).len()), (199_999, 100_000, 0x7860, 266_666));
        }
        """,
    ],
    wrong=dict(
        saturating_loop_bound=sub(NB_SOL, ("v.windows(2).map(|w| w[1] - w[0]).collect()", "let mut out = Vec::new();\n    for i in 0..v.len().saturating_sub(1) {\n        out.push(v[i] - v[i + 1]);\n    }\n    out")),
        peak_index_of_window=sub(NB_SOL, (".map(|(i, _)| i + 1)", ".map(|(i, _)| i)")),
        odd_byte_dropped=sub(NB_SOL, ("[last] => u16::from_be_bytes([*last, 0]),", "[_] => 0,")),
        odd_byte_as_low_byte=sub(NB_SOL, ("[last] => u16::from_be_bytes([*last, 0]),", "[last] => u16::from(*last),")),
        groups_from_the_left=sub(NB_SOL, ("digits.as_bytes().rchunks(3).rev()", "digits.as_bytes().chunks(3)")),
    ),
    hints=[("rust", "`v.windows(2)` yields `&[a, b]` for each neighbouring pair and nothing for fewer than 2 elements; `windows(3).enumerate()` gives the index of each window's first element."),
           ("rust", "`let words = bytes.chunks_exact(2);` then `words.remainder()` is the odd byte (if any), available before you consume `words`."),
           ("rust", "`rchunks(3)` starts at the end: `\"1234567\"` gives `567`, `234`, `1`. Reverse that before joining.")],
    notes=("""Every bug is index arithmetic at the edges. `v.len() - 1` is a `usize` subtraction that panics (debug) or wraps (release) on an empty slice; `v[i + 1]` in a loop to `len` reads one past the end; `step_by(2)` assumes an even length. The slice iterators encode the edge cases: `windows(n)` yields nothing for short input, `chunks_exact` hands the leftover to `remainder()` instead of a short last chunk, and `rchunks` aligns groups at the end. `sum16` is the core of the Internet checksum (RFC 1071), which pads an odd byte on the right, making it the *high* byte of the last word. Syntax to remember: `s.windows(n)`, `s.chunks(n)`, `s.chunks_exact(n)` + `.remainder()`, `s.rchunks(n)`, `s.chunks_exact_mut(n)`, `iter.rev()`, `u16::from_be_bytes([hi, lo])`, `a.wrapping_add(b)`.""", "O(n)", "O(n)"),
    follow_up="`with_commas` builds a `Vec<&str>` just to join it. How would you write it straight into a `String` with the right capacity?",
    rules=dict(lines=22),
    related=["S6"],
))

ROT_SOL = """
        /// Rotates `v` right by `k` with three reversals (no `rotate_*`).
        pub fn rotate_right(v: &mut [i32], k: usize) {
            if v.is_empty() {
                return;
            }
            let k = k % v.len();
            v.reverse();
            v[..k].reverse();
            v[k..].reverse();
        }

        /// Moves the element at `from` to index `to`, shifting everything in between by one place (drag and drop).
        /// Does nothing if either index is out of range. Touches only the elements between the two indices.
        pub fn move_item<T>(v: &mut [T], from: usize, to: usize) {
            if from >= v.len() || to >= v.len() {
                return;
            }
            if from < to {
                v[from..=to].rotate_left(1);
            } else {
                v[to..=from].rotate_right(1);
            }
        }

        /// Swaps each pair of neighbours: [1, 2, 3, 4, 5] → [2, 1, 4, 3, 5]. An odd last element stays put.
        pub fn swap_pairs<T>(v: &mut [T]) {
            for pair in v.chunks_exact_mut(2) {
                pair.swap(0, 1);
            }
        }
"""

ROT_STARTER = """
        /// Rotates `v` right by `k` with three reversals (no `rotate_*`).
        pub fn rotate_right(v: &mut [i32], k: usize) {
            todo!()
        }

        /// Moves the element at `from` to index `to`, shifting everything in between by one place (drag and drop).
        /// Does nothing if either index is out of range. Touches only the elements between the two indices.
        pub fn move_item<T>(v: &mut [T], from: usize, to: usize) {
            todo!()
        }

        /// Swaps each pair of neighbours: [1, 2, 3, 4, 5] → [2, 1, 4, 3, 5]. An odd last element stays put.
        pub fn swap_pairs<T>(v: &mut [T]) {
            todo!()
        }
"""


def mv(name, v, a, b):
    w = list(v)
    if a < len(w) and b < len(w):
        x = w.pop(a)
        w.insert(b, x)
    arr = lambda xs: "[" + ", ".join(f'"{x}"' for x in xs) + "]"
    return T(name, f"v = {arr(v)}, from = {a}, to = {b}", "v", arr(w), setup=f"let mut v = {arr(v)};\nmove_item(&mut v, {a}, {b});")


P.append(dict(
    slug="rotate-in-place", title="Rotate, move and swap in place", level="easy", stage="use-it", tags=["reverse", "rotate_left", "rotate_right", "swap", "chunks_exact_mut"],
    teaches=[
        "Three reversals rotate a slice in O(1) space; reduce `k` modulo the length first.",
        "Moving one item is a rotation of the sub-slice between the two positions: `rotate_left(1)` when moving right, `rotate_right(1)` when moving left.",
        "`chunks_exact_mut(2)` + `swap(0, 1)` handles pairs and leaves an odd tail alone.",
    ],
    statement="""
        - `rotate_right(v, k)`: rotate right by `k` using three reversals (the interview version; don't call
          `rotate_left`/`rotate_right` here). `k` may exceed the length, and the slice may be empty.
        - `move_item(v, from, to)`: drag-and-drop reordering. Take the element at `from` and put it at index `to`,
          shifting the elements in between by one place. If either index is out of range, do nothing. Only the
          elements between the two positions may move.
        - `swap_pairs(v)`: swap each pair of neighbours; an odd last element stays where it is.
    """,
    examples=[("rotate_right([1, 2, 3, 4, 5], 2)", "[4, 5, 1, 2, 3]"), ("move_item([a, b, c, d, e], 1, 3)", "[a, c, d, b, e]"), ("swap_pairs([1, 2, 3, 4, 5])", "[2, 1, 4, 3, 5]")],
    starter=ROT_STARTER,
    solution=ROT_SOL,
    visible=[
        T("rotate_two", "v = [1, 2, 3, 4, 5], k = 2", "{ let mut v = [1, 2, 3, 4, 5]; rotate_right(&mut v, 2); v }", "[4, 5, 1, 2, 3]"),
        T("rotate_leetcode_189", "v = [1, 2, 3, 4, 5, 6, 7], k = 3", "{ let mut v = [1, 2, 3, 4, 5, 6, 7]; rotate_right(&mut v, 3); v }", "[5, 6, 7, 1, 2, 3, 4]"),
        mv("move_right", ["a", "b", "c", "d", "e"], 1, 3),
        mv("move_left", ["a", "b", "c", "d", "e"], 4, 0),
        T("swap_odd_length", "v = [1, 2, 3, 4, 5]", "{ let mut v = [1, 2, 3, 4, 5]; swap_pairs(&mut v); v }", "[2, 1, 4, 3, 5]"),
    ],
    hidden=[
        T("rotate_empty", "v = [], k = 3", "{ let mut v: [i32; 0] = []; rotate_right(&mut v, 3); v }", "[]"),
        T("rotate_large_k", "v = [1, 2, 3], k = 7", "{ let mut v = [1, 2, 3]; rotate_right(&mut v, 7); v }", "[3, 1, 2]"),
        T("rotate_k_max", "v = [1, 2, 3, 4, 5, 6, 7], k = usize::MAX (≡ 1 mod 7)", "{ let mut v = [1, 2, 3, 4, 5, 6, 7]; rotate_right(&mut v, usize::MAX); v }", "[7, 1, 2, 3, 4, 5, 6]"),
        T("rotate_full_turn", "v = [1, 2], k = 2", "{ let mut v = [1, 2]; rotate_right(&mut v, 2); v }", "[1, 2]"),
        mv("move_same_index", ["a", "b", "c"], 1, 1),
        mv("move_to_end", ["a", "b", "c"], 0, 2),
        mv("move_adjacent_left", ["a", "b", "c"], 2, 1),
        mv("move_from_out_of_range", ["a", "b"], 2, 0),
        mv("move_to_out_of_range", ["a", "b"], 0, 2),
        T("move_only_touches_between", "30 Strings, move 5 → 7: the rest keep their buffers", "(v[..5].iter().zip(&ptrs[..5]).all(|(s, p)| s.as_ptr() == *p), v[8..].iter().zip(&ptrs[8..]).all(|(s, p)| s.as_ptr() == *p), v[7].as_str())",
          '(true, true, "5")', setup="let mut v: Vec<String> = (0..30).map(|i| i.to_string()).collect();\nlet ptrs: Vec<*const u8> = v.iter().map(|s| s.as_ptr()).collect();\nmove_item(&mut v, 5, 7);"),
        T("swap_even_length", "v = [1, 2, 3, 4]", "{ let mut v = [1, 2, 3, 4]; swap_pairs(&mut v); v }", "[2, 1, 4, 3]"),
        T("swap_short", "v = [] and [7]", "{ let mut a: [i32; 0] = []; let mut b = [7]; swap_pairs(&mut a); swap_pairs(&mut b); (a, b) }", "([], [7])"),
        T("swap_strings", 'v = ["a", "b", "c"]', '{ let mut v = vec!["a".to_string(), "b".to_string(), "c".to_string()]; swap_pairs(&mut v); v }', 'vec!["b", "a", "c"]'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(7306);
            for _ in 0..400 {
                let n = rng.below(9);
                let v: Vec<i32> = (0..n as i32).collect();
                let k = rng.below(20);
                let want_rot: Vec<i32> = (0..n).map(|i| v[(i + n - k % n.max(1)) % n.max(1)]).collect();
                let (from, to) = (rng.below(n + 2), rng.below(n + 2));
                let mut want_move = v.clone();
                if from < n && to < n {
                    let x = want_move.remove(from);
                    want_move.insert(to, x);
                }
                let want_swap: Vec<i32> = (0..n).map(|i| if i % 2 == 0 && i + 1 < n { v[i + 1] } else if i % 2 == 1 { v[i - 1] } else { v[i] }).collect();
                let (mut a, mut b, mut c) = (v.clone(), v.clone(), v.clone());
                rotate_right(&mut a, k);
                move_item(&mut b, from, to);
                swap_pairs(&mut c);
                check!(format!("v = {v:?}, k = {k}, from = {from}, to = {to}"), (a, b, c), (want_rot, want_move, want_swap));
            }
        }

        #[test]
        fn scale_200k() {
            let mut v: Vec<i32> = (0..200_000).collect();
            rotate_right(&mut v, 100_000);
            for i in 0..100_000 {
                move_item(&mut v, i, i + 1);
            }
            swap_pairs(&mut v);
            check!("v = 0..200000: rotate 100000, 100000 adjacent moves, swap pairs", (v[0], v[1], v[99_999], v[100_000], v[199_999]), (100_002, 100_001, 199_999, 1, 99_998));
        }
        """,
    ],
    wrong=dict(
        rotates_left=sub(ROT_SOL, ("""v.reverse();
            v[..k].reverse();
            v[k..].reverse();""", """v[..k].reverse();
            v[k..].reverse();
            v.reverse();""")),
        k_not_reduced=sub(ROT_SOL, ("let k = k % v.len();", "if k > v.len() {\n        return;\n    }")),
        rotation_direction_swapped=sub(ROT_SOL, ("v[from..=to].rotate_left(1);", "v[from..=to].rotate_right(1);")),
        swaps_the_endpoints=sub(ROT_SOL, ("""if from < to {
                v[from..=to].rotate_left(1);
            } else {
                v[to..=from].rotate_right(1);
            }""", "v.swap(from, to);")),
        swaps_across_pairs=sub(ROT_SOL, ("""for pair in v.chunks_exact_mut(2) {
                pair.swap(0, 1);
            }""", """for i in 1..v.len() {
                if i % 2 == 1 {
                    v.swap(i - 1, i);
                }
            }
            if v.len() % 2 == 1 && v.len() > 1 {
                let n = v.len();
                v.swap(n - 2, n - 1);
            }""")),
    ),
    hints=[("approach", "Rotating right by k: reverse everything, then reverse the first k and the rest separately."),
           ("rust", "Moving from 1 to 3 in `[a, b, c, d]` is `v[1..=3].rotate_left(1)`: `b` goes to the end of that window. Moving left is `rotate_right(1)` on `v[to..=from]`."),
           ("rust", "`v.chunks_exact_mut(2)` yields `&mut [T]` pairs and skips an odd tail; `pair.swap(0, 1)` swaps inside one.")],
    notes=("""All three are in place, O(1) extra space. `move_item` as a rotation of `v[from..=to]` costs O(|to − from|); `v.remove(from)` + `v.insert(to, x)` does the same job on a `Vec` in O(n) with two shifts, and doesn't work on a slice at all. `slice::rotate_left`/`rotate_right` are O(n) and O(1) space (std picks between a buffer-based and a cycle-based algorithm). Syntax to remember: `v.reverse()`, `v[a..b].reverse()`, `v[a..=b].rotate_left(1)` / `rotate_right(1)`, `v.swap(i, j)`, `v.chunks_exact_mut(2)`, `a.swap_with_slice(b)`, `std::mem::swap(&mut x, &mut y)`.""", "O(n), O(|to − from|), O(n)", "O(1)"),
    follow_up="Prove that the three reversals produce the rotation. Why is `rotate_left(1)` on a window cheaper than remove + insert?",
    related=["D2"],
))

DD_SOL = """
        /// `v` is sorted. Moves the values to the front so each appears at most `k` times (k ≥ 1), in order, and
        /// returns how many there are. O(n) time, O(1) extra space.
        pub fn dedup_keep(v: &mut [i32], k: usize) -> usize {
            let mut write = 0;
            for read in 0..v.len() {
                if write < k || v[read] != v[write - k] {
                    v[write] = v[read];
                    write += 1;
                }
            }
            write
        }

        /// The same on a `Vec`: drop the extra copies in place.
        pub fn dedup_keep_vec(v: &mut Vec<i32>, k: usize) {
            let n = dedup_keep(v, k);
            v.truncate(n);
        }
"""

DD_STARTER = """
        /// `v` is sorted. Moves the values to the front so each appears at most `k` times (k ≥ 1), in order, and
        /// returns how many there are. O(n) time, O(1) extra space.
        pub fn dedup_keep(v: &mut [i32], k: usize) -> usize {
            todo!()
        }

        /// The same on a `Vec`: drop the extra copies in place.
        pub fn dedup_keep_vec(v: &mut Vec<i32>, k: usize) {
            todo!()
        }
"""


def dk(name, v, k):
    out = []
    for x in v:
        if out.count(x) < k:
            out.append(x)
    return T(name, f"v = {v}, k = {k}", f"{{ let mut v = {v}; let n = dedup_keep(&mut v, {k}); (n, v[..n].to_vec()) }}" if v else f"{{ let mut v: [i32; 0] = []; let n = dedup_keep(&mut v, {k}); (n, v[..n].to_vec()) }}",
             f"({len(out)}, vec!{out})" if out else "(0, vec![])")


P.append(dict(
    slug="remove-duplicates-sorted", title="Remove duplicates in place, keeping at most k", level="easy", stage="use-it", tags=["two pointers", "in place", "truncate"],
    teaches=[
        "A write index compacts in place: copy a value down only when it should stay.",
        "\"At most k copies\" compares with what was *written* k places back, `v[write - k]`, not with the input's neighbours, which may already be overwritten.",
        "A slice can't shrink, so the slice version returns a length; the `Vec` version then `truncate`s.",
    ],
    statement="""
        `v` is sorted in ascending order.

        - `dedup_keep(v, k)`: move the values to the front so that each distinct value appears at most `k` times
          (`k ≥ 1`), keeping them in order, and return how many values that is. What's left after them doesn't
          matter. O(n) time, O(1) extra space.
        - `dedup_keep_vec(v, k)`: the same on a `Vec`, which ends up holding exactly those values.
    """,
    examples=[("v = [0, 0, 1, 1, 1, 2], k = 1", "3, v starts [0, 1, 2]"), ("v = [1, 1, 1, 2, 2, 3], k = 2", "5, v starts [1, 1, 2, 2, 3]")],
    starter=DD_STARTER,
    solution=DD_SOL,
    visible=[
        dk("leetcode_26", [0, 0, 1, 1, 1, 2, 2, 3, 3, 4], 1),
        dk("leetcode_80_first", [1, 1, 1, 2, 2, 3], 2),
        dk("leetcode_80_second", [0, 0, 1, 1, 1, 1, 2, 3, 3], 2),
        dk("empty", [], 2),
        T("vec_truncated", "v = [1, 1, 1, 1], k = 3", "{ let mut v = vec![1, 1, 1, 1]; dedup_keep_vec(&mut v, 3); v }", "vec![1, 1, 1]"),
    ],
    hidden=[
        dk("single", [7], 1),
        dk("k_larger_than_runs", [1, 1, 2], 5),
        dk("all_same_k_three", [4] * 7, 3),
        dk("all_distinct", [-3, 0, 7], 1),
        dk("negatives_and_extremes", [-2147483648, -2147483648, -2147483648, 0, 2147483647, 2147483647], 2),
        dk("alternating_run_lengths", [1, 2, 2, 2, 3, 4, 4, 4, 4, 5], 2),
        dk("runs_at_the_end", [1, 2, 3, 3, 3, 3], 2),
        T("vec_empty_and_k_one", "v = [], then [2, 2, 3] with k = 1", "{ let mut a: Vec<i32> = vec![]; dedup_keep_vec(&mut a, 1); let mut b = vec![2, 2, 3]; dedup_keep_vec(&mut b, 1); (a, b) }", "(vec![], vec![2, 3])"),
        T("vec_keeps_capacity", "v = [5; 100], k = 2: truncated in place", "(v, v_cap_same)", "(vec![5, 5], true)",
          setup="let mut v = vec![5; 100];\nlet cap = v.capacity();\ndedup_keep_vec(&mut v, 2);\nlet v_cap_same = v.capacity() == cap;"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(7307);
            for _ in 0..400 {
                let n = rng.below(14);
                let mut v: Vec<i32> = rng.vec(n, -3, 3);
                v.sort();
                let k = rng.below(4) + 1;
                let mut want: Vec<i32> = Vec::new();
                for &x in &v {
                    if want.iter().filter(|&&y| y == x).count() < k {
                        want.push(x);
                    }
                }
                let mut got = v.clone();
                let len = dedup_keep(&mut got, k);
                let mut got_vec = v.clone();
                dedup_keep_vec(&mut got_vec, k);
                check!(format!("v = {v:?}, k = {k}"), (len, got[..len].to_vec(), got_vec), (want.len(), want.clone(), want));
            }
        }

        #[test]
        fn scale_200k() {
            let mut v: Vec<i32> = (0..200_000).map(|i| i / 4).collect();
            v.extend(vec![50_000; 100_000]);
            let k = dedup_keep(&mut v, 3);
            check!("v = [0, 0, 0, 0, 1, …, 49999 ×4] then 100000 × 50000, k = 3", (k, v[k - 1], v[k - 4]), (150_003, 50_000, 49_999));
        }
        """,
    ],
    wrong=dict(
        compares_with_input_neighbours=sub(DD_SOL, ("if write < k || v[read] != v[write - k] {", "if read < k || v[read] != v[read - k] {")),
        compares_with_previous_written=sub(DD_SOL, ("if write < k || v[read] != v[write - k] {", "if write == 0 || v[read] != v[write - 1] || (write >= k && v[read] != v[write - k]) {")),
        forgets_to_truncate=sub(DD_SOL, ("let n = dedup_keep(v, k);\n    v.truncate(n);", "dedup_keep(v, k);")),
        shift_left_each_time=sub(DD_SOL, ("""let mut write = 0;
            for read in 0..v.len() {
                if write < k || v[read] != v[write - k] {
                    v[write] = v[read];
                    write += 1;
                }
            }
            write""", """let mut len = v.len();
            let mut i = k;
            while i < len {
                if v[i] == v[i - k] {
                    v[i..len].rotate_left(1);
                    len -= 1;
                } else {
                    i += 1;
                }
            }
            len.min(v.len())""")),
    ),
    hints=[("approach", "Keep a write position. Copy `v[read]` down if fewer than `k` values have been written, or if it differs from the value written `k` places back."),
           ("edge case", "Comparing `v[read]` with `v[read - k]` reads input that the write index may already have overwritten."),
           ("rust", "`v.truncate(n)` drops the tail in place and keeps the capacity.")],
    notes=("""Because `v` is sorted, "this value already has k copies" is exactly "the value written k places back equals it". The write index never passes the read index, so reading `v[read]` is always the original value, but `v[read - k]` may not be. `Vec::dedup` is the k = 1 case followed by `truncate`, and `dedup_by(|a, b| …)` generalises the test. Syntax to remember: `v.truncate(n)`, `v.dedup()`, `v.dedup_by_key(|x| …)`, `v[..n].to_vec()`, `v.copy_within(src_range, dest)`.""", "O(n)", "O(1)"),
    follow_up="How would you do the same on an unsorted slice, keeping first-seen order, and what would it cost?",
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
        T("empty_sep", "parts = [\"a\", \"b\"], sep = \"\"", '{ let s = join_with(&["a", "b"], ""); (s.clone(), s.capacity() == s.len()) }', '("ab".to_string(), true)'),
        T("no_parts", "parts = [], sep = \",\"", 'join_with(&[], ",")', "String::new()"),
        T("empty_parts_keep_seps", "parts = [\"\", \"\"], sep = \",\"", '{ let s = join_with(&["", ""], ","); (s.clone(), s.capacity() == s.len()) }', '(",".to_string(), true)'),
    ],
    hidden=[
        T("none", "parts = [], sep = \",\"", 'join_with(&[], ",")', '""'),
        T("many", "100 parts of \"xyz\", sep = \"/\"", '{ let parts = vec!["xyz"; 100]; let s = join_with(&parts, "/"); (s.len(), s.capacity() == s.len()) }', "(399, true)"),
        T("single_empty_part", "parts = [\"\"], sep = \"-\"", 'join_with(&[""], "-")', "String::new()"),
        T("unicode", "parts = [\"日本\", \"é\"], sep = \" → \"", '{ let s = join_with(&["日本", "é"], " → "); (s.clone(), s.capacity()) }', '("日本 → é".to_string(), 13)'),
        T("long_sep", "parts = [\"a\", \"b\", \"c\"], sep = \"<->\"", 'join_with(&["a", "b", "c"], "<->")', '"a<->b<->c".to_string()'),
        T("capacity_ten_parts", "10 parts of \"abc\", sep = \", \"", '{ let s = join_with(&["abc"; 10], ", "); (s.len(), s.capacity()) }', "(48, 48)"),
        T("no_trailing_sep", "parts = [\"x\", \"y\"], sep = \";\"", 'join_with(&["x", "y"], ";")', '"x;y".to_string()'),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2308);
            for _ in 0..300 {
                let n = rng.below(6);
                let mut parts = Vec::new();
                for _ in 0..n {
                    let len = rng.below(4);
                    parts.push(rng.string(len, "ab日"));
                }
                let len = rng.below(3);
                let sep = rng.string(len, ",→");
                let refs: Vec<&str> = parts.iter().map(|p| p.as_str()).collect();
                let mut want = String::new();
                for (i, p) in parts.iter().enumerate() {
                    if i > 0 {
                        want += &sep;
                    }
                    want += p;
                }
                let got = join_with(&refs, &sep);
                check!(format!("parts = {parts:?}, sep = {sep:?}"), (got.capacity(), got), (want.len(), want));
            }
        }

        #[test]
        fn scale_500k_parts() {
            let parts = vec!["ab"; 500_000];
            let s = join_with(&parts, ",");
            check!("parts = [\\"ab\\"; 500000], sep = \\",\\"", (s.len(), s.capacity()), (1_499_999, 1_499_999));
        }
        """,
    ],
    wrong=dict(
        grows_as_it_goes="""
            pub fn join_with(parts: &[&str], sep: &str) -> String {
                let mut out = String::new();
                for (i, p) in parts.iter().enumerate() {
                    if i > 0 {
                        out.push_str(sep);
                    }
                    out.push_str(p);
                }
                out
            }
        """,
        one_separator_too_many="""
            pub fn join_with(parts: &[&str], sep: &str) -> String {
                let total = parts.iter().map(|p| p.len() + sep.len()).sum::<usize>();
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
        rebuilds_each_time="""
            pub fn join_with(parts: &[&str], sep: &str) -> String {
                let mut out = String::new();
                for (i, p) in parts.iter().enumerate() {
                    out = if i == 0 { p.to_string() } else { format!("{out}{sep}{p}") };
                }
                out.shrink_to_fit();
                out
            }
        """,
    ),
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
        T("some_reallocations", "REALLOCATIONS", "REALLOCATIONS > 0", "true"),
        T("room_for_all_100", "FINAL_CAPACITY", "FINAL_CAPACITY >= 100", "true"),
        T("capacity_is_a_power_of_two", "FINAL_CAPACITY", "FINAL_CAPACITY.is_power_of_two()", "true"),
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

        fn run() -> (usize, usize) {
            let mut v: Vec<u32> = Vec::new();
            let (mut changes, mut cap) = (0, v.capacity());
            for i in 0..100 {
                v.push(i);
                if v.capacity() != cap {
                    changes += 1;
                    cap = v.capacity();
                }
            }
            (changes, v.capacity())
        }

        #[test]
        fn both_constants() {
            check!("(REALLOCATIONS, FINAL_CAPACITY) for 100 pushes", (REALLOCATIONS, FINAL_CAPACITY), run());
        }

        #[test]
        fn first_capacity_is_not_one() {
            check!("FINAL_CAPACITY >> (REALLOCATIONS - 1): the first capacity", FINAL_CAPACITY >> REALLOCATIONS.saturating_sub(1), 4);
        }

        #[test]
        fn not_an_exact_fit() {
            check!("FINAL_CAPACITY != 100", FINAL_CAPACITY != 100, true);
        }

        #[test]
        fn doubling_steps() {
            check!("REALLOCATIONS as doublings from 4", REALLOCATIONS, (FINAL_CAPACITY / 4).trailing_zeros() as usize + 1);
        }

        #[test]
        fn fewer_than_ten() {
            check!("REALLOCATIONS < 10", REALLOCATIONS < 10, true);
        }

        #[test]
        fn capacity_below_double() {
            check!("FINAL_CAPACITY < 200", FINAL_CAPACITY < 200, true);
        }

        #[test]
        fn reallocations_exact() {
            check!("REALLOCATIONS", REALLOCATIONS, run().0);
        }
        """,
    ],
    wrong=dict(
        doubling_from_one="""
            /// How many times the capacity changes while pushing 0..100 into Vec::<u32>::new().
            pub const REALLOCATIONS: usize = 8;

            /// The capacity after those 100 pushes.
            pub const FINAL_CAPACITY: usize = 128;
        """,
        counts_the_start="""
            /// How many times the capacity changes while pushing 0..100 into Vec::<u32>::new().
            pub const REALLOCATIONS: usize = 7;

            /// The capacity after those 100 pushes.
            pub const FINAL_CAPACITY: usize = 128;
        """,
        exact_fit="""
            /// How many times the capacity changes while pushing 0..100 into Vec::<u32>::new().
            pub const REALLOCATIONS: usize = 1;

            /// The capacity after those 100 pushes.
            pub const FINAL_CAPACITY: usize = 100;
        """,
    ),
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
        T("tail_at_zero", "v = [1, 2], at = 0", "{ let mut v = vec![1, 2]; let t = take_tail(&mut v, 0); (v, t) }", "(vec![], vec![1, 2])"),
        T("tail_at_len", "v = [1, 2], at = 2", "{ let mut v = vec![1, 2]; let t = take_tail(&mut v, 2); (v, t) }", "(vec![1, 2], vec![])"),
        T("splice_delete", "v = [1, 2, 3, 4], replace 1..3 with []", "{ let mut v = vec![1, 2, 3, 4]; let r = replace_range(&mut v, 1, 3, &[]); (v, r) }", "(vec![1, 4], vec![2, 3])"),
    ],
    hidden=[
        T("tail_past_end", "v = [1], at = 5", "{ let mut v = vec![1]; let t = take_tail(&mut v, 5); (v, t) }", "(vec![1], vec![])"),
        T("splice_insert", "v = [1, 4], replace 1..1 with [2, 3]", "{ let mut v = vec![1, 4]; let r = replace_range(&mut v, 1, 1, &[2, 3]); (v, r) }", "(vec![1, 2, 3, 4], vec![])"),
        T("tail_of_empty", "v = [], at = 0", "{ let mut v: Vec<i32> = vec![]; let t = take_tail(&mut v, 0); (v, t) }", "(vec![], vec![])"),
        T("tail_huge_at", "v = [1, 2], at = usize::MAX", "{ let mut v = vec![1, 2]; let t = take_tail(&mut v, usize::MAX); (v, t) }", "(vec![1, 2], vec![])"),
        T("splice_whole", "v = [1, 2, 3], replace 0..3 with [7]", "{ let mut v = vec![1, 2, 3]; let r = replace_range(&mut v, 0, 3, &[7]); (v, r) }", "(vec![7], vec![1, 2, 3])"),
        T("splice_longer", "v = [1, 2], replace 0..1 with [5, 6, 7]", "{ let mut v = vec![1, 2]; let r = replace_range(&mut v, 0, 1, &[5, 6, 7]); (v, r) }", "(vec![5, 6, 7, 2], vec![1])"),
        T("splice_at_end", "v = [1], replace 1..1 with [2]", "{ let mut v = vec![1]; let r = replace_range(&mut v, 1, 1, &[2]); (v, r) }", "(vec![1, 2], vec![])"),
        T("splice_empty_vec", "v = [], replace 0..0 with [1, 2]", "{ let mut v = vec![]; let r = replace_range(&mut v, 0, 0, &[1, 2]); (v, r) }", "(vec![1, 2], vec![])"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2309);
            for _ in 0..300 {
                let n = rng.below(8);
                let v: Vec<i32> = rng.vec(n, 0, 9);
                let at = rng.below(10);
                let start = rng.below(n + 1);
                let end = start + rng.below(n - start + 1);
                let wl = rng.below(4);
                let with: Vec<i32> = rng.vec(wl, 10, 19);
                let cut = at.min(n);
                let want_tail = (v[..cut].to_vec(), v[cut..].to_vec());
                let want_splice = ([&v[..start], &with[..], &v[end..]].concat(), v[start..end].to_vec());
                let (mut a, mut b) = (v.clone(), v.clone());
                let t = take_tail(&mut a, at);
                let r = replace_range(&mut b, start, end, &with);
                check!(format!("v = {v:?}, at = {at}, replace {start}..{end} with {with:?}"), ((a, t), (b, r)), (want_tail, want_splice));
            }
        }

        #[test]
        fn scale_200k() {
            let mut v: Vec<i32> = (0..200_000).collect();
            let r = replace_range(&mut v, 1, 199_999, &[-1]);
            let t = take_tail(&mut v, 1);
            check!("v = 0..200000, replace 1..199999 with [-1], then take_tail(1)", (v, t, r.len()), (vec![0], vec![-1, 199_999], 199_998));
        }
        """,
    ],
    wrong=dict(
        tail_not_clamped="""
            pub fn take_tail(v: &mut Vec<i32>, at: usize) -> Vec<i32> {
                v.drain(at..).collect()
            }

            pub fn replace_range(v: &mut Vec<i32>, start: usize, end: usize, with: &[i32]) -> Vec<i32> {
                v.splice(start..end, with.iter().copied()).collect()
            }
        """,
        end_inclusive="""
            pub fn take_tail(v: &mut Vec<i32>, at: usize) -> Vec<i32> {
                let at = at.min(v.len());
                v.split_off(at)
            }

            pub fn replace_range(v: &mut Vec<i32>, start: usize, end: usize, with: &[i32]) -> Vec<i32> {
                let end = (end + 1).min(v.len());
                v.splice(start..end.max(start), with.iter().copied()).collect()
            }
        """,
        returns_the_front="""
            pub fn take_tail(v: &mut Vec<i32>, at: usize) -> Vec<i32> {
                let at = at.min(v.len());
                let tail = v.split_off(at);
                std::mem::replace(v, tail)
            }

            pub fn replace_range(v: &mut Vec<i32>, start: usize, end: usize, with: &[i32]) -> Vec<i32> {
                v.splice(start..end, with.iter().copied()).collect()
            }
        """,
    ),
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
        T("leetcode_643", "v = [1, 12, -5, -6, 50, 3], k = 4", "max_window_sum(&[1, 12, -5, -6, 50, 3], 4)", "Some(51)"),
        T("window_is_whole_slice", "v = [5], k = 1", "max_window_sum(&[5], 1)", "Some(5)"),
        T("chunk_bigger_than_v", "v = [1, 2], size = 5", "chunk_sums(&[1, 2], 5)", "vec![3]"),
    ],
    hidden=[
        T("window_too_big", "v = [1, 2], k = 3", "max_window_sum(&[1, 2], 3)", "None"),
        T("chunks_empty", "v = [], size = 3", "chunk_sums(&[], 3)", "Vec::<i32>::new()"),
        T("window_on_empty", "v = [], k = 1", "max_window_sum(&[], 1)", "None"),
        T("all_negative_windows", "v = [-3, -1, -2], k = 2", "max_window_sum(&[-3, -1, -2], 2)", "Some(-3)"),
        T("chunk_size_one", "v = [4, -5], size = 1", "chunk_sums(&[4, -5], 1)", "vec![4, -5]"),
        T("exact_multiple", "v = [1, 2, 3, 4], size = 2", "chunk_sums(&[1, 2, 3, 4], 2)", "vec![3, 7]"),
        T("k_equals_len", "v = [1, 2, 3], k = 3", "max_window_sum(&[1, 2, 3], 3)", "Some(6)"),
        T("best_window_last", "v = [1, 1, 1, 9, 9], k = 2", "max_window_sum(&[1, 1, 1, 9, 9], 2)", "Some(18)"),
        T("extremes", "v = [i32::MAX, i32::MIN], size = 1, k = 1", "(chunk_sums(&[i32::MAX, i32::MIN], 1), max_window_sum(&[i32::MIN, i32::MAX], 1))", "(vec![i32::MAX, i32::MIN], Some(i32::MAX))"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2310);
            for _ in 0..300 {
                let n = rng.below(10);
                let v: Vec<i32> = rng.vec(n, -50, 50);
                let size = rng.below(4) + 1;
                let k = rng.below(5) + 1;
                let mut want_chunks = Vec::new();
                let mut i = 0;
                while i < n {
                    want_chunks.push(v[i..(i + size).min(n)].iter().sum::<i32>());
                    i += size;
                }
                let mut want_max: Option<i32> = None;
                for s in 0..n {
                    if s + k <= n {
                        let sum: i32 = v[s..s + k].iter().sum();
                        want_max = Some(want_max.map_or(sum, |m| m.max(sum)));
                    }
                }
                check!(format!("v = {v:?}, size = {size}, k = {k}"), (chunk_sums(&v, size), max_window_sum(&v, k)), (want_chunks, want_max));
            }
        }

        #[test]
        fn scale_200k() {
            let v: Vec<i32> = (0..200_000).map(|i| i % 7 - 3).collect();
            let sums = chunk_sums(&v, 3);
            check!("v = 200000 values, size = 3, k = 2", (sums.len(), sums[0], max_window_sum(&v, 2)), (66_667, -6, Some(5)));
        }
        """,
    ],
    wrong=dict(
        max_from_zero="""
            pub fn chunk_sums(v: &[i32], size: usize) -> Vec<i32> {
                v.chunks(size).map(|c| c.iter().sum()).collect()
            }

            pub fn max_window_sum(v: &[i32], k: usize) -> Option<i32> {
                if v.len() < k {
                    return None;
                }
                Some(v.windows(k).map(|w| w.iter().sum()).fold(0, i32::max))
            }
        """,
        drops_short_chunk="""
            pub fn chunk_sums(v: &[i32], size: usize) -> Vec<i32> {
                v.chunks_exact(size).map(|c| c.iter().sum()).collect()
            }

            pub fn max_window_sum(v: &[i32], k: usize) -> Option<i32> {
                v.windows(k).map(|w| w.iter().sum()).max()
            }
        """,
        zero_when_too_short="""
            pub fn chunk_sums(v: &[i32], size: usize) -> Vec<i32> {
                v.chunks(size).map(|c| c.iter().sum()).collect()
            }

            pub fn max_window_sum(v: &[i32], k: usize) -> Option<i32> {
                Some(v.windows(k).map(|w| w.iter().sum()).max().unwrap_or(0))
            }
        """,
    ),
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
        T("two", "v = [1, 2]", "{ let mut v = [1, 2]; add_halves(&mut v); v }", "[1, 3]"),
        T("five", "v = [1, 2, 3, 4, 5] (mid = 2, the last value is untouched)", "{ let mut v = [1, 2, 3, 4, 5]; add_halves(&mut v); v }", "[1, 2, 4, 6, 5]"),
        T("negatives", "v = [-1, -2, 1, 2]", "{ let mut v = [-1, -2, 1, 2]; add_halves(&mut v); v }", "[-1, -2, 0, 0]"),
    ],
    hidden=[
        T("empty", "v = []", "{ let mut v: [i32; 0] = []; add_halves(&mut v); v }", "[]"),
        T("one", "v = [4]", "{ let mut v = [4]; add_halves(&mut v); v }", "[4]"),
        T("three", "v = [1, 2, 3]", "{ let mut v = [1, 2, 3]; add_halves(&mut v); v }", "[1, 3, 3]"),
        T("zeros", "v = [0, 0, 0, 0]", "{ let mut v = [0; 4]; add_halves(&mut v); v }", "[0; 4]"),
        T("big_values", "v = [1000000000, 1000000000]", "{ let mut v = [1_000_000_000, 1_000_000_000]; add_halves(&mut v); v }", "[1_000_000_000, 2_000_000_000]"),
        T("first_half_unchanged", "v = [7, 8, 9, 1, 2, 3]", "{ let mut v = [7, 8, 9, 1, 2, 3]; add_halves(&mut v); v }", "[7, 8, 9, 8, 10, 12]"),
        T("extremes", "v = [i32::MIN, 0, i32::MAX, 0]", "{ let mut v = [i32::MIN, 0, i32::MAX, 0]; add_halves(&mut v); v }", "[i32::MIN, 0, -1, 0]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2311);
            for _ in 0..300 {
                let n = rng.below(10);
                let v: Vec<i32> = rng.vec(n, -100, 100);
                let mid = n / 2;
                let mut want = v.clone();
                for i in 0..mid {
                    want[mid + i] += v[i];
                }
                let mut got = v.clone();
                add_halves(&mut got);
                check!(format!("v = {v:?}"), got, want);
            }
        }

        #[test]
        fn scale_200k() {
            let mut v = vec![1; 200_001];
            add_halves(&mut v);
            check!("v = [1; 200001]", (v[99_999], v[100_000], v[199_999], v[200_000]), (1, 2, 2, 1));
        }
        """,
    ],
    wrong=dict(
        mid_rounds_up="""
            pub fn add_halves(v: &mut [i32]) {
                let mid = (v.len() + 1) / 2;
                let (first, second) = v.split_at_mut(mid);
                for (a, b) in first.iter().zip(second.iter_mut()) {
                    *b += *a;
                }
            }
        """,
        adds_into_first="""
            pub fn add_halves(v: &mut [i32]) {
                let mid = v.len() / 2;
                let (first, second) = v.split_at_mut(mid);
                for (a, b) in first.iter_mut().zip(second.iter()) {
                    *a += *b;
                }
            }
        """,
        mirrored="""
            pub fn add_halves(v: &mut [i32]) {
                let n = v.len();
                for i in 0..n / 2 {
                    v[n - 1 - i] += v[i];
                }
            }
        """,
    ),
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
        T("single", "v = [7]", "{ let mut v = vec![7]; double_up(&mut v); v }", "vec![7, 7]"),
        T("three", "v = [1, 2, 3]", "{ let mut v = vec![1, 2, 3]; double_up(&mut v); v }", "vec![1, 2, 3, 1, 2, 3]"),
        T("duplicates", "v = [5, 5]", "{ let mut v = vec![5, 5]; double_up(&mut v); v }", "vec![5, 5, 5, 5]"),
    ],
    hidden=[
        T("big", "v = 0..1000", "{ let mut v: Vec<i32> = (0..1000).collect(); double_up(&mut v); (v.len(), v[1000], v[1999]) }", "(2000, 0, 999)"),
        T("negatives", "v = [-1, -2]", "{ let mut v = vec![-1, -2]; double_up(&mut v); v }", "vec![-1, -2, -1, -2]"),
        T("extremes", "v = [i32::MIN, i32::MAX]", "{ let mut v = vec![i32::MIN, i32::MAX]; double_up(&mut v); v }", "vec![i32::MIN, i32::MAX, i32::MIN, i32::MAX]"),
        T("twice", "v = [1, 2], double_up twice", "{ let mut v = vec![1, 2]; double_up(&mut v); double_up(&mut v); v }", "vec![1, 2, 1, 2, 1, 2, 1, 2]"),
        T("order_kept", "v = [3, 1, 2]", "{ let mut v = vec![3, 1, 2]; double_up(&mut v); v }", "vec![3, 1, 2, 3, 1, 2]"),
        T("single_zero", "v = [0]", "{ let mut v = vec![0]; double_up(&mut v); v }", "vec![0, 0]"),
        T("first_half_untouched", "v = [9, 8, 7, 6]", "{ let mut v = vec![9, 8, 7, 6]; double_up(&mut v); v[..4].to_vec() }", "vec![9, 8, 7, 6]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2312);
            for _ in 0..300 {
                let n = rng.below(10);
                let v: Vec<i32> = rng.vec(n, -9, 9);
                let want = [&v[..], &v[..]].concat();
                let mut got = v.clone();
                double_up(&mut got);
                check!(format!("v = {v:?}"), got, want);
            }
        }

        #[test]
        fn scale_200k() {
            let mut v: Vec<i32> = (0..200_000).collect();
            double_up(&mut v);
            check!("v = 0..200000", (v.len(), v[199_999], v[200_000], v[399_999]), (400_000, 199_999, 0, 199_999));
        }
        """,
    ],
    wrong=dict(
        each_doubled_in_place="""
            /// Appends a copy of every element: [1, 2] → [1, 2, 1, 2].
            pub fn double_up(v: &mut Vec<i32>) {
                let n = v.len();
                for i in 0..n {
                    let x = v[2 * i];
                    v.insert(2 * i + 1, x);
                }
            }
        """,
        appended_reversed="""
            /// Appends a copy of every element: [1, 2] → [1, 2, 1, 2].
            pub fn double_up(v: &mut Vec<i32>) {
                for i in (0..v.len()).rev() {
                    let x = v[i];
                    v.push(x);
                }
            }
        """,
    ),
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
    solution=GRID,
    visible=[
        T("set_and_get", "3×2 grid, set (2, 1) = 7", "{ let mut g = Grid::new(3, 2); g.set(2, 1, 7); (g.get(2, 1), g.get(0, 0)) }", "(Some(7), Some(0))"),
        T("row", "3×2 grid, set (1, 1) = 5", "g.row(1)", "Some(&[0, 5, 0][..])", setup="let mut g = Grid::new(3, 2);\ng.set(1, 1, 5);"),
        T("out_of_bounds", "3×2 grid", "{ let mut g = Grid::new(3, 2); (g.get(3, 0), g.set(0, 2, 1), g.row(2).is_none()) }", "(None, false, true)"),
        T("fresh_row", "2×3 grid, row 0", "Grid::new(2, 3).row(0).map(|r| r.to_vec())", "Some(vec![0, 0])"),
        T("set_in_bounds", "2×2 grid, set (1, 0) = 4", "{ let mut g = Grid::new(2, 2); (g.set(1, 0, 4), g.get(1, 0), g.get(0, 1)) }", "(true, Some(4), Some(0))"),
    ],
    hidden=[
        T("empty_grid", "0×0 grid", "{ let g = Grid::new(0, 0); (g.get(0, 0), g.row(0).is_none()) }", "(None, true)"),
        T("x_not_wrapping", "2×2 grid, get (2, 0)", "{ let mut g = Grid::new(2, 2); g.set(0, 1, 9); g.get(2, 0) }", "None"),
        T("one_by_one", "1×1 grid", "{ let mut g = Grid::new(1, 1); (g.set(0, 0, 3), g.get(0, 0), g.row(0).map(|r| r.to_vec())) }", "(true, Some(3), Some(vec![3]))"),
        T("wide", "5×1 grid, set (4, 0) = 9", "{ let mut g = Grid::new(5, 1); g.set(4, 0, 9); g.row(0).map(|r| r.to_vec()) }", "Some(vec![0, 0, 0, 0, 9])"),
        T("tall", "1×5 grid, set (0, 4) = 9", "{ let mut g = Grid::new(1, 5); g.set(0, 4, 9); (g.row(4).map(|r| r.to_vec()), g.get(0, 3)) }", "(Some(vec![9]), Some(0))"),
        T("row_major_not_column_major", "3×2 grid, set (2, 0) = 5", "{ let mut g = Grid::new(3, 2); g.set(2, 0, 5); (g.row(0).map(|r| r.to_vec()), g.row(1).map(|r| r.to_vec())) }", "(Some(vec![0, 0, 5]), Some(vec![0, 0, 0]))"),
        T("overwrite", "2×2 grid, set (1, 1) = 1 then 2", "{ let mut g = Grid::new(2, 2); g.set(1, 1, 1); g.set(1, 1, 2); g.get(1, 1) }", "Some(2)"),
        T("huge_coordinates", "2×2 grid, x or y = usize::MAX", "{ let mut g = Grid::new(2, 2); (g.get(usize::MAX, 0), g.get(0, usize::MAX), g.set(usize::MAX, 1, 1), g.row(usize::MAX).is_none()) }", "(None, None, false, true)"),
        T("zero_width_rows", "0×3 grid", "{ let g = Grid::new(0, 3); (g.get(0, 0), g.row(2).map(|r| r.len())) }", "(None, Some(0))"),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2313);
            for _ in 0..200 {
                let (w, h) = (rng.below(5), rng.below(5));
                let mut g = Grid::new(w, h);
                let mut model = vec![vec![0u8; w]; h];
                let mut ops = Vec::new();
                for _ in 0..10 {
                    let (x, y, value) = (rng.below(6), rng.below(6), rng.below(256) as u8);
                    ops.push((x, y, value));
                    let ok = x < w && y < h;
                    if ok {
                        model[y][x] = value;
                    }
                    check!(format!("{w}×{h} grid, sets {ops:?}"), g.set(x, y, value), ok);
                }
                for y in 0..6 {
                    for x in 0..6 {
                        let want = if x < w && y < h { Some(model[y][x]) } else { None };
                        check!(format!("{w}×{h} grid, sets {ops:?}, get({x}, {y})"), g.get(x, y), want);
                    }
                    check!(format!("{w}×{h} grid, sets {ops:?}, row({y})"), g.row(y).map(|r| r.to_vec()), model.get(y).cloned());
                }
            }
        }

        #[test]
        fn big_grid() {
            let mut g = Grid::new(1000, 1000);
            g.set(999, 0, 1);
            g.set(0, 999, 2);
            g.set(999, 999, 3);
            check!("1000×1000 grid, corners set", (g.get(999, 0), g.get(0, 999), g.row(999).map(|r| r[999]), g.get(1000, 999)), (Some(1), Some(2), Some(3), None));
        }
        """,
    ],
    wrong=dict(
        no_x_check=sub(GRID, ("(x < self.w && y < self.h).then(|| y * self.w + x)", "let i = y * self.w + x;\n        (y < self.h && i < self.cells.len()).then_some(i)")),
        column_major=sub(GRID, ("(x < self.w && y < self.h).then(|| y * self.w + x)", "(x < self.w && y < self.h).then(|| x * self.h + y)")),
    ),
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
        T("insert_duplicate", "v = [1, 2, 2, 3], x = 2", "{ let mut v = vec![1, 2, 2, 3]; insert_sorted(&mut v, 2); v }", "vec![1, 2, 2, 2, 3]"),
        T("count_none_inside", "v = [1, 5], lo = 2, hi = 4", "count_in_range(&[1, 5], 2, 4)", "0"),
        T("count_bounds_inclusive", "v = [1, 2, 3], lo = 1, hi = 3", "count_in_range(&[1, 2, 3], 1, 3)", "3"),
    ],
    hidden=[
        T("insert_front_and_back", "v = [5], x = 1 then 9", "{ let mut v = vec![5]; insert_sorted(&mut v, 1); insert_sorted(&mut v, 9); v }", "vec![1, 5, 9]"),
        T("empty_range", "v = [1, 2, 3], lo = 5, hi = 1", "count_in_range(&[1, 2, 3], 5, 1)", "0"),
        T("insert_into_empty", "v = [], x = 4", "{ let mut v = vec![]; insert_sorted(&mut v, 4); v }", "vec![4]"),
        T("count_on_empty", "v = [], lo = 0, hi = 9", "count_in_range(&[], 0, 9)", "0"),
        T("lo_equals_hi", "v = [1, 2, 2, 3], lo = 2, hi = 2", "count_in_range(&[1, 2, 2, 3], 2, 2)", "2"),
        T("negatives", "v = [-5, -3, 0], lo = -4, hi = 0", "count_in_range(&[-5, -3, 0], -4, 0)", "2"),
        T("extremes", "v = [i32::MIN, 0, i32::MAX], lo = i32::MIN, hi = i32::MAX", "count_in_range(&[i32::MIN, 0, i32::MAX], i32::MIN, i32::MAX)", "3"),
        T("insert_extremes", "v = [0], x = i32::MAX then i32::MIN", "{ let mut v = vec![0]; insert_sorted(&mut v, i32::MAX); insert_sorted(&mut v, i32::MIN); v }", "vec![i32::MIN, 0, i32::MAX]"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2314);
            for _ in 0..300 {
                let n = rng.below(10);
                let mut v: Vec<i32> = rng.vec(n, -5, 5);
                v.sort();
                let x = rng.int(-6, 6) as i32;
                let (lo, hi) = (rng.int(-6, 6) as i32, rng.int(-6, 6) as i32);
                let want_count = v.iter().filter(|&&y| lo <= y && y <= hi).count();
                let mut want_v = v.clone();
                want_v.push(x);
                want_v.sort();
                let mut got_v = v.clone();
                insert_sorted(&mut got_v, x);
                check!(format!("v = {v:?}, x = {x}, lo = {lo}, hi = {hi}"), (got_v, count_in_range(&v, lo, hi)), (want_v, want_count));
            }
        }

        #[test]
        fn scale_200k_queries() {
            let v: Vec<i32> = (0..200_000).map(|i| i * 2).collect();
            let total: usize = (0..200_000).map(|q| count_in_range(&v, q, q + 10)).sum();
            check!("v = [0, 2, 4, …, 399998], 200000 queries lo = q, hi = q + 10", total, 1_100_000);
        }
        """,
    ],
    wrong=dict(
        linear_count="""
            pub fn insert_sorted(v: &mut Vec<i32>, x: i32) {
                let i = v.partition_point(|&y| y < x);
                v.insert(i, x);
            }

            pub fn count_in_range(v: &[i32], lo: i32, hi: i32) -> usize {
                v.iter().filter(|&&y| lo <= y && y <= hi).count()
            }
        """,
        exclusive_hi="""
            pub fn insert_sorted(v: &mut Vec<i32>, x: i32) {
                let i = v.partition_point(|&y| y < x);
                v.insert(i, x);
            }

            pub fn count_in_range(v: &[i32], lo: i32, hi: i32) -> usize {
                let start = v.partition_point(|&y| y < lo);
                let end = v.partition_point(|&y| y < hi);
                end.saturating_sub(start)
            }
        """,
        unchecked_subtraction="""
            pub fn insert_sorted(v: &mut Vec<i32>, x: i32) {
                let i = v.partition_point(|&y| y < x);
                v.insert(i, x);
            }

            pub fn count_in_range(v: &[i32], lo: i32, hi: i32) -> usize {
                let start = v.partition_point(|&y| y < lo);
                let end = v.partition_point(|&y| y <= hi);
                end - start
            }
        """,
    ),
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
        T("get_on_empty", "new MiniVec, get(0)", "MiniVec::<i32>::new().get(0).copied()", "None"),
        T("len_tracks_pushes_and_pops", "push 1, 2, 3, pop", "{ let mut v = MiniVec::new(); v.push(1); v.push(2); v.push(3); v.pop(); (v.len(), v.get(1).copied(), v.get(2).copied()) }", "(2, Some(2), None)"),
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
        T("capacity_sequence", "capacity after 1, 4, 5, 8, 9, 16 and 17 pushes", "{ let mut v = MiniVec::new(); let mut caps = vec![]; for i in 1..=17u32 { v.push(i); if [1, 4, 5, 8, 9, 16, 17].contains(&i) { caps.push(v.capacity()); } } caps }", "vec![4, 4, 8, 8, 16, 16, 32]"),
        T("lifo", "push 0..10, then pop everything", "{ let mut v = MiniVec::new(); for i in 0..10 { v.push(i); } let mut out = vec![]; while let Some(x) = v.pop() { out.push(x); } (out, v.len()) }", "((0..10).rev().collect::<Vec<_>>(), 0)"),
        T("pop_then_push", "push 1, 2, pop, push 3", "{ let mut v = MiniVec::new(); v.push(1); v.push(2); v.pop(); v.push(3); (v.len(), v.get(0).copied(), v.get(1).copied()) }", "(2, Some(1), Some(3))"),
        T("get_after_pop", "push 1, pop, get(0)", "{ let mut v = MiniVec::new(); v.push(1); v.pop(); v.get(0).copied() }", "None"),
        """
        #[test]
        fn drop_releases_a_thousand() {
            let counter = Rc::new(());
            {
                let mut v = MiniVec::new();
                for _ in 0..1000 {
                    v.push(Rc::clone(&counter));
                }
                check!("1000 Rc clones inside the MiniVec", Rc::strong_count(&counter), 1001);
            }
            check!("1000 Rc clones pushed, then the MiniVec dropped", Rc::strong_count(&counter), 1);
        }

        #[test]
        fn popped_value_is_owned() {
            let counter = Rc::new(());
            let mut v = MiniVec::new();
            v.push(Rc::clone(&counter));
            let x = v.pop();
            drop(v);
            check!("an Rc popped out, then the MiniVec dropped", Rc::strong_count(&counter), 2);
            drop(x);
        }

        #[test]
        fn random_vs_vec() {
            let mut rng = anneal_prelude::Rng::new(2315);
            for _ in 0..200 {
                let mut ours = MiniVec::new();
                let mut want: Vec<String> = Vec::new();
                let mut ops = Vec::new();
                for _ in 0..rng.below(30) {
                    if rng.below(3) == 0 {
                        ops.push("pop".to_string());
                        check!(format!("{ops:?}"), ours.pop(), want.pop());
                    } else {
                        let s = rng.below(100).to_string();
                        ops.push(format!("push {s}"));
                        ours.push(s.clone());
                        want.push(s);
                    }
                }
                let got: Vec<Option<String>> = (0..want.len() + 1).map(|i| ours.get(i).cloned()).collect();
                let expected: Vec<Option<String>> = want.iter().cloned().map(Some).chain([None]).collect();
                check!(format!("{ops:?}, then get(0..=len)"), (ours.len(), got), (want.len(), expected));
            }
        }

        #[test]
        fn scale_200k() {
            let mut v = MiniVec::new();
            for i in 0..200_000u64 {
                v.push(i);
            }
            let mut sum = 0;
            while let Some(x) = v.pop() {
                sum += x;
            }
            check!("push 0..200000, then pop everything", (sum, v.len(), v.capacity()), (19_999_900_000, 0, 262_144));
        }
        """,
    ],
    wrong=dict(
        grows_by_four=sub(MINIVEC, ("self.cap * 2", "self.cap + 4")),
        leaks_elements=sub(MINIVEC, ("        while self.pop().is_some() {}\n", "")),
    ),
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
    solution=MINIVEC + DEREF_IMPLS,
    visible=[
        T("iter_sum", "push 1..=4", "{ let mut v = MiniVec::new(); for i in 1..=4 { v.push(i); } v.iter().sum::<i32>() }", "10"),
        T("sort", "push 3, 1, 2", "{ let mut v = MiniVec::new(); v.push(3); v.push(1); v.push(2); v.sort(); v.as_slice().to_vec() }", "vec![1, 2, 3]"),
        T("index", "push 10, 20", "{ let mut v = MiniVec::new(); v.push(10); v.push(20); (v[0], v[1]) }", "(10, 20)"),
        T("slice_length", "push 3 values", "{ let mut v = MiniVec::new(); for i in 0..3 { v.push(i); } (v.as_slice().len(), v.len()) }", "(3, 3)"),
        T("write_through_as_mut_slice", "push 1, 2, then as_mut_slice()[0] = 9", "{ let mut v = MiniVec::new(); v.push(1); v.push(2); v.as_mut_slice()[0] = 9; v.as_slice().to_vec() }", "vec![9, 2]"),
    ],
    hidden=[
        T("empty_slice", "new MiniVec", "MiniVec::<String>::new().as_slice().len()", "0"),
        T("range_index", "push 10, 20, 30", "{ let mut v = MiniVec::new(); v.push(10); v.push(20); v.push(30); v[1..].to_vec() }", "vec![20, 30]"),
        T("mutate_through_slice", "push 1, 2", "{ let mut v = MiniVec::new(); v.push(1); v.push(2); for x in v.iter_mut() { *x *= 5; } v.as_slice().to_vec() }", "vec![5, 10]"),
        T("empty_mut_slice", "new MiniVec", "MiniVec::<u8>::new().as_mut_slice().len()", "0"),
        T("contains_and_search", "push 1, 3, 5", "{ let mut v = MiniVec::new(); for x in [1, 3, 5] { v.push(x); } (v.contains(&3), v.contains(&4), v.binary_search(&5)) }", "(true, false, Ok(2))"),
        T("first_last", "push \"a\", \"b\", \"c\"", '{ let mut v = MiniVec::new(); for s in ["a", "b", "c"] { v.push(s.to_string()); } (v.first().cloned(), v.last().cloned()) }', '(Some("a".to_string()), Some("c".to_string()))'),
        T("reverse", "push 1, 2, 3, then reverse", "{ let mut v = MiniVec::new(); for x in 1..=3 { v.push(x); } v.reverse(); v.to_vec() }", "vec![3, 2, 1]"),
        T("windows_through_deref", "push 1, 2, 3", "{ let mut v = MiniVec::new(); for x in 1..=3 { v.push(x); } v.windows(2).map(|w| w[0] + w[1]).collect::<Vec<_>>() }", "vec![3, 5]"),
        T("after_pop", "push 1, 2, 3, pop", "{ let mut v = MiniVec::new(); for x in 1..=3 { v.push(x); } v.pop(); v.to_vec() }", "vec![1, 2]"),
        """
        #[test]
        fn random_vs_vec() {
            let mut rng = anneal_prelude::Rng::new(2316);
            for _ in 0..200 {
                let n = rng.below(20);
                let values: Vec<i32> = rng.vec(n, -50, 50);
                let mut v = MiniVec::new();
                for &x in &values {
                    v.push(x);
                }
                let mut want = values.clone();
                want.sort();
                v.sort();
                check!(format!("push {values:?}, then sort"), (v.to_vec(), v.len()), (want, n));
            }
        }

        #[test]
        fn scale_200k_sort() {
            let mut v = MiniVec::new();
            for i in 0..200_000u32 {
                v.push(i.wrapping_mul(2_654_435_761));
            }
            v.sort_unstable();
            check!("200000 values, sorted through DerefMut", (v.len(), v.windows(2).all(|w| w[0] <= w[1])), (200_000, true));
        }
        """,
    ],
    wrong=dict(
        drops_the_last=MINIVEC + DEREF_IMPLS.replace("self.len)", "self.len.saturating_sub(1))"),
        always_empty=MINIVEC + """
impl<T> MiniVec<T> {
    pub fn as_slice(&self) -> &[T] {
        &[]
    }

    pub fn as_mut_slice(&mut self) -> &mut [T] {
        &mut []
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
    ),
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
    solution=SMALLVEC,
    visible=[
        T("stays_inline", "push 4 items", "{ let mut v = SmallVec4::new(); for i in 0..4 { v.push(i); } (v.len(), v.is_inline(), v.get(3).copied()) }", "(4, true, Some(3))"),
        T("spills", "push 5 items", "{ let mut v = SmallVec4::new(); for i in 0..5 { v.push(i * 10); } (v.len(), v.is_inline(), v.get(0).copied(), v.get(4).copied()) }", "(5, false, Some(0), Some(40))"),
        T("new_is_empty", "new SmallVec4", "{ let v = SmallVec4::<i32>::new(); (v.len(), v.is_inline(), v.get(0).copied()) }", "(0, true, None)"),
        T("order_after_spill", "push 0..6", "{ let mut v = SmallVec4::new(); for i in 0..6 { v.push(i); } (0..6).map(|i| v.get(i).copied()).collect::<Vec<_>>() }", "(0..6).map(Some).collect::<Vec<_>>()"),
        T("get_past_len_after_spill", "push 5 items, get(5)", "{ let mut v = SmallVec4::new(); for i in 0..5 { v.push(i); } v.get(5).copied() }", "None"),
    ],
    hidden=[
        T("get_past_len", "push 1 item", "{ let mut v = SmallVec4::new(); v.push('a'); (v.get(1).copied(), v.get(0).copied()) }", "(None, Some('a'))"),
        T("strings", "push 6 Strings", '{ let mut v = SmallVec4::new(); for w in ["a", "b", "c", "d", "e", "f"] { v.push(w.to_string()); } v.get(5).cloned() }', 'Some("f".to_string())'),
        T("three_inline", "push 3 items", "{ let mut v = SmallVec4::new(); for i in 0..3 { v.push(i); } (v.len(), v.is_inline(), v.get(3).copied()) }", "(3, true, None)"),
        T("hundred", "push 0..100", "{ let mut v = SmallVec4::new(); for i in 0..100 { v.push(i); } (v.len(), v.is_inline(), v.get(99).copied(), v.get(100).copied()) }", "(100, false, Some(99), None)"),
        T("spilled_keeps_first_four", "push 5 Strings", '{ let mut v = SmallVec4::new(); for w in ["a", "b", "c", "d", "e"] { v.push(w.to_string()); } (0..5).map(|i| v.get(i).cloned().unwrap_or_default()).collect::<String>() }', '"abcde".to_string()'),
        T("get_past_len_inline", "push 4 items, get(4)", "{ let mut v = SmallVec4::new(); for i in 0..4 { v.push(i); } (v.get(4).copied(), v.is_inline()) }", "(None, true)"),
        """
        use std::rc::Rc;

        #[test]
        fn nothing_leaks_after_spill() {
            let counter = Rc::new(());
            {
                let mut v = SmallVec4::new();
                for _ in 0..6 {
                    v.push(Rc::clone(&counter));
                }
                check!("6 Rc clones inside", Rc::strong_count(&counter), 7);
            }
            check!("6 Rc clones pushed, then the SmallVec4 dropped", Rc::strong_count(&counter), 1);
        }

        #[test]
        fn random_vs_vec() {
            let mut rng = anneal_prelude::Rng::new(2317);
            for _ in 0..200 {
                let n = rng.below(12);
                let values: Vec<i32> = rng.vec(n, -50, 50);
                let mut v = SmallVec4::new();
                for &x in &values {
                    v.push(x);
                }
                let got: Vec<Option<i32>> = (0..n + 1).map(|i| v.get(i).copied()).collect();
                let want: Vec<Option<i32>> = values.iter().copied().map(Some).chain([None]).collect();
                check!(format!("push {values:?}"), (v.len(), v.is_inline(), got), (n, n <= 4, want));
            }
        }

        #[test]
        fn scale_200k() {
            let mut v = SmallVec4::new();
            for i in 0..200_000u32 {
                v.push(i);
            }
            check!("push 0..200000", (v.len(), v.get(3).copied(), v.get(199_999).copied()), (200_000, Some(3), Some(199_999)));
        }
        """,
    ],
    wrong=dict(
        spills_at_four=sub(SMALLVEC, ("if *len < 4 =>", "if *len < 3 =>")),
        loses_the_fifth=sub(SMALLVEC, ("                heap.push(value);\n", "")),
        spills_reversed=sub(SMALLVEC, ("items.iter_mut().filter_map(Option::take)", "items.iter_mut().rev().filter_map(Option::take)")),
    ),
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
    solution=RING,
    visible=[
        T("not_full", "capacity 3, push 1, 2", "{ let mut r = Ring::with_capacity(3); r.push(1); r.push(2); r.iter().copied().collect::<Vec<_>>() }", "vec![1, 2]"),
        T("evicts_oldest", "capacity 2, push 1, 2, 3", "{ let mut r = Ring::with_capacity(2); r.push(1); r.push(2); let e = r.push(3); (e, r.iter().copied().collect::<Vec<_>>()) }", "(Some(1), vec![2, 3])"),
        T("exactly_full", "capacity 3, push 1, 2, 3", "{ let mut r = Ring::with_capacity(3); let e = (r.push(1), r.push(2), r.push(3)); (e, r.iter().copied().collect::<Vec<_>>()) }", "((None, None, None), vec![1, 2, 3])"),
        T("len_stops_at_capacity", "capacity 2, push 1, 2, 3", "{ let mut r = Ring::with_capacity(2); r.push(1); r.push(2); r.push(3); r.len() }", "2"),
        T("evictions_in_order", "capacity 2, push 1, 2, 3, 4", "{ let mut r = Ring::with_capacity(2); r.push(1); r.push(2); (r.push(3), r.push(4)) }", "(Some(1), Some(2))"),
    ],
    hidden=[
        T("wraps_many_times", "capacity 3, push 0..10", "{ let mut r = Ring::with_capacity(3); for i in 0..10 { r.push(i); } (r.len(), r.iter().copied().collect::<Vec<_>>()) }", "(3, vec![7, 8, 9])"),
        T("capacity_one", "capacity 1, push \"a\", \"b\"", '{ let mut r = Ring::with_capacity(1); r.push("a"); (r.push("b"), r.iter().copied().collect::<Vec<_>>()) }', '(Some("a"), vec!["b"])'),
        T("empty_ring", "capacity 3, nothing pushed", "{ let r = Ring::<u8>::with_capacity(3); (r.len(), r.iter().count()) }", "(0, 0)"),
        T("zero_capacity_panics", "capacity 0", "std::panic::catch_unwind(|| Ring::<u8>::with_capacity(0)).is_err()", "true"),
        T("strings", "capacity 2, push \"a\", \"b\", \"c\"", '{ let mut r = Ring::with_capacity(2); r.push("a".to_string()); r.push("b".to_string()); (r.push("c".to_string()), r.iter().cloned().collect::<Vec<_>>()) }', '(Some("a".to_string()), vec!["b".to_string(), "c".to_string()])'),
        T("big", "capacity 1000, push 0..2500", "{ let mut r = Ring::with_capacity(1000); let evicted = (0..2500).filter_map(|i| r.push(i)).count(); let v: Vec<i32> = r.iter().copied().collect(); (evicted, v.len(), v[0], v[999]) }", "(1500, 1000, 1500, 2499)"),
        T("iter_twice", "capacity 3, push 1..=4, iterate twice", "{ let mut r = Ring::with_capacity(3); for i in 1..=4 { r.push(i); } (r.iter().copied().collect::<Vec<_>>(), r.iter().copied().collect::<Vec<_>>()) }", "(vec![2, 3, 4], vec![2, 3, 4])"),
        """
        #[test]
        fn random_vs_model() {
            let mut rng = anneal_prelude::Rng::new(2318);
            for _ in 0..300 {
                let cap = rng.below(5) + 1;
                let mut r = Ring::with_capacity(cap);
                let mut model = std::collections::VecDeque::new();
                let mut pushed = Vec::new();
                for _ in 0..rng.below(15) {
                    let x = rng.below(100) as u32;
                    pushed.push(x);
                    model.push_back(x);
                    let want = if model.len() > cap { model.pop_front() } else { None };
                    check!(format!("capacity {cap}, push {pushed:?}"), r.push(x), want);
                }
                check!(format!("capacity {cap}, push {pushed:?}, then iter"), (r.len(), r.iter().copied().collect::<Vec<_>>()), (model.len(), model.into_iter().collect::<Vec<_>>()));
            }
        }

        #[test]
        fn scale_300k_pushes() {
            let mut r = Ring::with_capacity(150_000);
            let mut evicted = 0u64;
            for i in 0..300_000u64 {
                evicted += r.push(i).unwrap_or(0);
            }
            let first = r.iter().next().copied();
            check!("capacity 150000, push 0..300000", (r.len(), first, evicted), (150_000, Some(150_000), 11_249_925_000));
        }
        """,
    ],
    wrong=dict(
        evicts_newest=sub(RING, ("let old = self.buf[self.head].replace(value);\n            self.head = (self.head + 1) % cap;\n            old", "let newest = (self.head + self.len - 1) % cap;\n            self.buf[newest].replace(value)")),
        iter_ignores_head=sub(RING, ("self.buf[(self.head + i) % cap]", "self.buf[i % cap]")),
        shifts_on_evict=sub(RING, ("let old = self.buf[self.head].replace(value);\n            self.head = (self.head + 1) % cap;\n            old", "let old = self.buf[0].take();\n            self.buf.rotate_left(1);\n            self.buf[cap - 1] = Some(value);\n            old")),
    ),
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
        T("even_length", "v = [1, 2, 3, 4]", "pairs(&[1, 2, 3, 4]).map(|(a, b)| (*a, *b)).collect::<Vec<_>>()", "vec![(1, 2), (3, 4)]"),
        T("single", "v = [1]", "pairs(&[1]).count()", "0"),
        T("len_of_five", "v = [1, 2, 3, 4, 5]", "pairs(&[1, 2, 3, 4, 5]).len()", "2"),
    ],
    hidden=[
        T("len", "v = [0; 7]", "pairs(&[0; 7]).len()", "3"),
        T("empty", "v = []", "pairs::<u8>(&[]).next()", "None"),
        T("len_after_next", "v = [0; 7], one next()", "{ let mut it = pairs(&[0; 7]); it.next(); it.len() }", "2"),
        T("size_hint_exact", "v = [0; 6]", "pairs(&[0; 6]).size_hint()", "(3, Some(3))"),
        T("two", "v = [8, 9]", "pairs(&[8, 9]).map(|(a, b)| (*a, *b)).collect::<Vec<_>>()", "vec![(8, 9)]"),
        T("strings", "v = [\"a\", \"b\", \"c\", \"d\", \"e\"]", 'pairs(&["a", "b", "c", "d", "e"]).map(|(a, b)| format!("{a}{b}")).collect::<Vec<_>>()', 'vec!["ab", "cd"]'),
        T("next_after_end", "v = [1, 2]", "{ let mut it = pairs(&[1, 2]); it.next(); (it.next(), it.next(), it.len()) }", "(None, None, 0)"),
        T("refs_point_into_v", "v = [1, 2]", "{ let (a, b) = pairs(&v).next().unwrap(); (std::ptr::eq(a, &v[0]), std::ptr::eq(b, &v[1])) }", "(true, true)", setup="let v = [1, 2];"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(2319);
            for _ in 0..300 {
                let n = rng.below(10);
                let v: Vec<i32> = rng.vec(n, -9, 9);
                let want: Vec<(i32, i32)> = (0..n / 2).map(|i| (v[2 * i], v[2 * i + 1])).collect();
                let it = pairs(&v);
                let len = it.len();
                check!(format!("v = {v:?}"), (len, it.map(|(a, b)| (*a, *b)).collect::<Vec<_>>()), (n / 2, want));
            }
        }

        #[test]
        fn scale_200k() {
            let v: Vec<u32> = (0..200_001).collect();
            let sum: u64 = pairs(&v).map(|(a, b)| (*a + *b) as u64).sum();
            check!("v = 0..200001", (pairs(&v).len(), sum), (100_000, 19_999_900_000));
        }
        """,
    ],
    wrong=dict(
        overlapping="""
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
                        [a, b, ..] => {
                            self.rest = &self.rest[1..];
                            Some((a, b))
                        }
                        _ => None,
                    }
                }

                fn size_hint(&self) -> (usize, Option<usize>) {
                    let n = self.rest.len().saturating_sub(1);
                    (n, Some(n))
                }
            }

            impl<T> ExactSizeIterator for Pairs<'_, T> {}
        """,
        size_hint_rounds_up="""
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
                    let n = (self.rest.len() + 1) / 2;
                    (n, Some(n))
                }
            }

            impl<T> ExactSizeIterator for Pairs<'_, T> {}
        """,
    ),
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
