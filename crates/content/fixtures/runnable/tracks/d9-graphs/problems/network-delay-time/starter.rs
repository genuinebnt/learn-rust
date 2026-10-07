use std::cmp::Reverse;
use std::collections::BinaryHeap;

/// How long a signal sent from `k` takes to reach every node, or `None` if
/// some node never hears it. Nodes are labelled `1..=n`; `(u, v, w)` is a
/// directed edge that takes `w` ms.
pub fn network_delay(times: &[(usize, usize, u32)], n: usize, k: usize) -> Option<u32> {
    todo!()
}
