from _c import C
M_R, M_1A = "00-rust-on-ramp", "01-disk-manager"
CH = []

CH.append(C("r-c3", M_R, "92-challenge-a-bit-set", "build", "Challenge: a bit set", "easy", "stages_r::sr_c3",
  ["storing many yes/no answers in machine words","shifts and masks, with indexes that may be out of range"],
  ["shifts-masks-and-bit-tricks","bytes-endianness-and-views"],
  "`BitSet` in `src/rust_primer/bits.rs`: a fixed-capacity set of small integers stored one bit each in `u64` words, with `set`, `clear`, `test`, `count`, an ascending iterator, `first_clear`, and `union_with`.",
  "Free-space maps, null bitmaps, visibility maps and Bloom filters are all bit sets. A bit set uses an eighth of the memory of a `Vec<bool>` and does set operations a word at a time, and the details (the last word, indexes past the end) are where the bugs are.",
  ["`new(capacity)` holds indexes `0..capacity`; every bit starts clear.","`set(i)` and `clear(i)` return true if the bit changed. An index at or past the capacity changes nothing and returns false; `test` of such an index is false.","`count()` is the number of set bits; `iter()` yields set indexes in increasing order; `first_clear()` is the smallest index below the capacity that is clear.","`union_with(&other)` sets every bit that is set in `other` (indexes of `other` past this capacity are ignored)."],
  ["`count()` equals the length of `iter()`.","No bit at or past the capacity is ever set (even in the unused part of the last word).","`iter()` is strictly increasing."],
  ["`set(i)` then `test(i)` is true; `clear(i)` then `test(i)` is false.","`set` twice reports a change only the first time.","`union_with` equals setting each index of the other set."],
  ["capacity 70: set(0), set(63), set(64), set(69) -> count 4, iter [0, 63, 64, 69]","set(70) -> false, count unchanged","first_clear on a full set -> None"],
  ["Bits across word boundaries (63, 64) and at the capacity edge.","Out-of-range indexes change nothing.","`first_clear` on empty, partly full and full sets.","A property against a `BTreeSet`."],
  src=("src/rust_primer/bits.rs", '''
//! A fixed-capacity set of small integers, one bit each.

pub struct BitSet {
    // @begin r-c3
    words: Vec<u64>,
    capacity: usize,
    //~ _bits: (),
    // @end
}

impl BitSet {
    pub fn new(capacity: usize) -> BitSet {
        // @begin r-c3
        BitSet { words: vec![0; capacity.div_ceil(64)], capacity }
        //~ todo!("r-c3: enough words for `capacity` bits, all clear")
        // @end
    }

    pub fn capacity(&self) -> usize {
        // @begin r-c3
        self.capacity
        //~ todo!("r-c3: how many indexes fit")
        // @end
    }

    /// Sets bit `i`; true if it was clear. Out of range: false, no change.
    pub fn set(&mut self, i: usize) -> bool {
        // @begin r-c3
        if i >= self.capacity {
            return false;
        }
        let (w, b) = (i / 64, i % 64);
        let was = self.words[w] >> b & 1 == 1;
        self.words[w] |= 1 << b;
        !was
        //~ todo!("r-c3: set the bit and say whether it changed")
        // @end
    }

    /// Clears bit `i`; true if it was set. Out of range: false, no change.
    pub fn clear(&mut self, i: usize) -> bool {
        // @begin r-c3
        if i >= self.capacity {
            return false;
        }
        let (w, b) = (i / 64, i % 64);
        let was = self.words[w] >> b & 1 == 1;
        self.words[w] &= !(1 << b);
        was
        //~ todo!("r-c3: clear the bit and say whether it changed")
        // @end
    }

    pub fn test(&self, i: usize) -> bool {
        // @begin r-c3
        i < self.capacity && self.words[i / 64] >> (i % 64) & 1 == 1
        //~ todo!("r-c3: is the bit set (false past the capacity)")
        // @end
    }

    pub fn count(&self) -> usize {
        // @begin r-c3
        self.words.iter().map(|w| w.count_ones() as usize).sum()
        //~ todo!("r-c3: how many bits are set")
        // @end
    }

    /// The set indexes, in increasing order.
    pub fn iter(&self) -> Box<dyn Iterator<Item = usize> + '_> {
        // @begin r-c3
        Box::new(self.words.iter().enumerate().flat_map(|(w, &word)| {
            (0..64).filter(move |b| word >> b & 1 == 1).map(move |b| w * 64 + b)
        }))
        //~ todo!("r-c3: the set indexes in increasing order")
        // @end
    }

    /// The smallest clear index below the capacity.
    pub fn first_clear(&self) -> Option<usize> {
        // @begin r-c3
        (0..self.capacity).find(|&i| !self.test(i))
        //~ todo!("r-c3: the first clear bit, if any")
        // @end
    }

    pub fn union_with(&mut self, other: &BitSet) {
        // @begin r-c3
        for i in other.iter() {
            self.set(i);
        }
        //~ todo!("r-c3: set every bit that is set in `other`")
        // @end
    }
}
'''),
  test=("tests/stages_r.rs", '''
use bustub::rust_primer::bits::BitSet;
use std::collections::BTreeSet;

#[test]
fn sr_c3_bits_across_word_boundaries() {
    let mut b = BitSet::new(70);
    for i in [0, 63, 64, 69] {
        assert!(b.set(i), "bit {i} was clear");
    }
    assert_eq!(b.count(), 4);
    assert_eq!(b.iter().collect::<Vec<_>>(), vec![0, 63, 64, 69]);
    assert!(b.test(63) && b.test(64) && !b.test(65));
}

#[test]
fn sr_c3_set_and_clear_report_whether_they_changed_anything() {
    let mut b = BitSet::new(10);
    assert!(b.set(3));
    assert!(!b.set(3), "already set");
    assert!(b.clear(3));
    assert!(!b.clear(3), "already clear");
    assert_eq!(b.count(), 0);
}

#[test]
fn sr_c3_indexes_past_the_capacity_change_nothing() {
    let mut b = BitSet::new(70);
    assert!(!b.set(70));
    assert!(!b.set(127), "inside the last word but past the capacity");
    assert!(!b.set(10_000));
    assert!(!b.test(70) && !b.test(10_000));
    assert!(!b.clear(70));
    assert_eq!(b.count(), 0);
    assert_eq!(b.capacity(), 70);
}

#[test]
fn sr_c3_first_clear_on_empty_partial_and_full_sets() {
    let mut b = BitSet::new(130);
    assert_eq!(b.first_clear(), Some(0));
    for i in 0..65 {
        b.set(i);
    }
    assert_eq!(b.first_clear(), Some(65));
    for i in 0..130 {
        b.set(i);
    }
    assert_eq!(b.first_clear(), None, "a full set has no clear bit, and the unused bits of the last word do not count");
    b.clear(100);
    assert_eq!(b.first_clear(), Some(100));
    assert_eq!(BitSet::new(0).first_clear(), None);
}

#[test]
fn sr_c3_union_sets_what_the_other_has() {
    let (mut a, mut b) = (BitSet::new(100), BitSet::new(200));
    a.set(1);
    b.set(1);
    b.set(99);
    b.set(150);
    a.union_with(&b);
    assert_eq!(a.iter().collect::<Vec<_>>(), vec![1, 99], "bit 150 is past a's capacity and is ignored");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: a bit set behaves like a `BTreeSet` of indexes below the capacity.
    #[test]
    fn sr_c3_property_a_bit_set_is_a_set(capacity in 0usize..200, ops in proptest::collection::vec((0u8..3, 0usize..220), 0..100)) {
        let mut b = BitSet::new(capacity);
        let mut m = BTreeSet::new();
        for (op, i) in ops {
            let inside = i < capacity;
            match op {
                0 => prop_assert_eq!(b.set(i), inside && m.insert(i)),
                1 => prop_assert_eq!(b.clear(i), inside && m.remove(&i)),
                _ => prop_assert_eq!(b.test(i), m.contains(&i)),
            }
            prop_assert_eq!(b.count(), m.len());
        }
        prop_assert_eq!(b.iter().collect::<Vec<_>>(), m.iter().copied().collect::<Vec<_>>());
        prop_assert_eq!(b.first_clear(), (0..capacity).find(|i| !m.contains(i)));
    }
}
''')))

CH.append(C("r-c4", M_R, "93-challenge-frames-from-a-stream", "build", "Challenge: frames from a stream", "medium", "stages_r::sr_c4",
  ["parsing a byte stream that arrives in arbitrary pieces","carrying partial input from one call to the next"],
  ["positional-io-and-short-reads","errors-as-values-with-result","bytes-endianness-and-views"],
  "`FrameDecoder` in `src/rust_primer/framing.rs`: bytes arrive from a socket or a log file in pieces of any size; each message (a **frame**) is a 2-byte big-endian length followed by that many payload bytes. `push` takes the next piece and returns the frames that are now complete; what is left over waits for the next call.",
  "A read never promises to return a whole message: TCP splits and joins at will, and a log can end mid-record after a crash. Every protocol parser and every recovery routine has this loop in it. Getting it right means the *same* frames come out however the bytes were cut.",
  ["`push(bytes)` appends to what is buffered and returns every complete frame, in order.","A frame announcing more than `max_frame` payload bytes is an error `TooLong { len }`; the decoder then forgets its buffered bytes.","`buffered()` is the number of bytes held that are not yet part of a returned frame."],
  ["`buffered()` is always less than one whole frame (2 + length of the frame being waited for).","Frames come out in the order their bytes went in; none is returned twice."],
  ["Cutting the same stream into pieces differently (one byte at a time, all at once, random cuts) gives the same frames.","Pushing an empty slice changes nothing.","The frames of a stream followed by more bytes start with the frames of the stream alone."],
  ["[0,3,a,b,c] -> [abc]","[0,3,a] then [b,c,0,1,z] -> [] then [abc, z]","[0,0] -> one empty frame","[255,255,...] with max 100 -> TooLong"],
  ["Whole frames, split frames, empty frames.","A header split across two pushes.","Too-long frames are an error and the decoder recovers.","A property: any chunking gives the same frames."],
  src=("src/rust_primer/framing.rs", '''
//! Frames from a stream of bytes that arrives in pieces: a 2-byte big-endian length, then that many bytes.

#[derive(Debug, PartialEq, Eq)]
pub enum FrameError {
    /// A frame announced more payload bytes than the decoder accepts.
    TooLong { len: usize },
}

pub struct FrameDecoder {
    // @begin r-c4
    buf: Vec<u8>,
    max_frame: usize,
    //~ _frames: (),
    // @end
}

impl FrameDecoder {
    pub fn new(max_frame: usize) -> FrameDecoder {
        // @begin r-c4
        FrameDecoder { buf: Vec::new(), max_frame }
        //~ todo!("r-c4: a decoder with nothing buffered")
        // @end
    }

    /// Adds the next piece of the stream; returns the frames (payloads) that are complete now.
    pub fn push(&mut self, bytes: &[u8]) -> Result<Vec<Vec<u8>>, FrameError> {
        // @begin r-c4
        self.buf.extend_from_slice(bytes);
        let mut frames = Vec::new();
        let mut at = 0;
        loop {
            let rest = &self.buf[at..];
            if rest.len() < 2 {
                break;
            }
            let len = u16::from_be_bytes([rest[0], rest[1]]) as usize;
            if len > self.max_frame {
                self.buf.clear();
                return Err(FrameError::TooLong { len });
            }
            if rest.len() < 2 + len {
                break;
            }
            frames.push(rest[2..2 + len].to_vec());
            at += 2 + len;
        }
        self.buf.drain(..at);
        Ok(frames)
        //~ todo!("r-c4: take every whole frame off the front of the buffer; keep the rest")
        // @end
    }

    /// Bytes held that are not yet part of a returned frame.
    pub fn buffered(&self) -> usize {
        // @begin r-c4
        self.buf.len()
        //~ todo!("r-c4: how many bytes are waiting")
        // @end
    }
}
'''),
  test=("tests/stages_r.rs", '''
use bustub::rust_primer::framing::{FrameDecoder, FrameError};

fn frame(payload: &[u8]) -> Vec<u8> {
    let mut v = (payload.len() as u16).to_be_bytes().to_vec();
    v.extend_from_slice(payload);
    v
}

#[test]
fn sr_c4_whole_frames_come_out_in_order() {
    let mut d = FrameDecoder::new(100);
    let mut bytes = frame(b"abc");
    bytes.extend(frame(b""));
    bytes.extend(frame(b"z"));
    assert_eq!(d.push(&bytes).unwrap(), vec![b"abc".to_vec(), b"".to_vec(), b"z".to_vec()]);
    assert_eq!(d.buffered(), 0);
}

#[test]
fn sr_c4_a_frame_split_across_pushes_waits_for_the_rest() {
    let mut d = FrameDecoder::new(100);
    assert_eq!(d.push(&[0, 3, b'a']).unwrap(), Vec::<Vec<u8>>::new());
    assert_eq!(d.buffered(), 3);
    assert_eq!(d.push(&[b'b', b'c', 0, 1, b'z']).unwrap(), vec![b"abc".to_vec(), b"z".to_vec()]);
}

#[test]
fn sr_c4_a_header_cut_in_the_middle_is_not_lost() {
    let mut d = FrameDecoder::new(100);
    assert!(d.push(&[0]).unwrap().is_empty());
    assert_eq!(d.buffered(), 1);
    assert_eq!(d.push(&[2, 9, 8]).unwrap(), vec![vec![9, 8]]);
}

#[test]
fn sr_c4_pushing_nothing_changes_nothing() {
    let mut d = FrameDecoder::new(100);
    d.push(&[0, 5, 1]).unwrap();
    assert!(d.push(&[]).unwrap().is_empty());
    assert_eq!(d.buffered(), 3);
}

#[test]
fn sr_c4_a_frame_that_is_too_long_is_an_error_and_the_decoder_recovers() {
    let mut d = FrameDecoder::new(10);
    assert_eq!(d.push(&[0, 11, 1, 2]), Err(FrameError::TooLong { len: 11 }));
    assert_eq!(d.buffered(), 0, "the buffered bytes are forgotten");
    assert_eq!(d.push(&frame(b"ok")).unwrap(), vec![b"ok".to_vec()]);
    assert!(d.push(&frame(&[7; 10])).is_ok(), "exactly the maximum is fine");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: however the stream is cut into pieces, the same frames come out, and what is left is less than one whole frame.
    #[test]
    fn sr_c4_property_chunking_does_not_change_the_frames(frames in proptest::collection::vec(proptest::collection::vec(any::<u8>(), 0..20), 0..8), cuts in proptest::collection::vec(1usize..12, 1..30), tail in 0usize..3) {
        let mut stream: Vec<u8> = frames.iter().flat_map(|f| frame(f)).collect();
        let whole = stream.len();
        stream.extend(std::iter::repeat_n(0u8, tail).take(tail.min(1))); // an unfinished header at the end
        let mut d = FrameDecoder::new(64);
        let mut got = Vec::new();
        let mut at = 0;
        let mut i = 0;
        while at < stream.len() {
            let n = cuts[i % cuts.len()].min(stream.len() - at);
            got.extend(d.push(&stream[at..at + n]).unwrap());
            at += n;
            i += 1;
        }
        prop_assert_eq!(got, frames);
        prop_assert_eq!(d.buffered(), stream.len() - whole);
    }
}
''')))

CH.append(C("r-c5", M_R, "94-challenge-the-offset-that-wraps", "debug", "Challenge: the offset that wraps", "easy", "stages_r::sr_c5",
  ["finding an integer-overflow bug that only shows on huge inputs"],
  ["overflow-and-checked-arithmetic","integers-and-casts","property-testing-and-fuzzing"],
  "`src/rust_primer/offsets.rs` has the arithmetic of a paged file: the byte offset of a page, and how many pages a number of bytes needs. It looks right on every ordinary input, and it has one bug that only shows on very large ones. Find it and fix it.",
  "Overflow bugs are invisible for years and then corrupt a file at the 4 GiB mark or the 16 EiB mark. In a storage engine the result is a write to the wrong place. Rust's `checked_*` operations make the intent explicit; the exercise is to notice where it was missing.",
  ["`page_offset(page, page_size)` is `page * page_size`, or `None` if it does not fit in a `u64` or `page_size` is 0.","`pages_for(bytes, page_size)` is the number of pages that hold `bytes` bytes (rounded up), `None` if `page_size` is 0."],
  ["A result that is `Some` is exactly the mathematical answer (checked with 128-bit arithmetic).","A result is never a wrapped value."],
  ["`pages_for(b, s) * s >= b` and `(pages_for(b, s) - 1) * s < b` for `b > 0`.","`page_offset(p, s)` grows with `p` until it overflows, and then stays `None`."],
  ["page_offset(3, 4096) = Some(12288)","page_offset(u64::MAX, 2) = None","pages_for(4097, 4096) = Some(2)","pages_for(u64::MAX, 4096) = Some(4503599627370496)"],
  ["Ordinary values.","Values at and past the overflow boundary.","A page size of 0.","A property against 128-bit arithmetic."],
  src=("src/rust_primer/offsets.rs", '''
//! The arithmetic of a file made of fixed-size pages.

/// The byte offset of page `page`: `page * page_size`, or `None` if that does not fit in a `u64` (or the page size is 0).
pub fn page_offset(page: u64, page_size: u64) -> Option<u64> {
    if page_size == 0 {
        return None;
    }
    page.checked_mul(page_size)
}

/// How many pages are needed to hold `bytes` bytes (rounded up); `None` if the page size is 0.
pub fn pages_for(bytes: u64, page_size: u64) -> Option<u64> {
    if page_size == 0 {
        return None;
    }
    // @begin r-c5
    Some(bytes.div_ceil(page_size))
    //~ Some(bytes.wrapping_add(page_size - 1) / page_size)
    // @end
}
'''),
  test=("tests/stages_r.rs", '''
use bustub::rust_primer::offsets::{page_offset, pages_for};

#[test]
fn sr_c5_ordinary_values() {
    assert_eq!(page_offset(3, 4096), Some(12288));
    assert_eq!(page_offset(0, 4096), Some(0));
    assert_eq!(pages_for(0, 4096), Some(0));
    assert_eq!(pages_for(1, 4096), Some(1));
    assert_eq!(pages_for(4096, 4096), Some(1));
    assert_eq!(pages_for(4097, 4096), Some(2));
}

#[test]
fn sr_c5_a_page_size_of_zero_has_no_answer() {
    assert_eq!(page_offset(5, 0), None);
    assert_eq!(pages_for(5, 0), None);
}

#[test]
fn sr_c5_an_offset_that_does_not_fit_is_none_not_a_wrapped_number() {
    assert_eq!(page_offset(u64::MAX, 2), None);
    assert_eq!(page_offset(1 << 63, 2), None);
    assert_eq!(page_offset((1 << 63) - 1, 2), Some(u64::MAX - 1));
}

#[test]
fn sr_c5_the_page_count_of_a_huge_file_is_right() {
    assert_eq!(pages_for(u64::MAX, 4096), Some(4_503_599_627_370_496), "2^64 / 4096 = 2^52, rounded up from just below");
    assert_eq!(pages_for(u64::MAX - 3, 4), Some((1 << 62) - 1), "2^64 - 4 is exactly 2^62 - 1 pages of 4");
    assert_eq!(pages_for(u64::MAX, 1), Some(u64::MAX));
    assert_eq!(pages_for(u64::MAX, u64::MAX), Some(1));
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 512, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: against 128-bit arithmetic, for ordinary and for huge values alike.
    #[test]
    fn sr_c5_property_the_arithmetic_matches_128_bit(a in prop_oneof![any::<u64>(), 0u64..5000, (u64::MAX - 5000)..=u64::MAX], s in prop_oneof![1u64..10, any::<u64>(), Just(4096u64)]) {
        let wide = a as u128 * s as u128;
        prop_assert_eq!(page_offset(a, s), if wide <= u64::MAX as u128 { Some(wide as u64) } else { None });
        let pages = (a as u128).div_ceil(s as u128);
        prop_assert_eq!(pages_for(a, s), Some(pages as u64));
    }
}
''')))

CH.append(C("1a-c3", M_1A, "92-challenge-a-page-bitmap", "build", "Challenge: a page bitmap", "easy", "stages_1a::s1a_c3",
  ["allocating and freeing page numbers from a bitmap","rejecting a double free and an out-of-range free"],
  ["slot-allocation-and-invariants","shifts-masks-and-bit-tricks"],
  "`PageBitmap` in `src/storage/disk/page_bitmap.rs`: a bitmap that hands out page numbers `0..capacity`: `allocate` gives the **lowest** free page, `free` gives one back, and both refuse nonsense instead of corrupting the map.",
  "The free-space map of a file is the other half of a disk manager. Handing out the lowest free page keeps the file compact, and a bitmap makes `allocate` cheap and `free` constant time. The real work is what happens on a double free: a bitmap that quietly accepts one will later hand the same page to two owners.",
  ["`allocate()` returns the lowest page that is free and marks it used, or `None` when all are used.","`free(page)` marks it free; `Err(DoubleFree)` if it is already free, `Err(OutOfRange)` if `page >= capacity`; the map is unchanged on error.","`is_allocated(page)` and `used()` report the state."],
  ["`used()` equals the number of allocated pages.","No page is allocated twice without a `free` in between.","Every allocated page is below the capacity."],
  ["After `free(p)`, the next `allocate()` returns `min(p, any lower free page)`.","Allocating until `None` then freeing everything restores the map.","`allocate` order is always increasing when nothing has been freed."],
  ["capacity 3: allocate -> 0, 1, 2, None","free(1); allocate -> 1","free(1) twice -> Err(DoubleFree)","free(3) -> Err(OutOfRange)"],
  ["The order of allocation and reuse of the lowest page.","Errors leave the map unchanged.","A property against a `BTreeSet` of free pages."],
  src=("src/storage/disk/page_bitmap.rs", '''
//! A bitmap of which pages of a file are in use.

#[derive(Debug, PartialEq, Eq)]
pub enum FreeError {
    DoubleFree,
    OutOfRange,
}

pub struct PageBitmap {
    // @begin 1a-c3
    used: Vec<bool>,
    count: usize,
    //~ _map: (),
    // @end
}

impl PageBitmap {
    pub fn new(capacity: usize) -> PageBitmap {
        // @begin 1a-c3
        PageBitmap { used: vec![false; capacity], count: 0 }
        //~ todo!("1a-c3: every page free")
        // @end
    }

    /// The lowest free page, marked used.
    pub fn allocate(&mut self) -> Option<usize> {
        // @begin 1a-c3
        let at = self.used.iter().position(|u| !u)?;
        self.used[at] = true;
        self.count += 1;
        Some(at)
        //~ todo!("1a-c3: find the lowest free page")
        // @end
    }

    pub fn free(&mut self, page: usize) -> Result<(), FreeError> {
        // @begin 1a-c3
        match self.used.get_mut(page) {
            None => Err(FreeError::OutOfRange),
            Some(false) => Err(FreeError::DoubleFree),
            Some(u) => {
                *u = false;
                self.count -= 1;
                Ok(())
            }
        }
        //~ todo!("1a-c3: give the page back, or say why not")
        // @end
    }

    pub fn is_allocated(&self, page: usize) -> bool {
        // @begin 1a-c3
        self.used.get(page).copied().unwrap_or(false)
        //~ todo!("1a-c3: is this page in use")
        // @end
    }

    pub fn used(&self) -> usize {
        // @begin 1a-c3
        self.count
        //~ todo!("1a-c3: how many pages are in use")
        // @end
    }
}
'''),
  test=("tests/stages_1a.rs", '''
use bustub::storage::disk::page_bitmap::{FreeError, PageBitmap};
use std::collections::BTreeSet;

#[test]
fn s1a_c3_pages_are_handed_out_in_increasing_order_until_none_is_left() {
    let mut b = PageBitmap::new(3);
    assert_eq!((b.allocate(), b.allocate(), b.allocate(), b.allocate()), (Some(0), Some(1), Some(2), None));
    assert_eq!(b.used(), 3);
}

#[test]
fn s1a_c3_the_lowest_free_page_is_reused_first() {
    let mut b = PageBitmap::new(5);
    for _ in 0..5 {
        b.allocate();
    }
    b.free(3).unwrap();
    b.free(1).unwrap();
    assert_eq!(b.allocate(), Some(1));
    assert_eq!(b.allocate(), Some(3));
    assert_eq!(b.allocate(), None);
}

#[test]
fn s1a_c3_a_double_free_and_an_out_of_range_free_are_refused() {
    let mut b = PageBitmap::new(4);
    let p = b.allocate().unwrap();
    assert_eq!(b.free(p), Ok(()));
    assert_eq!(b.free(p), Err(FreeError::DoubleFree));
    assert_eq!(b.free(2), Err(FreeError::DoubleFree), "never allocated, so already free");
    assert_eq!(b.free(4), Err(FreeError::OutOfRange));
    assert_eq!(b.used(), 0, "errors change nothing");
    assert_eq!((b.allocate(), b.allocate()), (Some(0), Some(1)), "and no page is handed out twice after a refused free");
}

#[test]
fn s1a_c3_is_allocated_tracks_the_state() {
    let mut b = PageBitmap::new(2);
    assert!(!b.is_allocated(0) && !b.is_allocated(9));
    b.allocate();
    assert!(b.is_allocated(0) && !b.is_allocated(1));
}

#[test]
fn s1a_c3_an_empty_bitmap_has_nothing_to_give() {
    let mut b = PageBitmap::new(0);
    assert_eq!(b.allocate(), None);
    assert_eq!(b.free(0), Err(FreeError::OutOfRange));
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: against a set of free pages, for any sequence of allocations and frees (including wrong ones).
    #[test]
    fn s1a_c3_property_a_bitmap_matches_a_set_of_free_pages(capacity in 0usize..12, ops in proptest::collection::vec(prop_oneof![Just(None), (0usize..14).prop_map(Some)], 0..60)) {
        let mut b = PageBitmap::new(capacity);
        let mut free: BTreeSet<usize> = (0..capacity).collect();
        for op in ops {
            match op {
                None => {
                    let want = free.iter().next().copied();
                    prop_assert_eq!(b.allocate(), want);
                    if let Some(p) = want { free.remove(&p); }
                }
                Some(p) => {
                    let want = if p >= capacity { Err(FreeError::OutOfRange) } else if free.contains(&p) { Err(FreeError::DoubleFree) } else { Ok(()) };
                    if want.is_ok() { free.insert(p); }
                    prop_assert_eq!(b.free(p), want);
                }
            }
            prop_assert_eq!(b.used(), capacity - free.len());
        }
    }
}
''')))

CH.append(C("1a-c4", M_1A, "93-challenge-snapshots", "build", "Challenge: snapshots", "medium", "stages_1a::s1a_c4",
  ["a store whose old versions stay readable","sharing unchanged data between versions instead of copying it"],
  ["persistent-data-structures-and-path-copying","model-based-testing"],
  "`VersionedPages` in `src/storage/disk/versioned_pages.rs`: a page store (pages are `u64` values here) where `snapshot()` returns an id that reads the store **as it was at that moment**, however much it is written afterwards.",
  "Backups, consistent reads and MVCC all need a view of the data that does not move. The simplest way to give one is to never overwrite: a write adds a new version, a snapshot remembers how far the versions had got. This is the idea under module 4a's version chains, in a form small enough to see whole.",
  ["`write(page, value)` makes `value` the current value of the page.","`read(page)` is the current value (`None` if never written).","`snapshot()` returns a new snapshot id; `read_at(snapshot, page)` is the value the page had when the snapshot was taken (`None` if unwritten then, or if the snapshot was dropped).","`drop_snapshot(id)` forgets it (false if unknown)."],
  ["A snapshot never changes after it is taken.","Snapshot ids are never reused.","`read` equals what `read_at` would give for a snapshot taken right now."],
  ["Writing after a snapshot changes `read` and never `read_at` of existing snapshots.","Two snapshots taken with no write in between read identically.","Dropping one snapshot does not affect another."],
  ["write(1, 10); s = snapshot(); write(1, 20) -> read(1) = 20, read_at(s, 1) = 10","read_at(s, 2) = None if page 2 was written only after the snapshot"],
  ["A snapshot stays fixed while the store changes.","Several snapshots at different times.","Dropped and unknown snapshots.","A property against a model that clones the whole map."],
  src=("src/storage/disk/versioned_pages.rs", '''
//! A page store whose snapshots read the past.

use std::collections::BTreeMap;

pub type SnapshotId = u64;

pub struct VersionedPages {
    // @begin 1a-c4
    /// page -> (version number, value), in increasing version order.
    versions: BTreeMap<u32, Vec<(u64, u64)>>,
    clock: u64,
    next_id: SnapshotId,
    /// snapshot id -> the clock when it was taken.
    snapshots: BTreeMap<SnapshotId, u64>,
    //~ _versions: (),
    // @end
}

impl VersionedPages {
    pub fn new() -> VersionedPages {
        // @begin 1a-c4
        VersionedPages { versions: BTreeMap::new(), clock: 0, next_id: 0, snapshots: BTreeMap::new() }
        //~ todo!("1a-c4: an empty store")
        // @end
    }

    pub fn write(&mut self, page: u32, value: u64) {
        // @begin 1a-c4
        self.clock += 1;
        self.versions.entry(page).or_default().push((self.clock, value));
        //~ todo!("1a-c4: add a version, never overwrite")
        // @end
    }

    pub fn read(&self, page: u32) -> Option<u64> {
        // @begin 1a-c4
        self.versions.get(&page).and_then(|v| v.last()).map(|&(_, x)| x)
        //~ todo!("1a-c4: the newest value")
        // @end
    }

    pub fn snapshot(&mut self) -> SnapshotId {
        // @begin 1a-c4
        let id = self.next_id;
        self.next_id += 1;
        self.snapshots.insert(id, self.clock);
        id
        //~ todo!("1a-c4: remember how far the store had got")
        // @end
    }

    pub fn read_at(&self, snapshot: SnapshotId, page: u32) -> Option<u64> {
        // @begin 1a-c4
        let at = *self.snapshots.get(&snapshot)?;
        self.versions.get(&page)?.iter().rev().find(|&&(ts, _)| ts <= at).map(|&(_, x)| x)
        //~ todo!("1a-c4: the newest value written no later than the snapshot")
        // @end
    }

    pub fn drop_snapshot(&mut self, id: SnapshotId) -> bool {
        // @begin 1a-c4
        self.snapshots.remove(&id).is_some()
        //~ todo!("1a-c4: forget the snapshot")
        // @end
    }
}

impl Default for VersionedPages {
    fn default() -> Self {
        VersionedPages::new()
    }
}
'''),
  test=("tests/stages_1a.rs", '''
use bustub::storage::disk::versioned_pages::VersionedPages;
use std::collections::HashMap;

#[test]
fn s1a_c4_a_snapshot_keeps_the_value_it_saw() {
    let mut s = VersionedPages::new();
    s.write(1, 10);
    let snap = s.snapshot();
    s.write(1, 20);
    assert_eq!((s.read(1), s.read_at(snap, 1)), (Some(20), Some(10)));
}

#[test]
fn s1a_c4_a_page_written_after_the_snapshot_is_absent_from_it() {
    let mut s = VersionedPages::new();
    let snap = s.snapshot();
    s.write(2, 5);
    assert_eq!((s.read(2), s.read_at(snap, 2)), (Some(5), None));
}

#[test]
fn s1a_c4_snapshots_taken_at_different_times_see_different_pasts() {
    let mut s = VersionedPages::new();
    s.write(0, 1);
    let a = s.snapshot();
    s.write(0, 2);
    let b = s.snapshot();
    s.write(0, 3);
    assert_eq!((s.read_at(a, 0), s.read_at(b, 0), s.read(0)), (Some(1), Some(2), Some(3)));
}

#[test]
fn s1a_c4_dropping_one_snapshot_leaves_the_others_alone() {
    let mut s = VersionedPages::new();
    s.write(0, 1);
    let a = s.snapshot();
    let b = s.snapshot();
    assert!(s.drop_snapshot(a));
    assert!(!s.drop_snapshot(a), "already dropped");
    assert!(!s.drop_snapshot(99));
    assert_eq!(s.read_at(a, 0), None);
    assert_eq!(s.read_at(b, 0), Some(1));
    let c = s.snapshot();
    assert!(c != a && c != b, "ids are never reused");
}

#[test]
fn s1a_c4_two_snapshots_with_nothing_written_between_them_agree() {
    let mut s = VersionedPages::new();
    for p in 0..5 {
        s.write(p, p as u64 * 7);
    }
    let (a, b) = (s.snapshot(), s.snapshot());
    for p in 0..6 {
        assert_eq!(s.read_at(a, p), s.read_at(b, p));
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: against a model that copies the whole map at every snapshot.
    #[test]
    fn s1a_c4_property_snapshots_equal_copies(ops in proptest::collection::vec((0u8..4, 0u32..6, any::<u64>()), 0..60)) {
        let mut s = VersionedPages::new();
        let mut now: HashMap<u32, u64> = HashMap::new();
        let mut copies: Vec<(u64, Option<HashMap<u32, u64>>)> = Vec::new();
        for (op, page, value) in ops {
            match op {
                0 | 1 => { s.write(page, value); now.insert(page, value); }
                2 => { let id = s.snapshot(); copies.push((id, Some(now.clone()))); }
                _ => {
                    let idx = (value as usize) % copies.len().max(1);
                    if let Some(c) = copies.get_mut(idx) {
                        prop_assert_eq!(s.drop_snapshot(c.0), c.1.is_some());
                        c.1 = None;
                    }
                }
            }
            for (id, copy) in &copies {
                for p in 0..6 {
                    prop_assert_eq!(s.read_at(*id, p), copy.as_ref().and_then(|m| m.get(&p).copied()));
                }
            }
            for p in 0..6 { prop_assert_eq!(s.read(p), now.get(&p).copied()); }
        }
    }
}
''')))

CH.append(C("1a-c5", M_1A, "94-challenge-the-slot-handed-out-twice", "debug", "Challenge: the slot handed out twice", "easy", "stages_1a::s1a_c5",
  ["finding a free-list bug from an invariant that two owners never share a slot"],
  ["slot-allocation-and-invariants","property-testing-and-fuzzing","checking-invariants"],
  "`src/storage/disk/slot_allocator.rs` hands out slot numbers and takes them back through a free list. It looks right, and under some sequences it hands the same slot to two different owners. Find the bug and fix it.",
  "A free list that is not defended against misuse eventually corrupts data: two pages that think they own the same place overwrite each other, and nothing reports it. The invariant (every live slot has one owner) is simple; what is hard is realising which call can break it.",
  ["`allocate()` returns a slot not currently in use: a freed one if there is one, otherwise the next fresh one.","`free(slot)` returns a slot that was in use; freeing a slot that is not in use (never allocated, or already freed) is ignored and returns false.","`in_use()` is the number of slots handed out and not freed."],
  ["No slot is in use twice: `allocate` never returns a slot that is in use.","`in_use()` equals allocations minus successful frees."],
  ["Freeing a slot twice has the same effect as freeing it once.","Freeing a slot that was never allocated changes nothing."],
  ["allocate -> 0, 1; free(0); free(0) (ignored); allocate -> 0; allocate -> 2 (not 0 again)"],
  ["Allocation and reuse in the ordinary case.","A double free followed by allocations.","A free of a slot never handed out.","A property: no slot is ever in use twice."],
  src=("src/storage/disk/slot_allocator.rs", '''
//! Slot numbers handed out from a counter and a free list.

pub struct SlotAllocator {
    next: usize,
    free_list: Vec<usize>,
    in_use: usize,
}

impl SlotAllocator {
    pub fn new() -> SlotAllocator {
        SlotAllocator { next: 0, free_list: Vec::new(), in_use: 0 }
    }

    pub fn allocate(&mut self) -> usize {
        self.in_use += 1;
        if let Some(slot) = self.free_list.pop() {
            return slot;
        }
        self.next += 1;
        self.next - 1
    }

    /// Takes `slot` back; false if it was not in use.
    pub fn free(&mut self, slot: usize) -> bool {
        // @begin 1a-c5
        if slot >= self.next || self.free_list.contains(&slot) {
            return false;
        }
        self.free_list.push(slot);
        self.in_use -= 1;
        true
        //~ self.free_list.push(slot);
        //~ self.in_use = self.in_use.saturating_sub(1);
        //~ true
        // @end
    }

    pub fn in_use(&self) -> usize {
        self.in_use
    }
}

impl Default for SlotAllocator {
    fn default() -> Self {
        SlotAllocator::new()
    }
}
'''),
  test=("tests/stages_1a.rs", '''
use bustub::storage::disk::slot_allocator::SlotAllocator;
use std::collections::HashSet;

#[test]
fn s1a_c5_slots_are_handed_out_and_reused() {
    let mut a = SlotAllocator::new();
    assert_eq!((a.allocate(), a.allocate(), a.allocate()), (0, 1, 2));
    assert!(a.free(1));
    assert_eq!(a.allocate(), 1, "a freed slot is reused before a fresh one");
    assert_eq!(a.in_use(), 3);
}

#[test]
fn s1a_c5_freeing_twice_is_the_same_as_once() {
    let mut a = SlotAllocator::new();
    a.allocate();
    a.allocate();
    assert!(a.free(0));
    assert!(!a.free(0), "already free");
    assert_eq!(a.in_use(), 1);
    let (x, y) = (a.allocate(), a.allocate());
    assert_ne!(x, y, "the freed slot must not be handed out twice");
}

#[test]
fn s1a_c5_a_slot_that_was_never_handed_out_cannot_be_freed() {
    let mut a = SlotAllocator::new();
    assert!(!a.free(5));
    assert_eq!(a.in_use(), 0);
    assert_eq!(a.allocate(), 0, "and it does not enter the free list");
}

#[test]
fn s1a_c5_in_use_counts_allocations_minus_frees() {
    let mut a = SlotAllocator::new();
    let s: Vec<_> = (0..5).map(|_| a.allocate()).collect();
    for &x in &s[..3] {
        a.free(x);
        a.free(x);
    }
    assert_eq!(a.in_use(), 2);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: whatever mix of allocations and frees (right and wrong), no slot is ever in use twice and the count is right.
    #[test]
    fn s1a_c5_property_no_slot_is_in_use_twice(ops in proptest::collection::vec(prop_oneof![Just(None), (0usize..8).prop_map(Some)], 0..80)) {
        let mut a = SlotAllocator::new();
        let mut live: HashSet<usize> = HashSet::new();
        for op in ops {
            match op {
                None => {
                    let s = a.allocate();
                    prop_assert!(live.insert(s), "slot {} handed out while still in use", s);
                }
                Some(s) => {
                    prop_assert_eq!(a.free(s), live.remove(&s));
                }
            }
            prop_assert_eq!(a.in_use(), live.len());
        }
    }
}
''')))
