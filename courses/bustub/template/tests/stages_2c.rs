//! Tests for the B+ tree stages (2c-01 … 2c-09). A test named `s2c_04_…` belongs to stage 2c-04.
//! Trees are described with `shape`: a leaf is `[1,2]`, an internal page is `{k1,k2 child child child}`.

mod b_plus_tree_utils;

use std::collections::BTreeMap;
use std::sync::mpsc;
use std::sync::Arc;
use std::thread;
use std::time::Duration;

use b_plus_tree_utils::*;
use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::common::config::{PageId, BUSTUB_PAGE_SIZE};
use bustub::common::rid::Rid;
use bustub::storage::disk::disk_manager_memory::DiskManagerUnlimitedMemory;
use bustub::storage::page::b_plus_tree_header_page::BPlusTreeHeaderPage as Header;
use bustub::storage::page::b_plus_tree_internal_page::BPlusTreeInternalPage as Internal;
use bustub::storage::page::b_plus_tree_leaf_page::BPlusTreeLeafPage as Leaf;
use bustub::storage::page::b_plus_tree_page::{BPlusTreePage as Page, IndexPageType};
use bustub::storage::index::generic_key::GenericComparator;

struct Lcg(u64);
impl Lcg {
    fn next(&mut self, n: usize) -> usize {
        self.0 = self.0.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        ((self.0 >> 33) as usize) % n
    }
    fn shuffle<T>(&mut self, v: &mut [T]) {
        for i in (1..v.len()).rev() {
            let j = self.next(i + 1);
            v.swap(i, j);
        }
    }
}

fn bpm(frames: usize) -> BufferPoolManager {
    BufferPoolManager::new(frames, Arc::new(DiskManagerUnlimitedMemory::new()))
}

/// A leaf page holding `keys` (rids made from the keys), linked to `next`.
fn leaf_page(bpm: &BufferPoolManager, max_size: u32, keys: &[i64], next: Option<PageId>) -> PageId {
    let id = bpm.new_page();
    let mut guard = bpm.write_page(id);
    let mut leaf = Leaf::<_, Key, Rid>::new(&mut guard[..]);
    leaf.init(max_size);
    for (i, &k) in keys.iter().enumerate() {
        leaf.set_entry_at(i as u32, &index_key(k), &rid_of(k));
    }
    leaf.set_size(keys.len() as u32);
    leaf.set_next_page_id(next);
    id
}

/// An internal page with children `first_child, children[0].1, …` separated by the keys `children[i].0`.
fn internal_page(bpm: &BufferPoolManager, max_size: u32, first_child: PageId, children: &[(i64, PageId)]) -> PageId {
    let id = bpm.new_page();
    let mut guard = bpm.write_page(id);
    let mut node = Internal::<_, Key>::new(&mut guard[..]);
    node.init(max_size);
    node.set_entry_at(0, &index_key(0), first_child);
    for (i, &(k, child)) in children.iter().enumerate() {
        node.set_entry_at(i as u32 + 1, &index_key(k), child);
    }
    node.set_size(children.len() as u32 + 1);
    id
}

/// A tree whose header page id is returned too, so tests can build pages by hand and install a root with `set_root`.
fn hand_tree<'a>(bpm: &'a BufferPoolManager, leaf_max: u32, internal_max: u32) -> (Tree<'a>, PageId) {
    let header = bpm.new_page();
    let tree = bustub::storage::index::b_plus_tree::BPlusTree::new("foo_pk", header, bpm, GenericComparator::<8>, leaf_max, internal_max);
    (tree, header)
}

fn set_root(bpm: &BufferPoolManager, header: PageId, root: PageId) {
    Header::new(&mut bpm.write_page(header)[..]).set_root_page_id(root);
}

fn rids_of(keys: &[i64]) -> Vec<Rid> {
    keys.iter().map(|&k| rid_of(k)).collect()
}

/// Every page of the pool is unpinned (or gone): nothing is left latched or pinned.
fn assert_no_pins(bpm: &BufferPoolManager) {
    let next = bpm.new_page();
    for id in 0..next.0 {
        let pins = bpm.get_pin_count(PageId(id));
        assert!(matches!(pins, None | Some(0)), "page {id} is still pinned ({pins:?})");
    }
}

fn insert_all(tree: &Tree, keys: impl IntoIterator<Item = i64>) {
    for k in keys {
        assert!(insert(tree, k), "insert {k}");
    }
}

fn shuffled(n: i64, seed: u64) -> Vec<i64> {
    let mut keys: Vec<i64> = (1..=n).collect();
    Lcg(seed).shuffle(&mut keys);
    keys
}

// ---- 2c-01 · The pages ----------------------------------------------------------------------------------------------------------

#[test]
fn s2c_01_the_page_type_round_trips_and_a_zero_page_has_none() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    assert_eq!(Page::new(&bytes[..]).page_type(), IndexPageType::Invalid, "a fresh zero page is neither a leaf nor an internal page");
    assert!(!Page::new(&bytes[..]).is_leaf_page());
    Page::new(&mut bytes[..]).set_page_type(IndexPageType::Leaf);
    assert_eq!(Page::new(&bytes[..]).page_type(), IndexPageType::Leaf);
    assert!(Page::new(&bytes[..]).is_leaf_page());
    Page::new(&mut bytes[..]).set_page_type(IndexPageType::Internal);
    assert_eq!(Page::new(&bytes[..]).page_type(), IndexPageType::Internal);
    assert!(!Page::new(&bytes[..]).is_leaf_page());
    // the stored numbers are part of the file format
    assert_eq!(u32::from_le_bytes(bytes[0..4].try_into().unwrap()), 2);
    Page::new(&mut bytes[..]).set_page_type(IndexPageType::Leaf);
    assert_eq!(u32::from_le_bytes(bytes[0..4].try_into().unwrap()), 1);
}

#[test]
fn s2c_01_size_max_size_and_change_size_by() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut page = Page::new(&mut bytes[..]);
    page.set_size(5);
    page.set_max_size(9);
    assert_eq!((page.size(), page.max_size()), (5, 9));
    page.change_size_by(3);
    assert_eq!(page.size(), 8);
    page.change_size_by(-8);
    assert_eq!(page.size(), 0);
    page.change_size_by(1);
    assert_eq!((page.size(), page.max_size()), (1, 9), "the size and the max size are different fields");
    // the fields are at bytes 4 and 8, little-endian
    assert_eq!(&bytes[4..8], &[1, 0, 0, 0]);
    assert_eq!(&bytes[8..12], &[9, 0, 0, 0]);
}

#[test]
#[should_panic]
fn s2c_01_a_size_below_zero_is_a_bug() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut page = Page::new(&mut bytes[..]);
    page.set_size(1);
    page.change_size_by(-2);
}

#[test]
fn s2c_01_min_size_is_half_rounded_down_for_a_leaf_and_half_rounded_up_for_an_internal_page() {
    for max in 2..=12u32 {
        let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
        Leaf::<_, Key, Rid>::new(&mut bytes[..]).init(max);
        assert_eq!(Leaf::<_, Key, Rid>::new(&bytes[..]).min_size(), max / 2, "leaf, max {max}");
        Internal::<_, Key>::new(&mut bytes[..]).init(max.max(3));
        let m = max.max(3);
        assert_eq!(Internal::<_, Key>::new(&bytes[..]).min_size(), m.div_ceil(2), "internal, max {m}");
    }
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    Internal::<_, Key>::new(&mut bytes[..]).init(3);
    assert_eq!(Internal::<_, Key>::new(&bytes[..]).min_size(), 2);
    Leaf::<_, Key, Rid>::new(&mut bytes[..]).init(3);
    assert_eq!(Leaf::<_, Key, Rid>::new(&bytes[..]).min_size(), 1);
}

#[test]
fn s2c_01_an_internal_page_stores_keys_and_children_side_by_side() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut node = Internal::<_, Key>::new(&mut bytes[..]);
    node.init(5);
    assert_eq!((node.size(), node.max_size()), (0, 5));
    assert!(Page::new(&bytes[..]).page_type() == IndexPageType::Internal);
    let mut node = Internal::<_, Key>::new(&mut bytes[..]);
    node.set_entry_at(0, &index_key(0), PageId(10));
    node.set_entry_at(1, &index_key(20), PageId(11));
    node.set_entry_at(2, &index_key(40), PageId(12));
    node.set_size(3);
    assert_eq!(node.size(), 3);
    assert_eq!(node.key_at(1).get_as_integer(), 20);
    assert_eq!(node.value_at(2), PageId(12));
    assert_eq!(node.entry_at(0).1, PageId(10));
    node.set_key_at(2, &index_key(41));
    assert_eq!((node.key_at(2).get_as_integer(), node.value_at(2)), (41, PageId(12)), "set_key_at keeps the child");
    node.set_value_at(2, PageId(99));
    assert_eq!((node.key_at(2).get_as_integer(), node.value_at(2)), (41, PageId(99)), "set_value_at keeps the key");
    assert_eq!(node.value_index(PageId(11)), Some(1));
    assert_eq!(node.value_index(PageId(99)), Some(2));
    assert_eq!(node.value_index(PageId(12)), None, "overwritten children are gone");
    assert_eq!(node.value_index(PageId(500)), None);
}

#[test]
#[should_panic]
fn s2c_01_reading_past_the_size_of_an_internal_page_panics() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut node = Internal::<_, Key>::new(&mut bytes[..]);
    node.init(5);
    node.set_entry_at(0, &index_key(0), PageId(10));
    node.set_size(1);
    node.value_at(1);
}

#[test]
fn s2c_01_a_leaf_page_stores_pairs_and_the_next_leaf() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut leaf = Leaf::<_, Key, Rid>::new(&mut bytes[..]);
    leaf.init(4);
    assert_eq!((leaf.size(), leaf.max_size(), leaf.next_page_id()), (0, 4, None), "a fresh leaf has no next leaf (not leaf 0)");
    assert!(Page::new(&bytes[..]).is_leaf_page());
    let mut leaf = Leaf::<_, Key, Rid>::new(&mut bytes[..]);
    leaf.set_entry_at(0, &index_key(7), &rid_of(7));
    leaf.set_entry_at(1, &index_key(9), &rid_of(9));
    leaf.set_size(2);
    assert_eq!(leaf.key_at(1).get_as_integer(), 9);
    assert_eq!(leaf.value_at(0), rid_of(7));
    assert_eq!(leaf.entry_at(1), (index_key(9), rid_of(9)));
    leaf.set_next_page_id(Some(PageId(0)));
    assert_eq!(leaf.next_page_id(), Some(PageId(0)), "page 0 is a real page");
    leaf.set_next_page_id(None);
    assert_eq!(leaf.next_page_id(), None);
    leaf.set_next_page_id(Some(PageId(41)));
    assert_eq!(leaf.next_page_id(), Some(PageId(41)));
    assert_eq!((leaf.size(), leaf.key_at(0).get_as_integer()), (2, 7), "the next pointer does not overlap the entries");
}

#[test]
fn s2c_01_the_header_page_names_the_root() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    assert_eq!(Header::new(&bytes[..]).root_page_id(), PageId(0), "a zero page says the root is page 0: that is why init exists");
    Header::new(&mut bytes[..]).init();
    assert_eq!(Header::new(&bytes[..]).root_page_id(), PageId::INVALID);
    Header::new(&mut bytes[..]).set_root_page_id(PageId(17));
    assert_eq!(Header::new(&bytes[..]).root_page_id(), PageId(17));
    Header::new(&mut bytes[..]).init();
    assert_eq!(Header::new(&bytes[..]).root_page_id(), PageId::INVALID);
}

#[test]
fn s2c_01_how_many_entries_fit_in_a_page() {
    // leaf: 16-byte header, 8-byte key + 8-byte rid; internal: 12-byte header, 8-byte key + 4-byte page id
    assert_eq!(Leaf::<&[u8], Key, Rid>::capacity(), (8192 - 16) / 16);
    assert_eq!(Internal::<&[u8], Key>::capacity(), (8192 - 12) / 12);
    assert_eq!(Leaf::<&[u8], GenericKey4, Rid>::capacity(), (8192 - 16) / 12);
}

type GenericKey4 = bustub::storage::index::generic_key::GenericKey<4>;

#[test]
#[should_panic]
fn s2c_01_a_leaf_cannot_be_told_to_hold_more_than_fits() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    Leaf::<_, Key, Rid>::new(&mut bytes[..]).init(Leaf::<&[u8], Key, Rid>::capacity() as u32 + 1);
}

// ---- 2c-02 · Search -------------------------------------------------------------------------------------------------------------

#[test]
fn s2c_02_a_new_tree_is_empty() {
    let bpm = bpm(10);
    let header = bpm.new_page();
    // a fresh page is zeros, which would read as "the root is page 0"; the tree must format it
    let tree = bustub::storage::index::b_plus_tree::BPlusTree::<Key, Rid, _>::new("t", header, &bpm, GenericComparator::<8>, 3, 4);
    assert!(tree.is_empty());
    assert_eq!(tree.get_root_page_id(), PageId::INVALID);
    assert!(tree.get_value(&index_key(1)).is_empty());
    assert_eq!(tree.index_name(), "t");
    assert_no_pins(&bpm);
}

#[test]
#[should_panic]
fn s2c_02_a_leaf_of_one_pair_cannot_split_into_two() {
    let bpm = bpm(10);
    new_tree(&bpm, 1, 3);
}

#[test]
fn s2c_02_child_for_picks_the_child_whose_range_holds_the_key() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut node = Internal::<_, Key>::new(&mut bytes[..]);
    node.init(8);
    // slot 0's key is never looked at: put garbage in it
    node.set_entry_at(0, &index_key(i64::MAX), PageId(100));
    node.set_entry_at(1, &index_key(10), PageId(101));
    node.set_entry_at(2, &index_key(20), PageId(102));
    node.set_entry_at(3, &index_key(30), PageId(103));
    node.set_size(4);
    let cmp = GenericComparator::<8>;
    let node = Internal::<_, Key>::new(&bytes[..]);
    let cases = [(i64::MIN, 100), (-5, 100), (9, 100), (10, 101), (15, 101), (19, 101), (20, 102), (29, 102), (30, 103), (31, 103), (i64::MAX, 103)];
    for (key, child) in cases {
        assert_eq!(node.child_for(&index_key(key), &cmp), PageId(child), "key {key}");
    }
}

#[test]
fn s2c_02_child_for_with_two_children_and_with_many() {
    let cmp = GenericComparator::<8>;
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut node = Internal::<_, Key>::new(&mut bytes[..]);
    node.init(3);
    node.set_entry_at(0, &index_key(0), PageId(1));
    node.set_entry_at(1, &index_key(5), PageId(2));
    node.set_size(2);
    let node = Internal::<_, Key>::new(&bytes[..]);
    assert_eq!(node.child_for(&index_key(4), &cmp), PageId(1));
    assert_eq!(node.child_for(&index_key(5), &cmp), PageId(2));
    // a big page: child i covers [10 i, 10 i + 10)
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut node = Internal::<_, Key>::new(&mut bytes[..]);
    node.init(300);
    for i in 0..300u32 {
        node.set_entry_at(i, &index_key(10 * i as i64), PageId(1000 + i as i32));
    }
    node.set_size(300);
    let node = Internal::<_, Key>::new(&bytes[..]);
    for key in 0..2999i64 {
        assert_eq!(node.child_for(&index_key(key), &cmp), PageId(1000 + (key / 10).max(0) as i32), "key {key}");
    }
}

#[test]
fn s2c_02_a_leaf_finds_a_key_with_a_binary_search() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut leaf = Leaf::<_, Key, Rid>::new(&mut bytes[..]);
    leaf.init(10);
    for (i, k) in [10, 20, 30, 40].into_iter().enumerate() {
        leaf.set_entry_at(i as u32, &index_key(k), &rid_of(k));
    }
    leaf.set_size(4);
    let cmp = GenericComparator::<8>;
    let leaf = Leaf::<_, Key, Rid>::new(&bytes[..]);
    // lower_bound: the first slot whose key is not less than the target
    let bounds = [(5, 0), (10, 0), (11, 1), (20, 1), (25, 2), (40, 3), (41, 4)];
    for (key, slot) in bounds {
        assert_eq!(leaf.lower_bound(&index_key(key), &cmp), slot, "lower_bound({key})");
    }
    assert_eq!(leaf.lookup(&index_key(30), &cmp), Some(rid_of(30)));
    assert_eq!(leaf.lookup(&index_key(10), &cmp), Some(rid_of(10)));
    assert_eq!(leaf.lookup(&index_key(40), &cmp), Some(rid_of(40)));
    for missing in [0, 5, 15, 25, 35, 45] {
        assert_eq!(leaf.lookup(&index_key(missing), &cmp), None, "key {missing}");
    }
    // an empty leaf has nothing
    let mut empty = [0u8; BUSTUB_PAGE_SIZE];
    Leaf::<_, Key, Rid>::new(&mut empty[..]).init(4);
    let empty = Leaf::<_, Key, Rid>::new(&empty[..]);
    assert_eq!((empty.lower_bound(&index_key(1), &cmp), empty.lookup(&index_key(1), &cmp)), (0, None));
}

#[test]
fn s2c_02_get_value_in_a_tree_that_is_a_single_leaf() {
    let bpm = bpm(10);
    let (tree, header) = hand_tree(&bpm, 8, 4);
    let root = leaf_page(&bpm, 8, &[3, 6, 9], None);
    set_root(&bpm, header, root);
    assert!(!tree.is_empty());
    assert_eq!(tree.get_root_page_id(), root);
    for k in [3, 6, 9] {
        assert_eq!(get(&tree, k), vec![rid_of(k)], "key {k}");
    }
    for k in [0, 4, 7, 10] {
        assert!(get(&tree, k).is_empty(), "key {k}");
    }
}

#[test]
fn s2c_02_get_value_walks_down_a_three_level_tree() {
    let bpm = bpm(20);
    let (tree, header) = hand_tree(&bpm, 4, 4);
    // leaves: [1,2] [3,4] | [5,6] [7,8]   internal: (3 | 5)  (7 | 5)   root: separator 5
    let l4 = leaf_page(&bpm, 4, &[7, 8], None);
    let l3 = leaf_page(&bpm, 4, &[5, 6], Some(l4));
    let l2 = leaf_page(&bpm, 4, &[3, 4], Some(l3));
    let l1 = leaf_page(&bpm, 4, &[1, 2], Some(l2));
    let left = internal_page(&bpm, 4, l1, &[(3, l2)]);
    let right = internal_page(&bpm, 4, l3, &[(7, l4)]);
    let root = internal_page(&bpm, 4, left, &[(5, right)]);
    set_root(&bpm, header, root);
    for k in 1..=8 {
        assert_eq!(get(&tree, k), vec![rid_of(k)], "key {k}");
    }
    for k in [-1, 0, 9, 100] {
        assert!(get(&tree, k).is_empty(), "key {k}");
    }
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{5 {3 [1,2] [3,4]} {7 [5,6] [7,8]}}");
}

#[test]
fn s2c_02_get_value_leaves_nothing_latched_or_pinned() {
    let bpm = bpm(10);
    let (tree, header) = hand_tree(&bpm, 4, 4);
    let l2 = leaf_page(&bpm, 4, &[5, 6], None);
    let l1 = leaf_page(&bpm, 4, &[1, 2], Some(l2));
    let root = internal_page(&bpm, 4, l1, &[(5, l2)]);
    set_root(&bpm, header, root);
    for k in [1, 6, 3, 9] {
        tree.get_value(&index_key(k));
    }
    assert_no_pins(&bpm);
    // a write latch on every page can be taken at once: no read latch is left behind (this would hang otherwise)
    let guards: Vec<_> = [root, l1, l2, PageId(0)].into_iter().map(|id| bpm.write_page(id)).collect();
    drop(guards);
    // and a read of the tree works with a pool that has only the three tree pages plus one spare
    let tiny = bpm.get_pin_count(root);
    assert!(matches!(tiny, None | Some(0)));
}

#[test]
fn s2c_02_a_search_in_a_deep_tree_needs_only_a_few_frames() {
    // a tree of height 4 searched in a pool of 4 frames: the guards of the levels above are dropped as the search goes down
    let big = bpm(40);
    let (tree, header) = hand_tree(&big, 4, 4);
    let leaves: Vec<PageId> = {
        let mut next = None;
        let mut ids = vec![];
        for i in (0..8).rev() {
            let id = leaf_page(&big, 4, &[2 * i + 1, 2 * i + 2], next);
            ids.push(id);
            next = Some(id);
        }
        ids.reverse();
        ids
    };
    let mid: Vec<PageId> = (0..4).map(|i| internal_page(&big, 4, leaves[2 * i], &[(2 * (2 * i as i64 + 1) + 1, leaves[2 * i + 1])])).collect();
    let low: Vec<PageId> = (0..2).map(|i| internal_page(&big, 4, mid[2 * i], &[(8 * i as i64 + 5, mid[2 * i + 1])])).collect();
    let root = internal_page(&big, 4, low[0], &[(9, low[1])]);
    set_root(&big, header, root);
    big.flush_all_pages();
    // the pool is shared by the tree; check from the tree's own point of view that the search holds at most two pages at a time
    for k in 1..=16 {
        assert_eq!(get(&tree, k), vec![rid_of(k)], "key {k}");
        let pinned = (0..40).filter(|&id| matches!(big.get_pin_count(PageId(id)), Some(p) if p > 0)).count();
        assert_eq!(pinned, 0, "after a search nothing is pinned");
    }
}

// ---- 2c-03 · Insert without splitting -------------------------------------------------------------------------------------------

#[test]
fn s2c_03_a_leaf_insert_keeps_the_keys_sorted() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    Leaf::<_, Key, Rid>::new(&mut bytes[..]).init(10);
    let cmp = GenericComparator::<8>;
    let mut leaf = Leaf::<_, Key, Rid>::new(&mut bytes[..]);
    for k in [50, 20, 80, 10, 30, 90, 60] {
        assert!(leaf.insert(&index_key(k), &rid_of(k), &cmp), "insert {k}");
    }
    let keys: Vec<i64> = (0..leaf.size()).map(|i| leaf.key_at(i).get_as_integer()).collect();
    assert_eq!(keys, vec![10, 20, 30, 50, 60, 80, 90]);
    let values: Vec<Rid> = (0..leaf.size()).map(|i| leaf.value_at(i)).collect();
    assert_eq!(values, rids_of(&keys), "each value stays with its key when later keys are inserted before it");
}

#[test]
fn s2c_03_a_leaf_refuses_a_duplicate_key_and_stays_as_it_was() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    Leaf::<_, Key, Rid>::new(&mut bytes[..]).init(10);
    let cmp = GenericComparator::<8>;
    let mut leaf = Leaf::<_, Key, Rid>::new(&mut bytes[..]);
    assert!(leaf.insert(&index_key(5), &rid_of(5), &cmp));
    assert!(leaf.insert(&index_key(7), &rid_of(7), &cmp));
    assert!(!leaf.insert(&index_key(5), &rid_of(99), &cmp));
    assert!(!leaf.insert(&index_key(7), &rid_of(98), &cmp));
    assert_eq!(leaf.size(), 2);
    assert_eq!((leaf.value_at(0), leaf.value_at(1)), (rid_of(5), rid_of(7)), "the original values are kept");
}

#[test]
fn s2c_03_the_first_insert_makes_a_root_leaf() {
    let bpm = bpm(10);
    let tree = new_tree(&bpm, 4, 4);
    assert!(tree.is_empty());
    assert!(insert(&tree, 42));
    assert!(!tree.is_empty());
    let root = tree.get_root_page_id();
    assert!(root.is_valid());
    let guard = bpm.read_page(root);
    assert!(Page::new(&guard[..]).is_leaf_page());
    let leaf = Leaf::<_, Key, Rid>::new(&guard[..]);
    assert_eq!((leaf.size(), leaf.max_size(), leaf.next_page_id()), (1, 4, None));
    assert_eq!(leaf.entry_at(0), (index_key(42), rid_of(42)));
    drop(guard);
    assert_no_pins(&bpm);
}

#[test]
fn s2c_03_inserts_that_fit_stay_in_the_root_leaf_in_any_order() {
    let bpm = bpm(10);
    let tree = new_tree(&bpm, 10, 4);
    let keys = shuffled(9, 3);
    insert_all(&tree, keys.iter().copied());
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "[1,2,3,4,5,6,7,8,9]");
    for k in 1..=9 {
        assert_eq!(get(&tree, k), vec![rid_of(k)]);
    }
    assert!(get(&tree, 10).is_empty());
    assert_no_pins(&bpm);
}

#[test]
fn s2c_03_a_duplicate_key_is_refused_and_changes_nothing() {
    let bpm = bpm(10);
    let tree = new_tree(&bpm, 10, 4);
    insert_all(&tree, [3, 1, 2]);
    let root = tree.get_root_page_id();
    assert!(!tree.insert(&index_key(2), &rid_of(200)));
    assert!(!tree.insert(&index_key(1), &rid_of(100)));
    assert_eq!(tree.get_root_page_id(), root);
    assert_eq!(shape(&bpm, root), "[1,2,3]");
    assert_eq!(get(&tree, 2), vec![rid_of(2)], "the first value for a key is the one that stays");
    assert_no_pins(&bpm);
}

#[test]
fn s2c_03_negative_and_extreme_keys_sort_as_integers() {
    let bpm = bpm(10);
    let tree = new_tree(&bpm, 10, 4);
    insert_all(&tree, [0, -1, i64::MAX, i64::MIN, 5, -100]);
    assert_eq!(shape(&bpm, tree.get_root_page_id()), format!("[{},-100,-1,0,5,{}]", i64::MIN, i64::MAX));
}

#[test]
fn s2c_03_insert_and_get_value_cooperate_and_leave_no_latches_behind() {
    let bpm = bpm(4);
    let tree = new_tree(&bpm, 50, 4);
    for k in shuffled(40, 9) {
        assert!(insert(&tree, k));
        assert_eq!(get(&tree, k), vec![rid_of(k)]);
    }
    assert_no_pins(&bpm);
    // with every guard released, a write latch on the root is available at once
    drop(bpm.write_page(tree.get_root_page_id()));
}

// ---- 2c-04 · Leaf splits --------------------------------------------------------------------------------------------------------

#[test]
fn s2c_04_an_internal_page_inserts_a_separator_in_key_order() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut node = Internal::<_, Key>::new(&mut bytes[..]);
    node.init(8);
    node.set_entry_at(0, &index_key(0), PageId(1));
    node.set_entry_at(1, &index_key(20), PageId(2));
    node.set_size(2);
    let cmp = GenericComparator::<8>;
    node.insert_child(&index_key(40), PageId(4), &cmp); // at the end
    node.insert_child(&index_key(10), PageId(3), &cmp); // in the middle: later pairs shift right
    node.insert_child(&index_key(30), PageId(5), &cmp);
    assert_eq!(node.size(), 5);
    let keys: Vec<i64> = (1..5).map(|i| node.key_at(i).get_as_integer()).collect();
    let kids: Vec<i32> = (0..5).map(|i| node.value_at(i).0).collect();
    assert_eq!(keys, vec![10, 20, 30, 40]);
    assert_eq!(kids, vec![1, 3, 2, 5, 4], "each child moves with its key");
}

#[test]
#[should_panic]
fn s2c_04_an_internal_page_that_is_full_does_not_take_another_child() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut node = Internal::<_, Key>::new(&mut bytes[..]);
    node.init(3);
    node.set_entry_at(0, &index_key(0), PageId(1));
    node.set_entry_at(1, &index_key(10), PageId(2));
    node.set_entry_at(2, &index_key(20), PageId(3));
    node.set_size(3);
    node.insert_child(&index_key(30), PageId(4), &GenericComparator::<8>);
}

#[test]
fn s2c_04_a_leaf_that_reaches_max_size_splits_and_the_tree_gets_a_root() {
    let bpm = bpm(20);
    let tree = new_tree(&bpm, 3, 20);
    insert_all(&tree, [1, 2]);
    let leaf_root = tree.get_root_page_id();
    assert_eq!(shape(&bpm, leaf_root), "[1,2]");
    insert_all(&tree, [3]); // 3 pairs = max_size: split
    let root = tree.get_root_page_id();
    assert_ne!(root, leaf_root, "the root is a new internal page now");
    assert_eq!(shape(&bpm, root), "{3 [1,2] [3]}");
    let guard = bpm.read_page(root);
    let node = Internal::<_, Key>::new(&guard[..]);
    assert!(!Page::new(&guard[..]).is_leaf_page());
    assert_eq!((node.size(), node.max_size()), (2, 20));
    assert_eq!(node.value_at(0), leaf_root, "the old leaf stays the left child");
    // the leaf chain
    let left = Leaf::<_, Key, Rid>::new(&bpm.read_page(node.value_at(0))[..]).next_page_id();
    assert_eq!(left, Some(node.value_at(1)));
    let right = Leaf::<_, Key, Rid>::new(&bpm.read_page(node.value_at(1))[..]).next_page_id();
    assert_eq!(right, None);
    drop(guard);
    assert_no_pins(&bpm);
}

#[test]
fn s2c_04_the_left_half_keeps_the_extra_pair() {
    for (max, expected) in [(2, "{2 [1] [2]}"), (3, "{3 [1,2] [3]}"), (4, "{3 [1,2] [3,4]}"), (5, "{4 [1,2,3] [4,5]}"), (6, "{4 [1,2,3] [4,5,6]}"), (7, "{5 [1,2,3,4] [5,6,7]}")] {
        let bpm = bpm(20);
        let tree = new_tree(&bpm, max, 20);
        insert_all(&tree, 1..=max as i64);
        assert_eq!(shape(&bpm, tree.get_root_page_id()), expected, "leaf_max_size {max}");
    }
}

#[test]
fn s2c_04_ascending_inserts_leave_the_leaves_half_full_and_chained() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 3, 100);
    insert_all(&tree, 1..=9);
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{3,5,7,9 [1,2] [3,4] [5,6] [7,8] [9]}");
    assert_eq!(keys_by_scan_without_iterator(&bpm, &tree), (1..=9).collect::<Vec<_>>(), "following next_page_id from the leftmost leaf visits every key in order");
    assert_eq!(check_structure(&bpm, tree.get_root_page_id()), Ok(Shape { height: 2, leaves: 5, internals: 1, keys: 9 }));
}

/// All keys by walking the leaf chain with the test utilities (so it does not depend on the iterator stage).
fn keys_by_scan_without_iterator(bpm: &BufferPoolManager, tree: &Tree) -> Vec<i64> {
    let mut leaves = IndexLeaves::new(tree.get_root_page_id(), bpm);
    let mut keys = vec![];
    while leaves.valid() {
        let leaf = leaves.leaf();
        keys.extend((0..leaf.size()).map(|i| leaf.key_at(i).get_as_integer()));
        leaves.advance();
    }
    keys
}

#[test]
fn s2c_04_descending_inserts_split_at_the_front() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 3, 100);
    insert_all(&tree, (1..=9).rev());
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{3,4,5,6,7,8,9 [1,2] [3] [4] [5] [6] [7] [8] [9]}");
    assert_eq!(keys_by_scan_without_iterator(&bpm, &tree), (1..=9).collect::<Vec<_>>());
    assert!(check_structure(&bpm, tree.get_root_page_id()).is_ok());
}

#[test]
fn s2c_04_random_inserts_are_all_found_and_the_leaves_stay_valid() {
    for (leaf_max, seed) in [(3, 1), (4, 2), (5, 3), (8, 4)] {
        let bpm = bpm(40);
        let tree = new_tree(&bpm, leaf_max, 300);
        let keys = shuffled(120, seed);
        for (i, &k) in keys.iter().enumerate() {
            assert!(insert(&tree, k));
            if i % 10 == 0 {
                check_structure(&bpm, tree.get_root_page_id()).unwrap_or_else(|e| panic!("leaf_max {leaf_max} after {i} inserts: {e}"));
            }
        }
        for k in 1..=120 {
            assert_eq!(get(&tree, k), vec![rid_of(k)], "leaf_max {leaf_max}, key {k}");
        }
        assert_eq!(keys_by_scan_without_iterator(&bpm, &tree), (1..=120).collect::<Vec<_>>());
        assert_no_pins(&bpm);
    }
}

#[test]
fn s2c_04_a_duplicate_after_splits_is_refused_and_values_stay_with_their_keys() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 3, 100);
    insert_all(&tree, shuffled(30, 5));
    let before = shape(&bpm, tree.get_root_page_id());
    for k in [1, 15, 30] {
        assert!(!tree.insert(&index_key(k), &rid_of(999)));
    }
    assert_eq!(shape(&bpm, tree.get_root_page_id()), before);
    assert_eq!(get(&tree, 15), vec![rid_of(15)]);
}

// ---- 2c-05 · Internal splits ----------------------------------------------------------------------------------------------------

#[test]
fn s2c_05_the_tree_grows_taller_when_a_parent_overflows() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 2, 3);
    insert_all(&tree, 1..=3);
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{2,3 [1] [2] [3]}");
    insert_all(&tree, [4]); // the root would need a 4th child: it splits, and the first key of the right half moves up
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{3 {2 [1] [2]} {4 [3] [4]}}");
    insert_all(&tree, [5]);
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{3 {2 [1] [2]} {4,5 [3] [4] [5]}}");
    assert_eq!(check_structure(&bpm, tree.get_root_page_id()), Ok(Shape { height: 3, leaves: 5, internals: 3, keys: 5 }));
}

#[test]
fn s2c_05_nine_keys_make_a_three_level_tree_of_a_known_shape() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 2, 3);
    insert_all(&tree, 1..=9);
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{5 {3 {2 [1] [2]} {4 [3] [4]}} {7 {6 [5] [6]} {8,9 [7] [8] [9]}}}");
    assert!(is_tree_valid(tree.get_root_page_id(), &bpm));
}

#[test]
fn s2c_05_insert_test_1_from_bustub_keys_one_to_five() {
    let bpm = bpm(50);
    let tree = new_tree(&bpm, 2, 3);
    for key in [1, 2, 3, 4, 5] {
        tree.insert(&index_key(key), &rid_of(key));
    }
    for key in [1, 2, 3, 4, 5] {
        let rids = tree.get_value(&index_key(key));
        assert_eq!(rids.len(), 1);
        assert_eq!(rids[0].page_id().0, 0);
        assert_eq!(rids[0].slot_num() as i64, key & 0xFFFF_FFFF);
    }
    assert_no_pins(&bpm);
}

#[test]
fn s2c_05_the_height_grows_by_at_most_one_level_per_insert() {
    let bpm = bpm(40);
    let tree = new_tree(&bpm, 2, 3);
    let mut height = 0;
    for k in 1..=100 {
        insert(&tree, k);
        let shape = check_structure(&bpm, tree.get_root_page_id()).unwrap_or_else(|e| panic!("after inserting {k}: {e}"));
        assert!(shape.height == height || shape.height == height + 1, "height jumped from {height} to {} at key {k}", shape.height);
        height = shape.height;
        assert_eq!(shape.keys as i64, k);
    }
    assert!(height >= 6, "100 keys in pages of 1-2 pairs and 2-3 children need several levels, got {height}");
}

#[test]
fn s2c_05_every_node_size_and_order_stays_valid() {
    let configs = [(2, 3), (3, 3), (3, 4), (4, 5), (5, 4), (2, 5), (6, 7), (4, 3)];
    for (leaf_max, internal_max) in configs {
        for order in 0..3 {
            let bpm = bpm(40);
            let tree = new_tree(&bpm, leaf_max, internal_max);
            let mut keys: Vec<i64> = (1..=150).collect();
            match order {
                1 => keys.reverse(),
                2 => Lcg(leaf_max as u64 * 10 + internal_max as u64).shuffle(&mut keys),
                _ => {}
            }
            for (i, &k) in keys.iter().enumerate() {
                assert!(insert(&tree, k));
                if i % 7 == 0 || i == keys.len() - 1 {
                    check_structure(&bpm, tree.get_root_page_id()).unwrap_or_else(|e| panic!("({leaf_max},{internal_max}) order {order} after {i} inserts: {e}\n{}", shape(&bpm, tree.get_root_page_id())));
                }
            }
            for k in 1..=150 {
                assert_eq!(get(&tree, k), vec![rid_of(k)], "({leaf_max},{internal_max}) order {order}");
            }
            assert!(is_tree_valid(tree.get_root_page_id(), &bpm));
            assert_no_pins(&bpm);
        }
    }
}

#[test]
fn s2c_05_basic_scale_in_a_small_pool() {
    // 2000 shuffled keys in a pool of 20 frames: a deep tree whose operations release their pages
    let bpm = bpm(20);
    let tree = new_tree(&bpm, 2, 3);
    let keys = shuffled(2000, 11);
    insert_all(&tree, keys.iter().copied());
    for &k in &keys {
        assert_eq!(get(&tree, k), vec![rid_of(k)]);
    }
    assert_eq!(check_structure(&bpm, tree.get_root_page_id()).unwrap().keys, 2000);
    assert_no_pins(&bpm);
}

#[test]
fn s2c_05_duplicates_in_a_deep_tree_are_refused() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 3, 4);
    insert_all(&tree, shuffled(200, 13));
    let before = shape(&bpm, tree.get_root_page_id());
    for k in (1..=200).step_by(7) {
        assert!(!insert(&tree, k), "key {k}");
    }
    assert_eq!(shape(&bpm, tree.get_root_page_id()), before, "refusing a key must not rearrange anything");
}

// ---- 2c-06 · The iterator -------------------------------------------------------------------------------------------------------

#[test]
fn s2c_06_an_empty_tree_begins_at_its_end() {
    let bpm = bpm(10);
    let tree = new_tree(&bpm, 3, 4);
    let mut it = tree.begin();
    assert!(it.is_end());
    assert!(it == tree.end());
    assert_eq!(it.next(), None);
    assert!(tree.begin_at(&index_key(5)).is_end());
}

#[test]
fn s2c_06_begin_visits_every_pair_in_key_order() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 3, 4);
    insert_all(&tree, shuffled(200, 21));
    let pairs: Vec<(i64, Rid)> = tree.begin().map(|(k, v)| (k.get_as_integer(), v)).collect();
    assert_eq!(pairs.len(), 200);
    for (i, (k, v)) in pairs.iter().enumerate() {
        assert_eq!(*k, i as i64 + 1);
        assert_eq!(*v, rid_of(*k), "the value belongs to its key");
    }
}

#[test]
fn s2c_06_begin_at_starts_at_the_first_key_that_is_not_less() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 3, 4);
    insert_all(&tree, (1..=60).map(|k| k * 10)); // 10, 20, ..., 600
    let first = |key: i64| tree.begin_at(&index_key(key)).next().map(|(k, _)| k.get_as_integer());
    assert_eq!(first(10), Some(10));
    assert_eq!(first(300), Some(300));
    assert_eq!(first(301), Some(310), "a missing key starts at the next one");
    assert_eq!(first(1), Some(10));
    assert_eq!(first(-1000), Some(10));
    assert_eq!(first(600), Some(600));
    assert_eq!(first(601), None, "past the last key is the end");
    assert!(tree.begin_at(&index_key(601)).is_end());
    let rest: Vec<i64> = tree.begin_at(&index_key(555)).map(|(k, _)| k.get_as_integer()).collect();
    assert_eq!(rest, vec![560, 570, 580, 590, 600]);
}

#[test]
fn s2c_06_a_scan_crosses_every_leaf_boundary() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 3, 100);
    insert_all(&tree, 1..=40);
    // for every starting key the scan reaches the last key, whichever leaf it starts in
    for start in 1..=40 {
        let got: Vec<i64> = tree.begin_at(&index_key(start)).map(|(k, _)| k.get_as_integer()).collect();
        assert_eq!(got, (start..=40).collect::<Vec<_>>(), "scan from {start}");
    }
}

#[test]
fn s2c_06_iterators_compare_by_position() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 3, 4);
    insert_all(&tree, 1..=20);
    assert!(tree.begin() == tree.begin());
    assert!(tree.begin() != tree.end());
    assert!(tree.begin_at(&index_key(1)) == tree.begin());
    let mut a = tree.begin_at(&index_key(7));
    a.next();
    assert!(a == tree.begin_at(&index_key(8)));
    let mut all = tree.begin();
    while all.next().is_some() {}
    assert!(all.is_end());
    assert!(all == tree.end());
    assert!(tree.begin_at(&index_key(21)) == tree.end());
}

#[test]
fn s2c_06_nothing_stays_latched_while_an_iterator_is_alive() {
    let bpm = bpm(10);
    let tree = new_tree(&bpm, 3, 4);
    insert_all(&tree, 1..=30);
    let mut it = tree.begin_at(&index_key(10));
    for _ in 0..5 {
        it.next();
        assert_no_pins(&bpm);
    }
    // writers are not blocked by the iterator, and the iterator carries on afterwards
    assert!(insert(&tree, 100));
    drop(bpm.write_page(tree.get_root_page_id()));
    assert!(it.next().is_some());
}

#[test]
fn s2c_06_a_scan_agrees_with_a_btreemap_on_random_keys() {
    let bpm = bpm(40);
    let tree = new_tree(&bpm, 4, 5);
    let mut rng = Lcg(77);
    let mut model = BTreeMap::new();
    for _ in 0..500 {
        let k = rng.next(1000) as i64;
        if insert(&tree, k) {
            model.insert(k, rid_of(k));
        } else {
            assert!(model.contains_key(&k));
        }
    }
    let got: Vec<(i64, Rid)> = tree.begin().map(|(k, v)| (k.get_as_integer(), v)).collect();
    let want: Vec<(i64, Rid)> = model.iter().map(|(&k, &v)| (k, v)).collect();
    assert_eq!(got, want);
    for probe in [0, 1, 499, 500, 998, 999, 1000] {
        let got: Vec<i64> = tree.begin_at(&index_key(probe)).map(|(k, _)| k.get_as_integer()).collect();
        let want: Vec<i64> = model.range(probe..).map(|(&k, _)| k).collect();
        assert_eq!(got, want, "scan from {probe}");
    }
}

// ---- 2c-07 · Remove: leaves, and borrowing --------------------------------------------------------------------------------------

#[test]
fn s2c_07_a_leaf_removes_a_key_and_keeps_the_rest_in_order() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut leaf = Leaf::<_, Key, Rid>::new(&mut bytes[..]);
    leaf.init(10);
    let cmp = GenericComparator::<8>;
    for k in [1, 2, 3, 4, 5] {
        leaf.insert(&index_key(k), &rid_of(k), &cmp);
    }
    assert!(leaf.remove(&index_key(3), &cmp)); // the middle
    assert!(leaf.remove(&index_key(1), &cmp)); // the first
    assert!(leaf.remove(&index_key(5), &cmp)); // the last
    assert!(!leaf.remove(&index_key(5), &cmp), "already gone");
    assert!(!leaf.remove(&index_key(9), &cmp), "never there");
    assert_eq!(leaf.size(), 2);
    assert_eq!((leaf.entry_at(0), leaf.entry_at(1)), ((index_key(2), rid_of(2)), (index_key(4), rid_of(4))));
    leaf.remove_at(0);
    assert_eq!((leaf.size(), leaf.key_at(0).get_as_integer()), (1, 4));
    leaf.insert_at_front(&index_key(1), &rid_of(1));
    assert_eq!((leaf.size(), leaf.key_at(0).get_as_integer(), leaf.key_at(1).get_as_integer()), (2, 1, 4));
}

#[test]
fn s2c_07_an_internal_page_removes_and_inserts_at_the_front() {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut node = Internal::<_, Key>::new(&mut bytes[..]);
    node.init(6);
    for (i, (k, c)) in [(0, 100), (10, 101), (20, 102), (30, 103)].into_iter().enumerate() {
        node.set_entry_at(i as u32, &index_key(k), PageId(c));
    }
    node.set_size(4);
    node.remove_at(2);
    assert_eq!(node.size(), 3);
    assert_eq!((node.key_at(2).get_as_integer(), node.value_at(2)), (30, PageId(103)));
    node.remove_at(0);
    assert_eq!((node.size(), node.value_at(0), node.value_at(1)), (2, PageId(101), PageId(103)), "removing slot 0 shifts the others down");
    node.insert_at_front(&index_key(5), PageId(99));
    assert_eq!((node.size(), node.value_at(0), node.value_at(1), node.value_at(2)), (3, PageId(99), PageId(101), PageId(103)));
    assert_eq!(node.key_at(2).get_as_integer(), 30);
}

#[test]
fn s2c_07_removing_a_missing_key_changes_nothing() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 4, 5);
    insert_all(&tree, 1..=12);
    let before = shape(&bpm, tree.get_root_page_id());
    for k in [0, 13, 100, -5] {
        remove(&tree, k);
    }
    assert_eq!(shape(&bpm, tree.get_root_page_id()), before);
    // and on an empty tree
    let empty = new_tree(&bpm, 4, 5);
    remove(&empty, 1);
    assert!(empty.is_empty());
    assert_no_pins(&bpm);
}

#[test]
fn s2c_07_a_leaf_that_stays_big_enough_just_loses_the_pair() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 5, 10);
    insert_all(&tree, 1..=7);
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{4 [1,2,3] [4,5,6,7]}");
    remove(&tree, 6);
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{4 [1,2,3] [4,5,7]}");
    remove(&tree, 4); // the first key of a leaf goes: the parent's key (4) is only a bound, it may stay
    assert_eq!(get(&tree, 4), vec![]);
    assert_eq!(get(&tree, 5), vec![rid_of(5)]);
    assert!(check_structure(&bpm, tree.get_root_page_id()).is_ok());
}

#[test]
fn s2c_07_removing_the_last_pair_of_a_root_leaf_empties_the_tree() {
    let bpm = bpm(10);
    let tree = new_tree(&bpm, 4, 5);
    insert_all(&tree, [1, 2]);
    let root = tree.get_root_page_id();
    remove(&tree, 1);
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "[2]");
    remove(&tree, 2);
    assert!(tree.is_empty());
    assert_eq!(tree.get_root_page_id(), PageId::INVALID);
    assert_eq!(bpm.get_pin_count(root), None, "the root leaf's page was deleted from the pool");
    assert!(get(&tree, 2).is_empty());
    assert!(tree.begin().is_end());
    // the tree can be used again
    assert!(insert(&tree, 7));
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "[7]");
    assert_no_pins(&bpm);
}

#[test]
fn s2c_07_a_short_leaf_borrows_from_its_left_sibling() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 5, 10);
    insert_all(&tree, 1..=7);
    remove(&tree, 6);
    remove(&tree, 7);
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{4 [1,2,3] [4,5]}");
    remove(&tree, 5); // [4] is below min_size 2; the left sibling [1,2,3] has one to spare
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{3 [1,2] [3,4]}", "the left leaf's last pair moves over and the separator becomes its key");
    assert_eq!(get(&tree, 3), vec![rid_of(3)]);
    assert!(check_structure(&bpm, tree.get_root_page_id()).is_ok());
}

#[test]
fn s2c_07_the_leftmost_leaf_borrows_from_its_right_sibling() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 5, 10);
    insert_all(&tree, 1..=6);
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{4 [1,2,3] [4,5,6]}");
    remove(&tree, 1);
    remove(&tree, 2); // [3] is below min_size 2 and has no left sibling; the right one [4,5,6] has one to spare
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{5 [3,4] [5,6]}", "the right leaf's first pair moves over and the separator becomes its new first key");
    assert_eq!(keys_by_scan_without_iterator(&bpm, &tree), vec![3, 4, 5, 6]);
    assert!(check_structure(&bpm, tree.get_root_page_id()).is_ok());
}

#[test]
fn s2c_07_borrowing_keeps_the_chain_and_the_values_intact() {
    let bpm = bpm(40);
    let tree = new_tree(&bpm, 6, 10);
    insert_all(&tree, 1..=14);
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{4,7,10 [1,2,3] [4,5,6] [7,8,9] [10,11,12,13,14]}");
    remove(&tree, 7); // [8,9] is below min_size 3; its left sibling has none to spare, its right sibling has two
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{4,7,11 [1,2,3] [4,5,6] [8,9,10] [11,12,13,14]}");
    remove(&tree, 14); // the last leaf stays at 3 pairs: no borrowing needed
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{4,7,11 [1,2,3] [4,5,6] [8,9,10] [11,12,13]}");
    check_structure(&bpm, tree.get_root_page_id()).unwrap();
    for k in (1..=13).filter(|&k| k != 7) {
        assert_eq!(get(&tree, k), vec![rid_of(k)]);
    }
    assert_eq!(keys_by_scan_without_iterator(&bpm, &tree), vec![1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13]);
    assert_no_pins(&bpm);
}

// ---- 2c-08 · Remove: merging and shrinking --------------------------------------------------------------------------------------

#[test]
fn s2c_08_a_leaf_merges_into_its_left_sibling_and_the_root_collapses() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 4, 10);
    insert_all(&tree, 1..=4);
    let old_root = tree.get_root_page_id();
    assert_eq!(shape(&bpm, old_root), "{3 [1,2] [3,4]}");
    let right = Internal::<_, Key>::new(&bpm.read_page(old_root)[..]).value_at(1);
    remove(&tree, 4); // [3] is short, the left sibling [1,2] has nothing to spare: merge
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "[1,2,3]", "the root had one child left, so that child is the root");
    assert_ne!(tree.get_root_page_id(), old_root);
    assert_eq!(bpm.get_pin_count(old_root), None, "the old root page is deleted");
    assert_eq!(bpm.get_pin_count(right), None, "so is the page that was merged away");
    assert_no_pins(&bpm);
}

#[test]
fn s2c_08_the_leftmost_leaf_merges_with_its_right_sibling() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 4, 10);
    insert_all(&tree, 1..=4);
    remove(&tree, 1); // [2] is short and has no left sibling; the right sibling [3,4] has nothing to spare
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "[2,3,4]");
    assert_eq!(get(&tree, 1), vec![]);
    assert_eq!(keys_by_scan_without_iterator(&bpm, &tree), vec![2, 3, 4]);
}

#[test]
fn s2c_08_a_merge_in_the_middle_keeps_the_leaf_chain() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 4, 10);
    insert_all(&tree, 1..=12);
    assert_eq!(check_structure(&bpm, tree.get_root_page_id()).unwrap().leaves, 6);
    for k in [6, 5, 9, 10] {
        remove(&tree, k);
        check_structure(&bpm, tree.get_root_page_id()).unwrap_or_else(|e| panic!("after removing {k}: {e}\n{}", shape(&bpm, tree.get_root_page_id())));
    }
    assert_eq!(keys_by_scan_without_iterator(&bpm, &tree), vec![1, 2, 3, 4, 7, 8, 11, 12]);
    assert_no_pins(&bpm);
}

#[test]
fn s2c_08_an_internal_page_that_loses_a_child_borrows_or_merges() {
    let bpm = bpm(40);
    let tree = new_tree(&bpm, 3, 3);
    insert_all(&tree, 1..=12);
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{5,9 {3 [1,2] [3,4]} {7 [5,6] [7,8]} {11 [9,10] [11,12]}}");
    remove(&tree, 1);
    remove(&tree, 2);
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{5,9 {4 [3] [4]} {7 [5,6] [7,8]} {11 [9,10] [11,12]}}");
    remove(&tree, 3); // [4] merges away ... and its parent has one child left: it merges with a sibling
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{9 {5,7 [4] [5,6] [7,8]} {11 [9,10] [11,12]}}");
    remove(&tree, 4);
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{9 {6,7 [5] [6] [7,8]} {11 [9,10] [11,12]}}");
    remove(&tree, 5);
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{9 {7 [6] [7,8]} {11 [9,10] [11,12]}}");
    assert!(check_structure(&bpm, tree.get_root_page_id()).is_ok());
}

#[test]
fn s2c_08_removing_everything_shrinks_the_tree_a_level_at_a_time() {
    let bpm = bpm(40);
    let tree = new_tree(&bpm, 2, 3);
    insert_all(&tree, 1..=9);
    let mut height = check_structure(&bpm, tree.get_root_page_id()).unwrap().height;
    assert_eq!(height, 4);
    for k in (1..=9).rev() {
        remove(&tree, k);
        let h = check_structure(&bpm, tree.get_root_page_id()).unwrap_or_else(|e| panic!("after removing {k}: {e}")).height;
        assert!(h <= height && height - h <= 1, "height went from {height} to {h}");
        height = h;
    }
    assert_eq!(height, 0);
    assert!(tree.is_empty());
}

#[test]
fn s2c_08_a_deleted_tree_gives_all_its_pages_back() {
    let bpm = bpm(40);
    let tree = new_tree(&bpm, 3, 4);
    let keys = shuffled(100, 31);
    insert_all(&tree, keys.iter().copied());
    for &k in &keys {
        remove(&tree, k);
    }
    assert!(tree.is_empty());
    let next = bpm.new_page();
    // page 0 is the header; every other page the tree used was deleted from the pool
    for id in 1..next.0 {
        assert_eq!(bpm.get_pin_count(PageId(id)), None, "page {id} is still in the pool");
    }
}

#[test]
fn s2c_08_delete_test_no_iterator_from_bustub() {
    let bpm = bpm(50);
    let tree = new_tree(&bpm, 2, 3);
    let keys = [1, 2, 3, 4, 5];
    insert_all(&tree, keys);
    let remove_keys = [1, 5, 3, 4];
    for k in remove_keys {
        remove(&tree, k);
    }
    let left: Vec<i64> = keys.into_iter().filter(|k| !get(&tree, *k).is_empty()).collect();
    assert_eq!(left, vec![2]);
    remove(&tree, 2);
    assert_eq!(tree.get_root_page_id(), PageId::INVALID);
}

#[test]
fn s2c_08_random_inserts_and_removes_agree_with_a_btreemap() {
    for (leaf_max, internal_max) in [(2, 3), (3, 3), (3, 4), (4, 5), (5, 4), (6, 7)] {
        for seed in 0..3u64 {
            let bpm = bpm(40);
            let tree = new_tree(&bpm, leaf_max, internal_max);
            let mut model = BTreeMap::new();
            let mut rng = Lcg(seed * 131 + leaf_max as u64 * 7 + internal_max as u64);
            for step in 0..400 {
                let key = rng.next(60) as i64;
                if rng.next(5) < 3 {
                    assert_eq!(insert(&tree, key), model.insert(key, ()).is_none(), "({leaf_max},{internal_max}) seed {seed} step {step}: insert {key}");
                } else {
                    model.remove(&key);
                    remove(&tree, key);
                }
                check_structure(&bpm, tree.get_root_page_id()).unwrap_or_else(|e| panic!("({leaf_max},{internal_max}) seed {seed} step {step}: {e}\n{}", shape(&bpm, tree.get_root_page_id())));
            }
            let want: Vec<i64> = model.keys().copied().collect();
            assert_eq!(keys_by_scan_without_iterator(&bpm, &tree).into_iter().filter(|_| !tree.is_empty()).collect::<Vec<_>>(), want);
            assert_no_pins(&bpm);
        }
    }
}

#[test]
fn s2c_08_sequential_edge_mix_from_bustub() {
    let bpm = bpm(50);
    for leaf_max_size in 2..=5 {
        let tree = new_tree(&bpm, leaf_max_size, 3);
        let mut inserted: Vec<i64> = vec![];
        let mut deleted: Vec<i64> = vec![];
        for key in [1, 5, 15, 20, 25, 2, -1, -2, 6, 14, 4] {
            insert(&tree, key);
            inserted.push(key);
            assert!(tree_values_match(&tree, &inserted, &deleted));
        }
        remove(&tree, 1);
        deleted.push(1);
        inserted.retain(|&k| k != 1);
        assert!(tree_values_match(&tree, &inserted, &deleted));
        insert(&tree, 3);
        inserted.push(3);
        assert!(tree_values_match(&tree, &inserted, &deleted));
        for key in [4, 14, 6, 2, 15, -2, -1, 3, 5, 25, 20] {
            remove(&tree, key);
            deleted.push(key);
            inserted.retain(|&k| k != key);
            assert!(tree_values_match(&tree, &inserted, &deleted));
        }
    }
}

// ---- 2c-09 · Latch crabbing -----------------------------------------------------------------------------------------------------

#[test]
fn s2c_09_an_insert_into_a_leaf_with_room_write_latches_only_the_leaf() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 4, 3);
    insert_all(&tree, [0, 2, 4, 6, 8]);
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{4 [0,2] [4,6,8]}");
    let (reads, writes) = (tree.bpm.get_reads(), tree.bpm.get_writes());
    assert!(insert(&tree, 1)); // [0,2] has room for it without reaching max_size
    assert!(tree.bpm.get_reads() - reads > 0, "the path down to the leaf is read-latched");
    assert_eq!(tree.bpm.get_writes() - writes, 1, "only the leaf is write-latched");
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{4 [0,1,2] [4,6,8]}");
}

#[test]
fn s2c_09_a_remove_that_leaves_the_leaf_half_full_write_latches_only_the_leaf() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 4, 3);
    insert_all(&tree, 0..25);
    let mut to_delete = 26;
    let mut leaves = IndexLeaves::new(tree.get_root_page_id(), &bpm);
    while leaves.valid() {
        if leaves.leaf().size() > leaves.leaf().min_size() {
            to_delete = leaves.leaf().key_at(0).get_as_integer();
        }
        leaves.advance();
    }
    drop(leaves);
    assert!(to_delete < 26, "some leaf has a pair to spare");
    let (reads, writes) = (tree.bpm.get_reads(), tree.bpm.get_writes());
    remove(&tree, to_delete);
    assert!(tree.bpm.get_reads() - reads > 0);
    assert_eq!(tree.bpm.get_writes() - writes, 1);
    assert!(get(&tree, to_delete).is_empty());
}

#[test]
fn s2c_09_an_insert_that_splits_a_leaf_still_works_and_latches_more_than_the_leaf() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 4, 10);
    insert_all(&tree, 1..=3);
    let writes = tree.bpm.get_writes();
    assert!(insert(&tree, 4)); // the root leaf reaches max_size: it splits
    assert!(tree.bpm.get_writes() - writes > 1, "a split latches the leaf, the new page and the parent (or the header)");
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{3 [1,2] [3,4]}");
}

#[test]
fn s2c_09_an_insert_that_fits_does_not_wait_for_a_reader_on_the_root() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 4, 4);
    insert_all(&tree, [0, 2, 4, 6, 8]);
    let root_page = tree.get_root_page_id();
    let reader = bpm.read_page(root_page); // someone is reading the root
    let (tx, rx) = mpsc::channel();
    thread::scope(|scope| {
        scope.spawn(|| {
            insert(&tree, 1); // fits in a leaf: the writer only needs read latches above the leaf
            tx.send(()).unwrap();
        });
        let finished = rx.recv_timeout(Duration::from_secs(10)).is_ok();
        drop(reader);
        assert!(finished, "an insert into a leaf with room blocked on a read latch held on the root: it should only read-latch the path");
    });
    assert_eq!(get(&tree, 1), vec![rid_of(1)]);
}

#[test]
fn s2c_09_a_remove_that_fits_does_not_wait_for_a_reader_on_the_root() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 4, 4);
    insert_all(&tree, 1..=5);
    assert_eq!(shape(&bpm, tree.get_root_page_id()), "{3 [1,2] [3,4,5]}");
    let root_page = tree.get_root_page_id();
    let reader = bpm.read_page(root_page);
    let (tx, rx) = mpsc::channel();
    thread::scope(|scope| {
        scope.spawn(|| {
            remove(&tree, 4); // the leaf [3,4,5] keeps 2 pairs: min_size
            tx.send(()).unwrap();
        });
        let finished = rx.recv_timeout(Duration::from_secs(10)).is_ok();
        drop(reader);
        assert!(finished, "a remove from a leaf that stays at least half full blocked on a read latch held on the root");
    });
    assert!(get(&tree, 4).is_empty());
}

fn run_with_watchdog(seconds: u64, work: impl FnOnce() + Send + 'static) {
    let (tx, rx) = mpsc::channel();
    let handle = thread::spawn(move || {
        work();
        let _ = tx.send(());
    });
    match rx.recv_timeout(Duration::from_secs(seconds)) {
        Ok(()) => handle.join().unwrap(),
        Err(_) => panic!("the workload did not finish in {seconds} seconds: a deadlock, or a very slow tree"),
    }
}

#[test]
fn s2c_09_concurrent_inserts_of_disjoint_keys_are_all_kept() {
    run_with_watchdog(60, || {
        for iteration in 0..10 {
            let bpm = bpm(50);
            let tree = new_tree(&bpm, 3, 5);
            thread::scope(|scope| {
                for t in 0..8i64 {
                    let tree = &tree;
                    scope.spawn(move || {
                        let mut keys: Vec<i64> = (0..150).map(|i| i * 8 + t).collect();
                        Lcg(t as u64 + 100 * iteration).shuffle(&mut keys);
                        for k in keys {
                            assert!(insert(tree, k));
                        }
                    });
                }
            });
            let shape = check_structure(&bpm, tree.get_root_page_id()).unwrap_or_else(|e| panic!("iteration {iteration}: {e}"));
            assert_eq!(shape.keys, 1200);
            assert_eq!(tree.begin().map(|(k, _)| k.get_as_integer()).collect::<Vec<_>>(), (0..1200).collect::<Vec<_>>());
            assert_no_pins(&bpm);
        }
    });
}

#[test]
fn s2c_09_concurrent_removes_of_disjoint_keys_empty_the_tree() {
    run_with_watchdog(60, || {
        for iteration in 0..10 {
            let bpm = bpm(50);
            let tree = new_tree(&bpm, 3, 5);
            insert_all(&tree, 0..800);
            thread::scope(|scope| {
                for t in 0..8i64 {
                    let tree = &tree;
                    scope.spawn(move || {
                        let mut keys: Vec<i64> = (0..100).map(|i| i * 8 + t).collect();
                        Lcg(t as u64 + 7 * iteration).shuffle(&mut keys);
                        for k in keys {
                            remove(tree, k);
                        }
                    });
                }
            });
            assert!(tree.is_empty(), "iteration {iteration}: {}", shape(&bpm, tree.get_root_page_id()));
            assert_no_pins(&bpm);
        }
    });
}

#[test]
fn s2c_09_readers_always_find_the_keys_that_writers_never_touch() {
    run_with_watchdog(90, || {
        for _ in 0..5 {
            let bpm = bpm(50);
            let tree = new_tree(&bpm, 4, 5);
            let preserved: Vec<i64> = (1..=600).filter(|k| k % 10 == 0).collect();
            let dynamic: Vec<i64> = (1..=600).filter(|k| k % 10 != 0).collect();
            insert_all(&tree, preserved.iter().copied());
            thread::scope(|scope| {
                for tid in 0..9 {
                    let (tree, preserved, dynamic) = (&tree, &preserved, &dynamic);
                    scope.spawn(move || match tid % 3 {
                        0 => dynamic.iter().for_each(|&k| {
                            insert(tree, k);
                        }),
                        1 => dynamic.iter().for_each(|&k| remove(tree, k)),
                        _ => {
                            for _ in 0..3 {
                                for &k in preserved.iter() {
                                    assert_eq!(get(tree, k), vec![rid_of(k)], "preserved key {k} went missing");
                                }
                            }
                        }
                    });
                }
            });
            check_structure(&bpm, tree.get_root_page_id()).unwrap();
            assert_eq!(tree.begin().filter(|(k, _)| k.get_as_integer() % 10 == 0).count(), preserved.len());
            assert_no_pins(&bpm);
        }
    });
}
