//! Port of `test/include/storage/b_plus_tree_utils.h` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University Database
//! Group), plus a stricter checker of this course's own (`check_structure`) and a text rendering of a tree's shape.
//! Not part of any stage: nothing here for you to write.
#![allow(dead_code)]

use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::common::config::PageId;
use bustub::common::rid::Rid;
use bustub::storage::index::b_plus_tree::BPlusTree;
use bustub::storage::index::generic_key::{GenericComparator, GenericKey, KeyComparator};
use bustub::storage::page::b_plus_tree_internal_page::BPlusTreeInternalPage as Internal;
use bustub::storage::page::b_plus_tree_leaf_page::BPlusTreeLeafPage as Leaf;
use bustub::storage::page::b_plus_tree_page::BPlusTreePage as Page;
use bustub::storage::page::page_guard::ReadPageGuard;

pub type Key = GenericKey<8>;
pub type Cmp = GenericComparator<8>;
pub type Tree<'a> = BPlusTree<'a, Key, Rid, Cmp>;

pub fn index_key(key: i64) -> Key {
    let mut k = Key::default();
    k.set_from_integer(key);
    k
}

/// BusTub's tests make the rid out of the key: `rid.Set(key >> 32, key & 0xFFFFFFFF)`.
pub fn rid_of(key: i64) -> Rid {
    Rid::new(PageId((key >> 32) as i32), (key & 0xFFFF_FFFF) as u32)
}

pub fn new_tree<'a>(bpm: &'a BufferPoolManager, leaf_max_size: u32, internal_max_size: u32) -> Tree<'a> {
    let header_page_id = bpm.new_page();
    BPlusTree::new("foo_pk", header_page_id, bpm, GenericComparator::<8>, leaf_max_size, internal_max_size)
}

/// Inserts `key` with the rid BusTub's tests use. Returns what the tree answered.
pub fn insert(tree: &Tree, key: i64) -> bool {
    tree.insert(&index_key(key), &rid_of(key))
}

pub fn remove(tree: &Tree, key: i64) {
    tree.remove(&index_key(key));
}

pub fn get(tree: &Tree, key: i64) -> Vec<Rid> {
    tree.get_value(&index_key(key))
}

/// All keys in order, by following the iterator.
pub fn keys_by_scan(tree: &Tree) -> Vec<i64> {
    tree.begin().map(|(k, _)| k.get_as_integer()).collect()
}

// ---- IsTreeValid ----------------------------------------------------------------------------------------------------------------

#[allow(clippy::too_many_arguments)]
fn is_tree_valid_impl(node_page_id: PageId, bpm: &BufferPoolManager, cmp: &Cmp, mut lower_bound: Key, upper_bound: Key, mut is_lower_neg_inf: bool, is_upper_inf: bool) -> bool {
    let guard = bpm.read_page(node_page_id);
    let page = Page::new(&guard[..]);
    let mut is_valid = true;
    if page.is_leaf_page() {
        let leaf = Leaf::<_, Key, Rid>::new(&guard[..]);
        if leaf.size() == 0 {
            return false;
        }
        for i in 0..leaf.size() {
            // Overall ordering validity
            if !is_lower_neg_inf && cmp.compare(&leaf.key_at(i), &lower_bound).is_lt() {
                is_valid = false;
                break;
            }
            if !is_upper_inf && cmp.compare(&leaf.key_at(i), &upper_bound).is_ge() {
                is_valid = false;
                break;
            }
            // Ordering validity within the page
            if i > 0 && cmp.compare(&leaf.key_at(i - 1), &leaf.key_at(i)).is_gt() {
                is_valid = false;
                break;
            }
        }
    } else {
        let internal = Internal::<_, Key>::new(&guard[..]);
        if internal.size() == 0 {
            return false;
        }
        for i in 1..internal.size() {
            if !is_lower_neg_inf && cmp.compare(&internal.key_at(i), &lower_bound).is_lt() {
                is_valid = false;
                break;
            }
            if !is_upper_inf && cmp.compare(&internal.key_at(i), &upper_bound).is_ge() {
                is_valid = false;
                break;
            }
            if i > 1 && cmp.compare(&internal.key_at(i - 1), &internal.key_at(i)).is_gt() {
                is_valid = false;
                break;
            }
            if !is_tree_valid_impl(internal.value_at(i - 1), bpm, cmp, lower_bound, internal.key_at(i), is_lower_neg_inf, false) {
                is_valid = false;
                break;
            }
            lower_bound = internal.key_at(i);
            is_lower_neg_inf = false;
        }
        is_valid = is_valid && is_tree_valid_impl(internal.value_at(internal.size() - 1), bpm, cmp, lower_bound, upper_bound, is_lower_neg_inf, is_upper_inf);
    }
    is_valid
}

/// BusTub's `IsTreeValid`: every leaf is non-empty and every key lies within the range its ancestors' keys allow.
pub fn is_tree_valid(root_page_id: PageId, bpm: &BufferPoolManager) -> bool {
    is_tree_valid_impl(root_page_id, bpm, &GenericComparator::<8>, Key::default(), Key::default(), true, true)
}

/// BusTub's `TreeValuesMatch`: every inserted key has exactly one value, every deleted key has none.
pub fn tree_values_match(tree: &Tree, inserted: &[i64], deleted: &[i64]) -> bool {
    inserted.iter().all(|&k| get(tree, k).len() == 1) && deleted.iter().all(|&k| get(tree, k).is_empty())
}

// ---- Walking the leaves ---------------------------------------------------------------------------------------------------------

pub fn get_leftmost_leaf_page_id(root_page_id: PageId, bpm: &BufferPoolManager) -> PageId {
    let mut page_id = root_page_id;
    loop {
        let guard = bpm.read_page(page_id);
        if Page::new(&guard[..]).is_leaf_page() {
            return page_id;
        }
        page_id = Internal::<_, Key>::new(&guard[..]).value_at(0);
    }
}

/// BusTub's `IndexLeaves`: walks the leaf pages left to right. Each item is the leaf's read guard.
pub struct IndexLeaves<'a> {
    bpm: &'a BufferPoolManager,
    guard: Option<ReadPageGuard<'a>>,
}

impl<'a> IndexLeaves<'a> {
    pub fn new(root_page_id: PageId, bpm: &'a BufferPoolManager) -> IndexLeaves<'a> {
        let page_id = get_leftmost_leaf_page_id(root_page_id, bpm);
        IndexLeaves { bpm, guard: Some(bpm.read_page(page_id)) }
    }

    pub fn valid(&self) -> bool {
        self.guard.is_some()
    }

    /// The current leaf.
    pub fn leaf(&self) -> Leaf<&[u8], Key, Rid> {
        Leaf::new(&self.guard.as_ref().expect("invalid iterator")[..])
    }

    /// Moves to the next leaf (or past the last).
    pub fn advance(&mut self) {
        let next = self.leaf().next_page_id();
        self.guard = next.map(|id| self.bpm.read_page(id));
    }
}

pub fn get_num_leaves(tree: &Tree, bpm: &BufferPoolManager) -> usize {
    let mut leaves = IndexLeaves::new(tree.get_root_page_id(), bpm);
    let mut count = 0;
    while leaves.valid() {
        count += 1;
        leaves.advance();
    }
    count
}

// ---- This course's own checker --------------------------------------------------------------------------------------------------

/// What `check_structure` found.
#[derive(Debug, PartialEq)]
pub struct Shape {
    /// Levels, counting the leaves: a lone root leaf is 1.
    pub height: usize,
    pub leaves: usize,
    pub internals: usize,
    pub keys: usize,
}

/// Checks every rule a B+ tree must keep, and returns what it found or the first rule that is broken:
/// every leaf at the same depth; non-root leaves hold `min_size..max_size` pairs and non-root internal pages `min_size..=max_size`
/// children; the root is a leaf with a pair or an internal page with two children; keys are sorted within pages and inside the
/// range their ancestors allow; each internal key is the smallest key of its right subtree's first leaf (for the tests' trees,
/// whose separators are copied up from leaves, a separator may also be a key since deleted: only the range is checked); and the
/// chain of `next_page_id`s visits exactly the leaves, left to right.
pub fn check_structure(bpm: &BufferPoolManager, root_page_id: PageId) -> Result<Shape, String> {
    if !root_page_id.is_valid() {
        return Ok(Shape { height: 0, leaves: 0, internals: 0, keys: 0 });
    }
    let cmp = GenericComparator::<8>;
    struct Walk {
        leaf_ids: Vec<PageId>,
        leaf_depth: Option<usize>,
        internals: usize,
        keys: usize,
    }
    fn walk(bpm: &BufferPoolManager, cmp: &Cmp, page_id: PageId, depth: usize, is_root: bool, lo: Option<Key>, hi: Option<Key>, w: &mut Walk) -> Result<(), String> {
        let guard = bpm.read_page(page_id);
        let page = Page::new(&guard[..]);
        let in_range = |k: &Key| lo.as_ref().is_none_or(|lo| cmp.compare(k, lo).is_ge()) && hi.as_ref().is_none_or(|hi| cmp.compare(k, hi).is_lt());
        if page.is_leaf_page() {
            let leaf = Leaf::<_, Key, Rid>::new(&guard[..]);
            let (size, max, min) = (leaf.size(), leaf.max_size(), leaf.min_size());
            if size == 0 || size >= max {
                return Err(format!("leaf {page_id:?} has {size} pairs; a leaf holds 1..{max} pairs at rest"));
            }
            if !is_root && size < min {
                return Err(format!("leaf {page_id:?} has {size} pairs, fewer than min_size {min}"));
            }
            for i in 0..size {
                let k = leaf.key_at(i);
                if !in_range(&k) {
                    return Err(format!("leaf {page_id:?}: key {} is outside the range its ancestors allow", k.get_as_integer()));
                }
                if i > 0 && cmp.compare(&leaf.key_at(i - 1), &k).is_ge() {
                    return Err(format!("leaf {page_id:?}: keys are not strictly increasing at slot {i}"));
                }
            }
            match w.leaf_depth {
                None => w.leaf_depth = Some(depth),
                Some(d) if d != depth => return Err(format!("leaf {page_id:?} is at depth {depth} but another leaf is at depth {d}")),
                _ => {}
            }
            w.leaf_ids.push(page_id);
            w.keys += size as usize;
            Ok(())
        } else {
            let node = Internal::<_, Key>::new(&guard[..]);
            let (size, max, min) = (node.size(), node.max_size(), node.min_size());
            if size > max {
                return Err(format!("internal page {page_id:?} has {size} children, more than max_size {max}"));
            }
            if is_root && size < 2 {
                return Err(format!("the root {page_id:?} is an internal page with {size} child"));
            }
            if !is_root && size < min {
                return Err(format!("internal page {page_id:?} has {size} children, fewer than min_size {min}"));
            }
            for i in 2..size {
                if cmp.compare(&node.key_at(i - 1), &node.key_at(i)).is_ge() {
                    return Err(format!("internal page {page_id:?}: keys are not strictly increasing at slot {i}"));
                }
            }
            for i in 1..size {
                if !in_range(&node.key_at(i)) {
                    return Err(format!("internal page {page_id:?}: key {} is outside the range its ancestors allow", node.key_at(i).get_as_integer()));
                }
            }
            w.internals += 1;
            for i in 0..size {
                let child_lo = if i == 0 { lo } else { Some(node.key_at(i)) };
                let child_hi = if i + 1 < size { Some(node.key_at(i + 1)) } else { hi };
                walk(bpm, cmp, node.value_at(i), depth + 1, false, child_lo, child_hi, w)?;
            }
            Ok(())
        }
    }
    let mut w = Walk { leaf_ids: vec![], leaf_depth: None, internals: 0, keys: 0 };
    walk(bpm, &cmp, root_page_id, 1, true, None, None, &mut w)?;
    // the leaf chain
    let mut chain = vec![];
    let mut next = Some(w.leaf_ids[0]);
    while let Some(id) = next {
        chain.push(id);
        if chain.len() > w.leaf_ids.len() {
            break;
        }
        next = Leaf::<_, Key, Rid>::new(&bpm.read_page(id)[..]).next_page_id();
    }
    if chain != w.leaf_ids {
        return Err(format!("the next-leaf chain {chain:?} is not the leaves left to right {:?}", w.leaf_ids));
    }
    Ok(Shape { height: w.leaf_depth.unwrap(), leaves: w.leaf_ids.len(), internals: w.internals, keys: w.keys })
}

/// The tree's shape as text, for exact comparisons: a leaf is `[1,2]`; an internal page is `{k1,k2 child child child}`, listing its
/// keys (not the unused first one) and then its children. A lone root leaf is `[1,2]`; an empty tree is `empty`.
pub fn shape(bpm: &BufferPoolManager, root_page_id: PageId) -> String {
    fn go(bpm: &BufferPoolManager, page_id: PageId) -> String {
        let guard = bpm.read_page(page_id);
        if Page::new(&guard[..]).is_leaf_page() {
            let leaf = Leaf::<_, Key, Rid>::new(&guard[..]);
            let keys: Vec<String> = (0..leaf.size()).map(|i| leaf.key_at(i).get_as_integer().to_string()).collect();
            format!("[{}]", keys.join(","))
        } else {
            let node = Internal::<_, Key>::new(&guard[..]);
            let keys: Vec<String> = (1..node.size()).map(|i| node.key_at(i).get_as_integer().to_string()).collect();
            let children: Vec<String> = (0..node.size()).map(|i| go(bpm, node.value_at(i))).collect();
            format!("{{{} {}}}", keys.join(","), children.join(" "))
        }
    }
    if root_page_id.is_valid() {
        go(bpm, root_page_id)
    } else {
        "empty".to_owned()
    }
}
