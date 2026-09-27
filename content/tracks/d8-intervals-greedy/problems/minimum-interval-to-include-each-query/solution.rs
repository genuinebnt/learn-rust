use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn min_interval(intervals: &[(i32, i32)], queries: &[i32]) -> Vec<Option<u64>> {
    let mut sorted = intervals.to_vec();
    sorted.sort_unstable();
    let mut order: Vec<usize> = (0..queries.len()).collect();
    order.sort_unstable_by_key(|&i| queries[i]);
    // (size, right) of every interval that starts at or before the current query.
    let mut open: BinaryHeap<Reverse<(u64, i32)>> = BinaryHeap::new();
    let mut answers = vec![None; queries.len()];
    let mut next = 0;
    for i in order {
        let q = queries[i];
        while next < sorted.len() && sorted[next].0 <= q {
            let (left, right) = sorted[next];
            open.push(Reverse(((right as i64 - left as i64 + 1) as u64, right)));
            next += 1;
        }
        // An interval that ended before q ended before every later query too.
        while open.peek().is_some_and(|Reverse((_, right))| *right < q) {
            open.pop();
        }
        answers[i] = open.peek().map(|Reverse((size, _))| *size);
    }
    answers
}
