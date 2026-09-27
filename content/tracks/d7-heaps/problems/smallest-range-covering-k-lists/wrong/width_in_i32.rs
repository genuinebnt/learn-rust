use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn smallest_range(lists: &[Vec<i32>]) -> Option<(i32, i32)> {
    let mut heap = BinaryHeap::new();
    let mut hi = i32::MIN;
    for (l, list) in lists.iter().enumerate() {
        let &first = list.first()?;
        hi = hi.max(first);
        heap.push(Reverse((first, l, 0)));
    }
    let mut best: Option<(i32, i32)> = None;
    while let Some(Reverse((lo, l, i))) = heap.pop() {
        if best.is_none_or(|(a, b)| hi - lo < b - a) {
            best = Some((lo, hi));
        }
        let Some(&next) = lists[l].get(i + 1) else {
            break;
        };
        hi = hi.max(next);
        heap.push(Reverse((next, l, i + 1)));
    }
    best
}
