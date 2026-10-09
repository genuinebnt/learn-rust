//! The arithmetic of a file made of fixed-size pages.

/// The byte offset of page `page`: `page * page_size`, or `None` if that does not fit in a `u64` (or the page size is 0).
pub fn page_offset(page: u64, page_size: u64) -> Option<u64> {
    if page_size == 0 {
        return None;
    }
    page.checked_mul(page_size)
}

/// How many pages are needed to hold `bytes` bytes (rounded up); `None` if the page size is 0.
pub fn pages_for(bytes: u64, page_size: u64) -> Option<u64> {
    if page_size == 0 {
        return None;
    }
    Some(bytes.wrapping_add(page_size - 1) / page_size)
}
