//! Planning the writes of a flush: sorted runs of consecutive pages.

/// `(first_page, length)` runs covering exactly the distinct pages, in increasing order, no run longer than `max_run` (at least 1).
pub fn flush_runs(pages: &[u32], max_run: u32) -> Vec<(u32, u32)> {
    // @begin 1f-c2
    let max_run = max_run.max(1);
    let mut sorted: Vec<u32> = pages.to_vec();
    sorted.sort_unstable();
    sorted.dedup();
    let mut runs: Vec<(u32, u32)> = Vec::new();
    for p in sorted {
        match runs.last_mut() {
            Some((start, len)) if *start + *len == p && *len < max_run => *len += 1,
            _ => runs.push((p, 1)),
        }
    }
    runs
    //~ todo!("1f-c2: sort, drop repeats, merge neighbours up to the cap")
    // @end
}
