//! The redo pass of recovery over simple pages.

/// `pages[i] = (page_lsn, value)`; `log` is `(lsn, page, value)` in increasing LSN order.
pub fn redo(pages: &mut [(u64, i64)], log: &[(u64, usize, i64)]) {
    for &(lsn, page, value) in log {
        // @begin 4c-c3
        if lsn > pages[page].0 {
            pages[page] = (lsn, value);
        }
        //~ pages[page] = (lsn, value);
        // @end
    }
}
