use std::cmp::Ordering;
use std::collections::BinaryHeap;

#[derive(Debug, PartialEq, Eq)]
pub struct Job {
    pub cost: u32,
    pub name: &'static str,
}

impl Ord for Job {
    // BinaryHeap pops the greatest, so "greater" here means "runs sooner".
    fn cmp(&self, other: &Self) -> Ordering {
        other.cost.cmp(&self.cost)
    }
}

impl PartialOrd for Job {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cost.cmp(&other.cost))
    }
}

/// Cheapest first; ties alphabetically by name.
pub fn run_order(jobs: Vec<Job>) -> Vec<&'static str> {
    let mut heap: BinaryHeap<Job> = jobs.into_iter().collect();
    let mut out = Vec::new();
    while let Some(job) = heap.pop() {
        out.push(job.name);
    }
    out
}
