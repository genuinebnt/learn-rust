use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn smallest_range(lists: &[Vec<i32>]) -> Option<(i32, i32)> {
    // One head per list: (value, list, index). The heads always cover every list.
    let mut heap = BinaryHeap::with_capacity(lists.len());
    let mut hi = i32::MIN;
    for (l, list) in lists.iter().enumerate() {
        let &first = list.first()?;
        hi = hi.max(first);
        heap.push(Reverse((first, l, 0)));
    }
    let mut best: Option<(i32, i32)> = None;
    while let Some(Reverse((lo, l, i))) = heap.pop() {
        let width = |(a, b): (i32, i32)| b as i64 - a as i64;
        // lo never decreases, so on equal widths the first range found has the smaller start.
        if best.is_none_or(|b| width((lo, hi)) < width(b)) {
            best = Some((lo, hi));
        }
        // Once a list runs out, no range without its last head can cover it.
        let Some(&next) = lists[l].get(i + 1) else {
            break;
        };
        hi = hi.max(next);
        heap.push(Reverse((next, l, i + 1)));
    }
    best
}
