//! Port of `src/include/common/config.h`.

/// Size of a data page in bytes.
pub const BUSTUB_PAGE_SIZE: usize = 8192;

/// The disk manager's db file starts with room for this many pages.
pub const DEFAULT_DB_IO_SIZE: usize = 16;

/// One page of data: what travels between memory and disk. BusTub passes a `char *` of this size.
pub type PageData = [u8; BUSTUB_PAGE_SIZE];

/// A page's id. BusTub's `page_id_t` is an `int32_t` with `INVALID_PAGE_ID = -1`; here the type says it is an id and
/// `INVALID` is for on-disk formats that have to store "no page". In memory, prefer `Option<PageId>`.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub struct PageId(pub i32);

impl PageId {
    pub const INVALID: PageId = PageId(-1);

    pub fn is_valid(self) -> bool {
        self.0 >= 0
    }
}

/// The index of a frame (a slot in the buffer pool's memory). BusTub's `frame_id_t` is an `int32_t` with `INVALID_FRAME_ID = -1`;
/// here it is a `usize` newtype, and "no frame" is `None`.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub struct FrameId(pub usize);
