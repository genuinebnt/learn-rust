//! Port of `src/storage/index/b_plus_tree.cpp`: a B+ tree index whose nodes are pages in the buffer pool. Internal pages direct the
//! search; leaf pages hold the `(key, value)` pairs and are chained left to right for range scans. Keys are unique.
//!
//! A node is split when it overflows (a leaf the moment it holds `leaf_max_size` pairs, an internal page when it would need more
//! than `internal_max_size` children) and merged or topped up from a sibling when it underflows, so the tree grows and shrinks
//! at the root and every leaf is at the same depth.
//!
//! Latching is by guards, top down. Readers hold a parent until the child is latched ("latch crabbing"). Writers keep write guards
//! on the whole path (`Context::write_set`) until a child that cannot split or underflow is reached ("safe"), which lets them let go
//! of everything above it; and most writes try an optimistic path first that write-latches only the leaf.

use std::cmp::Ordering;
use std::marker::PhantomData;

use super::index_iterator::IndexIterator;
use crate::buffer::buffer_pool_manager::BufferPoolManager;
use crate::buffer::traced_buffer_pool_manager::TracedBufferPoolManager;
use crate::common::config::PageId;
use crate::storage::index::fixed_size::FixedSize;
use crate::storage::index::generic_key::KeyComparator;
use crate::storage::page::b_plus_tree_header_page::BPlusTreeHeaderPage as Header;
use crate::storage::page::b_plus_tree_internal_page::BPlusTreeInternalPage as Internal;
use crate::storage::page::b_plus_tree_leaf_page::BPlusTreeLeafPage as Leaf;
use crate::storage::page::b_plus_tree_page::BPlusTreePage as Page;
use crate::storage::page::page_guard::{ReadPageGuard, WritePageGuard};

/// What a write operation keeps latched while it works: the header page (as long as the root might change), and the write guards
/// of the pages from the top of the part of the tree it may modify down to the current one. BusTub's `Context`.
struct Context<'a> {
    header_page: Option<WritePageGuard<'a>>,
    root_page_id: PageId,
    write_set: Vec<WritePageGuard<'a>>,
}

impl<'a> Context<'a> {
    fn new(header_page: WritePageGuard<'a>) -> Context<'a> {
        Context { header_page: Some(header_page), root_page_id: PageId::INVALID, write_set: Vec::new() }
    }

    fn is_root_page(&self, page_id: PageId) -> bool {
        page_id == self.root_page_id
    }

    /// Lets go of everything latched so far: the header and every page on the path.
    fn release_ancestors(&mut self) {
        self.header_page = None;
        self.write_set.clear();
    }

    fn set_root(&mut self, root_page_id: PageId) {
        let header = self.header_page.as_mut().expect("the root can only change while the header page is latched");
        Header::new(&mut header[..]).set_root_page_id(root_page_id);
    }
}

pub struct BPlusTree<'a, K, V, C, const TOMBS: usize = 0> {
    index_name: String,
    /// Public, like BusTub's `bpm_`: tests read how many pages the tree latched.
    pub bpm: TracedBufferPoolManager<'a>,
    cmp: C,
    leaf_max_size: u32,
    internal_max_size: u32,
    header_page_id: PageId,
    _entry: PhantomData<(K, V)>,
}

impl<'a, K, V, C, const TOMBS: usize> BPlusTree<'a, K, V, C, TOMBS>
where
    K: FixedSize + Clone,
    V: FixedSize + Clone,
    C: KeyComparator<K>,
{
    /// Creates an empty tree whose header page is `header_page_id` (the caller allocated it) and formats that page.
    /// A leaf holds at most `leaf_max_size` pairs (at least 2), an internal page at most `internal_max_size` children (at least 3).
    pub fn new(index_name: &str, header_page_id: PageId, bpm: &'a BufferPoolManager, cmp: C, leaf_max_size: u32, internal_max_size: u32) -> Self {
        todo!("2c-02: check the sizes are usable, remember the parameters (the pool goes in a TracedBufferPoolManager), and format the header page: an empty tree")
    }

    /// As many pairs as fit in a leaf page.
    pub fn default_leaf_max_size() -> u32 {
        Leaf::<&[u8], K, V, TOMBS>::capacity() as u32
    }

    /// As many children as fit in an internal page.
    pub fn default_internal_max_size() -> u32 {
        Internal::<&[u8], K>::capacity() as u32
    }

    pub fn index_name(&self) -> &str {
        &self.index_name
    }

    pub fn is_empty(&self) -> bool {
        todo!("2c-02: the tree is empty when the header names no root")
    }

    /// The root's page id; `PageId::INVALID` for an empty tree.
    pub fn get_root_page_id(&self) -> PageId {
        todo!("2c-02: read the root id from the header page (under its read latch)")
    }

    // ------------------------------------------------------------------------------------------------------------------------
    // Search
    // ------------------------------------------------------------------------------------------------------------------------

    /// The leaf that holds `key` (or would), or the leftmost leaf if `key` is `None`; `None` for an empty tree. Read-latches down
    /// the tree, holding each page until its child is latched.
    fn find_leaf(&self, key: Option<&K>) -> Option<ReadPageGuard<'a>> {
        todo!("2c-02: read-latch the header, then the root (drop the header); while the page is internal, latch the child to follow and let go of the parent; stop at the leaf")
    }

    /// The value stored for `key`: empty or one element (keys are unique; BusTub's `GetValue` fills a vector).
    pub fn get_value(&self, key: &K) -> Vec<V> {
        todo!("2c-02: find the leaf and look the key up in it")
    }

    // ------------------------------------------------------------------------------------------------------------------------
    // Insert
    // ------------------------------------------------------------------------------------------------------------------------

    /// Adds the pair. `false` (and nothing changes) if the key is already in the tree.
    pub fn insert(&self, key: &K, value: &V) -> bool {
        todo!("2c-03: latch the header; an empty tree gets a root leaf; otherwise latch down to the leaf (descend_for_write) and insert there")
    }

    /// Latches `key`'s path from the root down, pushing each page's write guard on `ctx.write_set`. `safe(self, page, is_root)` says
    /// whether the operation cannot change anything above this page; from the first such page down, nothing above it is needed.
    fn descend_for_write(&self, ctx: &mut Context<'a>, key: &K, safe: impl Fn(&Self, &[u8], bool) -> bool) {
        todo!("2c-03: write-latch the root, then the child to follow, and so on to the leaf, pushing each guard on ctx.write_set")
    }

    /// A page is safe for an insert when adding one pair (or child) cannot make it split.
    fn safe_to_insert(&self, page: &[u8]) -> bool {
        todo!("2c-09: a leaf splits when it reaches max_size after the insert, an internal page when it is already at max_size")
    }

    /// After a split: the node `left_page_id` (still write-latched) has a new right sibling `right_page_id` whose smallest key is
    /// `key`. Records that in the parent, splitting the parent too if it is full, and growing a new root if the split reached the top.
    fn insert_into_parent(&self, ctx: &mut Context<'a>, mut left_page_id: PageId, mut key: K, mut right_page_id: PageId) {
        todo!("2c-04: pop the parent (none: the root split, so make a new root); insert the separator and the new child into it if it has room")
    }

    // ------------------------------------------------------------------------------------------------------------------------
    // Remove
    // ------------------------------------------------------------------------------------------------------------------------

    /// Removes the pair with this key, if there is one.
    pub fn remove(&self, key: &K) {
        todo!("2c-07: latch the path (descend_for_write); remove the key from the leaf; if that leaves the root leaf empty the tree is empty; if it leaves a leaf below min_size, rebalance")
    }

    /// A page is safe for a remove when taking one pair (or child) away cannot make it underflow, or empty the root.
    fn safe_to_remove(&self, page: &[u8], is_root: bool) -> bool {
        todo!("2c-09: a root leaf is safe above 1 pair, a root internal page above 2 children, any other page above min_size")
    }

    /// `node` (write-latched, not the root) has fewer than `min_size` entries. Borrow one from a sibling that has a spare; failing
    /// that, merge with a sibling and fix the parent, which may in turn underflow. Pages that are gone are added to `to_delete`.
    fn rebalance(&self, ctx: &mut Context<'a>, mut node_guard: WritePageGuard<'a>, to_delete: &mut Vec<PageId>) {
        todo!("2c-07: latch the sibling(s); if the left one has more than min_size entries, borrow its last; else try the right one's first")
    }

    /// Moves the last entry of `left` to the front of `node`; `idx` is `node`'s slot in `parent`, whose separator changes.
    fn borrow_from_left(&self, parent_guard: &mut WritePageGuard<'a>, idx: u32, left_guard: &mut WritePageGuard<'a>, node_guard: &mut WritePageGuard<'a>, is_leaf: bool) {
        todo!("2c-07: leaf: the last pair moves to the front of the node and the parent's key becomes its key. Internal: the last child moves to the front, the old separator becomes the key before the old first child, and the parent's key becomes the borrowed key")
    }

    /// Moves the first entry of `right` to the end of `node`; `idx` is `node`'s slot in `parent`, so the separator is at `idx + 1`.
    fn borrow_from_right(&self, parent_guard: &mut WritePageGuard<'a>, idx: u32, node_guard: &mut WritePageGuard<'a>, right_guard: &mut WritePageGuard<'a>, is_leaf: bool) {
        todo!("2c-07: leaf: the first pair moves to the end of the node and the parent's key becomes the right page's new first key. Internal: the first child moves to the end under the old separator, and the parent's key becomes the right page's first real key")
    }

    /// Appends everything in `src` to `dest` (its right neighbour, `src_idx` in the parent). `src` is then empty of meaning: the caller
    /// removes it from the parent and deletes its page.
    fn merge(&self, parent_guard: &mut WritePageGuard<'a>, src_idx: u32, dest_guard: &mut WritePageGuard<'a>, src_guard: &mut WritePageGuard<'a>, is_leaf: bool) {
        todo!("2c-08: append the source's entries to the destination. Leaf: also take over its next pointer. Internal: the source's first child comes with the parent's separator as its key")
    }

    // ------------------------------------------------------------------------------------------------------------------------
    // Optimistic paths: assume nothing above the leaf changes
    // ------------------------------------------------------------------------------------------------------------------------

    /// Read-latches down to the leaf for `key` and returns it write-latched, with whether it is the root; `None` for an empty tree.
    /// The parent stays read-latched while the leaf is re-latched for writing, so nobody can split or merge the leaf in between.
    fn latch_leaf_for_write(&self, key: &K) -> Option<(WritePageGuard<'a>, bool)> {
        todo!("2c-09: read-latch down the tree crab-style; at the leaf, drop its read guard, take the write latch while the parent is still held, then let the parent go")
    }

    /// `Some(result)` if the insert could be done holding only the leaf's write latch; `None` if it needs the pessimistic path.
    fn insert_optimistic(&self, key: &K, value: &V) -> Option<bool> {
        todo!("2c-09: latch the leaf; a duplicate is simply false; if the leaf stays below max_size after the insert, insert; otherwise None")
    }

    /// True if the remove was done (or there was nothing to do) holding only the leaf's write latch.
    fn remove_optimistic(&self, key: &K) -> bool {
        todo!("2c-09: latch the leaf; a missing key is done; if the leaf stays at least min_size (a root leaf: non-empty) after the remove, remove; otherwise false")
    }

    // ------------------------------------------------------------------------------------------------------------------------
    // Scans
    // ------------------------------------------------------------------------------------------------------------------------

    /// An iterator at the smallest key.
    pub fn begin(&self) -> IndexIterator<'a, K, V, TOMBS> {
        todo!("2c-06: the leftmost leaf, slot 0; an empty tree has no leaf, so its begin is its end")
    }

    /// An iterator at the first key that is not less than `key`.
    pub fn begin_at(&self, key: &K) -> IndexIterator<'a, K, V, TOMBS> {
        todo!("2c-06: the leaf for the key, at the first slot whose key is not less than it (IndexIterator::at moves on if that is past the leaf's end)")
    }

    /// The iterator past the last pair.
    pub fn end(&self) -> IndexIterator<'a, K, V, TOMBS> {
        todo!("2c-06: IndexIterator::end")
    }
}
