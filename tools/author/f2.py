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

# ---------------------------------------------------------------- pick the representation (medium)

EVENT_HEAD = """
use std::collections::VecDeque;

/// The largest payload a packet event carries.
pub const MTU: usize = 1500;
"""

EVENT_INLINE = EVENT_HEAD + """
/// What the network thread hands the connection thread: millions a second, through a queue.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Event {
    Tick(u64),
    Ack { conn: u32, seq: u32 },
    Close(u32),
    Packet { conn: u32, len: u16, data: [u8; MTU] },
}

impl Event {
    /// A packet event for `conn` carrying `payload`. Panics if `payload` is longer than `MTU`.
    pub fn packet(conn: u32, payload: &[u8]) -> Event {
        assert!(payload.len() <= MTU, "payload of {} bytes is over the MTU", payload.len());
        let mut data = [0; MTU];
        data[..payload.len()].copy_from_slice(payload);
        Event::Packet { conn, len: payload.len() as u16, data }
    }

    /// The connection an event is about, if any.
    pub fn conn(&self) -> Option<u32> {
        match self {
            Event::Tick(_) => None,
            Event::Ack { conn, .. } | Event::Packet { conn, .. } => Some(*conn),
            Event::Close(conn) => Some(*conn),
        }
    }

    pub fn payload(&self) -> Option<&[u8]> {
        match self {
            Event::Packet { len, data, .. } => Some(&data[..*len as usize]),
            _ => None,
        }
    }
}
"""

PACKET_STRUCT = """
/// A packet's payload, kept out of line: most events are ticks and acks, and they shouldn't pay for it.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Packet {
    conn: u32,
    len: u16,
    data: [u8; MTU],
}
"""

PACKET_CTOR = """        let mut packet = Box::new(Packet { conn, len: payload.len() as u16, data: [0; MTU] });
        packet.data[..payload.len()].copy_from_slice(payload);
        Event::Packet(packet)"""


def event_boxed(packet_ty="Box<Packet>", packet_struct=PACKET_STRUCT, ctor=PACKET_CTOR, conn_arm="Event::Packet(p) => Some(p.conn),",
                payload_arm="Event::Packet(p) => Some(&p.data[..p.len as usize]),"):
    return EVENT_HEAD + packet_struct + """
/// What the network thread hands the connection thread: millions a second, through a queue.
/// 16 bytes: a one-byte tag, padding, and 8 bytes of payload (a `u64`, two `u32`s, or a thin `Box`).
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Event {
    Tick(u64),
    Ack { conn: u32, seq: u32 },
    Close(u32),
    Packet(PACKET_TY),
}

impl Event {
    /// A packet event for `conn` carrying `payload`. Panics if `payload` is longer than `MTU`.
    pub fn packet(conn: u32, payload: &[u8]) -> Event {
        assert!(payload.len() <= MTU, "payload of {} bytes is over the MTU", payload.len());
CTOR
    }

    /// The connection an event is about, if any.
    pub fn conn(&self) -> Option<u32> {
        match self {
            Event::Tick(_) => None,
            Event::Ack { conn, .. } => Some(*conn),
            Event::Close(conn) => Some(*conn),
            CONN_ARM
        }
    }

    pub fn payload(&self) -> Option<&[u8]> {
        match self {
            PAYLOAD_ARM
            _ => None,
        }
    }
}
""".replace("PACKET_TY", packet_ty).replace("CTOR", ctor).replace("CONN_ARM", conn_arm).replace("PAYLOAD_ARM", payload_arm)


EVENT_DRAIN = """
/// What the connection thread saw in one batch.
#[derive(Debug, Default, PartialEq, Eq)]
pub struct Summary {
    pub last_tick: u64,
    pub acks: usize,
    pub packets: usize,
    pub bytes: usize,
    pub closed: Vec<u32>,
}

/// Empties `queue`, oldest first.
pub fn drain(queue: &mut VecDeque<Event>) -> Summary {
    let mut s = Summary::default();
    while let Some(ev) = queue.pop_front() {
        match &ev {
            Event::Tick(t) => s.last_tick = *t,
            Event::Ack { .. } => s.acks += 1,
            Event::Close(conn) => s.closed.push(*conn),
            _ => {
                s.packets += 1;
                s.bytes += ev.payload().map_or(0, <[u8]>::len);
            }
        }
    }
    s
}
"""

EVENT_RANDOM = """
#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(8204);
    for _ in 0..150 {
        let mut queue = std::collections::VecDeque::new();
        let (mut last_tick, mut acks, mut packets, mut bytes, mut closed) = (0, 0, 0, 0, Vec::new());
        let mut log = Vec::new();
        for _ in 0..rng.below(12) {
            let conn = rng.int(0, 9) as u32;
            let ev = match rng.below(4) {
                0 => {
                    last_tick = rng.int(0, 1_000_000) as u64;
                    log.push(format!("Tick({last_tick})"));
                    check!(format!("Tick({last_tick}).conn()"), Event::Tick(last_tick).conn(), None);
                    Event::Tick(last_tick)
                }
                1 => {
                    acks += 1;
                    log.push(format!("Ack {{ conn: {conn}, .. }}"));
                    Event::Ack { conn, seq: rng.int(0, 99) as u32 }
                }
                2 => {
                    closed.push(conn);
                    log.push(format!("Close({conn})"));
                    Event::Close(conn)
                }
                _ => {
                    let n = if rng.bool() { rng.below(20) } else { rng.below(MTU + 1) };
                    let data: Vec<u8> = rng.vec(n, 0, 255);
                    let ev = Event::packet(conn, &data);
                    log.push(format!("packet({conn}, {n} bytes)"));
                    check!(format!("packet({conn}, {n} bytes): conn, payload, clone == original"), (ev.conn(), ev.payload() == Some(&data[..]), ev.clone() == ev), (Some(conn), true, true));
                    packets += 1;
                    bytes += n;
                    ev
                }
            };
            queue.push_back(ev);
        }
        let want = Summary { last_tick, acks, packets, bytes, closed };
        check!(format!("drain [{}]", log.join(", ")), drain(&mut queue), want);
    }
}
"""

P.append(dict(
    slug="box-the-large-variant", title="Box the large variant", mode="fix", level="medium", stage="pick-the-representation",
    tags=["enum layout", "large_enum_variant", "Box", "thin vs fat pointers", "allocation"],
    teaches=["An enum is as big as its largest variant plus the tag, so one rare 1.5 KB variant makes every `Tick` 1.5 KB.",
             "Box the large, rare variant: the enum shrinks to the size of its common variants and only packets allocate.",
             "`Box<T>` is a thin 8-byte pointer; `Box<[u8]>` and `Vec<u8>` carry a length (16 and 24 bytes), which here decides whether the enum is 16 bytes or 24."],
    statement="""
        A network thread feeds a connection thread through a `VecDeque<Event>`. Almost every event is a `Tick`,
        an `Ack` or a `Close`, but `Event::Packet` carries its 1500-byte buffer inline, so every event is
        1512 bytes and the queue moves 1.5 KB per tick (clippy's `large_enum_variant` warns about exactly this).

        Make `Event` **16 bytes** (and `Option<Event>` too), keeping the public API: `Event::Tick(t)`,
        `Event::Ack { conn, seq }` and `Event::Close(conn)` are still built directly, packets through
        `Event::packet(conn, payload)`, and `conn`, `payload` and `drain` behave as before.

        Allocation budget: building a packet event makes **exactly one** allocation; ticks, acks and closes
        make none.
    """,
    examples=[("size_of::<Event>(), size_of::<Option<Event>>()", "16, 16"),
              ("allocations for Event::packet(7, b\"hello\")", "1")],
    constraints=["payloads are 0 to 1500 bytes", "the enum's small variants keep their shape"],
    starter=EVENT_INLINE + EVENT_DRAIN,
    solution=event_boxed() + EVENT_DRAIN,
    visible=[
        T("event_is_16_bytes", "size_of::<Event>(), size_of::<Option<Event>>()", "(std::mem::size_of::<Event>(), std::mem::size_of::<Option<Event>>())", "(16, 16)"),
        T("packet_allocates_once", "allocations for Event::packet(7, b\"hello\")", "(n.count, ev.payload(), ev.conn())", '(1, Some(&b"hello"[..]), Some(7))',
          setup='let (ev, n) = anneal_prelude::allocs(|| Event::packet(7, b"hello"));'),
        T("small_events_dont_allocate", "allocations for Tick(1), Ack { 2, 3 }, Close(4), pushed into a queue with room", "(n.count, q.len())", "(0, 3)",
          setup="let mut q = std::collections::VecDeque::with_capacity(8);\nlet (_, n) = anneal_prelude::allocs(|| {\n    q.push_back(Event::Tick(1));\n    q.push_back(Event::Ack { conn: 2, seq: 3 });\n    q.push_back(Event::Close(4));\n});"),
        T("accessors", "conn() and payload() of Tick(9), Ack { conn: 2, seq: 5 }, Close(3)",
          "(Event::Tick(9).conn(), Event::Ack { conn: 2, seq: 5 }.conn(), Event::Close(3).conn(), Event::Close(3).payload())", "(None, Some(2), Some(3), None)"),
        T("drain_in_order", "drain [Tick(5), packet(1, [1, 2, 3]), Ack { 1, 9 }, Close(1), Tick(8)]", "(drain(&mut q), q.is_empty())",
          "(Summary { last_tick: 8, acks: 1, packets: 1, bytes: 3, closed: vec![1] }, true)",
          setup="let mut q: std::collections::VecDeque<Event> = vec![Event::Tick(5), Event::packet(1, &[1, 2, 3]), Event::Ack { conn: 1, seq: 9 }, Event::Close(1), Event::Tick(8)].into();"),
    ],
    hidden=[
        T("empty_payload", "Event::packet(3, &[])", "(ev.payload().map(|p| p.len()), ev.conn(), n.count)", "(Some(0), Some(3), 1)",
          setup="let (ev, n) = anneal_prelude::allocs(|| Event::packet(3, &[]));"),
        T("full_mtu_payload", "Event::packet(4, 1500 bytes of 0xAB)", "(ev.payload() == Some(&data[..]), n.count)", "(true, 1)",
          setup="let data = vec![0xABu8; MTU];\nlet (ev, n) = anneal_prelude::allocs(|| Event::packet(4, &data));"),
        """
        #[test]
        #[should_panic]
        fn over_mtu_panics() {
            Event::packet(1, &[0; MTU + 1]);
        }
        """,
        T("clone_small_is_free", "allocations to clone Tick(1) and Ack { 1, 2 }", "n.count", "0",
          setup="let (t, a) = (Event::Tick(1), Event::Ack { conn: 1, seq: 2 });\nlet (_, n) = anneal_prelude::allocs(|| (t.clone(), a.clone()));"),
        T("clone_packet_copies", "clone of packet(2, [9, 9]): equal, one allocation", "(copy == ev, copy.payload(), n.count)", "(true, Some(&[9u8, 9][..]), 1)",
          setup="let ev = Event::packet(2, &[9, 9]);\nlet (copy, n) = anneal_prelude::allocs(|| ev.clone());"),
        T("queue_of_a_million_events", "bytes requested by VecDeque::<Event>::with_capacity(1_000_000)", "n.bytes", "16_000_000",
          setup="let (q, n) = anneal_prelude::allocs(|| std::collections::VecDeque::<Event>::with_capacity(1_000_000));\ndrop(q);"),
        T("equality", "packet(1, [1]) vs packet(1, [1]), packet(2, [1]), packet(1, [2])",
          "(Event::packet(1, &[1]) == Event::packet(1, &[1]), Event::packet(1, &[1]) == Event::packet(2, &[1]), Event::packet(1, &[1]) == Event::packet(1, &[2]))", "(true, false, false)"),
        T("drain_empty", "drain of an empty queue", "drain(&mut std::collections::VecDeque::new())", "Summary::default()"),
        T("drain_bytes_add_up", "drain [packet(1, 1000 B), packet(2, 1500 B), Close(2), Close(1)]", "drain(&mut q)",
          "Summary { last_tick: 0, acks: 0, packets: 2, bytes: 2500, closed: vec![2, 1] }",
          setup="let mut q: std::collections::VecDeque<Event> = vec![Event::packet(1, &[0; 1000]), Event::packet(2, &[1; 1500]), Event::Close(2), Event::Close(1)].into();"),
        EVENT_RANDOM,
    ],
    hints=[("approach", "The enum is as large as its largest variant. Move the packet's buffer behind a pointer so that variant is 8 bytes, the same as `Tick(u64)`."),
           ("rust", "`Packet(Box<Packet>)` with `struct Packet { conn, len, data: [u8; MTU] }` is a thin pointer. `Box<[u8]>` is a fat pointer (pointer + length, 16 bytes), which with the tag makes the enum 24; `Box<Vec<u8>>` is thin but allocates twice."),
           ("edge case", "`Option<Event>` stays 16 bytes on its own: the tag byte has unused values, and `None` takes one of them.")],
    notes=("""An enum's size is its largest variant plus the tag, rounded to its alignment, so one rare 1506-byte variant makes every tick 1512 bytes, and a queue of a million events 1.5 GB. Boxing the rare variant makes it a thin 8-byte pointer: the enum becomes a tag byte, padding and 8 bytes of payload (`u64`, two `u32`s or the `Box`), 16 in total, and a million-event queue is 16 MB. Only packets allocate, once each. The payload representation matters: `Box<[u8]>` is a fat pointer (16 bytes, so the enum is 24), `Vec<u8>` is 24 (enum 32), and `Box<Vec<u8>>` is thin but costs two allocations per packet. `Option<Event>` stays 16 bytes because the tag byte has spare values.

This is clippy's `large_enum_variant` lint, and why rustc guards its hot enums with `static_assert_size!` (`ast::Expr`, `mir::Statement`): a variant added carelessly would grow every value.""", "O(1) per event; one allocation per packet", "16 bytes per queued event + 1508 per packet"),
    follow_up="Packets arrive in bursts of thousands. What would you use instead of one `Box` per packet, and what does `Event` hold then?",
    source="clippy large_enum_variant; rustc's static_assert_size! on ast::Expr and mir::Statement",
    related=["S7", "F3"],
    perf=dict(allocs=True),
    wrong=dict(
        boxed_slice=event_boxed(packet_ty="u32, Box<[u8]>", packet_struct="",
                                ctor="        Event::Packet(conn, payload.into())", conn_arm="Event::Packet(conn, _) => Some(*conn),", payload_arm="Event::Packet(_, data) => Some(data),") + EVENT_DRAIN,
        box_of_vec=event_boxed(packet_ty="Box<(u32, Vec<u8>)>", packet_struct="",
                               ctor="        Event::Packet(Box::new((conn, payload.to_vec())))", conn_arm="Event::Packet(p) => Some(p.0),", payload_arm="Event::Packet(p) => Some(&p.1),") + EVENT_DRAIN,
    ),
))

HEAD_NAIVE = """
use std::collections::HashSet;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub struct SeriesId(pub u32);

/// A series' labels as handed to the query engine. They must outlive the `Head` (compaction replaces it).
pub type Labels = Vec<(String, String)>;

/// One time series in the head block.
pub struct Series {
    name: String,
    labels: Labels,
    samples: Vec<(i64, f64)>,
}

/// A TSDB head block: every series written since the last compaction.
pub struct Head {
    series: Vec<Series>,
}

impl Head {
    /// Room for `series` series and `symbols` distinct strings, reserved up front.
    pub fn with_capacity(series: usize, symbols: usize) -> Head {
        let _ = symbols;
        Head { series: Vec::with_capacity(series) }
    }

    /// Adds a series. `labels` arrive sorted by name, as Prometheus keeps them.
    pub fn add_series(&mut self, name: &str, labels: &[(&str, &str)]) -> SeriesId {
        let id = SeriesId(self.series.len() as u32);
        let labels = labels.iter().map(|&(k, v)| (k.to_string(), v.to_string())).collect();
        self.series.push(Series { name: name.to_string(), labels, samples: Vec::new() });
        id
    }

    pub fn append(&mut self, id: SeriesId, t: i64, v: f64) {
        self.series[id.0 as usize].samples.push((t, v));
    }

    pub fn name(&self, id: SeriesId) -> &str {
        &self.series[id.0 as usize].name
    }

    pub fn label(&self, id: SeriesId, key: &str) -> Option<&str> {
        let labels = &self.series[id.0 as usize].labels;
        labels.binary_search_by(|(k, _)| k.as_str().cmp(key)).ok().map(|i| labels[i].1.as_str())
    }

    pub fn samples(&self, id: SeriesId) -> &[(i64, f64)] {
        &self.series[id.0 as usize].samples
    }

    /// The labels of `id`, for the query engine to keep.
    pub fn labels_of(&self, id: SeriesId) -> Labels {
        self.series[id.0 as usize].labels.clone()
    }

    /// Every series with label `key` = `value`, in id order.
    pub fn select(&self, key: &str, value: &str) -> Vec<SeriesId> {
        (0..self.series.len() as u32).map(SeriesId).filter(|&id| self.label(id, key) == Some(value)).collect()
    }

    /// How many distinct strings (metric names, label names and values) the head holds.
    pub fn symbols(&self) -> usize {
        let mut seen = HashSet::new();
        for s in &self.series {
            seen.insert(s.name.as_str());
            for (k, v) in &s.labels {
                seen.insert(k.as_str());
                seen.insert(v.as_str());
            }
        }
        seen.len()
    }
}
"""

HEAD_TAIL = """
    pub fn append(&mut self, id: SeriesId, t: i64, v: f64) {
        self.series[id.0 as usize].samples.push((t, v));
    }

    pub fn name(&self, id: SeriesId) -> &str {
        &self.series[id.0 as usize].name
    }

    pub fn label(&self, id: SeriesId, key: &str) -> Option<&str> {
        let labels = &self.series[id.0 as usize].labels;
        labels.binary_search_by(|(k, _)| k[..].cmp(key)).ok().map(|i| &labels[i].1[..])
    }

    pub fn samples(&self, id: SeriesId) -> &[(i64, f64)] {
        &self.series[id.0 as usize].samples
    }

    /// The labels of `id`, for the query engine to keep: a reference count bump, no copy.
    pub fn labels_of(&self, id: SeriesId) -> Labels {
        LABELS_OF
    }

    /// Every series with label `key` = `value`, in id order.
    pub fn select(&self, key: &str, value: &str) -> Vec<SeriesId> {
        (0..self.series.len() as u32).map(SeriesId).filter(|&id| self.label(id, key) == Some(value)).collect()
    }

    /// How many distinct strings (metric names, label names and values) the head holds.
    pub fn symbols(&self) -> usize {
        self.symbols.len()
    }
}
"""


def head_shared(labels_ty="Arc<[(Arc<str>, Arc<str>)]>", sym_ty="Arc<str>", intern_body="""        if let Some(sym) = symbols.get(s) {
            return Arc::clone(sym);
        }
        let sym: Arc<str> = Arc::from(s);
        symbols.insert(Arc::clone(&sym));
        sym""", build_labels="labels.iter().map(|&(k, v)| (Head::intern(symbols, k), Head::intern(symbols, v))).collect()",
                labels_of="Arc::clone(&self.series[id.0 as usize].labels)"):
    return """
use std::collections::HashSet;
use std::sync::Arc;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub struct SeriesId(pub u32);

/// A series' labels as handed to the query engine. They must outlive the `Head` (compaction replaces it).
/// Frozen at creation, so a shared slice: one allocation holding the count and the pairs, cloned by a
/// reference count bump.
pub type Labels = LABELS_TY;

/// One time series in the head block. `name` is shared by every series of the metric; `samples` is the
/// only part that grows, so it's the only `Vec`.
pub struct Series {
    name: SYM,
    labels: Labels,
    samples: Vec<(i64, f64)>,
}

/// A TSDB head block: every series written since the last compaction.
pub struct Head {
    symbols: HashSet<SYM>,
    series: Vec<Series>,
}

impl Head {
    /// Room for `series` series and `symbols` distinct strings, reserved up front.
    pub fn with_capacity(series: usize, symbols: usize) -> Head {
        Head { symbols: HashSet::with_capacity(symbols), series: Vec::with_capacity(series) }
    }

    /// The shared copy of `s`, made on first sight. `Arc<str>: Borrow<str>`, so the lookup takes a `&str`.
    fn intern(symbols: &mut HashSet<SYM>, s: &str) -> SYM {
INTERN
    }

    /// Adds a series. `labels` arrive sorted by name, as Prometheus keeps them.
    pub fn add_series(&mut self, name: &str, labels: &[(&str, &str)]) -> SeriesId {
        let id = SeriesId(self.series.len() as u32);
        let symbols = &mut self.symbols;
        let name = Head::intern(symbols, name);
        // A mapped slice iterator knows its length, so this collects straight into one allocation.
        let labels: Labels = BUILD;
        self.series.push(Series { name, labels, samples: Vec::new() });
        id
    }
""".replace("LABELS_TY", labels_ty).replace("SYM", sym_ty).replace("INTERN", intern_body).replace("BUILD", build_labels) + HEAD_TAIL.replace("LABELS_OF", labels_of)


HEAD_RANDOM = """
#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(8205);
    let names = ["up", "http_requests_total", "cpu_seconds_total"];
    let keys = ["env", "instance", "job"];
    let values = ["prod", "dev", "a:9090", "b:9090", "api", "db", "env"];
    for _ in 0..100 {
        let mut head = Head::with_capacity(4, 4);
        let mut model: Vec<(String, Vec<(String, String)>)> = Vec::new();
        let mut log = Vec::new();
        for _ in 0..rng.below(10) {
            let name = *rng.pick(&names);
            let mut labels: Vec<(&str, &str)> = Vec::new();
            for &k in &keys {
                if rng.bool() {
                    labels.push((k, *rng.pick(&values)));
                }
            }
            log.push(format!("{name}{labels:?}"));
            let id = head.add_series(name, &labels);
            check!(format!("add_series: {}", log.join(", ")), id, SeriesId(model.len() as u32));
            model.push((name.to_string(), labels.iter().map(|&(k, v)| (k.to_string(), v.to_string())).collect()));
        }
        let ctx = log.join(", ");
        for (i, (name, labels)) in model.iter().enumerate() {
            let id = SeriesId(i as u32);
            let got: Vec<(String, String)> = head.labels_of(id).iter().map(|(k, v)| (k.to_string(), v.to_string())).collect();
            check!(format!("{ctx}: name and labels_of {id:?}"), (head.name(id).to_string(), got), (name.clone(), labels.clone()));
            let k = *rng.pick(&keys);
            let want = labels.iter().find(|(lk, _)| lk == k).map(|(_, v)| v.as_str());
            check!(format!("{ctx}: label({id:?}, {k:?})"), head.label(id, k), want);
        }
        let (k, v) = (*rng.pick(&keys), *rng.pick(&values));
        let want: Vec<SeriesId> = (0..model.len()).filter(|&i| model[i].1.iter().any(|(lk, lv)| lk == k && lv == v)).map(|i| SeriesId(i as u32)).collect();
        check!(format!("{ctx}: select({k:?}, {v:?})"), head.select(k, v), want);
        let mut distinct = std::collections::HashSet::new();
        for (name, labels) in &model {
            distinct.insert(name.clone());
            for (lk, lv) in labels {
                distinct.insert(lk.clone());
                distinct.insert(lv.clone());
            }
        }
        check!(format!("{ctx}: symbols()"), head.symbols(), distinct.len());
    }
}
"""

HEAD_SETUP = """let mut head = Head::with_capacity(16, 64);
head.add_series("http_requests_total", &[("env", "prod"), ("job", "api")]);"""

P.append(dict(
    slug="freeze-shared-strings", title="Frozen, shared, or growing", mode="fix", level="medium", stage="pick-the-representation",
    tags=["Arc<str>", "Arc<[T]>", "Box<[T]>", "interning", "allocation"],
    teaches=["`Arc<str>` / `Arc<[T]>` put the count and the data in one allocation behind a 16-byte fat pointer; `Arc<String>` / `Arc<Vec<T>>` take two allocations and two hops.",
             "Choose per field: `Vec` for what grows, a boxed or shared slice for what's frozen, a shared `str` for what's repeated.",
             "`Arc<str>: Borrow<str>` lets a `HashSet<Arc<str>>` interner look up by `&str` without allocating."],
    statement="""
        A metrics database keeps every live series in a head block. Each series stores its metric name, its
        labels (sorted by name, fixed at creation) and its samples. Thousands of series share the same few
        strings, the query engine takes copies of label sets that must outlive the head, and ingestion adds
        series all day, so the owned-`String` representation allocates on every step.

        Keep the API and change the representation:

        - `size_of::<Series>()` at most **56** bytes (it's 72);
        - `add_series` whose strings the head has seen before makes **exactly one** allocation, and each new
          distinct string costs exactly one more (`with_capacity` reserves room, so nothing else grows);
        - `labels_of` makes **no** allocation, and its result still outlives the `Head`;
        - `append` stays amortised O(1); `symbols()` is the number of distinct strings held.
    """,
    examples=[("add_series(\"up\", [(\"env\", \"prod\"), (\"job\", \"api\")]) after both were added before", "1 allocation"),
              ("labels_of(id)", "0 allocations")],
    constraints=["labels arrive sorted by name, with distinct names", "series ids are dense from 0"],
    starter=HEAD_NAIVE,
    solution=head_shared(),
    visible=[
        T("series_fits_56_bytes", "size_of::<Series>() <= 56", "std::mem::size_of::<Series>() <= 56", "true"),
        T("known_strings_one_allocation", "add http_requests_total{env=prod, job=api}, then the same metric with job=api, env=prod again",
          "(n.count, head.name(id), head.label(id, \"job\"))", '(1, "http_requests_total", Some("api"))',
          setup=HEAD_SETUP + '\nlet (id, n) = anneal_prelude::allocs(|| head.add_series("http_requests_total", &[("env", "prod"), ("job", "api")]));'),
        T("new_strings_one_each", "then add up{env=dev, instance=a:9090}: 4 new strings", "(n.count, head.symbols())", "(5, 9)",
          setup=HEAD_SETUP + '\nlet (_, n) = anneal_prelude::allocs(|| head.add_series("up", &[("env", "dev"), ("instance", "a:9090")]));'),
        T("labels_of_is_free", "labels_of(first series), allocations; it outlives the head", "(n.count, pairs)",
          '(0, vec![("env".to_string(), "prod".to_string()), ("job".to_string(), "api".to_string())])',
          setup=HEAD_SETUP + "\nlet (labels, n) = anneal_prelude::allocs(|| head.labels_of(SeriesId(0)));\ndrop(head);\nlet pairs: Vec<(String, String)> = labels.iter().map(|(k, v)| (k.to_string(), v.to_string())).collect();"),
        T("select_and_samples", "three series; select job=api; append two samples to the first", "(head.select(\"job\", \"api\"), head.samples(SeriesId(0)).to_vec())",
          "(vec![SeriesId(0), SeriesId(2)], vec![(1000, 1.5), (2000, 2.5)])",
          setup=HEAD_SETUP + '\nhead.add_series("up", &[("job", "db")]);\nhead.add_series("up", &[("job", "api")]);\nhead.append(SeriesId(0), 1000, 1.5);\nhead.append(SeriesId(0), 2000, 2.5);'),
    ],
    hidden=[
        T("labels_of_twice", "labels_of the same series twice: allocations, equal, len", "(n.count, a == b, a.len())", "(0, true, 2)",
          setup=HEAD_SETUP + "\nlet ((a, b), n) = anneal_prelude::allocs(|| (head.labels_of(SeriesId(0)), head.labels_of(SeriesId(0))));"),
        T("no_labels", "add_series(\"up\", []) twice", "(head.label(a, \"job\"), head.labels_of(b).len(), head.name(b), n.count <= 1)", '(None, 0, "up", true)',
          setup="let mut head = Head::with_capacity(4, 4);\nlet a = head.add_series(\"up\", &[]);\nlet (b, n) = anneal_prelude::allocs(|| head.add_series(\"up\", &[]));"),
        T("value_equal_to_a_name", "a value that is also a label name is one symbol: up{job=job}", "head.symbols()", "2",
          setup="let mut head = Head::with_capacity(4, 4);\nhead.add_series(\"up\", &[(\"job\", \"job\")]);"),
        T("thousand_series_known_strings", "1000 series over already-seen strings: allocations", "n.count", "1000",
          setup="let mut head = Head::with_capacity(2000, 64);\nhead.add_series(\"rpc_seconds\", &[(\"method\", \"get\"), (\"service\", \"users\"), (\"zone\", \"eu\")]);\nhead.add_series(\"rpc_seconds\", &[(\"method\", \"put\"), (\"service\", \"orders\"), (\"zone\", \"us\")]);\nlet (_, n) = anneal_prelude::allocs(|| {\n    for i in 0..1000 {\n        let m = if i % 2 == 0 { \"get\" } else { \"put\" };\n        head.add_series(\"rpc_seconds\", &[(\"method\", m), (\"service\", \"users\"), (\"zone\", \"us\")]);\n    }\n});"),
        T("append_grows_amortised", "1000 appends to one series: allocations at most 12", "(n.count <= 12, head.samples(id).len(), head.samples(id)[999])", "(true, 1000, (999, 0.5))",
          setup="let mut head = Head::with_capacity(1, 4);\nlet id = head.add_series(\"up\", &[]);\nlet (_, n) = anneal_prelude::allocs(|| {\n    for t in 0..1000 {\n        head.append(id, t, 0.5);\n    }\n});"),
        T("label_missing_key", "label of a key between, before and after the stored ones", "(head.label(SeriesId(0), \"a\"), head.label(SeriesId(0), \"instance\"), head.label(SeriesId(0), \"zz\"))", "(None, None, None)",
          setup=HEAD_SETUP),
        T("select_nothing", "select on a missing value and on an empty head", "(head.select(\"job\", \"db\"), Head::with_capacity(0, 0).select(\"job\", \"api\"))", "(vec![], vec![])",
          setup=HEAD_SETUP),
        T("unicode_labels", "up{city=Zürich}: label and symbols", "(head.label(SeriesId(0), \"city\"), head.symbols())", '(Some("Zürich"), 3)',
          setup="let mut head = Head::with_capacity(4, 4);\nhead.add_series(\"up\", &[(\"city\", \"Zürich\")]);"),
        T("labels_are_send_and_sync", "Labels can go to another thread", "std::thread::spawn(move || labels.len()).join().unwrap()", "2",
          setup=HEAD_SETUP + "\nlet labels = head.labels_of(SeriesId(0));"),
        HEAD_RANDOM,
    ],
    hints=[("approach", "Ask of each field: does it grow, is it frozen, is it repeated? Samples grow (`Vec`). Labels are frozen and handed out (`Arc<[_]>`). Names and values repeat across series (intern them as `Arc<str>` in a `HashSet`)."),
           ("rust", "`HashSet<Arc<str>>::get(s)` works with `s: &str` because `Arc<str>: Borrow<str>`; `Arc::from(s)` makes the one allocation. `iter.map(..).collect::<Arc<[_]>>()` allocates once when the iterator knows its length."),
           ("edge case", "`Arc<String>` and `Arc<Vec<T>>` are 8 bytes, but each costs two allocations, and a `HashSet<Arc<String>>` can't be searched with a `&str` without building a `String` first.")],
    notes=("""Pick each field's type by how it's used. `samples` grows, so it stays a `Vec` (24 bytes: pointer, capacity, length). `labels` never changes after creation and is handed to queries that outlive the head, so it's an `Arc<[(Arc<str>, Arc<str>)]>`: one allocation holding the reference counts and the pairs, a 16-byte fat pointer, and `labels_of` is a count bump. `Box<[T]>` would be the choice for frozen data with one owner: 16 bytes and no spare capacity. The strings repeat across thousands of series, so they're interned once as `Arc<str>` in a `HashSet`, which can be searched with a plain `&str` because `Arc<str>: Borrow<str>`.

The two-level versions are the trap: `Arc<String>` and `Arc<Vec<T>>` are thinner (8 bytes) but take two allocations and two dependent loads, and a `HashSet<Arc<String>>` can only be searched by building a `String`. Prometheus fought the same costs in Go: its `stringlabels` build packs a series' labels into one string, and its head block interns symbols.""", "O(k) per add_series with k labels; O(1) labels_of", "56 bytes per series + one shared copy of each string"),
    follow_up="Replace the `Arc<str>` symbols with `u32` ids into a symbol table. What does `Series` shrink to, what does `labels_of` return then, and what does the query engine lose?",
    source="Prometheus TSDB head block and its stringlabels build; rustc's Lrc<str> source text",
    related=["S7", "F3", "F4"],
    perf=dict(allocs=True),
    wrong=dict(
        arc_vec_labels=head_shared(labels_ty="Arc<Vec<(Arc<str>, Arc<str>)>>",
                                   build_labels="Arc::new(labels.iter().map(|&(k, v)| (Head::intern(symbols, k), Head::intern(symbols, v))).collect())"),
        arc_string_symbols=head_shared(labels_ty="Arc<[(Arc<String>, Arc<String>)]>", sym_ty="Arc<String>", intern_body="""        let key = Arc::new(s.to_string());
        if let Some(sym) = symbols.get(&key) {
            return Arc::clone(sym);
        }
        symbols.insert(Arc::clone(&key));
        key"""),
    ),
))

CFG_HEAD = """
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub struct BlockId(pub u32);
"""

CFG_BODY = """
/// A basic block: a run of statements and its control-flow edges, in the order they were added.
pub struct Block {
    pub stmts: u32,
    succs: Edges,
    preds: Edges,
}

/// A function's control-flow graph.
pub struct Cfg {
    blocks: Vec<Block>,
}

impl Cfg {
    pub fn new() -> Cfg {
        Cfg { blocks: Vec::new() }
    }

    pub fn with_capacity(blocks: usize) -> Cfg {
        Cfg { blocks: Vec::with_capacity(blocks) }
    }

    pub fn len(&self) -> usize {
        self.blocks.len()
    }

    pub fn is_empty(&self) -> bool {
        self.blocks.is_empty()
    }

    pub fn add_block(&mut self, stmts: u32) -> BlockId {
        let id = BlockId(self.blocks.len() as u32);
        self.blocks.push(Block { stmts, succs: Edges::new(), preds: Edges::new() });
        id
    }

    /// Adds the edge `from -> to`, unless it's already there.
    pub fn add_edge(&mut self, from: BlockId, to: BlockId) {
        if self.blocks[from.0 as usize].succs.contains(&to) {
            return;
        }
        self.blocks[from.0 as usize].succs.push(to);
        self.blocks[to.0 as usize].preds.push(from);
    }

    pub fn stmts(&self, b: BlockId) -> u32 {
        self.blocks[b.0 as usize].stmts
    }

    pub fn succs(&self, b: BlockId) -> &[BlockId] {
        &self.blocks[b.0 as usize].succs
    }

    pub fn preds(&self, b: BlockId) -> &[BlockId] {
        &self.blocks[b.0 as usize].preds
    }

    /// Depth-first from `entry`, successors in order; the reverse of the post-order. Unreachable blocks
    /// are left out.
    pub fn reverse_postorder(&self, entry: BlockId) -> Vec<BlockId> {
        let mut seen = vec![false; self.blocks.len()];
        let mut post = Vec::new();
        let mut stack = vec![(entry, 0)];
        seen[entry.0 as usize] = true;
        while let Some((b, next)) = stack.last_mut() {
            let b = *b;
            if let Some(&s) = self.blocks[b.0 as usize].succs.get(*next) {
                *next += 1;
                if !seen[s.0 as usize] {
                    seen[s.0 as usize] = true;
                    stack.push((s, 0));
                }
            } else {
                post.push(b);
                stack.pop();
            }
        }
        post.reverse();
        post
    }
"""

CFG_SPLIT_TODO = """
    /// Splits every critical edge: an edge from a block with several successors to a block with several
    /// predecessors gets a new empty block (0 statements) on it. The new block takes the edge's place in
    /// both lists. Blocks are visited in id order and successors in order; returns how many were split.
    pub fn split_critical_edges(&mut self) -> usize {
        todo!()
    }
}
"""


def cfg_split(replace="""                self.blocks[from].succs[i] = mid;"""):
    return """
    /// Splits every critical edge: an edge from a block with several successors to a block with several
    /// predecessors gets a new empty block (0 statements) on it. The new block takes the edge's place in
    /// both lists. Blocks are visited in id order and successors in order; returns how many were split.
    pub fn split_critical_edges(&mut self) -> usize {
        let original = self.blocks.len();
        let mut split = 0;
        for from in 0..original {
            if self.blocks[from].succs.len() < 2 {
                continue;
            }
            for i in 0..self.blocks[from].succs.len() {
                let to = self.blocks[from].succs[i];
                if self.blocks[to.0 as usize].preds.len() < 2 {
                    continue;
                }
                let mid = BlockId(self.blocks.len() as u32);
                let mut succs = Edges::new();
                succs.push(to);
                let mut preds = Edges::new();
                preds.push(BlockId(from as u32));
                self.blocks.push(Block { stmts: 0, succs, preds });
REPLACE
                let to_preds = &mut self.blocks[to.0 as usize].preds;
                let at = to_preds.iter().position(|&p| p.0 as usize == from).expect("edges are kept in both lists");
                to_preds[at] = mid;
                split += 1;
            }
        }
        split
    }
}
""".replace("REPLACE", replace)


def cfg_solution(n=4, split=None):
    return CFG_HEAD + """
use smallvec::SmallVec;

/// Nearly every block has at most N edges each way (a goto, a branch, a small switch). Four `u32`s are
/// 16 bytes: the same space as the heap pointer and length they share a union with, so the inline
/// capacity costs nothing over a `Vec`'s 24 bytes, and a switch with more targets spills to the heap.
type Edges = SmallVec<[BlockId; N]>;
""".replace("N]", f"{n}]").replace("most N", f"most {n}") + CFG_BODY + (split or cfg_split())


CFG_MODEL = """
/// The same graph as plain adjacency lists, with the same algorithms.
struct Model {
    succs: Vec<Vec<usize>>,
    preds: Vec<Vec<usize>>,
}

impl Model {
    fn edge(&mut self, a: usize, b: usize) {
        if !self.succs[a].contains(&b) {
            self.succs[a].push(b);
            self.preds[b].push(a);
        }
    }

    fn split(&mut self) -> usize {
        let n = self.succs.len();
        let mut count = 0;
        for a in 0..n {
            if self.succs[a].len() < 2 {
                continue;
            }
            for i in 0..self.succs[a].len() {
                let b = self.succs[a][i];
                if self.preds[b].len() < 2 {
                    continue;
                }
                let mid = self.succs.len();
                self.succs.push(vec![b]);
                self.preds.push(vec![a]);
                self.succs[a][i] = mid;
                let at = self.preds[b].iter().position(|&p| p == a).unwrap();
                self.preds[b][at] = mid;
                count += 1;
            }
        }
        count
    }

    fn rpo(&self, entry: usize) -> Vec<usize> {
        fn dfs(m: &Model, b: usize, seen: &mut Vec<bool>, post: &mut Vec<usize>) {
            seen[b] = true;
            for &s in &m.succs[b] {
                if !seen[s] {
                    dfs(m, s, seen, post);
                }
            }
            post.push(b);
        }
        let mut seen = vec![false; self.succs.len()];
        let mut post = Vec::new();
        dfs(self, entry, &mut seen, &mut post);
        post.reverse();
        post
    }
}
"""

CFG_IDS = """
fn ids(xs: &[BlockId]) -> Vec<usize> {
    xs.iter().map(|b| b.0 as usize).collect()
}
"""

CFG_RANDOM = """
#[test]
fn random_vs_adjacency_lists() {
    let mut rng = anneal_prelude::Rng::new(8206);
    for _ in 0..200 {
        let n = 1 + rng.below(9);
        let mut cfg = Cfg::new();
        let mut model = Model { succs: vec![Vec::new(); n], preds: vec![Vec::new(); n] };
        for i in 0..n {
            cfg.add_block(i as u32);
        }
        let mut log = Vec::new();
        for _ in 0..rng.below(3 * n) {
            let (a, b) = (rng.below(n), rng.below(n));
            log.push(format!("{a}->{b}"));
            cfg.add_edge(BlockId(a as u32), BlockId(b as u32));
            model.edge(a, b);
        }
        let ctx = format!("{n} blocks, edges [{}]", log.join(", "));
        check!(format!("{ctx}: reverse_postorder(0)"), ids(&cfg.reverse_postorder(BlockId(0))), model.rpo(0));
        let got = cfg.split_critical_edges();
        let want = model.split();
        check!(format!("{ctx}: split_critical_edges()"), (got, cfg.len()), (want, model.succs.len()));
        for b in 0..model.succs.len() {
            let id = BlockId(b as u32);
            check!(format!("{ctx}: after splitting, succs and preds of {b}"), (ids(cfg.succs(id)), ids(cfg.preds(id))), (model.succs[b].clone(), model.preds[b].clone()));
        }
        check!(format!("{ctx}: after splitting, reverse_postorder(0)"), ids(&cfg.reverse_postorder(BlockId(0))), model.rpo(0));
    }
}
"""

CFG_SWITCHES = """
/// `groups` copies of: a block switching 4 ways, the 4 arms, and a join block with 4 predecessors that
/// falls through to the next group.
fn switches(cfg: &mut Cfg, groups: usize) {
    let mut prev: Option<BlockId> = None;
    for _ in 0..groups {
        let head = cfg.add_block(3);
        if let Some(p) = prev {
            cfg.add_edge(p, head);
        }
        let join = cfg.add_block(1);
        for _ in 0..4 {
            let arm = cfg.add_block(2);
            cfg.add_edge(head, arm);
            cfg.add_edge(arm, join);
        }
        prev = Some(join);
    }
}
"""

P.append(dict(
    slug="inline-edge-lists", title="Inline edge lists for a CFG", mode="fix", level="medium", stage="pick-the-representation",
    tags=["SmallVec", "inline capacity", "compiler IR", "allocation", "critical edges"],
    teaches=["`SmallVec<[T; N]>` stores up to N items inline and spills to the heap after; most CFG blocks have 1 or 2 edges, so most never allocate.",
             "Pick N from the element size: with smallvec's `union` layout, 16 bytes of inline items cost nothing over the 24 bytes of a `Vec`; each 8 bytes more grows every block.",
             "Critical-edge splitting: an edge from a multi-successor block to a multi-predecessor block needs its own block before code can be placed on it."],
    statement="""
        A compiler's control-flow graph keeps each block's successors and predecessors. Nearly every block has at
        most 4 edges each way (a `goto`, an `if`, a small `match`); a big `switch` is rare. With a `Vec` per
        list, building the CFG of a large function allocates twice per block.

        1. Change the edge lists so that `size_of::<Block>()` stays **at most 56 bytes**, and building a graph
           where no block has more than **4** edges each way makes **no allocation** once `Cfg::with_capacity`
           has reserved the blocks. Larger switches must still work. (`smallvec` is available.)
        2. Write `split_critical_edges`: every edge from a block with several successors to a block with
           several predecessors gets a new empty block (0 statements) on it, which takes the edge's place in
           both lists. Visit blocks in id order (only the original ones) and successors in order, so new ids
           come out in that order; return how many edges were split.

        `add_edge`, the accessors and `reverse_postorder` keep their behaviour.
    """,
    examples=[("0 -> 1, 0 -> 2, 1 -> 2; split_critical_edges()", "1: new block 3 on 0 -> 2; succs(0) = [1, 3], preds(2) = [3, 1]"),
              ("1000 four-way switches built after with_capacity(6000)", "0 allocations")],
    constraints=["a graph has at most 2³² − 1 blocks", "add_edge ignores an edge that already exists", "self-loops are edges like any other"],
    crates=["smallvec"],
    starter=CFG_HEAD + """
/// Every edge list is a `Vec`.
type Edges = Vec<BlockId>;
""" + CFG_BODY + CFG_SPLIT_TODO,
    solution=cfg_solution(),
    visible=[
        T("block_fits_56_bytes", "size_of::<Block>() <= 56", "std::mem::size_of::<Block>() <= 56", "true"),
        CFG_SWITCHES,
        CFG_IDS,
        T("small_blocks_dont_allocate", "Cfg::with_capacity(6000), then 1000 four-way switches: allocations", "(n.count, cfg.len(), cfg.succs(BlockId(0)).len(), cfg.preds(BlockId(1)).len())", "(0, 6000, 4, 4)",
          setup="let mut cfg = Cfg::with_capacity(6000);\nlet (_, n) = anneal_prelude::allocs(|| switches(&mut cfg, 1000));"),
        T("split_one_critical_edge", "0 -> 1, 0 -> 2, 1 -> 2; split", "(count, ids(cfg.succs(BlockId(0))), ids(cfg.preds(BlockId(2))), ids(cfg.succs(BlockId(3))), ids(cfg.preds(BlockId(3))), cfg.stmts(BlockId(3)))",
          "(1, vec![1, 3], vec![3, 1], vec![2], vec![0], 0)",
          setup="let mut cfg = Cfg::new();\nfor s in [4, 2, 7] {\n    cfg.add_block(s);\n}\ncfg.add_edge(BlockId(0), BlockId(1));\ncfg.add_edge(BlockId(0), BlockId(2));\ncfg.add_edge(BlockId(1), BlockId(2));\nlet count = cfg.split_critical_edges();"),
        T("diamond_has_none", "a diamond 0 -> {1, 2} -> 3: split", "(cfg.split_critical_edges(), cfg.len())", "(0, 4)",
          setup="let mut cfg = Cfg::new();\nfor _ in 0..4 {\n    cfg.add_block(1);\n}\nfor (a, b) in [(0, 1), (0, 2), (1, 3), (2, 3)] {\n    cfg.add_edge(BlockId(a), BlockId(b));\n}"),
        T("big_switch_spills", "block 0 switching to 9 blocks", "(ids(cfg.succs(BlockId(0))), cfg.preds(BlockId(9)).to_vec())", "((1..=9).collect::<Vec<usize>>(), vec![BlockId(0)])",
          setup="let mut cfg = Cfg::new();\nfor _ in 0..10 {\n    cfg.add_block(0);\n}\nfor b in 1..=9 {\n    cfg.add_edge(BlockId(0), BlockId(b));\n}"),
    ],
    hidden=[
        CFG_SWITCHES,
        CFG_IDS,
        T("switch_graph_splits", "one four-way switch group, split: none of its edges is critical", "(cfg.split_critical_edges(), cfg.len())", "(0, 6)",
          setup="let mut cfg = Cfg::new();\nswitches(&mut cfg, 1);"),
        T("loop_back_edge", "0 -> 1, 1 -> 1, 1 -> 2: the self-loop is critical", "(count, ids(cfg.succs(BlockId(1))), ids(cfg.preds(BlockId(1))), ids(cfg.succs(BlockId(3))))",
          "(1, vec![3, 2], vec![0, 3], vec![1])",
          setup="let mut cfg = Cfg::new();\nfor _ in 0..3 {\n    cfg.add_block(1);\n}\nfor (a, b) in [(0, 1), (1, 1), (1, 2)] {\n    cfg.add_edge(BlockId(a), BlockId(b));\n}\nlet count = cfg.split_critical_edges();"),
        T("duplicate_edges_ignored", "0 -> 1 added three times", "(ids(cfg.succs(BlockId(0))), ids(cfg.preds(BlockId(1))))", "(vec![1], vec![0])",
          setup="let mut cfg = Cfg::new();\ncfg.add_block(0);\ncfg.add_block(0);\nfor _ in 0..3 {\n    cfg.add_edge(BlockId(0), BlockId(1));\n}"),
        T("rpo_skips_unreachable", "0 -> 2, 2 -> 3, 1 -> 3 from 0", "ids(&cfg.reverse_postorder(BlockId(0)))", "vec![0, 2, 3]",
          setup="let mut cfg = Cfg::new();\nfor _ in 0..4 {\n    cfg.add_block(0);\n}\nfor (a, b) in [(0, 2), (2, 3), (1, 3)] {\n    cfg.add_edge(BlockId(a), BlockId(b));\n}"),
        T("split_order", "0 -> {2, 3}, 1 -> {3, 2}: new blocks in (block, successor) order", "(count, ids(cfg.succs(BlockId(0))), ids(cfg.succs(BlockId(1))), ids(cfg.preds(BlockId(2))), ids(cfg.preds(BlockId(3))))",
          "(4, vec![4, 5], vec![6, 7], vec![4, 7], vec![5, 6])",
          setup="let mut cfg = Cfg::new();\nfor _ in 0..4 {\n    cfg.add_block(0);\n}\nfor (a, b) in [(0, 2), (0, 3), (1, 3), (1, 2)] {\n    cfg.add_edge(BlockId(a), BlockId(b));\n}\nlet count = cfg.split_critical_edges();"),
        T("empty_cfg", "Cfg::new()", "(cfg.len(), cfg.is_empty(), cfg.split_critical_edges())", "(0, true, 0)", setup="let mut cfg = Cfg::new();"),
        T("stmts_kept", "blocks with 5 and 9 statements", "(cfg.stmts(a), cfg.stmts(b), cfg.succs(a).is_empty())", "(5, 9, true)",
          setup="let mut cfg = Cfg::new();\nlet a = cfg.add_block(5);\nlet b = cfg.add_block(9);"),
        T("big_join", "10 blocks all jumping to block 10, then split", "(cfg.preds(BlockId(10)).len(), cfg.split_critical_edges())", "(10, 0)",
          setup="let mut cfg = Cfg::new();\nfor _ in 0..11 {\n    cfg.add_block(0);\n}\nfor b in 0..10 {\n    cfg.add_edge(BlockId(b), BlockId(10));\n}"),
        CFG_MODEL,
        CFG_RANDOM,
    ],
    hints=[("approach", "Most lists hold 1 to 4 ids. Keep that many inline in the block and fall back to the heap only for the rare big switch: `smallvec::SmallVec<[BlockId; N]>` does exactly that."),
           ("rust", "With the `union` feature, `SmallVec<[T; N]>` is `max(N * size_of::<T>(), 16) + 8` bytes: a length/capacity word plus a union of the inline array and (pointer, length). `[BlockId; 4]` is 16 bytes, so it costs no more than a `Vec`."),
           ("edge case", "When splitting, overwrite the edge in place in both lists (`succs[i] = mid`, and `from`'s position in `to`'s preds) so the order of the other edges doesn't change. A self-loop on a block with several successors is critical too.")],
    notes=("""`SmallVec<[T; N]>` keeps up to N items inline and moves them to the heap when it outgrows them. The size question decides N: with the `union` feature it's one word (the length while inline, the capacity once spilled) plus a union of the inline array and the heap's (pointer, length), so any array up to 16 bytes is free: `SmallVec<[u32; 4]>` is 24 bytes, exactly a `Vec`. Eight inline ids would make every block 88 bytes, most of it empty; two would allocate for every 3- and 4-way branch. N = 4 is what rustc uses for its MIR predecessor lists (`IndexVec<BasicBlock, SmallVec<[BasicBlock; 4]>>`). The trade-off: every access checks whether it's spilled, and moving a `SmallVec` copies its inline items.

Critical-edge splitting is a standard pass (rustc's `AddCallGuards`, LLVM's `SplitCriticalEdges`): an edge from a block with several successors into a block with several predecessors has nowhere to put code that must run only on that edge, so it gets a block of its own.""", "O(1) add_edge for small degrees; O(E · d) to split", "24 bytes per edge list; heap only past 4 edges"),
    follow_up="rustc's dep graph uses `SmallVec<[DepNodeIndex; 8]>` for edges. How would you pick N from a profile, and what does a spilled `SmallVec` cost compared with a `Vec`?",
    source="rustc MIR predecessors (SmallVec<[BasicBlock; 4]>), the smallvec crate, LLVM SplitCriticalEdges",
    related=["S3", "D9", "F3"],
    perf=dict(allocs=True),
    wrong=dict(
        inline_eight=cfg_solution(n=8),
        inline_two=cfg_solution(n=2),
        split_moves_edge_last=cfg_solution(split=cfg_split(replace="""                self.blocks[from].succs.remove(i);
                self.blocks[from].succs.push(mid);""")),
    ),
))

SMALLSTR_TRAITS = """
impl Deref for SmallStr {
    type Target = str;
    fn deref(&self) -> &str {
        self.as_str()
    }
}

impl Borrow<str> for SmallStr {
    fn borrow(&self) -> &str {
        self.as_str()
    }
}

impl From<&str> for SmallStr {
    fn from(s: &str) -> SmallStr {
        SmallStr::new(s)
    }
}

impl PartialOrd for SmallStr {
    fn partial_cmp(&self, other: &SmallStr) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}
"""

SMALLSTR_STARTER = """
use std::borrow::Borrow;
use std::cmp::Ordering;
use std::fmt;
use std::hash::{Hash, Hasher};
use std::ops::Deref;

/// An immutable string for a column of mostly short values (country codes, user names, enum-like tags).
#[derive(Clone)]
pub struct SmallStr {
    // Replace this: a `String` allocates for every non-empty value.
    s: String,
}

impl SmallStr {
    /// The longest string kept inline, in bytes.
    pub const INLINE_CAP: usize = 22;

    pub fn new(s: &str) -> SmallStr {
        todo!()
    }

    pub fn as_str(&self) -> &str {
        todo!()
    }

    /// Whether the bytes live inside the value rather than on the heap.
    pub fn is_inline(&self) -> bool {
        todo!()
    }
}

impl PartialEq for SmallStr {
    fn eq(&self, other: &SmallStr) -> bool {
        todo!()
    }
}

impl Eq for SmallStr {}

impl Hash for SmallStr {
    fn hash<H: Hasher>(&self, state: &mut H) {
        todo!()
    }
}

impl Ord for SmallStr {
    fn cmp(&self, other: &SmallStr) -> Ordering {
        todo!()
    }
}

/// Prints like a `&str`: `"abc"`.
impl fmt::Debug for SmallStr {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        todo!()
    }
}

impl fmt::Display for SmallStr {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        todo!()
    }
}
""" + SMALLSTR_TRAITS


def smallstr(heap_ty="Box<str>", heap_new="Box::from(s)", repr_derive="#[derive(Clone)]", str_derive="#[derive(Clone)]", hash_impl="""
/// Must hash exactly like the `str` it holds: `Borrow<str>` promises that, and `HashSet<SmallStr>` looks
/// values up by `&str`.
impl Hash for SmallStr {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.as_str().hash(state);
    }
}
""", ord_body="self.as_str().cmp(other.as_str())"):
    return """
use std::borrow::Borrow;
use std::cmp::Ordering;
use std::fmt;
use std::hash::{Hash, Hasher};
use std::ops::Deref;

/// Up to 22 bytes live inside the value; longer strings go to the heap. `Box<str>` (16 bytes) keeps the
/// heap variant as small as the inline one: tag, length and 22 bytes is 24, and so is tag, padding and
/// the box. A `String` there (24 bytes) would make every value 32.
REPR_DERIVE
enum Repr {
    Inline { len: u8, buf: [u8; SmallStr::INLINE_CAP] },
    Heap(HEAP_TY),
}

/// An immutable string for a column of mostly short values (country codes, user names, enum-like tags).
STR_DERIVE
pub struct SmallStr(Repr);

impl SmallStr {
    /// The longest string kept inline, in bytes.
    pub const INLINE_CAP: usize = 22;

    pub fn new(s: &str) -> SmallStr {
        if s.len() <= SmallStr::INLINE_CAP {
            let mut buf = [0; SmallStr::INLINE_CAP];
            buf[..s.len()].copy_from_slice(s.as_bytes());
            SmallStr(Repr::Inline { len: s.len() as u8, buf })
        } else {
            SmallStr(Repr::Heap(HEAP_NEW))
        }
    }

    pub fn as_str(&self) -> &str {
        match &self.0 {
            // Always a whole `&str`'s bytes, so this can't fail (compact_str skips the check with unsafe).
            Repr::Inline { len, buf } => std::str::from_utf8(&buf[..*len as usize]).expect("copied from a &str"),
            Repr::Heap(s) => s,
        }
    }

    /// Whether the bytes live inside the value rather than on the heap.
    pub fn is_inline(&self) -> bool {
        matches!(self.0, Repr::Inline { .. })
    }
}

/// Equality, hashing and ordering all go through `as_str`, so they agree with `str`'s, as `Borrow<str>`
/// requires.
impl PartialEq for SmallStr {
    fn eq(&self, other: &SmallStr) -> bool {
        self.as_str() == other.as_str()
    }
}

impl Eq for SmallStr {}
HASH_IMPL
impl Ord for SmallStr {
    fn cmp(&self, other: &SmallStr) -> Ordering {
        ORD_BODY
    }
}

/// Prints like a `&str`: `"abc"`.
impl fmt::Debug for SmallStr {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        fmt::Debug::fmt(self.as_str(), f)
    }
}

impl fmt::Display for SmallStr {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        fmt::Display::fmt(self.as_str(), f)
    }
}
""".replace("REPR_DERIVE", repr_derive).replace("STR_DERIVE", str_derive).replace("HEAP_TY", heap_ty).replace("HEAP_NEW", heap_new) \
       .replace("HASH_IMPL", hash_impl).replace("ORD_BODY", ord_body) + SMALLSTR_TRAITS


SMALLSTR_HASH = """
fn hash_of<T: std::hash::Hash + ?Sized>(x: &T) -> u64 {
    use std::hash::{BuildHasher, BuildHasherDefault};
    BuildHasherDefault::<std::collections::hash_map::DefaultHasher>::default().hash_one(x)
}
"""

SMALLSTR_RANDOM = """
#[test]
fn random_vs_string() {
    let mut rng = anneal_prelude::Rng::new(8207);
    let mut made = Vec::new();
    for _ in 0..300 {
        let n = if rng.bool() { rng.below(24) } else { rng.below(40) };
        let s = rng.string(n, "abcXYZ09 _éß中😀");
        let (small, a) = anneal_prelude::allocs(|| SmallStr::new(&s));
        let heap = s.len() > SmallStr::INLINE_CAP;
        check!(format!("SmallStr::new({s:?}): as_str, len, is_inline, allocations"), (small.as_str(), small.len(), small.is_inline(), a.count),
               (s.as_str(), s.len(), !heap, heap as u64));
        check!(format!("hash of SmallStr::new({s:?}) vs the str's"), hash_of(&small), hash_of(s.as_str()));
        made.push((small, s));
    }
    for _ in 0..300 {
        let (x, xs) = rng.pick(&made);
        let (y, ys) = rng.pick(&made);
        check!(format!("{xs:?} vs {ys:?}: ==, cmp"), (x == y, x.cmp(y)), (xs == ys, xs.cmp(ys)));
    }
}
"""

P.append(dict(
    slug="inline-small-strings", title="Inline small strings", level="medium", stage="pick-the-representation",
    tags=["small string optimisation", "enum layout", "Box<str>", "Borrow", "Hash"],
    teaches=["Small-string optimisation: short strings live inside the 24 bytes a `String` would spend on pointer, capacity and length.",
             "The heap variant has to be as small as the inline one: `Box<str>` (16 bytes) keeps the enum at 24; `String` would make it 32.",
             "`Borrow<str>` is a contract: `Hash`, `Eq` and `Ord` must match `str`'s, or `HashSet<SmallStr>::contains(\"x\")` silently misses."],
    statement="""
        A columnar database stores millions of short strings (country codes, user names, status tags), each
        a `String`: 24 bytes plus a heap allocation, even for `"DE"`.

        Write `SmallStr`, an immutable string that keeps up to `INLINE_CAP` = **22** bytes inside the value
        and puts longer ones on the heap:

        - `size_of::<SmallStr>()` is **24**, the same as `String`, and so is `Option<SmallStr>`;
        - `new` makes **no** allocation for strings of up to 22 bytes and **exactly one** for longer ones;
          cloning follows the same rule;
        - `as_str`, `Deref<Target = str>`, `is_inline`, `Debug` and `Display` (both print like the `&str`);
        - `Eq`, `Hash` and `Ord` agree with `str`'s, because `Borrow<str>` lets a `HashSet<SmallStr>` or
          `BTreeSet<SmallStr>` be searched with a plain `&str`.
    """,
    examples=[("SmallStr::new(\"DE\"): allocations, is_inline()", "0, true"),
              ("SmallStr::new(\"a string of 23 bytes...\"): allocations, is_inline()", "1, false"),
              ("HashSet<SmallStr> holding \"DE\": contains(\"DE\")", "true")],
    constraints=["lengths are in bytes (UTF-8), not chars", "no crates (compact_str, smol_str)"],
    starter=SMALLSTR_STARTER,
    solution=smallstr(),
    visible=[
        T("same_size_as_string", "size_of::<SmallStr>(), size_of::<Option<SmallStr>>()", "(std::mem::size_of::<SmallStr>(), std::mem::size_of::<Option<SmallStr>>())", "(24, 24)"),
        T("short_is_inline", "SmallStr::new(\"DE\")", "(s.as_str(), s.is_inline(), n.count)", '("DE", true, 0)',
          setup='let (s, n) = anneal_prelude::allocs(|| SmallStr::new("DE"));'),
        T("long_goes_to_heap", "SmallStr::new(\"payments-service-eu-west-1\") (26 bytes)", "(s.as_str(), s.is_inline(), n.count, n.bytes)", '("payments-service-eu-west-1", false, 1, 26)',
          setup='let (s, n) = anneal_prelude::allocs(|| SmallStr::new("payments-service-eu-west-1"));'),
        T("lookup_by_str", "HashSet and BTreeSet of SmallStr: contains(\"DE\"), contains(\"FR\")",
          '(hashed.contains("DE"), hashed.contains("FR"), sorted.contains("DE"), sorted.contains("a-much-longer-country-name"))', "(true, false, true, true)",
          setup='let words = ["DE", "US", "a-much-longer-country-name"];\nlet hashed: std::collections::HashSet<SmallStr> = words.iter().map(|&w| SmallStr::new(w)).collect();\nlet sorted: std::collections::BTreeSet<SmallStr> = words.iter().map(|&w| SmallStr::new(w)).collect();'),
        T("prints_like_str", "format!(\"{:?} {}\") of SmallStr::new(\"say \\\"hi\\\"\")", 'format!("{:?} {}", s, s)', r'"\"say \\\"hi\\\"\" say \"hi\""',
          setup='let s = SmallStr::new("say \\"hi\\"");'),
    ],
    hidden=[
        T("exactly_22_inline", "22 and 23 ASCII bytes", "(a.is_inline(), b.is_inline(), a.len(), b.len())", "(true, false, 22, 23)",
          setup='let a = SmallStr::new(&"x".repeat(22));\nlet b = SmallStr::new(&"x".repeat(23));'),
        T("multibyte_counts_bytes", "11 × 'é' (22 bytes), 8 × '中' (24 bytes)", "(a.is_inline(), a.as_str().chars().count(), b.is_inline(), b.as_str())", '(true, 11, false, "中中中中中中中中")',
          setup='let a = SmallStr::new(&"é".repeat(11));\nlet b = SmallStr::new(&"中".repeat(8));'),
        T("empty", "SmallStr::new(\"\")", "(s.as_str(), s.is_inline(), s.is_empty(), n.count)", '("", true, true, 0)',
          setup='let (s, n) = anneal_prelude::allocs(|| SmallStr::new(""));'),
        T("clone_costs", "clone an inline and a heap SmallStr: allocations", "(a.count, b.count, x2 == x, y2 == y)", "(0, 1, true, true)",
          setup='let x = SmallStr::new("tag");\nlet y = SmallStr::new("a string that is far too long to fit");\nlet (x2, a) = anneal_prelude::allocs(|| x.clone());\nlet (y2, b) = anneal_prelude::allocs(|| y.clone());'),
        T("column_of_short_values", "collect 1000 short SmallStrs into a Vec: allocations", "(n.count, col.len(), col[999].as_str())", '(1, 1000, "c999")',
          setup='let (col, n) = anneal_prelude::allocs(|| (0..1000).map(|i| SmallStr::new(if i < 999 { "US" } else { "c999" })).collect::<Vec<_>>());'),
        T("order_matches_str", "sort [\"b\", \"ab\", \"a-very-long-string-indeed-yes\", \"B\", \"\"]", "v.iter().map(|s| s.as_str()).collect::<Vec<_>>()",
          'vec!["", "B", "a-very-long-string-indeed-yes", "ab", "b"]',
          setup='let mut v: Vec<SmallStr> = ["b", "ab", "a-very-long-string-indeed-yes", "B", ""].iter().map(|&s| SmallStr::new(s)).collect();\nv.sort();'),
        T("deref_to_str_methods", "SmallStr::new(\"Hello\"): to_uppercase, starts_with, len", '(s.to_uppercase(), s.starts_with("He"), s.len())', '("HELLO".to_string(), true, 5)',
          setup='let s = SmallStr::new("Hello");'),
        SMALLSTR_HASH,
        T("hash_matches_str", "hash of SmallStr vs &str, inline and heap", 'hash_of(&SmallStr::new("DE")) == hash_of("DE") && hash_of(&SmallStr::new("x-long-enough-to-live-on-the-heap")) == hash_of("x-long-enough-to-live-on-the-heap")', "true"),
        T("display_pads", "format!(\"[{:>5}]\", SmallStr::new(\"ab\"))", 'format!("[{:>5}]", SmallStr::new("ab"))', '"[   ab]"'),
        SMALLSTR_RANDOM,
    ],
    hints=[("approach", "An enum with two variants: `Inline { len: u8, buf: [u8; 22] }` and a heap variant. Work out each variant's size with the tag byte: the inline one is 1 + 1 + 22 = 24 bytes, so the heap one must fit in 24 too."),
           ("rust", "`Box<str>` is a 16-byte fat pointer, so the heap variant is tag + padding + 16 = 24. `String` is 24 on its own, which makes the enum 32. Wrap the enum in a `pub struct SmallStr(Repr)` so callers can't build a broken one."),
           ("edge case", "Don't derive `Hash` or `Ord` on the enum: derived ones see the tag, the length and the padding bytes, not the string, and `HashSet<SmallStr>::contains(\"x\")` stops finding values. Delegate all three to `as_str()`.")],
    notes=("""A `String` is 24 bytes of pointer, capacity and length before it stores anything, so a short string can live in those 24 bytes instead: a one-byte tag, a length, and 22 bytes of text. The heap variant must fit the same 24 bytes, which rules out `String` (the enum becomes 32) and leaves `Box<str>`: an immutable string doesn't need a capacity, so a 16-byte fat pointer is enough. Both variants leave the tag's other values free, so `Option<SmallStr>` is still 24.

`Borrow<str>` is what lets a `HashSet<SmallStr>` or `BTreeSet<SmallStr>` be searched with `&str`, and it comes with a contract: `Eq`, `Hash` and `Ord` must give the same answers as on the borrowed `str`. Derived impls on the enum would hash the tag, length and zero padding, and order by length first, so lookups silently miss. The same trade shows up in production: smol_str (rust-analyzer) keeps 23 bytes inline, and compact_str squeezes 24 by using the last byte as both length and tag, because a UTF-8 string's last byte is never 0xC0 or above.""", "O(n) to build; O(1) as_str (plus a UTF-8 check of ≤ 22 bytes here)", "24 bytes inline; + len bytes on the heap past 22"),
    follow_up="compact_str keeps 24 bytes inline in a 24-byte value. Where does it put the length and the tag, and why does UTF-8 make that possible?",
    source="compact_str, smol_str (rust-analyzer)",
    related=["S2", "S8"],
    perf=dict(allocs=True),
    wrong=dict(
        heap_string=smallstr(heap_ty="String", heap_new="s.to_string()"),
        derived_hash=smallstr(repr_derive="#[derive(Clone, Hash)]", str_derive="#[derive(Clone, Hash)]", hash_impl=""),
        derived_order=smallstr(repr_derive="#[derive(Clone, PartialEq, Eq, PartialOrd, Ord)]", ord_body="self.0.cmp(&other.0)"),
    ),
))

ZIP_FIELDS = """
    signature: u32,
    version: u16,
    flags: u16,
    method: u16,
    mod_time: u16,
    mod_date: u16,
    crc32: u32,
    compressed_size: u32,
    uncompressed_size: u32,
    name_len: u16,
    extra_len: u16,
}
"""

ZIP_VIEW = """
impl LocalHeader {
    /// The header at the start of `bytes`, read in place without copying. `None` if `bytes` is shorter
    /// than a header or doesn't start with the signature.
    pub fn view(bytes: &[u8]) -> Option<&LocalHeader> {
        if bytes.len() < std::mem::size_of::<LocalHeader>() {
            return None;
        }
        // SAFETY: `bytes` holds at least size_of::<LocalHeader>() bytes, every bit pattern is a valid
        // LocalHeader (it's all integers), and LocalHeader has alignment 1, so any address is aligned for it.
        let header = unsafe { &*bytes.as_ptr().cast::<LocalHeader>() };
        (header.signature() == SIGNATURE).then_some(header)
    }

    // The archive is little-endian; `from_le` is a no-op on little-endian machines.
    pub fn signature(&self) -> u32 {
        u32::from_le(self.signature)
    }

    pub fn method(&self) -> u16 {
        u16::from_le(self.method)
    }

    pub fn crc32(&self) -> u32 {
        u32::from_le(self.crc32)
    }

    pub fn compressed_size(&self) -> u32 {
        u32::from_le(self.compressed_size)
    }

    pub fn uncompressed_size(&self) -> u32 {
        u32::from_le(self.uncompressed_size)
    }

    pub fn name_len(&self) -> usize {
        u16::from_le(self.name_len) as usize
    }

    pub fn extra_len(&self) -> usize {
        u16::from_le(self.extra_len) as usize
    }
"""

ZIP_ENTRIES = """
/// One entry of an archive: its name and its (still compressed) data, borrowed from the archive.
#[derive(Debug, PartialEq, Eq)]
pub struct Entry<'a> {
    pub name: &'a [u8],
    pub method: u16,
    pub crc32: u32,
    pub data: &'a [u8],
}

/// The entries at the front of `archive`: a header, the name, the extra field, the data, then the next
/// header, until the bytes no longer start with a local header (the central directory begins). `None` if
/// an entry is cut short.
pub fn entries(archive: &[u8]) -> Option<Vec<Entry<'_>>> {
    let mut out = Vec::new();
    let mut at = 0;
    while let Some(h) = LocalHeader::view(&archive[at..]) {
        let name_at = at + std::mem::size_of::<LocalHeader>();
        let data_at = name_at + h.name_len() + SKIP_EXTRA;
        let end = data_at + h.compressed_size() as usize;
        if end > archive.len() {
            return None;
        }
        out.push(Entry { name: &archive[name_at..name_at + h.name_len()], method: h.method(), crc32: h.crc32(), data: &archive[data_at..end] });
        at = end;
    }
    Some(out)
}
"""

ZIP_HEAD = """
/// Starts every local file header: "PK\\x03\\x04".
pub const SIGNATURE: u32 = 0x0403_4b50;
"""


def zip_code(repr_line="#[repr(C, packed)]", derive="#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]", extra="h.extra_len()", fixed=True):
    doc = ("""
/// A ZIP local file header exactly as it sits in the archive: 30 bytes, little-endian, at any offset.
/// `packed` removes the padding before `crc32` (offset 14) and drops the alignment to 1, which is what
/// makes `view`'s cast sound at any address. The price: no references to fields, only copies.
""" if fixed else """
/// A ZIP local file header exactly as it sits in the archive: 30 bytes, little-endian, at any offset.
""")
    methods = ("""
    /// Stored (method 0) entries aren't compressed.
    pub fn is_stored(&self) -> bool {
        self.method() == 0
    }

    /// `crc 0000abcd, 12 -> 34 bytes`, for logs. Accessors copy the fields out; `self.crc32` inside
    /// `format!` would take a reference to an unaligned field (E0793).
    pub fn describe(&self) -> String {
        format!("crc {:08x}, {} -> {} bytes", self.crc32(), self.compressed_size(), self.uncompressed_size())
    }
}
""" if fixed else """
    /// Stored (method 0) entries aren't compressed.
    pub fn is_stored(&self) -> bool {
        self.method.eq(&0)
    }

    /// `crc 0000abcd, 12 -> 34 bytes`, for logs.
    pub fn describe(&self) -> String {
        format!("crc {:08x}, {} -> {} bytes", self.crc32, self.compressed_size, self.uncompressed_size)
    }
}
""")
    return ZIP_HEAD + doc + repr_line + "\n" + derive + "\npub struct LocalHeader {" + ZIP_FIELDS + ZIP_VIEW + methods + ZIP_ENTRIES.replace("SKIP_EXTRA", extra)


ZIP_HELPER = """
/// One local header, name, extra field and data, as a ZIP writer lays them out (little-endian).
fn local(name: &str, extra: &[u8], data: &[u8], method: u16, crc: u32) -> Vec<u8> {
    let mut v = Vec::new();
    v.extend_from_slice(&0x0403_4b50u32.to_le_bytes());
    v.extend_from_slice(&20u16.to_le_bytes()); // version needed
    v.extend_from_slice(&0u16.to_le_bytes()); // flags
    v.extend_from_slice(&method.to_le_bytes());
    v.extend_from_slice(&0x6000u16.to_le_bytes()); // time
    v.extend_from_slice(&0x5a21u16.to_le_bytes()); // date
    v.extend_from_slice(&crc.to_le_bytes());
    v.extend_from_slice(&(data.len() as u32).to_le_bytes());
    v.extend_from_slice(&(data.len() as u32 * 3).to_le_bytes()); // uncompressed size
    v.extend_from_slice(&(name.len() as u16).to_le_bytes());
    v.extend_from_slice(&(extra.len() as u16).to_le_bytes());
    v.extend_from_slice(name.as_bytes());
    v.extend_from_slice(extra);
    v.extend_from_slice(data);
    v
}
"""

ZIP_RANDOM = """
#[test]
fn random_archives() {
    let mut rng = anneal_prelude::Rng::new(8208);
    for _ in 0..200 {
        let junk = rng.below(2);
        let mut archive: Vec<u8> = rng.vec(junk, 0, 255);
        let skip = archive.len();
        let mut want = Vec::new();
        let mut log = Vec::new();
        for _ in 0..rng.below(5) {
            let name_len = rng.below(12);
            let name = rng.string(name_len, "abcdefghij/._");
            let extra_len = if rng.bool() { 0 } else { rng.below(9) };
            let extra: Vec<u8> = rng.vec(extra_len, 0, 255);
            let data_len = rng.below(40);
            let data: Vec<u8> = rng.vec(data_len, 0, 255);
            let (method, crc) = (if rng.bool() { 0 } else { 8 }, rng.next_u64() as u32);
            log.push(format!("{name:?} (extra {}, data {}, method {method}, crc {crc:#x})", extra.len(), data.len()));
            archive.extend(local(&name, &extra, &data, method, crc));
            want.push((name.into_bytes(), method, crc, data));
        }
        archive.extend_from_slice(b"PK\\x01\\x02 central directory");
        let got = entries(&archive[skip..]).map(|es| es.into_iter().map(|e| (e.name.to_vec(), e.method, e.crc32, e.data.to_vec())).collect::<Vec<_>>());
        check!(format!("archive at offset {skip}: [{}]", log.join(", ")), got, Some(want));
    }
}
"""

P.append(dict(
    slug="fix-packed-zip-header", title="Fix: an unaligned ZIP header", mode="fix", level="medium", stage="pick-the-representation",
    tags=["repr(packed)", "repr(C)", "E0793", "unaligned access", "zero-copy parsing"],
    teaches=["`#[repr(C)]` pads fields to their alignment; an on-disk format with a `u32` at offset 14 needs `#[repr(C, packed)]`.",
             "A packed struct has alignment 1, which is what makes casting a `&[u8]` at any offset to it sound.",
             "E0793: no references to packed fields, including the hidden ones in `format!` and `&self` methods; copy the value out (`{ self.x }`, an accessor, `read_unaligned`)."],
    statement="""
        A backup tool lists ZIP archives without unpacking them: `LocalHeader::view` casts the bytes in place to
        a `LocalHeader` and `entries` walks header → name → extra field → data → next header.

        It returns garbage. A local header is 30 bytes with `crc32` at offset **14**, but `#[repr(C)]` pads
        `crc32` to offset 16, making the struct 32 bytes with alignment 4. `view`'s `SAFETY` comment claims
        alignment 1, which is also false, so any header at an odd offset is undefined behaviour (debug builds
        catch it as a misaligned-pointer panic).

        Make `LocalHeader` match the format: **30 bytes, alignment 1**, fields at their on-disk offsets.
        Then fix what that breaks without changing the API: `view`, the accessors, `is_stored`, `describe`
        and `entries` behave as documented, and `LocalHeader` stays `Debug`, `PartialEq`, `Eq` and `Hash`.
    """,
    examples=[("size_of::<LocalHeader>(), align_of::<LocalHeader>()", "30, 1"),
              ("LocalHeader::view(&archive[1..]) for a header at offset 1", "the right crc32 and sizes")],
    constraints=["headers are little-endian", "archives may start with junk before the first header (a self-extractor stub)", "keep the unsafe cast in view; no copying the header out"],
    starter=zip_code(repr_line="#[repr(C)]", derive="#[derive(Debug, PartialEq, Eq, Hash)]", fixed=False),
    solution=zip_code(),
    visible=[
        ZIP_HELPER,
        T("thirty_bytes_align_one", "size_of::<LocalHeader>(), align_of::<LocalHeader>()", "(std::mem::size_of::<LocalHeader>(), std::mem::align_of::<LocalHeader>())", "(30, 1)"),
        T("view_reads_fields", "view(local(\"a.txt\", [], 5 bytes, method 8, crc 0xCAFEF00D))", "(h.crc32(), h.compressed_size(), h.uncompressed_size(), h.name_len(), h.method())", "(0xCAFEF00D, 5, 15, 5, 8)",
          setup='let bytes = local("a.txt", &[], b"hello", 8, 0xCAFE_F00D);\nlet h = LocalHeader::view(&bytes).unwrap();'),
        T("view_at_odd_offset", "the same header behind one byte of junk: view(&bytes[1..])", "(h.crc32(), h.name_len())", "(0xCAFEF00D, 5)",
          setup='let mut bytes = vec![0xEE];\nbytes.extend(local("a.txt", &[], b"hello", 8, 0xCAFE_F00D));\nlet h = LocalHeader::view(&bytes[1..]).unwrap();'),
        T("describe_and_is_stored", "describe() and is_stored() of a stored 4-byte entry with crc 0xABCD", "(h.describe(), h.is_stored())", '("crc 0000abcd, 4 -> 12 bytes".to_string(), true)',
          setup='let bytes = local("x", &[], b"data", 0, 0xABCD);\nlet h = LocalHeader::view(&bytes).unwrap();'),
        T("walk_entries", "entries of [\"a.txt\": \"hello\", \"dir/b\": \"xyz\"] then a central directory", "entries(&archive).unwrap().iter().map(|e| (e.name, e.data)).collect::<Vec<_>>()",
          'vec![(&b"a.txt"[..], &b"hello"[..]), (&b"dir/b"[..], &b"xyz"[..])]',
          setup='let mut archive = local("a.txt", &[], b"hello", 0, 1);\narchive.extend(local("dir/b", &[], b"xyz", 0, 2));\narchive.extend_from_slice(b"PK\\x01\\x02...");'),
        T("view_rejects", "view of 29 bytes, and of 30 bytes without the signature", "(LocalHeader::view(&bytes[..29]).is_some(), LocalHeader::view(&zeros).is_some())", "(false, false)",
          setup='let bytes = local("", &[], b"", 0, 0);\nlet zeros = [0u8; 30];'),
    ],
    hidden=[
        ZIP_HELPER,
        T("extra_field_skipped", "entries of one file with a 7-byte extra field", "entries(&archive).unwrap().iter().map(|e| (e.name, e.crc32, e.data)).collect::<Vec<_>>()",
          'vec![(&b"n"[..], 7, &b"payload"[..])]',
          setup='let archive = local("n", &[1, 2, 3, 4, 5, 6, 7], b"payload", 8, 7);'),
        T("every_offset", "the same header at offsets 0 to 7", "crcs", "vec![0x0102_0304; 8]",
          setup='let mut crcs = Vec::new();\nfor off in 0..8 {\n    let mut bytes = vec![0; off];\n    bytes.extend(local("f", &[], b"z", 0, 0x0102_0304));\n    crcs.push(LocalHeader::view(&bytes[off..]).unwrap().crc32());\n}'),
        T("header_is_eq_hash_debug", "two views of equal headers: ==, a HashSet of both, Debug", "(a == b, set.len(), format!(\"{:?}\", a).starts_with(\"LocalHeader\"))", "(true, 1, true)",
          setup='let (x, y) = (local("f", &[], b"z", 0, 9), local("f", &[], b"z", 0, 9));\nlet (a, b) = (LocalHeader::view(&x).unwrap(), LocalHeader::view(&y).unwrap());\nlet set: std::collections::HashSet<&LocalHeader> = [a, b].into_iter().collect();'),
        T("empty_archive", "entries of [] and of a lone central directory", '(entries(&[]), entries(b"PK\\x01\\x02xx"))', "(Some(vec![]), Some(vec![]))"),
        T("truncated_data", "a header promising 5 bytes of data followed by 4", "entries(&archive[..archive.len() - 1])", "None",
          setup='let archive = local("a", &[], b"hello", 0, 1);'),
        T("large_values", "crc 0xFFFFFFFF and a 60000-byte entry", "(h.crc32(), h.compressed_size(), h.describe())", '(u32::MAX, 60000, "crc ffffffff, 60000 -> 180000 bytes".to_string())',
          setup='let bytes = local("big", &[], &vec![7; 60000], 8, u32::MAX);\nlet h = LocalHeader::view(&bytes).unwrap();'),
        T("arrays_and_options", "size_of::<[LocalHeader; 2]>(), size_of::<Option<&LocalHeader>>()",
          "(std::mem::size_of::<[LocalHeader; 2]>(), std::mem::size_of::<Option<&LocalHeader>>())", "(60, 8)"),
        T("deflated_not_stored", "is_stored() for method 8", "LocalHeader::view(&local(\"a\", &[], b\"x\", 8, 0)).unwrap().is_stored()", "false"),
        ZIP_RANDOM,
    ],
    hints=[("approach", "The format has no padding: `crc32` sits at offset 14, which isn't a multiple of 4. Only a packed layout puts it there, and a packed struct has alignment 1."),
           ("rust", "`#[repr(C, packed)]` keeps the order and removes the padding. Then every reference to a field is an error (E0793): `format!(\"{}\", self.crc32)` and `self.method.eq(&0)` both borrow. Copy the value out instead: an accessor, or `{ self.crc32 }` in braces."),
           ("edge case", "`#[derive(Debug, PartialEq, Hash)]` still work on a packed struct: rustc makes them copy each field instead of borrowing it (so every field must be `Copy`). Reading a packed field through a raw pointer needs `ptr::read_unaligned(&raw const (*p).crc32)`.")],
    notes=("""`#[repr(C)]` gives C's layout, and C pads a `u32` to a multiple of 4, so the struct had `crc32` at 16, not 14, and was 32 bytes with alignment 4. `#[repr(C, packed)]` keeps the order and drops the padding: 30 bytes, alignment 1, every field at its on-disk offset. Alignment 1 is what makes `view` sound: casting `&[u8]` at any offset to `&LocalHeader` is only valid if `LocalHeader` needs no alignment, and in a debug build the old code panics with a misaligned-pointer check at odd offsets.

Packed has a price: a reference to a field might be unaligned, and `&u32` must always be aligned, so taking one is an error (E0793). References hide in `format!` arguments and `&self` methods like `eq`, so the fix is to copy each field out first (the accessors, or `{ self.crc32 }`). Derives keep working because rustc generates them to copy each field, which is also why a packed struct can't derive over a non-`Copy` field. The CPU pays for unaligned loads on some targets, which is fine for parsing a header once. With a raw pointer, use `ptr::read_unaligned(&raw const (*p).crc32)`.

Real parsers do the same: the `zip` and `object` crates read packed little-endian records in place (`object` uses `U32<LittleEndian>` byte-array fields, which have alignment 1 with no `packed` at all).""", "O(1) per header; O(n) for entries", "no copies: headers are read in place"),
    follow_up="The `object` crate avoids `repr(packed)` by using fields like `U32Bytes<LE>` (a `[u8; 4]`). What does that buy over packed, and what does it cost at each read?",
    source="ZIP APPNOTE 4.3.7 (local file header); the zip and object crates",
    related=["Y2", "Y3", "F7"],
    wrong=dict(
        packed_two=zip_code(repr_line="#[repr(C, packed(2))]"),
        ignores_extra=zip_code(extra="0"),
    ),
))

IR_OP = """
/// One of the interpreter's 256 registers.
pub type Reg = u8;

/// What the front end emits. Arithmetic wraps; `Lt` sets `dst` to 1 or 0; `BrIf` jumps when `cond` isn't 0;
/// `BrTable` jumps to `targets[index]`, or to `default` when `index` is negative or out of range.
#[derive(Clone, Debug, PartialEq)]
pub enum Op {
    Const { dst: Reg, value: i64 },
    Add { dst: Reg, a: Reg, b: Reg },
    Sub { dst: Reg, a: Reg, b: Reg },
    Mul { dst: Reg, a: Reg, b: Reg },
    Lt { dst: Reg, a: Reg, b: Reg },
    Jump { target: u32 },
    BrIf { cond: Reg, target: u32 },
    BrTable { index: Reg, targets: Vec<u32>, default: u32 },
    Ret { src: Reg },
}
"""

IR_NAIVE = IR_OP + """
/// What the interpreter runs, one per op. For now, the op itself.
pub type Inst = Op;

/// A function body: instructions indexed from 0.
pub struct Program {
    insts: Vec<Inst>,
}

impl Program {
    pub fn new() -> Program {
        Program { insts: Vec::new() }
    }

    /// Appends `op` and returns its index.
    pub fn push(&mut self, op: Op) -> u32 {
        self.insts.push(op);
        self.insts.len() as u32 - 1
    }

    pub fn len(&self) -> usize {
        self.insts.len()
    }

    pub fn is_empty(&self) -> bool {
        self.insts.is_empty()
    }

    /// Runs from instruction 0 with every register 0 until a `Ret`, and returns its value. `None` if
    /// control runs off the end or more than `fuel` instructions execute.
    pub fn run(&self, fuel: u64) -> Option<i64> {
        let mut regs = [0i64; 256];
        let mut pc = 0usize;
        for _ in 0..fuel {
            let inst = self.insts.get(pc)?;
            pc += 1;
            match inst {
                Op::Const { dst, value } => regs[*dst as usize] = *value,
                Op::Add { dst, a, b } => regs[*dst as usize] = regs[*a as usize].wrapping_add(regs[*b as usize]),
                Op::Sub { dst, a, b } => regs[*dst as usize] = regs[*a as usize].wrapping_sub(regs[*b as usize]),
                Op::Mul { dst, a, b } => regs[*dst as usize] = regs[*a as usize].wrapping_mul(regs[*b as usize]),
                Op::Lt { dst, a, b } => regs[*dst as usize] = (regs[*a as usize] < regs[*b as usize]) as i64,
                Op::Jump { target } => pc = *target as usize,
                Op::BrIf { cond, target } => {
                    if regs[*cond as usize] != 0 {
                        pc = *target as usize;
                    }
                }
                Op::BrTable { index, targets, default } => {
                    let i = regs[*index as usize];
                    pc = usize::try_from(i).ok().and_then(|i| targets.get(i)).copied().unwrap_or(*default) as usize;
                }
                Op::Ret { src } => return Some(regs[*src as usize]),
            }
        }
        None
    }
}
"""


def ir_compact(const_variant="Const { dst: Reg, k: u32 },", const_push="""            Op::Const { dst, value } => {
                self.consts.push(value);
                Inst::Const { dst, k: self.consts.len() as u32 - 1 }
            }""", const_run="Inst::Const { dst, k } => regs[dst as usize] = self.consts[k as usize],",
               table_variant="BrTable { index: Reg, table: u32 },", table_push="""            Op::BrTable { index, targets, default } => {
                // Default first, then the targets: one slice per table in a side pool.
                let mut table = Vec::with_capacity(targets.len() + 1);
                table.push(default);
                table.extend(targets);
                self.tables.push(table.into_boxed_slice());
                Inst::BrTable { index, table: self.tables.len() as u32 - 1 }
            }""", table_run="""Inst::BrTable { index, table } => {
                    let table = &self.tables[table as usize];
                    let i = regs[index as usize];
                    // Targets start at 1; anything negative or past the end takes the default at 0.
                    pc = usize::try_from(i).ok().and_then(|i| table.get(i + 1)).copied().unwrap_or(table[0]) as usize;
                }"""):
    return IR_OP + """
/// What the interpreter runs: 8 bytes. A tag byte and at most 7 bytes of operands laid out around it;
/// anything bigger (an `i64` constant, a jump table) lives in a side pool and is named by a `u32` index,
/// as Cranelift's `InstructionData` does with its constant and jump-table pools.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Inst {
    CONST_VARIANT
    Add { dst: Reg, a: Reg, b: Reg },
    Sub { dst: Reg, a: Reg, b: Reg },
    Mul { dst: Reg, a: Reg, b: Reg },
    Lt { dst: Reg, a: Reg, b: Reg },
    Jump { target: u32 },
    BrIf { cond: Reg, target: u32 },
    TABLE_VARIANT
    Ret { src: Reg },
}

/// A function body: instructions indexed from 0, plus the pools they point into.
pub struct Program {
    insts: Vec<Inst>,
    consts: Vec<i64>,
    tables: Vec<Box<[u32]>>,
}

impl Program {
    pub fn new() -> Program {
        Program { insts: Vec::new(), consts: Vec::new(), tables: Vec::new() }
    }

    /// Appends `op` and returns its index.
    pub fn push(&mut self, op: Op) -> u32 {
        let inst = match op {
CONST_PUSH
            Op::Add { dst, a, b } => Inst::Add { dst, a, b },
            Op::Sub { dst, a, b } => Inst::Sub { dst, a, b },
            Op::Mul { dst, a, b } => Inst::Mul { dst, a, b },
            Op::Lt { dst, a, b } => Inst::Lt { dst, a, b },
            Op::Jump { target } => Inst::Jump { target },
            Op::BrIf { cond, target } => Inst::BrIf { cond, target },
TABLE_PUSH
            Op::Ret { src } => Inst::Ret { src },
        };
        self.insts.push(inst);
        self.insts.len() as u32 - 1
    }

    pub fn len(&self) -> usize {
        self.insts.len()
    }

    pub fn is_empty(&self) -> bool {
        self.insts.is_empty()
    }

    /// Runs from instruction 0 with every register 0 until a `Ret`, and returns its value. `None` if
    /// control runs off the end or more than `fuel` instructions execute.
    pub fn run(&self, fuel: u64) -> Option<i64> {
        let mut regs = [0i64; 256];
        let mut pc = 0usize;
        for _ in 0..fuel {
            let inst = *self.insts.get(pc)?;
            pc += 1;
            match inst {
                CONST_RUN
                Inst::Add { dst, a, b } => regs[dst as usize] = regs[a as usize].wrapping_add(regs[b as usize]),
                Inst::Sub { dst, a, b } => regs[dst as usize] = regs[a as usize].wrapping_sub(regs[b as usize]),
                Inst::Mul { dst, a, b } => regs[dst as usize] = regs[a as usize].wrapping_mul(regs[b as usize]),
                Inst::Lt { dst, a, b } => regs[dst as usize] = (regs[a as usize] < regs[b as usize]) as i64,
                Inst::Jump { target } => pc = target as usize,
                Inst::BrIf { cond, target } => {
                    if regs[cond as usize] != 0 {
                        pc = target as usize;
                    }
                }
                TABLE_RUN
                Inst::Ret { src } => return Some(regs[src as usize]),
            }
        }
        None
    }
}
""".replace("CONST_VARIANT", const_variant).replace("CONST_PUSH", const_push).replace("CONST_RUN", const_run) \
       .replace("TABLE_VARIANT", table_variant).replace("TABLE_PUSH", table_push).replace("TABLE_RUN", table_run)


IR_MODEL = """
/// The reference interpreter, straight over the ops.
fn model(ops: &[Op], fuel: u64) -> Option<i64> {
    let mut regs = [0i64; 256];
    let mut pc = 0usize;
    for _ in 0..fuel {
        let op = ops.get(pc)?;
        pc += 1;
        let r = |x: &u8| regs[*x as usize];
        match op {
            Op::Const { dst, value } => regs[*dst as usize] = *value,
            Op::Add { dst, a, b } => regs[*dst as usize] = r(a).wrapping_add(r(b)),
            Op::Sub { dst, a, b } => regs[*dst as usize] = r(a).wrapping_sub(r(b)),
            Op::Mul { dst, a, b } => regs[*dst as usize] = r(a).wrapping_mul(r(b)),
            Op::Lt { dst, a, b } => regs[*dst as usize] = (r(a) < r(b)) as i64,
            Op::Jump { target } => pc = *target as usize,
            Op::BrIf { cond, target } => {
                if r(cond) != 0 {
                    pc = *target as usize;
                }
            }
            Op::BrTable { index, targets, default } => {
                let i = r(index);
                pc = if i >= 0 && (i as u64) < targets.len() as u64 { targets[i as usize] } else { *default } as usize;
            }
            Op::Ret { src } => return Some(r(src)),
        }
    }
    None
}

fn program(ops: &[Op]) -> Program {
    let mut p = Program::new();
    for op in ops {
        p.push(op.clone());
    }
    p
}
"""

IR_RANDOM = """
#[test]
fn random_programs_vs_model() {
    let mut rng = anneal_prelude::Rng::new(8209);
    let consts = [0i64, 1, -1, 7, 1 << 40, i64::MIN, i64::MAX, 4_294_967_297];
    for _ in 0..300 {
        let n = 1 + rng.below(14);
        let mut ops = Vec::new();
        for _ in 0..n {
            let reg = |rng: &mut anneal_prelude::Rng| rng.below(4) as u8;
            let target = rng.below(n + 1) as u32;
            let op = match rng.below(9) {
                0 | 1 => Op::Const { dst: reg(&mut rng), value: if rng.bool() { *rng.pick(&consts) } else { rng.int(-50, 50) } },
                2 => Op::Add { dst: reg(&mut rng), a: reg(&mut rng), b: reg(&mut rng) },
                3 => Op::Sub { dst: reg(&mut rng), a: reg(&mut rng), b: reg(&mut rng) },
                4 => Op::Mul { dst: reg(&mut rng), a: reg(&mut rng), b: reg(&mut rng) },
                5 => Op::Lt { dst: reg(&mut rng), a: reg(&mut rng), b: reg(&mut rng) },
                6 => Op::BrIf { cond: reg(&mut rng), target },
                7 => {
                    let k = rng.below(4);
                    let targets: Vec<u32> = rng.vec(k, 0, n as i64);
                    Op::BrTable { index: reg(&mut rng), targets, default: target }
                }
                _ => Op::Ret { src: reg(&mut rng) },
            };
            ops.push(op);
        }
        let fuel = rng.below(60) as u64;
        check!(format!("{ops:?}, run({fuel})"), program(&ops).run(fuel), model(&ops, fuel));
    }
}
"""

IR_SUM = """
/// sum = 0; i = 0; while i < n { sum += i * i; i += 1 }; return sum
fn sum_of_squares(n: i64) -> Vec<Op> {
    vec![
        Op::Const { dst: 0, value: 0 },         // 0: sum
        Op::Const { dst: 1, value: 0 },         // 1: i
        Op::Const { dst: 2, value: n },         // 2: n
        Op::Const { dst: 3, value: 1 },         // 3: one
        Op::Lt { dst: 4, a: 1, b: 2 },          // 4: i < n
        Op::BrIf { cond: 4, target: 7 },        // 5
        Op::Ret { src: 0 },                     // 6
        Op::Mul { dst: 5, a: 1, b: 1 },         // 7
        Op::Add { dst: 0, a: 0, b: 5 },         // 8
        Op::Add { dst: 1, a: 1, b: 3 },         // 9
        Op::Jump { target: 4 },                 // 10
    ]
}
"""

P.append(dict(
    slug="eight-byte-instructions", title="An 8-byte IR instruction", mode="fix", level="medium", stage="pick-the-representation",
    tags=["enum layout", "side tables", "u32 indices", "compiler IR", "interpreter"],
    teaches=["rustc lays each enum variant's fields out around the tag, so `{ u8, u32 }` after a tag byte is 8 bytes, not 12.",
             "Anything that doesn't fit (an `i64`, a `Vec`) moves to a side pool and the instruction keeps a `u32` index: no allocation per instruction, no fat pointer.",
             "Cranelift and rustc assert their instruction sizes (`InstructionData` is 16 bytes) because the size multiplies across every function compiled."],
    statement="""
        A JIT's interpreter tier stores a function as a `Vec<Inst>`. Today `Inst` is just `Op`: **32 bytes**,
        because one rare variant carries an `i64` and another a `Vec` of jump targets. The dispatch loop
        streams through instructions, so every byte of `Inst` costs cache space.

        Make `Inst` **8 bytes** (and `Option<Inst>` too). The front end still hands `push` an `Op`, and
        `run` behaves exactly as before: registers start at 0, arithmetic wraps, `BrTable` falls back to
        `default` when the index is negative or out of range, and `run` returns `None` when control runs
        off the end or `fuel` instructions have executed without a `Ret`.
    """,
    examples=[("size_of::<Inst>(), size_of::<Option<Inst>>()", "8, 8"),
              ("sum of i * i for i in 0..10, run(1000)", "Some(285)")],
    constraints=["up to 2³² − 1 instructions, constants and jump tables", "registers are u8"],
    starter=IR_NAIVE,
    solution=ir_compact(),
    visible=[
        IR_MODEL,
        IR_SUM,
        T("inst_is_8_bytes", "size_of::<Inst>(), size_of::<Option<Inst>>()", "(std::mem::size_of::<Inst>(), std::mem::size_of::<Option<Inst>>())", "(8, 8)"),
        T("loop_sum_of_squares", "sum of i * i for i in 0..10, run(1000)", "program(&sum_of_squares(10)).run(1000)", "Some(285)"),
        T("big_constant", "Const r0 = 1 << 40; Const r1 = -3; Mul r2 = r0 * r1; Ret r2", "p.run(10)", "Some(-3 * (1i64 << 40))",
          setup="let p = program(&[Op::Const { dst: 0, value: 1 << 40 }, Op::Const { dst: 1, value: -3 }, Op::Mul { dst: 2, a: 0, b: 1 }, Op::Ret { src: 2 }]);"),
        T("jump_table", "r0 = 2; br_table r0 [2, 4, 6] default 8; each target t does r1 = 10 * t and returns it", "p.run(10)", "Some(60)",
          setup="let mut ops = vec![Op::Const { dst: 0, value: 2 }, Op::BrTable { index: 0, targets: vec![2, 4, 6], default: 8 }];\nfor t in [2, 4, 6, 8] {\n    ops.push(Op::Const { dst: 1, value: 10 * t });\n    ops.push(Op::Ret { src: 1 });\n}\nlet p = program(&ops);"),
        T("runs_out", "an infinite loop with fuel 100, and running off the end", "(program(&[Op::Jump { target: 0 }]).run(100), program(&[Op::Const { dst: 0, value: 1 }]).run(100))", "(None, None)"),
    ],
    hidden=[
        IR_MODEL,
        IR_SUM,
        T("default_on_negative_and_large", "br_table with index -1 and with 2³² + 1, 2 targets", "(p(-1).run(10), p(4_294_967_297).run(10), p(1).run(10))", "(Some(30), Some(30), Some(20))",
          setup="let p = |i: i64| program(&[\n    Op::Const { dst: 0, value: i },\n    Op::BrTable { index: 0, targets: vec![2, 4], default: 6 },\n    Op::Const { dst: 1, value: 10 },\n    Op::Ret { src: 1 },\n    Op::Const { dst: 1, value: 20 },\n    Op::Ret { src: 1 },\n    Op::Const { dst: 1, value: 30 },\n    Op::Ret { src: 1 },\n]);"),
        T("empty_table", "br_table with no targets goes to default", "program(&[Op::BrTable { index: 0, targets: vec![], default: 2 }, Op::Ret { src: 5 }, Op::Const { dst: 0, value: 4 }, Op::Ret { src: 0 }]).run(10)", "Some(4)"),
        T("extreme_constants", "i64::MIN, i64::MAX: MAX + 1 wraps, MIN - 1 wraps", "p.run(10)", "Some(0)",
          setup="let p = program(&[\n    Op::Const { dst: 0, value: i64::MAX },\n    Op::Const { dst: 1, value: i64::MIN },\n    Op::Const { dst: 2, value: 1 },\n    Op::Add { dst: 3, a: 0, b: 2 },\n    Op::Sub { dst: 4, a: 1, b: 2 },\n    Op::Add { dst: 5, a: 3, b: 4 },\n    Op::Sub { dst: 6, a: 5, b: 5 },\n    Op::Ret { src: 6 },\n]);"),
        T("fuel_is_exact", "Const, Ret: fuel 1 runs out, fuel 2 returns", "(p.run(1), p.run(2), p.run(0))", "(None, Some(5), None)",
          setup="let p = program(&[Op::Const { dst: 0, value: 5 }, Op::Ret { src: 0 }]);"),
        T("push_returns_index", "push three ops", "(a, b, c, p.len(), p.is_empty())", "(0, 1, 2, 3, false)",
          setup="let mut p = Program::new();\nlet a = p.push(Op::Const { dst: 0, value: 1 });\nlet b = p.push(Op::BrTable { index: 0, targets: vec![0; 100], default: 0 });\nlet c = p.push(Op::Ret { src: 0 });"),
        T("empty_program", "Program::new().run(10)", "(Program::new().run(10), Program::new().is_empty())", "(None, true)"),
        T("high_registers", "registers 200 and 255", "program(&[Op::Const { dst: 255, value: 9 }, Op::Const { dst: 200, value: 4 }, Op::Lt { dst: 7, a: 200, b: 255 }, Op::Ret { src: 7 }]).run(10)", "Some(1)"),
        T("vec_of_a_million", "bytes a Vec<Inst> of 1_000_000 takes", "std::mem::size_of::<Inst>() * 1_000_000", "8_000_000"),
        T("loop_to_1000", "sum of i * i for i in 0..1000", "program(&sum_of_squares(1000)).run(100_000)", "Some(332_833_500)"),
        IR_RANDOM,
    ],
    hints=[("approach", "The tag takes a byte, which leaves 7 bytes of an 8-byte, 4-aligned value: room for a few `u8` registers and one `u32`. An `i64` or a `Vec` can't fit, so store those in pools on `Program` and keep a `u32` index in the instruction."),
           ("rust", "rustc lays out each variant separately after the tag, so `BrIf { cond: u8, target: u32 }` puts `cond` at byte 1 and `target` at byte 4: 8 bytes. `Box<[u32]>` is 16 bytes (pointer + length) and would make every instruction 24."),
           ("edge case", "Keep `BrTable`'s semantics exact: the index is an `i64`, so compare it before narrowing. `i as u32 as usize` turns 2³² + 1 into 1 instead of taking the default.")],
    notes=("""Enum layout works per variant: the tag goes first and each variant's fields are placed after it in whatever order packs them best, so a variant with a `u8` and a `u32` fits in 8 bytes with the tag in byte 0. What doesn't fit moves out: the `i64` constant into a `consts` pool, the jump table into a `tables` pool, each named by a `u32`. A `Box<[u32]>` in the variant would work but costs a fat pointer (16 bytes, so the instruction is 24) and one allocation per table; a pool index is 4 bytes and the pools are two vectors per function. `Option<Inst>` stays 8 because the tag has unused values.

This is how production IRs are built. Cranelift's `InstructionData` holds `Value`/`Block`/`JumpTable`/`Constant` entity indices (all `u32`) and has a test pinning it to 16 bytes; rustc wraps its hot enums in `static_assert_size!`. A function with 100k instructions is 800 KB here instead of 3.2 MB, and the dispatch loop fits 8 instructions per cache line instead of 2.""", "O(1) per instruction executed", "8 bytes per instruction + pools"),
    follow_up="Cranelift stores an instruction's result types and value lists outside `InstructionData` too. Where would you keep the argument list of a `Call` with any number of arguments, still at 8 bytes per instruction?",
    source="Cranelift InstructionData (cranelift-codegen ir/instructions.rs), rustc static_assert_size!",
    related=["F3", "L7"],
    wrong=dict(
        inline_constant=ir_compact(const_variant="Const { dst: Reg, value: i64 },", const_push="            Op::Const { dst, value } => Inst::Const { dst, value },",
                                   const_run="Inst::Const { dst, value } => regs[dst as usize] = value,").replace("#[derive(Clone, Copy, Debug, PartialEq, Eq)]\npub enum Inst", "#[derive(Clone, Copy, Debug, PartialEq, Eq)]\npub enum Inst"),
        slice_in_inst=ir_compact(table_variant="BrTable { index: Reg, table: &'static [u32] },", table_push="""            Op::BrTable { index, targets, default } => {
                let mut table = vec![default];
                table.extend(targets);
                Inst::BrTable { index, table: Box::leak(table.into_boxed_slice()) }
            }""", table_run="""Inst::BrTable { index, table } => {
                    let i = regs[index as usize];
                    pc = usize::try_from(i).ok().and_then(|i| table.get(i + 1)).copied().unwrap_or(table[0]) as usize;
                }"""),
        truncating_index=ir_compact(table_run="""Inst::BrTable { index, table } => {
                    let table = &self.tables[table as usize];
                    let i = regs[index as usize] as u32 as usize;
                    pc = table.get(i + 1).copied().unwrap_or(table[0]) as usize;
                }"""),
    ),
))

BOOK_COMMON = """
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Side {
    Bid,
    Ask,
}

impl Side {
    pub fn opposite(self) -> Side {
        match self {
            Side::Bid => Side::Ask,
            Side::Ask => Side::Bid,
        }
    }
}

/// A resting order's handle.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct OrderId(u64);

/// One execution against a resting (maker) order.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Fill {
    pub maker: OrderId,
    pub price: u32,
    pub qty: u64,
}
"""

BOOK_NAIVE = """
use std::collections::{BTreeMap, HashMap, VecDeque};
""" + BOOK_COMMON + """
/// Every resting order at one price on one side, oldest first. 96 bytes.
#[allow(dead_code)]
pub struct PriceLevel {
    price: i64,
    symbol: String,
    orders: VecDeque<OrderId>,
    total_qty: u64,
    last_update: Option<u64>,
    side: Side,
    active: bool,
}

impl PriceLevel {
    pub fn price(&self) -> u32 {
        self.price as u32
    }

    /// The quantity resting at this price.
    pub fn qty(&self) -> u64 {
        self.total_qty
    }

    /// How many orders rest at this price.
    pub fn count(&self) -> usize {
        self.orders.len()
    }

    /// When an order at this price was last added, cancelled or filled.
    pub fn last_update(&self) -> Option<u64> {
        self.last_update
    }
}

struct Resting {
    side: Side,
    price: u32,
    qty: u64,
}

/// A limit order book for one instrument, with price-time priority.
pub struct Book {
    symbol: String,
    bids: BTreeMap<u32, PriceLevel>,
    asks: BTreeMap<u32, PriceLevel>,
    orders: HashMap<OrderId, Resting>,
    next_id: u64,
}

impl Book {
    pub fn new(symbol: &str) -> Book {
        Book::with_capacity(symbol, 0)
    }

    /// Room for `orders` resting orders, reserved up front.
    pub fn with_capacity(symbol: &str, orders: usize) -> Book {
        Book { symbol: symbol.to_string(), bids: BTreeMap::new(), asks: BTreeMap::new(), orders: HashMap::with_capacity(orders), next_id: 0 }
    }

    pub fn symbol(&self) -> &str {
        &self.symbol
    }

    /// Resting orders on both sides.
    pub fn len(&self) -> usize {
        self.orders.len()
    }

    pub fn is_empty(&self) -> bool {
        self.orders.is_empty()
    }

    /// Rests an order for `qty` (more than 0) at `price`, behind every order already there.
    pub fn add(&mut self, side: Side, price: u32, qty: u64, ts: u64) -> OrderId {
        assert!(qty > 0, "orders need a quantity");
        let id = OrderId(self.next_id);
        self.next_id += 1;
        let levels = match side {
            Side::Bid => &mut self.bids,
            Side::Ask => &mut self.asks,
        };
        let symbol = &self.symbol;
        let level = levels.entry(price).or_insert_with(|| PriceLevel {
            price: price as i64,
            symbol: symbol.clone(),
            orders: VecDeque::new(),
            total_qty: 0,
            last_update: None,
            side,
            active: false,
        });
        level.orders.push_back(id);
        level.total_qty += qty;
        level.last_update = Some(ts);
        level.active = true;
        self.orders.insert(id, Resting { side, price, qty });
        id
    }

    /// Takes a resting order off the book. `false` if `id` isn't resting (filled, cancelled or unknown).
    pub fn cancel(&mut self, id: OrderId, ts: u64) -> bool {
        let Some(o) = self.orders.remove(&id) else {
            return false;
        };
        let levels = match o.side {
            Side::Bid => &mut self.bids,
            Side::Ask => &mut self.asks,
        };
        let level = levels.get_mut(&o.price).expect("a resting order's level exists");
        level.orders.retain(|&x| x != id);
        level.total_qty -= o.qty;
        level.last_update = Some(ts);
        if level.orders.is_empty() {
            levels.remove(&o.price);
        }
        true
    }

    pub fn level(&self, side: Side, price: u32) -> Option<&PriceLevel> {
        match side {
            Side::Bid => self.bids.get(&price),
            Side::Ask => self.asks.get(&price),
        }
    }

    /// The best level: the highest bid, or the lowest ask.
    pub fn best(&self, side: Side) -> Option<&PriceLevel> {
        match side {
            Side::Bid => self.bids.values().next_back(),
            Side::Ask => self.asks.values().next(),
        }
    }

    /// The orders resting at a price, oldest first, with their remaining quantity.
    pub fn orders_at(&self, side: Side, price: u32) -> Vec<(OrderId, u64)> {
        self.level(side, price).map_or(Vec::new(), |l| l.orders.iter().map(|id| (*id, self.orders[id].qty)).collect())
    }

    /// A market order: takes from the other side, best price first and oldest order first, until `qty`
    /// is filled or that side is empty.
    pub fn execute(&mut self, taker: Side, qty: u64, ts: u64) -> Vec<Fill> {
        let side = taker.opposite();
        let mut left = qty;
        let mut fills = Vec::new();
        while left > 0 {
            let levels = match side {
                Side::Bid => &mut self.bids,
                Side::Ask => &mut self.asks,
            };
            let best = match side {
                Side::Bid => levels.keys().next_back(),
                Side::Ask => levels.keys().next(),
            };
            let Some(price) = best.copied() else {
                break;
            };
            let level = levels.get_mut(&price).expect("just found it");
            while left > 0 {
                let Some(&id) = level.orders.front() else {
                    break;
                };
                let o = self.orders.get_mut(&id).expect("queued orders are resting");
                let take = o.qty.min(left);
                o.qty -= take;
                left -= take;
                level.total_qty -= take;
                fills.push(Fill { maker: id, price, qty: take });
                if o.qty == 0 {
                    level.orders.pop_front();
                    self.orders.remove(&id);
                }
            }
            level.last_update = Some(ts);
            if level.orders.is_empty() {
                levels.remove(&price);
            }
        }
        fills
    }
}
"""


def book_arena(level_ts="last_update: u64,", ts_get="Some(self.last_update)", ts_set="ts", link="""        let old_tail = level.tail;
        self.orders[slot.get()].prev = old_tail;
        match old_tail {
            Some(t) => self.orders[t.get()].next = Some(slot),
            None => level.head = Some(slot),
        }
        level.tail = Some(slot);""", id_bits="((self.orders[s.get()].gen as u64) << 32) | s.get() as u64",
               gen_check="o.live && o.gen == (id.0 >> 32) as u32"):
    return """
use std::collections::BTreeMap;
use std::num::NonZeroU32;
""" + BOOK_COMMON + """
/// An index into the book's order arena. Stored as `index + 1` in a `NonZeroU32`, so `Option<Slot>` is
/// 4 bytes.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Slot(NonZeroU32);

impl Slot {
    fn new(i: usize) -> Slot {
        Slot(NonZeroU32::new(i as u32 + 1).expect("fewer than u32::MAX orders"))
    }

    fn get(self) -> usize {
        self.0.get() as usize - 1
    }
}

/// Every resting order at one price on one side, oldest first. 32 bytes, half a cache line:
/// - the orders live in the book's arena, linked into a FIFO, so the level keeps only `head` and `tail`;
/// - the side is which map the level sits in, and the symbol belongs to the book;
/// - "active" is `count > 0` (empty levels are removed); prices are `u32` ticks;
/// - a level only exists once something touched it, so its timestamp is never missing.
pub struct PriceLevel {
    qty: u64,
    LEVEL_TS
    price: u32,
    count: u32,
    head: Option<Slot>,
    tail: Option<Slot>,
}

impl PriceLevel {
    pub fn price(&self) -> u32 {
        self.price
    }

    /// The quantity resting at this price.
    pub fn qty(&self) -> u64 {
        self.qty
    }

    /// How many orders rest at this price.
    pub fn count(&self) -> usize {
        self.count as usize
    }

    /// When an order at this price was last added, cancelled or filled.
    pub fn last_update(&self) -> Option<u64> {
        TS_GET
    }
}

/// One order in the arena. A freed slot joins the free list through `next`, and its generation moves
/// on, so an old `OrderId` for the slot stops matching.
struct Order {
    qty: u64,
    price: u32,
    gen: u32,
    prev: Option<Slot>,
    next: Option<Slot>,
    side: Side,
    live: bool,
}

/// A limit order book for one instrument, with price-time priority.
pub struct Book {
    symbol: Box<str>,
    bids: BTreeMap<u32, PriceLevel>,
    asks: BTreeMap<u32, PriceLevel>,
    orders: Vec<Order>,
    free: Option<Slot>,
    live: usize,
}

impl Book {
    pub fn new(symbol: &str) -> Book {
        Book::with_capacity(symbol, 0)
    }

    /// Room for `orders` resting orders, reserved up front.
    pub fn with_capacity(symbol: &str, orders: usize) -> Book {
        Book { symbol: symbol.into(), bids: BTreeMap::new(), asks: BTreeMap::new(), orders: Vec::with_capacity(orders), free: None, live: 0 }
    }

    pub fn symbol(&self) -> &str {
        &self.symbol
    }

    /// Resting orders on both sides.
    pub fn len(&self) -> usize {
        self.live
    }

    pub fn is_empty(&self) -> bool {
        self.live == 0
    }

    /// The low 32 bits are the slot, the high 32 its generation.
    fn id_of(&self, s: Slot) -> OrderId {
        OrderId(ID_BITS)
    }

    fn resolve(&self, id: OrderId) -> Option<Slot> {
        let i = (id.0 & 0xFFFF_FFFF) as usize;
        let o = self.orders.get(i)?;
        (GEN_CHECK).then(|| Slot::new(i))
    }

    /// A slot for `order`: the head of the free list, or a new one at the end.
    fn alloc(&mut self, order: Order) -> Slot {
        self.live += 1;
        match self.free {
            Some(s) => {
                let old = &mut self.orders[s.get()];
                self.free = old.next;
                *old = Order { gen: old.gen, ..order };
                s
            }
            None => {
                self.orders.push(order);
                Slot::new(self.orders.len() - 1)
            }
        }
    }

    /// Rests an order for `qty` (more than 0) at `price`, behind every order already there.
    pub fn add(&mut self, side: Side, price: u32, qty: u64, ts: u64) -> OrderId {
        assert!(qty > 0, "orders need a quantity");
        let slot = self.alloc(Order { qty, price, gen: 0, prev: None, next: None, side, live: true });
        let levels = match side {
            Side::Bid => &mut self.bids,
            Side::Ask => &mut self.asks,
        };
        let level = levels.entry(price).or_insert(PriceLevel { qty: 0, last_update: TS_SET, price, count: 0, head: None, tail: None });
LINK
        level.count += 1;
        level.qty += qty;
        level.last_update = TS_SET;
        self.id_of(slot)
    }

    /// Unlinks `slot` from its level (removing the level if it empties) and frees it: O(1).
    fn remove(&mut self, slot: Slot, ts: u64) {
        let o = &self.orders[slot.get()];
        let (side, price, prev, next, qty) = (o.side, o.price, o.prev, o.next, o.qty);
        let levels = match side {
            Side::Bid => &mut self.bids,
            Side::Ask => &mut self.asks,
        };
        let level = levels.get_mut(&price).expect("a resting order's level exists");
        match prev {
            Some(p) => self.orders[p.get()].next = next,
            None => level.head = next,
        }
        match next {
            Some(n) => self.orders[n.get()].prev = prev,
            None => level.tail = prev,
        }
        level.count -= 1;
        level.qty -= qty;
        level.last_update = TS_SET;
        if level.count == 0 {
            levels.remove(&price);
        }
        let o = &mut self.orders[slot.get()];
        o.live = false;
        o.gen = o.gen.wrapping_add(1);
        o.next = self.free;
        self.free = Some(slot);
        self.live -= 1;
    }

    /// Takes a resting order off the book. `false` if `id` isn't resting (filled, cancelled or unknown).
    pub fn cancel(&mut self, id: OrderId, ts: u64) -> bool {
        match self.resolve(id) {
            Some(slot) => {
                self.remove(slot, ts);
                true
            }
            None => false,
        }
    }

    pub fn level(&self, side: Side, price: u32) -> Option<&PriceLevel> {
        match side {
            Side::Bid => self.bids.get(&price),
            Side::Ask => self.asks.get(&price),
        }
    }

    /// The best level: the highest bid, or the lowest ask.
    pub fn best(&self, side: Side) -> Option<&PriceLevel> {
        match side {
            Side::Bid => self.bids.values().next_back(),
            Side::Ask => self.asks.values().next(),
        }
    }

    /// The orders resting at a price, oldest first, with their remaining quantity.
    pub fn orders_at(&self, side: Side, price: u32) -> Vec<(OrderId, u64)> {
        let mut out = Vec::new();
        let mut cur = self.level(side, price).and_then(|l| l.head);
        while let Some(s) = cur {
            out.push((self.id_of(s), self.orders[s.get()].qty));
            cur = self.orders[s.get()].next;
        }
        out
    }

    /// A market order: takes from the other side, best price first and oldest order first, until `qty`
    /// is filled or that side is empty.
    pub fn execute(&mut self, taker: Side, qty: u64, ts: u64) -> Vec<Fill> {
        let side = taker.opposite();
        let mut left = qty;
        let mut fills = Vec::new();
        while left > 0 {
            let Some(level) = self.best(side) else {
                break;
            };
            let (price, head) = (level.price, level.head.expect("empty levels are removed"));
            let take = self.orders[head.get()].qty.min(left);
            fills.push(Fill { maker: self.id_of(head), price, qty: take });
            left -= take;
            if take == self.orders[head.get()].qty {
                self.remove(head, ts);
            } else {
                self.orders[head.get()].qty -= take;
                let levels = match side {
                    Side::Bid => &mut self.bids,
                    Side::Ask => &mut self.asks,
                };
                let level = levels.get_mut(&price).expect("just found it");
                level.qty -= take;
                level.last_update = TS_SET;
            }
        }
        fills
    }
}
""".replace("LEVEL_TS", level_ts).replace("TS_GET", ts_get).replace("TS_SET", ts_set).replace("LINK", link).replace("ID_BITS", id_bits).replace("GEN_CHECK", gen_check)


BOOK_MODEL = """
/// The book as a list of resting orders in arrival order, and each level's last update.
#[derive(Default)]
struct Model {
    live: Vec<(OrderId, Side, u32, u64)>,
    touched: std::collections::HashMap<(Side, u32), u64>,
}

impl Model {
    fn gone(&mut self, side: Side, price: u32) {
        if !self.live.iter().any(|o| o.1 == side && o.2 == price) {
            self.touched.remove(&(side, price));
        }
    }

    fn cancel(&mut self, id: OrderId, ts: u64) -> bool {
        let Some(i) = self.live.iter().position(|o| o.0 == id) else {
            return false;
        };
        let (_, side, price, _) = self.live.remove(i);
        self.touched.insert((side, price), ts);
        self.gone(side, price);
        true
    }

    fn execute(&mut self, taker: Side, qty: u64, ts: u64) -> Vec<Fill> {
        let side = taker.opposite();
        let mut left = qty;
        let mut fills = Vec::new();
        while left > 0 {
            let prices = self.live.iter().filter(|o| o.1 == side).map(|o| o.2);
            let best = if side == Side::Bid { prices.max() } else { prices.min() };
            let Some(price) = best else {
                break;
            };
            let i = self.live.iter().position(|o| o.1 == side && o.2 == price).unwrap();
            let take = self.live[i].3.min(left);
            fills.push(Fill { maker: self.live[i].0, price, qty: take });
            left -= take;
            self.touched.insert((side, price), ts);
            if take == self.live[i].3 {
                self.live.remove(i);
                self.gone(side, price);
            } else {
                self.live[i].3 -= take;
            }
        }
        fills
    }

    fn orders_at(&self, side: Side, price: u32) -> Vec<(OrderId, u64)> {
        self.live.iter().filter(|o| o.1 == side && o.2 == price).map(|o| (o.0, o.3)).collect()
    }
}

/// Every level of `book` in 95..=105 against the model: (qty, count, last_update), the queue, the bests.
fn compare(book: &Book, model: &Model, ctx: &str) {
    for side in [Side::Bid, Side::Ask] {
        for price in 95..=105 {
            let got = book.level(side, price).map(|l| (l.price(), l.qty(), l.count(), l.last_update()));
            let queue = model.orders_at(side, price);
            let want = (!queue.is_empty()).then(|| (price, queue.iter().map(|o| o.1).sum::<u64>(), queue.len(), model.touched.get(&(side, price)).copied()));
            check!(format!("{ctx}: level({side:?}, {price})"), got, want);
            check!(format!("{ctx}: orders_at({side:?}, {price})"), book.orders_at(side, price), queue);
        }
        let prices = model.live.iter().filter(|o| o.1 == side).map(|o| o.2);
        let want = if side == Side::Bid { prices.max() } else { prices.min() };
        check!(format!("{ctx}: best({side:?})"), book.best(side).map(|l| l.price()), want);
    }
    check!(format!("{ctx}: len()"), book.len(), model.live.len());
}
"""

BOOK_RANDOM = """
#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(8210);
    for _ in 0..60 {
        let mut book = Book::new("BTC-USD");
        let mut model = Model::default();
        let mut ever: Vec<OrderId> = Vec::new();
        let mut log = Vec::new();
        for ts in 1..=40u64 {
            let side = if rng.bool() { Side::Bid } else { Side::Ask };
            match rng.below(5) {
                0 | 1 => {
                    let price = rng.int(95, 105) as u32;
                    let qty = rng.int(1, 9) as u64;
                    log.push(format!("add({side:?}, {price}, {qty})"));
                    let id = book.add(side, price, qty, ts);
                    check!(format!("{}: the id is new", log.join(", ")), ever.contains(&id), false);
                    ever.push(id);
                    model.live.push((id, side, price, qty));
                    model.touched.insert((side, price), ts);
                }
                2 | 3 if !ever.is_empty() => {
                    let id = *rng.pick(&ever);
                    log.push(format!("cancel(#{})", ever.iter().position(|&x| x == id).unwrap()));
                    check!(log.join(", "), book.cancel(id, ts), model.cancel(id, ts));
                }
                _ => {
                    let qty = rng.int(1, 25) as u64;
                    log.push(format!("execute({side:?}, {qty})"));
                    check!(log.join(", "), book.execute(side, qty, ts), model.execute(side, qty, ts));
                }
            }
            compare(&book, &model, &log.join(", "));
        }
    }
}
"""

P.append(dict(
    slug="shrink-a-price-level", title="Shrink a price level to 32 bytes", mode="fix", level="medium", stage="pick-the-representation",
    tags=["order book", "intrusive list", "arena", "niche", "generational index", "allocation"],
    teaches=["Every field of a hot struct needs a reason: remove what's derivable (side, active), what belongs to the parent (symbol), and what can be narrowed (`u32` ticks, `Option<Slot>` in 4 bytes).",
             "An intrusive FIFO through an arena replaces a `VecDeque` per level: the level holds `head` and `tail`, cancels are O(1), and nothing allocates once the arena has room.",
             "Arena slots are reused, so handles carry a generation: a stale `OrderId` must not cancel the order that took its slot."],
    statement="""
        A matching engine keeps one `PriceLevel` per price on each side of the book, and a busy instrument has
        thousands of them. Each level is **96 bytes**: a copy of the symbol, a `VecDeque` of order ids that
        allocates as it grows, an `Option<u64>` timestamp, the side, an `active` flag. Cancels scan the queue.

        Shrink `PriceLevel` to **32 bytes** with the same public API and behaviour (price-time priority,
        `level`, `best`, `orders_at`, `execute`, `cancel`), and:

        - once `Book::with_capacity(n)` has run, adding and cancelling orders at an **existing** level makes
          **no allocation**, as long as at most `n` orders rest;
        - `cancel` is O(1) (a level may hold 100 000 orders);
        - an `OrderId` stays unique: cancelling a filled or cancelled order returns `false` and touches nothing.

        Timestamps are any `u64`; prices are `u32` ticks; quantities are `u64` and never 0.
    """,
    examples=[("size_of::<PriceLevel>()", "32"),
              ("asks: 5 @ 101, 3 @ 100, 4 @ 100; execute(Bid, 6)", "fills 3 @ 100 (2nd order), 3 @ 100 (3rd order)")],
    constraints=["at most u32::MAX − 1 orders rest at once", "timestamps are passed in, not read from a clock"],
    starter=BOOK_NAIVE,
    solution=book_arena(),
    visible=[
        T("level_is_32_bytes", "size_of::<PriceLevel>()", "std::mem::size_of::<PriceLevel>()", "32"),
        T("price_time_priority", "asks: a 5 @ 101, b 3 @ 100, c 4 @ 100; execute(Bid, 6)", "(fills, book.best(Side::Ask).map(|l| (l.price(), l.qty(), l.count())), book.orders_at(Side::Ask, 100))",
          "(vec![Fill { maker: b, price: 100, qty: 3 }, Fill { maker: c, price: 100, qty: 3 }], Some((100, 1, 1)), vec![(c, 1)])",
          setup="let mut book = Book::new(\"ETH-USD\");\nlet _a = book.add(Side::Ask, 101, 5, 1);\nlet b = book.add(Side::Ask, 100, 3, 2);\nlet c = book.add(Side::Ask, 100, 4, 3);\nlet fills = book.execute(Side::Bid, 6, 4);"),
        T("cancel_from_the_middle", "bids x, y, z at 99 (qty 1, 2, 3); cancel y twice", "(first, second, book.orders_at(Side::Bid, 99), book.level(Side::Bid, 99).map(|l| (l.qty(), l.count(), l.last_update())))",
          "(true, false, vec![(x, 1), (z, 3)], Some((4, 2, Some(7))))",
          setup="let mut book = Book::new(\"ETH-USD\");\nlet x = book.add(Side::Bid, 99, 1, 1);\nlet y = book.add(Side::Bid, 99, 2, 2);\nlet z = book.add(Side::Bid, 99, 3, 3);\nlet first = book.cancel(y, 7);\nlet second = book.cancel(y, 8);"),
        T("no_allocation_at_a_level", "with_capacity(1000): first order at 100, then 500 adds, 200 cancels, 100 adds at 100: allocations", "(n.count, book.len(), book.level(Side::Bid, 100).map(|l| l.count()))",
          "(0, 401, Some(401))",
          setup="let mut book = Book::with_capacity(\"ETH-USD\", 1000);\nbook.add(Side::Bid, 100, 1, 0);\nlet mut ids = Vec::with_capacity(600);\nlet (_, n) = anneal_prelude::allocs(|| {\n    for t in 0..500 {\n        ids.push(book.add(Side::Bid, 100, 1 + t % 7, t));\n    }\n    for i in 0..200 {\n        book.cancel(ids[i * 2], 600);\n    }\n    for t in 0..100 {\n        book.add(Side::Bid, 100, 2, 700 + t);\n    }\n});"),
        T("symbol_and_empty_book", "Book::new(\"ETH-USD\"), then execute(Ask, 5)", "(book.symbol(), book.best(Side::Bid).is_none(), book.is_empty(), fills)", '("ETH-USD", true, true, vec![])',
          setup="let mut book = Book::new(\"ETH-USD\");\nlet fills = book.execute(Side::Ask, 5, 1);"),
        T("partial_fill_keeps_its_place", "ask a 5 @ 100; execute(Bid, 2); then ask b 1 @ 100", "(fills, book.orders_at(Side::Ask, 100))",
          "(vec![Fill { maker: a, price: 100, qty: 2 }], vec![(a, 3), (b, 1)])",
          setup="let mut book = Book::new(\"ETH-USD\");\nlet a = book.add(Side::Ask, 100, 5, 1);\nlet fills = book.execute(Side::Bid, 2, 2);\nlet b = book.add(Side::Ask, 100, 1, 3);"),
    ],
    hidden=[
        BOOK_MODEL,
        T("sweep_both_levels", "asks 2 @ 100, 3 @ 101; execute(Bid, 10) takes everything", "(fills.len(), fills.iter().map(|f| f.qty).sum::<u64>(), book.best(Side::Ask).is_none(), book.len())",
          "(2, 5, true, 0)",
          setup="let mut book = Book::new(\"X\");\nbook.add(Side::Ask, 100, 2, 1);\nbook.add(Side::Ask, 101, 3, 2);\nlet fills = book.execute(Side::Bid, 10, 3);"),
        T("best_bid_is_highest", "bids at 90, 95, 93", "book.best(Side::Bid).map(|l| l.price())", "Some(95)",
          setup="let mut book = Book::new(\"X\");\nfor p in [90, 95, 93] {\n    book.add(Side::Bid, p, 1, 1);\n}"),
        T("stale_id_after_reuse", "add a, cancel a, add b (reusing a's slot), cancel a again", "(again, book.orders_at(Side::Ask, 50), book.len(), a != b)", "(false, vec![(b, 9)], 1, true)",
          setup="let mut book = Book::new(\"X\");\nlet a = book.add(Side::Ask, 50, 4, 1);\nbook.cancel(a, 2);\nlet b = book.add(Side::Ask, 50, 9, 3);\nlet again = book.cancel(a, 4);"),
        T("filled_order_cant_cancel", "bid m 5 @ 10; execute(Ask, 5); cancel m", "(book.cancel(m, 3), book.len(), book.level(Side::Bid, 10).is_none())", "(false, 0, true)",
          setup="let mut book = Book::new(\"X\");\nlet m = book.add(Side::Bid, 10, 5, 1);\nbook.execute(Side::Ask, 5, 2);"),
        T("partial_fill_touches_level", "ask 10 @ 7 at t=1; execute(Bid, 4) at t=9", "book.level(Side::Ask, 7).map(|l| (l.qty(), l.count(), l.last_update()))", "Some((6, 1, Some(9)))",
          setup="let mut book = Book::new(\"X\");\nbook.add(Side::Ask, 7, 10, 1);\nbook.execute(Side::Bid, 4, 9);"),
        T("extremes", "bid u32::MAX with qty 2⁶²; ask 0 with qty 1", "(book.best(Side::Bid).map(|l| (l.price(), l.qty())), book.best(Side::Ask).map(|l| l.price()))",
          "(Some((u32::MAX, 1 << 62)), Some(0))",
          setup="let mut book = Book::new(\"X\");\nbook.add(Side::Bid, u32::MAX, 1 << 62, u64::MAX);\nbook.add(Side::Ask, 0, 1, 0);"),
        T("cancel_unknown", "cancel an id from another book", "(book.cancel(foreign, 1), book.len())", "(false, 1)",
          setup="let mut other = Book::new(\"Y\");\nother.add(Side::Bid, 1, 1, 1);\nlet foreign = other.add(Side::Bid, 1, 1, 1);\nlet mut book = Book::new(\"X\");\nbook.add(Side::Bid, 1, 1, 1);"),
        T("sides_are_separate", "bid and ask at the same price 100", "(book.level(Side::Bid, 100).map(|l| l.qty()), book.level(Side::Ask, 100).map(|l| l.qty()))", "(Some(3), Some(4))",
          setup="let mut book = Book::new(\"X\");\nbook.add(Side::Bid, 100, 3, 1);\nbook.add(Side::Ask, 100, 4, 1);"),
        """
        #[test]
        fn cancel_is_constant_time() {
            let mut book = Book::with_capacity("X", 100_000);
            let mut ids: Vec<OrderId> = (0..100_000u64).map(|t| book.add(Side::Bid, 500, 1, t)).collect();
            let mut rng = anneal_prelude::Rng::new(8211);
            rng.shuffle(&mut ids);
            let cancelled = ids.iter().filter(|&&id| book.cancel(id, 1)).count();
            check!("100000 orders at one price, cancelled in random order", (cancelled, book.len(), book.best(Side::Bid).is_none()), (100_000, 0, true));
        }
        """,
        BOOK_RANDOM,
    ],
    hints=[("approach", "List what each byte is for. The symbol is the book's; the side is which map you're in; `active` is `count > 0`; the price fits in `u32`. The queue is the big one: keep the orders in one arena `Vec` and link each level's orders through it, so the level only stores `head` and `tail`."),
           ("rust", "Arena indices as `NonZeroU32` (`index + 1`) make `Option<Slot>` 4 bytes, so head, tail, count and price fit in 16 bytes next to `qty` and the timestamp. A level only exists after something touched it, so the timestamp doesn't need to be an `Option` (16 bytes) at all."),
           ("edge case", "Freed slots go on a free list and get reused, so an `OrderId` must carry the slot's generation: bump it on free and check it on cancel, or a stale id cancels someone else's order.")],
    notes=("""A 96-byte level is mostly things it doesn't need. The symbol is the same for every level, so it moves to the book. The side is implied by which map holds the level, `active` is `count > 0`, and prices fit in `u32` ticks. `Option<u64>` is 16 bytes because `u64` has no niche, but a level only exists once an order touched it, so the timestamp is a plain `u64`. The `VecDeque` (32 bytes plus its own allocation) becomes an intrusive FIFO: orders live in one arena `Vec`, each with `prev`/`next` slots, and the level keeps `head` and `tail` as `Option<Slot>`, which the `NonZeroU32` niche keeps at 4 bytes each. The result is `qty`, `last_update`, `price`, `count`, `head`, `tail`: 8 + 8 + 4 + 4 + 4 + 4 = 32 bytes, two levels per cache line.

Behaviour improves with the layout: cancel unlinks in O(1) instead of scanning, freed slots are reused through a free list threaded through `next`, and once the arena is reserved no add or cancel allocates. Reuse brings the ABA problem, so each `OrderId` packs the slot with a generation that moves on when the slot is freed. Real engines (LMAX-style exchange engines and the order books in trading firms' market-data handlers) use exactly this: pooled order nodes, intrusive per-level queues, and levels in an array or tree keyed by tick.""", "O(log L) to find a level, O(1) to link or unlink an order", "32 bytes per level + one arena slot per order"),
    follow_up="Prices cluster near the touch. How would you replace the `BTreeMap` with an array indexed by tick offset from a moving base, and what happens when the price walks off the end of it?",
    source="exchange matching engines (LMAX Disruptor-style order books), intrusive lists in the Linux kernel",
    related=["F3", "D14", "D5"],
    perf=dict(allocs=True),
    wrong=dict(
        optional_timestamp=book_arena(level_ts="last_update: Option<u64>,", ts_get="self.last_update", ts_set="Some(ts)"),
        newest_first=book_arena(link="""        let old_head = level.head;
        self.orders[slot.get()].next = old_head;
        match old_head {
            Some(h) => self.orders[h.get()].prev = Some(slot),
            None => level.tail = Some(slot),
        }
        level.head = Some(slot);"""),
        no_generation=book_arena(id_bits="s.get() as u64", gen_check="o.live"),
    ),
))

STAGES = [
    ("size-it", "Size it", "easy"),
    ("pick-the-representation", "Pick the representation", "medium"),
]

for p in P:
    if p.get("mode", "write") == "write":
        p.pop("rules", None)

if __name__ == "__main__":
    n = write_track("f2-data-layout", "F2", "Data layout", "F", "sde3", 2,
                    "How many bytes a value takes and where they sit: padding, niches, enum tags, fat and thin pointers, inline storage, packed records, and laying data out for the cache.",
                    STAGES, P)
    print("F2", n)
