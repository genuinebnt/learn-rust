//! Tests for module R (optional): the Rust a storage engine needs before module 1a: bytes and positional I/O, errors as values, ownership
//! shapes, shared state, and testing against a model.

use std::collections::VecDeque;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Duration;

use proptest::prelude::*;

use bustub::rust_primer::bytes::{pack_u32s, unpack_u32s, Header, PageFile, PAGE};
use bustub::rust_primer::records::{encode_records, load_records, parse_records, FormatError, LoadError, Record};
use bustub::rust_primer::ring::RingBuffer;
use bustub::rust_primer::shapes::{Slab, Stack};
use bustub::rust_primer::shared::{parallel_sum, BoundedQueue, IdGenerator};

fn temp_path(name: &str) -> std::path::PathBuf {
    let dir = std::env::temp_dir().join(format!("anneal-r-{}-{}", std::process::id(), name));
    let _ = std::fs::remove_file(&dir);
    dir
}

/// Runs `f` on its own thread and fails the test, instead of hanging, if it does not finish: a loop that never ends, or a thread waiting for a wake-up that never came.
fn finish_within<T: Send + 'static>(what: &str, f: impl FnOnce() -> T + Send + 'static) -> T {
    let (tx, rx) = std::sync::mpsc::channel();
    thread::spawn(move || {
        let _ = tx.send(std::panic::catch_unwind(std::panic::AssertUnwindSafe(f)));
    });
    match rx.recv_timeout(Duration::from_secs(10)) {
        Ok(Ok(value)) => value,
        Ok(Err(panic)) => std::panic::resume_unwind(panic),
        Err(_) => panic!("{what}: still waiting after 10 seconds. Something waits for a thing that never comes: a loop that never ends, or a thread nobody wakes."),
    }
}

// ---- r-01: bytes and positional I/O -------------------------------------------------------------------------------------------------------

fn page_of(byte: u8) -> [u8; PAGE] {
    [byte; PAGE]
}

#[test]
fn sr_01_a_header_is_sixteen_little_endian_bytes() {
    let h = Header { magic: 0x0102_0304, version: 0x0506, flags: 0x0708, len: 0x090A_0B0C_0D0E_0F10 };
    assert_eq!(
        h.to_bytes(),
        [0x04, 0x03, 0x02, 0x01, 0x06, 0x05, 0x08, 0x07, 0x10, 0x0F, 0x0E, 0x0D, 0x0C, 0x0B, 0x0A, 0x09],
        "magic, version, flags and len, each little-endian, one after the other"
    );
}

#[test]
fn sr_01_a_header_reads_back_and_wrong_sizes_are_refused() {
    let h = Header { magic: 0xDEAD_BEEF, version: 7, flags: 0xF00D, len: u64::MAX - 5 };
    assert_eq!(Header::from_bytes(&h.to_bytes()), Some(h), "Header::from_bytes(&h.to_bytes()) == Some(h)");
    assert_eq!(Header::from_bytes(&[0; 15]), None, "15 bytes are not a header");
    assert_eq!(Header::from_bytes(&[0; 17]), None, "17 bytes are not a header");
    assert_eq!(Header::from_bytes(&[]), None, "no bytes are not a header");
}

#[test]
fn sr_01_numbers_pack_four_bytes_each() {
    assert_eq!(pack_u32s(&[1, 256]), vec![1, 0, 0, 0, 0, 1, 0, 0], "1 and 256, little-endian");
    assert_eq!(pack_u32s(&[]), Vec::<u8>::new());
    assert_eq!(unpack_u32s(&[1, 0, 0, 0, 0, 1, 0, 0]), vec![1, 256]);
    assert_eq!(unpack_u32s(&[1, 0, 0, 0, 9, 9]), vec![1], "a last group of fewer than 4 bytes is ignored");
}

#[test]
fn sr_01_a_page_file_keeps_what_was_written_where_it_was_written() {
    finish_within("a page file keeps what was written where it was written", move || {
        let path = temp_path("pages");
        let file = PageFile::open(&path).unwrap();
        file.write_page(2, &page_of(0xAA)).unwrap();
        file.write_page(0, &page_of(0x11)).unwrap();
        assert_eq!(file.read_page(2).unwrap(), page_of(0xAA));
        assert_eq!(file.read_page(0).unwrap(), page_of(0x11));
        assert_eq!(file.read_page(1).unwrap(), page_of(0), "page 1 was never written: zeros (a hole in the file)");
        assert_eq!(file.page_count().unwrap(), 3, "pages 0 to 2 exist");
        let _ = std::fs::remove_file(&path);
    });
}

#[test]
fn sr_01_reading_beyond_the_end_gives_zeros_and_reopening_keeps_the_data() {
    finish_within("reading beyond the end gives zeros and reopening keeps the data", move || {
        let path = temp_path("reopen");
        {
            let file = PageFile::open(&path).unwrap();
            assert_eq!(file.page_count().unwrap(), 0, "a new file is empty");
            file.write_page(0, &page_of(7)).unwrap();
            assert_eq!(file.read_page(40).unwrap(), page_of(0), "far beyond the end of the file");
        }
        let file = PageFile::open(&path).unwrap();
        assert_eq!(file.read_page(0).unwrap(), page_of(7), "opening an existing file keeps its contents (do not truncate)");
        let _ = std::fs::remove_file(&path);
    });
}

#[test]
fn sr_01_a_partly_written_last_page_reads_with_zeros_after_its_bytes() {
    finish_within("a partly written last page reads with zeros after its bytes", move || {
        use std::io::Write;
        let path = temp_path("partial");
        std::fs::File::create(&path).unwrap().write_all(&[5u8; PAGE + 10]).unwrap();
        let file = PageFile::open(&path).unwrap();
        assert_eq!(file.page_count().unwrap(), 2, "256 + 10 bytes: one full page and a part of a second");
        let page = file.read_page(1).unwrap();
        assert_eq!(&page[..10], &[5u8; 10]);
        assert!(page[10..].iter().all(|&b| b == 0), "the part after the end of the file reads as zeros");
        let _ = std::fs::remove_file(&path);
    });
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 48, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: a header always reads back as written, and its bytes are what the format says.
    #[test]
    fn sr_01_property_headers_round_trip(magic in any::<u32>(), version in any::<u16>(), flags in any::<u16>(), len in any::<u64>()) {
        let h = Header { magic, version, flags, len };
        let bytes = h.to_bytes();
        prop_assert_eq!(&bytes[0..4], &magic.to_le_bytes()[..]);
        prop_assert_eq!(&bytes[8..16], &len.to_le_bytes()[..]);
        prop_assert_eq!(Header::from_bytes(&bytes), Some(h));
    }

    /// Property: numbers survive packing, and packing is four bytes per number.
    #[test]
    fn sr_01_property_numbers_round_trip(values in proptest::collection::vec(any::<u32>(), 0..64)) {
        let bytes = pack_u32s(&values);
        prop_assert_eq!(bytes.len(), values.len() * 4);
        prop_assert_eq!(unpack_u32s(&bytes), values);
    }
}

/// Property: a page file behaves like an array of pages that start as zeros.
#[test]
fn sr_01_property_a_page_file_is_an_array_of_pages() {
    use proptest::test_runner::{Config, TestRunner};
    finish_within("a page file is an array of pages", move || {
        let mut runner = TestRunner::new(Config { cases: 48, failure_persistence: None, ..Config::default() });
        let strategy = proptest::collection::vec((0u64..8, any::<u8>(), any::<bool>()), 1..40);
        let result = runner.run(&strategy, |ops| {
            let path = temp_path("prop");
            let file = PageFile::open(&path).unwrap();
            let mut model: Vec<[u8; PAGE]> = vec![[0; PAGE]; 8];
            let mut written = 0u64;
            for (index, byte, write) in ops {
                if write {
                    file.write_page(index, &page_of(byte)).unwrap();
                    model[index as usize] = page_of(byte);
                    written = written.max(index + 1);
                } else {
                    prop_assert_eq!(file.read_page(index).unwrap(), model[index as usize]);
                }
            }
            prop_assert_eq!(file.page_count().unwrap(), written);
            let _ = std::fs::remove_file(&path);
            Ok(())
        });
        if let Err(e) = result {
            panic!("{e}");
        }
    });
}

// ---- r-02: errors as values ---------------------------------------------------------------------------------------------------------------

fn rec(key: &str, value: &[u8]) -> Record {
    Record { key: key.to_string(), value: value.to_vec() }
}

#[test]
fn sr_02_records_are_a_length_header_then_the_key_then_the_value() {
    let bytes = encode_records(&[rec("ab", &[9, 8, 7])]).unwrap();
    assert_eq!(bytes, vec![2, 3, 0, b'a', b'b', 9, 8, 7], "key_len (u8), value_len (u16 little-endian), key, value");
    assert_eq!(encode_records(&[]).unwrap(), Vec::<u8>::new());
}

#[test]
fn sr_02_records_read_back_in_order() {
    let records = vec![rec("a", b"1"), rec("", b""), rec("héllo", &[0; 300])];
    let bytes = encode_records(&records).unwrap();
    assert_eq!(parse_records(&bytes), Ok(records));
    assert_eq!(parse_records(&[]), Ok(vec![]));
}

#[test]
fn sr_02_a_truncated_stream_says_where_and_how_much_is_missing() {
    let mut bytes = encode_records(&[rec("a", b"12"), rec("bc", b"xyz")]).unwrap();
    let first = 3 + 1 + 2;
    bytes.pop();
    assert_eq!(
        parse_records(&bytes),
        Err(FormatError::Truncated { at: first, needed: 3 + 2 + 3, have: 3 + 2 + 3 - 1 }),
        "the second record starts at byte {first} and is one byte short"
    );
    assert_eq!(parse_records(&[1, 0]), Err(FormatError::Truncated { at: 0, needed: 3, have: 2 }), "not even a whole header");
}

#[test]
fn sr_02_a_key_that_is_not_utf8_is_an_error_not_a_panic() {
    let bytes = vec![2, 0, 0, 0xFF, 0xFE];
    assert_eq!(parse_records(&bytes), Err(FormatError::BadKey { at: 0 }));
    let mut two = encode_records(&[rec("ok", b"")]).unwrap();
    let at = two.len();
    two.extend_from_slice(&[1, 0, 0, 0xC0]);
    assert_eq!(parse_records(&two), Err(FormatError::BadKey { at }), "the offset is where the bad record starts");
}

#[test]
fn sr_02_a_key_or_value_that_does_not_fit_is_refused() {
    let long_key = "k".repeat(256);
    assert_eq!(encode_records(&[rec(&long_key, b"")]), Err(FormatError::KeyTooLong { len: 256 }));
    assert!(encode_records(&[rec(&"k".repeat(255), b"")]).is_ok(), "255 bytes still fit");
    assert_eq!(encode_records(&[rec("k", &vec![0; 65536])]), Err(FormatError::ValueTooLong { len: 65536 }));
    assert!(encode_records(&[rec("k", &vec![0; 65535])]).is_ok());
}

#[test]
fn sr_02_errors_explain_themselves() {
    let e = FormatError::Truncated { at: 12, needed: 8, have: 3 };
    let text = e.to_string();
    assert!(text.contains("12") && text.contains('8') && text.contains('3'), "the message names its numbers: {text}");
    let text = FormatError::KeyTooLong { len: 300 }.to_string();
    assert!(text.contains("300"), "the message names its numbers: {text}");
}

#[test]
fn sr_02_a_load_error_keeps_its_cause_and_tells_the_two_failures_apart() {
    use std::error::Error;
    let missing = load_records(temp_path("does-not-exist"));
    match missing {
        Err(LoadError::Io(ref e)) => assert_eq!(e.kind(), std::io::ErrorKind::NotFound),
        other => panic!("a missing file is an I/O error, got {other:?}"),
    }
    let err = missing.unwrap_err();
    assert!(err.source().is_some(), "`source()` is the wrapped error");
    assert!(!err.to_string().is_empty());

    let path = temp_path("broken-records");
    std::fs::write(&path, [5, 0, 0, b'x']).unwrap();
    match load_records(&path) {
        Err(LoadError::Format(FormatError::Truncated { at: 0, .. })) => {}
        other => panic!("a truncated file is a format error, got {other:?}"),
    }
    std::fs::write(&path, encode_records(&[rec("a", b"b")]).unwrap()).unwrap();
    assert_eq!(load_records(&path).unwrap(), vec![rec("a", b"b")]);
    let _ = std::fs::remove_file(&path);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: records encode and parse back, whatever they hold.
    #[test]
    fn sr_02_property_records_round_trip(items in proptest::collection::vec(("\\PC{0,12}", proptest::collection::vec(any::<u8>(), 0..40)), 0..12)) {
        let records: Vec<Record> = items.into_iter().map(|(key, value)| Record { key, value }).collect();
        let bytes = encode_records(&records).unwrap();
        prop_assert_eq!(parse_records(&bytes), Ok(records));
    }

    /// Property: parsing never panics, whatever the bytes are; and every strict prefix of a good stream is either complete records or an error.
    #[test]
    fn sr_02_property_parsing_never_panics(bytes in proptest::collection::vec(any::<u8>(), 0..200)) {
        let _ = parse_records(&bytes);
    }

    #[test]
    fn sr_02_property_a_cut_stream_is_an_error_or_a_shorter_list(items in proptest::collection::vec(("[a-z]{0,6}", proptest::collection::vec(any::<u8>(), 0..10)), 1..8), cut in any::<prop::sample::Index>()) {
        let records: Vec<Record> = items.into_iter().map(|(key, value)| Record { key, value }).collect();
        let bytes = encode_records(&records).unwrap();
        let cut = cut.index(bytes.len());
        match parse_records(&bytes[..cut]) {
            Ok(parsed) => {
                prop_assert!(parsed.len() < records.len(), "a cut stream cannot hold every record");
                prop_assert_eq!(&parsed[..], &records[..parsed.len()]);
            }
            Err(FormatError::Truncated { at, needed, have }) => {
                prop_assert!(at <= cut && have < needed && at + have == cut, "the numbers describe what was left: at {at}, needed {needed}, have {have}, cut {cut}");
            }
            Err(other) => prop_assert!(false, "only Truncated is possible for ASCII keys, got {other:?}"),
        }
    }
}

// ---- r-03: ownership shapes ---------------------------------------------------------------------------------------------------------------

#[test]
fn sr_03_a_stack_pops_in_reverse_order() {
    let mut s = Stack::new();
    assert!(s.is_empty() && s.pop().is_none() && s.peek().is_none());
    for i in 1..=3 {
        s.push(i);
    }
    assert_eq!(s.len(), 3);
    assert_eq!(s.peek(), Some(&3));
    assert_eq!(s.pop(), Some(3));
    assert_eq!(s.pop(), Some(2));
    assert_eq!(s.pop(), Some(1));
    assert_eq!(s.pop(), None);
    assert_eq!(s.len(), 0);
}

#[test]
fn sr_03_peek_mut_changes_the_top_in_place() {
    let mut s = Stack::new();
    s.push(String::from("a"));
    s.push(String::from("b"));
    s.peek_mut().unwrap().push('!');
    assert_eq!(s.to_vec(), vec!["b!".to_string(), "a".to_string()]);
}

#[test]
fn sr_03_reverse_turns_the_stack_upside_down() {
    let mut s = Stack::new();
    for i in 0..5 {
        s.push(i);
    }
    s.reverse();
    assert_eq!(s.to_vec(), vec![0, 1, 2, 3, 4]);
    assert_eq!(s.len(), 5);
    let mut empty: Stack<i32> = Stack::new();
    empty.reverse();
    assert!(empty.is_empty());
}

#[test]
fn sr_03_values_are_moved_not_cloned_and_dropped_exactly_once() {
    use std::rc::Rc;
    let token = Rc::new(());
    {
        let mut s = Stack::new();
        for _ in 0..10 {
            s.push(Rc::clone(&token));
        }
        assert_eq!(Rc::strong_count(&token), 11, "pushing moves the Rc in: one count each, no extra clones");
        s.reverse();
        assert_eq!(Rc::strong_count(&token), 11, "reverse moves nodes, it does not clone values");
        drop(s.pop());
        assert_eq!(Rc::strong_count(&token), 10, "a popped value is dropped when the caller drops it");
    }
    assert_eq!(Rc::strong_count(&token), 1, "dropping the stack drops every value left in it");
}

#[test]
fn sr_03_a_very_long_stack_can_be_dropped() {
    // A stack overflow aborts the whole process, so the real work runs in a child process that this test starts again.
    if std::env::var_os("ANNEAL_R_DEEP_DROP").is_some() {
        let mut s = Stack::new();
        for i in 0..200_000u32 {
            s.push(i);
        }
        drop(s);
        return;
    }
    let exe = std::env::current_exe().unwrap();
    let out = std::process::Command::new(exe)
        .args(["sr_03_a_very_long_stack_can_be_dropped", "--exact", "--test-threads=1"])
        .env("ANNEAL_R_DEEP_DROP", "1")
        .output()
        .unwrap();
    assert!(
        out.status.success(),
        "dropping a stack of 200 000 nodes crashed the program (a recursive drop overflows the call stack): drop the nodes in a loop"
    );
}

#[test]
fn sr_03_a_slab_hands_out_handles_and_gives_values_back() {
    let mut slab = Slab::new();
    let a = slab.insert("a");
    let b = slab.insert("b");
    assert_eq!((slab.get(a), slab.get(b)), (Some(&"a"), Some(&"b")));
    assert_eq!(slab.len(), 2);
    *slab.get_mut(a).unwrap() = "A";
    assert_eq!(slab.get(a), Some(&"A"));
    assert_eq!(slab.remove(a), Some("A"));
    assert_eq!(slab.get(a), None, "a removed value is gone");
    assert_eq!(slab.remove(a), None, "removing twice finds nothing");
    assert_eq!(slab.len(), 1);
}

#[test]
fn sr_03_a_handle_to_a_removed_value_never_finds_the_value_that_reuses_its_slot() {
    let mut slab = Slab::new();
    let old = slab.insert(1);
    slab.remove(old);
    let new = slab.insert(2);
    assert_ne!(old, new, "same slot, other generation: the handles differ");
    assert_eq!(slab.get(old), None, "the old handle is dead even though its slot is in use again");
    assert_eq!(slab.get(new), Some(&2));
    assert_eq!(slab.remove(old), None);
    assert_eq!(slab.len(), 1);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: a stack is a vector that grows and shrinks at one end.
    #[test]
    fn sr_03_property_a_stack_is_a_vec(ops in proptest::collection::vec(prop_oneof![any::<i32>().prop_map(Some), Just(None)], 0..80)) {
        let mut stack = Stack::new();
        let mut model: Vec<i32> = Vec::new();
        for op in ops {
            match op {
                Some(v) => { stack.push(v); model.push(v); }
                None => prop_assert_eq!(stack.pop(), model.pop()),
            }
            prop_assert_eq!(stack.len(), model.len());
            prop_assert_eq!(stack.peek(), model.last());
        }
        let mut top_down = model.clone();
        top_down.reverse();
        prop_assert_eq!(stack.to_vec(), top_down);
        stack.reverse();
        prop_assert_eq!(stack.to_vec(), model);
    }

    /// Property: a slab is a map from handles to values; handles of removed values stay dead.
    #[test]
    fn sr_03_property_a_slab_is_a_map(ops in proptest::collection::vec((0u8..3, any::<u16>(), any::<prop::sample::Index>()), 0..120)) {
        let mut slab = Slab::new();
        let mut live: Vec<(bustub::rust_primer::shapes::Handle, u16)> = Vec::new();
        let mut dead = Vec::new();
        for (op, value, pick) in ops {
            match op {
                0 => live.push((slab.insert(value), value)),
                1 if !live.is_empty() => {
                    let (h, v) = live.swap_remove(pick.index(live.len()));
                    prop_assert_eq!(slab.remove(h), Some(v));
                    dead.push(h);
                }
                _ if !live.is_empty() => {
                    let (h, v) = live[pick.index(live.len())];
                    prop_assert_eq!(slab.get(h), Some(&v));
                }
                _ => {}
            }
            prop_assert_eq!(slab.len(), live.len());
            for h in &dead {
                prop_assert_eq!(slab.get(*h), None, "a dead handle stays dead");
            }
        }
    }
}

// ---- r-04: shared state -------------------------------------------------------------------------------------------------------------------

#[test]
fn sr_04_a_queue_gives_values_back_in_order() {
    let q = BoundedQueue::new(4);
    assert!(q.is_empty() && q.try_pop().is_none());
    for i in 0..3 {
        q.push(i).unwrap();
    }
    assert_eq!(q.len(), 3);
    assert_eq!((q.pop(), q.try_pop(), q.pop()), (Some(0), Some(1), Some(2)));
    assert!(q.try_pop().is_none());
}

#[test]
fn sr_04_a_closed_queue_refuses_pushes_and_drains_what_is_left() {
    let q = BoundedQueue::new(4);
    q.push(1).unwrap();
    q.push(2).unwrap();
    q.close();
    assert_eq!(q.push(3), Err(3), "push after close gives the value back");
    assert_eq!(q.pop(), Some(1));
    assert_eq!(q.pop(), Some(2));
    assert_eq!(q.pop(), None, "closed and empty: None, not waiting forever");
}

#[test]
fn sr_04_pop_waits_for_a_push_and_close_wakes_a_waiting_pop() {
    finish_within("pop waits for a push and close wakes a waiting pop", move || {
        let q = Arc::new(BoundedQueue::new(2));
        let waiting = {
            let q = Arc::clone(&q);
            thread::spawn(move || (q.pop(), q.pop()))
        };
        thread::sleep(Duration::from_millis(60));
        q.push(41).unwrap();
        thread::sleep(Duration::from_millis(60));
        q.close();
        assert_eq!(waiting.join().unwrap(), (Some(41), None), "the first pop waited for the push; the second was woken by close");
    });
}

#[test]
fn sr_04_push_waits_while_the_queue_is_full() {
    finish_within("push waits while the queue is full", move || {
        let q = Arc::new(BoundedQueue::new(1));
        q.push(1).unwrap();
        let done = Arc::new(AtomicBool::new(false));
        let pusher = {
            let (q, done) = (Arc::clone(&q), Arc::clone(&done));
            thread::spawn(move || {
                q.push(2).unwrap();
                done.store(true, Ordering::SeqCst);
            })
        };
        thread::sleep(Duration::from_millis(80));
        assert!(!done.load(Ordering::SeqCst), "the queue holds 1 value of 1: the second push must wait");
        assert_eq!(q.pop(), Some(1));
        pusher.join().unwrap();
        assert_eq!(q.pop(), Some(2));
    });
}

#[test]
fn sr_04_close_wakes_a_waiting_push_with_its_value() {
    finish_within("close wakes a waiting push with its value", move || {
        let q = Arc::new(BoundedQueue::new(1));
        q.push(1).unwrap();
        let pusher = {
            let q = Arc::clone(&q);
            thread::spawn(move || q.push(2))
        };
        thread::sleep(Duration::from_millis(60));
        q.close();
        assert_eq!(pusher.join().unwrap(), Err(2));
    });
}

#[test]
fn sr_04_ids_are_handed_out_once_each() {
    let ids = Arc::new(IdGenerator::new());
    assert_eq!((ids.next(), ids.next(), ids.next()), (0, 1, 2));
    let workers: Vec<_> = (0..4)
        .map(|_| {
            let ids = Arc::clone(&ids);
            thread::spawn(move || (0..2000).map(|_| ids.next()).collect::<Vec<_>>())
        })
        .collect();
    let mut all: Vec<u64> = workers.into_iter().flat_map(|w| w.join().unwrap()).collect();
    all.sort_unstable();
    all.dedup();
    assert_eq!(all.len(), 8000, "four threads took 2000 numbers each and no number was handed out twice");
    assert_eq!(ids.next(), 8003);
}

#[test]
fn sr_04_producers_and_consumers_lose_nothing() {
    finish_within("producers and consumers lose nothing", move || {
        let q = Arc::new(BoundedQueue::new(3));
        let producers: Vec<_> = (0..3u64)
            .map(|p| {
                let q = Arc::clone(&q);
                thread::spawn(move || {
                    for i in 0..500u64 {
                        q.push(p * 1000 + i).unwrap();
                    }
                })
            })
            .collect();
        let consumers: Vec<_> = (0..2)
            .map(|_| {
                let q = Arc::clone(&q);
                thread::spawn(move || {
                    let mut got = Vec::new();
                    while let Some(v) = q.pop() {
                        got.push(v);
                    }
                    got
                })
            })
            .collect();
        for p in producers {
            p.join().unwrap();
        }
        q.close();
        let mut got: Vec<u64> = consumers.into_iter().flat_map(|c| c.join().unwrap()).collect();
        got.sort_unstable();
        let mut want: Vec<u64> = (0..3u64).flat_map(|p| (0..500).map(move |i| p * 1000 + i)).collect();
        want.sort_unstable();
        assert_eq!(got, want, "every value pushed was popped exactly once");
    });
}

#[test]
fn sr_04_a_parallel_sum_is_the_sum() {
    let values: Vec<u64> = (1..=1000).collect();
    for threads in [0, 1, 3, 7, 1000, 5000] {
        assert_eq!(parallel_sum(&values, threads), 500_500, "{threads} threads");
    }
    assert_eq!(parallel_sum(&[], 4), 0);
    assert_eq!(parallel_sum(&[u64::MAX, 2], 2), 1, "the sum wraps");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 64, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: a parallel sum equals the sequential one, whatever the split.
    #[test]
    fn sr_04_property_parallel_sum_equals_sequential(values in proptest::collection::vec(any::<u64>(), 0..300), threads in 0usize..12) {
        let want = values.iter().fold(0u64, |a, &b| a.wrapping_add(b));
        prop_assert_eq!(parallel_sum(&values, threads), want);
    }
}

// ---- r-05: testing against a model --------------------------------------------------------------------------------------------------------

#[test]
fn sr_05_a_ring_buffer_is_first_in_first_out() {
    let mut r = RingBuffer::new(3);
    assert!(r.is_empty() && !r.is_full() && r.capacity() == 3);
    assert_eq!((r.pop(), r.front(), r.back()), (None, None, None));
    r.push('a').unwrap();
    r.push('b').unwrap();
    r.push('c').unwrap();
    assert!(r.is_full());
    assert_eq!((r.front(), r.back()), (Some(&'a'), Some(&'c')));
    assert_eq!((r.pop(), r.pop(), r.pop(), r.pop()), (Some('a'), Some('b'), Some('c'), None));
}

#[test]
fn sr_05_a_full_buffer_gives_the_value_back() {
    let mut r = RingBuffer::new(2);
    r.push(String::from("x")).unwrap();
    r.push(String::from("y")).unwrap();
    assert_eq!(r.push(String::from("z")), Err(String::from("z")), "refused, and the caller gets the value back");
    assert_eq!(r.len(), 2);
}

#[test]
fn sr_05_the_buffer_wraps_around_the_end_of_its_array() {
    let mut r = RingBuffer::new(3);
    for round in 0..10 {
        r.push(round * 2).unwrap();
        r.push(round * 2 + 1).unwrap();
        assert_eq!(r.pop(), Some(round * 2));
        assert_eq!(r.pop(), Some(round * 2 + 1));
    }
    r.push(100).unwrap();
    r.push(101).unwrap();
    r.push(102).unwrap();
    assert_eq!(r.iter().copied().collect::<Vec<_>>(), vec![100, 101, 102], "after many wraps the order is still the order of the pushes");
    assert_eq!(r.back(), Some(&102));
}

#[test]
fn sr_05_push_overwriting_drops_the_oldest() {
    let mut r = RingBuffer::new(2);
    assert_eq!(r.push_overwriting(1), None);
    assert_eq!(r.push_overwriting(2), None);
    assert_eq!(r.push_overwriting(3), Some(1), "the oldest value was dropped to make room, and is returned");
    assert_eq!(r.iter().copied().collect::<Vec<_>>(), vec![2, 3]);
    let mut zero = RingBuffer::new(0);
    assert_eq!(zero.push(5), Err(5));
    assert_eq!(zero.push_overwriting(6), Some(6), "a buffer of capacity 0 cannot hold anything");
    assert!(zero.is_empty() && zero.pop().is_none());
}

#[test]
fn sr_05_clear_drops_the_values_at_once_and_the_buffer_is_reusable() {
    use std::rc::Rc;
    let token = Rc::new(());
    let mut r = RingBuffer::new(4);
    for _ in 0..3 {
        r.push(Rc::clone(&token)).unwrap();
    }
    r.pop();
    r.clear();
    assert_eq!(Rc::strong_count(&token), 1, "clear drops every value now, not later");
    assert!(r.is_empty());
    r.push(Rc::clone(&token)).unwrap();
    assert_eq!(r.len(), 1);
}

/// One operation on a ring buffer.
#[derive(Clone, Debug)]
enum Op {
    Push(u8),
    PushOverwriting(u8),
    Pop,
    Clear,
}

fn ops() -> impl Strategy<Value = Vec<Op>> {
    proptest::collection::vec(
        prop_oneof![
            4 => any::<u8>().prop_map(Op::Push),
            2 => any::<u8>().prop_map(Op::PushOverwriting),
            4 => Just(Op::Pop),
            1 => Just(Op::Clear),
        ],
        0..150,
    )
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: whatever the capacity and the operations, the ring buffer answers like a `VecDeque` with a limit.
    #[test]
    fn sr_05_property_a_ring_buffer_is_a_limited_deque(capacity in 0usize..9, ops in ops()) {
        let mut ring = RingBuffer::new(capacity);
        let mut model: VecDeque<u8> = VecDeque::new();
        for op in ops {
            match op {
                Op::Push(v) => {
                    let want = if model.len() < capacity { model.push_back(v); Ok(()) } else { Err(v) };
                    prop_assert_eq!(ring.push(v), want);
                }
                Op::PushOverwriting(v) => {
                    let want = if capacity == 0 { Some(v) } else {
                        let dropped = if model.len() == capacity { model.pop_front() } else { None };
                        model.push_back(v);
                        dropped
                    };
                    prop_assert_eq!(ring.push_overwriting(v), want);
                }
                Op::Pop => prop_assert_eq!(ring.pop(), model.pop_front()),
                Op::Clear => { ring.clear(); model.clear(); }
            }
            prop_assert_eq!(ring.len(), model.len());
            prop_assert_eq!(ring.is_full(), model.len() == capacity);
            prop_assert_eq!(ring.front(), model.front());
            prop_assert_eq!(ring.back(), model.back());
            prop_assert_eq!(ring.iter().copied().collect::<Vec<_>>(), model.iter().copied().collect::<Vec<_>>());
        }
    }
}
