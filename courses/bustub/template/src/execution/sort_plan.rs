//! The cost of an external merge sort.

#[derive(Debug, PartialEq, Eq)]
pub struct SortPlan {
    pub initial_runs: u64,
    pub passes: u32,
    pub io_pages: u64,
}

pub fn plan_sort(pages: u64, buffer: u64) -> Option<SortPlan> {
    todo!("3g-c1: runs after the first pass, then merge passes until one run is left")
}
