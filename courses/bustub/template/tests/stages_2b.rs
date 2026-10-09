//! Tests for module 2b, the extendible hash table. A test name starts with its stage: `s2b_03_…` belongs to stage 2b-03, and
//! `anneal course test` runs just those.
//!
//! The tests use only the public items: `murmur_hash3_x64_128`, `HashFunction` and `DiskExtendibleHashTable`. Pages are yours.
//! The table is run against a `HashMap` on random operation sequences, with `verify_integrity` after every step and a check that
//! no guard is leaked. Whether an insert can fail is decided by the keys alone: a key fails when it is already present, or when the
//! keys already in the table that share its header slot and its low `directory_max_depth` hash bits fill a whole bucket (nothing
//! can split them further), and the model computes exactly that with the table's own hash function.
//! The hash values in the first stage come from running BusTub's MurmurHash3.cpp (compiled with clang) on the same bytes.

use std::collections::HashMap;
use std::thread;

use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::common::config::PageId;
use bustub::container::disk::hash::disk_extendible_hash_table::DiskExtendibleHashTable;
use bustub::container::hash::hash_function::HashFunction;
use bustub::container::hash::murmur3::murmur_hash3_x64_128;
use bustub::storage::index::generic_key::GenericKey;
use bustub::storage::index::int_comparator::IntComparator;
#[path = "common/pool.rs"]
mod pool;
use pool::{pool_with, Policy};
use proptest::prelude::*;

mod common;

struct Lcg(u64);
impl Lcg {
    fn next(&mut self, n: usize) -> usize {
        self.0 = self.0.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        ((self.0 >> 33) as usize) % n
    }
}

// ---- 2b-01 · MurmurHash3 -------------------------------------------------------------------------------------------------------

/// (length, h1, h2) of MurmurHash3_x64_128 over the first `length` bytes of [3, 10, 17, 24, ...] (byte i = i * 7 + 3), seed 0.
const BY_LENGTH: &[(usize, u64, u64)] = &[
    (0, 0x0000000000000000, 0x0000000000000000),
    (1, 0x726ac6dd306a3e59, 0x4e711127c5b5a8e4),
    (2, 0x20397a993ff70362, 0x2cab193a4622361c),
    (3, 0x6e3febcaf3b53dce, 0xe5bb83e375ffb688),
    (4, 0x0e29ed82ded0aa06, 0xadb20c1802c28885),
    (5, 0xa82aed5674c88370, 0x30a0320850949358),
    (6, 0x46cdbf2912314129, 0x3fd9512a9d1601ac),
    (7, 0xbecbbf54236ce3a1, 0x2b3ba492e39cef50),
    (8, 0xa5ee2a9a9132d3bd, 0x259e7f3a617e003a),
    (9, 0x51ba2ea10afadbb6, 0x1f8153c3131e0496),
    (10, 0x0cfb7360d9faa194, 0xecb86c2f3d9ba94f),
    (11, 0xe8c32ab7814b03d0, 0x13720d13e51ad72d),
    (12, 0x92408898cf3ea070, 0x7b0fd157afb4f215),
    (13, 0xd067c85b9518a027, 0x0fd77b52596e08ec),
    (14, 0x87c460807cb73876, 0x2b4ff4a6aee2ecf8),
    (15, 0xba6a4b5e80ade4f4, 0xe00e5a8ff7e8f26d),
    (16, 0xc4b099c52f8f4ea1, 0x7d670219d92afe48),
    (17, 0xd4ae4b39fe53b127, 0x6602453b6681dbe9),
    (18, 0xabda0633173c8e39, 0xe324b4c61bb1fab9),
    (19, 0xfb8da97a73286c48, 0xa63e0672f1dd646a),
    (20, 0x68c959647c4b852f, 0x47a01f7ab6ecafcc),
    (21, 0xef572bbd37bd4cff, 0xb373833552388cec),
    (22, 0x3ef71b4b96724a89, 0x83a05a3f0a197d37),
    (23, 0x4dcc0798a0ad4570, 0x7cc110ecbb0142cd),
    (24, 0xecebc073185cf2dd, 0xa824e81f1e1ed450),
    (25, 0x90cd94cfd82e1b1c, 0x0b07b1821236d3d0),
    (26, 0xd065cd117d0a7981, 0x1de492a7503f6989),
    (27, 0x25bf19510bd8f800, 0x2f3bf2ecd8ea43e9),
    (28, 0x947909dc6fbb0a99, 0x4e1b7027149d70b6),
    (29, 0x3573e8ed18d5b747, 0x0844c1c68d890d4a),
    (30, 0x658c7af80a8fac5e, 0x9fbb561421f0e98e),
    (31, 0x9d91fedff00436fb, 0x7ea851ba737ebfd0),
    (32, 0x65bdb8dd080643ff, 0xbec31b8aa5f3910a),
    (33, 0xb16757d8c4f72f1a, 0x9171ee56072d60a6),
    (34, 0x36f32887d9505de8, 0x0148bfe8f9d2d2bf),
    (35, 0x43827073936f3060, 0x997c53eea1c262f1),
    (36, 0x3fcaf101067c352b, 0xaa73f9ccfb87df0c),
    (37, 0x2c5b9ecfee19d335, 0x58f7886b2cc2d93c),
    (38, 0x4c559caee2106b6b, 0xe0863fe84efa4a3e),
    (39, 0x8f0f3223bfe2888d, 0xc1877ca40de15177),
    (40, 0x673bff07bd120303, 0xf0656121415a2357),
];

/// (seed, h1, h2) over the first 23 of those bytes.
const BY_SEED: &[(u32, u64, u64)] = &[
    (1, 0x71f74884482c98dd, 0x67d1595ff2b515e5),
    (42, 0xd36633ed9087d5af, 0x147751c3e6fcddef),
    (4294967295, 0xedd0e5f14c2c7a1e, 0x9683343da69a8389),
];

fn pattern(len: usize) -> Vec<u8> {
    (0..len).map(|i| (i * 7 + 3) as u8).collect()
}

#[test]
fn s2b_01_the_empty_input_hashes_to_zero() {
    assert_eq!(murmur_hash3_x64_128(b"", 0), [0, 0], "the empty input hashes to zero");
}

#[test]
fn s2b_01_short_inputs_use_only_the_tail() {
    for &(len, h1, h2) in BY_LENGTH.iter().filter(|(len, _, _)| *len < 16) {
        assert_eq!(murmur_hash3_x64_128(&pattern(len), 0), [h1, h2], "length {len}");
    }
}

#[test]
fn s2b_01_one_full_block_and_beyond() {
    for &(len, h1, h2) in BY_LENGTH.iter().filter(|(len, _, _)| *len >= 16) {
        assert_eq!(murmur_hash3_x64_128(&pattern(len), 0), [h1, h2], "length {len}");
    }
}

#[test]
fn s2b_01_the_seed_changes_the_hash() {
    for &(seed, h1, h2) in BY_SEED {
        assert_eq!(murmur_hash3_x64_128(&pattern(23), seed), [h1, h2], "seed {seed}");
    }
}

#[test]
fn s2b_01_known_strings() {
    assert_eq!(murmur_hash3_x64_128(b"hello", 0), [0xcbd8a7b341bd9b02, 0x5b1e906a48ae1d19], "known strings");
    assert_eq!(murmur_hash3_x64_128(b"a", 0)[0], 9607679276477937801, "known strings");
    assert_eq!(murmur_hash3_x64_128(b"The quick brown fox jumps over the lazy dog", 0), [16378391709484522348, 8809951995912426311], "known strings");
    assert_eq!(murmur_hash3_x64_128(b"0123456789abcdef", 0), [5467490433528156583, 9782763267945859290], "known strings");
    assert_eq!(murmur_hash3_x64_128(b"0123456789abcdefX", 0), [14838185036522510071, 10336343437188549415], "known strings");
}

// ---- 2b-01 · HashFunction -----------------------------------------------------------------------------------------------------

const INTS: &[(i32, u64)] = &[
    (0, 0xcfa0f7ddd84c76bc),
    (1, 0x8895a3f5af28cafe),
    (2, 0xda0ce907e4355b60),
    (3, 0x4848de7f7bd2a13b),
    (7, 0x7f2769b67e461dfb),
    (8, 0x72f24e286b62c7e4),
    (100, 0xba90e3db7b5a891d),
    (-1, 0x43da45eb34664641),
    (123456789, 0xff48578368beace4),
];

const KEYS: &[(i64, u64)] = &[
    (0, 0x28df63b7cc57c3cb),
    (1, 0x004403b7fb05c44a),
    (2, 0xde0820a06c76c0a8),
    (99, 0x62b09d4e363b3f0c),
    (-5, 0x50c7c275d0793924),
    (4294967296, 0x237ebf69459a7ebb),
];

#[test]
fn s2b_01_an_int_is_hashed_by_its_four_bytes() {
    let hash = HashFunction::<i32>::new();
    for &(i, want) in INTS {
        assert_eq!(hash.get_hash(&i), want, "key {i}");
    }
}

#[test]
fn s2b_01_a_generic_key_is_hashed_by_its_eight_bytes() {
    let hash = HashFunction::<GenericKey<8>>::new();
    for &(n, want) in KEYS {
        let mut key = GenericKey::<8>::default();
        key.set_from_integer(n);
        assert_eq!(hash.get_hash(&key), want, "key {n}");
    }
}

#[test]
fn s2b_01_only_the_first_half_of_the_128_bits_is_kept() {
    let hash = HashFunction::<i32>::new();
    assert_eq!(hash.get_hash(&0), 14961230494313510588, "only the first half of the 128 bits is kept");
    assert_eq!(hash.get_hash(&1), 9841952836289088254, "only the first half of the 128 bits is kept");
}

#[test]
fn s2b_01_the_low_bits_spread_small_integers() {
    // The table uses the low bits for buckets: 0..16 must not all share them.
    let hash = HashFunction::<i32>::new();
    let low_two: Vec<u64> = (0..16).map(|i| hash.get_hash(&i) & 3).collect();
    for class in 0..4 {
        assert!(low_two.iter().filter(|&&b| b == class).count() >= 2, "{low_two:?}");
    }
}


// ---- The table under test ---------------------------------------------------------------------------------------------------

type Table<'a> = DiskExtendibleHashTable<'a, i32, i32, IntComparator>;

#[derive(Clone, Copy, Debug)]
struct Shape {
    header_depth: u32,
    directory_depth: u32,
    bucket_size: u32,
}

fn hash32(key: i32) -> u32 {
    HashFunction::<i32>::new().get_hash(&key) as u32
}

/// Keys fall in the same "class" when no amount of splitting can separate them: same header slot, same low `directory_depth` bits.
fn class_of(shape: Shape, key: i32) -> (u32, u32) {
    let h = hash32(key);
    let header = if shape.header_depth == 0 { 0 } else { h >> (32 - shape.header_depth) };
    (header, h & ((1u32 << shape.directory_depth) - 1))
}

/// Whether inserting a new `key` into a table holding `model` must succeed.
fn insert_must_succeed(shape: Shape, model: &HashMap<i32, i32>, key: i32) -> bool {
    let class = class_of(shape, key);
    model.keys().filter(|&&k| class_of(shape, k) == class).count() < shape.bucket_size as usize
}

fn table<'a>(bpm: &'a BufferPoolManager, shape: Shape) -> Table<'a> {
    DiskExtendibleHashTable::new("test", bpm, IntComparator, HashFunction::new(), shape.header_depth, shape.directory_depth, shape.bucket_size)
}

/// No page may stay pinned between operations: every guard the table took has been dropped.
fn assert_nothing_pinned(bpm: &BufferPoolManager) {
    for id in 0..300 {
        assert!(matches!(bpm.get_pin_count(PageId(id)), None | Some(0)), "page {id} is still pinned between operations: a guard was kept");
    }
}

#[derive(Clone, Copy, Debug)]
enum Op {
    Insert(i32, i32),
    Get(i32),
    Remove(i32),
}

fn ops(keys: i32, with_remove: bool) -> impl Strategy<Value = Vec<Op>> {
    let remove = if with_remove { 4 } else { 0 };
    prop::collection::vec(
        prop_oneof![
            6 => (0..keys, any::<i32>()).prop_map(|(k, v)| Op::Insert(k, v)),
            3 => (0..keys).prop_map(Op::Get),
            remove => (0..keys).prop_map(Op::Remove),
        ],
        1..250,
    )
}

fn shapes() -> impl Strategy<Value = Shape> {
    (0u32..=2, 0u32..=4, 1u32..=4).prop_map(|(header_depth, directory_depth, bucket_size)| Shape { header_depth, directory_depth, bucket_size })
}

fn run_model(shape: Shape, ops: &[Op], frames: usize) -> Result<(), TestCaseError> {
    let (bpm, _disk) = pool_with(Policy::Fifo, frames);
    let ht = table(&bpm, shape);
    let mut model: HashMap<i32, i32> = HashMap::new();
    for (step, op) in ops.iter().enumerate() {
        match *op {
            Op::Insert(k, v) => {
                let want = !model.contains_key(&k) && insert_must_succeed(shape, &model, k);
                prop_assert_eq!(ht.insert(&k, &v), want, "step {}: insert({}) with {:?}: {}", step, k, shape, if model.contains_key(&k) { "the key is already there" } else { "its class is full or has room" });
                if want {
                    model.insert(k, v);
                }
            }
            Op::Get(k) => prop_assert_eq!(ht.get_value(&k), model.get(&k).map(|&v| vec![v]).unwrap_or_default(), "step {}: get_value({})", step, k),
            Op::Remove(k) => prop_assert_eq!(ht.remove(&k), model.remove(&k).is_some(), "step {}: remove({})", step, k),
        }
        ht.verify_integrity();
        assert_nothing_pinned(&bpm);
    }
    for k in 0..64 {
        prop_assert_eq!(ht.get_value(&k), model.get(&k).map(|&v| vec![v]).unwrap_or_default(), "final get_value({})", k);
    }
    Ok(())
}

fn config() -> ProptestConfig {
    ProptestConfig { cases: 48, max_shrink_iters: 3000, ..ProptestConfig::default() }
}

// ---- 2b-02 · Lookups and inserts without splits -------------------------------------------------------------------------

#[test]
fn s2b_02_an_empty_table_has_no_values() {
    let (bpm, _) = pool_with(Policy::Fifo, 6);
    let ht = table(&bpm, Shape { header_depth: 2, directory_depth: 3, bucket_size: 4 });
    assert!(ht.get_value(&7).is_empty(), "nothing was inserted");
    ht.verify_integrity();
    assert_eq!(ht.index_name(), "test");
    assert!(ht.get_header_page_id().is_valid());
}

#[test]
fn s2b_02_an_inserted_key_is_found_with_its_value() {
    let (bpm, _) = pool_with(Policy::Fifo, 6);
    let ht = table(&bpm, Shape { header_depth: 0, directory_depth: 3, bucket_size: 10 });
    assert!(ht.insert(&5, &50));
    assert_eq!(ht.get_value(&5), vec![50]);
    assert!(ht.get_value(&6).is_empty());
    ht.verify_integrity();
}

#[test]
fn s2b_02_a_duplicate_key_is_refused_and_keeps_its_value() {
    let (bpm, _) = pool_with(Policy::Fifo, 6);
    let ht = table(&bpm, Shape { header_depth: 0, directory_depth: 3, bucket_size: 10 });
    assert!(ht.insert(&5, &50));
    assert!(!ht.insert(&5, &99), "keys are unique");
    assert_eq!(ht.get_value(&5), vec![50]);
}

#[test]
fn s2b_02_keys_in_different_header_slots_do_not_disturb_each_other() {
    let (bpm, _) = pool_with(Policy::Fifo, 6);
    let shape = Shape { header_depth: 2, directory_depth: 2, bucket_size: 8 };
    let ht = table(&bpm, shape);
    // find keys that land in each of the four header slots
    let mut by_slot: HashMap<u32, Vec<i32>> = HashMap::new();
    for k in 0..400 {
        by_slot.entry(class_of(shape, k).0).or_default().push(k);
    }
    assert_eq!(by_slot.len(), 4, "the test hash spreads keys over all four header slots");
    for keys in by_slot.values() {
        for &k in &keys[..3] {
            assert!(ht.insert(&k, &(k * 2)));
        }
    }
    for keys in by_slot.values() {
        for &k in &keys[..3] {
            assert_eq!(ht.get_value(&k), vec![k * 2]);
        }
    }
    ht.verify_integrity();
}

#[test]
fn s2b_02_the_default_sizes_describe_what_a_page_holds() {
    assert_eq!(Table::default_header_max_depth(), 9);
    assert_eq!(Table::default_directory_max_depth(), 9);
    let n = Table::default_bucket_max_size();
    assert!((400..=1100).contains(&n), "a bucket of (i32, i32) pairs holds hundreds in an 8 KiB page, not {n}");
}

#[test]
fn s2b_02_a_page_worth_of_keys_fit_without_any_splitting() {
    let (bpm, _) = pool_with(Policy::Fifo, 6);
    let ht = DiskExtendibleHashTable::<i32, i32, IntComparator>::new("big", &bpm, IntComparator, HashFunction::new(), 0, 0, Table::default_bucket_max_size());
    for k in 0..300 {
        assert!(ht.insert(&k, &(k + 1)));
    }
    for k in 0..300 {
        assert_eq!(ht.get_value(&k), vec![k + 1]);
    }
    assert_nothing_pinned(&bpm);
}

proptest! {
    #![proptest_config(config())]

    /// Buckets big enough that nothing ever splits: the table is a map.
    #[test]
    fn s2b_02_a_table_with_roomy_buckets_behaves_like_a_hashmap(header_depth in 0u32..=2, ops in ops(48, false)) {
        run_model(Shape { header_depth, directory_depth: 3, bucket_size: 60 }, &ops, 5)?;
    }
}

// ---- 2b-03 · Full buckets split and the directory grows --------------------------------------------------------------------

/// `n` keys that share their header slot and their low `depth` bits, found by scanning.
fn colliding_keys(shape: Shape, n: usize) -> Vec<i32> {
    let mut by_class: HashMap<(u32, u32), Vec<i32>> = HashMap::new();
    for k in 0..20_000 {
        let v = by_class.entry(class_of(shape, k)).or_default();
        v.push(k);
        if v.len() == n {
            return v.clone();
        }
    }
    panic!("no {n} colliding keys found");
}

#[test]
fn s2b_03_a_full_bucket_splits_so_every_key_is_still_found() {
    let (bpm, _) = pool_with(Policy::Fifo, 8);
    let ht = table(&bpm, Shape { header_depth: 0, directory_depth: 9, bucket_size: 2 });
    for k in 0..100 {
        assert!(ht.insert(&k, &(k * 3)), "key {k} should fit after splitting");
        ht.verify_integrity();
    }
    for k in 0..100 {
        assert_eq!(ht.get_value(&k), vec![k * 3], "key {k} after all the splits");
    }
    assert_nothing_pinned(&bpm);
}

#[test]
fn s2b_03_the_directory_doubles_as_buckets_fill() {
    let (bpm, _) = pool_with(Policy::Fifo, 8);
    let ht = table(&bpm, Shape { header_depth: 0, directory_depth: 9, bucket_size: 2 });
    assert_eq!(ht.global_depth(&0), None, "no directory before the first insert");
    ht.insert(&0, &0);
    assert_eq!(ht.global_depth(&0), Some(0), "one bucket needs a directory of one slot");
    let mut last = 0;
    for k in 1..100 {
        ht.insert(&k, &k);
        let depth = ht.global_depth(&0).unwrap();
        assert!(depth >= last, "the directory never shrinks while only inserting");
        last = depth;
    }
    assert!(last >= 5, "100 keys in buckets of 2 need at least 50 buckets, so a directory of 64 slots or more (depth >= 6), not depth {last}");
    assert!(last <= 9);
}

#[test]
fn s2b_03_keys_that_cannot_be_separated_make_the_insert_fail() {
    let shape = Shape { header_depth: 0, directory_depth: 2, bucket_size: 2 };
    let keys = colliding_keys(shape, 3);
    let (bpm, _) = pool_with(Policy::Fifo, 8);
    let ht = table(&bpm, shape);
    assert!(ht.insert(&keys[0], &1));
    assert!(ht.insert(&keys[1], &2));
    assert!(!ht.insert(&keys[2], &3), "three keys with the same low 2 bits cannot fit in a bucket of 2 at directory depth 2");
    assert_eq!(ht.get_value(&keys[0]), vec![1]);
    assert_eq!(ht.get_value(&keys[1]), vec![2]);
    assert!(ht.get_value(&keys[2]).is_empty());
    ht.verify_integrity();
}

#[test]
fn s2b_03_a_directory_that_may_not_grow_is_full_when_its_bucket_is() {
    let shape = Shape { header_depth: 0, directory_depth: 0, bucket_size: 3 };
    let (bpm, _) = pool_with(Policy::Fifo, 8);
    let ht = table(&bpm, shape);
    for k in 0..3 {
        assert!(ht.insert(&k, &k));
    }
    assert!(!ht.insert(&3, &3), "one bucket, three slots, no room to split");
}

#[test]
fn s2b_03_failed_inserts_leave_the_table_as_it_was() {
    let shape = Shape { header_depth: 1, directory_depth: 3, bucket_size: 2 };
    let (bpm, _) = pool_with(Policy::Fifo, 8);
    let ht = table(&bpm, shape);
    let mut model = HashMap::new();
    for k in 0..200 {
        if ht.insert(&k, &k) {
            model.insert(k, k);
        }
        ht.verify_integrity();
    }
    assert!(model.len() < 200 && model.len() > 8, "some inserts fail and many succeed: {}", model.len());
    for k in 0..200 {
        assert_eq!(ht.get_value(&k), model.get(&k).map(|&v| vec![v]).unwrap_or_default(), "key {k}");
    }
}

#[test]
fn s2b_03_a_small_pool_is_enough_because_guards_are_released() {
    let (bpm, _) = pool_with(Policy::Fifo, 4);
    let ht = table(&bpm, Shape { header_depth: 2, directory_depth: 9, bucket_size: 3 });
    for k in 0..500 {
        assert!(ht.insert(&k, &k));
    }
    assert_nothing_pinned(&bpm);
}

proptest! {
    #![proptest_config(config())]

    /// Any table shape, inserts and lookups: success is decided by the keys' hash classes alone, and everything inserted is found.
    #[test]
    fn s2b_03_inserts_succeed_exactly_when_the_hash_classes_have_room(shape in shapes(), ops in ops(64, false)) {
        run_model(shape, &ops, 6)?;
    }
}

// ---- 2b-04 · Remove, merge and shrink ---------------------------------------------------------------------------------------------

#[test]
fn s2b_04_remove_says_whether_the_key_was_there() {
    let (bpm, _) = pool_with(Policy::Fifo, 6);
    let ht = table(&bpm, Shape { header_depth: 1, directory_depth: 4, bucket_size: 3 });
    assert!(!ht.remove(&1), "removing from an empty table");
    ht.insert(&1, &10);
    ht.insert(&2, &20);
    assert!(ht.remove(&1));
    assert!(!ht.remove(&1), "a second remove");
    assert!(ht.get_value(&1).is_empty());
    assert_eq!(ht.get_value(&2), vec![20]);
}

#[test]
fn s2b_04_removing_everything_leaves_a_table_that_still_works() {
    let (bpm, _) = pool_with(Policy::Fifo, 6);
    let ht = table(&bpm, Shape { header_depth: 2, directory_depth: 9, bucket_size: 2 });
    for round in 0..3 {
        for k in 0..150 {
            assert!(ht.insert(&k, &(k + round)), "round {round}: insert {k}");
        }
        for k in 0..150 {
            assert!(ht.remove(&k), "round {round}: remove {k}");
            ht.verify_integrity();
        }
        for k in 0..150 {
            assert!(ht.get_value(&k).is_empty());
        }
    }
    assert_nothing_pinned(&bpm);
}

#[test]
fn s2b_04_the_directory_shrinks_back_when_the_buckets_are_gone() {
    let (bpm, _) = pool_with(Policy::Fifo, 6);
    let ht = table(&bpm, Shape { header_depth: 0, directory_depth: 9, bucket_size: 2 });
    for k in 0..100 {
        ht.insert(&k, &k);
    }
    let grown = ht.global_depth(&0).unwrap();
    assert!(grown >= 5);
    for k in 0..100 {
        ht.remove(&k);
    }
    assert_eq!(ht.global_depth(&0), Some(0), "an emptied table's directory has shrunk back to one slot (it grew to depth {grown})");
    for k in 0..40 {
        assert!(ht.insert(&k, &k), "and it grows again");
    }
}

#[test]
fn s2b_04_empty_buckets_are_given_back_to_the_pool() {
    let (bpm, disk) = pool_with(Policy::Fifo, 6);
    let ht = table(&bpm, Shape { header_depth: 0, directory_depth: 9, bucket_size: 2 });
    for k in 0..100 {
        ht.insert(&k, &k);
    }
    assert!(disk.deletes.lock().unwrap().is_empty(), "nothing is deleted while the table only grows");
    for k in 0..100 {
        ht.remove(&k);
    }
    assert!(disk.deletes.lock().unwrap().len() >= 20, "after removing every key most of the ~50 bucket pages must have been deleted, only {} were", disk.deletes.lock().unwrap().len());
}

#[test]
fn s2b_04_removing_one_key_does_not_disturb_its_neighbours_in_a_merged_bucket() {
    let (bpm, _) = pool_with(Policy::Fifo, 6);
    let ht = table(&bpm, Shape { header_depth: 0, directory_depth: 9, bucket_size: 2 });
    for k in 0..40 {
        ht.insert(&k, &(k * 7));
    }
    for k in (0..40).step_by(2) {
        assert!(ht.remove(&k));
    }
    for k in 0..40 {
        let want = if k % 2 == 0 { vec![] } else { vec![k * 7] };
        assert_eq!(ht.get_value(&k), want, "key {k}");
    }
    ht.verify_integrity();
}

#[test]
fn s2b_04_merging_makes_room_for_keys_that_could_not_be_inserted_before() {
    let shape = Shape { header_depth: 0, directory_depth: 2, bucket_size: 2 };
    let keys = colliding_keys(shape, 3);
    let (bpm, _) = pool_with(Policy::Fifo, 6);
    let ht = table(&bpm, shape);
    ht.insert(&keys[0], &0);
    ht.insert(&keys[1], &1);
    assert!(!ht.insert(&keys[2], &2));
    assert!(ht.remove(&keys[0]));
    assert!(ht.insert(&keys[2], &2), "a slot freed by a remove can be used");
}

proptest! {
    #![proptest_config(config())]

    /// The full model: inserts, lookups and removals on any table shape.
    #[test]
    fn s2b_04_a_table_with_removals_agrees_with_the_model(shape in shapes(), ops in ops(64, true)) {
        run_model(shape, &ops, 6)?;
    }
}

// ---- 2b-05 · Boss: many threads --------------------------------------------------------------------------------------------------

#[test]
fn s2b_05_threads_on_disjoint_keys_lose_nothing() {
    let (bpm, _) = pool_with(Policy::Arc, 40);
    let ht = table(&bpm, Shape { header_depth: 2, directory_depth: 9, bucket_size: 8 });
    thread::scope(|scope| {
        for t in 0..4 {
            let ht = &ht;
            scope.spawn(move || {
                for i in 0..300 {
                    let k = t * 1000 + i;
                    assert!(ht.insert(&k, &(k + 1)), "thread {t}: insert {k}");
                }
            });
        }
    });
    ht.verify_integrity();
    for t in 0..4 {
        for i in 0..300 {
            let k = t * 1000 + i;
            assert_eq!(ht.get_value(&k), vec![k + 1], "key {k}");
        }
    }
    assert_nothing_pinned(&bpm);
}

#[test]
fn s2b_05_inserts_removes_and_lookups_at_the_same_time() {
    let (bpm, _) = pool_with(Policy::Arc, 40);
    let ht = table(&bpm, Shape { header_depth: 1, directory_depth: 9, bucket_size: 8 });
    for k in 10_000..10_200 {
        assert!(ht.insert(&k, &k)); // keys the readers expect to find throughout
    }
    thread::scope(|scope| {
        for t in 0..3 {
            let ht = &ht;
            scope.spawn(move || {
                let mut model = HashMap::new();
                let mut rng = Lcg(5 + t as u64);
                for _ in 0..1500 {
                    let k = t * 1000 + rng.next(200) as i32;
                    if rng.next(2) == 0 {
                        assert_eq!(ht.insert(&k, &k), !model.contains_key(&k), "thread {t}: insert {k}");
                        model.insert(k, k);
                    } else {
                        assert_eq!(ht.remove(&k), model.remove(&k).is_some(), "thread {t}: remove {k}");
                    }
                }
                for k in t * 1000..t * 1000 + 200 {
                    assert_eq!(ht.get_value(&k), model.get(&k).map(|&v| vec![v]).unwrap_or_default(), "thread {t}: final {k}");
                }
            });
        }
        for _ in 0..2 {
            let ht = &ht;
            scope.spawn(move || {
                for round in 0..20 {
                    for k in 10_000..10_200 {
                        assert_eq!(ht.get_value(&k), vec![k], "reader, round {round}: the stable key {k} must always be found");
                    }
                }
            });
        }
    });
    ht.verify_integrity();
    assert_nothing_pinned(&bpm);
}

#[test]
fn s2b_05_a_long_single_threaded_run_agrees_with_a_hashmap() {
    let shape = Shape { header_depth: 2, directory_depth: 6, bucket_size: 4 };
    let (bpm, _) = pool_with(Policy::Arc, 8);
    let ht = table(&bpm, shape);
    let mut model: HashMap<i32, i32> = HashMap::new();
    let mut rng = Lcg(77);
    for step in 0..20_000 {
        let k = rng.next(300) as i32;
        match rng.next(5) {
            0 | 1 => {
                let want = !model.contains_key(&k) && insert_must_succeed(shape, &model, k);
                assert_eq!(ht.insert(&k, &step), want, "step {step}: insert {k}");
                if want {
                    model.insert(k, step);
                }
            }
            2 => assert_eq!(ht.remove(&k), model.remove(&k).is_some(), "step {step}: remove {k}"),
            _ => assert_eq!(ht.get_value(&k), model.get(&k).map(|&v| vec![v]).unwrap_or_default(), "step {step}: get {k}"),
        }
        if step % 1000 == 0 {
            ht.verify_integrity();
        }
    }
}
