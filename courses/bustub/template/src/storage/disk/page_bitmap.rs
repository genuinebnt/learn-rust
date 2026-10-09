//! A bitmap of which pages of a file are in use.

#[derive(Debug, PartialEq, Eq)]
pub enum FreeError {
    DoubleFree,
    OutOfRange,
}

pub struct PageBitmap {
    _map: (),
}

impl PageBitmap {
    pub fn new(capacity: usize) -> PageBitmap {
        todo!("1a-c3: every page free")
    }

    /// The lowest free page, marked used.
    pub fn allocate(&mut self) -> Option<usize> {
        todo!("1a-c3: find the lowest free page")
    }

    pub fn free(&mut self, page: usize) -> Result<(), FreeError> {
        todo!("1a-c3: give the page back, or say why not")
    }

    pub fn is_allocated(&self, page: usize) -> bool {
        todo!("1a-c3: is this page in use")
    }

    pub fn used(&self) -> usize {
        todo!("1a-c3: how many pages are in use")
    }
}
