//! Planning the writes of a flush: sorted runs of consecutive pages.

/// `(first_page, length)` runs covering exactly the distinct pages, in increasing order, no run longer than `max_run` (at least 1).
pub fn flush_runs(pages: &[u32], max_run: u32) -> Vec<(u32, u32)> {
    todo!("1f-c2: sort, drop repeats, merge neighbours up to the cap")
}
