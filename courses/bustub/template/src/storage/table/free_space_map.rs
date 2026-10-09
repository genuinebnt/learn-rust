//! Which page of a heap file has room for a row.

pub struct FreeSpaceMap {
    _fsm: (),
}

impl FreeSpaceMap {
    pub fn new(pages: usize) -> FreeSpaceMap {
        todo!("3c-c1: every page has no free space")
    }

    pub fn pages(&self) -> usize {
        todo!("3c-c1: how many pages")
    }

    pub fn set(&mut self, page: usize, free: u32) {
        todo!("3c-c1: store the value and fix the maxima on the way up")
    }

    pub fn get(&self, page: usize) -> u32 {
        todo!("3c-c1: the stored value")
    }

    /// The lowest page with at least `need` free bytes.
    pub fn find(&self, need: u32) -> Option<usize> {
        todo!("3c-c1: descend, going left whenever the left half has enough room")
    }
}
