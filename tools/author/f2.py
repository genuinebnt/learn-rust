from author import T, write_track

P = []

# Section F grading (CURRICULUM §6.1): layout assertions first, then allocation counters, then timing.
# `size_of` / `align_of` checks only use types whose layout is the same on x86_64 and aarch64.

# ---------------------------------------------------------------- size it (easy)

SQE_QUIZ = """
//! Work the quiz out by reasoning: `size_of`, `align_of`, `offset_of!` and `Layout` are off limits in this
//! file (the tests use them to check you).

#[allow(dead_code)]
pub struct Q1 {
    pub a: u8,
    pub b: u32,
    pub c: u8,
}

#[allow(dead_code)]
#[repr(C)]
pub struct Q2 {
    pub a: u8,
    pub b: u32,
    pub c: u8,
}

pub type Q3 = (u8, u64, u8);

#[allow(dead_code)]
#[repr(C)]
pub struct Q4 {
    pub a: u64,
    pub b: u8,
}

pub type Q5 = [Q4; 2];

#[allow(dead_code)]
#[repr(C)]
pub struct Q6 {
    pub tag: u8,
    pub inner: Q2,
}

pub type Q7 = (u8, [u16; 3]);

pub type Q8 = [u64; 0];

/// `(size_of, align_of)` of `Q1` to `Q8`, in order.
pub const LAYOUT: [(usize, usize); 8] = ANSWERS;
"""

SQE_BAD = """
/// One submission queue entry. The C consumer reads it by field offset, so it stays `#[repr(C)]`.
#[repr(C)]
#[derive(Clone, Copy, Debug, PartialEq, Eq, Default)]
pub struct Sqe {
    pub opcode: u8,
    pub fd: i32,
    pub flags: u8,
    pub off: u64,
    pub ioprio: u16,
    pub addr: u64,
    pub len: u32,
    pub user_data: u64,
    pub rw_flags: u32,
    pub buf_index: u16,
    pub personality: u16,
    pub file_index: u32,
}
"""

SQE_GOOD = """
/// One submission queue entry. The C consumer reads it by field offset, so it stays `#[repr(C)]`.
/// Ordered so every field lands on its alignment with no hole: 1 + 1 + 2 + 4 fill the first 8 bytes
/// behind `opcode`, then the 8-byte fields, then 4 + 4 and 2 + 2 + 4 pairs.
#[repr(C)]
#[derive(Clone, Copy, Debug, PartialEq, Eq, Default)]
pub struct Sqe {
    pub opcode: u8,
    pub flags: u8,
    pub ioprio: u16,
    pub fd: i32,
    pub off: u64,
    pub addr: u64,
    pub len: u32,
    pub rw_flags: u32,
    pub user_data: u64,
    pub buf_index: u16,
    pub personality: u16,
    pub file_index: u32,
}
"""

SQE_CTORS = """
pub const OP_NOP: u8 = 0;
pub const OP_READ: u8 = 22;
pub const OP_WRITE: u8 = 23;

impl Sqe {
    pub fn nop(user_data: u64) -> Sqe {
        Sqe { opcode: OP_NOP, user_data, ..Sqe::default() }
    }

    pub fn read(fd: i32, addr: u64, len: u32, off: u64, user_data: u64) -> Sqe {
        Sqe { opcode: OP_READ, fd, addr, len, off, user_data, ..Sqe::default() }
    }

    pub fn write(fd: i32, addr: u64, len: u32, off: u64, user_data: u64) -> Sqe {
        Sqe { opcode: OP_WRITE, fd, addr, len, off, user_data, ..Sqe::default() }
    }
}
"""

SQE_RING_TODO = """
/// A submission ring: `entries` slots (a power of two) and free-running `u32` counters.
pub struct SqRing {
    slots: Box<[Sqe]>,
    mask: u32,
    head: u32,
    tail: u32,
}

impl SqRing {
    pub fn new(entries: u32) -> SqRing {
        SqRing::starting_at(entries, 0)
    }

    /// Both counters start at `counter`. Panics unless `entries` is a power of two.
    pub fn starting_at(entries: u32, counter: u32) -> SqRing {
        todo!()
    }

    pub fn head(&self) -> u32 {
        self.head
    }

    pub fn tail(&self) -> u32 {
        self.tail
    }

    pub fn len(&self) -> usize {
        todo!()
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    pub fn is_full(&self) -> bool {
        todo!()
    }

    /// Queues `sqe`, or hands it back when the ring is full.
    pub fn push(&mut self, sqe: Sqe) -> Result<(), Sqe> {
        todo!()
    }

    /// The oldest entry.
    pub fn pop(&mut self) -> Option<Sqe> {
        todo!()
    }
}
"""


def sqe_ring(len_expr="self.tail.wrapping_sub(self.head) as usize"):
    return """
/// A submission ring: `entries` slots (a power of two) and free-running `u32` counters.
pub struct SqRing {
    slots: Box<[Sqe]>,
    mask: u32,
    head: u32,
    tail: u32,
}

impl SqRing {
    pub fn new(entries: u32) -> SqRing {
        SqRing::starting_at(entries, 0)
    }

    /// Both counters start at `counter`. Panics unless `entries` is a power of two.
    pub fn starting_at(entries: u32, counter: u32) -> SqRing {
        assert!(entries.is_power_of_two(), "entries must be a power of two, got {entries}");
        SqRing { slots: vec![Sqe::default(); entries as usize].into_boxed_slice(), mask: entries - 1, head: counter, tail: counter }
    }

    pub fn head(&self) -> u32 {
        self.head
    }

    pub fn tail(&self) -> u32 {
        self.tail
    }

    /// The counters run freely and wrap at `u32::MAX`; their wrapping difference is the length.
    pub fn len(&self) -> usize {
        LEN
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    pub fn is_full(&self) -> bool {
        self.len() == self.slots.len()
    }

    /// Queues `sqe`, or hands it back when the ring is full.
    pub fn push(&mut self, sqe: Sqe) -> Result<(), Sqe> {
        if self.is_full() {
            return Err(sqe);
        }
        self.slots[(self.tail & self.mask) as usize] = sqe;
        self.tail = self.tail.wrapping_add(1);
        Ok(())
    }

    /// The oldest entry.
    pub fn pop(&mut self) -> Option<Sqe> {
        if self.is_empty() {
            return None;
        }
        let sqe = self.slots[(self.head & self.mask) as usize];
        self.head = self.head.wrapping_add(1);
        Some(sqe)
    }
}
""".replace("LEN", len_expr)


SQE_ANSWERS = "[(8, 4), (12, 4), (16, 8), (16, 8), (32, 8), (16, 4), (8, 2), (0, 8)]"


def sqe_solution(answers=SQE_ANSWERS, sqe=SQE_GOOD, ring=None):
    return SQE_QUIZ.replace("ANSWERS", answers) + sqe + SQE_CTORS + (ring or sqe_ring())


SQE_NO_PADDING = """
#[test]
fn no_holes_anywhere() {
    use std::mem::{offset_of, size_of};
    let mut spans = vec![
        (offset_of!(Sqe, opcode), 1),
        (offset_of!(Sqe, flags), 1),
        (offset_of!(Sqe, ioprio), 2),
        (offset_of!(Sqe, fd), 4),
        (offset_of!(Sqe, off), 8),
        (offset_of!(Sqe, addr), 8),
        (offset_of!(Sqe, len), 4),
        (offset_of!(Sqe, rw_flags), 4),
        (offset_of!(Sqe, user_data), 8),
        (offset_of!(Sqe, buf_index), 2),
        (offset_of!(Sqe, personality), 2),
        (offset_of!(Sqe, file_index), 4),
    ];
    spans.sort();
    // Each field starts where the previous one ended, and the last one ends at size_of.
    let mut end = 0;
    let mut holes = Vec::new();
    for &(at, len) in &spans {
        if at != end {
            holes.push((end, at));
        }
        end = at + len;
    }
    if end != size_of::<Sqe>() {
        holes.push((end, size_of::<Sqe>()));
    }
    check!("padding holes in Sqe as (from, to) byte ranges", holes, Vec::<(usize, usize)>::new());
}
"""

SQE_RANDOM = """
#[test]
fn random_vs_vecdeque() {
    let mut rng = anneal_prelude::Rng::new(8201);
    for _ in 0..300 {
        let entries = 1u32 << rng.below(4);
        let start = if rng.bool() { u32::MAX - rng.below(6) as u32 } else { rng.below(1000) as u32 };
        let mut ring = SqRing::starting_at(entries, start);
        let mut model = std::collections::VecDeque::new();
        let mut log = Vec::new();
        for step in 0..40u64 {
            if rng.below(3) < 2 {
                let sqe = Sqe::nop(step);
                log.push(format!("push {step}"));
                let want = if model.len() == entries as usize { Err(sqe) } else { model.push_back(sqe); Ok(()) };
                check!(format!("entries {entries}, start {start}: {}", log.join(", ")), ring.push(sqe), want);
            } else {
                log.push("pop".to_string());
                check!(format!("entries {entries}, start {start}: {}", log.join(", ")), ring.pop(), model.pop_front());
            }
            check!(format!("entries {entries}, start {start}: {}; len", log.join(", ")), (ring.len(), ring.is_full()), (model.len(), model.len() == entries as usize));
        }
    }
}
"""

P.append(dict(
    slug="repack-a-submission-entry", title="Repack a submission entry", mode="fix", level="easy", stage="size-it",
    tags=["padding", "repr(C)", "field order", "alignment", "ring buffer"],
    teaches=["A field starts at a multiple of its alignment; a struct's size is a multiple of its largest alignment (the trailing padding is what makes arrays work).",
             "`repr(Rust)` lets rustc reorder fields to remove padding (tuples too); `#[repr(C)]` keeps your order, so you pack it by hand.",
             "io_uring's free-running `u32` head and tail counters: slot = `counter & mask`, length = `tail.wrapping_sub(head)`."],
    statement="""
        A proxy submits reads and writes through an io_uring-style submission ring: an array of `Sqe` entries
        in shared memory that a C consumer reads by field offset. `Sqe` stays `#[repr(C)]` (the C header is
        generated from it), and the consumer reads the first byte, `opcode`, before anything else.

        1. **Quiz.** Fill in `LAYOUT`: the `(size, align)` of the types `Q1` to `Q8`, in order. Reason it out:
           `size_of`, `align_of`, `offset_of!` and `Layout` are off limits in your code.
        2. **Shrink.** `Sqe` is 72 bytes, 24 of them padding. Reorder its fields so it is **48 bytes with no
           padding**, align 8, still `#[repr(C)]`, with `opcode` at offset 0. Keep every field and its type.
        3. **Ring.** Finish `SqRing`: `entries` slots (a power of two) and free-running `u32` `head` and `tail`
           counters, as the kernel keeps them. An entry lives in slot `counter & mask`; the counters wrap at
           `u32::MAX`, and the length is their wrapping difference. `push` hands the entry back when the ring
           is full; `pop` takes the oldest. `starting_at(entries, counter)` starts both counters at `counter`.
    """,
    examples=[("size_of::<Sqe>(), offset_of!(Sqe, opcode)", "48, 0"),
              ("SqRing::starting_at(4, u32::MAX - 1); push 3 entries", "len 3, tail 1")],
    constraints=["entries is a power of two, 1 to 2³¹", "Sqe keeps #[repr(C)], its 12 fields and their types",
                 "no size_of / align_of / offset_of! / Layout in your code"],
    starter=sqe_solution(answers="[(0, 0); 8]", sqe=SQE_BAD, ring=SQE_RING_TODO),
    solution=sqe_solution(),
    visible=[
        T("sqe_is_48_bytes", "size_of::<Sqe>(), align_of::<Sqe>()", "(std::mem::size_of::<Sqe>(), std::mem::align_of::<Sqe>())", "(48, 8)"),
        T("opcode_comes_first", "offset_of!(Sqe, opcode)", "std::mem::offset_of!(Sqe, opcode)", "0"),
        T("quiz_reordered_vs_repr_c", "LAYOUT[0..2]: Q1 { u8, u32, u8 } and #[repr(C)] Q2 { u8, u32, u8 }", "(LAYOUT[0], LAYOUT[1])",
          "((std::mem::size_of::<Q1>(), std::mem::align_of::<Q1>()), (std::mem::size_of::<Q2>(), std::mem::align_of::<Q2>()))"),
        T("ring_is_fifo", "SqRing::new(4): push nop 1, 2, 3, then pop 3 times", "(ring.pop(), ring.pop(), ring.pop(), ring.pop())",
          "(Some(Sqe::nop(1)), Some(Sqe::nop(2)), Some(Sqe::nop(3)), None)",
          setup="let mut ring = SqRing::new(4);\nfor u in 1..=3 {\n    ring.push(Sqe::nop(u)).unwrap();\n}"),
        T("full_ring_hands_entry_back", "SqRing::new(2): push nop 1, 2, then read(3, 0x1000, 512, 0, 9)", "(ring.push(extra), ring.len(), ring.is_full())",
          "(Err(Sqe::read(3, 0x1000, 512, 0, 9)), 2, true)",
          setup="let mut ring = SqRing::new(2);\nring.push(Sqe::nop(1)).unwrap();\nring.push(Sqe::nop(2)).unwrap();\nlet extra = Sqe::read(3, 0x1000, 512, 0, 9);"),
        T("counters_wrap", "SqRing::starting_at(4, u32::MAX - 1): push 3 entries", "(ring.len(), ring.head(), ring.tail(), ring.pop().map(|s| s.user_data))",
          "(3, u32::MAX - 1, 1, Some(0))",
          setup="let mut ring = SqRing::starting_at(4, u32::MAX - 1);\nfor u in 0..3 {\n    ring.push(Sqe::nop(u)).unwrap();\n}"),
    ],
    hidden=[
        T("quiz_tuple_is_reordered", "LAYOUT[2]: (u8, u64, u8)", "LAYOUT[2]", "(std::mem::size_of::<Q3>(), std::mem::align_of::<Q3>())"),
        T("quiz_trailing_padding", "LAYOUT[3..5]: #[repr(C)] Q4 { u64, u8 } and [Q4; 2]", "(LAYOUT[3], LAYOUT[4])",
          "((std::mem::size_of::<Q4>(), std::mem::align_of::<Q4>()), (std::mem::size_of::<Q5>(), std::mem::align_of::<Q5>()))"),
        T("quiz_nested", "LAYOUT[5]: #[repr(C)] Q6 { u8, Q2 }", "LAYOUT[5]", "(std::mem::size_of::<Q6>(), std::mem::align_of::<Q6>())"),
        T("quiz_arrays", "LAYOUT[6..8]: (u8, [u16; 3]) and [u64; 0]", "(LAYOUT[6], LAYOUT[7])",
          "((std::mem::size_of::<Q7>(), std::mem::align_of::<Q7>()), (std::mem::size_of::<Q8>(), std::mem::align_of::<Q8>()))"),
        SQE_NO_PADDING,
        T("ring_of_4096_entries", "size_of::<[Sqe; 4096]>()", "std::mem::size_of::<[Sqe; 4096]>()", "196608"),
        T("constructors_keep_fields", "Sqe::write(7, 0xdead0000, 4096, 1 << 40, 77)", "(s.opcode, s.fd, s.addr, s.len, s.off, s.user_data, s.flags, s.file_index)",
          "(OP_WRITE, 7, 0xdead0000, 4096, 1 << 40, 77, 0, 0)", setup="let s = Sqe::write(7, 0xdead0000, 4096, 1 << 40, 77);"),
        T("empty_ring", "SqRing::new(1): pop, then push twice", "(first_pop, ring.push(Sqe::nop(5)), ring.push(Sqe::nop(6)), ring.is_empty())",
          "(None, Ok(()), Err(Sqe::nop(6)), false)", setup="let mut ring = SqRing::new(1);\nlet first_pop = ring.pop();"),
        T("full_across_the_wrap", "SqRing::starting_at(8, u32::MAX - 3): push 8, pop 1, push 1", "(ring.len(), ring.is_full(), ring.head(), ring.tail())",
          "(8, true, u32::MAX - 2, 5)",
          setup="let mut ring = SqRing::starting_at(8, u32::MAX - 3);\nfor u in 0..8 {\n    ring.push(Sqe::nop(u)).unwrap();\n}\nring.pop();\nring.push(Sqe::nop(8)).unwrap();"),
        """
        #[test]
        #[should_panic]
        fn entries_must_be_a_power_of_two() {
            SqRing::new(6);
        }
        """,
        SQE_RANDOM,
    ],
    hints=[("approach", "Sort the fields in your head by alignment, but keep `opcode` first: the 7 bytes after it must be filled exactly by smaller fields (1 + 2 + 4), after which every 8-byte field is aligned."),
           ("rust", "`#[repr(C)]` lays fields out in declaration order, each at the next multiple of its alignment; a `repr(Rust)` struct or tuple is reordered by rustc. `[T; 0]` is zero bytes but keeps `T`'s alignment."),
           ("edge case", "The counters are compared, never reset: `tail.wrapping_sub(head)` is right even when `tail` has wrapped past `u32::MAX` and `head` hasn't. `tail - head` panics there in a debug build.")],
    notes=("""A field sits at the next multiple of its alignment, and the struct's size rounds up to its largest alignment so that `[T; n]` keeps every element aligned; that trailing padding is why `#[repr(C)] { u64, u8 }` is 16 bytes, and 32 in an array of two. `repr(Rust)` structs and tuples are reordered by rustc (`(u8, u64, u8)` is 16, not 24), but `#[repr(C)]` promises declaration order to C, so you pack it yourself: after `opcode` the next 7 bytes are filled by `flags` (1), `ioprio` (2) and `fd` (4), then the `u64`s, then pairs of 4-byte and 2-byte fields. That's the real `struct io_uring_sqe`'s order, and why its header says `BUILD_BUG_ON(sizeof(struct io_uring_sqe) != 64)`. Dropping `repr(C)` also gets 48 bytes, but then rustc places `opcode` where it likes (offset 46 today) and the C side reads garbage. Tools: `pahole` shows holes in C structs; `-Z print-type-sizes` does it for Rust.

The ring is the kernel's: counters never reset, the slot is `counter & mask`, and `tail.wrapping_sub(head)` is the length even across the wrap.""", "O(1) per push / pop", "48 bytes per entry"),
    follow_up="The real io_uring SQE is 64 bytes, and a later kernel added a 128-byte mode. Why keep entries a power of two, and what would a 72-byte entry cost per cache line?",
    source="Linux io_uring (include/uapi/linux/io_uring.h, struct io_uring_sqe), pahole",
    related=["F1", "Y3"],
    rules=dict(types=["size_of", "align_of", "size_of_val", "align_of_val", "offset_of", "Layout"]),
    wrong=dict(
        drops_repr_c=sqe_solution(sqe=SQE_GOOD.replace("#[repr(C)]\n", "")),
        tuple_as_repr_c=sqe_solution(answers=SQE_ANSWERS.replace("(16, 8), (16, 8), (32, 8)", "(24, 8), (16, 8), (32, 8)")),
        plain_subtraction=sqe_solution(ring=sqe_ring("(self.tail - self.head) as usize")),
    ),
))

NICHE_QUIZ = """
//! The quiz is reasoning only: `size_of`, `align_of`, `offset_of!` and `Layout` are off limits in this file.
use std::num::NonZeroU32;

pub type N1 = Option<NonZeroU32>;
pub type N2 = Option<Box<u64>>;
pub type N3 = Option<&'static str>;
pub type N4 = Option<f64>;
pub type N5 = Option<char>;
pub type N6 = Option<Option<bool>>;
pub type N7 = Option<(u8, u32)>;
pub type N8 = Option<Vec<u8>>;

/// `size_of` of `N1` to `N8`, in order.
pub const OPTION_SIZES: [usize; 8] = ANSWERS;
"""

NICHE_ANSWERS = "[4, 8, 16, 16, 4, 1, 12, 24]"

IDX_NAIVE = """
/// An index into `ChainMap`'s entries.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct Idx(u32);

impl Idx {
    /// The largest index an `Idx` holds.
    pub const MAX: usize = u32::MAX as usize - 1;

    /// Panics if `i > Idx::MAX`.
    pub fn new(i: usize) -> Idx {
        assert!(i <= Idx::MAX, "index {i} doesn't fit an Idx");
        Idx(i as u32)
    }

    pub fn index(self) -> usize {
        self.0 as usize
    }
}
"""


def idx_niche(store="!(i as u32)", load="!self.0.get() as usize"):
    return """
/// An index into `ChainMap`'s entries, stored as its bitwise complement in a `NonZeroU32`: every index up to
/// `u32::MAX - 1` has a non-zero complement, and the zero bit pattern is left free for `None`.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct Idx(NonZeroU32);

impl Idx {
    /// The largest index an `Idx` holds.
    pub const MAX: usize = u32::MAX as usize - 1;

    /// Panics if `i > Idx::MAX`.
    pub fn new(i: usize) -> Idx {
        assert!(i <= Idx::MAX, "index {i} doesn't fit an Idx");
        Idx(NonZeroU32::new(STORE).expect("i <= MAX, so the stored value is non-zero"))
    }

    pub fn index(self) -> usize {
        LOAD
    }
}
""".replace("STORE", store).replace("LOAD", load)


CHAIN_HEAD = """
/// One key/value pair and the next entry in its bucket's chain.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Entry {
    pub key: u32,
    pub value: u32,
    pub next: Option<Idx>,
}

/// A hash map with chaining through indices: `heads[b]` is the first entry of bucket `b`, and each entry
/// links to the next. Entries are never removed.
pub struct ChainMap {
    heads: Vec<Option<Idx>>,
    entries: Vec<Entry>,
}

impl ChainMap {
    /// `buckets` is a power of two.
    pub fn with_buckets(buckets: usize) -> ChainMap {
        assert!(buckets.is_power_of_two());
        ChainMap { heads: vec![None; buckets], entries: Vec::new() }
    }

    fn bucket(&self, key: u32) -> usize {
        key.wrapping_mul(0x9E37_79B9).rotate_left(16) as usize & (self.heads.len() - 1)
    }

    pub fn len(&self) -> usize {
        self.entries.len()
    }

    pub fn is_empty(&self) -> bool {
        self.entries.is_empty()
    }
"""

CHAIN_TODO = CHAIN_HEAD + """
    /// Sets `key` to `value` and returns the old value. A new key goes to the front of its bucket's chain.
    pub fn insert(&mut self, key: u32, value: u32) -> Option<u32> {
        todo!()
    }

    pub fn get(&self, key: u32) -> Option<u32> {
        todo!()
    }

    /// The keys in `key`'s bucket, front of the chain first.
    pub fn chain_of(&self, key: u32) -> Vec<u32> {
        todo!()
    }
}
"""

CHAIN_DONE = CHAIN_HEAD + """
    fn find(&self, key: u32) -> Option<usize> {
        let mut cur = self.heads[self.bucket(key)];
        while let Some(i) = cur {
            let e = &self.entries[i.index()];
            if e.key == key {
                return Some(i.index());
            }
            cur = e.next;
        }
        None
    }

    /// Sets `key` to `value` and returns the old value. A new key goes to the front of its bucket's chain.
    pub fn insert(&mut self, key: u32, value: u32) -> Option<u32> {
        if let Some(i) = self.find(key) {
            return Some(std::mem::replace(&mut self.entries[i].value, value));
        }
        let b = self.bucket(key);
        let at = Idx::new(self.entries.len());
        self.entries.push(Entry { key, value, next: self.heads[b] });
        self.heads[b] = Some(at);
        None
    }

    pub fn get(&self, key: u32) -> Option<u32> {
        self.find(key).map(|i| self.entries[i].value)
    }

    /// The keys in `key`'s bucket, front of the chain first.
    pub fn chain_of(&self, key: u32) -> Vec<u32> {
        let mut out = Vec::new();
        let mut cur = self.heads[self.bucket(key)];
        while let Some(i) = cur {
            out.push(self.entries[i.index()].key);
            cur = self.entries[i.index()].next;
        }
        out
    }
}
"""


def niche_solution(answers=NICHE_ANSWERS, idx=None):
    return NICHE_QUIZ.replace("ANSWERS", answers) + (idx or idx_niche()) + CHAIN_DONE


NICHE_RANDOM = """
#[test]
fn random_vs_hashmap() {
    let mut rng = anneal_prelude::Rng::new(8202);
    for _ in 0..200 {
        let buckets = 1usize << rng.below(5);
        let mut map = ChainMap::with_buckets(buckets);
        let mut model = std::collections::HashMap::new();
        let mut log = Vec::new();
        for _ in 0..rng.below(60) {
            let key = rng.int(0, 40) as u32;
            if rng.below(3) < 2 {
                let value = rng.int(0, 999) as u32;
                log.push(format!("insert({key}, {value})"));
                check!(format!("with_buckets({buckets}): {}", log.join(", ")), map.insert(key, value), model.insert(key, value));
            } else {
                log.push(format!("get({key})"));
                check!(format!("with_buckets({buckets}): {}", log.join(", ")), map.get(key), model.get(&key).copied());
            }
        }
        check!(format!("with_buckets({buckets}): {}; len", log.join(", ")), map.len(), model.len());
    }
}
"""

P.append(dict(
    slug="four-byte-optional-index", title="Four-byte optional indices", mode="fix", level="easy", stage="size-it",
    tags=["niche", "NonZeroU32", "Option layout", "newtype index", "chaining"],
    teaches=["A niche is a bit pattern a type never uses; `Option` stores `None` there and costs nothing (`&T`, `Box<T>`, `NonZero*`, `char`, `bool`, `Vec`).",
             "No niche, no free `Option`: `Option<f64>` and `Option<u32>` double, and padding is never a niche.",
             "Give an index type a niche by storing it in a `NonZeroU32` (as `!i` or `i + 1`), like rustc's `newtype_index!`."],
    statement="""
        A compiler's symbol table is a hash map that chains through indices instead of pointers:
        `heads[bucket]` is the first entry of the bucket, and each `Entry` links to the next with
        `next: Option<Idx>`. There are millions of entries, so every byte counts.

        1. **Quiz.** Fill in `OPTION_SIZES`: `size_of` of `N1` to `N8`, from reasoning alone (`size_of`,
           `align_of`, `offset_of!` and `Layout` are off limits in your code).
        2. **Give `Idx` a niche.** Today `Option<Idx>` is 8 bytes and `Entry` 16. Change `Idx`'s
           representation so `Option<Idx>` is **4 bytes** and `Entry` **12**, keeping `Idx::new` and
           `index` (indices `0` to `Idx::MAX`, and `new` panics above that).
        3. **Finish `ChainMap`:** `insert` (returns the old value; a new key goes to the front of its
           chain), `get`, and `chain_of(key)`: the keys in `key`'s bucket, front first.
    """,
    examples=[("size_of::<Option<Idx>>(), size_of::<Entry>()", "4, 12"),
              ("with_buckets(1); insert(1, 10), insert(2, 20), insert(1, 11); chain_of(1)", "[2, 1]")],
    constraints=["buckets is a power of two", "indices 0 ≤ i ≤ Idx::MAX = u32::MAX − 1", "no size_of / align_of / offset_of! / Layout in your code"],
    starter=NICHE_QUIZ.replace("ANSWERS", "[0; 8]") + IDX_NAIVE + CHAIN_TODO,
    solution=niche_solution(),
    visible=[
        T("option_idx_is_free", "size_of::<Idx>(), size_of::<Option<Idx>>()", "(std::mem::size_of::<Idx>(), std::mem::size_of::<Option<Idx>>())", "(4, 4)"),
        T("entry_is_12_bytes", "size_of::<Entry>()", "std::mem::size_of::<Entry>()", "12"),
        T("idx_round_trips", "Idx::new(0), Idx::new(7), Idx::new(Idx::MAX): index()", "(Idx::new(0).index(), Idx::new(7).index(), Idx::new(Idx::MAX).index())", "(0, 7, Idx::MAX)"),
        T("quiz_pointers", "OPTION_SIZES[0..3]: Option<NonZeroU32>, Option<Box<u64>>, Option<&str>", "&OPTION_SIZES[0..3]",
          "&[std::mem::size_of::<N1>(), std::mem::size_of::<N2>(), std::mem::size_of::<N3>()][..]"),
        T("insert_and_get", "with_buckets(8): insert(5, 50), insert(9, 90), insert(5, 55)", "(first, again, map.get(5), map.get(9), map.get(6), map.len())",
          "(None, Some(50), Some(55), Some(90), None, 2)",
          setup="let mut map = ChainMap::with_buckets(8);\nlet first = map.insert(5, 50);\nmap.insert(9, 90);\nlet again = map.insert(5, 55);"),
        T("new_keys_go_first", "with_buckets(1): insert(1, 10), insert(2, 20), insert(3, 30), insert(1, 11)", "map.chain_of(2)", "vec![3, 2, 1]",
          setup="let mut map = ChainMap::with_buckets(1);\nfor (k, v) in [(1, 10), (2, 20), (3, 30), (1, 11)] {\n    map.insert(k, v);\n}"),
    ],
    hidden=[
        T("quiz_no_niche", "OPTION_SIZES[3]: Option<f64>", "OPTION_SIZES[3]", "std::mem::size_of::<N4>()"),
        T("quiz_char_and_nested", "OPTION_SIZES[4..6]: Option<char>, Option<Option<bool>>", "&OPTION_SIZES[4..6]",
          "&[std::mem::size_of::<N5>(), std::mem::size_of::<N6>()][..]"),
        T("quiz_padding_is_not_a_niche", "OPTION_SIZES[6]: Option<(u8, u32)>", "OPTION_SIZES[6]", "std::mem::size_of::<N7>()"),
        T("quiz_vec", "OPTION_SIZES[7]: Option<Vec<u8>>", "OPTION_SIZES[7]", "std::mem::size_of::<N8>()"),
        T("heads_array", "size_of::<[Option<Idx>; 1024]>()", "std::mem::size_of::<[Option<Idx>; 1024]>()", "4096"),
        T("idx_distinct", "Idx::new(0) != Idx::new(1), Some(Idx::new(0)) != None", "(Idx::new(0) != Idx::new(1), Some(Idx::new(0)).is_some(), Idx::new(Idx::MAX - 1).index())",
          "(true, true, Idx::MAX - 1)"),
        """
        #[test]
        #[should_panic]
        fn idx_above_max_panics() {
            Idx::new(Idx::MAX + 1);
        }
        """,
        T("empty_map", "with_buckets(4), nothing inserted", "(map.get(0), map.len(), map.is_empty(), map.chain_of(0))", "(None, 0, true, Vec::<u32>::new())",
          setup="let map = ChainMap::with_buckets(4);"),
        T("zero_and_max_keys", "with_buckets(2): insert(0, 1), insert(u32::MAX, 2)", "(map.get(0), map.get(u32::MAX), map.get(1))", "(Some(1), Some(2), None)",
          setup="let mut map = ChainMap::with_buckets(2);\nmap.insert(0, 1);\nmap.insert(u32::MAX, 2);"),
        T("update_keeps_chain_order", "with_buckets(1): insert 1..=4, then insert(2, 0)", "(map.chain_of(9), map.get(2), map.len())", "(vec![4, 3, 2, 1], Some(0), 4)",
          setup="let mut map = ChainMap::with_buckets(1);\nfor k in 1..=4 {\n    map.insert(k, k * 10);\n}\nmap.insert(2, 0);"),
        """
        #[test]
        fn many_keys_one_bucket_each() {
            let mut map = ChainMap::with_buckets(1024);
            for k in 0..20_000u32 {
                map.insert(k * 7, k);
            }
            let wrong = (0..20_000u32).filter(|&k| map.get(k * 7) != Some(k)).count();
            let misses = (0..20_000u32).filter(|&k| map.get(k * 7 + 1).is_some()).count();
            check!("20000 keys k * 7 in 1024 buckets: wrong lookups, false hits on k * 7 + 1, len", (wrong, misses, map.len()), (0, 0, 20_000));
        }
        """,
        NICHE_RANDOM,
    ],
    hints=[("approach", "`Option<T>` is free when `T` has a bit pattern it never uses. `u32` uses all of them; `NonZeroU32` never uses 0. Map index `i` to a non-zero `u32` and back."),
           ("rust", "`NonZeroU32::new(!(i as u32))` (or `i as u32 + 1`) and `!self.0.get() as usize` back. Both leave exactly one index, `u32::MAX`, unrepresentable, which is why `Idx::MAX` is `u32::MAX - 1`."),
           ("edge case", "Walk a chain with `let mut cur = self.heads[b]; while let Some(i) = cur { ...; cur = entry.next; }`. Padding bytes are never a niche, so `Option<(u8, u32)>` still needs a tag.")],
    notes=("""`Option<T>` costs nothing when `T` has a niche, a bit pattern it can never hold: null for `&T`, `Box<T>` and `Vec`'s pointer, 0 for `NonZero*`, values past `0x10FFFF` for `char`, 2..=255 for `bool` (so `Option<Option<bool>>` is still 1 byte). `u32` and `f64` use every pattern, so `Option<u32>` is 8 bytes and `Option<f64>` 16, and padding doesn't count: `Option<(u8, u32)>` is 12.

rustc's `newtype_index!` gives every compiler index (`BasicBlock`, `Local`, `DefIndex`) a niche by reserving the top values, so `Option<BasicBlock>` stays 4 bytes; in stable Rust the same trick is a `NonZeroU32` holding `!i` or `i + 1`. Here that takes `Entry` from 16 to 12 bytes and every bucket head from 8 to 4: 25% and 50% less memory, for free, in a table with millions of entries. Lua's `ltable.c` chains its hash part the same way, with an integer `next` offset instead of a pointer.""", "O(1) expected per insert / get", "12 bytes per entry + 4 per bucket"),
    follow_up="rustc reserves the top 256 values instead of zero. What does that allow that a `NonZeroU32` with `i + 1` doesn't, and why can't stable code do it the same way?",
    source="rustc's newtype_index! (rustc_index), Lua's ltable.c chaining",
    related=["F3", "S7"],
    rules=dict(types=["size_of", "align_of", "size_of_val", "align_of_val", "offset_of", "Layout"]),
    wrong=dict(
        plus_one_without_minus=niche_solution(idx=idx_niche(store="i as u32 + 1", load="self.0.get() as usize")),
        sentinel_in_u32=niche_solution(idx=IDX_NAIVE),
        padding_as_niche=niche_solution(answers=NICHE_ANSWERS.replace(", 1, 12, 24]", ", 1, 8, 24]")),
    ),
))

TCP_BOOLS = """
use std::ops::{BitAnd, BitOr, BitOrAssign, Not, Sub};

/// The six classic TCP control bits.
#[derive(Clone, Copy, PartialEq, Eq, Hash, Default, Debug)]
pub struct TcpFlags {
    fin: bool,
    syn: bool,
    rst: bool,
    psh: bool,
    ack: bool,
    urg: bool,
}

const NONE: TcpFlags = TcpFlags { fin: false, syn: false, rst: false, psh: false, ack: false, urg: false };

impl TcpFlags {
    pub const FIN: TcpFlags = TcpFlags { fin: true, ..NONE };
    pub const SYN: TcpFlags = TcpFlags { syn: true, ..NONE };
    pub const RST: TcpFlags = TcpFlags { rst: true, ..NONE };
    pub const PSH: TcpFlags = TcpFlags { psh: true, ..NONE };
    pub const ACK: TcpFlags = TcpFlags { ack: true, ..NONE };
    pub const URG: TcpFlags = TcpFlags { urg: true, ..NONE };

    pub fn empty() -> TcpFlags {
        NONE
    }

    pub fn all() -> TcpFlags {
        TcpFlags { fin: true, syn: true, rst: true, psh: true, ack: true, urg: true }
    }

    /// The wire byte: FIN = 0x01, SYN = 0x02, RST = 0x04, PSH = 0x08, ACK = 0x10, URG = 0x20.
    pub fn bits(self) -> u8 {
        [self.fin, self.syn, self.rst, self.psh, self.ack, self.urg].iter().enumerate().map(|(i, &on)| (on as u8) << i).sum()
    }

    /// `None` if any bit outside the six is set.
    pub fn from_bits(bits: u8) -> Option<TcpFlags> {
        if bits >= 0x40 {
            return None;
        }
        Some(TcpFlags::from_bits_truncate(bits))
    }

    /// Drops unknown bits.
    pub fn from_bits_truncate(bits: u8) -> TcpFlags {
        let on = |i: u8| bits & (1 << i) != 0;
        TcpFlags { fin: on(0), syn: on(1), rst: on(2), psh: on(3), ack: on(4), urg: on(5) }
    }

    pub fn is_empty(self) -> bool {
        self == NONE
    }

    /// Every flag in `other` is set in `self`.
    pub fn contains(self, other: TcpFlags) -> bool {
        self.intersection(other) == other
    }

    pub fn intersects(self, other: TcpFlags) -> bool {
        !self.intersection(other).is_empty()
    }

    pub fn union(self, other: TcpFlags) -> TcpFlags {
        TcpFlags::from_bits_truncate(self.bits() | other.bits())
    }

    pub fn intersection(self, other: TcpFlags) -> TcpFlags {
        TcpFlags::from_bits_truncate(self.bits() & other.bits())
    }

    pub fn difference(self, other: TcpFlags) -> TcpFlags {
        TcpFlags::from_bits_truncate(self.bits() & !other.bits())
    }

    /// The flags not in `self`.
    pub fn complement(self) -> TcpFlags {
        TcpFlags::from_bits_truncate(!self.bits())
    }

    /// Whether conntrack accepts this combination (PSH is ignored): SYN, SYN|URG, SYN|ACK, RST, RST|ACK,
    /// FIN|ACK, FIN|ACK|URG, ACK or ACK|URG.
    pub fn is_valid(self) -> bool {
        matches!(self.bits() & !0x08, 0x02 | 0x22 | 0x12 | 0x04 | 0x14 | 0x11 | 0x31 | 0x10 | 0x30)
    }
}

impl BitOr for TcpFlags {
    type Output = TcpFlags;
    fn bitor(self, rhs: TcpFlags) -> TcpFlags {
        self.union(rhs)
    }
}

impl BitOrAssign for TcpFlags {
    fn bitor_assign(&mut self, rhs: TcpFlags) {
        *self = self.union(rhs);
    }
}

impl BitAnd for TcpFlags {
    type Output = TcpFlags;
    fn bitand(self, rhs: TcpFlags) -> TcpFlags {
        self.intersection(rhs)
    }
}

impl Sub for TcpFlags {
    type Output = TcpFlags;
    fn sub(self, rhs: TcpFlags) -> TcpFlags {
        self.difference(rhs)
    }
}

impl Not for TcpFlags {
    type Output = TcpFlags;
    fn not(self) -> TcpFlags {
        self.complement()
    }
}

/// The header fields a TCP stack keeps per queued segment.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SegmentMeta {
    pub seq: u32,
    pub ack: u32,
    pub window: u16,
    pub flags: TcpFlags,
}

// TODO: `pub const VALID: [bool; 64]`, indexed by the flag byte, built at compile time.
"""


def tcp_flags(from_bits="if bits & !TcpFlags::ALL == 0 { Some(TcpFlags(bits)) } else { None }",
              complement="TcpFlags(!self.0 & TcpFlags::ALL)", combos_psh="table[(c | TcpFlags::PSH.0) as usize] = true;"):
    return """
use std::fmt;
use std::ops::{BitAnd, BitOr, BitOrAssign, Not, Sub};

/// The six classic TCP control bits in one byte, exactly as they sit in the header.
#[derive(Clone, Copy, PartialEq, Eq, Hash, Default)]
#[repr(transparent)]
pub struct TcpFlags(u8);

impl TcpFlags {
    pub const FIN: TcpFlags = TcpFlags(0x01);
    pub const SYN: TcpFlags = TcpFlags(0x02);
    pub const RST: TcpFlags = TcpFlags(0x04);
    pub const PSH: TcpFlags = TcpFlags(0x08);
    pub const ACK: TcpFlags = TcpFlags(0x10);
    pub const URG: TcpFlags = TcpFlags(0x20);
    const ALL: u8 = 0x3F;
    const NAMES: [(TcpFlags, &'static str); 6] =
        [(TcpFlags::FIN, "FIN"), (TcpFlags::SYN, "SYN"), (TcpFlags::RST, "RST"), (TcpFlags::PSH, "PSH"), (TcpFlags::ACK, "ACK"), (TcpFlags::URG, "URG")];

    pub const fn empty() -> TcpFlags {
        TcpFlags(0)
    }

    pub const fn all() -> TcpFlags {
        TcpFlags(TcpFlags::ALL)
    }

    /// The wire byte: FIN = 0x01, SYN = 0x02, RST = 0x04, PSH = 0x08, ACK = 0x10, URG = 0x20.
    pub const fn bits(self) -> u8 {
        self.0
    }

    /// `None` if any bit outside the six is set.
    pub const fn from_bits(bits: u8) -> Option<TcpFlags> {
        FROM_BITS
    }

    /// Drops unknown bits.
    pub const fn from_bits_truncate(bits: u8) -> TcpFlags {
        TcpFlags(bits & TcpFlags::ALL)
    }

    pub const fn is_empty(self) -> bool {
        self.0 == 0
    }

    /// Every flag in `other` is set in `self`.
    pub const fn contains(self, other: TcpFlags) -> bool {
        self.0 & other.0 == other.0
    }

    pub const fn intersects(self, other: TcpFlags) -> bool {
        self.0 & other.0 != 0
    }

    pub const fn union(self, other: TcpFlags) -> TcpFlags {
        TcpFlags(self.0 | other.0)
    }

    pub const fn intersection(self, other: TcpFlags) -> TcpFlags {
        TcpFlags(self.0 & other.0)
    }

    pub const fn difference(self, other: TcpFlags) -> TcpFlags {
        TcpFlags(self.0 & !other.0)
    }

    /// The flags not in `self`: masked to the six, or `!SYN` would carry two bits that aren't flags.
    pub const fn complement(self) -> TcpFlags {
        COMPLEMENT
    }

    /// Whether conntrack accepts this combination (PSH is ignored).
    pub const fn is_valid(self) -> bool {
        VALID[self.0 as usize]
    }
}

/// The combinations netfilter's `tcp_valid_flags` accepts, before PSH is added back.
const VALID_COMBOS: [u8; 9] = [0x02, 0x22, 0x12, 0x04, 0x14, 0x11, 0x31, 0x10, 0x30];

/// Indexed by the flag byte, built at compile time: `const fn` can't use `for` or iterators, so `while`.
pub const VALID: [bool; 64] = {
    let mut table = [false; 64];
    let mut i = 0;
    while i < VALID_COMBOS.len() {
        let c = VALID_COMBOS[i];
        table[c as usize] = true;
        COMBOS_PSH
        i += 1;
    }
    table
};

impl BitOr for TcpFlags {
    type Output = TcpFlags;
    fn bitor(self, rhs: TcpFlags) -> TcpFlags {
        self.union(rhs)
    }
}

impl BitOrAssign for TcpFlags {
    fn bitor_assign(&mut self, rhs: TcpFlags) {
        self.0 |= rhs.0;
    }
}

impl BitAnd for TcpFlags {
    type Output = TcpFlags;
    fn bitand(self, rhs: TcpFlags) -> TcpFlags {
        self.intersection(rhs)
    }
}

impl Sub for TcpFlags {
    type Output = TcpFlags;
    fn sub(self, rhs: TcpFlags) -> TcpFlags {
        self.difference(rhs)
    }
}

impl Not for TcpFlags {
    type Output = TcpFlags;
    fn not(self) -> TcpFlags {
        self.complement()
    }
}

/// `TcpFlags(SYN | ACK)`, `TcpFlags(empty)`.
impl fmt::Debug for TcpFlags {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        if self.is_empty() {
            return write!(f, "TcpFlags(empty)");
        }
        let names: Vec<&str> = TcpFlags::NAMES.iter().filter(|(flag, _)| self.contains(*flag)).map(|(_, name)| *name).collect();
        write!(f, "TcpFlags({})", names.join(" | "))
    }
}

/// The header fields a TCP stack keeps per queued segment.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SegmentMeta {
    pub seq: u32,
    pub ack: u32,
    pub window: u16,
    pub flags: TcpFlags,
}
""".replace("FROM_BITS", from_bits).replace("COMPLEMENT", complement).replace("COMBOS_PSH", combos_psh)


TCP_RANDOM = """
#[test]
fn random_vs_byte_model() {
    let mut rng = anneal_prelude::Rng::new(8203);
    let valid = [0x02u8, 0x22, 0x12, 0x04, 0x14, 0x11, 0x31, 0x10, 0x30];
    for _ in 0..400 {
        let raw = rng.int(0, 255) as u8;
        check!(format!("from_bits({raw:#04x})"), TcpFlags::from_bits(raw).map(|f| f.bits()), if raw < 0x40 { Some(raw) } else { None });
        check!(format!("from_bits_truncate({raw:#04x})"), TcpFlags::from_bits_truncate(raw).bits(), raw & 0x3F);
        let (a, b) = (raw & 0x3F, rng.int(0, 63) as u8);
        let (fa, fb) = (TcpFlags::from_bits(a).unwrap(), TcpFlags::from_bits(b).unwrap());
        check!(format!("{a:#04x} op {b:#04x}: |, &, -, !a"), ((fa | fb).bits(), (fa & fb).bits(), (fa - fb).bits(), (!fa).bits()),
               (a | b, a & b, a & !b, !a & 0x3F));
        check!(format!("{a:#04x} contains / intersects {b:#04x}"), (fa.contains(fb), fa.intersects(fb)), (a & b == b, a & b != 0));
        check!(format!("{a:#04x}.is_valid()"), (fa.is_valid(), VALID[a as usize]), (valid.contains(&(a & !0x08)), valid.contains(&(a & !0x08))));
    }
}
"""

P.append(dict(
    slug="tcp-flags-in-a-byte", title="TCP flags in one byte", mode="fix", level="easy", stage="size-it",
    tags=["bitflags", "const fn", "repr(transparent)", "operator traits", "lookup table"],
    teaches=["Six `bool`s are six bytes; six bits are one. A `#[repr(transparent)]` newtype over `u8` keeps the wire byte's layout.",
             "A `const fn` API lets flag sets be built in `const` items and match arms; `const fn` bodies loop with `while`, not `for`.",
             "`Not` on a flag set must mask to the known bits, and `from_bits` must reject unknown ones."],
    statement="""
        A user-space TCP stack keeps a `SegmentMeta` for every queued segment, and its `TcpFlags` is six `bool`s:
        6 bytes where the wire uses one, which makes `SegmentMeta` 16 bytes instead of 12. Its methods also
        can't be used in `const` items, and conntrack wants a lookup table built at compile time.

        Rewrite `TcpFlags` as **one byte** (`#[repr(transparent)]` over `u8`, bit values as on the wire:
        FIN = 0x01, SYN = 0x02, RST = 0x04, PSH = 0x08, ACK = 0x10, URG = 0x20), keeping the API, and:

        - make every inherent method a `const fn`;
        - add `pub const VALID: [bool; 64]`, indexed by the flag byte and computed at compile time: the
          combinations netfilter accepts, ignoring PSH, are SYN, SYN|URG, SYN|ACK, RST, RST|ACK, FIN|ACK,
          FIN|ACK|URG, ACK and ACK|URG; `is_valid` reads it;
        - `Debug` prints set flags in bit order: `TcpFlags(SYN | ACK)`, or `TcpFlags(empty)`.

        `!flags` and `complement` stay within the six flags; `from_bits` rejects any other bit.
    """,
    examples=[("size_of::<TcpFlags>(), size_of::<SegmentMeta>()", "1, 12"),
              ("format!(\"{:?}\", TcpFlags::SYN | TcpFlags::ACK)", "\"TcpFlags(SYN | ACK)\""),
              ("(!TcpFlags::SYN).bits()", "0x3D")],
    constraints=["no bitflags crate", "every inherent method is a const fn", "VALID is a const item"],
    starter=TCP_BOOLS,
    solution=tcp_flags(),
    visible=[
        T("one_byte", "size_of::<TcpFlags>(), size_of::<SegmentMeta>()", "(std::mem::size_of::<TcpFlags>(), std::mem::size_of::<SegmentMeta>())", "(1, 12)"),
        """
        #[test]
        fn usable_in_const_items() {
            const SYN_ACK: TcpFlags = TcpFlags::SYN.union(TcpFlags::ACK);
            const BARE_SYN: TcpFlags = SYN_ACK.difference(TcpFlags::ACK);
            const CHECKS: [bool; 3] = [SYN_ACK.contains(TcpFlags::SYN), BARE_SYN.is_valid(), TcpFlags::SYN.union(TcpFlags::FIN).is_valid()];
            check!("SYN_ACK.bits(), BARE_SYN.bits(), [SYN_ACK ⊇ SYN, SYN valid, SYN|FIN valid]", (SYN_ACK.bits(), BARE_SYN.bits(), CHECKS), (0x12, 0x02, [true, true, false]));
        }
        """,
        T("debug_lists_flags", "format!(\"{:?}\") of SYN | ACK and of empty()", 'format!("{:?} {:?}", TcpFlags::ACK | TcpFlags::SYN, TcpFlags::empty())',
          '"TcpFlags(SYN | ACK) TcpFlags(empty)"'),
        T("not_stays_in_six_bits", "(!TcpFlags::SYN).bits()", "(!TcpFlags::SYN).bits()", "0x3D"),
        T("from_bits_rejects_unknown", "from_bits(0x12), from_bits(0x40), from_bits_truncate(0xFF)", "(TcpFlags::from_bits(0x12), TcpFlags::from_bits(0x40), TcpFlags::from_bits_truncate(0xFF))",
          "(Some(TcpFlags::SYN | TcpFlags::ACK), None, TcpFlags::all())"),
        T("valid_table", "VALID[SYN], VALID[SYN | FIN], VALID[ACK | PSH]", "(VALID[0x02], VALID[0x03], VALID[0x18])", "(true, false, true)"),
    ],
    hidden=[
        T("valid_count", "number of true entries in VALID", "VALID.iter().filter(|&&v| v).count()", "18"),
        T("valid_is_a_const", "a const indexed into VALID", "X", "true", setup="const X: bool = VALID[0x31] && !VALID[0x00] && TcpFlags::RST.union(TcpFlags::ACK).is_valid();"),
        T("debug_all", "format!(\"{:?}\", TcpFlags::all())", 'format!("{:?}", TcpFlags::all())', '"TcpFlags(FIN | SYN | RST | PSH | ACK | URG)"'),
        T("contains_empty", "SYN.contains(empty), SYN.intersects(empty), empty().contains(empty)",
          "(TcpFlags::SYN.contains(TcpFlags::empty()), TcpFlags::SYN.intersects(TcpFlags::empty()), TcpFlags::empty().contains(TcpFlags::empty()))", "(true, false, true)"),
        T("complement_of_all_and_empty", "(!all()).bits(), (!empty()) == all()", "((!TcpFlags::all()).bits(), !TcpFlags::empty() == TcpFlags::all(), TcpFlags::FIN.complement().bits())", "(0, true, 0x3E)"),
        T("or_assign_and_sub", "f = SYN; f |= ACK; f |= PSH; then f - PSH", "(f.bits(), (f - TcpFlags::PSH).bits(), f.is_valid())", "(0x1A, 0x12, true)",
          setup="let mut f = TcpFlags::SYN;\nf |= TcpFlags::ACK;\nf |= TcpFlags::PSH;"),
        T("default_is_empty", "TcpFlags::default()", "(TcpFlags::default().is_empty(), TcpFlags::default().bits())", "(true, 0)"),
        T("layout_in_arrays", "size_of::<[TcpFlags; 64]>(), size_of::<Option<TcpFlags>>(), align_of::<SegmentMeta>()",
          "(std::mem::size_of::<[TcpFlags; 64]>(), std::mem::size_of::<Option<TcpFlags>>(), std::mem::align_of::<SegmentMeta>())", "(64, 2, 4)"),
        T("from_bits_edges", "from_bits(0x3F), from_bits(0x80), from_bits(0)", "(TcpFlags::from_bits(0x3F), TcpFlags::from_bits(0x80), TcpFlags::from_bits(0))",
          "(Some(TcpFlags::all()), None, Some(TcpFlags::empty()))"),
        T("match_on_consts", "classify SYN | ACK with a match on const flag sets", "kind", '"syn-ack"',
          setup='const SYN_ACK: TcpFlags = TcpFlags::SYN.union(TcpFlags::ACK);\nlet kind = match TcpFlags::ACK | TcpFlags::SYN {\n    TcpFlags::SYN => "syn",\n    SYN_ACK => "syn-ack",\n    _ => "other",\n};'),
        TCP_RANDOM,
    ],
    hints=[("approach", "One `u8`, one bit per flag. Every set operation is a single bitwise op; `contains` is `self & other == other`."),
           ("rust", "`#[repr(transparent)] pub struct TcpFlags(u8);` and `pub const fn union(self, other: Self) -> Self`. Build the table in a `const` block: `let mut t = [false; 64]; let mut i = 0; while i < N { ...; i += 1 } t`."),
           ("edge case", "`!` on the byte flips the two unused high bits too: mask with `0x3F`. `from_bits(0x40)` is `None`, and PSH is ignored by validity, so both `x` and `x | PSH` are valid.")],
    notes=("""Six `bool`s cost six bytes because each needs its own address; the six flags fit in one byte, the one on the wire, and `#[repr(transparent)]` guarantees the newtype has exactly `u8`'s layout (it can be passed to C or cast from a header byte). `SegmentMeta` drops from 16 to 12 bytes. Making the API `const fn` means flag sets can be `const` items, which also makes them usable as `match` patterns (the type derives `PartialEq, Eq`), and lets the validity table be computed by the compiler: `const fn` has no `for` or iterators, so the builder uses `while`. The traps are the ones the bitflags crate handles: `!` must mask to the known bits, and `from_bits` must reject unknown ones (`from_bits_truncate` drops them).

Netfilter's conntrack keeps exactly this table (`tcp_valid_flags[]` in `nf_conntrack_proto_tcp.c`), indexed by the flag byte with PSH masked out, and drops segments with invalid combinations such as SYN|FIN.

Syntax to remember: `impl BitOr for TcpFlags { type Output = Self; fn bitor(self, rhs: Self) -> Self }`, `impl BitOrAssign for TcpFlags { fn bitor_assign(&mut self, rhs: Self) }`.""", "O(1) per operation", "1 byte per flag set; a 64-byte table"),
    follow_up="The real TCP header has ECE and CWR too (8 bits). What changes in `from_bits`, `!` and `VALID`, and how would you add a flag later without breaking callers that match on `TcpFlags`?",
    source="Linux netfilter (nf_conntrack_proto_tcp.c, tcp_valid_flags), the bitflags crate",
    related=["L5", "F5"],
    wrong=dict(
        not_masked=tcp_flags(complement="TcpFlags(!self.0)"),
        from_bits_keeps_unknown=tcp_flags(from_bits="Some(TcpFlags(bits))"),
        psh_not_ignored=tcp_flags(combos_psh=""),
    ),
))

STAGES = [
    ("size-it", "Size it", "easy"),
]

for p in P:
    if p.get("mode", "write") == "write":
        p.pop("rules", None)

if __name__ == "__main__":
    n = write_track("f2-data-layout", "F2", "Data layout", "F", "sde3", 2,
                    "How many bytes a value takes and where they sit: padding, niches, enum tags, fat and thin pointers, inline storage, packed records, and laying data out for the cache.",
                    STAGES, P)
    print("F2", n)
