//! Tests for the extendible hash table stages (2b-01 … 2b-22). A test named `s2b_05_…` belongs to stage 2b-05.
//! The hash values come from running BusTub's own MurmurHash3.cpp (compiled with clang) on the same bytes.

use std::collections::HashMap;
use std::sync::Arc;
use std::thread;

use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::common::config::{PageId, BUSTUB_PAGE_SIZE};
use bustub::common::rid::Rid;
use bustub::container::disk::hash::disk_extendible_hash_table::DiskExtendibleHashTable;
use bustub::container::hash::hash_function::HashFunction;
use bustub::container::hash::murmur3::murmur_hash3_x64_128;
use bustub::storage::disk::disk_manager_memory::DiskManagerUnlimitedMemory;
use bustub::storage::index::generic_key::{GenericComparator, GenericKey};
use bustub::storage::index::int_comparator::IntComparator;
use bustub::storage::page::extendible_htable_bucket_page::ExtendibleHTableBucketPage as Bucket;
use bustub::storage::page::extendible_htable_directory_page::ExtendibleHTableDirectoryPage as Directory;
use bustub::storage::page::extendible_htable_header_page::ExtendibleHTableHeaderPage as Header;

struct Lcg(u64);
impl Lcg {
    fn next(&mut self, n: usize) -> usize {
        self.0 = self.0.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        ((self.0 >> 33) as usize) % n
    }
}

fn bpm(frames: usize) -> BufferPoolManager {
    BufferPoolManager::new(frames, Arc::new(DiskManagerUnlimitedMemory::new()))
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
    assert_eq!(murmur_hash3_x64_128(b"", 0), [0, 0]);
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
    assert_eq!(murmur_hash3_x64_128(b"hello", 0), [0xcbd8a7b341bd9b02, 0x5b1e906a48ae1d19]);
    assert_eq!(murmur_hash3_x64_128(b"a", 0)[0], 9607679276477937801);
    assert_eq!(murmur_hash3_x64_128(b"The quick brown fox jumps over the lazy dog", 0), [16378391709484522348, 8809951995912426311]);
    assert_eq!(murmur_hash3_x64_128(b"0123456789abcdef", 0), [5467490433528156583, 9782763267945859290]);
    assert_eq!(murmur_hash3_x64_128(b"0123456789abcdefX", 0), [14838185036522510071, 10336343437188549415]);
}

// ---- 2b-02 · HashFunction -----------------------------------------------------------------------------------------------------

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
fn s2b_02_an_int_is_hashed_by_its_four_bytes() {
    let hash = HashFunction::<i32>::new();
    for &(i, want) in INTS {
        assert_eq!(hash.get_hash(&i), want, "key {i}");
    }
}

#[test]
fn s2b_02_a_generic_key_is_hashed_by_its_eight_bytes() {
    let hash = HashFunction::<GenericKey<8>>::new();
    for &(n, want) in KEYS {
        let mut key = GenericKey::<8>::default();
        key.set_from_integer(n);
        assert_eq!(hash.get_hash(&key), want, "key {n}");
    }
}

#[test]
fn s2b_02_only_the_first_half_of_the_128_bits_is_kept() {
    let hash = HashFunction::<i32>::new();
    assert_eq!(hash.get_hash(&0), 14961230494313510588);
    assert_eq!(hash.get_hash(&1), 9841952836289088254);
}

#[test]
fn s2b_02_the_low_bits_spread_small_integers() {
    // The table uses the low bits for buckets: 0..16 must not all share them.
    let hash = HashFunction::<i32>::new();
    let low_two: Vec<u64> = (0..16).map(|i| hash.get_hash(&i) & 3).collect();
    for class in 0..4 {
        assert!(low_two.iter().filter(|&&b| b == class).count() >= 2, "{low_two:?}");
    }
}

// ---- 2b-03 · header page: init and accessors ---------------------------------------------------------------------------------------

#[test]
fn s2b_03_init_sets_the_depth_and_empties_every_slot() {
    let mut page = vec![0u8; BUSTUB_PAGE_SIZE];
    let mut header = Header::new(&mut page[..]);
    header.init(2);
    assert_eq!(header.max_depth(), 2);
    assert_eq!(header.max_size(), 4);
    for i in 0..4 {
        assert_eq!(header.get_directory_page_id(i), PageId::INVALID, "a fresh slot is INVALID, not page 0");
    }
}

#[test]
fn s2b_03_slots_hold_directory_page_ids() {
    let mut page = vec![0u8; BUSTUB_PAGE_SIZE];
    let mut header = Header::new(&mut page[..]);
    header.init(3);
    header.set_directory_page_id(0, PageId(10));
    header.set_directory_page_id(7, PageId(77));
    assert_eq!(header.get_directory_page_id(0), PageId(10));
    assert_eq!(header.get_directory_page_id(7), PageId(77));
    assert_eq!(header.get_directory_page_id(3), PageId::INVALID);
}

#[test]
fn s2b_03_the_layout_matches_bustubs() {
    let mut page = vec![0u8; BUSTUB_PAGE_SIZE];
    let mut header = Header::new(&mut page[..]);
    header.init(2);
    header.set_directory_page_id(1, PageId(5));
    assert_eq!(&page[4..8], &[5, 0, 0, 0], "slot 1 is at byte 4");
    assert_eq!(&page[2048..2052], &[2, 0, 0, 0], "max depth is at byte 2048");
}

#[test]
fn s2b_03_a_read_only_view_works() {
    let mut page = vec![0u8; BUSTUB_PAGE_SIZE];
    Header::new(&mut page[..]).init(1);
    let view = Header::new(&page[..]);
    assert_eq!(view.max_size(), 2);
}

#[test]
#[should_panic(expected = "out of range")]
fn s2b_03_a_slot_past_max_size_is_a_bug() {
    let mut page = vec![0u8; BUSTUB_PAGE_SIZE];
    let mut header = Header::new(&mut page[..]);
    header.init(2);
    header.get_directory_page_id(4);
}

#[test]
#[should_panic(expected = "does not fit")]
fn s2b_03_a_depth_above_nine_does_not_fit() {
    let mut page = vec![0u8; BUSTUB_PAGE_SIZE];
    Header::new(&mut page[..]).init(10);
}

// ---- 2b-04 · header page: the directory index of a hash --------------------------------------------------------------------------------

#[test]
fn s2b_04_the_top_bits_choose_the_directory() {
    // BusTub's HeaderDirectoryPageSampleTest: with max depth 2 the top two bits of these hashes are 00, 01, 10, 11.
    let mut page = vec![0u8; BUSTUB_PAGE_SIZE];
    let mut header = Header::new(&mut page[..]);
    header.init(2);
    let hashes = [32768u32, 1073774592, 2147516416, 3221258240];
    for (i, h) in hashes.iter().enumerate() {
        assert_eq!(header.hash_to_directory_index(*h), i as u32);
    }
}

#[test]
fn s2b_04_a_depth_of_zero_means_one_directory() {
    let mut page = vec![0u8; BUSTUB_PAGE_SIZE];
    let mut header = Header::new(&mut page[..]);
    header.init(0);
    for h in [0u32, 1, 0x8000_0000, u32::MAX] {
        assert_eq!(header.hash_to_directory_index(h), 0);
    }
}

#[test]
fn s2b_04_depth_one_looks_at_the_top_bit_only() {
    let mut page = vec![0u8; BUSTUB_PAGE_SIZE];
    let mut header = Header::new(&mut page[..]);
    header.init(1);
    assert_eq!(header.hash_to_directory_index(0x7FFF_FFFF), 0);
    assert_eq!(header.hash_to_directory_index(0x8000_0000), 1);
    assert_eq!(header.hash_to_directory_index(u32::MAX), 1);
}

#[test]
fn s2b_04_the_largest_depth() {
    let mut page = vec![0u8; BUSTUB_PAGE_SIZE];
    let mut header = Header::new(&mut page[..]);
    header.init(9);
    assert_eq!(header.hash_to_directory_index(u32::MAX), 511);
    assert_eq!(header.hash_to_directory_index(0), 0);
    assert_eq!(header.hash_to_directory_index(0x0080_0000), 1);
}

#[test]
fn s2b_04_the_low_bits_are_ignored() {
    let mut page = vec![0u8; BUSTUB_PAGE_SIZE];
    let mut header = Header::new(&mut page[..]);
    header.init(3);
    for low in [0u32, 1, 0xFFFF, 0x1FFF_FFFF] {
        assert_eq!(header.hash_to_directory_index(0xA000_0000 | low), 5);
    }
}

// ---- 2b-05 · directory page: init and accessors ------------------------------------------------------------------------------------

fn directory(max_depth: u32) -> Vec<u8> {
    let mut page = vec![0u8; BUSTUB_PAGE_SIZE];
    Directory::new(&mut page[..]).init(max_depth);
    page
}

#[test]
fn s2b_05_a_fresh_directory_has_one_unassigned_slot() {
    let mut page = directory(3);
    let dir = Directory::new(&mut page[..]);
    assert_eq!((dir.get_max_depth(), dir.get_global_depth(), dir.size(), dir.max_size()), (3, 0, 1, 8));
    assert_eq!(dir.get_bucket_page_id(0), PageId::INVALID);
    assert_eq!(dir.get_local_depth(0), 0);
}

#[test]
fn s2b_05_every_slot_starts_invalid_and_at_depth_zero() {
    let mut page = vec![0xFFu8; BUSTUB_PAGE_SIZE]; // garbage first: init must overwrite it
    let mut dir = Directory::new(&mut page[..]);
    dir.init(9);
    for i in 0..512 {
        assert_eq!(dir.get_bucket_page_id(i), PageId::INVALID, "slot {i}");
        assert_eq!(dir.get_local_depth(i), 0, "slot {i}");
    }
}

#[test]
fn s2b_05_bucket_page_ids_are_stored_per_slot() {
    let mut page = directory(4);
    let mut dir = Directory::new(&mut page[..]);
    dir.set_bucket_page_id(0, PageId(3));
    dir.set_bucket_page_id(15, PageId(9));
    assert_eq!((dir.get_bucket_page_id(0), dir.get_bucket_page_id(15), dir.get_bucket_page_id(1)), (PageId(3), PageId(9), PageId::INVALID));
}

#[test]
fn s2b_05_the_layout_matches_bustubs() {
    let mut page = directory(3);
    Directory::new(&mut page[..]).set_bucket_page_id(2, PageId(7));
    assert_eq!(&page[0..4], &[3, 0, 0, 0], "max depth at byte 0");
    assert_eq!(&page[4..8], &[0, 0, 0, 0], "global depth at byte 4");
    assert_eq!(&page[520 + 8..520 + 12], &[7, 0, 0, 0], "bucket page ids start at byte 520");
}

#[test]
#[should_panic(expected = "out of range")]
fn s2b_05_a_slot_past_max_size_is_a_bug() {
    let mut page = directory(2);
    Directory::new(&mut page[..]).get_bucket_page_id(4);
}

#[test]
#[should_panic(expected = "does not fit")]
fn s2b_05_a_max_depth_above_nine_does_not_fit() {
    let mut page = vec![0u8; BUSTUB_PAGE_SIZE];
    Directory::new(&mut page[..]).init(10);
}

// ---- 2b-06 · directory page: masks and indexes ---------------------------------------------------------------------------------------

#[test]
fn s2b_06_masks_have_as_many_ones_as_the_depth() {
    let mut page = directory(5);
    bustub::storage::page::page_bytes::write_u32(&mut page, 4, 3); // global depth 3
    page[8] = 2; // local depths start at byte 8; slot 0 gets depth 2
    let dir = Directory::new(&page[..]);
    assert_eq!(dir.get_global_depth_mask(), 0b111);
    assert_eq!(dir.get_local_depth_mask(0), 0b11);
    assert_eq!(dir.get_local_depth_mask(1), 0);
}

#[test]
fn s2b_06_a_hash_maps_to_its_low_bits() {
    let mut page = directory(5);
    bustub::storage::page::page_bytes::write_u32(&mut page, 4, 2);
    let dir = Directory::new(&page[..]);
    for h in 0..100u32 {
        assert_eq!(dir.hash_to_bucket_index(h), h % 4);
    }
    assert_eq!(dir.hash_to_bucket_index(0xFFFF_FFFF), 3);
}

#[test]
fn s2b_06_depth_zero_maps_everything_to_slot_zero() {
    let page = directory(5);
    let dir = Directory::new(&page[..]);
    assert_eq!(dir.get_global_depth_mask(), 0);
    for h in [0u32, 1, 12345, u32::MAX] {
        assert_eq!(dir.hash_to_bucket_index(h), 0);
    }
}

#[test]
fn s2b_06_the_split_image_flips_the_top_distinguished_bit() {
    let mut page = directory(5);
    bustub::storage::page::page_bytes::write_u32(&mut page, 4, 3);
    for (slot, depth) in [(0usize, 1u8), (1, 1), (2, 2), (3, 3), (4, 3), (5, 2), (6, 3), (7, 3)] {
        page[8 + slot] = depth; // local depths start at byte 8
    }
    let dir = Directory::new(&page[..]);
    assert_eq!(dir.get_split_image_index(0), 1, "depth 1: flip bit 0");
    assert_eq!(dir.get_split_image_index(1), 0);
    assert_eq!(dir.get_split_image_index(2), 0, "depth 2: flip bit 1");
    assert_eq!(dir.get_split_image_index(5), 7, "5 = 101, depth 2: flip bit 1 -> 111");
    assert_eq!(dir.get_split_image_index(3), 7, "depth 3: flip bit 2 -> 111");
    assert_eq!(dir.get_split_image_index(4), 0);
}

#[test]
fn s2b_06_a_bucket_of_depth_zero_is_its_own_split_image() {
    let page = directory(5);
    let dir = Directory::new(&page[..]);
    assert_eq!(dir.get_split_image_index(0), 0);
}

// ---- 2b-07 · directory page: local depths ----------------------------------------------------------------------------------------------

#[test]
fn s2b_07_local_depths_are_set_and_read() {
    let mut page = directory(4);
    let mut dir = Directory::new(&mut page[..]);
    dir.set_local_depth(3, 2);
    dir.set_local_depth(15, 4);
    assert_eq!((dir.get_local_depth(3), dir.get_local_depth(15), dir.get_local_depth(4)), (2, 4, 0));
}

#[test]
fn s2b_07_incr_and_decr_move_one_step() {
    let mut page = directory(4);
    let mut dir = Directory::new(&mut page[..]);
    dir.incr_local_depth(1);
    dir.incr_local_depth(1);
    assert_eq!(dir.get_local_depth(1), 2);
    dir.decr_local_depth(1);
    assert_eq!(dir.get_local_depth(1), 1);
    assert_eq!(dir.get_local_depth(0), 0, "other slots are untouched");
}

#[test]
#[should_panic(expected = "max depth")]
fn s2b_07_a_local_depth_cannot_pass_the_max_depth() {
    let mut page = directory(2);
    let mut dir = Directory::new(&mut page[..]);
    dir.set_local_depth(0, 2);
    dir.incr_local_depth(0);
}

#[test]
#[should_panic(expected = "already 0")]
fn s2b_07_a_local_depth_cannot_go_below_zero() {
    let mut page = directory(2);
    Directory::new(&mut page[..]).decr_local_depth(0);
}

#[test]
#[should_panic(expected = "out of range")]
fn s2b_07_a_slot_past_max_size_is_a_bug() {
    let mut page = directory(1);
    Directory::new(&mut page[..]).set_local_depth(2, 0);
}

// ---- 2b-08 · directory page: growing ---------------------------------------------------------------------------------------------------

#[test]
fn s2b_08_growing_copies_the_lower_half_into_the_upper_half() {
    let mut page = directory(3);
    let mut dir = Directory::new(&mut page[..]);
    dir.set_bucket_page_id(0, PageId(7));
    dir.incr_global_depth();
    assert_eq!((dir.get_global_depth(), dir.size()), (1, 2));
    assert_eq!(dir.get_bucket_page_id(1), PageId(7), "both slots point at the one bucket until it splits");
    assert_eq!(dir.get_local_depth(1), 0);
}

#[test]
fn s2b_08_depths_are_copied_too() {
    let mut page = directory(3);
    let mut dir = Directory::new(&mut page[..]);
    dir.set_bucket_page_id(0, PageId(1));
    dir.incr_global_depth();
    dir.set_local_depth(0, 1);
    dir.set_bucket_page_id(1, PageId(2));
    dir.set_local_depth(1, 1);
    dir.incr_global_depth();
    assert_eq!((0..4).map(|i| dir.get_bucket_page_id(i).0).collect::<Vec<_>>(), [1, 2, 1, 2]);
    assert_eq!((0..4).map(|i| dir.get_local_depth(i)).collect::<Vec<_>>(), [1, 1, 1, 1]);
}

#[test]
fn s2b_08_bustubs_directory_walkthrough() {
    // The first half of HeaderDirectoryPageSampleTest.
    let mut page = directory(3);
    let mut dir = Directory::new(&mut page[..]);
    dir.set_bucket_page_id(0, PageId(2));
    assert_eq!(dir.size(), 1);
    dir.set_local_depth(0, 1);
    dir.incr_global_depth();
    dir.set_bucket_page_id(1, PageId(3));
    dir.set_local_depth(1, 1);
    assert_eq!((dir.get_bucket_page_id(0), dir.get_bucket_page_id(1)), (PageId(2), PageId(3)));
    for i in 0..100 {
        assert_eq!(dir.hash_to_bucket_index(i), i % 2);
    }
    dir.set_local_depth(0, 2);
    dir.incr_global_depth();
    dir.set_bucket_page_id(2, PageId(4));
    assert_eq!(dir.size(), 4);
    assert_eq!((0..4).map(|i| dir.get_bucket_page_id(i).0).collect::<Vec<_>>(), [2, 3, 4, 3]);
    dir.set_local_depth(0, 3);
    dir.incr_global_depth();
    dir.set_bucket_page_id(4, PageId(5));
    assert_eq!((0..8).map(|i| dir.get_bucket_page_id(i).0).collect::<Vec<_>>(), [2, 3, 4, 3, 5, 3, 4, 3]);
    for i in 0..100 {
        assert_eq!(dir.hash_to_bucket_index(i), i % 8);
    }
}

#[test]
#[should_panic(expected = "max depth")]
fn s2b_08_growing_past_the_max_depth_is_a_bug() {
    let mut page = directory(1);
    let mut dir = Directory::new(&mut page[..]);
    dir.incr_global_depth();
    dir.incr_global_depth();
}

#[test]
fn s2b_08_growing_to_the_largest_size() {
    let mut page = directory(9);
    let mut dir = Directory::new(&mut page[..]);
    dir.set_bucket_page_id(0, PageId(1));
    for _ in 0..9 {
        dir.incr_global_depth();
    }
    assert_eq!(dir.size(), 512);
    assert!((0..512).all(|i| dir.get_bucket_page_id(i) == PageId(1)));
}

// ---- 2b-09 · directory page: shrinking -------------------------------------------------------------------------------------------------

#[test]
fn s2b_09_a_directory_cannot_shrink_while_a_bucket_uses_every_bit() {
    let mut page = directory(3);
    let mut dir = Directory::new(&mut page[..]);
    dir.incr_global_depth();
    dir.incr_global_depth();
    dir.set_local_depth(0, 2);
    assert!(!dir.can_shrink());
}

#[test]
fn s2b_09_it_can_when_every_local_depth_is_below_the_global_depth() {
    let mut page = directory(3);
    let mut dir = Directory::new(&mut page[..]);
    dir.incr_global_depth();
    dir.incr_global_depth();
    dir.incr_global_depth();
    for i in 0..8 {
        dir.set_local_depth(i, 2);
    }
    assert!(dir.can_shrink());
    dir.decr_global_depth();
    assert_eq!((dir.get_global_depth(), dir.size()), (2, 4));
}

#[test]
fn s2b_09_a_directory_of_depth_zero_cannot_shrink() {
    let page = directory(3);
    assert!(!Directory::new(&page[..]).can_shrink());
}

#[test]
fn s2b_09_one_slot_at_full_depth_blocks_the_shrink() {
    let mut page = directory(3);
    let mut dir = Directory::new(&mut page[..]);
    for _ in 0..3 {
        dir.incr_global_depth();
    }
    for i in 0..8 {
        dir.set_local_depth(i, 2);
    }
    dir.set_local_depth(5, 3);
    assert!(!dir.can_shrink());
}

#[test]
#[should_panic(expected = "depth 0")]
fn s2b_09_shrinking_below_zero_is_a_bug() {
    let mut page = directory(3);
    Directory::new(&mut page[..]).decr_global_depth();
}

#[test]
fn s2b_09_only_slots_in_use_count() {
    // After shrinking, slots beyond the new size hold stale depths; they must not block a second shrink.
    let mut page = directory(3);
    let mut dir = Directory::new(&mut page[..]);
    for _ in 0..3 {
        dir.incr_global_depth();
    }
    for i in 0..8 {
        dir.set_local_depth(i, 2);
    }
    dir.decr_global_depth();
    for i in 0..4 {
        dir.set_local_depth(i, 1);
    }
    assert!(dir.can_shrink(), "slots 4..8 still say depth 2, but they are no longer part of the directory");
}

// ---- 2b-10 · directory page: verify_integrity ----------------------------------------------------------------------------------------------

/// A correct depth-2 directory: slots 0 and 2 have their own buckets (depth 2), slots 1 and 3 share one (depth 1).
fn good_directory() -> Vec<u8> {
    let mut page = directory(3);
    let mut dir = Directory::new(&mut page[..]);
    dir.incr_global_depth();
    dir.incr_global_depth();
    for (slot, id, depth) in [(0, 10, 2), (1, 11, 1), (2, 12, 2), (3, 11, 1)] {
        dir.set_bucket_page_id(slot, PageId(id));
        dir.set_local_depth(slot, depth);
    }
    page
}

#[test]
fn s2b_10_a_correct_directory_verifies() {
    let page = good_directory();
    Directory::new(&page[..]).verify_integrity();
}

#[test]
fn s2b_10_a_fresh_directory_with_one_bucket_verifies() {
    let mut page = directory(3);
    Directory::new(&mut page[..]).set_bucket_page_id(0, PageId(4));
    Directory::new(&page[..]).verify_integrity();
}

#[test]
#[should_panic(expected = "above the global depth")]
fn s2b_10_a_local_depth_above_the_global_depth_is_caught() {
    let mut page = good_directory();
    Directory::new(&mut page[..]).set_local_depth(0, 3);
    Directory::new(&page[..]).verify_integrity();
}

#[test]
#[should_panic(expected = "slots")]
fn s2b_10_a_bucket_with_the_wrong_number_of_pointers_is_caught() {
    let mut page = good_directory();
    let mut dir = Directory::new(&mut page[..]);
    dir.set_bucket_page_id(2, PageId(11)); // bucket 11 (depth 1) now has three pointers where 2^(2-1) = 2 are allowed
    dir.set_local_depth(2, 1);
    Directory::new(&page[..]).verify_integrity();
}

#[test]
#[should_panic(expected = "two different local depths")]
fn s2b_10_one_bucket_with_two_depths_is_caught() {
    let mut page = good_directory();
    Directory::new(&mut page[..]).set_local_depth(3, 2);
    Directory::new(&page[..]).verify_integrity();
}

// ---- 2b-11 · bucket page: basics ----------------------------------------------------------------------------------------------------------

type Entry = (GenericKey<8>, Rid);
type BucketPage<'a> = Bucket<&'a mut [u8], GenericKey<8>, Rid>;

fn key(n: i64) -> GenericKey<8> {
    let mut k = GenericKey::<8>::default();
    k.set_from_integer(n);
    k
}

fn rid(n: i64) -> Rid {
    Rid::new(PageId(n as i32), n as u32)
}

fn new_bucket(max_size: u32) -> Vec<u8> {
    let mut page = vec![0xEEu8; BUSTUB_PAGE_SIZE];
    BucketPage::new(&mut page[..]).init(max_size);
    page
}

#[test]
fn s2b_11_a_fresh_bucket_is_empty() {
    let mut page = new_bucket(10);
    let bucket = BucketPage::new(&mut page[..]);
    assert_eq!((bucket.size(), bucket.max_size()), (0, 10));
    assert!(bucket.is_empty());
    assert!(!bucket.is_full());
}

#[test]
fn s2b_11_a_page_holds_511_pairs_of_a_key_and_a_rid() {
    assert_eq!(Bucket::<&[u8], GenericKey<8>, Rid>::capacity(), 511);
    assert_eq!(Bucket::<&[u8], i32, i32>::capacity(), 1023);
}

#[test]
fn s2b_11_the_layout_matches_bustubs() {
    let mut page = new_bucket(10);
    assert_eq!(&page[0..4], &[0, 0, 0, 0], "size at byte 0");
    assert_eq!(&page[4..8], &[10, 0, 0, 0], "max size at byte 4");
    let _ = &mut page;
}

#[test]
#[should_panic(expected = "do not fit")]
fn s2b_11_a_max_size_that_does_not_fit_is_a_bug() {
    let mut page = vec![0u8; BUSTUB_PAGE_SIZE];
    BucketPage::new(&mut page[..]).init(512);
}

#[test]
#[should_panic(expected = "past the bucket's size")]
fn s2b_11_entries_past_the_size_are_not_there() {
    let mut page = new_bucket(10);
    BucketPage::new(&mut page[..]).entry_at(0);
}

// ---- 2b-12 · bucket page: lookup and insert -------------------------------------------------------------------------------------------------

#[test]
fn s2b_12_insert_then_lookup() {
    let mut page = new_bucket(10);
    let mut bucket = BucketPage::new(&mut page[..]);
    let cmp = GenericComparator::<8>;
    for i in 0..5 {
        assert!(bucket.insert(&key(i), &rid(i), &cmp));
    }
    assert_eq!(bucket.size(), 5);
    for i in 0..5 {
        assert_eq!(bucket.lookup(&key(i), &cmp), Some(rid(i)));
    }
    assert_eq!(bucket.lookup(&key(99), &cmp), None);
}

#[test]
fn s2b_12_the_entries_are_where_the_accessors_say() {
    let mut page = new_bucket(10);
    let mut bucket = BucketPage::new(&mut page[..]);
    let cmp = GenericComparator::<8>;
    bucket.insert(&key(7), &rid(70), &cmp);
    bucket.insert(&key(3), &rid(30), &cmp);
    assert_eq!(bucket.entry_at(0), (key(7), rid(70)));
    assert_eq!((bucket.key_at(1), bucket.value_at(1)), (key(3), rid(30)));
}

#[test]
fn s2b_12_a_full_bucket_refuses_more() {
    let mut page = new_bucket(10);
    let mut bucket = BucketPage::new(&mut page[..]);
    let cmp = GenericComparator::<8>;
    for i in 0..10 {
        assert!(bucket.insert(&key(i), &rid(i), &cmp));
    }
    assert!(bucket.is_full());
    assert!(!bucket.insert(&key(11), &rid(11), &cmp));
    assert_eq!(bucket.size(), 10);
}

#[test]
fn s2b_12_a_key_that_is_already_there_is_refused() {
    let mut page = new_bucket(10);
    let mut bucket = BucketPage::new(&mut page[..]);
    let cmp = GenericComparator::<8>;
    assert!(bucket.insert(&key(1), &rid(1), &cmp));
    assert!(!bucket.insert(&key(1), &rid(2), &cmp));
    assert_eq!(bucket.lookup(&key(1), &cmp), Some(rid(1)), "the old value stays");
    assert_eq!(bucket.size(), 1);
}

#[test]
fn s2b_12_keys_are_compared_by_the_comparator_not_by_bytes() {
    // Two keys whose bytes differ beyond the first 8 compare equal under GenericComparator<16>.
    let mut page = vec![0u8; BUSTUB_PAGE_SIZE];
    let mut bucket = Bucket::<&mut [u8], GenericKey<16>, i32>::new(&mut page[..]);
    bucket.init(4);
    let (mut a, mut b) = (GenericKey::<16>::default(), GenericKey::<16>::default());
    a.set_from_integer(5);
    b.set_from_integer(5);
    b.data[12] = 9;
    let cmp = GenericComparator::<16>;
    assert!(bucket.insert(&a, &1, &cmp));
    assert!(!bucket.insert(&b, &2, &cmp), "equal under the comparator: a duplicate");
    assert_eq!(bucket.lookup(&b, &cmp), Some(1));
}

#[test]
fn s2b_12_ints_work_too() {
    let mut page = vec![0u8; BUSTUB_PAGE_SIZE];
    let mut bucket = Bucket::<&mut [u8], i32, i32>::new(&mut page[..]);
    bucket.init(1023);
    for i in 0..1023 {
        assert!(bucket.insert(&i, &(i * 2), &IntComparator));
    }
    assert!(bucket.is_full());
    assert_eq!(bucket.lookup(&1000, &IntComparator), Some(2000));
}

// ---- 2b-13 · bucket page: remove -------------------------------------------------------------------------------------------------------------

fn filled(n: i64) -> Vec<u8> {
    let mut page = new_bucket(10);
    let mut bucket = BucketPage::new(&mut page[..]);
    for i in 0..n {
        assert!(bucket.insert(&key(i), &rid(i), &GenericComparator::<8>));
    }
    page
}

#[test]
fn s2b_13_remove_takes_a_pair_out() {
    let mut page = filled(5);
    let mut bucket = BucketPage::new(&mut page[..]);
    let cmp = GenericComparator::<8>;
    assert!(bucket.remove(&key(2), &cmp));
    assert_eq!(bucket.size(), 4);
    assert_eq!(bucket.lookup(&key(2), &cmp), None);
    assert_eq!(bucket.lookup(&key(3), &cmp), Some(rid(3)));
}

#[test]
fn s2b_13_remove_keeps_the_order_of_the_rest() {
    let mut page = filled(5);
    let mut bucket = BucketPage::new(&mut page[..]);
    bucket.remove(&key(1), &GenericComparator::<8>);
    assert_eq!((0..4).map(|i| bucket.key_at(i).get_as_integer()).collect::<Vec<_>>(), [0, 2, 3, 4]);
}

#[test]
fn s2b_13_removing_a_missing_key_says_so() {
    let mut page = filled(3);
    let mut bucket = BucketPage::new(&mut page[..]);
    let cmp = GenericComparator::<8>;
    assert!(!bucket.remove(&key(99), &cmp));
    assert!(bucket.remove(&key(1), &cmp));
    assert!(!bucket.remove(&key(1), &cmp), "the second removal finds nothing");
    assert_eq!(bucket.size(), 2);
}

#[test]
fn s2b_13_remove_at_by_slot() {
    let mut page = filled(4);
    let mut bucket = BucketPage::new(&mut page[..]);
    bucket.remove_at(0);
    assert_eq!(bucket.key_at(0).get_as_integer(), 1);
    assert_eq!(bucket.size(), 3);
}

#[test]
fn s2b_13_a_bucket_can_be_emptied_and_refilled() {
    let mut page = filled(10);
    let mut bucket = BucketPage::new(&mut page[..]);
    let cmp = GenericComparator::<8>;
    for i in 0..10 {
        assert!(bucket.remove(&key(i), &cmp));
    }
    assert!(bucket.is_empty());
    for i in 20..30 {
        assert!(bucket.insert(&key(i), &rid(i), &cmp));
    }
    assert!(bucket.is_full());
}

#[test]
#[should_panic(expected = "past the bucket's size")]
fn s2b_13_remove_at_past_the_size_is_a_bug() {
    let mut page = filled(2);
    BucketPage::new(&mut page[..]).remove_at(2);
}

// ---- 2b-14 · BusTub's page samples -------------------------------------------------------------------------------------------------------

#[test]
fn s2b_14_the_bucket_sample_end_to_end() {
    // BusTub's BucketPageSampleTest, through a real page of the buffer pool.
    let bpm = bpm(5);
    let page_id = bpm.new_page();
    let mut guard = bpm.write_page(page_id);
    let mut bucket = BucketPage::new(&mut guard.get_data_mut()[..]);
    bucket.init(10);
    let cmp = GenericComparator::<8>;
    for i in 0..10 {
        assert!(bucket.insert(&key(i), &rid(i), &cmp));
    }
    assert!(bucket.is_full());
    assert!(!bucket.insert(&key(11), &rid(11), &cmp));
    for i in 0..10 {
        assert_eq!(bucket.lookup(&key(i), &cmp), Some(rid(i)));
    }
    for i in (1..10).step_by(2) {
        assert!(bucket.remove(&key(i), &cmp));
    }
    for i in 0..10 {
        assert_eq!(bucket.remove(&key(i), &cmp), i % 2 == 0, "key {i}");
    }
    assert!(bucket.is_empty());
}

// ---- 2b-15 · the table: new, get_value on an empty table, verify_integrity -----------------------------------------------------------------

type IntTable<'a> = DiskExtendibleHashTable<'a, i32, i32, IntComparator>;
type KeyTable<'a> = DiskExtendibleHashTable<'a, GenericKey<8>, Rid, GenericComparator<8>>;

fn int_table(bpm: &BufferPoolManager, header: u32, directory: u32, bucket: u32) -> IntTable<'_> {
    DiskExtendibleHashTable::new("test", bpm, IntComparator, HashFunction::new(), header, directory, bucket)
}

#[test]
fn s2b_15_a_new_table_has_a_formatted_header() {
    let bpm = bpm(10);
    let ht = int_table(&bpm, 2, 3, 4);
    let guard = bpm.read_page(ht.get_header_page_id());
    let header = Header::new(&guard[..]);
    assert_eq!(header.max_depth(), 2);
    for i in 0..4 {
        assert_eq!(header.get_directory_page_id(i), PageId::INVALID);
    }
}

#[test]
fn s2b_15_an_empty_table_has_no_values() {
    let bpm = bpm(10);
    let ht = int_table(&bpm, 0, 3, 4);
    for k in 0..20 {
        assert!(ht.get_value(&k).is_empty());
    }
}

#[test]
fn s2b_15_an_empty_table_verifies() {
    let bpm = bpm(10);
    int_table(&bpm, 3, 3, 4).verify_integrity();
}

#[test]
fn s2b_15_the_defaults_fill_a_page() {
    assert_eq!(IntTable::default_bucket_max_size(), 1023);
    assert_eq!(KeyTable::default_bucket_max_size(), 511);
    assert_eq!(IntTable::default_header_max_depth(), 9);
    assert_eq!(IntTable::default_directory_max_depth(), 9);
}

#[test]
fn s2b_15_reading_an_empty_table_pins_nothing() {
    let bpm = bpm(2);
    let ht = int_table(&bpm, 0, 3, 4);
    ht.get_value(&1);
    ht.verify_integrity();
    assert_eq!(bpm.get_pin_count(ht.get_header_page_id()), Some(0));
}

// ---- 2b-16 · insert: the first key creates a directory and a bucket -----------------------------------------------------------------------

/// The page ids reachable from the header: (directory page id, its bucket page ids).
fn page_ids(bpm: &BufferPoolManager, ht: &IntTable<'_>) -> Vec<(PageId, Vec<PageId>)> {
    let header_guard = bpm.read_page(ht.get_header_page_id());
    let header = Header::new(&header_guard[..]);
    let mut out = Vec::new();
    for i in 0..header.max_size() {
        let dir_id = header.get_directory_page_id(i);
        if dir_id.is_valid() {
            let dir_guard = bpm.read_page(dir_id);
            let dir = Directory::new(&dir_guard[..]);
            out.push((dir_id, (0..dir.size()).map(|s| dir.get_bucket_page_id(s)).collect()));
        }
    }
    out
}

#[test]
fn s2b_16_the_first_insert_makes_a_directory_and_a_bucket() {
    let bpm = bpm(10);
    let ht = int_table(&bpm, 0, 3, 4);
    assert!(ht.insert(&5, &50));
    let ids = page_ids(&bpm, &ht);
    assert_eq!(ids.len(), 1);
    let (dir_id, buckets) = &ids[0];
    assert_eq!(buckets.len(), 1);
    let dir_guard = bpm.read_page(*dir_id);
    let dir = Directory::new(&dir_guard[..]);
    assert_eq!((dir.get_global_depth(), dir.get_local_depth(0), dir.get_max_depth()), (0, 0, 3));
    let bucket_guard = bpm.read_page(buckets[0]);
    let bucket = Bucket::<_, i32, i32>::new(&bucket_guard[..]);
    assert_eq!((bucket.size(), bucket.max_size()), (1, 4));
    assert_eq!(bucket.entry_at(0), (5, 50));
}

#[test]
fn s2b_16_keys_with_different_top_bits_get_different_directories() {
    let bpm = bpm(20);
    let ht = int_table(&bpm, 2, 3, 4);
    let hash = HashFunction::<i32>::new();
    let header_guard = bpm.read_page(ht.get_header_page_id());
    let header_idx = |k: i32| Header::new(&header_guard[..]).hash_to_directory_index(hash.get_hash(&k) as u32);
    // pick keys in two different directory slots
    let a = 0;
    let b = (1..200).find(|&k| header_idx(k) != header_idx(a)).expect("some key lands elsewhere");
    drop(header_guard);
    assert!(ht.insert(&a, &1));
    assert!(ht.insert(&b, &2));
    assert_eq!(page_ids(&bpm, &ht).len(), 2);
}

#[test]
fn s2b_16_inserting_leaves_nothing_pinned() {
    let bpm = bpm(4);
    let ht = int_table(&bpm, 0, 3, 4);
    assert!(ht.insert(&1, &1));
    assert_eq!(bpm.get_pin_count(ht.get_header_page_id()), Some(0));
    for (dir_id, buckets) in page_ids(&bpm, &ht) {
        assert_eq!(bpm.get_pin_count(dir_id), Some(0));
        assert!(buckets.iter().all(|b| bpm.get_pin_count(*b) == Some(0)));
    }
}

#[test]
fn s2b_16_the_table_passes_its_own_integrity_check_after_the_first_insert() {
    let bpm = bpm(10);
    let ht = int_table(&bpm, 1, 3, 4);
    ht.insert(&3, &3);
    ht.verify_integrity();
}

// ---- 2b-17 · insert into an existing bucket, and get_value --------------------------------------------------------------------------------

#[test]
fn s2b_17_inserted_values_can_be_read_back() {
    let bpm = bpm(10);
    let ht = int_table(&bpm, 0, 3, 8);
    for i in 0..8 {
        assert!(ht.insert(&i, &(i * 10)));
        assert_eq!(ht.get_value(&i), vec![i * 10]);
    }
    for i in 0..8 {
        assert_eq!(ht.get_value(&i), vec![i * 10]);
    }
}

#[test]
fn s2b_17_missing_keys_have_no_value() {
    let bpm = bpm(10);
    let ht = int_table(&bpm, 0, 3, 8);
    for i in 0..5 {
        ht.insert(&i, &i);
    }
    for i in 5..10 {
        assert!(ht.get_value(&i).is_empty());
    }
}

#[test]
fn s2b_17_a_duplicate_key_is_refused() {
    let bpm = bpm(10);
    let ht = int_table(&bpm, 0, 3, 8);
    assert!(ht.insert(&1, &10));
    assert!(!ht.insert(&1, &20));
    assert_eq!(ht.get_value(&1), vec![10]);
}

#[test]
fn s2b_17_several_directories_work_side_by_side() {
    let bpm = bpm(30);
    let ht = int_table(&bpm, 2, 3, 16);
    for i in 0..12 {
        assert!(ht.insert(&i, &(i + 100)));
    }
    for i in 0..12 {
        assert_eq!(ht.get_value(&i), vec![i + 100], "key {i}");
    }
    assert!(page_ids(&bpm, &ht).len() > 1, "12 keys should reach more than one of the 4 directories");
}

#[test]
fn s2b_17_lookups_leave_nothing_pinned_or_latched() {
    let bpm = bpm(4);
    let ht = int_table(&bpm, 0, 3, 8);
    ht.insert(&1, &1);
    for _ in 0..50 {
        ht.get_value(&1);
        ht.get_value(&2);
    }
    ht.insert(&2, &2); // would hang on a stuck latch
    assert_eq!(bpm.get_pin_count(ht.get_header_page_id()), Some(0));
}

// ---- 2b-18 · splitting a full bucket, and growing the directory ---------------------------------------------------------------------------

#[test]
fn s2b_18_eight_well_spread_keys_fit_a_ninth_does_not() {
    // BusTub's InsertTest1 (directory max depth 2, buckets of 2) assumes keys 0..8 land two to a bucket. With BusTub's own
    // MurmurHash3 they don't: 0, 2, 4 and 6 all end in the bits 00, so no correct table can hold them. This test picks keys that
    // do spread (two per value of the low two bits of the hash), which is the property the original meant.
    let bpm = bpm(50);
    let ht = int_table(&bpm, 0, 2, 2);
    let hash = HashFunction::<i32>::new();
    let mut per_class = [0; 4];
    let mut keys = Vec::new();
    for k in 0.. {
        let class = (hash.get_hash(&k) & 3) as usize;
        if per_class[class] < 2 {
            per_class[class] += 1;
            keys.push(k);
        }
        if keys.len() == 8 {
            break;
        }
    }
    for k in &keys {
        assert!(ht.insert(k, k), "key {k}");
        assert_eq!(ht.get_value(k), vec![*k]);
    }
    ht.verify_integrity();
    let ninth = (0..).find(|k| !keys.contains(k)).unwrap();
    assert!(!ht.insert(&ninth, &ninth), "every bucket is full and the directory can't grow");
}

#[test]
fn s2b_18_bustubs_key_0_to_7_do_not_all_fit_with_murmur() {
    // The same test with BusTub's literal keys: four of them share their low bits, so the fifth of those is refused.
    let bpm = bpm(50);
    let ht = int_table(&bpm, 0, 2, 2);
    let accepted = (0..8).filter(|k| ht.insert(k, k)).count();
    assert_eq!(accepted, 5, "keys 0 and 2 fit in the 00 bucket (4 and 6 don't), 1 in the 10 bucket, 3 and 5 in the 11 bucket (7 doesn't)");
    ht.verify_integrity();
}

#[test]
fn s2b_18_a_split_distributes_the_entries_by_the_new_bit() {
    let bpm = bpm(20);
    let ht = int_table(&bpm, 0, 4, 2);
    let hash = HashFunction::<i32>::new();
    // find three keys that share their lowest hash bit, so the third forces a split of a depth-0 bucket
    let keys: Vec<i32> = (0..100).filter(|k| hash.get_hash(k) & 1 == 0).take(3).collect();
    for k in &keys {
        assert!(ht.insert(k, k));
    }
    let ids = page_ids(&bpm, &ht);
    let (dir_id, buckets) = &ids[0];
    let dir_guard = bpm.read_page(*dir_id);
    let dir = Directory::new(&dir_guard[..]);
    assert!(dir.get_global_depth() >= 1, "the directory grew");
    assert!(buckets.len() >= 2);
    dir.verify_integrity();
    for k in &keys {
        assert_eq!(ht.get_value(k), vec![*k]);
    }
}

#[test]
fn s2b_18_many_keys_survive_many_splits() {
    let bpm = bpm(60);
    let ht = int_table(&bpm, 0, 9, 4);
    for i in 0..400 {
        assert!(ht.insert(&i, &(i * 3)), "key {i}");
    }
    ht.verify_integrity();
    for i in 0..400 {
        assert_eq!(ht.get_value(&i), vec![i * 3], "key {i}");
    }
    assert!(ht.get_value(&400).is_empty());
}

#[test]
fn s2b_18_the_directory_stops_growing_at_its_max_depth() {
    let bpm = bpm(60);
    let ht = int_table(&bpm, 0, 3, 2); // 8 slots x 2 = at most 16 keys
    let mut inserted = 0;
    for i in 0..100 {
        if ht.insert(&i, &i) {
            inserted += 1;
        }
    }
    assert!(inserted <= 16);
    assert!(inserted >= 8, "a decent hash gets at least half the capacity: {inserted}");
    ht.verify_integrity();
    let guard = bpm.read_page(ht.get_header_page_id());
    let dir_id = Header::new(&guard[..]).get_directory_page_id(0);
    drop(guard);
    let dir_guard = bpm.read_page(dir_id);
    assert_eq!(Directory::new(&dir_guard[..]).get_global_depth(), 3);
}

#[test]
fn s2b_18_a_model_with_random_keys() {
    let bpm = bpm(100);
    let ht = int_table(&bpm, 1, 9, 8);
    let mut model: HashMap<i32, i32> = HashMap::new();
    let mut rng = Lcg(11);
    for _ in 0..600 {
        let k = rng.next(500) as i32;
        let v = rng.next(1000) as i32;
        let expect_new = !model.contains_key(&k);
        assert_eq!(ht.insert(&k, &v), expect_new, "key {k}");
        model.entry(k).or_insert(v);
    }
    ht.verify_integrity();
    for (k, v) in &model {
        assert_eq!(ht.get_value(k), vec![*v], "key {k}");
    }
}

#[test]
fn s2b_18_splitting_does_not_leak_pins() {
    let bpm = bpm(8);
    let ht = int_table(&bpm, 0, 9, 2);
    for i in 0..100 {
        ht.insert(&i, &i);
    }
    for (dir_id, buckets) in page_ids(&bpm, &ht) {
        assert_eq!(bpm.get_pin_count(dir_id), Some(0));
        assert!(buckets.iter().all(|b| bpm.get_pin_count(*b).unwrap_or(0) == 0));
    }
}

// ---- 2b-19 · remove -------------------------------------------------------------------------------------------------------------------------

#[test]
fn s2b_19_remove_takes_a_key_out() {
    let bpm = bpm(10);
    let ht = int_table(&bpm, 0, 3, 8);
    for i in 0..5 {
        ht.insert(&i, &i);
    }
    assert!(ht.remove(&2));
    assert!(ht.get_value(&2).is_empty());
    assert_eq!(ht.get_value(&3), vec![3]);
}

#[test]
fn s2b_19_removing_a_missing_key_is_false() {
    let bpm = bpm(10);
    let ht = int_table(&bpm, 0, 3, 8);
    assert!(!ht.remove(&1), "an empty table has nothing to remove");
    ht.insert(&1, &1);
    assert!(!ht.remove(&2));
    assert!(ht.remove(&1));
    assert!(!ht.remove(&1), "the second removal finds nothing");
}

#[test]
fn s2b_19_a_removed_key_can_be_inserted_again() {
    let bpm = bpm(10);
    let ht = int_table(&bpm, 0, 3, 8);
    ht.insert(&1, &10);
    ht.remove(&1);
    assert!(ht.insert(&1, &20));
    assert_eq!(ht.get_value(&1), vec![20]);
}

#[test]
fn s2b_19_removing_from_a_grown_table() {
    let bpm = bpm(60);
    let ht = int_table(&bpm, 1, 9, 4);
    for i in 0..200 {
        ht.insert(&i, &i);
    }
    for i in (0..200).step_by(2) {
        assert!(ht.remove(&i), "key {i}");
    }
    ht.verify_integrity();
    for i in 0..200 {
        assert_eq!(ht.get_value(&i).len(), (i % 2) as usize, "key {i}");
    }
}

#[test]
fn s2b_19_bustubs_remove_test_1() {
    let bpm = bpm(50);
    let ht = int_table(&bpm, 2, 3, 2);
    let n = 5;
    for i in 0..n {
        assert!(ht.insert(&i, &i));
        assert_eq!(ht.get_value(&i), vec![i]);
    }
    ht.verify_integrity();
    for i in n..2 * n {
        assert!(ht.get_value(&i).is_empty());
    }
    for i in 0..n {
        assert!(ht.remove(&i));
        assert!(ht.get_value(&i).is_empty());
    }
    ht.verify_integrity();
    for i in n..2 * n {
        assert!(!ht.remove(&i));
        assert!(ht.get_value(&i).is_empty());
    }
    ht.verify_integrity();
}

// ---- 2b-20 · merging empty buckets -------------------------------------------------------------------------------------------------------------

fn bucket_count(bpm: &BufferPoolManager, ht: &IntTable<'_>) -> usize {
    let mut distinct: Vec<PageId> = page_ids(bpm, ht).into_iter().flat_map(|(_, b)| b).collect();
    distinct.sort();
    distinct.dedup();
    distinct.len()
}

#[test]
fn s2b_20_emptying_a_bucket_merges_it_with_its_split_image() {
    let bpm = bpm(30);
    let ht = int_table(&bpm, 0, 4, 2);
    for i in 0..16 {
        ht.insert(&i, &i);
    }
    let before = bucket_count(&bpm, &ht);
    assert!(before >= 4);
    for i in 0..16 {
        ht.remove(&i);
    }
    ht.verify_integrity();
    assert!(bucket_count(&bpm, &ht) < before, "empty buckets must be merged away");
}

#[test]
fn s2b_20_a_merged_bucket_page_is_deleted_from_the_pool() {
    let bpm = bpm(30);
    let ht = int_table(&bpm, 0, 4, 2);
    for i in 0..16 {
        ht.insert(&i, &i);
    }
    let all: Vec<PageId> = page_ids(&bpm, &ht).into_iter().flat_map(|(_, b)| b).collect();
    for i in 0..16 {
        ht.remove(&i);
    }
    let alive: Vec<PageId> = page_ids(&bpm, &ht).into_iter().flat_map(|(_, b)| b).collect();
    // every page that left the directory is gone from the pool (deleted, not just unreferenced)
    for page in all.iter().filter(|p| !alive.contains(p)) {
        assert_eq!(bpm.get_pin_count(*page), None, "page {page:?} should have been deleted");
    }
}

#[test]
fn s2b_20_merging_keeps_every_remaining_key_findable() {
    let bpm = bpm(60);
    let ht = int_table(&bpm, 0, 9, 4);
    for i in 0..300 {
        ht.insert(&i, &i);
    }
    for i in 0..300 {
        if i % 3 != 0 {
            assert!(ht.remove(&i));
        }
    }
    ht.verify_integrity();
    for i in 0..300 {
        assert_eq!(ht.get_value(&i).len(), (i % 3 == 0) as usize, "key {i}");
    }
}

#[test]
fn s2b_20_a_table_emptied_completely_is_one_bucket_again() {
    let bpm = bpm(60);
    let ht = int_table(&bpm, 0, 9, 4);
    for i in 0..200 {
        ht.insert(&i, &i);
    }
    for i in 0..200 {
        assert!(ht.remove(&i));
    }
    ht.verify_integrity();
    assert_eq!(bucket_count(&bpm, &ht), 1);
}

#[test]
fn s2b_20_the_table_works_after_everything_was_removed() {
    let bpm = bpm(60);
    let ht = int_table(&bpm, 0, 9, 4);
    for round in 0..3 {
        for i in 0..150 {
            assert!(ht.insert(&i, &(i + round)), "round {round} key {i}");
        }
        for i in 0..150 {
            assert!(ht.remove(&i));
        }
        ht.verify_integrity();
    }
}

// ---- 2b-21 · shrinking the directory -------------------------------------------------------------------------------------------------------------

fn global_depth(bpm: &BufferPoolManager, ht: &IntTable<'_>) -> u32 {
    let guard = bpm.read_page(ht.get_header_page_id());
    let dir_id = Header::new(&guard[..]).get_directory_page_id(0);
    drop(guard);
    let dir_guard = bpm.read_page(dir_id);
    Directory::new(&dir_guard[..]).get_global_depth()
}

#[test]
fn s2b_21_a_table_that_was_emptied_shrinks_to_global_depth_zero() {
    let bpm = bpm(60);
    let ht = int_table(&bpm, 0, 9, 4);
    for i in 0..200 {
        ht.insert(&i, &i);
    }
    assert!(global_depth(&bpm, &ht) >= 3);
    for i in 0..200 {
        ht.remove(&i);
    }
    assert_eq!(global_depth(&bpm, &ht), 0);
}

#[test]
fn s2b_21_the_directory_shrinks_as_buckets_merge_not_only_at_the_end() {
    let bpm = bpm(60);
    let ht = int_table(&bpm, 0, 9, 2);
    for i in 0..64 {
        ht.insert(&i, &i);
    }
    let full = global_depth(&bpm, &ht);
    for i in 0..48 {
        ht.remove(&i);
    }
    let after = global_depth(&bpm, &ht);
    assert!(after < full, "{after} should be below {full}");
    ht.verify_integrity();
    for i in 48..64 {
        assert_eq!(ht.get_value(&i), vec![i]);
    }
}

#[test]
fn s2b_21_a_directory_that_cannot_shrink_keeps_its_depth() {
    let bpm = bpm(60);
    let ht = int_table(&bpm, 0, 9, 2);
    for i in 0..64 {
        ht.insert(&i, &i);
    }
    let depth = global_depth(&bpm, &ht);
    ht.remove(&0);
    assert!(global_depth(&bpm, &ht) <= depth);
    ht.verify_integrity();
}

#[test]
fn s2b_21_a_model_with_random_inserts_and_removes() {
    let bpm = bpm(100);
    let ht = int_table(&bpm, 0, 9, 4);
    let mut model: HashMap<i32, i32> = HashMap::new();
    let mut rng = Lcg(2024);
    for step in 0..2000 {
        let k = rng.next(300) as i32;
        if rng.next(2) == 0 {
            let expect = !model.contains_key(&k);
            assert_eq!(ht.insert(&k, &step), expect, "step {step} insert {k}");
            model.entry(k).or_insert(step);
        } else {
            assert_eq!(ht.remove(&k), model.remove(&k).is_some(), "step {step} remove {k}");
        }
        if step % 100 == 0 {
            ht.verify_integrity();
        }
    }
    ht.verify_integrity();
    for k in 0..300 {
        assert_eq!(ht.get_value(&k), model.get(&k).map(|v| vec![*v]).unwrap_or_default(), "key {k}");
    }
}

// ---- 2b-22 · the module as a whole -------------------------------------------------------------------------------------------------------------

fn gk(n: i64) -> GenericKey<8> {
    key(n)
}

fn key_table(bpm: &BufferPoolManager) -> KeyTable<'_> {
    DiskExtendibleHashTable::new("blah", bpm, GenericComparator::<8>, HashFunction::new(), 9, 9, KeyTable::default_bucket_max_size())
}

fn insert_keys(ht: &KeyTable<'_>, keys: &[i64]) {
    for &k in keys {
        ht.insert(&gk(k), &Rid::new(PageId((k >> 32) as i32), (k & 0xFFFF_FFFF) as u32));
    }
}

#[test]
fn s2b_22_two_threads_insert_the_same_keys() {
    let bpm = bpm(50);
    let ht = key_table(&bpm);
    let keys: Vec<i64> = (1..100).collect();
    thread::scope(|s| {
        for _ in 0..2 {
            s.spawn(|| insert_keys(&ht, &keys));
        }
    });
    for &k in &keys {
        let found = ht.get_value(&gk(k));
        assert_eq!(found.len(), 1, "key {k}");
        assert_eq!(found[0].slot_num() as i64, k & 0xFFFF_FFFF);
    }
}

#[test]
fn s2b_22_two_threads_insert_disjoint_keys() {
    let bpm = bpm(50);
    let ht = key_table(&bpm);
    let keys: Vec<i64> = (1..100).collect();
    thread::scope(|s| {
        for t in 0..2i64 {
            let (ht, keys) = (&ht, &keys);
            s.spawn(move || {
                let mine: Vec<i64> = keys.iter().copied().filter(|k| k % 2 == t).collect();
                insert_keys(ht, &mine);
            });
        }
    });
    for &k in &keys {
        assert_eq!(ht.get_value(&gk(k)).len(), 1, "key {k}");
    }
}

#[test]
fn s2b_22_two_threads_delete_the_same_keys() {
    let bpm = bpm(50);
    let ht = key_table(&bpm);
    insert_keys(&ht, &[1, 2, 3, 4, 5]);
    thread::scope(|s| {
        for _ in 0..2 {
            s.spawn(|| {
                for k in [1, 5, 3, 4] {
                    ht.remove(&gk(k));
                }
            });
        }
    });
    for k in 1..=5 {
        assert_eq!(ht.get_value(&gk(k)).len(), (k == 2) as usize, "key {k}");
    }
}

#[test]
fn s2b_22_two_threads_delete_disjoint_keys() {
    let bpm = bpm(50);
    let ht = key_table(&bpm);
    insert_keys(&ht, &(1..=10).collect::<Vec<_>>());
    thread::scope(|s| {
        for t in 0..2i64 {
            let ht = &ht;
            s.spawn(move || {
                for k in [1, 4, 3, 2, 5, 6] {
                    if k % 2 == t {
                        ht.remove(&gk(k));
                    }
                }
            });
        }
    });
    for k in 1..=10 {
        assert_eq!(ht.get_value(&gk(k)).len(), (k > 6) as usize, "key {k}");
    }
}

#[test]
fn s2b_22_inserts_deletes_and_lookups_at_once() {
    // BusTub's MixTest2: preserved keys (multiples of 5) must always be findable while others are inserted and deleted.
    let bpm = bpm(50);
    let ht = key_table(&bpm);
    let (preserved, dynamic): (Vec<i64>, Vec<i64>) = (1..=50).partition(|k| k % 5 == 0);
    insert_keys(&ht, &preserved);
    thread::scope(|s| {
        for i in 0..6 {
            let (ht, preserved, dynamic) = (&ht, &preserved, &dynamic);
            s.spawn(move || match i % 3 {
                0 => insert_keys(ht, dynamic),
                1 => {
                    for &k in dynamic {
                        ht.remove(&gk(k));
                    }
                }
                _ => {
                    for &k in preserved {
                        assert_eq!(ht.get_value(&gk(k)).len(), 1, "preserved key {k} must always be there");
                    }
                }
            });
        }
    });
    for &k in &preserved {
        assert_eq!(ht.get_value(&gk(k)).len(), 1);
    }
}

#[test]
fn s2b_22_a_heavy_concurrent_workload_keeps_the_table_consistent() {
    let bpm = bpm(100);
    let ht = int_table(&bpm, 2, 9, 4);
    thread::scope(|s| {
        for t in 0..4 {
            let ht = &ht;
            s.spawn(move || {
                let mut rng = Lcg(100 + t);
                for _ in 0..1500 {
                    let k = (rng.next(200) * 4) as i32 + t as i32; // each thread owns its residue class
                    match rng.next(3) {
                        0 => {
                            ht.insert(&k, &k);
                        }
                        1 => {
                            ht.remove(&k);
                        }
                        _ => {
                            let v = ht.get_value(&k);
                            assert!(v.is_empty() || v == vec![k]);
                        }
                    }
                }
            });
        }
    });
    ht.verify_integrity();
}
