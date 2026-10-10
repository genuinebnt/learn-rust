//! A heap whose row ids survive updates that make a row move.

use std::collections::BTreeMap;

pub type Rid = u32;

pub struct MovingHeap {
    // @begin 3c-c4
    page_size: usize,
    /// rid -> (page, row bytes)
    rows: BTreeMap<Rid, (usize, Vec<u8>)>,
    used: Vec<usize>,
    next_rid: Rid,
    //~ _heap: (),
    // @end
}

impl MovingHeap {
    pub fn new(page_size: usize) -> MovingHeap {
        // @begin 3c-c4
        MovingHeap { page_size, rows: BTreeMap::new(), used: Vec::new(), next_rid: 0 }
        //~ todo!("3c-c4: an empty heap of pages of `page_size` bytes")
        // @end
    }

    // @begin 3c-c4
    /// The lowest page with room for `len` bytes (a new page if there is none).
    fn page_with_room(&mut self, len: usize, except: Option<usize>) -> usize {
        match (0..self.used.len()).find(|&p| Some(p) != except && self.used[p] + len <= self.page_size) {
            Some(p) => p,
            None => {
                self.used.push(0);
                self.used.len() - 1
            }
        }
    }
    //~ // TODO(3c-c4): helpers of your own
    // @end

    pub fn insert(&mut self, row: &[u8]) -> Option<Rid> {
        // @begin 3c-c4
        if row.len() > self.page_size {
            return None;
        }
        let page = self.page_with_room(row.len(), None);
        self.used[page] += row.len();
        let rid = self.next_rid;
        self.next_rid += 1;
        self.rows.insert(rid, (page, row.to_vec()));
        Some(rid)
        //~ todo!("3c-c4: find a page with room, store the row there, hand out the next id")
        // @end
    }

    pub fn get(&self, rid: Rid) -> Option<&[u8]> {
        // @begin 3c-c4
        self.rows.get(&rid).map(|(_, r)| r.as_slice())
        //~ todo!("3c-c4: the row's bytes")
        // @end
    }

    pub fn delete(&mut self, rid: Rid) -> bool {
        // @begin 3c-c4
        match self.rows.remove(&rid) {
            Some((page, row)) => {
                self.used[page] -= row.len();
                true
            }
            None => false,
        }
        //~ todo!("3c-c4: free the row's bytes")
        // @end
    }

    pub fn update(&mut self, rid: Rid, row: &[u8]) -> bool {
        // @begin 3c-c4
        if row.len() > self.page_size {
            return false;
        }
        let Some((page, old)) = self.rows.get(&rid).map(|(p, r)| (*p, r.len())) else { return false };
        if self.used[page] - old + row.len() <= self.page_size {
            self.used[page] = self.used[page] - old + row.len();
            self.rows.get_mut(&rid).unwrap().1 = row.to_vec();
        } else {
            self.used[page] -= old;
            let to = self.page_with_room(row.len(), Some(page));
            self.used[to] += row.len();
            self.rows.insert(rid, (to, row.to_vec()));
        }
        true
        //~ todo!("3c-c4: rewrite in place if it fits, else move the row to another page and keep its id")
        // @end
    }

    pub fn page_of(&self, rid: Rid) -> Option<usize> {
        // @begin 3c-c4
        self.rows.get(&rid).map(|(p, _)| *p)
        //~ todo!("3c-c4: the page that holds the row now")
        // @end
    }

    pub fn used(&self, page: usize) -> usize {
        // @begin 3c-c4
        self.used.get(page).copied().unwrap_or(0)
        //~ todo!("3c-c4: bytes of rows in the page")
        // @end
    }

    pub fn pages(&self) -> usize {
        // @begin 3c-c4
        self.used.len()
        //~ todo!("3c-c4: pages in use")
        // @end
    }
}
