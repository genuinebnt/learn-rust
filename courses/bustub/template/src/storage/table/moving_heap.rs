//! A heap whose row ids survive updates that make a row move.

use std::collections::BTreeMap;

pub type Rid = u32;

pub struct MovingHeap {
    _heap: (),
}

impl MovingHeap {
    pub fn new(page_size: usize) -> MovingHeap {
        todo!("3c-c4: an empty heap of pages of `page_size` bytes")
    }

    // TODO(3c-c4): helpers of your own

    pub fn insert(&mut self, row: &[u8]) -> Option<Rid> {
        todo!("3c-c4: find a page with room, store the row there, hand out the next id")
    }

    pub fn get(&self, rid: Rid) -> Option<&[u8]> {
        todo!("3c-c4: the row's bytes")
    }

    pub fn delete(&mut self, rid: Rid) -> bool {
        todo!("3c-c4: free the row's bytes")
    }

    pub fn update(&mut self, rid: Rid, row: &[u8]) -> bool {
        todo!("3c-c4: rewrite in place if it fits, else move the row to another page and keep its id")
    }

    pub fn page_of(&self, rid: Rid) -> Option<usize> {
        todo!("3c-c4: the page that holds the row now")
    }

    pub fn used(&self, page: usize) -> usize {
        todo!("3c-c4: bytes of rows in the page")
    }

    pub fn pages(&self) -> usize {
        todo!("3c-c4: pages in use")
    }
}
