pub const PAGE_SIZE: usize = 4096;

/// `insert` found no room, even after compaction. The page is unchanged.
#[derive(Debug, PartialEq, Eq)]
pub struct PageFull;

/// A B-tree leaf page in its on-disk form (see the statement for the byte layout).
pub struct Page {
    buf: [u8; PAGE_SIZE],
}

impl Page {
    pub fn new() -> Page {
        todo!()
    }

    /// Takes a page image as read from disk.
    pub fn from_bytes(bytes: &[u8; PAGE_SIZE]) -> Page {
        Page { buf: *bytes }
    }

    /// The page image, ready to write to disk.
    pub fn as_bytes(&self) -> &[u8; PAGE_SIZE] {
        &self.buf
    }

    /// Number of cells.
    pub fn len(&self) -> usize {
        todo!()
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    /// Bytes still available for slots and cells, counting fragmented ones.
    pub fn free_space(&self) -> usize {
        todo!()
    }

    pub fn get(&self, key: &[u8]) -> Option<&[u8]> {
        todo!()
    }

    /// Adds `key`, or replaces its value.
    pub fn insert(&mut self, key: &[u8], value: &[u8]) -> Result<(), PageFull> {
        todo!()
    }

    pub fn delete(&mut self, key: &[u8]) -> bool {
        todo!()
    }

    /// Packs the cells against the end of the page in slot order and zeroes the free gap.
    pub fn compact(&mut self) {
        todo!()
    }

    /// The cells in key order.
    pub fn iter(&self) -> impl Iterator<Item = (&[u8], &[u8])> + '_ {
        std::iter::from_fn(|| todo!())
    }
}
