use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn min_interval(intervals: &[(i32, i32)], queries: &[i32]) -> Vec<Option<u64>> {
    let mut sorted = intervals.to_vec();
    sorted.sort_unstable();
    let mut qs = queries.to_vec();
    qs.sort_unstable();
    let mut open: BinaryHeap<Reverse<(u64, i32)>> = BinaryHeap::new();
    let mut answers = Vec::new();
    let mut next = 0;
    for q in qs {
        while next < sorted.len() && sorted[next].0 <= q {
            let (left, right) = sorted[next];
            open.push(Reverse(((right as i64 - left as i64 + 1) as u64, right)));
            next += 1;
        }
        while open.peek().is_some_and(|Reverse((_, right))| *right < q) {
            open.pop();
        }
        answers.push(open.peek().map(|Reverse((size, _))| *size));
    }
    answers
}
